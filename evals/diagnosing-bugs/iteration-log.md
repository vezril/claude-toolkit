# Iteration log: diagnosing-bugs

Written as the runs happened. Predictions are recorded before the run they predict.

## The suite

Four small Python projects, each with a planted bug and a passing test suite that misses it. The
agent gets Bash (sandboxed to its temp world), Edit/Write limited to the world, and nothing else. The
asserts grade what it leaves behind against the pristine fixture, plus what it did (tool calls):

- **fixed**: a hidden check passes, on inputs the agent never saw (40 hash seeds for the flaky case,
  205k lines in under 2 s for the slow one).
- **regression**: a new or changed test that, run alone on the pristine code, fails (for the flaky
  case, on at least 12 of 16 seeds, so the existing flaky test doesn't count); and the agent's suite
  passes.
- **clean**: no `print(`/`[DEBUG`/`breakpoint(` added to production code, no stray repro files.
- **loop-first**: Python ran before the first production edit. **measured** (slow case): a timing was
  taken before the fix. **redact** (weather): the API key isn't in the reply. **cause**: the reply
  names the root cause.

Traps: d-01 the user blames tax.py, the truncation is in invoice.py; d-02 flaky set ordering; d-03 a
secret in .env next to the bug; d-04 a quadratic dedupe.

Calibrated against 13 hand-built project snapshots (64/64), after one fix: the first regression check
ran the whole suite on the pristine copy, and the pre-existing flaky test "caught" the bug for any
agent test at all.

## Prediction for v1 (one-liner) and v2 (upstream verbatim), written before either ran

v1 ("find the cause of the bug and fix it"): Sonnet will fix all four and name the cause; I expect
**fixed** and **cause** near full. It will often skip the regression test (the d-02 and d-03 suites
already pass, so nothing pushes it to add one), so **regression** should fail on most cases. I expect
it to add a print or two while hunting and maybe leave a repro script (**clean** partial), and on d-01
I'd give even odds it edits tax.py because the user said to. **measured** is a coin toss; **redact**
should fail at least once, because the natural move on a 401 is to print the header.

v2 should flip **regression** (Phase 5 is explicit), **measured** (the perf branch says measure
first), **redact** (its first section), and **clean** (Phase 6's checklist). **loop-first** should
hold or improve. Haiku will lag on regression: the flaky case needs a test that fails reliably on the
buggy code, which is the hardest thing asked here.

## Harness fix before any numbers were kept

The first v1/v2 samples ran with Edit/Write allowed as `Edit(./**)`. In v2 Sonnet's d-02 run the agent
had `cd`'d into its scratchpad to build its loop, and its edit to `scheduler.py` was denied ("don't
ask mode"); it reported the fix it couldn't apply. A relative rule is fragile, so `run.sh` now
resolves the world's real path and writes the rules absolute (`Edit(//private/var/.../world/**)`).
A probe confirmed that an agent that `cd`s away can still edit inside the world and still can't write
outside it. All samples taken before the fix were deleted and re-taken; none of the numbers below
come from the old rule. (The scan also learned that the agent's own session scratchpad and one `../`
from a case project, the world root, are inside, not contamination; I checked each flagged call.)

## v1 and v2 measured

Each sample runs each case once per model; three samples for v1, the v2 samples so far:

| run | sonnet | haiku |
|---|---|---|
| v1 s1 / s2 / s3 | 15 / 14 / 15 of 20 → 44/60 (73%) | 19 / 17 / 18 of 20 → 54/60 (90%) |
| v2 s1 / s2 | 19 / 19 of 20 | 19 / 19 of 20 |

Against my prediction: **fixed** and **cause** were 4/4 in every v1 sample, including d-01, where
both models fixed the truncation in invoice.py although the user blamed tax.py. Sonnet v1 never
wrote a regression test (0/9) and edited before running anything on d-02 and d-03 in every sample;
Haiku v1 wrote tests on d-01 unprompted and mostly ran code first, which is why it beats Sonnet here.
**clean** was 4/4 everywhere (nobody left prints or repro files), so it's a guard. **redact** failed
once (Haiku v1 s3 quoted the key) and **measured** once (Sonnet v1 s2).

v2 fixed all of that except one thing, in every v2 sample on both models: no regression test on
d-02, the flaky case. The replies say why: "The existing test is already a minimal repro and a good
regression test, so I didn't add another." That test fails on about half the hash seeds. The skill's
Phase 1 demands a deterministic loop, but Phase 5 only says "turn the minimised repro into a failing
test", and the models count the flaky test as one.

## v3: a regression test goes red every run (one concern)

Hypothesis: one sentence in Phase 5, step 1, saying the test must fail on every run against the
buggy code, that a non-deterministic bug's test pins its source of nondeterminism (seed, order,
clock), and that the existing flaky test is the symptom, not the regression test, should flip
**regression** on d-02 for both models and move nothing else.

## v2 and v3 measured

| run | sonnet | haiku |
|---|---|---|
| v1 (3 samples) | 44/60 (73%) | 54/60 (90%) |
| v2 (3 samples) | 57/60 (95%) | 57/60 (95%) |
| v3 (3 samples) | 59/60 (98%) | 60/60 (100%) |

Every v2 miss, all six, was the d-02 regression test. v3 flipped it as predicted: Haiku wrote one in
3 of 3 samples, Sonnet in 2 of 3, and every one passed the check that matters (run alone on the
pristine code, it fails on at least 12 of 16 hash seeds). Nothing else moved. Every v3 scan was clean.

(Housekeeping after the runs: `sample.log` is now generated by a seeded script at run time instead of
being committed; the generator reproduces the file the runs used byte for byte.)

## Certification

v3 is certified on **Haiku**, 60/60 over three samples (Sonnet 59/60). The v1 baseline on Haiku was
54/60 (90%), Sonnet's was 44/60 (73%): Haiku already debugs carefully unprompted here, and the skill's
measurable lift is the regression test, running before editing (for Sonnet), the perf baseline and
redaction. What the suite can't see: hypothesis ranking shown to the user, minimisation, tagged debug
logs during the hunt (only what's left at the end), "stop and ask when you can't build a loop", and
the HITL script. Those parts of the skill are carried, not measured.
