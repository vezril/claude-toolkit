#!/usr/bin/env python3
"""The last gate before a Stage 4 submission: can this be submitted, and on what evidence?

Usage:
    check-submission.py [--repo <path>] [--json] [--min-runs N]

One command answering one question, over every criterion the certification examines. Run it
from the delivery repo.

**Why this exists.** `package-evidence.py` assembles the package and gates only on the chain
being certified. Asked to build with the Stage 4 figure reading `—`, it produced five populated
directories, a 3,123-entry manifest and no complaint: a package that looks finished with the
one number the certification asks for absent. That is the same defect this project has found
repeatedly — a step that is present, successful, and checking nothing — sitting on the last
thing anyone does before submitting.

So this checks the claims, not the file count:

  1. every chain step is certified, and the prompts still match their evidence
  2. the evidence package builds without a DRAFT stamp
  3. **criterion 4 has a certified-only rate at all**, on a stated denominator
  4. the runs behind it have step records, so the audit trail is real
  5. the composition of that denominator is disclosed (replays named, not padded)

Exit codes: 0 submittable, 1 not, 2 a usage or environment error. A check that cannot run is
reported as a failure, never as a pass — refusing to pass by absence is the rule every other
gate here follows.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common  # noqa: E402

# A rate over one run is arithmetic, not evidence. Not a certification requirement — the
# reviewer sets the bar — but submitting n=1 at 100% invites the obvious question, so the
# default makes that a visible warning rather than a silent pass.
DEFAULT_MIN_RUNS = 5


def _run(*args, cwd=None):
    return subprocess.run([str(a) for a in args], cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True)


def check_chain_certified() -> dict:
    out = _run(sys.executable, "-I", HERE / "check-certification.py", "--all", "--chain-only")
    said = (out.stdout or "") + (out.stderr or "")
    return {"name": "chain steps certified", "ok": out.returncode == 0,
            "detail": said.strip() or "(no output)",
            "fix": "re-run the failing step's eval suite and update its registry entry"}


def check_package_builds(repo: Path) -> dict:
    out = _run(sys.executable, "-I", HERE / "package-evidence.py", "--dry-run", cwd=repo)
    said = (out.stdout or "") + (out.stderr or "")
    draft = "DRAFT" in said
    return {"name": "evidence package builds clean",
            "ok": out.returncode == 0 and not draft,
            "detail": ("stamped DRAFT" if draft else said.strip().splitlines()[-1]
                       if said.strip() else "(no output)"),
            "fix": "fix the uncertified step the packager names"}


def _report(repo: Path):
    out = _run(sys.executable, "-I", HERE / "delivery-report.py", "--json", cwd=repo)
    if out.returncode != 0 and not (out.stdout or "").strip():
        return None, ((out.stdout or "") + (out.stderr or "")).strip()
    try:
        return json.loads(out.stdout), None
    except json.JSONDecodeError as e:
        return None, f"the report did not return JSON: {e}"


def check_criterion_4(summary: dict, min_runs: int) -> list:
    """The checks that actually decide whether there is a submission."""
    overall = ((summary or {}).get("overall") or {}).get("certified_only") or {}
    done = overall.get("completed") or 0
    failed = overall.get("failed") or 0
    punched = overall.get("punched_out") or 0
    n = done + failed + punched
    rate = overall.get("rate_excluding_punch_outs")

    checks = [{
        "name": "criterion 4 has a certified-only rate",
        "ok": n > 0 and rate is not None,
        "detail": (f"n = {n} certified terminal runs, rate "
                   f"{'—' if rate is None else f'{rate:.1f}%'}"),
        "fix": ("drive triage-profile runs from a session whose cwd IS the delivery repo — "
                "trace-step.py records only then, so runs driven from anywhere else produce "
                "no step records and cannot be certified"),
    }]

    # Only meaningful once there is a rate; reported as a warning rather than a refusal,
    # because the denominator a reviewer will accept is the reviewer's call, not this script's.
    if n:
        checks.append({
            "name": f"the denominator is at least {min_runs}",
            "ok": n >= min_runs, "warn_only": True,
            "detail": f"n = {n}",
            "fix": f"accumulate runs until n >= {min_runs}; a rate over one run is arithmetic",
        })
    return checks


def check_runs_have_step_records(summary: dict) -> dict:
    """A run with no step records cannot be certified and cannot evidence criterion 5.

    This is the failure that wasted a fortnight: three completed runs read `Certified: unknown`
    because the trace hook never fired, and nothing said so until the report was read closely.
    """
    items = (summary or {}).get("items") or []
    terminal = [r for r in items
                if r.get("status") in ("completed", "failed", "punched-out", "abandoned")]
    empty = [r["item"] for r in terminal if not r.get("steps")]
    return {"name": "every terminal run has step records",
            "ok": bool(terminal) and not empty,
            "detail": (f"{len(terminal) - len(empty)} of {len(terminal)} terminal runs have "
                       f"step records" + (f"; empty: {', '.join(empty)}" if empty else "")),
            "fix": ("those runs were driven from outside the delivery repo and are unusable — "
                    "discard them (rename DISCARDED-<KEY>) and re-run from a correctly rooted "
                    "session")}


def check_denominator_disclosed(summary: dict) -> dict:
    """Replays are countable but must be named, so a rate does not imply live work."""
    items = (summary or {}).get("items") or []
    terminal = [r for r in items
                if r.get("status") in ("completed", "failed", "punched-out", "abandoned")]
    replays = [r["item"] for r in terminal if r.get("replay")]
    return {"name": "the denominator's composition is disclosed",
            "ok": True,  # informational: the report states it either way
            "warn_only": True,
            "detail": (f"{len(replays)} of {len(terminal)} terminal runs are replays"
                       + (f" ({', '.join(replays)})" if replays else "")),
            "fix": "none needed — delivery-report states the split"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-runs", type=int, default=DEFAULT_MIN_RUNS)
    args = ap.parse_args(argv)

    repo = common.repo_root(Path(args.repo).resolve())
    if not (repo / common.CONFIG_NAME).exists():
        print(f"{repo} is not a delivery-flow repo (no {common.CONFIG_NAME}); run this from "
              f"the repo the runs live in", file=sys.stderr)
        return 2

    checks = [check_chain_certified(), check_package_builds(repo)]

    summary, err = _report(repo)
    if err:
        # Cannot read the report => cannot judge criterion 4. A failure, not a skip.
        checks.append({"name": "criterion 4 is readable", "ok": False, "detail": err,
                       "fix": "fix delivery-report.py or the artifact root it reads"})
    else:
        checks += check_criterion_4(summary, args.min_runs)
        checks.append(check_runs_have_step_records(summary))
        checks.append(check_denominator_disclosed(summary))

    blocking = [c for c in checks if not c["ok"] and not c.get("warn_only")]
    warnings = [c for c in checks if not c["ok"] and c.get("warn_only")]

    if args.json:
        print(json.dumps({"submittable": not blocking, "checks": checks}, indent=2))
    else:
        for c in checks:
            mark = "ok  " if c["ok"] else ("WARN" if c.get("warn_only") else "FAIL")
            print(f"{mark} {c['name']}")
            print(f"     {c['detail']}")
            if not c["ok"]:
                print(f"     -> {c['fix']}")
        print()
        if blocking:
            print(f"NOT SUBMITTABLE — {len(blocking)} blocking check(s) failed.")
        elif warnings:
            print(f"Submittable, with {len(warnings)} warning(s) a reviewer may raise.")
        else:
            print("Submittable.")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
