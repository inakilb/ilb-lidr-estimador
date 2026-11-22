# Tasks

## 1. Models

- [ ] 1.1 Add `gpt-4o-mini: {}` and `gpt-6-luna: {"reasoning_effort": "low"}` to `MODEL_REQUEST_OPTIONS`, and update its comment (applied by both providers)
- [ ] 1.2 Apply `MODEL_REQUEST_OPTIONS.get(model, {})` in the OpenAI Chat Completions call
- [ ] 1.3 Add the `gpt-6-luna` price (0.10 / 0.50 / cache write 0.125 / cache read 0.01) and update the module docstring's provider list

## 2. Errors

- [ ] 2.1 In `_upstream_error`, detect an exhausted quota before the rate-limit branch (OpenAI `insufficient_quota` code, Anthropic "credit balance" message) and return `retryable=False` with a "no credits" message

## 3. Config

- [ ] 3.1 Add provider model-prefix rules next to `DEFAULT_MODELS` in `app/config.py`
- [ ] 3.2 In the `Settings` validator, reject an explicit `LLM_MODEL` that matches the other provider's prefixes, naming `LLM_MODEL` and `LLM_PROVIDER` and suggesting leaving it empty

## 4. Verification

- [ ] 4.1 Offline (scratchpad): re-run the existing service checks. Add `gpt-6-luna` options and cost, `gpt-4o-mini` with no options, quota errors for both SDKs (`retryable=False`, clear message), a genuine 429 still retryable
- [ ] 4.2 Config checks: re-run the step 2 config scenarios. Add a Claude model with `openai` rejected, a GPT model with `anthropic` rejected, a custom name accepted, and the current `.env` still loading with `anthropic`
- [ ] 4.3 Live: one estimation through the service with `LLM_PROVIDER=openai` and `LLM_MODEL=gpt-6-luna`. Check the Spanish output, the result's model and cost, and report the tokens
- [ ] 4.4 Confirm `uv run uvicorn app.main:app` still starts

## 5. Documentation

- [ ] 5.1 README: add `gpt-6-luna` to the providers table and the cost table, note that `gpt-4o-mini` is deprecated, and advise leaving `LLM_MODEL` empty so the model follows the provider
- [ ] 5.2 CLAUDE.md and `openspec/config.yaml`: mention `gpt-6-luna` as the opt-in OpenAI model
