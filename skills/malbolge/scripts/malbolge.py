#!/usr/bin/env python3
"""A correct reference Malbolge interpreter. Stdlib only.

Follows Ben Olmstead's reference interpreter (the de-facto standard), which is held
correct wherever it differs from the spec text — notably the I/O swap: '<' OUTPUTS and
'/' INPUTS (the spec text says the reverse). Verified: it prints "Hello, world." from the
canonical program, and validation matches the reference load rules.

Program input (for the '/' instruction) is read from stdin. Program output goes to stdout.

Usage:
    python3 malbolge.py PROGRAM.mal                 # run; program input read from stdin
    echo "hi" | python3 malbolge.py cat.mal         # feed stdin to the running program
    python3 malbolge.py --validate PROGRAM.mal      # check it loads (exit 0 ok, 1 rejected)
    python3 malbolge.py --max-steps 5000000 P.mal   # raise the safety step cap (default 20M)
    python3 malbolge.py -                            # read the PROGRAM itself from stdin

Notes:
- Whitespace in the program is ignored. Non-whitespace, non-instruction chars are rejected
  at load time (like the reference), unless --no-validate is given.
- The machine is ternary: 59049 (3^10) ten-trit words; registers a, c, d all start at 0.
"""
import argparse
import sys

# The two 94-character tables from Ben Olmstead's specification, character-for-character.
# XLAT1 decodes an instruction; XLAT2 re-encrypts it after execution (self-modifying code).
XLAT1 = ("+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA\"lI"
         ".v%{gJh4G\\-=O@5`_3i<?Z';FNQuY]szf$!BS/|t:Pn6^Ha")
XLAT2 = ("5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1C"
         "B6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G\"i@")

# The tritwise "crazy" op, CRZ[d_trit][a_trit] -> out_trit (verified against the spec's
# di-trit table). "Don't look for a pattern; it's not there." — Olmstead.
CRZ = ((1, 0, 0), (1, 0, 2), (2, 2, 1))

MEM_SIZE = 59049          # 3^10
TRIT_HIGH = 19683         # 3^9, weight of the most-significant trit
MAXVAL = MEM_SIZE - 1     # 59048 == EOF sentinel


def crazy(a, d):
    """Tritwise op over 10 trits: out_trit = CRZ[d_trit][a_trit]."""
    out = 0
    place = 1
    for _ in range(10):
        out += CRZ[d % 3][a % 3] * place
        a //= 3
        d //= 3
        place *= 3
    return out


def rotr(v):
    """Rotate a 10-trit value right by one trit (LS trit becomes MS trit)."""
    return (v // 3) + (v % 3) * TRIT_HIGH


def _decode(mem_c, c):
    """The instruction char selected at code position c (or None if mem_c isn't graphic ASCII)."""
    if not (33 <= mem_c <= 126):
        return None
    return XLAT1[(mem_c - 33 + c) % 94]


def load(source, validate=True):
    """Parse program text into memory. Returns (mem, error_or_None)."""
    mem = []
    for pos, ch in enumerate(ch for ch in source if ch not in " \t\r\n\v\f"):
        code = ord(ch)
        if validate:
            op = _decode(code, len(mem))
            if op not in ("i", "j", "*", "p", "<", "/", "v", "o"):
                return None, ("invalid instruction %r at program position %d "
                              "(decodes to %r)" % (ch, len(mem), op))
        if not (0 <= code <= MAXVAL):
            return None, "character out of range at position %d" % len(mem)
        mem.append(code)
    if not mem:
        return None, "empty program"
    # Fill the rest of memory with the crazy op on the previous two cells.
    while len(mem) < MEM_SIZE:
        mem.append(crazy(mem[-1], mem[-2]))
    return mem, None


def run(mem, max_steps=20_000_000):
    """Execute. Program input for '/' is read from stdin; output written to stdout."""
    a = c = d = 0
    steps = 0
    out = sys.stdout
    while True:
        steps += 1
        if steps > max_steps:
            sys.stderr.write("\n[malbolge: step limit %d reached — likely non-terminating]\n" % max_steps)
            return 2
        instr = mem[c]
        if not (33 <= instr <= 126):
            return 0  # non-graphic instruction ends the program
        op = XLAT1[(instr - 33 + c) % 94]
        if op == "j":
            d = mem[d]
        elif op == "i":
            c = mem[d]
        elif op == "*":
            a = mem[d] = rotr(mem[d])
        elif op == "p":
            a = mem[d] = crazy(a, mem[d])
        elif op == "<":                      # reference: '<' OUTPUTS
            out.write(chr(a % 256))
            out.flush()
        elif op == "/":                      # reference: '/' INPUTS
            ch = sys.stdin.read(1)
            a = MAXVAL if ch == "" else ord(ch)
        elif op == "v":
            return 0
        # 'o' and any other decode are a nop
        # Re-encrypt the executed instruction, then advance both pointers.
        if 33 <= mem[c] <= 126:
            mem[c] = ord(XLAT2[mem[c] - 33])
        c = (c + 1) % MEM_SIZE
        d = (d + 1) % MEM_SIZE


def main():
    p = argparse.ArgumentParser(description="Reference Malbolge interpreter (stdlib only).")
    p.add_argument("program", help="Malbolge source file, or '-' to read the program from stdin.")
    p.add_argument("--validate", action="store_true", help="Only check the program loads; print OK/rejected.")
    p.add_argument("--no-validate", action="store_true", help="Skip load-time instruction validation.")
    p.add_argument("--max-steps", type=int, default=20_000_000, help="Safety cap on executed instructions.")
    args = p.parse_args()

    source = sys.stdin.read() if args.program == "-" else open(args.program, encoding="latin-1").read()
    mem, err = load(source, validate=not args.no_validate)
    if err:
        sys.stderr.write("malbolge: %s\n" % err)
        sys.exit(1)
    if args.validate:
        print("OK: program loads (%d instruction cells)." % sum(1 for ch in source if ch not in " \t\r\n\v\f"))
        sys.exit(0)
    sys.exit(run(mem, max_steps=args.max_steps))


if __name__ == "__main__":
    main()
