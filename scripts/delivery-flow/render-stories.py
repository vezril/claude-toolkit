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
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import is_delivery_repo, load_json, repo_root  # noqa: E402
from stories import missing_from, sources_for, stories_from, story_filename  # noqa: E402


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
    item_dir = repo / "delivery" / args.item
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

    written = []
    for story in stories:
        path = item_dir / story_filename(story["epic"], story["story"])
        if not args.dry_run:
            path.write_text(json.dumps(story, indent=2, sort_keys=True) + "\n")
        written.append(path.name)

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
