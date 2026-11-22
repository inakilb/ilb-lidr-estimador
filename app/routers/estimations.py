"""HTTP routes for software estimations.

`POST /estimate` receives a meeting transcription and returns the estimation generated
by `app.services.llm_service`. The app includes this router with the `/api/v1` prefix,
so the route is served at `POST /api/v1/estimate`.

Service errors are mapped to HTTP status codes:

- `UnsupportedProviderError` -> 501
- `LLMUpstreamError` (retryable) -> 503 with `Retry-After`
- `LLMUpstreamError` (not retryable) -> 502
- `IncompleteEstimationError` -> 502
- invalid configuration -> 500
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.config import Settings, describe_config_error, get_settings
from app.services.llm_service import (
    EstimationResult,
    LLMServiceError,
    LLMUpstreamError,
    UnsupportedProviderError,
    generate_estimation,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["estimations"])

MAX_TRANSCRIPTION_CHARS = 50_000
RETRY_AFTER_SECONDS = 30

EXAMPLE_TRANSCRIPTION = (
    "En la reunión con el equipo de marketing, el cliente explicó que necesita una landing "
    "page con formulario de contacto, integración con su CRM actual (HubSpot), y una sección "
    "de blog con editor WYSIWYG. El plazo ideal sería tenerlo listo en 4 semanas. El diseño "
    "ya existe en Figma."
)


# --------------------------------------------------------------------------- schemas


class EstimationRequest(BaseModel):
    """Meeting transcription to estimate."""

    transcription: str = Field(
        min_length=1,
        max_length=MAX_TRANSCRIPTION_CHARS,
        description="Transcription (or summary) of the meeting with the client.",
        examples=[EXAMPLE_TRANSCRIPTION],
    )

    @field_validator("transcription")
    @classmethod
    def _strip_and_require_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("transcription must not be empty or whitespace only")
        return value


class TokenUsage(BaseModel):
    """Token usage of the LLM call."""

    input_tokens: int = Field(description="Uncached input tokens.")
    output_tokens: int = Field(description="Output tokens, including any reasoning tokens.")
    cache_read_input_tokens: int = Field(description="Input tokens read from the prompt cache.")
    cache_creation_input_tokens: int = Field(description="Input tokens written to the prompt cache.")


class EstimationResponse(BaseModel):
    """Generated estimation plus metadata of the LLM call."""

    estimation: str = Field(description="The estimation in Markdown (in Spanish).")
    model: str = Field(description="Model that generated the estimation.", examples=["claude-haiku-4-5"])
    provider: str = Field(description="LLM provider.", examples=["anthropic"])
    usage: TokenUsage
    estimated_cost_usd: float | None = Field(
        description="Estimated cost of the call at list prices; null if the model's price is unknown."
    )
    generated_at: datetime = Field(description="When the estimation was generated (UTC).")

    @classmethod
    def from_result(cls, result: EstimationResult) -> "EstimationResponse":
        """Build the HTTP response from the service result."""
        return cls(
            estimation=result.estimation,
            model=result.model,
            provider=result.provider,
            usage=TokenUsage(
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cache_read_input_tokens=result.cache_read_input_tokens,
                cache_creation_input_tokens=result.cache_creation_input_tokens,
            ),
            estimated_cost_usd=result.estimated_cost_usd,
            generated_at=datetime.now(timezone.utc),
        )


class ErrorResponse(BaseModel):
    """Error body returned by FastAPI's HTTPException."""

    detail: str


# --------------------------------------------------------------------------- dependencies


def settings_dependency() -> Settings:
    """Provide the settings; an invalid configuration becomes a 500 with a safe message."""
    try:
        return get_settings()
    except ValidationError as e:
        problems = describe_config_error(e)
        logger.error("Invalid configuration: %s", problems)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Service misconfigured: {problems}",
        ) from None


def _to_http_exception(error: LLMServiceError) -> HTTPException:
    """Translate a service error into the HTTP error the client receives."""
    headers = None
    if isinstance(error, UnsupportedProviderError):
        status_code = status.HTTP_501_NOT_IMPLEMENTED
    elif isinstance(error, LLMUpstreamError) and error.retryable:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        headers = {"Retry-After": str(RETRY_AFTER_SECONDS)}
    else:  # non-retryable upstream failure or incomplete estimation
        status_code = status.HTTP_502_BAD_GATEWAY
    logger.warning("Estimation failed (%d): %s", status_code, error)
    return HTTPException(status_code=status_code, detail=str(error), headers=headers)


# --------------------------------------------------------------------------- routes


@router.post(
    "/estimate",
    response_model=EstimationResponse,
    summary="Generate a software estimation from a meeting transcription",
    description=(
        "Sends the transcription to the LLM together with the static example estimations "
        "(CAG) and returns the generated estimation in Spanish, with token usage and cost."
    ),
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Service misconfigured."},
        status.HTTP_501_NOT_IMPLEMENTED: {"model": ErrorResponse, "description": "LLM provider not implemented."},
        status.HTTP_502_BAD_GATEWAY: {
            "model": ErrorResponse,
            "description": "The LLM provider failed (invalid key, no credits, model not found) "
            "or returned an unusable estimation.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "The LLM provider is temporarily unavailable; retry after `Retry-After` seconds.",
        },
    },
)
def estimate(
    request: EstimationRequest,
    settings: Settings = Depends(settings_dependency),
) -> EstimationResponse:
    """Generate the estimation for the request's transcription."""
    try:
        result = generate_estimation(request.transcription, settings)
    except LLMServiceError as e:
        raise _to_http_exception(e) from e
    return EstimationResponse.from_result(result)
