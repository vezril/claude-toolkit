# Testing a Stripe integration

Source: docs.stripe.com/testing, /webhooks (CLI), /rate-limits (load testing). Fetched 2026-09.

## Environments

- Use **sandboxes** (isolated test environments, Dashboard account picker) with `sk_test_` / `pk_test_` keys. Never test live mode with real cards; that violates the Stripe Services Agreement.
- Agents/CI without an account: `npm i -g @stripe/cli` then `stripe sandbox create --help` provisions an anonymous sandbox with working keys.
- Sandbox rate limit is 25 rps and networks are mocked. **Don't load-test against Stripe**; stub the Stripe client with latency sampled from real live calls.
- Copy sandbox products to live with "Copy to live mode" (copies don't stay in sync).

## Cards (any future expiry, any 3-digit CVC, any postal code)

| Scenario | Number | PaymentMethod token |
|---|---|---|
| Success | 4242 4242 4242 4242 | `pm_card_visa` |
| Generic decline | 4000 0000 0000 0002 | `pm_card_visa_chargeDeclined` |
| Insufficient funds | 4000 0000 0000 9995 | `pm_card_visa_chargeDeclinedInsufficientFunds` |
| Lost card | 4000 0000 0000 9987 | `pm_card_visa_chargeDeclinedLostCard` |
| Stolen card | 4000 0000 0000 9979 | `pm_card_visa_chargeDeclinedStolenCard` |
| Expired card | 4000 0000 0000 0069 | — |
| Incorrect CVC | 4000 0000 0000 0127 | — |
| Luhn failure | 4242 4242 4242 4241 | — |
| UnionPay variable length | 6205 5000 0000 0000 004 | — |

Invalid data without special cards: expiry month `13`, a year in the past, 2-digit CVC `99`.

## 3D Secure / SCA

| Scenario | Number | Token |
|---|---|---|
| Authenticate unless already set up (the classic SCA card) | 4000 0025 0000 3155 | `pm_card_authenticationRequiredOnSetup` |
| Always authenticate (tests off-session `authentication_required`) | 4000 0027 6000 3184 | `pm_card_authenticationRequired` |
| Already set up for off-session | 4000 0038 0000 0446 | `pm_card_authenticationRequiredSetupForOffSession` |
| 3DS2 required, succeeds | 4000 0000 0000 3220 | `pm_card_threeDSecure2Required` |
| 3DS required, then declined | 4000 0084 0000 1629 | `pm_card_threeDSecureRequiredChargeDeclined` |
| 3DS required, processing error | 4000 0084 0000 1280 | `pm_card_threeDSecureRequiredProcessingError` |
| 3DS supported, optional | 4000 0000 0000 3055 | `pm_card_threeDSecureOptional` |
| 3DS not supported | 3782 822463 10005 | `pm_card_amex_threeDSecureNotSupported` |
| Frictionless 3DS | 4000 0000 3220 0000 | — |

## Disputes, fraud, refunds

| Scenario | Number | Token |
|---|---|---|
| Fraudulent dispute | 4000 0000 0000 0259 | `pm_card_createDispute` |
| Product not received dispute | 4000 0000 0000 2685 | `pm_card_createDisputeProductNotReceived` |
| Inquiry | 4000 0000 0000 1976 | `pm_card_createDisputeInquiry` |
| Early fraud warning | 4000 0000 0000 5423 | `pm_card_createIssuerFraudRecord` |
| Multiple disputes | 4000 0040 4000 0079 | `pm_card_createMultipleDisputes` |
| Radar always blocks | 4100 0000 0000 0019 | `pm_card_radarBlock` |
| Highest risk | 4000 0000 0000 4954 | `pm_card_riskLevelHighest` |
| Elevated risk (review) | 4000 0000 0000 9235 | `pm_card_riskLevelElevated` |
| CVC check fails | 4000 0000 0000 0101 | `pm_card_cvcCheckFail` |
| Postal code check fails | 4000 0000 0000 0036 | `pm_card_avsZipFail` |
| Refund pending → succeeded | 4000 0000 0000 7726 | `pm_card_pendingRefund` |
| Refund succeeded → failed | 4000 0000 0000 5126 | `pm_card_refundFail` |

Dispute evidence test values (put in `evidence[uncategorized_text]`): `winning_evidence`, `losing_evidence`, `escalate_inquiry_evidence`.

## Bank debits and redirects

- ACH (routing `110000000`): success `000123456789` / `pm_usBankAccount_success`; closed `000111111113`; no account `000111111116`; insufficient funds `000222222227`; stays processing `000000000009`. Microdeposits: amounts `32` and `45`, or descriptor `SM11AA`.
- SEPA: success `AT321904300235473204` (processing → succeeded in ~3 min); fails to `requires_payment_method`: `AT861904300235473202`.
- BECS: account `900123456`, BSB `000000` succeeds after ~3 min; `111111113` → `account_closed`.
- Redirect methods (iDEAL, Bancontact, EPS, P24, Pay by Bank): click **Complete** or **Fail test payment** on the redirect page. Vouchers (Boleto, OXXO): close the dialog.

## Stripe CLI

```bash
stripe listen --forward-to localhost:4242/webhook        # prints session whsec_
stripe trigger checkout.session.completed
stripe trigger payment_intent.payment_failed
stripe events resend evt_123 --webhook-endpoint=we_123
stripe v2 core accounts list                             # v2 endpoints
```

## What a good test plan covers

1. Happy path with `4242…` → webhook fulfills exactly once (replay the event: still once).
2. Decline → PI back to `requires_payment_method`, retry on the same PI succeeds.
3. 3DS required (`…3155`) → `requires_action` handled by Stripe.js; closed tab mid-auth → no fulfillment.
4. Async method (SEPA/ACH) → `checkout.session.completed` with `payment_status=unpaid`, no fulfillment until `async_payment_succeeded`; failure path notifies.
5. Webhook with bad signature → 400; with a modified body → 400; old timestamp → rejected.
6. Duplicate and out-of-order events (`stripe events resend`, trigger related events in reverse).
7. Off-session charge with `pm_card_authenticationRequired` → `authentication_required` recovery flow.
8. Refunds full/partial; `pm_card_refundFail` → `refund.failed` handled.
9. Subscriptions: advance a **test clock** through trial end, renewal, failed renewal (`past_due` → final state), and cancellation.
10. Network timeout on create → retry with the same idempotency key → one object.
