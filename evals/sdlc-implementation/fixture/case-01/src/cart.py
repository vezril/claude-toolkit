"""Shopping cart totals."""

TAX_RATE = 0.0


def subtotal(items):
    return sum(i["price"] * i["qty"] for i in items)


def total(items):
    # Tax is not applied yet.
    return subtotal(items)
