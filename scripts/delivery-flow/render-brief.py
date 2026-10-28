#!/usr/bin/env python3
"""Render the brief: `summary.md` for one item, from its structured artifacts.

Usage:
    render-brief.py <ITEM-KEY> [--repo <path>] [--stdout]

The brief is the `triage` profile's terminal artifact: a human reads it, no step consumes it.
It is a script rather than a node because everything it needs is already structured, so a
node would buy a certification package and a hallucination risk for no new information. The
template lives in `brief.py`, shared with the edge check that verifies this output.

Writes `delivery/<ITEM-KEY>/summary.md` and nothing else. No sentinel: a sentinel is a node's
claim about its own output, and there is no claim to test when the producer is deterministic —
the edge recomputes coverage from the same inputs instead.

Exit codes: 0 written, 2 not a delivery-flow repo, no such item, or a required artifact
missing or unreadable.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brief  # noqa: E402
from common import (CONFIG_NAME, is_delivery_repo, load_json,  # noqa: E402
                    open_punch_outs, repo_root)


def load_inputs(item_dir: Path):
    """(inputs, error). `item.json` and `triage.json` are required; the breakdown, its
    challenge and the proposal are absent on the quick path or before `propose` runs, which the
    brief states rather than hiding."""
    item, err = load_json(item_dir / "item.json")
    if err:
        return None, f"item.json is required to render a brief: {err}"
    triage, err = load_json(item_dir / "triage.json")
    if err:
        return None, f"triage.json is required to render a brief: {err}"

    out = {"item": item, "triage": triage, "breakdown": None, "challenge": None, "proposal": None}
    for key, name in (("breakdown", "breakdown.json"), ("challenge", "challenge-breakdown.json"),
                      ("proposal", "proposal.json")):
        path = item_dir / name
        if not path.exists():
            continue
        doc, err = load_json(path)
        if err:
            return None, f"{name} exists but cannot be read: {err}"
        out[key] = doc
    return out, None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing summary.md")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo))
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo: no {CONFIG_NAME} at its root", file=sys.stderr)
        return 2
    item_dir = repo / "delivery" / args.item
    if not item_dir.is_dir():
        print(f"no such item: {args.item}", file=sys.stderr)
        return 2

    inputs, err = load_inputs(item_dir)
    if err:
        print(err, file=sys.stderr)
        return 2

    text = brief.render(inputs["item"], inputs["triage"], inputs["breakdown"],
                        inputs["challenge"], open_punch_outs(item_dir), inputs["proposal"])

    if args.stdout:
        print(text, end="")
        return 0
    (item_dir / "summary.md").write_text(text)
    print(f"wrote {item_dir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
