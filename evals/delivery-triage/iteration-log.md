# Iteration log: triage node

The first node of the certified chain. It turns a tracker item into `triage.json`: the
classification the rest of the flow branches on (type, path, domains) and the three
policy flags that decide whether the flow stops and asks a human.

Fixtures are 10 real items (six archived OpenSpec proposals, the one real open issue in
the constellation, a Dependabot bump, two Olympus backlog bullets). Four deterministic
criteria: schema (via the same `validate-artifact.py` the edge hook runs), classification,
domains, grounding. Three repeats per case per model; the bar is 95% per run.

## v1 baseline (Red): Haiku 30/120 (25.0%), Sonnet 29/116 (25.0%)

**Baseline:** the naive one-liner — "Classify this work item… Return JSON with: item, type,
path, domains, summary, rationale, handoff, handoff_reason, architecture_change, breaking_change."
**Hypothesis:** none; this is the baseline.
**Change:** none.
**Result:** everything fails except grounding.

| criterion | Haiku | Sonnet |
|-----------|-------|--------|
| schema | 0/30 | 0/29 |
| classification | 0/30 | 0/29 |
| domains | 0/30 | 0/29 |
| grounding | 30/30 | 29/29 |

**Reasoning:** the failures are three distinct concerns, which is what the next three
iterations address.

- *Shape.* No output contract, so nothing parses raw: prose around the JSON, fences, or
  commentary. This criterion owns every formatting penalty.
- *Vocabulary.* The field names were given; the legal values were not. The models invented
  `type: "chore"`, `type: "epic"`, `path: "fast-track"`, `path: "greenfield"`, and — the
  telling one — returned `handoff` as a *string naming an agent* ("solution-architect",
  "requirements-analyst") rather than a boolean. A field name is not a contract.
- *Domains.* Free-form taxonomy every time: "pekko-cluster", "multi-tenancy",
  "observability", "branding-assets". Useful words, but the roster can't dispatch on them.
- *Grounding held at 30/30.* Both models describe the item in front of them accurately.
  What they can't do is guess a closed vocabulary nobody showed them.

One Sonnet case died on the harness's `max_turns: 3`, so `n` is 116 rather than 120 for
Sonnet. The config now uses `max_turns: 5`, matching the other suites.

## v1 re-baseline on max_turns 5: clean

The first re-run after the harness fix hit the account's usage limit 16 runs in; partial
runs are not evidence, so it was deleted rather than reported. The second re-run completed
with no provider errors: **Haiku 30/120 (25.0%), Sonnet 30/120 (25.0%)**, the same 0 / 0 / 0
/ 30 shape per criterion on both models. That run is the baseline of record
(`results/run_v1_all.json`); the max_turns 3 numbers above are superseded.

## v2 hypothesis (written before the run)

**Change:** an output contract only — raw JSON, first character `{`, the exact key names,
and the legal values for every enum and boolean, with "never a string, never the name of an
agent" stated for the three flags. Nothing about which domains exist.

**Prediction:** schema 0 → ~30 on both models. Classification jumps a long way, because most
of its failures were illegal values (`chore`, `epic`, `fast-track`, `handoff` as an agent
name) rather than wrong judgement — but it should not reach 30, since the genuinely hard
calls (the logging item that reads like a feature, the two architecture flags, the one-line
new-service item) are judgement, not vocabulary. Domains stays near 0: the contract says
`domains` is an array of strings and nothing about which strings are legal.

## v2 result: Haiku 44/120 (36.7%), Sonnet 78/120 (65.0%)
**Baseline:** Haiku 30/120, Sonnet 30/120 (v1).
**Hypothesis:** an output contract flips schema and most of classification; domains stays at 0.
**Change:** the output contract only — raw JSON, exact keys, legal values for every enum and boolean.
**Result:** Haiku 44/120 (36.7%), Sonnet 78/120 (65.0%).
**Reasoning:** see below — two thirds of the prediction held, and the miss is model-specific.


| criterion | Haiku v1 → v2 | Sonnet v1 → v2 |
|-----------|---------------|----------------|
| schema | 0 → 0 | 0 → **30** |
| classification | 0 → 15 | 0 → 18 |
| domains | 0 → 0 | 0 → 0 |
| grounding | 30 → 29 | 30 → 30 |

Two thirds of the prediction held. Sonnet's schema went 0 → 30/30, classification jumped on
both models (0 → 15 and 0 → 18) because the illegal values stopped appearing, and domains
stayed at 0 as expected — the contract says `domains` is an array of strings and nothing
about which strings exist.

The miss: **Haiku's schema stayed at 0/30, and the cause is the same on every single run** —
it wraps the object in a ```json fence. The anchored literal ("the first character of your
reply is `{`") was not enough on its own. Sonnet obeyed the same sentence 30/30, so this is a
model-specific habit, not an ambiguous instruction. Haiku's grounding also slipped by one.

## v3 hypothesis (written before the run)

**Change:** one addition, aimed only at the fence — state what the reply is *for* and what
the fence costs: the reply is written straight to `triage.json` and parsed by `json.loads`
with no cleanup step, so a fence is a parse error and the step fails. Ends with "Begin with
`{`".

**Prediction:** Haiku schema 0 → ~30. Sonnet stays at 30. Classification may rise slightly on
Haiku, since a fenced reply still scores on the lenient parse and shouldn't change judgement.
Domains stays at 0.

## v3 result: Haiku 45/120 (37.5%), Sonnet 73/120 (60.8%)
**Baseline:** Haiku 44/120, Sonnet 78/120 (v2).
**Hypothesis:** stating what the reply is for, and what a fence costs, fixes Haiku's schema.
**Change:** one addition about `json.loads` and the parse error, ending "Begin with `{`".
**Result:** Haiku 45/120 (37.5%), Sonnet 73/120 (60.8%); Haiku schema still 0/30.
**Reasoning:** telling a model not to do something, twice, did not stop it doing it.


The prediction failed. **Haiku schema stayed at 0/30** — the fence survives being told what
the reply is for and what the fence costs. Sonnet held schema 30/30 and lost 3 classification
and 2 grounding asserts, which is run-to-run movement on judgement calls rather than an effect
of a rule about fences.

Telling a model not to do something, twice, in two different ways, did not stop it doing it.

## v4 hypothesis (written before the run)

**Change:** stop describing the format and show it — one worked example of a complete reply,
compact single-line JSON, appended to v3.

**Prediction:** Haiku schema 0 → ~30. If it does not land, the honest conclusion is that this
harness cannot get raw-JSON-only out of Haiku, and the step escalates to Sonnet with the three
runs as the recorded evidence.

**Scope:** run on Haiku only. Sonnet's schema is settled at 30/30 across v2 and v3, and the
change is aimed at a Haiku-specific habit.

## v4 result (Haiku only): 51/120 (42.5%), schema 4/30

The worked example moved Haiku's schema from 0 to 4 of 30. Four runs out of thirty produced
a bare object; the other twenty-six still arrived in a ```json fence.

**Decision: triage certifies on Sonnet, not Haiku.** Three runs (v2, v3, v4) with three
different tactics — an anchored literal, a stated consequence, and a worked example — leave
Haiku's schema criterion at 0, 0 and 4 of 30. That is the escalation evidence the model-tier
policy asks for: the cheapest tier was tried first and recorded failing, rather than assumed
unsuitable. Everything else about Haiku's triage is respectable (grounding 30/30, classification
17/30 and rising with the contract), so this is a formatting ceiling in this harness, not a
judgement ceiling.

Iterations from here run on Sonnet. Haiku's results stay in the record as the evidence.

## v5 hypothesis (written before the run)

**Change:** a closed domain vocabulary — the eight roster words with a one-line definition
each, the rule that an empty array is a legal answer, and the sentence that a technology is
not a domain (Pekko clustering, authentication and logging are `backend` or `infra` work).

**Prediction:** Sonnet domains 0 → ~27+. The near-misses should be items where the right set
is arguable (does a metrics endpoint touch `infra` as well as `backend`?) rather than items
where invented words appear. Classification and schema should not move: nothing about type,
path or the flags changed.

## v5 result (Sonnet): 94/120 (78.3%) — domains 0 → 16/30
**Baseline:** Sonnet 73/120 (v3).
**Hypothesis:** a closed domain vocabulary takes domains to ~27.
**Change:** the eight roster words with definitions, the empty-array rule, and "a technology is not a domain".
**Result:** 94/120 as first scored (90/120 on the corrected basis); domains 0 → 16.
**Reasoning:** invented words stopped; the remaining disagreements are about which legal word, and several were my labels.


| criterion | v3 | v5 |
|-----------|----|----|
| schema | 30 | 29 |
| classification | 15 | 20 |
| domains | 0 | **16** |
| grounding | 28 | 29 |

The vocabulary worked in the sense that invented words stopped appearing: every remaining
domain failure uses legal words. It missed the 27+ I predicted because the disagreements are
about *which* legal words, and reading them, several are my labels being under-specified
rather than the model being wrong:

- `frontend` added beside `ux` on both UI items (3x, 3x). My own definitions — "what a person
  sees" versus "browser application code" — do not separate a sidebar rewrite. That is an
  ambiguous vocabulary, not a wrong answer.
- `data` added for the pantry item's new ingredient fields (3x). Defensible: it is a schema
  change. My label said `backend`.
- `backend`/`data` on the one-sentence recommender item (3x), where my label is an empty array.

Classification's remaining failures are a different thing and clearly the model's: flags fire
too eagerly. `architecture_change` true for a metrics endpoint (3x) and for UI changes (2x);
`handoff` true for clustering (2x) and auth (1x), both of which are large but fully described.

## v6 hypothesis (written before the run)

**Change:** the three flags get a definition each, with the bright line stated as what does
*not* count — an endpoint, dependency, logging or metrics inside one service is not an
architecture change; a change described as backward compatible is not breaking; a large,
well-described change is not a handoff. Plus the rule that a true `handoff` leaves `domains`
empty rather than guessing. Nothing about the domain vocabulary itself.

**Prediction:** Sonnet classification 20 → ~27. Domains should rise a little as a side effect,
because the recommender item's empty-array answer is now a stated rule rather than a guess —
that one is attributable and I will say so rather than claim it for v7.

## v6 result (Sonnet): 101/120 (84.2%)
**Baseline:** Sonnet 94/120 (v5).
**Hypothesis:** defining the three flags takes classification to ~27.
**Change:** a definition per flag, each stating what does not count, plus empty domains on handoff.
**Result:** 101/120 as first scored (98/120 corrected); classification 20 → 24.
**Reasoning:** the over-eager flags went away, and a negative rule without its positive half created the opposite error.


| criterion | v5 | v6 |
|-----------|----|----|
| schema | 29 | 29 |
| classification | 20 | **24** |
| domains | 16 | 20 |
| grounding | 29 | 28 |

Classification 20 → 24, short of the 27 I predicted, and domains rose 4 as the attributable
side effect of the empty-`domains`-on-handoff rule. The over-eager flags are gone: no metrics
endpoint is an architecture change any more, and clustering and auth are no longer handoffs.

The first run of v6 was cut short by the account's usage limit with 22 of 30 rows errored and
was deleted unscored; the numbers above are the clean re-run.

**My bright line over-corrected, and it cost accuracy in the other direction.** Writing "adding
an endpoint, a dependency, logging or metrics inside one service is not an architecture change"
taught the model to answer false for a *whole new service* (3x) and for a cross-cutting auth
and tenancy layer (2x) — both of which are architecture changes by my own ground truth. A
negative rule without its positive half is a new wrong answer.

Two more gaps the failures exposed:
- the prompt never stated how `path` follows from `type`, so a small UI feature got `quick` (1x);
- `structured-logging` loses `backend` (3x) because my definition put a service's own
  operational config outside `backend`, and `auth-tenancy` gains `contracts` (1x) because my
  definition didn't say that a service's own API surface is not a contract.

## v7 hypothesis (written before the run)

**Change — and this iteration moves two concerns at once, so its deltas are not individually
attributable. I am taking that trade deliberately to save runs, and saying so rather than
claiming a clean attribution:**

1. Domain definitions rewritten where they were ambiguous: UI work is `ux` including the code
   that renders it (never `ux` + `frontend` together); a service's own config, including
   operational config, is `backend`; `contracts` means a shared artifact outside the service,
   so a service's own REST or gRPC surface is `backend`; `data` means analytics and pipelines,
   not an application's own schema.
2. The positive half of `architecture_change` restored (a new service, including one proposed
   in a sentence, and a new cross-cutting layer), plus the `type` → `path` mapping stated.

**Prediction:** domains 20 → ~28, classification 24 → ~29. Schema and grounding unchanged.

## v7 result (Sonnet): 116/120 (96.7%) — first run over the bar
**Baseline:** Sonnet 101/120 (v6).
**Hypothesis:** rewriting the ambiguous domain definitions and restoring the positive half of `architecture_change` takes domains to ~28 and classification to ~29.
**Change:** two concerns at once (stated as such): domain definitions, and the flag/path rules.
**Result:** 116/120 (96.7%); per repeat 95.0%, 97.5%, 97.5%.
**Reasoning:** first version over the bar, with each repeat over it on its own.


| criterion | v6 | v7 |
|-----------|----|----|
| schema | 29 | 30 |
| classification | 24 | **29** |
| domains | 20 | **27** |
| grounding | 28 | 30 |

Both halves landed. Per repeat: 95.0%, 97.5%, 97.5% — each one over the bar on its own, which
is what certification asks for rather than a good average.

## v8: refactor to Role / Task / Context / Constraints
**Baseline:** Sonnet 116/120 (v7).
**Hypothesis:** restructuring costs nothing.
**Change:** structure only, plus two implicit behaviours written down.
**Result:** 95.0% / 92.5% / 95.0% as first scored; 100% / 97.5% / 100% after the ground-truth correction below.
**Reasoning:** the refactor held, and its re-run is what surfaced the label bug.


**Change:** structure only — the same rules reorganised into Role, Task, Context, Output and
Constraints, with two behaviours the model was doing implicitly written down: what separates
bug/feature/task, and that the rationale should say what *in the item* drove the call.

**Result, first scoring:** three consecutive runs at 95.0%, 92.5%, 95.0%. Run 2 under the bar.

**Every failure in all three runs was the same one**: the model left `infra` off
service-internal observability work — structured logging (3/3), the metrics endpoint (3/3),
clustering (1/3).

## The ground-truth correction

Reading those failures, the model was following my own vocabulary and my labels were
contradicting it. v7's definitions say a service's own config, *including operational config
such as its logging and metrics wiring*, is `backend`, and that `infra` is the platform side —
build, CI, containers, charts, deployment. Then my expected sets demanded `infra` as well for:

- `structured-logging`, which adds one dependency and edits `logback.xml` inside the service;
- `metrics-endpoint`, which adds a route, a registry and a config toggle inside the service.

Both are `backend` by the definition I wrote. I corrected those two labels to `["backend"]` and
recorded why in each `expected/*.json`. Clustering keeps `[backend, infra]`: it changes cluster
formation, discovery and a management port, which is deployment-side work.

Two things about that correction, because the easy version of this story would be dishonest:

1. **It raises scores, so leaving it would have been the conservative choice.** v8 was already
   passing two of three runs; I corrected the labels because they were wrong, not because they
   were inconvenient.
2. **Every prior version was re-scored on the corrected basis** with `rescore.js`, which replays
   the saved outputs through the current asserts with no model calls. v5 and v6 both drop a few
   asserts under the correction (94 → 90 and 101 → 98), because runs that *included* `infra` now
   count it as an extra domain. The progression below is all on one basis.

## Score progression (Sonnet unless noted, corrected basis)

| Run | Change | schema | classification | domains | grounding | Total |
|-----|--------|--------|----------------|---------|-----------|-------|
| v1 | naive baseline | 0/30 | 0/30 | 0/30 | 30/30 | 30/120 (25.0%) |
| v1 (Haiku) | naive baseline | 0/30 | 0/30 | 0/30 | 30/30 | 30/120 (25.0%) |
| v2 | output contract | 30/30 | 18/30 | 0/30 | 30/30 | 78/120 (65.0%) |
| v2 (Haiku) | output contract | 0/30 | 15/30 | 0/30 | 29/30 | 44/120 (36.7%) |
| v3 | anti-fence consequence | 30/30 | 15/30 | 0/30 | 28/30 | 73/120 (60.8%) |
| v3 (Haiku) | anti-fence consequence | 0/30 | 16/30 | 0/30 | 29/30 | 45/120 (37.5%) |
| v4 (Haiku) | worked example | 4/30 | 17/30 | 0/30 | 30/30 | 51/120 (42.5%) |
| v5 | domain vocabulary | 29/30 | 20/30 | 12/30 | 29/30 | 90/120 (75.0%) |
| v6 | flag definitions | 29/30 | 24/30 | 17/30 | 28/30 | 98/120 (81.7%) |
| v7 | domain + flag corrections, path rule | 30/30 | 29/30 | 27/30 | 30/30 | 116/120 (96.7%) |
| **v8** | **RTCC refactor** | **30/30** | **30/30** | **29/30** | **30/30** | **119/120 (99.2%)** |

**Certification runs (v8, Sonnet, three consecutive):** 40/40 (100%), 39/40 (97.5%), 40/40 (100%).
Evidence: `results/run_v8_sonnet_run{1,2,3}.json`.

**Certified tier: Sonnet.** Haiku was tried first and recorded failing across three tactics
(v2, v3, v4) at 0, 0 and 4 of 30 on schema, for one reason: it wraps the object in a ```json
fence. Its judgement was never the problem — grounding 30/30, classification climbing with the
contract — but a node whose output is parsed with no cleanup step cannot ship on a model that
fences it 26 times out of 30. Evidence: `results/run_v4_haiku.json`.

## Known residual

One domain assert fails in about one run in three: `clustering` sometimes comes back
`["backend"]` without `infra`. The line between "this service's own config" and "the platform
side" is genuinely thin for a change that edits cluster discovery, and the prompt could be
sharpened there. It sits inside the bar, so it is recorded rather than papered over.

## What I'd carry to the next node

- A negative rule without its positive half teaches a new wrong answer. "Logging inside one
  service is not an architecture change" produced "a brand-new service is not an architecture
  change" two iterations later.
- Naming a field is not specifying it. v1 named `handoff` and got back the string
  "solution-architect"; the contract had to say boolean, never an agent's name.
- When the model keeps disagreeing with the labels in the same direction, suspect the labels.
  Two of mine contradicted my own vocabulary, and the model was right both times.
- A refactor needs its re-run. v8's restructure looked harmless and surfaced the label bug.
