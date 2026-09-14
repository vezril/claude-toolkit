# REST vs HTTP APIs, integrations, throttling, CORS

Source: AWS's serverless agent skill (`references/api-gateway.md`) + docs.aws.amazon.com. Fetched 2026-09.

## Full REST-exclusive feature list

Default to HTTP API; only reach for REST API when the workload needs one of:

- API keys / usage plans / per-client throttling
- Request validation (built in — HTTP API has none)
- Request/response body transformation (VTL — Velocity Template Language)
- Built-in caching
- Private API endpoints
- Edge-optimized endpoints
- Canary deployments
- Execution logs / X-Ray tracing (HTTP API has access logs but not the same execution-log depth)
- Resource policies
- Mock integrations
- Response streaming

None of these needed → HTTP API. It's lower latency, lower cost, has native JWT auth, built-in CORS configuration, and auto-deploy (no separate "Deploy API" step per stage change the way REST API requires).

## Integration timeouts and payloads

| | REST API | HTTP API |
|---|---|---|
| Integration timeout | 50ms – 29s, default 29s. Raisable **only** for Regional/private endpoints — edge-optimized is capped at 29s regardless. | **30s hard max**, can only be lowered, never raised. |
| Payload size | 10 MB | 10 MB |
| Endpoint types | Edge, Regional, Private | Regional only |
| Response streaming | Yes — proxy integration, `STREAM` mode | No |

**REST API streaming caveats**: no built-in caching applies to streamed content, no VTL transforms, WAF doesn't inspect streamed content, and the throughput cap is 2 MBps after the first 10 MB (contrast Lambda Function URLs, which cap after 6 MB — don't conflate the two limits).

## Throttling depth

Order of application, most to least specific: **per-client/method** (usage plan + API key, REST only) → **per-method** → **account-level** → **Region-wide hard ceiling**. Each is an independent token bucket; an empty bucket at any level returns `429`, and a temporary burst above steady-state is absorbed by the bucket's burst capacity until it's drained.

Client-side handling: exponential backoff with jitter, honor `Retry-After` if present, and — for a client you control — rate-limit proactively to stay under the limits you know about rather than only reacting to 429s.

## CORS: the failure modes beyond the basics

| Symptom | Cause | Fix |
|---|---|---|
| OPTIONS preflight 502s | Binary media type `*/*` set on the API | Set `contentHandling: CONVERT_TO_TEXT` on the OPTIONS integration |
| Browser rejects response with credentials | `Access-Control-Allow-Origin: *` combined with `credentials: include` | Return the exact origin, never a wildcard, when credentials are involved |
| CORS "still broken" after a config change | Stage wasn't redeployed | Redeploy the stage — REST API changes don't take effect until deployed |
| Error responses (4XX/5XX) fail CORS in the browser, masking the real error | Gateway responses don't inherit method/integration response CORS headers | Add CORS headers to gateway responses explicitly, not just success responses |
| Proxy-integration Lambda "ignores" the console CORS toggle | Under Lambda proxy integration, API Gateway doesn't inject CORS headers — the function must | Return `Access-Control-Allow-*` headers from the Lambda response itself |

## Pitfalls

- Choosing REST API by habit/default when the workload has no REST-exclusive requirement — needless cost and complexity.
- Assuming the 29s REST API default timeout is fixed — it's raisable for Regional/private, capped for edge-optimized.
- Treating HTTP API's 30s timeout as raisable — it isn't, only lowerable.
- Debugging a CORS failure by staring at headers when the real issue is a missing redeploy.
