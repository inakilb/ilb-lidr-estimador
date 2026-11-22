# Spec

## Purpose

Defines the static few-shot dataset injected into the system prompt (CAG): its shape, size and coverage (3 course projects and 4 WordPress/WooCommerce projects), language, section structure, and the arithmetic and duration rules every estimation follows.

## Requirements

### Requirement: Dataset shape

`app/context/examples.py` SHALL define `ESTIMATION_EXAMPLES`, a list of dicts typed as `EstimationExample` (a `TypedDict`). Each dict SHALL have exactly two non-empty string keys: `meeting_summary` (what the client asked for in the meeting) and `estimation` (the resulting estimation in Markdown).

#### Scenario: Every entry has both fields

- **WHEN** `ESTIMATION_EXAMPLES` is imported
- **THEN** every entry has exactly the keys `meeting_summary` and `estimation`, both non-empty strings

#### Scenario: Data-only module

- **WHEN** `app.context.examples` is imported
- **THEN** it performs no I/O, reads no configuration, and defines no prompt-formatting function

### Requirement: Size and coverage

The dataset SHALL contain 7 examples. It SHALL include the three course projects (inventory management platform, real estate landing page with CRM integration, SaaS subscription management MVP) and four WordPress-based projects:

- a corporate website with at least 10 sections;
- a legacy site migration and redesign to WordPress;
- a WooCommerce shop integrated with Correos or a multi-carrier shipping service;
- a WooCommerce shop synchronized with a physical store's POS system.

Both WooCommerce shops SHALL take card payments through the Redsys payment gateway, and their task breakdowns SHALL include a Redsys integration task.

#### Scenario: Count

- **WHEN** `len(ESTIMATION_EXAMPLES)` is evaluated
- **THEN** it is 7

#### Scenario: Redsys in the e-commerce examples

- **WHEN** the task tables of the two WooCommerce examples are read
- **THEN** each one contains a task for the Redsys payment gateway integration

#### Scenario: Corporate website section count

- **WHEN** the corporate website example is read
- **THEN** its meeting summary lists at least 10 distinct site sections

### Requirement: Language and fictitious data

All example text SHALL be in English. Client names SHALL be fictitious or generic. Real third-party products and services (for example WordPress, WooCommerce, Correos, HubSpot, Stripe) MAY be named.

#### Scenario: English content

- **WHEN** any `meeting_summary` or `estimation` is read
- **THEN** it is written in English

### Requirement: Estimation structure

Every `estimation` SHALL start with a `##` title and contain these `###` sections, in this order: `Task Breakdown`, `Totals`, `Assumptions`, `Out of Scope`, `Risks`, `Recommended Team`, `Estimated Duration`.

- `Task Breakdown` SHALL be a Markdown table with the columns `Task`, `Hours` and `Cost (EUR)`.
- `Totals` SHALL state the subtotal, a 15% contingency, the total, the blended rate, and that prices exclude VAT.

#### Scenario: Sections present and ordered

- **WHEN** the `###` headings of any estimation are extracted
- **THEN** they are exactly the seven sections above, in that order

#### Scenario: VAT stated

- **WHEN** the `Totals` section of any estimation is read
- **THEN** it states that the amounts exclude VAT

### Requirement: Arithmetic consistency

Every estimation SHALL be arithmetically consistent:

- every task cost SHALL equal its hours × 62.5 EUR;
- the subtotal SHALL equal the sum of the task rows, in hours and in cost;
- the contingency SHALL be 15% of the subtotal hours, rounded to the nearest even number of hours, and costed at the same rate;
- the total SHALL equal subtotal plus contingency.

All hour figures SHALL be even numbers, so that every cost is a whole number of euros.

#### Scenario: Rows and totals add up

- **WHEN** the task table and totals of any estimation are parsed
- **THEN** row costs, subtotal, contingency and total satisfy the rules above

### Requirement: Duration consistent with effort

`Estimated Duration` SHALL state the number of weeks and the team size in FTE (full-time equivalents). The weeks SHALL equal the total hours divided by (FTE × 30 productive hours per week), rounded up.

#### Scenario: Duration matches hours and team

- **WHEN** the total hours, FTE and weeks of any estimation are parsed
- **THEN** weeks = ceil(total hours / (FTE × 30))
