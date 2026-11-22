# Proposal

## Why

Step 7 of the exercise: before the exercise counts as complete, the course asks to start the server, try the endpoint with `curl` or Swagger, and go through a seven-item checklist. Most items were checked piece by piece in steps 2–6. Two things are still missing:

- One end-to-end pass on the finished service, recorded somewhere the teaching assistant can read it.
- Evidence for the only item that is a judgment call: "the generated estimation draws on the injected context examples".

## What Changes

- **Run the full course checklist against the running service** (`uv run uvicorn app.main:app --reload`), with the course's own `curl` command and Swagger UI:
  1. The project starts without errors.
  2. API keys come from `.env` and never appear in the code.
  3. `GET /health` answers 200.
  4. `POST /api/v1/estimate` returns an estimation.
  5. The estimation draws on the injected examples.
  6. Swagger is reachable at `/docs`.
  7. `.env` is in `.gitignore`.
- **Show that the examples influence the output, with two checks:**
  - **Similarity:** a transcription close to one example (a WooCommerce shop with Correos shipping and Redsys payments) should produce an estimation that follows that example. That means the same structure, the 62.5 EUR/h rate, the 15% contingency, the VAT note, the duration rule, and comparable tasks and figures.
  - **Ablation:** the same transcription sent with the examples removed from the prompt, through a scratch script that does not change the code. The difference in structure, rate and figures shows what the examples contribute.
- **Add sample transcriptions as files in `transcripciones/`**, each one a ready-to-send JSON request body (`{"transcription": "..."}`):
  - `curso-landing.json`: the course's sample (landing page + HubSpot);
  - `tienda-vinos.json`: a WooCommerce shop with Correos and Redsys, similar to example 6;
  - `no-es-proyecto.json`: a text that is not a software request;
  - `vacia.json`: whitespace only;
  - `inyeccion.json`: a project request with a prompt-injection attempt inside.

  They cover the brief's later item "add the meeting transcription used as the exercise input to the repo". Step 8's pipeline can reuse them.
- **Add a "Pruebas manuales" block to README.md** (Spanish): one `curl -d @transcripciones/<file>` command per file, plus `/health` and Swagger, each with its expected result. Readers can paste them into a second terminal while the server runs.
- **Add a "Verificación" section to README.md** (Spanish): one row per checklist item, with how it was checked, the result and the command to re-run it, plus a summary of the influence evidence and the date and model used. Step 7 is marked done.
- No application code changes. Anything the verification breaks is reported and fixed in a follow-up change.

## Capabilities

### New Capabilities

- `service-verification`: the documented, reproducible verification of the finished service against the course checklist, including evidence that the examples shape the estimations.

### Modified Capabilities

<!-- none -->

## Impact

- README.md, and a new `transcripciones/` folder with 5 small JSON files. These files sit outside the course's required layout, so the layout check must allow extra files. Verification scripts live in the scratchpad. Step 8 turns the automatable checks into a CI pipeline.
- Cost: about 7 live estimations (the 5 sample files, where the empty one costs nothing because it is rejected before the LLM, plus the ablation and one Swagger try), under $0.10 at Haiku 4.5 prices.
