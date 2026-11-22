# Design

## Context

`app.services.llm_service.generate_estimation(transcription, settings)` (step 4) returns an `EstimationResult` dataclass or raises a subclass of `LLMServiceError`:

- `UnsupportedProviderError`;
- `LLMUpstreamError`, with `retryable` and `status_code`;
- `IncompleteEstimationError`.

It also raises `ValueError` for empty input. `get_settings()` (step 2) is cached and raises a Pydantic `ValidationError` when the configuration is invalid. `app/main.py` is still the hello-world scaffold. Step 6 adds the router, `GET /health` and the Swagger metadata. FastAPI is 0.165 with Pydantic 2.14, and `TestClient` works on the installed `httpx2`.

## Goals / Non-Goals

**Goals:**

- The course contract: `POST /api/v1/estimate`, request `{transcription}`, response `{estimation, model, provider}`.
- Useful extra fields (token usage, cost, timestamp) that cost nothing, since the service already returns them.
- HTTP status codes that tell a client whether to retry, fix its request, or report a server problem.
- Testable without network calls or real keys.

**Non-Goals:**

- Mounting the router in `app/main.py`, `GET /health`, and API title and description: step 6.
- Authentication, rate limiting and CORS: not requested by the course.
- Streaming the estimation, async endpoints and background jobs.
- Automated tests in the repository and CI: step 8. This change verifies with scratchpad scripts.

## Decisions

- **The router declares `POST /estimate`, and the app adds `/api/v1`.** This is the course's layout ("incluye el router de estimaciones con el prefijo /api/v1"). The router stays reusable, and versioning is decided in one place.
- **A synchronous `def` endpoint.** The service and SDK clients are synchronous. FastAPI runs `def` endpoints in its thread pool, so a call that takes 5–10 s does not block the event loop. Alternative: `async def` with the async SDK clients. More code for no gain at course scale.
- **Request validation in Pydantic, not in the endpoint:**
  - `transcription: str` with `min_length=1` and `max_length=50_000`.
  - A `field_validator` strips whitespace, then rejects an empty result.
  - Rejected input returns FastAPI's standard 422 before the service is touched.
  - 50,000 characters is about 12k tokens. That covers a long meeting transcription and caps the cost of a single request, given Haiku 4.5's 200K-token context.
  - Unknown fields are ignored (Pydantic's default), so clients can send extra metadata.
- **Response: the course fields at the top level, extras grouped.**
  - `estimation`, `model` and `provider` stay at the top level, exactly as in the course example.
  - Token counts are grouped under `usage` (`TokenUsage` model), plus `estimated_cost_usd` and `generated_at` (`datetime`, timezone-aware UTC).
  - The response models are defined in the router module, because they are part of the HTTP contract. The service keeps its own dataclass, so the HTTP layer and the service stay independent.
  - `EstimationResponse.from_result(result)` builds the response from the dataclass explicitly, without `from_attributes` tricks, and stamps `generated_at`.
- **A thin route: receive, delegate, return.** The route body is a single `generate_estimation(...)` call. A service error is translated by `_to_http_exception()`, and the result by `EstimationResponse.from_result()`. All business logic (prompt, LLM call, caching, cost, error classification) stays in `app/services/llm_service.py`. The router only translates between HTTP and the service, which is the job the course gives `routers/`.
- **Error mapping in one helper, `_to_http_exception(error) -> HTTPException`:**

  | Exception                           | Status                                      | Why                                                                                              |
  | ----------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------ |
  | `UnsupportedProviderError`          | 501 Not Implemented                         | The server cannot do this yet.                                                                   |
  | `LLMUpstreamError(retryable=True)`  | 503 Service Unavailable + `Retry-After: 30` | Temporary; the client can retry.                                                                 |
  | `LLMUpstreamError(retryable=False)` | 502 Bad Gateway                             | The upstream provider failed, and retrying will not help (bad key, no credits, model not found). |
  | `IncompleteEstimationError`         | 502 Bad Gateway                             | The upstream returned something unusable.                                                        |

  ***
  - `detail` carries the service error's message. Those messages were designed in step 4 to be safe: status code and request ID, never the key.
  - The route catches only the base class `LLMServiceError`, and the helper picks the status. A single `try/except` keeps the route readable without app-level exception handlers. Those could replace the helper in `main.py` if more routes appear.
  - No `ValueError` branch: the request schema already rejects empty input before the route runs.

- **A settings dependency that turns configuration errors into 500:**
  - `def settings_dependency() -> Settings` calls `get_settings()`. It catches `pydantic.ValidationError` and raises `HTTPException(500, "Service misconfigured: <field>: <message>")`, built from each error's location and message only.
  - The configuration errors are written in step 2: a missing key, a model belonging to the other provider, an invalid provider. They name variables, never values, so they are safe to return.
  - A missing key is a server problem, not the client's, which is why it is a 500.
  - Tests override this dependency.
- **Logging:** a WARNING per mapped error, in `_to_http_exception`. The service already logs the request size (DEBUG) and the usage and cost (INFO), so the route adds no logging of its own.
- **Verification without touching `main.py`:**
  - A scratchpad test app does `FastAPI(); app.include_router(router, prefix="/api/v1")`, driven with `TestClient`.
  - The service function is replaced through `monkeypatch`-style assignment on the router module, and the settings through `dependency_overrides`.
  - One live request goes through the same test app, to confirm the real path end to end.

## Risks / Trade-offs

- [5–10 s latency per request ties up a thread-pool worker] → Acceptable for a course service. The thread pool has 40 workers by default. Async or streaming can come later.
- [`Retry-After: 30` is a guess] → The SDK has already retried before the error reaches the router. 30 s is a conservative hint, not a contract.
- [The 50,000-character limit could reject a very long real transcription] → The 422 message states the limit. The limit is one constant, easy to raise.
- [The timestamp makes responses non-deterministic] → Only `generated_at` varies. Tests check its format, not its value.
