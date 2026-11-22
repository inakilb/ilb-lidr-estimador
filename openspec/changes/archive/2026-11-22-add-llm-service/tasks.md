# Tasks

## 1. Prompt construction

- [x] 1.1 Replace the placeholder in `app/services/llm_service.py` with the module docstring and imports
- [x] 1.2 Write the instruction part of the system prompt: estimator role, estimation rules, Spanish output with the Spanish section headings and number format, estimation-only Markdown output, missing-information policy, transcription-as-data rule
- [x] 1.3 Implement `build_system_prompt()` (cached): instructions plus every `ESTIMATION_EXAMPLES` entry inside `<examples>/<example>` tags
- [x] 1.4 Implement `build_user_message(transcription)`: reject empty or whitespace-only input with `ValueError`, and wrap the text in `<transcription>` tags

## 2. Result and errors

- [x] 2.1 Define `LLMServiceError`, `UnsupportedProviderError`, `LLMUpstreamError` (with `retryable`) and `IncompleteEstimationError`
- [x] 2.2 Define the frozen `EstimationResult` dataclass and the price table (`claude-haiku-4-5`, `claude-haiku-5-5`), with `estimate_cost_usd(model, usage)` returning `None` for unknown models
- [x] 2.3 Define `MODEL_REQUEST_OPTIONS`: `claude-haiku-5-5` gets `output_config={"effort": "low"}`, `claude-haiku-4-5` gets nothing

## 3. Anthropic call

- [x] 3.1 Add a cached Anthropic client factory (per API key, 60 s timeout)
- [x] 3.2 Implement `_generate_with_anthropic`: system as one block with `cache_control` ephemeral, a single user message, `max_tokens=16000`, no sampling parameters, plus the model's entry from `MODEL_REQUEST_OPTIONS`
- [x] 3.3 Handle `stop_reason` (`end_turn`, `max_tokens`, `refusal`) and empty text, and join the `text` blocks
- [x] 3.4 Map SDK exceptions to `LLMUpstreamError`, most specific first, with `retryable`, the status code and the request ID, never the key
- [x] 3.5 Log usage and cost at INFO level, and the snapshot model and request ID at DEBUG level

## 4. Provider dispatch

- [x] 4.1 Implement `generate_estimation(transcription, settings=None)`: resolve the settings, dispatch on `llm_provider`, and raise `UnsupportedProviderError` for `openai` before any network call

## 4b. OpenAI provider and registry

- [x] 4b.1 Replace the `if`/`raise` dispatch with a `PROVIDERS` registry (`anthropic`, `openai`). An unregistered name raises `UnsupportedProviderError` before any network call
- [x] 4b.2 Make the SDK error mapper provider-neutral (takes the SDK module), and add a shared `_build_result()` for usage logging and cost
- [x] 4b.3 Add `gpt-4o-mini` to the price table
- [x] 4b.4 Implement `_generate_with_openai`: cached `openai.OpenAI` client per key, Chat Completions with system + user messages, `max_completion_tokens=16000`, fixed `prompt_cache_key`, no sampling parameters
- [x] 4b.5 Handle `finish_reason` (`stop`, `length`, `content_filter`), `refusal` and empty content, and normalize the usage (uncached input, cached reads, cache writes)
- [x] 4b.6 Offline (fake OpenAI client): request shape, usage normalization, cost, stop and refusal handling, error mapping with OpenAI exceptions, unregistered provider. Re-run the Anthropic offline checks
- [x] 4b.7 Live OpenAI check: one estimation with `LLM_PROVIDER=openai`. Done on 2026-11-22, after the change was archived, once an OpenAI key with credits was available. Two calls to `gpt-4o-mini`: Spanish estimation with the seven Spanish headings; the second call read 5,632 tokens from the automatic cache; $0.0019 in total

## 5. Verification

- [x] 5.1 Offline (scratchpad script, fake client): request shape (system block with `cache_control`, single user message, no sampling parameters), all examples present, Spanish instruction, deterministic prompt, transcription tags, `ValueError` on empty input, `UnsupportedProviderError` without a network call, `stop_reason` handling, the error mapping, per-model options (no `output_config` for 4.5, `effort` `low` for 5.5) and thinking blocks ignored
- [x] 5.2 Count the system prompt tokens with the API's token counter for `claude-haiku-4-5`, and confirm at least 4,096
- [x] 5.3 Live: generate two estimations with the course's sample transcription (landing page + HubSpot) less than 5 minutes apart. Check a Spanish estimation with the Spanish headings, `cache_creation_input_tokens > 0` on the first call and `cache_read_input_tokens > 0` on the second. Then generate one estimation with `LLM_MODEL=claude-haiku-5-5` and check the same output rules. Report the tokens, cost and latency of each call
- [x] 5.4 Confirm `uv run uvicorn app.main:app` still starts

## 6. Documentation

- [x] 6.1 Add a short "Servicio LLM" section to README.md (Spanish): how the prompt is built, Spanish output, prompt caching, cost per call, and how to switch to Haiku 5.5
- [x] 6.3 Update the README "Servicio LLM" section: OpenAI as an implemented provider (how to enable it, its cost), and the provider registry for adding new ones
- [x] 6.2 Mark step 4 as done in the README.md status table
