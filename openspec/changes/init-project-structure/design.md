# Design

## Context

The uv project (Python 3.11), its dependencies, `uv.lock`, `.gitignore` and the docs were committed in the setup commit. `app/` has `__init__.py` and a hello-world `main.py`. The course fixes the folder layout and file names, and the teaching assistant checks against them. Steps 2–6 then fill in each module.

## Goals / Non-Goals

**Goals:**

- Every path of the required layout exists, so the structure check passes from step 1 on.
- Each module states its responsibility, so later steps have a clear place to land.
- The app keeps starting with `uv run uvicorn app.main:app`.

**Non-Goals:**

- Any real logic: settings (step 2), examples (step 3), LLM calls (step 4), endpoint (step 5) and the FastAPI app rewrite (step 6).
- `.env` and `.env.example`: their contents are the variable list, which step 2 defines, so step 2 creates them. `.env` is already gitignored.
- CI or automated structure checks (step 8).

## Decisions

- **Docstring-only placeholders instead of stub code.** Each new module contains just a module docstring naming its role and the step that implements it. Alternatives: empty files, which say nothing to the reviewer, or stub functions and classes, which would preempt design choices of later steps and produce dead code. A docstring is importable, self-documenting and leaves each later step's diff clean.
- **Empty `__init__.py` files.** Packages need no re-exports. Callers import from the concrete module (`from app.services.llm_service import ...`), which keeps the layout explicit.
- **Leave `main.py` untouched.** Step 6 owns the app definition. Changing it now would blur the per-step history the teaching assistant reviews.
- **Keep both LLM SDKs for now.** Which provider(s) to implement is decided in step 4. The unused SDK is dropped there if only one is implemented.

## Risks / Trade-offs

- [Placeholder modules look like unfinished code to a reviewer] → The docstring states which step fills each one, and the README status table tracks progress.
- [`.env.example` is listed in the step 1 tree but arrives in step 2] → Documented here as a non-goal. Step 2 creates it together with `config.py`.
