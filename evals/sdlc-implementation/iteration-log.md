# Iteration log: sdlc-implementation (test-writer)

Every number here comes from a promptfoo run that executed. Results files are in `results/`.

## Iteration 1 — v1, the naive baseline

**Baseline:** none. This is the first run.

**Hypothesis:** v1 is the one-liner someone would actually type — *"Write failing tests for the
story in story.md. Only touch test files."* I expected `territory` to hold (the instruction is
right there in the one line) and `scope` to collapse, because nothing in v1 mentions priorities
at all. The suite had a fifth case at the time, which I expected to fail outright; its premise
turned out to be wrong and it is gone — `load-bearing.md` records why, under instruction 4.
Every number in this log is over the four cases that survived, v1 included.

**Change:** `prompts/prompt_v1.md`, run on both models over every fixture.

**Result** — `results/run_v1_all.json`, **25/32 (78.1%)** over four cases and two models:

| criterion | score |
|---|---|
| territory | 8/8 |
| red | 8/8 |
| green | 7/8 |
| scope | **2/8** |

haiku 12/16 (75%), sonnet 13/16 (81%).

**Reasoning.** Both predictions held, and the shape is more interesting than the total.

`scope` is 2/8 and it is the clearest signal in the run. v1 never mentions priorities, so the
models tested whatever looked worth testing: case-01's P3 display criterion, case-04's P3
traversal check. Both wrote tests for criteria the story explicitly ranks out of scope. That is
the behaviour the P0/P1 rule exists for, and the baseline shows it is not a default — it has to
be instructed.

`territory` and `red` are both 8/8, better than I would have guessed from a one-line prompt.
"Only touch test files" in plain English was enough, on every case, for both models. Whatever
v2 adds, it is not adding that.

`green` at 7/8 is the one I would have been wrong about. I expected `red` and `green` to move
together — a test that fails now and passes with the fix. They did not: haiku passed `red` and
failed `green`, which means it wrote a test that fails now and *still* fails against the
correct implementation. That test asserts the wrong thing. Nothing but applying the reference
distinguishes it from a good red hand-off, which is the whole argument for the `green`
criterion existing.

**Next hypothesis:** v2 is the real `agents/test-writer.md`, which writes out the P0/P1 scope
rule. I expect `scope` to carry almost the whole gain and `territory`/`red` to stay flat.

## Iteration 2 — v2, the real agent prompt

**Baseline:** v1 at 25/32 (78.1%).

**Hypothesis:** stated above before the run. `scope` moves most; `territory` and `red` do not
move because v1 already had them.

**Change:** `prompts/prompt_v2.md`, a verbatim copy of `agents/test-writer.md`.

**Result** — three samples, all eight rows fully scored, no provider errors:

| criterion | v1 | v2 | delta |
|---|---|---|---|
| territory | 8/8 | 8/8 | 0 |
| red | 8/8 | 8/8 | 0 |
| green | 7/8 | 8/8 | +1 |
| **scope** | **2/8** | **7/8** | **+5** |
| total | 25/32 (78.1%) | **31/32 (96.9%)** | +6 |

| sample | sonnet | haiku |
|---|---|---|
| `run_v2_all.json` | 16/16 (100%) | 15/16 (93.8%) |
| `run_v2_all.s2.json` | 16/16 (100%) | 15/16 (93.8%) |
| `run_v2_all.s3.json` | **15/16 (93.8%)** | 15/16 (93.8%) |

**The prediction held almost exactly.** `scope` carried five of the six points and
`territory`/`red` did not move at all. v1 never mentions priorities, so the models tested
whatever looked worth testing — case-01's P3 display criterion, case-04's P3 traversal check.
Both are criteria the story explicitly ranks out of scope, and the rule has to be written down
to be followed.

**But this does not certify, and the third sample is why.** Sonnet ran 100%, 100%, then 93.8%.
The bar is 95% on *each* of three consecutive runs, not on their mean, and this is exactly the
case that rule exists for — `readiness` v1 passed two runs and then scored 83.3%. Two good
samples and a confident write-up would have been wrong here.

**Every failure in all three samples is the same defect**, which makes it a finding rather than
noise:

```
run_v2_all.json      haiku   case-05  scope  the WEAKENED challenge finding is unaddressed
run_v2_all.s2.json   haiku   case-05  scope  the WEAKENED challenge finding is unaddressed
run_v2_all.s3.json   sonnet  case-05  scope  the WEAKENED challenge finding is unaddressed
run_v2_all.s3.json   haiku   case-05  scope  the WEAKENED challenge finding is unaddressed
```

haiku misses it 3 of 3; sonnet misses it 1 of 3. So **instruction 17** — read
`challenge-breakdown.json`, and treat a WEAKENED verdict's findings as constraints — is not
reliably followed by either model. It is also the instruction most easily missed by
construction: it sits as one bullet in a section about inputs, and the finding it points at
lives in a second file the agent has to think to open.

**Next hypothesis** (not yet run): v3 moves the challenge-findings rule out of the inputs
bullet list and anchors it the way the method's own high-leverage fix suggests — a named step
in the loop rather than a note about where to look. I expect case-05's `scope` to go to 3/3 on
sonnet and to improve on haiku. I do **not** expect anything else to move, since every other
criterion is already saturated.

That change edits `agents/test-writer.md`, a live agent file that `CLAUDE.md` pairs with two
other places, so it is a deliberate change rather than a tweak and is not made here.

## The harness bugs, and why the first three runs were discarded

Four runs happened before a trustworthy number. The first three are not in `results/` because
reporting them would have been reporting noise, and each produced plausible output:

1. **Cases 04 and 05 were never wired into `promptfooconfig.yaml`.** Their fixtures and
   expectations existed, so the suite looked complete; the run silently measured 3 of 5 cases
   and reported 6 rows as if that were the suite.

2. **Both providers shared one work tree.** promptfoo runs them in parallel, and both did
   `rm -rf` and `cp` into `.work/<case>` — producing `.work/case-01/case-01`, one provider's
   copy landing inside the other's. Every criterion then read files nobody had touched, and
   `territory` "failed" on `story.md` and `Makefile`. Fixed by keying the work tree on case
   **and** model.

3. **`territory` could not fail at all.** `grade.py` diffed the work tree against
   `fixture/<case>` — the very directory the agent was editing, so it compared a tree to
   itself and reported "0 files touched" regardless. `calibrate.py` could not catch this: it
   copies to a temp tree, so the calibration harness and the real run disagreed about where
   work happens. The agent now works on a copy, the way calibration always did.

4. **There was never a two-model comparison.** promptfoo's exec provider does not pass
   `config.env`, so `CLI_MODEL` never arrived and the provider's `${CLI_MODEL:-sonnet}`
   default made *both* providers run as sonnet. The "haiku" rows were sonnet's output graded
   against a directory that was never created, reported as 0/20 — which I would have been
   wrong to read as a capability gap. There is no default now: the model is set by an explicit
   per-model wrapper and the provider errors if it is unset.

Bug 4 is the one worth keeping. The case id had hit the same wall earlier — `config.env` not
reaching the script — and I fixed it by routing the case through the prompt without asking
whether anything else depended on that env. The same bug, twice, because I fixed the symptom
rather than the mechanism. And the silent `:-sonnet` default is what let it masquerade as a
result instead of failing.

## Provider

Exec over the Claude Code CLI (`provider/claude-{haiku,sonnet}.sh`), which authenticates from
the keychain. The `anthropic:claude-agent-sdk` provider the other suites use reports
`Not logged in` in this environment; `skills/prompt-edd` names the CLI as the keyless route and
notes any teammate can re-run it. This suite has no prior runs, so choosing the provider now
breaks no comparability with anything.

**Only `$1` is read.** promptfoo passes three arguments and the third is a context JSON
containing the test's ground truth. Reading it would feed the expected answer to the model and
invalidate every score while looking like it worked.
