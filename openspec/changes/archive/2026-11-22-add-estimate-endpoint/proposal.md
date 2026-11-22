# Proposal

## Why

Step 5 of the exercise: the LLM service (step 4) has to be reachable over HTTP, so that a client (curl, Postman, Swagger UI) can send a meeting transcription and receive the estimation as JSON. The course asks for `POST /api/v1/estimate` in `app/routers/estimations.py`, with Pydantic request and response schemas. Extra response fields (tokens, cost, timestamp) are allowed.

## What Changes

- **Implement `app/routers/estimations.py`** with an `APIRouter` and `POST /estimate`. The `/api/v1` prefix is applied when the router is included in the app (step 6), giving `POST /api/v1/estimate`.
- **Request schema `EstimationRequest`:** `transcription`, a non-empty string after trimming whitespace, at most 50,000 characters. It includes the course's sample transcription as the Swagger example.
- **Response schema `EstimationResponse`:**
  - the course fields `estimation`, `model` and `provider`;
  - `usage`: input, output, cache read and cache write tokens;
  - `estimated_cost_usd`;
  - `generated_at`: a UTC timestamp.
- **HTTP errors, each with a JSON `detail` message that never contains secrets:**

  | Case                                                                      | Status                  |
  | ------------------------------------------------------------------------- | ----------------------- |
  | Invalid request body                                                      | 422                     |
  | Provider not implemented                                                  | 501                     |
  | Retryable provider failure (rate limit, overload, timeout)                | 503, with `Retry-After` |
  | Non-retryable provider failure (invalid key, no credits, model not found) | 502                     |
  | Incomplete estimation (truncated, refused, empty)                         | 502                     |
  | Invalid configuration (for example, a missing API key)                    | 500                     |

- **Settings injected with FastAPI's `Depends`**, so tests can override them.
- `app/main.py` is **not** changed. Including the router, `GET /health` and the Swagger metadata are step 6. This change is verified with a test app that includes the router.
- README.md: the "Uso" section shows the full response with the extra fields and the error codes; step 5 is marked done.

## Capabilities

### New Capabilities

- `estimate-endpoint`: the HTTP contract for estimations: route, request and response schemas, error mapping, and how settings are injected.

### Modified Capabilities

<!-- none -->

## Impact

- `app/routers/estimations.py`: the placeholder is replaced by the router.
- No new dependencies: FastAPI's `TestClient` works with the already-installed `httpx2`.
- Verification: offline tests through a test app with a fake service, plus one live request through the router (about $0.005–0.013).
