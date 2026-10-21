"""Shared helpers for delivery-flow scripts and hooks. Standard library only.

Everything here answers one of four questions: where is the repo, is this a
delivery-flow repo at all, which artifact is this path, and what does its schema say.
"""

import hashlib
import json
import os
import re
from pathlib import Path

CONFIG_NAME = ".delivery-flow.yaml"
SENTINEL_SUFFIX = ".sentinel.json"
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parents[2]))
SCHEMA_DIR = PLUGIN_ROOT / "schemas"

# delivery/<ITEM-KEY>/<artifact>, the only place artifacts live.
ARTIFACT_RE = re.compile(r"(?:^|/)delivery/([A-Za-z0-9][A-Za-z0-9._-]*)/([A-Za-z0-9][A-Za-z0-9._-]*)$")


def repo_root(start: Path) -> Path:
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return start


def is_delivery_repo(path: Path) -> bool:
    """A delivery-flow repo has the config at its root. Everything is inert otherwise."""
    return (repo_root(path) / CONFIG_NAME).exists()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_artifact_path(path):
    """Return (item_key, filename) for a path inside delivery/<ITEM>/, else (None, None)."""
    m = ARTIFACT_RE.search(str(path).replace(os.sep, "/"))
    return (m.group(1), m.group(2)) if m else (None, None)


def load_schemas(schema_dir: Path = None) -> dict:
    """Map artifact file name -> schema. The sentinel schema is keyed by its suffix."""
    schema_dir = schema_dir or SCHEMA_DIR
    out = {}
    for p in sorted(schema_dir.glob("*.schema.json")):
        schema = json.loads(p.read_text())
        schema["_path"] = str(p)
        out[schema["artifact"]] = schema
    return out


def schema_for(filename: str, schemas: dict):
    if filename.endswith(SENTINEL_SUFFIX):
        return schemas.get("*.sentinel.json")
    return schemas.get(filename)


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


def load_json(path: Path):
    """Return (doc, error). Never raises on bad input: the caller reports it as a failure."""
    try:
        return json.loads(path.read_text()), None
    except FileNotFoundError:
        return None, f"{path} does not exist"
    except json.JSONDecodeError as e:
        return None, f"{path} is not valid JSON: {e}"
    except OSError as e:  # unreadable, a directory, a broken link
        return None, f"{path} could not be read: {e}"


def load_config(repo: Path) -> dict:
    """Parse `.delivery-flow.yaml`. Supported subset: top-level `key: value`, one level of
    nesting, inline lists `[a, b]`, and block sequences. Standard library only, so a hook
    can read it on a machine with no PyYAML."""
    text = (repo / CONFIG_NAME).read_text()
    root, section, pending = {}, None, None

    def scalar(v):
        v = v.strip()
        if v in ("", "null", "~"):
            return None
        if v in ("true", "True"):
            return True
        if v in ("false", "False"):
            return False
        if v.startswith("[") and v.endswith("]"):
            return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        if v[0] == v[-1] and v[0] in "'\"" and len(v) >= 2:
            return v[1:-1]
        return v

    for raw in text.splitlines():
        line = "" if raw.lstrip().startswith("#") else raw.split(" #")[0].rstrip()
        if not line.strip():
            continue
        m = re.match(r"^(\s*)-\s+(.+)$", line)
        if m and pending is not None:
            pending.append(scalar(m.group(2)))
            continue
        m = re.match(r"^(\s*)([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        indent, key, value = len(m.group(1)), m.group(2), m.group(3)
        target = root if indent == 0 else section
        if target is None:
            continue
        if value == "":
            nxt = {}
            target[key] = nxt
            if indent == 0:
                section = nxt
            # a key with no value may open either a mapping or a sequence; the next
            # line decides, and a sequence replaces the empty mapping
            pending = _Pending(target, key)
        else:
            target[key] = scalar(value)
            pending = None
            if indent == 0:
                section = root
    return _resolve(root)


class _Pending(list):
    """A key whose value is still unknown: a block sequence appends here, and if nothing
    appends, it stays the empty mapping the parser first assumed."""

    def __init__(self, owner, key):
        super().__init__()
        self.owner, self.key = owner, key

    def append(self, item):
        super().append(item)
        self.owner[self.key] = list(self)


def _resolve(node):
    if isinstance(node, dict):
        return {k: _resolve(v) for k, v in node.items()}
    return node


def trace_path(repo: Path, item: str) -> Path:
    return repo / "delivery" / item / "trace.jsonl"


def append_trace(repo: Path, item: str, record: dict) -> None:
    p = trace_path(repo, item)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
