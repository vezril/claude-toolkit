---
name: vue
description: Vue.js (3) — the progressive framework for building UIs — distilled from *Fullstack Vue: The Complete Guide to Vue.js*. Covers the reactivity system (ref/reactive, computed, watch), Single-File Components (.vue — template/script/style), the Composition API (setup/<script setup>) vs the Options API, templates & directives (v-bind/:, v-on/@, v-model two-way binding, v-if/v-show, v-for with keys, v-slot), props/emits/component communication, slots, lifecycle hooks, provide/inject, the ecosystem (Vue Router, Pinia state management, Vite), and scoped styles. Use when building or reviewing Vue components, choosing Composition vs Options API, wiring reactivity/computed/watchers, handling forms with v-model, structuring SFCs, or working with Vue Router/Pinia. A frontend-framework alternative to react; builds on javascript/typescript/html-css.
---

# Vue.js

The **progressive** JavaScript framework for building UIs — Vue 3 — from ***Fullstack Vue: The Complete Guide to Vue.js***. "Progressive" = adoptable incrementally (a sprinkle of interactivity on a page up to a full SPA). An approachable alternative to [[react]] with first-class **reactivity** and **Single-File Components**.

Cross-links: [[javascript]] / [[typescript]] (the language — Vue 3 is TS-friendly), [[html-css]] (templates/scoped styles), [[react]] (the sibling framework — same problems, different ergonomics), [[functional-programming]] (reactivity ≈ derived values), [[clean-code]].

## Reactivity (Vue's core idea)

Vue tracks dependencies and **re-renders automatically** when reactive state changes:
- **`ref(value)`** — a reactive container for any value; read/write via `.value` in script (auto-unwrapped in templates). The default for primitives.
- **`reactive(obj)`** — a deeply reactive object/array (no `.value`; don't destructure it — that breaks reactivity; use `toRefs`).
- **`computed(() => …)`** — a cached derived value that updates when its dependencies change (use instead of methods for derived data — like a memoized getter).
- **`watch` / `watchEffect`** — run side effects when reactive sources change (`watch(source, cb)` explicit; `watchEffect(cb)` auto-tracks). Use for effects (fetching, syncing), not for deriving (that's `computed`).

## Single-File Components (.vue)

A component is one `.vue` file with three blocks:
```vue
<script setup>
import { ref, computed } from 'vue'
const count = ref(0)
const doubled = computed(() => count.value * 2)
</script>
<template>
  <button @click="count++">{{ count }} → {{ doubled }}</button>
</template>
<style scoped>
button { font-weight: bold; }   /* scoped to this component */
</style>
```
`<style scoped>` keeps CSS local to the component (no leakage — see [[html-css]]).

## Composition API vs Options API

- **Composition API** (`<script setup>`) — the modern default: logic organized by **feature** in `setup`, reusable via **composables** (`useX()` functions — Vue's answer to React hooks/mixins). Best for TS and larger components.
- **Options API** — the classic object form (`data()`, `methods`, `computed`, `watch`, lifecycle) — organized by option type; fine for simple components and still fully supported.
Pick one style per project; Composition API + `<script setup>` is recommended for new code.

## Templates & directives

Vue templates are HTML with **directives**:
- **`:prop` / `v-bind`** — bind an attribute/prop to an expression (`:href="url"`).
- **`@event` / `v-on`** — listen for events (`@click="handler"`).
- **`v-model`** — **two-way binding** on form inputs (the big ergonomic win vs React's controlled inputs); works on components too (`v-model` ↔ `modelValue` + `update:modelValue`).
- **`v-if` / `v-else` / `v-show`** — conditional render (`v-if` adds/removes; `v-show` toggles CSS display).
- **`v-for`** — list rendering: `v-for="item in items" :key="item.id"` (always a stable **`:key`**, like [[react]]).
- **`{{ }}`** interpolation; `v-slot` for slots; modifiers (`@submit.prevent`, `v-model.trim`).

## Components: props, emits, slots

- **Props** down (`defineProps`), **events** up (`defineEmits` → `emit('change', payload)`) — one-way data flow like [[react]].
- **`v-model` on components** for two-way (sugar over a prop + update event).
- **Slots** — content projection (`<slot>` / named slots / scoped slots) for flexible composition.
- **`provide`/`inject`** — pass data to deep descendants without prop-drilling (Vue's Context).
- **Lifecycle hooks** — `onMounted`, `onUnmounted`, `onUpdated`, etc. (Composition API) for setup/teardown (e.g. subscriptions, timers).

## The ecosystem

- **Vite** — the build tool/dev server (instant HMR); the default for Vue projects.
- **Vue Router** — official client-side routing (routes, dynamic params, nested routes, navigation guards).
- **Pinia** — the official state-management store (the modern replacement for Vuex): typed stores with state/getters/actions, composable, devtools-friendly. Use for cross-component/app state; local state stays in components.
- **Vue DevTools**, **Nuxt** (the meta-framework — Vue's [[nextjs]] analog: SSR/SSG/file routing).

## React comparison (you may know one)

- Reactivity is **automatic & fine-grained** (no manual deps array); `ref/computed/watch` vs `useState/useMemo/useEffect`.
- **`v-model`** gives built-in two-way binding (React is one-way + controlled inputs).
- **Templates + directives** (Vue) vs **JSX** (React) — Vue separates template/script/style; both compile to virtual-DOM renders.
- **Composables** ≈ React custom hooks; **Pinia** ≈ Zustand/Redux; **Nuxt** ≈ Next.js.

## Anti-patterns

- Destructuring a **`reactive`** object (loses reactivity) — use `ref`, or `toRefs`; forgetting `.value` in script.
- Using **`watch`** to derive state that should be a **`computed`**; methods for derived data instead of `computed` (no caching).
- Missing/`index` **`:key`** in `v-for` (same issue as [[react]]); mutating props.
- `v-if` + `v-for` on the same element (precedence/perf); `v-show` for rarely-shown heavy content (it still renders).
- Mixing Options and Composition API arbitrarily; global Pinia state where local state suffices.
- Unscoped styles leaking globally; heavy logic in templates instead of `computed`/methods.

## Always-apply

1. **Composition API + `<script setup>`** for new code; one style per project.
2. State with **`ref`/`reactive`**; **derive with `computed`** (cached); **`watch`/`watchEffect`** only for side effects.
3. **Props down, emits up**; `v-model` for two-way form binding; **stable `:key`** in `v-for`.
4. Extract reuse into **composables**; share app state with **Pinia**; route with **Vue Router**; scope component CSS.
5. Don't destructure `reactive`; prefer `computed` over `watch` for derived data.

## Related

- [[javascript]] / [[typescript]] — the language; [[html-css]] — templates and scoped styles.
- [[react]] — the sibling framework (Composition API ≈ hooks; Nuxt ≈ Next.js).
- [[functional-programming]] — reactivity as derived values; [[clean-code]].
- Source: *Fullstack Vue: The Complete Guide to Vue.js* (Hassan Djirdeh, Nate Murray, Ari Lerner), Vue 3.
