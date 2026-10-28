import unittest
from decimal import Decimal

from invoice import invoice_total, line_total
from tax import tax_amount


class InvoiceTest(unittest.TestCase):
    def test_line_without_discount(self):
        self.assertEqual(line_total(2, 10.0), 20.0)

    def test_line_with_round_discount(self):
        self.assertEqual(line_total(1, 10.0, 10), 9.0)

    def test_tax_rounds_half_up(self):
        self.assertEqual(tax_amount(Decimal("10.00"), Decimal("0.14975")), Decimal("1.50"))

    def test_simple_invoice(self):
        self.assertEqual(invoice_total([{"quantity": 2, "unit_price": 10.0}]), Decimal("23.00"))


if __name__ == "__main__":
    unittest.main()
