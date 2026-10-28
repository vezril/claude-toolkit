import unittest

from scheduler import SLOTS, book, free_slots, next_slot


class SchedulerTest(unittest.TestCase):
    def test_full_day_has_no_slot(self):
        self.assertIsNone(next_slot(SLOTS))

    def test_free_slots_keeps_day_order(self):
        self.assertEqual(free_slots(["09:00"]), SLOTS[1:])

    def test_next_slot_picks_earliest(self):
        busy = [s for s in SLOTS if s not in ("09:30", "15:00")]
        self.assertEqual(next_slot(busy), "09:30")

    def test_book_rejects_double_booking(self):
        with self.assertRaises(ValueError):
            book(["10:00"], "10:00")


if __name__ == "__main__":
    unittest.main()
