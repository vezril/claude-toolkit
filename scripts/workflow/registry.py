"""Which repos opted into a workflow — the registry the hooks consult instead of guessing.

Workflow-agnostic (certify-sdlc-pipeline task 1.1). This is the module the hook generalisation
in section 2 needs: a hook is handed the *session's* `cwd`, never the directory a command
actually wrote to, so it cannot learn the target repo from its payload. A shell command can
`cd`, hold the path in a variable, or use an absolute path from an unrelated cwd. Three
separate hooks were each guessing, and each missed a real write. The registry removes the
guessing.

Two things are injected rather than assumed, and they are exactly what the descriptor
supplies:

- **where the registry lives** — `~/.config/<workflow>/repos`, overridable by
  `<WORKFLOW>_REPOS`. Derived from the workflow name, which happens to reproduce
  delivery-flow's existing `DELIVERY_FLOW_REPOS` and `~/.config/delivery-flow/repos` exactly,
  so the generalisation changes no behaviour and no test fixture.
- **what counts as opted in** — a predicate, because the answer is "a file named
  `config_name` sits at the repo root" and that name is per workflow.

Keeping both out of this module is what stops a second workflow reading the first one's list
of repos, which would make hooks fire in repos that never opted into them.

Stdlib only: reached from all three hooks.
"""

import os
from pathlib import Path


def env_var(workflow: str) -> str:
    """The override variable for a workflow's registry: `delivery-flow` -> `DELIVERY_FLOW_REPOS`."""
    return workflow.upper().replace("-", "_") + "_REPOS"


def path_for(workflow: str) -> Path:
    """Where a workflow's opted-in repos are listed.

    Read at call time, not import time, so an override reaches a subprocess started after this
    module was first imported. Reading it once at import meant tests wrote to the real
    registry instead of their fixture.
    """
    default = f"~/.config/{workflow}/repos"
    return Path(os.environ.get(env_var(workflow), default)).expanduser()


def known(registry: Path, is_member) -> list:
    """Every registered repo that still satisfies `is_member`, in file order, newest last.

    Entries are re-checked rather than trusted: a repo can be deleted, moved, or have its
    config removed after registering, and a stale entry would send a hook looking for
    artifacts in a tree that no longer opts in.
    """
    out = []
    try:
        lines = Path(registry).read_text().splitlines()
    except OSError:
        return out
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        path = Path(line).expanduser()
        if path not in out and is_member(path):
            out.append(path)
    return out


def register(repo: Path, registry: Path) -> bool:
    """Record a repo. True if added, False if it was already listed.

    Appends rather than rewriting: several sessions may register concurrently, and a
    read-modify-write would lose one of them.
    """
    registry = Path(registry)
    repo = Path(repo).expanduser().resolve()
    existing = []
    try:
        existing = [l.split("#", 1)[0].strip() for l in registry.read_text().splitlines()]
    except OSError:
        pass
    if str(repo) in existing:
        return False
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("a") as f:
        f.write(f"{repo}\n")
    return True


def candidates(payload: dict, is_member, registry: Path, root_of, extra=None) -> list:
    """Every repo a hook should consider for this tool call, cwd-derived ones FIRST.

    Order matters and this order is deliberate. A caller that wants one repo should pick the
    one that actually holds the thing it is looking for — the item's `.current-step`, its open
    punch-out — not simply the head of this list. But where a caller must choose blind, the
    session's own repo is a better guess than an arbitrary registry entry, so it leads.

    `root_of` must be the caller's **repository root** finder, not "the nearest ancestor
    holding the opt-in file". The first draft of this function conflated the two and quietly
    changed behaviour: a git root without the config, under a configured parent directory,
    would have started resolving to the parent. Find the root, then ask whether it opted in —
    a repo opts in at its own root or not at all.
    """
    out = []
    for base in [Path(payload.get("cwd") or ".")] + list(extra or []):
        try:
            repo = root_of(Path(base))
        except OSError:
            continue
        if repo not in out and is_member(repo):
            out.append(repo)
    for repo in known(registry, is_member):
        if repo not in out:
            out.append(repo)
    return out
