# Auth, secrets, crypto/TLS, secure defaults & the SDLC

Defensive reference. References: OWASP Top 10 (A01 Broken Access Control, A02 Cryptographic Failures, A07 Auth Failures, A05 Misconfiguration), OWASP ASVS/Cheat Sheets, CWE-287/862/798.

## Authentication & authorization

- **Authenticate, then authorize, on every request, server-side.** UI/gateway checks are convenience, not security — enforce at the resource.
- **Deny by default.** Grant access explicitly; missing/unknown → denied.
- **Authorize the object, not just the action (avoid IDOR/CWE-639).** When a request references an id, verify the caller owns/may access *that* resource — don't trust client-supplied ids.
- **Passwords:** never store plaintext or fast hashes — use a slow KDF (**Argon2id**, scrypt, bcrypt, PBKDF2) with a per-user salt ([[cryptography]]). Enforce length over complexity; support MFA; rate-limit and lock out on repeated failures; use constant-time comparison for secrets/tokens.
- **Sessions/tokens:** high-entropy random session ids (CSPRNG); cookies `Secure; HttpOnly; SameSite`; rotate on privilege change; sensible expiry/idle timeout; server-side revocation. For JWTs: verify signature with a pinned algorithm (reject `alg: none`/algorithm confusion), validate `exp`/`aud`/`iss`, keep them short-lived, and don't put secrets in the (readable) payload.

## Secrets management

- **No secrets in source, config-in-VCS, container images, logs, error messages, or URLs.** Load from a secrets manager (Vault, cloud KMS/Secrets Manager) or injected env; reference by name.
- **Scan for committed secrets** (gitleaks/trufflehog) in CI and pre-commit; rotate anything that leaks (and assume git history exposed it).
- **Redact** secrets/PII in logs and exception messages; keep keys/tokens out of stack traces.
- Prefer short-lived, scoped credentials and per-service identities over long-lived shared keys.

## Cryptography & transport (use, don't invent)

- Defer to [[cryptography]] for the details. In short: **use vetted libraries** (libsodium/Tink/platform), **AEAD** (AES-GCM, ChaCha20-Poly1305) with unique nonces, **CSPRNG** for keys/IVs/tokens (`SecureRandom`, never `Math.random()`/`rand()`), modern key sizes (AES-256, RSA≥2048 or X25519/Ed25519), **SHA-256/SHA-3** (never MD5/SHA-1), and HMAC (not `hash(key‖msg)`). No homegrown crypto, no ECB.
- **TLS everywhere** for data in transit; modern TLS (1.2+/1.3), validate certificates and hostnames (don't disable verification), HSTS for web; mutual TLS for service-to-service where warranted.
- Encrypt sensitive data at rest; classify what's actually sensitive and minimize what you store.

## Secure defaults, headers & config

- **Fail closed**, ship secure defaults (features that weaken security are opt-in, not opt-out).
- **Minimize disclosure:** generic client-facing errors + a correlation id; full detail only in server logs; no stack traces, versions, or internal paths returned to clients.
- Web hardening: strict **Content-Security-Policy**, `X-Content-Type-Options: nosniff`, `X-Frame-Options`/frame-ancestors, HSTS; **CORS** with an explicit origin allow-list (never `*` together with credentials); cookies as above.
- Disable debug endpoints, default/sample accounts, directory listings, and verbose banners in production; review framework defaults.
- **Logging & monitoring:** log security-relevant events (authn/authz decisions, failures) without logging secrets/PII; ensure logs are tamper-resistant and actually monitored (A09).

## Dependencies & the secure SDLC

- **Dependency hygiene (A06):** track known-vulnerable libraries with SCA (OWASP Dependency-Check, `npm audit`, Dependabot, Snyk); pin and update promptly; prefer well-maintained libraries; verify integrity (checksums/signatures, lockfiles).
- **Threat-model** designs early (trust boundaries, what an attacker controls, what they're after — ties to [[cryptography]]'s professional-paranoia mindset and [[event-storming]]/[[domain-driven-design]] for the domain).
- **Automate checks in CI:** SAST (static analysis/linters with security rules), DAST (dynamic scanning), SCA (dependencies), secret scanning, and fuzzing for parsers (see `memory-safety.md`).
- **Security review** as part of code review: walk the trust boundaries and each sink; the `crypto-reviewer` agent covers the crypto slice. Clear, simple code ([[clean-code]], [[software-design]]) is easier to review and has fewer places for vulnerabilities to hide.

## Review checklist

- Every endpoint authenticates and authorizes server-side, denies by default, and checks object ownership (no IDOR)?
- Passwords via a slow salted KDF; tokens/sessions high-entropy, scoped, expiring, revocable; JWTs verified with a pinned alg?
- No secrets in code/VCS/logs/images; secret scanning + rotation in place?
- Crypto via vetted libs (AEAD, CSPRNG, modern sizes); TLS enforced with cert/hostname validation?
- Secure defaults, minimal error disclosure, security headers, CORS allow-list, debug off in prod?
- Dependencies scanned and patched; SAST/DAST/SCA/secret-scan in CI?
