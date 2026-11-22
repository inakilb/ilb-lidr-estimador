# Tasks

## 1. Schemas

- [x] 1.1 Replace the placeholder in `app/routers/estimations.py` with the module docstring, imports and `router = APIRouter(tags=["estimations"])`
- [x] 1.2 Define `EstimationRequest`: `transcription` with `min_length=1` and `max_length=50_000`, a validator that trims and rejects whitespace-only input, and the course sample transcription as the example
- [x] 1.3 Define `TokenUsage` and `EstimationResponse` (`estimation`, `model`, `provider`, `usage`, `estimated_cost_usd`, `generated_at`), with field descriptions for Swagger

## 2. Endpoint

- [x] 2.1 Implement `settings_dependency()`: call `get_settings()`, and turn a `ValidationError` into a 500 with a safe message (field and message only)
- [x] 2.2 Implement `POST /estimate` as a sync, thin `def`: call `generate_estimation(request.transcription, settings)` and return `EstimationResponse.from_result(result)`, which stamps a UTC `generated_at`
- [x] 2.3 Map errors in one helper, `_to_http_exception()`: `UnsupportedProviderError` → 501, retryable `LLMUpstreamError` → 503 with `Retry-After: 30`, non-retryable `LLMUpstreamError` and `IncompleteEstimationError` → 502. Log a WARNING per mapped error
- [x] 2.4 Add `summary`, `description` and the `responses` documentation (422/500/501/502/503) to the route, for Swagger

## 3. Verification

- [x] 3.1 Offline (scratchpad test app with `include_router(prefix="/api/v1")`, `TestClient`, fake service, overridden settings): 200 with the course fields plus extras, 422 for `{}`, `""`, `"   "` and over 50,000 characters without calling the service, whitespace trimmed, 501/503 (with `Retry-After`)/502/502 mapping, 500 on invalid configuration without secrets, settings override honored
- [x] 3.2 Check the OpenAPI schema of the test app: `POST /api/v1/estimate` exists, the request example is present, and the documented responses include 422/500/501/502/503
- [x] 3.3 Live: one request through the test app with the course sample transcription (default provider). Check 200, a Spanish estimation and the extra fields, and report the latency and cost
- [x] 3.4 Confirm `uv run uvicorn app.main:app` still starts (`main.py` is unchanged)

## 4. Documentation

- [x] 4.1 Update the README "Uso" section (Spanish): full response example with `usage`, `estimated_cost_usd` and `generated_at`, and a table of error codes
- [x] 4.2 Mark step 5 as done in the README.md status table
