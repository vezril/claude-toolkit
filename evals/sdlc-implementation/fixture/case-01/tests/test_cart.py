import unittest

from src.cart import subtotal


class TestSubtotal(unittest.TestCase):
    def test_sums_line_items(self):
        self.assertEqual(6.0, subtotal([{"price": 2.0, "qty": 3}]))


if __name__ == "__main__":
    unittest.main()
