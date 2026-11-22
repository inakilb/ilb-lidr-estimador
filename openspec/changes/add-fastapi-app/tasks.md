# Tasks

## 1. Config helpers

- [ ] 1.1 Add `describe_config_error(e: ValidationError) -> str` to `app/config.py` (field location plus message, never values)
- [ ] 1.2 Reword the provider/model mismatch error: "... belongs to the {provider} provider, but LLM_PROVIDER=...; leave LLM_MODEL empty ..."
- [ ] 1.3 Use `describe_config_error` in `settings_dependency` (`app/routers/estimations.py`), with the same output

## 2. Application

- [ ] 2.1 Rewrite `app/main.py`: module docstring, `APP_VERSION`, `API_PREFIX`, `FastAPI(title, description, version, lifespan)`; remove the hello-world routes
- [ ] 2.2 Implement the `lifespan` logging setup: `basicConfig` format, `app` logger level from `LOG_LEVEL`, INFO plus an ERROR log on invalid configuration
- [ ] 2.3 Include the estimations router with `prefix=API_PREFIX`
- [ ] 2.4 Implement `GET /health` with a `HealthResponse` model: `ok` with provider, model and environment, or `degraded` with `llm: null` and a safe `detail`; always 200, no LLM call
- [ ] 2.5 Add `GET /` redirecting to `/docs`, hidden from the schema

## 3. Verification

- [ ] 3.1 Offline (`TestClient` on the real `app`, fake service, overridden settings): `/docs` 200, OpenAPI title, description and version, `POST /api/v1/estimate` mounted (422 on an empty body, 200 with the fake service), `/items/1` 404, `/` redirects to `/docs`, `/health` ok and degraded (no secrets, no LLM call), log level applied and fallback on invalid configuration
- [ ] 3.2 Re-run the step 5 endpoint checks and the config checks (step 2 and refine-llm-models), including the new mismatch wording
- [ ] 3.3 Running server: `uv run uvicorn app.main:app`, then `curl` `/health`, `/docs` and `/` (redirect). Stop the server
- [ ] 3.4 Live: one `curl` `POST /api/v1/estimate` with the course sample transcription against the running server. Check 200 and the Spanish estimation, and report the latency and cost

## 4. Documentation

- [ ] 4.1 README (Spanish): in "Puesta en marcha", Swagger at `/docs`, `GET /health` (with an example response and the `status` field), `/` → `/docs`, and restarting after editing `.env`
- [ ] 4.2 Mark step 6 as done in the README.md status table
