# WASI and the server side

Source: Sletten (O'Reilly 2021) chapters 8, 11–12, 15–16 — the conceptual model is durable; the ecosystem snapshot is 2021 and marked so.

## WASI: the capability model

**"WebAssembly makes your code portable. WASI endeavors to make your application portable."** A bare `wasm32-unknown-unknown` module can't even run as a CLI (no `_start`, no ABI); a `wasm32-wasi` build exports `_start` and imports `wasi_snapshot_preview1.fd_write`, `proc_exit`, `environ_get`… — an ABI plus standard-library *expectations* the host may or may not grant.

- **Capabilities-based security**: no ambient authority. Resources arrive as **unforgeable, opaque handles**; the threat model is the **confused deputy**. Deny-by-default: a file-writing program panics under `wasmtime prog.wasm` and works under `wasmtime --dir=. prog.wasm` — the granted directory handle is a **preopen** (preopened file descriptor).
- WASI is namespaces, plural — filesystem, clocks, random, and proposals beyond (crypto, nn, sockets); a host can **virtualize** any of them (a browser can satisfy "filesystem" with localStorage). "WASI may never be 'done.'"
- The same capability logic appears host-side in Deno (`--allow-read/--allow-net/--allow-write`) — the book's bridge example: SQLite-compiled-to-wasm inside a Deno server, replacing brittle native add-ons (node-gyp, per-OS binaries, V8 Isolate pain).
- Date-stamp: the book's era is `wasi_snapshot_preview1` and "Module Linking + `.wit` interface files". That proposal line became the **component model** (WASI 0.2/preview2 era, WIT as its IDL) — treat the book's module-linking specifics as superseded; the *goals* (shared-nothing composition, virtualizable interfaces, swappable implementations) carried over intact.

## The embedding API (Wasmtime's shape, mirrored across languages)

**Engine** (global config) → **Module** (compiled) → **Store** (the isolation unit — instances/memories/tables live and die together; never shared across Stores) → **Linker** (name-based composition; `Func::wrap` for host callbacks) → **Instance** → `get_typed_func` for type-safe calls. `WasiCtxBuilder` grants WASI (e.g. `.inherit_stdio()`). This vocabulary (engine/store/linker) is the lingua franca of embedding APIs in Rust, C#, Python, Go.

**Metering**: Wasmtime **fuel** (`consume_fuel(true)`, `store.add_fuel(n)` — traps when exhausted, per-instruction costs) is the generic runaway-code answer; Ethereum's **gas** is the same idea priced in money. Any plugin host should decide its fuel policy explicitly.

## Runtimes and niches (2021 map — niches stable, details move)

- **wasmtime** — Bytecode Alliance reference (Cranelift), proposal-leading, embeddings everywhere.
- **wasmer** — standalone + many language embeddings (+ the WAPM package manager, wasienv — verify currency).
- **wasm3** — tiny interpreter; embedded/IoT.
- **WasmEdge** (Second State, CNCF) — edge/FaaS, execution metering, TF inference.
- **wasmCloud** (CNCF) — actor model + hot-swappable capability providers + NATS lattice mesh.
- **Lucet** (Fastly) — merged into wasmtime; its numbers made the case: **instantiation < 50 µs vs ~5 ms for V8; kilobytes not tens-of-MB per instance**.

## The architectural theses

- **Wasm as the next virtualization granularity**: hardware → VMs → containers → wasm modules; smaller, faster-starting, capability-gated. The quote to deploy (Solomon Hykes, Docker co-founder): *"If WASM+WASI existed in 2008, we wouldn't have needed to create Docker. That's how important it is. WebAssembly on the server is the future of computing."* (His caveat: containers aren't going away; they'll cooperate — Krustlet's Kubernetes kubelet scheduling wasm beside OCI containers is that cooperation.)
- **Plugin systems**: the sandbox + capability grants make third-party extension safe — Envoy/Istio filters, Fastly/Cloudflare edge functions, even MS Flight Simulator replacing DLL plugins with wasm. Supply-chain risk is the motivation: "we are running potentially untrusted code from untrusted third parties with the privileges we normally give ourselves."
- **Decentralized**: ewasm (Ethereum's wasm VM; gas via opcode-cost mapping), Polkadot/Substrate, IPFS serving wasm apps content-addressed and unhosted — the sandbox is what makes running unhosted apps acceptable.
- **Bytecode Alliance** — the "nanoprocess" vision: lightweight isolation instead of heavyweight IPC.

## Server-side checklist

1. Pick the target: `wasm32-wasi` for CLI/hosted apps, bare + explicit imports for plugins.
2. Grant minimum capabilities (preopens, env, stdio) — and test that denial actually denies.
3. One Store per tenant/request when isolation matters; Stores are the blast-radius boundary.
4. Meter untrusted code (fuel or the host's equivalent) and cap memory via limits.
5. For composition/interfaces, reach for the component model (WIT) — not the book's module-linking syntax.
6. Sizes and startup are the selling points — measure them; if your wasm artifact rivals a container image, something's wrong.
