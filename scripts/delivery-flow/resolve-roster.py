#!/usr/bin/env python3
"""Resolve kinds of work to the specialists who handle them.

Usage:
    resolve-roster.py <kind> [<kind> ...] [--repo <path>] [--json]
    resolve-roster.py --from-proposal <path> [--repo <path>] [--json]

Returns the union of skills, the de-duplicated reviewers and one architect per kind, from
`templates/delivery-flow/roster.yaml` with any `roster_overrides:` in the repo's
`.delivery-flow.yaml` applied.

`skills/delivery-flow/references/roster.md` has documented this script since the roster was
written; it did not exist. The roster's `reviewers:` field was therefore declared, documented
and dispatched by nothing. The `review` step is its first consumer.

**The lookup is a script, not a judgement**, so the same story always dispatches the same way.
That is what makes the dispatch auditable rather than something the orchestrator remembered.

Exit codes: 0 resolved, 1 a kind outside the vocabulary or an entry with no reviewer,
2 a usage error.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common  # noqa: E402

# The closed vocabulary, repeated in roster.yaml's header, roster.md and
# tests/delivery-flow/test_roster.py. All of them change together.
KINDS = ("ux", "frontend", "backend", "contracts", "infra", "data", "mobile", "docs")


def resolve(kinds, repo: Path = None) -> dict:
    """`{skills, reviewers, architects}` for the given kinds.

    A kind outside the vocabulary raises. An invented domain would dispatch to nobody, and
    dispatching to nobody silently is the failure this whole file exists to prevent.
    """
    roster = common.load_roster()
    # A repo with no `.delivery-flow.yaml` has no overrides — not a failure. The resolve is
    # useful standalone (and the suites run with no config at all), so an absent config means
    # the plugin roster as written, while an unreadable one is left to raise: "no overrides"
    # and "I could not read your overrides" are different answers.
    if repo is not None and (repo / common.CONFIG_NAME).exists():
        overrides = (common.load_config(repo) or {}).get("roster_overrides") or {}
        # An override *replaces* an entry rather than merging into it, so what a repo writes is
        # what dispatches. Merging would let a plugin-level reviewer survive a repo's decision
        # to drop it, which is the opposite of an override.
        for kind, entry in overrides.items():
            roster[kind] = entry

    unknown = [k for k in kinds if k not in KINDS]
    if unknown:
        raise ValueError(
            f"kind(s) outside the vocabulary: {', '.join(sorted(unknown))}; "
            f"known kinds are {', '.join(KINDS)}")

    missing = [k for k in kinds if k not in roster]
    if missing:
        raise ValueError(f"no roster entry for: {', '.join(sorted(missing))}")

    skills, reviewers, architects = [], [], {}
    no_reviewer = []
    for kind in kinds:
        entry = roster[kind] or {}
        for s in entry.get("skills") or []:
            if s not in skills:
                skills.append(s)
        rs = entry.get("reviewers") or []
        if not rs:
            no_reviewer.append(kind)
        for r in rs:
            if r not in reviewers:
                reviewers.append(r)
        architects[kind] = entry.get("architect")

    # An entry naming no reviewer is an error, not a kind that skips review. A silent skip is
    # how the review step would become decorative: the run would look reviewed and nobody
    # would have read the diff.
    if no_reviewer:
        raise ValueError(
            f"roster entry names no reviewer for: {', '.join(sorted(no_reviewer))}; "
            "a kind with no reviewer cannot be reviewed, and skipping it silently would make "
            "the review step decorative")

    return {"kinds": list(kinds), "skills": skills, "reviewers": reviewers,
            "architects": architects}


def kinds_from_proposal(path: Path) -> list:
    """The `domains` a proposal or story declares, in declared order."""
    doc, err = common.load_json(path)
    if err:
        raise ValueError(err)
    for key in ("domains", "kinds"):
        if isinstance(doc.get(key), list) and doc[key]:
            return list(doc[key])
    raise ValueError(f"{path} declares no `domains`; nothing to resolve")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kinds", nargs="*")
    ap.add_argument("--from-proposal", default=None)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if bool(args.kinds) == bool(args.from_proposal):
        ap.print_usage(sys.stderr)
        print("give either kinds or --from-proposal, not both and not neither", file=sys.stderr)
        return 2

    repo = common.repo_root(Path(args.repo).resolve())
    try:
        kinds = args.kinds or kinds_from_proposal(Path(args.from_proposal))
        out = resolve(kinds, repo)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"kinds:      {', '.join(out['kinds'])}")
        print(f"skills:     {', '.join(out['skills']) or '(none)'}")
        print(f"reviewers:  {', '.join(out['reviewers'])}")
        for kind, a in out["architects"].items():
            print(f"architect:  {kind} -> {a or '(none for this kind)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
