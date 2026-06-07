---
name: nextjs
description: Next.js — the React framework for full-stack web apps — from the official docs (App Router era, v15/16). Covers the App Router (file-system routing in app/, layout/page/loading/error/not-found files, dynamic & catch-all segments, route groups, parallel/intercepting routes), Server Components by default vs "use client" boundaries, data fetching in async server components (fetch caching/memoization, revalidation, streaming with Suspense/loading.js), Server Actions and mutations ("use server", forms, useActionState, revalidatePath/Tag, redirect), rendering strategies (SSR, static/SSG, ISR, streaming, partial prerendering / cache components), route handlers (route.js APIs), metadata & OG images, the Image/Link/Font components, middleware/proxy, caching layers, and deployment. Use when building or reviewing a Next.js app, structuring App Router routes/layouts, deciding server vs client components, fetching or mutating data, choosing a rendering/caching strategy, or writing route handlers. Builds on react/typescript; pairs with nodejs and nginx (hosting/reverse proxy). Note: the framework moves fast — verify version-specifics.
---

# Next.js

The **React framework for full-stack web apps** — *"The React Framework for the Web"* — from the official docs (the **App Router** era, v15/16). *"You use React Components to build user interfaces, and Next.js for additional features and optimizations"* (routing, data, rendering, bundling, image/font optimization).

> Next.js moves **fast** (App Router, RSC, caching model, and even feature names change between majors — e.g. middleware → "Proxy", the new Cache Components model). Treat version-specifics here as a snapshot and verify against the current docs.

Cross-links: [[react]] (the library — Next delivers Server Components/Actions), [[typescript]] (TS-first), [[html-css]] (styling), [[nodejs]] (the server runtime under it), [[nginx]] (reverse proxy in front of a self-hosted Next app), [[secure-coding]] (auth in server actions).

## App Router (the current model)

Two routers exist; **use the App Router** (`app/`) for new apps (the Pages Router `pages/` is legacy but supported). The App Router uses **React Server Components** and React 19 features.

**File-system routing** — folders under `app/` are route segments; special files define behavior:
- **`page.tsx`** — the route's UI (makes the segment publicly routable).
- **`layout.tsx`** — shared UI wrapping a segment + its children (root layout required, renders `<html>/<body>`); persists across navigation.
- **`loading.tsx`** — a Suspense fallback auto-wrapping the page (streaming).
- **`error.tsx`** — an error boundary for the segment (Client Component); also `not-found.tsx`, `forbidden.tsx`, `unauthorized.tsx`.
- **`route.ts`** — **Route Handlers** (API endpoints; export `GET`/`POST`… using `NextRequest`/`NextResponse`).
- **Dynamic segments** `[id]`, catch-all `[...slug]`, optional `[[...slug]]` → `params` (now a **Promise** — `await` it).
- **Route groups** `(group)` (organize without affecting the URL); **parallel** (`@slot`) and **intercepting** routes for advanced layouts/modals.
- Metadata files (`opengraph-image`, `sitemap.ts`, `robots.ts`, `icon`), `src/` and `public/`.

## Server vs Client Components

- **Server Components are the default.** They render on the server: fetch data close to the source, keep secrets and heavy deps off the client, reduce JS, and stream HTML. They can be `async` and `await` data directly.
- **`"use client"`** marks the boundary into a **Client Component** — needed for state, event handlers, `useEffect`, browser APIs, and React Context. Everything imported into a client module joins the client bundle; **push the boundary as deep as possible** and pass Server Components as `children`/props to interleave.
- Only `NEXT_PUBLIC_`-prefixed env vars reach the client; use `server-only`/`client-only` to catch leaks at build time. Context providers must be Client Components.

## Data fetching

- **In Server Components:** make the component `async` and `await` — use `fetch` (identical requests are **memoized per render**; **not cached by default** in current versions — opt in with the `use cache` directive / `cacheLife`/`cacheTag`), or call a DB/ORM directly.
- **Streaming:** wrap slow parts in **`<Suspense>`** (granular) or use **`loading.tsx`** (whole page) so the shell renders immediately and data streams in. (A layout reading runtime data like `cookies()` won't fall back to same-segment `loading.tsx` — wrap that read in its own Suspense.)
- **Parallel** fetches: kick them off then `await Promise.all([...])`; avoid accidental waterfalls.
- **In Client Components:** React's **`use(promise)`** (pass a promise from a server component, read under Suspense) or libraries (SWR, TanStack Query).

## Server Actions & mutations

- *"A Server Function is an async function that runs on the server"*; in a mutation context it's a **Server Action**, marked with **`"use server"`** (top of the function or file). Behind the scenes they use **POST** and are directly reachable — **always verify auth/authorization inside every action** ([[secure-coding]]).
- Invoke via `<form action={fn}>` (gets `FormData`; **progressive enhancement** — works without JS), `formAction`, props to Client Components, or event handlers. Pending state via **`useActionState`** (run inside `startTransition`).
- After a mutation: **`revalidatePath`/`revalidateTag`** (refresh cached data), `redirect()`, set `cookies()`, or `router.refresh()`. Optimistic UI via React's `useOptimistic`.

## Rendering strategies

- **Static (SSG)** — prerender at build (default for non-dynamic routes); fastest.
- **Dynamic (SSR)** — render per request (when using runtime data: `cookies()`, `headers()`, uncached fetch, dynamic params).
- **ISR** — `revalidate` + `generateStaticParams` to rebuild static pages on a schedule/on-demand.
- **Streaming** — Suspense/`loading.tsx` to send the shell first and stream the rest.
- **Partial Prerendering / Cache Components** — the modern direction: a static shell with dynamic holes; opt into caching explicitly via `use cache` (`cacheLife`/`cacheTag`). Verify what's stable in your version.

## APIs, metadata, components, middleware

- **Route Handlers** (`route.ts`) — REST/webhook endpoints in the App Router (replaces `pages/api/*`).
- **Metadata** — static `export const metadata` or dynamic `generateMetadata()`; file-based OG images via `ImageResponse`.
- **Built-ins:** **`<Image>`** (automatic optimization/lazy/responsive), **`<Link>`** (client nav + prefetch), **`next/font`** (self-hosted, layout-shift-free fonts), `<Script>`, `<Form>`.
- **Middleware / "Proxy"** (`proxy.ts`/`middleware.ts`) — run code before a request completes (auth gates, redirects, rewrites, headers); runs on the edge.

## Caching & deployment

- Caching layers: per-render `fetch` **memoization**, the **Data/Full-Route cache** (`use cache`, `cacheLife`, `cacheTag`, `revalidateTag`/`revalidatePath`, `updateTag`), the client **Router Cache**, and CDN caching. The caching model has shifted across versions — read the current "Caching" + "Cache Components" docs.
- **Deploy:** Vercel (first-class), or self-host (Node server / standalone output / Docker — [[docker]]) behind a reverse proxy ([[nginx]]); static export for static-only sites. Turbopack is the default bundler in v16.

## Anti-patterns

- Marking everything **`"use client"`** (loses RSC benefits — ships JS, no server data); putting the client boundary too high.
- Forgetting `params`/`searchParams` are **Promises** now (must `await`); reading runtime data in a layout without wrapping in Suspense (breaks streaming).
- **No auth check inside a Server Action** (it's a public POST endpoint); trusting client input in actions.
- Fetching server data in a client `useEffect` instead of a Server Component / `use` / query lib; accidental **fetch waterfalls** (sequential awaits).
- Leaking secrets to the client (non-`NEXT_PUBLIC_` only on server; use `server-only`); assuming a stale caching mental model across versions.
- Using the legacy **Pages Router** patterns (`getServerSideProps`) in new App Router code.

## Always-apply

1. **App Router**, **Server Components by default**; add `"use client"` only where you need interactivity, as deep as possible.
2. Fetch in **async Server Components** (memoized; opt into caching with `use cache`); **stream** slow parts with Suspense/`loading.tsx`; parallelize with `Promise.all`.
3. **Server Actions** for mutations (`"use server"`) — always **auth-check inside**; revalidate with `revalidatePath`/`Tag`.
4. Use **`<Image>`/`<Link>`/`next/font`**, route handlers for APIs, metadata APIs for SEO; keep secrets server-side.
5. Pick the **rendering/caching strategy** deliberately (static/ISR/dynamic/streaming) and **verify version-specifics** — Next moves fast.

## Related

- [[react]] — the underlying library (hooks, Server Components/Actions); [[typescript]] — the language.
- [[nodejs]] — the server runtime; [[nginx]] — reverse-proxy a self-hosted app; [[docker]] — containerized deploy.
- [[html-css]] — styling; [[secure-coding]] — auth in actions, input validation; [[sdlc-orchestration]] — fits a full-stack pipeline.
- Source: official Next.js documentation (nextjs.org/docs), App Router (v15/16).
