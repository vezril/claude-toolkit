# Toolchains and source languages

Source: Sletten, *WebAssembly: The Definitive Guide* (O'Reilly 2021) — tooling names verified durable; version-sensitive claims date-stamped. The book's lineage framing: NaCl (fast, sandboxed, but arch-specific and Chrome-only) → asm.js (portable but parser-hot, can't be AOT-optimized) → WebAssembly ("binary syntax for low-level safe code… the Web's polyglot object-file format" — Eich).

## Inspection first (WABT, "wabbit")

- `wat2wasm` / `wasm2wat` — assemble/disassemble (also the online wat2wasm demo); `wat2wasm --debug-names` keeps names in the custom section.
- `wasm-objdump -x` (headers/sections; also `-d/-h/-s`) — the first tool to reach for on any mystery `.wasm`.
- `wasm3` — C interpreter with a repl; runs everywhere from routers to microcontrollers ("fastest wasm interpreter, most universal runtime"); great for portability demos and embedded.
- Empty module = 8 bytes; a hello-add module ≈ 45 bytes; sizes are a feature — treat bloat as a smell.

## C/C++ without Emscripten (understanding the raw path)

```
clang --target=wasm32 -nostdlib -Wl,--no-entry -Wl,--export-all -o out.wasm in.c
```
No stdlib, no `main` expected, `--export-all` or dead-code elimination strips everything uncalled. Clang emits scaffolding (`__heap_base`, `__stack_pointer`, `__wasm_call_ctors`). A "pointer" returned to JS is **just an index into the Memory buffer** — JS wraps `memory.buffer` in a typed array at that offset. Minimal-libc pattern: ship tiny malloc/free/printf; route output through an imported host function; `extern "C"` (or the `WASM_EXPORT` visibility macro) to stop C++ name mangling from breaking exports.

## Emscripten (the legacy-code workhorse)

`emcc hello.c -o hello.js` → `.wasm` + ~120 KB JS glue emulating the missing OS (that's why hello-world is bigger than native: no dynamically loadable libc in a browser). The glue's `wasi_snapshot_preview1.fd_write` import is WASI foreshadowing. Key switches: `-s INVOKE_RUN=0`, `-s EXTRA_EXPORTED_RUNTIME_METHODS="['callMain','cwrap']"`, `-s FORCE_FILESYSTEM=1` (virtual FS, `FS.readFile()` from JS), `-s ALLOW_MEMORY_GROWTH=1`, `-s EXPORTED_FUNCTIONS="['_main','_run_test']"` (**leading underscore**; C++ needs `extern "C"`). `cwrap('fn','number',['number'])` returns a typed JS wrapper. Porting recipe: swap the Makefile compiler to `em++`, keep a native Makefile beside it. Provenance argument: recompiling trusted C (libsodium) beats a JS rewrite — fresher crypto, no reintroduced timing bugs.

## Rust (the first-class citizen)

- Targets differ: `wasm32-unknown-unknown` (bare module, browser via bindgen) vs `wasm32-wasi` (exports `_start`, imports WASI — runnable in wasmtime/wasmer).
- **wasm-bindgen**: the symmetric bridge — `#[wasm_bindgen] extern` blocks make JS APIs look like Rust (`js_namespace = console`); `#[wasm_bindgen]` on Rust functions makes them look like JS. Generates malloc/realloc shims for string passing.
- **wasm-pack build --target web|bundler|nodejs|deno** → `pkg/` with `.wasm`, JS glue, TypeScript `.d.ts`, package.json; auto-runs **wasm-opt** (Binaryen) on output.
- In/out-of-browser single codebase: `#[cfg(target_arch = "wasm32")]` gates the wasm entry point (egui/eframe pattern); the wasm build can be *smaller* than native (3.5 vs 5.6 MB in the book's egui example).

## AssemblyScript

"Definitely **not** a TypeScript-to-Wasm compiler" (their words): a Binaryen-based compiler for a TS-*like* language — for JS/TS developers wanting wasm output without C/Rust. Differences: no `any`/`undefined`/unions/closures/exceptions; wasm numeric types (i32/i64/f32/f64, usize); no DOM — imports or WASI only. `asc hello.ts -b hello.wasm` (hello add = **91 bytes**). Ships its own GC inside the module (`--exportRuntime`, `--runtime incremental|minimal|stub`) — date-stamp: written before wasm-GC shipped; the language-level GC-in-module approach persists. `@assemblyscript/loader` gives JS-side `__newString/__getString/__pin/__unpin/__getArray`.

## .NET and the app frameworks

- **Wasmtime NuGet** — embed wasm plugins in C# (Engine/Store/Module/Linker mirror the Rust API).
- **Blazor WebAssembly** — .NET assemblies on a Mono runtime compiled to wasm, downloaded to the browser (big first download, cacheable) vs Blazor Server (SignalR, latency-bound). **Uno Platform** — C#/WinUI everywhere incl. web-via-wasm. Book's thesis: for these users "WebAssembly is simply a convenient implementation detail."

## The rest of the language map (2021 snapshot — verify currency before recommending)

TinyGo (LLVM Go, embedded focus, `syscall/js` + `wasm_exec.js`); SwiftWasm (`swiftc -target wasm32-unknown-wasi`); Zig (`zig build-lib -target wasm32-freestanding|wasm32-wasi` — its WASI example prints granted preopens, a clean capability demo); Grain (designed *for* wasm); Artichoke (Ruby-on-Rust, early); Java/Kotlin were the laggards (GC/threads blockers — now shipped in the spec, so re-check the ecosystem before repeating the book's pessimism).

## Performance posture

Near-native for compute kernels; boundary crossings and small workloads eat the gains ("for small data sets the overhead is probably still not worth it"). The TF.js case study: wasm backend beats plain JS always, loses to WebGL on big models, **wins on small models** (fixed per-op GPU costs); SIMD + threads close most of the gap; CUDA still 1105× plain JS. Honest line: "WebAssembly is not always going to be the fastest solution in every case." Feature-test at runtime with Google's **wasm-feature-detect** when shipping SIMD/threads variants.
