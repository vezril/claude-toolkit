# Input validation & injection prevention

Defensive reference. Injection bugs all share a root cause: **untrusted data is interpreted as code/structure by some downstream "sink."** The fix is always the same shape — keep data as *data* (parameterize / use safe APIs), and where data must be embedded, **encode for that specific sink**. References: OWASP Top 10 (A03 Injection), OWASP Cheat Sheets, CWE-20/89/78/79/22/134/502/918.

## Input validation strategy

- **Validate at the trust boundary**, as data enters: check type, length, range, format, and charset against an **allow-list** (what's permitted) rather than a deny-list (what's forbidden — always incomplete).
- **Parse, don't validate** (FP idiom, [[functional-programming]]): convert raw input into a precise typed value once (a smart-constructor / refined type), so the rest of the code can't receive a malformed value. Reject early, fail closed.
- **Canonicalize before checking** (decode/normalize once) so checks aren't bypassed by alternate encodings; reject ambiguous input.
- Validation is a *first* layer, **not a substitute** for safe sinks below — use both (defense in depth).

## Per-sink prevention

- **SQL injection (CWE-89).** Use **parameterized queries / prepared statements** (bind variables) for *all* untrusted values — never string-concatenate. ORMs/query builders help but check that raw fragments are also parameterized. Identifiers (table/column names) can't be bound — allow-list them. Run with a least-privilege DB account.
- **OS command injection (CWE-78).** Avoid invoking a shell with untrusted data. Use APIs that take an **argument array** (`ProcessBuilder("cmd", arg1, arg2)`, `execve`-style) so arguments aren't re-parsed by a shell; never pass user input to `sh -c`/`Runtime.exec(String)`/`system()`. Prefer a library call over shelling out at all.
- **Path traversal (CWE-22).** Canonicalize the resolved path and verify it's **contained within** the intended base directory (`realpath`/`toRealPath().startsWith(base)`); reject `..`, absolute paths, and symlinks that escape. Better: map untrusted names to opaque IDs and never use them directly as file paths.
- **Format string (CWE-134).** Never pass untrusted data as the format string — `printf("%s", userInput)`, not `printf(userInput)`; `logger.info("{}", x)`, not string-built messages.
- **Cross-site scripting / XSS (CWE-79).** **Context-aware output encoding** at render time (HTML body, attribute, JS, URL, CSS each need different encoding); prefer auto-escaping template engines; set a strict **Content-Security-Policy**; mark cookies `HttpOnly`. Sanitize rich HTML with a vetted library (e.g. OWASP Java HTML Sanitizer) only when you must allow markup.
- **LDAP / XPath / NoSQL injection.** Use parameterized/builder APIs and escape per the target's special characters; validate structure.
- **Template / expression-language / SSTI injection.** Don't render untrusted input as a template or evaluate it as an expression (SpEL/OGNL/EL); keep user data in the data model, not the template source.

## Unsafe deserialization (CWE-502)

- **Don't deserialize untrusted data with a code-executing deserializer** — Java native serialization, `pickle`, PHP `unserialize`, etc. can instantiate arbitrary types and run gadget chains.
- Use **data-only formats** (JSON, CBOR, protobuf) with a **strict schema** and a **type allow-list**; bind to known target types. For Jackson, never enable default typing / `@JsonTypeInfo(use = Id.CLASS)` (see [[akka-serialization]], [[modern-java]] Items 85–90).
- If native serialization is unavoidable, apply serialization filtering (`ObjectInputFilter` allow-list) and isolate it.

## Server-Side Request Forgery (CWE-918)

When the server fetches a URL supplied/influenced by the client: validate against an **allow-list of hosts/schemes**, resolve the hostname and **block private/link-local/metadata ranges** (`127.0.0.0/8`, `10/8`, `169.254.169.254`, etc.), **don't follow redirects** into those ranges, and disable unneeded schemes (`file:`, `gopher:`). Prefer fetching only from known, fixed endpoints.

## Review checklist

- Every SQL/command/path/markup/LDAP sink fed by untrusted data uses parameterization / a safe API / context encoding — never concatenation?
- Validation is allow-list, applied at the boundary, after canonicalization; ambiguous input rejected?
- No untrusted data used as a format string, template, or expression?
- No code-executing deserialization of untrusted bytes; data-only formats with schemas + type allow-lists?
- Outbound URL fetches allow-listed and blocked from internal ranges (SSRF)?
- A least-privilege account/permission behind each sink (defense in depth)?
