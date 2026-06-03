---
name: secure-coding
description: Defensive secure-coding practices — how to write and review code so common vulnerability classes can't occur. Covers the security mindset (trust boundaries, validate untrusted input, least privilege, defense in depth, fail safe/closed, the weakest-link property), and prevention of the major weakness classes: memory-safety bugs (buffer/stack/heap overflow, use-after-free, integer overflow) and the compiler/OS mitigations that harden against them; injection (SQL/command/LDAP/XSS/path-traversal/format-string) via validation, parameterization, and output encoding; unsafe deserialization and SSRF; authentication/authorization mistakes; secrets management; safe use of cryptography and TLS; and secure defaults, logging, and the secure SDLC/review. Use whenever writing or reviewing code that handles untrusted input, parses data, builds queries/commands, manages auth or secrets, does crypto/TLS, or processes files/network data — i.e. hardening software against attack. Defensive/prevention-focused (not exploitation); language-agnostic with JVM/Scala notes; complements the cryptography skill.
---

# Secure Coding (defensive)

How to write and review code so that whole classes of vulnerabilities **can't happen** — the prevention side of security. This skill is strictly **defensive**: it describes weakness classes at the level needed to *avoid and review for* them, and points to hardening, not to exploitation. Language-agnostic principles with JVM/Scala notes. Complements [[cryptography]] (and the `crypto-reviewer` agent), and shares the "weakest-link" mindset from *Cryptography Engineering*.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Otherwise this is the default security posture.

## The security mindset

- **Define trust boundaries.** Anything crossing into your code from outside — network requests, files, env, CLI args, DB rows, message payloads, other services, even other modules — is **untrusted** until validated. Most vulnerabilities live where untrusted data meets a powerful operation (a query, a buffer, a command, a deserializer).
- **Validate input at the boundary, encode/escape at the sink.** Check structure/length/range/charset as data enters; encode appropriately for the context where it's used (SQL, shell, HTML, path). Prefer allow-lists over deny-lists.
- **Least privilege.** Code, processes, credentials, and tokens get the minimum access they need (narrow DB grants, drop privileges, scoped tokens, read-only where possible).
- **Defense in depth.** Don't rely on one control; layer them (validation + parameterization + least-privilege DB user). Assume any single layer can fail.
- **Fail safe / fail closed.** On error or ambiguity, deny rather than allow; never leak secrets or internals in errors; default to the secure option.
- **Weakest-link property** ([[cryptography]]): a system is only as strong as its weakest part — usually input handling, auth, key management, or config, not the algorithm. Spend attention there.
- **Don't roll your own security primitives** — use vetted libraries/frameworks for crypto, authn, parsing, and serialization (see [[cryptography]]).

## Always-apply defaults

1. **Treat all external input as hostile** — validate type/length/range/format at the boundary; reject what doesn't fit an allow-list; never trust client-side validation alone.
2. **Never build a query/command/path/markup by string concatenation with untrusted data** — use parameterized queries / prepared statements, safe process APIs (argument arrays, no shell), path canonicalization + containment checks, and context-aware output encoding.
3. **Prefer memory-safe languages and bounds-safe APIs**; where you must touch unsafe code (C/C++, JNI, `sun.misc.Unsafe`), use bounded operations, check all arithmetic, and enable the compiler/OS mitigations (canaries, ASLR, NX/DEP, FORTIFY).
4. **Don't deserialize untrusted data with a code-executing deserializer** (Java native serialization, pickle, etc.) — use data-only formats (JSON/protobuf) with strict schemas and allow-lists ([[akka-serialization]], [[modern-java]] Items 85–90).
5. **Authenticate then authorize on every request, server-side** — check permissions at the resource, not just the UI; deny by default.
6. **Keep secrets out of code and logs** — load from a secrets manager/env, never commit them, redact them in logs and errors.
7. **Use crypto correctly** — vetted libraries, AEAD, CSPRNG, modern key sizes; never homegrown ([[cryptography]]).
8. **Fail safe and minimize disclosure** — generic error messages to clients, detailed diagnostics only in server logs (with a correlation id); no stack traces or internal paths leaked.
9. **Keep dependencies patched** — track known-vulnerable libraries (SCA/`dependency-check`/Dependabot); pin and update.

## Common weakness classes (prevention)

A short map; prevention detail is in the references:
- **Memory safety** — overflow / use-after-free / integer overflow. *Prevent:* memory-safe languages, bounds-checked APIs, checked arithmetic, ownership/RAII, and mitigations (`references/memory-safety.md`).
- **Injection** — SQL, OS command, LDAP, XSS, path traversal, format string, template/expression injection. *Prevent:* parameterization, safe APIs, output encoding, canonicalization (`references/input-validation-and-injection.md`).
- **Unsafe deserialization & SSRF** — code-executing deserializers; server-side requests to attacker-controlled URLs. *Prevent:* data-only formats + schemas; URL allow-lists, no following redirects to internal ranges.
- **Auth / access control** — broken authentication, missing authorization, IDOR. *Prevent:* server-side checks at the resource, deny-by-default, session/token hygiene.
- **Secrets, crypto & transport** — hardcoded secrets, weak/misused crypto, plaintext transport. *Prevent:* secrets management, vetted crypto, TLS everywhere (`references/secrets-authz-and-platform.md`, [[cryptography]]).

## Anti-patterns (flag in review)

- Untrusted data concatenated into SQL/shell/HTML/paths; deny-list "sanitization"; trusting client-side validation.
- `strcpy`/`gets`/`sprintf`/unchecked `memcpy`; unchecked integer arithmetic feeding allocations/indices; ignoring compiler warnings.
- `printf(userInput)` (format string); `Runtime.exec(userString)` / shell `system(...)` with untrusted args.
- Java native deserialization of untrusted bytes; `enableDefaultTyping`/`@JsonTypeInfo(use=CLASS)`.
- Authorization checked only in the UI/gateway; IDs trusted from the client without ownership checks.
- Secrets in source/VCS/logs; homegrown crypto; `MD5`/`SHA-1`/`DES`/`ECB`; `Math.random()` for security; missing/weak TLS; permissive CORS `*` with credentials.
- Verbose error messages/stack traces returned to clients; outdated, known-vulnerable dependencies.

## How to use this skill

- **`references/memory-safety.md`** — preventing buffer/stack/heap overflows, use-after-free, and integer overflow; bounds-safe APIs; and the compiler/OS mitigations (stack canaries, ASLR, NX/DEP, FORTIFY_SOURCE, RELRO, CFI) — framed as defense.
- **`references/input-validation-and-injection.md`** — validation strategy and per-sink prevention for SQL, OS command, path traversal, format string, XSS, LDAP, template/expression injection, plus unsafe deserialization and SSRF.
- **`references/secrets-authz-and-platform.md`** — authentication/authorization, session & token hygiene, secrets management, safe crypto & TLS usage, secure defaults/headers/CORS, logging & error handling, dependency hygiene, and the secure SDLC (threat modeling, review, SAST/DAST/SCA).

## Related

- [[cryptography]] — correct use of crypto primitives, key management, and the weakest-link/threat-model mindset; pair with the `crypto-reviewer` agent.
- [[modern-java]] — Effective Java Items 85–90 (avoid Java serialization), 49–50 (validate parameters, defensive copies), and minimizing accessibility.
- [[akka-serialization]] — safe (Jackson/CBOR) serialization and why Java serialization is off by default.
- [[clean-code]] / [[software-design]] — clear, simple code is easier to secure and review; complexity hides vulnerabilities.
- [[functional-programming]], [[scala]] — immutability, total functions, and parsing-not-validating reduce whole bug classes.
- Defensive references: OWASP Top 10 & Cheat Sheets, CERT/SEI Secure Coding Standards, CWE.
