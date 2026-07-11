# Feature flags, CSS status, and standards positions

Sources: webkit.org/feature-policy/, /css-status/, /standards-positions/ (fetched 2026-07).

## The feature policy (how engine features ship)

This is WebKit's *engine-development* policy — not the web `Permissions-Policy` header.

- **Runtime flags are the core mechanism**: new author-facing features land behind flags, **disabled on trunk** while immature (young implementation, unstable spec, not web-exposed, or trunk-stability risk).
- **Enabled on trunk** when the standard and implementation are mature or web compat demands it; **flag removed** (always-on) when "most or all major ports ship it and none plan to turn it off".
- **Ports decide shipping** — the policy explicitly does not set release criteria for Safari/GTK/WPE; each port flips flags on its own schedule (Safari Technology Preview is in practice where Apple's port enables experimental flags first).
- Compile-time flags exist for platform-specific backends, resource-constrained ports, or trunk-hackability; runtime flags preferred.
- Naming: **no prefixes** on new web-exposed features; non-exposed features prefer a product prefix over `-webkit-`.

Embedder reading: an "experimental" flag in your WKWebView/port is a feature WebKit itself considers not ready — ship it off by default; *you* own your port's flag decisions.

## css-status (trunk truth for CSS)

- Live table generated from `Source/WebCore/css/CSSProperties.json` on WebKit **trunk** (fetched at page load — reflects the repo, not any shipped Safari). The JSON is machine-readable if you want to check programmatically.
- Status vocabulary: **Supported**, **In Development**, **Experimental** (behind a flag), **Non-standard**, **Obsolete**; untagged mainstream properties default to supported (~500 of them).
- 2026-07 snapshot examples — supported: `color-scheme`, `paint-order`; in development: `text-spacing-trim`, `overflow-anchor`, `block-step-*`; experimental: `line-clamp`, `max-lines`, `block-ellipsis`; non-standard: `-webkit-font-smoothing`, `-webkit-text-size-adjust`; obsolete: `-webkit-box-*`.
- **The general JS/web-API status page (webkit.org/status/) is retired** — it now points to **MDN** and **Can I Use** for support data and to standards-positions for project intent. CSS status remains maintained.

## standards-positions (the roadmap oracle)

- Public record of the WebKit project's opinion on proposed web specs: repo **github.com/WebKit/standards-positions** (decided in issues; webkit.org renders `summary.json`).
- Positions: **support** ("worth prototyping and iterating"), **neutral** (not harmful, unconvinced), **oppose** ("harmful in its current state"); process labels blocked/duplicate/invalid/meta.
- **Position ≠ implementation ≠ shipped** — WebKit may support a spec it never implements and implement one it dislikes for compat. Only the applied label is official, not issue comments.
- Requesting: file a *request-for-position* issue; a position proposal with rationale stands ≥7 days; unopposed → label applied.
- Corpus (2026-07): ~565 requests — 178 support, 27 oppose, 12 neutral, ~334 unpositioned. Notable: **oppose** WebUSB, Web Bluetooth, Topics API; **support** WebGPU/WGSL, Navigation API, View Transitions, Popover API, CSS Nesting.

## Using the three in practice

- Need a CSS feature? → css-status (or CSSProperties.json). Flag-gated = test behind the flag, don't ship reliance on it.
- Need a JS/web API? → MDN / Can I Use for today; standards-positions for whether WebKit ever intends to.
- An **oppose** (WebUSB, Web Bluetooth, Topics…) means the capability will likely never land upstream — a custom browser wanting it signs up to maintain a fork of that surface alone, against the privacy posture the engine enforces.
- Cross-reference, never conflate: standards-positions = intent; css-status/flags = trunk state; your port's defaults = what users get.
