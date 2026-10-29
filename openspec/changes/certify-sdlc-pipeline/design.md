## Context

`delivery-flow` was built to be certified at Stage 4 and is the submission. This change is
about the thing the certification is *for*: continuing to build workflows, including large ones,
without each new workflow re-deriving the whole certification apparatus.

The sdlc pipeline is the large one. It has four phases, a maker-checker-clarifier pattern per
phase, 12 role agents, and a human gate between phases. Measured against
`skills/workflow-certification/` it fails three of five criteria and partially meets a fourth.

The constraint that shapes every decision below: **Stage 4's unit of certification is a chain of
2–3 nodes.** A 13-node pipeline cannot be submitted, and padding it with more guardrails does
not change that. So the question is not "how do we certify the sdlc pipeline" but "what is the
composition rule by which a pipeline made of certified chains is itself trustworthy".

`add-jira-triage-profile` answered that for one workflow with profiles: a named ordered subset
of a step table, with a declared terminus that writes `outcome.json` and stops. It works, and
it is currently private to `scripts/delivery-flow/`. The reusable asset is the substrate, not
the delivery steps.

## Goals / Non-Goals

**Goals**

- A workflow-agnostic substrate: registry, router, trace, edge dispatch, outcome, certification
  enforcement, punch-out enforcement, bypass harness.
- The sdlc pipeline registered as certifiable segments with schema-backed hand-offs.
- One segment — readiness — actually certified, end to end, with real runs.
- A documented composition rule so segment three onward is mechanical.

**Non-Goals**

- Certifying all 12 role agents. Each segment gets certified when it is needed, not up front.
- Certifying the whole pipeline in this change. The end-to-end rate for a 13-node chain is a
  later problem and may never be worth buying.
- Touching `delivery-flow`'s behaviour. Its artifacts, paths and step names stay as submitted.
- Replacing markdown everywhere. Prose is legitimate where a human is the reader.

## Decisions

### D1 — Segments, not a monolith

A **segment** is a 2–3 node chain with: schema-backed artifacts between its nodes, a
deterministic edge hook after each node's write, a declared terminus, and a hand-off artifact
that is either schema-backed data (consumed by the next segment) or prose (read by a human at a
gate). Each segment is independently Stage 3 certified per node and independently submittable.

The pipeline is then trustworthy *by composition*: every intra-segment hand-off is schema-checked
by a hook, and every inter-segment join is either an edge or a human punch-out. Nothing anywhere
depends on a model choosing to run a check.

Proposed segmentation, which also tells you the certification order:

| Segment | Nodes | Hand-off out |
|---|---|---|
| `analysis` | analyst → (human gate) | `brief.json` |
| `planning` | pm → requirements-reviewer | `prd.json` |
| `solutioning` | solution-architect → adversarial-validator | `design.json` + OpenSpec change dir |
| **`readiness`** | **story-planner → readiness-reviewer** | **`story.json[]` + verdict** |
| `implementation` | test-writer → implementer | diff + test results |
| `verification` | reviewers (fan-out) → ci-watcher | `outcome.json` |

### D2 — Extract the substrate, but only after submission

`scripts/workflow/` takes the workflow-agnostic core. A workflow supplies a **descriptor**
(`workflow.yaml`: step table, schema dir, artifact root, profiles, punch-out triggers) and the
substrate does the rest. `delivery-flow` becomes consumer one; its current module paths remain
as thin re-export shims so nothing in the submitted tree changes shape.

**Sequencing is a hard constraint, not a preference.** No extraction lands until the
`delivery-flow` submission is accepted. Refactoring the artifact under review while it is under
review risks the certification to tidy the tree, which is the wrong trade at any price. Phase 0
of `tasks.md` is a gate on that, not a checklist item.

### D3 — The story becomes data; markdown becomes a view

`story.json` validated against `schemas/story.schema.json` is the artifact `test-writer` and
`implementer` consume. `story.md` is generated from it for humans and is never parsed.

This is the `brief.py` pattern already in the repo: the renderer and the checker import the same
module, so they cannot disagree about what the artifact is. `lint-story.py` keeps its name and
its CLI, and becomes a schema validator plus the semantic checks a schema cannot express —
Given/When/Then grammar, task↔AC closure, resolvable references, FR/CAP traceability.

Rejected: keeping markdown and arguing the lint makes it a contract. That is exactly the
substitution Rule 1 names, and a reviewer who knows the course will reject it. Writing a
proposal that depends on a reviewer not noticing is not a plan.

### D4 — The readiness gate moves onto a hook

Today `SKILL.md` instructs the orchestrator to run `lint-story.py` and `openspec validate`. Both
are deterministic and neither is a guardrail, because a model that skips them produces no
failure. They move into `check-edge.py`'s dispatch on `PostToolUse`, keyed by the artifact
written, recording a verdict in the trace either way.

A `PostToolUse` hook cannot un-write a file, and the design does not pretend otherwise: the
verdict is recorded and the orchestrator refuses to advance past a failed edge. That is the same
honesty `workflow-certification` requires of `delivery-flow`.

`enforce-dev-pair-boundary.py` stays `PreToolUse`. It is prevention rather than verification —
it stops the write rather than judging it — and it already satisfies the unskippability test.

### D5 — The reviewer is a node; the rules are the edge

Maker-checker becomes: reviewer node in a **fresh context**, with its **own Stage 3
certification**, emitting a verdict against `schemas/readiness-verdict.schema.json`
(`REFUTED` / `WEAKENED` / `SURVIVED` plus findings). A harness in the substrate applies fixed
rules — `REFUTED` reruns the producing node, `WEAKENED` requires every finding addressed before
advance, `SURVIVED` proceeds — and the orchestrator does not interpret the verdict.

`agents/adversarial-validator.md` already uses that vocabulary and already has an eval suite
(`evals/cross-examine/`, 0% → 100% at N=3). It is the readiness reviewer candidate, and the
cheapest certified reviewer available. Note its suite currently tests format heavily and
reasoning lightly; promoting it to a certified node means strengthening the reasoning asserts
first, not reusing the number as-is.

### D6 — Certify readiness first

It is the cheapest real win: two nodes, both deterministic edges already written, one fixed rule
(`CONCERNS = FAIL`) already specified, and a bounded ~3-iteration loop already designed. Every
other segment registers in `steps.yaml` as uncertified, and `check-certification.py` blocks
delegation to an uncertified step — so the pipeline stays honest about what it can and cannot
run unattended.

### D7 — Model policy inverts

sdlc currently says "use a separate, stronger model for validation". The substrate enforces the
certification skill's reading instead: **haiku first, then sonnet, frontier only with a committed
results file showing the cheaper tier below the bar on the same suite.** The checker must differ
from the generator — a different model, or the same model in a fresh context with a
refute-framed prompt — which is not the same as "use the big model". Traces record the model a
step *actually ran on* and flag drift from the declared tier.

### D8 — The run unit for the success rate is one story, not one project

Criterion four needs real runs, and a 13-node project-scale run produces a denominator of three
in a quarter. The unit is therefore **one story through the readiness and implementation
segments**, which produces runs at a useful rate. `write-outcome.py` distinguishes
`completed` / `punched-out` / `failed` / `abandoned`, and detects manual correction by comparing
the artifact sha to the trace — a hand-edit to make a gate pass is a failed run, not a repair.

Both readings of the punch-out denominator are emitted, as `delivery-flow` already does, since
whether punched-out runs belong inside it is a question for the reviewer.

### D9 — Prose only at human-read boundaries

`brief.md`, `summary.md`, rendered `story.md`, review reports for people: all fine. The rule is
mechanical — if a node consumes it, it has a schema; if only a human reads it, it can be prose.
Every segment hand-off in the D1 table is named accordingly.

## Risks / Trade-offs

- **The extraction destabilises the submitted workflow.** Highest risk here. Mitigated by
  sequencing (D2), by shims rather than moves, and by requiring the existing
  `tests/delivery-flow/` suite plus the bypass suite to pass unchanged before and after.
- **Cost.** Each certified node needs a `prompt-edd` package: ≥3 criteria, ≥95% of asserts, a
  load-bearing map, an iteration log, three consecutive runs, escalation evidence. The recent
  nine-skill EDD batch ran 78 model runs for suites far simpler than these. Certifying the
  readiness segment is two nodes; certifying all six segments is twelve. **Budget per segment and
  stop when the value stops** — the composition rule means an uncertified segment degrades to a
  human gate rather than breaking the pipeline.
- **Story JSON is a breaking change** for any existing story file and for `test-writer` /
  `implementer` prompts. Mitigated by the renderer and a one-shot migration script, but the
  three-place dev-pair territory definition and the story-schema reference must move together.
- **A thirteen-node end-to-end rate may never be good.** Each segment's rate multiplies. This is
  an argument for certifying segments and reporting per-segment rates rather than promising a
  pipeline number, and it should be said to the reviewer rather than discovered by them.
- **`openspec validate` is an external CLI** inside an edge. It is deterministic, which is what
  the rule requires, but its absence must block rather than pass — as the current gate already
  specifies.

## Migration Plan

1. Submission of `delivery-flow` accepted. Nothing before this.
2. `scripts/workflow/` added; `delivery-flow` re-pointed behind shims; full existing test and
   bypass suites green with no diff in behaviour.
3. Hooks generalised to resolve a descriptor; both workflows inert where no descriptor exists.
4. `schemas/story.schema.json`, the rewritten `lint-story.py`, the renderer, the migration
   script. Docs and figures in the same PR.
5. `skills/sdlc-orchestration/steps.yaml` registering all six segments, readiness alone
   certifiable, everything else blocked by `check-certification.py`.
6. EDD packages for `story-planner` and the readiness reviewer; three consecutive runs each.
7. Bypass suite generalised and run against sdlc's gates; holes fixed and recorded.
8. Real runs at story granularity until the rate means something.

## Open Questions

1. **Does a reviewer accept composition at all?** The whole plan rests on "a pipeline of
   certified segments joined by edges is certifiable segment by segment". That reading is mine,
   not the deck's. Ask before building step 5 onward — it is the one assumption that invalidates
   everything if wrong.
2. **Do knowledge skills loaded as context need their own certification?** `workflow-certification`
   records this as unconfirmed and assumes they are covered by the consuming agent's eval. sdlc
   loads far more of them than delivery-flow does, so the answer matters more here.
3. **Are punched-out runs inside the success-rate denominator?** Both readings emitted until
   someone rules.
4. **Is `evals/cross-examine/` reusable as the readiness reviewer's certification**, or does the
   reviewer need its own suite because the artifact under review is different? Leaning toward its
   own suite.
5. **Where does the dev-pair boundary hook live** once territories are defined by `story.json`
   rather than by path convention?
