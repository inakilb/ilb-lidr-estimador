"""Configuration loading, defaults, validation and secrecy (spec: app-config)."""

import json

import pytest
from pydantic import SecretStr, ValidationError

from app.config import Settings, describe_config_error, get_settings

KEY = "sk-ant-test-SECRET-123"
OTHER = "sk-proj-test-OTHER-456"


def load(monkeypatch, env=None, dotenv=None):
    """Build settings the way the app does: process env + .env in the working directory."""
    for name, value in (env or {}).items():
        monkeypatch.setenv(name, value)
    if dotenv is not None:
        with open(".env", "w") as f:
            f.write(dotenv)
    return Settings()


def test_values_read_from_dotenv(monkeypatch):
    s = load(monkeypatch, dotenv=f"LLM_PROVIDER=anthropic\nANTHROPIC_API_KEY={KEY}\n")
    assert s.llm_provider == "anthropic"
    assert s.anthropic_api_key.get_secret_value() == KEY


def test_environment_overrides_dotenv(monkeypatch):
    s = load(monkeypatch, env={"LOG_LEVEL": "INFO"}, dotenv=f"ANTHROPIC_API_KEY={KEY}\nLOG_LEVEL=DEBUG\n")
    assert s.log_level == "INFO"


def test_defaults_with_only_anthropic_key(monkeypatch):
    s = load(monkeypatch, env={"ANTHROPIC_API_KEY": KEY})
    assert (s.llm_provider, s.llm_model, s.app_env, s.log_level) == ("anthropic", "claude-haiku-4-5", "development", "DEBUG")


def test_copy_of_env_example_with_key_uses_defaults(monkeypatch, repo_root):
    template = (repo_root / ".env.example").read_text()
    s = load(monkeypatch, dotenv=template + f"\nANTHROPIC_API_KEY={KEY}\n")
    assert s.llm_provider == "anthropic" and s.llm_model == "claude-haiku-4-5"


def test_model_follows_provider(monkeypatch):
    s = load(monkeypatch, env={"LLM_PROVIDER": "openai", "OPENAI_API_KEY": OTHER})
    assert s.llm_model == "gpt-4o-mini"


def test_explicit_model_wins(monkeypatch):
    s = load(monkeypatch, env={"ANTHROPIC_API_KEY": KEY, "LLM_MODEL": "claude-sonnet-4-5"})
    assert s.llm_model == "claude-sonnet-4-5"


@pytest.mark.parametrize(
    ("env", "mentions"),
    [
        ({"LLM_PROVIDER": "gemini", "ANTHROPIC_API_KEY": KEY}, "llm_provider"),
        ({"LOG_LEVEL": "VERBOSE", "ANTHROPIC_API_KEY": KEY}, "log_level"),
        ({}, "ANTHROPIC_API_KEY"),
        ({"LLM_PROVIDER": "openai"}, "OPENAI_API_KEY"),
    ],
    ids=["unknown-provider", "invalid-log-level", "missing-anthropic-key", "missing-openai-key"],
)
def test_invalid_configuration_rejected(monkeypatch, env, mentions):
    with pytest.raises(ValidationError) as exc:
        load(monkeypatch, env=env)
    assert mentions.lower() in str(exc.value).lower()


def test_other_provider_key_not_required(monkeypatch):
    s = load(monkeypatch, env={"ANTHROPIC_API_KEY": KEY})
    assert s.openai_api_key is None


@pytest.mark.parametrize(
    ("provider", "model"),
    [("openai", "claude-haiku-4-5"), ("anthropic", "gpt-6-luna"), ("anthropic", "o3-mini")],
)
def test_model_from_other_provider_rejected(monkeypatch, provider, model):
    env = {"LLM_PROVIDER": provider, "LLM_MODEL": model, "ANTHROPIC_API_KEY": KEY, "OPENAI_API_KEY": OTHER}
    with pytest.raises(ValidationError) as exc:
        load(monkeypatch, env=env)
    assert "LLM_MODEL" in str(exc.value) and "LLM_PROVIDER" in str(exc.value)


def test_unrecognized_model_name_accepted(monkeypatch):
    s = load(monkeypatch, env={"LLM_PROVIDER": "openai", "OPENAI_API_KEY": OTHER, "LLM_MODEL": "my-custom-model"})
    assert s.llm_model == "my-custom-model"


def test_secrets_masked(monkeypatch):
    s = load(monkeypatch, env={"ANTHROPIC_API_KEY": KEY, "OPENAI_API_KEY": OTHER})
    dumped = str(s) + repr(s) + json.dumps(s.model_dump(mode="json"))
    assert KEY not in dumped and OTHER not in dumped


def test_describe_config_error_names_variables_not_values():
    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=None, llm_provider="anthropic", openai_api_key=SecretStr(OTHER))
    text = describe_config_error(exc.value)
    assert "ANTHROPIC_API_KEY" in text and OTHER not in text


def test_import_without_configuration(repo_root, tmp_path):
    # Fresh interpreter, empty folder (no .env), no config variables: importing must not fail.
    import os
    import subprocess
    import sys

    env = {k: v for k, v in os.environ.items() if k not in {"ANTHROPIC_API_KEY", "OPENAI_API_KEY", "LLM_PROVIDER", "LLM_MODEL"}}
    env["PYTHONPATH"] = str(repo_root)
    result = subprocess.run([sys.executable, "-c", "import app.config, app.main"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_get_settings_returns_same_instance(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", KEY)
    assert get_settings() is get_settings()
