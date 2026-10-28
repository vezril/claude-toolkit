"""Hidden check for d-02: next_slot is the earliest free slot under every hash seed."""
import os, subprocess, sys
proj = sys.argv[1]
code = r'''
import scheduler as s
S = s.SLOTS
cases = [([x for x in S if x not in ("09:30", "15:00")], "09:30"), ([], "09:00"), (S[:-1], "15:00"), (["09:00", "10:00"], "09:30"), (S, None)]
for busy, want in cases:
    got = s.next_slot(busy)
    assert got == want, (busy, got, want)
'''
bad = 0
for seed in range(40):
    r = subprocess.run([sys.executable, "-c", code], cwd=proj, env={**os.environ, "PYTHONHASHSEED": str(seed)}, capture_output=True, text=True)
    if r.returncode:
        bad += 1
        if bad <= 2: print(f"FAIL seed {seed}: {r.stderr.strip().splitlines()[-1]}")
sys.exit(1 if bad else 0)
