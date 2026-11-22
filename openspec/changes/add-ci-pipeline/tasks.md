# Tasks

## 1. Test setup

- [x] 1.1 `uv add --dev pytest`. Confirm `pyproject.toml` has a `dev` dependency group and that `uv export --no-dev` (`requirements.txt`) is unchanged
- [x] 1.2 Add `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `pythonpath = ["."]`) to `pyproject.toml`
- [x] 1.3 Create `tests/conftest.py`: autouse isolation (delete config variables, temporary working directory, clear caches), `REPO_ROOT`, settings builders, fake Anthropic and OpenAI clients, SDK error builders, and a `client` fixture (`TestClient` with the settings overridden)

## 2. Test modules

- [x] 2.1 `tests/test_structure.py`: parametrized required paths, `__init__.py` per package, `.env` ignored by git (skipped without git), `.env.example` values empty
- [x] 2.2 `tests/test_config.py`: `.env` and environment precedence, defaults and empty values, model per provider and explicit model, invalid provider and log level, missing key, the other provider's key not required, a model from the other provider rejected and an unrecognized model accepted, secrets masked, import without configuration, same instance
- [x] 2.3 `tests/test_examples.py`: shape and count, coverage (Redsys in both shops, 10+ corporate sections), English, sections in order, row costs, subtotal, contingency, total, even hours, VAT note, duration formula
- [x] 2.4 `tests/test_llm_service.py`: prompt content and determinism, transcription tags, empty input, Anthropic request shape (cached system block, options per model, no sampling parameters), OpenAI request shape, thinking blocks ignored, usage normalization, cost, stop reasons and refusals, provider registry, error mapping for both SDKs (including quota exhausted)
- [x] 2.5 `tests/test_estimations.py`: 200 response fields, trimming, 422 cases (missing, empty, whitespace, over 50,000 characters, not a string), 501/503 (with `Retry-After`)/502 mapping, 500 on invalid configuration without secrets, settings override
- [x] 2.6 `tests/test_app.py`: `/docs`, OpenAPI metadata and paths, router mounted, scaffold routes gone, `/` redirect, `/health` ok and degraded without an LLM call, log level from configuration, and the INFO fallback with an error log
- [x] 2.7 `tests/test_transcripciones.py`: each file is `{"transcription": str}`, the 4 non-empty files are accepted by `EstimationRequest`, and `vacia.json` is rejected
- [x] 2.8 Run `uv run pytest` locally: all pass, with no network calls. Run it again with the real `.env` present, to show that the results don't change

## 3. CI workflow

- [x] 3.1 Create `.github/workflows/ci.yml`: triggers (push, pull_request, workflow_dispatch with `live`), job `test` with setup-uv, Python from `.python-version`, `uv sync --locked`, the requirements diff, `uv run pytest`
- [x] 3.2 Add the smoke-test steps: start uvicorn with dummy keys, wait for `/health`, assert `status: ok`, `/docs` 200 and `vacia.json` 422; print the log on failure, and stop the server with `if: always()`
- [x] 3.3 Add job `live` (`needs: test`, manual dispatch only, `ANTHROPIC_API_KEY` secret): start the server, send `curso-landing.json`, assert 200 and a non-empty estimation
- [x] 3.4 Validate the YAML syntax, and run the workflow's commands locally (requirements diff, pytest, smoke test with dummy keys)

## 4. Documentation

- [x] 4.1 README (Spanish): CI badge, a "Tests y CI" section (`uv run pytest`, what each test module covers, what the pipeline does, how to run the live check and set the secret), `tests/` and `.github/` in "Estructura", and step 8 marked done
- [x] 4.2 CLAUDE.md: add `uv run pytest` to Commands, replace "No tests, linter or CI exist yet", and mention `tests/` and the workflow
