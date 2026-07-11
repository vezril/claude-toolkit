# The core language (Spec Release 3.0)

Source: WebAssembly Core Specification, Release 3.0 (draft 2026-07-10), ed. Andreas Rossberg — read independently in web and PDF editions, findings corroborated. Formal grounding derives from the PLDI 2017 paper (Haas, Rossberg et al.); mechanized soundness proofs: Watt (CPP 2018), Watt et al. (FM 2021).

## Design goals (§1.1.1)

Fast / **Safe** ("no program can break WebAssembly's memory model" — though an unsafe source language can corrupt its own layout *inside* linear memory) / Well-defined / hardware-, language-, platform-independent / Open — and as a representation: Compact, Modular, Efficient (one fast pass to decode+validate+compile), **Streamable**, Parallelizable, Portable.

## Three phases

**Decoding** (binary → abstract syntax) → **Validation** (type check; only valid modules instantiate) → **Execution** = Instantiation + Invocation, both embedder operations. Every rule is stated twice (prose + formal), declared equivalent.

## Types

- **Number types** `i32 i64 f32 f64` — integers are sign-agnostic (the *operation* chooses signed/unsigned interpretation; two's complement); floats IEEE 754. i32 doubles as boolean and (32-bit) address.
- **Vector** `v128` — reinterpretable as i8x16/i16x8/i32x4/i64x2/f32x4/f64x2 lanes.
- **Reference types** `ref null? heaptype` — *opaque* (unlike transparent number/vector types): storable in tables, never in linear memory. Three **disjoint hierarchies**, each with top and uninhabited bottom: `func`/`nofunc`; `extern`/`noextern`; `any` ⊃ `eq` ⊃ (`i31`, `struct`, `array`) ⊃ `none` (+ `exn`/`noexn`). `funcref`/`externref`/`anyref` are abbreviations for the nullable forms. `i31` = unboxed scalars (31 bits — pointer tagging).
- **Composite types** (3.0 GC): `struct` (heterogeneous, static fields), `array` (homogeneous, dynamic index), `func [t*]→[t*]`; fields can be `mut` and packed (i8/i16). Recursive `rec` groups with declared subtyping; equality is **iso-recursive** (same recursive structure = equal — cheap syntactic check across module boundaries).
- Limits `{min, max?}`; memory type = address type (i32|i64) + limits in **64 KiB pages**; table type = address type + limits + reftype.

## The module

Fields: **types**, **imports** (two-level names, not necessarily unique; occupy the FRONT of each index space), **tags** (exceptions), **globals** (`mut? valtype` + const init), **mems** (multiple since 3.0), **tables**, **funcs** (type index + locals + body), **datas** (active = copied at instantiation / passive = `memory.init`), **elems** (active / passive / declarative — the last forward-declares `ref.func` targets), **start** (runs at instantiation, after segment init, before exports are callable), **exports** (unique names). Separate zero-based index space per kind; locals include params.

## Validation

Declarative type system over a context (types, funcs, tables, mems, globals, locals, labels, return). Instruction types `[t1*] →x* [t2*]` (the `x*` tracks initialization of non-defaultable locals, a 3.0 addition). Stack-polymorphic typing with a bottom type ⊥ gives **principal types → single-pass validation with no backtracking** (sound-and-complete algorithm in the appendix, integrable into the decoder). Properties: greatest lower bounds always exist; least upper bounds only conditionally (no top type); valid sequences compose and split anywhere.

## Execution

Small-step reduction over configurations `(store; frame; instr*)`; **values ARE `const` instructions**, so the operand stack lives inside the instruction sequence. The runtime stack interleaves values, labels (branch targets), frames (locals + module instance), exception handlers.

- **Store/instances**: the store holds all runtime objects (func/table/mem/global/tag instances, segments, structs/arrays/exceptions), referenced by dynamic **addresses**; a module instance maps static indices → addresses. Function instances close over their module instance; host functions are function instances too.
- **Traps** abort immediately, no further store changes, uncatchable inside Wasm (the host observes them): out-of-bounds, div-by-zero, `unreachable`, null/`call_indirect` type mismatch, stack exhaustion.
- **Linear memory**: bounds-checked on every access; `memory.grow` by whole pages, may non-deterministically fail (returns −1, no trap); unaligned access legal (alignment is a hint).
- **Tables + `call_indirect`**: dynamic index → funcref, trap on null/OOB/type-mismatch — the runtime check that makes function pointers safe.
- **Structured control flow**: `block`/`loop`/`if` + `br`/`br_if`/`br_table` targeting enclosing labels by nesting depth; branch to a block = forward exit, to a loop = back-edge. No goto; call stack inaccessible.
- **Determinism**: exactly three non-deterministic points — NaN payloads (canonical in → canonical out; else any arithmetic NaN), `memory.grow`/`table.grow` resource failure, relaxed SIMD. The **deterministic profile (DET)** fixes NaNs (positive canonical) and relaxed SIMD; grow-failure remains.

## Soundness (Appendix 7.4)

Preservation + Progress: every valid configuration either diverges, traps, throws, or steps to a valid configuration of the same type. Consequences, verbatim-grade: all validated types respected at runtime; "no memory location will be read or written except those explicitly defined by the program"; no undefined behavior; function/module scopes encapsulated.

## Feature ledger (Appendix change history)

- **2.0 over 1.0/MVP**: sign-extension ops, non-trapping float→int (`trunc_sat`), multi-value (blocks/functions with multiple params/results), reference types, direct table instructions + multiple tables, bulk memory/table ops (`memory.copy/fill/init`, `table.copy/init`), fixed-width SIMD (v128).
- **3.0**: extended constant expressions, **tail calls** (`return_call`/`return_call_indirect`), **exception handling** (tags, `try_table`/`throw`/`throw_ref`, exnref), **multiple memories**, **memory64** (i64 addresses for memories AND tables), **typed function references**, **GC** (struct/array/i31, subtyping, rec groups), **relaxed SIMD**, **profiles**, text-format annotations.
- Backwards compatibility contract: valid modules stay valid; binary version byte stays **1**; opcode 0xFF permanently reserved.

## Binary format (§5)

Preamble `0x00 0x61 0x73 0x6D` (`\0asm`) + version `0x01 0x00 0x00 0x00`. LEB128 integers (non-canonical encodings legal — decoders must accept); length-prefixed lists; UTF-8 names. Sections: `id + u32 size + contents`, fixed order, each non-custom at most once — ids: 0 custom (anywhere; `name` section = debug info), 1 type, 2 import, 3 function, 4 table, 5 memory, 6 global, 7 export, 8 start, 9 element, 10 code, 11 data, 12 data count, 13 tag. Function *declarations* (§3) split from *bodies* (§10) deliberately — that's what enables streaming/parallel compilation. `.wasm`, `application/wasm`.

## Text format (WAT)

S-expressions in ~1:1 correspondence with the binary (same abstract syntax); `$identifiers` sugar numeric indices; instructions flat (`block … end`) or **folded** (nested parens — pure sugar for the identical linear sequence). Canonical starter:

```wat
(module
  (func $add (param $lhs i32) (param $rhs i32) (result i32)
    local.get $lhs
    local.get $rhs
    i32.add)
  (export "add" (func $add)))
```

## Embedding & profiles

The appendix defines the embedder interface abstractly (decode/validate/instantiate/invoke + per-kind alloc/read/write/grow); an embedder that treats addresses opaquely preserves store validity automatically. Host APIs (JS API, WASI) are separate documents by design. Profiles subset the language (FUL, DET); they never add syntax and are not a versioning mechanism. Implementations may impose numeric limits but may NOT omit features.
