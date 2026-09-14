# WebSocket APIs, Lambda integration, and stages

Source: AWS's serverless agent skill (`references/api-gateway.md`) + task skills (`connecting-lambda-to-api-gateway`, `creating-api-gateway-stage`) + docs.aws.amazon.com. Fetched 2026-09.

## WebSocket API routes

| Route | Purpose |
|---|---|
| `$connect` | Fires on connection open — authenticate here, store the `connectionId` |
| `$disconnect` | Fires on close — **best-effort only**, not guaranteed to fire on every disconnect (network drops, client crashes) |
| `$default` | Catch-all for unmatched routes and non-JSON messages |
| Custom routes | Selected by `$request.body.action` in the incoming JSON message |

Server-initiated pushes go through the **`@connections` management API** (`PostToConnectionCommand` / `post_to_connection`), not through the route model — you call it from your backend with a stored `connectionId`.

| Limit | Value |
|---|---|
| Idle connection timeout | 10 minutes |
| Max connection duration | 2 hours |
| Message payload | 128 KB (hard) |

Close codes worth recognizing: **1001** idle/max-duration reached, 1003 unsupported binary frame, 1006 abnormal close (no close frame received — this is the common "`$disconnect` never fired" case), **1008** throttled, **1009** message too large, 1011 internal error, 1012 service restart.

**Since `$disconnect` isn't guaranteed**, store `connectionId` in DynamoDB with a **TTL attribute set to `now + 7200s`** (the 2-hour max duration) so stale connection records self-clean even when the disconnect event never lands. Enable DynamoDB TTL on that attribute — without it, dead connections silently accumulate in your table.

## Connecting Lambda (REST/HTTP API, proxy integration)

Core procedure: create the API, add resource/method (or route), set Lambda proxy integration, grant `lambda:InvokeFunction` to the API Gateway service principal scoped to the specific API's source ARN, configure CORS, deploy.

**The proxy response contract (get this exactly right):**
```js
return {
  statusCode: 200,
  headers: { "Access-Control-Allow-Origin": "https://example.com" },
  body: JSON.stringify({ message: "ok" }),  // body MUST be a string
};
```
Returning `body` as a raw object instead of a `JSON.stringify`'d string is the single most common cause of a 502 under proxy integration.

**Permission grant** — scope precisely, don't grant broadly:
```bash
aws lambda add-permission --function-name my-fn \
  --statement-id apigw-invoke --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:<region>:<account>:<api-id>/*/*/<resource-path>"
```

**Troubleshooting:**
- **502** → almost always the proxy response shape. Check `body` is a string, not an object.
- **"Permission denied" invoking Lambda** → the `add-permission` source ARN doesn't match the actual invoking method/stage/resource combination.
- **CORS errors in the browser** → confirm the OPTIONS method exists, CORS is set on both the method and integration response, and the stage was redeployed.

## Stage configuration (production hardening)

A stage should ship with:
- **CloudWatch logging** — execution logs and/or access logs, with an IAM role granting `logs:*` scoped appropriately.
- **X-Ray tracing** enabled for distributed tracing across the API → Lambda → downstream path.
- **WAF web ACL association** for Layer 7 filtering (managed rule groups plus rate-based rules) — API Gateway caching doesn't protect an origin from unthrottled dynamic/API traffic; WAF does.
- **Throttling** set explicitly at the stage and/or method level, not left at account defaults.
- **Method-level authorization** matching the stage's intended access model (IAM, Cognito, Lambda authorizer, or none for genuinely public routes).

**Troubleshooting:**
- **CloudWatch logs not appearing** → check the CloudWatch role's permissions, that the log group exists, and that logging is enabled at *both* the stage and method level (one without the other is a common half-configuration).
- **Stage creation fails** → verify the REST API ID, deployment ID, IAM permissions, and stage naming.
- **WAF blocking legitimate traffic** → review WAF logs, adjust or add exceptions, or run the rule in count mode while tuning.

## Pitfalls

- Relying on `$disconnect` firing reliably for connection cleanup — it doesn't; use DynamoDB TTL as the real cleanup mechanism.
- Returning an object instead of a string for the proxy integration `body`.
- Granting `lambda:InvokeFunction` broadly instead of scoped to the specific API's source ARN.
- Shipping a stage with logging/X-Ray/WAF/throttling all left at defaults because "we'll harden it later."
