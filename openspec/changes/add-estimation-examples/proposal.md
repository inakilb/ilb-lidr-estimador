# Proposal

## Why

Step 3 of the exercise: in a CAG architecture, the few-shot examples are the system's whole "knowledge". The model copies their structure, granularity, rates and ratios, so the quality of the estimations depends directly on them.

The course provides three examples, which are a good base, but they have problems:

- No hourly rate is stated, and one row in the landing page example uses a different, unexplained rate.
- Durations are padded compared with the hours.
- They have no assumptions, out-of-scope items, contingency, risks or VAT note.
- They cover only three kinds of project, none of them the WordPress websites and WooCommerce shops this estimator will mostly receive.

## What Changes

- Implement `app/context/examples.py` with `ESTIMATION_EXAMPLES`: 7 fictitious examples, each a `{meeting_summary, estimation}` dict as the course requires.
- Include the 3 course examples, fixed:
  - One explicit blended rate (62.5 EUR/h) applied to every row.
  - Durations recalculated from the hours and the team.
  - The new sections added.
- Add 4 new WordPress-based examples:
  - corporate website with 10+ sections, multilingual, with SEO and GDPR;
  - WooCommerce shop integrated with Correos or a multi-carrier service (shipping rates, labels, tracking, returns) and Redsys card payments;
  - WooCommerce shop with two-way sync to a physical store's POS system (stock, orders, click & collect) and Redsys card payments;
  - migration and redesign of a legacy site to WordPress (content migration, SEO redirects, performance).
- Every estimation follows one Markdown structure:
  - task table (hours and cost);
  - totals with subtotal, 15% contingency and total, prices excluding VAT;
  - assumptions, out of scope and risks;
  - recommended team;
  - duration.
- Examples are written in English, which uses fewer tokens. The instruction to answer in Spanish belongs to the system prompt in step 4, not to the examples.
- Keep the module data-only. The course's `format_examples_for_prompt` helper is not copied here, because building the prompt is step 4's job (`llm_service`).

## Capabilities

### New Capabilities

- `estimation-examples`: the static few-shot dataset injected into the prompt: its shape, size, coverage, format conventions and arithmetic consistency.

### Modified Capabilities

<!-- none -->

## Impact

- `app/context/examples.py`: the docstring placeholder is replaced by the dataset. Its size is roughly 5–6k tokens, which fits Claude Haiku's context window comfortably, and Anthropic prompt caching can reuse it in step 4.
- No new dependencies and no API changes. `llm_service` (step 4) is the only consumer.
- README.md: step 3 marked done, plus a short note on the examples and their conventions.
