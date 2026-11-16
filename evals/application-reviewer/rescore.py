#!/usr/bin/env python3
"""Re-grade a recorded run with the current graders, with no model calls.

    rescore.py results/run_v1_all.json            # print
    rescore.py results/run_v1_all.json --write     # also regrade the file

Use it when a grader changes mid-series. prompt-edd requires every earlier
version to be re-scored so the progression stays comparable, and the recorded
model outputs are the evidence: only the grading moves. ``--write`` replaces
each row's gradingResult and stamps ``results.rescored`` with the time, so
score.js and anyone reading the file afterwards see the current verdicts.

It is also how a new criterion gets applied to an old run without paying for
the calls again.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from grade import CRITERIA, grade  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rescore.py")
    parser.add_argument("results")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--criteria", help="comma-separated subset; default is whatever the run recorded")
    parser.add_argument("--fails", action="store_true", help="print every failure reason")
    args = parser.parse_args(argv)

    path = Path(args.results)
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = (data.get("results") or {}).get("results") or []
    if not rows:
        print(f"{path}: no result rows", file=sys.stderr)
        return 2

    if args.criteria:
        wanted = [c.strip() for c in args.criteria.split(",")]
    else:
        recorded = []
        for row in rows:
            for comp in (row.get("gradingResult") or {}).get("componentResults") or []:
                metric = (comp.get("assertion") or {}).get("metric")
                if metric and metric not in recorded:
                    recorded.append(metric)
        wanted = recorded or list(CRITERIA)
    unknown = [c for c in wanted if c not in CRITERIA]
    if unknown:
        print(f"unknown criteria: {unknown}", file=sys.stderr)
        return 2

    summary: dict[str, dict] = {}
    for row in rows:
        provider = (row.get("provider") or {})
        label = provider.get("label") or provider.get("id") or "?"
        cid = (row.get("vars") or {}).get("case") or "?"
        output = (row.get("response") or {}).get("output")

        components = []
        for name in wanted:
            bucket = summary.setdefault(label, {}).setdefault(name, {"pass": 0, "n": 0, "fails": {}})
            bucket["n"] += 1
            if output is None:
                result = {"pass": False, "score": 0.0,
                          "reason": "no output (" + str(row.get("error") or "")[:80] + ")"}
            else:
                result = grade(cid, str(output), name)[name]
            components.append({
                "pass": result["pass"], "score": result["score"], "reason": result["reason"],
                "assertion": {"type": "javascript", "metric": name,
                              "value": f"file://asserts/{name}.js"},
            })
            if result["pass"]:
                bucket["pass"] += 1
            else:
                key = f"{cid}: {result['reason'][:220]}"
                bucket["fails"][key] = bucket["fails"].get(key, 0) + 1

        if output is not None and args.write:
            passed = all(c["pass"] for c in components)
            row["gradingResult"] = {
                "pass": passed,
                "score": sum(1 for c in components if c["pass"]) / max(1, len(components)),
                "reason": "All assertions passed" if passed
                else "; ".join(c["reason"] for c in components if not c["pass"]),
                "componentResults": components,
            }
            row["success"] = passed

    for label, metrics in summary.items():
        total = sum(m["n"] for m in metrics.values())
        passed = sum(m["pass"] for m in metrics.values())
        pct = f"{100 * passed / total:.1f}" if total else "0.0"
        print(f"\n=== {label}: {passed}/{total} ({pct}%)")
        for name, m in metrics.items():
            mpct = f"{100 * m['pass'] / m['n']:.0f}" if m["n"] else "0"
            print(f"  {name}: {m['pass']}/{m['n']} ({mpct}%)")
            if args.fails:
                for reason, count in m["fails"].items():
                    print(f"    - [x{count}] {reason}")

    if args.write:
        data.setdefault("results", {}).setdefault("rescored", datetime.now(timezone.utc).isoformat())
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nrewrote {path} with the current grading")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
