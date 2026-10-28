#!/usr/bin/env python3
"""Create the graph structure inside an existing Obsidian vault. Additive, never destructive.

Usage:
    scaffold-vault.py [--repo <path>] [--vault <path>] [--graph-root <path>]
                      [--binding <project>] [--create] [--git] [--remote <url>]
                      [--dry-run] [--json]

The vault is somebody's own notes. A tool that reorganizes them is worse than no tool, so this
only ever adds: it creates the graph root and its folders, one `project` entity for the binding,
and the note templates. Anything already present is left byte-identical and reported as skipped,
running it twice is a no-op, and every write is checked to resolve inside the vault path.

**The vault is a local git clone; the NAS hosts the canonical bare repo.** `--create` makes the
vault directory when it is absent (without it, a missing vault is still exit 3 — creating one by
accident where a mount should have been is how you end up with two divergent vaults). `--git`
makes it a work tree: `git init`, a `.gitignore` for the Obsidian files that churn, and an
initial commit. `--remote <url>` sets `origin` and implies `--git`.

**Nothing here pushes.** A push is an outward action over a network that may not be there, and
the point of this design is that work continues when the NAS is unreachable. Commits accumulate
locally and go to the NAS when you are back on the home network.

Exit codes: 0 fine, 2 a usage or configuration error (including a path escaping the vault),
3 the vault itself is unreachable and `--create` was not given.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util

from common import CONFIG_NAME, is_delivery_repo, load_config, repo_root  # noqa: E402

_spec = importlib.util.spec_from_file_location("vault_recall", Path(__file__).parent / "vault-recall.py")
vr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vr)

FOLDERS = ("decisions", "deliveries", "incidents", "lessons", "patterns", "entities")

# Obsidian rewrites these on every pane move. Tracking them would make `dirty: true` the normal
# state of the vault, and a signal that is always on tells you nothing — recall reports dirty
# precisely so that uncommitted *notes* stand out.
GITIGNORE = """# Obsidian's volatile state. Settings and plugins stay tracked on purpose: they
# are worth syncing between machines. These churn on every pane move.
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/
.DS_Store
"""


def git(repo: Path, *args):
    """(ok, output) for a local git command. Never pushes, never fetches."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", str(repo), *args],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    return out.returncode == 0, (out.stdout or out.stderr or "").strip()

TEMPLATES = {
    "_templates/decision.md": """---
type: decision
project: {binding}
status: proposed        # proposed | accepted | superseded
date: {{{{date}}}}
superseded_by: []       # [[slug]] of the decision that replaced this one
services: []            # [[entity]] links this decision binds
refs:
  change:               # the OpenSpec change or ADR this records — link, never copy
  pr:
context: one line: what forced a decision
decision: one line: what was decided
consequences: one line: what this costs or constrains
---

## Context

## Decision

## Consequences
""",
    "_templates/delivery.md": """---
type: delivery
ticket: {{{{title}}}}
project: {binding}
status: shipped         # in-progress | shipped | reverted
date: {{{{date}}}}
domains: []             # backend, frontend, infra, data, contracts, docs
services: []            # [[entity]] links this change touched
decisions: []           # [[slug]] links to the decisions it followed
patterns: []
refs:
  pr:
  ticket:
goal: one line: what this delivered, for whom
approach: one line: how, at the level a future reader needs
outcome: one line: what actually happened
---

## What shipped

## Notes for next time
""",
    "_templates/entity.md": """---
type: entity
entity_type: service    # service | component | platform | team | project
project: {binding}
aliases: []
---

## What it is

## Who owns it
""",
    "_templates/lesson.md": """---
type: lesson
project: {binding}
domains: []
date: {{{{date}}}}
lesson: one line: what was learned
practice: one line: what to do differently
why: one line: the evidence behind it
---

## Where this came from
""",
}


def project_note(binding: str) -> str:
    return f"""---
type: entity
entity_type: project
project: {binding}
aliases: []
---

## What it is

The `{binding}` project. Deliveries, decisions and lessons scoped to it carry
`project: {binding}` in their frontmatter, which is how recall scopes a search.

## Conventions

- One note per decision, keyed by a kebab-case slug.
- One note per delivered item, keyed by its tracker key.
- Entities are stubbed on first reference and filled in later.
"""


def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--vault", default=None)
    ap.add_argument("--graph-root", default=None)
    ap.add_argument("--binding", default=None)
    ap.add_argument("--create", action="store_true",
                    help="create the vault directory when it is absent")
    ap.add_argument("--git", action="store_true",
                    help="make the vault a git work tree and commit the scaffold")
    ap.add_argument("--remote", default=None, metavar="URL",
                    help="set origin to the NAS bare repo; implies --git. Never pushes.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    cfg = {}
    repo = repo_root(Path(args.repo))
    if is_delivery_repo(repo):
        cfg = load_config(repo)
    vault_cfg = cfg.get("vault") or {}

    vault_path = args.vault or vault_cfg.get("path")
    binding = args.binding or vault_cfg.get("binding")
    if not vault_path:
        print("no vault path: pass --vault or set vault.path in " + CONFIG_NAME, file=sys.stderr)
        return 2
    if not binding:
        print("no project binding: pass --binding or set vault.binding", file=sys.stderr)
        return 2

    want_git = bool(args.git or args.remote)
    vault = Path(str(vault_path)).expanduser()
    if not vault.is_dir():
        if not args.create:
            print(f"the vault is not reachable at {vault}\n"
                  "Pass --create to make it here. Without that flag this will not create a "
                  "vault: creating one where a mount should have been is how you end up with "
                  "two divergent vaults and no way to tell which is which.", file=sys.stderr)
            return 3
        if not args.dry_run:
            vault.mkdir(parents=True, exist_ok=True)

    root_rel = args.graph_root if args.graph_root is not None else (vault_cfg.get("graph_root") or "")
    if ".." in Path(str(root_rel)).parts:
        print(f"graph_root {root_rel!r} escapes the vault; refusing", file=sys.stderr)
        return 2
    root = (vault / str(root_rel)) if root_rel else vault
    if not inside(vault, root):
        print(f"the graph root {root} is outside the vault {vault}; refusing", file=sys.stderr)
        return 2

    created, skipped = [], []

    def ensure_dir(p: Path):
        if not inside(vault, p):
            raise ValueError(f"{p} is outside the vault")
        if p.is_dir():
            skipped.append(f"{p.relative_to(vault)}/ (already a directory)")
            return
        created.append(f"{p.relative_to(vault)}/")
        if not args.dry_run:
            p.mkdir(parents=True, exist_ok=True)

    def ensure_file(p: Path, body: str):
        if not inside(vault, p):
            raise ValueError(f"{p} is outside the vault")
        if p.exists():
            skipped.append(f"{p.relative_to(vault)} (already exists, left untouched)")
            return
        created.append(str(p.relative_to(vault)))
        if not args.dry_run:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)

    try:
        ensure_dir(root)
        for folder in FOLDERS:
            ensure_dir(root / folder)
        ensure_dir(root / "_templates")
        ensure_file(root / "entities" / f"{binding}.md", project_note(binding))
        for rel, body in sorted(TEMPLATES.items()):
            ensure_file(root / rel, body.format(binding=binding))
    except ValueError as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2

    git_actions = []
    if want_git and not args.dry_run:
        tracked, _ = git(vault, "rev-parse", "--show-toplevel")
        if tracked:
            git_actions.append("already a git work tree")
        else:
            ok, msg = git(vault, "init", "-b", "main")
            if not ok:
                print(f"git init failed in {vault}: {msg}", file=sys.stderr)
                return 2
            git_actions.append("git init -b main")

        ignore = vault / ".gitignore"
        if ignore.exists():
            skipped.append(".gitignore (already exists, left untouched)")
        else:
            ignore.write_text(GITIGNORE)
            created.append(".gitignore")

        if args.remote:
            have, current = git(vault, "remote", "get-url", "origin")
            if not have:
                git(vault, "remote", "add", "origin", args.remote)
                git_actions.append(f"origin -> {args.remote}")
            elif current != args.remote:
                git_actions.append(
                    f"origin is already {current} and was left alone; it disagrees with "
                    f"{args.remote}. Change it yourself if the new one is right.")
            else:
                git_actions.append(f"origin already {current}")

        _, status = git(vault, "status", "--porcelain")
        if status:
            git(vault, "add", "-A")
            ok, msg = git(vault, "-c", "commit.gpgsign=false", "commit", "-m",
                          f"Scaffold the {binding} delivery graph")
            git_actions.append("committed the scaffold" if ok else f"commit failed: {msg}")
        else:
            git_actions.append("nothing to commit")
        # Deliberately no push: the NAS may be unreachable, and an outward action is not this
        # script's to take. Push when you are back on the home network.
    elif want_git:
        git_actions.append("(dry run: would init, write .gitignore and commit)")

    result = {"vault": str(vault), "graph_root": str(root), "binding": binding,
              "created": created, "skipped": skipped, "git": git_actions,
              "dry_run": args.dry_run}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(f"vault:      {vault}")
    print(f"graph root: {root}")
    print(f"binding:    {binding}")
    print(f"\ncreated ({len(created)}):")
    for c in created:
        print(f"  + {c}")
    if not created:
        print("  nothing — the graph is already scaffolded")
    if skipped:
        print(f"\nleft alone ({len(skipped)}):")
        for s in skipped:
            print(f"  = {s}")
    if git_actions:
        print("\ngit:")
        for g in git_actions:
            print(f"  . {g}")
        print("  . not pushed — do that from the home network")
    if args.dry_run:
        print("\n(dry run: nothing was written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
