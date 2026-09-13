---
name: stripe-payments
description: "Building, reviewing, and debugging Stripe payment integrations, distilled from the live docs.stripe.com API reference and guides (fetched 2026-09, API version 2026-08-26.dahlia). Covers the mental model (Checkout Session → PaymentIntent → Charge; SetupIntent → PaymentMethod; Customer; Invoice → Subscription), choosing an integration (Stripe-hosted Checkout vs Elements with the Checkout Sessions API vs raw PaymentIntents + Payment Element — Stripe now recommends Checkout Sessions by default), the PaymentIntent/SetupIntent status machine (requires_payment_method → requires_action → processing → requires_capture → succeeded/canceled), webhook-driven fulfillment (signature verification on the raw body, 5-minute tolerance, duplicate/out-of-order delivery, 3-day live retries, checkout.session.completed + async_payment_succeeded, idempotent fulfill function), saving cards and off-session charges (setup_future_usage, off_session=true, authentication_required recovery), manual capture and authorization windows, subscriptions (incomplete 23-hour window, past_due/unpaid/paused, invoice.paid provisioning, invoice.created blocking finalization up to 72h), refunds/cancel vs refund, disputes and declines, Connect charge types (direct, destination, separate charges and transfers, application_fee_amount, on_behalf_of, reverse_transfer), and API conventions (secret/restricted/publishable keys, form-encoded v1 vs JSON v2, Stripe-Version pinning, error types, Idempotency-Key 24h, cursor pagination, expand depth 4, Search API eventual consistency, metadata 50/40/500 limits, rate limits 100/25 rps). Use when integrating Stripe payments or billing, writing a Stripe webhook handler, choosing between Checkout and PaymentIntents, handling 3DS/SCA or declines, implementing refunds/subscriptions/Connect payouts, debugging a Stripe API error or signature failure, or reviewing Stripe code for correctness and security."
license: MIT
---

# Stripe Payments

How to build a Stripe payments integration that is **correct under retries, redirects, async payment methods, and malicious input** — the four things that break naive integrations. Distilled from the live [API reference](https://docs.stripe.com/api) and guides (fetched 2026-09; current API version `2026-08-26.dahlia`). Cross-links: [[secure-coding]] (keys, webhook trust boundary), [[cryptography]] (HMAC-SHA256 signature verification), [[cqrs-event-sourcing]] (webhooks as an event stream: at-least-once, unordered), [[nodejs]] / [[python]] / [[nextjs]] for the server side.

> **Freshness.** Stripe ships monthly API releases and renames client APIs. Treat exact function names and version strings here as a dated snapshot; when writing code against a real account, confirm against the SDK version actually installed (`Stripe-Version` is pinned per SDK release) and the live docs. Stripe also publishes its own agent skills and an MCP server (`stripe agent setup`) — complementary to this skill, which focuses on the *why* and the failure modes.

## The mental model

**Objects, not charges.** Modern Stripe never "creates a charge" directly. You create an *intent* and Stripe drives it through a state machine, creating the underlying `Charge` objects as attempts happen.

```
Checkout Session ──(mode=payment)──▶ PaymentIntent ──attempts──▶ Charge(s) ──▶ Refund(s) / Dispute
                 ──(mode=setup)────▶ SetupIntent  ──────────────▶ PaymentMethod (attached to Customer)
                 ──(mode=subscription)▶ Subscription ──each period──▶ Invoice ──▶ PaymentIntent
```

- **PaymentIntent** = "collect this amount from someone." Owns status, retries, 3DS, capture.
- **SetupIntent** = "save this payment method for later, no money now." Same status machine minus capture.
- **Checkout Session** = a higher-level wrapper that creates the intent/subscription for you and adds line items, tax, discounts, shipping, currency localization. Some features (Adaptive Pricing) exist *only* here.
- **Customer** (or, in preview, a customer-configured v2 `Account`) = the thing saved payment methods and subscriptions hang off. Store `cus_…` against your user record.
- **Event** = an immutable record of a state change, pushed to your webhook. *Events, not redirects, are the source of truth.*

**The client never decides money.** Amounts, prices, and what's being bought are computed server-side. The browser only ever receives a `client_secret` (scoped to one intent/session) and the **publishable** key.

## Choose the integration (decide this first)

| You want | Use | Complexity | Client confirm |
|---|---|---|---|
| Fastest path, Stripe-hosted page, redirect | **Checkout Session**, `ui_mode` default (hosted page), redirect to `session.url` | 2/5 | none — Stripe hosts it |
| Your own page/branding, Stripe handles tax/discounts/shipping | **Checkout Session** with `ui_mode: "elements"` + Payment Element | 3/5 | `checkout.confirm()` / `actions.confirm()` |
| Full control, you compute everything, or user explicitly asks | **PaymentIntent** + Payment Element | higher | `stripe.confirmPayment()` |
| Save a card now, charge later | **SetupIntent** (or Checkout `mode=setup`) | — | `stripe.confirmSetup()` |
| Recurring billing | **Checkout `mode=subscription`** (or Subscriptions API + Payment Element) | — | — |
| Marketplace / platform paying others | **Connect** + one of the three charge types | high | — |

Stripe's own current guidance: **prefer the Checkout Sessions API over Payment Intents for most integrations**; use raw PaymentIntents only when you need what Checkout can't do. Never use the legacy Charges API, Sources, Tokens, or the old Card Element for new work. Enable **dynamic payment methods** (don't hardcode `payment_method_types=[card]`; configure methods in the Dashboard / `automatic_payment_methods`).

Flow walkthroughs with code shapes: `references/payment-flows.md`.

## Non-negotiables (review checklist)

1. **Fulfill from webhooks, not from the success page.** Customers close tabs; bank debits settle days later. Handle `checkout.session.completed` **and** `checkout.session.async_payment_succeeded` (or `payment_intent.succeeded`). Optionally *also* run fulfillment on the landing page for speed — through the **same idempotent function**.
2. **Verify webhook signatures against the raw request body.** Any JSON parse/re-serialize by your framework breaks verification. Use the SDK's `constructEvent`/`construct_event`; never tolerance `0`. Exempt the route from CSRF, not from verification.
3. **Make fulfillment idempotent and concurrency-safe.** Events are delivered at least once, possibly concurrently, in any order. Dedupe on `event.id` and guard fulfillment on the business object (e.g. a unique constraint on `checkout_session_id`). Never use `event.created` for ordering.
4. **Return 2xx fast; process async.** Enqueue, then ack. Slow handlers time out and get retried (live: up to 3 days with backoff). For `invoice.created`, a non-2xx delays invoice finalization up to 72 hours.
5. **Idempotency-Key on every mutating POST** you might retry (SDKs do this when `maxNetworkRetries` > 0). Derive it from your own operation (cart ID, order ID) to also stop double-submits. Keys live 24h (v1).
6. **Secret keys only on the server, from a secrets vault/env.** Use **restricted keys** (`rk_live_…`) with least privilege in production. Publishable key (`pk_…`) is the only key in browser/mobile code. Pre-commit scan for `sk_live_` / `rk_live_`.
7. **Amounts are integers in the smallest currency unit** (`2000` = 20.00 USD; zero-decimal currencies like JPY are whole units). Never floats.
8. **Load Stripe.js from `js.stripe.com`** (don't bundle/self-host it — PCI). Card data never touches your server; that is what keeps you in the lightest PCI scope.
9. **Pin and match API versions.** Typed SDKs (Java, Go, .NET, and Node ≥12/Python ≥6/Ruby ≥9/PHP ≥11) pin the version of their release. Create webhook endpoints with the **same** API version, or event payload shapes won't match your types.
10. **Store Stripe IDs + your IDs in `metadata`** (`order_id`, `user_id`) so webhooks and 500-reconciliation can be joined back to your data. Never put secrets/PII like card data in metadata or `description`.

## Status machine you must handle

| PaymentIntent status | Meaning | Your move |
|---|---|---|
| `requires_payment_method` | New, **or a failed attempt returned here** (decline) | Collect/retry a payment method |
| `requires_confirmation` | PM attached, not confirmed (most integrations skip) | Confirm |
| `requires_action` | 3DS/redirect/next_action needed | Client handles `next_action` (Stripe.js does it in confirm) |
| `processing` | Async method (ACH, SEPA, BECS…) in flight — up to days | Wait for webhook; don't fulfill yet |
| `requires_capture` | Authorized, `capture_method=manual` | Capture before the auth expires (cards ≈7 days CIT; Visa MIT ~5 days) or cancel |
| `succeeded` | Money collected | Fulfill (idempotently) |
| `canceled` | Terminal; held funds released | Nothing more on this intent |

Cancel is possible before `processing`/`succeeded` (and during `processing` for some bank debits). **Uncaptured → cancel; captured → refund.**

## Top gotchas

- **Declines don't fail the PaymentIntent** — it drops back to `requires_payment_method`. Don't treat a decline as terminal; don't create a new PI per retry (you lose attempt history).
- **`checkout.session.completed` ≠ paid.** Check `payment_status` (`paid` / `unpaid` / `no_payment_required`). Delayed methods complete the session while `unpaid`.
- **Webhook payloads are snapshots at event time and never expanded.** Re-retrieve the object (with `expand`) when you need current or nested data (e.g. `line_items`).
- **Off-session charges can still demand authentication.** Catch `authentication_required`, email the customer, bring them back on-session with the declined PI's client secret.
- **Subscriptions start `incomplete`** when the first payment needs action or fails; after 23 hours they become `incomplete_expired` and you must create a new subscription.
- **`active` doesn't mean every invoice is paid**, and delayed-method subscriptions can be `active` while the PI is still `processing`.
- **API version drift renames fields.** E.g. from `2025-03-31.basil` an invoice's subscription lives at `parent.subscription_details.subscription`, not `invoice.subscription`.
- **Search is eventually consistent** (usually < 1 min). Never search right after a write; use list/retrieve.
- **A `500` is indeterminate.** The idempotent result is cached, so a retry with the same key returns the same 500; don't blindly retry with a new key — reconcile via webhooks + metadata.
- **Sandbox ≠ production for load tests** (25 rps vs 100 rps, mocked networks). Mock Stripe for load tests.

## References

- `references/api-conventions.md` — auth & key types, versioning, errors & retries, idempotency, pagination, expand, search, metadata, rate limits, v1 vs v2.
- `references/payment-flows.md` — hosted Checkout, Elements + Checkout Sessions, PaymentIntents + Payment Element, SetupIntents & off-session, manual capture.
- `references/webhooks-and-fulfillment.md` — endpoint setup, signature verification (library + manual), delivery semantics, the fulfill function, event catalog.
- `references/subscriptions.md` — lifecycle, statuses, invoice finalization, events, provisioning, portal.
- `references/refunds-disputes-declines.md` — cancel vs refund, refund states, disputes lifecycle and evidence, decline/advice codes.
- `references/connect.md` — charge types, fees, on_behalf_of, refunds/disputes per type, onboarding.
- `references/testing.md` — test cards and `pm_card_*` tokens, 3DS, disputes, bank debits, Stripe CLI.
