# Creating a distribution, caching, and edge compute

Source: AWS's CloudFront agent skill (`when-to-use-cloudfront.md`) + docs.aws.amazon.com. Fetched 2026-09.

## Creating a distribution

Every standard distribution gets a default `d111111abcdef8.cloudfront.net` domain, usable immediately for testing with no custom domain or certificate needed. (Multi-tenant distributions don't get this default test domain.)

Minimum viable, secure-by-default creation sequence for an S3 origin:
1. **Create the OAC first**, so the origin is locked from the start rather than created open and hardened afterward (see `protecting-origins.md`).
2. **Resolve the current managed `CachingOptimized` cache policy ID by name** rather than hardcoding a UUID — managed policy IDs can change:
```bash
aws cloudfront list-cache-policies --type managed \
  --query "CachePolicyList.Items[?CachePolicy.CachePolicyConfig.Name=='Managed-CachingOptimized'].CachePolicy.Id | [0]" --output text
```
3. **Create the distribution**, referencing the OAC and resolved cache policy ID, with `ViewerProtocolPolicy: redirect-to-https`.
4. **Enable standard logging immediately** — it isn't set by the create call itself.
5. **Attach a WAF web ACL** with baseline managed rules (Core Rule Set + Known Bad Inputs) for public-facing distributions, and a **rate-based rule** specifically for API origins — caching alone doesn't shield an origin from unthrottled dynamic/API traffic.
6. **Attach a response headers policy** with browser security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options) — the managed `SecurityHeadersPolicy` is a reasonable starting point.
7. **Wait for `Deployed` status** before expecting the `cloudfront.net` URL to serve content — errors immediately after creation are expected and not a sign of misconfiguration.

## Cache policies vs cache behaviors

A **cache behavior** (default, or path-pattern-scoped) says *which requests this configuration applies to*. A **cache policy**, attached to the behavior, holds the actual **TTLs and cache key definition**. This separation trips people up: looking for TTL fields directly on the behavior is looking in the wrong place.

- Use a **managed cache policy** for standard cases; write a custom one only when the cache key genuinely needs to differ (e.g. include a specific header or query string).
- **Minimum TTL above zero overrides origin `no-cache`/`no-store`/`private` directives** for at least that duration — set minimum TTL to zero if you need CloudFront to always respect origin cache-control headers.
- **Path-pattern behaviors are evaluated before the default behavior** (which runs last) — use them when caching rules genuinely differ per path, e.g. long-TTL on `*.jpg`, no-cache on `/api/*`.

## CloudFront Functions vs Lambda@Edge

| | CloudFront Functions | Lambda@Edge |
|---|---|---|
| Events | Viewer-request, viewer-response only | Viewer-request/response **and** origin-request/response |
| Latency/cost | Sub-millisecond, cheap | Higher on both dimensions |
| Network access | No | Yes |
| Use for | URL rewrites, header manipulation, redirects, lightweight token checks | Anything needing network calls, a larger runtime, or origin-facing logic |

**A function must be published to the `LIVE` stage before it can be associated with a distribution** — this is the near-universal cause of "the function association just failed" right after writing new function code.

## Pitfalls

- Looking for TTL settings on the cache behavior instead of the cache policy it points to.
- Leaving minimum TTL above zero and being confused when origin `no-cache` headers seem to be ignored.
- Associating a CloudFront Function before publishing it to `LIVE`.
- Skipping WAF on an API-backed distribution because "CloudFront caching already protects the origin" — caching doesn't throttle dynamic/uncacheable requests.
- Creating the distribution before the OAC, leaving a window where the origin is open.
