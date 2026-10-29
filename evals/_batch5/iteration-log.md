# EDD batch 5 — repo conventions and niche domains

Batch 4 concluded that a skill gains where it encodes **something a well-read model would not
already conclude**. I picked these ten to test that rule directly: this repo's own machinery
(`prompt-edd`, `vault-graphrag`, `toolkit-archive`), territory-split scaffolds
(`python-tests`, `scala-sbt-build`), niche or bespoke domains (`flipper-unleashed`,
`openclaw-agents`, `akka-sdk-agents`), a skill whose facts I had **personally verified the model
getting wrong** (`gitbucket`), and the repo's densest rule set (`stripe-payments`).

I predicted **6–8 gains**.

**Result: 1 gain, 9 ties.**

| Skill | Baseline | With skill | Delta |
|---|---|---|---|
| `akka-sdk-agents` | 1/2 | 2/2 | **+50%** |
| `prompt-edd` | 3/3 | 3/3 | 0 |
| `vault-graphrag` | 3/3 | 3/3 | 0 |
| `gitbucket` | 3/3 | 3/3 | 0 |
| `flipper-unleashed` | 2/2 | 2/2 | 0 |
| `openclaw-agents` | 2/2 | 2/2 | 0 |
| `python-tests` | 2/2 | 2/2 | 0 |
| `toolkit-archive` | 2/2 | 2/2 | 0 |
| `scala-sbt-build` | 2/2 | 2/2 | 0 |
| `stripe-payments` | 3/3 | 3/3 | 0 |

## The one gain, and why it is the one

`akka-sdk-agents`: **an Agent cannot be a tool for another agent — orchestrate with Workflows.**
Baseline FPF on naming `Workflow` and `AgentRegistry`/`dynamicCall`; skill PPP.

This is consistent with the whole Akka SDK family, which holds the lowest baselines in the
table — `akka-sdk-event-sourced-entities` at 79%, `akka-sdk-workflows` at 83%, both annotated
*"naive hallucinates SDK API"*. That is the one domain where the model reliably invents, because
the SDK is recent, the surface is specific, and there is little public text to have absorbed.

## My prediction was wrong twice running, and that is now the finding

Batch 4: predicted 4–6 gains, got 1. Batch 5: predicted 6–8, got 1. **I am not able to predict
where a skill will show a delta**, and two wrong predictions in a row is enough to stop treating
my heuristics as reliable.

What the five batches actually show, pooled:

- **Gains cluster in a narrow band.** Unusual rails the model has no reason to hold (DSM's
  refuse-to-diagnose, 15 of 18 chapters), territory splits in paired scaffolds
  (`python-package` +50%), calibration behaviour (`detect-ai` 25% → 100%), credential handling
  (`dockerhub-setup`), and **recent APIs the model hallucinates** (the Akka SDK family).
- **Everything else ties**, including things I was confident about: repo-specific conventions,
  bespoke systems, niche hardware, payments rails.

The surprise in this batch is that *repo-specific* content tied. `prompt-edd`'s refusals,
`vault-graphrag`'s upsert-don't-duplicate rule, `toolkit-archive`'s referrer guard — the
baseline got all of them. A strong model reconstructs sensible conventions from the request
itself; "unknowable" turns out to mean far less than I assumed, because most good conventions
are *derivable*.

**The honest operating conclusion:** stop predicting. Either accept that most remaining skills
will tie and stop spending runs on them, or change what the suites measure — because the thing
the ties have in common may be my case design rather than the skills.

## `gitbucket` deserves a caveat rather than a clean tie

I had **personally verified** the model getting GitBucket facts wrong against a live 4.48.0
instance: the `- path:` map schema, `/user/repos` 404ing from route shadowing, no
`PATCH /issues/:id`. It scored 3/3 baseline here anyway.

That is partly my case design, and I should say so. I wrote the cases as *"does not invent a VM
mount"*, *"declines the false premise"*, *"says there is no issue-close endpoint"* — soft,
refusal-shaped asserts the model passes by being appropriately cautious. I did **not** test the
hard facts I had measured, like asking for the `additional_directories` YAML and checking for
`path:`. A suite that asks for caution measures caution. **The tie here is weak evidence, and a
fact-shaped rerun would likely show a real delta.**

## One more harness bug, and the check that finally catches it

`python-tests` scored FFF in both arms with `i is not defined`. Cause: an unescaped trailing
slash in a generated regex — `/…|error|src//i.test(output)` — the same class as batch 3.

**The compile-check I added in batch 4 did not catch it, because it is a runtime error, not a
syntax one.** `new Function(body)` compiles that program happily; it only fails when run. So the
check now **executes** each assert against a probe string and ignores only the deliberate
`throw new Error(...)`:

```bash
node -e "const fs=require('fs');for(const d of fs.readdirSync('evals')){const p='evals/'+d+'/tests.yaml';
if(!fs.existsSync(p))continue;for(const m of fs.readFileSync(p,'utf8').matchAll(/value: \|\n((?:        .*\n)+)/g)){
const b=m[1].replace(/^        /gm,'');try{const f=new Function('output',b);
try{f('probe')}catch(e){if(!/^Error: /.test(String(e)))console.log('RUNTIME',d,String(e))}}
catch(e){console.log('SYNTAX',d,e.message)}}}"
```

That passes 265 asserts across the whole `evals/` tree. **This is the seventh assert bug across
five batches**, and each new check has caught the previous class and missed the next. Executing
is the first one that would have caught all seven.

## Limits

- **Two to three cases per suite.** Nine ties at this size cannot distinguish base-strong from
  under-tested, and `gitbucket` above is a concrete case of a tie that is probably an artifact
  of case design.
- The refusal-shaped asserts used throughout this batch are easy to pass. Fact-shaped asserts
  discriminate better and I under-used them.
- Reference files untested for all ten.

## Reproducing

```bash
for s in prompt-edd vault-graphrag gitbucket akka-sdk-agents flipper-unleashed openclaw-agents \
         python-tests toolkit-archive scala-sbt-build stripe-payments; do
  for n in 1 2 3; do
    npx promptfoo@latest eval -c evals/$s/promptfooconfig.baseline.yaml --no-cache -o evals/$s/results/baseline_$n.json
    npx promptfoo@latest eval -c evals/$s/promptfooconfig.yaml          --no-cache -o evals/$s/results/skill_$n.json
  done
done
```
