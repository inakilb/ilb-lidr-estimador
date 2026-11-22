"""Plain test helpers (no fixtures): settings builders, fake responses, fake clients, SDK errors."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx2
from pydantic import SecretStr

from app.config import Settings

REPO_ROOT = Path(__file__).resolve().parent.parent

FAKE_ANTHROPIC_KEY = "sk-ant-test-FAKE-KEY-0001"
FAKE_OPENAI_KEY = "sk-proj-test-FAKE-KEY-0002"


def make_settings(**overrides: Any) -> Settings:
    """Settings that never read .env; Anthropic with a fake key unless overridden."""
    values: dict[str, Any] = {"anthropic_api_key": SecretStr(FAKE_ANTHROPIC_KEY)}
    values.update(overrides)
    return Settings(_env_file=None, **values)


def make_openai_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {"llm_provider": "openai", "openai_api_key": SecretStr(FAKE_OPENAI_KEY)}
    values.update(overrides)
    return make_settings(**values)


# --------------------------------------------------------------------------- fake responses


def anthropic_response(
    text: str = "## Estimación: Test\n\n### Desglose de tareas\n...",
    *,
    stop_reason: str = "end_turn",
    blocks: list | None = None,
    stop_details: Any = None,
    input_tokens: int = 300,
    output_tokens: int = 1500,
    cache_read: int = 6400,
    cache_write: int = 0,
) -> SimpleNamespace:
    content = blocks if blocks is not None else [SimpleNamespace(type="text", text=text)]
    usage = SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_input_tokens=cache_read,
        cache_creation_input_tokens=cache_write,
    )
    return SimpleNamespace(
        content=content, stop_reason=stop_reason, stop_details=stop_details, usage=usage, model="snapshot", _request_id="req_test"
    )


def openai_response(
    content: str | None = "## Estimación: Test\n...",
    *,
    finish_reason: str = "stop",
    refusal: str | None = None,
    prompt_tokens: int = 6800,
    cached: int = 6656,
    cache_write: int | None = None,
    completion_tokens: int = 900,
) -> SimpleNamespace:
    details = SimpleNamespace(cached_tokens=cached, cache_write_tokens=cache_write)
    usage = SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, prompt_tokens_details=details)
    message = SimpleNamespace(content=content, refusal=refusal)
    choice = SimpleNamespace(finish_reason=finish_reason, message=message)
    return SimpleNamespace(choices=[choice], usage=usage, id="chatcmpl_test", model="gpt-snapshot")


# --------------------------------------------------------------------------- fake clients


class FakeLLMClient:
    """Records `create(**kwargs)` calls; returns `result` or raises it if it is an exception.

    Exposes both `client.messages.create` (Anthropic) and `client.chat.completions.create` (OpenAI).
    """

    def __init__(self, result: Any):
        self.result = result
        self.calls: list[dict[str, Any]] = []
        self.messages = self
        self.chat = self
        self.completions = self

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


# --------------------------------------------------------------------------- SDK errors


def status_error(sdk_error_cls: type, status_code: int, *, message: str = "boom", body: Any = None, url: str = "https://api.test/v1"):
    """Build an SDK APIStatusError subclass instance (anthropic or openai) for a given status."""
    request = httpx2.Request("POST", url)
    response = httpx2.Response(status_code, request=request, headers={"request-id": "req_x", "x-request-id": "req_x"})
    return sdk_error_cls(message, response=response, body=body)


def timeout_error(sdk: Any):
    return sdk.APITimeoutError(request=httpx2.Request("POST", "https://api.test/v1"))


def connection_error(sdk: Any):
    return sdk.APIConnectionError(request=httpx2.Request("POST", "https://api.test/v1"))
