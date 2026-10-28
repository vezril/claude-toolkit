import unittest

from scheduler import SLOTS, book, next_slot


class SchedulerTest(unittest.TestCase):
    def test_full_day_has_no_slot(self):
        self.assertIsNone(next_slot(SLOTS))

    def test_next_slot_picks_earliest(self):
        busy = [s for s in SLOTS if s not in ("09:30", "15:00")]
        self.assertEqual(next_slot(busy), "09:30")

    def test_next_slot_is_earliest_whatever_the_set_order(self):
        # Free slots come from a set, whose order depends on the hash seed.
        # Check every suffix of the day so the result can't pass by luck.
        for i, expected in enumerate(SLOTS):
            busy = SLOTS[:i]
            self.assertEqual(next_slot(busy), expected)

    def test_book_rejects_double_booking(self):
        with self.assertRaises(ValueError):
            book(["10:00"], "10:00")


if __name__ == "__main__":
    unittest.main()
