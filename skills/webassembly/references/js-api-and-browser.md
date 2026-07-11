# The JS API and the browser embedding

Source: MDN WebAssembly hub, Guides, and Reference (fetched 2026-07). MDN's framing: Wasm is "a complement to JavaScript, not a replacement" — a feature for efficiently generating high-performance functions.

## Loading (prefer streaming)

- **`WebAssembly.instantiateStreaming(source, importObject, compileOptions?)`** → `{module, instance}` — the preferred path: compiles as bytes arrive, never buffers the whole module. **Requires the server to send `application/wasm`** or it rejects. Keep the `module` for caching and worker sharing.
- `compileStreaming` (Module only) · `instantiate(bytes, imports)` → `{module, instance}` · `instantiate(module, imports)` → Instance · `compile(bytes)` · `validate(bytes)` · sync `new WebAssembly.Module(bytes)` (off the main thread only).
- `compileOptions`: `builtins: ["js-string"]` and `importedStringConstants` — the platform's emerging answer to the strings problem.
- CSP can block compilation (`'wasm-unsafe-eval'`); pages must be http(s) — `file://` fails.
- **ES module integration is NOT shipped** — no `import mod from "./m.wasm"`; fetch + instantiateStreaming remains the way (Node: `fs.readFile` + `instantiate`).
- JSPI (newest, limited support): `WebAssembly.Suspending` (wrap an async JS import) + `WebAssembly.promising` (wrap a wasm export) let wasm suspend on JS promises.

## The objects

- **Module** — stateless, structured-cloneable (postMessage to workers). Statics: `Module.exports/imports/customSections`.
- **Instance** — `.exports` (frozen): functions (real JS callables), memory, tables, globals.
- **Memory** `{initial, maximum?, shared?, address?}` — 64 KiB pages; `.buffer` (ArrayBuffer, or SharedArrayBuffer when `shared: true` — maximum then required); `.grow(n)`. **THE gotcha: `grow()` detaches the previous ArrayBuffer — every TypedArray/DataView on the old buffer dies; re-acquire `memory.buffer` after any grow, including wasm-side `memory.grow`.** (Shared memories don't detach; you still get a fresh larger buffer from the accessor.) `address: "i64"` + BigInt sizes = Memory64. Wasm memory is little-endian — use DataView for portable multi-byte access.
- **Table** `{initial, maximum?, element: "anyfunc"|externref}` — `.get/.set/.grow/.length`; `table.get(0)()` calls from JS.
- **Global** `{value: type, mutable}` — `.value` getter/setter; live values shared across JS and multiple instances.
- **Tag / Exception** — the JS face of exception handling: `new Tag({parameters})`, `Exception(tag, args)`, `.is(tag)`, `.getArg(i)`.
- **Errors**: `CompileError` (bad bytes) / `LinkError` (import mismatch at instantiation — every declared import must be satisfied) / `RuntimeError` (traps: unreachable, OOB, call_indirect mismatch, stack exhaustion).
- Imports object mirrors the two-level import names: `{ console: { log: f }, js: { mem, table, global } }`.
- Multiplicity: one Module → many Instances; instances importing the SAME Memory/Table = dynamic linking / shared address space.

## Interop model (and its costs)

- Calls are synchronous both ways; exported wasm functions are JS functions, imported JS functions are wasm-callable. Each boundary crossing is a real call — keep chatty exchanges off hot paths.
- **Only numbers (and opaque references) cross.** i64 ↔ BigInt is shipped. Strings/objects don't: strings live as UTF-8 in linear memory — `new Uint8Array(memory.buffer, ptr, len)` + `TextDecoder`/`TextEncoder`, or toolchain glue (Emscripten `ccall`/`cwrap`, wasm-bindgen), or `js-string` builtins.
- Memory is **shared, not copied**: `memory.buffer` is the very bytes the module addresses. `externref` lets wasm hold (not inspect) arbitrary JS values — "an unforgeable bearer token".
- No DOM/Web API access from wasm — everything routes through imported JS.

## Threads

Shared Memory (`{shared: true}`, WAT `(memory 1 2 shared)`) + atomics + workers. **SharedArrayBuffer requires secure context AND cross-origin isolation: `Cross-Origin-Opener-Policy: same-origin` + `Cross-Origin-Embedder-Policy: require-corp`; check `crossOriginIsolated`** — without the headers, posting a SAB throws.

## Instructions by category (working vocabulary)

- **Numeric**: `const`; `add/sub/mul/div_s|u/rem_s|u`; `eq/ne/eqz/lt/gt/le/ge(_s|u)`; float `abs/neg/sqrt/min/max/ceil/floor/nearest/trunc/copysign`; bits `and/or/xor/shl/shr_s|u/rotl/rotr/clz/ctz/popcnt`; conversions `wrap`, `extend`, `trunc(_sat)`, `convert`, `demote/promote`, `reinterpret`.
- **Variable**: `local.get/set/tee`, `global.get/set`.
- **Memory**: `load`/`store` (width/sign variants like `i32.load8_s`), `memory.size/grow`, bulk `memory.copy/fill/init`, `data.drop`.
- **Control**: `block`/`loop`/`if..else..end`, `br`/`br_if`/`br_table`, `call`, `return`, `select`, `nop`, `unreachable`.
- **Exceptions**: `throw`, `throw_ref`, `try_table` + `catch/catch_ref/catch_all(_ref)`.
- **References**: `ref.null/func/is_null` (funcref, externref, exnref).
- **Table**: `table.get/set/size/grow/fill/copy/init`, `elem.drop`, **`call_indirect`** (typed, trapping).
- **Vector (v128)**: `splat`, `extract/replace_lane`, `shuffle/swizzle`, saturating arithmetic, `extmul`, `dot`, `bitselect`, `any_true/all_true/bitmask`, widening loads / `load*_splat` / lane loads.

## WAT essentials (as MDN teaches)

Signatures `(param i32) (result f64)`; locals after params, indices count params first; `$names` sugar. Export inline `(func (export "add") …)`; import `(import "console" "log" (func $log (param i32)))`. Memory: `(memory 1)` / import / `(export "memory" (memory 0))`; init `(data (i32.const 0) "Hi")`. Tables + `call_indirect (type $sig)` — the dynamic-dispatch/function-pointer pattern; sharing one imported Table+Memory across modules is MDN's dynamic-linking example. `(start $f)` runs during instantiation.

## Shipped-feature ledger (per MDN, with BCD caveats)

Shipped broadly: reference types, bulk memory, multi-value, fixed-width SIMD (Safari was last), threads/atomics (behind COOP/COEP), BigInt↔i64, non-trapping conversions, sign-extension, extended constants, tail calls, exception handling (exnref form). Recent/caveated: GC, multiple memories, Memory64, JSPI, js-string builtins. **Not shipped: ES module integration.**
