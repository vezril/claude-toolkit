# EDD batch 4 — the ten "most likely to gain" skills

I picked these ten by predicting where a delta would appear, using what had gained in batches
1–3: rails, territory boundaries and contrarian judgment gain; reference content ties. I
predicted **4–6 gains**.

**Result: 1 gain, 9 ties.** The prediction was wrong, and that is the finding.

| Skill | Baseline | With skill | Delta |
|---|---|---|---|
| `cross-examine` (the skill) | 2/3 | 3/3 | **+33%** |
| `swift-concurrency-expert` | 3/3 | 3/3 | 0 |
| `ux-design` | 3/3 | 3/3 | 0 |
| `swiftui-performance-audit` | 3/3 | 3/3 | 0 |
| `event-storming` | 3/3 | 3/3 | 0 |
| `godot` | 3/3 | 3/3 | 0 |
| `game-programming-patterns` | 3/3 | 3/3 | 0 |
| `game-development` | 2/2 | 2/2 | 0 |
| `web-development` | 2/2 | 2/2 | 0 |
| `game-production` | 2/2 | 2/2 | 0 |

Every baseline except `cross-examine` scored 100%. Unprompted, the naive arm refused dark
patterns and invoked Jakob's Law, pushed back on `@unchecked Sendable`, demanded code before
diagnosing SwiftUI jank, named orange past-tense domain events and framed hot spots as valuable
output, prescribed scene composition over deep inheritance in Godot, warned against speculative
patterns, required playtesting, reasoned about rendering strategy from the auth characteristics,
and pushed back on crunch.

The one gain is `cross-examine`'s **REFUTED means rerun the producing step, not patch the
holes** — baseline PFF, skill PPP. A specific procedural rule rather than a judgment call,
which is consistent with what has gained before.

## Why the prediction failed

My selection heuristic was "rails and judgment gain". That was drawn from batches where the
rails were **unusual** — DSM's refuse-to-diagnose, the python scaffolds' territory split,
`detect-ai`'s calibration, `dockerhub-setup`'s credential handling. Those are rails a general
model has no reason to hold.

The rails in this batch are different: refusing dark patterns, demanding a profile before
optimising, preferring composition to inheritance, not crunching a team. **A safety-trained,
well-read model already holds all of those.** They are good engineering consensus, widely
written about, and the skill restates rather than installs them.

So the rule that actually predicts a delta is narrower than "rails and judgment":

> **A skill gains where it encodes something a well-read model would not already conclude** —
> a project-specific convention, a counter-intuitive reversal in a named source, a procedural
> rule with an arbitrary correct answer, or a boundary the model has no way to know.

Consensus best practice, however well written, ties. That is not an argument against those
skills — they make the behaviour reliable and they document the reasoning — but it does mean an
eval cannot show their value, and the blank EDD rows should be read accordingly.

## Two harness bugs, one of them shipped

**`ux-design` scored FFF in both arms on two cases.** Both answers were correct — they named
Hick's Law and Jakob's Law explicitly. The asserts threw `missing ) after argument list`:
my generator wrote `throw new Error('names Hick's Law')`, and the apostrophe closed the JS
string.

The compile-check I added in batch 3 did not catch it, because **it validated only the regex
literal, not the whole assert body.** Widened to compile the full body with
`new Function('output', body)` — and that immediately found something worse.

**Two asserts in the already-merged `dsm-other-mental` suite have been broken since batch 2**,
from the identical apostrophe bug (`chapter's`). Two of its five cases threw on every run in
both arms. That is why it was the one flat suite in that batch, and the numbers I committed for
it — 3/5 → 3/5 — were wrong. Fixed here; the true score is **5/5 → 5/5**. Still a tie, but the
recorded figure was an artifact, not a measurement.

**A third problem was my own cleanup.** The apostrophe-fix script edited every `tests.yaml` it
could find, including 20 already-merged ones, and damaged
`evals/release-app-store-changelog/tests.yaml`. Reverted all tracked files and verified none was
left modified. **This is the second time a fix script of mine has corrupted merged work** — the
first was `evals/dsm-anxiety/tests.yaml` in batch 3. A repair script needs to be scoped to the
files in play, not to a glob.

**And a collision.** `evals/cross-examine/` already exists on `main`, testing the
`adversarial-validator` *agent*. My generator wrote a skill suite into the same directory,
mixing the two; after the revert the baseline arm ran my cases and the skill arm ran the
merged ones. The skill suite now lives at **`evals/cross-examine-skill/`** and the agent suite
is untouched. The naming trap I flagged in batch 2 caught me in batch 4.

## Limits

- **Two to three cases per suite.** Nine ties on 2–3 cases cannot distinguish base-strong from
  under-tested, and should not be read as proof a skill adds nothing.
- Reference files are untested for every skill here.
- `cross-examine`'s suite tests the verdict-handling rules only, not the adversarial reasoning.

## Reproducing

```bash
for s in swift-concurrency-expert ux-design swiftui-performance-audit event-storming godot \
         game-programming-patterns game-development web-development game-production \
         cross-examine-skill; do
  for n in 1 2 3; do
    npx promptfoo@latest eval -c evals/$s/promptfooconfig.baseline.yaml --no-cache -o evals/$s/results/baseline_$n.json
    npx promptfoo@latest eval -c evals/$s/promptfooconfig.yaml          --no-cache -o evals/$s/results/skill_$n.json
  done
done
```

Before running anything, compile-check the asserts:

```bash
node -e "const fs=require('fs');for(const d of fs.readdirSync('evals')){const p='evals/'+d+'/tests.yaml';
if(!fs.existsSync(p))continue;for(const m of fs.readFileSync(p,'utf8').matchAll(/value: \|\n((?:        .*\n)+)/g))
{try{new Function('output',m[1].replace(/^        /gm,''))}catch(e){console.log('BAD',d,e.message)}}}"
```
