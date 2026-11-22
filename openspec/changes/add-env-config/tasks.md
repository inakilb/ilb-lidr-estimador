# Tasks

## 1. Settings module

- [ ] 1.1 Replace the placeholder in `app/config.py` with a `Settings(BaseSettings)` class: `model_config` with `env_file=".env"`, `extra="ignore"`, `env_ignore_empty=True`
- [ ] 1.2 Add fields `openai_api_key` / `anthropic_api_key` (`SecretStr | None = None`), `llm_provider` (`Literal["openai", "anthropic"] = "anthropic"`), `llm_model` (`str | None = None`), `app_env` (`str = "development"`), `log_level` (`Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"`)
- [ ] 1.3 Add an after-model validator that requires the selected provider's API key (error names the variable) and fills `llm_model` with the provider default when empty
- [ ] 1.4 Add `get_settings()` with `functools.lru_cache`, and no module-level instance

## 2. Environment files

- [ ] 2.1 Create `.env.example` with all six variables, empty values, and comments stating each default
- [ ] 2.2 Create the local `.env` by copying `.env.example`, without writing any key value. Confirm `git check-ignore .env` reports it as ignored
- [ ] 2.3 Ask the user to fill in their real API key in `.env`

## 3. Documentation

- [ ] 3.1 Add a "Configuración" section to README.md (Spanish): variable table with description and default, noting that Anthropic is the default provider for now. Update the Stack line and the sample response (`claude-haiku-4-5` / `anthropic`) to match
- [ ] 3.2 Mark step 2 as done in the README.md status table

## 4. Verification

- [ ] 4.1 With `uv run python` and temporary environments (no real keys), check every spec scenario: defaults, empty values, env precedence, model per provider, explicit model, invalid provider, missing key, other key not required, masked secrets, import without config, same instance
- [ ] 4.2 Search tracked files for key-like values (`sk-`) and confirm none are present
- [ ] 4.3 Confirm `uv run uvicorn app.main:app` still starts
