# Spec

## ADDED Requirements

### Requirement: Application and API documentation

`app/main.py` SHALL define the FastAPI application as `app`, with a title, a description of the service (CAG software estimator: transcription in, estimation out) and a version. The interactive documentation SHALL be served at `/docs` (Swagger UI), and the OpenAPI schema at `/openapi.json`.

#### Scenario: Swagger available

- **WHEN** a client requests `GET /docs`
- **THEN** the response is 200 and serves the Swagger UI

#### Scenario: API metadata

- **WHEN** a client requests `GET /openapi.json`
- **THEN** the schema contains the configured title, description and version

### Requirement: Estimations router mounted

The application SHALL include the estimations router with the prefix `/api/v1`, so that the estimation operation is served at `POST /api/v1/estimate`. The hello-world routes (`GET /items/{item_id}`) SHALL be removed.

#### Scenario: Estimate route reachable

- **WHEN** a client sends `POST /api/v1/estimate` with an empty body
- **THEN** the response is 422 from the request validation, not 404

#### Scenario: Scaffold routes removed

- **WHEN** a client requests `GET /items/1`
- **THEN** the response is 404

### Requirement: Health endpoint

The application SHALL expose `GET /health`, which answers 200 with a JSON body containing:

- `status`: `ok` when the configuration is valid, `degraded` when it is not;
- `version`;
- `environment`: the value of `APP_ENV`;
- `llm`: an object with `provider` and `model`, or `null` when the configuration is invalid;
- `detail`: only when degraded, a description of the configuration problem.

The endpoint SHALL NOT call the LLM and SHALL NOT include any API key.

#### Scenario: Healthy service

- **WHEN** the configuration is valid and a client requests `GET /health`
- **THEN** the response is 200 with `status` `ok`, the version, the environment, and the configured provider and model

#### Scenario: Invalid configuration

- **WHEN** the configuration is invalid (for example, the selected provider's API key is missing) and a client requests `GET /health`
- **THEN** the response is 200 with `status` `degraded`, `llm` `null`, and a `detail` that names the problem without exposing any secret value

#### Scenario: No LLM call

- **WHEN** `GET /health` is requested
- **THEN** no request is sent to any LLM provider

### Requirement: Root redirect

`GET /` SHALL redirect to `/docs` and SHALL NOT appear in the OpenAPI schema.

#### Scenario: Base URL opens the documentation

- **WHEN** a client requests `GET /` without following redirects
- **THEN** the response is a redirect whose `Location` is `/docs`

### Requirement: Logging from configuration

At startup the application SHALL set the level of the `app` loggers to `LOG_LEVEL`, using a format that includes time, level and logger name. If the configuration is invalid, the application SHALL still start, use INFO level, and log the configuration problem.

#### Scenario: Configured level applied

- **WHEN** the application starts with `LOG_LEVEL=WARNING`
- **THEN** the `app` logger's effective level is WARNING

#### Scenario: Startup with invalid configuration

- **WHEN** the application starts and the configuration is invalid
- **THEN** startup succeeds, the `app` logger uses INFO level, and the problem is logged
