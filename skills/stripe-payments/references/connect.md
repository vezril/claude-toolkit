# Connect (platforms and marketplaces)

Source: docs.stripe.com/connect/charges, /connect/destination-charges (hosted), /connect/onboarding, /refunds (Connect section), /rate-limits. Fetched 2026-09.

## Choose the charge type

| | Direct charges | Destination charges | Separate charges and transfers |
|---|---|---|---|
| Charge lives on | Connected account | Platform | Platform |
| Customer sees | Connected account (often unaware of the platform) | Platform (or connected account with `on_behalf_of`) | Platform (or `on_behalf_of`) |
| Parties per payment | 1 seller | 1 seller | Many sellers, or seller unknown at charge time |
| Stripe fees paid by | Your choice (connected account or platform) | Platform | Platform |
| Refunds/chargebacks debit | Connected account | Platform (recover with transfer reversal) | Platform (recover with transfer reversal) |
| Typical | SaaS / storefront builders (Shopify-like) | Marketplaces, rideshare (Lyft/Airbnb-like) | Multi-vendor cart, delivery split (DoorDash-like) |
| How | `Stripe-Account: acct_…` header on the create call; `application_fee_amount` | `transfer_data[destination]` + `application_fee_amount` **or** `transfer_data[amount]` | Charge normally, then `POST /v1/transfers` with `transfer_group` / `source_transaction` |

- Direct charges need the account's `card_payments` capability and aren't recommended for legacy v1 Express/Custom accounts (use v2 accounts, or destination charges).
- Destination charges and separate charges and transfers are cross-region only in some regions; otherwise the platform and account must share a region unless you use `on_behalf_of`.
- Only use separate charges and transfers when you truly need one-to-many, many-to-one, transfer-before-charge, or transfer > charge. You must watch your balance, or tie a transfer to a charge with `source_transaction` so it waits for the funds.

## Destination charge (Checkout)

```bash
curl https://api.stripe.com/v1/checkout/sessions -u "$STRIPE_SECRET_KEY:" \
  -d mode=payment \
  -d "line_items[0][price_data][currency]=usd" \
  -d "line_items[0][price_data][product_data][name]=T-shirt" \
  -d "line_items[0][price_data][unit_amount]=1000" \
  -d "line_items[0][quantity]=1" \
  -d "payment_intent_data[application_fee_amount]=123" \
  -d "payment_intent_data[transfer_data][destination]=acct_123" \
  --data-urlencode "success_url=https://example.com/success?session_id={CHECKOUT_SESSION_ID}"
# add payment_intent_data[on_behalf_of]=acct_123 to make the seller the settlement merchant
```

Funds flow for a 10.00 USD charge with `application_fee_amount=123`: the full 10.00 goes to the connected account, 1.23 comes back to the platform as an Application Fee, and Stripe's fee (e.g. 0.59) is taken from the platform, leaving it 0.64.

- `application_fee_amount`: capped at the charge amount, same currency; creates an Application Fee object (good reporting); the seller sees total + fee.
- `transfer_data[amount]` (alternative): the platform keeps the charge and transfers this amount; the seller sees only the transfer. Compute the platform take as `amount − transfer_data.amount`.
- **`on_behalf_of`** makes the connected account the settlement merchant: their country's settlement and fees, their statement descriptor (and address/phone if cross-country), their payout delay. Requires a payments capability (not accounts on the recipient service agreement).
- Checkout uses **platform** branding for destination charges and **connected account** branding for direct charges.

## Refunds and disputes by type

- Direct: refund debits the connected account's balance (`pending` until it has funds).
- Destination / SCT: refund debits the **platform**. To claw back: `reverse_transfer=true` (proportional on partial refunds). To return the platform fee to the seller: `refund_application_fee=true`, which also requires reversing the transfer for destination charges. If the reversal would overdraw the seller, the refund request errors instead of going `pending`.
- Failed or canceled refunds on destination charges return funds to the platform; transfer them onward manually if needed.
- Disputes on destination / SCT debit the platform (amount + fee). Listen for `charge.dispute.created` and reverse the transfer to recover; re-transfer if you win (cross-border re-transfers may be impossible, so for cross-border `on_behalf_of` wait until the dispute is lost before reversing).
- Async method failure on destination charges: Stripe auto-reverses the pending transfer.
- **Skipped transfers**: if the destination lost its `transfers` capability or closed while an async payment settled, the transfer is skipped and funds stay with the platform. Detect with `charge.updated` where `transfer_data` is `null`.
- Negative connected balances: Stripe debits the seller's external account only if `debit_negative_balances=true`.
- Legacy Express/Custom accounts: the platform is liable for disputes and fraud.

## Accounts and onboarding

- **Accounts v2** (`/v2/core/accounts`) is the current model (GA for Connect). An account carries *configurations*, e.g. `merchant` (accept payments), `customer` (be billed), `recipient` (receive transfers). Payout settings still use Accounts v1. Legacy v1 types: Standard, Express, Custom.
- Onboarding options, in recommended order:
  1. **Stripe-hosted onboarding**: redirect to an Account Link (single-use and short-lived; with `refresh_url` for regenerating an expired link and `return_url`). Least effort; stays current with compliance requirements automatically; supports networked onboarding.
  2. **Embedded onboarding**: the Account onboarding Connect embedded component in your app; themeable; also auto-updates.
  3. **API onboarding**: you build every form. Most effort; must follow requirement changes yourself (review at least every 6 months). Avoid unless necessary.
- Returning to `return_url` **doesn't** mean onboarding finished. Check the account's requirements (currently due / past due / disabled reason) and capabilities (`card_payments`, `transfers`) before charging or transferring, and keep watching `account.updated` (v1) or the v2 account thin events, since requirements change over time.
- Connect embedded components (payments, payment details, disputes list) let sellers manage refunds and disputes inside your site; for destination charges with `on_behalf_of` enable `destination_on_behalf_of_charge_management`.
- Webhooks: register a "Connected accounts" destination for events on connected accounts and a "Your account" destination for platform-owned charges (see `webhooks-and-fulfillment.md`).
- Rate limit: 30 account creations/s live, 5/s sandbox.
