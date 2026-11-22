# Proposal

## Why

Step 6 of the exercise: wire everything into the FastAPI application. The estimations router (step 5) exists but is not mounted, so `POST /api/v1/estimate` returns 404. `app/main.py` is still the hello-world scaffold. The course asks `main.py` to include the router with the prefix `/api/v1`, add `GET /health`, and set the API title and description for the Swagger documentation at `/docs`.

## What Changes

- **Replace the hello-world scaffold in `app/main.py`**, removing `GET /` and `GET /items/{item_id}`, with a configured `FastAPI` app:
  - title, description and version for Swagger at `/docs` (and ReDoc at `/redoc`);
  - the estimations router included with `prefix="/api/v1"`, so `POST /api/v1/estimate` is served;
  - `GET /health` returning the service status, version, environment and the configured LLM provider and model. It never calls the LLM and never exposes secrets. When the configuration is invalid it still answers 200, with `status: "degraded"` and the problem, so the process can be told apart from its configuration;
  - `GET /` redirecting to `/docs`, hidden from the schema, so opening the base URL lands on the documentation.
- **Configure logging from `LOG_LEVEL` at startup.** The app's own loggers (`app.*`) use the configured level and a readable format. If the configuration is invalid, the app still starts at INFO level and logs the problem, and requests answer as defined in step 5 (500 with the problem).
- **Fix the wording of the provider/model mismatch error in `app/config.py`:** "LLM_MODEL=claude-haiku-4-5 belongs to the anthropic provider, but LLM_PROVIDER=openai; …" replaces "is a anthropic model". The message is shown to API clients in step 5's 500 responses.
- README.md: "Puesta en marcha" and "Uso" mention `/docs`, `/health` and the root redirect; step 6 is marked done.

## Capabilities

### New Capabilities

- `fastapi-app`: the application object: API metadata, mounted routes and prefix, the health endpoint, the root redirect, and logging set up from the configuration.

### Modified Capabilities

<!-- none: the app-config requirement only asks the error to mention LLM_MODEL and LLM_PROVIDER, which the rewording keeps -->

## Impact

- `app/main.py`: rewritten. `app/config.py`: one message reworded.
- No new dependencies.
- The service is now reachable as the course describes: `uv run uvicorn app.main:app --reload`, then `curl` to `/api/v1/estimate`, and Swagger at `/docs`.
- Verification: offline tests on the real app with `TestClient`, a running server checked with `curl`, and one live estimation through it (about $0.005–0.013).
