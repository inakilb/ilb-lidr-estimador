# Spec

## Purpose

Defines how the estimator service loads its configuration: the sources and their precedence, the defaults (Anthropic as the default provider, and a model that follows the provider), value validation, how API keys are kept secret, cached access through `get_settings()`, and the committed `.env.example` template.

## Requirements

### Requirement: Settings loaded from environment and .env

`app/config.py` SHALL define a Pydantic `BaseSettings` class that reads `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `APP_ENV` and `LOG_LEVEL` from process environment variables and from a `.env` file at the repository root. Process environment variables SHALL take precedence over `.env`. Variable names SHALL be case-insensitive, and unknown variables SHALL be ignored.

#### Scenario: Values read from .env

- **WHEN** `.env` contains `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY=sk-test`
- **THEN** the settings expose provider `anthropic` and that API key

#### Scenario: Environment overrides .env

- **WHEN** `.env` contains `LOG_LEVEL=DEBUG` and the process environment has `LOG_LEVEL=INFO`
- **THEN** the settings expose log level `INFO`

### Requirement: Defaults

When a variable is unset or set to an empty value, the settings SHALL use these defaults: `LLM_PROVIDER=anthropic`, `APP_ENV=development`, `LOG_LEVEL=DEBUG`. When `LLM_MODEL` is unset or empty, it SHALL default to the provider's economy model: `gpt-4o-mini` for `openai` and `claude-haiku-4-5` for `anthropic`. API keys SHALL have no default.

#### Scenario: Only the Anthropic key is set

- **WHEN** only `ANTHROPIC_API_KEY` is set
- **THEN** provider is `anthropic`, model is `claude-haiku-4-5`, environment is `development` and log level is `DEBUG`

#### Scenario: Empty values in .env behave as unset

- **WHEN** `.env` is a copy of `.env.example` with only `ANTHROPIC_API_KEY` filled in
- **THEN** settings load with the defaults and no validation error

#### Scenario: Model follows the provider

- **WHEN** `LLM_PROVIDER=openai`, `OPENAI_API_KEY` is set and `LLM_MODEL` is unset
- **THEN** model is `gpt-4o-mini`

#### Scenario: Explicit model wins

- **WHEN** `LLM_MODEL=claude-sonnet-4-5` is set
- **THEN** model is `claude-sonnet-4-5` regardless of the provider default

### Requirement: Value validation

`LLM_PROVIDER` SHALL accept only `openai` or `anthropic`. `LOG_LEVEL` SHALL accept only `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. The API key of the selected provider SHALL be required. Any violation SHALL raise a validation error that names the offending variable.

#### Scenario: Unknown provider

- **WHEN** `LLM_PROVIDER=gemini`
- **THEN** loading the settings fails with an error mentioning `LLM_PROVIDER`

#### Scenario: Missing key for the selected provider

- **WHEN** `ANTHROPIC_API_KEY` is unset and `LLM_PROVIDER` is unset (defaults to `anthropic`)
- **THEN** loading the settings fails with an error mentioning `ANTHROPIC_API_KEY`

#### Scenario: Key of the other provider not required

- **WHEN** `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY` is set and `OPENAI_API_KEY` is unset
- **THEN** settings load successfully

### Requirement: Secrets are not exposed

API keys SHALL never appear in source code. They SHALL be stored as secret values that are masked when the settings object is printed, logged or serialized.

#### Scenario: Printing the settings

- **WHEN** the settings object is converted to a string or its `repr` is logged
- **THEN** the output does not contain the API key values

#### Scenario: No keys in tracked files

- **WHEN** the tracked files of the repository are searched for API key values
- **THEN** no real key is found, and `.env.example` contains only empty values

### Requirement: Lazy, cached access

The settings SHALL be obtained through a `get_settings()` function that builds the instance on first call and returns the same instance afterwards. Importing `app.config` SHALL NOT read or validate the environment.

#### Scenario: Import without configuration

- **WHEN** `app.config` is imported in an environment with no `.env` and no variables set
- **THEN** the import succeeds

#### Scenario: Same instance

- **WHEN** `get_settings()` is called twice
- **THEN** both calls return the same object

### Requirement: Environment template and ignored secrets file

The repository SHALL contain a committed `.env.example` listing all six variables with empty values. `.env` SHALL be listed in `.gitignore`.

#### Scenario: Template is complete

- **WHEN** `.env.example` is read
- **THEN** it defines `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `APP_ENV` and `LOG_LEVEL`, each with an empty value

#### Scenario: .env is ignored

- **WHEN** `git check-ignore .env` is run
- **THEN** it reports `.env` as ignored
