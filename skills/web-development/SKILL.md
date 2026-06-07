---
name: web-development
description: Web development — the meta/overview skill that ties the web cluster together and routes among its parts. Covers how a modern web app fits together (browser ↔ network ↔ server ↔ data), the language layer (JavaScript, TypeScript), the presentation layer (HTML/CSS), UI frameworks (React, Vue) and meta-frameworks (Next.js), the server (Node.js) and the edge/reverse proxy (Nginx); the rendering-strategy spectrum (CSR/SPA, SSR, SSG, ISR, streaming, RSC) and how to choose; the request lifecycle, client–server boundary, and API styles (REST/GraphQL/RPC); build tooling (bundlers/Vite, package managers, transpilers); state management (client vs server state); web performance (Core Web Vitals), accessibility, and web security (XSS/CSRF/CORS/CSP, auth); and testing/deployment. Use to get oriented in web development, choose a stack or rendering strategy, understand how the pieces interrelate, or decide which specific web skill to reach for. Routes to javascript, typescript, html-css, react, vue, nextjs, nodejs, nginx; pairs with ux-design, secure-coding, software-architecture, and sdlc-orchestration.
---

# Web Development

The **meta/overview** of the web cluster — how a modern web application fits together, the cross-cutting concerns, and which specialist skill to reach for. This skill owns *the big picture and the trade-offs*; the others own the depth.

The map: **[[html-css]]** (structure & style) · **[[javascript]]** / **[[typescript]]** (the language) · **[[react]]** / **[[vue]]** (UI frameworks) · **[[nextjs]]** (the full-stack meta-framework) · **[[nodejs]]** (the server runtime) · **[[nginx]]** (reverse proxy / edge). Cross-links: [[ux-design]] (the design layer), [[secure-coding]] (web security), [[software-architecture]] (system design), [[sdlc-orchestration]] (the delivery pipeline), [[docker]] / [[github-actions]] (deploy/CI), [[network-security]] (TLS/exposure).

## How a web app fits together

```
Browser (HTML/CSS/JS, a framework)
   │  HTTP(S) / WebSocket  ── over TLS, often through a CDN
Reverse proxy / edge (Nginx)  ── TLS termination, static, routing, load balancing
   │
App server (Node.js / Next.js)  ── render HTML, run API/Server Actions, auth
   │
Data (SQL / MongoDB / cache / external APIs)
```
The enduring split: a **client** (the browser, where the user is, untrusted) and a **server** (trusted, owns secrets and data), talking over HTTP. Everything in web dev is about *where code runs* and *what crosses the boundary*. ([[javascript]]'s event loop runs on both sides.)

## The layers (and the skill for each)

- **Markup & style** — semantic HTML5 + CSS (cascade, Flexbox/Grid, responsive, a11y) → [[html-css]]. You always end up producing HTML/CSS, even through a framework.
- **Language** — [[javascript]] (the runtime language) with [[typescript]] on top (static types — strongly recommended for anything non-trivial). Both run in browser and server.
- **UI framework** — component-based UIs: [[react]] (largest ecosystem) or [[vue]] (progressive, batteries-included). Both: components, reactivity/state, one-way data flow, a virtual-DOM render.
- **Meta-framework** — [[nextjs]] adds routing, server rendering, data fetching, Server Actions, and build tooling around React (Vue's equivalent is Nuxt).
- **Server** — [[nodejs]] for APIs/SSR/real-time (JS on the server); or any backend ([[scala]]/[[akka]], etc.) behind the same HTTP contract.
- **Edge / proxy** — [[nginx]] for TLS, static serving, caching, and load balancing in front of the app.

## Rendering strategies (the central architecture choice)

Where and when HTML is produced — pick per route, not per app:
- **CSR / SPA** — ship JS, render in the browser. Rich interactivity; weaker SEO/first paint; needs an API.
- **SSR** — render HTML per request on the server. Fresh + SEO-friendly; server cost/latency.
- **SSG (static)** — render at build time. Fastest, cacheable on a CDN; stale until rebuilt.
- **ISR** — static + periodic/on-demand revalidation (best of static + freshness).
- **Streaming + Suspense** — send the shell immediately, stream slow parts.
- **RSC (React Server Components)** — components that render on the server, keep JS off the client, fetch data directly (the [[nextjs]] App Router default).
Choose by: SEO needs, data freshness, interactivity, and infra. Often a mix — static marketing pages, SSR/RSC for dynamic, CSR islands for interactivity. ([[nextjs]] implements all of these; [[software-architecture]] for the trade-off lens.)

## The request lifecycle & APIs

- A page load: DNS → TLS → request hits the proxy/CDN → server renders/streams HTML → browser paints → hydrates JS → subsequent data via fetch/Server Actions. ([[tcp-ip]]/[[computer-networks]] underneath.)
- **API styles:** **REST** (resources + verbs, the default), **GraphQL** (client-specified queries, one endpoint), **RPC/tRPC** (typed function calls). Plus **WebSocket/SSE** for real-time. Validate every input server-side ([[secure-coding]]); type the contract end-to-end ([[typescript]]).

## Build tooling & state

- **Bundlers/dev servers:** Vite (default for new apps), Turbopack/webpack; **transpile** TS/JSX → JS; tree-shaking, code-splitting, minification. **Package managers:** npm/pnpm/yarn + lockfiles. Linters/formatters: ESLint, Prettier.
- **State:** distinguish **client/UI state** (component state, [[react]] hooks / [[vue]] reactivity, Zustand/Pinia) from **server state** (data from APIs — use a query library like TanStack Query, or RSC, with caching/revalidation). Conflating them is a top source of bugs.

## Cross-cutting concerns

- **Performance** — Core Web Vitals (LCP/INP/CLS): ship less JS, code-split, optimize images/fonts ([[nextjs]] Image/Font), cache (CDN/[[nginx]]), avoid layout thrash. Measure (Lighthouse) before optimizing.
- **Accessibility** — semantic HTML, labels, keyboard, contrast, ARIA-as-needed → [[html-css]] / [[ux-design]]. Non-optional.
- **Security** — the web threat model: **XSS** (escape output / framework auto-escaping / CSP), **CSRF** (tokens/SameSite), **CORS**, **auth** (sessions vs JWT, OAuth/OIDC), input validation at the boundary, secrets server-side, HTTPS everywhere → [[secure-coding]] / [[network-security]]. Server Actions/APIs are public endpoints — authorize inside.
- **Testing** — unit (Vitest/Jest), component (Testing Library), e2e (Playwright/Cypress) → [[test-strategy]] / [[tdd]].
- **Deploy/CI** — build → test → deploy via [[github-actions]]; host on a platform (Vercel) or self-host ([[docker]] + [[nginx]]); observability ([[site-reliability-engineering]]).

## Choosing a stack (factors, not dogma)

- **Interactivity-heavy app / SEO matters** → [[react]]+[[nextjs]] (or [[vue]]+Nuxt) with SSR/RSC.
- **Mostly content** → SSG (Next/Astro) + CDN.
- **Simple interactivity on server-rendered pages** → progressive enhancement, minimal JS.
- **Type safety end-to-end** → [[typescript]] everywhere (+ tRPC/zod).
- **Self-hosting** → [[nodejs]] behind [[nginx]] in [[docker]]. **Team familiarity and the [[software-architecture]] "-ilities" decide more than fashion.** Start as simple as the requirements allow.

## Anti-patterns

- **SPA-by-default** when SSR/SSG would serve users better (slow first paint, poor SEO); or SSR everything when static would do.
- Plain **JavaScript** on a large codebase instead of [[typescript]]; ignoring accessibility and Core Web Vitals.
- Treating **server state** like client state (manual fetching in effects) instead of a query lib / RSC.
- Trusting the client: missing server-side **validation/authorization**; secrets in client bundles; XSS via unescaped HTML.
- Over-engineering (a heavy framework + global store for a brochure site); chasing the newest framework over fit/team.
- Exposing the app server directly without **TLS / a reverse proxy**; no CI/tests before deploy.

## Always-apply

1. Reason about **where code runs** (client vs server) and **what crosses the boundary**; never trust the client.
2. **TypeScript by default**; pick the **rendering strategy per route** (static/SSR/ISR/RSC) by SEO + freshness + interactivity.
3. Separate **client state from server state**; keep secrets server-side; validate/authorize on the server.
4. **Accessibility + Core Web Vitals** are requirements, not extras; measure before optimizing.
5. **HTTPS + reverse proxy** ([[nginx]]), CI/tests before deploy; start as simple as the requirements allow.

## Related

- Cluster: [[html-css]] · [[javascript]] · [[typescript]] · [[react]] · [[vue]] · [[nextjs]] · [[nodejs]] · [[nginx]].
- [[ux-design]] (design heuristics), [[secure-coding]] / [[network-security]] (web security/TLS), [[software-architecture]] (system design & trade-offs), [[test-strategy]] / [[tdd]] (testing), [[docker]] / [[github-actions]] / [[site-reliability-engineering]] (deploy/CI/ops), [[sdlc-orchestration]] (the delivery pipeline).
- Agents: **frontend-reviewer** (reviews React/Vue/TS/HTML/CSS), **full-stack-architect** (designs the stack & rendering strategy).
