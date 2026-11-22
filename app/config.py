"""Application settings loaded from environment variables and the `.env` file.

Process environment variables take precedence over `.env`. Empty values count as
unset, so a fresh copy of `.env.example` falls back to the defaults. Run the app
from the repository root so `.env` is found.
"""

import re
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProvider = Literal["openai", "anthropic"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Economy model used for each provider when LLM_MODEL is not set.
DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5",
}

# Model-name patterns that clearly belong to each provider. An explicit LLM_MODEL that
# matches another provider's pattern is rejected; names matching none are accepted.
MODEL_PATTERNS: dict[str, str] = {
    "openai": r"^(gpt-|o\d)",
    "anthropic": r"^claude-",
}


class Settings(BaseSettings):
    """Typed service configuration. Field names map to upper-case env variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    llm_provider: LLMProvider = "anthropic"
    llm_model: str | None = None
    app_env: str = "development"
    log_level: LogLevel = "DEBUG"

    @model_validator(mode="after")
    def _check_provider(self) -> "Settings":
        """Require the selected provider's API key and resolve the default model."""
        key_var = f"{self.llm_provider.upper()}_API_KEY"
        if getattr(self, key_var.lower()) is None:
            raise ValueError(f"{key_var} is required when LLM_PROVIDER={self.llm_provider}")
        if self.llm_model:
            for provider, pattern in MODEL_PATTERNS.items():
                if provider != self.llm_provider and re.match(pattern, self.llm_model):
                    raise ValueError(
                        f"LLM_MODEL={self.llm_model} is a {provider} model but LLM_PROVIDER="
                        f"{self.llm_provider}; leave LLM_MODEL empty to use the provider's default model"
                    )
        if not self.llm_model:
            self.llm_model = DEFAULT_MODELS[self.llm_provider]
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the shared settings instance, built and validated on first call."""
    return Settings()
