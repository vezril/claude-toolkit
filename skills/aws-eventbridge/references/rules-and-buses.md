# Event buses, rules, and patterns

Source: docs.aws.amazon.com (eventbridge/latest/userguide) + AWS's serverless agent skill. Fetched 2026-09.

## Event buses

- **Default bus** — receives events automatically from AWS services in your account. Use it for AWS-service events; don't crowd it with application events.
- **Custom bus** — you create one per application domain (order-service, billing-service, …). This is the recommended home for your own `PutEvents` traffic — isolates pattern management and IAM scoping per domain.
- **Partner bus** — receives events from a supported SaaS partner integration.
- **Cross-account** — a bus can receive events from rules in other AWS accounts (resource-based policy on the receiving bus, a rule with that bus as its target on the sending account's bus).

## Event pattern syntax

A pattern is matched against the event JSON. **All specified top-level fields must match (AND)**; **values within one field's array are OR'd**.

| Operator | Example | Meaning |
|---|---|---|
| Exact match | `"status": ["active"]` | Value is exactly `active` |
| Prefix | `{"prefix": "order-"}` | Starts with `order-` |
| Suffix | `{"suffix": "-east"}` | Ends with `-east` |
| Anything-but | `{"anything-but": "cancelled"}` | Any value except `cancelled` |
| Numeric | `{"numeric": [">", 0, "<=", 100]}` | Range comparison |
| Exists | `{"exists": true}` / `{"exists": false}` | Field presence, regardless of value |
| Wildcard | `{"wildcard": "prod-*-east"}` | Glob-style match |

```json
{
  "source": ["myapp.orders"],
  "detail-type": ["Order Placed"],
  "detail": {
    "status": ["pending", "processing"],
    "amount": [{"numeric": [">", 100]}]
  }
}
```

## Rule design best practices

1. **Dedicated bus per domain** (see above).
2. **Precise patterns** — the narrower the pattern, the smaller the blast radius of a misconfigured rule, and the lower the risk of an accidental routing loop (a target that re-emits an event the same rule would match).
3. **One target per rule** — simplifies both debugging (which target failed?) and IAM (each target's permissions stay legible).
4. **DLQ on every target** (see `pipes-targets-retries-and-dlq.md`) — non-negotiable, not optional hardening.
5. **Test in the EventBridge Sandbox** before deploying a new or changed pattern — patterns that look right can silently match nothing, or match too much.

## Pitfalls

- Putting application events on the default bus — makes IAM and pattern scoping messier as the app grows, and mixes your traffic with every AWS service event in the account.
- A pattern broad enough to create a routing loop (rule → target → re-emitted event → same rule).
- Multiple unrelated targets on one rule, making a partial failure hard to attribute.
- Assuming a rule "not firing" means the pattern is wrong, when it's actually the bus (wrong bus, event landed on the default bus instead of the custom one you're watching).
