# JavaScript — language internals & async

Depth on the confusing parts (Flanagan, *The Definitive Guide* 7th ed).

## Closures
A function "closes over" the variables in scope where it was **defined** (not called), and keeps them alive after that scope returns.
```js
function counter() {
  let n = 0;                 // captured
  return () => ++n;          // closure over n
}
const next = counter(); next(); // 1  next(); // 2  — n is private, persistent
```
Uses: private state, callbacks, currying/partial application, memoization, module pattern, React hooks (each render closes over its own props/state). Classic bug: closures over a `var` loop variable share one binding — use `let` (per-iteration binding).

## `this` — resolved by call-site
- **Method call** `obj.fn()` → `this = obj`.
- **Plain call** `fn()` → `this = undefined` (strict) / global (sloppy).
- **`new` Fn()** → `this` = the new object.
- **`fn.call/apply/bind(x)`** → `this = x`.
- **Arrow function** → no own `this`; uses the enclosing lexical `this` (the fix for "lost this" in callbacks).
Rule: if you pass a method as a callback, you lose its `this` — wrap in an arrow or `bind`.

## Prototypes
Every object has an internal `[[Prototype]]` (`Object.getPrototypeOf`); property lookup walks the **prototype chain**. `class`/`extends` is sugar over this; `Object.create(proto)` makes the chain explicit. Instance methods live on `Class.prototype` (shared, not per-instance).

## The event loop & microtasks
Single thread; a call stack; a **macrotask** queue (timers, I/O, events) and a **microtask** queue (Promise callbacks, `queueMicrotask`).
- Run sync code to completion → drain **all** microtasks → render → next macrotask.
- So a `Promise.then` runs **before** a `setTimeout(…,0)`. `await x` schedules the continuation as a microtask.
- Blocking the stack (heavy sync loop) blocks rendering and all callbacks — offload (Web Workers / [[nodejs]] worker threads, or chunk the work).

## Promises & async
```js
async function load(ids) {
  try {
    const users = await Promise.all(ids.map(fetchUser)); // concurrent
    return users;
  } catch (e) { /* handle rejection */ }
}
```
- A Promise is pending → fulfilled/rejected (settled, once). `.then/.catch/.finally`.
- Combinators: `Promise.all` (all or first reject), `allSettled` (never rejects), `race`, `any`.
- `async` fn always returns a Promise; `await` unwraps one. **Don't** `await` in a loop when calls are independent (use `Promise.all`). Always handle rejections (unhandled = crash in Node, warning in browser).

## Modules
- **ESM** (standard): `import {x} from './m.js'`, `export`, `export default`; static, tree-shakeable; `import type` (in TS). Top-level `await` allowed.
- **CommonJS** (Node legacy): `const x = require('m')`, `module.exports`. Don't mix carelessly; new code → ESM.

## Modern-syntax cheat sheet
```js
const {a, b = 1, ...rest} = obj;          // destructure + default + rest
const [first, ...others] = arr;
const merged = {...a, ...b};               // immutable-ish update
const list = [...arr, item];
const name = user?.profile?.name ?? "anon";// optional chain + nullish
const f = (x, y = 0) => x + y;             // arrow + default
label: for (const x of iterable) { ... }   // for…of over iterables
```

## Equality & coercion quick rules
`===` always; `Number.isNaN(x)`; `Array.isArray(x)`; `typeof` for primitives, `instanceof` for objects; `Object.is` for edge cases (`-0`, `NaN`). Avoid `==` except the idiom `x == null` (matches null *or* undefined) if you know what you're doing.
