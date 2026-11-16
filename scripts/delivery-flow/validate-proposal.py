#!/usr/bin/env python3
"""The proposal edge: does `proposal.json` describe the change directory that exists?

Usage:
    validate-proposal.py <proposal.json> [--repo <path>] [--json]

`proposal.json` is the contract the implementation step reads; the OpenSpec change directory is
what a human reads and what `openspec archive` promotes. Two artifacts for one proposal means
they can disagree, and the interesting failure is exactly that: a convincing change directory
whose JSON omits half the work, or a JSON describing tasks the markdown never lists. So the
checks run in both directions.

`openspec validate --strict` runs as an *additional* layer when the CLI is on PATH. It is not
installed on every machine, and an edge that cannot run is not a guardrail — so the
deterministic checks here never depend on it, and its absence is recorded as skipped rather
than quietly treated as a pass.

Importable: `hooks/check-edge.py` calls `problems()` directly.

Exit codes: 0 valid, 1 at least one problem, 2 usage error.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, repo_root  # noqa: E402

REQUIRED_ARTIFACTS = ("proposal.md", "design.md", "tasks.md")
# A tasks.md checklist line, with the task id the proposal refers to it by.
TASK_LINE_RE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(T[0-9]+)\b", re.M)


def tasks_md_ids(tasks_md: Path) -> set:
    try:
        return {m.group(2) for m in TASK_LINE_RE.finditer(tasks_md.read_text())}
    except OSError:
        return set()


def inside_repo(repo: Path, candidate: str) -> bool:
    """True when a declared path stays inside the repository.

    Checked without touching the filesystem: the files a proposal names mostly do not exist
    yet, so this is about the shape of the path, not its presence.
    """
    p = Path(candidate)
    if p.is_absolute():
        try:
            p.relative_to(repo.resolve())
            return True
        except ValueError:
            return False
    return ".." not in Path(candidate).parts


def openspec_layer(repo: Path, change_id: str) -> dict:
    """The optional `openspec validate --strict` layer.

    Returns {"ran": bool, "ok": bool, "detail": str}. A missing CLI is `ran: False`, which the
    caller records as skipped — never as a pass.
    """
    if not shutil.which("openspec"):
        return {"ran": False, "ok": True, "detail": "skipped: openspec is not installed"}
    try:
        out = subprocess.run(["openspec", "validate", change_id, "--strict"],
                             cwd=repo, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return {"ran": False, "ok": True, "detail": f"skipped: could not run openspec ({e})"}
    detail = ((out.stdout or "") + (out.stderr or "")).strip()[:400]
    return {"ran": True, "ok": out.returncode == 0,
            "detail": detail or f"openspec validate exited {out.returncode}"}


def problems(path: Path, repo: Path = None) -> tuple:
    """(problems, info) for one proposal.json. Never raises on bad input.

    `repo` is the **code** repository — the one whose `openspec/changes/` this proposal is a
    contract about. **Pass it.** It is not derivable from `path`: with `artifacts.root`
    pointing outside the project, `proposal.json` sits in the vault, and walking up from it
    finds the vault or nothing at all. `hooks/check-edge.py` hands in the repo its
    `identify()` resolved, and the CLI takes `--repo`.

    The fallback inference remains for the in-repo layout, where the artifact really does live
    under the code repo. When it is wrong it is now wrong *loudly*: the missing-change-directory
    message names the absolute path it looked in, because the relative form read as "the node
    never created the directory" when the truth was "the checker looked in the wrong repo" —
    a check that blames the artifact for its own misresolution is worse than one that fails.
    """
    repo = repo or repo_root(path.parent)
    doc, err = load_json(path)
    if err:
        return [err], {}

    out = []
    change_id = doc.get("change_id") or ""
    declared = doc.get("change_path") or ""
    change_dir = (repo / declared) if declared else (repo / "openspec" / "changes" / change_id)

    if declared and not inside_repo(repo, declared):
        out.append(f"change_path {declared!r} is outside the repository")
    if not change_dir.is_dir():
        shown = declared or f"openspec/changes/{change_id}"
        out.append(f"no change directory at {shown} (looked in {change_dir})")
        return out, {"change_id": change_id, "repo": str(repo)}

    for name in REQUIRED_ARTIFACTS:
        if not (change_dir / name).is_file():
            out.append(f"the change directory has no {name}")
    deltas = sorted((change_dir / "specs").glob("*/spec.md")) if (change_dir / "specs").is_dir() else []
    if not deltas:
        out.append("the change directory has no delta spec under specs/<capability>/spec.md")

    # Both directions. A contract that omits planned work understates the change just as badly
    # as one that invents work the markdown never agreed to.
    json_ids = {t.get("id") for t in (doc.get("tasks") or []) if t.get("id")}
    md_ids = tasks_md_ids(change_dir / "tasks.md")
    for missing in sorted(json_ids - md_ids):
        out.append(f"proposal.json lists task {missing} but the change's tasks.md does not")
    for missing in sorted(md_ids - json_ids):
        out.append(f"the change's tasks.md lists task {missing} but proposal.json does not")
    if not md_ids and json_ids:
        out.append("the change's tasks.md has no `- [ ] T<n>` checklist items to match against")

    for spec in doc.get("specs_touched") or []:
        if not inside_repo(repo, spec):
            out.append(f"specs_touched names {spec!r}, which is outside the repository")
        elif not (repo / spec).is_file():
            out.append(f"specs_touched names {spec}, which does not exist")

    for task in doc.get("tasks") or []:
        tid = task.get("id") or "?"
        if not (task.get("description") or "").strip():
            out.append(f"task {tid} has an empty description")
        files = task.get("files") or []
        if not files:
            out.append(f"task {tid} names no files")
        for f in files:
            if not inside_repo(repo, f):
                out.append(f"task {tid} names {f!r}, which is outside the repository")

    layer = openspec_layer(repo, change_id)
    if layer["ran"] and not layer["ok"]:
        out.append(f"openspec validate --strict failed: {layer['detail']}")

    return out, {"change_id": change_id, "openspec_validate": layer["detail"],
                 "tasks": len(json_ids),
                 "files": len({f for t in (doc.get("tasks") or []) for f in (t.get("files") or [])})}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proposal")
    ap.add_argument("--repo", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    path = Path(args.proposal)
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 2
    repo = repo_root(Path(args.repo)) if args.repo else repo_root(path.parent)

    found, info = problems(path, repo)
    if args.json:
        print(json.dumps({"ok": not found, "problems": found, **info}, indent=2, sort_keys=True))
    elif found:
        print(f"{path}: {len(found)} problem(s)")
        for p in found:
            print(f"  - {p}")
    else:
        print(f"{path}: ok ({info.get('tasks', 0)} tasks, {info.get('files', 0)} files); "
              f"{info.get('openspec_validate', '')}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
