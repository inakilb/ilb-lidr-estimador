# Tasks

## 1. Schemas

- [ ] 1.1 Replace the placeholder in `app/routers/estimations.py` with the module docstring, imports and `router = APIRouter(tags=["estimations"])`
- [ ] 1.2 Define `EstimationRequest`: `transcription` with `min_length=1` and `max_length=50_000`, a validator that trims and rejects whitespace-only input, and the course sample transcription as the example
- [ ] 1.3 Define `TokenUsage` and `EstimationResponse` (`estimation`, `model`, `provider`, `usage`, `estimated_cost_usd`, `generated_at`), with field descriptions for Swagger

## 2. Endpoint

- [ ] 2.1 Implement `settings_dependency()`: call `get_settings()`, and turn a `ValidationError` into a 500 with a safe message (field and message only)
- [ ] 2.2 Implement `POST /estimate` as a sync `def`: call `generate_estimation(request.transcription, settings)`, and build `EstimationResponse` with a UTC `generated_at`
- [ ] 2.3 Map errors: `UnsupportedProviderError` → 501, retryable `LLMUpstreamError` → 503 with `Retry-After: 30`, non-retryable `LLMUpstreamError` → 502, `IncompleteEstimationError` → 502, `ValueError` → 422. Log a WARNING per mapped error
- [ ] 2.4 Add `summary`, `description` and the `responses` documentation (422/500/501/502/503) to the route, for Swagger

## 3. Verification

- [ ] 3.1 Offline (scratchpad test app with `include_router(prefix="/api/v1")`, `TestClient`, fake service, overridden settings): 200 with the course fields plus extras, 422 for `{}`, `""`, `"   "` and over 50,000 characters without calling the service, whitespace trimmed, 501/503 (with `Retry-After`)/502/502 mapping, 500 on invalid configuration without secrets, settings override honored
- [ ] 3.2 Check the OpenAPI schema of the test app: `POST /api/v1/estimate` exists, the request example is present, and the documented responses include 422/500/501/502/503
- [ ] 3.3 Live: one request through the test app with the course sample transcription (default provider). Check 200, a Spanish estimation and the extra fields, and report the latency and cost
- [ ] 3.4 Confirm `uv run uvicorn app.main:app` still starts (`main.py` is unchanged)

## 4. Documentation

- [ ] 4.1 Update the README "Uso" section (Spanish): full response example with `usage`, `estimated_cost_usd` and `generated_at`, and a table of error codes
- [ ] 4.2 Mark step 5 as done in the README.md status table
