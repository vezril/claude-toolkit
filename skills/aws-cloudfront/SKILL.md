---
name: aws-cloudfront
description: "Configuring Amazon CloudFront content delivery, distilled from AWS's own CloudFront agent skill and docs.aws.amazon.com (fetched 2026-09). Covers when CloudFront is the right layer (HTTP/HTTPS only, DDoS absorption via Shield built in, the attachment point for WAF/Lambda@Edge/CloudFront Functions/Route 53/ACM — use Global Accelerator instead for non-HTTP protocols, static-IP entry, or sub-minute failover), origin type selection (S3 via origin access control by default, VPC origins for a private ALB/NLB/EC2, origin mutual TLS for public/hybrid origins), origin locking as a mandatory pairing for every content control (OAC + scoped bucket policy with both aws:SourceArn and aws:SourceAccount, never origin access identity for new setups), content security (signed URLs vs signed cookies backed by trusted key groups — never the deprecated CloudFront key pairs, geographic restrictions at the whole-distribution country level, viewer mutual TLS, and edge token validation via CloudFront Functions that MUST actually verify a signature, not just check token presence), caching (a cache policy — not the cache behavior — holds TTLs and the cache key; a minimum TTL above zero overrides origin no-cache/no-store/private headers), CloudFront Functions vs Lambda@Edge (viewer-facing sub-millisecond transforms vs network access / origin-facing events), custom-domain TLS certificates (ACM always in us-east-1 regardless of where the app runs), pay-as-you-go vs Flat Rate Pricing, and observability (standard/real-time logs, CloudTrail for the management plane). Use when deciding whether to put CloudFront in front of an origin, creating a distribution, locking an origin, restricting who can view content, debugging stale-cache or access-denied issues, or setting up a custom domain."
license: MIT
---

# Amazon CloudFront

CloudFront does three jobs at once — accelerates delivery, absorbs Layer 3/4 DDoS at the edge, and is the single attachment point for the rest of the edge security/compute stack (WAF, Shield, CloudFront Functions, Lambda@Edge, Route 53, ACM). Design the edge once, around that attachment point, rather than bolting pieces on ad hoc. Distilled from AWS's own CloudFront agent skill and `docs.aws.amazon.com`, fetched 2026-09. Cross-links: [[aws-s3]] for the origin side of an S3-backed distribution, [[secure-coding]] for the signing-key and header hardening throughout.

> CloudFront is a **global** service — its API calls and every ACM certificate it uses are made in **`us-east-1`**, regardless of where the application or its origin actually runs.

## Is CloudFront the right layer?

| Signal | Fit |
|---|---|
| Cacheable/static content, or dynamic web/API traffic worth accelerating | Yes — caching and edge TLS termination reduce latency and origin load |
| Need Layer 3/4 DDoS absorption and Layer 7 filtering at the edge | Yes — Shield is built in, WAF attaches directly |
| HTTP/HTTPS only | Yes |
| Non-HTTP (raw TCP/UDP), a static-IP entry point for partner allowlisting, or sub-minute failover | **No — use Global Accelerator instead** |

CloudFront serves more than media — static assets, dynamic pages, REST/GraphQL APIs, and large downloads are all legitimate CloudFront workloads. For dynamic/API traffic it still helps: TLS termination closer to the user, persistent connection pooling to the origin (fewer TCP/TLS handshakes), optimized edge-to-origin network paths.

## Origin type — pick the locking mechanism by type

| Origin | Approach |
|---|---|
| Private S3 bucket | Standard bucket origin + **origin access control (OAC)** — the default |
| S3 that must *also* be public outside CloudFront | S3 website endpoint as a custom origin — an exception, not the default |
| ALB, NLB, or EC2 in a private subnet | **VPC origin** |
| Public, on-premises, or other-cloud HTTP origin | Custom origin, optionally with **origin mutual TLS** |

These three mechanisms aren't interchangeable — they're chosen by origin type, and an origin can need more than one (e.g. a VPC origin *and* origin mTLS).

## Non-negotiables

1. **Every content control is bypassed while the origin is directly reachable.** Signed URLs, geo restrictions, viewer mTLS, edge token checks — none of them hold unless the origin is *also* locked (OAC for S3, VPC origin or origin mTLS for everything else). Never present a content control as "done" while the origin still answers requests directly.
2. **Default to origin access control (OAC), not origin access identity (OAI), for any new S3 origin.** OAI doesn't cover all Regions, SSE-KMS, or write requests — reserve it for migrating an existing legacy setup.
3. **Scope every service-principal grant with both `aws:SourceArn` and `aws:SourceAccount`.** The S3 bucket policy admitting `cloudfront.amazonaws.com`, and the KMS key policy if using SSE-KMS, must both be scoped to the *specific* distribution — a broad grant is a confused-deputy hole.
4. **A cache policy — not the cache behavior — holds the TTLs and cache key.** Looking for per-path TTL settings on the behavior itself is the wrong place; attach a cache policy.
5. **A minimum TTL above zero overrides origin `no-cache`/`no-store`/`private` directives** for at least that long. If CloudFront keeps serving stale content despite correct origin headers, this is almost always why.
6. **A CloudFront Function must be published to the `LIVE` stage before it can be associated with a distribution** — a function association failing immediately after writing the code is this, not a permissions issue.
7. **An edge token-validation function must actually verify the signature**, not just check that a token is present and non-empty. A presence-only check is a false sense of security — any arbitrary string passes.
8. **Enable standard logging at distribution creation, not after.** Request access logs are the only audit/forensic trail for what was actually served; enable AWS CloudTrail separately to capture *who changed the distribution's configuration* — access logs don't record that.
9. **Store signing keys (for signed URLs/cookies) in Secrets Manager or SSM Parameter Store SecureString** — never on disk or in application config.

## CloudFront Functions vs Lambda@Edge

| Need | Choose |
|---|---|
| Lightweight viewer-facing transform: URL rewrite, header manipulation, redirect, token check | **CloudFront Functions** — viewer-request/viewer-response only, sub-millisecond |
| Network access, or origin-request/origin-response events, or a larger runtime | **Lambda@Edge** — higher latency and cost, but strictly more capable |

## Pricing

**Pay-as-you-go** (per distribution) fits variable or low, unpredictable traffic. **Flat Rate Pricing (FRP)** fits predictable, sustained high-volume traffic — lower per-GB rates under a fixed monthly commitment, with overage at pay-as-you-go rates; the two coexist, and existing distributions can move to FRP through the console. Don't quote a specific commitment threshold — check the pricing page or account team, since commitment levels change.

## References

- `references/origins-and-caching.md` — creating a distribution, cache policies vs behaviors, CloudFront Functions vs Lambda@Edge in depth, the distribution-creation procedure.
- `references/protecting-origins.md` — OAC + scoped bucket policy for S3, VPC origins for private ALB/NLB/EC2, origin mutual TLS for public/hybrid origins.
- `references/securing-content.md` — signed URLs vs signed cookies, geographic restrictions, viewer mutual TLS, edge token validation, and why every one of these must pair with origin locking.
