"""Deriving punch-out triggers from the artifacts, independently of the node's own flags.

`triage.json` carries `handoff`, `architecture_change` and `breaking_change`. Until now those
booleans *were* the gate: the node that produced them decided whether a human got asked, which
is the guard depending on the thing it guards. A node that writes `false` walks through.

So each trigger gets a derivation that never reads the node's boolean, and the two are combined:

  fired = derived OR claimed          — a human gets asked whenever either says so

That one line is what closes the hole: suppressing a flag no longer skips a gate whose
derivation fires. Where the two disagree, the disagreement is *recorded* on the edge and
reported, but it does not fail the edge — see `disagreement` below for why.

**What these derivations can see.** In the `triage` profile nothing is implemented, so there is
no diff: `breakdown.json` closes a story to id, statement, domains and acceptance criteria, with
no file paths anywhere. The available material is text, labels, domains and counts, and the
derivations are correspondingly coarse. That is a deliberate trade: a false positive costs one
question to a human, a false negative costs the guarantee the gate exists for. The diff-based
derivations (`contract_paths`, `protected_paths`) still run in `check-punch-out.py` and carry
the strong version of this check once there is code to look at.

Shared by `check-punch-out.py` (which writes the punch-outs) and `hooks/check-edge.py` (which
fails the edge on a mismatch), so the two cannot drift.
"""

import re

DEFAULT_EPIC_CEILING = 4
DEFAULT_STORY_CEILING = 12
DEFAULT_DOMAIN_CEILING = 2
DEFAULT_PROPOSAL_TASK_CEILING = 8
DEFAULT_PROPOSAL_FILE_CEILING = 15

# An item that states no expected outcome cannot be scoped by anyone, model or human.
ACCEPTANCE_SIGNAL = re.compile(
    r"\b(acceptance|criteri\w+|should\b|must\b|expect\w*|so that\b|given\b|then\b|"
    r"repro\w*|steps to\b|definition of done)\b", re.I)

ARCHITECTURE_WORDS = re.compile(
    r"\b(new service|new microservice|microservices?|re-?architect\w*|rearchitect\w*|"
    r"boundar(?:y|ies)|migrat\w+|decoupl\w+|extract (?:a |the )?(?:service|module|library)|"
    r"split (?:out|up|the)|replace (?:the )?(?:service|datastore|database|queue)|"
    r"event bus|message bus|introduce (?:a |an )?(?:queue|broker|cache)|"
    r"data model|schema (?:change|migration)|rewrite)\b", re.I)

BREAKING_WORDS = re.compile(
    r"\b(breaking change|breaking|backward[- ]?incompat\w*|non-?backward\w*|"
    r"remove (?:the )?(?:endpoint|field|column|parameter|header|route)|"
    r"rename (?:the )?(?:endpoint|field|column|parameter|header|route)|"
    r"drop (?:the )?(?:column|table|field)|major version|bump (?:the )?major|"
    r"change (?:the )?(?:signature|contract|wire format)|deprecat\w+)\b", re.I)

# trigger -> (the triage flag that claims it, the question a human is being asked)
CLAIMS = {
    "scope": ("handoff", "Is this in scope, and what should it be cut down to?"),
    "architecture": ("architecture", "This moves a boundary. Is that the intent?"),
    "breaking": ("breaking", "Callers will have to change. Proceed?"),
}
FLAG_FOR = {"scope": "handoff", "architecture": "architecture_change", "breaking": "breaking_change"}
OPTIONS = {
    "scope": ["proceed with a narrowed scope", "stop", "redirect to another item"],
    "architecture": ["proceed", "stop", "redirect to a design discussion first"],
    "breaking": ["proceed", "stop", "redirect: add a compatibility path first"],
}


def ceilings(cfg: dict) -> dict:
    policy = (cfg or {}).get("punch_out") or {}
    def num(key, default):
        try:
            return int(policy.get(key))
        except (TypeError, ValueError):
            return default
    return {"epics": num("epic_ceiling", DEFAULT_EPIC_CEILING),
            "stories": num("story_ceiling", DEFAULT_STORY_CEILING),
            "domains": num("domain_ceiling", DEFAULT_DOMAIN_CEILING),
            "proposal_tasks": num("proposal_task_ceiling", DEFAULT_PROPOSAL_TASK_CEILING),
            "proposal_files": num("proposal_file_ceiling", DEFAULT_PROPOSAL_FILE_CEILING)}


def item_text(item: dict) -> str:
    i = item or {}
    return " ".join(str(x) for x in (i.get("title"), i.get("body"),
                                     " ".join(i.get("labels") or [])) if x)


def breakdown_text(breakdown: dict) -> str:
    parts = []
    for epic in (breakdown or {}).get("epics") or []:
        parts.append(str(epic.get("title") or ""))
        for story in epic.get("stories") or []:
            parts.append(str(story.get("statement") or ""))
            for ac in story.get("acceptance_criteria") or []:
                parts += [str(ac.get(k) or "") for k in ("given", "when", "then")]
    return " ".join(parts)


def breakdown_shape(breakdown: dict) -> dict:
    epics = (breakdown or {}).get("epics") or []
    stories = [s for e in epics for s in (e.get("stories") or [])]
    domains = {d for s in stories for d in (s.get("domains") or [])}
    return {"epics": len(epics), "stories": len(stories), "domains": sorted(domains)}


def _contract_hits(text: str, cfg: dict) -> list:
    """`contract_paths` names appearing in the text. Weak, but it is what exists before code."""
    hits = []
    for prefix in ((cfg or {}).get("punch_out") or {}).get("contract_paths") or []:
        name = str(prefix).strip("/").split("/")[-1]
        if name and re.search(rf"\b{re.escape(name)}\b", text, re.I):
            hits.append(str(prefix))
    return hits


def derive(item: dict, triage: dict, breakdown: dict, cfg: dict) -> dict:
    """trigger -> {"fired": bool|None, "evidence": str}.

    `fired: None` means not determinable from the artifacts present — at triage time the
    counts do not exist yet, and an undetermined derivation must not be read as "no".
    """
    caps = ceilings(cfg)
    # **The item and the breakdown only — never triage's own prose.** The spec says the
    # derivation runs over "the item and breakdown text, the domains and the counts", and
    # including triage's `summary`/`rationale` broke the whole point of deriving: the guard was
    # reading the guarded node's reasoning as evidence about the item.
    #
    # It also inverted. On AN-3630 the architecture trigger fired on the phrase "new service"
    # found inside triage's rationale — in the sentence "a single library change with **no new
    # service**, topology or incompatible change described". The node correctly explained why
    # this is not an architecture change, and that explanation became the evidence that it is.
    # A derivation that punishes a well-argued negative is worse than no derivation, because
    # it trains nodes to say less.
    text = " ".join(x for x in (item_text(item), breakdown_text(breakdown)) if x)
    shape = breakdown_shape(breakdown) if breakdown else None
    out = {}

    # scope: an item nobody can state the expected outcome of, or a breakdown that grew.
    if not item:
        out["scope"] = {"fired": None, "evidence": "item.json is not available"}
    else:
        reasons = []
        # A ticket stating no expected outcome is one nobody can scope, model or human. It is
        # also common enough on a real tracker to be worth a switch: turn it off and the scope
        # trigger rests on the ceilings and the node's own flag alone.
        require_acceptance = ((cfg or {}).get("punch_out") or {}).get("require_acceptance_signal")
        if require_acceptance is None:
            require_acceptance = True
        if require_acceptance and not ACCEPTANCE_SIGNAL.search(item_text(item)):
            reasons.append("the item text states no expected outcome, acceptance criterion or "
                           "reproduction step")
        if shape and shape["epics"] > caps["epics"]:
            reasons.append(f"the breakdown has {shape['epics']} epics, over the ceiling of {caps['epics']}")
        if shape and shape["stories"] > caps["stories"]:
            reasons.append(f"the breakdown has {shape['stories']} stories, over the ceiling of {caps['stories']}")
        out["scope"] = {"fired": bool(reasons), "evidence": "; ".join(reasons) or "no scope signal"}

    # architecture: breadth of domains, or the vocabulary of moving a boundary.
    reasons = []
    if shape and len(shape["domains"]) > caps["domains"]:
        reasons.append(f"the breakdown spans {len(shape['domains'])} domains "
                       f"({', '.join(shape['domains'])}), over the ceiling of {caps['domains']}")
    m = ARCHITECTURE_WORDS.search(text)
    if m:
        reasons.append(f"the text says {m.group(0)!r}")
    hits = _contract_hits(text, cfg)
    if hits:
        reasons.append(f"the text names a shared contract: {', '.join(hits)}")
    out["architecture"] = {"fired": bool(reasons), "evidence": "; ".join(reasons) or "no architecture signal"}

    reasons = []
    m = BREAKING_WORDS.search(text)
    if m:
        reasons.append(f"the text says {m.group(0)!r}")
    if hits:
        reasons.append(f"the text names a shared contract: {', '.join(hits)}")
    out["breaking"] = {"fired": bool(reasons), "evidence": "; ".join(reasons) or "no breaking-change signal"}

    return out


# The proposal-sourced triggers. Unlike the triage ones these match *paths*, because the
# proposal names the files each task will touch — so rewording the prose does not evade them.
# They are still claims about the future: `verify` rechecks the realized diff against the same
# path lists, which is where a proposal that planned one thing and did another is caught.
PROPOSAL_FLAG_FOR = {"proposal-scope": "scope", "proposal-architecture": "architecture",
                     "proposal-breaking": "breaking"}
PROPOSAL_DECISIONS = {
    "proposal-scope": ("This change is larger than the policy allows without a decision. Proceed?",
                       ["proceed", "stop", "redirect: split it into smaller changes"]),
    "proposal-architecture": ("The proposal moves a boundary. Is that the intent?",
                              ["proceed", "stop", "redirect to a design discussion first"]),
    "proposal-breaking": ("The proposal touches a shared contract. Callers will have to change. Proceed?",
                          ["proceed", "stop", "redirect: add a compatibility path first"]),
    "protected-path": ("The proposal plans to edit a protected path. Proceed?",
                       ["proceed", "stop", "redirect: leave the protected path alone"]),
    "new-dependency": ("The proposal adds a dependency. Accept it?",
                       ["proceed", "stop", "redirect: implement it without the dependency"]),
}


def proposal_paths(proposal: dict) -> list:
    return sorted({f for t in (proposal or {}).get("tasks") or [] for f in (t.get("files") or [])})


def under(path: str, prefix: str) -> bool:
    """True when a path sits at or under a configured prefix.

    Public because both halves of the path gates use it: the *planned* paths here, and the
    *realized* diff in `check-punch-out.py`. `verify` compares the two, so a prefix that
    matched a plan and not the diff that implemented it would be a false finding. Note this
    is a path-segment test, not a string prefix — `nx_neptune` must not match
    `nx_neptune_extra/foo.py`.
    """
    p, q = str(path).strip("/"), str(prefix).strip("/")
    return bool(q) and (p == q or p.startswith(q + "/"))


def _prefix_hits(paths: list, cfg: dict, key: str) -> list:
    hits = []
    for prefix in ((cfg or {}).get("punch_out") or {}).get(key) or []:
        matched = [p for p in paths if under(p, prefix)]
        if matched:
            hits.append((str(prefix), matched))
    return hits


def derive_proposal(proposal: dict, cfg: dict) -> dict:
    """trigger -> {"fired": bool|None, "evidence": str} from the proposal's planned paths.

    `None` throughout when there is no proposal yet: undetermined is not "no".
    """
    if not proposal:
        return {t: {"fired": None, "evidence": "no proposal has been written yet"}
                for t in (*PROPOSAL_FLAG_FOR, "protected-path", "new-dependency")}

    caps = ceilings(cfg)
    paths = proposal_paths(proposal)
    tasks = proposal.get("tasks") or []
    out = {}

    reasons = []
    if len(tasks) > caps["proposal_tasks"]:
        reasons.append(f"{len(tasks)} tasks, over the ceiling of {caps['proposal_tasks']}")
    if len(paths) > caps["proposal_files"]:
        reasons.append(f"{len(paths)} files, over the ceiling of {caps['proposal_files']}")
    out["proposal-scope"] = {"fired": bool(reasons),
                             "evidence": "; ".join(reasons) or "within the size ceilings"}

    contract = _prefix_hits(paths, cfg, "contract_paths")
    out["proposal-breaking"] = {
        "fired": bool(contract),
        "evidence": "; ".join(f"a task plans to touch {prefix}: {', '.join(m[:4])}"
                              for prefix, m in contract) or "no contract path is planned"}

    # Architecture has no path signature of its own before there is code; the shared-contract
    # hit is the only structural evidence available, and the node's own claim covers the rest.
    out["proposal-architecture"] = {
        "fired": bool(contract),
        "evidence": out["proposal-breaking"]["evidence"] if contract
        else "no structural architecture signal in the planned paths"}

    protected = _prefix_hits(paths, cfg, "protected_paths")
    out["protected-path"] = {
        "fired": bool(protected),
        "evidence": "; ".join(f"a task plans to touch {prefix}: {', '.join(m[:4])}"
                              for prefix, m in protected) or "no protected path is planned"}

    deps = proposal.get("dependencies_added") or []
    out["new-dependency"] = {"fired": bool(deps),
                             "evidence": f"the proposal adds {', '.join(deps)}" if deps
                             else "no dependency is added"}
    return out


def combine_proposal(proposal: dict, cfg: dict) -> dict:
    """Same composition rule as the triage triggers: fire on derivation or claim."""
    derived = derive_proposal(proposal, cfg)
    out = {}
    for trigger, d in derived.items():
        flag = PROPOSAL_FLAG_FOR.get(trigger)
        c = bool(proposal.get(flag)) if (proposal and flag) else None
        fired = bool(d["fired"]) or bool(c)
        source = ("both" if d["fired"] and c else "derivation" if d["fired"]
                  else "claim" if c else None)
        out[trigger] = {
            "fired": fired, "source": source, "evidence": d["evidence"],
            "claim": c, "derived": d["fired"],
            "disagreement": d["fired"] is not None and c is not None and bool(d["fired"]) != bool(c),
        }
    return out


def proposal_disagreements(proposal: dict, cfg: dict) -> list:
    out = []
    for trigger, v in sorted(combine_proposal(proposal, cfg).items()):
        if not v["disagreement"]:
            continue
        out.append({"trigger": trigger, "flag": PROPOSAL_FLAG_FOR.get(trigger),
                    "claimed": v["claim"], "derived": v["derived"], "evidence": v["evidence"]})
    return out


def claimed(triage: dict) -> dict:
    """trigger -> the node's boolean, or None when triage.json is absent."""
    if not triage:
        return {t: None for t in FLAG_FOR}
    return {t: bool(triage.get(flag)) for t, flag in FLAG_FOR.items()}


def combine(item: dict, triage: dict, breakdown: dict, cfg: dict) -> dict:
    """trigger -> {fired, source, evidence, claim, derived, mismatch}."""
    derived, claims = derive(item, triage, breakdown, cfg), claimed(triage)
    out = {}
    for trigger in FLAG_FOR:
        d = derived.get(trigger) or {"fired": None, "evidence": ""}
        c = claims.get(trigger)
        fired = bool(d["fired"]) or bool(c)
        if d["fired"] and c:
            source = "both"
        elif d["fired"]:
            source = "derivation"
        elif c:
            source = "claim"
        else:
            source = None
        out[trigger] = {
            "fired": fired, "source": source, "evidence": d["evidence"],
            "claim": c, "derived": d["fired"],
            # Undetermined is not disagreement: at triage time the counts do not exist yet.
            "disagreement": d["fired"] is not None and c is not None and bool(d["fired"]) != bool(c),
        }
    return out


def disagreements(item: dict, triage: dict, breakdown: dict, cfg: dict) -> list:
    """Claims the derivations contradict, as evidence for the trace.

    Deliberately not edge failures. The derivations available before any code exists are
    textual heuristics, and a node is entitled to disagree with a keyword match. The
    propositions also differ: `handoff` asserts the item is unclear or out of scope, while an
    epic count over its ceiling asserts the work is large, and a node can be right about the
    first while the second holds. What protects the gate is that the trigger fires on either
    signal; what this list adds is a countable record of how often the node and the evidence
    part company, which is the thing a reviewer should be able to ask about.
    """
    out = []
    for trigger, v in sorted(combine(item, triage, breakdown, cfg).items()):
        if not v["disagreement"]:
            continue
        out.append({"trigger": trigger, "flag": FLAG_FOR[trigger], "claimed": v["claim"],
                    "derived": v["derived"], "evidence": v["evidence"]})
    return out
