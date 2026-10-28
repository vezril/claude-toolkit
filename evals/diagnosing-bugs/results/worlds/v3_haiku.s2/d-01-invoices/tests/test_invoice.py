import os
import unittest
from decimal import Decimal

from invoice import invoice_total, line_total, load
from tax import tax_amount

INV_1043 = os.path.join(os.path.dirname(__file__), "..", "data", "INV-1043.json")


class InvoiceTest(unittest.TestCase):
    def test_line_without_discount(self):
        self.assertEqual(line_total(2, 10.0), 20.0)

    def test_line_with_round_discount(self):
        self.assertEqual(line_total(1, 10.0, 10), 9.0)

    def test_line_discount_rounds_half_up(self):
        # 12.49 * 0.85 = 10.6165, which must round to 10.62, not truncate to 10.61
        self.assertEqual(line_total(1, 12.49, 15), 10.62)

    def test_fixture_invoice_total_matches_customer(self):
        self.assertEqual(invoice_total(load(INV_1043)), Decimal("71.65"))

    def test_tax_rounds_half_up(self):
        self.assertEqual(tax_amount(Decimal("10.00"), Decimal("0.14975")), Decimal("1.50"))

    def test_simple_invoice(self):
        self.assertEqual(invoice_total([{"quantity": 2, "unit_price": 10.0}]), Decimal("23.00"))


if __name__ == "__main__":
    unittest.main()
