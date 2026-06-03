# Registers, flags, instructions & addressing modes

Reference detail for the 6502 model (from *Easy 6502*). Opcode tables with cycle counts live at 6502.org/tutorials/6502opcodes.html and obelisk.me.uk/6502/reference.html — use those for the exact per-instruction flag/operand matrix.

## Registers

| Reg | Name | Role |
|-----|------|------|
| `A` | Accumulator | primary register for arithmetic/logic; most ops touch it |
| `X` | Index X | counters, loops, indexed addressing |
| `Y` | Index Y | counters, loops, indexed addressing |
| `SP` | Stack pointer | offset into page `$01`; `$ff` at reset, decrements on push |
| `PC` | Program counter | address of next instruction (easy6502 starts at `$0600`) |

Each register holds **one byte** (`$00`–`$ff`); `PC` is 16-bit.

## Processor status flags (the status byte)

Seven 1-bit flags, set as side effects of instructions and tested by branches:

- **C — Carry**: set when an unsigned add overflows a byte (or per shift/compare). `CLC`/`SEC` clear/set it.
- **Z — Zero**: set when the last result was `$00`. Drives `BEQ`/`BNE`.
- **N — Negative**: copy of bit 7 of the last result (sign bit). Drives `BMI`/`BPL`.
- **V — Overflow**: signed-arithmetic overflow. Drives `BVC`/`BVS`. `CLV` clears.
- **I — Interrupt disable**: masks IRQs. `SEI`/`CLI`.
- **D — Decimal**: BCD mode for `ADC`/`SBC`. `SED`/`CLD` — leave **clear** unless intentionally doing BCD.
- **B — Break**: indicates a `BRK` happened (in the pushed status).

You rarely set N/Z/V directly — you arrange code so the last flag-setting instruction leaves the flag reflecting what you want to branch on.

## Instruction categories (with flag effects)

- **Load / store** — `LDA LDX LDY` set N,Z from the loaded value; `STA STX STY` set no flags.
- **Register transfer** — `TAX TAY TXA TYA` set N,Z; `TSX` sets N,Z; `TXS` sets none.
- **Arithmetic** — `ADC` (A = A + M + C) and `SBC` (A = A − M − (1−C)) set N,V,Z,C. Always `CLC` before a fresh `ADC`, `SEC` before a fresh `SBC`.
- **Inc / dec** — `INX INY DEX DEY` (registers) and `INC DEC` (memory) set N,Z. Note: no `INA`/`DEA` on the NMOS 6502.
- **Logic** — `AND ORA EOR` set N,Z. `BIT` ANDs A with memory to set **Z** (and copies memory bits 7,6 into N,V) but **discards the result** — pure test.
- **Shift / rotate** — `ASL LSR ROL ROR` move bits through **carry**; set N,Z,C. `LSR` drops the LSB into C (used to decode one-hot values).
- **Compare** — `CMP CPX CPY` compute register − memory to set N,Z,C without storing: equal ⇒ Z=1; register ≥ memory ⇒ C=1.
- **Control** — branches (below), `JMP`, `JSR`/`RTS`, `RTI`, stack ops, `BRK`, `NOP`.

## Branches (relative addressing, ~±128 bytes)

| Branch | Taken when |
|--------|-----------|
| `BEQ` / `BNE` | Z set / clear (equal / not equal) |
| `BCS` / `BCC` | C set / clear |
| `BMI` / `BPL` | N set / clear (negative / positive) |
| `BVS` / `BVC` | V set / clear |

Idiom: `CPX #$03` then `BNE loop`. For longer distances, branch over a `JMP`.

## Addressing modes — runnable examples

**Immediate** `#$c0` — literal value:
```
LDX #$01      ; X = $01
```

**Zero page** `$c0` — one-byte address (first 256 bytes; fast/small):
```
STA $c000     ; absolute (two-byte) ...
STA $c0       ; ... vs zero page (one-byte) at $00c0
```

**Zero page,X** `$c0,X` (wraps within zero page):
```
LDX #$01
LDA #$aa
STA $a0,X     ; store A at $a1
INX
STA $a0,X     ; store A at $a2
; wrap:
LDX #$05
STA $ff,X     ; store A at $04  (($ff+$05) & $ff)
```
**Zero page,Y** `$c0,Y` — only with `LDX`/`STX`.

**Absolute,X / Absolute,Y** `$c000,X`:
```
LDX #$01
STA $0200,X   ; store A at $0201
```
(`absolute,Y` works with `LDA`/`STA` but not `STX`.)

**Indirect** `($c000)` — pointer; little-endian (low byte first):
```
LDA #$01
STA $f0
LDA #$cc
STA $f1
JMP ($00f0)   ; reads $f0/$f1 = $01/$cc -> jumps to $cc01
```

**Indexed indirect** `($c0,X)` — add X to the zp address, *then* dereference:
```
LDX #$01
LDA #$05
STA $01
LDA #$07
STA $02
LDY #$0a
STY $0705
LDA ($00,X)   ; ($00+X)=($01) -> bytes $05,$07 -> $0705 -> A = $0a
```

**Indirect indexed** `($c0),Y` — dereference the zp pointer, *then* add Y (the common one):
```
LDY #$01
LDA #$03
STA $01
LDA #$07
STA $02
LDX #$0a
STX $0704
LDA ($01),Y   ; ($01)-> $0703, + Y -> $0704 -> A = $0a
```

**Relative** — branch offset (see Branches). **Implicit** — no operand (`INX`, `RTS`, `BRK`).

## Hexdump intuition

Assembling `LDA #$01 / CMP #$02 / BNE notequal / STA $22 / notequal: BRK` gives:
```
a9 01 c9 02 d0 02 85 22 00
```
`a9`=immediate LDA, `c9`=immediate CMP, `d0`=BNE (operand `02` = skip 2 bytes = the `85 22` `STA $22`), `00`=BRK. Change `STA $22` to absolute `STA $2222` and the BNE operand becomes `03` (skipping a now-3-byte instruction) — a concrete way to see relative offsets.
