# Proposal

## Why

Step 8 of the exercise: "define how to validate that the folder structure is correct and that the service works, and create a pipeline that does it automatically". Every check so far (about 120 scenario checks across steps 2–7) lives in throwaway scratchpad scripts and was run by hand. The repository has no tests and no CI, so nothing protects the delivered branch from regressions, and the teaching assistant cannot see the checks run. The brief's other item, adding the meeting transcription used as input, is already covered by `transcripciones/` (step 7).

## What Changes

- **Add `pytest` as a development dependency** (`uv add --dev pytest`, which creates a `dev` group in `pyproject.toml` and updates `uv.lock`). `requirements.txt` stays runtime-only.
- **Add a `tests/` suite.** It turns the scratchpad checks into repeatable tests, all offline: no real LLM calls, no API keys needed, no cost.
  - `test_structure.py`: every path of the course layout exists, each package has `__init__.py`, `.env` is ignored by git and `.env.example` has only empty values. Extra files are allowed.
  - `test_config.py`: sources and precedence, defaults, validation (including a model from the other provider), secret masking, cached access.
  - `test_examples.py`: shape, coverage, section order and arithmetic of the 7 examples.
  - `test_llm_service.py`: prompt content, request shape per provider and model, caching markup, usage normalization, cost, error mapping (with fake SDK clients).
  - `test_estimations.py`: request validation, response fields, HTTP error mapping, settings override (with `TestClient` and a fake service).
  - `test_app.py`: Swagger and OpenAPI metadata, mounted router, `/health` ok and degraded, root redirect, logging level.
  - `test_transcripciones.py`: each sample file is a valid request body, and the empty one is rejected by the schema.
- **Add a GitHub Actions workflow `.github/workflows/ci.yml`**, running on pushes and pull requests:
  1. set up uv and Python 3.11, then `uv sync --locked`;
  2. check that `requirements.txt` matches `uv.lock`;
  3. run `uv run pytest`;
  4. **smoke test:** start `uvicorn app.main:app` with dummy keys, check `/health` (200 and `status: ok`), `/docs` (200) and `POST /api/v1/estimate` with `transcripciones/vacia.json` (422, which needs no LLM), then stop the server.
- **Add an optional manual live check** in the same workflow. It runs only on manual dispatch (`workflow_dispatch` with `live: true`), sends `transcripciones/curso-landing.json` to the running service with a real key from the `ANTHROPIC_API_KEY` repository secret, and expects 200 with an estimation. It costs about $0.01 per run, and it is skipped unless requested.
- **Docs:** README gets a "Tests y CI" section (how to run the tests, what the pipeline checks, how to trigger the live check) and a CI badge, and step 8 is marked done. CLAUDE.md gets `uv run pytest` in its commands and loses "No tests, linter or CI exist yet".

## Capabilities

### New Capabilities

- `ci-pipeline`: the automated validation: the offline test suite, the folder-structure checks, and the GitHub Actions workflow with its smoke test and optional live check.

### Modified Capabilities

<!-- none -->

## Impact

- New: `tests/` (7 test modules plus `conftest.py`), `.github/workflows/ci.yml`.
- Changed: `pyproject.toml` and `uv.lock` (dev group with `pytest`), README.md, CLAUDE.md.
- No application code changes. CI needs no secrets except for the optional live job.
- The pipeline runs on GitHub once the branch is pushed; locally the same steps can be reproduced with `uv run pytest` and the smoke-test commands.
