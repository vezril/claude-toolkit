#!/usr/bin/env python3
"""Calibrate the graders against hand-labelled outputs. Run before any eval run.

For every fixture: the good output passes every criterion, and each bad output
fails exactly the criteria it declares and passes the rest. If this does not
hold, the suite's numbers mean nothing yet, so this runs first and is cheap.

    python3 evals/application-reviewer/calibration/run.py
    python3 evals/application-reviewer/calibration/run.py -v   # show reasons

Standard library only, and no model calls.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import fixtures as F  # noqa: E402
from grade import BASELINE_METRICS, CERTIFIED, CRITERIA, grade  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="calibration/run.py")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    # Only the certified criteria are calibrated against these fixtures. The
    # baseline-arm measurements (coverage, no_score) are about prose the naive
    # prompt produces, and a correctly-refused case legitimately mentions no
    # requirements at all, so holding them to the same fixtures would mean
    # labelling failures that carry no information. They get their own
    # fixtures below.
    criteria = CERTIFIED

    failures: list[str] = []
    checks = 0

    for cid, fixture in F.FIXTURES.items():
        print(f"\n=== {cid}")

        result = grade(cid, fixture["good"])
        for name in criteria:
            checks += 1
            ok = result[name]["pass"]
            print(f"  good / {name:9} {'pass' if ok else 'FAIL'}")
            if not ok:
                failures.append(f"{cid} good: {name} should pass but failed: {result[name]['reason']}")
            elif args.verbose:
                print(f"      {result[name]['reason']}")

        for bad in fixture["bad"]:
            must_fail = set(bad["fails"])
            unknown = must_fail - set(criteria)
            if unknown:
                failures.append(f"{cid} {bad['label']}: unknown criteria {sorted(unknown)}")
            result = grade(cid, bad["text"])
            verdicts = []
            for name in criteria:
                checks += 1
                failed = not result[name]["pass"]
                expected_fail = name in must_fail
                mark = "ok" if failed == expected_fail else "WRONG"
                verdicts.append(f"{name}={'fail' if failed else 'pass'}({mark})")
                if failed != expected_fail:
                    if expected_fail:
                        failures.append(
                            f"{cid} {bad['label']!r}: {name} should have failed and passed"
                        )
                    else:
                        failures.append(
                            f"{cid} {bad['label']!r}: {name} should have passed and failed: "
                            f"{result[name]['reason']}"
                        )
                elif args.verbose and failed:
                    print(f"      {name}: {result[name]['reason']}")
            print(f"  bad  / {bad['label']}: " + " ".join(verdicts))

    # The prose measurements, calibrated on prose.
    print("\n=== baseline measurements (prose)")
    for label, text, must_fail in F.PROSE_FIXTURES:
        result = grade("case-01-clean", text)
        verdicts = []
        for name in BASELINE_METRICS:
            checks += 1
            failed = not result[name]["pass"]
            expected_fail = name in must_fail
            mark = "ok" if failed == expected_fail else "WRONG"
            verdicts.append(f"{name}={'fail' if failed else 'pass'}({mark})")
            if failed != expected_fail:
                failures.append(
                    f"prose {label!r}: {name} should have "
                    f"{'failed' if expected_fail else 'passed'}: {result[name]['reason']}"
                )
        print(f"  {label}: " + " ".join(verdicts))

    print(f"\n{checks} checks")
    if failures:
        print(f"\n{len(failures)} calibration failure(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("calibration holds: the criteria fire where they should and nowhere else")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
