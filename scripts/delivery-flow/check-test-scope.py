#!/usr/bin/env python3
"""Edge check for `verify.json`: the tests cover P0/P1 and nothing below.

Usage:
    check-test-scope.py <verify.json> [--repo <path>]

Declared in `skills/delivery-flow/workflow.yaml` under `edge_checks`, so `hooks/check-edge.py`
runs it when `verify.json` is written. Exposes `problems(path, repo) -> (problems, info)`, the
same contract `validate-proposal.py` and `readiness-gate.py` have.

**Both directions, and the second one is the point.** An uncovered P0 is a coverage failure
anyone would catch. Thirty tests for P3 criteria is the actual complaint this change exists to
answer, and nothing noticed it before — a suite only ever gets checked for being too small.

A story whose criteria carry no priorities is the older format: there is no declared scope, so
there is nothing to check in either direction and this returns no problems. That is not a pass
for "the scope is right", it is the honest answer that no scope was declared — and it is why
delivery-flow's verify step passes `lint-story.py --require-priority`, which refuses the
unprioritised story before it ever reaches here.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common  # noqa: E402

# `- AC-1 (P0): …` — kept in step with AC_ITEM_RE in scripts/lint-story.py. Both read the same
# normative format in skills/spec-driven-development/references/story-schema.md.
AC_RE = re.compile(r"^[-*]\s+AC-(\d+)\s*(?:\(\s*(P[0-3])\s*\))?\s*:?\s*(.*)$")

IN_SCOPE = ("P0", "P1")


def ac_priorities(story_text: str) -> dict:
    """`{ac_id: priority|None}` from a story's Acceptance Criteria section."""
    out, in_section = {}, False
    for line in story_text.splitlines():
        if line.strip().lower().startswith("## "):
            in_section = "acceptance criteria" in line.strip().lower()
            continue
        if not in_section:
            continue
        m = AC_RE.match(line.strip())
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def covered_acs(verify: dict) -> dict:
    """`{ac_id: [test names]}` from verify.json's `tests[]`.

    Each test may name several criteria it pins. One test covering two P0 behaviours counts for
    both — demanding a test per criterion would force duplicates that make the diff bigger,
    which is the thing this whole change is bounding.
    """
    out = {}
    for t in verify.get("tests") or []:
        name = t.get("name") or t.get("test") or "?"
        for ac in t.get("covers") or []:
            try:
                out.setdefault(int(str(ac).lstrip("AC-").lstrip("ac-")), []).append(name)
            except (TypeError, ValueError):
                continue
    return out


def problems(path: Path, repo: Path):
    """(problems, info) — the edge-check contract."""
    doc, err = common.load_json(Path(path))
    if err:
        return [err], {}

    story_rel = doc.get("story")
    if not story_rel:
        # No story reference means nothing to check against. Reported as info rather than a
        # problem: `verify.json` has never been required to name one, and turning that into a
        # failure here would block every existing run on a field they do not write.
        return [], {"test_scope": "verify.json names no story; no scope to check"}

    story = Path(repo) / story_rel
    if not story.exists():
        return [f"verify.json names a story that does not exist: {story_rel}"], {}

    priorities = ac_priorities(story.read_text())
    if not priorities:
        return [], {"test_scope": f"{story_rel} declares no acceptance criteria"}
    if not any(priorities.values()):
        return [], {"test_scope": (f"{story_rel} carries no AC priorities (older format), so "
                                   "no test scope is declared to check")}

    covered = covered_acs(doc)
    found = []

    # Direction 1: every in-scope criterion has a test.
    for ac, prio in sorted(priorities.items()):
        if prio in IN_SCOPE and ac not in covered:
            found.append(f"AC-{ac} is {prio} and no test covers it")

    # Direction 2: nothing below P1 was tested. This is the direction that bounds the diff.
    for ac, tests in sorted(covered.items()):
        prio = priorities.get(ac)
        if prio is None:
            found.append(f"a test covers AC-{ac}, which the story does not declare: "
                         f"{', '.join(sorted(set(tests)))}")
        elif prio not in IN_SCOPE:
            found.append(f"AC-{ac} is {prio}, below the P1 scope, but "
                         f"{len(set(tests))} test(s) cover it: {', '.join(sorted(set(tests)))}")

    info = {"test_scope": {
        "in_scope": sorted(a for a, p in priorities.items() if p in IN_SCOPE),
        "out_of_scope": sorted(a for a, p in priorities.items() if p and p not in IN_SCOPE),
        "covered": sorted(covered),
    }}
    return found, info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("artifact")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)

    found, info = problems(Path(args.artifact), common.repo_root(Path(args.repo).resolve()))
    for p in found:
        print(f"  - {p}")
    if info:
        print(json.dumps(info, indent=2))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
