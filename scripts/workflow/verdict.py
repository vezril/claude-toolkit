"""What a review verdict means for the flow — fixed rules, in the substrate (design D5).

Workflow-agnostic (task 4.7). A reviewer node emits `REFUTED` / `WEAKENED` / `SURVIVED` plus
findings; this decides what happens next. The orchestrator does not interpret the verdict,
because a model deciding what its own reviewer's verdict implies is not a guardrail.

The three rules:

    SURVIVED   advance
    REFUTED    rerun the producing node — and twice on the same target is a punch-out, not a
               third attempt, because a node that cannot satisfy its reviewer twice is a
               decision for a human rather than a loop
    WEAKENED   per the workflow's declared policy, below

**WEAKENED differs by workflow, and that is why the policy is declared rather than decided
here.** delivery-flow documents "a verdict of WEAKENED never blocks — it proceeds, and its
findings are reported as constraints the consuming step has to address". Design D5 for the
SDLC pipeline says the opposite: WEAKENED requires every finding addressed before advance.
Both are defensible — delivery-flow's breakdown feeds a human-read brief, the SDLC pipeline's
stories feed a build — and a substrate that imposed either would silently change one of them.

How "every finding addressed" is tested, without inventing an artifact for it: the target must
have been **rewritten since the verdict was written**. That is the staleness rule delivery-flow
already applies to challenges ("a challenge whose target has been rewritten since is stale, and
the challenge reruns against the version that now exists"), used here for a second purpose. If
the stories have not changed, nothing was addressed, whatever anyone claims. If they have, the
verdict no longer describes what is on disk and the reviewer runs again.

The deliberate consequence: under `require-addressed`, there is no path from WEAKENED to
advance that does not pass through a fresh verdict. A caller cannot mark findings resolved,
because self-reported resolution is exactly the claim an edge exists to not take on trust.
"""

REFUTED = "REFUTED"
WEAKENED = "WEAKENED"
SURVIVED = "SURVIVED"
VERDICTS = (REFUTED, WEAKENED, SURVIVED)

# Two REFUTED verdicts on the same target is a punch-out. Matches delivery-flow's loop bound
# (design D14) rather than introducing a second number for the same idea.
REFUTE_LIMIT = 2

ADVANCE = "advance"
RERUN_PRODUCER = "rerun-producer"
RERUN_REVIEWER = "rerun-reviewer"
PUNCH_OUT = "punch-out"
BLOCKED = "blocked"

# What a workflow may declare for WEAKENED.
ADVANCE_ON_WEAKENED = "advance"
REQUIRE_ADDRESSED = "require-addressed"
WEAKENED_POLICIES = (ADVANCE_ON_WEAKENED, REQUIRE_ADDRESSED)


def weakened_policy(descriptor: dict, step: str = None) -> str:
    """The WEAKENED policy for a step, falling back to the workflow's, then to `advance`.

    The workflow-level default is `advance` because that is delivery-flow's documented
    behaviour, and the workflow that existed before this module must not change by having it
    added. A workflow wanting the stricter rule says so.

    **Per step, because one workflow legitimately wants both.** delivery-flow's breakdown
    challenge feeds a brief a human reads, where a WEAKENED verdict should not block — that is
    documented behaviour of the certified triage chain. Its `review` step feeds a merge, where
    unaddressed findings are exactly what must block. A single workflow-wide value cannot say
    both, and setting the workflow to `require-addressed` to get the review's behaviour would
    silently change the certified chain's.

    Declared as `verdict_policy.weakened_<step>`, read **before** the workflow-level key so an
    explicit per-step rule always wins over an inherited one.

    Flat rather than a nested `weakened_by_step:` block because `descriptor.py`'s YAML subset
    flattens two-level nesting into the parent mapping: a nested block silently parsed as a
    sibling key and the per-step rule never resolved at all.
    """
    policy_block = (descriptor or {}).get("verdict_policy") or {}

    if step:
        per_step = policy_block.get(f"weakened_{step}")
        if per_step in WEAKENED_POLICIES:
            return per_step
        # A per-step value that is not a recognised policy is ignored rather than honoured, and
        # the workflow-level answer is used. Guessing which policy a typo meant is how a
        # merge-blocking rule becomes a non-blocking one without anybody editing it.

    policy = policy_block.get("weakened")
    return policy if policy in WEAKENED_POLICIES else ADVANCE_ON_WEAKENED


def decide(verdict: dict, *, target_changed: bool, refutations: int = 0,
           descriptor: dict = None, step: str = None) -> dict:
    """{action, reason, findings} for one verdict. Never raises on bad input.

    `target_changed` — has the reviewed artifact been rewritten since this verdict was written?
    `refutations`    — how many times this target has come back REFUTED, including this one.

    An unreadable or unrecognised verdict blocks. A verdict is the thing a segment's advance
    turns on, so "I could not tell what it said" has to stop the flow; treating it as SURVIVED
    would let a malformed artifact advance a build, and treating it as REFUTED would rerun a
    node that may have been right.
    """
    doc = verdict or {}
    value = doc.get("verdict")
    findings = [f for f in (doc.get("findings") or []) if isinstance(f, dict)]

    if value not in VERDICTS:
        return {"action": BLOCKED, "findings": findings,
                "reason": f"the verdict is {value!r}, which is not one of "
                          f"{', '.join(VERDICTS)}; a verdict that cannot be read must not "
                          f"advance a segment"}

    if value == SURVIVED:
        # Findings alongside SURVIVED are a contradiction worth stopping on rather than
        # resolving in favour of either side: the reviewer said the artifact stands and also
        # named something wrong with it, and only its author knows which it meant.
        if findings:
            return {"action": BLOCKED, "findings": findings,
                    "reason": f"SURVIVED with {len(findings)} finding(s): a verdict cannot "
                              f"both stand and carry defects"}
        return {"action": ADVANCE, "findings": [], "reason": "SURVIVED with no findings"}

    if value == REFUTED:
        if refutations >= REFUTE_LIMIT:
            return {"action": PUNCH_OUT, "findings": findings,
                    "reason": f"REFUTED {refutations} times, and the limit is "
                              f"{REFUTE_LIMIT}: a node that cannot satisfy its reviewer "
                              f"twice is a human decision, not a third attempt"}
        return {"action": RERUN_PRODUCER, "findings": findings,
                "reason": "REFUTED: the artifact is wrong, so the node that produced it reruns"}

    # WEAKENED
    if weakened_policy(descriptor, step) == ADVANCE_ON_WEAKENED:
        return {"action": ADVANCE, "findings": findings,
                "reason": f"WEAKENED with {len(findings)} finding(s), and this workflow does "
                          f"not block on it; the findings travel as constraints the consuming "
                          f"step has to address"}

    if not target_changed:
        return {"action": BLOCKED, "findings": findings,
                "reason": f"WEAKENED with {len(findings)} finding(s) and the target is "
                          f"unchanged since the verdict, so nothing has been addressed"}

    return {"action": RERUN_REVIEWER, "findings": findings,
            "reason": "WEAKENED and the target has been rewritten since: the verdict no "
                      "longer describes what is on disk, so the reviewer runs again"}
