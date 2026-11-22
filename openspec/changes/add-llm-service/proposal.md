# Proposal

## Why

Step 4 of the exercise is the core of the CAG architecture. Steps 2 and 3 built the configuration and the examples. This step turns a meeting transcription into an estimation by sending the static context and the transcription to the LLM in a single call. The endpoint (step 5) and the app (step 6) depend on it.

## What Changes

- Implement `app/services/llm_service.py`:
  - **System prompt:** the expert software estimator role, the estimation rules (rate, contingency, VAT, duration formula, structure), the instruction to answer in Spanish with Spanish section headings, and all 7 `ESTIMATION_EXAMPLES` injected verbatim.
  - **Messages:** the course pattern `[system]` → `[user]` (the transcription) → `[assistant]` (the estimation).
  - **Provider:** Anthropic. `claude-haiku-4-5` is the default (the course's model, taken from `LLM_MODEL`), and `claude-haiku-5-5` is supported as a tested alternative, selected with `LLM_MODEL=claude-haiku-5-5`. It is about 5–8× cheaper per estimation and follows instructions better, but has thinking on by default, so the service sends it `effort: low`. Selecting `openai` raises a clear "not implemented yet" error and makes no network call. OpenAI, and possibly Gemini, come later.
  - **Prompt caching:** the system prompt is identical on every call (about 6.5k tokens, above Haiku 4.5's 4,096-token minimum), so it is cached. Repeated calls read it at 10% of the input price and with lower latency.
  - **Result:** an `EstimationResult` with the estimation text, model, provider, token usage (including cache reads and writes) and an estimated cost in USD. Step 5 can expose these as extra response fields.
  - **Errors:** a small set of service errors (unsupported provider, upstream API failure, incomplete estimation) that step 5 maps to HTTP status codes. The API key never appears in logs or error messages.

## Capabilities

### New Capabilities

- `llm-estimation-service`: prompt construction, provider selection, the LLM call with prompt caching, the result shape, and error handling.

### Modified Capabilities

<!-- none -->

## Impact

- `app/services/llm_service.py`: the placeholder is replaced by the implementation. It reads `app.config.get_settings()` and `app.context.examples.ESTIMATION_EXAMPLES`.
- No new dependencies: the `anthropic` SDK (2.12) is already locked. The `openai` SDK stays installed for later.
- Cost: about $0.015 per estimation without caching, and about $0.009 with a cache hit, on Haiku 4.5 (about 6.7k input and about 1.5k output tokens). About $0.002–0.003 on Haiku 5.5. Verification makes 3 real calls (2 on Haiku 4.5, 1 on Haiku 5.5), under $0.05 in total.
- README.md: step 4 marked done, plus a short note on how the prompt is built.
