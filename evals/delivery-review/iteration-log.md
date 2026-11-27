# Iteration log: delivery-review

Every number here comes from a promptfoo run that executed. The results JSON for each is in
`results/`. The suite is 14 cases × 2 models × 4 criteria = 112 asserts.

Six of the fourteen cases exist because of eight review comments filed on real pull requests.
Four of those comments' *Required* lines begin with the word "Confirm" — a reviewer carrying a
burden the change should have discharged — which is what the fourth criterion measures.

## Score progression

| criterion | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| contract | 0/28 | 0/28 | **28/28** | 28/28 |
| accuracy | 0/28 | 12/28 | 19/28 | 21/28 |
| grounding | 1/28 | 26/28 | 26/28 | 24/28 |
| assumptions | 21/28 | 22/28 | 23/28 | **25/28** |
| **total** | **22/112 (19.6%)** | **60/112 (53.6%)** | **96/112 (85.7%)** | **98/112 (87.5%)** |

| version | haiku | sonnet |
|---|---|---|
| v1 | 11/56 | 11/56 |
| v2 | 30/56 | 30/56 |
| v3 | 48/56 | 48/56 |
| v4 | 51/56 | 47/56 |

**Nothing is certified on this.** 87.5% is under the 95% bar, and `steps.yaml` keeps
`certified: false` with no `results` or `prompt_sha256` field.

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
