# Design

## Context

What exists:

- `app/routers/estimations.py` (step 5) exports `router` with `POST /estimate`, plus `settings_dependency()`, which turns a configuration error into a 500.
- `app.config.get_settings()` (step 2) is cached and raises a Pydantic `ValidationError` on invalid configuration. `LOG_LEVEL` and `APP_ENV` exist but nothing uses them yet.
- `app/main.py` is the uv hello-world scaffold.
- FastAPI is 0.165. `pyproject.toml` holds the project version (`0.1.0`).
- The course only asks for the router under `/api/v1`, `GET /health`, and the title and description in Swagger.

## Goals / Non-Goals

**Goals:**

- `uv run uvicorn app.main:app --reload` serves the whole service: `POST /api/v1/estimate`, `GET /health`, `/docs`.
- A health endpoint that is useful for a quick check and for the step 8 pipeline, without spending money on an LLM call.
- Logs at the configured level, readable in the terminal next to uvicorn's own logs.
- The app starts even with a broken configuration, so `/health` and `/docs` can show what is wrong.

**Non-Goals:**

- CORS, authentication, middleware, metrics.
- A "deep" health check that calls the LLM: it would cost money and add latency to every check.
- Changing uvicorn's own logging (access logs keep uvicorn's format and level, controlled by uvicorn flags).
- Step 7's full verification checklist and step 8's CI.

## Decisions

- **App metadata:**
  - `title="Estimador de software (CAG)"`.
  - A Markdown `description`: what the service does, the CAG flow (transcription → static examples in the prompt → LLM → estimation in Spanish), and the supported providers.
  - `version="0.1.0"` from a module constant `APP_VERSION`. It is kept in sync with `pyproject.toml` by hand; reading the installed package metadata does not work, because the project has no build backend and is not installed.
  - Title and description in Spanish, because Swagger is what the teaching assistant and users read. Route summaries stay in English, like the rest of the code, as decided in step 5.
- **`app.include_router(estimations.router, prefix="/api/v1")`**, exactly as the course asks. The prefix is a constant `API_PREFIX`.
- **The health endpoint as a plain `def` in `main.py`, with a `HealthResponse` model:**
  - The handler calls `get_settings()` directly, not through `settings_dependency`. A configuration error must not turn `/health` into a 500: the process is alive, and the body reports `degraded` plus a safe description.
  - The description is built the same way as in step 5, from each error's location and message, which name variables and never values.
  - `environment` comes from the settings when they are valid. When they are not, it is `null`, because reading `APP_ENV` would need valid settings.
  - It always returns 200: `/health` is a liveness signal. The `status` field tells a monitor or the step 8 pipeline whether the configuration is usable, and the pipeline can assert `status == "ok"`.
  - Alternative: 503 when degraded. Rejected for now, because the course checklist expects `/health` to answer 200, and the pipeline needs to tell "server down" apart from "server up, misconfigured".
- **`GET /` redirects to `/docs`** (`RedirectResponse`, 307, `include_in_schema=False`). The scaffold's greeting goes away, and the base URL becomes useful without adding a documented endpoint.
- **Logging set up in a `lifespan` handler, not at import time:**
  - `logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s")`, with the root level left at WARNING, so third-party libraries stay quiet.
  - The `app` logger level is set from `settings.log_level`.
  - On a `ValidationError`, the handler sets INFO and logs an ERROR with the safe description. The app still starts.
  - Setting the level on the `app` logger only, not the root logger, keeps the SDKs' and httpx's debug output out even at `LOG_LEVEL=DEBUG`.
  - Doing it at startup instead of import means importing `app.main` in tests has no side effects.
  - `basicConfig` is a no-op when the root logger already has handlers (for example under pytest). Acceptable.
- **The safe description of a configuration error, shared:** step 5's router builds it inline in `settings_dependency`. Step 6 needs the same text twice more (health and startup log). To avoid three copies, a small `describe_config_error(e: ValidationError) -> str` function goes into `app/config.py`, next to the settings it describes. `settings_dependency` is updated to use it, and its output does not change.
- **Wording fix in `config.py`:** "LLM_MODEL={model} belongs to the {provider} provider, but LLM_PROVIDER={selected}; leave LLM_MODEL empty to use the provider's default model". It still names both variables, so the app-config requirement is unchanged.

## Risks / Trade-offs

- [`APP_VERSION` and `pyproject.toml` drift apart] → One constant, noted next to it. The step 8 pipeline can check that they match.
- [A health check that always returns 200 hides a broken configuration from naive monitors] → The `status` field is explicit, and the README tells monitors and CI to check it.
- [Logging configured in `lifespan` does not cover messages logged at import time] → Nothing in the app logs at import time.
- [The settings are cached: fixing `.env` needs a restart, and a failed load is retried on the next call because `lru_cache` doesn't cache exceptions] → Expected. `--reload` restarts on code changes only, not on `.env` changes. The README says to restart after editing `.env`.
