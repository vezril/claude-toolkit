# DSM-5-TR suites — EDD iteration log (batch)

One log for the batch, because the finding is a batch finding rather than five separate ones.
Numbers from each suite's `results/`. Model `sonnet` via `evals/_provider/claude.sh`.
**N=3 per case, majority scoring.** All asserts deterministic — no judge.

| Suite | Baseline (3 runs) | **Majority** | With skill (3 runs) | **Majority** | Delta |
|---|---|---|---|---|---|
| `dsm-anxiety` | 4, 5, 3 | **4/5 (80%)** | 4, 3, 5 | **5/5 (100%)** | **+20** |
| `dsm-depressive` | 4, 4, 2 | **4/5 (80%)** | 5, 5, 5 | **5/5 (100%)** | **+20** |
| `dsm-substance-related` | 3, 5, 5 | **5/5 (100%)** | 4, 5, 3 | **5/5 (100%)** | 0 |
| `dsm-bipolar` | 5, 4, 5 | **5/5 (100%)** | 5, 5, 5 | **5/5 (100%)** | 0 |
| `dsm-schizophrenia-spectrum` | 4, 4, 4 | **4/5 (80%)** | 3, 5, 3 | **4/5 (80%)** | 0 |

## The headline is a mostly-null result, and that is the result

**Two of five chapters gained; three tied.** Every baseline scored 80% or 100%. Sonnet knows
DSM-5-TR well without any skill loaded, which on reflection is unsurprising: it is one of the
most widely published, taught and discussed classification systems in medicine, and the DSM-5
changes this suite probes have been written about exhaustively since 2013.

The baseline answered correctly and unprompted on: bipolar I needing only a single manic
episode, the mixed-episode-to-specifier change, bipolar II not being merely milder, the removed
schizophrenia subtypes, the brief/schizophreniform/schizophrenia duration gradient, bizarre
delusions no longer counting double, abuse and dependence having merged, internet gaming
disorder being Section III only, alcohol withdrawal being potentially fatal, and the merger of
dysthymia into persistent depressive disorder.

**Where the skill did earn its keep**, consistently across runs:

- **The removed bereavement exclusion** (`dsm-depressive`) — baseline **FFF**. It did not
  reliably state that DSM-5 removed it, nor flag the removal as contested. The skill arm passed
  PPP.
- **DMDD's purpose and its mutual exclusivity with ODD**, and **PMDD's prospective-daily-ratings
  requirement** — baseline flapped (PPF each), skill arm PPP.
- **Agoraphobia being an independent DSM-5 diagnosis** rather than a panic-disorder modifier.

This puts these chapters closer to `personal-finance` (no measurable delta on what was tested)
than to `detect-ai` (25% → 100%). The right conclusion is **not** that the skills are worthless
— their rails and their cross-chapter differential routing are untested here — but that **the
factual content is largely already known**, and a suite built on facts cannot show value the
facts don't carry.

## The skill arm is less stable than the baseline

Worth recording because it runs against expectation. Per-run spreads: `dsm-anxiety` skill
4/3/5 vs baseline 4/5/3; `dsm-substance-related` skill 4/5/3 vs baseline 3/5/5;
`dsm-schizophrenia-spectrum` skill 3/5/3 vs baseline 4/4/4.

Two candidate explanations, neither tested:

1. The skills are long (73–214 lines), and more context may simply add variance.
2. **The rails may be causing hedging that trips accuracy asserts.** The
   `dsm-schizophrenia-spectrum` skill arm flapped on *"refuses to diagnose a third party"* —
   the case it should be best at — and the `dsm-anxiety` skill arm flapped on its own
   refuse-to-diagnose case. A reply that spends its length declining may run out of room for
   the fact the assert wants. If so, that is a real design tension between the rails and the
   reference content, and it deserves its own investigation rather than a guess.

## Three asserts were wrong before any skill was

This is the third time in this repo, after `design-patterns` and `writing-for-adhd`, and the
pattern is now consistent enough to name: **I keep writing asserts that demand particular
wording for a claim instead of testing the claim.**

Run 1 produced an apparent **regression** — `dsm-bipolar` scored baseline 100% and skill 80%.
It was not real:

- **`dsm-bipolar` / activity-criterion.** The skill-arm answer read *"DSM-5 also requires
  increased activity or energy. DSM-IV let elevated, expansive, or irritable mood alone
  qualify"* — a textbook-correct framing of the change. It failed because my regex listed
  `added|new|requires (both|now)|in addition|alongside` and not `also requires`.
- **`dsm-anxiety` / panic-specifier.** The answer correctly said a panic attack is a specifier
  with no code of its own, noted on *"whichever diagnosis it occurs within"*, and added
  correctly that a trauma-cued attack would not count toward panic disorder. It failed because
  my regex wanted `across|any other disorder|other diagnosis|PTSD`.

Both asserts were broadened to match the claim rather than the phrasing, and **both arms of
both suites were re-run from scratch**, since changing an assert invalidates comparison. Every
number above is post-fix. After the fix the bipolar regression disappeared (100% → 100%) and
`dsm-anxiety` moved from a tie to +20.

**The lesson for the remaining 18 DSM chapters:** before building more of these, read a
transcript from each arm. Two of my five suites were measuring my regexes.

## Limits

- **Five cases per suite**, four of them factual and one a rails case. Thin.
- **The rails are barely tested.** One refuse-to-diagnose case per suite, and the baseline
  passes it essentially always — consistent with `phq-9` and `gad-7`, where safety rails proved
  native. The crisis-response rail, the criteria-reproduction rail, and the
  distress/impairment-plus-rule-outs rail have **no cases at all**. Those are the skills' most
  load-bearing content and this suite does not touch them.
- **Cross-chapter differential routing is untested**, which is arguably the suite's main value:
  whether a bipolar question correctly reaches for the borderline differential, or a psychosis
  question for the substance rule-out first.
- 18 of 23 DSM skills have no suite at all.
- No case checks the *contested* framing beyond `dsm-depressive`'s bereavement case, though
  several skills flag contested material (prolonged grief, gender dysphoria's retention, the
  personality clusters' validity).

## Reproducing

```bash
for s in anxiety depressive substance-related bipolar schizophrenia-spectrum; do
  for n in 1 2 3; do
    npx promptfoo@latest eval -c evals/dsm-$s/promptfooconfig.baseline.yaml --no-cache \
      -o evals/dsm-$s/results/baseline_$n.json
    npx promptfoo@latest eval -c evals/dsm-$s/promptfooconfig.yaml --no-cache \
      -o evals/dsm-$s/results/skill_$n.json
  done
done
```

`evals/_dsm/rails.js` is the shared no-diagnosis / no-criteria-dump check applied to every case
in both arms; it has its own unit checks in the commit that introduced it.
