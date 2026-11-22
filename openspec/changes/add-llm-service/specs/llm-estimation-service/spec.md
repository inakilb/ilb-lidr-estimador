# Spec

## ADDED Requirements

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

The system prompt SHALL be sent as a single content block marked with `cache_control: {"type": "ephemeral"}`. Its length SHALL be at least 4,096 tokens, the minimum cacheable prefix for `claude-haiku-4-5`.

#### Scenario: Prompt long enough to cache

- **WHEN** the system prompt tokens are counted for `claude-haiku-4-5`
- **THEN** the count is at least 4,096

#### Scenario: Second call reads from cache

- **WHEN** two estimations are generated less than 5 minutes apart
- **THEN** the second response reports `cache_read_input_tokens` greater than 0

### Requirement: Provider and model selection

The service SHALL use the provider and model from the settings (`LLM_PROVIDER`, `LLM_MODEL`). The `anthropic` provider SHALL be implemented. Selecting a provider that is not implemented yet (`openai`) SHALL raise `UnsupportedProviderError` without making any network call.

#### Scenario: Anthropic default

- **WHEN** the settings use the defaults
- **THEN** the request goes to Anthropic with model `claude-haiku-4-5`

#### Scenario: OpenAI not implemented yet

- **WHEN** `LLM_PROVIDER=openai` and an estimation is requested
- **THEN** `UnsupportedProviderError` is raised and no request is sent

### Requirement: Supported models

The service SHALL support `claude-haiku-4-5` (the default) and `claude-haiku-5-5`. Requests to `claude-haiku-5-5` SHALL include `output_config: {"effort": "low"}` and SHALL NOT set `thinking`, so that the model's default adaptive thinking applies at low effort. Requests to `claude-haiku-4-5` SHALL NOT include `effort` or `thinking`, because that model does not accept `effort` and thinking stays off. Any other configured model ID SHALL be sent without extra options.

#### Scenario: Haiku 4.5 request

- **WHEN** the model is `claude-haiku-4-5`
- **THEN** the request contains neither `output_config` nor `thinking`

#### Scenario: Haiku 5.5 request

- **WHEN** `LLM_MODEL=claude-haiku-5-5`
- **THEN** the request contains `output_config.effort` `low` and no `thinking` field, and the result's `model` is `claude-haiku-5-5`

#### Scenario: Thinking blocks ignored

- **WHEN** a response contains `thinking` blocks before the `text` blocks
- **THEN** `estimation` contains only the text of the `text` blocks

### Requirement: Estimation result

A successful call SHALL return an `EstimationResult` with:

- `estimation`: the text of the model's response;
- `model`: the configured model ID;
- `provider`;
- token usage: input, output, cache read and cache write tokens;
- `estimated_cost_usd`: the cost computed from the usage at the model's list prices (known for `claude-haiku-4-5` and `claude-haiku-5-5`), or `None` when the model has no known price.

#### Scenario: Successful estimation

- **WHEN** the model finishes normally (`stop_reason` is `end_turn`)
- **THEN** the result has a non-empty `estimation`, `model` `claude-haiku-4-5`, `provider` `anthropic`, the token counts, and a positive `estimated_cost_usd`

### Requirement: Error handling

The service SHALL turn failures into its own exceptions, all subclasses of `LLMServiceError`:

- `UnsupportedProviderError` when the provider is not implemented;
- `LLMUpstreamError` when the API or the connection fails, with a `retryable` flag that is true for rate limits, overload, server errors, timeouts and connection errors;
- `IncompleteEstimationError` when the response is truncated (`max_tokens`), refused (`refusal`) or contains no text.

Error messages and logs SHALL NOT contain the API key.

#### Scenario: Truncated response

- **WHEN** the response has `stop_reason` `max_tokens`
- **THEN** `IncompleteEstimationError` is raised

#### Scenario: Rate limited

- **WHEN** the API returns 429 after the SDK's own retries
- **THEN** `LLMUpstreamError` is raised with `retryable` true

#### Scenario: Invalid key

- **WHEN** the API returns 401
- **THEN** `LLMUpstreamError` is raised with `retryable` false, and its message does not contain the key
