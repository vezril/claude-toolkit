# EDD batch 3 — procedure and load-bearing skills

Eight previously unscored skills: four procedure skills (chosen because `dockerhub-setup` showed
50% → 100% and procedure skills grade deterministically) and four referenced by multiple agents.

Model `sonnet` via `evals/_provider/claude.sh`. **N=3 per case, majority scoring.** Deterministic
asserts only, no judge.

| Skill | Baseline | With skill | Delta |
|---|---|---|---|
| `python-package` | 1/2 | 2/2 | **+50%** |
| `python-uv-build` | 2/3 | 3/3 | **+33%** |
| `software-design` | 2/3 | 3/3 | **+33%** |
| `release-app-store-changelog` | 2/2 | 2/2 | 0 |
| `release-macos-spm-packaging` | 2/2 | 2/2 | 0 |
| `agentic-workflows` | 3/3 | 3/3 | 0 |
| `network-security` | 2/2 | 2/2 | 0 |
| `modern-java` | 3/3 | 3/3 | 0 |

**3 gains, 5 ties, 0 losses.**

## What moved

- **`python-package` / `python-uv-build`** — the **territory rails**. The naive arm, asked to
  also write tests, sources, README and CI as part of a scaffold, agrees. The skills decline:
  these are halves of a deliberately split pair, and crossing the boundary is the failure.
- **`software-design`** — the **deep-module** judgment. Shown five single-method classes
  (`UserValidator`, `UserMapper`, `UserFetcher`, `UserCacheKeyBuilder`, `UserResponseShaper`)
  and asked "good separation of concerns?", the naive arm often approves. The skill names it as
  shallow modules / classitis and argues the interface complexity went *up*.

Everything else was already base-strong. `modern-java`, `agentic-workflows` and
`network-security` baselines got records-over-mutable-bags, start-simple-before-agents, and
segment-plus-default-deny unprompted.

## Six broken asserts, and the pattern is now the main finding

This batch produced, in order: a suite scoring 0/2 in both arms, another at 1/3, an apparent
**regression** on `modern-java`, and a corrupted assert in an *already-merged* suite. None of it
was a skill. All of it was my harness.

1. **Four asserts had JavaScript syntax errors.** Unescaped forward slashes inside regex
   literals — `/src/|__init__/i` terminates at the first `/`, so the rest parsed as code and
   threw `__init__ is not defined` / `Invalid regular expression flags`. These produced the 0/2
   and 1/3 "results".
2. **My fix for that corrupted a merged DSM assert.** The repair script read a line holding
   *two* regex literals as one and escaped the separators, mangling
   `evals/dsm-anxiety/tests.yaml`. Reverted; verified no merged file was left modified. A fix
   script needs its own check.
3. **A negative assert that passed trivially.** `/^(?!.*(bump deps|…)).*$/` cannot cross
   newlines, so it matched the first line of any multi-line reply and never failed. Replaced
   with an explicit absence check — and then *that* failed a correct answer which listed the
   notes and afterwards explained which commits it had deliberately left out as internal. Final
   version scopes the check to the bullet lines only.
4. **`modern-java`'s apparent regression.** The skill-arm answer opened *"Verdict: replace it
   with a record"* and listed *"Non-final public fields: anyone can change them at any time"* —
   exactly right. It failed because my regex wanted `no public field` and the text said
   `public fields`. Broadened; the regression vanished and the suite is a tie.

**Counting the earlier batches, this is the sixth time.** The failure mode is identical every
time: I assert a particular *wording* for a claim rather than the claim, and the failures land
disproportionately on the *best* answers, because a good answer phrases things in ways the
regex author did not anticipate. Two habits actually catch it, and both are cheap:

- **When a case fails in both arms, or the skill arm looks worse than baseline, read the
  transcript before believing the number.** This has caught every one.
- **Compile-check generated regex literals before running anything.** A one-line
  `new Function('return ' + literal)` over the suite would have caught four of the six
  instantly, for free.

## A real harness limitation, found here

**`python-uv-build` and `python-package` are action skills.** They work by running
`scaffold.sh`, and the eval provider disables all tools — necessarily, since a baseline arm with
`Read` could pull the SKILL.md off disk and contaminate the comparison. So the model correctly
replied *"I couldn't scaffold anything, Bash is disabled"*, and my action-shaped cases scored
that correct refusal as a failure.

Both cases were reworded to ask for the **rule** rather than the action ("what's in and out of
your territory, and which generated file do you deliberately not create?"). That tests the
territory rail honestly without tools. But the general point stands and is worth recording:
**this harness cannot evaluate what an action skill actually does**, only what it says it will
do. Skills whose value is in the doing need a different harness — a sandbox with tools enabled
and assertions on the resulting file tree.

## Limits

- **Two to three cases per suite.** Thin, and five of the eight suites are ties on 2–3 cases,
  which cannot distinguish "base-strong" from "under-tested". Do not read a tie here as proof a
  skill adds nothing.
- The four procedure skills are tested on their stated rules, not their execution (above).
- `software-design`, `modern-java`, `network-security` and `agentic-workflows` each get one
  judgment case per major claim at most; their reference files are untested entirely.

## Reproducing

```bash
for s in python-uv-build python-package release-app-store-changelog release-macos-spm-packaging \
         software-design agentic-workflows network-security modern-java; do
  for n in 1 2 3; do
    npx promptfoo@latest eval -c evals/$s/promptfooconfig.baseline.yaml --no-cache -o evals/$s/results/baseline_$n.json
    npx promptfoo@latest eval -c evals/$s/promptfooconfig.yaml          --no-cache -o evals/$s/results/skill_$n.json
  done
done
```
