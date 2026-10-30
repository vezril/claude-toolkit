# Iteration log: the Pocock folds (software-design, tdd, domain-driven-design, software-architecture)

Written as the runs happened. Predictions are recorded before the run they predict.

The original suites behind these skills' README rows (`promptfoo/skill-evals/`) aren't in this repo
or on this machine, so this suite measures the folds against the skills as they were on `main`:
v1 is each target skill on `main`, v2 is the same skill with the fold. Nine single-turn cases, each
graded on **target** (the behaviour the fold adds) and, where it applies, **guard** (something the
skill already did that the fold mustn't break). Calibrated on 18 hand-written replies (28 checks).

## Prediction, written before either version ran

- **software-design** (new `references/seams-and-testing.md`): v1 will already say "port and
  in-memory adapter" on sd-01 (APoSD and the FP notes mention ports & adapters) but won't say to
  delete the old wrapper tests; v2 should add it. sd-02 (a trait with one adapter) is the case I
  expect to flip: v1 tends to say "add the trait, it's good practice". sd-03 (design it twice) may
  pass on v1 too, since the skill already names the principle; v2 adds the comparison axes.
- **tdd**: Sonnet will spot the tautology and the internal mock with v1 (it's the kind of thing a
  reviewer notices), so I expect little lift there; the lift should be on t-03, where v1 may say
  "sounds good, make sure each fails first" instead of refusing horizontal slicing.
- **domain-driven-design**: v1 makes a glossary but without *Avoid* aliases, so target fails on v1
  and passes on v2.
- **software-architecture**: v1 will write the trivial ADR because it was asked to (target fails);
  v2's three-test gate should make it push back. arch-02 should pass both.
