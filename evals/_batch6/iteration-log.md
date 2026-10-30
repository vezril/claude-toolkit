# EDD batch 6 — the Akka SDK family, and the point where this method stops paying

Picked on the only evidence left: the Akka SDK family holds the three lowest baselines in the
table — `akka-sdk-event-sourced-entities` 79%, `akka-sdk-workflows` 83%, `akka-sdk-agents` 50%
— all annotated *"naive hallucinates SDK API"*. Five direct siblings were blank, plus
`swiftui-liquid-glass` (a 2025 API) and four newer Akka modules on the same recency logic.

I declined to predict a number, having been wrong twice.

**Result: 0 gains, 10 ties.**

| Skill | Baseline | With skill |
|---|---|---|
| `akka-sdk-endpoints` | 2/2 | 2/2 |
| `akka-sdk-views` | 2/2 | 2/2 |
| `akka-sdk-key-value-entities` | 2/2 | 2/2 |
| `akka-sdk-consumers` | 2/2 | 2/2 |
| `akka-sdk-timed-actions` | 2/2 | 2/2 |
| `swiftui-liquid-glass` | 2/2 | 2/2 |
| `akka-edge` | 2/2 | 2/2 |
| `akka-distributed-cluster` | 2/2 | 2/2 |
| `akka-insights` | 1/1 | 1/1 |
| `akka-diagnostics` | 2/2 | 2/2 |

The baseline answered correctly, unprompted, on: endpoints are thin and delegate via
`ComponentClient`; SSE must resume from offsets because instances rebalance; views are
eventually consistent so poll rather than read-your-write; the only way to change KV state is
`effects().updateState`; use event sourcing when you need history; `ignore()` events you do not
handle; register the timer **before** the business operation; a renamed timed-action id breaks
the serialized timer; don't stretch one Akka Cluster across regions, give each region its own
database and replicate events; put application config outside `akka.*`; and
`.interactive()` only on genuinely interactive glass.

## The finding that matters: my suites, not the skills, are producing the ties

The Akka SDK family was chosen **because** its scored members sit at 50–83% baseline. My suites
put the same family at **100%** baseline. Both cannot be measuring the same thing.

The earlier scores came from a different harness — the README records them as run externally via
`claude -p --model <m>` with per-case majority at N=3, with suites and logs under
`promptfoo/skill-evals/<skill>/`, which is not in this repo. So the comparison across harnesses
is not valid, and more importantly: **a 1–2 case suite with asserts I wrote from the skill's own
"Always-apply" list is close to unfalsifiable.** I am writing down the claim, then checking the
model restates it. A competent model restates it.

Pooled across the last three batches: **30 skills, 2 gains.** Batches 4 and 5 each produced one;
this one produced none. The marginal value of another batch of this shape is approximately zero,
and continuing would mostly generate more blank-equivalent rows at ~60 model runs each.

## Recommendation: stop, and change the method before resuming

Three things would have to change for the next batch to mean anything:

1. **Calibrate asserts against a known-wrong answer.** The `gitbucket` case proved the point: I
   had *measured* the model getting those facts wrong on a live instance, then wrote
   refusal-shaped cases it passed 3/3. An assert that the model's own default answer already
   satisfies cannot show a delta. Write the case against the observed wrong answer, not against
   the skill's bullet list.
2. **More cases, or none.** At 1–3 cases a single flip is 33–100%, and a tie carries almost no
   information. Either 8–10 cases per skill, or accept the row stays blank.
3. **Test what the skill does that prose cannot.** Several of these are reference catalogs whose
   value is recall under load and consistency across a long session — neither of which a
   single-turn suite sees at all.

The blank rows are not a bug to be cleared. **169 blank out of 282 is a reasonable resting
state**, and the honest annotation for most of them is "untested, and a cheap test would not
distinguish it from the baseline" rather than a number.

## Eighth assert bug

`akka-distributed-cluster`'s `db` case failed in both arms. Both answers were correct — *"Give
each region its own database and replicate events between regions"* — and my regex required
`own(s) its database`, i.e. "own" **before** "its". The text said "its own database". Word
order.

That is the eighth across six batches, and every one has been the same mistake in a new costume:
**asserting a phrasing instead of a claim.** The execute-check added in batch 5 catches broken
asserts; nothing catches *semantically narrow* ones except reading the transcript, which remains
the only reliable habit.

## Limits

One to two cases per suite — thinner than any previous batch, and the main reason to distrust
these ties. `akka-insights` has a single case. No reference files tested.

## Reproducing

```bash
for s in akka-sdk-endpoints akka-sdk-views akka-sdk-key-value-entities akka-sdk-consumers \
         akka-sdk-timed-actions swiftui-liquid-glass akka-edge akka-distributed-cluster \
         akka-insights akka-diagnostics; do
  for n in 1 2 3; do
    npx promptfoo@latest eval -c evals/$s/promptfooconfig.baseline.yaml --no-cache -o evals/$s/results/baseline_$n.json
    npx promptfoo@latest eval -c evals/$s/promptfooconfig.yaml          --no-cache -o evals/$s/results/skill_$n.json
  done
done
```
