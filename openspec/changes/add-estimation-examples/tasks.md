# Tasks

## 1. Dataset scaffolding

- [x] 1.1 Replace the placeholder in `app/context/examples.py` with a module docstring, the `EstimationExample` `TypedDict` and `ESTIMATION_EXAMPLES: list[EstimationExample]`
- [x] 1.2 Document the conventions in the docstring: English, blended rate 62.5 EUR/h, even hours, 15% contingency, prices exclude VAT, weeks = ceil(hours / (FTE × 30))

## 2. Course examples (fixed)

- [x] 2.1 Inventory management platform: keep the rows, add the totals with contingency, assumptions, out of scope, risks, team in FTE and a recalculated duration
- [x] 2.2 Real estate landing page: change the Figma row to 62.5 EUR/h (1,000 EUR), add the new sections and recalculate the totals and duration
- [x] 2.3 SaaS subscription MVP: add the new sections, and resize the team so the duration is plausible

## 3. New WordPress examples

- [x] 3.1 Corporate website with at least 10 sections, multilingual (WPML or Polylang), SEO, GDPR cookie consent
- [x] 3.2 WooCommerce shop integrated with Correos or a multi-carrier service: shipping rates at checkout, labels, tracking, returns, and Redsys card payments
- [x] 3.3 WooCommerce shop with two-way sync to a physical store's POS system: stock, orders, click & collect, and Redsys card payments
- [x] 3.4 Legacy site migration and redesign to WordPress: content migration, 301 redirects, performance

## 4. Verification

- [x] 4.1 Write a verification script in the scratchpad that imports `ESTIMATION_EXAMPLES` and checks every spec rule: shape, count, sections and their order, VAT note, row costs, subtotal, contingency, total, even hours, duration formula
- [x] 4.2 Fix every inconsistency until the script passes for all 7 examples
- [x] 4.3 Estimate the dataset size in tokens and report it
- [x] 4.4 Confirm `app.context.examples` imports cleanly and `uv run uvicorn app.main:app` still starts

## 5. Documentation

- [x] 5.1 Add a short "Contexto (ejemplos)" section to README.md (Spanish): what the examples are and their conventions
- [x] 5.2 Mark step 3 as done in the README.md status table
