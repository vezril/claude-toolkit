# Iteration log: delivery-review

Every number here comes from a promptfoo run that executed. The results JSON for each is in
`results/`. The suite is 14 cases × 2 models × 4 criteria = 112 asserts.

**The live prompt is v6 as of 2026-11-27.** v2 is the version it replaced, kept here as the
historical record: v2 is what `skills/delivery-flow/references/review.md` contained when this
suite was first run, and `prompts/prompt_v2.md` is a verbatim copy of it.

Six of the fourteen cases exist because of eight review comments filed on real pull requests.
Four of those comments' *Required* lines begin with the word "Confirm" — a reviewer carrying a
burden the change should have discharged — which is what the fourth criterion measures.

## Score progression

Re-run after each suite correction, so the row for a version is the version on the suite as it
stands. The v1/v2 figures below come from the run before the `case-01` fixture was fixed; that
fixture made clean-case rows unwinnable, so if anything those two are flattered.

| criterion | v1 | v2 (the old live prompt) | v3 | v4 | v5 | v6 |
|---|---|---|---|---|---|---|
| contract | 0/28 | 0/28 | **28/28** | 28/28 | 28/28 | 28/28 |
| accuracy | 0/28 | 13/28 | 22/28 | 19/28 | 19–22/28 | 18–24/28 |
| grounding | 1/28 | 24/28 | 27/28 | 27/28 | 25–28/28 | 26/28 |
| assumptions | 21/28 | 22/28 | 22/28 | **25/28** | 24–25/28 | 24–26/28 |
| **total** | **22 (19.6%)** | **59 (52.7%)** | **99 (88.4%)** | **99 (88.4%)** | **97–102** | **97–104** |

**v6, three consecutive samples: 104, 102, 97 of 112 — 92.9%, 91.1%, 86.6%.** Mean 90.2%,
spread 7 marks.

**Nothing is certified.** The bar is 95% on each of three consecutive runs and no sample
reaches it, so `steps.yaml` keeps `certified: false` with no `results` or `prompt_sha256`.

## Iteration 1 — v1, the naive baseline

**Baseline:** none.

**Hypothesis:** v1 is the one-liner someone would type — *"Review this diff against the story
and say whether it should merge."* I expected `contract` to collapse, because nothing in v1
describes an output format at all, and `assumptions` to score moderately on its precision half
for the same reason — a naive reviewer does not invent preconditions, it simply never raises
any.

**Result:** 22/112. `contract` 0/28, `accuracy` 0/28, `grounding` 1/28, `assumptions` 21/28.

**Reasoning.** Both predictions held. Every reply came back fenced, with `verdict` values like
`request_changes` and `approve`, and findings with no evidence field — so `contract` and
`accuracy` could not score at all, since accuracy checks the verdict vocabulary first.

`assumptions` at 21/28 is the number worth keeping. Its precision half passes almost
everywhere, and it fails exactly the three cases that require *raising* a precondition. A naive
reviewer is not reckless about assumptions. It is silent about them, which is a different
problem and takes a different fix.

## Iteration 2 — v2, the live prompt

**Baseline:** v1 at 22/112.

**Hypothesis:** v2 is `skills/delivery-flow/references/review.md` verbatim, which has the
output rules, the verdict vocabulary, the evidence rule and the five review questions. I
expected most of `contract`, `accuracy` and `grounding` to come with it.

**Result:** 60/112. `grounding` 1→26, `accuracy` 0→12, **`contract` 0→0**, `assumptions` 21→22.

**Reasoning.** The prediction was wrong about `contract`, and the way it was wrong is the most
useful thing in this log.

`contract` stayed at **0 of 28 — every row, both models.** The prompt names the six required
top-level fields and the `evidence` key, and never names the nested ones. So the model invents
them: `reviewers[].specialist` instead of `agent`, and findings with neither `finding` nor
`reviewer`. The artifact is validated against `schemas/review.schema.json` before anything
downstream runs, so **every review this prompt produces would fail its edge.** The step is
uncertified and has never run on a live item, which is the only reason nobody had hit it.

`assumptions` moved by one mark, from 21 to 22. Everything the live prompt adds — and it adds
a great deal — does nothing for the class of defect that produced half the review comments.
That is the cleanest evidence in the suite that this was a missing instruction and not a
tendency to be trained out.

## Iteration 3 — v3, the full output contract

**Baseline:** v2 at 60/112.

**Hypothesis:** write the shape out, every key named, with an anchored rule for
`diff_sha256`. I expected `contract` to go from 0 to near-full and `accuracy` to gain where a
parse failure had been masking a correct judgement. I expected `assumptions` to stay flat,
since v3 says nothing about assumptions.

**Result:** 96/112. `contract` 0→28, `accuracy` 12→19, `grounding` 26→26, `assumptions` 22→23.

**Reasoning.** All three predictions held, and `contract` went to 28/28 rather than merely
improving.

But the first v3 run scored 76/112, not 96, and the gap was **my fixtures, not the prompt.**
Fifteen of the seventeen remaining failures were `diff_sha256 is not a 64-char hex digest`,
and the suite had never supplied one. Two more rows were haiku *refusing*, correctly and in
plain terms: *"the material gives no `diff_sha256`, and the rules say not to invent one."* A
reviewer declining to fabricate a digest is exactly the behaviour the prompt asks for, and the
suite was marking it wrong. Every case now carries the real sha256 of its own diff, which is
what production computes.

Two false positives in my own fourth criterion went with it. It counted `verify.json` as an
invented dependency — the handed-over artifacts are part of the material, which `grounding.js`
had already learned and I had repeated the omission of — and it rejected `bisect_right` where
the diff calls `bisect`, which is a reviewer naming the real function more precisely rather
than making one up.

So v1, v2 and v3 were all re-run on the corrected suite, and the table above is the re-run.
The numbers in this log are not the numbers I first saw.

## Iteration 4 — v4, one instruction about what the change takes on faith

**Baseline:** v3 at 96/112.

**Hypothesis:** add a single review question — *what does this change rely on from something
it does not own, and does the material establish it?* — phrased to require the shape the
original comments took: confirm it, or do this instead. I expected `assumptions` to move and
nothing else to.

**Result:** 98/112. `assumptions` 23→25, `accuracy` 19→21, `grounding` **26→24**,
`contract` 28→28.

**Reasoning.** It moved the target, and it cost something I had not predicted.

`grounding` lost two marks, both on the large-diff case, where the reviewer now raises
assumptions about `base.Adapter` and `module_NN.py` — a shorthand for forty generated files.
Asking for assumptions produces more speculative findings, and some of them reach past the
material. That is a genuine trade-off rather than noise, and a v5 that tightens the
instruction to *assumptions about code in the diff* is the obvious next hypothesis.

The gain is also smaller than the instruction deserves, which points at where the residual is.

## What is still failing, and what it is

Fourteen asserts, in three groups:

1. **The clean case is now refuted by both models** (`accuracy`, case-01). A reviewer that
   blocks a correct one-line change is worse in practice than one that misses a defect, and
   this is the group I would fix first. The prompt already says an empty `findings` list with
   `SURVIVED` is a real answer; it is not winning against the pull to find something.
2. **Class A is improved but not solved** (cases 09 and 11). sonnet still does not raise
   `on_created` on the lost-update case, and neither model reaches for "the dataset the
   previous form already populated". The instruction gets the reviewer to talk about
   assumptions; it does not yet get it to the right one.
3. **The inert test is missed by both models** (case-13). `verify.json` hands them a surviving
   `if True:` mutant on the line the new test is named for, and they do not articulate that
   the test cannot reach the branch. They have the evidence and do not use it — which is its
   own finding about the prompt, since nothing in it says what a surviving mutant means.

## Iteration 5 — v5, scope the assumptions instruction to the diff

**Baseline:** v4 at 99/112.

**Hypothesis:** v4 bought `assumptions` at the cost of two `grounding` marks, because asking
for assumptions produced findings about modules the reviewer had never seen. Add one clause —
an assumption has to be anchored to a symbol, call or path in the material — and `grounding`
should recover without giving the assumptions gain back.

**Result:** 102/112 on the first sample. `grounding` 27→28, `accuracy` 19→22,
`assumptions` 25→24.

**Reasoning.** The prediction held and the trade reversed: one assumption mark for three
elsewhere.

Then the `case-01` fixture correction landed and v5 was re-run: **97/112.** Same prompt, same
suite, five marks apart. That is the most useful number in this log and it is not about any
prompt — at `REPEAT=1` this suite has a spread of roughly ±2 percentage points, so a +3 delta
is inside the noise. Every single-sample comparison above iteration 3 should be read with that
in mind, and the three-sample figures for v6 exist because of it.

Two more of my own assert bugs surfaced in the v5 failures, both the same mistake: it rejected
`base.Adapter` and `Row.amount` as invented when `base`, `Adapter`, `Row` and `amount` all
appear in those diffs and only the dotted spelling does not. A dotted or underscored name is
now grounded when every part of it is present. Split on `.` and `_` only, **never on case** —
splitting CamelCase would ground `RetryScheduler` against any diff containing the word
"retry", which is exactly the invention this half of the criterion exists to catch. The mutant
proving that still dies.

## Iteration 6 — v6, what a surviving mutant means

**Baseline:** v5, 97–102/112.

**Hypothesis:** on `case-13` both models were handed a surviving `if True:` mutant in
`verify.json` and neither said the test could not reach the branch. Nothing in the prompt says
what `mutation.survived` is. Say it — a green suite and a surviving mutant cannot both be good
news — and name the required output: which test, which line, why it cannot get there. I
expected `case-13` to flip and little else to move.

**Result:** 104/112 (92.9%), then 102 and 97 on two further samples.

**Reasoning.** `case-13` flipped on both models in the first two samples and failed once in the
third, so the instruction works and is not yet reliable. The rest of the movement is within the
variance established in iteration 5, so I am not claiming the other criteria moved.

This is the one iteration whose instruction depends on another part of the pipeline existing:
the `mutation` block it tells the reviewer to read is produced by `scripts/delivery-flow/
mutation-gate.py`. A reviewer told to read a field nothing writes would be an instruction about
nothing, which is why the gate came first.

## What is still failing, after three samples

Counting failures per `(case, criterion)` across all three v6 samples — 6 means both models
failed it in all three runs:

| failures | case | criterion |
|---|---|---|
| **6 of 6** | case-09-unverified-precondition | accuracy |
| **5 of 6** | case-10-assumed-error-semantics | accuracy |
| **5 of 6** | case-11-lost-update | assumptions |
| 3 of 6 | case-03-out-of-scope-tests | accuracy |
| ≤2 of 6 | everything else | — |

The first three are the residual and everything below them is noise. All three are **Class A**:
the change leans on something it does not own, and the reviewer does not name the specific
thing. On `case-09` it never reaches "the dataset the previous form already populated"; on
`case-10` it does not offer deletion protection as an alternative meaning for the exception; on
`case-11` it does not raise `on_created` firing after another run has recorded its own dataset.

The instruction added in v4 and narrowed in v5 gets the reviewer **talking** about assumptions.
It does not get it to the right assumption. That is a harder problem than a missing instruction
and the honest read is that it needs either a worked example per failure mode in the prompt, or
acceptance that a reviewer catches two of these three classes and a human catches the third.

Class B (`case-11`'s lost update, `case-12`'s blocking sleep) and Class C (`case-13`'s inert
test, `case-14`'s contradicted documentation) are reliably caught on `accuracy`. Class A is the
one the original comments had to be written four times about, and it is the one a prompt moves
least.

## Provider

Exec over the Claude Code CLI (`provider/claude-{haiku,sonnet}.sh`), authenticating from the
keychain. `anthropic:claude-agent-sdk` is what the config named first and it reports
`Not logged in` here, which is why this step had a mutation-tested suite and no scores at all.
There were no prior runs, so choosing the provider now breaks no comparability.

**Only `$1` is read.** promptfoo passes three arguments and the third is a context JSON holding
the test's ground truth.

`run.sh` also refuses to run on Node below 22. promptfoo requires it, the repo default is 18,
and the runner used to swallow the version error — the suite looked like it ran and wrote
nothing.
