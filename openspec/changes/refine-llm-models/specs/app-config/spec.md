# Spec

## MODIFIED Requirements

### Requirement: Value validation

`LLM_PROVIDER` SHALL accept only `openai` or `anthropic`. `LOG_LEVEL` SHALL accept only `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. The API key of the selected provider SHALL be required. An explicitly set `LLM_MODEL` that clearly belongs to the other provider SHALL be rejected: a `claude-` model with `openai`, or a `gpt-` or `o<digit>` model with `anthropic`. Model names that match neither pattern SHALL be accepted. Any violation SHALL raise a validation error that names the offending variable.

#### Scenario: Unknown provider

- **WHEN** `LLM_PROVIDER=gemini`
- **THEN** loading the settings fails with an error mentioning `LLM_PROVIDER`

#### Scenario: Missing key for the selected provider

- **WHEN** `ANTHROPIC_API_KEY` is unset and `LLM_PROVIDER` is unset (defaults to `anthropic`)
- **THEN** loading the settings fails with an error mentioning `ANTHROPIC_API_KEY`

#### Scenario: Key of the other provider not required

- **WHEN** `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY` is set and `OPENAI_API_KEY` is unset
- **THEN** settings load successfully

#### Scenario: Model from the other provider

- **WHEN** `LLM_PROVIDER=openai`, `OPENAI_API_KEY` is set and `LLM_MODEL=claude-haiku-4-5`
- **THEN** loading the settings fails with an error mentioning `LLM_MODEL` and `LLM_PROVIDER`

#### Scenario: Unrecognized model name accepted

- **WHEN** `LLM_PROVIDER=openai`, `OPENAI_API_KEY` is set and `LLM_MODEL=my-custom-model`
- **THEN** settings load successfully
