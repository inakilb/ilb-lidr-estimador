"""Shared fixtures: test isolation, fake LLM clients and an HTTP client on the real app.

Every test runs offline: no `.env` is read, no configuration variables leak in from the
environment, and the LLM SDK clients are replaced by fakes that record their calls.
"""

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

import app.config as config
import app.services.llm_service as llm_service
from helpers import REPO_ROOT, FakeLLMClient, anthropic_response, make_settings, openai_response

CONFIG_VARS = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LLM_PROVIDER", "LLM_MODEL", "APP_ENV", "LOG_LEVEL")


@pytest.fixture(autouse=True)
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Run each test with no config env vars, in an empty folder (no .env), with fresh caches."""
    for var in CONFIG_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(tmp_path)
    config.get_settings.cache_clear()
    llm_service.build_system_prompt.cache_clear()
    yield
    config.get_settings.cache_clear()
    llm_service.build_system_prompt.cache_clear()


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def fake_anthropic(monkeypatch: pytest.MonkeyPatch):
    """Install a fake Anthropic client; call `fake_anthropic(result)` to set what it returns."""

    def install(result: Any = None) -> FakeLLMClient:
        client = FakeLLMClient(anthropic_response() if result is None else result)
        monkeypatch.setattr(llm_service, "_anthropic_client", lambda api_key: client)
        return client

    return install


@pytest.fixture
def fake_openai(monkeypatch: pytest.MonkeyPatch):
    """Install a fake OpenAI client; call `fake_openai(result)` to set what it returns."""

    def install(result: Any = None) -> FakeLLMClient:
        client = FakeLLMClient(openai_response() if result is None else result)
        monkeypatch.setattr(llm_service, "_openai_client", lambda api_key: client)
        return client

    return install


# --------------------------------------------------------------------------- HTTP client


@pytest.fixture
def api_client():
    """TestClient on the real app, with settings overridden to fake-key settings."""
    from app.main import app
    from app.routers.estimations import settings_dependency

    settings = make_settings()
    app.dependency_overrides[settings_dependency] = lambda: settings
    with TestClient(app) as client:
        client.settings = settings  # type: ignore[attr-defined]
        yield client
    app.dependency_overrides.clear()
