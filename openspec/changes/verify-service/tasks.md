# Tasks

## 0. Sample transcriptions

- [ ] 0.1 Create `transcripciones/` with `curso-landing.json`, `tienda-vinos.json`, `no-es-proyecto.json`, `vacia.json` and `inyeccion.json`, each a valid `{"transcription": "..."}` body in Spanish
- [ ] 0.2 Validate that every file parses as JSON with a string `transcription`

## 1. Checklist on the running service

- [ ] 1.1 Start `uv run uvicorn app.main:app --reload` from the repository root and confirm a clean startup (log lines, no errors)
- [ ] 1.2 Keys: no key patterns in `git ls-files`, keys read only in `app/config.py`, `.env.example` with empty values
- [ ] 1.3 `GET /health` → 200 with `status: ok`
- [ ] 1.4 The course `curl` verbatim → 200 with a Spanish estimation; record the latency, tokens and cost
- [ ] 1.4b Send each file in `transcripciones/` with `curl -d @file` and check the expected results (200 Spanish estimation / 200 "cannot estimate" sentence / 422 / 200 estimation that ignores the injection)
- [ ] 1.5 Swagger: `/docs` serves Swagger UI and `/openapi.json` lists `POST /api/v1/estimate`
- [ ] 1.6 `git check-ignore -v .env` reports it as ignored
- [ ] 1.7 Stop the server (separate command, by PID)

## 2. Influence of the examples

- [ ] 2.1 Similarity: estimate `transcripciones/tienda-vinos.json` and compare it with example 6 (sections, rate, contingency, VAT, duration rule, Correos and Redsys tasks, subtotal range)
- [ ] 2.2 Ablation: the same transcription with `ESTIMATION_EXAMPLES = []` in a scratch process (cleared prompt cache); record the differences (number of tasks, task names, hours, team) and which rules still hold
- [ ] 2.3 Summarize both comparisons in a short table of key figures

## 3. Documentation

- [ ] 3.1 Add the "Verificación" section to README.md (Spanish), after "Uso": the checklist table (item, how it was checked, result, re-run command), "Pruebas manuales" (one `curl -d @transcripciones/<file>` per file plus `/health` and Swagger, with expected results, and a loop to run them all), "Influencia de los ejemplos", and the date and model, with a note that runs vary
- [ ] 3.1b Add `transcripciones/` to the README "Estructura" tree and to the CLAUDE.md target architecture
- [ ] 3.2 Mark step 7 as done in the README.md status table
