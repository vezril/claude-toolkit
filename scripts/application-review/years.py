#!/usr/bin/env python3
"""Years-of-experience arithmetic, the way CV parsers do it (design D5).

The rules, all of them deliberate:

  * Overlapping positions are merged, never summed. Two roles held at once are
    one stretch of calendar time, and a naive sum is the single most common way
    a CV's "years of experience" gets overstated.
  * Month counts are inclusive at both ends. Jan 2018 to Dec 2018 is twelve
    months of work.
  * Ranges that touch are contiguous: ending in December and starting in
    January is continuous employment, so it merges into one range.
  * "Present" dates to the run date, which is injectable so tests and recorded
    eval runs do not drift with the calendar.
  * A month-less year is treated as January (or December for an end) and the
    range is flagged `approximate`.
  * Self-declared totals in the CV prose ("15 years of experience") are ignored
    entirely. This module only ever sees date ranges.

This is Textkernel's documented behaviour, and it is the deterministic half of
the pipeline: S2 (the model) decides *which* positions evidence a skill, and
this module does the arithmetic on their dates.

Standard library only.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Iterable, NamedTuple

__all__ = [
    "Range",
    "merge_ranges",
    "meets_threshold",
    "months_to_years",
    "parse_month",
    "position_range",
    "total_months",
]

# A near miss on a years threshold: short by less than this many months is
# reported as `partial` rather than `unmet`. The employer's parser may round
# differently than we do, and claiming a clean knockout on a four-month gap
# would be overstating what we know.
NEAR_MISS_MONTHS = 6

_MONTHS = {
    # English, including the common abbreviations and the "Sept" that trips
    # three-letter truncation.
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12,
    "december": 12,
    # French. Accents are stripped before lookup, so these keys are unaccented.
    "janvier": 1, "fevrier": 2, "fev": 2, "mars": 3, "avril": 4, "avr": 4,
    "mai": 5, "juin": 6, "juillet": 7, "juil": 7, "aout": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "decembre": 12, "dec.": 12,
}

# Words that mean "this position has not ended".
_PRESENT = {
    "present", "current", "currently", "now", "today", "ongoing", "to date",
    "aujourdhui", "aujourd hui", "en cours", "a ce jour", "actuel",
    "actuellement", "maintenant", "ce jour",
}


def _fold(text: str) -> str:
    """Lowercase, strip accents and punctuation noise, collapse whitespace.

    Accent stripping is what lets one month table serve French and English, and
    it means "fevrier" and "février" are the same key.
    """
    s = unicodedata.normalize("NFKD", str(text))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("'", " ").replace("’", " ")
    s = re.sub(r"[,]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_month(text: str, *, end: bool = False, run_date: str | None = None) -> tuple[int, int, bool]:
    """Parse one endpoint of a date range into ``(year, month, approximate)``.

    ``end=True`` makes a bare year resolve to December instead of January, so
    that "2018" as an end date means the end of 2018.

    ``run_date`` is an ISO date string and is required to resolve "Present".
    It is a parameter rather than a call to ``date.today()`` so that tests and
    replayed eval runs give the same answer next year as they do today.

    Raises ``ValueError`` on anything it cannot read, which is deliberate: a
    silently wrong date would feed a wrong verdict.
    """
    raw = _fold(text)
    if not raw:
        raise ValueError("empty date")

    if raw in _PRESENT:
        if not run_date:
            raise ValueError(f"cannot resolve {text!r} without a run_date")
        today = date.fromisoformat(run_date)
        return (today.year, today.month, False)

    # 2018-01, 2018-01-17, 2018/01, 2018.01
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})(?:[-/.]\d{1,2})?", raw)
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        if not 1 <= month <= 12:
            raise ValueError(f"month out of range in {text!r}")
        return (year, month, False)

    # 01/2018, 1-2018
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{4})", raw)
    if m:
        month, year = int(m.group(1)), int(m.group(2))
        if not 1 <= month <= 12:
            raise ValueError(f"month out of range in {text!r}")
        return (year, month, False)

    # January 2018 / janvier 2018 / Jan. 2018 / 2018 January
    m = re.fullmatch(r"([a-z.]+)\s*(\d{4})", raw) or re.fullmatch(r"(\d{4})\s*([a-z.]+)", raw)
    if m:
        a, b = m.group(1), m.group(2)
        name, year = (a, b) if not a.isdigit() else (b, a)
        key = name.rstrip(".")
        if key in _MONTHS:
            return (int(year), _MONTHS[key], False)
        raise ValueError(f"unknown month name in {text!r}")

    # A bare year: approximate by construction.
    m = re.fullmatch(r"(\d{4})", raw)
    if m:
        return (int(m.group(1)), 12 if end else 1, True)

    raise ValueError(f"unparseable date {text!r}")


class Range(NamedTuple):
    """A half-open-free, fully inclusive month range: both endpoints count."""

    start: tuple[int, int]
    end: tuple[int, int]
    approximate: bool

    @property
    def months(self) -> int:
        return _index(self.end) - _index(self.start) + 1

    def iso(self) -> tuple[str, str]:
        return (f"{self.start[0]:04d}-{self.start[1]:02d}", f"{self.end[0]:04d}-{self.end[1]:02d}")


def _index(ym: tuple[int, int]) -> int:
    """Absolute month number, so arithmetic never worries about year borders."""
    return ym[0] * 12 + (ym[1] - 1)


def position_range(start: str, end: str, *, run_date: str | None = None) -> Range:
    """Build a ``Range`` from two raw date strings as they appear on a CV."""
    sy, sm, sa = parse_month(start, run_date=run_date)
    ey, em, ea = parse_month(end, end=True, run_date=run_date)
    if _index((ey, em)) < _index((sy, sm)):
        raise ValueError(f"end {end!r} is before start {start!r}")
    return Range(start=(sy, sm), end=(ey, em), approximate=sa or ea)


def merge_ranges(ranges: Iterable[Range]) -> list[Range]:
    """Merge overlapping and adjacent ranges into the fewest covering ranges.

    This is the step that stops concurrent roles from being double-counted.
    """
    ordered = sorted(ranges)
    if not ordered:
        return []
    merged: list[Range] = []
    cur = ordered[0]
    for nxt in ordered[1:]:
        # Adjacent (next starts the month after current ends) counts as
        # continuous, hence the +1.
        if _index(nxt.start) <= _index(cur.end) + 1:
            end = cur.end if _index(cur.end) >= _index(nxt.end) else nxt.end
            cur = Range(start=cur.start, end=end, approximate=cur.approximate or nxt.approximate)
        else:
            merged.append(cur)
            cur = nxt
    merged.append(cur)
    return merged


def total_months(ranges: Iterable[Range]) -> int:
    """Total calendar months covered, overlaps counted once."""
    return sum(r.months for r in merge_ranges(ranges))


def months_to_years(months: int) -> float:
    """Months as years to one decimal, for the report's arithmetic line."""
    return round(months / 12.0, 1)


def meets_threshold(months: int, required_years: float, *, approximate: bool = False) -> str:
    """Compare computed months against a posting's years threshold.

    Returns ``met``, ``partial`` or ``unmet``. ``approximate`` dates can never
    turn a miss into a pass; the most they do is soften an ``unmet`` to
    ``partial``, because we genuinely do not know the months.
    """
    needed = int(round(required_years * 12))
    if months >= needed:
        return "met"
    short = needed - months
    if short < NEAR_MISS_MONTHS or approximate:
        return "partial"
    return "unmet"


@dataclass(frozen=True)
class YearsReport:
    """What the report prints: the ranges, the sum, and whether it is fuzzy."""

    merged: tuple[Range, ...]
    total_months: int
    approximate: bool

    @property
    def total_years(self) -> float:
        return months_to_years(self.total_months)


def report(ranges: Iterable[Range]) -> YearsReport:
    merged = tuple(merge_ranges(ranges))
    return YearsReport(
        merged=merged,
        total_months=sum(r.months for r in merged),
        approximate=any(r.approximate for r in merged),
    )
