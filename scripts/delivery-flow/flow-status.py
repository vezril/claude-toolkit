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
  3. a challenge whose target has been rewritten since is stale, and the challenge reruns
     against the version that now exists;
  4. a challenge verdict of REFUTED reruns the step that produced its target (twice on the
     same target is a punch-out, not a third attempt);
  5. otherwise the next step is the first one in the table whose artifact is missing.

A verdict of WEAKENED never blocks. It proceeds, and its findings are reported as
constraints the consuming step has to address — which is the whole difference between the
two: REFUTED says the artifact is wrong, WEAKENED says it is right but incomplete.

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

# challenge artifact -> (the artifact it attacks, the step that produced that artifact).
# The adversarial validator is a node, not a guardrail, so its verdict is not trusted as a
# judgement — it is routed mechanically, and these are the only routes it has.
CHALLENGES = {
    "challenge-breakdown.json": ("breakdown.json", "breakdown"),
    "challenge-implementation.json": ("implementation.json", "implementation"),
}
MAX_REFUTATIONS = 2


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


def last_write_index(trace: list, artifact: str) -> int:
    """Where in the trace the artifact was last written, or -1.

    Edge records are the ledger of writes: the hook appends one every time an artifact is
    written, pass or fail. Their order is what tells a stale challenge from a current one.
    """
    found = -1
    for i, rec in enumerate(trace):
        if rec.get("artifact") == artifact and rec.get("edge"):
            found = i
    return found


def refutation_counts(trace: list, item_dir: Path) -> dict:
    """target artifact -> how many times a challenge of it has come back REFUTED.

    Counted the same way `check-punch-out.py` counts it, so the two agree on when the
    rerun becomes a punch-out: from the trace, which records every challenge run, and from
    the file on disk only when the trace has nothing to say — otherwise one refutation
    would count twice.
    """
    counts = {}
    for rec in trace:
        if rec.get("verdict") == "REFUTED":
            target = rec.get("target") or CHALLENGES.get(rec.get("artifact") or "", (None,))[0]
            if target:
                counts[target] = counts.get(target, 0) + 1
    if counts:
        return counts
    for challenge, (target, _step) in CHALLENGES.items():
        doc, err = load_json(item_dir / challenge)
        if not err and doc.get("verdict") == "REFUTED":
            counts[target] = 1
    return counts


def challenges(item_dir: Path, trace: list) -> list:
    """The challenge artifacts on disk, each with its verdict and whether it still applies.

    A challenge attacks one version of its target. If the target has been written again
    since, the verdict on disk is about an artifact that no longer exists, so the challenge
    reruns rather than the step it already refuted — otherwise a refutation would block the
    flow forever, and the rerun it asked for would be the thing that kept it blocked.
    """
    refuted = refutation_counts(trace, item_dir)
    out = []
    for challenge, (target, producing_step) in CHALLENGES.items():
        path = item_dir / challenge
        if not path.exists():
            continue
        doc, err = load_json(path)
        if err:
            out.append({"artifact": challenge, "target": target, "step": producing_step,
                        "verdict": None, "stale": False, "unreadable": err,
                        "findings": [], "refutations": refuted.get(target, 0)})
            continue
        c_at, t_at = last_write_index(trace, challenge), last_write_index(trace, target)
        out.append({
            "artifact": challenge,
            "target": doc.get("target") or target,
            "step": producing_step,
            "verdict": doc.get("verdict"),
            # Both present and the target written later: the challenge is about an older
            # version. With no trace at all there is nothing to compare, so it is current.
            "stale": c_at >= 0 and t_at > c_at,
            "unreadable": None,
            "findings": [f.get("finding") for f in (doc.get("findings") or []) if f.get("finding")],
            "refutations": refuted.get(target, 0),
        })
    return out


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
    verdicts = challenges(item_dir, trace)

    stale = [c for c in verdicts if c["stale"]]
    refuted = [c for c in verdicts if not c["stale"] and c["verdict"] == "REFUTED"]
    weakened = [c for c in verdicts if not c["stale"] and c["verdict"] == "WEAKENED"]
    unreadable = [c for c in verdicts if c["unreadable"]]

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
    elif unreadable:
        c = unreadable[0]
        next_step, blocked = None, (
            f"{c['artifact']} cannot be read ({c['unreadable']}), so its verdict cannot be routed")
    elif stale:
        c = stale[0]
        next_step, blocked = c["artifact"].removesuffix(".json"), (
            f"rerun {c['artifact'].removesuffix('.json')}: {c['target']} was written again after it "
            f"was challenged, so the verdict on disk is about a version that no longer exists")
    elif refuted:
        c = refuted[0]
        if c["refutations"] >= MAX_REFUTATIONS:
            next_step, blocked = None, (
                f"{c['target']} has been REFUTED {c['refutations']} times: the limit is "
                f"{MAX_REFUTATIONS}, so this is a punch-out, not a third attempt")
        else:
            findings = "; ".join(c["findings"][:2]) or "see the findings in the challenge artifact"
            next_step, blocked = c["step"], (
                f"rerun {c['step']}: {c['artifact']} came back REFUTED — {findings[:200]}")
    elif missing:
        next_step, blocked = missing[0]["step"], None
    else:
        next_step, blocked = None, None

    return {"item": item, "repo": str(repo), "exists": item_dir.exists(),
            "path": path_kind, "vault": has_vault, "table": table,
            "punch_outs": punch_outs, "challenges": verdicts,
            # WEAKENED does not block; the findings travel with the flow as constraints the
            # consuming step is required to address, and the challenge is not rerun for them.
            "carry_forward": [f for c in weakened for f in c["findings"]],
            "next_step": next_step, "blocked": blocked,
            "complete": not missing and not punch_outs and not failed and not stale and not refuted}


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
    for c in st.get("challenges") or []:
        if c["unreadable"]:
            lines.append(f"  !  {c['artifact']}: unreadable — {c['unreadable']}")
        elif c["stale"]:
            lines.append(f"  !  {c['artifact']}: stale, {c['target']} changed after it was challenged")
        elif c["verdict"]:
            note = f" ({c['refutations']}x)" if c["verdict"] == "REFUTED" and c["refutations"] > 1 else ""
            lines.append(f"     {c['artifact']}: {c['verdict']}{note} on {c['target']}")
    for f in st.get("carry_forward") or []:
        lines.append(f"  →  carry forward: {f[:100]}")
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
