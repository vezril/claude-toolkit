#!/usr/bin/env python3
"""Where is this item, and what runs next?

Usage:
    flow-status.py <ITEM-KEY> [--json] [--repo <path>]

The flow's position is computed from what is on disk, never from memory: which artifacts
exist, what the edge hook recorded for each of them in `trace.jsonl`, and whether any
punch-out is unresolved. The skill runs this and does what it says; it does not decide for
itself where an item has got to.

Blocking, in the order it is applied:
  1. an unresolved punch-out blocks everything;
  2. an artifact whose latest edge result failed blocks the step that consumes it, and the
     producing step reruns (at most 3 times, then a punch-out is due);
  3. otherwise the next step is the first one in the table whose artifact is missing.

Exit codes: 0 printed a status, 2 not a delivery-flow repo or no such item.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONFIG_NAME, is_delivery_repo, load_config, load_json, repo_root, sha256  # noqa: E402

MAX_RERUNS = 3

# (artifact, step, kind, optional-when) — the routing table, in order.
# "optional_when" names a config question; the step is skipped when the answer is no.
STEPS = [
    ("item.json", "intake", "adapter", None),
    ("triage.json", "triage", "node", None),
    ("project-context.json", "project-memory", "node", "vault"),
    ("breakdown.json", "breakdown", "node", None),
    ("challenge-breakdown.json", "challenge-breakdown", "node", None),
    ("spec-ready.json", "solutioning", "sdlc", None),
    ("implementation.json", "implementation", "sdlc", None),
    ("verify.json", "verify", "build", None),
    ("challenge-implementation.json", "challenge-implementation", "node", None),
    ("pr.md", "pr-description", "node", None),
    ("pr-opened.json", "open-pr", "adapter", None),
    ("post.md", "post-summary", "node", None),
    ("posted.json", "post-back", "adapter", None),
    ("outcome.json", "report", "script", None),
    ("vault-updated.json", "vault-update", "node", "vault"),
]

# Steps the quick path skips: a bug or a task gets no epic breakdown and no challenge of it.
QUICK_PATH_SKIPS = {"breakdown", "challenge-breakdown"}


def read_trace(path: Path) -> list:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # a torn line is not a reason to refuse to report status
    return out


def latest_edges(trace: list) -> dict:
    """artifact -> the most recent edge result recorded for it."""
    out = {}
    for rec in trace:
        if rec.get("artifact") and rec.get("edge"):
            out[rec["artifact"]] = rec["edge"]
    return out


def rerun_counts(trace: list) -> dict:
    """artifact -> how many times its edge has failed (how often the step has been redone)."""
    counts = {}
    for rec in trace:
        edge = rec.get("edge") or {}
        if rec.get("artifact") and edge.get("exit"):
            counts[rec["artifact"]] = counts.get(rec["artifact"], 0) + 1
    return counts


def open_punch_outs(item_dir: Path) -> list:
    """Punch-outs with no decision file, or whose decision no longer matches the file.

    Signature verification is the enforcement hook's job; this reports what is unresolved.
    """
    out = []
    for p in sorted(item_dir.glob("punch-out-*.md")):
        decision = item_dir / "decisions" / (p.stem + ".json")
        doc, err = load_json(decision)
        if err:
            out.append({"punch_out": p.name, "state": "undecided"})
            continue
        if doc.get("sha256") != sha256(p):
            out.append({"punch_out": p.name, "state": "decision is stale: the punch-out changed after it was decided"})
            continue
        if doc.get("choice") != "proceed":
            out.append({"punch_out": p.name, "state": f"decided: {doc.get('choice')}", "stops_flow": True})
    return out


def status(repo: Path, item: str) -> dict:
    item_dir = repo / "delivery" / item
    cfg = load_config(repo)
    has_vault = bool((cfg.get("vault") or {}).get("binding"))

    triage, _ = load_json(item_dir / "triage.json")
    path_kind = (triage or {}).get("path")

    trace = read_trace(item_dir / "trace.jsonl")
    edges, reruns = latest_edges(trace), rerun_counts(trace)

    table, missing = [], []
    for artifact, step, kind, optional_when in STEPS:
        skipped = (optional_when == "vault" and not has_vault) or \
                  (path_kind == "quick" and step in QUICK_PATH_SKIPS)
        present = (item_dir / artifact).exists()
        edge = edges.get(artifact)
        row = {"artifact": artifact, "step": step, "kind": kind, "present": present,
               "skipped": skipped, "edge": edge, "reruns": reruns.get(artifact, 0)}
        table.append(row)
        if not present and not skipped:
            missing.append(row)

    punch_outs = open_punch_outs(item_dir)
    failed = [r for r in table if r["present"] and (r["edge"] or {}).get("exit")]

    if punch_outs:
        first = punch_outs[0]
        next_step, blocked = None, (
            f"{first['punch_out']} is {first['state']} — a decision is required before anything else runs")
    elif failed:
        r = failed[0]
        if r["reruns"] >= MAX_RERUNS:
            next_step, blocked = None, (
                f"{r['artifact']} failed its edge {r['reruns']} times ({r['edge']['summary'][:120]}): "
                f"the rerun limit is {MAX_RERUNS}, so this is a punch-out, not another attempt")
        else:
            next_step, blocked = r["step"], (
                f"rerun {r['step']}: {r['artifact']} failed its edge — {r['edge']['summary'][:160]}")
    elif missing:
        next_step, blocked = missing[0]["step"], None
    else:
        next_step, blocked = None, None

    return {"item": item, "repo": str(repo), "exists": item_dir.exists(),
            "path": path_kind, "vault": has_vault, "table": table,
            "punch_outs": punch_outs, "next_step": next_step, "blocked": blocked,
            "complete": not missing and not punch_outs and not failed}


def render(st: dict) -> str:
    lines = [f"{st['item']} — {'quick path' if st['path'] == 'quick' else 'standard path' if st['path'] else 'not yet triaged'}"]
    for r in st["table"]:
        if r["skipped"]:
            mark, note = "·", "skipped"
        elif not r["present"]:
            mark, note = " ", ""
        elif (r["edge"] or {}).get("exit"):
            mark, note = "✗", f"edge failed: {r['edge']['summary'][:60]}"
        elif r["edge"]:
            mark, note = "✓", "edge ok"
        else:
            mark, note = "✓", "no edge recorded"
        lines.append(f"  [{mark}] {r['artifact']:<32} {r['step']:<24} {note}")
    for p in st["punch_outs"]:
        lines.append(f"  !  {p['punch_out']}: {p['state']}")
    if st["blocked"]:
        lines.append(f"\nBLOCKED — {st['blocked']}")
    elif st["next_step"]:
        lines.append(f"\nNext: {st['next_step']}")
    elif st["complete"]:
        lines.append("\nComplete: every step has run.")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo))
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo: no {CONFIG_NAME} at its root", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.item):
        print(f"not an item key: {args.item!r}", file=sys.stderr)
        return 2

    st = status(repo, args.item)
    print(json.dumps(st, indent=2) if args.json else render(st))
    return 0


if __name__ == "__main__":
    sys.exit(main())
