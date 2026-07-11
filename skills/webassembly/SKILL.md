---
name: webassembly
description: "WebAssembly (Wasm) — the portable, sandboxed compilation target, in and out of the browser. Covers the core language (stack machine, modules, linear memory, tables, validation and the soundness guarantee, binary/WAT text formats) against Core Spec Release 3.0 (GC, tail calls, exception handling, memory64, multiple memories, relaxed SIMD, deterministic profile), the browser story (the WebAssembly JS API, streaming instantiation, Memory/Table/Global, JS interop and the strings problem, threads with COOP/COEP), the toolchains (clang/Emscripten, Rust wasm-bindgen/wasm-pack, AssemblyScript, TinyGo/Swift/Zig, WABT), and the server side (WASI capability security with preopens, wasmtime/wasmer/WasmEdge runtimes, fuel metering, edge/serverless/plugin architectures). Distilled from Sletten's WebAssembly: The Definitive Guide (O'Reilly 2021, MVP-era claims date-stamped), the Core Specification Release 3.0 (2026-07-10, read twice independently), and MDN (fetched 2026-07). Use when compiling any language to Wasm, embedding modules in web apps or native hosts, designing plugin/edge/sandbox architectures, debugging .wasm binaries or WAT, choosing runtimes, or judging when Wasm is and isn't worth it. Separate from the webkit skill (the engine that runs it in Safari)."
license: MIT
---

# WebAssembly

A **virtual ISA**: safe, fast, portable, compact code — "the Web's polyglot object-file
format" (Eich) that outgrew the web. Not a JavaScript replacement; a way to run any
language, sandboxed, on any computational surface.

Load the reference for the layer you're working at:

- **[references/core-language-and-spec.md](references/core-language-and-spec.md)** — the
  language itself: types, module anatomy, validation/execution semantics, soundness, binary
  + WAT formats, the 1.0→2.0→3.0 feature ledger. Load when reading/writing WAT, debugging
  .wasm, or making normative claims.
- **[references/js-api-and-browser.md](references/js-api-and-browser.md)** — the JS API
  surface, interop patterns (memory sharing, the strings problem), threads, shipped-feature
  status. Load for any browser/Node embedding work.
- **[references/toolchains-and-languages.md](references/toolchains-and-languages.md)** —
  compiling C/C++ (clang direct, Emscripten), Rust (wasm-bindgen/wasm-pack), AssemblyScript,
  the other languages, WABT inspection tools. Load when building modules from source.
- **[references/wasi-and-server-side.md](references/wasi-and-server-side.md)** — WASI's
  capability model, the runtimes and their niches, metering, edge/serverless/plugin/
  decentralized architectures. Load for anything outside a browser.

## The mental model

- **A stack machine in a sandbox.** Instructions push/pop a typed operand stack; validation
  proves stack discipline before anything runs; structured control flow only (block/loop/
  if + br — no goto), which is what makes single-pass validation and compilation possible.
- **The module is everything.** Unit of deployment/compilation/instantiation: types, funcs,
  tables, memories, globals, imports (front of every index space), exports, segments,
  optional start function. One Module, many Instances.
- **Linear memory is the only memory pages can corrupt — their own.** A bounds-checked byte
  array in 64 KiB pages, disjoint from the host and from other instances. The soundness
  theorem is real (mechanized proofs exist): validated code touches nothing it didn't
  declare, no undefined behavior — but an unsafe source language can still corrupt *its
  own* data inside that memory.
- **No ambient capabilities.** "WebAssembly has no way of printing to the console…
  unless you give it a way to do so" (Sletten). Every effect enters through imports; on
  the server WASI makes that a capability system (unforgeable handles, preopens,
  deny-by-default).
- **Portable code ≠ portable application.** The bytecode ports; API expectations don't.
  WASI exists to make *applications* portable — the book's structural spine, still true.

## When Wasm is (and isn't) worth it

Worth it: compute-heavy kernels; reusing trusted C/C++/Rust code (crypto provenance —
libsodium over a JS rewrite); plugin systems and untrusted-code hosts; edge/serverless
(microsecond instantiation, KB-scale overhead — "If WASM+WASI existed in 2008, we wouldn't
have needed to create Docker" — Hykes); shipping capabilities ahead of browser consensus.
Not worth it: trivial workloads (boundary-crossing overhead), plain UI logic, anywhere the
GPU already wins (Wasm+SIMD+threads narrows but doesn't erase that gap).

## Always-apply

1. **Date-stamp your claims.** Core Spec is Release 3.0 (2026-07-10): GC, tail calls,
   exception handling, multiple memories/tables, memory64, typed references, relaxed SIMD,
   profiles are IN the language. 2021-era material ("one memory per module", "GC/threads
   are future", module-linking/`.wit`-as-module-types) is superseded — the component model
   replaced module linking (see the WASI reference's note).
2. **`memory.grow` detaches the old ArrayBuffer** — re-acquire `memory.buffer` after every
   grow, both JS- and wasm-initiated. The single most common embedding bug.
3. **Prefer `instantiateStreaming`** (needs `application/wasm` MIME); keep the `Module` for
   caching/worker sharing. Threads need shared Memory + COOP/COEP cross-origin isolation.
4. **Strings don't cross the boundary** — only numbers and opaque references do. UTF-8 in
   linear memory + TextEncoder/TextDecoder, or toolchain glue (wasm-bindgen, cwrap), or the
   new `js-string` builtins. Chatty JS↔wasm calls off the hot path.
5. **Determinism has exactly three holes** (NaN payloads, grow-failure, relaxed SIMD) and
   the deterministic profile closes two — the answer to "is Wasm deterministic".
6. **Inspect before you theorize**: `wasm-objdump -x`, `wasm2wat` (WABT); magic `\0asm`,
   binary version still 1 across releases.
7. On the server, **grant capabilities explicitly and minimally** (`wasmtime --dir=.`);
   metering exists when you need runaway protection (wasmtime fuel, gas-style).

## Related

- [[webkit]] — the engine embedding story on Apple platforms (JavaScriptCore runs Wasm;
  a WKWebView browser inherits it — this skill is the language, that one is the vessel).
- [[javascript]] · [[web-development]] — the host language and the platform around it.
- [[secure-coding]] — the sandbox complements, not replaces, source-level safety.
- [[docker]] · [[devops]] — the "smaller than containers" deployment conversation.
- Sources: *WebAssembly: The Definitive Guide* (Brian Sletten, O'Reilly, 1st ed. 2021);
  WebAssembly Core Specification Release 3.0 (draft 2026-07-10; webassembly.github.io/spec/core
  + the PDF, read independently); MDN WebAssembly docs + Reference (fetched 2026-07).
