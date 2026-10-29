#!/usr/bin/env python3
"""Render the story set from a challenged breakdown. The seam between the two workflows.

Usage:
    render-stories.py <ITEM-KEY> [--repo <path>] [--change <openspec/changes/id>]
                      [--stdout] [--dry-run]

`delivery-flow` ends a run holding `breakdown.json`: epics, stories and acceptance criteria,
written by a certified node and then attacked by `challenge-breakdown`. The build pipeline
needs stories. This renders one from the other.

**It is an edge, not a node** (design D10 in `certify-sdlc-pipeline`). Every field is carried
across unchanged, so there is no judgement to certify — and nothing here can invent a story the
challenge never saw. Feeding the breakdown to `story-planner` instead would put an uncertified
decomposition downstream of a certified one, which both voids the chain's end-to-end number and
creates a second place the plan can drift from the ticket.

**It refuses to run on an unchallenged or refuted breakdown.** The challenge is the control for
a dropped requirement — "a deliverable the item requires appears in no story" is one of its
three REFUTED conditions — and the `breakdown` node's known residual is exactly that defect,
about one run in three. Rendering before the challenge would carry the drop straight into the
build.

Two gaps it states rather than fills:

- **No Dev Notes.** A story carries a `sources` array pointing at the artifacts it came from.
  A summary would be a node's claim about the context; pointers are the context.
- **No dependency order.** Stories are in breakdown order with `ordering.determined: false`.
  Ordering is a judgement and belongs to a node or a human.

Exit codes: 0 rendered, 1 refused (no challenge, or a REFUTED verdict), 2 a usage error.
"""

import argparse
import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import artifact_root, is_delivery_repo, load_json, repo_root  # noqa: E402
from stories import missing_from, sources_for, stories_from, story_filename  # noqa: E402


def _write_sentinel(path: Path, claimed_acs: int) -> tuple:
    """Write the sentinel beside a rendered story. Returns (ok, message).

    Without this every story failed its edge with "no readable sentinel beside the artifact" —
    the same defect as recall's (delivery-flow defect 5). It went unnoticed because the edge
    was not reaching stories at all until the `story-*.json` schema glob landed; making the
    gate live is what exposed it.

    The acceptance-criteria count is claimed from the **breakdown**, not read back from the
    file just written. A count derived from the output would agree with the output by
    construction and assert nothing — the sentinel exists precisely so the edge can compare a
    claim against reality, so the claim has to come from the source.
    """
    spec = importlib.util.spec_from_file_location("write_sentinel", HERE / "write-sentinel.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = mod.main([str(path), "--step", "render-stories",
                       "--count", f"acceptance_criteria={claimed_acs}"])
    return rc == 0, buf.getvalue().strip()


def breakdown_ac_counts(breakdown: dict) -> dict:
    """(epic id, story id) -> how many acceptance criteria the breakdown holds for it."""
    return {(e.get("id"), s.get("id")): len(s.get("acceptance_criteria") or [])
            for e in breakdown.get("epics") or []
            for s in e.get("stories") or []}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--change", default=None,
                    help="the OpenSpec change directory, where propose has run")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo).expanduser())
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo", file=sys.stderr)
        return 2
    item_dir = artifact_root(repo) / args.item
    if not item_dir.is_dir():
        print(f"no such item: {item_dir}", file=sys.stderr)
        return 2

    breakdown, err = load_json(item_dir / "breakdown.json")
    if err:
        print(f"{err}\nThis is the standard path's planning artifact; a quick-path item has no "
              "breakdown and no stories to render.", file=sys.stderr)
        return 2

    # The challenge is the gate, not a nicety. See the module docstring.
    challenge, cerr = load_json(item_dir / "challenge-breakdown.json")
    if cerr:
        print("refusing to render: breakdown.json has not been challenged.\n"
              "challenge-breakdown is the control for a dropped requirement, and the breakdown "
              "node's known residual is exactly that — run it first.", file=sys.stderr)
        return 1
    verdict = (challenge or {}).get("verdict")
    if verdict == "REFUTED":
        findings = "; ".join(f.get("finding", "") for f in (challenge.get("findings") or []))
        print(f"refusing to render: the challenge REFUTED this breakdown — {findings}\n"
              "REFUTED means the breakdown is not a plan for this item. Rerun breakdown; do "
              "not build from it.", file=sys.stderr)
        return 1

    sources = sources_for(item_dir, args.change)
    stories = stories_from(breakdown, sources)
    if not stories:
        print("the breakdown contains no stories, so there is nothing to render",
              file=sys.stderr)
        return 2

    dropped = missing_from(stories, breakdown)
    if dropped:  # impossible by construction; checked because code can be edited
        print("refusing to render: " + "; ".join(dropped), file=sys.stderr)
        return 1

    if args.stdout:
        print(json.dumps(stories, indent=2, sort_keys=True))
        return 0

    claimed = breakdown_ac_counts(breakdown)
    written, sentinel_errors = [], []
    for story in stories:
        path = item_dir / story_filename(story["epic"], story["story"])
        if not args.dry_run:
            path.write_text(json.dumps(story, indent=2, sort_keys=True) + "\n")
            # Each story is its own artifact and the edge checks each one, so each needs its
            # own sentinel. Written immediately after the file, before the next story, so a
            # crash mid-render leaves matched pairs rather than orphan artifacts.
            ok, msg = _write_sentinel(path, claimed.get((story["epic"], story["story"]), 0))
            if not ok:
                sentinel_errors.append(f"{path.name}: {msg}")
        written.append(path.name)

    if sentinel_errors:
        # Refuse rather than warn. An artifact with no sentinel fails its edge, so leaving
        # these behind would hand the build a story set the flow must not advance past.
        print("rendered the stories but could not write every sentinel, so the set is not "
              "usable:", file=sys.stderr)
        for e in sentinel_errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    verb = "would write" if args.dry_run else "wrote"
    print(f"{verb} {len(written)} stories from breakdown.json "
          f"(verdict {verdict}, {len(sources)} sources each)")
    for name in written:
        print(f"  {name}")
    if verdict == "WEAKENED":
        print("\nnote: the challenge WEAKENED this breakdown. The plan stands, but its findings "
              "are meant to be fixed in place — read them before building.")
    print("\nordering: breakdown order, dependency ordering undetermined")
    return 0


if __name__ == "__main__":
    sys.exit(main())
