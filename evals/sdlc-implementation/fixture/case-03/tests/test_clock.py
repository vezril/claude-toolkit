import unittest

from src.clock import SESSION_TTL


class TestTtl(unittest.TestCase):
    def test_ttl_is_thirty_minutes(self):
        self.assertEqual(1800, SESSION_TTL)


if __name__ == "__main__":
    unittest.main()
