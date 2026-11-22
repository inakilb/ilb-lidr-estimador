# Design

## Context

`app/context/examples.py` is a docstring placeholder from step 1. The course repository provides three examples, written in English, plus a `format_examples_for_prompt` helper. The user's copy is local course material and is not committed.

Reviewing them found these problems:

- The blended rate is implicit (62.5 EUR/h), and one row uses 50 EUR/h without explanation (landing page, "UI design adaptation", 16 h for 800 EUR).
- Durations are padded: about 7–10 h per person per week.
- There are no assumptions, scope limits, contingency, risks or VAT note.

The service targets a Spanish web agency profile: mostly WordPress and WooCommerce work, prices in EUR, local services such as Correos. Decisions agreed with the user: examples in English to save tokens, answers in Spanish (step 4), the 3 course examples fixed and kept, 4 new WordPress-based examples (the dataset is capped at 7 to keep the context small), no small change-request example.

## Goals / Non-Goals

**Goals:**

- A consistent dataset the model can imitate: one structure, one rate, one contingency rule, one duration rule.
- Coverage of the project types this estimator will see most: corporate sites, shops with logistics or POS integrations, migrations, plus the three custom-software course cases.
- Arithmetic that is correct and machine-checkable, so step 8 CI can reuse the check.

**Non-Goals:**

- Building the prompt from the examples, and instructing the model to answer in Spanish: step 4.
- Prompt caching: step 4, `cache_control` on the system prompt.
- Small change requests, mobile apps, membership/LMS and booking sites: left out for now at the user's request, to keep the context small.
- Perfect estimation quality. The live session iterates on the examples.

## Decisions

- **Keep the course data shape `{meeting_summary, estimation}` and add a `TypedDict`.** The shape is what the course checks. `EstimationExample(TypedDict)` documents it and lets type checkers catch mistakes. Alternative: Pydantic models. Rejected: the data is static and runtime validation adds nothing.
- **Put all structure inside the `estimation` Markdown, not in extra keys.** Assumptions, risks and the rest are part of what the model must produce, so the model should see them in the same format it is expected to write. Separate keys (`assumptions: list[str]`) would need a formatter, and the model would see a different shape than its output.
- **One fixed section order:** `Task Breakdown`, `Totals`, `Assumptions`, `Out of Scope`, `Risks`, `Recommended Team`, `Estimated Duration`. The cost comes first because the client reads it first. The caveats follow, so the numbers are never read without them.
- **Blended rate of 62.5 EUR/h on every row, stated in `Totals`.**
  - This keeps the course's own figures, so most existing row costs stay the same. Only the 50 EUR/h row is fixed: 16 h becomes 1,000 EUR.
  - Alternative: a rate card per role (senior, mid, designer, QA). More realistic, but it multiplies the arithmetic the model has to reproduce, and it raises the risk of inconsistent output. It can come later.
- **Even hour values everywhere.** 62.5 × an even number is a whole number of euros, so there are no cents. All course rows are already even. The contingency is rounded to the nearest even hour.
- **Contingency of 15% on the subtotal, shown as its own line.** A visible buffer is common practice in agencies and is honest with the client. Hiding it inside the task hours teaches the model to inflate tasks silently.
- **"Prices exclude VAT" stated in `Totals`.** Spanish B2B quotes are given without IVA (21%). An explicit note avoids ambiguity.
- **Duration formula: weeks = ceil(total hours / (FTE × 30)).**
  - The 30 productive hours per week allows for meetings and overhead.
  - Part-time roles count as 0.5 FTE.
  - The duration line states both numbers (e.g. `**4 weeks** with 2.5 FTE`), so the rule is visible and checkable.
  - When the formula gives an implausibly short duration for the course examples, the recommended team is resized, not the hours. For example, the SaaS MVP gets a smaller team, which gives a realistic calendar.
- **New examples range from about 100 to 320 total hours.** Together with the three course examples (about 120 to 280 h), this gives the model anchors at several sizes.
- **Redsys as the card payment gateway in both WooCommerce examples.** It is the standard gateway of Spanish banks, so it is what local clients ask for. Its integration effort is non-trivial: bank test environment, signature keys, notification URL and production activation with the bank. Including it teaches the model to estimate it as its own task.
- **Integrations named as real services, clients kept fictitious.** The estimates are only meaningful with real APIs (Correos, Packlink, Sendcloud, Redsys, Stripe, HubSpot) and real WordPress plugins (WooCommerce, WPML, Yoast). Company names are invented ("a Valencia-based olive oil producer").
- **Data only, no formatting helper.** `llm_service` owns how examples are rendered into the prompt. Keeping them apart lets step 4 change the format (XML tags, numbering) without touching the data.
- **A throwaway verification script for the arithmetic rules.** It parses each table and checks the spec rules. It runs during this change and is reusable as a CI test in step 8.

## Risks / Trade-offs

- [English examples, Spanish answers: the model may drift into English] → Step 4 adds an explicit "respond in Spanish" instruction. Verify it in step 7.
- [7 examples make the prompt long: about 5–6k tokens on every call] → Acceptable for CAG with Haiku, and step 4 can cache the system prompt.
- [Strong WordPress bias may push custom-software requests toward WordPress answers] → The three course examples remain as custom-software anchors, and the summaries make the technology choice explicit.
- [A single blended rate hides seniority differences] → Documented as a simplification. A rate card is a possible later iteration.
- [Fictitious figures may not match real market prices] → The live session exists to tune them. The structure matters more than the exact numbers now.
