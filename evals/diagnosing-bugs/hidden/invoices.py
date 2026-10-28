"""Hidden check for d-01: totals match the half-up-per-line rule on invoices the agent never saw."""
import sys, os
from decimal import Decimal, ROUND_HALF_UP
P = os.path.abspath(sys.argv[1]); os.chdir(P); sys.path.insert(0, P)
import invoice

def want(lines):
    sub = sum((Decimal(str(l["quantity"])) * Decimal(str(l["unit_price"])) * (1 - Decimal(str(l.get("discount_pct", 0))) / 100)).quantize(Decimal("0.01"), ROUND_HALF_UP) for l in lines)
    return sub + (sub * Decimal("0.14975")).quantize(Decimal("0.01"), ROUND_HALF_UP)

cases = [
    invoice.load("data/INV-1043.json"),
    [{"quantity": 5, "unit_price": 1.99}, {"quantity": 3, "unit_price": 2.49, "discount_pct": 20}],
    [{"quantity": 4, "unit_price": 3.35, "discount_pct": 5}],
    [{"quantity": 7, "unit_price": 0.1}, {"quantity": 1, "unit_price": 99.99, "discount_pct": 33}],
    [{"quantity": 2, "unit_price": 10.0}],
]
bad = 0
for c in cases:
    got = Decimal(str(invoice.invoice_total(c))).quantize(Decimal("0.01"))
    if got != want(c):
        bad += 1; print(f"FAIL {c}: got {got}, want {want(c)}")
sys.exit(1 if bad else 0)
