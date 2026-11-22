# Design

## Context

What already exists:

- `get_settings()` (step 2): provider `anthropic`, model `claude-haiku-4-5`, and the API key as a `SecretStr`.
- `ESTIMATION_EXAMPLES` (step 3): 7 English examples, about 5,970 tokens.
- The locked `anthropic` SDK is 2.12.

Relevant facts about Claude Haiku 4.5:

- 200K context and 64K max output.
- $1 / $5 per million input / output tokens. Cache writes cost 1.25× the input price and cache reads 0.1×.
- Minimum cacheable prefix: 4,096 tokens.
- No `effort` parameter. Thinking is off unless requested.

Claude Haiku 5.5 (`claude-haiku-5-5`) is supported as an alternative and is available on the user's key:

- 1M context and 128K max output.
- $0.10 / $0.50 per million tokens for prompts up to 100K tokens, with the same cache multipliers.
- Minimum cacheable prefix: 512 tokens.
- Adaptive thinking on by default, and `effort` from `low` to `max` (default `medium`).
- A newer tokenizer that counts about 30% more tokens.
- Refusals are possible and have no server-side fallback.

The router (step 5) is a FastAPI endpoint and will call this service. Users write the transcriptions in Spanish, and the estimation must come back in Spanish.

## Goals / Non-Goals

**Goals:**

- One function, `generate_estimation(transcription) -> EstimationResult`, that hides the provider from the router.
- A prompt that makes the model follow the examples' structure and arithmetic, in Spanish.
- Cheap and fast repeated calls through prompt caching.
- Clear, typed failures that the router can map to HTTP responses.

**Non-Goals:**

- The Gemini implementation: a later change, which plugs into the provider registry.
- Streaming responses: the course expects a single JSON response.
- Extended thinking: it is not needed for this structured task on Haiku and would add cost and latency. Revisit in the live session.
- An HTTP schema and status-code mapping: step 5.
- Automated tests in the repository: step 8. This change verifies with scratchpad scripts.

## Decisions

- **Module layout:**
  - `build_system_prompt()` is pure and cached with `lru_cache`.
  - `build_user_message(transcription)` is pure.
  - `generate_estimation(transcription, settings=None)` looks up the provider in `PROVIDERS` and calls it.
  - `_generate_with_anthropic(...)` and `_generate_with_openai(...)` each take `(transcription, settings)` and return an `EstimationResult`.
  - Shared pieces stay provider-neutral: prompt builders, `EstimationResult`, the errors, the cost table and a `_build_result()` helper that logs usage and computes the cost.
  - The pure builders can be tested without the network.
- **Provider registry instead of `if`/`elif`:** `PROVIDERS: dict[str, Callable[[str, Settings], EstimationResult]]`. Adding Gemini takes four steps:
  1. Add `"gemini"` to `LLMProvider` and a `GEMINI_API_KEY` field in `config.py`.
  2. Add the model default.
  3. Write `_generate_with_gemini`.
  4. Register it, and add its price.

  Everything stays in `llm_service.py`, because the course fixes the folder layout. A `providers/` subpackage would be cleaner past three or four providers, but it would add files the course structure does not list.
- **The system prompt as a single text block with `cache_control: {"type": "ephemeral"}`.**
  - Everything in it is static, so one breakpoint at its end caches all of it. At about 6.5k tokens it clears Haiku 4.5's 4,096-token minimum.
  - Default TTL of 5 minutes. A 1-hour TTL doubles the write price and only pays off with bursty traffic and long gaps, which a course demo does not have.
  - Alternative: no caching. Rejected, because every call would pay full price for the same 6.5k tokens, and caching is the natural optimization for CAG.
- **Prompt structure:** the instructions come first, then the examples inside `<examples><example index="N"><meeting_summary>…</meeting_summary><estimation>…</estimation></example></examples>` tags. XML tags separate the examples from the instructions and from each other, so the model doesn't take them as instructions. The rendering lives here, not in `examples.py`, so the data module stays data-only.
- **Spanish output, English examples:**
  - The prompt says: write the whole estimation in Spanish, and translate the section headings. It gives the exact headings: `Desglose de tareas`, `Totales`, `Supuestos`, `Fuera de alcance`, `Riesgos`, `Equipo recomendado`, `Duración estimada`.
  - It also asks for the Spanish number format (`14.375 €`). Fixed headings make the output predictable for the router and for the user.
  - The prompt asks for the estimation only, in Markdown starting with a `##` title, with no preamble or closing remarks.
- **Handling missing information:** the prompt tells the model to estimate anyway, state its assumptions in `Supuestos`, and list open questions as risks. If the text is not a software project request, it answers with one short Spanish sentence saying so. A best-effort answer suits a demo better than a refusal.
- **The transcription as data:**
  - The user message is `<transcription>…</transcription>` plus a one-line request.
  - The system prompt says that the content inside the tags is input and that instructions inside it are not followed.
  - This is cheap defense against prompt injection in client text.
  - Empty input raises `ValueError` before any call. The router will also validate it with Pydantic in step 5.
- **Haiku 4.5 is the default and Haiku 5.5 is a supported alternative, selected through `LLM_MODEL`.**
  - The course names Haiku 4.5, so the delivery matches it. Haiku 5.5 is cheaper and better at following instructions, and having both lets the live session compare them.
  - Per-model request options live in a small table (`MODEL_REQUEST_OPTIONS`):
    - `claude-haiku-5-5` gets `output_config={"effort": "low"}`. The examples already give the structure, so deep reasoning is not needed, and low effort keeps cost and latency down. `thinking` is left unset, so the model's adaptive default applies.
    - `claude-haiku-4-5` gets nothing, because it rejects `effort` and thinking stays off.
  - Unknown models get no extras.
  - Alternative: an `LLM_EFFORT` environment variable. Rejected for now, because it would add a seventh variable outside the course's list and change the step 2 spec. The table is easy to promote to config later.
- **OpenAI through Chat Completions (`client.chat.completions.create`) with `gpt-4o-mini`:**
  - Messages: `[{"role": "system", ...}, {"role": "user", ...}]`, built by the same prompt functions, so both providers see an identical prompt.
  - `max_completion_tokens=16000`. `max_tokens` is deprecated in the SDK, and gpt-4o-mini outputs at most 16,384 tokens.
  - Chat Completions rather than the newer Responses API, because it is the most widely documented and is what the course material assumes. Switching later would only affect this function.
  - **Caching:** OpenAI caches prompts of 1,024+ tokens automatically, with no markup. A fixed `prompt_cache_key="estimador-cag-system"` helps route requests that share the system prompt to the same cache.
  - **Response handling:**
    - `finish_reason` `length`: `IncompleteEstimationError` (truncated).
    - `content_filter`, or a non-empty `message.refusal`: `IncompleteEstimationError` (declined).
    - Empty content: `IncompleteEstimationError`.
  - **Usage normalization:** OpenAI's `prompt_tokens` includes cached tokens, so `input_tokens = prompt_tokens - cached_tokens - cache_write_tokens`. `cache_read_input_tokens = cached_tokens`, and `cache_creation_input_tokens = cache_write_tokens` or 0. Both providers then report usage, and compute cost, the same way.
  - Client: one `openai.OpenAI` per key (`lru_cache`), with a 60 s timeout and the SDK's default retries.
- **No sampling parameters.** The current API version rejects `temperature`, `top_p` and `top_k`, and consistency comes from the examples, not from sampling.
- **`max_tokens = 16000`.** The estimations are about 1.5–2.5k tokens. A tight cap risks truncated output, and an unused cap costs nothing. 16k keeps the non-streaming request well inside the SDK's HTTP timeout.
- **One Anthropic client per API key, cached with `lru_cache`.** It reuses the connection pool across requests. The key comes from `settings.anthropic_api_key.get_secret_value()`, read only at this boundary. The client gets a 60 s timeout and the SDK default of 2 retries for 408/409/429/5xx and connection errors.
- **A synchronous client.** The router can use a plain `def` endpoint, which FastAPI runs in its thread pool, so there are no async-specific concerns. An async client can come later if concurrency requires it.
- **Response handling:**
  - Join the `text` blocks (ignoring any other block types, which keeps the code safe if the model changes).
  - `stop_reason`:
    - `end_turn`: success.
    - `max_tokens`: `IncompleteEstimationError` (truncated).
    - `refusal`: `IncompleteEstimationError` with the category from `stop_details`.
    - Empty text: `IncompleteEstimationError`.
- **Error mapping, most specific first:**
  - `RateLimitError`, `InternalServerError` / status ≥ 500 (including 529 overloaded), `APITimeoutError` and `APIConnectionError` become `LLMUpstreamError(retryable=True)`.
  - `AuthenticationError`, `PermissionDeniedError`, `NotFoundError`, `BadRequestError` and other `APIStatusError`s become `LLMUpstreamError(retryable=False)`.
  - Messages include the status code and the request ID, never the key. The original exception is chained with `raise … from e`.
  - The `openai` SDK has the same exception hierarchy (`APITimeoutError` ⊂ `APIConnectionError`, plus `RateLimitError`, `APIStatusError`, and so on). The mapper takes the SDK module as a parameter, so one function serves both providers and every future SDK with this shape.
- **`EstimationResult` as a frozen dataclass:** `estimation`, `model`, `provider`, `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `estimated_cost_usd`. A plain dataclass keeps the service independent of the HTTP schema, which is Pydantic and belongs to step 5.
- **The cost estimate from a small price table** (USD per million tokens):
  - `claude-haiku-4-5`: input 1.00, output 5.00, cache write 1.25, cache read 0.10.
  - `claude-haiku-5-5`: input 0.10, output 0.50, cache write 0.125, cache read 0.01. These are the rates for prompts up to 100K tokens, which always applies here.
  - `gpt-4o-mini`: input 0.15, output 0.60, cache write 0.15 (OpenAI does not charge extra for writes), cache read 0.075.
  - Output tokens include thinking tokens, as the API bills them. Unknown models give `None` instead of a wrong number. The prices are list prices and are documented as an estimate.
- **`model` in the result is the configured ID** (`claude-haiku-4-5`), as in the course's sample response. The dated snapshot returned by the API is logged at DEBUG level.
- **Logging with `logging.getLogger(__name__)`:**
  - INFO level: model, token usage and estimated cost.
  - DEBUG level: transcription length and request ID.
  - Never the key, and never the full transcription.
  - The log level is wired to `LOG_LEVEL` in step 6.

## Risks / Trade-offs

- [OpenAI verified live only after the change was archived] → An OpenAI key with credits was not available at first, so the OpenAI path was verified offline against the installed SDK's types. The live check (task 4b.7) passed later the same day: Spanish output, correct usage normalization, and cache reads on the second call.

- [The model drifts into English, because the examples are English] → Explicit Spanish instruction plus fixed Spanish headings. Checked during verification and again in step 7.
- [The model makes arithmetic slips (totals that don't add up)] → The examples show consistent arithmetic, but LLMs can still slip. Accepted for now: the course says quality is iterated in the live session. A later step could recompute the totals in code.
- [A prompt edit invalidates the cache] → Expected. The cache refills on the next call, and the prompt stays deterministic.
- [Prices change or a different model is configured] → The cost is labelled as an estimate, and unknown models give `None`.
- [Haiku 5.5 thinking blocks or refusals] → Only `text` blocks are read, and refusals map to `IncompleteEstimationError`. Thinking counts toward `max_tokens`, and 16,000 leaves ample room.
- [The delivered model differs from what reviewers expect] → The default stays the course's `claude-haiku-4-5`. Haiku 5.5 is opt-in and documented in the README.
