# Securing content

Source: AWS's CloudFront agent skill (`securing-your-content.md`) + docs.aws.amazon.com. Fetched 2026-09. Every control here answers a different question — and **every one of them only holds if the origin is also locked** (see `protecting-origins.md`). Pair, don't substitute.

## Which control answers which question

| Question | Control |
|---|---|
| Is this viewer authorized (paying, licensed)? | Signed URLs or signed cookies |
| Is this viewer in an allowed country? | Geographic restrictions |
| Does this client hold a valid certificate? | Viewer mutual TLS |
| Does this request carry a valid auth token? | A CloudFront Function on viewer-request |

They're independent and combinable.

## Identity: signed URLs vs signed cookies

| | Use when |
|---|---|
| Signed URLs | A single file, or a client without cookie support. Signature/policy/expiration ride in query-string parameters. |
| Signed cookies | Many files, or the URL must stay unchanged. Same data goes in cookies instead. |

- Configure a **trusted key group** on the distribution; the application issues the signed URLs/cookies. **The legacy CloudFront key pairs mechanism is deprecated — don't use it for anything new.**
- **Store the private signing key in Secrets Manager or SSM Parameter Store SecureString** — never on disk or in application config.
- **Rotate signing keys on a schedule and on suspected compromise**, and keep expirations short — a signed URL/cookie stays valid until it expires, full stop; there's no revocation short of rotating keys.

## Location: geographic restrictions

Applies at the **whole-distribution, country level** — not per path. If you need finer-than-country or per-path geo control, that's a separate distribution or a third-party geolocation layer, not a CloudFront-native option.

## Client certificate: viewer mutual TLS

- Create a **trust store** from a PEM CA bundle in S3, then enable viewer mutual authentication in **required** mode (rejects any client without a valid certificate — `optional` lets unauthenticated clients through, `passthrough` just forwards the raw cert to the origin without CloudFront enforcing anything).
- **Disable HTTP/3 and set every cache behavior to HTTPS-only or redirect-to-HTTPS** before enabling viewer mTLS — leaving either misconfigured returns a configuration error when you try to enable it.
- **The trust store reads its CA bundle from S3 only at creation time** — rotating or revoking a CA requires a manual trust store update; a stale CA in the trust store keeps granting access until you do that update.

## Authorization token: validate at the edge

Use a **CloudFront Function on viewer-request** for lightweight bearer-token/JWT checks; route anything needing network access (e.g. calling out to validate against an external service) or origin-facing logic to Lambda@Edge instead.

**The function must perform real signature verification.** A function that only checks token presence and length is not a security control — any arbitrary string of the right shape passes it. The function must, at minimum: read the token from the `authorization` header, reject a missing/over-length token with 401, and **verify the token's cryptographic signature** (e.g. via `crypto.subtle` in a CloudFront Functions runtime that supports it) before returning `event.request`. Publish to `LIVE` and associate only after signature verification is actually implemented — not before.

## Pair every control with origin locking

Restated because it's the single most common way these controls fail in practice: **a content control is not "done" while the origin is still directly reachable.** Signing, geo-restricting, or token-gating the CloudFront path does nothing if a viewer can bypass CloudFront entirely and hit the S3 bucket, ALB, or origin server directly. Confirm origin locking (OAC / VPC origin / origin mTLS, per `protecting-origins.md`) as part of completing *any* content control here — never present one as finished on its own.

## Defense in depth

Attach a **response headers policy** (HSTS, CSP, X-Frame-Options, X-Content-Type-Options) alongside these controls — they defend against a different attack class (clickjacking, MIME sniffing, protocol downgrade) than access gating does. And pair everything with **AWS WAF** for Layer 7 filtering — these content controls decide *who* reaches content, not whether a given request is malicious.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Viewers still download files directly despite signed URLs | Origin is directly reachable — lock it |
| Geo restriction "doesn't apply to just this one path" | It's whole-distribution by design — use a separate distribution |
| Enabling viewer mTLS errors out | HTTP/3 still enabled, or a behavior still allows plain HTTP |
| Clients with no certificate still get through | Validation mode is `optional` or `passthrough`, not `required` |
| Token-check function association fails | Function wasn't published to `LIVE` first |

## Pitfalls

- Treating a token-presence check as "authentication" when there's no signature verification.
- Assuming signed URLs can be revoked — they can't; only key rotation and expiry end their validity.
- Enabling a content control and calling the origin "secured" without confirming it's actually locked.
- Forgetting the viewer mTLS trust store doesn't auto-refresh — a revoked CA silently keeps working until you manually update it.
