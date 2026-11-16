"""Where a workflow's artifacts live, and whether a repo opted in at all.

Workflow-agnostic (certify-sdlc-pipeline task 1.1), and the module section 2 is blocked on:
the three hooks currently decide "is this mine?" by looking for `.delivery-flow.yaml` and
`delivery/<ITEM>/<file>`, both hard-coded. Those two strings are the entire coupling between
the hooks and one particular workflow, and they come from the descriptor.

Everything here takes the layout as arguments. Nothing defaults, because a default is how a
second workflow ends up reading the first one's artifacts — the same failure the registry
module avoids by injecting its predicate.

Stdlib only: all three hooks reach this on every tool call, including in repos that opted into
nothing, so it has to be cheap and it has to be inert.
"""

import os
import re
from functools import lru_cache
from pathlib import Path


def repo_root(start: Path) -> Path:
    """The enclosing git repository root, or `start` itself if there is none.

    Not configurable and not workflow-specific: a repo is a repo. Returning `start` rather
    than None on failure is deliberate — callers then ask `opted_in`, which answers False for
    a non-repo directory anyway, so there is no separate "not a repo" path to get wrong.
    """
    start = Path(start).resolve()
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return start


def opted_in(path: Path, config_name: str) -> bool:
    """True when the repo enclosing `path` holds `config_name` at its root.

    The opt-in file at the *root* is the whole test. A repo opts in at its own root or not at
    all, which is why this resolves the root first rather than walking up looking for the
    file: a nested repo under a configured parent has not opted in, and treating it as though
    it had would fire hooks nobody asked for.
    """
    return (repo_root(path) / config_name).exists()


@lru_cache(maxsize=None)
def _artifact_re(artifact_dir: str):
    """`<artifact_dir>/<item>/<file>` anywhere in a path.

    Cached because the hooks call `parse_artifact_path` once per candidate repo per tool call,
    and compiling a pattern per call on a hot, usually-inert path is waste.
    """
    d = re.escape(artifact_dir.strip("/"))
    return re.compile(rf"(?:^|/){d}/([A-Za-z0-9][A-Za-z0-9._-]*)/([A-Za-z0-9][A-Za-z0-9._-]*)$")


def parse_artifact_path(path, artifact_dir: str, root: Path = None):
    """(item_key, filename) for a path inside the artifact root, else (None, None).

    With no `root` this matches the default `<artifact_dir>/<item>/<file>` anywhere in the
    path, which is what the hooks relied on before the root was configurable. With a `root` it
    matches that directory specifically, so a configured vault root is recognised and an
    unrelated directory that merely happens to share the name is not.

    Passing `root` is strongly preferred. Omitting it is why artifacts under a configured root
    were silently skipped once `artifacts.root` existed: the fallback pattern cannot match a
    path that does not contain the default directory name at all.
    """
    text = str(path).replace(os.sep, "/")
    if root is not None:
        base = str(Path(root)).replace(os.sep, "/").rstrip("/")
        if text.startswith(base + "/"):
            rest = text[len(base) + 1:].split("/")
            if len(rest) == 2 and rest[0] and rest[1]:
                return rest[0], rest[1]
        return (None, None)
    m = _artifact_re(artifact_dir).search(text)
    return (m.group(1), m.group(2)) if m else (None, None)


def artifact_root(repo: Path, artifact_dir: str, cfg: dict = None) -> Path:
    """Where this repo's run artifacts live.

    `artifacts.root` in the repo's own config: absolute to put them outside the repo (a vault,
    a shared drive), relative to keep them inside it. Absent, it is `<repo>/<artifact_dir>`,
    so a repo that says nothing behaves exactly as it did before the key existed.

    `cfg` is required rather than loaded here. Reading the config is workflow-specific — the
    file name is in the descriptor — and a module that loaded it would need to know the parser
    too. Callers that have a config pass it; the delivery-flow shim loads it.
    """
    configured = ((cfg or {}).get("artifacts") or {}).get("root")
    if not configured:
        return Path(repo) / artifact_dir
    path = Path(str(configured)).expanduser()
    return path if path.is_absolute() else Path(repo) / path


def item_dir(repo: Path, item: str, artifact_dir: str, cfg: dict = None) -> Path:
    return artifact_root(repo, artifact_dir, cfg) / item
