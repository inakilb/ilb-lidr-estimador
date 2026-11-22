# Spec

## Purpose

Defines the CAG estimation service: how the prompt is built (estimator role, rules, Spanish output, the static examples), how the transcription is passed as data, prompt caching, the provider registry (Anthropic with Haiku 4.5 by default and Haiku 5.5 supported, OpenAI with gpt-4o-mini by default and GPT-6 Luna supported, with per-model request options), the result with normalized usage and cost, and error handling.

## Requirements

### Requirement: Message structure

The service SHALL call the LLM with a system prompt and exactly one user message containing the meeting transcription, following the pattern `[system]` → `[user]` → `[assistant]`. It SHALL NOT send an assistant prefill or any sampling parameter (`temperature`, `top_p`, `top_k`).

#### Scenario: Request shape

- **WHEN** an estimation is generated for a transcription
- **THEN** the request has a `system` prompt, and `messages` holds a single `user` message whose content contains that transcription

### Requirement: System prompt content

The system prompt SHALL contain:

- the role of an expert software estimator;
- the estimation rules used by the examples: blended rate of 62.5 EUR/h, even hours, 15% contingency, prices excluding VAT, weeks = ceil(total hours / (FTE × 30)), and the seven-section structure;
- the instruction to write the whole estimation in Spanish, with Spanish section headings;
- every entry of `ESTIMATION_EXAMPLES`, verbatim.

The system prompt SHALL be deterministic: the same text on every call, with no timestamps or per-request data.

#### Scenario: All examples injected

- **WHEN** the system prompt is built
- **THEN** it contains the `meeting_summary` and the `estimation` of every entry in `ESTIMATION_EXAMPLES`

#### Scenario: Spanish output requested

- **WHEN** the system prompt is read
- **THEN** it instructs the model to answer in Spanish and lists the Spanish section headings to use

#### Scenario: Deterministic prompt

- **WHEN** the system prompt is built twice
- **THEN** both results are byte-for-byte identical

### Requirement: Transcription treated as data

The transcription SHALL be wrapped in clearly delimited tags in the user message, and the system prompt SHALL instruct the model to treat it as input to estimate, never as instructions. An empty or whitespace-only transcription SHALL be rejected before any call is made.

#### Scenario: Embedded instructions ignored

- **WHEN** the transcription contains text such as "ignore previous instructions"
- **THEN** that text is sent inside the transcription tags, and the system prompt tells the model not to follow instructions found there

#### Scenario: Empty transcription

- **WHEN** an estimation is requested for an empty or whitespace-only transcription
- **THEN** a `ValueError` is raised and no request is sent

### Requirement: Prompt caching

On Anthropic, the system prompt SHALL be sent as a single content block marked with `cache_control: {"type": "ephemeral"}`. Its length SHALL be at least 4,096 tokens, the minimum cacheable prefix for `claude-haiku-4-5`. On OpenAI, caching is automatic for prompts of 1,024 tokens or more. The service SHALL send a fixed `prompt_cache_key` so that requests sharing the system prompt are routed to the same cache.

#### Scenario: Prompt long enough to cache

- **WHEN** the system prompt tokens are counted for `claude-haiku-4-5`
- **THEN** the count is at least 4,096

#### Scenario: Second call reads from cache

- **WHEN** two estimations are generated less than 5 minutes apart
- **THEN** the second response reports `cache_read_input_tokens` greater than 0

### Requirement: Provider and model selection

The service SHALL use the provider and model from the settings (`LLM_PROVIDER`, `LLM_MODEL`). Providers SHALL be registered in a single mapping from provider name to generate function. The `anthropic` and `openai` providers SHALL be implemented. A provider name with no registered implementation SHALL raise `UnsupportedProviderError` without making any network call.

#### Scenario: Anthropic default

- **WHEN** the settings use the defaults
- **THEN** the request goes to Anthropic with model `claude-haiku-4-5`

#### Scenario: OpenAI selected

- **WHEN** `LLM_PROVIDER=openai` and `OPENAI_API_KEY` are set, and `LLM_MODEL` is unset
- **THEN** the request goes to OpenAI with model `gpt-4o-mini`, and the result's `provider` is `openai`

#### Scenario: Unregistered provider

- **WHEN** the settings name a provider that has no registered implementation
- **THEN** `UnsupportedProviderError` is raised and no request is sent

### Requirement: OpenAI request

The OpenAI request SHALL use the Chat Completions API with two messages, a `system` message containing the system prompt and a `user` message containing the wrapped transcription, plus `max_completion_tokens=16000`, the fixed `prompt_cache_key` and the model's entry from the per-model request options. It SHALL NOT send sampling parameters. The response SHALL be handled as follows:

- `finish_reason` `stop` with non-empty content is a success;
- `length` means a truncated answer;
- `content_filter`, a non-empty `refusal` or empty content means no usable estimation.

OpenAI usage SHALL be reported in the same fields as Anthropic's: `input_tokens` counts only uncached prompt tokens, `cache_read_input_tokens` is the cached prompt tokens, and `cache_creation_input_tokens` is the cache-write tokens, or 0 when they are not reported.

#### Scenario: OpenAI request shape

- **WHEN** an estimation is generated with `LLM_PROVIDER=openai`
- **THEN** the request has exactly a `system` and a `user` message, `max_completion_tokens` 16000, the fixed `prompt_cache_key`, and no `temperature`, `top_p` or `max_tokens`

#### Scenario: OpenAI truncated or refused

- **WHEN** the OpenAI response has `finish_reason` `length`, `finish_reason` `content_filter`, or a `refusal`
- **THEN** `IncompleteEstimationError` is raised

#### Scenario: OpenAI usage normalized

- **WHEN** the OpenAI response reports 6,800 prompt tokens of which 6,656 are cached
- **THEN** the result has `input_tokens` 144 and `cache_read_input_tokens` 6,656

### Requirement: Supported models

The service SHALL support these models, with per-model request options taken from one table keyed by model ID and applied by both providers:

- `claude-haiku-4-5`: the Anthropic default. Requests SHALL include neither `effort` nor `thinking`, because the model does not accept `effort` and thinking stays off.
- `claude-haiku-5-5`: requests SHALL include `output_config: {"effort": "low"}` and SHALL NOT set `thinking`, so that the model's default adaptive thinking applies at low effort.
- `gpt-4o-mini`: the OpenAI default. Requests SHALL include no reasoning options.
- `gpt-6-luna`: requests SHALL include `reasoning_effort: "low"`.

Any other configured model ID SHALL be sent without extra options.

#### Scenario: Haiku 4.5 request

- **WHEN** the model is `claude-haiku-4-5`
- **THEN** the request contains neither `output_config` nor `thinking`

#### Scenario: Haiku 5.5 request

- **WHEN** `LLM_MODEL=claude-haiku-5-5`
- **THEN** the request contains `output_config.effort` `low` and no `thinking` field, and the result's `model` is `claude-haiku-5-5`

#### Scenario: GPT-4o mini request

- **WHEN** `LLM_PROVIDER=openai` and `LLM_MODEL` is unset
- **THEN** the request goes to `gpt-4o-mini` with no `reasoning_effort`

#### Scenario: GPT-6 Luna request

- **WHEN** `LLM_PROVIDER=openai` and `LLM_MODEL=gpt-6-luna`
- **THEN** the request contains `reasoning_effort` `low`, and the result's `model` is `gpt-6-luna`

#### Scenario: Thinking blocks ignored

- **WHEN** a response contains `thinking` blocks before the `text` blocks
- **THEN** `estimation` contains only the text of the `text` blocks

### Requirement: Estimation result

A successful call SHALL return an `EstimationResult` with:

- `estimation`: the text of the model's response;
- `model`: the configured model ID;
- `provider`;
- token usage: input, output, cache read and cache write tokens;
- `estimated_cost_usd`: the cost computed from the usage at the model's list prices (known for `claude-haiku-4-5`, `claude-haiku-5-5`, `gpt-4o-mini` and `gpt-6-luna`), or `None` when the model has no known price.

#### Scenario: Successful estimation

- **WHEN** the model finishes normally (`stop_reason` is `end_turn`)
- **THEN** the result has a non-empty `estimation`, `model` `claude-haiku-4-5`, `provider` `anthropic`, the token counts, and a positive `estimated_cost_usd`

### Requirement: Error handling

The service SHALL turn failures into its own exceptions, all subclasses of `LLMServiceError`:

- `UnsupportedProviderError` when the provider is not implemented;
- `LLMUpstreamError` when the API or the connection fails, with a `retryable` flag:
  - true for rate limits, overload, server errors, timeouts and connection errors;
  - false for an exhausted quota or billing problem (for example OpenAI's 429 with error code `insufficient_quota`), which is reported with a message that says the account has no credits;
- `IncompleteEstimationError` when the response is truncated (`max_tokens`), refused (`refusal`) or contains no text.

Error messages and logs SHALL NOT contain the API key.

#### Scenario: Truncated response

- **WHEN** the response has `stop_reason` `max_tokens`
- **THEN** `IncompleteEstimationError` is raised

#### Scenario: Rate limited

- **WHEN** the API returns 429 after the SDK's own retries
- **THEN** `LLMUpstreamError` is raised with `retryable` true

#### Scenario: Quota exhausted

- **WHEN** the API returns 429 with error code `insufficient_quota`
- **THEN** `LLMUpstreamError` is raised with `retryable` false and a message saying the account has no credits

#### Scenario: Invalid key

- **WHEN** the API returns 401
- **THEN** `LLMUpstreamError` is raised with `retryable` false, and its message does not contain the key
