---
name: aws-api-gateway
description: "Building and securing APIs on Amazon API Gateway, distilled from AWS docs and AWS's own serverless/task agent skills (fetched 2026-09). Covers REST vs HTTP vs WebSocket APIs and when each's exclusive features (API keys/usage plans, request validation, VTL transforms, built-in caching, private/edge endpoints, canary deploys for REST; native JWT authorizer, lower latency/cost for HTTP) force the choice, integration timeouts and payload limits, throttling (the most-specific-to-least-specific token bucket: per-client → per-method → account → Region), Lambda proxy integration (the #1 cause of 502s: the response body must be a JSON.stringify'd string in {statusCode, headers, body}, and Lambda — not the console CORS button — must emit CORS headers), Lambda authorizers (TOKEN vs REQUEST, the 300s cache TTL that applies to ALL matching methods, the 401-without-invoking-Lambda case), the HTTP API native JWT authorizer and REST API's Cognito user pools authorizer (and what each does and doesn't enforce), WebSocket APIs (the ,connect/,disconnect/,default routes, 10-minute idle/2-hour max connection limits, the @connections push API, DynamoDB TTL for connection cleanup), CORS failure modes beyond basic header setup, and stage configuration (CloudWatch logging, X-Ray, WAF, throttling). Use when choosing REST vs HTTP vs WebSocket API, connecting Lambda to API Gateway, debugging a 502/504 or CORS error, configuring a Lambda or JWT or Cognito authorizer, building a WebSocket API, or hardening a stage for production."
license: MIT
---

# Amazon API Gateway

How to pick the right API type and avoid the handful of failures that account for most API Gateway production incidents — 502s from a malformed Lambda proxy response, CORS that "works locally" and breaks in prod, and an authorizer cache serving a stale decision to routes it was never meant to cover. Distilled from `docs.aws.amazon.com` and AWS's serverless/task agent skills, fetched 2026-09. Cross-links: [[aws-lambda]] for the function side of proxy integration, [[aws-cognito]] for the authorizer's identity provider, [[aws-eventbridge]] for event-driven alternatives to synchronous APIs.

## Choose the API type first

```
Need any of: API keys/usage plans, built-in request validation, VTL request/response
transforms, built-in caching, private endpoints, edge-optimized endpoints, canary
deploys, execution logs/X-Ray, resource policies, mock integrations, response streaming?
        │
        ├── Yes → REST API
        └── No  → HTTP API (lower latency, lower cost, simpler, native JWT authorizer, built-in CORS, auto-deploy)
```

**WebSocket API** is a separate, third type — for persistent bidirectional connections (chat, live updates, multiplayer), not a variant of REST/HTTP.

| | REST API | HTTP API |
|---|---|---|
| Integration timeout | 50ms–29s (default 29s; raisable only for Regional/private) | **30s hard max**, lowerable only |
| Payload | 10 MB | 10 MB |
| Endpoint types | Edge, Regional, Private | Regional only |
| Response streaming | Yes (proxy, STREAM mode) | No |
| Native JWT auth | No (Cognito or Lambda authorizer only) | Yes |

## Non-negotiables

1. **Lambda proxy responses must be exact.** `{statusCode, headers, body}`, and `body` must be a `JSON.stringify`'d **string**, not an object. This single shape mismatch is the number one cause of 502s.
2. **CORS headers come from the Lambda function under proxy integration**, not from API Gateway's console "Enable CORS" button — that button doesn't apply once you're in proxy mode. The function must emit `Access-Control-Allow-Origin` etc. itself.
3. **Redeploy the stage after any CORS change.** A correct configuration that hasn't been redeployed behaves exactly like an incorrect one.
4. **A Lambda authorizer's cached policy applies to every method/resource sharing that cache key** — default TTL 300s (0–3600 configurable). Don't assume a cached "allow" only covers the route that triggered it.
5. **If any configured identity source is missing/null/empty, the authorizer returns 401 without ever invoking your Lambda.** A missing header isn't a bug in your authorizer code — check the identity source configuration first.
6. **Gateway 4XX/5XX responses need their own CORS headers.** Headers configured on successful method/integration responses don't automatically apply to gateway-level error responses — add them separately or preflight-adjacent browser errors will mask the real error.
7. **Binary media type `*/*` breaks OPTIONS preflight (502)** unless the OPTIONS integration sets `contentHandling: CONVERT_TO_TEXT`.
8. **Prefer HTTP API by default.** Reach for REST API only when the workload genuinely needs one of its exclusive features — defaulting to REST "just in case" adds cost and complexity for nothing in most cases.

## Quick reference — throttling and quotas

Throttling applies most-specific → least-specific: per-client/method (usage plan + API key, REST only) → per-method → account-level → AWS Region (hard ceiling). An empty token bucket returns `429`; handle it client-side with exponential backoff + jitter, respecting `Retry-After`.

| Resource | REST API default | HTTP API default | Adjustable? |
|---|---|---|---|
| Resources/Routes per API | 300 | 300 | Yes |
| Stages per API | 10 | 10 | Yes |
| API keys per account | 10,000 | — | No |
| Custom domains per Region | 120 | 120 | Yes |
| Integrations per API | — | 300 | No |
| VPC links per Region | — | 10 | Yes |

Account-level steady-state RPS/burst varies by Region and is adjustable — check the current value rather than assuming a default: `aws service-quotas get-service-quota --service-code apigateway --quota-code L-8A5B8E43`.

## References

- `references/rest-vs-http-and-integrations.md` — the full decision matrix, integration timeout/payload details, throttling depth, CORS failure modes beyond the basics.
- `references/authorizers.md` — Lambda TOKEN vs REQUEST authorizers, the HTTP API JWT authorizer, REST API's Cognito user pools authorizer, and what each does (and doesn't) enforce.
- `references/websocket-and-stages.md` — WebSocket API routes and limits, connecting Lambda via proxy integration, and stage configuration (logging, X-Ray, WAF, throttling).
