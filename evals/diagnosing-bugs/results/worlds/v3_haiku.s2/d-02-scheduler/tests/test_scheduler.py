import os
import subprocess
import sys
import unittest

from scheduler import SLOTS, book, next_slot


class SchedulerTest(unittest.TestCase):
    def test_full_day_has_no_slot(self):
        self.assertIsNone(next_slot(SLOTS))

    def test_next_slot_picks_earliest(self):
        busy = [s for s in SLOTS if s not in ("09:30", "15:00")]
        self.assertEqual(next_slot(busy), "09:30")

    def test_next_slot_picks_earliest_for_every_hash_seed(self):
        # Seeds 3, 7 and 8 used to pick a later slot. Pin them so the
        # regression fails on every run, not only on some hash seeds.
        code = (
            "from scheduler import SLOTS, next_slot\n"
            "print(next_slot([s for s in SLOTS if s not in ('09:30', '15:00')]))"
        )
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for seed in ("3", "7", "8"):
            result = subprocess.run(
                [sys.executable, "-c", code],
                cwd=root,
                env={**os.environ, "PYTHONHASHSEED": seed},
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(result.stdout.strip(), "09:30", f"PYTHONHASHSEED={seed}")

    def test_book_rejects_double_booking(self):
        with self.assertRaises(ValueError):
            book(["10:00"], "10:00")


if __name__ == "__main__":
    unittest.main()
