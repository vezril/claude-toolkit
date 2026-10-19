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

## v1 re-baseline on max_turns 5: discarded

Re-ran to keep the comparison fair after the harness fix. The run hit the account's usage
limit 16 runs in, so 44 of 60 rows scored and the rest errored. Partial runs are not
evidence; the file was deleted rather than reported. The v1 numbers above stand as the
baseline, with the harness caveat stated.

## Next

v2: an output contract (raw JSON, the exact shape, the legal values for every enum and
boolean). Predict schema 0 → ~30 and a large jump in classification, since most of its
failures are illegal values rather than wrong judgement. Domains should stay near 0: the
contract says nothing about which vocabulary to use.
