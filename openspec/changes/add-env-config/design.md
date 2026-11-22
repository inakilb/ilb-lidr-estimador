# Design

## Context

`app/config.py` is a docstring placeholder from step 1. `.env` is already gitignored. `pydantic-settings` 2.16 and `python-dotenv` are locked. The course gives six variables with defaults. This project changes one of them: the default provider is `anthropic`, because the user only has an Anthropic API key for now. OpenAI, and possibly Gemini, will be added later. Their consumers arrive later: `llm_service` (step 4) needs the provider, model and keys, and `main.py` (step 6) needs `APP_ENV` and `LOG_LEVEL`. The step 8 CI pipeline will import and boot the app, so the config must not break imports when no secrets are present.

## Goals / Non-Goals

**Goals:**

- One typed source of configuration, loaded from the environment and `.env`, with the course defaults.
- Fail fast, with a clear message, on invalid values or a missing key for the selected provider.
- Keep secrets out of code, logs and the repository.

**Non-Goals:**

- Configuring Python logging from `LOG_LEVEL`: step 6 wires it into the app.
- Choosing which providers `llm_service` implements: step 4.
- Per-environment behavior based on `APP_ENV`: it is only exposed for now.

## Decisions

- **`pydantic-settings` `BaseSettings` with `SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True)`.** This is what the course requires. `extra="ignore"` tolerates unrelated variables in `.env`. `env_ignore_empty=True` matters because `.env.example` (and a fresh copy of it) has empty values. Without it, `LLM_PROVIDER=` would be read as an empty string and fail validation instead of falling back to `anthropic`. Field names in snake_case map to the upper-case variables because matching is case-insensitive (the default).
- **`.env` path relative to the working directory.** CLAUDE.md requires running commands from the repo root. Alternative: resolve the path from `__file__`. More robust, but it also hides a wrong working directory. Kept simple and documented.
- **`Literal` types for `llm_provider` (`openai` | `anthropic`) and `log_level` (`DEBUG` … `CRITICAL`).** Pydantic rejects invalid values with an error that names the field, and no custom code is needed. Adding Gemini later means extending the `Literal`, adding a `GEMINI_API_KEY` field and a model default. `app_env` stays a free `str`, because the course gives no closed list.
- **API keys as `SecretStr | None = None`.** `SecretStr` masks the value in `str`, `repr` and `model_dump`. Callers use `.get_secret_value()` only at the SDK boundary (step 4). Alternative: plain `str`. Rejected, because one stray `print(settings)` would leak the key.
- **`model_validator(mode="after")` for provider-dependent rules.**
  - It requires the selected provider's key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) and raises `ValueError` naming the variable.
  - It fills `llm_model` when it is empty: `gpt-4o-mini` for openai, `claude-haiku-4-5` for anthropic. For the default provider this gives `claude-haiku-4-5`, the course's economy Anthropic model, and with `LLM_PROVIDER=openai` it gives the course default `gpt-4o-mini`. It also avoids a broken combination such as `openai` + `claude-haiku-4-5` when a user switches only `LLM_PROVIDER`.
  - Alternative: a static model default. Rejected for that mismatch.
  - Implementation: `llm_model: str | None = None`, resolved in the validator so it is always a `str` afterwards.
- **`get_settings()` decorated with `functools.lru_cache`, and no module-level instance.** This is the FastAPI-recommended pattern. Importing `app.config` stays side-effect free, so structure and import checks (CI, step 1 spec) pass without secrets. The single instance is shared, and step 5 can use it as a FastAPI dependency (`Depends(get_settings)`), which tests can override. Alternative: `settings = Settings()` at module level. Rejected, because it validates at import and would crash any import of the app when the key is missing.
- **`.env.example` with empty values, grouped and commented.** The course says "sin valores". Comments state each default, so the template documents itself.
- **Local `.env` created by copying `.env.example`.** The user fills in their real key. Claude never writes a key value.

## Risks / Trade-offs

- [The default provider differs from the course table (`openai`)] → It is a deliberate deviation, recorded in the proposal and README. Setting `LLM_PROVIDER=openai` restores the course behavior.
- [Fail-fast key check makes the app unusable without a key] → Intended for the selected provider only, and the error names the missing variable. CI (step 8) will supply a dummy key through the environment.
- [`lru_cache` keeps stale settings if the environment changes at runtime] → Settings are static for the life of the process. Tests can call `get_settings.cache_clear()`.
- [Running from a directory other than the repo root ignores `.env`] → Documented in README and CLAUDE.md. The process environment still works.
