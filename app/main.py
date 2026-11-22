"""FastAPI application: CAG software estimator.

Mounts the estimations router under `/api/v1`, exposes `GET /health`, redirects `/` to
the Swagger UI at `/docs`, and configures logging from `LOG_LEVEL` at startup.

Run from the repository root: `uv run uvicorn app.main:app --reload`.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, ValidationError

from app.config import describe_config_error, get_settings
from app.routers import estimations

APP_VERSION = "0.1.0"  # keep in sync with pyproject.toml
API_PREFIX = "/api/v1"

DESCRIPTION = """\
Estimador de proyectos de software con arquitectura **CAG** (Cache-Augmented Generation).

Recibe la transcripción de una reunión con un cliente y devuelve una estimación de software \
generada por un LLM, en español:

1. La transcripción llega a `POST /api/v1/estimate`.
2. Se inyectan en el system prompt unos ejemplos estáticos de estimaciones previas (sin base \
de datos ni retrieval).
3. El LLM genera la estimación: desglose de tareas, totales, supuestos, fuera de alcance, \
riesgos, equipo y duración.

Proveedores: Anthropic (`claude-haiku-4-5` por defecto) y OpenAI (`gpt-4o-mini`), \
seleccionables con `LLM_PROVIDER` y `LLM_MODEL`. `GET /health` muestra el estado del servicio \
y la configuración del LLM, sin llamarlo.
"""

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Configure logging from LOG_LEVEL at startup; start anyway if the configuration is invalid."""
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        settings = get_settings()
    except ValidationError as e:
        logger.setLevel(logging.INFO)
        logger.error("Invalid configuration, estimations will fail until it is fixed: %s", describe_config_error(e))
    else:
        logger.setLevel(settings.log_level)
        logger.info(
            "Starting v%s (env=%s, provider=%s, model=%s, log_level=%s)",
            APP_VERSION,
            settings.app_env,
            settings.llm_provider,
            settings.llm_model,
            settings.log_level,
        )
    yield


app = FastAPI(
    title="Estimador de software (CAG)",
    description=DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.include_router(estimations.router, prefix=API_PREFIX)


# --------------------------------------------------------------------------- health


class LLMInfo(BaseModel):
    """Configured LLM provider and model."""

    provider: str = Field(examples=["anthropic"])
    model: str = Field(examples=["claude-haiku-4-5"])


class HealthResponse(BaseModel):
    """Service status. `degraded` means the process is up but the configuration is invalid."""

    status: Literal["ok", "degraded"]
    version: str
    environment: str | None = Field(default=None, description="APP_ENV; null when the configuration is invalid.")
    llm: LLMInfo | None = Field(default=None, description="Configured LLM; null when the configuration is invalid.")
    detail: str | None = Field(default=None, description="Configuration problem; only present when degraded.")


@app.get(
    "/health",
    response_model=HealthResponse,
    response_model_exclude_unset=True,
    tags=["health"],
    summary="Service status (does not call the LLM)",
)
def health() -> HealthResponse:
    """Report whether the service is up and its configuration is usable. Always 200."""
    try:
        settings = get_settings()
    except ValidationError as e:
        return HealthResponse(
            status="degraded",
            version=APP_VERSION,
            environment=None,
            llm=None,
            detail=f"Service misconfigured: {describe_config_error(e)}",
        )
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        environment=settings.app_env,
        llm=LLMInfo(provider=settings.llm_provider, model=settings.llm_model),
    )


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Send the base URL to the interactive documentation."""
    return RedirectResponse(url="/docs")
