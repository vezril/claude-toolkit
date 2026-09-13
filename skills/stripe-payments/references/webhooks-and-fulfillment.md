# Webhooks and fulfillment

Source: docs.stripe.com/webhooks, /checkout/fulfillment (hosted), /expand (webhooks note), /billing/subscriptions/webhooks. Fetched 2026-09.

## Why webhooks are mandatory

Redirects are unreliable (closed tab, lost connection), async methods settle days later, subscriptions renew with nobody present, and disputes/refund failures happen out of band. Stripe's docs state it directly: fulfilling only from the landing page is not reliable. **Webhooks are the source of truth; the landing page is a fast path into the same idempotent function.**

## Setting up an endpoint

- Public **HTTPS** URL (TLS 1.2/1.3, valid cert), accepts POST. Up to 16 webhook endpoints per account. Redirects (3xx) count as failures.
- Create in Workbench → Webhooks → *Create an event destination*, or `POST /v2/core/event_destinations` (`type: webhook_endpoint`, `event_payload: snapshot|thin`, `enabled_events`, `events_from: ["@self"]` or `["@accounts"]` for Connect). The signing secret `whsec_…` is shown once per endpoint and differs between sandbox and live.
- **Pick the API version** for the endpoint to match the version your SDK pins.
- **Subscribe only to the events you handle** — not `*`.
- **Snapshot events** (v1 resources): `data.object` is the object as it was at event time. **Thin events** (v2 resources, e.g. `v1.billing.meter.error_report_triggered`): minimal unversioned payload; fetch with `fetchRelatedObject()` / `fetchEvent()`; parse with `client.parseEventNotification(...)`. Thin events need a separate endpoint.
- Connect platforms: a "Connected accounts" destination receives events from connected accounts (direct charges, their customers, payouts); a "Your account" destination receives platform-owned objects (destination charges, separate charges and transfers). Many platforms need both. `event.account` / `context` identifies the account.
- Alternatives: Amazon EventBridge, Azure Event Grid destinations.
- Optional defense in depth: allowlist Stripe's webhook IPs (docs.stripe.com/ips). **Signature verification is still required.**

## Local development

```bash
stripe login
stripe listen --forward-to localhost:4242/webhook          # prints a whsec_ for this session
stripe listen --forward-connect-to localhost:4242/webhook  # Connect events
stripe listen --forward-thin-to localhost:4242/webhook --thin-events "*"
stripe trigger payment_intent.succeeded
stripe events resend evt_123 --webhook-endpoint=we_123     # up to 30 days old (Dashboard: 15 days)
```

## Signature verification

Library (recommended), Node/Express shape:

```js
// Must get the RAW body — not express.json()
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, req.headers['stripe-signature'], process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return res.status(400).send(`Webhook signature verification failed`);
  }
  queue.enqueue(event);          // durable queue; dedupe on event.id downstream
  res.sendStatus(200);           // ack fast
});
```

Common raw-body traps: Express global `express.json()` mounted before the route; Next.js App Router (use `await req.text()`); body-parsing middleware in serverless frameworks; API gateways that re-encode. Rails/Django: exempt the route from CSRF.

Manual verification (only if no SDK):

1. `Stripe-Signature: t=1492774577,v1=5257a8…,v0=6ffbb5…` — split on `,` then `=`. Keep `t` and **all `v1`** values; ignore every other scheme (`v0` is a fake test signature — accepting it enables downgrade attacks).
2. `signed_payload = t + "." + raw_body`.
3. `expected = HMAC_SHA256(key = whsec_secret, msg = signed_payload)`, hex.
4. Constant-time compare `expected` to each `v1`; accept if any matches **and** `now - t` is within tolerance.

- Library default tolerance **300 seconds**; never 0 (disables the replay check). Keep server clocks NTP-synced.
- Each delivery attempt (including retries) gets a fresh `t` and signature.
- Secret rotation ("Roll secret") can keep the old secret valid up to 24h; during overlap the header has one `v1` per active secret.

## Delivery semantics (design for these)

| Property | Consequence |
|---|---|
| **At least once** — duplicates happen, occasionally as two distinct Event objects | Dedupe on `event.id`; for the two-object case, also dedupe on `(data.object.id, event.type)`; business-level idempotency in fulfillment |
| **No ordering guarantee** (e.g. `invoice.paid` may precede `customer.subscription.created`) | Don't depend on order; don't use `created` (second resolution, ties). Retrieve missing related objects from the API |
| **Snapshot is frozen** at event time, in the endpoint's API version | Re-retrieve for current state; `expand` isn't applied to event payloads |
| **Retries**: live up to **3 days** with exponential backoff; sandbox 3 times over a few hours | Handler must be idempotent; a failing endpoint gets emailed about; disabled/deleted endpoints stop retries |
| **Timeouts count as failures** | Return 2xx before heavy work; process on a queue (renewal spikes at month start) |
| Manual resend doesn't cancel pending automatic retries | Still idempotent |

Delivery debugging (Workbench → endpoint → Event deliveries): unable to connect → not public; 3xx → register the final URL; 4xx → route/method/auth wrong; 5xx → your handler crashed; TLS error → cert chain; timeout → handler too slow.

## The fulfillment function (Checkout)

Contract: callable many times, concurrently, with the same session ID; does the work once.

```js
async function fulfillCheckout(sessionId) {
  // 1. Concurrency/idempotency guard on YOUR side, e.g.
  //    INSERT INTO fulfillments(session_id) ... ON CONFLICT DO NOTHING  → if no row inserted, return
  const session = await stripe.checkout.sessions.retrieve(sessionId, { expand: ['line_items'] });
  if (session.payment_status === 'unpaid') return;   // async method not settled yet (or failed)
  // 2. Fulfill line items (paginate line items if many)
  // 3. Record fulfillment status for sessionId (same transaction as the work where possible)
}

// Webhook worker
switch (event.type) {
  case 'checkout.session.completed':
  case 'checkout.session.async_payment_succeeded':
    await fulfillCheckout(event.data.object.id); break;
  case 'checkout.session.async_payment_failed':
    await notifyCustomerPaymentFailed(event.data.object); break;
}

// Landing page: GET /after-checkout?session_id=cs_...  → await fulfillCheckout(id); render result
```

`payment_status`: `paid`, `unpaid`, `no_payment_required` (e.g. 100% discount, trials, setup mode).

## Event catalog (what most integrations handle)

One-time payments
- `checkout.session.completed` — session submitted; check `payment_status`.
- `checkout.session.async_payment_succeeded` / `checkout.session.async_payment_failed` — delayed methods resolved.
- `checkout.session.expired` — abandoned; release inventory.
- `payment_intent.succeeded` / `payment_intent.processing` / `payment_intent.payment_failed` — PaymentIntents integrations.
- `payment_intent.amount_capturable_updated` — manual-capture authorization ready.
- `setup_intent.succeeded` — payment method saved.

Subscriptions (details in `subscriptions.md`)
- `invoice.paid` (provision/extend), `invoice.payment_failed`, `invoice.payment_action_required`, `invoice.created` (ack fast, blocks finalization), `invoice.finalized`, `invoice.finalization_failed`, `invoice.upcoming`.
- `customer.subscription.created` / `.updated` / `.deleted` / `.paused` / `.resumed` / `.trial_will_end`.
- `entitlements.active_entitlement_summary.updated`.

After payment
- `refund.created` / `refund.updated` / `refund.failed`, `charge.refunded`.
- `charge.dispute.created` / `.updated` / `.closed` / `.funds_withdrawn` / `.funds_reinstated`; `radar.early_fraud_warning.created`.

Connect
- `account.updated` (requirements/capabilities), `payout.failed`, `charge.updated` (check for skipped destination transfer: `transfer_data` null).
