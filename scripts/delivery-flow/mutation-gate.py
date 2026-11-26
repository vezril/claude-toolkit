#!/usr/bin/env python3
"""The mutation gate: prove the diff's tests can actually fail.

Usage:
    mutation-gate.py [--repo <path>] [--base <ref>] [--head <ref>]
                     [--subset-template "pytest {paths}"] [--max-mutants N]
                     [--timeout S] [--json]

A review comment on a client PR said it plainly: *"making it unconditional still passes."*
A test was added, named for a conditional write, and it never reached the branch — so removing
the condition broke nothing the suite could see. That is a surviving mutant, and it is the same
defect this repo keeps finding in its own guardrails: present, successful, checking nothing.

Judging that is not a matter of opinion, which is why this is a script and not a node. Break
the production line the diff introduced, run the diff's tests, and see whether anything
notices. A mutant nothing notices is a test that is not testing.

**Scope is the diff, not the repository.** Mutating untouched code measures the whole suite's
historical coverage, which nobody asked about and which would bury the finding. The lines
mutated here are the production lines this branch added or changed.

**Production lines only.** Mutating a test and watching it fail proves nothing at all. The
classifier is imported from `hooks/enforce-dev-pair-boundary.py` rather than written again —
that definition is already mirrored in three places and a fourth copy would be one more thing
to drift.

**Mutants run on a copy.** This tool deliberately breaks source files, and it points at a
client repository that may hold uncommitted work. It copies the tree once, mutates there, and
never writes inside the repo it was pointed at.

**An unrunnable gate reports that it did not run.** If the baseline subset is not green in the
copy, there is nothing to measure: a mutant "killed" by an already-failing suite is killed by
the failure, not by the test. That case emits `ran: false` with the reason, never an empty pass.

Exit codes: 0 every mutant killed (or nothing to mutate), 1 at least one survived, 2 a usage
error, 3 the gate could not run and said so.
"""

import argparse
import ast
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import common  # noqa: E402

# The file-territory definition lives in the hook; import it rather than restate it.
_spec = importlib.util.spec_from_file_location(
    "dev_pair_boundary", HERE.parent.parent / "hooks" / "enforce-dev-pair-boundary.py")
_boundary = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_boundary)
is_test_path = _boundary.is_test_path

# Directories never worth copying, and never worth mutating.
SKIP_COPY = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache",
             ".pytest_cache", ".ruff_cache", "dist", "build", ".tox", ".idea", ".work"}

# Test files a runner can be handed. Anything else under a test directory — a committed
# `.pyc`, a snapshot, a fixture blob — is test territory but not a runnable path.
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".go", ".rb", ".scala",
                   ".java", ".kt", ".cs", ".rs", ".swift"}

COMPARISONS = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">"}
BOOL_OPS = {"and": "or", "or": "and"}
BOOL_LITERALS = {"True": "False", "False": "True"}

DEFAULT_MAX_MUTANTS = 20
DEFAULT_TIMEOUT = 300


def changed_lines(repo: Path, base: str, head: str) -> dict:
    """{path: {new-side line numbers added or changed}} for production Python files.

    `-U0` so the hunk headers bound exactly the changed lines; anything wider would mutate
    untouched code and report it against this branch.
    """
    out = subprocess.run(["git", "-C", str(repo), "diff", "-U0", f"{base}...{head}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git diff failed: {(out.stderr or '').strip()}")
    files, path, lineno = {}, None, 0
    for line in out.stdout.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            continue
        if line.startswith("@@"):
            # @@ -a,b +c,d @@
            try:
                plus = [p for p in line.split() if p.startswith("+")][0]
                lineno = int(plus[1:].split(",")[0])
            except (IndexError, ValueError):
                lineno = 0
            continue
        if path and line.startswith("+") and not line.startswith("+++"):
            if path.endswith(".py") and not is_test_path(path):
                files.setdefault(path, set()).add(lineno)
            lineno += 1
    return files


def changed_test_files(repo: Path, base: str, head: str) -> list:
    """The diff's test files, as paths a test runner can be handed.

    `--diff-filter=d` drops deletions: a deleted path passed to a runner is a collection
    error, which would read as a red baseline and stop the gate for the wrong reason.

    The extension allowlist is the other half of that. `is_test_path` answers "is this test
    territory", and a committed `tests/__pycache__/*.pyc` is — it sits under `tests/`. Handing
    that to pytest is a collection error too, and the first run of this gate hit exactly that.
    """
    out = subprocess.run(["git", "-C", str(repo), "diff", "--name-only", "--diff-filter=d",
                          f"{base}...{head}"], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git diff failed: {(out.stderr or '').strip()}")
    keep = []
    for f in out.stdout.splitlines():
        f = f.strip()
        if not f or not is_test_path(f):
            continue
        if any(seg in SKIP_COPY for seg in f.split("/")):
            continue
        if Path(f).suffix.lower() not in SOURCE_SUFFIXES:
            continue
        keep.append(f)
    return sorted(keep)


def _unconditional(line: str):
    """`if <cond>:` -> `if True:` — the mutant the review comment named.

    A one-line body (`if x: return y`) is left alone: the trailing group has to reach the end
    of the line, so the colon it would need is the wrong colon.
    """
    import re
    m = re.match(r"^(\s*)(elif|if)\s+(?!True\s*:).+?:(\s*(?:#.*)?)$", line)
    if not m:
        return None
    return f"{m.group(1)}{m.group(2)} True:{m.group(3)}"


def mutants_for_file(path: Path, rel: str, targets: set) -> list:
    """Every candidate mutant on the target lines of one file.

    Tokenising rather than pattern-matching the raw text is what keeps this off the contents
    of strings and comments: `"a == b"` in a docstring is a STRING token and never a candidate.
    """
    try:
        src = path.read_text()
    except (OSError, UnicodeDecodeError):
        return []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return []

    lines = src.splitlines(keepends=True)
    out = []

    def add(lineno, operator, new_line):
        old_line = lines[lineno - 1]
        if new_line == old_line.rstrip("\n") + ("\n" if old_line.endswith("\n") else ""):
            return
        candidate = lines[:lineno - 1] + [new_line] + lines[lineno:]
        text = "".join(candidate)
        try:
            ast.parse(text)
        except SyntaxError:
            return  # a mutant that will not compile tests nothing
        out.append({"file": rel, "line": lineno, "operator": operator,
                    "before": old_line.strip(), "after": new_line.strip(), "source": text})

    for lineno in sorted(targets):
        if lineno < 1 or lineno > len(lines):
            continue
        raw = lines[lineno - 1]
        tail = "\n" if raw.endswith("\n") else ""
        flipped = _unconditional(raw.rstrip("\n"))
        if flipped is not None:
            add(lineno, "condition-always-true", flipped + tail)

    for tok in toks:
        if tok.type not in (tokenize.OP, tokenize.NAME):
            continue
        lineno, (srow, scol), (erow, ecol) = tok.start[0], tok.start, tok.end
        if lineno not in targets or srow != erow or lineno > len(lines):
            continue
        raw = lines[lineno - 1]
        tail = "\n" if raw.endswith("\n") else ""
        body = raw.rstrip("\n")

        def swap(repl, name):
            add(lineno, name, body[:scol] + repl + body[ecol:] + tail)

        if tok.type == tokenize.OP and tok.string in COMPARISONS:
            swap(COMPARISONS[tok.string], f"comparison {tok.string}->{COMPARISONS[tok.string]}")
        elif tok.type == tokenize.NAME and tok.string in BOOL_OPS:
            swap(BOOL_OPS[tok.string], f"bool-op {tok.string}->{BOOL_OPS[tok.string]}")
        elif tok.type == tokenize.NAME and tok.string in BOOL_LITERALS:
            swap(BOOL_LITERALS[tok.string],
                 f"literal {tok.string}->{BOOL_LITERALS[tok.string]}")
        elif tok.type == tokenize.NAME and tok.string == "not":
            swap("", "drop-not")

    # Deterministic, and de-duplicated: two operators can land on the same text.
    seen, unique = set(), []
    for m in sorted(out, key=lambda m: (m["file"], m["line"], m["operator"])):
        key = (m["file"], m["line"], m["after"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(m)
    return unique


def budget(mutants: list, cap: int) -> tuple:
    """Round-robin by file, so a cap thins every file instead of dropping the last one whole."""
    if len(mutants) <= cap:
        return mutants, False
    by_file = {}
    for m in mutants:
        by_file.setdefault(m["file"], []).append(m)
    picked, order = [], sorted(by_file)
    while len(picked) < cap:
        progressed = False
        for f in order:
            if by_file[f]:
                picked.append(by_file[f].pop(0))
                progressed = True
                if len(picked) == cap:
                    break
        if not progressed:
            break
    return picked, True


def copy_tree(repo: Path) -> Path:
    dest = Path(tempfile.mkdtemp(prefix="mutation-gate-"))
    shutil.copytree(repo, dest / "w",
                    ignore=shutil.ignore_patterns(*SKIP_COPY), symlinks=True)
    return dest / "w"


def subset_command(cfg: dict, template: str, tests: list) -> tuple:
    """(command, strategy). Falls back to the whole suite rather than guessing a runner."""
    full = cfg.get("test_command") or ""
    if template and tests:
        return template.replace("{paths}", " ".join(tests)), "template"
    if tests and "pytest" in full:
        return f"{full} {' '.join(tests)}", "pytest-paths-appended"
    return full, "full-suite"


def run(command: str, cwd: Path, timeout: int) -> int:
    """Non-zero, or a timeout, counts as noticing. A timeout is a behaviour change."""
    if not command:
        return 0
    try:
        return subprocess.run(command, shell=True, cwd=str(cwd),
                              capture_output=True, text=True, timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        return 124
    except OSError:
        return 0


def gate(repo: Path, cfg: dict, base: str, head: str, template: str,
         cap: int, timeout: int) -> dict:
    try:
        targets = changed_lines(repo, base, head)
        tests = changed_test_files(repo, base, head)
    except RuntimeError as e:
        return {"ran": False, "reason": str(e)}

    if not targets:
        return {"ran": True, "reason": "the diff changes no production Python lines",
                "mutants": 0, "killed": 0, "survived": [], "changed_test_files": tests,
                "capped": False, "subset_strategy": "n/a"}

    command, strategy = subset_command(cfg, template, tests)
    if not command:
        return {"ran": False,
                "reason": "no test_command is configured, so no mutant could be judged"}
    if not tests:
        # Worth naming rather than silently running the whole suite: a branch that changes
        # production and adds no tests is the finding, and the mutants cannot speak to it.
        strategy = "full-suite (the diff adds no test files)"

    work = copy_tree(repo)
    try:
        if run(command, work, timeout) != 0:
            return {"ran": False,
                    "reason": "the baseline subset is not green in the copy, so a mutant "
                              "would be killed by the existing failure rather than by a test",
                    "command": command}

        found = []
        for rel, lines in sorted(targets.items()):
            found += mutants_for_file(work / rel, rel, lines)
        chosen, capped = budget(found, cap)

        killed, survived = 0, []
        for m in chosen:
            target = work / m["file"]
            original = target.read_text()
            target.write_text(m["source"])
            try:
                code = run(command, work, timeout)
            finally:
                target.write_text(original)
            if code != 0:
                killed += 1
            else:
                survived.append({k: m[k] for k in ("file", "line", "operator",
                                                   "before", "after")})
        return {"ran": True, "command": command, "subset_strategy": strategy,
                "changed_test_files": tests, "mutants": len(chosen),
                "candidates": len(found), "capped": capped,
                "killed": killed, "survived": survived}
    finally:
        shutil.rmtree(work.parent, ignore_errors=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base", default=None, help="defaults to the configured base branch")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--subset-template", default="",
                    help='e.g. "pytest -q {paths}"; {paths} is the diff\'s test files')
    ap.add_argument("--max-mutants", type=int, default=DEFAULT_MAX_MUTANTS)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = common.repo_root(Path(args.repo).resolve())
    cfg = common.load_config(repo) or {}
    base = args.base or (cfg.get("forge") or {}).get("base") or "main"

    result = gate(repo, cfg, base, args.head, args.subset_template,
                  args.max_mutants, args.timeout)

    if args.json:
        print(json.dumps(result, indent=2))
    elif not result["ran"]:
        print(f"DID NOT RUN — {result['reason']}")
    elif not result.get("mutants"):
        print(f"nothing to mutate — {result.get('reason', '')}")
    else:
        print(f"{result['killed']}/{result['mutants']} mutants killed"
              + (f" (capped from {result['candidates']})" if result["capped"] else ""))
        for s in result["survived"]:
            print(f"  SURVIVED {s['file']}:{s['line']}  [{s['operator']}]")
            print(f"    {s['before']}  ->  {s['after']}")
        if result["survived"]:
            print("\nEach line above was changed by this branch and broken on purpose, and no "
                  "test noticed.")

    if not result["ran"]:
        return 3
    return 1 if result.get("survived") else 0


if __name__ == "__main__":
    sys.exit(main())
