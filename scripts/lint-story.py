#!/usr/bin/env python3
"""Deterministic story-file linter — layer zero of the implementation-readiness gate.

Enforces the normative schema in
skills/spec-driven-development/references/story-schema.md. Checks FORM only
(structure, Given/When/Then grammar, task-AC mapping closure, resolvable
[Source:] references, FR/CAP traceability); judging whether criteria are
MEANINGFUL stays with the LLM/human reviewer.

Exit 0: all stories pass. Exit 1: any story fails — the readiness gate must
short-circuit and return the report to the story-planner for rewrite.
"""
import argparse
import re
import sys
from pathlib import Path

H1_RE = re.compile(r"^#\s+Story\s+(\d+)\.(\d+)\s*:\s*(\S.*)$")
STATUS_RE = re.compile(r"^Status\s*:\s*(\S.*)$", re.IGNORECASE)
STORY_STMT_RE = re.compile(
    r"\bas\s+an?\s+.+?\bI\s+want\b.+?\bso\s+that\b\s*\S", re.IGNORECASE | re.DOTALL
)
AC_ITEM_RE = re.compile(r"^[-*]\s+AC-(\d+)\s*:?\s*(.*)$")
CHECKBOX_RE = re.compile(r"^\[[ xX]\]")
TASK_RE = re.compile(r"^([-*])\s+\[[ xX]\]\s+(.*)$")
TASK_AC_REF_RE = re.compile(r"\(\s*AC\s*[:\s-]\s*([0-9,\s]+)\)", re.IGNORECASE)
SOURCE_RE = re.compile(r"\[Source:\s*([^\]#]+?)\s*(?:#\s*([^\]]+?)\s*)?\]")
TRACE_ID_RE = re.compile(r"\b((?:FR|CAP)-\d+)\b")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")


def slugify(heading):
    slug = heading.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s+", "-", slug)


def gwt_ordered(text):
    lowered = text.lower()
    g = re.search(r"\bgiven\b", lowered)
    if not g:
        return False
    w = re.search(r"\bwhen\b", lowered[g.end():])
    if not w:
        return False
    return re.search(r"\bthen\b", lowered[g.end() + w.end():]) is not None


def split_sections(lines):
    """Map normalized h2/h3 heading -> list of (lineno, line) under it."""
    sections, current = {}, None
    for i, line in enumerate(lines, 1):
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if m:
            current = m.group(2).strip().lower()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append((i, line))
    return sections


def find_section(sections, *names):
    for key, body in sections.items():
        if any(key == n or key.startswith(n) for n in names):
            return body
    return None


def lint_story(path, root, gwt_only):
    errors, warnings = [], []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    headings = [l for l in lines if l.startswith("#")]
    if not headings or not H1_RE.match(headings[0]):
        errors.append("[title] first heading must be '# Story {epic}.{n}: {title}'")

    first_h2 = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
    sections = split_sections(lines)
    status_line = next((l for l in lines[:first_h2] if STATUS_RE.match(l)), None)
    if status_line is None:
        status_body = find_section(sections, "status")
        value = next((l.strip() for _, l in status_body or [] if l.strip()), "")
        if not value:
            errors.append("[status] missing 'Status: <value>' line (or '## Status' section)")

    story_body = find_section(sections, "story")
    if story_body is None:
        errors.append("[structure] missing '## Story' section")
    elif not STORY_STMT_RE.search("\n".join(l for _, l in story_body)):
        errors.append("[story] '## Story' must match 'As a …, I want …, so that …'")

    ac_ids = {}
    ac_body = find_section(sections, "acceptance criteria")
    if ac_body is None:
        errors.append("[structure] missing '## Acceptance Criteria' section")
    else:
        blocks, current_id = [], None
        for lineno, line in ac_body:
            m = AC_ITEM_RE.match(line.strip())
            if m:
                current_id = int(m.group(1))
                if current_id in ac_ids:
                    errors.append(f"[ac] duplicate id AC-{current_id} (line {lineno})")
                ac_ids[current_id] = lineno
                blocks.append((current_id, lineno, [m.group(2)]))
            elif blocks and line.strip() and not line.lstrip().startswith(("- ", "* ")):
                blocks[-1][2].append(line.strip())
        if not blocks:
            errors.append("[ac] no acceptance criteria of the form '- AC-{n}: …'")
        for ac_id, lineno, parts in blocks:
            block = " ".join(parts)
            is_checklist = bool(CHECKBOX_RE.match(block.strip()))
            if gwt_only and is_checklist:
                errors.append(f"[ac] AC-{ac_id} is a checklist item but --gwt-only is set (line {lineno})")
            elif not is_checklist and not gwt_ordered(block):
                errors.append(
                    f"[ac] AC-{ac_id} is neither Given/When/Then (in order) "
                    f"nor a checklist item '[ ]' (line {lineno})"
                )

    tasks_body = find_section(sections, "tasks")
    covered = set()
    if tasks_body is None:
        errors.append("[structure] missing '## Tasks / Subtasks' section")
    else:
        top_tasks = [
            (lineno, TASK_RE.match(line.strip()).group(2))
            for lineno, line in tasks_body
            if TASK_RE.match(line.strip()) and not line[:1].isspace()
        ]
        if not top_tasks:
            errors.append("[tasks] no top-level checkbox tasks ('- [ ] … (AC: n)')")
        for lineno, task_text in top_tasks:
            m = TASK_AC_REF_RE.search(task_text)
            if not m:
                errors.append(f"[tasks] task has no AC reference '(AC: n)' (line {lineno})")
                continue
            refs = [int(n) for n in re.findall(r"\d+", m.group(1))]
            for ref in refs:
                if ac_ids and ref not in ac_ids:
                    errors.append(f"[tasks] task references unknown AC-{ref} (line {lineno})")
            covered.update(refs)
        for ac_id in sorted(set(ac_ids) - covered):
            errors.append(f"[tasks] AC-{ac_id} is not covered by any task")

    if find_section(sections, "dev notes") is None:
        errors.append("[structure] missing '## Dev Notes' section")
    if find_section(sections, "dev agent record") is None:
        warnings.append("[warn] no '## Dev Agent Record' section (fine pre-implementation)")

    refs_body = find_section(sections, "references")
    sources = []
    if refs_body is None:
        errors.append("[structure] missing 'References' section (h2 or h3)")
    else:
        for lineno, line in refs_body:
            for m in SOURCE_RE.finditer(line):
                sources.append((lineno, m.group(1).strip(), (m.group(2) or "").strip()))
        if not sources:
            errors.append("[refs] References section has no '[Source: path#anchor]' entries")
    for lineno, rel, anchor in sources:
        target = (root / rel).resolve()
        if not target.is_file():
            errors.append(f"[refs] source file not found: {rel} (line {lineno})")
            continue
        if anchor:
            content = target.read_text(encoding="utf-8", errors="replace")
            slugs = {
                slugify(HEADING_RE.match(l).group(1))
                for l in content.splitlines()
                if HEADING_RE.match(l)
            }
            if slugify(anchor) not in slugs and anchor.lower() not in content.lower():
                errors.append(
                    f"[refs] anchor '#{anchor}' matches no heading or text in {rel} (line {lineno})"
                )

    trace_ids = sorted(set(TRACE_ID_RE.findall(text)))
    if not trace_ids:
        errors.append("[trace] story mentions no FR-{n}/CAP-{n} requirement ID")
    else:
        prd_like = [
            (root / rel).resolve()
            for _, rel, _ in sources
            if re.search(r"prd|srs|spec", Path(rel).name, re.IGNORECASE)
            and (root / rel).is_file()
        ]
        if prd_like:
            corpus = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in prd_like)
            for tid in trace_ids:
                if tid not in corpus:
                    errors.append(f"[trace] {tid} not found in any PRD-like source referenced by this story")
        else:
            warnings.append(f"[warn] cannot verify {', '.join(trace_ids)} — no PRD-like file among sources")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Lint story files against the normative schema.")
    parser.add_argument("paths", nargs="+", help="story .md files or directories of them")
    parser.add_argument("--root", default=".", help="base dir for resolving [Source:] paths (default: cwd)")
    parser.add_argument("--gwt-only", action="store_true", help="reject checklist-form ACs")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = []
    for p in map(Path, args.paths):
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"error: no such file or directory: {p}", file=sys.stderr)
            return 2
    if not files:
        print("error: no story files found", file=sys.stderr)
        return 2

    failed = 0
    for f in files:
        errors, warnings = lint_story(f, root, args.gwt_only)
        print(f"{'FAIL' if errors else 'PASS'} {f}")
        for e in errors:
            print(f"  - {e}")
        for w in warnings:
            print(f"  ! {w}")
        failed += bool(errors)

    print(f"\n{len(files)} storie(s): {len(files) - failed} pass, {failed} fail")
    if failed:
        print("GATE: FAIL — return this report to the story-planner for rewrite; "
              "do not proceed to LLM review or implementation.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
