"""Invoice totals."""
import json
from decimal import Decimal, ROUND_HALF_UP

from tax import tax_amount

TAX_RATE = Decimal("0.14975")


def line_total(quantity, unit_price, discount_pct=0):
    """Quantity times unit price, less the line's percentage discount, in dollars and cents."""
    amount = Decimal(quantity) * Decimal(str(unit_price)) * (1 - Decimal(str(discount_pct)) / 100)
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def subtotal(lines):
    return sum(line_total(**line) for line in lines)


def invoice_total(lines):
    sub = subtotal(lines)
    return sub + tax_amount(sub, TAX_RATE)


def load(path):
    with open(path) as f:
        return json.load(f)["lines"]
