#!/usr/bin/env python3
"""GitHub Issues tracker adapter.

Usage:
    github_issues.py fetch <NUMBER> [--repo owner/name]
    github_issues.py related <NUMBER> [--repo owner/name]
    github_issues.py comment <NUMBER> --body-file <path> [--repo owner/name]
    github_issues.py transition <NUMBER> <state> [--repo owner/name]

    states: open | closed | closed:completed | closed:not_planned

An adapter is a script, not a prompt. No model is invoked here: everything a node needs about
the issue arrives as `item.json`, which is also what lets the eval suites run with no network.

All remote access goes through `gh`, so authentication is whatever `gh auth status` says and no
token is read, stored or logged by this script.

Determinism is part of the contract: two fetches of an unchanged issue produce byte-identical
output, so collections are sorted and nothing request-varying is emitted.

Exit codes: 0 fine, 2 a usage or contract error (including a refusal), 3 a remote or auth
failure, with the fix on stderr.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import Remote, Usage, dispatch, emit, outward_refusal  # noqa: E402

TIMEOUT = 60
SOURCE = "github-issues"

# `gh issue view --json` fields. Sub-issue parentage is deliberately absent: it is not exposed
# consistently across gh versions, and `related` derives parentage from the body instead, which
# every version agrees about.
FIELDS = "number,title,body,labels,state,stateReason,url"

# A `type_hint` is a hint, so the label is passed through verbatim rather than translated. The
# order is the tie-break when an issue carries several: the most specific wins, deterministically.
TYPE_LABELS = ["bug", "defect", "feature", "enhancement", "task", "chore", "docs",
               "documentation", "question"]

CLOSE_REASONS = {"closed": None, "closed:completed": "completed",
                 "closed:not_planned": "not planned"}

# `#12` — but not `abc#12` and not `/pull/#12`, so a URL fragment is not read as a reference.
REF_RE = re.compile(r"(?<![\w/])#(\d+)\b")
# Deliberately anchored on *this* issue's owner/repo: a `#12` in another repository's URL is a
# different issue, and emitting its number as a link would point the chain at the wrong item.
URL_RE = "https://github\\.com/{owner}/{repo}/(?:issues|pull)/(\\d+)\\b"

PARENT_RE = re.compile(r"\b(parent|epic)\b", re.I)
DESIGN_RE = re.compile(r"\b(design|spec|rfc|doc|docs|document)\b", re.I)


def gh(args, parse_json=False, repo=None):
    """Run `gh` and map its failures onto the adapter contract's exit codes."""
    argv = ["gh", *args] + (["--repo", repo] if repo else [])
    try:
        out = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT)
    except FileNotFoundError:
        raise Remote("the `gh` CLI is not installed. Install it from https://cli.github.com "
                     "and run `gh auth login`.")
    except (OSError, subprocess.SubprocessError) as e:
        raise Remote(f"could not run gh: {e}")

    if out.returncode != 0:
        err = (out.stderr or "").strip()[:600]
        low = err.lower()
        if ("auth" in low or "401" in low or "credential" in low
                or "logged in" in low or "logged into" in low):
            raise Remote(f"gh is not authenticated for this repository: {err}\n"
                         "Run `gh auth login` (and `gh auth refresh -s repo` if the token "
                         "lacks the repo scope), then retry.")
        raise Remote(f"gh failed: {' '.join(argv)}\n{err}")

    if not parse_json:
        return out.stdout
    try:
        return json.loads(out.stdout or "{}")
    except json.JSONDecodeError as e:
        raise Remote(f"gh returned something that is not JSON for {' '.join(argv)}: {e}")


def view(key: str, repo=None) -> dict:
    if not key.isdigit():
        raise Usage(f"a GitHub issue key is its number; got {key!r}")
    return gh(["issue", "view", key, "--json", FIELDS], parse_json=True, repo=repo)


def labels_of(issue: dict) -> list:
    return sorted({(l.get("name") or "").strip() for l in (issue.get("labels") or [])
                   if (l.get("name") or "").strip()})


def type_hint(labels: list):
    lower = {l.lower(): l for l in labels}
    for name in TYPE_LABELS:
        if name in lower:
            return lower[name]
    return None


def status_of(issue: dict) -> str:
    """`open`, `closed`, or `closed:not_planned` — the state plus its reason when there is one.

    GitHub's two states lose the distinction between "we did it" and "we are not doing it",
    which triage reads differently, so the reason is kept when the API supplies one.
    """
    state = (issue.get("state") or "").strip().lower()
    reason = (issue.get("stateReason") or "").strip().lower().replace(" ", "_")
    return f"{state}:{reason}" if state and reason else state


def owner_repo(issue: dict):
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/", issue.get("url") or "")
    return (m.group(1), m.group(2)) if m else (None, None)


def references(issue: dict) -> list:
    """Every issue number this one's body points at: `#12` and same-repo issue or PR URLs."""
    body = issue.get("body") or ""
    found = set(REF_RE.findall(body))
    owner, repo = owner_repo(issue)
    if owner and repo:
        found |= set(re.findall(URL_RE.format(owner=re.escape(owner), repo=re.escape(repo)), body))
    found.discard(str(issue.get("number")))
    return sorted(found, key=int)


def to_item(issue: dict) -> dict:
    """Map a GitHub issue onto `schemas/item.schema.json`. Identifier values are strings."""
    labels = labels_of(issue)
    return {
        "key": str(issue.get("number") or ""),
        "title": (issue.get("title") or "").strip(),
        "body": (issue.get("body") or "").strip(),
        "type_hint": type_hint(labels),
        "status": status_of(issue),
        "url": issue.get("url") or "",
        "source": SOURCE,
        "labels": labels,
        "links": references(issue),
    }


def classify_references(issue: dict) -> dict:
    """Split the body's references by the line each one sits on.

    GitHub has no link *types*, so there is nothing to read but the prose around a reference.
    A line naming a parent or an epic gives `parent`; one naming a design, spec, RFC or doc
    gives `design`; everything else is `related`. Line-scoped on purpose — a body whose first
    line says "Epic:" must not relabel every reference below it.
    """
    owner, repo = owner_repo(issue)
    url_re = re.compile(URL_RE.format(owner=re.escape(owner or "x"), repo=re.escape(repo or "x")))
    self_key = str(issue.get("number"))
    parent, design, related = None, set(), set()

    for line in (issue.get("body") or "").splitlines():
        keys = {k for k in REF_RE.findall(line) + url_re.findall(line) if k != self_key}
        if not keys:
            continue
        if PARENT_RE.search(line):
            for k in sorted(keys, key=int):
                if parent is None:
                    parent = k
                else:
                    related.add(k)
        elif DESIGN_RE.search(line):
            design |= keys
        else:
            related |= keys
    return {"parent": parent,
            "design": sorted(design, key=int),
            "related": sorted(related - design, key=int)}


def refuse_if_blocked(key: str, action: str) -> None:
    """The policy is `common.outward_refusal`, shared with every other adapter."""
    why = outward_refusal(key, action)
    if why:
        raise Usage(why)


def cmd_fetch(args) -> int:
    return emit(to_item(view(args.key, args.repo)))


def cmd_related(args) -> int:
    return emit(classify_references(view(args.key, args.repo)))


def cmd_comment(args) -> int:
    path = Path(args.body_file)
    if not path.is_file():
        raise Usage(f"no such body file: {path}")
    if not path.read_text().strip():
        raise Usage(f"{path} is empty; refusing to post an empty comment")
    refuse_if_blocked(args.key, f"comment on #{args.key}")

    out = (gh(["issue", "comment", args.key, "--body-file", str(path)], repo=args.repo) or "").strip()
    url = out.splitlines()[-1].strip() if out else ""
    m = re.search(r"#issuecomment-(\d+)", url)
    return emit({"posted": True, "id": m.group(1) if m else "", "url": url})


def cmd_transition(args) -> int:
    wanted = args.state.strip().lower()
    if wanted not in ("open", *CLOSE_REASONS):
        raise Usage(f"#{args.key} has no transition to {args.state!r}. GitHub issues are "
                    "open or closed; available: open, closed, closed:completed, "
                    "closed:not_planned")
    refuse_if_blocked(args.key, f"transition #{args.key} to {wanted!r}")

    current = status_of(view(args.key, args.repo))
    if current == wanted or (wanted == "closed" and current.startswith("closed")):
        # Already there. Saying so beats a remote call that would do nothing.
        return emit({"from": current, "to": current})

    if wanted == "open":
        gh(["issue", "reopen", args.key], repo=args.repo)
    else:
        reason = CLOSE_REASONS[wanted]
        gh(["issue", "close", args.key] + (["--reason", reason] if reason else []), repo=args.repo)
    return emit({"from": current, "to": wanted})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fetch", "related"):
        p = sub.add_parser(name)
        p.add_argument("key")
        p.add_argument("--repo", default=None, metavar="owner/name")
    p = sub.add_parser("comment")
    p.add_argument("key")
    p.add_argument("--body-file", required=True)
    p.add_argument("--repo", default=None, metavar="owner/name")
    p = sub.add_parser("transition")
    p.add_argument("key")
    p.add_argument("state")
    p.add_argument("--repo", default=None, metavar="owner/name")
    args = ap.parse_args(argv)

    return dispatch({"fetch": cmd_fetch, "related": cmd_related,
                     "comment": cmd_comment, "transition": cmd_transition}, args.cmd, args)


if __name__ == "__main__":
    sys.exit(main())
