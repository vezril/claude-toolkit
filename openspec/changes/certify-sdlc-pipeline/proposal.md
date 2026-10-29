## Why

`delivery-flow` is the Stage 4 submission. The reason to hold the certification is not the
submission — it is to keep building workflows afterwards, including large ones. The
`sdlc-orchestrator` is the large one, and today it is not certifiable. The gaps were measured
against `skills/workflow-certification/` and the seven-question self-test:

| Criterion | State |
|---|---|
| Workflow definition | **Partial** — the sequence is prose in `SKILL.md` plus routing tables a model reads; no step registry, no router |
| Guardrails | **Mixed** — `enforce-dev-pair-boundary.py` is a real `PreToolUse` hook and a genuine edge; the readiness gate's `lint-story.py` and `openspec validate` are deterministic but *orchestrator-invoked*, which Rule 2 says is not a guardrail |
| Punch-out evidence | **Fail** — gates exist, nothing has attacked them |
| End-to-end success rate | **Fail** — no outcome record, no manual-correction detection |
| Audit trail | **Fail** — `check-edge.py` and `trace-step.py` exit early without `.delivery-flow.yaml`, so sdlc runs are untraced |

Three of those are structural rather than missing paperwork:

**Its central artifact is the disqualified form.** Story files are markdown with agreed section
headings, and `scripts/lint-story.py` enforces that structure carefully. Rule 1 is explicit
that this is the substitution the course names as not counting. Story files are consumed by
`test-writer` and `implementer`, so the main hand-off of the implementation phase is precisely
the excluded representation. The lint is a good check of a representation that cannot qualify.

**No node is Stage 3 certified.** There is no eval suite for the orchestrator or any of its 12
role agents. The certification skill's own words: *"An uncertified node makes the end-to-end
number meaningless."*

**It is the wrong size to submit.** Stage 4's scale is a chain of roughly 2–3 nodes; it says
outright *"It is not 'certify all forty of my agents'."* The sdlc pipeline is four phases, a
maker-checker-clarifier per phase, and 12 role agents — around 13 nodes. Submitted whole it is
Stage 3 repeated thirteen times.

That last point is the one that generalises, and it is what this change is really about. **A
large workflow is never one certified chain. It is a sequence of certified segments joined by
deterministic edges and human gates.** `add-jira-triage-profile` already found this for
`delivery-flow` — profiles slice a 15-step table into a certifiable 6-step one — but it
implemented it as delivery-flow-private machinery. The substrate is where the reusable value
is, and extracting it is what makes the third and fourth workflows cheap instead of each one
re-deriving registry, router, trace, edge dispatch, outcome and certification enforcement from
scratch.

## What Changes

- **Extract the certification substrate.** `scripts/workflow/` gains the workflow-agnostic core
  that `scripts/delivery-flow/` currently owns privately: the step registry loader, the
  profile-aware router, trace append, edge dispatch, outcome writing with manual-correction
  detection, and `check-certification.py`. A workflow becomes a **descriptor** — a step table, a
  schema directory, an artifact root — rather than a bespoke set of scripts. `delivery-flow`
  becomes its first consumer and keeps its current import paths behind a shim.

- **Generalise the hooks.** `check-edge.py` and `trace-step.py` stop keying on
  `delivery/<ITEM-KEY>/` and `.delivery-flow.yaml`, and instead resolve the active workflow
  descriptor from the repo. Both stay inert where no descriptor is present, so nothing changes
  for repos that have neither workflow.

- **Segment the sdlc pipeline.** `skills/sdlc-orchestration/steps.yaml` registers the pipeline
  as named segments of 2–3 nodes each, with a declared terminus per segment and a schema-backed
  hand-off artifact between segments. Prose survives only where a human is the reader.

- **Make the story a data contract.** `story.json` against a schema becomes the artifact nodes
  consume; `story.md` becomes a rendered human view, generated from it. `lint-story.py` is
  rewritten as a schema validator plus the renderer's shared coverage check — the
  `brief.py`/`render-brief.py` pattern already in the repo, where the renderer and the hook
  cannot disagree about what the artifact is.

- **Move the readiness gate into a hook.** The lint and `openspec validate` run on
  `PostToolUse` after the story set is written, record a verdict in the trace, and the
  orchestrator refuses to advance past a failed edge — rather than being two commands the
  orchestrator is trusted to invoke.

- **Turn maker-checker into a node plus an edge.** The reviewer runs in a fresh context, carries
  its own Stage 3 certification, and emits a structured verdict
  (`REFUTED` / `WEAKENED` / `SURVIVED`, the vocabulary `agents/adversarial-validator.md`
  already uses). A harness applies fixed rules to that verdict; the orchestrator does not get
  to interpret it.

- **Certify the first segment only.** The **readiness segment** — `story-planner` →
  `readiness-reviewer` — is the first chain to certify: two nodes, both deterministic edges
  already exist, and `CONCERNS = FAIL` is already a fixed rule. Every other segment is
  registered but marked uncertified, and the certification check blocks delegation to an
  uncertified step exactly as it does in `delivery-flow`.

- **Punch-outs and their attack evidence.** sdlc's human gates adopt
  `hooks/enforce-punch-outs.py` through the shared substrate, and the 15-attack bypass suite in
  `tests/delivery-flow/bypass/` is generalised to run against any registered workflow's gates.

- **Correct one inconsistency.** `skills/sdlc-orchestration/SKILL.md` tells the reader to use a
  *"separate, stronger model for validation"*. `workflow-certification` calls that a misreading:
  the checker must *differ* from the generator, and *"It does not mean 'use the big model'."*
  The line changes, and the model policy becomes haiku-first with committed escalation evidence.

## Impact

- **Affected specs:** `workflow-certification-substrate` (new), `sdlc-story-contract` (new),
  `sdlc-readiness-segment` (new).
- **Affected code:** new `scripts/workflow/`; `scripts/delivery-flow/*` reduced to
  delivery-specific steps behind a compatibility shim; `hooks/check-edge.py`,
  `hooks/trace-step.py`, `hooks/enforce-punch-outs.py` generalised;
  `scripts/lint-story.py` rewritten; new `skills/sdlc-orchestration/steps.yaml`;
  `schemas/story.schema.json` and `schemas/readiness-verdict.schema.json` added;
  `tests/delivery-flow/bypass/` generalised.
- **Docs that must change in the same PR** (per `CLAUDE.md`): `docs/using-the-sdlc-dev-team.md`,
  the affected `docs/figures/*.svg` (`readiness-gate`, `sdlc-pipeline`, `human-gates`),
  `agents/README.md`, `skills/sdlc-orchestration/SKILL.md`, the `skills/prime/` team bindings,
  and the three-place dev-pair territory definition if the boundary hook moves.
- **Sequencing constraint:** none of the substrate extraction lands until the `delivery-flow`
  submission is accepted. Refactoring the thing under review, while it is under review, trades
  a certification for a tidier tree.
