# Iteration log: challenge-breakdown node

The third node of the certified chain, and the one the Stage 4 course is most specific
about. Its "reviewer trap" is exact: an LLM reviewing another LLM's output in shared context
is a second non-deterministic node that rationalizes rather than reviews. So this node is
certified as a node — fresh context, its own suite, a structured verdict — and the thing that
makes it a guardrail is not the node at all but the code that routes its verdict
(`flow-status.py`: REFUTED reruns the breakdown, WEAKENED carries findings forward,
SURVIVED proceeds, a verdict about a rewritten target is stale).

It reads `item.json`, `triage.json` and `breakdown.json` and writes
`challenge-breakdown.json`: a verdict, an attack log, and findings.

## Fixtures

Nine cases, built by `derive-fixtures.py` from the six outputs of
`evals/delivery-breakdown` run v6 / Sonnet / run 1 — every one of which passed all four
breakdown criteria. Two are left clean; seven carry exactly one planted defect, made of the
item's own words by a deletion, substitution or insertion. Run the script and the committed
`inputs/` are reproduced byte for byte, so the ground truth is auditable rather than asserted.

Epic and story ids are renumbered contiguously after the defect is planted (`renumber`).
Without that step the edit signed its own work and three runs had to be thrown away — see
**The fixture defect** below.

| case | defect | class | expected |
|------|--------|-------|----------|
| 01-clean-dlq | none | — | SURVIVED |
| 02-clean-sidebar | none | — | SURVIVED |
| 03-missing-deliverable | the zero-quantity / out-of-stock epic deleted | A1 | REFUTED |
| 04-contradicts-item | an epic migrating the journal the item says is unchanged | A2 | REFUTED |
| 05-unrequested-epic | an epic of Grafana dashboards and alerts nobody asked for | A3 | REFUTED |
| 06-criteria-miss-story | the toggle story's criteria test JVM metrics instead | B1 | WEAKENED |
| 07-vague-outcome | one `then` replaced with "the feature works correctly" | B2 | WEAKENED |
| 08-duplicate-stories | the out-of-stock story repeated in a second epic | B3 | WEAKENED |
| 09-wrong-domains | the sidebar story tagged `backend` | B4 | WEAKENED |

**Every one of the nine passes `breakdown.schema.json`.** That is deliberate and it is checked:
a defect the edge hook already catches would make this node look effective at work that is
not its job. The obvious candidate — a story with an empty `acceptance_criteria` array — was
dropped for exactly that reason, since the schema's `minItems: 1` fails it at the edge.

## Criteria

Four deterministic criteria, no LLM judge:

- **schema** — raw JSON conforming to `challenge-breakdown.json`, via the same
  `validate-artifact.py` the edge hook runs. The verdict enum and the three-attack floor
  live in the schema.
- **verdict** — the verdict equals the ground truth. Scored on its own because it is the
  only field the harness routes on.
- **detection** — the findings name the planted defect (keyword groups, so paraphrase
  survives). On the two clean cases the test runs the other way: it passes only with no
  findings at all.
- **discipline** — the log is honest: three distinct attacks, each with a method that says
  what was checked; landed/failed consistent with the verdict and with the findings; and
  every id and filename a finding cites exists in the material the node was given.

Three repeats per case per model; the bar is 95% per run, over three consecutive runs.

### Testing the test, before spending a single model call

`node asserts/self-test.js` scores 22 hand-built outputs whose verdict is known: a correct
REFUTED and a correct SURVIVED, a fenced reply, a prose preamble, a missed hole, a right
verdict with the wrong hole named, an invented hole on a clean breakdown, a citation of a
story that does not exist, SURVIVED with a landed attack, two attacks, the same attack three
times, methods that say nothing, REFUTED with nothing landed, WEAKENED where REFUTED is
right, and prose instead of JSON. All 22 scored as intended.

It also checks the opposite direction, which matters more than it sounds: one plausible
**correct** finding per planted defect must score as detected. A `must_find` group nothing
can satisfy makes a case unwinnable, and the suite would then read as the model failing when
the label was wrong — which has already happened twice in this chain.

## v1 baseline (Red)

**Baseline:** none; this is it.
**Hypothesis:** none.
**Change:** none — the naive instruction, naming the fields and nothing else.
**Run:** `./run.sh v1 haiku` and `./run.sh v1 sonnet`, 2026-10-27, 27 rows each. These are the
**second** v1 runs; the first pair was discarded against the leaky fixtures described below,
and nothing from them is reported here.

**Result:**

| model | total | schema | verdict | detection | discipline |
|---|---|---|---|---|---|
| haiku | 35/108 (32.4%) | 0/27 | 15/27 | 20/27 | 0/27 |
| sonnet | 33/108 (30.6%) | 0/27 | 14/27 | 19/27 | 0/27 |

**schema 0/27 on both, for two different reasons.** Haiku wrapped the reply in a
` ```json ` fence in **all 27** rows — the same failure that cost it triage (26/30) and
breakdown (0/18), now confirmed a third time on a third node. Sonnet failed 25/27 the same
way (preamble or fence); its other two failures are worth keeping, because both are clean
raw JSON spoiled by one detail. One wrote prose into `attacks[].result` where the schema has
the enum `landed` / `failed` ("All clauses are covered by at least…"), reading `result` as a
place to narrate the result rather than record it; the other was a correct object with
leading/trailing whitespace. v1 names the fields and never says `result` is an enum or that
the reply must start at `{`, so both are the prompt's fault, not the model's.

**discipline 0/27 on both, and this number is not meaningful.** Every single failure is
"no attack recorded as landed". v1 never asks for an attack log at all, so there is nothing
for the assert to read; the metric is measuring an absent instruction. It becomes real from
v2 on, once the output contract exists.

**Reasoning:** the content is largely right and the container is entirely wrong — the same
shape as the triage and breakdown baselines. Judgement is the strongest axis (detection
19–20/27) before any instruction about how to judge, while the two criteria the harness
depends on most, schema and verdict, are at or near zero. So the first iteration is the
output contract, and the verdict rule follows it; nothing about finding defects needs
touching yet.

**No fabricated ids at baseline: 0 rows on either model.** This is a correction to an
earlier reading of this suite. The first v1 runs showed 4 rows citing ids absent from the
breakdown (E3/S4/S5, E4/E8/S8, E5/E8), which looked like baseline fabrication and like
v4's justification. On the corrected fixtures it is zero on both models. The models were
not fabricating; the fixtures were inviting it. **v4's anti-fabrication rule is therefore
addressing a failure this suite has never actually observed**, and that needs re-examining
before v4 is run rather than after.

**The verdict collapse is the headline.** Ground truth across 27 rows is 6 SURVIVED,
9 REFUTED, 12 WEAKENED. What came back:

| model | SURVIVED | WEAKENED | REFUTED | unparsable |
|---|---|---|---|---|
| haiku | 0 | 17 | 3 | 7 |
| sonnet | 0 | 21 | 2 | 4 |

**Neither model said SURVIVED once.** Given no rule for choosing between the three, both
hedge to WEAKENED — including on the two clean breakdowns, where they generated 6–11
findings each against an artifact with no planted defect. An adversarial reviewer with no
verdict rule does not review, it complains. This is exactly the failure v3's verdict rule is
staged to fix, and it is the single biggest contributor to the score.

**detection is the strongest axis even naive** (haiku 20/27, sonnet 19/27): the planted
defect is usually named. Judgement is not the problem; the output contract and the verdict
rule are. That matches the chain's earlier finding that Haiku's grounding was never at fault
(30/30 on triage).

**Haiku fails the naive prompt**, schema 0/27, driven by the fence. The model-tier policy is
discharged for the baseline: Haiku was tried first and the failure is recorded. Iteration
continues on Sonnet — but see **Haiku on the certified prompt** below, which overturns the
conclusion this paragraph originally drew from these numbers.

**Provenance.** Run through Bedrock on the work Mac (`CLAUDE_CODE_USE_BEDROCK=1`,
`us-west-2`), not the personal Mac. The results record `claude-haiku-5-5` and
`claude-sonnet-5-5` — *not* the `global.anthropic.*` ids the handoff predicted, so that
worry does not materialise. There is still a smaller discrepancy for a reviewer to notice:
triage and breakdown carry `claude-sonnet-5` and this node carries `claude-sonnet-5-5`.
`check-certification.py` matches the provider label (`sonnet`), so no gate is affected.

## v2 output contract (Green on schema only)

**Baseline:** v1 sonnet, 33/108 (30.6%) — schema 0/27, verdict 14/27, detection 19/27,
discipline 0/27.
**Change, one concern:** the output contract and nothing else. Role and task framing, the
`json.loads` consequence kept in the same paragraph as "no code fence" (the refactor that
separated them cost breakdown 7 of 18 runs), an anchored literal first line, every key and
both enums spelled out, and the three-attack floor. **No verdict rule and no honesty or
anti-fabrication rule** — those are v3 and v4.

**Hypothesis:** written before the run.

1. **schema: 0/27 → 24+/27.** Both v1 failure modes are addressed where they occurred. The
   fence rule now carries its reason beside it and an anchored literal shows the first
   character; `attacks[].result` is now written as the enum `"landed" | "failed"` with a
   gloss, which is what the 5 clean-JSON Sonnet rows got wrong by narrating into it.
2. **discipline: becomes a real number for the first time, and I expect it to be bad —
   roughly 8–16/27.** v2 asks for the attack log, so the assert finally has something to
   read, but v2 says nothing about landed/failed being consistent with the verdict or with
   the findings, and nothing about only citing ids that exist. The 4 fabricated-id runs at
   baseline should persist.
3. **verdict: roughly flat, 14–19/27.** v2 adds no rule for choosing among the three
   verdicts, so the WEAKENED collapse should survive almost intact. **This is the
   falsifiable part.** If verdict jumps past ~20/27 the gain did not come from where I think
   it did — most likely the "assume it is wrong and hunt for the evidence" framing pushing
   toward REFUTED — and v3's verdict rule would then be solving an already-solved problem
   and need rescoping.
4. **detection: flat or slightly up, 18–23/27.** Judgement was never the weak axis.

**Result:** `./run.sh v2 sonnet`, 27 rows. **88/108 (81.5%)**, from a v1 sonnet baseline of
33/108 (30.6%).

| metric | v1 sonnet | v2 sonnet | hypothesis | verdict on the hypothesis |
|---|---|---|---|---|
| schema | 0/27 | **27/27** | 24+/27 | right, and at ceiling |
| verdict | 14/27 | 13/27 | 14–19/27 | right in direction, one below the range |
| detection | 19/27 | 21/27 | 18–23/27 | right |
| discipline | 0/27 | **27/27** | 8–16/27 | **wrong, and badly** |

**schema went to ceiling.** Both v1 failure modes are gone: no fence, no preamble, no
whitespace, and no prose in `attacks[].result`. Keeping the `json.loads` consequence in the
same paragraph as "no code fence", plus the anchored literal first line, did the work — the
same pairing whose separation cost breakdown 7 of 18 runs.

**discipline went to ceiling too, and my hypothesis was wrong.** I predicted 8–16/27 on the
reasoning that v2 says nothing about landed/failed being consistent with the verdict, so
consistency failures would persist. They did not occur at all. Spelling the enum as
`"landed" | "failed"` with the gloss "landed = it broke; failed = the artifact held" was
apparently enough to make the log self-consistent without a rule demanding it. Worth
remembering: a well-specified field did the job a behavioural rule was budgeted for.

**verdict did not move, exactly as predicted, and the shape of the failure is now precise.**
13/27, and all 14 failures fall into two groups with nothing else in them:

| what happened | rows | cases |
|---|---|---|
| clean breakdown called WEAKENED instead of SURVIVED | 6 | 01, 02 (3/3 each) |
| B-class incompleteness escalated to REFUTED | 8 | 06 (2/3), 07 (3/3), 08 (3/3) |

All three A-class cases pass as REFUTED 3/3, and B4 passes as WEAKENED 3/3. So:

1. **SURVIVED has never been emitted once** — 0 of 81 rows, across two models and two
   prompts. Neither model will declare a clean artifact clean.
2. **The hedge moved rather than resolved.** v1 collapsed everything to WEAKENED (21 of 27);
   v2 collapses to REFUTED (17 of 27). The adversarial framing ("assume it is wrong and hunt
   for the evidence") changed *which* verdict it over-uses without teaching it to
   discriminate. Over-escalating B to REFUTED is the expensive direction: in
   `flow-status.py` REFUTED reruns the producing step, so eight of these rows would rerun a
   breakdown that was merely incomplete, and twice on the same target is a punch-out.

**Reasoning:** the output contract did everything a contract can do and nothing it cannot.
Two criteria went to ceiling, and the one criterion that depends on judgement rather than
format did not move at all — which is the right outcome for a change that only described the
container. The surprise was discipline reaching 27/27 without a rule about honesty: a
well-specified enum field, `"landed" | "failed"` with its gloss, produced a self-consistent
log on its own, so the behavioural rule budgeted for it was never needed. The lesson I take
forward is to specify the field before writing a rule about how to fill it in.

This is v3's job and the ground is now clear for it: a rule that separates "wrong"
(REFUTED) from "incomplete but right" (WEAKENED) from "no defect found" (SURVIVED), with
each half stated positively, since "a negative rule without its positive half teaches a new
wrong answer" is already on this project's list of things that bit us.

## The fixture defect, and three discarded runs

Found while reading v2's discipline failures, which were all one shape — `cites ids that are
not in the breakdown: E3, S4, S5` and `E5, E8`, on exactly two cases, 3/3 repeats each. One
consistent direction of disagreement is this project's documented tell for a bad label, so
the fixtures got audited instead of the model.

`derive-fixtures.py` planted every insertion at a hardcoded `E9` / `S90` / `S91`, and the A1
deletion removed `E3` and left the hole. The result, across the suite:

| case | class | ids before the fix | tell |
|---|---|---|---|
| 03-missing-deliverable | A1 | `E[E1,E2,E4]` `S[S1,S2,S3,S6]` | gap where the epic was |
| 04-contradicts-item | A2 | `E[…,E9]` `S[…,S90]` | inserted ids stand out |
| 05-unrequested-epic | A3 | `E[…,E9]` `S[…,S90,S91]` | inserted ids stand out |
| 08-duplicate-stories | B3 | `E[E1,E2,E3,E4,E9]` | inserted id stands out |

**Four of the seven defect cases carried their own answer in the numbering.** A node could
score a detection by noticing an odd or missing id without ever comparing the breakdown
against the item — which is the one thing this suite exists to measure. The three
content-only defects (B1, B2, B4) and both clean cases were unaffected, because they move no
nodes.

**Fix:** a `renumber` pass in `derive-fixtures.py` that makes epic and story ids contiguous
in document order after the defect is planted. No assert was touched. Criterion ids are
per-story and already local. Verified: all nine cases contiguous, `--check` reproduces 36
files byte for byte, no prose in any fixture cites an id, and `case-08`'s `must_find` group
still resolves (`S5`, `S7` both exist post-renumber).

`asserts/self-test.js` fell to 20/22 on the new fixtures: its hand-built "correct finding"
for cases 04 and 05 cited `E9`, now `E4` and `E3`. That hardcoding was the same mistake one
level up, so the ids are now resolved from the fixture by epic title rather than written in.
Back to 22/22.

**Discarded, not re-scored:** the first `run_v1_haiku`, `run_v1_sonnet` and `run_v2_sonnet`.
`rescore.js` replays saved outputs, which is the right tool when an *assert* was wrong; here
the *inputs* changed, so those outputs answered a different question and no number from them
is reportable. All three were re-run, and the originals were deleted rather than kept as
`DISCARDED-*`, matching `delivery-triage` and `delivery-breakdown`, which keep none. What
they contained is recorded here instead:

| metric | v2 on leaky fixtures | v2 on corrected fixtures |
|---|---|---|
| schema | 27/27 | 27/27 |
| verdict | 13/27 | 13/27 |
| detection | 20/27 | 21/27 |
| discipline | 21/27 | 27/27 |

**The same comparison, stated once more because it is the point:**

| metric | v2 leaky | v2 fixed |
|---|---|---|
| schema | 27/27 | 27/27 |
| verdict | 13/27 | 13/27 |
| detection | 20/27 | 21/27 |
| discipline | **21/27** | **27/27** |

**detection did not move.** I expected the leak to have inflated it, and it had not: the
models were finding the defects by content, not by spotting the odd id. The whole measurable
harm was in discipline — the gap *baited* a fabrication the models would not otherwise
commit, because the natural way to report a hole at `E3` is to name `E3`. So the leak was
not making the node look better at detection; it was making it look worse at honesty. That
is the opposite of the usual direction and worth keeping in mind: a fixture artifact can
manufacture a defect as easily as it can hide one.

## v3a verdict rule (the one concern v2 left failing)

**Baseline:** v2 sonnet, 88/108 (81.5%) — schema 27/27, verdict 13/27, detection 21/27,
discipline 27/27.

**Why this is not the staged v3.** `prompt_v3.md` bundles three changes: an "the item is the
authority" constraint, a prescribed list of seven attacks to run, and the verdict rule. One
concern per iteration is not optional here, and load-bearing.md has to say which rule earns
its place — if v3 jumps to 95% with all three landing at once, that is unanswerable. v2
leaves exactly one axis failing, so v3a is **v2 plus the verdict rule and nothing else**.
`SURVIVED` is reworded to depend on the seven defect *conditions* rather than the seven
attack *procedures*, which is what coupled them in the staged version. The seven attacks
become v3b.

**Change:** one section. REFUTED is defined by the three A-class conditions, WEAKENED by the
four B-class conditions, SURVIVED by the absence of all seven. Each verdict carries its
reason in the same sentence ("REFUTED throws the breakdown away and runs it again"; "the plan
stands and these are fixed in place"), and SURVIVED gets a positive half — a plan you cannot
fault SURVIVED even if you would have written it differently — because a negative rule
without its positive half is on this project's list of things that bit us.

**Hypothesis:**

1. **verdict: 13/27 → 24+/27.** Both v2 failure groups are addressed by name. The 6 clean
   rows should go to SURVIVED now that SURVIVED has a definition and explicit permission to
   be chosen. The 8 over-escalated B rows should go to WEAKENED now that the four B
   conditions are listed under it and REFUTED is closed to "these are the only three".
2. **schema: holds at 27/27.** The output contract is untouched.
3. **discipline: holds at 24+/27.** No new honesty rule, but nothing removed either. The one
   risk is the verdict/landed consistency check: if the model now reports SURVIVED while
   still logging a landed attack, discipline falls. That coupling is the thing to watch.
4. **detection: flat, 19–23/27.** v3a names the defect *classes* without prescribing how to
   hunt for them. **This is the falsifiable part.** If detection jumps past ~24 then merely
   naming the seven classes is what finds defects, and v3b's seven prescribed attacks are
   largely redundant — which would be the more valuable result, since it means a shorter
   prompt certifies.

**Result:** **107/108 (99.1%)**, from 88/108 (81.5%).

| metric | v2 | v3a | hypothesis | verdict on the hypothesis |
|---|---|---|---|---|
| schema | 27/27 | 27/27 | holds | right |
| verdict | 13/27 | **27/27** | 24+/27 | right |
| detection | 21/27 | **26/27** | flat, 19–23 | **wrong — it jumped** |
| discipline | 27/27 | 27/27 | 24+/27 | right |

**verdict went to ceiling, and every v2 failure group closed.** All six clean rows now come
back SURVIVED — the first SURVIVED verdicts this suite has ever seen, after 0 in 81 prior
rows. All eight over-escalated B rows come back WEAKENED. The two halves that did it are
"these are the only three" closing REFUTED, and SURVIVED having both a definition and
explicit permission to be chosen.

**The detection jump is the result worth keeping, and it falsifies my hypothesis 4.** I
predicted detection would stay flat because v3a names the defect *classes* without
prescribing how to hunt for them. It went 21 → 26. Naming the seven classes is itself what
finds the defects; the hunting procedure was not the missing piece. Which means:

**Reasoning:** the verdict rule was aimed at `verdict` and hit `detection` as well, which is
the opposite of the usual outcome and says something about what this node actually needs.
Enumerating the seven defect classes gave the model a checklist of what a defect *is*; it did
not need to be told how to search. That is why the rule serves two criteria in
load-bearing.md, and why the prescribed-attacks version was dropped rather than run — the
procedure it adds is downstream of a checklist the model already has. The remaining failure
is one keyword-group miss, not a class of defect the prompt fails to describe.

**v3b and v4 are not needed, and will not be run.** The staged `prompt_v3.md` adds seven
prescribed attacks on top of this, and `prompt_v4.md` adds an anti-fabrication rule. Against
the evidence: detection is already 26/27 without the prescribed attacks, and fabrication is
0 rows at every version once the fixtures stopped baiting it, so v4's rule addresses a
failure this suite has never observed. Adding either would mean certifying rules with no
measured effect, and this project has already paid for the opposite instinct — "a shape
constraint makes models terser" and a rule moved from its reason cost 7 of 18 runs. The
shorter prompt is the one with the evidence behind it. `prompt_v3.md` and `prompt_v4.md`
stay in `prompts/` unrun, as the record of what was considered and why it was dropped.

## Certification: three consecutive runs

`RUN=<n> ./run.sh v3a sonnet`, REPEAT=3, three separate invocations:

| run | total | schema | verdict | detection | discipline |
|---|---|---|---|---|---|
| run1 | 107/108 (99.1%) | 27/27 | 27/27 | 26/27 | 27/27 |
| run2 | 108/108 (100.0%) | 27/27 | 27/27 | 27/27 | 27/27 |
| run3 | 108/108 (100.0%) | 27/27 | 27/27 | 27/27 | 27/27 |

Three consecutive runs at or above the 95% bar, on Sonnet. Each run is REPEAT=3 (27 rows,
108 asserts), where `delivery-triage` and `delivery-breakdown` certified at REPEAT=1 (40 and
24 asserts). More samples per run, same bar — a single assert failure is 0.9% here instead
of 2.5%, so the margin is not an artifact of a small denominator.

**Known residual:** the one failure in run1 is `case-07-vague-outcome` on detection. The
model found the defect and called the verdict correctly; its finding just did not use any of
the words the keyword group looks for (`observ`, `assert`, `vague`, `not testable`,
`untestable`, `nothing`). This is a vocabulary miss in the assert, not a missed defect, and
it is recorded rather than fixed by widening the group — widening it to admit the phrasing
would be weakening an assert to improve a score.

## Haiku on the certified prompt: the ruling-out was wrong

The model-tier policy wants the cheapest passing model, and "Haiku fenced on the naive
prompt" is weak evidence when Sonnet fenced on it too. So the certified prompt was run
against Haiku as proper escalation evidence. The result overturns the premise:

| run | total | schema | verdict | detection | discipline |
|---|---|---|---|---|---|
| v1 haiku (naive) | 35/108 (32.4%) | **0/27** | 15/27 | 20/27 | 0/27 |
| v3a haiku (certified) | **104/108 (96.3%)** | **27/27** | 25/27 | 25/27 | 27/27 |

**Haiku clears the 95% bar, and its schema score is perfect.** The fence that cost it triage
(26/30) and breakdown (0/18) is absent in all 27 rows. So the fence was never a Haiku
limitation; it was the absence of an output contract. The handoff's "Haiku is ruled out for
both chain nodes, with evidence" does not hold for this node, and the evidence it rests on
for the other two was gathered on prompts whose contracts were weaker than v3a's. **Worth
re-testing triage and breakdown on Haiku before accepting their Sonnet tiers** — that is a
standing per-item cost on every delivery-flow run.

**Sonnet is still the certified tier here, for a narrower reason than before.** Haiku's four
remaining failures are all `case-02-clean-sidebar`, 2 of 3 repeats, where it calls a clean
breakdown WEAKENED over `AC7` being circular ("uses the full desktop sidebar width" without
defining it). The failure is systematic, not noise, so more runs will not clear it, and it
lands on `verdict` — the one field `flow-status.py` routes on, where a spurious WEAKENED
injects false constraints into a breakdown that was correct. Haiku sits 1.3 points above the
bar; Sonnet sits 4–5 points above it, three times. For a routed node that margin is the
decision. The reason is margin and the failure's location, **not** capability.

### An assert was wrong, and is fixed

Haiku's one discipline failure was a false positive. `case-07` cited `breakdown.json`, and
the anti-fabrication check flagged it as a file absent from the material — but
`breakdown.json` is the artifact under challenge, and the prompt's own output contract tells
the node to write `"target": "breakdown.json"`. Naming it is the contract working. The check
now exempts the pipeline's own artifact names (`item.json`, `triage.json`, `breakdown.json`,
`challenge-breakdown.json`); a genuinely invented file still fails.

Every run was re-scored on the corrected basis with `rescore.js`, no model calls:

| run | before | after |
|---|---|---|
| v1 haiku | 35/108 | 35/108 |
| v1 sonnet | 33/108 | 33/108 |
| v2 sonnet | 88/108 | 88/108 |
| v3a sonnet run1 / run2 / run3 | 107 / 108 / 108 | **unchanged** |
| v3a haiku | 103/108 (95.4%) | **104/108 (96.3%)** |

Only the Haiku run moved: the false positive had fired exactly once, in the whole suite's
history. The Sonnet certification is unaffected. `asserts/self-test.js` still 22/22.

**Also discarded:** a `run_v1_all.json` left from the previous session — 54 rows, every one
`Could not load AWS credentials`, deleted. The old `run.sh` swallowed
promptfoo's output and would have scored it as a prompt failure. `run.sh` now exports
Bedrock credentials for promptfoo's subprocess, refuses to start without enough credential
life for the run, and aborts rather than scoring a run containing a credential or
authorization error. It caught a syntax error in its own credential helper on first use.
