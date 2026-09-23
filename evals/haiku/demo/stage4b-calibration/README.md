# Stage 4b — calibrating the checker

```bash
cd evals/haiku/demo/stage4b-calibration
node calibrate.js          # → PASS: 12/12 checks
```

**No model calls.** This runs offline, which also makes it the safest thing to
show if the conference Wi-Fi dies.

## Why this stage exists

Stage 4 replaced keyword matching with hand-written JavaScript. That bought real
checks — and a new liability: **the checker is now code, and code has bugs.** A
bug here doesn't fail loudly. It quietly changes every number in the iteration
log, in either direction.

So before trusting a score, check the checker against replies whose verdict you
already know.

## The two directions

```js
{ name: 'perfect shape, 5-7-5 content',
  text: 'My morning coffee\nwarm like a gentle embrace\ncozy and serene',
  fails: ['craft'] }        // contract must still PASS
```

1. A **good** reply passes every criterion.
2. A **bad** reply fails *exactly* the criteria it lists — and **passes the rest**.

The second half is the one people skip, and it's the one that matters. The coffee
fixture has a perfectly good *shape*, so it must fail craft and pass contract. If a
single mistake could flip two metrics, every prompt change would move every number
and you could never attribute a delta to a cause.

The six fixtures are chosen to pin that separation down: a clean poem, a reply that
fails both criteria, one that fails only craft, one that fails only contract (a
markdown title over a fine poem), a trailing explanation, and one that exercises the
syllable counter's known weak spot — "aches" is one syllable and "Montreal" is
three, and a naive vowel-group counter reads that poem as 5-7-5 when it's 5-6-4.

## What the real suite does

`../../calibration/` is the full version, and it's worth showing next to this one:

- **`syllables.js`** — the counter against **181 hand-counted lines** in four sets,
  including a **20-line holdout written after tuning and never used to tune**. The
  honest accuracy number comes from that set. Bar: every line within ±1, at least
  90% exact. Currently 100% on all four.
- **`fixtures.js` + `scorers.js`** — a good and a bad reply for all 13 cases, each
  bad one declaring which criteria it must fail. **77/77** checks.
- **`real-v1-critiques.json`**, **`real-labeled-pass.json`**, **`real-craft-pass.json`**
  — real model replies, hand-labelled, frozen as regression cases. Each file is a
  scorer bug that was found by reading outputs: a knowledge check that let three
  critiques repeat the 5-7-5 myth, a verdict detector that saw "unlike senryu" and
  failed a correct answer, a season-word list missing *zansetsu* ("last patch of snow").

## The numbers behind the slide

- The counter was wrong on **6 of 45** hand-counted lines on first writing.
- **Five scorer bugs** total, all found by reading outputs — **three of them made
  the skill look *worse* than it was.**
- Every fix was followed by `rescore.js --write`, which re-scores recorded outputs
  with **no new model calls**, so the whole progression table stays comparable.

> Calibrate the ruler before you report the measurement.
