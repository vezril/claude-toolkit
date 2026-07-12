---
name: gcp-media-cdn
description: "Google Cloud Media CDN — planet-scale deep-edge CDN built on the edge caches that serve YouTube, optimized for HLS/DASH streaming and large file downloads (Tbps-scale egress). Its own resource family (EdgeCacheService -> routes -> EdgeCacheOrigin, EdgeCacheKeyset for signed playback), not the load-balancer-attached Cloud CDN. Use when delivering live/VOD video or big binaries at scale, configuring edge-cache YAML/gcloud resources, signed tokens/dual-token auth, origin shielding/failover, cache invalidation, or choosing Media CDN vs Cloud CDN."
license: MIT
---

# GCP Media CDN

Media delivery CDN running on Google's deepest edge tier — the global edge-cache
infrastructure that serves YouTube, in thousands of locations. Built for
high-throughput egress: streaming video (HLS/DASH, live and VOD) and large file
downloads, at Tbps scale. It is deliberately NOT a web-asset CDN — Google's own
docs compare misusing it for JS/CSS to "using BigQuery for 5-GB tables."

Access is gated: a project must be enabled for Media CDN by a Google Cloud sales
representative or account team before the APIs work. Pricing is likewise
sales/quote-driven rather than public rate-card-first.

## The mental model

Media CDN is its own resource family (`gcloud edge-cache ...`, under the Network
Services API) — it does NOT hang off an external Application Load Balancer the
way Cloud CDN does. Three resources:

1. **EdgeCacheService** — the front door. Owns hostnames, TLS certs, and routing:
   `hostRules` map hostnames to a `pathMatcher`; each pathMatcher holds
   `routeRules` with unique priorities 1–999 (lower wins; catch-all at 999 with
   `prefixMatch: /`). A route matches on exactly one of `prefixMatch`,
   `fullPathMatch`, or `pathTemplateMatch` (`*` = one segment, `**` = many,
   `{var}` / `{path=**}` named captures; max 10 operators), plus optional header,
   query-param, and method matches (ANDed). Route action = fetch from an origin
   or redirect (301/302/303/307/308), with per-route `cdnPolicy` (cache mode +
   TTLs), `urlRewrite`, `headerAction`, and `corsPolicy` (OPTIONS answered at edge).
2. **EdgeCacheOrigin** — an upstream: Cloud Storage bucket (public, or private via
   IAM service account), S3-compatible bucket (private via AWS Signature V4),
   Azure Blob, an external ALB, or any public HTTP(S) server. Protocol defaults to
   HTTP/2 (needs valid origin TLS); HTTP/1.1 over TLS or plaintext also supported.
   Failover chain: `maxAttempts` retries on the current origin, `retryConditions`
   (connect failure, 5xx, 404, 429...), then `failoverOrigin` — max 4 attempts
   total, and only safe methods (GET/HEAD/OPTIONS) are ever retried.
3. **EdgeCacheKeyset** — named set of keys for signed playback. Multiple keys per
   keyset for rotation; any listed key validates. Backs both signature mode
   (`REQUIRE_SIGNATURES`: signed URLs/cookies, Ed25519) and token mode
   (`REQUIRE_TOKENS`: short-lived tokens, incl. dual-token auth for streaming —
   a Media CDN-only feature). Only GET/HEAD/OPTIONS can be signed; expirations
   are mandatory (sign for at least the stream length).

Config workflow is YAML-first: `gcloud edge-cache services export/import`, plus
`gcloud edge-cache origins|keysets ...`, or Terraform (`google_network_services_edge_cache_*`).

## Caching behavior

- **Cache modes** (per route): `CACHE_ALL_STATIC` (default — obeys origin
  directives, else caches static MIME types with defaultTtl), `USE_ORIGIN_HEADERS`
  (cache only what the origin explicitly allows; no TTL overrides),
  `FORCE_CACHE_ALL` (ignore origin directives — never use for per-user content),
  `BYPASS_CACHE` (debugging only).
- **TTLs**: defaultTtl 3600s, maxTtl 86400s (both rangeable 0–31,536,000s =
  1 year); clientTtl optional, capped at 86400s and <= maxTtl.
- **Negative caching**: opt-in per-status TTLs (404 = 120s, 301/308 = 600s, etc.)
  for 3xx/4xx/5xx codes — vital for live streaming where players hammer
  not-yet-published segment URLs.
- **Cache keys**: host + path + sorted query string by default (protocol excluded);
  query params can be include/exclude-listed; headers and cookies opt-in only.
- **Eviction is popularity-based, not TTL-guaranteed**: long-tail objects may be
  evicted early; popular content gets revalidated with origin HEAD requests.

## Origin shielding

Built-in and hierarchical: deep edge caches -> peering edge -> long-tail regional
caches, so misses collapse upward instead of stampeding the origin. Default
shielding follows user location; optional "flexible shielding" pins all cache
fill through a chosen geography — useful for a single-region origin with global
viewers (better offload, fewer long-haul fills).

## Invalidation

`gcloud edge-cache services invalidate-cache` by host/path (prefix + wildcard) or
by **cache tags** (`Cache-Tag` response header from origin; built-in tags for
status code, MIME type, and origin are automatic). Up to 10 tags per request;
tags OR together, host+path+tags AND together. Global propagation typically
under a minute across thousands of locations. Still: prefer versioned URLs for
routine content changes; invalidation is the correction tool, not the workflow.

## Gotchas and pricing shape

- **Onboarding gate**: no self-service enablement — sales/account team must
  turn it on per project. Plan lead time.
- **Pricing shape** (quote-driven; no simple public rate card like Cloud CDN):
  billed on cache egress per GiB (region-dependent, volume-tiered), cache fill
  per GiB, and requests. Cloud Storage origins get storage data-transfer charges
  waived — you pay Media CDN cache-fill rates instead. High cache-hit ratios are
  the whole cost model; watch cache-fill on live workloads with short TTLs.
- Signed-request expiry must be in the future by >= 1 minute or the stream
  duration, whichever is greater — short expirations break mid-stream.
- FORCE_CACHE_ALL on a route serving personalized responses is the classic
  cross-user data leak; keep it to immutable segment/manifest paths.
- No FedRAMP/HIPAA coverage (as of docs) — regulated workloads go to Cloud CDN.

## vs Cloud CDN

- **Audience**: Media CDN = streaming media + large downloads (throughput);
  Cloud CDN = websites/APIs, small mixed static+dynamic assets (latency at rps).
- **Edge depth**: Media CDN sits in Google's deepest edge tier (ISP-embedded,
  thousands of locations) with tiered origin shielding; Cloud CDN uses Google's
  standard edge PoPs, shielding not built-in.
- **Resource model**: Media CDN = standalone EdgeCacheService/Origin/Keyset
  resources; Cloud CDN = a checkbox + policy on an external Application Load
  Balancer backend.
- **Auth**: both do signed URLs/cookies; only Media CDN has signed tokens and
  dual-token authentication.
- **Access**: Cloud CDN is self-service with public pricing; Media CDN is
  sales-gated. Both speak HTTP/3-QUIC, HTTP/2, TLS 1.2/1.3, global anycast v4/v6.

## Related

[[gcp-cloud-cdn]], [[gcp-cloud-storage]], [[gcp-load-balancing]], [[gcp-certificate-manager]],
[[gcp-cloud-dns]], [[gcp-cloud-monitoring]], [[gcp-cloud-logging]], [[gcp-iam]]

Sources: https://docs.cloud.google.com/media-cdn/docs (+ /docs/overview, /docs/caching,
/docs/origins, /docs/routing, /docs/signed-requests, /docs/cache-invalidation,
/docs/choose-cdn-product) (fetched 2026-07).
