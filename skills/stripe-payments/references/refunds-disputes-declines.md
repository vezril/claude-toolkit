# Refunds, disputes, declines

Source: docs.stripe.com/refunds, /disputes/how-disputes-work, /declines, /api/errors. Fetched 2026-09.

## Cancel vs refund

| PaymentIntent state | Operation | Cost |
|---|---|---|
| Not yet succeeded (`requires_payment_method`, `requires_confirmation`, `requires_action`), or authorized (`requires_capture`) | **Cancel** `POST /v1/payment_intents/:id/cancel` | Free; releases hold |
| `processing` (US bank account; some other debits, best effort) | Cancel | — |
| `succeeded` | **Refund** | Original processing fees **not** returned |

An uncaptured charge can't be refunded; cancel the PI instead. Incomplete PIs can be left alone (useful for conversion analytics) rather than canceled.

## Refunds

```bash
curl https://api.stripe.com/v1/refunds -u "$STRIPE_SECRET_KEY:" \
  -d payment_intent=pi_123 \
  -d amount=1000 \                # optional partial, smallest unit
  -H "Idempotency-Key: refund-order-123-1"
```

- Multiple partial refunds are allowed; total can't exceed the charge amount. Refunds go only to the original payment method.
- Funded from **available** balance. Insufficient balance: card refunds stay `pending` until covered, other methods fail. Negative balances may be debited from your bank.
- Refund statuses: `pending`, `requires_action`, `succeeded`, `failed`, `canceled`.
- **Failed refunds** (`refund.failed`): funds return to your balance (can take up to 30 days); `failure_reason` is one of `charge_for_pending_refund_disputed`, `declined`, `expired_or_canceled_card`, `insufficient_funds`, `lost_or_stolen_card`, `merchant_request`, `unknown`; `failure_balance_transaction`. You must refund the customer another way.
- **`requires_action` refunds** (Konbini, PromptPay, Boleto, bank transfers): Stripe emails the customer for bank details (`next_action.display_details`); flows `requires_action` → `pending` → `succeeded`; bounced funds return to `requires_action`; no response by `expires_at` → `failed`; cancelable while `requires_action`.
- Card refunds can be canceled only briefly and only from the Dashboard.
- Refunds soon after the charge may process as a **reversal** (the charge disappears from the statement, lower network fees): `destination_details.card.type = 'reversal'`. Otherwise customers see the credit in ~5–10 business days. For "where's my refund?", give them the ARN/STAN/RRN from `destination_details.card.reference` (up to 7 business days to appear; not available for reversals).
- Bank debits (SEPA, Bacs, ACH, ACSS, BECS): risk of **double refund** if you refund while the customer's bank also disputes.
- Connect: direct charges debit the connected account; destination charges and separate charges and transfers debit the platform (use `reverse_transfer`, `refund_application_fee`; see `connect.md`).
- Events: `refund.created` (minimum to listen to), `refund.updated` (ARN available, metadata), `refund.failed`, `charge.refunded` (includes partial).
- If many refunds happen shortly after purchase, manual capture + cancel is cheaper.

## Disputes

**Pre-dispute signals**
- **Early fraud warnings** (Visa TC40, Mastercard SAFE; `radar.early_fraud_warning.created`): no response required. About 80% become fraud disputes unless liability shifted via 3DS. Refunding every EFW is wasteful: refund mainly when the charge amount is at or below roughly the dispute fee. A refund only prevents the fraud report when it processes as a reversal (~within 2h of capture).
- **Inquiries** (mostly Amex, Discover; Mexico domestic): status `warning_needs_response` → `warning_under_review` → `warning_closed` (after 120 days without escalation). Answer them: unanswered inquiries can escalate to unwinnable chargebacks. Resolve with evidence or a full refund (a partial refund can still escalate).

**Chargeback lifecycle**
- On creation: disputed amount + a **dispute fee** are debited immediately; funds held for the duration. **You can't refund while a dispute is open.** Your dispute rate for that network goes up.
- Cardholders usually have 120 days from payment (longer for future-dated services; LPMs like Klarna/PayPal often 180 days).
- Status: `needs_response` → `under_review` → `won` | `lost` (rare late win: `lost` → `won`). Some disputes are unchallengeable and close as `lost` immediately (Cartes Bancaires in SEPA, Nigerian methods, unanswered Discover inquiries).
- Response window typically **7–21 days** (`evidence_details.due_by`); issuer decision 60–75 days; 2–3 months end to end. Stripe doesn't support arbitration.
- Respond via Dashboard or `POST /v1/disputes/:id` with `evidence[...]` fields and `submit=true` (submission is final), or accept/close the dispute. Even if the customer says they withdrew, you must submit evidence to win.
- Fees: dispute-received fee usually non-refundable (Mexico exception; none for Cartes Bancaires in SEPA). Countering adds a dispute-countered fee, refunded if you win (not charged in Mexico/Japan).
- Disputed amount can differ from the charge (FX changes, bundled recurring charges, partial disputes, partially refunded charges).
- Multiple disputes on one payment are possible; handle each.
- Events: `charge.dispute.created`, `.updated`, `.closed`, `.funds_withdrawn`, `.funds_reinstated`.
- 3DS-authenticated fraud disputes usually shift liability to the issuer; Stripe auto-attaches 3DS evidence.

## Declines

Three failure types, visible in `charge.outcome.type`:
- **`issuer_declined`**: the bank said no. `decline_code` (Stripe), `network_decline_code`, `advice_code`, `network_advice_code`.
- **`blocked`**: Radar (risk rules/score) or Adaptive Acceptance (`low_probability_of_authorization`) blocked it before the network (`network_status: not_sent_to_network`). A customer may briefly see a pending auth. An allow-list entry permits future attempts but doesn't retry this one.
- **`invalid`**: bad API call. Fix the integration.

`outcome` also has `network_status` (`approved_by_network`, `declined_by_network`, `not_sent_to_network`, `reversed_after_approval`), `reason`, `risk_level` (`normal`/`elevated`/`highest`), `seller_message` (for you, not the customer).

`advice_code` drives retries:
- `do_not_try_again`: don't retry this card. Networks penalize repeated retries.
- `try_again_later`: retry later (Smart Retries does this for invoices).
- `confirm_card_data`: ask the customer to re-enter or update details.

What to show customers: the `card_error` `message` is safe. **Don't reveal fraud-specific reasons** (`fraudulent`, `stolen_card`, `lost_card`, `merchant_blacklist`, Radar blocks); show a generic "your card was declined" instead. After a decline the PI returns to `requires_payment_method`, so retry on the same PI with a new method.
