---
name: javascript
description: Modern JavaScript (ES2020+) — the language, distilled from Flanagan's *JavaScript: The Definitive Guide* (7th ed.) and *JavaScript & jQuery: The Missing Manual*. Covers the type system (primitives vs objects, dynamic/weak typing, ===, coercion pitfalls), functions as first-class values & closures, prototypal inheritance and classes, `this` binding, the modern toolkit (let/const, arrow functions, destructuring, spread/rest, template literals, default params, optional chaining ?. and nullish ??), arrays/iterators/generators, async JavaScript (the event loop, callbacks, Promises, async/await), ES modules, error handling, the DOM and events (and where jQuery fits historically), JSON, and the runtime/tooling landscape (browser vs Node, npm, bundlers, linters). Use when writing or reviewing JavaScript, explaining language behavior (closures, prototypes, this, coercion, the event loop, async), choosing modern idioms, or debugging async/scope/equality issues. The base for typescript, react, vue, nodejs, and html-css; carries a Scala/FP comparison lens.
---

# JavaScript

The JavaScript **language**, modern (ES2020+) — from **Flanagan's *JavaScript: The Definitive Guide* (7th ed.)** and ***JavaScript & jQuery: The Missing Manual***. The language of the web (browser *and*, via Node, the server); the foundation the rest of the web cluster builds on.

Cross-links: [[typescript]] (types over JS), [[react]] / [[vue]] (frameworks), [[nodejs]] (server runtime), [[html-css]] (the DOM it scripts), [[functional-programming]] (first-class functions, the comparison lens), [[secure-coding]] (XSS/injection), [[python]] (a sibling dynamic language).

## The type system (and its traps)

- **Primitives** (immutable, compared by value): `number` (one 64-bit float type — no int/float split), `bigint`, `string`, `boolean`, `null`, `undefined`, `symbol`. Everything else is an **object** (compared by reference): objects, arrays, functions, dates, regexps.
- **Dynamically & weakly typed** — variables hold any type; the engine coerces freely. This is the #1 source of bugs (and why [[typescript]] exists).
- **Equality:** use **`===`/`!==`** (strict, no coercion), almost never `==` (coerces with surprising rules). `NaN !== NaN` (use `Number.isNaN`). `typeof null === "object"` (historical bug). Falsy values: `false, 0, -0, 0n, "", null, undefined, NaN`.
- **null vs undefined** — `undefined` = "not assigned/absent"; `null` = "intentionally empty." Guard with optional chaining `?.` and nullish coalescing `??` (only null/undefined, unlike `||`).

## Functions & closures (the heart of the language)

- **Functions are first-class values** — pass them, return them, store them ([[functional-programming]]). Higher-order functions everywhere (`map`/`filter`/`reduce`, callbacks).
- **Closures** — a function captures the variables of the scope it was defined in, and keeps them alive. The basis of modules, callbacks, currying, private state, and React hooks. Understand them or JavaScript stays mysterious.
- **Scope:** `let`/`const` are block-scoped (use these); `var` is function-scoped and hoisted (avoid). `const` = no rebinding (not deep immutability).
- **Arrow functions** — concise, and **lexically bind `this`** (no own `this`/`arguments`) — the fix for the classic `this` problems.
- **`this`** — dynamic, set by *how* a function is called (method call, plain call, `new`, `call`/`apply`/`bind`, or lexically in arrows). The other great confusion; arrows + understanding call-sites resolve most of it.

## Objects, prototypes & classes

- **Objects** are dynamic key→value maps; properties added/removed at will. Literal syntax, shorthand, computed keys, getters/setters.
- **Prototypal inheritance** — objects delegate to a **prototype** object; the prototype chain is the lookup path. This is JavaScript's real inheritance model.
- **`class`** syntax (ES2015) is sugar over prototypes: `constructor`, methods, `extends`/`super`, `static`, private `#fields`. Cleaner, but it's still prototypes underneath.
- Prefer **composition and plain objects/closures** over deep class hierarchies (the FP/[[clean-code]] lean).

## The modern toolkit (use these)

`let`/`const`, **arrow functions**, **destructuring** (`const {a, b} = obj`, `const [x, ...rest] = arr`), **spread/rest** (`...`), **template literals** (`` `${x}` ``), default params, **optional chaining `?.`**, **nullish coalescing `??`**, shorthand properties, computed keys, `for…of`, object/array spread for immutable updates.

## Arrays, iteration, generators

- Array methods are the workhorses: `map`, `filter`, `reduce`, `forEach`, `find`, `some`/`every`, `flatMap`, `sort` (mutates! copy first). Prefer these over index loops.
- **Iterables/iterators** (`Symbol.iterator`) power `for…of`, spread, destructuring. `Map`/`Set` for keyed/unique collections (object keys are string/symbol only).
- **Generators** (`function*`/`yield`) produce lazy sequences and underpin some async patterns.

## Async JavaScript (the event loop)

JavaScript is **single-threaded** with an **event loop**: synchronous code runs to completion, then queued callbacks/microtasks run. Blocking the loop freezes the UI/server.
- **Callbacks** — the original async style; nesting → "callback hell."
- **Promises** — a value that resolves/rejects later; `.then`/`.catch`/`.finally`, `Promise.all`/`allSettled`/`race`. Microtask queue (runs before the next macrotask).
- **async/await** — syntactic sugar over promises; write async code that reads sequentially. `await` only inside `async` functions (and top-level in modules); always `try/catch` or `.catch` rejections. Use `Promise.all` for concurrency, not sequential `await`s.
- This event-loop model is shared by the browser and [[nodejs]].

## Modules, errors, JSON

- **ES Modules** (`import`/`export`, `.mjs`/`type:"module"`) are the standard; CommonJS (`require`/`module.exports`) is Node's legacy. Use ESM for new code.
- **Errors:** `throw`/`try/catch/finally`; `Error` and subclasses; reject promises with `Error` objects, not strings.
- **JSON:** `JSON.parse`/`JSON.stringify`; the lingua franca of web APIs.

## The DOM & events (browser) — and jQuery's place

- The **DOM** is the live tree of the page; script it with `document.querySelector`, `element.addEventListener`, `classList`, `textContent`, `fetch` (the modern HTTP API). Event handling: bubbling/capturing, delegation, `event.preventDefault()`.
- **jQuery** (from the Missing Manual) solved cross-browser DOM/AJAX pain in the 2010s — `$(...)`, chaining, `$.ajax`. **Mostly obsolete now**: modern DOM APIs (`querySelector`, `fetch`, `classList`) and frameworks ([[react]]/[[vue]]) replace it. Know it for legacy code; don't reach for it in new projects.

## Scala / FP comparison lens

- **First-class functions, closures, map/filter/reduce** map to FP — but JS is **mutable-by-default**, **dynamically/weakly typed**, and **not expression-oriented**. ([[typescript]] adds the static types; [[functional-programming]] the discipline.)
- **No real immutability** without discipline (`const` ≠ immutable; use spread/`Object.freeze`/immutable libs).
- **Errors as exceptions**, no `Option`/`Either` built in (use `?.`/`??`, or a result type in [[typescript]]).
- **Prototypes vs Scala's classes/traits**; **single-threaded event loop** vs JVM threads ([[scala]]/[[akka]]).

## Anti-patterns

- `==` instead of `===`; relying on coercion; `var` instead of `let`/`const`.
- Misunderstanding `this` (losing it in callbacks — use arrows); deep class hierarchies over composition.
- Blocking the event loop (heavy sync work); sequential `await`s where `Promise.all` fits; unhandled promise rejections.
- Mutating shared objects/arrays (or `sort`/`reverse` in place) unexpectedly; treating `const` as deep-immutable.
- New code on **jQuery** / CommonJS instead of modern DOM/ESM (or a framework).
- `eval`, building HTML by string concatenation (XSS — [[secure-coding]]); not validating/escaping untrusted input.

## Always-apply

1. **`===`**, `let`/`const`, modern syntax (`?.`, `??`, destructuring, spread, template literals).
2. Lean on **first-class functions & closures**; array methods over index loops; composition over deep inheritance.
3. Respect the **single-threaded event loop**: `async/await` + `Promise.all`, never block it, always handle rejections.
4. **ES modules** for new code; `Error` objects for throws; `fetch`/modern DOM (not jQuery).
5. Reach for **[[typescript]]** on anything non-trivial — JS's weak typing is its biggest liability.

## How to use the reference

- **`references/language-and-async.md`** — closures/`this`/prototypes in depth, the event loop & microtasks, Promises/async patterns, modules, and the modern-syntax cheat sheet.

## Related

- [[typescript]] — static types over JavaScript (strongly recommended for real projects).
- [[react]] / [[vue]] — the UI frameworks; [[nodejs]] — JS on the server (same event loop).
- [[html-css]] — the DOM JS manipulates; [[functional-programming]] — first-class functions/closures + the comparison lens.
- [[secure-coding]] — XSS, injection, untrusted input; [[clean-code]] — readable JS.
- Sources: *JavaScript: The Definitive Guide, 7th ed.* (David Flanagan); *JavaScript & jQuery: The Missing Manual* (David McFarland).
