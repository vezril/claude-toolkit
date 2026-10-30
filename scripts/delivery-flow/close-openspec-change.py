#!/usr/bin/env python3
"""Close the loop on an OpenSpec change: tick what shipped, and tell a human to archive.

Usage:
    close-openspec-change.py <ITEM-KEY> [--repo <path>] [--json] [--dry-run]

The flow proposes a change, then implements from `proposal.json`. Without this step the
change's own `tasks.md` never learns what shipped: it keeps claiming everything is open, nobody
archives it, and the delta specs never reach `openspec/specs/`. Change directories pile up and
the markdown quietly stops being true.

So this ticks the items `implementation.json` says are done, by id, and leaves the rest alone.
It **does not archive**: the live `sdlc-solutioning-openspec` spec makes archiving
human-triggered, `enforce-punch-outs.py` blocks an agent from doing it, and promoting deltas
into the living specs is exactly the sort of irreversible act that should cost a deliberate
keystroke. It prints the command instead.

Exit codes: 0 fine, 1 the implementation claims a task the markdown does not have, 2 a usage
error or a missing artifact.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONFIG_NAME, artifact_root, is_delivery_repo, load_json, repo_root  # noqa: E402

TASK_LINE_RE = re.compile(
    r"^(?P<indent>[ \t]*)-\s*\[(?P<mark>[ xX])\]\s*(?P<id>T[0-9]+)\b(?P<rest>.*)$", re.M)


def done_task_ids(implementation: dict) -> set:
    """Task ids the implementation artifact records as done.

    Accepts either `tasks: [{id, status}]` or a plain `tasks_done: [ids]`, because the
    implementation step's own contract is the parent change's to settle and this should not
    force it either way.
    """
    out = set()
    for tid in implementation.get("tasks_done") or []:
        if tid:
            out.add(str(tid))
    for t in implementation.get("tasks") or []:
        if isinstance(t, str):
            out.add(t)
        elif isinstance(t, dict) and t.get("id"):
            status = (t.get("status") or "done").lower()
            if status in ("done", "complete", "completed", "shipped"):
                out.add(str(t["id"]))
    return out


def retick(text: str, done: set) -> tuple:
    """(new text, ticked ids, left-open ids, all ids present)."""
    ticked, left, present = [], [], []

    def sub(m):
        tid = m.group("id")
        present.append(tid)
        if tid in done:
            if m.group("mark") == " ":
                ticked.append(tid)
            return f"{m.group('indent')}- [x] {tid}{m.group('rest')}"
        if m.group("mark") == " ":
            left.append(tid)
        return m.group(0)

    return TASK_LINE_RE.sub(sub, text), ticked, left, present


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo))
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo: no {CONFIG_NAME} at its root", file=sys.stderr)
        return 2
    item_dir = artifact_root(repo) / args.item

    proposal, err = load_json(item_dir / "proposal.json")
    if err:
        print(f"no readable proposal.json for {args.item}: {err}", file=sys.stderr)
        return 2
    implementation, err = load_json(item_dir / "implementation.json")
    if err:
        print(f"no readable implementation.json for {args.item}: {err}", file=sys.stderr)
        return 2

    change_id = proposal.get("change_id") or ""
    change_dir = repo / (proposal.get("change_path") or f"openspec/changes/{change_id}")
    tasks_md = change_dir / "tasks.md"
    if not tasks_md.is_file():
        print(f"the change has no tasks.md at {tasks_md}", file=sys.stderr)
        return 2

    done = done_task_ids(implementation)
    original = tasks_md.read_text()
    updated, ticked, left, present = retick(original, done)

    unknown = sorted(done - set(present))
    if unknown:
        print(f"implementation.json claims task(s) {', '.join(unknown)} that {tasks_md.name} "
              f"does not list — refusing to tick nothing silently", file=sys.stderr)
        return 1

    if not args.dry_run and updated != original:
        tasks_md.write_text(updated)

    archive_cmd = f"openspec archive {change_id}"
    result = {"item": args.item, "change_id": change_id,
              "ticked": sorted(ticked), "left_open": sorted(left),
              "outstanding": len(left), "archive_command": archive_cmd,
              "archived": False}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(f"{args.item} → {change_id}")
    print(f"  ticked:    {', '.join(sorted(ticked)) or 'nothing new'}")
    print(f"  left open: {', '.join(sorted(left)) or 'nothing'}")
    if left:
        print(f"\n{len(left)} task(s) still open, so the change is not ready to archive.")
    else:
        print(f"\nEvery task is ticked. A human archives it — this script never does:\n\n"
              f"    {archive_cmd}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
