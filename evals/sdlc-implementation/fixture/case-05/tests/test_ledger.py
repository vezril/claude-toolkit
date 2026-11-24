import unittest

from src.ledger import apply_entry


class TestApplyEntry(unittest.TestCase):
    def test_credit_increases_the_balance(self):
        self.assertEqual(150.0, apply_entry(100.0, {"amount": 50.0, "kind": "credit"}))


if __name__ == "__main__":
    unittest.main()
