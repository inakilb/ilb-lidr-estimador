# Tasks

## 1. Prompt construction

- [ ] 1.1 Replace the placeholder in `app/services/llm_service.py` with the module docstring and imports
- [ ] 1.2 Write the instruction part of the system prompt: estimator role, estimation rules, Spanish output with the Spanish section headings and number format, estimation-only Markdown output, missing-information policy, transcription-as-data rule
- [ ] 1.3 Implement `build_system_prompt()` (cached): instructions plus every `ESTIMATION_EXAMPLES` entry inside `<examples>/<example>` tags
- [ ] 1.4 Implement `build_user_message(transcription)`: reject empty or whitespace-only input with `ValueError`, and wrap the text in `<transcription>` tags

## 2. Result and errors

- [ ] 2.1 Define `LLMServiceError`, `UnsupportedProviderError`, `LLMUpstreamError` (with `retryable`) and `IncompleteEstimationError`
- [ ] 2.2 Define the frozen `EstimationResult` dataclass and the price table (`claude-haiku-4-5`, `claude-haiku-5-5`), with `estimate_cost_usd(model, usage)` returning `None` for unknown models
- [ ] 2.3 Define `MODEL_REQUEST_OPTIONS`: `claude-haiku-5-5` gets `output_config={"effort": "low"}`, `claude-haiku-4-5` gets nothing

## 3. Anthropic call

- [ ] 3.1 Add a cached Anthropic client factory (per API key, 60 s timeout)
- [ ] 3.2 Implement `_generate_with_anthropic`: system as one block with `cache_control` ephemeral, a single user message, `max_tokens=16000`, no sampling parameters, plus the model's entry from `MODEL_REQUEST_OPTIONS`
- [ ] 3.3 Handle `stop_reason` (`end_turn`, `max_tokens`, `refusal`) and empty text, and join the `text` blocks
- [ ] 3.4 Map SDK exceptions to `LLMUpstreamError`, most specific first, with `retryable`, the status code and the request ID, never the key
- [ ] 3.5 Log usage and cost at INFO level, and the snapshot model and request ID at DEBUG level

## 4. Provider dispatch

- [ ] 4.1 Implement `generate_estimation(transcription, settings=None)`: resolve the settings, dispatch on `llm_provider`, and raise `UnsupportedProviderError` for `openai` before any network call

## 5. Verification

- [ ] 5.1 Offline (scratchpad script, fake client): request shape (system block with `cache_control`, single user message, no sampling parameters), all examples present, Spanish instruction, deterministic prompt, transcription tags, `ValueError` on empty input, `UnsupportedProviderError` without a network call, `stop_reason` handling, the error mapping, per-model options (no `output_config` for 4.5, `effort` `low` for 5.5) and thinking blocks ignored
- [ ] 5.2 Count the system prompt tokens with the API's token counter for `claude-haiku-4-5`, and confirm at least 4,096
- [ ] 5.3 Live: generate two estimations with the course's sample transcription (landing page + HubSpot) less than 5 minutes apart. Check a Spanish estimation with the Spanish headings, `cache_creation_input_tokens > 0` on the first call and `cache_read_input_tokens > 0` on the second. Then generate one estimation with `LLM_MODEL=claude-haiku-5-5` and check the same output rules. Report the tokens, cost and latency of each call
- [ ] 5.4 Confirm `uv run uvicorn app.main:app` still starts

## 6. Documentation

- [ ] 6.1 Add a short "Servicio LLM" section to README.md (Spanish): how the prompt is built, Spanish output, prompt caching, cost per call, and how to switch to Haiku 5.5
- [ ] 6.2 Mark step 4 as done in the README.md status table
