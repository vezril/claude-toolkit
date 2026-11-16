"""Artifact schemas: load a directory of them, resolve one by file name, count its fields.

Workflow-agnostic (certify-sdlc-pipeline task 1.1). Moved out of
`scripts/delivery-flow/common.py` unchanged. Nothing here knows what a delivery item is — it
reads `*.schema.json` files, matches a file name to one, and evaluates the `counts`
expressions a sentinel is checked against.

Named `schema` rather than `schemas` on purpose: the plugin has a top-level `schemas/`
directory, and a module sharing that name invites an import that resolves to the wrong thing
depending on `sys.path` order.

As with pricing, `load` takes a required directory. Which schemas apply is a property of the
workflow — the descriptor's `schemas:` pointer — and a default here would quietly validate a
second workflow's artifacts against this one's contracts.

Stdlib only: this is the hot path of `hooks/check-edge.py`.
"""

import fnmatch
import json
from pathlib import Path


def load(schema_dir: Path) -> dict:
    """Map artifact file name -> schema, for every `*.schema.json` in a directory.

    Most artifacts are one fixed file name. A sentinel is not — there is one per artifact —
    so `*.sentinel.json` declares a glob as its `artifact` and `schema_for` resolves it.
    """
    schema_dir = Path(schema_dir)
    out = {}
    for p in sorted(schema_dir.glob("*.schema.json")):
        schema = json.loads(p.read_text())
        schema["_path"] = str(p)
        out[schema["artifact"]] = schema
    return out


def for_name(filename: str, schemas: dict):
    """The schema for an artifact file name, by exact name then by glob.

    The glob fallback is what makes a *set* of artifacts checkable rather than only fixed file
    names. Globs are matched longest-first so a specific pattern always beats a broad one: an
    artifact and its sentinel are both `<name>.json`-shaped, and the sentinel must not resolve
    to the artifact's schema.
    """
    if filename in schemas:
        return schemas[filename]
    for key in sorted((k for k in schemas if "*" in k), key=len, reverse=True):
        if fnmatch.fnmatch(filename, key):
            return schemas[key]
    return None


def count_expr(doc, expr: str) -> int:
    """Evaluate a count expression: 'epics[]' or 'epics[].stories[]'.

    Each '<key>[]' segment descends into a list; the result is the number of items at
    the deepest level, summed across the branches above it.
    """
    parts = [p for p in expr.split(".") if p]
    nodes = [doc]
    total = 0
    for i, part in enumerate(parts):
        if not part.endswith("[]"):
            raise ValueError(f"count expression segment must end with []: {part!r}")
        key = part[:-2]
        nxt = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            value = node.get(key)
            if isinstance(value, list):
                if i == len(parts) - 1:
                    total += len(value)
                else:
                    nxt.extend(value)
        nodes = nxt
    return total


def expected_counts(doc, schema: dict) -> dict:
    return {name: count_expr(doc, expr) for name, expr in (schema.get("counts") or {}).items()}
