"""Generate fixture/logs/sample.log (50k access-log lines, ~1% duplicated), seeded so it is
the same file every time. run.sh writes it into each world; it isn't committed (1.7 MB)."""
import random, sys
random.seed(7)
ips = [f"10.0.{a}.{b}" for a in range(8) for b in range(32)]
paths = [f"/recipes/{i}" for i in range(400)] + ["/plan", "/list", "/login"]
lines = []
for i in range(50000):
    lines.append(f"{random.choice(ips)} {random.choice(['GET', 'GET', 'POST'])} {random.choice(paths)} {random.choice([200, 200, 200, 304, 404, 500])} {random.randint(1, 900)}")
    if random.random() < 0.01:
        lines.append(lines[-1])
open(sys.argv[1], "w").write("\n".join(lines) + "\n")
