"""Sales tax on a subtotal, rounded half-up to the cent (the rule the tax authority uses)."""
from decimal import Decimal, ROUND_HALF_UP


def tax_amount(subtotal, rate):
    return (Decimal(subtotal) * Decimal(rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
