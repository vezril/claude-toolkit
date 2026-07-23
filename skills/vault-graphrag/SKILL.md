---
name: vault-graphrag
description: "Build and query a GraphRAG knowledge graph inside an Obsidian vault using nothing but notes, frontmatter properties, and typed wikilinks — no external index, no embeddings, no sync problem. Three note types (incident, entity, pattern) turn each handled defect/investigation into durable, linked, queryable knowledge. Covers the note schema and naming conventions, the vault-update operation (upsert an incident note + entity stubs + pattern links after handling a defect), and the vault-recall operation (deterministic graph retrieval: 'have we seen something like this before?' → a compact prior-incidents artifact). Use when setting up a knowledge graph over an Obsidian vault, writing an incident/defect into the vault, recalling similar prior incidents, designing frontmatter schemas for graph traversal, or wiring a workflow pipeline (e.g. a defect-handling flow) to accumulate and reuse organizational memory. Client- and domain-agnostic: all instance vocabulary (which services, which teams, vault location) comes from a binding config the caller supplies."
argument-hint: "[update <ticket-key> | recall <ticket-key> | a schema/setup question]"
---

# vault-graphrag — an Obsidian vault as a knowledge graph

An Obsidian vault already *is* a graph: notes are nodes, wikilinks are edges,
frontmatter properties are typed attributes. This skill turns that latent graph
into a deliberate one — a schema strict enough for deterministic traversal, loose
enough to stay pleasant to read and edit by hand. No database, no embedding index,
no sync daemon: the notes are the graph, and `rg` + YAML parsing are the query
engine.

**Schema first, index later.** Everything here works with plain text tooling. If
retrieval quality ever demands semantic search, an embedding index can be bolted
on without changing a single note — the schema is the contract, the query path is
an implementation detail. Don't reach for infrastructure until traversal provably
fails you.

Load the reference for the operation at hand:

- **[references/schema.md](references/schema.md)** — the three note types, their
  frontmatter contracts, naming/folder conventions, the typed-link vocabulary,
  and worked examples. Read before writing any note.
- **[references/recall.md](references/recall.md)** — the deterministic retrieval
  algorithm (candidate entities → link/keyword scan → scoring → the
  `prior-incidents.md` output contract), and the v2 escalation path.

## The model in one paragraph

Four note types. An **incident** is one handled defect/investigation — keyed by
its ticket id, carrying symptom / root cause / resolution as *frontmatter fields*
so retrieval never has to parse prose. An **entity** is a durable thing incidents
happen to: a service, platform, component, or team. A **pattern** is a recurring
failure shape ("silent await on a downstream dependency") that generalizes across
incidents. A **lesson** is a measured practice improvement (a prompt technique,
an eval-design finding) written by evidence-producing workflows like EDD runs. Incidents link *to* entities and patterns via frontmatter wikilinks;
Obsidian's backlinks give you the reverse edges for free. The payoff compounds:
every handled incident makes the next "have we seen this before?" cheaper.

## The two operations

**vault-update** (write path — run after handling a defect):

1. Read the pipeline's artifacts for the ticket (structured ticket context,
   proposal/analysis, summary, PR/post receipts — whatever the calling workflow
   produced).
2. **Upsert** the incident note keyed by ticket id — never a duplicate; re-runs
   update fields in place (status transitions, added links).
3. Ensure every linked entity note exists — create missing ones as stubs from the
   binding vocabulary (schema.md § entity).
4. Link patterns with restraint: list existing pattern notes first, link the one
   that fits; **mint a new pattern only when nothing fits**, following the
   minting rules in schema.md — near-duplicate patterns are how graphs rot.
5. Never delete or rewrite history; corrections edit fields in place.

No human gate needed — the vault is local, private, and every change is a
reviewable diff in a text file.

**vault-recall** (read path — run early in an investigation):

Given a new ticket's context, find the k most relevant prior incidents by entity
overlap and symptom keywords, and emit a compact `prior-incidents.md` artifact —
frontmatter fields only, never raw note dumps. Full algorithm, scoring, and
output contract in recall.md. An honest empty result ("no prior incidents share
these entities") is a valid and useful artifact.

## The binding: everything instance-specific

This skill is domain-agnostic. The caller supplies a binding (a YAML block or
file) with the instance facts; nothing below may be hardcoded in notes-writing
logic:

```yaml
vault:
  path: /path/to/Vault          # the Obsidian vault root
  graph_root: graph             # subfolder holding the graph (created if absent)
  client: acme                  # stamped on notes; lets one vault host several engagements
  entity_vocabulary:            # seed entities; entity notes are stubbed from these
    - name: orders-api
      type: service
      aliases: [orders, order-service]
    - name: voice-gateway
      type: service
      aliases: []
    - name: TelephonyCo
      type: external
      aliases: []
```

A defect-handling pipeline binds this once per client; swapping clients swaps the
binding, not the skill. Keep client vocabularies out of any public repo — they
are the binding's business.

## Rules that keep the graph healthy

- **Frontmatter is canonical, prose is commentary.** Traversal reads only
  frontmatter; anything load-bearing (links, status, symptom) must live there.
  Prose wikilinks are welcome for humans but carry no schema weight.
- **Rely on backlinks; never maintain reverse-index lists by hand** ("incidents
  affecting this service") — hand-kept lists drift, backlinks don't.
- **Basenames are globally unique** (Obsidian resolves links by basename).
  Naming rules in schema.md exist to guarantee this — follow them.
- **Stubs are fine, wrong facts are not.** A two-line entity note is healthy;
  an invented root cause in an incident note poisons every future recall.
