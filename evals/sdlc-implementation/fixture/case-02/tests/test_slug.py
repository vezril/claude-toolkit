import unittest

from src.slug import slugify


class TestSlugify(unittest.TestCase):
    def test_lowercases_and_dashes(self):
        self.assertEqual("hello-world", slugify("Hello World"))


if __name__ == "__main__":
    unittest.main()
