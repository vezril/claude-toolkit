#!/usr/bin/env python3
"""Give a ticket its own git worktree in the code repo, once.

Usage:
    ensure-worktree.py <ITEM-KEY> [--repo <path>] [--base <ref>] [--json] [--dry-run]

One item, one worktree, one branch. Run it at the start of a ticket and again on every
resumption: it is idempotent, so the second call reports the worktree the first one made
rather than failing or making another. `git worktree list` is the record — there is no
artifact for this, because git already knows and a second source of truth would be a second
thing to get wrong.

**Why.** Three sessions sharing one checkout spent an afternoon stepping on each other: a
branch switch with uncommitted work in it, a merge left half-resolved, and one `git add -A`
that swept another session's files into a commit describing something else. A ticket that owns
its own worktree cannot do that to another ticket.

**The trap this exists to avoid.** `.delivery-flow.yaml` is often untracked — in `nx-neptune`
it is in `.git/info/exclude`, because the file carries a client's Jira project and local
paths and the repo is a public AWS checkout. A fresh worktree therefore has no config, and
`is_delivery_repo()` returns false for it, and **every hook goes inert**: no edge checks, no
punch-out enforcement, no trace. The run would look like it was working. So this script
copies the config in when it is untracked, registers the worktree so the hooks can find it,
and refuses to report success unless `is_delivery_repo()` agrees afterwards.

Exit codes: 0 the worktree is ready (made or already there), 1 refused, 2 a usage error.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONFIG_NAME, is_delivery_repo, load_config,  # noqa: E402
                    register_repo, repo_root)

WORKTREE_DIR = ".worktrees"
BRANCH_PREFIX = "delivery/"


def git(repo: Path, *args):
    """(ok, stdout) for a git command in `repo`."""
    try:
        out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                             timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    return out.returncode == 0, (out.stdout if out.returncode == 0 else out.stderr).strip()


def existing(repo: Path, branch: str):
    """The worktree already checked out on `branch`, or None.

    Read from `git worktree list` rather than from the path, so a worktree someone moved is
    still found and a stale directory with no worktree registered is not mistaken for one.
    """
    ok, out = git(repo, "worktree", "list", "--porcelain")
    if not ok:
        return None
    path = None
    for line in out.splitlines():
        if line.startswith("worktree "):
            path = Path(line[len("worktree "):])
        elif line.startswith("branch ") and path is not None:
            if line[len("branch "):].strip() in (f"refs/heads/{branch}", branch):
                return path
    return None


def excluded(repo: Path, fragment: str) -> bool:
    """Add `fragment` to `.git/info/exclude` if absent. Local, never the tracked .gitignore.

    The tracked file belongs to the project — on a public upstream it is not ours to edit for
    a local convenience. `.git/info/exclude` is per-clone and invisible to everyone else.
    """
    p = repo / ".git" / "info" / "exclude"
    try:
        if p.exists() and fragment in p.read_text().split():
            return False
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a") as f:
            f.write(f"\n# delivery-flow: per-ticket worktrees\n{fragment}\n")
        return True
    except OSError:
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base", default=None, help="ref to branch from (default: forge.base)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo))
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo", file=sys.stderr)
        return 2
    # A worktree of a worktree is legal to git and confusing to everyone, and the config copy
    # below would be copying a copy. Point this at the main checkout.
    if (repo / ".git").is_file():
        print(f"refusing: {repo} is itself a worktree. Run this against the main checkout.",
              file=sys.stderr)
        return 1

    cfg = load_config(repo)
    branch = f"{BRANCH_PREFIX}{args.item}"
    base = args.base or (cfg.get("forge") or {}).get("base") or "main"
    target = repo / WORKTREE_DIR / args.item

    found = existing(repo, branch)
    created = False
    if found is None:
        if args.dry_run:
            print(json.dumps({"item": args.item, "worktree": str(target), "branch": branch,
                              "base": base, "created": False, "dry_run": True}, indent=2))
            return 0
        excluded(repo, f"/{WORKTREE_DIR}/")
        target.parent.mkdir(parents=True, exist_ok=True)
        ok, out = git(repo, "worktree", "add", "-b", branch, str(target), base)
        if not ok:
            print(f"refusing: could not create the worktree ({out})", file=sys.stderr)
            return 1
        found, created = target, True
    elif args.dry_run:
        print(json.dumps({"item": args.item, "worktree": str(found), "branch": branch,
                          "created": False, "dry_run": True}, indent=2))
        return 0

    # The config, or the hooks are inert and nothing says so. Copied only when the repo does
    # not track it: where it *is* tracked the worktree already has it and a copy would drift.
    tracked, _ = git(repo, "ls-files", "--error-unmatch", CONFIG_NAME)
    copied = False
    if not tracked and not (found / CONFIG_NAME).exists():
        try:
            shutil.copy2(repo / CONFIG_NAME, found / CONFIG_NAME)
            copied = True
        except OSError as e:
            print(f"refusing: could not copy {CONFIG_NAME} into the worktree ({e}). Without "
                  "it the worktree is not a delivery-flow repo and every hook is inert.",
                  file=sys.stderr)
            return 1

    # The check that makes the rest trustworthy. An inert hook layer is the failure this whole
    # script is built around, so success is not reported on the strength of having tried.
    if not is_delivery_repo(found):
        print(f"refusing: {found} is not a delivery-flow repo even after setup — the hooks "
              "would be inert there, so the run would produce no edges and no trace.",
              file=sys.stderr)
        return 1
    registered = register_repo(found)

    result = {"item": args.item, "worktree": str(found), "branch": branch,
              "created": created, "config_copied": copied, "registered": registered}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{'created' if created else 'already there'}: {found}")
        print(f"  branch:   {branch}" + (f" (from {base})" if created else ""))
        print(f"  config:   {'copied in' if copied else 'present'}")
        print(f"  registry: {'added' if registered else 'already listed'}")
        print(f"\nWork this ticket in {found}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
