# Design

## Context

What exists:

- The service is complete (steps 1–7): 7 main specs, about 50 scenarios.
- During development each step was verified with scratchpad scripts outside the repository: config (14 + 7 checks), examples consistency, service with fake SDK clients (57), endpoint (27), app (15).
- They used `TestClient` (which works on the installed `httpx2`), `Settings(_env_file=None, …)`, isolated subprocesses for environment tests, and module-attribute patching for fakes.
- The repository is on GitHub (`inakilb/ilb-lidr-estimador`, branch `feature/sesion-02`).
- `pyproject.toml` has no dev dependencies and no build backend. `requirements.txt` is exported from `uv.lock` with `--no-dev`.

## Goals / Non-Goals

**Goals:**

- One command, `uv run pytest`, that validates the structure and the behavior, offline, in seconds, with no secrets.
- A CI workflow that a reviewer can read in one screen and that fails loudly on any regression.
- A smoke test of the real app process, because unit tests with `TestClient` don't prove that `uvicorn app.main:app` starts.
- No spending in CI, except an explicitly requested live run.

**Non-Goals:**

- Linting, formatting and type checking (ruff, mypy): not asked for by the course. They can be added as one more CI step later.
- Coverage thresholds and test matrices across Python versions: the project targets Python 3.11 only.
- Deployment.
- Live LLM calls on every push.

## Decisions

- **pytest, in a uv `dev` dependency group.**
  - `uv add --dev pytest` writes `[dependency-groups] dev = ["pytest…"]`, which `uv sync` installs by default and `uv export --no-dev` leaves out, so `requirements.txt` stays runtime-only.
  - No other test libraries: FastAPI's `TestClient` and pytest's `monkeypatch` cover everything the scratch scripts did.
  - Alternative: `unittest`. Rejected, because pytest fixtures and parametrization make the ported checks much shorter.
- **Test isolation (`tests/conftest.py`):**
  - An autouse fixture deletes every config variable (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `APP_ENV`, `LOG_LEVEL`) with `monkeypatch.delenv`. It also changes the working directory to a temporary folder, so `.env` (looked up relative to the working directory) is never read. Last, it clears the `get_settings` and `build_system_prompt` caches.
  - Tests that need settings build them explicitly with `Settings(_env_file=None, …)`, or write a temporary `.env` in that folder.
  - Fixtures provide fake Anthropic and OpenAI clients (recording the calls, returning canned responses or raising SDK exceptions built from `httpx2` request/response objects), plus a `client` fixture: `TestClient(app)` with `settings_dependency` overridden.
  - The fakes replace `_anthropic_client` and `_openai_client` with `monkeypatch.setattr`, the same seam the scratch scripts used.
- **Paths:**
  - `pyproject.toml` gets `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and `pythonpath = ["."]`, so `app` imports from the repository root without packaging the project.
  - Tests that read repository files (structure, transcriptions) resolve paths from a `REPO_ROOT` fixture, based on `__file__`, because the working directory is a temporary folder.
- **One test module per main spec**, named after it, with scenario names in test names (for example `test_unknown_provider_rejected`), so a failing test maps back to a spec scenario:
  - `test_structure.py`: the paths are a parametrized list, so a failure names the missing path. `git check-ignore .env` runs through `subprocess`, and the test is skipped when `git` or `.git` is unavailable. `.env.example` is parsed line by line, and every `KEY=value` must have an empty value.
  - `test_examples.py`: ports the scratch consistency checker (section order, row costs, contingency rounding, totals, duration formula, Redsys in both shops, corporate site sections).
  - `test_transcripciones.py`: each file parses to `{"transcription": str}`. `EstimationRequest` accepts the 4 non-empty files and rejects `vacia.json`.
- **CI workflow:**
  - Triggers: `push` (all branches) and `pull_request`, so pushing `feature/sesion-02` runs it. Also `workflow_dispatch` with a boolean input `live`, default false.
  - Job `test` on `ubuntu-latest`, with `astral-sh/setup-uv` (with caching) and `uv python install` from `.python-version`.
  - **Step "requirements.txt in sync":** regenerate the file with exactly the command in CLAUDE.md (`uv export --no-hashes --no-emit-project --no-dev --format requirements-txt -o requirements.txt`), then `git diff --exit-code requirements.txt`. Piping the export into `diff -` was the first idea, but it always reports a difference: the export writes its own command line into the header comment, and the committed file was generated with `-o requirements.txt`. Regenerating in place compares like with like, and it was confirmed locally to give no diff.
  - **Step "smoke test":** environment `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY=ci-dummy-key`, `LOG_LEVEL=INFO`. It starts `uv run uvicorn app.main:app --port 8000 &`, polls `/health` for up to 30 s, then asserts with `curl` and `python -c` (no `jq` dependency). It prints the server log on failure and kills the server in a final step with `if: always()`.
  - Dummy keys are fine because none of these endpoints reach the LLM: `/health` doesn't call it, and the empty transcription is rejected by the schema.
  - **Job `live`:** `needs: test`, `if: github.event_name == 'workflow_dispatch' && inputs.live`, with environment `ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}`. It starts the server, sends `curso-landing.json`, and asserts 200 and a non-empty `estimation`. If the secret is missing, the step fails with a clear message.
  - Action versions are pinned to major tags (`actions/checkout@v4`, `astral-sh/setup-uv@v6`) for readability. Pinning to SHAs is stricter, but noisy for a course project.
- **Scratchpad checks are ported, not copied.** They are rewritten as small pytest functions. Checks that only made sense during development, such as mutation tests of the checker, are dropped.

## Risks / Trade-offs

- [The tests reach into private seams (`_anthropic_client`, `_openai_client`)] → They are the narrowest point where the SDK is created, and they keep the tests free of network mocking. Renaming them breaks the tests loudly, which is acceptable.
- [The action major versions age] → The workflow fails visibly if an action is retired. Updating is a one-line change.
- [The smoke test's fixed port 8000 could collide on a self-hosted runner] → GitHub-hosted runners are fresh VMs.
- [Network-dependent setup (uv download, Python install) can flake] → The setup-uv cache and the default retries reduce this. A rerun fixes the rest.
- [The pipeline is only proven on GitHub after a push] → Before archiving, the same commands run locally: pytest, the requirements diff and the smoke test. The workflow YAML is checked by parsing it with Python's `yaml` module if available, or else reviewed by hand.
