"""Shopping cart totals."""

TAX_RATE = 0.2


def subtotal(items):
    return sum(i["price"] * i["qty"] for i in items)


def total(items):
    return subtotal(items) * (1 + TAX_RATE)
