# vault-graphrag — note schema

The contract every note in the graph follows. Frontmatter is the machine surface;
the body is for humans. A note that violates this schema is invisible to
retrieval, so treat schema conformance the way you'd treat a failing type check.

## Layout and naming

```
<vault>/<graph_root>/
  incidents/   ABC-446.md            # basename = ticket key, verbatim
  entities/    orders-api.md         # basename = entity name from the binding
  patterns/    silent-downstream-await.md   # kebab-case failure shape
  lessons/     sentence-budgets-over-word-caps.md   # kebab-case practice
```

- Folders organize; the `type` field is the authority. Never infer type from path.
- **Basenames must be globally unique across the whole vault** — Obsidian resolves
  `[[links]]` by basename. Ticket keys, entity names, and kebab pattern names are
  three disjoint namespaces in practice; if a collision ever occurs, the new note
  yields and takes a suffix (`orders-api (team).md`) plus an `aliases` entry.
- One graph per vault. Multiple engagements share it, separated by the `client`
  field — never by parallel folder trees, which would fork entity notes.

## Type: incident

One note per handled defect/investigation. Upserted by ticket key — re-running an
update edits fields, never creates `ABC-446 1.md`.

```markdown
---
type: incident
ticket: ABC-446
client: acme
title: "Caller hears dead air after first reply"
date: 2026-07-23          # date handled (last update run)
status: fixed             # open | in-review | fixed | routed | wont-fix
severity: Sev2            # client's own scheme, verbatim
environment: PROD
services: ["[[voice-gateway]]", "[[orders-api]]"]
platforms: ["[[TelephonyCo]]"]
patterns: ["[[silent-downstream-await]]"]
symptom: "caller gets silence after their first utterance; session stays active"
root_cause: "speech-to-text timeout abandoned the turn with no caller-facing fallback"
resolution: "retry once, then spoken fallback; escalate to human after two failed turns"
refs:
  jira: https://jira.example.com/browse/ABC-446
  pr: https://github.com/example/repo/pull/482
---

## What happened
Two to four sentences of narrative a future reader needs beyond the symptom line.

## Root cause
The causal chain in prose — the frontmatter field is the one-liner, this is the why.

## Fix
What changed, at the level a future incident-handler needs.

## Lessons
Optional. Anything generalizable that ISN'T big enough to be a pattern note yet.
```

Field rules:

- `symptom`, `root_cause`, `resolution` are the retrieval payload — one sentence
  each, concrete, no ticket-speak. These three lines are what a future
  `vault-recall` shows verbatim, so write them for the reader who has 10 seconds.
- `status` uses the closed vocabulary above. `routed` means the fix was handed to
  another team/system (no code change here); pair it with a `Lessons` line saying
  where it went.
- Every wikilink in `services`/`platforms`/`patterns` must resolve to a real note
  by the end of the update run (stub creation is the updater's job).
- Do not add fields ad hoc. A recurring need for a new field is a schema change:
  update this reference and the update/recall logic together.

## Type: entity

A durable thing incidents happen to. Created as a stub from the binding
vocabulary the first time something links to it; enriched by hand over time.

```markdown
---
type: entity
entity_type: service      # service | platform | component | team | external
client: acme              # or "shared" for cross-engagement entities
aliases: [orders, order-service]
---

One paragraph: what this is, what it talks to, where its logs/dashboards live.
```

- **No hand-maintained incident lists.** Obsidian backlinks already answer "what
  happened to this service"; a written list drifts the day after it's written.
- `aliases` matter: recall matches ticket text against `name + aliases`, so put
  the informal names people actually type in tickets here.

## Type: pattern

A recurring failure shape — the graph's most valuable and most abusable node type.

```markdown
---
type: pattern
title: "Silent await on a downstream dependency"
aliases: []
---

## Signature
How to recognize it: the observable shape in symptoms/timelines, in 2–3 bullets.

## Fix shape
What resolutions of this pattern have in common (timeout + user-visible fallback
+ escalation path), not any one incident's specifics.
```

**Minting rules — read before creating any pattern:**

1. List existing patterns first (`ls patterns/` + their aliases). If one fits,
   link it — even a 70% fit beats a near-duplicate.
2. A pattern describes a **failure shape, not an incident**: "silent-downstream-
   await", never "stt-timeout-in-voice-gateway". If the name only makes sense for
   one system, it's not a pattern yet.
3. Two linked incidents are the informal bar for minting. One incident's hunch
   goes in that incident's `Lessons` section instead; promote it when the second
   occurrence shows up.
4. Kebab-case basename, ≤4 words, verb-or-shape not blame ("config-drift-between-
   environments", not "ops-forgot-to-sync").

## Type: lesson

A generalizable practice learned from **measured** work — prompt techniques,
eval-design findings, workflow habits. Where `pattern` captures how systems
fail, `lesson` captures how the practitioner works better. Written by processes
that produce evidence (an EDD iteration log, a pipeline retro), never from
vibes.

```markdown
---
type: lesson
title: "Sentence budgets beat word caps"
date: 2026-07-23
source: "EDD run: defect-summary eval iterations"
client: shared          # lessons are usually client-agnostic
tags: [prompting, evals]
---

## The lesson
One or two sentences stating the practice.

## Evidence
The measured observation that earned it: scores before/after, run references.
A lesson with no evidence section is an opinion — put it in a daily note, not here.

## How to apply
When to reach for it, in 1–3 bullets.
```

Minting rules: kebab-case basename stating the practice (≤6 words); check
`lessons/` for an existing note first and extend its Evidence section rather
than minting a near-duplicate; one lesson per note. Lessons are not scanned by
incident recall — they surface through Obsidian search, backlinks, and the
processes that write them re-reading them first.

## Link vocabulary summary

| From | Field | To | Meaning |
|------|-------|-----|---------|
| incident | `services` | entity | the incident manifested in / was fixed in these |
| incident | `platforms` | entity | external/platform systems in the causal path |
| incident | `patterns` | pattern | recognized failure shapes |
| any | prose `[[...]]` | any | human navigation only — no schema meaning |

Backlinks (entity ← incident, pattern ← incident) are derived, never written.
