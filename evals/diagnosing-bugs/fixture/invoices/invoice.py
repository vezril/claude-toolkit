"""Invoice totals."""
import json
from decimal import Decimal

from tax import tax_amount

TAX_RATE = Decimal("0.14975")


def line_total(quantity, unit_price, discount_pct=0):
    """Quantity times unit price, less the line's percentage discount, in dollars and cents."""
    amount = quantity * unit_price * (1 - discount_pct / 100)
    return int(amount * 100) / 100


def subtotal(lines):
    return sum(Decimal(str(line_total(**line))) for line in lines)


def invoice_total(lines):
    sub = subtotal(lines)
    return sub + tax_amount(sub, TAX_RATE)


def load(path):
    with open(path) as f:
        return json.load(f)["lines"]
