# vault-graphrag — note schema

The contract every note in the graph follows. Frontmatter is the machine surface;
the body is for humans. A note that violates this schema is invisible to
retrieval, so treat schema conformance the way you'd treat a failing type check.

## Layout and naming

```
<vault>/<graph_root>/
  incidents/   ABC-446.md            # basename = ticket key, verbatim
  deliveries/  DEM-12.md             # basename = ticket key, verbatim
  decisions/   grpc-bff-for-consoles.md     # kebab-case slug
  entities/    orders-api.md         # basename = entity name from the binding
               olympus.md            #   …including one note per project
  patterns/    silent-downstream-await.md   # kebab-case failure shape
  lessons/     sentence-budgets-over-word-caps.md   # kebab-case practice
  _templates/  delivery.md           # frontmatter skeletons, not part of the graph
```

- Folders organize; the `type` field is the authority. Never infer type from path.
- **Basenames must be globally unique across the whole vault** — Obsidian resolves
  `[[links]]` by basename. Ticket keys, entity names, and kebab pattern names are
  three disjoint namespaces in practice; if a collision ever occurs, the new note
  yields and takes a suffix (`orders-api (team).md`) plus an `aliases` entry.
- One graph per vault. Multiple engagements share it, separated by the `client`
  field — never by parallel folder trees, which would fork entity notes.
- **`_templates/` is not part of the graph.** Recall scans the four payload folders only, so a
  template's placeholder frontmatter can never score as a match.

## The `project` field

`client` separates engagements; **`project` scopes work within one.** Delivery recall weights a
same-project hit at **+3**, which is the single biggest term in its scoring, so this field is
what makes "what have we already decided *here*" a different question from "what do we know".

- Optional on `incident`, `lesson`, `decision` and `delivery` notes, and on service/component
  entities.
- Its value is the binding's project name, verbatim and lowercase (`olympus`, `amazon`).
- **Changing it later touches every note that carries it**, and nothing derives it — so settle
  the name before the vault fills up, not after.

A project is also an entity note (`entity_type: project`), which is what gives it a page to
hold conventions and a backlink list of everything scoped to it.

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
entity_type: service      # service | platform | component | team | external | project
client: acme              # or "shared" for cross-engagement entities
project: olympus          # optional; which project this belongs to
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

## Type: decision

A settled technical choice, ADR-shaped, keyed by a kebab-case slug. It exists so a future
proposal does not re-litigate a question this project already answered — and so that when the
answer *changes*, the old one stops being quoted as current.

```markdown
---
type: decision
project: olympus
client: acme
status: accepted          # proposed | accepted | superseded
date: 2026-06-01          # when it reached this status
superseded_by: []         # [[slug]] of the decision that replaced this one
services: ["[[orders-api]]", "[[voice-gateway]]"]
refs:
  change: openspec/changes/add-grpc-bff/       # the OpenSpec change or ADR — linked, never copied
  pr: https://github.com/example/repo/pull/482
context: one line: what forced a decision
decision: one line: what was decided
consequences: one line: what this costs or constrains
---

## Context
## Decision
## Consequences
```

Field rules:

- **`context`, `decision` and `consequences` are the retrieval payload** — one sentence each.
  Recall shows these three lines verbatim and nothing else from the note, so a `decision` of
  "use the new approach" is a note that costs storage and returns nothing.
- **`status` decides visibility, not just history.** Only `accepted` decisions appear under
  "Decisions in force". A `superseded` one that would otherwise have matched appears solely in
  the recall output's coverage section, named alongside its replacement — visible, and
  impossible to mistake for current.
- **`refs` links; it never copies.** The repo's OpenSpec change or ADR is the source of truth.
  A decision note that duplicates a design doc is a second copy to keep in step, and it will
  lose.
- **`proposed` is a real state.** A decision under discussion is worth recording, and it stays
  out of "in force" until someone accepts it.

### Superseding a decision

Two edits, both required, or the graph lies:

1. On the old note: `status: superseded` and `superseded_by: ["[[new-slug]]"]`.
2. Write the new note with `status: accepted`.

Never edit a decision in place to mean something else. The point of the type is that the record
of *having changed your mind* survives, and an overwritten decision destroys exactly that.

### Minting rules

Write a decision note when a choice **constrains future work** and a reader six months out
would otherwise have to reconstruct it. Not for every design detail — a vault where every
preference is a decision makes recall return noise, and noise is indistinguishable from nothing.

## Type: delivery

One delivered feature, fix or task, keyed by its tracker key. The delivery counterpart of
`incident`: where an incident records something that broke, a delivery records something that
shipped.

```markdown
---
type: delivery
ticket: DEM-12
project: olympus
client: acme
status: shipped           # in-progress | shipped | reverted
date: 2026-08-14
domains: [backend, infra]
services: ["[[orders-api]]"]
decisions: ["[[grpc-bff-for-consoles]]"]
patterns: []
refs:
  pr: https://github.com/example/repo/pull/512
  ticket: https://jira.example.com/browse/DEM-12
goal: one line: what this delivered, and for whom
approach: one line: how, at the level a future reader needs
outcome: one line: what actually happened
---

## What shipped
## Notes for next time
```

Field rules:

- **`goal`, `approach` and `outcome` are the retrieval payload** — one line each, and the only
  parts of the note recall ever shows. Write them for a reader with ten seconds. "Implemented
  the ticket" is the failure mode: it satisfies the schema and carries no information.
- **`domains` is what recall matches during implementation**, weighted +3 there against +2 at
  solutioning, so a story's kinds of work pull up the deliveries that touched the same ground.
- **`status: reverted` is written honestly.** A memory that only records successes reads as
  though nothing ever fails, which is worse than having no memory.
- **`decisions` links the choices this followed**, which is how a delivery and the decision it
  implements end up adjacent in recall rather than each needing to be found separately.
- **Upsert by key.** Re-running the update operation edits fields; it never produces `DEM-12
  1.md`.

### The collision rule

Basenames are unique across the whole vault, and a ticket key can plausibly name both an
incident and a delivery. The delivery yields: `DEM-12 (delivery).md`, with
`aliases: [DEM-12-delivery]`. The incident keeps the bare key, because incident recall is older
and more widely linked.

## Link vocabulary summary

| From | Field | To | Meaning |
|------|-------|-----|---------|
| incident | `services` | entity | the incident manifested in / was fixed in these |
| incident | `platforms` | entity | external/platform systems in the causal path |
| incident | `patterns` | pattern | recognized failure shapes |
| decision | `services` | entity | what this decision binds |
| decision | `superseded_by` | decision | the decision that replaced this one |
| delivery | `services` | entity | what this change touched |
| delivery | `decisions` | decision | the choices this delivery followed |
| delivery | `patterns` | pattern | failure shapes this delivery addressed |
| incident / delivery / decision / lesson | `project` | entity (`entity_type: project`) | which project scopes this |
| entity (service, component) | `project` | entity (`entity_type: project`) | which project owns it |
| any | prose `[[...]]` | any | human navigation only — no schema meaning |

Backlinks (entity ← incident, pattern ← incident, project ← everything, decision ← delivery)
are derived, never written.

## What reads this schema

`scripts/delivery-flow/vault-recall.py` is the normative consumer for delivery recall: it reads
**frontmatter only**, scores by the weights in
[delivery-recall.md](delivery-recall.md), and never reads a note body. Two consequences worth
knowing while writing notes:

- A field recall does not read might as well not exist for retrieval. The payload lines are the
  interface.
- A note whose frontmatter does not parse is invisible rather than broken — no error, no match.
  Treat schema conformance the way you would a failing type check.
