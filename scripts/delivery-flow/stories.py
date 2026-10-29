"""The breakdown→story mapping, shared by the renderer and the edge check.

One module so the two cannot disagree about what a story is — the same reason `brief.py` is
shared between `render-brief.py` and `hooks/check-edge.py`. If the renderer and the checker
each had their own idea of the mapping, a story could pass a check that was asking a different
question from the one the renderer answered.

**The mapping adds no judgement.** Every field of a story comes from the breakdown unchanged,
or from a fixed list of source paths. That is what makes this an edge rather than a node: there
is nothing here to certify, and nothing here can invent a story the challenged breakdown did
not contain.
"""

STORY_FILE = "story-{epic}-{story}.json"

# Artifacts a story points at instead of carrying a summary of them. A summary would be a
# node's claim about the context; a pointer is the context. Only those that exist are listed.
SOURCE_CANDIDATES = ["item.json", "triage.json", "breakdown.json",
                     "challenge-breakdown.json", "project-context.json", "proposal.json"]

ORDERING_BASIS = ("breakdown order; dependency ordering is undetermined. Ordering is a "
                  "judgement, so it belongs to a node or a human, not to this renderer.")


def story_filename(epic_id: str, story_id: str) -> str:
    return STORY_FILE.format(epic=epic_id, story=story_id)


def sources_for(item_dir, change_path=None) -> list:
    """The artifacts this story derives from, as repo-relative-ish names that exist."""
    out = [name for name in SOURCE_CANDIDATES if (item_dir / name).exists()]
    if change_path:
        out.append(str(change_path))
    return out


def stories_from(breakdown: dict, sources: list) -> list:
    """Every breakdown story as a story record, in breakdown order.

    Fields are carried across unchanged. `ordering.determined` is False because the breakdown
    expresses no dependency order and this renderer will not invent one — the position is
    recorded so the sequence is reproducible, with `basis` saying what it does and does not
    mean.
    """
    out, position = [], 0
    for epic in breakdown.get("epics") or []:
        for story in epic.get("stories") or []:
            position += 1
            out.append({
                "item": breakdown.get("item") or "",
                "epic": epic.get("id") or "",
                "story": story.get("id") or "",
                "statement": story.get("statement") or "",
                "domains": list(story.get("domains") or []),
                "acceptance_criteria": [
                    {"id": ac.get("id") or "", "given": ac.get("given") or "",
                     "when": ac.get("when") or "", "then": ac.get("then") or ""}
                    for ac in (story.get("acceptance_criteria") or [])
                ],
                "sources": list(sources),
                "ordering": {"determined": False, "position": position,
                             "basis": ORDERING_BASIS},
            })
    return out


def invented(story: dict, breakdown: dict) -> list:
    """What this story asserts that the breakdown does not. Empty is the only passing answer.

    The check the renderer exists to make unnecessary, run anyway: a renderer is code and code
    can be edited, so the edge verifies the property rather than trusting the producer.
    """
    problems = []
    match = None
    for epic in breakdown.get("epics") or []:
        for candidate in epic.get("stories") or []:
            if candidate.get("id") == story.get("story") and epic.get("id") == story.get("epic"):
                match = candidate
                break
    if match is None:
        return [f"story {story.get('epic')}/{story.get('story')} is not in the breakdown"]

    if (story.get("statement") or "") != (match.get("statement") or ""):
        problems.append("the statement does not match the breakdown's")

    extra_domains = set(story.get("domains") or []) - set(match.get("domains") or [])
    if extra_domains:
        problems.append(f"domains not in the breakdown: {', '.join(sorted(extra_domains))}")

    want = {(ac.get("id"), ac.get("given"), ac.get("when"), ac.get("then"))
            for ac in (match.get("acceptance_criteria") or [])}
    for ac in story.get("acceptance_criteria") or []:
        key = (ac.get("id"), ac.get("given"), ac.get("when"), ac.get("then"))
        if key not in want:
            problems.append(f"acceptance criterion {ac.get('id')} is not in the breakdown")
    return problems


def missing_from(stories: list, breakdown: dict) -> list:
    """Breakdown stories that reached no story file.

    The other direction, and the one that matters more: an invented story is visible, a dropped
    one is silence. The `breakdown` node's known residual is exactly a dropped requirement.
    """
    rendered = {(s.get("epic"), s.get("story")) for s in stories}
    out = []
    for epic in breakdown.get("epics") or []:
        for story in epic.get("stories") or []:
            if (epic.get("id"), story.get("id")) not in rendered:
                out.append(f"{epic.get('id')}/{story.get('id')} reached no story file")
    return out
