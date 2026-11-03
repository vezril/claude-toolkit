# delivery-flow: the next three workflows

*Assessment of three proposed workflows — AWS testing, ready-to-PR, PR review — against what
delivery-flow's routing table already declares. Nothing built. Written 2026-11-03.*

## The verdict in one line

**One of the three is a new workflow. The other two are steps delivery-flow already has.**

| Proposed | What it actually is | Where it goes |
|---|---|---|
| 1. AWS testing harness | `verify` (step 9) done properly | A step, unless it runs without a ticket |
| 2. Ready to PR | Steps 11–14, already declared | A `ship` profile |
| 3a. Review a colleague's PR | Genuinely new — different entry point | A new workflow |
| 3b. Act on review of my own PR | A resumption of delivery-flow | A new step |

## The constraint that should decide all of it

**Stage 4 certification is per workflow.** Each one needs its own `prompt-edd` package per node
(≥3 criteria, ≥95% of asserts, a load-bearing map, an iteration log, three consecutive runs),
its own deterministic guardrails, its own adversarial punch-out evidence, its own success rate
over *real* runs, and its own audit trail.

delivery-flow took weeks and, as of today, has **one** clean certified run. Three more workflows
is three more of that, in parallel, before any of them has a number.

A step *inside* delivery-flow inherits the edge hooks, the trace, the punch-out triggers, the
signed decisions and the report for free. That asymmetry is large enough that the default
answer to "should this be a workflow?" is **no, unless it has a different entry point.**

## 1. AWS testing harness

Step 9 is `verify.json`, currently "the repo's test command + protected-paths check". An
integration harness running against real AWS resources is that step with teeth, not a new
pipeline.

Two things make it more than routine:

- **It costs money**, so a run that loops is a bill rather than a slow afternoon.
- **It touches real resources**, so the blast radius is outside the repo.

Both put it behind a punch-out, and the config already has the vocabulary —
`deploy.auto_roll.never: [api, schema, breaking, first-deploy, exposure]`. Reuse that rather
than inventing a second gating concept.

**The question that decides workflow-vs-step:** does it ever run *without* a ticket? A nightly
regression sweep against AWS says yes and wants its own entry point. "Verify this item's
change" says no, and it is `verify`.

Note for whoever builds it: `verify` is one of the eight artifacts with **no schema**, so its
edge currently records `no-schema` and checks nothing. Giving it a real contract is part of
this work, not a separate cleanup.

## 2. Ready to PR

Already modelled. The `full` profile declares, in order:

```
pr-description → open-pr → post-summary → post-back
```

with `adapters/github_pr.py` behind `open-pr` and a certified `pr-description` prompt (it is
one of the four steps in `steps.yaml`). Building this as a separate workflow would duplicate
all of it and create a second thing to keep in step with the forge adapter.

What is genuinely missing is small:

- **commit and push the ticket's worktree** — `ensure-worktree.py` makes
  `delivery/<KEY>`, and nothing yet commits it;
- **attach verify results to the PR body** — `pr-description` has the artifacts but does not
  carry the test evidence;
- a **`ship` profile** in `templates/delivery-flow/profiles.yaml`, so the PR steps can run
  without re-triaging an item that is already implemented.

That is hours of work inside existing steps, and it needs no new certification: `pr-description`
is already certified, and the adapters are deterministic.

## 3. PR review — two workflows wearing one name

These have incompatible shapes and should not be one thing.

### 3a. Reviewing a colleague's PR — a new workflow

Not ticket-driven. The entry point is a PR URL, not a tracker item. It has no breakdown, no
proposal, and no vault memory of your own work to recall — the vault would be read for *their*
project context, if at all. The artifact chain is its own: PR → diff → findings → posted
review.

This is the one that justifies being a workflow, and it is also the one with a real
prior-art advantage: `code-review`, `adversarial-validator` and the language reviewers already
exist as skills and agents. The workflow is the orchestration and the guardrails, not the
reviewing.

**Its punch-out is obvious and non-negotiable:** posting a review to someone else's PR is an
outward action on a colleague's work. `tracker.external: true` is the existing precedent — a
post needs a signed decision.

### 3b. Acting on review feedback on your own PR — a new step

This is a *resumption* of delivery-flow after `open-pr`, and the current design has **no
concept of looping backwards**. Today the routing table is linear and `flow-status.py` computes
"the next step that has no artifact". Review feedback means re-entering at `implementation`
with new findings, which is the same shape as a `REFUTED` challenge verdict — and that already
has a rule: rerun the producing step with the findings, twice is a punch-out.

So the cheapest honest version is a step that fetches review comments into an artifact
(`review.json`) and feeds it to `carry_forward`, which the implementation step already knows
how to consume. No new workflow, and it reuses the one loop-back mechanism the design has.

## Recommended order

1. **Finish Stage 4 first.** A second workflow started before the first is certified doubles
   the unfinished work, and the current state is one clean run against a five-criteria
   submission. This is the whole recommendation; the rest is sequencing after it.
2. **#2's missing pieces** — commit/push the worktree, verify results in the PR body, a `ship`
   profile. Cheapest, no new certification, and it closes the ticket-to-PR path end to end.
3. **#1 as a real `verify`** — with a schema, so the edge stops recording `no-schema`, and
   behind the existing punch-out vocabulary.
4. **#3b** — `review.json` into `carry_forward`. Small, and it makes the PR path round-trip.
5. **#3a as a new workflow**, last, when there is appetite for a second certification package.

## What this assessment assumed

Worth re-checking rather than inheriting:

- That `verify` is still "the repo's test command". It is, as of 0.17.0.
- That `pr-description` is certified and the other three PR-path steps are deterministic
  adapters. True today — `steps.yaml` carries four certified steps and `pr-description` is one.
- That nothing in the routing table loops. True: `flow-status.py`'s `STEPS` is a flat ordered
  list, and profile handover is forward-only.
