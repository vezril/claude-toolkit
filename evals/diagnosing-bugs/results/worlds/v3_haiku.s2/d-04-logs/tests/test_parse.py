import time
import unittest

from parse import parse_line, parse_log


class ParseTest(unittest.TestCase):
    def test_parse_line(self):
        self.assertEqual(parse_line("1.2.3.4 GET /a 200 12"), ("1.2.3.4", "GET", "/a", 200, 12))

    def test_duplicates_dropped_in_order(self):
        text = "1.1.1.1 GET /a 200 5\n2.2.2.2 GET /b 404 3\n1.1.1.1 GET /a 200 5\n"
        self.assertEqual([r[2] for r in parse_log(text)], ["/a", "/b"])

    def test_large_log_parses_quickly(self):
        # 50k unique lines: the old list-based dedup took ~13s here; the set-based one takes milliseconds.
        text = "\n".join(f"10.0.{i // 256 % 256}.{i % 256} GET /recipes/{i} 200 {i % 999}" for i in range(50_000))
        start = time.perf_counter()
        records = parse_log(text)
        elapsed = time.perf_counter() - start
        self.assertEqual(len(records), 50_000)
        self.assertLess(elapsed, 2.0)


if __name__ == "__main__":
    unittest.main()
