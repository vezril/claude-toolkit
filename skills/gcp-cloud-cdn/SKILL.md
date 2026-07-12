---
name: gcp-cloud-cdn
description: "Google Cloud CDN — edge caching bolted onto external Application Load Balancers (not a standalone service): enable with --enable-cdn on backend services or backend buckets, control caching via cache modes (CACHE_ALL_STATIC / USE_ORIGIN_HEADERS / FORCE_CACHE_ALL), TTL hierarchy (client/default/max), cache keys (query-string include/exclude, headers, named cookies), negative caching, serve-while-stale, signed URLs/cookies for private content, and slow rate-limited invalidation (design around it with versioned URLs). Use when speeding up HTTP(S) delivery of static assets or Cloud Storage content behind a global external Application LB, tuning cache hit ratios, protecting paid content, or debugging why responses aren't cached."
license: MIT
---

# Google Cloud CDN

Content delivery network for HTTP(S) web content, built into Google's global external
Application Load Balancers and served from Google Front Ends (GFEs) at the network edge.

## The mental model

Cloud CDN is **not a standalone service you point DNS at**. It is a *flag on a backend* of a
global (or classic) external Application Load Balancer:

- **Backend service** (Compute Engine MIGs, GKE Ingress/Gateway, internet NEGs for external
  origins) or **backend bucket** (Cloud Storage) + `--enable-cdn` = CDN on.
- On a request, the GFE nearest the user computes the **cache key**; a hit is answered at the
  edge, a miss flows through the LB to the origin and the response is cached *if* the
  **cache mode** + response headers permit.
- Caching is reactive: nothing is pre-loaded; an object enters cache only after a request
  passes through for it.
- Everything else (routing, TLS certs, Cloud Armor, URL maps) is the load balancer's job —
  Cloud CDN only decides *what gets cached, under which key, for how long*.

## Enabling it

```bash
# Backend service (LB already exists)
gcloud compute backend-services update MY_BACKEND \
    --enable-cdn --cache-mode=CACHE_ALL_STATIC --global

# Backend bucket (Cloud Storage origin)
gcloud compute backend-buckets create MY_BB \
    --gcs-bucket-name=MY_BUCKET --enable-cdn --cache-mode=CACHE_ALL_STATIC
# then: url-map -> target proxy -> global forwarding rule as usual
```

## Controlling what gets cached

**Three cache modes** (`--cache-mode=`):

| Mode | Behavior | Use when |
|---|---|---|
| `CACHE_ALL_STATIC` (default) | Respects origin cache directives; additionally auto-caches static MIME types (CSS, JS, images, video, audio, fonts, PDF) that lack directives. HTML and JSON are **not** auto-cached. | General web apps |
| `USE_ORIGIN_HEADERS` | Caches only responses with valid caching directives from the origin; everything else passes through. | Origin owns cache policy |
| `FORCE_CACHE_ALL` | Caches all successful responses, ignoring `private`/`no-store`/`no-cache`. Does **not** override `Vary`. | Purely public content, e.g. a private-ACL Cloud Storage bucket |

**TTL hierarchy** (`--client-ttl`, `--default-ttl`, `--max-ttl`; also on backend-buckets):
- Origin `Cache-Control: s-maxage`/`max-age` wins when present (except in `FORCE_CACHE_ALL`,
  where default TTL rules); `--default-ttl` (default 3600s) fills in when absent;
  `--max-ttl` (default 86400s) caps everything; `--client-ttl` (default 3600s) caps the
  `max-age` browsers see. Max settable value: 31,622,400s (1 year). `--default-ttl=0`
  forces revalidation each time.
- Expired entries with `ETag`/`Last-Modified` are revalidated (`If-None-Match`/
  `If-Modified-Since`, 304 refreshes the entry); without validators the entry is refetched.
- `--serve-while-stale` (default 86400s, max 604800s) serves expired content while
  revalidating asynchronously — cheap origin-outage insurance.

**Cache keys** — the identity of a cached object:
- Backend services default to full URI: protocol + host + path + query string. Trim with
  `--no-cache-key-include-protocol`, `--no-cache-key-include-host`, and query-string control
  (`--cache-key-query-string-whitelist=` / `--cache-key-query-string-blacklist=`).
  Backend buckets ignore protocol/host by nature.
- Add request variance with `--cache-key-include-http-header=` or
  `--cache-key-include-named-cookie=`.
- Every excluded component is a correctness risk: excluding something the response actually
  varies on serves one user's content to another.

**Negative caching**: `--negative-caching` caches errors/redirects (300/301/302/307/308/404/
405/410/421/451/501) with sane defaults (404 = 120s, 405/501 = 60s); tune per-code with
`--negative-caching-policy='404=60,405=120'`. Shields origins from 404 storms.

## Private content: signed URLs and cookies

- Attach up to 3 keys per backend: `gcloud compute backend-services add-signed-url-key
  BACKEND --key-name K --key-file F` (128-bit random, base64url). Rotate by adding new,
  deleting oldest.
- Sign: `gcloud compute sign-url "URL" --key-name K --key-file F --expires-in 1h [--validate]`
  → appends `Expires`, `KeyName`, `Signature` (HMAC-SHA1) query params.
- `--signed-url-cache-max-age` bounds how long a signed response stays cached.
- Signed **cookies** grant access to a URL *prefix* (sessions, HLS/DASH segment trees);
  signed **URLs** grant one URL (download links).
- The CDN only gates the edge: origins must still validate signatures (and Cloud Storage
  buckets must drop `allUsers` read), or anyone who finds the origin bypasses the gate.

## Gotchas

- **Invalidation is an escape hatch, not a workflow**: rate-limited to ~500 invalidation
  requests/minute, ~10s to take effect, wildcard `*` only as the trailing character, no
  per-query-string targeting, and it doesn't touch browser or ISP caches. Design with
  **versioned URLs** (`/app.3f9c.js`) and correct TTLs; invalidate
  (`gcloud compute url-maps invalidate-cdn-cache MAP --path "/images/*"`) only for mistakes.
- **Never cached regardless of mode**: `Set-Cookie` responses, non-GET methods, `Vary` on
  anything beyond a short allowlist (Accept, Accept-Encoding, Origin, etc.) — a stray
  `Vary: Cookie` or `Vary: User-Agent` silently kills caching even under `FORCE_CACHE_ALL`.
  Size limits: 10 MiB without byte-range support at origin, 100 GiB with.
- `CACHE_ALL_STATIC` not caching your HTML/JSON API responses is by design — set explicit
  `Cache-Control: public, max-age=...` or switch modes.
- **Pricing shape**: cache data transfer out (egress, ~$0.02–0.20/GiB tiered by destination
  and monthly volume) + cache fill ($0.01–0.04/GiB by source/dest geography) + HTTP(S) cache
  lookups ($0.0075 per 10,000 GET/HEAD). Hits replace normal Compute/Storage egress charges;
  misses add LB/Storage processing. No listed charge for invalidation.
- Logging: cache hit/miss decisions land in the LB's Cloud Logging entries; async
  revalidations show a `Cloud-CDN-Google` User-Agent.

## vs siblings

- **[[gcp-media-cdn]]** — separate product on Google's deeper edge/ISP cache tier, built for
  streaming video and large-file egress at scale; allowlist-only onboarding, its own API
  (`EdgeCacheService`). Cloud CDN is the general web-acceleration tier attached to your LB.
- **[[gcp-cloud-storage]]** — a bucket alone serves globally but every request hits the
  bucket; fronting it with a backend bucket + CDN adds edge caching, custom domains + certs,
  and signed-URL semantics that differ from GCS's own signed URLs.

## Related

- [[gcp-load-balancing]] — the host: URL maps, backend services/buckets, target proxies
- [[gcp-media-cdn]] — streaming/large-file sibling
- [[gcp-cloud-storage]] — the usual static origin
- [[gcp-certificate-manager]] — TLS certs on the LB frontend
- [[gcp-iap]] — identity-gating apps behind the same LB
- [[gcp-cloud-logging]], [[gcp-cloud-monitoring]] — cache hit-rate observability

Sources: https://docs.cloud.google.com/cdn/docs/overview, https://docs.cloud.google.com/cdn/docs/caching, https://docs.cloud.google.com/cdn/docs/using-cache-keys, https://docs.cloud.google.com/cdn/docs/using-ttl-overrides, https://docs.cloud.google.com/cdn/docs/using-negative-caching, https://docs.cloud.google.com/cdn/docs/serving-stale-content, https://docs.cloud.google.com/cdn/docs/using-signed-urls, https://docs.cloud.google.com/cdn/docs/cache-invalidation-overview, https://docs.cloud.google.com/cdn/docs/setting-up-cdn-with-bucket, https://cloud.google.com/cdn/pricing (fetched 2026-07).
