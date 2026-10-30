#!/usr/bin/env python3
"""Check the README's EDD table against skills/ on disk.

The table is the inventory of what has and has not been evaluated, so a skill
missing from it is a skill nobody will notice is untested. That drifted silently
once: 12 directories had no row (including `pr-description`, which already had a
working suite and a full iteration log) and one row, `webui-quickfix-demo`, had no
directory. The backlog figure was wrong in both directions for weeks.

Exits non-zero on any of: a skill directory with no row, a row with no directory,
or a duplicated row. Prints the current scored/blank counts either way.

Usage:  python3 scripts/check-edd-table.py [--repo <path>]
"""

import argparse
import re
import sys
from pathlib import Path


def table_rows(readme: str) -> list[tuple[str, str]]:
    """Return (skill, baseline-cell) for every row of the EDD table."""
    rows, in_table = [], False
    for line in readme.splitlines():
        if line.startswith("| Skill | EDD"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|---"):
            continue
        if not line.startswith("|"):
            if rows:
                break
            continue
        cells = line.split("|")
        m = re.match(r"\s*`([^`]+)`\s*$", cells[1]) if len(cells) > 2 else None
        if m:
            rows.append((m.group(1), cells[2].strip()))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", type=Path)
    args = ap.parse_args()

    readme = (args.repo / "README.md").read_text(encoding="utf-8")
    rows = table_rows(readme)
    if not rows:
        print("error: could not find the EDD table in README.md", file=sys.stderr)
        return 1

    named = [s for s, _ in rows]
    on_disk = sorted(p.name for p in (args.repo / "skills").iterdir() if p.is_dir())

    dupes = sorted({s for s in named if named.count(s) > 1})
    missing_row = sorted(set(on_disk) - set(named))
    missing_dir = sorted(set(named) - set(on_disk))

    scored = sum(1 for _, b in rows if b)
    blank = len(rows) - scored
    print(f"rows {len(rows)}  scored {scored}  blank {blank}  dirs {len(on_disk)}")

    problems = False
    for label, items in (
        ("skill directory with no table row", missing_row),
        ("table row with no skill directory", missing_dir),
        ("duplicated table row", dupes),
    ):
        if items:
            problems = True
            print(f"\n{len(items)} {label}:", file=sys.stderr)
            for i in items:
                print(f"  {i}", file=sys.stderr)

    if problems:
        return 1
    print("EDD table is in sync with skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
