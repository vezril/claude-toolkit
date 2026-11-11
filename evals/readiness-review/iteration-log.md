# Iteration log — readiness-review node

Three cases (a set that stands, one with a dropped requirement, one where the requirement is
traced and delivered by nothing), three criteria: `contract` (validated by the project's own
`validate-artifact.py`), `accuracy`, `safety`.

## Why this suite exists rather than reusing `evals/cross-examine/`

Task 5.3 asked whether to reuse that suite for this node. My first answer was yes, on the
strength of its per-criterion breakdown — 4 of 6 asserts are reasoning, and its `safety`
criterion is a false-positive test, so design D5's claim that it "tests format heavily and
reasoning lightly" does not survive contact with the numbers.

That answer was still wrong, because I judged the criteria without checking the **inputs and
outputs**. `cross-examine` feeds an incident ticket and a distilled timeline and expects a
markdown verdict. This node is handed a *story set* and must emit `readiness-verdict.json`.
Same capability, different domain, different output contract — and certifying a node against
inputs it never sees in production is the same error as certifying a prompt the suite never
saw, one level up. So: its criteria *design* is reused here (contract / accuracy / safety, with
a sound case as the false-positive test); its cases and its output format are not.

## Iteration 1 — my `safety` criterion punished a correct review, twice over

**Baseline:** v1, 57–71%. `safety` 0/2. The reported reason: "claims a requirement is
untraced, which is false for this set".

**Hypothesis:** two separate bugs in my own assert. It scanned the whole verdict document, so
an *honest attack description* — "attack: is every requirement traced? method: checked each FR
against the set. result: failed" — matched the word list. And it treated any non-SURVIVED
verdict on the sound set as a false positive.

**Change:** scan `findings` only, never the attack log; permit WEAKENED.

**Result:** `safety` passed on one arm, and the run revealed something better: on the set I
hand-wrote to be *sound*, both models returned WEAKENED with real gaps — no column defines the
"2FA active" state the criteria depend on, no criterion covers signing in *without* 2FA, and
single-use is tested sequentially but not concurrently.

**Reasoning:** the reviewer was right and my fixture was wrong. A "sound" artifact with no
legitimate criticism available is close to impossible to construct by hand, and a criterion
demanding SURVIVED would have taught the reviewer to stop looking — which is exactly the
failure a false-positive test is supposed to prevent. Penalising the attack log is worse still:
it punishes the reviewer for recording what it checked, which is the one thing that log is for.

## Iteration 2 — the schema rejects a good review over a renamed key

**Baseline:** v1/v2. `contract` 2/3. `findings[0].story: shorter than 1 characters`, then
`findings[0]: unexpected field 'file'`, `unexpected field 'summary'`.

**Hypothesis:** the prompt showed the finding shape but never said the key set was closed, nor
that `story` must be omitted rather than empty when a finding belongs to no single file.

**Change:** v2 said to omit `story` entirely; v3 named the exact keys for both findings and
attacks, and named the wrong ones models reach for (`summary`, `file`, `detail`, `severity`).

**Result:** `contract` 3/3 on the haiku arm from v3 on.

**Reasoning:** worth stating what this is not. The reviews being discarded were good — correct
verdicts with grounded findings — and they were thrown away by a field name. That is the
schema working as designed, and it is also the cheapest possible certification failure, so the
prompt carries the burden rather than the schema being loosened.

## Iteration 3 — a regex cannot decide whether a finding is true

**Baseline:** v2. `safety` still failing on the set that stands, rejecting the finding "no
story covers recovery once the ten codes are exhausted".

**Hypothesis:** that claim is *true*, and it is about the change's goal rather than about a
requirement's traceability. My word list could not tell the difference, and this was its third
consecutive false rejection — after "no task adds the `totp_secret` column" and "nothing
defines the active state the criteria depend on", both also true.

**Change:** removed the truth-checking heuristic entirely. `safety` now checks only form: not
REFUTED, no requirement id the change does not contain, and at least one attack reported as
failed. Whether a finding is *true* is judged by the rubric on the vacuous case.

**Result:** `safety` 2/2 from v3 on.

**Reasoning:** the division of labour is the lesson. A script can check that this is JSON, that
there are three attacks, that an id exists in the change. It cannot check whether a sentence is
true, and every attempt to make it try rejected the reviewer for being more thorough than the
fixture author. Three strikes is enough: the check was deleted rather than refined again.

## Iteration 4 — an omitted key is not an empty list

**Baseline:** v3. One arm at 7/7, the other failing `(root): missing required field
'findings'` on the vacuous case.

**Hypothesis:** v3 said findings "must be empty when the verdict is SURVIVED", which reads as
permission to leave the key out when there is nothing to put in it. Run-to-run variance, not a
model difference — both local arms run the same model (see the caveat below), so this was haiku
disagreeing with itself.

**Change:** v4 states that `findings` is always present: `[]` for SURVIVED, non-empty
otherwise, and that omitting the key is not the same as an empty list.

**Result:** v4, three consecutive runs, **7/7 = 100%** on every criterion.
`results/run_v4_haiku_1.json`, `_2`, `_3`.

**Reasoning:** the variance is the point. v3 passed one arm and failed the other on identical
input, so a single run would have certified a prompt that fails about half the time on this
case. The three-consecutive rule caught it, as it caught the reviewer's haiku framing drift in
`evals/cross-examine/`. Two for two on that rule earning its place.

## Model

Haiku certifies: design D7 is haiku-first and haiku cleared three consecutive runs on v4, so
there is no escalation to justify.

**Caveat on the local arms.** The derived `.local` configs point both exec providers at
`_provider/claude.sh`, which takes its model from `EVAL_MODEL`. So within one local results
file the `haiku` and `sonnet` labels are the *same* model. That is why iterations 3 and 4
describe two arms disagreeing as variance rather than as a model comparison — and it is useful
by accident, because it gives each run two independent samples of the same model.
`make-local-configs.py` was written for single-provider suites.

## Reproducing

```bash
# local (exec providers; this machine is Bedrock-backed with no ANTHROPIC_API_KEY)
cd evals/readiness-review
EVAL_MODEL=haiku GRADER_MODEL=sonnet \
  npx promptfoo@latest eval -c promptfooconfig.local.yaml --no-cache \
  -o results/run_v4_haiku_1.json
node score.js results/run_v4_haiku_1.json
```

promptfoo needs Node >= 22.22 and this machine's global mise pin is 18.20.2, so `run.sh` puts
the 22 install on PATH itself.
