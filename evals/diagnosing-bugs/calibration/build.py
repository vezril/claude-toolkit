"""Build hand-labelled snapshots for calibrating the asserts: for each label, a copy of
a fixture project with a known change (a correct fix plus regression test, a fix in the
wrong place, leftover instrumentation, a stray repro script, no test). Writes
calibration/snaps/<label>/<case>/ and calibration/fixtures.json."""
import json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SNAPS = os.path.join(HERE, "snaps"); shutil.rmtree(SNAPS, ignore_errors=True)

def make(label, case, d, edits, add={}, remove=[]):
    dst = os.path.join(SNAPS, label, case); shutil.copytree(os.path.join(ROOT, "fixture", d), dst, ignore=shutil.ignore_patterns("sample.log", "__pycache__"))
    for f, (a, b) in edits:
        p = os.path.join(dst, f); s = open(p).read(); assert a in s, (label, f, a); open(p, "w").write(s.replace(a, b))
    for f, body in add.items():
        os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True); open(os.path.join(dst, f), "w").write(body)
    for f in remove: os.remove(os.path.join(dst, f))

INV_FIX = [("invoice.py", ("    amount = quantity * unit_price * (1 - discount_pct / 100)\n    return int(amount * 100) / 100",
                           "    amount = Decimal(str(quantity)) * Decimal(str(unit_price)) * (1 - Decimal(str(discount_pct)) / 100)\n    return float(amount.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP))")),
           ("invoice.py", ("from decimal import Decimal\n", "from decimal import Decimal, ROUND_HALF_UP\n"))]
INV_TEST = {"tests/test_inv1043.py": "import unittest\nfrom decimal import Decimal\nfrom invoice import invoice_total, load\n\nclass T(unittest.TestCase):\n    def test_inv1043(self):\n        self.assertEqual(invoice_total(load('data/INV-1043.json')), Decimal('71.65'))\n"}
SCH_FIX = [("scheduler.py", ("    return list(free)[0]", "    return min(free)"))]
SCH_TEST = {"tests/test_earliest.py": "import unittest\nfrom scheduler import SLOTS, next_slot\n\nclass T(unittest.TestCase):\n    def test_earliest_any_order(self):\n        self.assertEqual(next_slot([]), '09:00')\n        self.assertEqual(next_slot(['09:00']), '09:30')\n"}
WEA_FIX = [("client.py", ('f"Bearer{key}"', 'f"Bearer {key}"'))]
WEA_TEST = {"tests/test_auth.py": "import unittest\nimport client, fake_api\n\nclass T(unittest.TestCase):\n    def test_fake_api_accepts_key(self):\n        self.assertEqual(client.forecast('Montreal', fake_api)['city'], 'Montreal')\n"}
LOG_FIX = [("parse.py", ("    out = []\n", "    out, seen = [], set()\n")), ("parse.py", ("        if rec not in out:\n            out.append(rec)", "        if rec not in seen:\n            seen.add(rec)\n            out.append(rec)"))]

fx = []
def add(label, case, d, fails, edits=[], extra={}, calls=None, output=""):
    make(label, case, d, edits, extra); fx.append({"label": label, "case": case, "fails": fails, "calls": calls, "output": output})
RUN = [{"name": "Bash", "input": {"command": "cd X && python3 -m unittest"}}]
def EDIT(d, f): return [{"name": "Edit", "input": {"file_path": f"/w/{d}/{f}"}}]
TIME = [{"name": "Bash", "input": {"command": "cd logs && time python3 -c 'import parse; parse.parse_log(open(\"sample.log\").read())'"}}]

add("good", "d-01-invoices", "invoices", [], INV_FIX, INV_TEST, RUN + EDIT("invoices", "invoice.py"), "Root cause: line_total truncated with int() instead of rounding.")
add("wrong-place", "d-01-invoices", "invoices", ["fixed", "regression"], [("tax.py", ("ROUND_HALF_UP)\n", "ROUND_HALF_UP) + Decimal(\"0.01\")\n"))], {}, RUN + EDIT("invoices", "tax.py"), "The tax rounding truncates; fixed tax.py.")
add("leftover-print", "d-01-invoices", "invoices", ["clean"], INV_FIX + [("invoice.py", ("def subtotal(lines):\n", "def subtotal(lines):\n    print('[DEBUG-a1] lines', lines)\n"))], INV_TEST, RUN + EDIT("invoices", "invoice.py"), "int() truncation was the cause.")
add("stray-repro", "d-01-invoices", "invoices", ["clean"], INV_FIX, {**INV_TEST, "repro.py": "import invoice\nprint(invoice.invoice_total(invoice.load('data/INV-1043.json')))\n"}, RUN + EDIT("invoices", "invoice.py"), "Truncation in line_total.")
add("edit-first-no-cause", "d-01-invoices", "invoices", ["loop-first", "cause"], INV_FIX, INV_TEST, EDIT("invoices", "invoice.py") + RUN, "Fixed it.")
add("good", "d-02-scheduler", "scheduler", [], SCH_FIX, SCH_TEST, RUN + EDIT("scheduler", "scheduler.py"), "list(set) has no order across hash seeds; now min().")
add("no-test", "d-02-scheduler", "scheduler", ["regression"], SCH_FIX, {}, RUN + EDIT("scheduler", "scheduler.py"), "Sets are unordered.")
add("test-passes-on-bug", "d-02-scheduler", "scheduler", ["regression"], SCH_FIX, {"tests/test_full.py": "import unittest\nfrom scheduler import SLOTS, next_slot\n\nclass T(unittest.TestCase):\n    def test_full(self):\n        self.assertIsNone(next_slot(SLOTS))\n"}, RUN + EDIT("scheduler", "scheduler.py"), "Set ordering.")
add("good", "d-03-weather", "weather", [], WEA_FIX, WEA_TEST, RUN + EDIT("weather", "client.py"), "The header was 'Bearer<key>' with no space. Key: <REDACTED>.")
add("leaks-key", "d-03-weather", "weather", ["redact"], WEA_FIX, WEA_TEST, RUN + EDIT("weather", "client.py"), "Missing space: the header sent was Bearerwk_live_7Q2f9XcA41LmZ8dR.")
add("good", "d-04-logs", "logs", [], LOG_FIX, {}, TIME + EDIT("logs", "parse.py"), "Dedupe did `rec not in out` on a list: quadratic. Now a set.")
add("no-measure", "d-04-logs", "logs", ["measured"], LOG_FIX, {}, RUN + EDIT("logs", "parse.py"), "Quadratic list membership; now a set.")
add("not-fixed", "d-04-logs", "logs", ["fixed", "cause"], [], {}, TIME, "It's fine on my machine.")
json.dump(fx, open(os.path.join(HERE, "fixtures.json"), "w"), indent=1)
print(len(fx), "fixtures")
