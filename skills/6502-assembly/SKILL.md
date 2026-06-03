---
name: 6502-assembly
description: Writing and understanding 6502 assembly language, distilled from Nick Morgan's *Easy 6502* tutorial. Covers the MOS 6502 CPU model (the A/X/Y registers, SP stack pointer, PC program counter, and the processor status flags N V B D I Z C), hex/binary number notation (`$` hex, `#` immediate literal vs memory reference), the instruction set (load/store LDA/STA/LDX/LDY, transfers TAX/TXA/…, arithmetic ADC/SBC with the carry flag, increment/decrement INX/DEX, logic AND/ORA/EOR/BIT, shifts ASL/LSR/ROL/ROR, compares CMP/CPX/CPY, BRK/NOP), all addressing modes (immediate, zero page, zero-page/absolute indexed by X/Y, absolute, indirect, indexed-indirect (zp,X), indirect-indexed (zp),Y, relative, implicit), control flow (branches BNE/BEQ/BCC/BCS/BMI/BPL on flags, JMP, JSR/RTS subroutines), the stack ($0100–$01ff, PHA/PLA), labels and assembler constants/defines, and worked examples up to a full Snake game. Use whenever writing, reading, debugging, or explaining 6502 assembly, reasoning about registers/flags/addressing modes, retro/6502-family programming (NES, C64, Apple II, Atari, BBC Micro), or low-level/CPU-architecture learning. Pairs with operating-systems, osdev-kernel, and information-theory.
---

# 6502 Assembly

How to read and write **6502 assembly language** — the CPU model, the instruction set, every addressing mode, and the idioms — distilled from Nick Morgan's **Easy 6502**. The 6502 powered the NES, C64, Apple II, Atari 2600, and BBC Micro; it was *designed to be written by humans*, which makes it the best assembly language to learn for understanding how a processor actually works.

Cross-links: [[operating-systems]] / [[osdev-kernel]] (assembly is the bottom of the stack you reach for in boot/kernel/interrupt code — the concepts transfer), [[information-theory]] (binary, bit masking, carry). Examples use the [easy6502 in-browser assembler/simulator](https://skilldrick.github.io/easy6502/).

## Number notation (read this first)

- **`$`** = hexadecimal. `$01`, `$ff`, `$0200`. A byte is two hex digits (`$00`–`$ff`); a 16-bit address is four (`$0000`–`$ffff`).
- **`#`** = an **immediate literal value**. `LDA #$01` loads the *number* `$01`. Without `#`, the operand is a **memory address**: `LDA $01` loads the *value stored at* location `$01`. This distinction is the single most common beginner confusion — keep it straight.
- Binary matters because so much 6502 logic is bit-twiddling (flags, masks like `$1f`/`$03`, powers of two for direction bits).

## CPU model: registers & flags

Three one-byte general registers plus three special ones:

- **`A`** — the **accumulator**; the hub of arithmetic and logic. Most operations read/write `A`.
- **`X`, `Y`** — index registers, used for counters, loops, and indexed addressing.
- **`SP`** — **stack pointer** (offset into page `$01`); decremented on push, incremented on pull. Starts at `$ff`.
- **`PC`** — **program counter**: the address of the next instruction (the easy6502 simulator assembles code at `$0600`, so PC starts there).

The **processor status** byte holds seven 1-bit flags, set as side effects of instructions: **N** (negative), **V** (overflow), **B** (break), **D** (decimal mode), **I** (interrupt disable), **Z** (zero — set when a result is 0), **C** (carry — set when an arithmetic result won't fit in a byte, and used by shifts/compares). Branch instructions test these flags. You don't set most flags directly; you arrange code so the flag you care about reflects the last operation.

## Instructions

Each instruction takes **zero or one operand**. Categories you'll use constantly:

- **Load/store**: `LDA`/`LDX`/`LDY` (load a register), `STA`/`STX`/`STY` (store a register to memory).
- **Transfer**: `TAX`/`TAY`/`TXA`/`TYA` (copy between A and X/Y), `TSX`/`TXS` (with SP).
- **Arithmetic**: `ADC` (add **with carry**), `SBC` (subtract with carry). The carry flag chains multi-byte math; remember `$c0 + $c4 = $84` **with carry set**, because the true `$184` doesn't fit in a byte. Clear carry with `CLC` before a standalone add, set it with `SEC` before a standalone subtract.
- **Inc/dec**: `INX`/`INY`/`DEX`/`DEY` (registers), `INC`/`DEC` (memory).
- **Logic**: `AND`, `ORA`, `EOR` (bitwise), and `BIT` (AND that sets flags but discards the result — used to test bits; powers-of-two trick in the Snake game).
- **Shifts/rotates**: `ASL`, `LSR` (logical shift, LSB/MSB into carry), `ROL`, `ROR`.
- **Compare**: `CMP`/`CPX`/`CPY` — subtract-and-set-flags without storing; sets `Z` if equal, `C` per magnitude. Pair with a branch.
- **Control**: branches, `JMP`, `JSR`/`RTS`, stack ops (below), `BRK` (break/halt), `NOP` (do nothing — used for timing/`spinWheels`).

The full opcode tables (operands, affected flags, cycle counts) live at 6502.org and obelisk.me.uk — those are the reference bibles; this skill is the working model.

## Addressing modes (how an operand names its data)

This is the heart of 6502 fluency. See `references/instruction-set-and-addressing.md` for examples of each:

- **Immediate** `#$c0` — a literal value.
- **Zero page** `$c0` — a one-byte address into the first 256 bytes ($0000–$00ff); faster and smaller than absolute.
- **Zero page,X / Zero page,Y** `$c0,X` — zero-page base **plus** index register; wraps within the zero page. (`,Y` only for `LDX`/`STX`.)
- **Absolute** `$c000` — a full two-byte address.
- **Absolute,X / Absolute,Y** `$c000,X` — absolute base plus index register.
- **Indirect** `($c000)` — the operand is a pointer; the CPU reads the two bytes there (little-endian: low byte first) to get the real address. Used by `JMP`.
- **Indexed indirect** `($c0,X)` — add X to the zero-page address *first*, then dereference. (Rare.)
- **Indirect indexed** `($c0),Y` — dereference the zero-page pointer *first*, then add Y to the resulting address. (Common — used to walk through memory/screen.)
- **Relative** — branch targets: a single signed byte offset from the next instruction (range ≈ −128..+127), so branches are local. Use labels and the assembler computes the offset.
- **Implicit** — no operand (`INX`, `RTS`, `BRK`).

**Little-endian** is fundamental: 16-bit values are stored low byte first. `$10`/`$04` at `$00`/`$01` means the address `$0410`.

## Control flow

- **Branches** test one flag and take the relative jump if it holds: `BNE`/`BEQ` (Z clear/set), `BCC`/`BCS` (carry clear/set), `BMI`/`BPL` (N set/clear), `BVC`/`BVS` (V). Typical loop: `CPX #$03` then `BNE label`. Branches reach only ~256 bytes.
- **`JMP`** — unconditional jump to a two-byte absolute address (or via indirect).
- **`JSR` / `RTS`** — call/return: `JSR` pushes the return address (minus one) to the stack and jumps; `RTS` pulls it, adds one, and resumes. This is how you build subroutines/functions and modular code.

## The stack

A fixed region `$0100`–`$01ff` indexed by `SP` (starts `$ff`, grows downward). `PHA`/`PLA` push/pull the accumulator; `PHP`/`PLP` the status byte. `JSR`/`RTS` and interrupts use it for return addresses. Push and pull in mirror order (LIFO) — see the stack example that draws a mirrored pixel pattern.

## Labels, constants & the assembler

- **Labels** mark addresses (`loop:`, `init:`); branches and jumps use them and the assembler resolves the real address/offset.
- **`define name value`** creates a constant/symbol (`define snakeDirection $02`, `define movingUp 1`). Use them for screen addresses, key codes, and state variables to make code self-documenting. Immediate operands still need `#`: `LDX #a_dozen`.
- Assemble → inspect the **hexdump** to see opcodes + operands (e.g. `a9 01` = immediate `LDA #$01`); use the **debugger** (step, watch registers/PC) and the **memory monitor** (Start + Length) to watch execution.

## easy6502 simulator specifics

These are simulator conventions, not real-hardware facts: memory **`$0200`–`$05ff`** maps to a 32×32 pixel display (16 colours `$0`–`$f`); **`$fe`** yields a fresh **random byte** each instruction; **`$ff`** holds the **ASCII of the last key** pressed. The display is four horizontal strips (`$0200–$02ff`, `$0300–$03ff`, `$0400–$04ff`, `$0500–$05ff`); +`$01` moves right, +`$20` moves down a row.

## Idioms & techniques (flag these as the "right way")

- **Test equality / loop bound** with `CMP`/`CPX`/`CPY` + `BNE`/`BEQ`, not arithmetic.
- **Detect overflow / chain bytes / detect row-wrap** via the **carry flag** (`ADC`/`SBC`, or after `INC`); branch on `BCC`/`BCS`.
- **Mask bits** with `AND` (`AND #$03` → range 0–3; `AND #$1f` / `BIT #$1f` → is it a multiple of `$20`?).
- **Test one-hot/power-of-two state** with `BIT` (the Snake direction bits 1/2/4/8: opposite-direction check is a single `BIT` + `BNE`).
- **Decode a one-hot value** by repeated `LSR` and branching on carry (Snake's direction dispatch).
- **Index through memory/screen** with `($zp),Y` (indirect indexed) and zero-page pointer pairs.
- **Structure with subroutines** (`JSR`/`RTS`) and a top-level game/event **loop**; busy-wait (`spinWheels`: `NOP`s + `DEX`/`BNE`) for crude timing.

## Anti-patterns / gotchas

- Confusing `#$01` (literal) with `$01` (address) — the classic bug.
- Forgetting to `CLC` before an `ADC` or `SEC` before an `SBC` — stale carry corrupts the result.
- Expecting a branch to reach far code — it can't (~±128 bytes); use `JMP` for distance.
- Forgetting **little-endian** byte order when building pointers for indirect addressing.
- Reading flags from the wrong instruction — flags reflect the *most recent* flag-setting op, so order matters.
- Decimal mode (`SED`/`D` flag) silently changing `ADC`/`SBC` to BCD — leave it clear unless you mean it.

## How to use this skill

- **`references/instruction-set-and-addressing.md`** — flag-by-flag register/status detail, every addressing mode with a runnable example, and the instruction categories with their flag effects.
- **`references/programming-patterns.md`** — branching/looping, the stack, `JSR`/`RTS` subroutines, constants/labels, and a full walkthrough of the **Snake** game (game loop, zero-page state, indirect-indexed rendering, the direction-bit and screen-wrap tricks).

## Always-apply defaults

1. Keep `#literal` vs `address` straight; remember **little-endian** pointers.
2. `CLC`/`SEC` before standalone `ADC`/`SBC`; reason about the **carry** and **zero** flags explicitly.
3. Compare-then-branch (`CMP`+`BNE`) for control; use **labels**, not raw offsets.
4. Use **zero page** for hot/pointer data; index memory with `($zp),Y`.
5. Factor into **subroutines** with `JSR`/`RTS`; name magic numbers with `define`.

## Related

- [[operating-systems]] / [[osdev-kernel]] — the low-level mindset (registers, memory maps, the stack, interrupts) that assembly makes concrete.
- [[information-theory]] — binary, bitwise masking, and the carry/overflow that underlie arithmetic.
- Source: *Easy 6502* by Nick Morgan (skilldrick.github.io/easy6502, CC BY 4.0); opcode references at 6502.org and obelisk.me.uk.
