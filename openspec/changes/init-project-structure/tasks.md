# Tasks

## 1. Package skeleton

- [x] 1.1 Create `app/routers/__init__.py`, `app/services/__init__.py` and `app/context/__init__.py` (empty)
- [x] 1.2 Create `app/config.py` with a module docstring (settings loaded from `.env`, implemented in step 2)
- [x] 1.3 Create `app/context/examples.py` with a module docstring (static `ESTIMATION_EXAMPLES` few-shot context, step 3)
- [x] 1.4 Create `app/services/llm_service.py` with a module docstring (prompt building and LLM call, step 4)
- [x] 1.5 Create `app/routers/estimations.py` with a module docstring (`POST /api/v1/estimate`, step 5)

## 2. Dependencies

- [x] 2.1 Check that `pyproject.toml` declares `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `python-dotenv`, `openai`, `anthropic` and `requires-python >=3.11`
- [x] 2.2 Run `uv sync --locked` and confirm it succeeds (lock in sync)

## 3. Verification

- [x] 3.1 Check that every path in the `project-structure` spec exists
- [x] 3.2 Import `app.config`, `app.routers.estimations`, `app.services.llm_service` and `app.context.examples` with `uv run python` without errors
- [x] 3.3 Start `uv run uvicorn app.main:app`, confirm it boots, and stop it
- [x] 3.4 Mark step 1 as done in the README.md status table
