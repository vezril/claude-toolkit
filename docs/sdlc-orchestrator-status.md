# SDLC orchestrator build — running status

Short and overwritten each session. Full spec is
`openspec/changes/certify-sdlc-pipeline/`. Last updated 2026-11-16.

## Where it stands

**43 of 60 tasks done, 15 retired, 2 open — and both open ones wait on something
other than code.** The readiness segment is certified, runs on haiku, and its
delegation gate is now confirmed at runtime. Seven of nine sections are closed.

| Section | State |
|---|---|
| 0. Sequencing | 0.2 and 0.3 open — both wait on the review, not on us |
| 1. Substrate extraction | Done |
| 2. Generalise the hooks | Done |
| 3. Story as data contract | Retired. Cleanup landed as PR #129 |
| 4. Register pipeline as segments | Done |
| 5. Certify readiness segment | Done — certified, and confirmed at runtime |
| 6. Punch-outs and attack evidence | Done |
| 7. Audit trail and success rate | 7.5 open — needs real runs |
| 8. Documentation | Done |

Certification, from `skills/sdlc-orchestration/steps.yaml` rather than from this
table: **1 of 6 segments.** The two `readiness` nodes are `certified: true` on
haiku. `analysis`, `planning`, `solutioning`, `implementation` and `verification`
are all `certified: false`. No end-to-end rate is asserted, by design.

## Not decisions — answers that arrive with the review

Tasks 0.2 and 0.3 are **blocked on the review coming back**, not on anyone asking
anything. Nobody owes a question. Recorded here so they are not mistaken for
pending actions.

**0.2 — is a pipeline of certified 2–3 node segments, joined by deterministic
edges, certifiable segment by segment?** The change's one load-bearing unknown.
The assumption is this project's own; it is not in the deck. Nothing shipped
depends on the answer and a "no" costs no rework — per-segment certification is
the submittable unit either way, and the pipeline-level claim is already hedged
in `skills/workflow-certification/SKILL.md` (records the rule as unconfirmed) and
`delivery-report.py` (refuses a pipeline-wide rate).

**0.3 — do knowledge skills loaded as context need their own certification?**
Pure sizing. sdlc loads many more knowledge skills than delivery-flow, so the
answer sets the cost of everything after `readiness`. Nothing shipped depends on
it.

## The only actionable work left

**Run the pipeline on real items. Task 7.5 is the last one, and it needs runs,
not code.**

The readiness success rate stays meaningless until real runs at story granularity
produce it. The evals in `evals/readiness-stories/` and `evals/readiness-review/`
guard regressions; they do not generate a rate. Nothing can be built to shortcut
this — it accumulates from use.

5.6 is closed. `tests/workflow/readiness/run-readiness.py` drives the real
`check-certification.py` and confirms both runtime claims: delegation to the two
certified nodes is permitted, and editing either live prompt re-blocks its node.
Evidence is committed at
`tests/workflow/readiness/readiness-gate-report.md`.

Worth knowing why that mattered: **nothing had ever invoked the gate.** Every
reference to `check-certification.py` was a doc or a unit test, so the control
that blocks delegation to an uncertified step had no caller — the same
present-but-checking-nothing defect as the three in the section below.

## Known gap, not forgotten

`claude-haiku-5-5` is absent from the pricing table (it covers
`claude-haiku-4-5`), so every haiku step records `api_equivalent_cost_usd: null`
with `pricing_missing: true`. Both certified nodes run on haiku, so criterion 4's
cost figures currently omit the cheapest and most-used tier.

This needs a published price. It will not be invented — a guessed price is worse
than none. A test in `tests/workflow/test_audit_trail.py` asserts the gap exists
and says to delete itself once a real price is added.

## The finding worth keeping

The recurring defect class this change kept hitting: **a checker that is present,
successful, and checking nothing.** Right checker, wrong input.

`enforce-punch-outs.py` recognised an sdlc repo and then looked for its artifacts
in `delivery/`, so it permitted everything — and reported nothing, because "no
punch-out is open" and "I looked in the wrong place" produce the same silence.
`delivery-report.py` could not see an sdlc run at all. `check-protected-paths.py`
matched `protected_paths:` only at column 0, so it found no block in either
config that nests the key. Each was caught by a refuse-to-pass-by-absence rule,
not by reading the code.
