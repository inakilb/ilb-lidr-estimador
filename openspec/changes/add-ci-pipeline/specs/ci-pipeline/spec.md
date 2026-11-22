# Spec

## ADDED Requirements

### Requirement: Offline test suite

The repository SHALL contain a `tests/` suite, runnable with `uv run pytest` from the repository root, that checks the behavior defined in the main specs (`project-structure`, `app-config`, `estimation-examples`, `llm-estimation-service`, `estimate-endpoint`, `fastapi-app`) and the sample transcriptions. The suite SHALL make no network calls to LLM providers and SHALL need no real API keys. It SHALL NOT read the developer's `.env` file.

#### Scenario: Suite passes without secrets

- **WHEN** `uv run pytest` runs in an environment with no `.env` and no API keys
- **THEN** all tests pass and no request is sent to any LLM provider

#### Scenario: Local .env ignored

- **WHEN** the developer's `.env` sets values such as `LLM_PROVIDER` or `LLM_MODEL`
- **THEN** the test results are the same as without it

### Requirement: Folder structure validated

The test suite SHALL fail when any path of the course layout is missing:

- `app/__init__.py`, `app/main.py`, `app/config.py`;
- `app/routers/__init__.py`, `app/routers/estimations.py`;
- `app/services/__init__.py`, `app/services/llm_service.py`;
- `app/context/__init__.py`, `app/context/examples.py`;
- `.env.example`, `.gitignore`, `pyproject.toml`, `README.md`.

It SHALL also fail when `.env` is not ignored by git, or when `.env.example` contains a non-empty value. Additional files and folders SHALL NOT make it fail.

#### Scenario: Missing required file

- **WHEN** a required path such as `app/services/llm_service.py` does not exist
- **THEN** the structure test fails and names the missing path

#### Scenario: Extra folders allowed

- **WHEN** the repository contains extra folders such as `transcripciones/` or `openspec/`
- **THEN** the structure test passes

### Requirement: Continuous integration workflow

The repository SHALL contain a GitHub Actions workflow, `.github/workflows/ci.yml`, triggered on pushes and pull requests. On a Linux runner it SHALL:

1. install the locked dependencies with uv (`uv sync --locked`), using Python 3.11;
2. check that `requirements.txt` matches the export of `uv.lock`;
3. run the test suite;
4. run a smoke test against the real application started with `uvicorn`.

Any failing step SHALL fail the workflow.

#### Scenario: Lock and requirements out of sync

- **WHEN** `requirements.txt` differs from `uv export --no-hashes --no-emit-project --no-dev --format requirements-txt`
- **THEN** the workflow fails at that step

#### Scenario: Failing test

- **WHEN** any test fails
- **THEN** the workflow fails

### Requirement: Smoke test of the running service

The workflow SHALL start the application with `uvicorn app.main:app`, using dummy API keys supplied through environment variables, and SHALL check:

- `GET /health` returns 200 with `status` `ok`;
- `GET /docs` returns 200;
- `POST /api/v1/estimate` with `transcripciones/vacia.json` returns 422.

These checks SHALL make no LLM call. The server SHALL be stopped at the end of the job.

#### Scenario: Service starts and answers

- **WHEN** the smoke-test step runs
- **THEN** `/health` reports `ok`, `/docs` answers 200, and the empty transcription is rejected with 422

### Requirement: Optional live check

The workflow SHALL offer a live check that runs only when started manually with the `live` input enabled. It SHALL use the `ANTHROPIC_API_KEY` repository secret, send `transcripciones/curso-landing.json` to the running service, and require a 200 response with a non-empty `estimation`. It SHALL NOT run on pushes or pull requests.

#### Scenario: Not run automatically

- **WHEN** the workflow is triggered by a push or a pull request
- **THEN** the live check is skipped

#### Scenario: Manual live run

- **WHEN** the workflow is dispatched manually with `live` enabled and the secret configured
- **THEN** the live check gets a 200 response with a non-empty estimation from the real provider
