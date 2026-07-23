# Programming in Malbolge — you (almost) don't

Sources: **Lou Scheffer, "Programming in Malbolge"** (lscheffer.com/malbolge.shtml) — the cryptanalysis that first made the language tractable; plus the esolangs.org and Wikipedia histories. Retrieved 2026-07.

## Why hand-writing is effectively impossible

Every feature is designed to defeat you (Scheffer's list):

- **Position-dependent instructions** — an instruction's meaning depends on its address mod 94, so you can't move code around.
- **Self-modifying by default** — every instruction executed is immediately rewritten by the permutation table, so a cell means one thing the first time through a loop and something else the next.
- **Both pointers auto-increment** every cycle — reusing code or data is fought at every step.
- **No LOAD/STORE, no way to set memory** to anything except the 8 instruction characters at load time.
- **Two opaque ternary operators** (`rotr`, `crazy`) and nothing else for data.
- **One control-flow construct** — an unconditional computed jump — and "no obvious way" to compute a useful jump target.

The result: the language sat from **1998 to 2000** with *no* program at all, and for years the most complex known program was `Hello, world`.

## Scheffer's reframe: think like a cryptographer, not a programmer

> "The correct way to think about Malbolge … is as a cryptographer and not a programmer. Think of it as a complex code … that transforms input to output. Then study it to see if you can take advantage of its weaknesses to forge a message that produces the output you want."

The exploitable weaknesses he found:

1. **Some permutation cycles are short.** The self-modification is *not* one giant permutation (if it were, any instruction run enough times would eventually become HALT). Instructions cycle: an executed cell returns to itself after **2, 9, 4, 5, 6, or 68** steps depending on its position mod 94. Short cycles let you keep an instruction usable across a loop. The **length-68 cycle at position 2 mod 94 is especially valuable** — it cycles among **input, output, and load-D** instructions, exactly the useful ones.
2. **Jump instructions do NOT self-modify.** The cycle is: execute at `c` → scramble `mem[c]` → increment `c`. But a jump changes `c` *between* execute and scramble, so the jump cell is never rewritten (the branch address ends up one before the target — hence the "land one early" behavior). A stable, reusable jump is the seed of real control flow.

From these, Scheffer built the pieces (stable code fragments, a way to synthesize data via `crazy`/`rotr`, conditional behavior via self-modifying jump destinations) that make the language genuinely, if barely, programmable.

## How real Malbolge programs are actually produced

**Nobody writes Malbolge by hand.** In practice:

- **Search / heuristics.** Andrew Cooke generated the first `Hello, world` (~2000) with a **beam search** written in Lisp — it did not "write" the program so much as *find* a byte sequence whose forging happened to emit the target. Later generators use **genetic algorithms** and constraint search.
- **The "99 bottles" myth.** An early "99 bottles of beer" was **not** looping/testing — it was a straight-line `printf` of the whole output, conceptually identical to Hello-World. General programming had not been achieved.
- **The real breakthrough (2005).** Iizawa, Sakabe, Sakai, Kusakari, and Nishida — *"Programming Method in Obfuscated Language Malbolge"* — gave a **systematic method** for compiling ordinary logic (loops, tests, real I/O) down to Malbolge, producing a genuine looping/branching **99 bottles** program. This is when Malbolge became programmable in a meaningful sense.
- **Higher-level tooling since:** **HeLL** (a low-level Malbolge assembly), the **LMFAO / LMAO** assemblers, and **Malbolge → normalized form** tooling let people write in an abstraction and generate the ciphertext. The workflow is always *compile/search down to the byte stream*, never type it.

**So the honest posture for this skill:** you can *run*, *trace*, *validate*, and *explain* Malbolge exactly (that's the interpreter + spec). You can hand-craft only trivial things by exploiting the short cycles. Anything real (a loop, conditional I/O) is a **compilation/search problem** — reach for HeLL/LMAO or a generator, and use the interpreter here to verify the result.

## History, in one paragraph

Designed by **Ben Olmstead in 1998**, named after **Malebolge**, the eighth circle of Dante's *Inferno* (the circle of fraud) — apt for a language built to deceive. Public domain. First program (Hello-World) ~2000 via beam search; Scheffer's cryptanalysis 2004 (and a cat program that didn't terminate cleanly on EOF); general programming method 2005. It is *believed* Turing-complete (Olmstead only conjectured it; the 2005 work and a later Malbolge-Unshackled analysis support it).

## Variants (know they exist)

- **Malbolge Unshackled** — Olmstead's own generalization removing the 59049-cell and 10-trit limits (memory and word size grow as needed). It sidesteps some hard limits of standard Malbolge and is where stronger Turing-completeness arguments live. Programs are *not* portable to/from standard Malbolge.
- **Normalized Malbolge** — a pre-decoded representation (each cell shown as its decoded instruction `ijpo*</v` regardless of position) used by assemblers/tools as an intermediate form; a "normalized" program is de-normalized to real Malbolge for a specific load offset.
- Various **dialects** tweak I/O, memory, or the tables; the bundled interpreter targets **standard Malbolge / the reference interpreter**, which is what `.mal` programs in the wild assume.

## Using this skill's interpreter

```bash
python3 scripts/malbolge.py references/hello_world.mal      # -> Hello, world.
python3 scripts/malbolge.py --validate program.mal          # will it load?
echo "text" | python3 scripts/malbolge.py cat.mal           # program input via stdin
```

Trace/explain a program by reading `machine-spec.md` and stepping the decode by hand for the first few cells — but for anything beyond a few instructions, **run it**; the whole point of Malbolge is that static reading tells you almost nothing about what executes.
