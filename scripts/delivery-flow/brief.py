"""The brief: a fixed-shape summary of one item, rendered from structured artifacts.

Shared by `render-brief.py` (which writes it) and `hooks/check-edge.py` (which checks it), so
the two cannot disagree about what an identifier is or which findings had to be carried.

The brief is the chain's terminal prose: a human reads it, no step consumes it. It is rendered
by code rather than written by a node for two reasons — everything it needs is already
structured, so a node would add a certification package for no new information; and it is the
artifact a human decision rests on, where a model's instinct to reassure is a liability.

Six sections, same order, every run. Empty sections say so rather than vanishing, because a
missing heading reads as "nothing to see" exactly when something was dropped.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SECTIONS = ["What this asks for", "How it was classified", "The work",
            "The challenge", "What will change", "What must be addressed", "Your decision"]

# What counts as an identifier for the no-invention check. Deliberately narrow: a file-like
# token or a breakdown id. A wider rule would flag ordinary words and make the edge noise.
FILE_RE = re.compile(r"\b[A-Za-z0-9_-]+\.(?:scala|py|ts|tsx|js|jsx|json|yaml|yml|md|sql|conf|sh|tf|java|kt|go|rs|rb|css|html)\b")
ID_RE = re.compile(r"\b(?:E|S|AC|T)[0-9]+\b")


def epic_story_ids(breakdown) -> list:
    """Every epic and story id in the breakdown, in document order."""
    out = []
    for epic in (breakdown or {}).get("epics") or []:
        if epic.get("id"):
            out.append(epic["id"])
        for story in epic.get("stories") or []:
            if story.get("id"):
                out.append(story["id"])
    return out


def counts(breakdown) -> dict:
    epics = (breakdown or {}).get("epics") or []
    stories = [s for e in epics for s in (e.get("stories") or [])]
    criteria = [c for s in stories for c in (s.get("acceptance_criteria") or [])]
    return {"epics": len(epics), "stories": len(stories), "acceptance_criteria": len(criteria)}


def proposal_files(proposal) -> list:
    """Every distinct file the proposal plans to touch, in sorted order."""
    return sorted({f for t in (proposal or {}).get("tasks") or [] for f in (t.get("files") or [])})


def proposal_task_ids(proposal) -> list:
    return [t.get("id") for t in (proposal or {}).get("tasks") or [] if t.get("id")]


def required_findings(challenge) -> list:
    """Findings the brief has to carry.

    A SURVIVED verdict's findings are optional colour. REFUTED and WEAKENED both oblige the
    reader: one means the breakdown is wrong, the other that it is incomplete, and in either
    case a decision taken without seeing the findings is taken blind.
    """
    if not challenge or challenge.get("verdict") not in ("REFUTED", "WEAKENED"):
        return []
    return [f.get("finding") for f in (challenge.get("findings") or []) if f.get("finding")]


def identifiers(text: str) -> set:
    return set(FILE_RE.findall(text)) | set(ID_RE.findall(text))


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _n(count: int, singular: str, plural: str = None) -> str:
    return f"{count} {singular if count == 1 else (plural or singular + 's')}"


def render(item, triage, breakdown, challenge, punch_outs=(), proposal=None) -> str:
    """The brief. Byte-identical for identical inputs: no clock, no randomness, no model."""
    t = triage or {}
    quick = t.get("path") == "quick"
    n = counts(breakdown)
    L = []

    L.append(f"# {(item or {}).get('key') or t.get('item') or 'item'} — {(item or {}).get('title') or 'untitled'}")
    L.append("")

    L.append(f"## {SECTIONS[0]}")
    L.append("")
    L.append(_norm(t.get("summary")) or "No summary: the triage step recorded none.")
    L.append("")

    L.append(f"## {SECTIONS[1]}")
    L.append("")
    L.append(f"- Type: {t.get('type') or 'unknown'}")
    L.append(f"- Path: {t.get('path') or 'unknown'}")
    L.append(f"- Domains: {', '.join(t.get('domains') or []) or 'none recorded'}")
    flags = [name for name, key in (("scope handoff", "handoff"),
                                    ("architecture change", "architecture_change"),
                                    ("breaking change", "breaking_change")) if t.get(key)]
    L.append(f"- Flags raised: {', '.join(flags) if flags else 'none'}")
    L.append("")

    L.append(f"## {SECTIONS[2]}")
    L.append("")
    if quick and not breakdown:
        L.append("Nothing to show: this is the quick path, which writes no breakdown.")
    elif not breakdown:
        L.append("Nothing to show: no breakdown has been produced yet.")
    else:
        L.append(f"{_n(n['epics'], 'epic')}, {_n(n['stories'], 'story', 'stories')}, "
                 f"{_n(n['acceptance_criteria'], 'acceptance criterion', 'acceptance criteria')}.")
        L.append("")
        for epic in breakdown.get("epics") or []:
            L.append(f"**{epic.get('id')} — {_norm(epic.get('title'))}**")
            L.append("")
            for story in epic.get("stories") or []:
                ac = len(story.get("acceptance_criteria") or [])
                L.append(f"- {story.get('id')}: {_norm(story.get('statement'))} "
                         f"({_n(ac, 'criterion', 'criteria')})")
            L.append("")
        L.pop()  # the trailing blank from the last epic; one blank line follows below
    L.append("")

    L.append(f"## {SECTIONS[3]}")
    L.append("")
    if quick and not challenge:
        L.append("Nothing to show: the quick path does not challenge a breakdown.")
    elif not challenge:
        L.append("Nothing to show: the breakdown has not been challenged yet.")
    else:
        landed = sum(1 for a in challenge.get("attacks") or [] if a.get("result") == "landed")
        total = len(challenge.get("attacks") or [])
        L.append(f"Verdict: **{challenge.get('verdict')}** — {landed} of {total} attacks landed.")
    L.append("")

    L.append(f"## {SECTIONS[4]}")
    L.append("")
    if not proposal:
        L.append("Nothing yet: no change has been proposed for this item.")
    else:
        files = proposal_files(proposal)
        tasks = proposal.get("tasks") or []
        deps = proposal.get("dependencies_added") or []
        L.append(f"`{proposal.get('change_id')}` — {_n(len(tasks), 'task')}, "
                 f"{_n(len(files), 'file')}.")
        L.append("")
        for t in tasks:
            L.append(f"- {t.get('id')}: {_norm(t.get('description'))}")
        L.append("")
        L.append(f"Files: {', '.join(files) if files else 'none named'}")
        L.append(f"New dependencies: {', '.join(deps) if deps else 'none'}")
        pflags = [name for name, key in (("scope", "scope"), ("architecture", "architecture"),
                                         ("breaking", "breaking")) if proposal.get(key)]
        L.append(f"Flags on the proposal: {', '.join(pflags) if pflags else 'none'}")
    L.append("")

    L.append(f"## {SECTIONS[5]}")
    L.append("")
    needed = required_findings(challenge)
    if not needed:
        L.append("Nothing: no findings require an answer.")
    else:
        for f in needed:
            L.append(f"- {_norm(f)}")
    L.append("")

    L.append(f"## {SECTIONS[6]}")
    L.append("")
    if not punch_outs:
        L.append("Nothing open. The flow stopped because it reached the end of its profile.")
    else:
        # The punch-out file holds the decision, the evidence and the options. Pointing at it
        # beats re-parsing its prose here: one fewer format with two readers.
        for p in punch_outs:
            L.append(f"- **{p.get('trigger') or 'punch-out'}** ({p.get('state') or 'open'})"
                     f" — read `{p.get('punch_out')}` and decide with `decide.py`")
    L.append("")

    return "\n".join(L)


def coverage_problems(text: str, triage, breakdown, challenge, proposal=None) -> list:
    """What the renderer is answerable for: nothing dropped, nothing invented.

    Not checked here: how readable the result is. The prose the brief carries is mostly
    inherited from the breakdown node, so failing the brief for its grade level would stop
    the chain on a property the renderer cannot change. Readability is measured instead.
    """
    problems = []
    flat = _norm(text)

    for section in SECTIONS:
        if f"## {section}" not in text:
            problems.append(f"section {section!r} is missing")

    for ident in epic_story_ids(breakdown):
        if not re.search(rf"\b{re.escape(ident)}\b", text):
            problems.append(f"{ident} is in breakdown.json but not in the brief")

    for ident in proposal_task_ids(proposal):
        if not re.search(rf"\b{re.escape(ident)}\b", text):
            problems.append(f"{ident} is in proposal.json but not in the brief")

    if challenge and challenge.get("verdict"):
        if challenge["verdict"] not in text:
            problems.append(f"the verdict {challenge['verdict']} is not stated in the brief")

    for finding in required_findings(challenge):
        if _norm(finding) not in flat:
            problems.append(f"a finding the verdict requires is not carried: {_norm(finding)[:80]}")

    known = identifiers(" ".join(json.dumps(d or {})
                                 for d in (triage, breakdown, challenge, proposal)))
    for ident in sorted(identifiers(text) - known):
        problems.append(f"the brief names {ident}, which occurs in none of its inputs")

    return problems


def readability(text: str, plugin_root: Path, timeout: float = 20.0) -> dict:
    """Flesch-Kincaid and Gunning Fog, or {} when they cannot be computed.

    Recorded in the trace, never gated on: see coverage_problems. An unavailable metric is a
    gap in the evidence, not a reason to stop a run.
    """
    script = Path(plugin_root) / "skills" / "readability" / "scripts" / "readability.py"
    if not script.exists():
        return {}
    try:
        out = subprocess.run([sys.executable, "-I", str(script)], input=text.encode(),
                             capture_output=True, timeout=timeout)
        scores = (json.loads(out.stdout or b"{}") or {}).get("scores") or {}
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
        return {}
    return {k: scores[k] for k in ("flesch_kincaid_grade", "gunning_fog") if k in scores}
