# Proposal

## Why

Step 2 of the exercise: the service needs API keys and runtime options (provider, model, environment, log level), and they must come from the environment, never from code. Steps 4–6 (LLM service, endpoint, app) read these values, so configuration comes first.

## What Changes

- Implement `app/config.py` with a Pydantic `BaseSettings` class that loads six variables from the environment and from `.env`: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `APP_ENV` and `LOG_LEVEL`.
- Apply defaults: provider `anthropic`, model `claude-haiku-4-5` (follows the provider), environment `development`, log level `DEBUG`. API keys have no default. This differs from the course table on purpose: its defaults are `openai` and `gpt-4o-mini`, but only an Anthropic key is available for now. OpenAI, and possibly Gemini, will be added later.
- Check that the API key of the selected provider is present, and fail with a clear error if it is missing.
- Expose a single cached settings instance through `get_settings()`.
- Add `.env.example`, listing every variable with an empty value. It is committed.
- Create a local `.env` from it for the user's real keys. It is gitignored and never committed.
- Document the variables in README.md (Spanish) and mark step 2 done.

## Capabilities

### New Capabilities

- `app-config`: loading, defaults, validation and secrecy of the service configuration, plus the committed `.env.example` template.

### Modified Capabilities

<!-- none -->

## Impact

- `app/config.py`: the docstring placeholder is replaced by the implementation.
- New file `.env.example`, committed. New local file `.env`, ignored by the existing `.env` rule in `.gitignore`.
- No new dependencies: `pydantic-settings` and `python-dotenv` are already locked.
- No API changes yet. `main.py` and the services start using the settings in steps 4–6.
