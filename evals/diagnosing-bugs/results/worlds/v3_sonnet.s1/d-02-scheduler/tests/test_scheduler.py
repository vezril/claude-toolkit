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

    def test_next_slot_independent_of_hash_seed(self):
        code = (
            "from scheduler import SLOTS, next_slot;"
            "busy = [s for s in SLOTS if s not in ('09:30', '15:00')];"
            "print(next_slot(busy))"
        )
        for seed in range(20):
            env = dict(os.environ, PYTHONHASHSEED=str(seed))
            out = subprocess.run([sys.executable, "-c", code], env=env,
                                 capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(out, "09:30", f"PYTHONHASHSEED={seed}")

    def test_book_rejects_double_booking(self):
        with self.assertRaises(ValueError):
            book(["10:00"], "10:00")


if __name__ == "__main__":
    unittest.main()
