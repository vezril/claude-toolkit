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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "workflow"))
from common import (CONFIG_NAME, artifact_root, artifact_root_problems,  # noqa: E402
                    is_delivery_repo, load_config, load_json,
                    load_profiles, open_punch_outs, repo_root, select_profile)
import descriptor as workflow_descriptor  # noqa: E402

MAX_RERUNS = 3

# The routing table, read from this workflow's descriptor rather than written here.
#
# It used to be Python literals in this file, which meant the one table a second workflow
# would need was locked inside delivery-flow's own status script. The descriptor
# (`skills/delivery-flow/workflow.yaml`) now owns it; the tuple shape below is unchanged, so
# every existing consumer of `STEPS` is untouched and the move is behaviour-free.
#
# `optional_when` still names a config question; the step is skipped when the answer is no.
# A *profile* (`templates/delivery-flow/profiles.yaml`) names an ordered subset of this
# table, and routing happens inside that subset only; a repo naming no profile gets `full`.
DESCRIPTOR = workflow_descriptor.load(
    workflow_descriptor.PLUGIN_ROOT / "skills" / "delivery-flow" / "workflow.yaml")
STEPS = workflow_descriptor.step_table(DESCRIPTOR)

BY_STEP = {step: (artifact, kind, optional_when) for artifact, step, kind, optional_when in STEPS}


def profile_steps(profile: dict):
    """[(artifact, step, kind, optional_when)] for a profile, or (None, error).

    The order is the profile's, and every step it names must exist in the routing table —
    a profile that names a step the table does not have would otherwise route to nothing.
    """
    rows, unknown = [], []
    for step in profile.get("steps") or []:
        if step not in BY_STEP:
            unknown.append(step)
            continue
        artifact, kind, optional_when = BY_STEP[step]
        rows.append((artifact, step, kind, optional_when))
    if unknown:
        return None, (f"profile {profile.get('profile')!r} names steps that are not in the "
                      f"routing table: {', '.join(unknown)}")
    return rows, None

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


def change_tasks(repo: Path, item_dir: Path) -> dict:
    """How many of the proposed change's tasks are still unticked, or {} with no proposal.

    A run that ends with the change's `tasks.md` still claiming everything is open has not
    really finished, and nothing else would say so: the artifacts are all present and the
    outcome reads `completed`. Surfacing it here keeps a change directory from being abandoned
    quietly.
    """
    proposal, err = load_json(item_dir / "proposal.json")
    if err or not proposal:
        return {}
    change_id = proposal.get("change_id") or ""
    tasks_md = repo / (proposal.get("change_path") or f"openspec/changes/{change_id}") / "tasks.md"
    try:
        text = tasks_md.read_text()
    except OSError:
        return {"change_id": change_id, "readable": False}
    open_ids = re.findall(r"^\s*-\s*\[ \]\s*(T[0-9]+)\b", text, re.M)
    done_ids = re.findall(r"^\s*-\s*\[[xX]\]\s*(T[0-9]+)\b", text, re.M)
    return {"change_id": change_id, "readable": True,
            "outstanding": len(open_ids), "done": len(done_ids),
            "archive_command": f"openspec archive {change_id}"}


def first_missing(item_dir: Path, rows: list, has_vault: bool, path_kind):
    """The first step in `rows` whose artifact is absent and which is not skipped."""
    for artifact, step, _kind, optional_when in rows:
        skipped = (optional_when == "vault" and not has_vault) or \
                  (path_kind == "quick" and step in QUICK_PATH_SKIPS)
        if not skipped and not (item_dir / artifact).exists():
            return step
    return None


def status(repo: Path, item: str, profile: dict, profiles: list) -> dict:
    item_dir = artifact_root(repo) / item
    cfg = load_config(repo)
    has_vault = bool((cfg.get("vault") or {}).get("binding"))

    rows, err = profile_steps(profile)
    if err:
        return {"item": item, "repo": str(repo), "exists": item_dir.exists(),
                "profile": profile.get("profile"), "error": err, "table": [],
                "punch_outs": [], "challenges": [], "carry_forward": [],
                "next_step": None, "blocked": err, "complete": False}

    triage, _ = load_json(item_dir / "triage.json")
    path_kind = (triage or {}).get("path")

    trace = read_trace(item_dir / "trace.jsonl")
    edges, reruns = latest_edges(trace), rerun_counts(trace)

    table, missing = [], []
    for artifact, step, kind, optional_when in rows:
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

    complete = not missing and not punch_outs and not failed and not stale and not refuted

    # A finished profile hands over through the artifact directory, not through a model: the
    # next profile recomputes its own position from what is on disk. All that is owed here is
    # the sentence naming it, so a human knows the run stopped by design and not by stalling.
    next_profile, next_profile_step = None, None
    if complete and profile.get("next"):
        nxt, nxt_err = select_profile({"profile": profile["next"]}, profiles)
        if nxt and not nxt_err:
            nxt_rows, nxt_rows_err = profile_steps(nxt)
            if not nxt_rows_err:
                next_profile = nxt.get("profile")
                next_profile_step = first_missing(item_dir, nxt_rows, has_vault, path_kind)

    return {"item": item, "repo": str(repo), "exists": item_dir.exists(),
            "profile": profile.get("profile"), "terminus": profile.get("terminus"),
            "change": change_tasks(repo, item_dir),
            "next_profile": next_profile, "next_profile_step": next_profile_step,
            "path": path_kind, "vault": has_vault, "table": table,
            "punch_outs": punch_outs, "challenges": verdicts,
            # WEAKENED does not block; the findings travel with the flow as constraints the
            # consuming step is required to address, and the challenge is not rerun for them.
            "carry_forward": [f for c in weakened for f in c["findings"]],
            "next_step": next_step, "blocked": blocked,
            "complete": complete}


def render(st: dict) -> str:
    if st.get("error"):
        return f"{st['item']} — {st['error']}"
    path_note = ("quick path" if st["path"] == "quick"
                 else "standard path" if st["path"] else "not yet triaged")
    lines = [f"{st['item']} — profile {st['profile']}, {path_note}"]
    for r in st["table"]:
        if r["skipped"]:
            mark, note = "·", "skipped"
        elif not r["present"]:
            mark, note = " ", ""
        elif (r["edge"] or {}).get("exit"):
            mark, note = "✗", f"edge failed: {r['edge']['summary'][:60]}"
        elif (r["edge"] or {}).get("name") == "no-schema":
            # Not a tick. The artifact is present and nothing checked it, which is a
            # different state from "checked and fine" and has to read as one.
            mark, note = "?", "unchecked: no schema declares this artifact"
        elif r["edge"]:
            mark, note = "✓", "edge ok"
        else:
            # Present, and not even a record saying nothing ran. Before the no-schema record
            # existed this was the only sign of an unchecked artifact, and it was a ✓.
            mark, note = "?", "no edge recorded"
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
    change = st.get("change") or {}
    if change.get("change_id"):
        if not change.get("readable"):
            lines.append(f"  !  {change['change_id']}: its tasks.md cannot be read")
        elif change.get("outstanding"):
            lines.append(f"  !  {change['change_id']}: {change['outstanding']} task(s) still "
                         f"unticked in the change's tasks.md")
        else:
            lines.append(f"     {change['change_id']}: every task ticked — a human runs "
                         f"`{change['archive_command']}`")
    for p in st["punch_outs"]:
        lines.append(f"  !  {p['punch_out']}: {p['state']}")
    if st["blocked"]:
        lines.append(f"\nBLOCKED — {st['blocked']}")
    elif st["next_step"]:
        lines.append(f"\nNext: {st['next_step']}")
    elif st["complete"] and st.get("next_profile"):
        nxt = f" (next step: {st['next_profile_step']})" if st.get("next_profile_step") else ""
        lines.append(f"\nProfile '{st['profile']}' complete — next profile: "
                     f"{st['next_profile']}{nxt}")
        lines.append("Set `profile: " + st["next_profile"] + "` in " + CONFIG_NAME
                     + " to continue; this invocation stops here.")
    elif st["complete"]:
        lines.append(f"\nComplete: every step in profile '{st['profile']}' has run.")
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

    cfg = load_config(repo)
    # Preflight, before any position is computed: a run whose artifacts sit in the code repo
    # is one `git add` from putting a client's ticket text on a branch. Refused here because
    # this is the one thing every invocation runs first — SKILL.md's rule is "do what
    # flow-status says", so a refusal here stops the flow rather than warning into a log.
    misplaced = artifact_root_problems(repo, cfg)
    if misplaced:
        print("BLOCKED — the run artifacts are in the wrong place:", file=sys.stderr)
        for p in misplaced:
            print(f"  - {p}", file=sys.stderr)
        return 2
    try:
        profiles = load_profiles()
    except (OSError, ValueError) as e:
        print(f"could not read profiles.yaml: {e}", file=sys.stderr)
        return 2
    profile, err = select_profile(cfg, profiles)
    if err:
        print(err, file=sys.stderr)
        return 2

    st = status(repo, args.item, profile, profiles)
    print(json.dumps(st, indent=2) if args.json else render(st))
    return 2 if st.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
