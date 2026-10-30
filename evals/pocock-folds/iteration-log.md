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

## First attempt, discarded

The first v1 and v2 runs went in parallel with the pr-description suite and hit my 5-hour usage
limit; 22 samples in each errored out. They're kept as `results/run_v*_all.DISCARDED-usage-limit-partial.json`
and not scored. Everything below is the re-run, one suite at a time, REPEAT=3, both models.

## Scorer fixes found by reading the replies

Both fixes were calibrated (34/34 hand labels agree, up from 28/28 with six new labels covering
both directions) and both runs were regraded with `rescore.js --write`, so v1 and v2 are scored by
the same asserts.

- **ddd-01, a glossary table.** v2 failed ddd-01 on 5 of 6 runs, which looked like the fold not
  working. It was working: both models wrote a glossary table with an **Avoid** column (`| Patron |
  … | Member, borrower |`). My check wanted "avoid" on the same line as the aliases, and in a table
  that word is only in the header. The check now also reads each table row as "term, header: cell"
  for any column headed "Avoid". A table with a "Synonyms" column still fails, and that's v1's shape.
- **sd-03, design labels.** Three v2 replies failed "3 labelled designs" while labelling three or
  four: `**1. Limiter bound to one policy**`, `**A. Decision-only core.**`, `### A. Minimal`. The
  check only knew the "Design A" form. It now also takes a bare letter or number opening a heading
  or bold line, and when letter labels exist it ignores numbers, because `## 1. Framing` is a
  section, not a design. My first version of that took the larger of the two counts and let
  numbered sections pad two designs to three; a calibration label caught it before it graded
  anything.

## Results

| Run | Model | target | guard | Total |
|-----|-------|--------|-------|-------|
| v1 (skills on main) | Haiku | 17/27 | 13/15 | 30/42 (71.4%) |
| v1 (skills on main) | Sonnet | 17/27 | 15/15 | 32/42 (76.2%) |
| v2 (folded) | Haiku | 26/27 | 15/15 | 41/42 (97.6%) |
| v2 (folded) | Sonnet | 27/27 | 15/15 | 42/42 (100%) |

Evidence: `results/run_v1_all.json`, `results/run_v2_all.json` (both regraded). Scan clean on both.

Per skill, target only (Haiku / Sonnet):

| Skill | v1 | v2 |
|-------|----|----|
| software-design (sd-01..03) | 5/9 / 3/9 | 8/9 / 9/9 |
| tdd (t-01..03) | 6/9 / 8/9 | 9/9 / 9/9 |
| domain-driven-design (ddd-01) | 0/3 / 0/3 | 3/3 / 3/3 |
| software-architecture (arch-01..02) | 6/6 / 6/6 | 6/6 / 6/6 |

## What the prediction got right and wrong

- **software-design:** v1 missed more than I guessed. On sd-01 Sonnet suggested the in-memory
  adapter but kept the old wrapper tests (2 of 3), and both models missed design-it-twice's
  comparison axes on sd-03 (v1 compared on one of depth/locality/seam, every run). v2 fixed both.
  Haiku's one remaining v2 miss is real: it compared its three designs on depth only.
- **tdd:** I said Sonnet would spot the tautology unaided and it mostly did (8/9). Haiku didn't
  (t-01 failed 3/3 on v1), so the anti-pattern entry earned its place on the cheaper model, which is
  the reverse of where I expected the lift. t-03 passed on v1 for both, so horizontal slicing was
  already handled; the new entry doesn't hurt it.
- **domain-driven-design:** exactly as predicted, 0/6 → 6/6 once the table bug was fixed.
- **software-architecture:** wrong. v1 already declined the trivial ADR on every run (6/6), so the
  three-test gate shows no lift here. I'm keeping it because it gives a reason to decline that v1
  had to improvise, but this suite doesn't prove it's load-bearing; see `load-bearing.md`.
- **guards:** v1 Haiku dropped two guards (mocked an owned `OrderValidator` on sd-01, didn't call
  the Payments mock fine on t-02); v2 held 15/15 on both models.

## Regression check on main's own suite

`evals/software-design/` (main's certified suite, three cases) was re-run against the folded skill,
3 runs: 8/9, against 9/9 on main (`results/skill_folded_{1,2,3}.json`). The one miss is deep-modules,
run 2: the reply calls it classitis and shallow modules and flags information leakage, which is the
judgment the case wants, but it says "genuine depth" where the assert needs the literal word "deep".
I'm reporting it as a miss and not loosening that suite's assert. tdd, software-architecture and
domain-driven-design have no re-runnable suite on main (their README rows come from the
`promptfoo/skill-evals/` suites noted at the top), so this suite's guards are the only regression
evidence for them.
