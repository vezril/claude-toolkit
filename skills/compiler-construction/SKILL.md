---
name: compiler-construction
description: >
  Building a C compiler — the full pipeline from source text to target machine code: lexing,
  recursive-descent + Pratt/precedence-climbing parsing, AST construction, semantic analysis
  (symbol tables, lexical scopes, the C type system and integer promotion), optional IR, and
  code generation. Includes the special discipline of generating code for a register-poor 8-bit
  target (the MOS 6502 / WDC 65C02): the expression-stack code model, the cc65-style calling
  convention and software parameter stack, zero-page pseudo-registers, and the hand-written
  assembly runtime (crt0, 16-bit mul/div/shift, stdlib). Also covers how to TEST a compiler
  (per-phase unit tests, golden-file/snapshot tests on emitted assembly, end-to-end execution
  on a simulator, differential testing) and how to grow a Small-C subset incrementally toward
  C89. Distilled from Nystrom's *Crafting Interpreters*, the Small-C lineage (Cain/Hendrix),
  Cooper & Torczon's *Engineering a Compiler*, Appel's *Modern Compiler Implementation in C*,
  and the cc65 source. Use when writing or designing a compiler/interpreter, building a lexer
  or parser, implementing a type checker or symbol table, generating assembly/machine code,
  designing a calling convention or runtime/ABI, retargeting codegen to the 6502/8-bit CPUs,
  or planning the phases of a compiler project. Pairs with 6502-assembly (the target ISA),
  design-patterns, tdd, and sdlc-orchestration.
---

# Compiler Construction

How to build a **C compiler** end to end, with special depth on **generating code for the 6502/65C02**. The running example is a from-scratch C cross-compiler (written in C, runs on a PC) that emits 65C02 assembly and links it into a ROM image — but the structure generalizes to any compiler.

Cross-links: [[6502-assembly]] (the **target** ISA — the output language and the runtime are written in it), [[design-patterns]] (the visitor/interpreter patterns structure the AST passes), [[software-design]] / [[clean-code]] (phase boundaries are module boundaries), [[tdd]] / [[test-strategy]] (a compiler is the canonical case for per-phase + golden + end-to-end testing), [[sdlc-orchestration]] (sequencing the build as stories). The canonical texts are listed under **References**.

## The pipeline (and the one distinction that matters most)

```
source text
  → [lexer]      → token stream
  → [parser]     → AST (abstract syntax tree)
  → [semantic]   → typed/annotated AST + symbol tables   (errors caught here)
  → [(optional) IR + optimizer]
  → [codegen]    → target assembly
  → [assembler + linker]  → ROM image / binary
```

**Separate the compiler's *internal architecture* from the *target's* code model.** These are independent decisions people constantly conflate:

- **Internal architecture** — single-pass (parse-and-emit, no tree, tiny memory: the Small-C model) vs. multi-phase (build an AST, then walk it in separate passes). *Choose multi-phase unless the compiler itself must run on a tiny machine.* An AST-based compiler is dramatically easier to type-check, optimize, and extend toward full C. The only reason to suffer single-pass is a RAM-constrained *self-hosting* target.
- **Target code model** — how the *generated* code uses the CPU. For the 6502 this is the **expression-stack model** (below), forced by the ISA regardless of how the compiler is structured internally.

> Rule of thumb: a PC-hosted cross-compiler should be a clean **multi-phase AST compiler**, even when its *output* uses the frugal 6502 expression-stack model.

## Phase 1 — Lexer (scanner)

Turns characters into a stream of **tokens**. A token has a *kind* (e.g. `IDENT`, `INT_LIT`, `STRING_LIT`, `PLUS`, `LPAREN`, `KW_WHILE`), a *lexeme*/value, and a *source location* (line/col — keep this on every token; you need it for every error message).

- Hand-write the scanner as a small state machine over a buffer. Don't reach for lex/flex for a learning compiler — the hand-written version is ~200 lines and teaches more.
- **Maximal munch**: always consume the longest valid token (`>>=` before `>>` before `>`). A fixed peek of 1–2 chars handles C.
- Keywords are just identifiers you look up in a keyword table after scanning an identifier.
- Handle: integer literals (decimal/hex/octal, `0x`/`0`), char literals with escapes, string literals, all multi-char operators, `//` and `/* */` comments, and whitespace/newlines.
- **Preprocessor**: for a v1, a *minimal* preprocessor (`#include` textual inclusion, object-like `#define`) can be a pre-pass over the token stream. Full C preprocessing (function-like macros, `#if`, token paste) is its own substantial sub-language — defer it.

## Phase 2 — Parser

Two techniques, used together, are the standard for C:

- **Recursive descent** for declarations and statements — one function per grammar nonterminal (`parse_stmt`, `parse_decl`, `parse_if`, `parse_while`…). Readable, gives great error messages, maps 1:1 to the grammar.
- **Pratt parsing / precedence climbing** for **expressions** — the clean way to handle C's ~15 precedence levels and associativity without a function per level. Each token kind gets a binding power (and optional prefix/infix handler). This is the single highest-leverage parsing technique to learn; see *Crafting Interpreters* ch. 17.

Output is an **AST**: typed node structs (`BinaryExpr`, `CallExpr`, `IfStmt`, `FuncDecl`, …). Model nodes as a tagged union / class hierarchy and walk them with the **visitor pattern** ([[design-patterns]]).

**The hard part of C specifically — declarators.** `int (*fp)(char)`, `char *argv[]`, `int *a, b;` — C's declarator syntax is notoriously gnarly (type info wraps around the name; `*` binds to the declarator not the type). Parse declarators with their own recursive routine that builds the type inside-out (the "spiral"). Get this isolated and well-tested early; it bites everyone.

**Error recovery**: on a syntax error, report with location, then synchronize (skip to the next `;` or `}`) so you can report multiple errors per compile. Don't stop at the first error.

## Phase 3 — Semantic analysis

Walk the AST to check meaning and annotate it. This is where most of C's rules live.

- **Symbol tables + scopes.** A stack of scopes (global → function → block). Each entry: name, type, storage class (`auto`/`static`/`extern`/global), and (for codegen) its *location* (a stack offset, a label, or a register). Push a scope on `{`, pop on `}`. Look up walks outward.
- **The C type system.** Represent types as a small algebra: base (`char`, `int`, `unsigned`…), `pointer-to T`, `array-of T`, `function returning T taking (…)`. Implement `sizeof`, type equality, and the **usual arithmetic conversions**.
- **Integer promotion is the load-bearing rule on 8-bit targets.** C promotes `char` operands to `int` for arithmetic. On the 6502 that means a naïve compiler emits a 16-bit helper call for `a + b` even when both are `char`. **Track when a value provably fits in 8 bits and keep it there** — this single optimization is the difference between tight and bloated 6502 output (see Pitfalls).
- Check: lvalue-ness of assignment targets, function call arity/types, return-type compatibility, undeclared identifiers, redeclaration, pointer/array/deref validity. Insert implicit conversion nodes where C requires them (so codegen sees an explicit, typed tree).

## Phase 4 — (Optional) IR

For a first working compiler you can generate target code **directly from the typed AST**. Add an IR when you want optimization or a second target:

- **Three-address code** (`t1 = a + b`) — the usual SSA-friendly choice; enables constant folding, dead-code elimination, register allocation.
- **Stack-based IR** — maps naturally onto the 6502 expression-stack model and onto a future bytecode VM.

Keep the *option* in mind by keeping codegen behind a clean interface; don't build the IR until a concrete optimization needs it (YAGNI).

## Phase 5 — Code generation for the 6502 / 65C02

This is where the target's poverty dictates the design. The 6502 has **one 8-bit accumulator (A)**, two 8-bit index registers (X, Y), a 256-byte hardware stack, and **no multiply/divide**. See [[6502-assembly]] for the ISA.

**The expression-stack code model** (the proven approach, from Small-C/cc65):

- The **"primary" value lives in A/X** (A = low byte, X = high byte — `int` is 16-bit).
- To evaluate `lhs OP rhs`: evaluate `lhs` into the primary, **push it to the software stack**, evaluate `rhs` into the primary, then call a runtime helper that pops the saved operand and combines (e.g. `tosaddax`).
- Recursive post-order tree walk emits exactly this. It's not optimal, but it's correct, simple, and uniform.

**The calling convention / ABI (cc65-style — pin this before writing codegen; everything depends on it):**

- **Return values in A/X** (A=low, X=high; reserve a 2-byte `sreg` zero-page pair for future 32-bit).
- **Software parameter stack**: a zero-page pointer pair (`sp`) into main RAM, growing downward, holds arguments and locals — *not* the 256-byte hardware stack (which holds return addresses only).
- **Last argument in A/X** (fastcall), rest pushed left-to-right onto the software stack.
- **Callee cleans up** args + locals on return.
- **Locals are stack-relative** (indexed off `sp` via `lda (sp),y`) → enables **recursion**.
- **Zero-page budget** (~26 bytes, à la cc65): `sp` (callee-saved), `sreg`, a few `ptr`/`tmp` cells (caller-clobbered), optional register-variable bank (callee-saved). Make the ZP addresses config-relocatable so they fit the target's memory map.

**65C02-specific codegen wins** (target the CMOS part): `STZ` (one-instruction zero — great for variable/BSS init), `(zp)` indirect without Y (simpler pointer deref), `PHX/PHY/PLX/PLY`, `INC A`/`DEC A`, `BRA`.

**No hardware multiply/divide** → `*`, `/`, `%`, and variable shifts compile to **runtime library calls** (shift-and-add / shift-and-subtract loops).

**Peephole pass**: a small, table-driven post-pass over emitted assembly (e.g. collapse `pha`/`pla` pairs, redundant loads) recovers a lot of the expression-stack model's waste. Keep it separable.

## Phase 6 — Runtime, crt0, and stdlib (hand-written assembly)

The compiler's output *calls into* a hand-written 6502 assembly runtime — keep this small and well-tested:

- **`crt0` / reset**: set the RESET vector ($FFFC), init the hardware stack (`LDX #$FF; TXS`), init the software `sp` to the top of RAM, zero BSS (cheap with `STZ`), copy initialized data, call `main`.
- **Software-stack helpers**: `pushax`, `popax`, `incsp`/`decsp`.
- **Arithmetic helpers**: 16-bit `mul`, `div`, `mod`, variable `shl`/`shr`, and stack-form `add`/`sub`/`and`/`or`/`xor`; relational helpers returning 0/1 in A/X.
- **stdlib for the target hardware**: e.g. on a board with a 6522 VIA + HD44780 LCD, a `putchar`/`puts` that drives the LCD; optional keyboard input.

## Testing a compiler

A compiler is the textbook case for a layered test strategy ([[tdd]], [[test-strategy]]). Every phase boundary is a test seam:

1. **Lexer unit tests** — input string → expected token list.
2. **Parser unit tests** — input → expected AST shape (or a pretty-printed S-expression of it).
3. **Semantic tests** — programs that *should* fail typecheck must fail with the right error; valid programs must pass.
4. **Golden-file / snapshot tests on emitted assembly** — compile a `.c` fixture, diff the emitted `.s` against a checked-in golden file. Catches unintended codegen changes; regenerate deliberately.
5. **End-to-end execution tests (the execution-grounded gate)** — compile → assemble → link → **run on a CPU simulator**, and assert on observable output (return code, memory, or LCD/serial output). For the 6502, use a simulator that models the actual memory map + I/O devices. This is the test that proves the whole chain; CI must run it ([[sdlc-orchestration]]: "execute, don't opine").
6. **Differential testing** — compile the same program with a reference compiler (e.g. `gcc`/`cc65`) and compare results; great for finding semantic bugs.
7. **Self-checking test programs** — each fixture computes and signals pass/fail itself, so the harness only checks one bit.

## Growing a subset toward C89

Start with a Small-C-style core and add features as stages (each a story with its own tests):

`int`/`char`/`unsigned` + pointers + 1-D arrays + full operators + `if`/`while`/`for`/`do`/`return` + functions/recursion + minimal preprocessor → **then** `struct`/`union` → `long`/32-bit → `switch`/`goto` → function pointers → multi-dimensional arrays → full preprocessor → `float` (soft-float). Order by *cost vs. value*; pin the ABI before adding anything that touches calling convention.

## Pitfalls (hard-won)

- **16-bit integer promotion is the silent cost center** on 8-bit targets — keep provably-8-bit values in 8 bits or code bloats badly.
- **Pin the ABI before codegen.** Return-in-A/X, fastcall, callee-cleanup, ZP save conventions — every runtime routine and call site depends on them; changing later is a rewrite.
- **Declarator parsing** is the trickiest part of a C front end — isolate and test it hard.
- **Keep source locations on everything** — tokens, AST nodes — or your error messages will be useless.
- **Don't graft a foreign backend onto the 6502** — endianness, 16-bit index assumptions, and flag semantics defeat reuse of e.g. an HC08 backend; write a purpose-built 6502 codegen layer.
- **Synchronize on errors**; report many per compile, not one.
- **Golden files rot** — make regenerating them a deliberate, reviewed action, never automatic.

## References

- **Crafting Interpreters** — Robert Nystrom (free: craftinginterpreters.com). Best modern intro; Pratt parsing (ch. 17), tree-walking + a bytecode compiler. *Start here.*
- **The Small-C lineage** — Ron Cain (Dr. Dobb's, 1980) + James Hendrix, *The Small-C Handbook*. The single-pass, self-hosting subset-C model; the closest prior art for a 6502 C compiler. Read the source.
- **Engineering a Compiler** — Cooper & Torczon. Strong on the back end: instruction selection, register allocation, optimization, peephole.
- **Modern Compiler Implementation in C** ("Tiger book") — Appel. Classic, in C.
- **The Dragon Book** — Aho, Lam, Sethi, Ullman. Comprehensive reference; theory-heavy — use as a lookup, not a tutorial.
- **cc65 source** (github.com/cc65/cc65) — a real, production 6502 C compiler: the calling convention, `asminc/zeropage.inc`, and `libsrc/runtime` are the gold reference for the ABI and runtime.

## Always-apply

1. Separate **compiler internal architecture** (clean multi-phase AST when PC-hosted) from **target code model** (expression-stack on the 6502).
2. One module per phase; AST node + visitor for passes; **source locations everywhere**.
3. **Pin the ABI first.** Codegen, runtime, and every call site are downstream of it.
4. Test at every seam: lexer/parser/semantic units → assembly golden files → **end-to-end execution on a simulator** (the real gate) → differential vs. a reference compiler.
5. Grow the language as staged subsets; order features by cost-vs-value; keep 8-bit values 8-bit.

## Related

- [[6502-assembly]] — the target ISA, runtime language, and code model.
- [[design-patterns]] — visitor/interpreter for AST passes; [[software-design]] / [[clean-code]] — phase = module boundary.
- [[tdd]] / [[test-strategy]] — the layered compiler test strategy.
- [[sdlc-orchestration]] / [[spec-driven-development]] — sequencing the compiler build as epics/stories with execution-grounded gates.
