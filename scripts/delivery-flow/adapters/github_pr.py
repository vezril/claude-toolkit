#!/usr/bin/env python3
"""GitHub forge adapter: opening a pull request and reading the checks on one.

Usage:
    github_pr.py open-pr --item <KEY> --head <branch> --base <branch> --title <t>
                         --body-file <path> [--repo owner/name] [--draft]
    github_pr.py ci-status <ref> [--repo owner/name]

`--item` is the tracker key the branch is delivering, and it is required rather than parsed
out of the branch name: the punch-out check is only as good as its idea of which item is being
worked on, and guessing that from a branch string would fail open.

All remote access goes through `gh`, so authentication is whatever `gh auth status` says and no
token is read, stored or logged here. No model is invoked: the PR body arrives as a file that
some earlier step wrote.

Exit codes: 0 fine, 2 a usage or contract error (including a refusal), 3 a remote or auth
failure, with the fix on stderr.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import Usage, dispatch, emit, outward_refusal  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from github_issues import gh  # noqa: E402  the same `gh` runner, so failures map identically

# A check run reports status + conclusion; a legacy status context reports one state. Both
# normalize onto the same four words so the flow has one thing to branch on.
PASSING = {"SUCCESS"}
FAILING = {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE", "ERROR"}
PENDING = {"QUEUED", "IN_PROGRESS", "PENDING", "WAITING", "REQUESTED", ""}
SKIPPED = {"SKIPPED", "NEUTRAL", "STALE"}


def normalize_check(entry: dict) -> dict:
    name = (entry.get("name") or entry.get("context") or "").strip()
    url = entry.get("detailsUrl") or entry.get("targetUrl") or ""
    if entry.get("status") and (entry.get("status") or "").upper() != "COMPLETED":
        raw = (entry.get("status") or "").upper()
    else:
        raw = (entry.get("conclusion") or entry.get("state") or "").upper()

    if raw in PASSING:
        state = "passing"
    elif raw in FAILING:
        state = "failing"
    elif raw in SKIPPED:
        state = "skipped"
    elif raw in PENDING:
        state = "pending"
    else:
        # An unrecognized conclusion is reported as itself rather than folded into "passing".
        # A green rollup is the thing this flow trusts least cheaply.
        state = raw.lower()
    return {"name": name, "state": state, "url": url}


def rollup(checks: list) -> str:
    """One word for the whole ref. Unknown states count as failing, never as passing."""
    states = {c["state"] for c in checks}
    if not checks:
        return "none"
    if states - {"passing", "pending", "skipped"}:
        return "failing"
    if "pending" in states:
        return "pending"
    return "passing"


def cmd_ci_status(args) -> int:
    pr = gh(["pr", "view", args.ref, "--json", "statusCheckRollup,number,url"],
            parse_json=True, repo=args.repo)
    checks = sorted((normalize_check(e) for e in (pr.get("statusCheckRollup") or [])),
                    key=lambda c: (c["name"], c["url"]))
    return emit({"state": rollup(checks), "checks": checks,
                 "number": str(pr.get("number") or ""), "url": pr.get("url") or ""})


def cmd_open_pr(args) -> int:
    body = Path(args.body_file)
    if not body.is_file():
        raise Usage(f"no such body file: {body}")
    if not body.read_text().strip():
        raise Usage(f"{body} is empty; refusing to open a PR with no description")

    why = outward_refusal(args.item, f"open a PR for {args.item}")
    if why:
        raise Usage(why)

    out = gh(["pr", "create", "--head", args.head, "--base", args.base,
              "--title", args.title, "--body-file", str(body)]
             + (["--draft"] if args.draft else []), repo=args.repo) or ""
    url = next((l.strip() for l in reversed(out.splitlines())
                if l.strip().startswith("https://")), "")
    m = re.search(r"/pull/(\d+)", url)
    return emit({"url": url, "number": m.group(1) if m else ""})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("open-pr")
    p.add_argument("--item", required=True, metavar="KEY")
    p.add_argument("--head", required=True)
    p.add_argument("--base", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True)
    p.add_argument("--repo", default=None, metavar="owner/name")
    p.add_argument("--draft", action="store_true")
    p = sub.add_parser("ci-status")
    p.add_argument("ref")
    p.add_argument("--repo", default=None, metavar="owner/name")
    args = ap.parse_args(argv)

    return dispatch({"open-pr": cmd_open_pr, "ci-status": cmd_ci_status}, args.cmd, args)


if __name__ == "__main__":
    sys.exit(main())
