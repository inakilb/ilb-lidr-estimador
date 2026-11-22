# Proposal

## Why

The live OpenAI check after step 4 brought up three things, before the endpoint (step 5) starts depending on the service:

- **A newer OpenAI model.** OpenAI marks `gpt-4o-mini`, the course's model, as deprecated. `gpt-6-luna` is current and cheaper per token ($0.10 / $0.01 cached / $0.50 per million tokens), and it produced a fully correct estimation in a probe call. The user wants the same arrangement as for Anthropic: the course model stays the default, and the newer model is supported as an option.
- **"No credits" reported as a temporary rate limit.** OpenAI returns HTTP 429 both for rate limits and for an exhausted quota (`insufficient_quota`). The service marked both retryable, so the SDK retried pointlessly, and step 5 would answer "try again later" for a billing problem.
- **Changing the provider without the model breaks the call.** With `LLM_MODEL=claude-haiku-4-5` in `.env`, setting only `LLM_PROVIDER=openai` sends a Claude model to OpenAI. The call fails with "model not found", far from the cause.

## What Changes

- **Support `gpt-6-luna`** as an opt-in OpenAI model (`LLM_MODEL=gpt-6-luna`), sent with `reasoning_effort: "low"`, and add its price. `gpt-4o-mini` stays the OpenAI default.
- **Apply `MODEL_REQUEST_OPTIONS` on OpenAI too.** The table is keyed by model ID, so it serves both providers: Haiku 5.5 gets `effort: low`, GPT-6 Luna gets `reasoning_effort: low`.
- **Map an exhausted quota to its own case:** `LLMUpstreamError(retryable=False)` with a "no credits / quota exhausted" message, for both SDKs (error code `insufficient_quota`, or a billing error). Genuine rate limits stay retryable.
- **Validate that the model matches the provider.** Loading the settings fails, naming `LLM_MODEL`, when an explicitly set model clearly belongs to the other provider: `claude-*` with `openai`, or `gpt-*` / `o<digit>*` with `anthropic`. Model names that match neither pattern are still accepted.
- Update the README and `CLAUDE.md` with the new model, its cost, and the `.env` advice (leave `LLM_MODEL` empty to follow the provider).

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `llm-estimation-service`:
  - **OpenAI request:** the model's request options are applied.
  - **Supported models:** `gpt-4o-mini` as the OpenAI default, `gpt-6-luna` with low reasoning effort.
  - **Estimation result:** a price for `gpt-6-luna`.
  - **Error handling:** an exhausted quota is not retryable.
- `app-config`:
  - **Value validation:** a model that belongs to the other provider is rejected.

## Impact

- `app/services/llm_service.py`: the options table and price table gain entries, the OpenAI call applies the options, and the error mapper detects an exhausted quota.
- `app/config.py`: a provider/model consistency check in the existing validator.
- No new dependencies and no API changes.
- Verification: offline checks, plus one live `gpt-6-luna` call through the service (about $0.001).
