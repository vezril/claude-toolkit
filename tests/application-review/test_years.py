#!/usr/bin/env python3
"""Tests for years.py: date parsing and the merged-range arithmetic of design D5.

Run: python3 tests/application-review/test_years.py
Standard library only, like the code under test.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "application-review"))

from years import (  # noqa: E402
    Range,
    merge_ranges,
    months_to_years,
    parse_month,
    position_range,
    total_months,
)

RUN_DATE = "2026-11-03"


class ParseMonth(unittest.TestCase):
    def test_iso_month(self):
        self.assertEqual(parse_month("2018-01"), (2018, 1, False))

    def test_iso_day_is_truncated_to_month(self):
        self.assertEqual(parse_month("2018-01-17"), (2018, 1, False))

    def test_year_only_is_approximate(self):
        # D5: a month-less year is Jan-Dec with an approximate flag.
        self.assertEqual(parse_month("2018"), (2018, 1, True))

    def test_year_only_as_end_is_december(self):
        self.assertEqual(parse_month("2018", end=True), (2018, 12, True))

    def test_english_month_names(self):
        self.assertEqual(parse_month("Jan 2018"), (2018, 1, False))
        self.assertEqual(parse_month("January 2018"), (2018, 1, False))
        self.assertEqual(parse_month("Sept 2018"), (2018, 9, False))

    def test_french_month_names(self):
        # D10: FR CVs are in scope, so FR month names must parse.
        self.assertEqual(parse_month("janvier 2018"), (2018, 1, False))
        self.assertEqual(parse_month("février 2019"), (2019, 2, False))
        self.assertEqual(parse_month("août 2020"), (2020, 8, False))
        self.assertEqual(parse_month("déc. 2021"), (2021, 12, False))

    def test_slash_and_dot_forms(self):
        self.assertEqual(parse_month("01/2018"), (2018, 1, False))
        self.assertEqual(parse_month("2018.03"), (2018, 3, False))

    def test_present_requires_run_date(self):
        self.assertEqual(parse_month("Present", run_date=RUN_DATE), (2026, 11, False))
        self.assertEqual(parse_month("present", run_date=RUN_DATE), (2026, 11, False))
        self.assertEqual(parse_month("Current", run_date=RUN_DATE), (2026, 11, False))
        self.assertEqual(parse_month("now", run_date=RUN_DATE), (2026, 11, False))

    def test_french_present_words(self):
        self.assertEqual(parse_month("aujourd'hui", run_date=RUN_DATE), (2026, 11, False))
        self.assertEqual(parse_month("en cours", run_date=RUN_DATE), (2026, 11, False))
        self.assertEqual(parse_month("à ce jour", run_date=RUN_DATE), (2026, 11, False))

    def test_present_without_run_date_is_an_error(self):
        # The run date is injectable so the tests do not drift with the calendar.
        with self.assertRaises(ValueError):
            parse_month("Present")

    def test_unparseable(self):
        for bad in ["", "   ", "sometime", "20188", "13/2018", "2018-13"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    parse_month(bad)


class PositionRange(unittest.TestCase):
    def test_inclusive_month_count(self):
        # Jan 2018 to Dec 2018 is 12 months of work, not 11.
        r = position_range("2018-01", "2018-12")
        self.assertEqual(r.start, (2018, 1))
        self.assertEqual(r.end, (2018, 12))
        self.assertEqual(r.months, 12)

    def test_single_month(self):
        self.assertEqual(position_range("2018-05", "2018-05").months, 1)

    def test_approximate_propagates_from_either_end(self):
        self.assertTrue(position_range("2018", "2019-06").approximate)
        self.assertTrue(position_range("2018-01", "2019").approximate)
        self.assertFalse(position_range("2018-01", "2019-06").approximate)

    def test_year_only_both_ends_spans_whole_years(self):
        r = position_range("2018", "2019")
        self.assertEqual(r.months, 24)
        self.assertTrue(r.approximate)

    def test_present_end(self):
        r = position_range("2026-01", "Present", run_date=RUN_DATE)
        self.assertEqual(r.months, 11)

    def test_end_before_start_is_an_error(self):
        with self.assertRaises(ValueError):
            position_range("2019-01", "2018-01")


class MergeRanges(unittest.TestCase):
    def test_overlapping_roles_are_merged_not_summed(self):
        # The spec's worked example: 2018-01..2021-12 and 2020-06..2023-06.
        # Naive sum is 48 + 37 = 85 months. Merged is 2018-01..2023-06 = 66.
        ranges = [position_range("2018-01", "2021-12"), position_range("2020-06", "2023-06")]
        merged = merge_ranges(ranges)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].start, (2018, 1))
        self.assertEqual(merged[0].end, (2023, 6))
        self.assertEqual(total_months(ranges), 66)

    def test_disjoint_ranges_are_kept_apart(self):
        ranges = [position_range("2018-01", "2018-12"), position_range("2020-01", "2020-12")]
        self.assertEqual(len(merge_ranges(ranges)), 2)
        self.assertEqual(total_months(ranges), 24)

    def test_adjacent_months_are_contiguous(self):
        # Ending in Dec and starting in Jan is continuous employment, one range.
        ranges = [position_range("2018-01", "2018-12"), position_range("2019-01", "2019-06")]
        self.assertEqual(len(merge_ranges(ranges)), 1)
        self.assertEqual(total_months(ranges), 18)

    def test_a_one_month_gap_is_a_gap(self):
        ranges = [position_range("2018-01", "2018-12"), position_range("2019-02", "2019-06")]
        self.assertEqual(len(merge_ranges(ranges)), 2)
        self.assertEqual(total_months(ranges), 17)

    def test_fully_contained_range_adds_nothing(self):
        ranges = [position_range("2018-01", "2023-12"), position_range("2020-01", "2020-06")]
        self.assertEqual(total_months(ranges), 72)

    def test_three_way_chain(self):
        ranges = [
            position_range("2018-01", "2019-06"),
            position_range("2019-01", "2020-06"),
            position_range("2020-01", "2021-06"),
        ]
        self.assertEqual(len(merge_ranges(ranges)), 1)
        self.assertEqual(total_months(ranges), 42)

    def test_empty(self):
        self.assertEqual(merge_ranges([]), [])
        self.assertEqual(total_months([]), 0)

    def test_order_does_not_matter(self):
        a = [position_range("2020-06", "2023-06"), position_range("2018-01", "2021-12")]
        self.assertEqual(total_months(a), 66)

    def test_merged_output_is_approximate_if_any_input_was(self):
        ranges = [position_range("2018", "2021-12"), position_range("2020-06", "2023-06")]
        self.assertTrue(merge_ranges(ranges)[0].approximate)


class YearsRendering(unittest.TestCase):
    def test_months_to_years_is_one_decimal(self):
        self.assertEqual(months_to_years(66), 5.5)
        self.assertEqual(months_to_years(12), 1.0)
        self.assertEqual(months_to_years(0), 0.0)
        self.assertEqual(months_to_years(50), 4.2)

    def test_range_is_hashable_and_comparable_for_stable_output(self):
        r = Range(start=(2018, 1), end=(2018, 12), approximate=False)
        self.assertEqual(r, Range(start=(2018, 1), end=(2018, 12), approximate=False))
        self.assertEqual(sorted([position_range("2020-01", "2020-02"), r])[0], r)


class ThresholdComparison(unittest.TestCase):
    """D5: self-declared totals are ignored; comparisons use computed months."""

    def test_meets_threshold(self):
        from years import meets_threshold

        self.assertEqual(meets_threshold(66, 5), "met")
        self.assertEqual(meets_threshold(60, 5), "met")

    def test_short_of_threshold(self):
        from years import meets_threshold

        self.assertEqual(meets_threshold(47, 5), "unmet")

    def test_within_six_months_is_partial(self):
        # A near miss is a rank signal, not a clean knockout: say so rather than
        # pretending the employer's parser rounds the way we do.
        from years import meets_threshold

        self.assertEqual(meets_threshold(55, 5), "partial")
        self.assertEqual(meets_threshold(54, 5), "unmet")

    def test_approximate_dates_never_upgrade_a_miss(self):
        from years import meets_threshold

        self.assertEqual(meets_threshold(47, 5, approximate=True), "partial")
        self.assertEqual(meets_threshold(66, 5, approximate=True), "met")


if __name__ == "__main__":
    unittest.main(verbosity=2)
