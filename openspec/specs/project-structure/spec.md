# Spec

## Purpose

Defines the required repository layout, package files, dependency set and startup contract of the CAG estimator service. The course reviewers check this layout, and every later capability builds on it.

## Requirements

### Requirement: Required package layout

The repository SHALL contain the application packages and modules at these exact paths: `app/__init__.py`, `app/main.py`, `app/config.py`, `app/routers/__init__.py`, `app/routers/estimations.py`, `app/services/__init__.py`, `app/services/llm_service.py`, `app/context/__init__.py` and `app/context/examples.py`.

#### Scenario: All required files exist

- **WHEN** the repository tree is listed from the root
- **THEN** every path above exists as a regular file

#### Scenario: Every package is importable

- **WHEN** `app.config`, `app.routers.estimations`, `app.services.llm_service` and `app.context.examples` are imported from the repository root with `uv run python`
- **THEN** each import succeeds without errors

### Requirement: Project metadata and tooling files

The repository root SHALL contain `pyproject.toml`, `uv.lock`, `.gitignore` and `README.md`. `pyproject.toml` SHALL require Python 3.11 or newer.

#### Scenario: Root files present

- **WHEN** the repository root is listed
- **THEN** `pyproject.toml`, `uv.lock`, `.gitignore` and `README.md` are present

#### Scenario: Python version constraint

- **WHEN** `pyproject.toml` is read
- **THEN** `requires-python` is `>=3.11`

### Requirement: Declared dependencies

`pyproject.toml` SHALL declare `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `python-dotenv` and at least one LLM SDK (`openai` or `anthropic`) as runtime dependencies, and `uv.lock` SHALL be in sync with it.

#### Scenario: Dependencies resolve from the lock

- **WHEN** `uv sync --locked` is run on a clean checkout
- **THEN** the command succeeds and installs all declared dependencies

### Requirement: Application starts

The FastAPI application SHALL be importable as `app.main:app` and SHALL start with `uv run uvicorn app.main:app`.

#### Scenario: Server boots

- **WHEN** `uv run uvicorn app.main:app` is started from the repository root
- **THEN** the server starts listening without import or startup errors
