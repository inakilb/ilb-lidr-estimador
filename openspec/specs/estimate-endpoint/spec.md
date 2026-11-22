# Spec

## Purpose

Defines the HTTP contract for estimations: the `POST /estimate` route (served at `/api/v1/estimate`), request validation, the response with the course fields plus usage, cost and timestamp, the mapping of service errors to HTTP status codes, and how settings are injected. The route stays thin: it delegates all business logic to the LLM service.

## Requirements

### Requirement: Estimation route

`app/routers/estimations.py` SHALL expose an `APIRouter` named `router` with a `POST /estimate` operation. When the router is included with the prefix `/api/v1`, the operation SHALL be served at `POST /api/v1/estimate`. The operation SHALL call the LLM service with the request's transcription and the injected settings, and return the result as JSON with status 200.

#### Scenario: Successful estimation

- **WHEN** a client sends `POST /api/v1/estimate` with `{"transcription": "<meeting text>"}`
- **THEN** the response is 200 with a JSON body containing the generated `estimation`, `model` and `provider`

### Requirement: Request schema

The request body SHALL be validated by `EstimationRequest`, with a single required field `transcription`:

- surrounding whitespace is trimmed;
- an empty or whitespace-only value is rejected;
- values longer than 50,000 characters are rejected;
- unknown fields are ignored.

The schema SHALL include an example transcription for the API documentation.

#### Scenario: Missing or empty transcription

- **WHEN** the body is `{}`, `{"transcription": ""}` or `{"transcription": "   "}`
- **THEN** the response is 422 and the LLM service is not called

#### Scenario: Transcription too long

- **WHEN** the transcription has more than 50,000 characters
- **THEN** the response is 422 and the LLM service is not called

#### Scenario: Whitespace trimmed

- **WHEN** the transcription has leading or trailing whitespace
- **THEN** the LLM service receives it trimmed

### Requirement: Response schema

A successful response SHALL match `EstimationResponse`:

- `estimation` (string): the Markdown estimation;
- `model` (string);
- `provider` (string);
- `usage` (object): `input_tokens`, `output_tokens`, `cache_read_input_tokens` and `cache_creation_input_tokens` (integers);
- `estimated_cost_usd` (number or null);
- `generated_at` (an ISO 8601 UTC timestamp).

#### Scenario: Course fields plus extras

- **WHEN** the LLM service returns a result
- **THEN** the response body contains `estimation`, `model` and `provider` with the result's values, the four token counts under `usage`, `estimated_cost_usd`, and a UTC `generated_at`

### Requirement: Error mapping

Service failures SHALL be returned as JSON errors with a `detail` message and these status codes:

- `UnsupportedProviderError` → 501;
- `LLMUpstreamError` with `retryable` true → 503, with a `Retry-After` header;
- `LLMUpstreamError` with `retryable` false → 502;
- `IncompleteEstimationError` → 502;
- invalid configuration when loading the settings → 500.

No `detail` message SHALL contain an API key.

#### Scenario: Provider temporarily unavailable

- **WHEN** the service raises `LLMUpstreamError` with `retryable` true
- **THEN** the response is 503 with a `Retry-After` header and the error's message in `detail`

#### Scenario: Provider failure that will not fix itself

- **WHEN** the service raises `LLMUpstreamError` with `retryable` false (for example, no credits or an invalid key)
- **THEN** the response is 502 with the error's message in `detail`

#### Scenario: Incomplete estimation

- **WHEN** the service raises `IncompleteEstimationError`
- **THEN** the response is 502

#### Scenario: Unsupported provider

- **WHEN** the service raises `UnsupportedProviderError`
- **THEN** the response is 501

#### Scenario: Invalid configuration

- **WHEN** loading the settings fails (for example, the selected provider's API key is missing)
- **THEN** the response is 500 with a `detail` that names the configuration problem without exposing any secret value

### Requirement: Injected settings

The operation SHALL obtain the settings through a FastAPI dependency based on `get_settings()`, so that tests can replace them with `app.dependency_overrides`.

#### Scenario: Settings overridden in tests

- **WHEN** a test overrides the settings dependency with custom settings
- **THEN** the LLM service is called with those settings
