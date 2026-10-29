#!/usr/bin/env python3
"""Local markdown backlog adapter: a tracker that is a file in the repository.

Usage:
    local_markdown.py fetch <KEY> [--backlog <path>]
    local_markdown.py related <KEY> [--backlog <path>]
    local_markdown.py comment <KEY> --body-file <path> [--backlog <path>]
    local_markdown.py transition <KEY> <state> [--backlog <path>]
    local_markdown.py import <source> --prefix <PFX> --out <path> [--force]

    states: todo | in-progress | blocked | done | wont-do

This is the adapter to pilot with. It has no credentials, no network and no rate limit, so an
end-to-end run can be exercised — and broken on purpose — without touching anyone's tracker.

The format is one `### <KEY>: <title>` heading per item, with `Type:`, `Status:`, `Parent:`,
`Design:`, `Related:` and `Labels:` metadata lines directly beneath it and the item's body
after a blank line:

    ## Payments service

    ### DEM-3: Retries hammer the DLQ consumer
    Type: bug
    Status: todo
    Parent: DEM-1
    Related: DEM-4, DEM-5

    The consumer retries with no backoff and collapses the downstream.

    Acceptance: delays grow to a 30s cap.

    #### Comment 1 — 2026-10-28

    Posted by the flow.

`#### Comment N` blocks are excluded from `body`. They have to be: a node reading its own
earlier post-back as part of the requirement would compound its own mistakes on a rerun.

`url` is the repo-relative path plus a `#<KEY>` anchor, never an absolute one — an absolute
path differs between machines and would make two runs of the same item differ in the trace.

Exit codes: 0 fine, 2 a usage or contract error (including a refusal), 3 unreadable backlog.
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import (CONFIG_NAME, Remote, Usage, dispatch, emit,  # noqa: E402
                    is_delivery_repo, load_config, outward_refusal, repo_root)

SOURCE = "local-markdown"
DEFAULT_BACKLOG = "docs/backlog.md"
STATES = ["todo", "in-progress", "blocked", "done", "wont-do"]

ITEM_RE = re.compile(r"^###\s+([A-Za-z0-9][A-Za-z0-9._-]*)\s*:\s*(.+?)\s*$")
META_RE = re.compile(r"^(Type|Status|Parent|Design|Related|Labels)\s*:\s*(.*)$", re.I)
COMMENT_RE = re.compile(r"^####\s+Comment\s+(\d+)\b", re.I)
# A heading that ends the item: another item, or any heading at `##` or shallower.
END_RE = re.compile(r"^(###\s|##\s|#\s)")
BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*\S)\s*$")


def backlog_path(args) -> Path:
    """The backlog file: the flag if given, else `tracker.backlog` from the repo's config."""
    if args.backlog:
        return Path(args.backlog).expanduser()
    repo = repo_root(Path("."))
    if not is_delivery_repo(repo):
        raise Usage(f"{repo} has no {CONFIG_NAME}, so there is no configured backlog. "
                    "Pass --backlog, or run init-delivery-flow.py first.")
    configured = (load_config(repo).get("tracker") or {}).get("backlog") or DEFAULT_BACKLOG
    return repo / configured


def read_backlog(path: Path) -> list:
    try:
        return path.read_text().splitlines()
    except FileNotFoundError:
        raise Usage(f"no backlog at {path}. Create it, or import one with "
                    "`local_markdown.py import <source> --prefix PFX --out <path>`.")
    except OSError as e:
        raise Remote(f"{path} could not be read: {e}")


def find_item(lines: list, key: str) -> tuple:
    """(start, end, title) for the item's `###` heading block, by exact key."""
    for i, line in enumerate(lines):
        m = ITEM_RE.match(line)
        if not m or m.group(1) != key:
            continue
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if END_RE.match(lines[j]):
                end = j
                break
        return i, end, m.group(2)
    keys = sorted(m.group(1) for m in (ITEM_RE.match(l) for l in lines) if m)
    raise Usage(f"no item {key!r} in the backlog. It holds: {', '.join(keys) or 'nothing'}")


def parse_section(lines: list, start: int, end: int) -> tuple:
    """(metadata, body) for one item's lines. Metadata runs until the first non-metadata line."""
    meta, body, in_meta = {}, [], True
    i = start + 1
    while i < end:
        line = lines[i]
        m = META_RE.match(line) if in_meta else None
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
            i += 1
            continue
        if in_meta and not line.strip():
            i += 1
            continue
        in_meta = False
        if COMMENT_RE.match(line):
            # Skip the comment block: everything up to the next heading or comment.
            i += 1
            while i < end and not COMMENT_RE.match(lines[i]):
                i += 1
            continue
        body.append(line)
        i += 1
    return meta, "\n".join(body).strip()


def keys_in(value: str) -> list:
    return [k for k in re.split(r"[,\s]+", value or "") if k]


def anchor_url(path: Path, key: str) -> str:
    repo = repo_root(Path("."))
    try:
        rel = path.resolve().relative_to(repo.resolve())
    except ValueError:
        rel = Path(path.name)
    return f"{rel.as_posix()}#{key}"


def to_item(path: Path, lines: list, key: str) -> dict:
    start, end, title = find_item(lines, key)
    meta, body = parse_section(lines, start, end)
    links = sorted({*keys_in(meta.get("parent", "")), *keys_in(meta.get("design", "")),
                    *keys_in(meta.get("related", ""))} - {key})
    return {
        "key": key,
        "title": title,
        "body": body,
        "type_hint": meta.get("type") or None,
        "status": meta.get("status", ""),
        "url": anchor_url(path, key),
        "source": SOURCE,
        "labels": sorted(set(keys_in(meta.get("labels", "")))),
        "links": links,
    }


def refuse_if_blocked(key: str, action: str) -> None:
    """The policy is `common.outward_refusal`, shared with every other adapter.

    A local backlog is not somebody else's system, so this mostly reduces to the punch-out
    check — but it runs anyway. A repo that marks its own tracker external has said something
    deliberate, and an adapter is not the place to second-guess it.
    """
    why = outward_refusal(key, action)
    if why:
        raise Usage(why)


def cmd_fetch(args) -> int:
    path = backlog_path(args)
    return emit(to_item(path, read_backlog(path), args.key))


def cmd_related(args) -> int:
    path = backlog_path(args)
    lines = read_backlog(path)
    start, end, _ = find_item(lines, args.key)
    meta, _ = parse_section(lines, start, end)
    parent = keys_in(meta.get("parent", ""))
    design = sorted(set(keys_in(meta.get("design", ""))))
    related = sorted(set(keys_in(meta.get("related", ""))) - set(design))
    return emit({"parent": parent[0] if parent else None,
                 "design": design, "related": related})


def cmd_comment(args) -> int:
    body_file = Path(args.body_file)
    if not body_file.is_file():
        raise Usage(f"no such body file: {body_file}")
    text = body_file.read_text().strip()
    if not text:
        raise Usage(f"{body_file} is empty; refusing to post an empty comment")

    path = backlog_path(args)
    lines = read_backlog(path)
    start, end, _ = find_item(lines, args.key)
    refuse_if_blocked(args.key, f"comment on {args.key}")

    n = 1 + max((int(m.group(1)) for m in
                 (COMMENT_RE.match(l) for l in lines[start:end]) if m), default=0)
    stamp = datetime.now(timezone.utc).date().isoformat()
    block = ["", f"#### Comment {n} — {stamp}", "", *text.splitlines()]

    # Insert at the item's end, before whatever heading follows, keeping one trailing blank.
    tail = end
    while tail > start + 1 and not lines[tail - 1].strip():
        tail -= 1
    path.write_text("\n".join([*lines[:tail], *block, *lines[tail:]]) + "\n")
    return emit({"posted": True, "id": f"comment-{n}",
                 "url": f"{anchor_url(path, args.key)}-comment-{n}"})


def cmd_transition(args) -> int:
    wanted = args.state.strip().lower()
    if wanted not in STATES:
        raise Usage(f"{args.key} has no transition to {args.state!r}. "
                    f"Available: {', '.join(STATES)}")

    path = backlog_path(args)
    lines = read_backlog(path)
    start, end, _ = find_item(lines, args.key)
    refuse_if_blocked(args.key, f"transition {args.key} to {wanted!r}")

    meta, _ = parse_section(lines, start, end)
    current = meta.get("status", "")
    if current.lower() == wanted:
        return emit({"from": current, "to": current})

    out = list(lines)
    for i in range(start + 1, end):
        m = META_RE.match(out[i])
        if m and m.group(1).lower() == "status":
            out[i] = f"Status: {wanted}"
            break
    else:
        # No Status line: add one directly under the heading rather than at the item's end,
        # where the metadata parser would no longer see it.
        out.insert(start + 1, f"Status: {wanted}")
    path.write_text("\n".join(out) + "\n")
    return emit({"from": current, "to": wanted})


def cmd_import(args) -> int:
    """Turn an unkeyed bullet backlog into keyed items, writing a new file.

    One-way and additive: the source is read and never written. A bullet backlog is usually
    someone's notes, and rewriting notes in place to suit a tool is how you lose the notes.
    """
    source = Path(args.source).expanduser()
    out_path = Path(args.out).expanduser()
    if not source.is_file():
        raise Usage(f"no such source file: {source}")
    if out_path.exists() and not args.force:
        raise Usage(f"{out_path} already exists; pass --force to replace it")
    if out_path.resolve() == source.resolve():
        raise Usage("--out is the source file; import never rewrites the source in place")
    prefix = args.prefix.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", prefix):
        raise Usage(f"--prefix {args.prefix!r} is not a usable key prefix")

    try:
        lines = source.read_text().splitlines()
    except OSError as e:
        raise Remote(f"{source} could not be read: {e}")

    rendered = [f"# Backlog imported from {source.name}", "",
                f"Generated by local_markdown.py import. Keys are `{prefix}-N` in source order;",
                "they are identifiers, not priorities. Edit freely — import never runs again.",
                ""]
    n, pending = 0, None

    def flush():
        nonlocal pending
        if pending:
            rendered.extend(pending)
            pending = None

    for raw in lines:
        heading = re.match(r"^(#{1,6})\s+(.*\S)\s*$", raw)
        if heading:
            flush()
            rendered += [f"## {heading.group(2)}", ""]
            continue
        bullet = BULLET_RE.match(raw)
        if not bullet:
            if pending and raw.strip():
                pending += [raw.strip()]       # a continuation line is part of the item's body
            continue
        if bullet.group(1):
            if pending:
                pending += [f"- {bullet.group(2)}"]   # a sub-bullet is body, not a new item
                continue
        flush()
        n += 1
        pending = [f"### {prefix}-{n}: {bullet.group(2)}", "Status: todo", ""]
    flush()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(rendered).rstrip() + "\n")
    return emit({"imported": n, "out": str(out_path), "source": str(source)})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fetch", "related"):
        p = sub.add_parser(name)
        p.add_argument("key")
        p.add_argument("--backlog", default=None)
    p = sub.add_parser("comment")
    p.add_argument("key")
    p.add_argument("--body-file", required=True)
    p.add_argument("--backlog", default=None)
    p = sub.add_parser("transition")
    p.add_argument("key")
    p.add_argument("state")
    p.add_argument("--backlog", default=None)
    p = sub.add_parser("import")
    p.add_argument("source")
    p.add_argument("--prefix", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    return dispatch({"fetch": cmd_fetch, "related": cmd_related, "comment": cmd_comment,
                     "transition": cmd_transition, "import": cmd_import}, args.cmd, args)


if __name__ == "__main__":
    sys.exit(main())
