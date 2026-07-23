---
name: malbolge
description: "Understanding, running, tracing, and explaining Malbolge — the esoteric programming language Ben Olmstead (1998) designed to be as close to impossible to program in as he could make it, named after Malebolge, the eighth circle of Dante's Inferno. Distilled from the authoritative public-domain sources (Olmstead's original specification and reference interpreter, Lou Scheffer's cryptanalysis essay, Wikipedia, esolangs.org) and VERIFIED by execution — a bundled stdlib-only reference interpreter (scripts/malbolge.py) prints 'Hello, world.' from the canonical program. Covers the exact ternary machine (59049 = 3^10 ten-trit words; registers a/c/d all starting at 0; both c and d auto-increment every cycle), the execution cycle (halt on non-graphic ASCII; decode via XLAT1 as (mem[c]-33+c) mod 94 so an instruction's meaning depends on its address; execute; re-encrypt the just-run cell via XLAT2 so all code self-modifies; advance), the eight instructions (i jump, < output, / input, * rotate-right, j set-data-pointer, p crazy, o nop, v halt) with the crucial spec-vs-reference-interpreter I/O SWAP (the spec text calls '<' input and '/' output; the interpreter — held correct — does the opposite), the tritwise 'crazy' operation table and the rotate-right formula ((v//3)+(v%3)*19683), the two authoritative 94-character tables reproduced exactly (Wikipedia's rotated encryption string is wrong), the load rules (whitespace ignored, characters valid only if they decode to one of the eight instructions, memory above the program filled by crazy(prev,prev2)), EOF = 59048, and — honestly — WHY you cannot hand-write it (position-dependence, self-modification, dual auto-increment pointers, no LOAD/STORE, opaque ternary ops, one computed jump) and how real programs are actually PRODUCED (Cooke's beam search for the first Hello World ~2000, Scheffer's cryptographic weaknesses — short permutation cycles 2/9/4/5/6/68 and the fact that jumps don't self-modify, the 2005 Iizawa et al. general-programming method, the HeLL/LMAO assemblers), plus variants (Malbolge Unshackled, Normalized Malbolge). Use to run or validate a .mal program, explain what a Malbolge program or instruction does, understand the machine/tables/crazy-op, decode the position-dependent semantics, or learn how the language is programmed at all. Includes a working interpreter and a verified Hello World."
argument-hint: "[a .mal program to run/explain, or a Malbolge question]"
license: MIT
---

# Malbolge

Malbolge is the language **deliberately built to be nearly impossible to program in** — Ben Olmstead, 1998, named after **Malebolge**, the eighth circle of Dante's *Inferno* (the circle of fraud). It sat for **two years after release with no program at all**, and its first "Hello, world" was *found by a beam search*, not written. Everything about it — position-dependent instructions, code that rewrites itself every step, opaque ternary operators, one nearly-useless jump — is engineered to defeat you.

This skill lets you **run, validate, trace, and explain** Malbolge exactly — grounded in a bundled interpreter that's **verified by execution** (it prints `Hello, world.` from the canonical program). It's honest about the one thing it can't hand you: *writing* a nontrivial program, which is a search/compilation problem, not a typing problem.

Load a reference for depth:

- **[references/machine-spec.md](references/machine-spec.md)** — the exact machine: registers/memory, the execution cycle, the eight instructions, the **crazy op** and **rotate** operations, the **two authoritative 94-char tables** (reproduced character-for-character), the load rules, and the **I/O swap** gotcha. Every value verified against a working interpreter.
- **[references/programming.md](references/programming.md)** — Scheffer's "think like a cryptographer" reframe, the exploitable weaknesses (short permutation cycles; jumps don't self-modify), the real history, **how programs are actually produced** (beam search, genetic algorithms, the 2005 method, HeLL/LMAO), and the variants.

## Run it

```bash
python3 scripts/malbolge.py references/hello_world.mal     # → Hello, world.
python3 scripts/malbolge.py --validate program.mal         # does it load? (exit 0 / 1)
echo "hi" | python3 scripts/malbolge.py cat.mal            # program input comes from stdin
python3 scripts/malbolge.py -                               # read the program itself from stdin
```

Stdlib only — no install. The interpreter follows **Olmstead's reference interpreter** (the de-facto standard), with a step cap so non-terminating programs don't hang.

## The mental model (why static reading fails)

- **An instruction's meaning depends on where it is.** Decode is `XLAT1[(mem[c] − 33 + c) mod 94]` — the same byte is a different instruction at a different address. You cannot relocate code.
- **Code rewrites itself as it runs.** After each instruction executes, `mem[c]` is replaced via `XLAT2`. The cell you read is not the cell that runs next time through a loop. **To know what a program does, run it** — reading it tells you almost nothing.
- **Both pointers march forward every cycle** (`c` and `d`, mod 59049). Reusing code or data is fought at every step.
- **Ternary, 10 trits, 59049 cells.** Registers `a`/`c`/`d` start at 0. The only data ops are `rotr` (rotate right one trit) and `crazy` (an opaque tritwise table). There is no LOAD/STORE.
- **It halts on any non-graphic-ASCII instruction** — and self-encryption pushes cells out of range, so "it just stopped" is normal and expected.

## The eight instructions

| char | does | note |
|---|---|---|
| `i` | `c = mem[d]` — **jump** | lands one before the target (encrypt happens after `c` moves) |
| `<` | **output** `chr(a mod 256)` | ⚠️ spec text says *input* — the interpreter (and reality) says output |
| `/` | **input** one char → `a` | ⚠️ spec says *output*; **EOF sets a = 59048** |
| `*` | `a = mem[d] = rotr(mem[d])` | rotate right one trit |
| `j` | `d = mem[d]` | set data pointer |
| `p` | `a = mem[d] = crazy(a, mem[d])` | the opaque tritwise op |
| `o` | nop | |
| `v` | **halt** | |

## Fast answers

| Question | Answer |
|---|---|
| Does `<` input or output? | **Output.** The spec text is wrong here; the reference interpreter is authoritative. |
| Why did my program stop? | It hit a **non-graphic-ASCII instruction** (33–126 required) — usually because self-encryption drove `mem[c]` out of range. Expected. |
| Can I write Hello World by hand? | Practically no. The canonical one was **beam-searched**. Use a generator/assembler; verify with this interpreter. |
| Where do the magic numbers come from? | `59049 = 3¹⁰` (memory), `19683 = 3⁹` (rotate weight), `94` (printable-ASCII instruction span), `59048` (max word / EOF). |
| Is it Turing-complete? | Believed so (Olmstead only conjectured it); the 2005 general-programming method and Unshackled analysis support it. |
| What are the two 94-char tables? | `XLAT1` decodes an instruction; `XLAT2` re-encrypts the executed cell. Both in the spec reference — **use those exact strings** (Wikipedia's encryption string is rotated/wrong). |

## Gotchas

- **Don't trust Wikipedia's single encryption string** — it's `XLAT2` at a shifted offset and produces wrong output. Use the two tables in `machine-spec.md`.
- **The crazy-op table is easy to transpose.** The orientation in this skill is the one that passes Hello-World; some secondary sources have it flipped.
- **The I/O swap** trips everyone. `<` = output, `/` = input.
- **A "99 bottles" claim isn't proof of looping** — the early one was straight-line `printf`. Real looping came in 2005.
- **`.mal` files assume standard Malbolge** (this interpreter). Malbolge Unshackled programs won't run here and vice-versa.

## Related

- [[python]] — the interpreter is plain Python 3 (stdlib only); read it to see the whole machine in ~120 lines.
- [[information-theory]] · [[cryptography]] — Malbolge is best understood as a **cipher** you forge inputs against (Scheffer's framing); ternary encoding, permutation cycles, and "find a preimage for the desired output" are the operative ideas.
- [[lambda-calculus]] · [[6502-assembly]] — the toolkit's other "computation from first principles" skills; Malbolge is the adversarial extreme of an assembly language.
- [[webassembly]] — the sane counterpart: a portable *compilation target* you generate rather than write. Real Malbolge programs are likewise *compiled/searched* down to the byte stream (HeLL/LMAO) — malbolge is the adversarial extreme of "don't write the machine code, produce it."

Sources: Ben Olmstead's original **Malbolge specification** and **reference interpreter** (public domain; via lscheffer.com mirrors of the dead mines.edu original), **Lou Scheffer's "Programming in Malbolge"** cryptanalysis, en.wikipedia.org/wiki/Malbolge, and esolangs.org/wiki/Malbolge — retrieved 2026-07. All machine values are **verified by the bundled interpreter**, which reproduces `Hello, world.` from the canonical program; where the spec text and the reference interpreter conflict, the interpreter governs.
