import unittest

from parse import parse_line, parse_log


class ParseTest(unittest.TestCase):
    def test_parse_line(self):
        self.assertEqual(parse_line("1.2.3.4 GET /a 200 12"), ("1.2.3.4", "GET", "/a", 200, 12))

    def test_duplicates_dropped_in_order(self):
        text = "1.1.1.1 GET /a 200 5\n2.2.2.2 GET /b 404 3\n1.1.1.1 GET /a 200 5\n"
        self.assertEqual([r[2] for r in parse_log(text)], ["/a", "/b"])


if __name__ == "__main__":
    unittest.main()
