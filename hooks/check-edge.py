#!/usr/bin/env python3
"""PostToolUse hook: check the edge after an artifact is written.

Stage 4's rule is that the check between two nodes is deterministic code that runs
*after* the write, not something the model chooses to call. This hook fires on writes
under `delivery/<ITEM-KEY>/` and checks, for the artifact just written:

  1. it parses;
  2. its sha256 matches its sentinel;
  3. it conforms to its schema;
  4. the sentinel's claimed counts match the real counts (the sentinel is a claim);
  5. it satisfies the input contract of every step that consumes it.

Every outcome is appended to `delivery/<ITEM-KEY>/trace.jsonl`, pass or fail, so the
trace shows which checks ran. On failure the hook exits 2, which returns the report to
the model as feedback. It cannot un-write the file; the orchestrator refuses to advance
on a failed edge, and the report counts items whose edges failed.

Inert outside a delivery-flow repo: no `.delivery-flow.yaml` at the git root, exit 0.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HELPERS = Path(__file__).resolve().parents[1] / "scripts" / "delivery-flow"

# Any path under delivery/<ITEM-KEY>/, in a tool input or a shell command. Checked against
# the raw payload first: a session that writes nothing there costs one regex and exits.
DELIVERY_HINT = re.compile(r"delivery/[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9]")


def _helpers():
    """Import the validator and shared helpers only once a delivery path is in play."""
    import importlib.util
    sys.path.insert(0, str(HELPERS))
    import common
    spec = importlib.util.spec_from_file_location("validate_artifact", HELPERS / "validate-artifact.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return common, mod


# Paths inside a Bash command line; quotes and redirects are stripped by the split.
BASH_PATH_RE = re.compile(r"[A-Za-z0-9._/-]*delivery/[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]+")


def written_paths(payload: dict) -> list:
    """Every path this tool call may have written, as absolute paths."""
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or ".")
    out = []
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        for key in ("file_path", "notebook_path"):
            if ti.get(key):
                out.append(Path(ti[key]))
    elif tool == "Bash":
        for token in BASH_PATH_RE.findall(ti.get("command", "")):
            out.append(Path(token))
    return [p if p.is_absolute() else (cwd / p) for p in out]


def check_artifact(path: Path, schemas: dict, common, validator) -> tuple:
    """Return (ok, problems, checks_run) for one artifact."""
    problems, ran = [], []
    schema = common.schema_for(path.name, schemas)
    if schema is None:
        return True, [], []  # not an artifact we govern

    ran.append("parse")
    doc, err = common.load_json(path)
    if err:
        return False, [err], ran

    ran.append("schema")
    validator.validate(doc, schema, "", problems)

    if not path.name.endswith(common.SENTINEL_SUFFIX):
        ran.append("sentinel")
        sentinel_path = path.with_name(path.name + common.SENTINEL_SUFFIX)
        sentinel, s_err = common.load_json(sentinel_path)
        if s_err:
            problems.append(f"no readable sentinel beside the artifact: {s_err}")
        else:
            actual_sha = common.sha256(path)
            sha_matches = sentinel.get("sha256") == actual_sha
            if not sha_matches:
                problems.append(
                    f"sentinel sha256 {str(sentinel.get('sha256'))[:12]}… does not match the file "
                    f"({actual_sha[:12]}…): the artifact changed after its sentinel was written")
            else:
                # Counts are only meaningful against the file the sentinel was written for.
                ran.append("counts")
                claimed = sentinel.get("counts") or {}
                for name, value in sorted(common.expected_counts(doc, schema).items()):
                    if name not in claimed:
                        problems.append(f"sentinel does not claim a count for {name!r}")
                    elif claimed[name] != value:
                        problems.append(
                            f"sentinel claims {name}={claimed[name]} but the file holds {value}")

        ran.append("input-contract")
        for consumer in schema.get("consumed_by", []):
            if consumer in (schema.get("consumers") or {}):
                problems += validator.consumer_problems(doc, schema, consumer)

    return not problems, problems, ran


def main() -> int:
    raw = sys.stdin.read()
    if not DELIVERY_HINT.search(raw):
        return 0  # nothing under delivery/ was touched: the common case, and the cheap one
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return 0  # not our business to fail a tool call over a malformed payload

    paths = written_paths(payload)
    if not paths:
        return 0

    common, validator = _helpers()
    schemas = common.load_schemas()
    failures = []
    for path in paths:
        item, filename = common.parse_artifact_path(path)
        if not item:
            continue
        repo = common.repo_root(path.parent if path.parent.exists() else Path(payload.get("cwd") or "."))
        if not common.is_delivery_repo(repo):
            continue
        if not path.exists():
            continue  # a command that mentioned the path without writing it

        ok, problems, ran = check_artifact(path, schemas, common, validator)
        if not ran:
            continue
        step = None
        current = repo / "delivery" / item / ".current-step"
        if current.exists():
            try:
                step = json.loads(current.read_text()).get("step")
            except (json.JSONDecodeError, ValueError, OSError):
                step = None
        summary = "ok" if ok else "; ".join(problems)
        common.append_trace(repo, item, {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "item": item,
            "step": step,
            "artifact": filename,
            "hook": "check-edge",
            "session_id": payload.get("session_id"),
            "agent_id": payload.get("agent_id"),
            "edge": {"name": "+".join(ran), "exit": 0 if ok else 1, "summary": summary[:500]},
        })
        if not ok:
            failures.append((path, problems))

    if failures:
        lines = ["Edge check failed. The artifact is on disk but the flow cannot advance past it."]
        for path, problems in failures:
            lines.append(f"\n{path}:")
            lines += [f"  - {p}" for p in problems]
        lines.append("\nFix the artifact (and its sentinel) and write it again.")
        print("\n".join(lines), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
