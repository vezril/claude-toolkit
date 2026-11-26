#!/usr/bin/env python3
"""The verify step: run the repo's tests and the protected-path check, emit `verify.json`.

Usage:
    run-verify.py <ITEM-KEY> --story <path> [--repo <path>] [--json] [--dry-run]
                  [--test <name>:<ac,ac> ...] [--mutation | --no-mutation] [--base <ref>]

`verify` was `kind: build` in the routing table with **nothing behind it**. Four things read
`verify.json` — `decide.py`, the `review` and `post-summary` prompts, `vault-update` — and
nothing wrote it, so the edge check on it could never fire and a `full` run could not get past
this step. This is the producer.

**A script, not a node.** Running a test command and diffing paths are mechanical; there is no
judgement to certify, and a deterministic producer reports facts by construction rather than
because a prompt was told to.

The one thing it cannot derive is which acceptance criteria each test covers. That mapping is
the dev pair's claim about its own work, passed in with `--test`, and it is what the P0/P1
scope edge checks — so it is recorded here and judged there, rather than being trusted by the
step that asserts it.

It also runs the **mutation gate** (`mutation-gate.py`), when the repo enables it. A green
suite says the tests pass; it does not say the tests would fail if the code were wrong. The
gate breaks the production lines this branch changed and records which ones no test noticed —
a review comment on a client PR put it as *"making it unconditional still passes"*, and that
is a measurement rather than an opinion, so it belongs in this script and not in a prompt.

Exit codes: 0 verify.json written (whatever the suite did), 1 the artifact could not be
written, 2 a usage error. **A red suite is a successful verify**: the step's job is to report
what happened, and the edge and the reviewer decide what it means. The same holds for surviving
mutants — they are recorded, not fatal here.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common  # noqa: E402

ARTIFACT = "verify.json"
TEST_TIMEOUT = 1800


def run_suite(repo: Path, command: str) -> dict:
    """Run the configured test command. A command that cannot start is `not-run`, not `red`.

    Those are different claims: a failing suite says something about the code, a suite that
    never started says nothing at all. Collapsing them would let a missing `test_command` read
    as a failing build, which is the flattering direction.
    """
    if not command:
        return {"status": "not-run", "exit_code": -1,
                "summary": "no test_command is configured, so no suite ran; this is not a "
                           "statement that the tests pass"}
    try:
        out = subprocess.run(command, shell=True, cwd=str(repo), capture_output=True,
                             text=True, timeout=TEST_TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"status": "not-run", "exit_code": -1,
                "summary": f"the suite did not finish within {TEST_TIMEOUT}s and was killed, "
                           "so its result is unknown"}
    except OSError as e:
        return {"status": "not-run", "exit_code": -1,
                "summary": f"the test command could not be started: {e}"}

    tail = ((out.stdout or "") + (out.stderr or "")).strip().splitlines()
    return {"status": "green" if out.returncode == 0 else "red",
            "exit_code": out.returncode,
            "summary": " / ".join(tail[-3:])[:400] or "(no output)"}


def run_protected(repo: Path, cfg: dict) -> tuple:
    """(checked, violations). An unrunnable check is `checked: False`, never an empty pass.

    `check-protected-paths.py` already refuses to pass by absence on an empty policy block;
    this preserves that distinction upward, so `protected_paths_checked: false` with no
    violations cannot be read as "nothing was touched".
    """
    policy = repo / common.CONFIG_NAME
    if not policy.exists():
        return False, []
    base = (cfg.get("forge") or {}).get("base") or "main"
    script = HERE.parent / "check-protected-paths.py"
    if not script.exists():
        return False, []
    out = subprocess.run([sys.executable, "-I", str(script), "--policy", str(policy),
                          "--base", base, "--repo", str(repo)],
                         capture_output=True, text=True)
    # Exit 2 is the script's "refusing to pass by absence" — an unusable policy, which is not a
    # clean result and must not be recorded as one.
    if out.returncode == 2:
        return False, []
    said = ((out.stdout or "") + (out.stderr or "")).strip()
    if out.returncode == 0:
        return True, []
    return True, [l.strip(" -") for l in said.splitlines() if l.strip()][:20]


def run_mutation(repo: Path, cfg: dict, enabled, base_override) -> dict:
    """Break the diff's own production lines and see whether its tests notice.

    Opt-in, because it runs the test subset once per mutant and that cost belongs to the
    repository that chose it. Disabled is recorded as `ran: false` with a reason rather than
    omitted — a missing field reads as "clean", which is the flattering direction and the
    mistake this script was written to stop making about `protected_paths_checked`.
    """
    opts = cfg.get("mutation") or {}
    if enabled is None:
        enabled = bool(opts.get("enabled"))
    if not enabled:
        return {"ran": False, "reason": "mutation gate not enabled (mutation.enabled in "
                                        f"{common.CONFIG_NAME}, or --mutation)"}
    script = HERE / "mutation-gate.py"
    if not script.exists():
        return {"ran": False, "reason": f"{script.name} is missing"}
    cmd = [sys.executable, "-I", str(script), "--repo", str(repo), "--json"]
    base = base_override or (cfg.get("forge") or {}).get("base")
    if base:
        cmd += ["--base", base]
    for key, flag in (("subset_template", "--subset-template"),
                      ("max_mutants", "--max-mutants"), ("timeout", "--timeout")):
        if opts.get(key) not in (None, ""):
            cmd += [flag, str(opts[key])]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(out.stdout)
    except (ValueError, TypeError):
        return {"ran": False,
                "reason": "the mutation gate produced no readable result: "
                          + ((out.stderr or out.stdout or "").strip()[:200] or "(no output)")}


def parse_tests(pairs) -> list:
    """`--test name:1,2` -> {"name": …, "covers": ["1", "2"]}."""
    tests = []
    for raw in pairs or []:
        if ":" not in raw:
            raise ValueError(f"--test needs <name>:<ac,ac>, got {raw!r}")
        name, acs = raw.split(":", 1)
        covers = [a.strip().removeprefix("AC-") for a in acs.split(",") if a.strip()]
        if not name.strip() or not covers:
            raise ValueError(f"--test needs a name and at least one AC, got {raw!r}")
        tests.append({"name": name.strip(), "covers": covers})
    return tests


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--story", required=True,
                    help="repo-relative path to the story; the scope edge resolves AC "
                         "priorities from it")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--test", action="append", default=[], metavar="NAME:AC,AC",
                    help="a test and the acceptance criteria it covers; repeatable")
    ap.add_argument("--mutation", dest="mutation", action="store_true", default=None,
                    help="run the mutation gate regardless of the config")
    ap.add_argument("--no-mutation", dest="mutation", action="store_false",
                    help="skip it regardless of the config")
    ap.add_argument("--base", default=None,
                    help="base ref for the mutation gate's diff; defaults to forge.base")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    repo = common.repo_root(Path(args.repo).resolve())
    if not (repo / common.CONFIG_NAME).exists():
        print(f"{repo} is not a delivery-flow repo (no {common.CONFIG_NAME})", file=sys.stderr)
        return 2
    cfg = common.load_config(repo) or {}

    if not (repo / args.story).exists():
        print(f"the story does not exist: {args.story}", file=sys.stderr)
        return 2
    try:
        tests = parse_tests(args.test)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    item_dir = common.artifact_root(repo) / args.item
    if not item_dir.exists():
        print(f"no run directory for {args.item} at {item_dir}", file=sys.stderr)
        return 2

    suite = run_suite(repo, cfg.get("test_command") or "")
    checked, violations = run_protected(repo, cfg)
    mutation = run_mutation(repo, cfg, args.mutation, args.base)

    # Field names follow the artifacts the step already produced in the field, not names
    # invented from the prompt descriptions. `test_command`, `passed` and `status` existed; a
    # first version of this script used `command` and `suite` instead and its schema rejected
    # all eight real artifacts, blocking their edges.
    doc = {"item": args.item, "story": args.story,
           "test_command": {"command": cfg.get("test_command") or "(none configured)",
                            "source": ".delivery-flow.yaml test_command",
                            "exit_code": suite["exit_code"],
                            "status": suite["status"],
                            "summary": suite["summary"]},
           "passed": suite["status"] == "green",
           "status": suite["status"],
           "tests": tests,
           "protected_paths_checked": checked, "protected_violations": violations,
           "mutation": mutation}

    if args.json:
        print(json.dumps(doc, indent=2))
    if args.dry_run:
        return 0

    (item_dir / ARTIFACT).write_text(json.dumps(doc, indent=2) + "\n")
    sentinel = subprocess.run(
        [sys.executable, "-I", str(HERE / "write-sentinel.py"),
         str(item_dir / ARTIFACT), "--step", "verify"],
        cwd=str(repo), capture_output=True, text=True)

    if not mutation.get("ran"):
        mut = f"mutation NOT run ({mutation.get('reason', 'no reason given')})"
    else:
        survived = mutation.get("survived") or []
        mut = (f"mutation {mutation.get('killed', 0)}/{mutation.get('mutants', 0)} killed"
               + (f", {len(survived)} SURVIVED" if survived else ""))
    print(f"wrote {ARTIFACT}: suite {suite['status']}, {len(tests)} test(s), "
          f"protected {'checked' if checked else 'NOT checked'}"
          + (f", {len(violations)} violation(s)" if violations else "")
          + f", {mut}")
    if sentinel.returncode != 0:
        print((sentinel.stdout or "") + (sentinel.stderr or ""), file=sys.stderr)
        return 1
    # Deliberately 0 on a red suite: the step reported what happened, which is its whole job.
    # The edge checks the scope and the reviewer judges the result.
    return 0


if __name__ == "__main__":
    sys.exit(main())
