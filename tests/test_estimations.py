"""POST /api/v1/estimate: validation, response, error mapping, settings (spec: estimate-endpoint)."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

import app.routers.estimations as est
from app.config import Settings
from app.main import app
from app.services.llm_service import (
    EstimationResult,
    IncompleteEstimationError,
    LLMUpstreamError,
    UnsupportedProviderError,
)
from helpers import FAKE_ANTHROPIC_KEY

URL = "/api/v1/estimate"
RESULT = EstimationResult(
    estimation="## Estimación: X",
    model="claude-haiku-4-5",
    provider="anthropic",
    input_tokens=111,
    output_tokens=800,
    cache_read_input_tokens=6736,
    cache_creation_input_tokens=0,
    estimated_cost_usd=0.0049,
)


@pytest.fixture
def service(monkeypatch):
    """Replace the LLM service in the router; `service(result_or_error)` sets its behavior."""
    calls = []

    def install(behavior=RESULT):
        def fake(transcription, settings):
            calls.append((transcription, settings))
            if isinstance(behavior, BaseException):
                raise behavior
            return behavior

        monkeypatch.setattr(est, "generate_estimation", fake)
        return calls

    return install


def test_success_returns_course_fields_and_extras(api_client, service):
    calls = service()
    response = api_client.post(URL, json={"transcription": "  Necesitamos una web.  ", "extra": "ignored"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"estimation", "model", "provider", "usage", "estimated_cost_usd", "generated_at"}
    assert (body["estimation"], body["model"], body["provider"]) == ("## Estimación: X", "claude-haiku-4-5", "anthropic")
    assert body["usage"] == {"input_tokens": 111, "output_tokens": 800, "cache_read_input_tokens": 6736, "cache_creation_input_tokens": 0}
    assert body["estimated_cost_usd"] == 0.0049
    generated_at = datetime.fromisoformat(body["generated_at"].replace("Z", "+00:00"))
    assert generated_at.utcoffset().total_seconds() == 0
    assert calls[0][0] == "Necesitamos una web."  # trimmed
    assert calls[0][1] is api_client.settings  # overridden settings reach the service


@pytest.mark.parametrize(
    "body",
    [{}, {"transcription": ""}, {"transcription": "   \n"}, {"transcription": "x" * 50_001}, {"transcription": 123}],
    ids=["missing", "empty", "whitespace", "too-long", "not-a-string"],
)
def test_invalid_request_is_422_without_calling_the_service(api_client, service, body):
    calls = service()
    assert api_client.post(URL, json=body).status_code == 422
    assert calls == []


def test_max_length_accepted(api_client, service):
    service()
    assert api_client.post(URL, json={"transcription": "x" * 50_000}).status_code == 200


@pytest.mark.parametrize(
    ("error", "status", "retry_after"),
    [
        (UnsupportedProviderError("LLM provider 'gemini' is not implemented"), 501, None),
        (LLMUpstreamError("LLM API error 429: rate limited.", retryable=True, status_code=429), 503, "30"),
        (LLMUpstreamError("The LLM API timed out.", retryable=True), 503, "30"),
        (LLMUpstreamError("LLM API error 401: invalid API key.", retryable=False, status_code=401), 502, None),
        (LLMUpstreamError("LLM API error 429: no credits (quota exhausted).", retryable=False, status_code=429), 502, None),
        (IncompleteEstimationError("The estimation was truncated."), 502, None),
    ],
    ids=["unsupported-provider", "rate-limited", "timeout", "invalid-key", "no-credits", "incomplete"],
)
def test_service_errors_mapped_to_http(api_client, service, error, status, retry_after):
    service(error)
    response = api_client.post(URL, json={"transcription": "algo"})
    assert response.status_code == status
    assert response.json()["detail"] == str(error)
    assert response.headers.get("retry-after") == retry_after


@pytest.mark.parametrize(
    "broken",
    [
        lambda: Settings(_env_file=None, llm_provider="anthropic", openai_api_key=SecretStr("sk-proj-SECRET-VALUE-77")),
        lambda: Settings(_env_file=None, llm_provider="openai", openai_api_key=SecretStr("sk-proj-SECRET-VALUE-77"), llm_model="claude-haiku-4-5"),
    ],
    ids=["missing-key", "model-provider-mismatch"],
)
def test_invalid_configuration_is_500_without_secrets(monkeypatch, service, broken):
    service()
    monkeypatch.setattr(est, "get_settings", broken)
    with TestClient(app) as client:
        response = client.post(URL, json={"transcription": "algo"})
    assert response.status_code == 500
    assert response.json()["detail"].startswith("Service misconfigured:")
    assert "SECRET-VALUE" not in response.text and FAKE_ANTHROPIC_KEY not in response.text
