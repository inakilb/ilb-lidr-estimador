# Design

## Context

Steps 1–6 are done and archived. Each step checked its own part (scratchpad suites: 14 + 7 config, 57 service, 27 endpoint and 15 app checks), and live calls confirmed both providers. The course's step 7 is a manual pass over the finished service with a seven-item checklist. Six items are mechanical. "The generated estimation draws on the injected examples" needs evidence, not just an assertion.

Two facts shape that evidence:

- **The system prompt states the rules in its instructions** (62.5 EUR/h, even hours, 15% contingency, VAT, the duration formula, Spanish headings), not only through the examples. Removing the examples therefore does not remove those rules.
- **The examples carry what the instructions don't:** task granularity and naming, typical hours per kind of task, team composition, and the kinds of assumptions, scope limits and risks. Example 6 (WooCommerce + Correos + Redsys) is the closest match for a shop request.

## Goals / Non-Goals

**Goals:**

- One recorded, reproducible pass over the course checklist on the running service.
- Honest evidence of the examples' influence: what they change and what the instructions already fix.
- A README section the teaching assistant can follow in a few minutes.

**Non-Goals:**

- Automating the checks in CI: step 8, which can reuse the commands recorded here.
- Measuring estimation quality or accuracy: the course leaves that for the live session.
- Fixing code. If a check fails, it is reported, and the fix goes into its own change.

## Decisions

- **Run the course's own commands.** `uv run uvicorn app.main:app --reload` from the repository root, the course `curl` verbatim, and `/docs` checked over HTTP (HTML containing Swagger UI) plus `/openapi.json`. The verification then shows that the course's instructions work as written.
- **Sample transcriptions as files in `transcripciones/`.**
  - Each file is a complete request body, so `curl -X POST localhost:8000/api/v1/estimate -H "Content-Type: application/json" -d @transcripciones/<file>` works as is. Swagger's *Try it out* takes the same content pasted in.
  - The texts are in Spanish, written like real meeting notes, and fictitious.
  - The folder name is Spanish, like the README and the brief's wording ("transcripción de reunión"). File names are short and descriptive.
  - Five files, one per behavior worth seeing by hand: the course sample, a request close to an example, a non-project text, an empty input and a prompt injection.
  - JSON instead of `.txt`: `curl -d @file` sends the file as the body, and a plain text file would need `jq` or shell quoting to wrap it in JSON. Step 8 can parse the files directly.
  - Alternative: inline `curl -d '{...}'` commands in the README. Rejected, because long one-line bodies make the README hard to read, and the texts would not be reusable.
- **README "Pruebas manuales" block**, inside the "Verificación" section: a table with the file or URL, the command and the expected result. A short shell loop runs all files in one go.
- **Secret checks:**
  - `git ls-files` piped to `grep -E` for `sk-ant-`, `sk-proj-` and `sk-` followed by 20+ characters, which must find nothing;
  - `git check-ignore -v .env`;
  - a search confirming that only `app/config.py` reads key variables, and that the code otherwise uses `get_settings()`;
  - `.env.example` holding only empty values.
- **Influence evidence in two parts, both live:**
  1. **Similarity:** `transcripciones/tienda-vinos.json`: "A Bilbao wine shop wants a WooCommerce shop with ~120 products, Redsys card and Bizum payments, Correos shipping with labels and tracking, and returns", written in Spanish like a real meeting. It is compared with example 6: the seven sections, the rate, the contingency, the VAT note, the duration rule, and the presence of Correos (rates, labels, tracking, returns) and Redsys tasks of comparable size. The total hours should land in the same range as example 6 (206 h subtotal) for a similar scope.
  2. **Ablation:** the same transcription through a scratch script that sets `ESTIMATION_EXAMPLES = []` in memory and clears the prompt cache, calling the real service. Expected: the rules still hold, because they are in the instructions, but task granularity, task names, hours and the team change. The README states this split honestly instead of claiming that the examples drive everything.
  - One run per variant. LLM outputs vary between runs, so the comparison is described qualitatively, with the key figures (number of tasks, subtotal, presence of the Correos and Redsys tasks), and not as a statistic.
- **README section "Verificación"**, placed after "Uso" and before "Desarrollo":
  - a table with the item, how it was checked, the result and the command to re-run it;
  - "Influencia de los ejemplos": the two comparisons in a few lines, with a small table of key figures;
  - the date, provider and model, and a note that results can vary between runs.

  No sample estimation is pasted in full: the README already shows the response shape, and a full estimation would double its length.
- **Default configuration from the user's `.env`** (Anthropic, `claude-haiku-4-5`), the course model. Other providers and models were verified live in step 4 and in `refine-llm-models`, and the README links to that.

## Risks / Trade-offs

- [`transcripciones/` is not in the course's folder layout] → It is an addition, not a change to the required files. The README lists it under "Estructura", and step 8's layout check verifies that the required paths exist without banning extra ones.

- [A single run per variant could be unrepresentative] → The rules are checked mechanically (they hold every time), and the influence claim is limited to what one comparison can show. The live session can repeat it with more runs.
- [The ablation reaches into module state] → Scratchpad only, in a separate process. The code and the repository are untouched.
- [The README grows] → One compact section. The detailed evidence stays out of the repository.
