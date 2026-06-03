# Programming patterns & the Snake game (Easy 6502)

Putting instructions together: loops, the stack, subroutines, constants, and the full Snake walkthrough.

## Branching & loops

A countdown loop with a label and `BNE`:
```
  LDX #$08
decrement:
  DEX
  STX $0200       ; draw current value as a pixel
  CPX #$03
  BNE decrement   ; loop until X == $03
  STX $0201
  BRK
```
`CPX` sets Z when X reaches `$03`; `BNE` (branch while Z clear) repeats. Labels become relative offsets at assembly time, so the loop body must stay within ~±128 bytes.

## The stack: PHA / PLA

The stack lives at `$0100`–`$01ff`, `SP` starts `$ff` and grows down. Push/pull are LIFO, so popping reverses order — this draws a mirrored colour pattern:
```
  LDX #$00
  LDY #$00
firstloop:
  TXA
  STA $0200,Y
  PHA             ; push colour
  INX
  INY
  CPY #$10
  BNE firstloop   ; first 16 pixels, pushing each colour
secondloop:
  PLA             ; pull in reverse order
  STA $0200,Y
  INY
  CPY #$20
  BNE secondloop
```

## Jumping & subroutines

`JMP` is an unconditional two-byte jump. `JSR`/`RTS` implement call/return: `JSR` pushes (return address − 1) and jumps; `RTS` pulls it, adds 1, resumes.
```
  JSR init
  JSR loop
  JSR end
init:
  LDX #$00
  RTS
loop:
  INX
  CPX #$05
  BNE loop
  RTS
end:
  BRK
```
This is the basis of modular code — small named subroutines called from a driver.

## Constants & labels (`define`)

```
define sysRandom $fe   ; an address
define a_dozen   $0c   ; a constant
  LDA sysRandom        ; == LDA $fe
  LDX #a_dozen         ; == LDX #$0c  (immediate still needs #)
```
Use `define` for screen addresses, key codes, and state variables so code reads intent, not magic numbers.

## Worked example: the Snake game

A complete game that ties everything together. Key design ideas:

### Top-level structure
```
  jsr init
  jsr loop
```
`init` sets up state; `loop` is the game loop that calls subroutines then jumps back to itself:
```
loop:
  jsr readKeys        ; input
  jsr checkCollision  ; update state
  jsr updateSnake
  jsr drawApple       ; render
  jsr drawSnake
  jsr spinWheels      ; crude delay
  jmp loop
```
The universal game-loop shape: **input → update → render**, repeated.

### Zero-page state
Game variables live in the zero page so they're cheap and usable as **indirect pointers**. Byte *pairs* hold two-byte screen addresses (`$0200`–`$05ff`):
- `$00/$01` apple location (low/high), `$10/$11` snake-head location, `$12+` body segment pairs.
- `$02` direction (one-hot: `1`=up, `2`=right, `4`=down, `8`=left), `$03` snake length in bytes (4 bytes = 2 pixels).

Remember **little-endian**: `$10`/`$04` at `$10`/`$11` ⇒ address `$0410`.

### Random apple via bit masking
```
generateApplePosition:
  lda sysRandom
  sta appleL          ; random low byte
  lda sysRandom
  and #$03            ; mask to 0..3
  clc
  adc #2              ; -> 2..5 (valid high byte for $0200-$05ff)
  sta appleH
  rts
```
`AND #$03` keeps the low two bits (range 0–3); adding 2 yields a high byte in 2–5.

### Direction logic with BIT (one-hot trick)
Each key handler rejects a reversal using `BIT` against the *opposite* direction. Because directions are powers of two, `dir AND opposite` is zero unless they're the same bit:
```
upKey:
  lda #movingDown
  bit snakeDirection
  bne illegalMove     ; currently moving down -> ignore
  lda #movingUp
  sta snakeDirection
  rts
```

### Moving the snake
Shift every body byte-pair forward one slot (high → low using `X` index and `BPL`), then move the head per direction:
```
updateSnake:
  ldx snakeLength
  dex
  txa
updateloop:
  lda snakeHeadL,x
  sta snakeBodyStart,x
  dex
  bpl updateloop      ; while X >= 0
```
Decode the one-hot direction by repeated `LSR`, branching on carry:
```
  lda snakeDirection
  lsr
  bcs up              ; bit0 -> up
  lsr
  bcs right           ; bit1 -> right
  lsr
  bcs down
  lsr
  bcs left
```

### Screen geometry & wrap detection
The 32×32 display is four strips: `$0200-$02ff`, `$0300-$03ff`, `$0400-$04ff`, `$0500-$05ff`. Within a strip, **+1 = right**, **+$20 = down**. Crossing a strip is handled by the **carry**: adding `$20` to a low byte ≥ `$e0` sets carry, signalling "increment the high byte too." Out-of-bounds checks use masks:
```
right:
  inc snakeHeadL
  lda #$1f
  bit snakeHeadL      ; multiple of $20? -> wrapped off the right edge
  beq collision
  rts
```
`$1f` masks the low 5 bits; a result of zero means the address is a multiple of `$20` (column 0), i.e. it wrapped.

### Rendering with indirect indexed addressing
```
drawApple:
  ldy #0
  lda sysRandom
  sta (appleL),y      ; write a random colour at the apple's address
  rts
drawSnake:
  ldx snakeLength
  lda #0
  sta (snakeHeadL,x)  ; erase old tail
  ldx #0
  lda #1
  sta (snakeHeadL,x)  ; paint head white
  rts
```
Only the head and tail change each frame, so two writes keep the snake moving.

### Timing
```
spinWheels:
  ldx #0
spinloop:
  nop
  nop
  dex
  bne spinloop        ; first DEX wraps $00 -> $ff, burning ~256 iterations
  rts
```
A busy-wait delay — no real timer needed in the simulator.

### Takeaways
Every technique in the tutorial appears here: zero-page pointers + indirect-indexed addressing for the screen, `BIT`/`AND` masking, carry-based wrap detection, `LSR` one-hot decoding, and `JSR`/`RTS` decomposition around an input→update→render loop. A fully annotated version of this source is linked from the tutorial (Willem van der Jagt's gist).
