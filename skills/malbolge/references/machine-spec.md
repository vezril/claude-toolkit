# Malbolge — the exact machine

Reproduced from **Ben Olmstead's original specification** (lscheffer.com/malbolge_spec.html — a mirror of the now-dead mines.edu original; Olmstead placed the language, docs, and interpreter in the **public domain**). Every table below is **verified by execution**: the bundled `scripts/malbolge.py`, built only from these values, prints `Hello, world.` from the canonical program and matches the reference interpreter's load rules. Retrieved 2026-07.

> **The one rule that overrides the spec text:** where the written spec and Olmstead's reference interpreter disagree, **the interpreter wins** (Scheffer's convention, and universal practice). The famous case is I/O — the spec text calls `<` input and `/` output; **the interpreter does the opposite**, and so does every real program. This doc documents the *interpreter's* behavior.

## Registers and memory

A **ternary** virtual machine. Words are **ten trits** (base-3 digits) wide → values `0..59048`. Memory is exactly **59049 = 3¹⁰** words. Code and data share it.

| Reg | Role |
|---|---|
| **a** | **accumulator** — implicitly set by every memory write, and the I/O register |
| **c** | **code pointer** — points at the instruction; **auto-increments** after each cycle |
| **d** | **data pointer** — points at the data cell the ops act on; **auto-increments** too |

**All three start at 0.**

## Loading a program

- **Whitespace is ignored.** Every other character loads one-per-cell.
- A character is **valid only if it decodes to one of the eight instructions** at its load position (see decoding below). Any character that doesn't → **the file is rejected**. This is why you can't just type arbitrary text: at position `p`, a character `ch` is legal iff `XLAT1[(ch − 33 + p) mod 94]` ∈ `{ i j * p < / v o }`.
- **Memory above the program is not zero** — it's filled by applying the crazy op to the previous two cells, repeatedly: for each cell `k` past the program, `mem[k] = crazy(mem[k−1], mem[k−2])`.

## The execution cycle

Each step, with `instr = mem[c]`:

1. **If `instr` is not graphic ASCII (33–126), the program halts immediately.** (Encryption tends to drive cells out of this range — a common "why did it stop" cause.)
2. **Decode:** `op = XLAT1[(instr − 33 + c) mod 94]`. So *the same byte means different instructions at different addresses* — position-dependence is core to the language.
3. **Execute** `op` (table below). Non-matching decode → **nop**.
4. **Encrypt the just-run instruction:** if `mem[c]` is still graphic ASCII, `mem[c] = XLAT2[mem[c] − 33]`. **Every executed instruction rewrites itself** — the code you wrote is not the code that runs next time through.
5. **Advance:** `c = (c+1) mod 59049`, `d = (d+1) mod 59049`.

## The eight instructions (interpreter semantics)

| Decoded char | `(mem[c]+c) mod 94` * | Action |
|---|---|---|
| **`i`** | 4 | **jump** — `c = mem[d]` (then step 4/5 still run; a jump lands you one before the target after the increment) |
| **`<`** | 5 | **output** — write `chr(a mod 256)` to stdout *(spec text wrongly says input)* |
| **`/`** | 23 | **input** — read one char to `a`; **EOF → a = 59048** *(spec text wrongly says output)* |
| **`*`** | 39 | **rotate** — `a = mem[d] = rotr(mem[d])` (rotate the 10-trit value right one trit) |
| **`j`** | 40 | **set data ptr** — `d = mem[d]` |
| **`p`** | 62 | **crazy** — `a = mem[d] = crazy(a, mem[d])` |
| **`o`** | 68 | **nop** |
| **`v`** | 81 | **halt** |

\* The `(mem[c]+c) mod 94 ∈ {4,5,23,39,40,62,68,81}` form is the common modern statement of the *load-time valid set*; it and the `XLAT1[(mem[c]−33+c) mod 94]` decode above are the same rule stated two ways (they differ by the `−33`, i.e. by 33 mod 94).

## `rotr` — rotate right one trit

The least-significant trit becomes the most-significant; everything else shifts down:

```
rotr(v) = (v // 3) + (v % 3) * 19683        # 19683 = 3^9
```

## `crazy` — the tritwise "op" ("don't look for a pattern; it's not there")

Applied trit-by-trit across all ten trits. Per trit, with the `mem[d]` trit selecting the row and the `a` trit the column:

```
            a trit
            0   1   2
mem[d]  0   1   0   0
 trit   1   1   0   2
        2   2   2   1
```

i.e. `out_trit = CRZ[d_trit][a_trit]`, `CRZ = ((1,0,0),(1,0,2),(2,2,1))`. *(This orientation is the one that reproduces Olmstead's di-trit table and passes the Hello-World test — some secondary sources transpose it. Trust this one.)*

## `XLAT1` — the instruction-decode table (94 chars)

```
+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA"lI.v%{gJh4G\-=O@5`_3i<?Z';FNQuY]szf$!BS/|t:Pn6^Ha
```

## `XLAT2` — the post-execution encryption table (94 chars)

```
5z]&gqtyfr$(we4{WP)H-Zn,[%\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G"i@
```

> ⚠️ Wikipedia's single encryption string is `XLAT2` **rotated to a different starting offset** — using it directly gives wrong results. These two Olmstead tables, at these offsets, are the authoritative ones; the interpreter proves them.

## I/O details

`a` holds a ternary value; output writes `chr(a mod 256)`. Newline is `10`. **EOF is `59048` (`2222222222` in trits)** — a `/` at end-of-input sets `a` there, which programs must test for to terminate cleanly (Scheffer's first cat program famously *didn't*).

## Trit ↔ char quick reference

A byte's 10-trit representation is what the crazy/rotate ops manipulate. Examples from Olmstead's conversion table: `!` = 33 = `01020`₃, `A` = 65 = `02101`₃, `~` = 126 = `11200`₃, and the max word `59048` = `2222222222`₃. The full table is in the spec; you rarely need it by hand because the interpreter does the arithmetic.
