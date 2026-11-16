#!/usr/bin/env python3
"""The readiness gate as an edge check, not an instruction (design D4, task 4.5).

Usage:
    readiness-gate.py <readiness-verdict.json> [--repo <path>] [--json]

`skills/sdlc-orchestration/SKILL.md` used to *tell* the orchestrator to run
`scripts/lint-story.py` and `openspec validate`. Both are deterministic and neither was a
guardrail, because a model that skipped them produced no failure — the gate existed only as
long as something chose to run it. This runs on the edge instead, keyed by the artifact
written, and records a verdict either way.

What it checks, given a `readiness-verdict.json`:

  1. the change directory it names exists in the **code repo** (not beside the artifact);
  2. `scripts/lint-story.py` passes over the story set in that directory;
  3. `openspec validate <change>` passes, and a missing CLI blocks rather than passes.

Three things it deliberately does not do:

- **It does not read the verdict's judgement.** `verdict`, `attacks` and `findings` are the
  reviewer node's claim and the schema's business. Whether the deterministic gates pass is a
  separate question, which is why the verdict schema has no `gates` field — a node must not be
  the witness for its own guardrail.
- **It does not un-write anything.** A `PostToolUse` hook cannot, and D4 does not pretend
  otherwise: the verdict is recorded, and the orchestrator refuses to advance past a failed
  edge.
- **It does not pass by absence.** No stories, no change directory, or no `openspec` on PATH
  are all failures. A gate that reports success when it could not look is the inert-guardrail
  shape this project has now found five times.

Contract mirrors `scripts/delivery-flow/validate-proposal.py`: `problems(path, repo)` returns
`(problems, info)` and never raises on bad input.

Exit codes: 0 clean, 1 the gate failed, 2 usage error.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
LINT_STORY = PLUGIN_ROOT / "scripts" / "lint-story.py"


def _load(path: Path):
    try:
        return json.loads(Path(path).read_text()), None
    except OSError as e:
        return None, f"cannot read {path}: {e}"
    except (json.JSONDecodeError, ValueError) as e:
        return None, f"{path} is not valid JSON: {e}"


def story_files(change_dir: Path) -> list:
    """The story set for a change. `stories/` by convention, else any markdown story file.

    Both spellings are accepted because the playbook puts stories under
    `openspec/changes/<id>/stories/` and nothing enforces that yet. Finding none is a failure,
    not an empty pass.
    """
    stories = change_dir / "stories"
    if stories.is_dir():
        return sorted(stories.rglob("*.md"))
    return sorted(p for p in change_dir.glob("*.md")
                  if p.name not in ("proposal.md", "design.md", "tasks.md", "README.md"))


def run_lint_story(paths: list, repo: Path) -> tuple:
    """(problems, ran) from `scripts/lint-story.py`.

    Invoked as a subprocess rather than imported: it is a CLI with its own exit-code contract,
    and shelling out keeps that contract the thing under test.
    """
    if not LINT_STORY.is_file():
        return [f"lint-story.py is missing at {LINT_STORY}"], False
    argv = [sys.executable, str(LINT_STORY), *[str(p) for p in paths], "--root", str(repo)]
    try:
        out = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return [f"lint-story.py could not be run: {e}"], False
    if out.returncode == 0:
        return [], True
    detail = [l.strip() for l in (out.stdout or "").splitlines() if l.strip().startswith("-")]
    return (detail or [f"lint-story.py exited {out.returncode}"]), True


def run_openspec_validate(change_id: str, repo: Path) -> tuple:
    """(problems, ran) from `openspec validate`.

    A missing CLI is a failure. It was tempting to skip when `openspec` is absent, which is
    precisely how a gate becomes inert on the machines that lack it — the report would say the
    change-artifact form was checked when nothing looked at it.
    """
    if shutil.which("openspec") is None:
        return (["openspec is not on PATH, so the change-artifact form was not checked; "
                 "the gate blocks rather than passing by absence"], False)
    try:
        out = subprocess.run(["openspec", "validate", change_id, "--strict"],
                             cwd=str(repo), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return [f"openspec validate could not be run: {e}"], False
    if out.returncode == 0:
        return [], True
    tail = (out.stderr or out.stdout or "").strip().splitlines()
    return ([f"openspec validate {change_id}: " + (tail[-1] if tail else "failed")], True)


def problems(path: Path, repo: Path = None) -> tuple:
    """(problems, info) for one readiness-verdict.json. Never raises on bad input.

    `repo` is the **code** repository — the one whose `openspec/changes/` holds the change this
    verdict is about. Pass it. With an artifact root outside the project, walking up from the
    artifact finds the vault, which is the defect that blocked a live run at propose.
    """
    path = Path(path)
    repo = Path(repo) if repo else path.parent
    doc, err = _load(path)
    if err:
        return [err], {}

    change_id = (doc or {}).get("change") or ""
    if not change_id:
        return ["the verdict names no change"], {}

    change_dir = repo / "openspec" / "changes" / change_id
    info = {"change": change_id, "change_dir": str(change_dir)}
    if not change_dir.is_dir():
        return [f"no change directory at openspec/changes/{change_id}"], info

    out = []
    stories = story_files(change_dir)
    info["stories"] = len(stories)
    if not stories:
        out.append(f"openspec/changes/{change_id} holds no story files, so there was nothing "
                   "for lint-story.py to check")
    else:
        found, ran = run_lint_story(stories, repo)
        info["lint_story_ran"] = ran
        out += found

    found, ran = run_openspec_validate(change_id, repo)
    info["openspec_validate_ran"] = ran
    out += found
    return out, info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    found, info = problems(Path(args.path), Path(args.repo))
    if args.json:
        print(json.dumps({"path": args.path, "ok": not found, "problems": found, "info": info},
                         indent=2))
    elif found:
        print(f"READINESS GATE FAILED {args.path}")
        for p in found:
            print(f"  - {p}")
    else:
        print(f"readiness gate clean: {args.path} "
              f"({info.get('stories', 0)} stories, openspec validate passed)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
