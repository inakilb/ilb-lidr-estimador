# Spec

## Purpose

Defines how the finished service is verified against the course checklist: a reproducible "Verificación" section in the README, sample transcriptions in `transcripciones/` with manual tests and expected results, checks run on the running service, secrets kept out of the repository, and evidence that the injected examples shape the estimations.

## Requirements

### Requirement: Course checklist verified

The README SHALL contain a "Verificación" section with one entry for each of the seven items of the course checklist. Each entry SHALL state:

- how the item was checked;
- the result;
- the command, URL or file that re-checks it.

The section SHALL record the date of the verification and the provider and model used.

#### Scenario: Every item documented

- **WHEN** the "Verificación" section is read
- **THEN** it has an entry for each of the 7 items: startup, keys from `.env` and absent from the code, `GET /health` 200, `POST /api/v1/estimate` returning an estimation, influence of the examples, Swagger at `/docs`, and `.env` in `.gitignore`

#### Scenario: Reproducible

- **WHEN** a reader follows the commands in the section on a clone with a valid `.env`
- **THEN** they can repeat each check without reading any other document

### Requirement: Sample transcriptions and manual tests

The repository SHALL contain a `transcripciones/` folder with sample request bodies, each a JSON file holding `{"transcription": "..."}` that can be sent with `curl -d @<file>`:

- `curso-landing.json`: the course's sample transcription;
- `tienda-vinos.json`: a WooCommerce shop with Correos shipping and Redsys payments;
- `no-es-proyecto.json`: a text that is not a software project request;
- `vacia.json`: a whitespace-only transcription;
- `inyeccion.json`: a project request containing an instruction that tries to override the system prompt.

The README SHALL contain a "Pruebas manuales" block with one command per file, plus commands for `GET /health` and Swagger, each with its expected result.

#### Scenario: Files are valid request bodies

- **WHEN** each file in `transcripciones/` is parsed as JSON
- **THEN** it is an object with a string `transcription` field

#### Scenario: Expected results hold

- **WHEN** each file is sent to the running service with `curl -d @transcripciones/<file>`
- **THEN** the results are:
  - `curso-landing.json` and `tienda-vinos.json`: 200 with a Spanish estimation;
  - `no-es-proyecto.json`: 200 with a short Spanish sentence saying it cannot be estimated;
  - `vacia.json`: 422;
  - `inyeccion.json`: 200 with a normal estimation that ignores the embedded instruction.

### Requirement: Checks performed on the running service

The checks SHALL be run against the service started with `uv run uvicorn app.main:app --reload` from the repository root, using the course's `curl` command for the estimation and a browser or HTTP request for Swagger.

#### Scenario: Course command works

- **WHEN** the course's `curl` command is sent to the running service
- **THEN** the response is 200 with a non-empty `estimation` in Spanish

### Requirement: Secrets kept out of the repository

The verification SHALL confirm that:

- no file tracked by git contains an API key value;
- `.env` is ignored by git;
- the code reads keys only through `app/config.py`.

#### Scenario: No keys in tracked files

- **WHEN** the files tracked by git are searched for key patterns (`sk-ant-`, `sk-proj-`, `sk-` followed by a long token)
- **THEN** no match is found

#### Scenario: .env ignored

- **WHEN** `git check-ignore .env` is run
- **THEN** it reports `.env` as ignored

### Requirement: Evidence that the examples shape the estimation

The verification SHALL compare an estimation for a transcription similar to one injected example with:

- that example, checking the structure, the rate, the contingency, the VAT note, the duration rule and comparable tasks;
- an estimation for the same transcription generated without the examples in the prompt.

The README SHALL summarize both comparisons.

#### Scenario: Similar request follows its example

- **WHEN** the service estimates `transcripciones/tienda-vinos.json` (a WooCommerce shop with Correos shipping and Redsys payments)
- **THEN** the estimation uses the seven sections, 62.5 EUR/h, a 15% contingency and the VAT note, and includes Correos and Redsys integration tasks comparable to the matching example

#### Scenario: Without examples the output changes

- **WHEN** the same transcription is estimated with no examples in the system prompt
- **THEN** the differences from the estimation made with examples (structure, rate, contingency or figures) are recorded as evidence of their influence
