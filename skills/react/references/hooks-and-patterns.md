# React hooks & patterns

Working detail (react.dev v19; *The Road to React*).

## Core hooks — usage & pitfalls
- **useState** — `const [v,setV]=useState(init)`. Setter replaces (objects: spread to merge). Use the **updater** form when next depends on prev: `setV(p=>p+1)`. Lazy init: `useState(()=>expensive())`. Pitfall: state updates are async/batched — don't read `v` right after `setV`.
- **useReducer** — `const [state,dispatch]=useReducer(reducer,init)`; reducer `(state,action)=>newState` (pure). For complex/related state and when next state depends on prior. Reducer + Context = app state.
- **useContext** — `const t=useContext(ThemeContext)`; provide with `<ThemeContext value={...}>` (React 19 — no `.Provider` needed). Re-renders consumers on value change; split contexts / memoize value to limit re-renders.
- **useRef** — `const r=useRef(null)`; `<input ref={r}/>`; `r.current` is mutable, **no re-render**. For DOM access and values that persist without rendering.
- **useEffect** — `useEffect(()=>{ const sub=connect(); return ()=>sub.close(); }, [deps])`. Runs after paint; **cleanup** on unmount/before re-run; **deps** must list everything reactive used inside (trust `exhaustive-deps`). `[]` = run once (mount); no array = every render (rarely right).
- **useMemo/useCallback** — `useMemo(()=>compute(a,b),[a,b])`, `useCallback(fn,[deps])`. Only for measured perf or referential stability passed to memoized children. The **Compiler** often makes these unnecessary.

## Dependency-array rules
List every reactive value (props, state, context, derived vars) used in the effect/callback. Don't lie to silence the linter — instead: move the function inside the effect, wrap it in `useCallback`, use the updater form of setState, or use `useEffectEvent` for non-reactive logic. Empty `[]` only when the effect truly uses nothing reactive.

## Custom hooks
Extract reusable stateful logic into a `useX` function that calls other hooks:
```jsx
function useToggle(init=false){
  const [on,setOn]=useState(init);
  const toggle=useCallback(()=>setOn(o=>!o),[]);
  return [on, toggle];
}
```
Naming `use*` lets the linter enforce hook rules. Custom hooks share *logic*, not state (each call is independent).

## Controlled form
```jsx
function NameForm(){
  const [name,setName]=useState("");
  return (
    <form onSubmit={e=>{e.preventDefault(); save(name);}}>
      <input value={name} onChange={e=>setName(e.target.value)} />
      <button type="submit">Save</button>
    </form>
  );
}
```
React 19 alternative: `<form action={async (formData)=>{...}}>` + `useActionState` for pending/result, `useFormStatus` in a child button.

## Lists & keys
```jsx
{users.map(u => <UserRow key={u.id} user={u} />)}   // stable id, NOT index
```
Keys identify items across renders (correct reordering, preserved state). Index keys break on insert/reorder/delete.

## "You might not need an Effect" — fixes table
| Smell | Fix |
|------|-----|
| state derived from props/state | compute in render |
| expensive derived value | `useMemo` (or Compiler) |
| reset state when prop changes | pass a new `key` |
| do X on a click | event handler, not effect |
| effect that sets state that triggers another effect | compute in render + set in handler |
| subscribe to external store | `useSyncExternalStore` |
| fetch on mount | effect with cleanup/ignore flag — or a query lib / RSC |

## Client vs Server Component (with a framework)
- **Server Component (default in [[nextjs]] App Router):** `async`, can `await` data/DB, no hooks/state/browser APIs, stays off the client bundle. Use for data fetching, secrets, static content.
- **Client Component (`"use client"`):** interactivity — `useState`/`useEffect`/event handlers/browser APIs. Push the boundary as deep as possible; pass Server Components as `children` into Client Components to interleave.
- `"use server"` = a **Server Action** (mutation), *not* a Server Component marker.

## State-management ladder
local `useState` → lift up → `useReducer`+`useContext` → external store via `useSyncExternalStore` → libraries: **TanStack Query** (server/async state — usually what you actually want for data), Zustand/Jotai (light client state), Redux Toolkit (large apps). Don't reach for global state before you need it.
