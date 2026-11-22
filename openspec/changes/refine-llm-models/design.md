# Design

## Context

Step 4 (`add-llm-service`, archived) implemented two providers behind `PROVIDERS`. Per-model request options (`MODEL_REQUEST_OPTIONS`) were applied only on the Anthropic path. The live OpenAI check showed three things:

- An account with no credits gets `429 insufficient_quota`, which the service reported as a retryable rate limit.
- `.env` sets `LLM_MODEL="claude-haiku-4-5"` explicitly, so switching only the provider would send a Claude model to OpenAI.
- OpenAI marks `gpt-4o-mini` as deprecated, and `gpt-6-luna` is current.

Facts about `gpt-6-luna`, from developers.openai.com:

- $0.10 input, $0.01 cached input, $0.125 cache writes and $0.50 output, per million tokens.
- 1.05M context and 128K max output.
- A reasoning model with `reasoning_effort` from `none` to `max` (default `medium`).
- Supports Chat Completions.

A probe call with the service's exact request plus `reasoning_effort="low"` returned a fully correct Spanish estimation with 397 reasoning tokens, for about $0.0011.

## Goals / Non-Goals

**Goals:**

- `gpt-6-luna` selectable with `LLM_MODEL`, while `gpt-4o-mini` stays the OpenAI default (course model first, mirroring Haiku 4.5 and 5.5).
- One per-model options table that both providers apply.
- No pointless retries and no misleading "try later" for billing problems.
- Fail at startup, with a clear message, when the model and the provider don't match.

**Non-Goals:**

- Changing the default provider or model.
- Disabling the SDK's own retries for 429s: the SDK cannot tell quota errors from rate limits before raising, and 2 quick retries are harmless.
- HTTP status mapping: step 5.
- Other OpenAI models (`gpt-5.4-mini` and the other gpt-6 models): they can be added later with one row each.

## Decisions

- **`MODEL_REQUEST_OPTIONS` stays one table keyed by model ID, now applied by both providers.** Model IDs are unique across providers, so one table is simpler than one per provider. Entries:
  - `claude-haiku-5-5`: `{"output_config": {"effort": "low"}}`.
  - `gpt-6-luna`: `{"reasoning_effort": "low"}`. Low effort mirrors Haiku 5.5: the examples carry the structure, and low effort keeps reasoning tokens, cost and latency down. The probe showed it still checks the arithmetic.
  - `claude-haiku-4-5` and `gpt-4o-mini`: `{}`.
  - The options are passed as `**kwargs` on each SDK call, so the SDK rejects a misplaced option early instead of sending it silently.
- **Price entry for `gpt-6-luna`:** input 0.10, output 0.50, cache write 0.125, cache read 0.01. The output includes reasoning tokens, as OpenAI bills them.
- **Detecting an exhausted quota, inside the provider-neutral mapper and before the generic rate-limit branch:**
  - **OpenAI:** the error's `code` (or `body["error"]["code"]`) is `insufficient_quota`.
  - **Anthropic:** a low credit balance comes back as a 400 whose message mentions the "credit balance". It was already non-retryable; it now gets the same clear message.
  - Both give `LLMUpstreamError("... the LLM provider account has no credits (quota exhausted).", retryable=False)`.
  - The check reads attributes with `getattr` and plain dict lookups, so it works with either SDK and never fails while handling an error.
- **Provider/model consistency check in the existing `Settings` validator, before the model default is filled.** It runs only when `LLM_MODEL` is set explicitly:
  - `claude-` with `openai` is rejected.
  - `gpt-` or `^o\d` with `anthropic` is rejected.
  - Anything else is accepted, so custom or future names (proxies, fine-tunes) still work.
  - The error names both variables and suggests leaving `LLM_MODEL` empty to follow the provider.
  - Alternative: ignore a mismatched model and silently use the provider default. Rejected, because it hides a configuration mistake.
  - Prefix rules live next to `DEFAULT_MODELS` in `config.py`, so a new provider adds its prefixes there.
- **The user's `.env` is not edited.** The README explains the fix: leave `LLM_MODEL=` empty. With the new check, the current `.env` keeps working as long as the provider is `anthropic`. If the user switches to `openai`, they get a clear error that says what to change.

## Risks / Trade-offs

- [`gpt-4o-mini` is deprecated and could be retired] → `gpt-6-luna` is ready as a one-line switch, and the README says so.
- [Prefix heuristics misclassify a future model name] → Only the two well-known prefix families are checked, and unknown names pass.
- [Quota detection depends on error codes and messages that providers could change] → When detection misses, the old behavior remains (retryable rate limit, or a non-retryable 400), so nothing breaks; only the message is less clear.
- [Reasoning tokens make `gpt-6-luna` no cheaper per estimation than `gpt-4o-mini`] → Documented. The reasons to choose it are that it is current and its output quality, not price.
