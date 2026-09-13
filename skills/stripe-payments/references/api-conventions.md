# Stripe API conventions

Source: docs.stripe.com/api (Authentication, Errors, Idempotent requests, Pagination, Versioning, Metadata), /expand, /search, /rate-limits, /error-low-level, /api-v2-overview, /keys-best-practices. Fetched 2026-09.

## Shape of the API

- Base URL `https://api.stripe.com`. HTTPS only — plain HTTP fails.
- **v1** (`/v1/...`, most of the API): **form-encoded** request bodies (`application/x-www-form-urlencoded`), JSON responses. Nested params use brackets: `line_items[0][price]=price_123`, `metadata[order_id]=6735`, `expand[]=customer`.
- **v2** (`/v2/...`: Accounts v2, event destinations, thin events, billing meter streams…): **JSON** request and response bodies, `Stripe-Version` header **required** on raw requests. Both namespaces mix freely in one integration; SDKs expose them as `client.v1.*` / `client.v2.*`.
- One object per request — no bulk updates.
- The API key decides the environment: sandbox/test key → sandbox data; live key → real money.

## Authentication and keys

| Key | Prefix | Where it may live | Notes |
|---|---|---|---|
| Publishable | `pk_test_` / `pk_live_` | Browser, mobile apps | Only identifies your account to Stripe.js/mobile SDKs |
| Secret | `sk_test_` / `sk_live_` | Server only | Full account access. Prefer restricted keys in live mode |
| Restricted | `rk_test_` / `rk_live_` | Server only | Per-resource permissions; create one per component/third party |
| Webhook signing secret | `whsec_` | Server only | One per endpoint, different per mode |

- Auth is HTTP Basic with the key as username and empty password (`curl -u sk_test_...:`), or `Authorization: Bearer <key>`.
- Connect: act on a connected account with the `Stripe-Account: acct_...` header (SDK per-request option). Organizations use `Stripe-Context`.
- Best practice: vault or environment variable, never source code or client bundles; least privilege (restricted keys); optional IP allowlist on keys; rotate periodically; audit request logs; pre-commit hook rejecting `sk_live_`/`rk_live_`. Treat any exposure as compromise → roll immediately. Stripe never asks for your secret key.

## Versioning

- Named major releases (Acacia, Basil, Clover, **Dahlia** …) carry breaking changes; **monthly** releases under the same name are backward-compatible. Current: `2026-08-26.dahlia` (v2 previews use `.preview` suffix).
- Raw HTTP/CLI requests use the **account default version** (set in Workbench) unless `Stripe-Version` overrides it.
- SDKs: Java, Go, .NET always pin the version current at SDK release; Node ≥12, Python ≥6, Ruby ≥9, PHP ≥11 also pin. Older dynamic SDKs use the account default. Upgrading the SDK = upgrading the API version.
- **Webhook events** are rendered in the endpoint's configured version (else account default) and never change after creation. Create the endpoint with the version your SDK pins.
- Backward-compatible changes Stripe may make at any time: new resources, new optional params, new response properties, changed ordering of properties, new event types, changed length/format of IDs and opaque strings. Your parsers must tolerate these (don't validate ID formats or reject unknown fields).

## Errors

HTTP status:

| Code | Meaning |
|---|---|
| 200 | OK |
| 400 | Bad request (missing/invalid param) |
| 401 | No valid API key |
| 402 | Request failed — valid params, but e.g. card declined |
| 403 | Key lacks permission (restricted key) |
| 404 | Not found |
| 409 | Conflict (e.g. idempotency key clash) |
| 424 | External dependency failed |
| 429 | Rate limited **or** `lock_timeout` |
| 500/502/503/504 | Stripe-side (rare) |

Error `type`: `card_error` (most common; `message` is safe to show the user), `invalid_request_error`, `idempotency_error` (same key, different endpoint/params), `api_error`.

Useful error fields: `code` (programmatic, see /error-codes), `decline_code`, `advice_code`, `network_decline_code`, `network_advice_code`, `param` (which field to highlight), `payment_intent` / `setup_intent` / `payment_method` (the object in its failed state — use its client secret to recover), `doc_url`, `request_log_url`. Every response has a `Request-Id` header — log it.

### Retrying safely

- **Network errors/timeouts:** outcome unknown → retry with the **same** idempotency key and **same** params until you get a definitive answer. SDK: set `maxNetworkRetries` (e.g. 2); it auto-generates keys and backs off.
- **`Stripe-Should-Retry: true|false`** header, when present, is authoritative; SDKs honor it.
- **4xx:** fix the request; use a **new** idempotency key (a 400 that began execution is cached under the old key). 429s and auth-less 401s run before the idempotency layer, so they may differ on replay.
- **429:** exponential backoff **with jitter**; for sustained load use a client-side token bucket. `lock_timeout` means concurrent mutation of the same object — serialize writes per object. SDK retries cover lock timeouts.
- **500:** indeterminate. Replay with same key returns the same 500. Don't mint a new key blindly; reconcile via webhooks (Stripe emits events for objects created during incident reconciliation) joined on your `metadata` IDs.

## Idempotency

- Header `Idempotency-Key: <≤255 chars>`; UUIDv4 or a deterministic key from your domain (cart/order ID) to also block double-submit. Don't embed PII (emails) in keys.
- v1: all POSTs accept it; GET/DELETE are already idempotent (don't send). First result (status + body, **including errors**) is stored once execution begins and replayed; keys pruned after ≥24h. Same key + different params → `idempotency_error`. Not stored if validation failed before execution or a concurrent request with that key is in flight — safe to retry. Replays carry `Idempotent-Replayed: true`.
- v2: POST and DELETE; window is **30 days**, same account/sandbox; failed requests are **re-executed** safely on replay instead of replaying the error; SDKs auto-generate a key if you don't.

## Pagination (v1)

- List endpoints: `limit` (1–100, default 10), `starting_after=<id>` (next page) or `ending_before=<id>` (previous) — mutually exclusive. Reverse chronological.
- Response: `{object: "list", data: [...], has_more, url}`.
- Use SDK auto-pagination (`for await (const x of stripe.customers.list())`, `.auto_paging_iter()`, `autoPagingIterable()`), and filter server-side (`customer=`, `created[gte]=`) to cut read volume.
- v2: `page` token, `next_page_url` / `previous_page_url`; filters fixed after first request; lists eventually consistent.

## Expand

- `expand[]=customer`, multiple allowed, dot-notation nesting (`payment_intent.payment_method`), **max depth 4**.
- In lists use `data.`: `expand[]=data.payment_method`.
- Some properties are **includable only via expand** (e.g. Checkout Session `line_items`).
- Webhook payloads are **never expanded** — retrieve in the handler.
- Costly on lists; contributes to concurrency limits.
- TypeScript: expandable fields are `string | Stripe.X` — cast after expanding.
- v2 has no `expand`; some endpoints support `include[]`.

## Search

- Resources: Charges, Customers, Invoices, PaymentIntents, Prices, Products, Subscriptions (`GET /v1/<resource>/search?query=...`).
- Syntax: `field:"value"` exact (case-insensitive), `field~"abc"` substring (≥3 chars, string fields like `email`, `name`), `amount>1000` numeric, `-field:value` negation, `field:null` presence, `metadata["key"]:"value"`. Up to 10 clauses joined by space/`AND` **or** `OR` — can't mix, no parentheses. String values need quotes.
- Pagination via `page` / `next_page`.
- **Eventually consistent** (normally < 1 minute, longer during incidents) and filters on cached status → never use for read-after-write. 20 read rps. Not available for businesses in India. For analytics use Sigma / Data Pipeline.

## Metadata

- On updatable objects (Customer, PaymentIntent, Charge, Refund, Subscription, Transfer, Account…). Up to **50 keys**, key ≤ **40 chars** (no `[` `]`), value ≤ **500 chars**, all strings.
- Unset a key by setting it to `""` (v1) / `null` (v2).
- Stripe doesn't act on it or show it to customers (unlike `description`, which can appear on receipts).
- Doesn't propagate automatically between related objects — set it where you'll read it (e.g. `payment_intent_data[metadata]` on a Checkout Session if handlers read the PI).
- Never store card numbers, bank details, or other sensitive data.

## Rate limits

| Scope | Limit |
|---|---|
| Global, live | 100 rps per account |
| Global, sandbox | 25 rps |
| Per endpoint (default) | 25 rps |
| PaymentIntent updates | 1000 per PI per hour |
| Subscriptions | 10 new invoices/sub/min, 20/day; 200 quantity updates/sub/hour |
| Search | 20 read rps |
| Files | 20 read + 20 write rps |
| Connect account creation | 30/s live, 5/s sandbox |

- 429 responses carry `Stripe-Rate-Limited-Reason`: `global-rate`, `endpoint-rate`, `global-concurrency`, `endpoint-concurrency`, `resource-specific`. A 429 **without** it is likely a lock timeout.
- Read allocation: average ≤ 500 GET requests per transaction over 30 days (min 10,000/month). Writes unlimited by allocation.
