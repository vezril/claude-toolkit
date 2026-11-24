import unittest

from src.upload import ALLOWED


class TestAllowList(unittest.TestCase):
    def test_png_is_allowed(self):
        self.assertIn(".png", ALLOWED)


if __name__ == "__main__":
    unittest.main()
