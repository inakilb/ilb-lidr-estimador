"""Static few-shot context for the CAG architecture.

`ESTIMATION_EXAMPLES` holds past estimations that are injected verbatim into the
system prompt (see `app.services.llm_service`). The model imitates their structure,
granularity and figures, so every example follows the same conventions:

- Written in English to save tokens; the model is told to answer in Spanish.
- Fictitious clients; real third-party products and services may be named.
- Blended rate of 62.5 EUR/h on every task; all hour figures are even, so costs are
  whole euros.
- Contingency of 15% of the subtotal hours, rounded to the nearest even hour.
- All prices exclude VAT.
- Duration in weeks = ceil(total hours / (FTE x 30 productive hours per week)).
- Sections, in order: Task Breakdown, Totals, Assumptions, Out of Scope, Risks,
  Recommended Team, Estimated Duration.

This module is data only: building the prompt from it is done in `llm_service`.
"""

from typing import TypedDict


class EstimationExample(TypedDict):
    """A past estimation: what the client asked for, and the estimation produced."""

    meeting_summary: str
    estimation: str


ESTIMATION_EXAMPLES: list[EstimationExample] = [
    {
        "meeting_summary": (
            "The client needs an inventory management web platform for a mid-size warehouse "
            "operation. They want real-time stock tracking, automated reorder alerts when items "
            "fall below a configurable threshold, a role-based access system (admin, warehouse "
            "manager, viewer), CSV/Excel import and export of inventory data, and a dashboard "
            "with key metrics (turnover rate, stock value, low-stock items). They already have "
            "a PostgreSQL database running in AWS that we should integrate with. No mobile app "
            "is needed: the warehouse team will use tablets with the web interface."
        ),
        "estimation": """\
## Inventory Management Web Platform

### Task Breakdown

| Task | Hours | Cost (EUR) |
|------|------:|-----------:|
| Requirements analysis and technical design | 16 | 1,000 |
| Database schema design and migrations | 12 | 750 |
| Authentication and role-based access control | 20 | 1,250 |
| Product and stock CRUD API | 24 | 1,500 |
| Automated reorder alert engine | 16 | 1,000 |
| CSV/Excel import and export module | 14 | 875 |
| Dashboard with key metrics and charts | 20 | 1,250 |
| Frontend: inventory views and search/filter | 24 | 1,500 |
| Frontend: admin panel and user management | 12 | 750 |
| AWS PostgreSQL integration and deployment | 10 | 625 |
| Testing (unit, integration, E2E) | 20 | 1,250 |
| Code review, QA, and bug fixing | 12 | 750 |

### Totals

- **Subtotal:** 200 h, 12,500 EUR
- **Contingency (15%):** 30 h, 1,875 EUR
- **Total:** 230 h, 14,375 EUR
- **Blended rate:** 62.5 EUR/h
- All prices exclude VAT.

### Assumptions

- The existing AWS PostgreSQL database is accessible and its current schema is documented.
- Real-time means updates visible within a few seconds (polling or websockets), not hardware integration.
- The client provides sample CSV/Excel files and the reorder rules per product category.
- Hosting runs on the client's existing AWS account.

### Out of Scope

- Barcode scanners, RFID or other hardware integration.
- Native mobile apps.
- Integration with ERP, accounting or purchasing systems.
- Ongoing hosting costs and maintenance after launch.

### Risks

- Legacy data quality in the existing database may require cleanup before migration.
- Reorder rules may grow more complex than a single threshold per item.
- Tablet browsers in the warehouse may need extra compatibility testing.

### Recommended Team

- 1 Senior Full-Stack Developer (lead) (1.0 FTE)
- 1 QA Engineer (0.5 FTE)

### Estimated Duration

**6 weeks** with 1.5 FTE (230 h at 30 productive hours per FTE per week).""",
    },
    {
        "meeting_summary": (
            "A real estate agency wants a high-conversion landing page to capture leads for "
            "luxury property listings. The page should feature a hero section with a video "
            "background, a curated property gallery with filtering by price range and location, "
            "a lead capture form, and client testimonials. All leads must be pushed in real "
            "time to their existing HubSpot CRM via the API. The design must be responsive, "
            "mobile-first, and follow their brand guidelines (they will provide a Figma file). "
            "They also want basic analytics integration with Google Tag Manager and Meta Pixel "
            "for ad campaign tracking."
        ),
        "estimation": """\
## Real Estate Landing Page with CRM Integration

### Task Breakdown

| Task | Hours | Cost (EUR) |
|------|------:|-----------:|
| Requirements review and UX analysis | 8 | 500 |
| UI design adaptation from Figma to code | 16 | 1,000 |
| Hero section with video background | 8 | 500 |
| Property gallery with filtering | 16 | 1,000 |
| Lead capture form with validation | 8 | 500 |
| HubSpot CRM API integration | 14 | 875 |
| Testimonials carousel component | 6 | 375 |
| Google Tag Manager and Meta Pixel setup | 6 | 375 |
| Responsive design and cross-browser testing | 10 | 625 |
| Performance optimization (Core Web Vitals) | 8 | 500 |
| Deployment and DNS configuration | 4 | 250 |

### Totals

- **Subtotal:** 104 h, 6,500 EUR
- **Contingency (15%):** 16 h, 1,000 EUR
- **Total:** 120 h, 7,500 EUR
- **Blended rate:** 62.5 EUR/h
- All prices exclude VAT.

### Assumptions

- The Figma file is final and covers desktop and mobile layouts.
- The client provides the video, property photos, texts and testimonials.
- The property list is curated by hand (up to 30 listings), not synced from a listings feed.
- HubSpot API access and the target lead properties are set up by the client.

### Out of Scope

- Integration with a property listings portal or MLS feed.
- Ad campaign setup and management.
- Copywriting, photography and video production.
- Multiple languages.

### Risks

- A heavy background video can hurt Core Web Vitals on mobile.
- HubSpot rate limits or custom property changes can break the lead sync.
- Cookie consent rules may delay tracking pixels until the user accepts.

### Recommended Team

- 1 Senior Frontend Developer (1.0 FTE)
- 1 UI/UX Designer (0.5 FTE)

### Estimated Duration

**3 weeks** with 1.5 FTE (120 h at 30 productive hours per FTE per week).""",
    },
    {
        "meeting_summary": (
            "A B2B startup is building a SaaS platform to manage software subscriptions for "
            "SMEs. Core features include: user registration and company onboarding, a dashboard "
            "showing all active subscriptions with renewal dates and monthly spend, the ability "
            "to add/edit/cancel subscriptions, integration with Stripe for payment processing "
            "and invoice generation, a notification system (email alerts 30/7/1 days before "
            "renewal), and an admin panel to manage customer accounts. They want a REST API "
            "with a React frontend. MVP scope: they plan to iterate after launch."
        ),
        "estimation": """\
## SaaS Subscription Management Platform (MVP)

### Task Breakdown

| Task | Hours | Cost (EUR) |
|------|------:|-----------:|
| Architecture design and project setup | 12 | 750 |
| User registration and authentication (JWT) | 16 | 1,000 |
| Company onboarding flow | 12 | 750 |
| Subscription CRUD API and data model | 20 | 1,250 |
| Dashboard: active subscriptions and spend analytics | 24 | 1,500 |
| Stripe integration: payments and invoices | 28 | 1,750 |
| Email notification system (renewal reminders) | 16 | 1,000 |
| Admin panel for customer management | 20 | 1,250 |
| React frontend: views, forms, and routing | 40 | 2,500 |
| API documentation (OpenAPI/Swagger) | 6 | 375 |
| Testing (unit, integration, Stripe sandbox) | 24 | 1,500 |
| Deployment, CI/CD pipeline, and staging env | 16 | 1,000 |
| Security audit and hardening | 10 | 625 |

### Totals

- **Subtotal:** 244 h, 15,250 EUR
- **Contingency (15%):** 36 h, 2,250 EUR
- **Total:** 280 h, 17,500 EUR
- **Blended rate:** 62.5 EUR/h
- All prices exclude VAT.

### Assumptions

- MVP scope is frozen for this estimate; new features go to a later iteration.
- Subscriptions are entered manually by users; no automatic discovery from bank or card data.
- Stripe account and transactional email provider are set up by the client.
- Single language (English) and a single currency (EUR).

### Out of Scope

- Mobile apps.
- Automatic import of subscriptions from bank statements or SaaS vendors.
- Multi-currency, tax calculation by country and accounting integrations.
- Visual design beyond a standard UI component library.

### Risks

- Stripe edge cases (failed payments, proration, refunds) often take longer than planned.
- Email deliverability may require domain setup (SPF, DKIM) on the client side.
- MVP scope creep during development is common in early-stage startups.

### Recommended Team

- 1 Senior Full-Stack Developer (lead) (1.0 FTE)
- 1 Mid-level Frontend Developer (0.5 FTE)
- 1 QA Engineer (0.5 FTE)

### Estimated Duration

**5 weeks** with 2.0 FTE (280 h at 30 productive hours per FTE per week).""",
    },
    {
        "meeting_summary": (
            "An engineering consultancy based in Bilbao wants to replace its outdated corporate "
            "website with a new WordPress site in Spanish, English and Basque. The site needs "
            "12 sections: Home, About Us, Services (overview plus 5 service pages), Industries, "
            "Case Studies, Team, Blog, News and Press, Careers (job listings with CV upload), "
            "FAQ, Contact (form and map) and Legal pages (legal notice, privacy and cookies). "
            "They want a custom design that matches their new brand book, easy editing for the "
            "marketing team, good SEO, GDPR-compliant cookie consent and fast loading. The "
            "client will provide all texts and images, already translated."
        ),
        "estimation": """\
## Multilingual Corporate Website (WordPress, 12 Sections)

### Task Breakdown

| Task | Hours | Cost (EUR) |
|------|------:|-----------:|
| Discovery, sitemap and content architecture | 12 | 750 |
| UI/UX design: wireframes and Figma mockups (desktop and mobile) | 40 | 2,500 |
| WordPress setup, staging environment and custom block theme base | 16 | 1,000 |
| Reusable Gutenberg blocks and patterns | 32 | 2,000 |
| Page templates for the 12 sections | 36 | 2,250 |
| Blog, news and case studies (custom post types, archives, filters) | 18 | 1,125 |
| Careers: job listings and application form with CV upload | 14 | 875 |
| Contact form and map | 6 | 375 |
| Multilingual setup with WPML (3 languages) | 16 | 1,000 |
| Content loading in 3 languages | 24 | 1,500 |
| On-page SEO (Yoast, schema markup, sitemaps) | 10 | 625 |
| GDPR: cookie consent, legal pages and form consent | 6 | 375 |
| Performance optimization and caching | 8 | 500 |
| Accessibility review (WCAG 2.1 AA basics) | 8 | 500 |
| Responsive and cross-browser QA | 12 | 750 |
| Deployment, editor training and handover documentation | 8 | 500 |

### Totals

- **Subtotal:** 266 h, 16,625 EUR
- **Contingency (15%):** 40 h, 2,500 EUR
- **Total:** 306 h, 19,125 EUR
- **Blended rate:** 62.5 EUR/h
- All prices exclude VAT.

### Assumptions

- The brand book (logo, colors, typography) is final.
- The client delivers all texts already translated into the 3 languages, and the images.
- Up to 2 rounds of design revisions.
- Hosting is managed WordPress hosting contracted by the client.
- Existing blog content is not migrated (fewer than 10 posts are recreated manually).

### Out of Scope

- Copywriting, translation and photography.
- Migration of content from the old website.
- CRM or marketing automation integration.
- Hosting, domain and premium plugin licenses (WPML, form plugin), billed separately.

### Risks

- Late delivery of translated content is the most common cause of delay in multilingual sites.
- Basque translations may change layouts (longer words), requiring design adjustments.
- Stakeholder feedback from several departments can extend design approval.

### Recommended Team

- 1 WordPress Developer (1.0 FTE)
- 1 UI/UX Designer (0.5 FTE)
- 1 QA and Content Specialist (0.5 FTE)

### Estimated Duration

**6 weeks** with 2.0 FTE (306 h at 30 productive hours per FTE per week).""",
    },
    {
        "meeting_summary": (
            "A regional industrial association runs its website on Joomla 3, which is no longer "
            "supported. The site has about 350 pages, 1,500 news items and 2,000 downloadable "
            "PDF documents, in Spanish and Basque. They want to migrate everything to WordPress "
            "with a refreshed design, keep their search engine rankings (every old URL must "
            "redirect to its new equivalent), improve loading speed, which is very poor today, "
            "and make the site easier for their two-person communications team to update."
        ),
        "estimation": """\
## Legacy Joomla Site Migration and Redesign to WordPress

### Task Breakdown

| Task | Hours | Cost (EUR) |
|------|------:|-----------:|
| Audit of the legacy site: content inventory, URLs and SEO baseline | 14 | 875 |
| Information architecture and sitemap redesign | 10 | 625 |
| UI/UX redesign in Figma (desktop and mobile) | 32 | 2,000 |
| WordPress setup and custom block theme | 24 | 1,500 |
| Page templates and reusable blocks | 28 | 1,750 |
| Migration scripts: pages, news, categories and authors | 24 | 1,500 |
| Media and PDF document library migration | 12 | 750 |
| Bilingual content migration (Spanish and Basque, Polylang) | 14 | 875 |
| Content cleanup and manual fixes after migration | 16 | 1,000 |
| 301 redirect map and implementation | 12 | 750 |
| SEO preservation: metadata, sitemaps and Search Console | 8 | 500 |
| Performance optimization (Core Web Vitals, caching, CDN) | 12 | 750 |
| Accessibility review | 8 | 500 |
| QA: content checks, broken link scan and cross-browser tests | 16 | 1,000 |
| Launch, DNS switch and 2 weeks of post-launch monitoring | 10 | 625 |
| Editor training and documentation | 6 | 375 |

### Totals

- **Subtotal:** 246 h, 15,375 EUR
- **Contingency (15%):** 36 h, 2,250 EUR
- **Total:** 282 h, 17,625 EUR
- **Blended rate:** 62.5 EUR/h
- All prices exclude VAT.

### Assumptions

- Full database and file access to the Joomla site is provided.
- Content is migrated as is; editorial rewriting is done by the client.
- Joomla extensions with custom data (forms, directories) are limited to standard articles and categories.
- Up to 2 rounds of design revisions.

### Out of Scope

- Members area or private content migration.
- Rewriting or translating content.
- New features not present in the current site.
- Hosting, domain and premium plugin licenses.

### Risks

- Old Joomla extensions may store content in non-standard tables, adding migration effort.
- Broken internal links and embedded HTML in old news items need manual cleanup.
- A temporary ranking dip is possible after launch even with full redirects.

### Recommended Team

- 1 WordPress Developer (1.0 FTE)
- 1 UI/UX Designer (0.5 FTE)
- 1 QA and Content Specialist (0.5 FTE)

### Estimated Duration

**5 weeks** with 2.0 FTE (282 h at 30 productive hours per FTE per week).""",
    },
    {
        "meeting_summary": (
            "A Valencia-based olive oil producer wants to start selling online in Spain and "
            "Portugal with a WooCommerce shop of about 150 products (several bottle sizes and "
            "gift packs). Payments must go through Redsys with cards and Bizum, since their "
            "bank provides it. Shipping is handled by Correos: shipping rates must be "
            "calculated at checkout by weight and destination, labels generated and printed in "
            "bulk from the admin panel, tracking sent automatically to customers, and returns "
            "managed with a prepaid Correos return label. They need correct VAT handling, PDF "
            "invoices, customer accounts and a design that conveys a premium product."
        ),
        "estimation": """\
## WooCommerce Shop with Correos Shipping and Redsys Payments

### Task Breakdown

| Task | Hours | Cost (EUR) |
|------|------:|-----------:|
| Discovery: catalog, shipping and payment requirements | 10 | 625 |
| UI design: premium theme adaptation and key templates | 24 | 1,500 |
| WordPress and WooCommerce setup, theme customization | 20 | 1,250 |
| Catalog structure: variants, attributes and gift packs | 12 | 750 |
| Product import (150 products from client CSV) | 8 | 500 |
| Cart and checkout customization | 12 | 750 |
| Customer accounts and order history | 6 | 375 |
| Redsys payment gateway (cards and Bizum): bank test environment and go-live | 14 | 875 |
| Correos integration: shipping rates at checkout by weight and zone | 16 | 1,000 |
| Correos label generation and bulk printing from admin | 12 | 750 |
| Shipment tracking and customer notification emails | 8 | 500 |
| Returns flow with Correos prepaid return label | 10 | 625 |
| Tax setup (VAT for Spain and Portugal, Canary Islands exclusion) and PDF invoices | 10 | 625 |
| Branded transactional emails | 4 | 250 |
| Legal pages, GDPR and cookie consent | 6 | 375 |
| SEO and performance optimization | 10 | 625 |
| End-to-end QA: test orders, payments and shipments | 16 | 1,000 |
| Deployment and shop management training | 8 | 500 |

### Totals

- **Subtotal:** 206 h, 12,875 EUR
- **Contingency (15%):** 30 h, 1,875 EUR
- **Total:** 236 h, 14,750 EUR
- **Blended rate:** 62.5 EUR/h
- All prices exclude VAT.

### Assumptions

- The client has an active Correos business contract with API credentials.
- The bank provides Redsys test and production credentials (merchant code, terminal, secret key).
- Product data, photos and descriptions come in a CSV prepared by the client.
- Shipping only to mainland Spain, the Balearic Islands and Portugal.

### Out of Scope

- Carriers other than Correos.
- Shipping to the Canary Islands, Ceuta, Melilla or outside Spain and Portugal.
- ERP or accounting software integration.
- Product photography and copywriting.
- Hosting, domain and premium plugin licenses.

### Risks

- Redsys activation depends on the bank's response times, which can delay go-live.
- Correos API credentials and contract setup can take weeks if not started early.
- Fragile goods (glass bottles) may need special packaging rules that affect rates.

### Recommended Team

- 1 WooCommerce Developer (1.0 FTE)
- 1 UI/UX Designer (0.5 FTE)

### Estimated Duration

**6 weeks** with 1.5 FTE (236 h at 30 productive hours per FTE per week).""",
    },
    {
        "meeting_summary": (
            "A fashion retailer with two physical stores in Zaragoza wants to open an online "
            "shop with WooCommerce, fully connected to the Lightspeed Retail POS they use in "
            "the stores. The POS is the master for products and prices (about 800 SKUs with "
            "sizes and colors). Stock must stay in sync both ways: an online sale must reduce "
            "store stock and a store sale must update the website within minutes. Online orders "
            "must appear in the POS. Customers should be able to buy online and pick up in a "
            "chosen store (click & collect), seeing stock per store. Card payments through "
            "Redsys (cards and Bizum). Home delivery uses simple flat rates by zone."
        ),
        "estimation": """\
## WooCommerce Shop Synced with In-Store POS and Redsys Payments

### Task Breakdown

| Task | Hours | Cost (EUR) |
|------|------:|-----------:|
| Discovery: POS API analysis and data mapping | 16 | 1,000 |
| UI design: theme adaptation and key templates | 24 | 1,500 |
| WordPress and WooCommerce setup, theme customization | 20 | 1,250 |
| Catalog structure: variants by size and color | 10 | 625 |
| Initial product import from the POS (800 SKUs) and mapping | 14 | 875 |
| POS to WooCommerce product and price sync | 20 | 1,250 |
| Two-way stock sync: webhooks and scheduled reconciliation | 32 | 2,000 |
| Online orders pushed to the POS | 18 | 1,125 |
| Click & collect: store selection, stock per store, pickup notifications | 20 | 1,250 |
| Sync conflict handling, retries, logs and admin alerts | 16 | 1,000 |
| Redsys payment gateway (cards and Bizum): bank test environment and go-live | 14 | 875 |
| Checkout, flat-rate shipping by zone, taxes and invoices | 12 | 750 |
| Legal pages, GDPR and cookie consent | 6 | 375 |
| SEO and performance optimization | 10 | 625 |
| QA: sync scenarios, test orders in sandbox and in stores | 26 | 1,625 |
| Deployment, store staff training and documentation | 10 | 625 |

### Totals

- **Subtotal:** 268 h, 16,750 EUR
- **Contingency (15%):** 40 h, 2,500 EUR
- **Total:** 308 h, 19,250 EUR
- **Blended rate:** 62.5 EUR/h
- All prices exclude VAT.

### Assumptions

- Lightspeed Retail API access (and a sandbox or test outlet) is available on the client's plan.
- The POS remains the single source of truth for products, prices and stock.
- Stock updates within 5 minutes are acceptable; true real time is not required.
- The bank provides Redsys test and production credentials.

### Out of Scope

- Unified loyalty program or customer accounts shared between POS and web.
- Carrier API integration (labels, tracking); shipping uses flat rates.
- Returns of online orders processed in stores.
- Product photography and copywriting.
- Hosting, domain, POS subscription and premium plugin licenses.

### Risks

- Overselling when the same item sells in store and online at the same moment; mitigated with stock buffers and reconciliation.
- POS API rate limits or changes can break the sync and require ongoing maintenance.
- Inconsistent product data in the POS (missing sizes or barcodes) slows the initial import.
- Redsys activation depends on the bank's response times.

### Recommended Team

- 1 Senior WooCommerce Developer (lead) (1.0 FTE)
- 1 UI/UX Designer (0.5 FTE)
- 1 QA Engineer (0.5 FTE)

### Estimated Duration

**6 weeks** with 2.0 FTE (308 h at 30 productive hours per FTE per week).""",
    },
]
