#!/usr/bin/env python3
"""Delivery recall: what has this project already decided, built and learned?

Usage:
    vault-recall.py <ITEM-KEY> [--repo <path>] [--mode solutioning|implementation]
                     [--story <id>] [--vault <path>] [--graph-root <path>] [--stdout]

**This is a script, not a node, and that is a deliberate departure** from
`extend-vault-graphrag-projects` task 3.4, which planned to certify recall as a prompt. The
algorithm that change specifies is arithmetic — 3 per same project, 3 per shared service link,
2 per shared domain (3 in implementation mode), 1 per keyword hit; drop below 3; tie-break by
date; cap at 5/5/3/3; frontmatter only; never advise. A prompt would need an eval suite and a
95% pass bar to approximate what Python computes exactly, and it would be a non-deterministic
step feeding a node, needing an edge of its own. As a script it *is* an edge. See the design
decision D1 in `openspec/changes/add-vault-delivery-memory/design.md`.

What it cannot do is notice relevance the schema never anticipated. That is why every run
reports its full search coverage: a thin result with the scan behind it is honest, and if
traversal provably misses what people needed, that is the evidence for adding a semantic layer.

**Unreachable is not empty.** A missing graph root makes scanning find nothing — identical at the
output to a vault with no relevant notes. So reachability is checked first and fails loudly,
because "no memory was applied" and "memory was consulted and had nothing" are different facts
about a run.

**The vault is a local git clone; the NAS hosts the canonical bare repo.** It used to be read
straight off an AFP mount, which meant recall failed outright whenever the laptop was away from
the home network — the mount being down is not a good enough reason to stop work. Reading a
local clone removes that dependency, and introduces a subtler one in its place: a clone can be
weeks behind without looking it, so recall could serve stale memory as current. A silent wrong
answer is worse than a loud missing one, so every run reports its sync state — HEAD, dirty,
ahead/behind, and how long since this clone last exchanged commits with the NAS — and sets
`stale` against `punch_out.vault_staleness_days`.

**No network call happens here.** Sync state is read from the clone's own files and reflog. A
recall step that hung waiting on an unreachable NAS would reintroduce exactly the dependency
this design removes.

Exit codes: 0 recalled (with or without matches, stale or fresh), 2 a usage or configuration
error (including an unimplemented backend), 3 the vault is unreachable — and no artifact is
written in that case.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONFIG_NAME, artifact_root, is_delivery_repo, load_config, load_json, repo_root  # noqa: E402

UTC = timezone.utc
GIT_TIMEOUT = 15
# Days since this clone last synced with the NAS before recall calls its memory stale. A
# ceiling, like the punch-out ones, so it is tuned from real runs rather than edited in code.
DEFAULT_STALENESS_DAYS = 14

# The scoring, straight from the spec. Constants in one place so they can be retuned against
# real recalls rather than hunted through the code.
SCORE_SAME_PROJECT = 3
SCORE_SHARED_SERVICE = 3
SCORE_SHARED_DOMAIN_SOLUTIONING = 2
SCORE_SHARED_DOMAIN_IMPLEMENTATION = 3
SCORE_KEYWORD = 1
THRESHOLD = 3
CAPS = {"decisions": 5, "deliveries": 5, "lessons": 3, "patterns": 3}
FOLDERS = {"decisions": "decisions", "deliveries": "deliveries",
           "lessons": "lessons", "patterns": "patterns"}
# The payload lines recall shows verbatim, per note type. Nothing else is read from a note.
PAYLOAD = {
    "decision": ("context", "decision", "consequences", "status"),
    "delivery": ("goal", "approach", "outcome", "status"),
    "lesson": ("lesson", "practice", "why"),
    "pattern": ("shape", "detection", "mitigation"),
}
MD_LINE_CAP = 80

STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "when", "then", "than",
    "have", "has", "had", "are", "was", "were", "will", "would", "should", "could", "can",
    "not", "but", "all", "any", "its", "it's", "our", "their", "there", "here", "what",
    "which", "who", "whom", "how", "why", "add", "adds", "added", "fix", "fixes", "fixed",
    "make", "makes", "made", "use", "uses", "used", "need", "needs", "needed", "also",
    "after", "before", "during", "while", "does", "done", "doing", "only", "some", "more",
    "most", "such", "very", "just", "like", "over", "under", "again", "still", "about",
}
MIN_KEYWORD_LEN = 4


class Unreachable(Exception):
    """The graph root is not there. Not the same as nothing matching."""


class Usage(Exception):
    pass


def keywords(*texts) -> list:
    """The keyword set, defined rather than improvised.

    Scoring awards a point per keyword hit, so an undefined keyword set makes the score
    unreproducible — and reproducibility is the whole argument for doing this in code.
    """
    out = []
    for token in re.split(r"[^A-Za-z0-9]+", " ".join(t for t in texts if t).lower()):
        if len(token) >= MIN_KEYWORD_LEN and token not in STOP_WORDS and token not in out:
            out.append(token)
    return sorted(out)


def parse_frontmatter(path: Path) -> dict:
    """The YAML subset Obsidian frontmatter actually uses: scalars, inline lists, block lists.

    Body text is never read — recall shows frontmatter payload lines and a wikilink, nothing
    else, so a note's narrative cannot leak into a machine-consumed artifact.
    """
    try:
        text = path.read_text()
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out, pending = {}, None
    for raw in text[3:end].splitlines():
        line = raw.split(" #")[0].rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^(\s*)-\s+(.*)$", line)
        if m and pending:
            out[pending].append(_scalar(m.group(2)))
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value == "":
            out[key] = []
            pending = key
        else:
            out[key] = _scalar(value)
            pending = None
    return out


def _scalar(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def as_list(value) -> list:
    if value is None:
        return []
    return [str(v) for v in value] if isinstance(value, list) else [str(value)]


def link_names(value) -> set:
    """`[[orders-api]]` -> `orders-api`, so a link and a bare name compare equal."""
    out = set()
    for v in as_list(value):
        out.add(re.sub(r"^\[\[|\]\]$", "", str(v).strip()))
    return {v for v in out if v}


def graph_root(cfg: dict, vault_override=None, root_override=None) -> Path:
    vault = cfg.get("vault") or {}
    backend = (vault.get("backend") or "filesystem").lower()
    if backend != "filesystem":
        raise Usage(f"vault.backend {backend!r} is not implemented; only `filesystem` is")
    path = vault_override or vault.get("path")
    if not path:
        raise Usage("the binding names no vault.path, so there is no graph to read")
    root = root_override or vault.get("graph_root") or ""
    if ".." in Path(str(root)).parts:
        raise Usage(f"vault.graph_root {root!r} escapes the vault")
    return (Path(str(path)).expanduser() / str(root)).resolve() if root \
        else Path(str(path)).expanduser().resolve()


def check_reachable(root: Path) -> None:
    """Fail loudly before scanning. A missing graph root looks exactly like an empty vault.

    The vault is a local clone now, so "unreachable" no longer means an unmounted NAS — it means
    the clone is not there at all, which is still a failure and still must not read as a cold
    start. What the NAS being down used to tell us loudly is now reported by `sync_state`.
    """
    if not root.exists():
        raise Unreachable(f"the vault graph root is not there: {root}\n"
                          "The vault is a local clone; if this is a new machine it has not been "
                          "cloned yet. Recall is refusing to report an empty result that would "
                          "be indistinguishable from a working one.")
    if not root.is_dir():
        raise Unreachable(f"the vault graph root is not a directory: {root}")
    try:
        next(root.iterdir(), None)
    except OSError as e:
        raise Unreachable(f"the vault graph root cannot be read: {root} ({e})")


def ceiling_days(cfg: dict):
    """`punch_out.vault_staleness_days`, or the default. `null` disables the staleness check."""
    punch = cfg.get("punch_out") or {}
    if "vault_staleness_days" not in punch:
        return DEFAULT_STALENESS_DAYS
    value = punch.get("vault_staleness_days")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise Usage(f"punch_out.vault_staleness_days must be a whole number of days or null, "
                    f"not {value!r}")


def vault_dir(cfg: dict, vault_override=None) -> Path:
    """The vault root — the git work tree — as distinct from the graph root inside it."""
    path = vault_override or (cfg.get("vault") or {}).get("path")
    if not path:
        raise Usage("the binding names no vault.path, so there is no graph to read")
    return Path(str(path)).expanduser().resolve()


def _git(repo: Path, *args):
    """(stdout, ok) for a git command. Never raises, and never touches the network."""
    try:
        out = subprocess.run(["git", "-C", str(repo), *args],
                             capture_output=True, text=True, timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return "", False
    return out.stdout.strip(), out.returncode == 0


def last_fetch(repo: Path):
    """When this clone last *learned* from its remote, from the mtime of `.git/FETCH_HEAD`.

    Deliberately a fetch and not "any contact with the remote". A push proves the NAS was
    reachable, but it only sends — it teaches this clone nothing, so a laptop that pushed an
    hour ago can still be a month behind what the other Mac decided. The question staleness
    answers is "might another machine hold decisions this recall could not see", and only a
    fetch moves that answer.

    `FETCH_HEAD` is written by every fetch, including the one inside a pull, and by nothing
    else — the remote-tracking ref's reflog would be ambiguous because a push updates it too.
    It is a local file, so this needs no network.
    """
    git_dir, ok = _git(repo, "rev-parse", "--absolute-git-dir")
    if not ok or not git_dir:
        return None
    try:
        return datetime.fromtimestamp((Path(git_dir) / "FETCH_HEAD").stat().st_mtime, UTC)
    except OSError:
        return None


def sync_state(repo: Path, cfg: dict) -> dict:
    """What can be said about this clone's freshness, from the clone alone.

    No network call. A recall step that hung waiting on an unreachable NAS would reintroduce the
    exact dependency this design removes, and a step that silently served month-old memory as
    current would be worse than one that failed — so the facts go in the artifact and the trace,
    and `stale` is set against a configured ceiling.
    """
    ceiling = ceiling_days(cfg)
    state = {"path": str(repo), "tracked": False, "head": None, "head_date": None,
             "dirty": None, "upstream": None, "remote": None, "ahead": None, "behind": None,
             "last_sync": None, "days_since_sync": None, "stale": False,
             "staleness_ceiling_days": ceiling, "notes": []}

    toplevel, ok = _git(repo, "rev-parse", "--show-toplevel")
    if not ok or not toplevel:
        state["notes"].append(
            "the vault is not a git work tree, so there is no sync state to report and no "
            "way to tell whether another machine has newer notes")
        return state
    state["tracked"] = True

    head, ok = _git(repo, "rev-parse", "--short", "HEAD")
    state["head"] = head if ok and head else None
    if not state["head"]:
        state["notes"].append("the vault repository has no commits yet")

    date, ok = _git(repo, "log", "-1", "--format=%cI")
    state["head_date"] = date if ok and date else None

    porcelain, ok = _git(repo, "status", "--porcelain")
    state["dirty"] = bool(porcelain) if ok else None
    if state["dirty"]:
        state["notes"].append("the vault has uncommitted changes, so notes written here are not "
                              "yet durable and cannot reach the other machine")

    state["remote"], _ = _git(repo, "remote", "get-url", "origin")
    state["remote"] = state["remote"] or None
    configured = (cfg.get("vault") or {}).get("remote")
    if configured and state["remote"] and str(configured) != state["remote"]:
        state["notes"].append(
            f"vault.remote in the config is {configured!r} but origin is "
            f"{state['remote']!r}; one of them is wrong")

    upstream, ok = _git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    state["upstream"] = upstream if ok and upstream else None
    if state["upstream"]:
        counts, ok = _git(repo, "rev-list", "--left-right", "--count",
                          f"HEAD...{state['upstream']}")
        if ok and counts:
            parts = counts.split()
            if len(parts) == 2 and all(p.isdigit() for p in parts):
                state["ahead"], state["behind"] = int(parts[0]), int(parts[1])
    else:
        state["notes"].append("the vault branch tracks no upstream, so ahead/behind counts "
                              "against the NAS are unknown")

    stamp = last_fetch(repo)
    if stamp:
        state["last_sync"] = stamp.isoformat()
        days = (datetime.now(UTC) - stamp).days
        state["days_since_sync"] = days
        if ceiling is not None and days > ceiling:
            state["stale"] = True
            state["notes"].append(
                f"this clone last synced with the NAS {days} days ago, over the "
                f"{ceiling}-day ceiling: another machine may hold newer decisions that this "
                "recall could not see")
    else:
        state["notes"].append("no record of this clone ever fetching from its remote, so "
                              "whether another machine holds newer decisions is unknown")
    if state["ahead"]:
        state["notes"].append(
            f"{state['ahead']} local commit(s) have not reached the NAS; push when you are "
            "back on the home network")
    return state


def score_note(fm: dict, project: str, entities: set, domains: set, words: list,
               kind: str, mode: str) -> tuple:
    """(score, reasons) for one note, by the specified weights."""
    score, why = 0, []
    if project and str(fm.get("project") or "").strip() == project:
        score += SCORE_SAME_PROJECT
        why.append(f"same project (+{SCORE_SAME_PROJECT})")

    shared = link_names(fm.get("services")) | link_names(fm.get("components"))
    overlap = sorted(shared & entities)
    if overlap:
        score += SCORE_SHARED_SERVICE * len(overlap)
        why.append(f"shared services {', '.join(overlap)} (+{SCORE_SHARED_SERVICE} each)")

    per_domain = (SCORE_SHARED_DOMAIN_IMPLEMENTATION if mode == "implementation"
                  else SCORE_SHARED_DOMAIN_SOLUTIONING)
    dom = sorted(set(as_list(fm.get("domains"))) & domains)
    if dom:
        score += per_domain * len(dom)
        why.append(f"shared domains {', '.join(dom)} (+{per_domain} each)")

    payload_text = " ".join(str(fm.get(k) or "") for k in PAYLOAD.get(kind, ())).lower()
    hits = sorted({w for w in words if w in payload_text})
    if hits:
        score += SCORE_KEYWORD * len(hits)
        why.append(f"keywords {', '.join(hits)} (+{SCORE_KEYWORD} each)")
    return score, why


def collect(root: Path, bucket: str, kind: str, project: str, entities: set, domains: set,
            words: list, mode: str) -> tuple:
    """(kept, scanned, dropped, superseded_skipped) for one folder."""
    folder = root / FOLDERS[bucket]
    if not folder.is_dir():
        return [], 0, 0, []

    kept, scanned, dropped, superseded = [], 0, 0, []
    for note in sorted(folder.glob("*.md")):
        scanned += 1
        fm = parse_frontmatter(note)
        score, _why = score_note(fm, project, entities, domains, words, kind, mode)
        if score < THRESHOLD:
            dropped += 1
            continue
        # Only accepted decisions are in force. A superseded one that would have matched is
        # reported in coverage with its replacement, so it is visible without being quoted
        # back as current.
        if kind == "decision" and str(fm.get("status") or "").strip() != "accepted":
            repl = ", ".join(sorted(link_names(fm.get("superseded_by")))) or "no replacement named"
            superseded.append(f"{note.stem} (status {fm.get('status') or 'unset'}; → {repl})")
            continue
        kept.append({
            "note": note.stem,
            "link": f"[[{note.stem}]]",
            "score": score,
            "date": str(fm.get("date") or "") or None,
            "project": str(fm.get("project") or "") or None,
            "payload": {k: str(fm[k]) for k in PAYLOAD.get(kind, ()) if fm.get(k)},
        })
    # Highest score first, then newest, then by name. Every key is explicit, because a stable
    # order is what makes "two runs are byte-identical" true rather than lucky.
    kept.sort(key=lambda m: (-m["score"], _date_key(m["date"]), m["note"]))
    return kept, scanned, dropped, superseded


def _date_key(value):
    """Newest first, with undated notes last."""
    try:
        return (0, -datetime.fromisoformat(str(value)).timestamp())
    except (TypeError, ValueError):
        return (1, 0)


def recall(item: dict, triage: dict, cfg: dict, mode: str, story: str = None,
           vault_override=None, root_override=None) -> dict:
    root = graph_root(cfg, vault_override, root_override)
    check_reachable(root)
    sync = sync_state(vault_dir(cfg, vault_override), cfg)

    project = str((cfg.get("vault") or {}).get("binding") or "").strip()
    if not project:
        raise Usage("vault.binding names no project, so there is nothing to scope recall to")

    entities = link_names((triage or {}).get("services")) | link_names((item or {}).get("services"))
    domains = set(as_list((triage or {}).get("domains")))
    words = keywords((item or {}).get("title"), (triage or {}).get("summary"))

    buckets, scanned, dropped, superseded, capped = {}, {}, 0, [], 0
    for bucket, kind in (("decisions", "decision"), ("deliveries", "delivery"),
                         ("lessons", "lesson"), ("patterns", "pattern")):
        kept, n, drop, sup = collect(root, bucket, kind, project, entities, domains, words, mode)
        capped += max(0, len(kept) - CAPS[bucket])
        buckets[bucket] = kept[:CAPS[bucket]]
        scanned[bucket], dropped, superseded = n, dropped + drop, superseded + sup

    return {
        "item": (item or {}).get("key") or (triage or {}).get("item") or "",
        "project": project,
        "mode": mode,
        "story": story,
        "matched": any(buckets.values()),
        **buckets,
        "vault": sync,
        "coverage": {
            "entities": sorted(entities),
            "keywords": words,
            "domains": sorted(domains),
            "scanned": scanned,
            "dropped": dropped,
            "capped": capped,
            "superseded_skipped": sorted(superseded),
        },
    }


def render_md(doc: dict) -> str:
    """The human rendering. Capped at 80 lines; facts only, by construction."""
    L = [f"# Project context — {doc['item']} ({doc['project']}, {doc['mode']})", ""]
    vsync = doc.get("vault") or {}
    if vsync.get("stale"):
        # First line, before any recalled content: a reader who stops here must still learn
        # that what follows may be out of date.
        L += [f"> **Stale memory.** This vault clone last synced with the NAS "
              f"{vsync.get('days_since_sync')} days ago, over the "
              f"{vsync.get('staleness_ceiling_days')}-day ceiling. Newer decisions may exist on "
              f"another machine and are not reflected below.", ""]
    if not doc["matched"]:
        L += ["Nothing in the vault matched this project context.", ""]
    for bucket, title in (("decisions", "Decisions in force"), ("deliveries", "Related deliveries"),
                          ("lessons", "Lessons"), ("patterns", "Patterns")):
        L.append(f"## {title}")
        L.append("")
        if not doc[bucket]:
            L.append("- none above the threshold")
        for m in doc[bucket]:
            L.append(f"- {m['link']} (score {m['score']})")
            for k, v in m["payload"].items():
                L.append(f"  - {k}: {v}")
        L.append("")
    c = doc["coverage"]
    L += ["## Search coverage", "",
          f"- entities: {', '.join(c['entities']) or 'none'}",
          f"- keywords: {', '.join(c['keywords']) or 'none'}",
          f"- domains: {', '.join(c['domains']) or 'none'}",
          f"- notes scanned: " + ", ".join(f"{k} {v}" for k, v in sorted(c["scanned"].items())),
          f"- candidates dropped below threshold: {c['dropped']}",
          f"- dropped to the result caps: {c['capped']}"]
    for s in c["superseded_skipped"]:
        L.append(f"- superseded decision skipped: {s}")
    ahead = vsync.get("ahead")
    days = vsync.get("days_since_sync")
    L += ["", "## Vault sync", "",
          f"- last synced with the remote: {vsync.get('last_sync') or 'never recorded'}"
          + (f" ({days} days ago)" if days is not None else ""),
          f"- local commits not yet pushed: {ahead if ahead is not None else 'unknown'}",
          f"- uncommitted changes: {'yes' if vsync.get('dirty') else 'no'}"]
    for note in vsync.get("notes") or []:
        L.append(f"- {note}")
    out = L[:MD_LINE_CAP]
    if len(L) > MD_LINE_CAP:
        out[-1] = "- (truncated at the 80-line cap)"
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--mode", default="solutioning", choices=["solutioning", "implementation"])
    ap.add_argument("--story", default=None)
    ap.add_argument("--vault", default=None)
    ap.add_argument("--graph-root", default=None)
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)

    repo = repo_root(Path(args.repo))
    if not is_delivery_repo(repo):
        print(f"{repo} is not a delivery-flow repo: no {CONFIG_NAME} at its root", file=sys.stderr)
        return 2
    item_dir = artifact_root(repo) / args.item
    if not item_dir.is_dir():
        print(f"no such item: {args.item}", file=sys.stderr)
        return 2
    if args.mode == "implementation" and not args.story:
        print("--mode implementation needs --story", file=sys.stderr)
        return 2

    cfg = load_config(repo)
    item, _ = load_json(item_dir / "item.json")
    triage, _ = load_json(item_dir / "triage.json")

    try:
        doc = recall(item, triage, cfg, args.mode, args.story, args.vault, args.graph_root)
    except Usage as e:
        print(str(e), file=sys.stderr)
        return 2
    except Unreachable as e:
        # Exit 3 and no artifact: the step fails, the flow stops, and nothing downstream gets
        # to mistake a dead mount for a vault with nothing to say.
        print(str(e), file=sys.stderr)
        return 3

    suffix = f"-{args.story}" if args.mode == "implementation" else ""
    if args.stdout:
        print(json.dumps(doc, indent=2, sort_keys=True))
        return 0
    path = item_dir / f"project-context{suffix}.json"
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    (item_dir / f"project-context{suffix}.md").write_text(render_md(doc))

    # `project-context.json` is a contract artifact that `breakdown` and `propose` consume, so
    # it needs its sentinel like any other — the edge check rejects an artifact without one,
    # and recall was leaving the flow stuck one step after itself. The brief deliberately
    # writes none because it is terminal prose nothing consumes; this is not that.
    #
    # Implementation mode writes `project-context-<story>.json`, and the schema registry keys
    # on exact filenames, so a suffixed artifact has no schema. The edge skips it for the same
    # reason, so a sentinel would be checked by nobody — it is written only where a schema
    # exists, and the gap (per-story recall output is unvalidated) is recorded in
    # add-vault-delivery-memory rather than papered over with a sentinel that proves nothing.
    import subprocess
    if not suffix:
        out = subprocess.run([sys.executable, "-I",
                              str(Path(__file__).resolve().parent / "write-sentinel.py"),
                              str(path), "--step", "project-memory"], capture_output=True)
        if out.returncode != 0:
            print((out.stderr or b"").decode().strip() or "could not write the sentinel",
                  file=sys.stderr)
            return 2

    print(f"wrote project-context{suffix}.json"
          + (" and its sentinel" if not suffix else " (no schema for a suffixed name, so no sentinel)")
          + " "
          f"({'matched' if doc['matched'] else 'nothing matched'}; "
          f"scanned {sum(doc['coverage']['scanned'].values())} notes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
