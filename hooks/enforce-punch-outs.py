#!/usr/bin/env python3
"""PreToolUse hook: the agent cannot decide, merge, or deploy.

Stage 4 asks for punch-out points that were actually tested — someone tried to get past them
and was blocked. These are the rules this hook enforces, in a delivery-flow repo only:

  1. Nobody but a human writes a decision. Writes under `delivery/*/decisions/` and to
     `punch-out-*.md` are denied, as are shell commands that touch them or run `decide.py`.
  2. While a punch-out is unresolved, the flow does not continue: no PR, no tracker write,
     no delegation to a downstream agent.
  3. Merging is always human. Always, regardless of decisions.
  4. Deploy actions need a `deploy` decision, unless the auto-roll rule covers them — and an
     auto-roll pass is written to the trace, so it is a recorded policy decision rather than
     a silent one.

A decision counts only when its signature verifies against the configured allowed signers:
an agent can fake a terminal, but not a key that requires a human's presence.

Inert outside a delivery-flow repo.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HELPERS = Path(__file__).resolve().parents[1] / "scripts" / "delivery-flow"

# Root-agnostic: `<root>/<ITEM>/decisions/` where the root may be anywhere, so the item
# directory plus `decisions/` is the stable part. Keeps the punch-out files and decide.py.
DECISION_PATHS = re.compile(r"[^/\s]+/decisions/|punch-out-\d+\.(?:md|json)|decide\.py")
MERGE = re.compile(r"\bgh\s+pr\s+merge\b|\bgh\s+api\b[^|;]*\bpulls/\d+/merge\b|\bgit\s+push\b[^|;]*\b(?:main|master)\b")
# Outward actions, in any argument order: `gh api -X POST …/issues/…` and
# `gh api …/issues/… -X POST` are the same thing, and a breach found both.
GH_API_WRITE = re.compile(r"\bgh\s+api\b(?=[^|;]*-X\s*(?:POST|PATCH|PUT|DELETE))"
                          r"(?=[^|;]*(?:issues|pulls|comments|merge))")
HTTP_WRITE = re.compile(r"\b(?:curl|wget|http|httpie)\b(?=[^|;]*https?://)"
                        r"(?=[^|;]*(?:-X\s*(?:POST|PATCH|PUT|DELETE)|--data|-d\b|--upload-file))")
OUTWARD = re.compile(r"\bgh\s+pr\s+create\b|\bgh\s+issue\s+(?:comment|edit|close)\b"
                     r"|\b(?:open-pr|comment|transition)\b")


def outward(cmd: str) -> bool:
    return bool(OUTWARD.search(cmd) or GH_API_WRITE.search(cmd) or HTTP_WRITE.search(cmd))
DEFAULT_DEPLOY = [r"helm\s+(?:upgrade|install)", r"flux\s+reconcile", r"docker\s+push", r"git\s+push\s+--tags"]


def deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    return 0


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return 0

    sys.path.insert(0, str(HELPERS))
    import common

    # The gate is a filesystem fact: is this working directory a delivery-flow repo. It used
    # to be `"delivery/" not in raw`, a text match on the payload — and an early exit that
    # depends on the command spelling `delivery/` is an early exit an artifact can be written
    # behind. With `artifacts.root` pointing outside the repo, the string never appears at
    # all, so this hook went inert exactly where it was most needed: it is the one that stops
    # an agent writing its own decision.
    if not common.is_delivery_repo(Path(payload.get("cwd") or ".")):
        return 0

    # cwd-based on purpose. A merge, push or deploy command runs *in* the repo it affects, so
    # the session cwd is the right answer here — and consulting the registry would make this
    # hook fire on tool calls that touch no delivery repo at all, losing the inertness every
    # part of this plugin depends on.
    repo = common.repo_root(Path(payload.get("cwd") or "."))
    if not common.is_delivery_repo(repo):
        return 0

    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    cfg = common.load_config(repo)
    text = json.dumps(ti)

    # 1. Only a human writes a decision or clears a punch-out.
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        target = str(ti.get("file_path") or ti.get("notebook_path") or "")
        if DECISION_PATHS.search(target.replace("\\", "/")):
            return deny("Decisions and punch-outs are the human's. This path is theirs to write, "
                        "not yours: a decision is only valid when signed by a key that asks for "
                        "their presence. Tell them what needs deciding and stop.")
    if tool == "Bash":
        cmd = ti.get("command", "")
        if DECISION_PATHS.search(cmd):
            return deny("That command writes, clears or decides a punch-out. Those are the human's; "
                        "report what needs deciding instead.")

    # 2–4 need to know which item is in flight.
    item, _ = None, None
    current = sorted(common.artifact_root(repo).glob("*/.current-step")) if common.artifact_root(repo).exists() else []
    if current:
        doc, err = common.load_json(current[0])
        item = (doc or {}).get("item") or current[0].parent.name if not err else current[0].parent.name
    if not item:
        # The configured root first — under `artifacts.root` the text contains that path and
        # never the word `delivery` — then the default shape for an unconfigured repo.
        root_text = str(common.artifact_root(repo)).replace("\\", "/")
        m = re.search(re.escape(root_text) + r"/([^/\s\"]+)/", text)
        if not m:
            m = re.search(r"delivery/([^/\s\"]+)/", text)
        item = m.group(1) if m else None

    cmd = ti.get("command", "") if tool == "Bash" else ""

    # 3. Merging is always human, decision or not.
    if cmd and MERGE.search(cmd):
        return deny("Merging is the human's decision, always — no decision file changes that. "
                    "Hand them the PR link instead.")

    # 4. Deploys need a decision, unless auto-roll covers them.
    deploy_cfg = cfg.get("deploy") or {}
    patterns = deploy_cfg.get("patterns") or DEFAULT_DEPLOY
    if cmd and any(re.search(p if isinstance(p, str) else str(p), cmd) for p in patterns):
        decision, ok = None, False
        if item:
            decision, err = common.load_json(common.artifact_root(repo) / item / "decisions" / "deploy.json")
            if not err:
                allowed = (cfg.get("decisions") or {}).get("allowed_signers") or "~/.config/delivery-flow/allowed_signers"
                ok, reason = common.verify_decision(decision, Path(allowed))
                ok = ok and decision.get("choice") == "proceed"
        if not ok:
            auto = (deploy_cfg.get("auto_roll") or {})
            triage, _ = common.load_json(common.artifact_root(repo) / (item or "") / "triage.json") if item else (None, "x")
            routine = bool(auto.get("routine_bumps")) and triage is not None \
                and not triage.get("architecture_change") and not triage.get("breaking_change")
            if routine:
                common.append_trace(repo, item, {
                    "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "item": item,
                    "hook": "enforce-punch-outs", "policy": "auto_roll",
                    "summary": "routine non-breaking bump rolled without a decision"})
            else:
                return deny("Deploying needs the human's decision: no valid signed deploy decision, "
                            "and the auto-roll rule does not cover this change.")

    # 2. An open punch-out stops everything outward and everything downstream.
    if item:
        item_dir = common.artifact_root(repo) / item
        open_ones = []
        for p in sorted(item_dir.glob("punch-out-*.md")):
            dec, err = common.load_json(item_dir / "decisions" / (p.stem + ".json"))
            if err:
                open_ones.append(f"{p.name} (undecided)")
                continue
            allowed = (cfg.get("decisions") or {}).get("allowed_signers") or "~/.config/delivery-flow/allowed_signers"
            ok, reason = common.verify_decision(dec, Path(allowed))
            if not ok:
                open_ones.append(f"{p.name} ({reason})")
            elif dec.get("sha256") != common.sha256(p):
                open_ones.append(f"{p.name} (decided, then edited)")
            elif dec.get("choice") != "proceed":
                open_ones.append(f"{p.name} (decided: {dec.get('choice')})")
        if open_ones:
            blocking = (tool in ("Task", "Agent")) or (cmd and outward(cmd))
            if blocking:
                return deny(f"{item} is waiting on a human: {', '.join(open_ones)}. "
                            f"Nothing continues past an open punch-out — not a PR, not a tracker "
                            f"post, not the next step. Say what is blocked and stop.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"enforce-punch-outs: {e}", file=sys.stderr)
        sys.exit(0)
