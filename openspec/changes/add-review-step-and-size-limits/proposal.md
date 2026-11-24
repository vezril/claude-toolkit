# Proposal

## Why

Three gaps, found while running the flow on real tickets.

**The roster already names reviewers and nothing dispatches them.**
`templates/delivery-flow/roster.yaml` carries a `reviewers:` list per work kind, and
`resolve-roster.py` returns the de-duplicated union of them — but no step in any profile
consumes it. The `full` profile goes `challenge-implementation → pr-description → open-pr`, so
a diff reaches a PR without any reviewer having read it. `challenge-implementation` does not
close this: it cross-examines the implementation *record* and its claims, not the code.

**The PRs are too large to review.** Nothing in the flow measures or bounds a change's size.
There is no `max_diff_files`, no line ceiling, and no point at which a run stops and says the
change has outgrown one review.

**The dev pair writes more tests than the change warrants.** `qa-test-architect` already
defines risk-based P0–P3 priorities, but nothing carries a priority down to `test-writer`, so
every story gets whatever coverage the pair decides on.

## What Changes

- **A `review` step between `challenge-implementation` and `pr-description`** in the `full`
  profile. It dispatches the reviewers the roster already names for the story's work kind, in a
  fresh context, and emits a schema-backed `review.json`. Ships **uncertified and declared**
  (`allow_uncertified`), like `propose` and `vault-update`, because it has no eval suite yet.
- **Diff-size punch-out ceilings.** New `punch_out.max_diff_files` and
  `punch_out.max_diff_lines` keys, derived in `scripts/delivery-flow/triggers.py` from the
  actual diff rather than from any node's claim about it, so they cannot be reworded away. A
  breach is a punch-out at `verify`: the run stops and a human decides split or proceed.
- **P0/P1 test scope.** The story/proposal carries a risk-priority map, and `test-writer` is
  instructed to cover P0 and P1 and nothing below. The priority is data a reviewer can check,
  not a judgement inside the pair.
- Review findings join the existing `carry_forward` mechanism, so a `WEAKENED`-style review
  obliges `pr-description` to address each finding rather than silently dropping it.

## Capabilities

### New Capabilities
- `delivery-review-step`: the reviewer node before PR creation — who reviews, what it is
  handed, what `review.json` asserts, how its verdict routes, and why it is distinct from
  `challenge-implementation`.
- `delivery-diff-budget`: bounding a change's size — the ceilings, their derivation from the
  real diff, where the punch-out fires, and what a human may decide.
- `delivery-test-scope`: how test priority reaches the dev pair — the risk map, the P0/P1
  rule, and what the verify edge checks.

### Modified Capabilities
<!-- None. The delivery-flow specs are not yet archived into openspec/specs/; they live under
     openspec/changes/add-delivery-flow/specs/. This change adds three new capability specs
     rather than editing requirements that are not yet promoted. -->

## Impact

The flow's own consistency rules in `CLAUDE.md` make this a wide change. A new step touches
every place that enumerates steps, and every one of those pairs is test-enforced:

- `templates/delivery-flow/profiles.yaml` (the `full` step list) **and** the `STEPS` table in
  `scripts/delivery-flow/flow-status.py` — `tests/delivery-flow/test_profiles.py` asserts
  every profile step exists in the table and no table step is left out of every profile.
- `skills/delivery-flow/workflow.yaml` — routing row and `edge_checks` for `review.json`.
- `skills/delivery-flow/steps.yaml` — the registry entry, `certified: false` with a stated
  residual.
- `schemas/review.schema.json` — new, plus registration so `schema_for` resolves it.
- `skills/delivery-flow/references/review.md` — the node prompt.
- `scripts/delivery-flow/triggers.py` — the derived diff-size triggers, imported by both
  `check-punch-out.py` and `hooks/check-edge.py`.
- `.delivery-flow.yaml` and `skills/delivery-flow/references/config.md` — the `punch_out.*`
  keys change together.
- `skills/delivery-flow/SKILL.md` — the routing table, the profile table, the certified-chain
  wording (the `full` rate is already not a Stage 4 number; this adds a second uncertified
  node, which the doc must say).
- `agents/test-writer.md` — the P0/P1 rule. Its file-territory definition is unchanged, so the
  three-place agreement with `agents/implementer.md` and
  `hooks/enforce-dev-pair-boundary.py` still holds.
- `docs/using-the-sdlc-dev-team.md` is **not** affected: this is delivery-flow, not the SDLC
  pipeline. `docs/delivery-flow-handoff.md` and `docs/delivery-flow-status.md` are.

**Not affected: the Stage 4 submission.** The certified chain is the `triage` profile, which
gains no step here. `review` lands in the `full` profile only, so the certified-only rate and
the four certified prompts are untouched.
