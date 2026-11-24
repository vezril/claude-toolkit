#!/usr/bin/env python3
"""Grade one test-writer run, by execution rather than by reading its prose.

Usage:
    grade.py <case> --work <dir> [--json]

The `implementation` step of the sdlc pipeline is the test-writer: the RED half of the dev
pair. Its output is **test source code**, not a structured document, so keyword matching would
measure almost nothing. What it says about its own work is also the weakest possible evidence —
the step's own instruction 3 is "run it and confirm it fails for the expected reason", so the
eval holds it to the same standard and runs the tests itself.

Four criteria, all deterministic:

  territory   it created or edited ONLY test files. The hard rule in `agents/test-writer.md`,
              and the one a hook already enforces in production — so a suite that did not check
              it would be scoring a weaker bar than the flow does.
  red         the suite fails now, and fails on an assertion rather than on a collection or
              import error. "It failed" is not enough: a syntax error also fails, and a test
              that cannot run guards nothing.
  green       the SAME tests pass once the reference implementation is applied. This is the
              criterion that catches a test guarding nothing — one that passes against the
              unfixed code, or that fails even against correct code because it asserts the
              wrong thing. Nothing else in the suite can catch either.
  scope       every P0/P1 acceptance criterion has a test and nothing below P1 does, read from
              the story the same way `check-test-scope.py` reads it in production.

`green` is why `hidden/` exists: the reference never sits in the fixture, so the agent cannot
read the answer, and it is applied only after the agent has finished.

Exit codes: 0 graded (whatever the scores), 2 a usage or setup error. A criterion that could
not be evaluated scores 0 with the reason, never a pass.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST_DIRS = ("tests/", "test/", "spec/", "__tests__/")
TIMEOUT = 300

AC_RE = re.compile(r"^[-*]\s+AC-(\d+)\s*(?:\(\s*(P[0-3])\s*\))?\s*:?\s*(.*)$")
IN_SCOPE = ("P0", "P1")


def run(cmd, cwd, timeout=TIMEOUT):
    try:
        return subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        class R:
            returncode, stdout, stderr = -1, "", f"timed out after {timeout}s"
        return R()


def is_test_path(rel: str) -> bool:
    return any(rel.startswith(d) or f"/{d}" in f"/{rel}" for d in TEST_DIRS)


def changed(pristine: Path, work: Path) -> dict:
    """{added, modified} relative paths, by comparing the work tree against the pristine one."""
    added, modified = [], []
    for p in sorted(work.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.name.endswith(".pyc"):
            continue
        rel = str(p.relative_to(work))
        ref = pristine / rel
        if not ref.exists():
            added.append(rel)
        elif ref.read_bytes() != p.read_bytes():
            modified.append(rel)
    return {"added": added, "modified": modified}


def ac_priorities(story: Path) -> dict:
    out, inside = {}, False
    if not story.exists():
        return out
    for line in story.read_text().splitlines():
        if line.strip().lower().startswith("## "):
            inside = "acceptance criteria" in line.strip().lower()
            continue
        if inside:
            m = AC_RE.match(line.strip())
            if m:
                out[int(m.group(1))] = m.group(2)
    return out


def referenced_acs(work: Path, token: str = "AC-") -> dict:
    """{id: [files]} from `<token><n>` mentions in the test files, so the mapping is read off
    the tests rather than taken from a claim the step makes about them.

    `token` because the two entry points name their criteria differently: a story has
    `AC-1`, a `proposal.json` has tasks `T1`. Reading only one shape made the proposal case
    report every criterion uncovered.
    """
    out = {}
    for p in work.rglob("*"):
        if not p.is_file() or not is_test_path(str(p.relative_to(work))):
            continue
        try:
            text = p.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        pattern = r"\bAC-(\d+)\b" if token == "AC-" else r"\bT(\d+)\b"
        for n in set(int(m) for m in re.findall(pattern, text)):
            out.setdefault(n, []).append(str(p.relative_to(work)))
    return out


def grade(case: str, work: Path, reply: str = "") -> dict:
    pristine = HERE / "fixture" / case
    if not pristine.exists():
        return {"error": f"no fixture for {case}"}
    expected_path = HERE / "expected" / f"{case}.json"
    exp = json.loads(expected_path.read_text()) if expected_path.exists() else {}

    diff = changed(pristine, work)
    scores, reasons = {}, {}

    # --- territory -----------------------------------------------------------------
    touched = diff["added"] + diff["modified"]
    offenders = [r for r in touched if not is_test_path(r)]
    scores["territory"] = 0 if offenders else 1
    reasons["territory"] = (f"edited non-test files: {', '.join(offenders)}" if offenders
                            else f"only test files touched ({len(touched)} file(s))")

    # Some cases are *supposed* to produce a hand-back instead of a test, because the change
    # cannot be tested without a production seam. There, writing no test is correct.
    if exp.get("expect_handback"):
        wrote_tests = [r for r in touched if is_test_path(r)]
        ok = not offenders and not wrote_tests
        scores["territory"] = 1 if ok else 0
        reasons["territory"] = ("handed back without editing anything, which is correct here"
                                if ok else
                                f"should have handed back; touched {', '.join(touched) or 'nothing'}")
        # The remaining three criteria do not apply to a hand-back: there is no test to run.
        for k in ("red", "green", "scope"):
            scores[k] = 1 if ok else 0
            reasons[k] = ("not applicable: the correct output here is a hand-back, not a test"
                          if ok else "no hand-back, so there is nothing valid to grade")
        return {"case": case, "scores": scores, "reasons": reasons, "changed": diff}

    cmd = exp.get("test_command", "python3 -m pytest -q")

    # --- red -----------------------------------------------------------------------
    before = run(cmd, work)
    out_before = (before.stdout or "") + (before.stderr or "")
    collection_error = bool(re.search(r"error|ERROR|SyntaxError|ImportError|ModuleNotFound",
                                      out_before)) and "assert" not in out_before.lower()
    if before.returncode == 0:
        scores["red"] = 0
        reasons["red"] = ("the suite passes against the unfixed code, so the hand-off is green: "
                          "nothing it wrote fails for the behaviour the story asks for")
    elif collection_error:
        scores["red"] = 0
        reasons["red"] = ("the suite fails to collect or import rather than on an assertion; a "
                          "test that cannot run guards nothing")
    else:
        scores["red"] = 1
        reasons["red"] = "the suite fails on an assertion, as a red hand-off should"

    # --- green (apply the reference, rerun the SAME tests) --------------------------
    ref = HERE / "hidden" / f"{case}.py"
    target = exp.get("reference_target")
    if not ref.exists() or not target:
        scores["green"] = 0
        reasons["green"] = (f"no reference implementation for {case}, so whether the test "
                            "actually guards the behaviour cannot be checked")
    else:
        backup = (work / target).read_bytes() if (work / target).exists() else None
        try:
            (work / target).write_bytes(ref.read_bytes())
            after = run(cmd, work)
            if after.returncode == 0:
                scores["green"] = 1
                reasons["green"] = "the same tests pass once the reference fix is applied"
            else:
                tail = ((after.stdout or "") + (after.stderr or "")).strip().splitlines()
                scores["green"] = 0
                reasons["green"] = ("still failing against the reference implementation, so the "
                                   f"test asserts the wrong thing: {' / '.join(tail[-2:])[:200]}")
        finally:
            if backup is not None:
                (work / target).write_bytes(backup)

    # --- scope ---------------------------------------------------------------------
    # Instruction 16: on the delivery-flow entry point the criteria live in `proposal.json`,
    # not in a story file. Priorities are read out of the task descriptions there, since that
    # is where that shape records them.
    if exp.get("criteria_source") == "proposal.json":
        priorities = {}
        doc, err = None, None
        try:
            doc = json.loads((work / "proposal.json").read_text())
        except (OSError, json.JSONDecodeError) as e:
            err = str(e)
        if doc:
            for i, task in enumerate(doc.get("tasks") or [], start=1):
                m = re.search(r"\(P([0-3])\)", task.get("description") or "")
                priorities[i] = f"P{m.group(1)}" if m else None
    else:
        priorities = ac_priorities(work / "story.md")
    covered = referenced_acs(
        work, token="T" if exp.get("criteria_source") == "proposal.json" else "AC-")
    if not priorities:
        scores["scope"] = 0
        reasons["scope"] = "the story declares no AC priorities, so no scope could be checked"
    else:
        problems = []
        for ac, prio in sorted(priorities.items()):
            label = "T" if exp.get("criteria_source") == "proposal.json" else "AC-"
            if prio in IN_SCOPE and ac not in covered:
                problems.append(f"{label}{ac} is {prio} and no test names it")
        for ac, files in sorted(covered.items()):
            prio = priorities.get(ac)
            if prio and prio not in IN_SCOPE:
                label = "T" if exp.get("criteria_source") == "proposal.json" else "AC-"
                problems.append(f"{label}{ac} is {prio}, below the P1 scope, but tested in "
                                f"{', '.join(files)}")
        # Instruction 15: a disputed priority is REPORTED, not acted on. Where a case plants
        # one, the agent must leave the criterion untested (covered above, since it is below
        # P1) *and* say the priority looks wrong. Writing the test anyway would be acting on
        # its own re-prioritisation, which is the failure; saying nothing leaves a story
        # everyone believes is correctly scoped.
        # Instruction 17: a WEAKENED verdict's findings are constraints this step must
        # address, not context it may note. Where a case carries one, a test has to pin it.
        carry = exp.get("expect_carry_forward")
        if carry:
            test_text = ""
            for f in work.rglob("*"):
                if f.is_file() and is_test_path(str(f.relative_to(work))):
                    try:
                        test_text += f.read_text()
                    except (OSError, UnicodeDecodeError):
                        pass
            words = [w.lower() for w in carry.get("keywords") or []]
            if not any(w in test_text.lower() for w in words):
                problems.append("the WEAKENED challenge finding is unaddressed: no test pins "
                                "the case it names")

        dispute = exp.get("expect_priority_dispute")
        if dispute:
            words = [w.lower() for w in dispute.get("keywords") or []]
            if not reply.strip():
                problems.append("no reply captured, so the disputed priority cannot be checked")
            elif not any(w in reply.lower() for w in words):
                problems.append(f"said nothing about AC-{dispute.get('ac')}'s priority, which "
                                "the story has marked below the behaviour it describes")

        scores["scope"] = 0 if problems else 1
        reasons["scope"] = "; ".join(problems) or (
            f"covers {sorted(a for a, p in priorities.items() if p in IN_SCOPE)} and nothing below P1"
            + (", and reported the disputed priority" if exp.get("expect_priority_dispute") else ""))

    return {"case": case, "scores": scores, "reasons": reasons, "changed": diff}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case")
    ap.add_argument("--work", required=True, help="the tree the agent worked in")
    ap.add_argument("--output-file", default=None,
                    help="the agent's reply, for the one criterion that reads what it said")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    work = Path(args.work).expanduser().resolve()
    if not work.exists():
        print(f"no such work tree: {work}", file=sys.stderr)
        return 2

    reply = ""
    if args.output_file and Path(args.output_file).exists():
        reply = Path(args.output_file).read_text()
    out = grade(args.case, work, reply)
    if out.get("error"):
        print(out["error"], file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for k in ("territory", "red", "green", "scope"):
            print(f"  {'PASS' if out['scores'].get(k) else 'FAIL'} {k:10} {out['reasons'][k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
