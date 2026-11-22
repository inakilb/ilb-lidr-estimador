"""FastAPI application: docs, mounted router, health, root redirect, logging (spec: fastapi-app)."""

import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

import app.main as main
from app.config import Settings
from helpers import make_settings

SECRET = "sk-proj-SECRET-VALUE-99"


def broken_settings():
    return Settings(_env_file=None, llm_provider="anthropic", openai_api_key=SecretStr(SECRET))


@pytest.fixture
def no_llm(monkeypatch):
    """Fail the test if anything tries to reach an LLM provider."""
    import app.services.llm_service as svc

    def forbidden(*args, **kwargs):
        raise AssertionError("an LLM client was created")

    monkeypatch.setattr(svc, "_anthropic_client", forbidden)
    monkeypatch.setattr(svc, "_openai_client", forbidden)


def test_swagger_and_openapi_metadata(api_client):
    assert api_client.get("/docs").status_code == 200
    spec = api_client.get("/openapi.json").json()
    assert spec["info"]["title"] == "Estimador de software (CAG)"
    assert spec["info"]["version"] == main.APP_VERSION == "0.1.0"
    assert "CAG" in spec["info"]["description"]
    assert sorted(spec["paths"]) == ["/api/v1/estimate", "/health"]


def test_estimate_route_mounted_under_api_v1(api_client):
    assert api_client.post("/api/v1/estimate", json={}).status_code == 422


def test_scaffold_routes_removed(api_client):
    assert api_client.get("/items/1").status_code == 404


def test_root_redirects_to_docs(api_client):
    response = api_client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307) and response.headers["location"] == "/docs"


def test_health_ok(monkeypatch, no_llm):
    monkeypatch.setattr(main, "get_settings", lambda: make_settings(app_env="testing"))
    with TestClient(main.app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "0.1.0",
        "environment": "testing",
        "llm": {"provider": "anthropic", "model": "claude-haiku-4-5"},
    }


def test_health_degraded_with_invalid_configuration(monkeypatch, no_llm):
    monkeypatch.setattr(main, "get_settings", broken_settings)
    with TestClient(main.app) as client:
        response = client.get("/health")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "degraded" and body["llm"] is None and body["environment"] is None
    assert "ANTHROPIC_API_KEY" in body["detail"] and SECRET not in response.text


def test_log_level_from_configuration(monkeypatch):
    monkeypatch.setattr(main, "get_settings", lambda: make_settings(log_level="WARNING"))
    with TestClient(main.app):
        assert logging.getLogger("app").getEffectiveLevel() == logging.WARNING


def test_startup_with_invalid_configuration_falls_back_to_info(monkeypatch, caplog):
    monkeypatch.setattr(main, "get_settings", broken_settings)
    logging.getLogger("app").setLevel(logging.NOTSET)
    with caplog.at_level(logging.INFO, logger="app"), TestClient(main.app) as client:
        assert client.get("/health").status_code == 200
        assert logging.getLogger("app").level == logging.INFO
    errors = [r for r in caplog.records if r.levelno == logging.ERROR and r.name == "app"]
    assert errors and "ANTHROPIC_API_KEY" in errors[0].getMessage() and SECRET not in errors[0].getMessage()
