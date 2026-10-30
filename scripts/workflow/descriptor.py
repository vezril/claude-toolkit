"""Workflow descriptors: the substrate's one piece of workflow-specific knowledge.

A workflow is a skill directory containing a `workflow.yaml`. This module loads those
descriptors and answers the only question the generic code needs to ask: *which workflow, if
any, is active in this repo?*

Why this exists. Everything in `scripts/delivery-flow/` currently hard-codes one workflow's
answers — `.delivery-flow.yaml` as the opt-in file, `delivery/` as the artifact directory, a
Python literal in `flow-status.py` as the routing table. None of that is wrong for
delivery-flow; it is just not reusable, so a second workflow would mean a second copy of the
machinery and a second place for every defect to live. The descriptor turns those answers into
data.

Stdlib only, and deliberately so: every hook in this plugin runs in whatever interpreter the
session happens to have, with no guarantee that PyYAML is installed. The parser is the same
hand-rolled subset `common.load_profiles` uses — block sequences of flat mappings, scalars,
and inline lists that must close on their own line.

Normative pair with `skills/*/workflow.yaml`: change the format and change this parser.
"""

import os
import re
from pathlib import Path

# Honours CLAUDE_PLUGIN_ROOT for the same reason `common.PLUGIN_ROOT` does, and it must agree
# with it: if one resolved from the installed plugin and the other from the checkout, the
# descriptors and the schemas they point at would come from different trees — a workflow
# validated against contracts it was not written for, with nothing to indicate it.
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT",
                                  Path(__file__).resolve().parents[2]))
DESCRIPTOR_NAME = "workflow.yaml"

# Keys a descriptor must carry. A descriptor missing one of these cannot be used to resolve a
# repo or route a step, so it is a hard error rather than a partially-working workflow.
REQUIRED = ("workflow", "config_name", "artifact_dir", "steps")

_SEQ_RE = re.compile(r"^(\s*)-\s+([A-Za-z0-9_-]+):\s*(.*)$")
_MAP_RE = re.compile(r"^(\s*)([A-Za-z0-9_-]+):\s*(.*)$")


def _scalar(value: str):
    """A YAML scalar, restricted to what a descriptor may contain.

    `null`/empty become None so an absent `optional_when` reads the same as the Python literal
    it replaces. Quotes are stripped; nothing is eval'd.
    """
    v = (value or "").strip()
    if not v or v in ("null", "~"):
        return None
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_scalar(p) for p in inner.split(",")] if inner else []
    return v


def parse(text: str, source: str = "<descriptor>") -> dict:
    """Parse a descriptor. Raises ValueError on anything it cannot represent faithfully.

    Refusing is the point. A descriptor that parsed "mostly" would route a flow with a step
    missing and still look like a successful run — the same failure the profiles parser
    guards against by rejecting an unclosed inline list.
    """
    doc, steps, cur = {}, [], None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = "" if raw.lstrip().startswith("#") else raw.split(" #")[0].rstrip()
        if not line.strip():
            continue

        if line.rstrip() == "steps:":
            cur = None
            continue

        seq = _SEQ_RE.match(line)
        if seq:
            cur = {}
            steps.append(cur)
            cur[seq.group(2)] = _scalar(seq.group(3))
            continue

        m = _MAP_RE.match(line)
        if not m:
            raise ValueError(f"{source}:{lineno}: cannot parse {line.strip()!r}")
        indent, key, value = len(m.group(1)), m.group(2), m.group(3)
        if value.lstrip().startswith("[") and not value.rstrip().endswith("]"):
            raise ValueError(
                f"{source}:{lineno}: `{key}:` opens an inline list that does not close on the "
                "same line; keep each list on one line so none is silently truncated")
        if indent and cur is not None:
            cur[key] = _scalar(value)
        else:
            cur = None
            doc[key] = _scalar(value)

    doc["steps"] = steps
    missing = [k for k in REQUIRED if not doc.get(k)]
    if missing:
        raise ValueError(f"{source}: descriptor is missing {', '.join(missing)}")
    for i, step in enumerate(steps, 1):
        for key in ("artifact", "step", "kind"):
            if not step.get(key):
                raise ValueError(f"{source}: step {i} is missing {key!r}")
        step.setdefault("optional_when", None)
    return doc


def load(path: Path) -> dict:
    """Load one descriptor, recording where it came from."""
    path = Path(path)
    doc = parse(path.read_text(), str(path))
    doc["_path"] = str(path)
    doc["_dir"] = str(path.parent)
    return doc


def descriptors(plugin_root: Path = None) -> list:
    """Every workflow the plugin defines, by workflow name.

    Found by scanning for `workflow.yaml`, so adding a workflow is adding a file rather than
    registering it somewhere a second time.
    """
    root = Path(plugin_root or PLUGIN_ROOT)
    out = [load(p) for p in sorted((root / "skills").glob("*/" + DESCRIPTOR_NAME))]
    names = [d["workflow"] for d in out]
    duplicate = {n for n in names if names.count(n) > 1}
    if duplicate:
        raise ValueError(f"two descriptors claim the same workflow name: {sorted(duplicate)}")
    return out


def for_repo(repo: Path, plugin_root: Path = None) -> list:
    """The workflows active in `repo` — those whose `config_name` sits at its root.

    A list, not one descriptor: a repo may opt into more than one workflow, and the hooks have
    to behave correctly when it does rather than picking the first. Empty means no workflow is
    active, which is the common case and must stay cheap — this is on the path of every hook
    invocation in every unrelated session.
    """
    repo = Path(repo)
    return [d for d in descriptors(plugin_root) if (repo / d["config_name"]).is_file()]


def resolve(repo: Path, plugin_root: Path = None):
    """(descriptor, error) for a repo expected to have exactly one active workflow.

    The ambiguous case is an error rather than a choice. Picking one of two silently is how a
    step gets routed by the wrong table, and the resulting run looks successful.
    """
    found = for_repo(repo, plugin_root)
    if not found:
        return None, None
    if len(found) > 1:
        names = ", ".join(sorted(d["workflow"] for d in found))
        return None, f"{repo} opts into more than one workflow ({names}); name one explicitly"
    return found[0], None


def step_table(descriptor: dict) -> list:
    """The routing table as the `(artifact, step, kind, optional_when)` tuples callers use.

    Keeps the descriptor's shape an implementation detail of this module: the existing
    consumers of `flow-status.STEPS` do not change, so the move is provably behaviour-free.
    """
    return [(s["artifact"], s["step"], s["kind"], s.get("optional_when"))
            for s in descriptor.get("steps") or []]
