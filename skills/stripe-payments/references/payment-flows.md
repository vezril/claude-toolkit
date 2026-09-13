# Payment flows

Source: docs.stripe.com/payments/accept-a-payment (hosted Checkout, Elements + Checkout Sessions, Payment Intents variants), /payments/paymentintents/lifecycle, /payments/save-and-reuse (Setup Intents), /payments/place-a-hold-on-a-payment-method. Fetched 2026-09. Code is shape-level Node/curl; adapt to the installed SDK version.

All flows share one rule: **the server builds the order and amount; the client gets only a `client_secret` or a redirect URL; fulfillment happens on webhooks** (see `webhooks-and-fulfillment.md`).

## 1. Stripe-hosted Checkout (default recommendation)

Server:

```js
const session = await stripe.checkout.sessions.create({
  mode: 'payment',                    // 'payment' | 'subscription' | 'setup'
  line_items: [
    { price: 'price_123', quantity: 1 },                 // a Price you created
    // or inline: { price_data: { currency: 'usd', product_data: { name: 'T-shirt' }, unit_amount: 2000 }, quantity: 1 }
  ],
  success_url: 'https://example.com/after-checkout?session_id={CHECKOUT_SESSION_ID}', // literal placeholder
  customer: 'cus_123',                // optional: prefill + link history (or customer_email)
  client_reference_id: order.id,      // your ID
  payment_intent_data: { metadata: { order_id: order.id } }, // metadata the PI/charge will carry
}, { idempotencyKey: `checkout-${order.id}` });
// respond: 303 redirect to session.url
```

- Sessions expire **24h** after creation by default.
- Payment methods are dynamic (Dashboard settings); Apple Pay/Google Pay work with no code.
- `integration_identifier` optionally labels a session for per-integration conversion metrics.
- With a `checkout.session.completed` webhook endpoint configured, Checkout waits **up to 10s** for your 2xx before redirecting to `success_url` — ack fast.
- Save the card for later during payment: `payment_intent_data[setup_future_usage]=off_session` (+ `customer_creation=always` if no customer). Let customers opt in to redisplay: `saved_payment_method_options[payment_method_save]=enabled`. Subscription mode saves automatically.
- Save without paying: `mode=setup`.
- Auth-only: `payment_intent_data[capture_method]=manual`.

## 2. Elements with the Checkout Sessions API (custom UI)

Server returns the session's `client_secret`:

```js
const session = await stripe.checkout.sessions.create({
  ui_mode: 'elements',
  mode: 'payment',
  line_items: [{ price: 'price_123', quantity: 1 }],
  return_url: 'https://example.com/return?session_id={CHECKOUT_SESSION_ID}',
});
res.json({ client_secret: session.client_secret });
```

Client (HTML/JS) — Stripe.js loaded from `https://js.stripe.com/dahlia/stripe.js` (npm `@stripe/stripe-js` ≥ 7 also fine; never self-host):

```js
const stripe = Stripe('pk_test_...');
const clientSecret = fetch('/create-checkout-session', { method: 'POST' })
  .then(r => r.json()).then(j => j.client_secret);

const checkout = stripe.initCheckoutElementsSdk({ clientSecret });
checkout.createPaymentElement().mount('#payment-element');
checkout.on('change', (session) => { payButton.disabled = !session.canConfirm; });

const loadActionsResult = await checkout.loadActions();
if (loadActionsResult.type === 'success') {
  const { actions } = loadActionsResult;
  // actions.getSession() -> lineItems, total.total.amount for your summary UI
  payButton.onclick = async () => {
    const result = await actions.confirm();
    if (result.type === 'error') showError(result.error.message);
  };
}
```

React: import from **`@stripe/react-stripe-js/checkout`** (react-stripe-js ≥ 5, stripe-js ≥ 8): wrap in `<CheckoutElementsProvider stripe={stripe} options={{ clientSecret }}>`, read state with `useCheckoutElements()` (`type: 'loading' | 'error' | 'success'`), render `<PaymentElement />`, confirm with `checkoutState.checkout.confirm()`.

- A valid customer email is required: `ContactDetailsElement`, or `customer_email` / `customer` on the session (not editable), or `defaultValues.email` (editable).
- Addresses: `BillingAddressElement` (`billing_address_collection=required`), `ShippingAddressElement` (`shipping_address_collection[allowed_countries]`).
- Display totals from the session object, so features like currency localization need no UI changes.
- Page must be HTTPS in live mode; don't nest the Payment Element in another iframe (redirect-based methods break). If you must, `allow="payment *"`.

## 3. PaymentIntents + Payment Element (only when you need it)

Server:

```js
const pi = await stripe.paymentIntents.create({
  amount: calculateOrderAmount(cart),     // server-side, smallest unit
  currency: 'usd',
  automatic_payment_methods: { enabled: true },
  customer: 'cus_123',                    // optional
  metadata: { order_id: order.id },
}, { idempotencyKey: `pi-${order.id}` });
res.json({ clientSecret: pi.client_secret });
```

Create the PI as soon as the amount is known and **reuse it** for retries of the same order (it records every attempt). Update the amount on the existing PI if the cart changes.

Client:

```js
const elements = stripe.elements({ clientSecret });
elements.create('payment').mount('#payment-element');

const { error } = await stripe.confirmPayment({
  elements,
  confirmParams: { return_url: 'https://example.com/complete' },
  redirect: 'if_required',     // only redirect for methods that need it
});
if (error) showError(error.message);   // card_error/validation_error messages are user-safe
```

Deferred intent (render before the amount is known): `stripe.elements({ mode: 'payment', amount, currency })`, then on submit `await elements.submit()`, create the PI server-side, and call `confirmPayment({ elements, clientSecret, ... })`.

Return page: read `payment_intent_client_secret` from the query string → `stripe.retrievePaymentIntent(secret)` → show status. **Display only; fulfill on webhook** (`payment_intent.succeeded`; also handle `payment_intent.processing`, `payment_intent.payment_failed`).

## PaymentIntent / SetupIntent lifecycle

```
requires_payment_method ──attach PM──▶ requires_confirmation ──confirm──▶ requires_action ──auth ok──▶ processing ──▶ succeeded
          ▲                                                                    │                    │
          └───────────── decline / auth failed / async failure ◀───────────────┴────────────────────┘
capture_method=manual:  … ──▶ requires_capture ──capture──▶ processing|succeeded
                                            └──expire/cancel──▶ canceled
any pre-processing state ──cancel──▶ canceled   (terminal; releases held funds)
```

- `requires_confirmation` is usually skipped (details submitted at confirm).
- Too many confirmations can auto-cancel a PI.
- Pre-`2019-02-11` API versions used `requires_source` / `requires_source_action`.
- `last_payment_error` on the PI explains the most recent failure; `next_action` describes the pending action (Stripe.js handles it; server-side flows use `stripe.handleNextAction(clientSecret)`).
- Cancelable statuses: `requires_payment_method`, `requires_confirmation`, `requires_action`, `requires_capture`, and `processing` only for some bank debits (ACH, ACSS, BECS, Bacs, SEPA — best effort).

## 4. Save a payment method, charge later (SetupIntents)

Compliance first: you may only charge a saved method for uses covered by your terms, and must get explicit consent (e.g. a "save for future use" checkbox) for off-session charges.

```js
// server
const setupIntent = await stripe.setupIntents.create({
  customer: 'cus_123',                               // or customer_account for v2 Accounts
  automatic_payment_methods: { enabled: true },
});
// client
const elements = stripe.elements({ clientSecret: setupIntent.client_secret });
elements.create('payment').mount('#payment-element');
const { error } = await stripe.confirmSetup({
  elements,
  confirmParams: { return_url: 'https://example.com/account/payments/setup-complete' },
  // redirect: 'if_required' to avoid redirect for cards
});
```

- Return URL gets `setup_intent_client_secret`; `stripe.retrieveSetupIntent()` → `setupIntent.payment_method` is now attached to the customer. Listen for `setup_intent.succeeded` server-side.
- To show saved methods and a save checkbox in the Payment Element, create a **CustomerSession** with `components.payment_element.enabled` and `features.payment_method_save`. Don't combine `setup_future_usage` with `payment_method_save_usage` in one transaction.
- Saving during a payment instead: `setup_future_usage: 'off_session'` (merchant-initiated later) or `'on_session'` (customer present later) on the PI / `payment_intent_data`.

Later, off-session charge:

```js
try {
  await stripe.paymentIntents.create({
    amount: 1099, currency: 'usd',
    customer: 'cus_123', payment_method: 'pm_123',
    off_session: true,     // customer not present; Stripe requests exemptions
    confirm: true,
  }, { idempotencyKey: `renewal-${invoiceId}` });
} catch (err) {
  if (err.code === 'authentication_required') {
    // err.raw.payment_intent is the failed PI (status requires_payment_method)
    // email the customer; on-session, call stripe.confirmPayment with that PI's client_secret
  }
}
```

`off_session: true` is a signal, not a guarantee: networks classify MIT vs CIT on actual cardholder participation (a present CVC makes it CIT).

## 5. Authorize now, capture later (manual capture)

- `capture_method: 'manual'` on the PI (or `payment_intent_data[capture_method]` on a Checkout Session). Mixed methods: set it per method, `payment_method_options[card][capture_method]=manual`, since e.g. ACH/iDEAL don't support separate capture.
- After confirm → `requires_capture`, event `payment_intent.amount_capturable_updated`, `amount_capturable` field; exact expiry in `charge.payment_method_details.card.capture_before`.
- Capture: `POST /v1/payment_intents/:id/capture` (`amount_to_capture` for less; remainder auto-released; usually **one** capture only, unless multicapture-eligible). Overcapture is a separate feature.
- Release: cancel the PI. Expired auth → PI `canceled`.
- Card-not-present windows: Visa **5 days** for merchant-initiated (exactly 4d18h) / 7 days customer-initiated; Mastercard, Amex, Discover 7 days. In-person: Visa 5 days, others 2 days. Extended authorization (up to ~30 days) exists for eligible cards/merchants; Japan JPY holds up to 30 days.
- Other methods: Klarna capture by midnight of day 28; PayPal 10 days (auto-extended to 20); Afterpay/Clearpay 13 days; Cash App Pay 7 days; Affirm 30 days.
- Cost tip: if you refund often shortly after purchase, manual capture + cancel is cheaper than capture + refund.
- Private preview: `payment_method_options[card][capture_method]=automatic_delayed` auto-captures ~6h before expiry, with `capture_by` (`auth_expiry` | `end_of_day` | `target_delay` + `capture_delay`).
