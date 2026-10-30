# writing-for-adhd — EDD iteration log

Model `sonnet` via `evals/_provider/claude.sh`. Deterministic asserts only, no judge.
**N=6 per case** — raised from 3 after the first estimate proved unstable (see below).

| Arm | Majority (4 of 6) | Case-run pass rate | Per-run (of 5) |
|---|---|---|---|
| naive baseline | **3/5 (60%)** | 17/30 (56%) | 4, 2, 2, 3, 3, 3 |
| with `SKILL.md` | **5/5 (100%)** | 26/30 (86%) | 4, 4, 3, 5, 5, 5 |

| Case | Baseline | With skill |
|---|---|---|
| expert question — no remedial background | **FFFFFF** | **PPPPPP** |
| status — front-loaded, short, one next action | PFFPPP | PPPPPP |
| bad news — open with what works | PPPFPP | PPPPPP |
| many findings — triage, point at the logs | PFFPFP | FPFPPP |
| what's next — one action, not a menu | PPPPPF | PFFPPP |

## The one unambiguous result

**The expert case is 0/6 baseline and 6/6 with the skill.** Told plainly *"I know what AES and
authenticated encryption are, I've been doing crypto work for a decade"*, the naive arm explains
them anyway, every single time. That is the expertise-reversal effect — support that helps a
novice actively costs an expert, because reconciling an explanation against knowledge you
already hold is extra load — and it is the most reliable finding in this suite.

`status` and `bad news` also favour the skill clearly. `many findings` and `what's next` are
noisy in both arms.

## I previously reported 20% → 100%, and that was wrong

The first run of this suite, in its original private location, gave baseline 1/5 and skill 5/5
at N=3, and I reported **20% → 100%**. A fresh N=3 after moving it into the repo gave
**40% → 60%** — a swing wide enough that the original number was not reportable.

Things I checked before concluding anything:

- **Suite, provider, cases, config and asserts are byte-identical** between the two locations
  (verified by `diff`). Not a configuration difference.
- **My first hypothesis was wrong.** I guessed the private run had been inflated by the model
  being unable to act and giving artificially short "I can't do that" replies, which would
  trivially pass the form asserts. Measured: only **1 of 30** private-run replies mentioned tool
  unavailability, and median reply length was comparable (43 vs 52 words). Discarded.

What remains is plain **run-to-run variance on a 5-case suite whose asserts are word-count
sensitive**. A single case flip moves the headline 20 points, and three of the five cases flap.
So N=3 was never enough here, and the fix was more samples rather than a better story. The
table above is N=6, and the case-run pass rate is reported alongside the majority score because
on a suite this noisy the majority alone hides the spread.

**This is the honest correction: the real delta is 60% → 100%, not 20% → 100%.** The skill still
wins, by less, and the single strongest effect is the expertise-reversal case.

## Limits

- **Five cases.** Nothing tests multi-turn drift, which is the real failure mode — a reply gets
  short and then creeps back up over a long session.
- The form check is deliberately generous (160-word default ceiling, ≤4 list items). It catches
  walls of text and memory-test lists; it does not enforce the skill's own 2–4 sentence target.
- **Measuring form is not measuring comprehension.** Every assert is a property of the text.
  Whether the reader actually acted on it is what matters and this suite cannot see it.
- Two cases remain unstable in both arms even at N=6.

## Reproducing

```bash
for n in 1 2 3 4 5 6; do
  npx promptfoo@latest eval -c evals/writing-for-adhd/promptfooconfig.baseline.yaml --no-cache \
    -o evals/writing-for-adhd/results/baseline_$n.json
  npx promptfoo@latest eval -c evals/writing-for-adhd/promptfooconfig.yaml --no-cache \
    -o evals/writing-for-adhd/results/skill_$n.json
done
```
