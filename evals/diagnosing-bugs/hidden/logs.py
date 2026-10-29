"""Hidden check for d-04: same records in the same order, and 200k lines parse in under 2
seconds. The timing runs in a subprocess with a 10-second cap, because the quadratic
version takes minutes."""
import os, subprocess, sys
P = os.path.abspath(sys.argv[1])
code = r'''
import random, sys, time
import parse
text = "1.1.1.1 GET /a 200 5\n2.2.2.2 GET /b 404 3\n1.1.1.1 GET /a 200 5\n\n3.3.3.3 POST /c 500 9\n2.2.2.2 GET /b 404 3\n"
got = [r[2] for r in parse.parse_log(text)]
if got != ["/a", "/b", "/c"]:
    print("FAIL order/dedupe:", got); sys.exit(1)
random.seed(11)
lines = [f"10.1.{random.randint(0,255)}.{random.randint(0,255)} GET /r/{random.randint(0,5000)} 200 {random.randint(1,999)}" for _ in range(200000)]
lines += lines[:5000]
t = time.perf_counter(); n = len(parse.parse_log("\n".join(lines))); dt = time.perf_counter() - t
if n != len(set(lines)):
    print(f"FAIL count: {n} != {len(set(lines))}"); sys.exit(1)
if dt > 2.0:
    print(f"FAIL slow: {dt:.1f}s for 205k lines"); sys.exit(1)
'''
try:
    r = subprocess.run([sys.executable, "-c", code], cwd=P, capture_output=True, text=True, timeout=10)
except subprocess.TimeoutExpired:
    print("FAIL slow: over 10s for 205k lines"); sys.exit(1)
if r.returncode:
    print((r.stdout + r.stderr).strip().splitlines()[-1]); sys.exit(1)
