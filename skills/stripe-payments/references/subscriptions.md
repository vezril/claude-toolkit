# Subscriptions (Stripe Billing)

Source: docs.stripe.com/billing/subscriptions/overview, /billing/subscriptions/webhooks. Fetched 2026-09.

## Objects

- **Product** (what you sell) → **Price** (amount, currency, `recurring[interval]` month/year/week/day, optional `lookup_key` so code refers to `standard_monthly` instead of a hardcoded `price_…` ID that differs between sandbox and live).
- **Customer** with a default payment method (`invoice_settings.default_payment_method` or `subscription.default_payment_method`).
- **Subscription** → each billing period generates an **Invoice** → which creates a **PaymentIntent**. Invoice and PI IDs are reachable from the subscription (`latest_invoice`).
- **Entitlements** (optional): features attached to products; Stripe maintains active entitlements per customer, so you can gate on those instead of hand-tracking status.

## Recommended build

1. Create Products/Prices (Dashboard or API), give Prices `lookup_key`s.
2. Checkout Session with `mode: 'subscription'`, `line_items: [{ price, quantity }]`, `success_url` with `{CHECKOUT_SESSION_ID}`, `customer` if you already have one. Checkout saves the payment method automatically.
3. Webhooks: on `checkout.session.completed` store the `customer` and `subscription` IDs against your user. Grant or extend access on `invoice.paid`. React to status changes via `customer.subscription.updated` / `.deleted`.
4. Self-service: create a **customer portal** session server-side (`stripe.billingPortal.sessions.create({ customer, return_url })`) and redirect to its `url`. Configure allowed actions (cancel, switch plan, update card) in the Dashboard portal settings.
5. Configure Smart Retries / dunning and the "after all retries fail" outcome in Dashboard billing settings.
6. Test renewals and trials with **test clocks** (simulated time).

Alternative (custom UI): Subscriptions API with `payment_behavior: 'default_incomplete'`, then confirm the first invoice's PaymentIntent client secret with the Payment Element.

## Statuses

| Status | Meaning | Access |
|---|---|---|
| `trialing` | In trial | Grant |
| `active` | Good standing. **Doesn't mean every invoice is paid** | Grant |
| `incomplete` | First payment failed / needs action / still processing. 23 hours to pay | Don't grant yet |
| `incomplete_expired` | First payment never succeeded within 23h; first invoice voided. Terminal | Create a new subscription |
| `past_due` | Latest finalized invoice failed or wasn't attempted; retries may run | Your policy (grace period + notify) |
| `unpaid` | Chosen outcome after retries exhausted; invoices still generate but aren't attempted | Revoke |
| `canceled` | Terminal; auto-collection disabled on open invoices; only metadata/cancellation_details editable | Revoke |
| `paused` | Trial ended without a payment method and `trial_settings.end_behavior.missing_payment_method=pause`; no invoices | Revoke until resumed |

Transitions to know:
- Creation with immediate payment: `incomplete` → `active` on payment. Customer returns after 23h → create a new subscription (and don't reuse the old Checkout session).
- `current_period_start` is set when the first invoice is created. Paying late doesn't shift it, so a slow 3DS completion leaves less of the first period.
- `past_due` → `active` by paying the latest invoice (or marking it uncollectible). After final retry → `canceled`, `unpaid`, or stays `past_due` per settings.
- Voided invoices don't affect status; status follows the most recent non-voided invoice.
- **Delayed payment methods** (ACH Direct Debit etc.) can go straight to `active` with the PI still `processing`. If the payment later fails, the invoice is voided but the subscription **stays `active`**. Build access control accordingly.
- Checkout: you can't update a subscription (or its invoice) while the session's subscription is `incomplete`. Wait for `checkout.session.completed`, or expire the session to cancel it.
- `collection_method: send_invoice` (emailed invoice with due date): starts `active` even while the first invoice is unpaid, and there's no `invoice.upcoming`.

Payment outcome → statuses (first invoice):

| Outcome | PaymentIntent | Invoice | Subscription |
|---|---|---|---|
| Success | `succeeded` | `paid` | `active` |
| Card error | `requires_payment_method` | `open` | `incomplete` |
| Needs authentication | `requires_action` | `open` | `incomplete` |

Invoice statuses: `draft` → `open` (finalized) → `paid` | `void` | `uncollectible`. Invoices for `unpaid` subscriptions pile up as drafts.

## Events and what to do

| Event | Action |
|---|---|
| `invoice.paid` | Provision/extend access (store an access-expiry timestamp + a day or two of leeway; check it on login) |
| `invoice.payment_failed` | Notify; collect new PM; update `default_payment_method`; rely on Smart Retries. `next_payment_attempt` shows the next retry |
| `invoice.payment_action_required` | Email customer to authenticate; on-session, `stripe.handleNextAction(pi.client_secret)`; confirm via `invoice.paid`, not the client callback |
| `invoice.created` | **Return 2xx promptly.** No successful response → auto-finalization delayed up to **72h** (then Stripe finalizes anyway). Stripe waits ~1h after success before charging; add invoice items in that window if needed. Applies to every endpoint on the account, including connected platforms' |
| `invoice.finalized` | Ready to pay/send |
| `invoice.finalization_failed` | Can't collect! Inspect `last_finalization_error`; with Stripe Tax check `automatic_tax.status` (`requires_location_inputs` → collect address; `failed` → retry later). Subscription stays active meanwhile |
| `invoice.upcoming` | N days before renewal (Dashboard setting); add one-off items |
| `customer.subscription.created` | May be `incomplete` |
| `customer.subscription.updated` | Plan change, renewal, status change. Revoke on `canceled`/`unpaid`; dunning on `past_due` |
| `customer.subscription.deleted` | Ended: revoke |
| `customer.subscription.trial_will_end` | 3 days before trial end (immediately if trial < 3 days): ensure a PM exists |
| `customer.subscription.paused` / `.resumed` | Trial-without-PM pause (not "pause payment collection") |
| `entitlements.active_entitlement_summary.updated` | Provision/deprovision features |

Mapping a refunded charge back to its subscription: `charge.payment_intent` → list InvoicePayments filtered by `payment.payment_intent` → `invoice` → from API `2025-03-31.basil` on, `invoice.parent.subscription_details.subscription` (older: `invoice.subscription`).

## Changes, cancellation, limits

- Upgrade/downgrade by updating subscription items (proration behaviour configurable); pause collection by setting `pause_collection` (invoices still generate); cancel now or at period end (`cancel_at_period_end`). Resubscribing after cancel needs a new subscription.
- Rate limits: 10 new invoices per subscription per minute, 20 per day; 200 quantity updates per subscription per hour.
- Test clock objects are omitted from "list all" calls; list scoped by `customer`, `subscription`, or `test_clock` to see them.
