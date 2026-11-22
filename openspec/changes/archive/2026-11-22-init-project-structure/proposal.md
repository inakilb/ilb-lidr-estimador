# Proposal

## Why

Step 1 of the exercise asks for a uv project with a fixed folder layout. The teaching assistant checks that layout. The uv project, its dependencies and the lock file already exist, but `app/` only has `__init__.py` and a hello-world `main.py`. The `routers/`, `services/` and `context/` packages that later steps fill in don't exist yet.

## What Changes

- Create the `app/routers/`, `app/services/` and `app/context/` packages, each with an `__init__.py`.
- Add placeholder modules at the paths the course requires: `app/config.py`, `app/routers/estimations.py`, `app/services/llm_service.py` and `app/context/examples.py`. Each holds only a module docstring stating its responsibility and the step that implements it.
- Confirm the required dependencies are declared and locked: `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `python-dotenv`, `openai`, `anthropic`.
- Keep the app runnable: `uv run uvicorn app.main:app` must still start. `main.py` stays as it is until step 6 replaces it.

## Capabilities

### New Capabilities

- `project-structure`: the required repository layout, package files and dependency set of the estimator service.

### Modified Capabilities

<!-- none -->

## Impact

- New files under `app/` (empty placeholder modules and `__init__.py` files). No behavior or API changes.
- No dependency changes: everything required is already in `pyproject.toml` and `uv.lock`.
- README.md status table: step 1 is marked done.
