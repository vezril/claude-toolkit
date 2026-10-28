# Iteration log: breakdown node

The second node of the certified chain, and the one the Stage 4 course uses as its own
example: a PRD breakdown "only counts as Stage 4 if that breakdown is YAML against a fixed
schema — not a written summary". This node reads `item.json` and `triage.json` and writes
`breakdown.json`: epics → stories → acceptance criteria.

Fixtures are the six standard-path items from the triage suite — the ones a breakdown
actually runs on — each paired with the triage artifact the certified triage node produces.
Four deterministic criteria: schema (via the same `validate-artifact.py` the edge hook runs),
coverage (every deliverable the item asks for appears, as keyword groups), acceptance (the
criteria are distinct, specific, and assert observable outcomes), scope (right item key,
story domains drawn from triage's, nothing invented, a reviewable size).

Three repeats per case per model; the bar is 95% per run.

## v1 baseline (Red): Haiku 44/68 (64.7%), Sonnet 52/72 (72.2%)

**Baseline:** none; this is it.
**Hypothesis:** none.
**Change:** none — the naive instruction, naming the fields and nothing else.
**Result:** Haiku 44/68 (64.7%), Sonnet 52/72 (72.2%).

| criterion | Haiku | Sonnet |
|-----------|-------|--------|
| schema | 0/17 | 0/18 |
| coverage | 15/17 | 18/18 |
| acceptance | 16/17 | 18/18 |
| scope | 13/17 | 16/18 |

**Reasoning:** the same shape as the triage baseline — the content is largely right and the
contract is entirely absent. Schema is 0 on both models with no output contract. What is
different, and worth noting before iterating: coverage and acceptance are already near
perfect, so the work this node does is not the problem. Both models break an item into
sensible stories with specific criteria when simply asked. Scope is the softer edge (13/17
and 16/18) and the failures there are the interesting ones.

One Haiku case errored in the provider, so n is 17 rather than 18 for that model.

## v2 result: Haiku 51/72 (70.8%), Sonnet 69/72 (95.8%)

**Baseline:** Haiku 44/68, Sonnet 52/72 (v1).
**Hypothesis:** an output contract flips schema; content criteria stay where they are.
**Change:** the output contract only — raw JSON, the exact shape, the id patterns, the
`json.loads` consequence for a fence.
**Result:** Haiku 51/72 (70.8%), Sonnet 69/72 (95.8%).
**Reasoning:** Sonnet's schema went 0 → 16/18 and the suite landed above the bar on the first
contract, which says the judgement was never the problem here — only the shape. Per repeat,
though: 100%, 87.5%, 100%. Run 2 is under the bar, so this is not certifiable yet.

| criterion | Haiku v1 → v2 | Sonnet v1 → v2 |
|-----------|---------------|----------------|
| schema | 0 → 0 | 0 → 16 |
| coverage | 15 → 18 | 18 → 18 |
| acceptance | 16 → 17 | 18 → 18 |
| scope | 13 → 16 | 16 → 17 |

**Haiku's schema stayed at 0/18, with the same cause as the triage node: it fences the
object.** Two nodes, two suites, the same model-specific habit — the triage finding
generalises, and this node will certify on Sonnet too.

Sonnet's three remaining failures are all in run 2: two fenced replies, and one story set
tagged with the domain `security`, which is not in the roster vocabulary. The prompt never
gave the vocabulary, so that one is my omission rather than the model's invention.

## v3 hypothesis (written before the run)

**Change:** the domain rule only — the eight roster words, the instruction to draw from the
set triage already found (fewer, never more), and "a technology is not a domain".

**Prediction:** scope 17 → 18. Schema unchanged at ~16/18: nothing in this change speaks to
fences, and I will deal with those separately rather than claiming them here.

## v3 result (Sonnet): 68/72 (94.4%)

**Baseline:** Sonnet 69/72 (v2).
**Hypothesis:** scope 17 → 18; schema unchanged at ~16.
**Change:** the domain rule only.
**Result:** 68/72 (94.4%). Scope 17 → 18 as predicted. Schema also went 16 → 18, which I did
not predict and will not claim: nothing in this change mentions fences, and v2's two fenced
replies were both in one repeat, so the honest reading is that the fences were variance rather
than something v3 fixed.
**Reasoning:** the total went *down* because coverage and acceptance each lost two asserts, and
reading them they are not a side effect of the domain rule: two stories carried two acceptance
criteria ending in the same outcome, and two runs dropped a detail the item mentions once
("becomes a Client Component", "replay should be idempotent"). Story counts stayed healthy
(3–10 per case), so the breakdown did not get smaller or coarser.

These are gaps in what I told the model a breakdown must contain, not damage from v3.

## v4 hypothesis (written before the run)

**Change:** a "Covering the item" section — account for everything the item names, including a
detail mentioned once in passing, and no two acceptance criteria in a story may assert the same
outcome.

**Prediction:** coverage 16 → 18 and acceptance 16 → 18. Schema and scope hold at 18.

## v4 result (Sonnet): 70/72 (97.2%) — and a second wrong assert

**Baseline:** Sonnet 68/72 (v3).
**Hypothesis:** coverage 16 → 18 and acceptance 16 → 18.
**Change:** a "Covering the item" section — account for every change the item names, including
a detail mentioned once; no two criteria in a story assert the same outcome.
**Result:** as first scored, 68/72 (94.4%) with coverage 17 and acceptance 15. On the corrected
assert below, 70/72 (97.2%).
**Reasoning:** every acceptance failure was the same case, and reading the outputs my assert was
wrong, not the model. `auth-tenancy` produced criteria like "given a missing token … then the
request is rejected" and "given an expired token … then the request is rejected". Sharing an
outcome across different preconditions is how you write authentication tests; my check flagged
any repeated `then` as a duplicate.

Corrected to compare the whole given/when/then triple, which is what "the same criterion twice"
actually means, and every prior version re-scored through `rescore.js` with no model calls:

| Run | schema | coverage | acceptance | scope | Total |
|-----|--------|----------|------------|-------|-------|
| v1 Haiku | 0/17 | 15/17 | 16/17 | 13/17 | 44/68 (64.7%) |
| v1 Sonnet | 0/18 | 18/18 | 18/18 | 16/18 | 52/72 (72.2%) |
| v2 Haiku | 0/18 | 18/18 | 17/18 | 16/18 | 51/72 (70.8%) |
| v2 Sonnet | 16/18 | 18/18 | 18/18 | 17/18 | 69/72 (95.8%) |
| v3 Sonnet | 18/18 | 16/18 | 18/18 | 18/18 | 70/72 (97.2%) |
| v4 Sonnet | 18/18 | 17/18 | 17/18 | 18/18 | 70/72 (97.2%) |

This is the second time in two nodes that the model disagreeing with me in the same direction
meant my assert was wrong. That is becoming the most useful signal in the suite.

## v5: refactor to Role / Task / Context / Constraints — regressed

**Baseline:** Sonnet 70/72 (v4).
**Hypothesis:** restructuring costs nothing.
**Change:** structure only, with the rules reorganised into Role, Task, Context, Output and
Constraints.
**Result:** three consecutive runs at 83.3%, 91.7%, 91.7% — all below the bar.
**Reasoning:** seven of the eight failures are fenced replies, and the cause is in the diff.
v2–v4 kept the fence rule and its consequence in one place: "no code fence. Your reply is
written straight to `breakdown.json` and parsed by `json.loads` with no cleanup step, so a
fence is a parse error". The refactor moved the consequence up into Context and left Output
with a bare "a fence is a parse error and the step fails". Splitting a rule from the reason it
exists cost 7 of 18 runs.

The refactor's re-run earned its place again: the restructure looked harmless and was not.

## v6 hypothesis (written before the run)

**Change:** put the full consequence back beside the rule in Output, and add the compact
worked-example line that holds Sonnet's schema at 30/30 in the triage suite.

**Prediction:** schema back to 18/18 across three runs; coverage, acceptance and scope
unchanged. One coverage miss on `idempoten` may persist — it has survived three versions now.

## v6 result (Sonnet): certified — 100%, 95.8%, 100%

**Baseline:** Sonnet 83.3 / 91.7 / 91.7% (v5).
**Hypothesis:** schema back to 18/18 across three runs; everything else unchanged.
**Change:** the fence rule and its consequence back in one place, plus the compact
worked-example line proven in the triage suite.
**Result:** three consecutive runs at 100%, 95.8% and 100% — each over the bar on its own.
**Reasoning:** the regression was exactly what the diff said it was. Putting the reason back
beside the rule recovered every fenced run, and the refactor's structure survived intact: v6 is
v5's Role/Task/Context/Constraints shape with one paragraph moved back where it belongs.

The single remaining failure across all three runs is the `idempoten` coverage miss on the DLQ
item, which has now survived four versions. The item mentions idempotency once, in a subordinate
clause; the model writes stories for browsing, inspecting and redriving and lets that detail go.
It sits inside the bar, so it is recorded here rather than chased with a rule aimed at one case.

## Score progression (corrected basis)

| Run | Change | schema | coverage | acceptance | scope | Total |
|-----|--------|--------|----------|------------|-------|-------|
| v1 Haiku | naive | 0/17 | 15/17 | 16/17 | 13/17 | 44/68 (64.7%) |
| v1 Sonnet | naive | 0/18 | 18/18 | 18/18 | 16/18 | 52/72 (72.2%) |
| v2 Haiku | output contract | 0/18 | 18/18 | 17/18 | 16/18 | 51/72 (70.8%) |
| v2 Sonnet | output contract | 16/18 | 18/18 | 18/18 | 17/18 | 69/72 (95.8%) |
| v3 Sonnet | domain rule | 18/18 | 16/18 | 18/18 | 18/18 | 70/72 (97.2%) |
| v4 Sonnet | covering the item | 18/18 | 17/18 | 17/18 | 18/18 | 70/72 (97.2%) |
| v5 Sonnet | RTCC refactor | — | — | — | — | 83.3 / 91.7 / 91.7% |
| **v6 Sonnet** | **fence rule restored** | — | — | — | — | **100 / 95.8 / 100%** |

**Certification runs (v6, Sonnet, three consecutive):** 24/24, 23/24, 24/24.
Evidence: `results/run_v6_sonnet_run{1,2,3}.json`.

**Certified tier: Sonnet.** Haiku was tried first and recorded failing: with the same output
contract that took Sonnet to 95.8%, Haiku's schema stayed at 0/18 because it wraps the object
in a ```json fence — the identical habit that ruled it out for triage. Two nodes, two suites,
the same cause. Its planning was never weak (coverage 18/18, acceptance 17/18 at v2).
Evidence: `results/run_v2_all.json`.

## What I'd carry to the next node

- Keep a rule and the reason it exists in the same place. Moving the `json.loads` consequence
  one section away from "no code fence" cost 7 of 18 runs, and nothing else in that refactor
  mattered.
- The second wrong assert of this chain had the same tell as the first: the model disagreeing
  with me in one consistent direction. Criteria sharing an outcome across different
  preconditions is how authentication tests are written; my check called it duplication.
- A naive baseline that already scores 72% is not a reason to skip the contract. Everything
  this node got wrong at v1 was shape, and shape is what the next node consumes.
