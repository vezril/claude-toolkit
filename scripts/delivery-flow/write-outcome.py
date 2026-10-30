#!/usr/bin/env python3
"""The report step: close an item out with `outcome.json`.

Usage:
    write-outcome.py <ITEM-KEY> [--repo <path>] [--status abandoned --reason <text>]
                     [--json] [--dry-run]

A profile does not finish by running out of steps — that is indistinguishable from stalling.
It finishes when this script writes a terminal artifact saying how it ended:

  completed    every non-skipped step before the terminus produced an artifact whose edge passed
  punched-out  a human holds an unresolved decision; the system worked, the run stopped
  failed       an edge is still failing, or an artifact was corrected by hand
  abandoned    a human called it off (`--status abandoned`, which is the only status this
               script will take on trust)

**Manual-correction detection.** Stage 4 counts a hand-edited artifact as a failed run, not a
repair: a pipeline whose number depends on quiet fixes has no number. Every edge record in the
trace carries the sha256 of the bytes it ran over, so an artifact whose current sha differs
from the last one traced was changed after its check — and the run is `failed` with reason
`manual-correction`, however good the artifact now looks.

Exit codes: 0 written, 2 not a delivery-flow repo / no such item / nothing to report yet.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONFIG_NAME, artifact_root, is_delivery_repo, load_config, load_json,  # noqa: E402
                    load_profiles, open_punch_outs, repo_root, select_profile, sha256)

HERE = Path(__file__).resolve().parent
OUTCOME = "outcome.json"

# Kept in step with flow-status.py: a bug or a task gets no breakdown and no challenge of it.
QUICK_PATH_SKIPS = {"breakdown", "challenge-breakdown"}


def read_trace(item_dir: Path) -> list:
    path = item_dir / "trace.jsonl"
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def traced_state(trace: list) -> tuple:
    """(last traced sha per artifact, latest edge per artifact)."""
    shas, edges = {}, {}
    for rec in trace:
        artifact = rec.get("artifact")
        if not artifact:
            continue
        if rec.get("sha256"):
            shas[artifact] = rec["sha256"]
        if rec.get("edge"):
            edges[artifact] = rec["edge"]
    return shas, edges


def manual_corrections(item_dir: Path, shas: dict) -> list:
    """Artifacts whose bytes changed after the edge that last checked them.

    Only artifacts the trace has a sha for are checkable. One written before this detection
    existed, or by a path that bypassed the hook, is not evidence of innocence — it is a gap,
    and `--json` reports it as `unverifiable` so it cannot be mistaken for a clean run.
    """
    found = []
    for artifact, traced in sorted(shas.items()):
        path = item_dir / artifact
        if not path.exists():
            continue
        actual = sha256(path)
        if actual != traced:
            found.append({"artifact": artifact, "traced_sha256": traced, "actual_sha256": actual})
    return found


def classify(item_dir: Path, rows: list, has_vault: bool, path_kind, shas: dict, edges: dict) -> tuple:
    """(status, reason, step) for the item as it stands."""
    corrections = manual_corrections(item_dir, shas)
    if corrections:
        names = ", ".join(c["artifact"] for c in corrections)
        return "failed", f"manual-correction: {names} changed after its edge ran", "report"

    punch_outs = open_punch_outs(item_dir)
    if punch_outs:
        p = punch_outs[0]
        return "punched-out", f"{p['punch_out']} ({p['trigger']}) is {p['state']}", "report"

    for artifact, step, _kind, optional_when in rows:
        if artifact == OUTCOME:
            continue
        skipped = (optional_when == "vault" and not has_vault) or \
                  (path_kind == "quick" and step in QUICK_PATH_SKIPS)
        if skipped:
            continue
        if not (item_dir / artifact).exists():
            return None, f"{artifact} has not been produced, so {step} has not run", step
        if (edges.get(artifact) or {}).get("exit"):
            return "failed", f"{artifact} is failing its edge: {edges[artifact].get('summary', '')[:160]}", step

    return "completed", None, "report"



def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--status", choices=["abandoned"],
                    help="only `abandoned` may be asserted; every other status is derived")
    ap.add_argument("--reason", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo))
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo: no {CONFIG_NAME} at its root", file=sys.stderr)
        return 2
    item_dir = artifact_root(repo) / args.item
    if not item_dir.is_dir():
        print(f"no such item: {args.item}", file=sys.stderr)
        return 2

    cfg = load_config(repo)
    try:
        profiles = load_profiles()
    except (OSError, ValueError) as e:
        print(f"could not read profiles.yaml: {e}", file=sys.stderr)
        return 2
    profile, err = select_profile(cfg, profiles)
    if err:
        print(err, file=sys.stderr)
        return 2

    sys.path.insert(0, str(HERE))
    import importlib.util
    spec = importlib.util.spec_from_file_location("flow_status", HERE / "flow-status.py")
    flow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flow)
    rows, rows_err = flow.profile_steps(profile)
    if rows_err:
        print(rows_err, file=sys.stderr)
        return 2

    has_vault = bool((cfg.get("vault") or {}).get("binding"))
    triage, _ = load_json(item_dir / "triage.json")
    path_kind = (triage or {}).get("path")

    trace = read_trace(item_dir)
    shas, edges = traced_state(trace)
    corrections = manual_corrections(item_dir, shas)

    if args.status == "abandoned":
        status, reason, step = "abandoned", args.reason or "called off by a human", "report"
    else:
        status, reason, step = classify(item_dir, rows, has_vault, path_kind, shas, edges)
        if status is None:
            print(f"nothing to report yet: {reason}", file=sys.stderr)
            return 2

    unverifiable = sorted(a for a, _step, _kind, _opt in rows
                          if a != OUTCOME and (item_dir / a).exists() and a not in shas)

    doc = {"item": args.item, "profile": profile.get("profile"), "status": status,
           "reason": reason, "step": step,
           "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "manual_corrections": corrections}

    if args.json:
        print(json.dumps({**doc, "unverifiable": unverifiable}, indent=2))
    if args.dry_run:
        return 0

    path = item_dir / OUTCOME
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    out = subprocess.run([sys.executable, "-I", str(HERE / "write-sentinel.py"),
                          str(path), "--step", "report"], capture_output=True)
    if out.returncode != 0:
        print((out.stderr or b"").decode().strip() or "could not write the sentinel", file=sys.stderr)
        return 2

    if not args.json:
        print(f"{args.item}: {status}" + (f" — {reason}" if reason else ""))
        for u in unverifiable:
            print(f"  warning: {u} has no sha in the trace, so a hand-edit of it is undetectable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
