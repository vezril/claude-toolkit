#!/usr/bin/env python3
"""Deterministic protected-path check for unattended SDLC runs.

Compares the work branch's diff against the protected-path globs in the
target repo's unattended policy file, and fails the run if any changed file
matches. This is the mechanical half of the unattended safety rule "the
pipeline never modifies CI config, its own policy, hooks/validators, release
scripts, or prompt templates" — the charter states it, this script enforces it
(same pattern as hooks/enforce-dev-pair-boundary.py for the dev pair).

Policy file format (parsed without external dependencies — keep it simple):

    protected_paths:
      - .github/workflows/**
      - .claude/unattended-policy.yml
      - hooks/**
      - scripts/**

Only the `protected_paths:` block is read here; other keys are ignored.
Glob semantics: `**` crosses directory separators, `*` and `?` do not;
patterns match the full repo-relative path.

Exit codes: 0 = diff clean; 1 = at least one protected path modified
(violations listed on stdout); 2 = usage/environment error (missing policy
file, no protected_paths block, git failure). A broken setup must fail the
run, never pass silently.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def parse_protected_paths(policy_path):
    """Extract the `protected_paths:` list without a YAML dependency.

    The key is matched at **any** indentation, because the same concept lives in two shapes:
    top-level in `templates/unattended/unattended-policy.yml`, and nested under `punch_out:` in
    `.delivery-flow.yaml` and `templates/sdlc/sdlc.yaml`. Matching only column 0 meant this
    checker could read one of them and returned an empty list for the others — caught because
    an empty list exits 2 rather than passing, which is the one design decision here worth
    keeping above all others.

    A list item belongs to the block while it is indented *more* than the key. That is what
    ends the block when a sibling key follows at the same level, without needing to know
    anything else about the file.
    """
    globs, key_indent = [], None
    for raw in policy_path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        m = re.match(r"^(\s*)protected_paths\s*:\s*$", line)
        if m:
            key_indent = len(m.group(1))
            continue
        if key_indent is None:
            continue
        item = re.match(r"^(\s*)-\s+(\S.*)$", line)
        if item and len(item.group(1)) > key_indent:
            globs.append(item.group(2).strip().strip("'\""))
            continue
        # Anything else at or left of the key's indentation closes the block. A deeper
        # non-list line is ignored rather than ending it, so a comment or a nested mapping
        # inside the block cannot truncate the list silently.
        indent = len(line) - len(line.lstrip())
        if indent <= key_indent:
            key_indent = None
    return globs


def glob_to_regex(pattern):
    out, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            if pattern[i:i + 2] == "**":
                out.append(".*")
                i += 2
                if i < len(pattern) and pattern[i] == "/":
                    i += 1
                continue
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(c))
        i += 1
    return re.compile("^" + "".join(out) + "$")


def changed_files(repo, base, head):
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", f"{base}...{head}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"error: git diff failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return [f for f in result.stdout.splitlines() if f.strip()]


def main():
    parser = argparse.ArgumentParser(description="Fail if the branch diff touches protected paths.")
    parser.add_argument("--policy", required=True, help="path to the unattended policy file")
    parser.add_argument("--base", required=True, help="base ref (e.g. origin/main)")
    parser.add_argument("--head", default="HEAD", help="head ref (default: HEAD)")
    parser.add_argument("--repo", default=".", help="repository directory (default: cwd)")
    args = parser.parse_args()

    policy_path = Path(args.policy)
    if not policy_path.is_file():
        print(f"error: policy file not found: {policy_path}", file=sys.stderr)
        return 2
    globs = parse_protected_paths(policy_path)
    if not globs:
        print(f"error: no protected_paths block in {policy_path} — refusing to pass by absence",
              file=sys.stderr)
        return 2

    patterns = [(g, glob_to_regex(g)) for g in globs]
    violations = []
    for path in changed_files(Path(args.repo), args.base, args.head):
        for g, rx in patterns:
            if rx.match(path):
                violations.append((path, g))
                break

    if violations:
        print("PROTECTED-PATH VIOLATIONS:")
        for path, g in violations:
            print(f"  - {path}  (matches: {g})")
        print("GATE: FAIL — the unattended run may not modify these files; escalate to needs-human.")
        return 1
    print(f"protected-path check: clean ({len(globs)} globs, base {args.base})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
