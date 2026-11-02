# Iteration log — readiness story-planner node

Built for task 5.1. Three changes, four criteria: `schema` (runs the real `lint-story.py`),
`coverage`, `grounding`, `decomposition` (rubric, on the two cases built to invite the failure
it looks for).

**Read this before trusting the numbers.** Two of the three iterations below are *suite*
iterations, not prompt iterations — the measurement was wrong and I fixed the measurement. Only
iteration 3 changed the prompt. I am saying so explicitly because
`check-certification.py` counts any section carrying the five labels, and two harness fixes
could silently stand in for prompt development. They are not the same thing, and a reviewer
reading this should know which they are getting.

## Iteration 1 — the rubric had no grader, so a third of the suite never ran

**Baseline:** first run of v1 on haiku. promptfoo reported `2 passed (33.33%), 4 errors
(66.67%)`, and `score.js` printed **PASS at 100%**.

**Hypothesis:** the two cases carrying `llm-rubric` asserts had no grader provider, so
promptfoo fell back to its OpenAI default and errored on a missing `OPENAI_API_KEY`. The
scorer then averaged only the cases that produced output — the two with no rubric — and found
them perfect.

**Change:** set `defaultTest.options.provider` to the Claude grader in the canonical config
(the derived `.local` configs swap it to `_provider/claude-grader.sh` automatically), and made
`score.js` void a run if any case produced no measurement.

**Result:** 6 of 6 cases graded, 0 errors, 11 asserts per provider.

**Reasoning:** a scorer that ignores errors reports a bar nobody met, and this one reported
100% on a run where two thirds of the cases never executed. That is the same inert-check
failure this project has found in the edge hook, in a schema declaration and in a dispatch
boundary — here in the thing doing the measuring, which is the worst place for it: every
number downstream would have inherited it. The missing grader was a ten-character
configuration bug; the scorer calling it a pass was the defect.

## Iteration 2 — a failure is not an error, and the distinction hid a real one

**Baseline:** v1, haiku, run 3. promptfoo reported `4 passed, 2 failed, 0 errors`. `score.js`
reported *2 errored cases* and no criterion failure.

**Hypothesis:** promptfoo populates a row's `error` field even when the row merely failed an
assert, so keying the scorer on `error` alone classified genuine failures as infrastructure
problems.

**Change:** the discriminator is now whether the row was graded at all — a row with component
results was measured, whatever `error` says.

**Result:** the same results file re-scored to **81.8%, with `schema` at 1/3**, naming the two
cases and the linter's complaint.

**Reasoning:** this was worse than iteration 1's bug, not milder. Over-reporting errors sends
someone to debug the harness while the prompt is the thing at fault, and the run that
triggered it was the third of three — the one that decides certification. The first version of
the scorer hid a passing bar that was not met; the second hid *which* of prompt or harness was
failing. Both are the same error at bottom: a measurement that cannot distinguish "nothing
happened" from "something was wrong".

## Iteration 3 — `<epic>` invited a name, and the linter wants digits

**Baseline:** v1, haiku, three runs: 100%, 100%, **81.8%**. `schema` 1/3 on the third, failing
`[title] first heading must be '# Story {epic}.{n}: {title}'` on case-01 and case-02.

**Hypothesis:** the prompt's format block showed `# Story <epic>.<n>: <title>` and the file
name as `stories/<epic>-<n>-<slug>.md`. "Epic" reads as the epic's *identity*, so the model
wrote `# Story 2fa.1:` using the change name — a reasonable reading of an ambiguous
placeholder, and one `lint-story.py` rejects because its H1 pattern requires digits. The
failure was intermittent because nothing in v1 made the type explicit, so it depended on how
the model resolved the ambiguity that run.

**Change:** v2 renames the placeholders to `<E>` and `<N>`, states that both are digits, shows
a concrete `# Story 1.1:` example, names `# Story 2fa.1:` and `# Story auth.1:` as rejected,
and says that a single-epic change makes every story `1.<N>`.

**Result:** v2 on haiku, three consecutive runs, **11/11 = 100%** each, all four criteria at
100%. `results/run_v2_haiku_1.json`, `_2`, `_3`.

**Reasoning:** the fix is to the prompt rather than to the linter, because the linter's rule is
the normative story schema and the prompt was the thing being vague. Worth noting what the
defect was *not*: haiku understood the decomposition task throughout — `coverage`, `grounding`
and `decomposition` were 100% in all three v1 runs, including the one that failed. It got the
work right and the format wrong, which is the opposite of the reviewer suite's haiku failure,
where the format rule it broke (endorsement vocabulary) was really a framing rule.

## Model

Haiku certifies. Design D7 is haiku-first and haiku passed three consecutive runs on v2, so
there is no escalation to justify and no sonnet evidence is needed for the decision. Sonnet was
measured too (`run_v1_sonnet.json`) and also scored 100%, which tells you the task is not at
the edge of either model's ability.

**One caveat about the local arms.** The derived `.local` configs point both exec providers at
the same `_provider/claude.sh`, which takes its model from `EVAL_MODEL`. So within a single
local results file, the `haiku` and `sonnet` labels are the *same* model — whichever
`EVAL_MODEL` named. The per-file evidence is still correct because each file was produced with
one model, but the labels inside it are not two arms. `make-local-configs.py` was written for
single-provider suites and this is the first two-provider suite to use it.

## Reproducing

```bash
# canonical (CI, agent-sdk provider)
cd evals/readiness-stories && ./run.sh v2 haiku

# local (exec providers, for a Bedrock-backed install with no ANTHROPIC_API_KEY)
EVAL_MODEL=haiku GRADER_MODEL=sonnet \
  npx promptfoo@latest eval -c promptfooconfig.local.yaml --no-cache \
  -o results/run_v2_haiku_1.json
node score.js results/run_v2_haiku_1.json
```

promptfoo needs Node >= 22.22; this machine's global mise pin is 18.20.2, so `run.sh` puts
the 22 install on PATH itself rather than asking for a machine-wide repin.
