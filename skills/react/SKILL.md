---
name: react
description: React (v19) — the library for building UIs out of components — distilled from Wieruch's *The Road to React* and the official react.dev reference. Covers the function-component + JSX model, props/state/composition, the Hooks (useState, useEffect, useContext, useReducer, useRef, useMemo, useCallback) and the React 19-era additions (use, useTransition, useDeferredValue, useOptimistic, useActionState, useFormStatus, useId, useSyncExternalStore), the Rules of React and Rules of Hooks, "you might not need an Effect" (derive in render, handle events in handlers), lists/keys, controlled forms, context for shared state, refs as an escape hatch, Suspense & error boundaries, the React Compiler (auto-memoization), and Server Components/Actions (delivered via frameworks like Next.js). Use when building or reviewing React components, choosing/ debugging hooks, managing state or effects, lifting state, handling forms/lists, or deciding client vs server components. Builds on javascript/typescript/html-css; pairs with nextjs (the framework) and the swiftui-reviewer-style review mindset.
---

# React

The library for building **user interfaces out of components** — modern React (v19) from **Wieruch's *The Road to React*** and the official **react.dev** reference. *"The library for web and native user interfaces."* Function components + Hooks; no classes in new code.

Cross-links: [[javascript]] / [[typescript]] (the language — React is TS-first today), [[html-css]] (what it renders), [[nextjs]] (the framework that delivers Server Components/Actions/routing), [[vue]] (the sibling framework), [[functional-programming]] (components as pure functions of props/state), [[clean-code]].

## The model: components, JSX, props, composition

- A **component** is a JavaScript function that returns **JSX** (HTML-like markup that compiles to `React.createElement`). Components compose — small components combine into bigger ones.
- **Props** are read-only inputs passed parent → child; **never mutate props**. Children via the `children` prop. UI = `f(props, state)`.
- **One-way data flow:** data flows down via props; events flow up via callbacks. Lift shared state to the closest common parent.
- **Rendering** is React calling your component to produce a description of the UI, then reconciling it against the DOM. Keep components **pure** (no side effects during render — Rule #1).

## State & the core Hooks

*"Hooks let you use different React features from your components."* The essentials:
- **`useState`** — local component state (`const [count, setCount] = useState(0)`); setting it re-renders. State updates are **batched** and the setter can take an updater fn (`setX(prev => prev+1)`).
- **`useReducer`** — state with update logic in a reducer (for complex/related state). Reducer + Context is the documented app-state pattern.
- **`useContext`** — read shared data from a `Context.Provider` without prop-drilling.
- **`useRef`** — a mutable box that **doesn't** trigger re-render; usually a DOM node ref (`<input ref={inputRef}>`) or to hold a value across renders. An **escape hatch**.
- **`useMemo`** / **`useCallback`** — cache an expensive value / a function identity (perf). *Increasingly unnecessary with the React Compiler.*
- **`useEffect`** — synchronize with an **external system** (subscriptions, non-React widgets, manual DOM). It runs after render; **return a cleanup function**; declare a correct **dependency array**. (See "you might not need an Effect" — most things aren't effects.)

## The Rules (non-negotiable)

**Rules of React:** (1) **components & hooks must be pure** (no side effects in render; same input → same output); (2) **React calls them** (don't call components as functions); (3) follow the **Rules of Hooks**.

**Rules of Hooks:** **only call Hooks at the top level** (never in loops, conditions, nested functions, or after an early return) and **only from React functions** (components or custom hooks). Enforced by `eslint-plugin-react-hooks` (`rules-of-hooks`, `exhaustive-deps`). Custom hooks (`useX`) compose built-in hooks to share logic.

## "You might not need an Effect" (the most important review lens)

Effects are an **escape hatch for external systems** — not for data flow. Common misuses → fixes:
- **Derived state** → compute it **during render** ("if it can be calculated from props/state, don't put it in state").
- **Expensive calc** → `useMemo` (or let the Compiler do it).
- **Resetting state on prop change** → pass a different **`key`**.
- **Responding to a user event** → put the logic in the **event handler**, not an effect.
- **Chains of effects** → compute in render + set in the handler.
- **Subscribing to an external store** → `useSyncExternalStore`.
- **Data fetching** *is* a valid effect — but add a cleanup/`ignore` flag for races (and frameworks fetch better; see [[nextjs]]).
Rule: *code that runs because the component was displayed* → effect; *because the user did something* → event handler.

## Lists, keys, forms

- **Lists:** `items.map(i => <Li key={i.id} … />)`. **Keys** must be stable & unique (use IDs, **not array index** for dynamic lists) — they tell React which item is which.
- **Forms:** **controlled inputs** (`value` + `onChange` bound to state) are the default; uncontrolled (refs) for simple cases. React 19 adds form **Actions** (`<form action={fn}>`), `useActionState` (pending/result), and `useFormStatus`.
- **Events:** `onClick`/`onChange` with camelCase; synthetic events; pass handler *references*, not calls.

## State sharing & context

Built-ins first: local `useState`/`useReducer` → **lift state up** to a common parent → **Context** (with reducer) for app-wide state → `useSyncExternalStore` for external stores. Reach for a library (Zustand, Redux Toolkit, Jotai, TanStack Query for server state) only when the built-ins strain — and prefer **server-state libraries** for data fetching/caching.

## Refs, Suspense, error boundaries

- **Refs** = escape hatch for imperative DOM access (focus, scroll, measure, integrate non-React libs) and mutable values that shouldn't re-render. In React 19 `ref` is a normal prop (no `forwardRef` needed).
- **`<Suspense fallback={…}>`** shows a fallback while children (lazy components, RSC data via `use`) load; enables streaming.
- **Error boundaries** catch render errors in a subtree (still class-based) — wrap risky regions.

## React 19 additions & the Compiler

- **`use`** — read a Promise or Context (can be called conditionally); reads data streamed from the server.
- **`useTransition`/`useDeferredValue`** — keep the UI responsive during heavy updates (concurrent).
- **`useOptimistic`** — optimistic UI before a mutation resolves; **`useActionState`/`useFormStatus`** — form actions + pending state.
- **React Compiler** — build-time **auto-memoization**; reduces (often removes) the need for manual `useMemo`/`useCallback`/`memo`.

## Server Components / Actions (via frameworks)

- **Server Components** render ahead of time on the server (build-time or per-request), keep heavy deps out of the client bundle, and can `await` data directly. **There is no `"use server"` directive for them**; `"use server"` marks **Server Functions/Actions** (mutations). `"use client"` marks the boundary into interactive Client Components. These ship to app devs through frameworks — see [[nextjs]].

## Anti-patterns

- **Effects for everything** (derived state, event responses, effect chains) — the cardinal React mistake; compute in render / handle in events.
- Breaking the **Rules of Hooks** (conditional/looped hooks); calling components as functions.
- **Array index as key** for dynamic lists; mutating state/props directly (always produce new objects/arrays).
- Lifting state too high (prop-drilling) or reaching for Redux when `useState`/Context suffices; using an effect+state for **server data** instead of a query library / RSC.
- Manual `useMemo`/`useCallback` sprinkled everywhere (premature; let the Compiler) — or none where a real perf problem exists.
- Stale closures from wrong/empty dependency arrays; forgetting effect **cleanup**.

## Always-apply

1. **Function components + JSX**; pure render; data down via **props**, events up via callbacks; lift shared state.
2. Obey the **Rules of Hooks** (top-level, React functions only); extract reuse into **custom hooks**.
3. **You might not need an Effect** — derive in render, handle in events; effects only for external systems (with cleanup + deps).
4. **Stable keys** (not index); **controlled forms** / React 19 Actions; Context (+reducer) or a query lib for shared/server state.
5. Use **Suspense**/error boundaries; lean on the **Compiler** over manual memoization; render on the server via [[nextjs]] where it helps.

## How to use the reference

- **`references/hooks-and-patterns.md`** — each core hook with usage + pitfalls, the dependency-array rules, custom-hook patterns, controlled-form/list-key recipes, and the client-vs-server-component decision.

## Related

- [[javascript]] / [[typescript]] — the language (TS-first React).
- [[nextjs]] — the framework: routing, Server Components/Actions, data fetching, rendering.
- [[html-css]] — markup/styling React produces; [[vue]] — the sibling framework.
- [[functional-programming]] — components as pure functions, immutable updates; [[clean-code]].
- Sources: *The Road to React* (Robin Wieruch); official React docs (react.dev, v19).
