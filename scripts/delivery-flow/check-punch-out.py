#!/usr/bin/env python3
"""Decide whether this item needs a human, from files rather than judgement.

Usage:
    check-punch-out.py <ITEM-KEY> [--step <name>] [--repo <path>] [--json] [--dry-run]

Stage 4 separates two things: guardrails between steps must be automated, and a punch-out
raises a decision that should not be left to an AI. So this runs at every handoff and fires
only on triggers that can be read off disk:

  scope            triage set handoff: true
  architecture     triage set architecture_change: true
  breaking         triage set breaking_change: true, or the diff touches a contract path
  refuted-twice    the same step has been REFUTED twice
  retry-limit      an artifact's edge has failed more times than the limit
  budget           the item's API-equivalent cost has passed the configured budget
  protected-path   the diff touches a protected path
  external-post    a post is due to a tracker marked external

When one matches it writes `punch-out-<n>.md` — the trigger, its evidence, the decision
needed and the options — and the flow stops until a human decides.

Exit codes: 0 nothing fired, 1 a punch-out was written (or would be, with --dry-run),
2 not a delivery-flow repo.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import triggers as trigger_rules  # noqa: E402  (the local `triggers()` owns that name)
from common import artifact_root, is_delivery_repo, load_config, load_json, repo_root  # noqa: E402

DEFAULT_RETRY_LIMIT = 3


def git_changed_files(repo: Path) -> list:
    """Files changed against the merge base, or [] when git can't say."""
    for args in (["git", "diff", "--name-only", "origin/HEAD...HEAD"],
                 ["git", "diff", "--name-only", "HEAD"]):
        try:
            out = subprocess.run(args, cwd=repo, capture_output=True, text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                return [l.strip() for l in out.stdout.splitlines() if l.strip()]
        except (OSError, subprocess.SubprocessError):
            continue
    return []


def read_trace(item_dir: Path) -> list:
    p = item_dir / "trace.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def triggers(repo: Path, item: str, step: str, cfg: dict) -> list:
    item_dir = artifact_root(repo) / item
    policy = cfg.get("punch_out") or {}
    found = []

    # The three triage-sourced triggers. Each fires on the node's flag OR on a derivation that
    # never reads that flag, so a node cannot skip its own gate by writing false. Where the two
    # disagree, check-edge.py records it on the edge as `policy_disagreement` evidence and the
    # edge still passes; the punch-out is written either way.
    item_doc, _ = load_json(item_dir / "item.json")
    triage, _ = load_json(item_dir / "triage.json")
    breakdown, _ = load_json(item_dir / "breakdown.json")
    for name, v in sorted(trigger_rules.combine(item_doc, triage, breakdown, cfg).items()):
        if not v["fired"]:
            continue
        flag = trigger_rules.FLAG_FOR[name]
        if v["source"] == "claim":
            evidence = f"triage.json sets {flag}: true"
            if name == "scope" and (triage or {}).get("handoff_reason"):
                evidence += f" — {triage['handoff_reason']}"
            evidence += "; the derivation did not independently find it"
        elif v["source"] == "derivation":
            evidence = (f"derived from the artifacts ({v['evidence']}); "
                        f"triage.json did not set {flag}")
        else:
            evidence = f"triage.json sets {flag}: true, and the artifacts agree: {v['evidence']}"
        found.append({"trigger": name, "evidence": evidence,
                      "decision": trigger_rules.CLAIMS[name][1], "options": trigger_rules.OPTIONS[name]})

    # The proposal-sourced triggers, evaluated only when the flow is leaving the brief. Raising
    # them earlier would ask a human to decide before the brief that explains the change exists.
    if step == "implementation":
        proposal, _ = load_json(item_dir / "proposal.json")
        for name, v in sorted(trigger_rules.combine_proposal(proposal, cfg).items()):
            if not v["fired"]:
                continue
            flag = trigger_rules.PROPOSAL_FLAG_FOR.get(name)
            if v["source"] == "claim":
                evidence = (f"proposal.json sets {flag}: true; the planned paths did not "
                            "independently show it")
            elif v["source"] == "derivation":
                evidence = f"derived from the proposal's planned changes ({v['evidence']})"
                if flag:
                    evidence += f"; proposal.json did not set {flag}"
            else:
                evidence = f"proposal.json sets {flag}: true, and the planned paths agree: {v['evidence']}"
            ask, options = trigger_rules.PROPOSAL_DECISIONS[name]
            found.append({"trigger": name, "evidence": evidence,
                          "decision": ask, "options": options})

    changed = git_changed_files(repo)
    for kind, key, question in (("breaking", "contract_paths", "A shared contract changed. Proceed?"),
                                ("protected-path", "protected_paths", "A protected path changed. Proceed?")):
        for prefix in policy.get(key) or []:
            hits = [f for f in changed if f.startswith(prefix)]
            if hits:
                found.append({"trigger": kind, "evidence": f"the diff touches {prefix}: " + ", ".join(hits[:5]),
                              "decision": question, "options": ["proceed", "stop", "redirect"]})
                break

    trace = read_trace(item_dir)
    refuted = {}
    fails = {}
    cost = 0.0
    for rec in trace:
        cost += rec.get("api_equivalent_cost_usd") or 0
        edge = rec.get("edge") or {}
        if rec.get("artifact") and edge.get("exit"):
            fails[rec["artifact"]] = fails.get(rec["artifact"], 0) + 1
        if rec.get("verdict") == "REFUTED" and rec.get("step"):
            refuted[rec["step"]] = refuted.get(rec["step"], 0) + 1

    # The trace records every challenge run; the file on disk is only the latest one, so it
    # counts only when the trace has nothing to say — otherwise one refutation counts twice.
    if not refuted:
        for challenge in sorted(item_dir.glob("challenge-*.json")):
            doc, err = load_json(challenge)
            if not err and doc.get("verdict") == "REFUTED":
                target = doc.get("target") or challenge.stem
                refuted[target] = 1

    for target, n in refuted.items():
        if n >= 2:
            found.append({"trigger": "refuted-twice", "evidence": f"{target} has been REFUTED {n} times",
                          "decision": "Two refutations on the same step. Is the approach wrong?",
                          "options": ["proceed with the findings addressed", "stop", "redirect"]})

    limit = int(policy.get("retry_limit") or DEFAULT_RETRY_LIMIT)
    for artifact, n in sorted(fails.items()):
        if n >= limit:
            found.append({"trigger": "retry-limit", "evidence": f"{artifact} has failed its edge {n} times (limit {limit})",
                          "decision": "The step cannot produce a valid artifact. What now?",
                          "options": ["proceed by hand (counts as a failed run)", "stop", "redirect"]})

    budget = policy.get("cost_budget_usd")
    if budget is not None and cost > float(budget):
        found.append({"trigger": "budget", "evidence": f"API-equivalent cost ${cost:.4f} is over the ${float(budget):.2f} budget",
                      "decision": "This item has cost more than its budget. Keep going?",
                      "options": ["proceed", "stop", "redirect"]})

    if step in ("post-back", "post-summary") and (cfg.get("tracker") or {}).get("external"):
        found.append({"trigger": "external-post", "evidence": "the tracker is marked external: true",
                      "decision": "This posts to someone else's tracker. Send it?",
                      "options": ["proceed", "stop", "redirect: edit the summary first"]})
    return found


def write_punch_out(item_dir: Path, item: str, step: str, t: dict) -> Path:
    n = 1 + len(list(item_dir.glob("punch-out-*.md")))
    path = item_dir / f"punch-out-{n}.md"
    path.write_text(
        f"# Punch-out {n}: {t['trigger']}\n\n"
        f"- **Item:** {item}\n- **Step:** {step or 'unknown'}\n"
        f"- **Raised:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n\n"
        f"## Evidence\n\n{t['evidence']}\n\n"
        f"## Decision needed\n\n{t['decision']}\n\n"
        f"## Options\n\n" + "\n".join(f"- {o}" for o in t["options"]) + "\n\n"
        f"Decide with:\n\n```\ndecide.py {item} punch-out-{n} --choose proceed|stop|redirect\n```\n")
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--step", default="")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo))
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo", file=sys.stderr)
        return 2
    item_dir = artifact_root(repo) / args.item
    if not item_dir.exists():
        print(f"no such item: {args.item}", file=sys.stderr)
        return 2

    cfg = load_config(repo)
    found = triggers(repo, args.item, args.step, cfg)

    # One punch-out per trigger kind: a second architecture flag on a rerun is the same decision.
    existing = {p.read_text().split("\n", 1)[0].split(": ", 1)[-1].strip()
                for p in item_dir.glob("punch-out-*.md")}
    new = [t for t in found if t["trigger"] not in existing]

    written = []
    for t in new:
        written.append(str(write_punch_out(item_dir, args.item, args.step, t)) if not args.dry_run
                       else f"(dry run) {t['trigger']}")

    if args.json:
        print(json.dumps({"item": args.item, "step": args.step, "triggered": found,
                          "written": written, "already_open": sorted(existing)}, indent=2))
    elif written:
        for w in written:
            print(f"punch-out written: {w}")
    else:
        print("no punch-out triggered" + (f" ({len(found)} already open)" if found else ""))
    return 1 if written else 0


if __name__ == "__main__":
    sys.exit(main())
