## Why

`project-memory` and `vault-update` have sat in the routing table since `add-delivery-flow`
with nothing behind them: no prompt, no script, no registry entry, and no schema for
`project-context.json`. They are skipped whenever `vault.binding` is null, which is every repo,
so the pipeline has never had organizational memory. The item in front of it is always the first
item it has ever seen.

`extend-vault-graphrag-projects` specifies the memory model — a `project` entity, `decision` and
`delivery` note types, and a delivery-recall algorithm — but is unimplemented, and its task 3.4
assumes recall is a prompt to be certified at Stage 3.

Reading that spec closely says otherwise, and it is the reason this change exists in the shape it
does. The algorithm is arithmetic: **3** per same project, **3** per shared service link, **2**
per shared domain (**3** in implementation mode), **1** per keyword hit; drop below **3**;
tie-break by date; cap at 5/5/3/3; frontmatter only; output facts and never advice. There is no
judgement in it. Implemented as a prompt it needs an eval suite, three consecutive runs, a
load-bearing map and an iteration log, to approximate a calculation Python performs exactly.
Implemented as a script it is deterministic, free, byte-identical on reruns, and **edge-grade**
rather than another node whose output has to be policed.

There is also a failure mode specific to this machine. The vault is an AFP mount on a NAS
(`/Volumes/Private/Amazon RAG`). When the volume is not mounted a naive recall returns nothing —
indistinguishable, at the output, from a vault that genuinely holds nothing relevant. The run
then proceeds with no memory, looks successful in the trace, and nobody learns that the memory
step was dead.

## What Changes

- **`vault-recall.py`: delivery recall as a deterministic script.** Implements the specified
  scoring, thresholds, caps, accepted-only rule and coverage reporting with `rg`-style scanning
  and stdlib YAML-subset parsing. No model, no network, no certification — it joins the edges,
  not the nodes. Emits `project-context.json` and, for a human, an equivalent
  `project-context.md`.
- **`project-context.json` becomes the contract**, against `schemas/project-context.schema.json`,
  with a sentinel. The vault spec's `project-context.md` stays as the human rendering: the
  routing table has always named the `.json`, and anything a node consumes must be schema-backed.
- **Reachability is distinguished from emptiness.** Before scanning, recall checks the graph root
  exists and is readable. Unreachable is **exit 3** and no artifact — the step fails and the flow
  stops. Reachable-but-nothing-matched is **exit 0** with an artifact whose `matched: false` and
  whose coverage section states what was scanned. The trace therefore shows the difference
  between "no memory applied" and "memory consulted, nothing relevant", which is the difference
  between a broken pipeline and a cold start.
- **`scaffold-vault.py`** creates the graph root and its five folders in an existing Obsidian
  vault, writes one `project` entity and the note templates, and touches nothing already there.
  Idempotent, and it refuses to write outside the configured vault path.
- **The schema work from `extend-vault-graphrag-projects`** lands in
  `skills/vault-graphrag/references/schema.md`: the `project` entity type, the optional `project`
  field, the `decision` and `delivery` note types with their frontmatter contracts and minting
  rules, and the extended link vocabulary. `references/delivery-recall.md` documents the
  algorithm as implemented, pointing at the script as the normative definition.
- **`vault-update` stays a node**, and ships uncertified and declared. Writing a delivery note
  means composing one-line `goal` / `approach` / `outcome` fields from the run — that is
  generation, not traversal, and it is the one part of this that genuinely needs a model.
- **The binding gains `graph_root` and `backend`.** `vault.binding` names the project;
  `vault.path` and `vault.graph_root` locate the graph; `vault.backend` is `filesystem`
  (the only implementation) with `iris` reserved and returning a clear not-implemented error.

## Capabilities

### New Capabilities
- `deterministic-vault-recall`: recall as a script — the scoring, thresholds, caps,
  accepted-only rule, the two call points, the `project-context.json` contract, the coverage
  report, and the facts-not-advice rule enforced by construction rather than by prompt.
- `vault-binding-reachability`: the binding keys, the reachability check, the exit-code
  distinction between unreachable and empty, and what the trace records for each.
- `vault-delivery-update`: the update node, what it upserts, the stubs it may mint, and its
  declared-uncertified status.

### Modified Capabilities

<!-- none live: vault-graphrag predates OpenSpec here and has no spec; the delivery-flow specs
     belong to unarchived changes. This change implements the schema deltas already specified by
     extend-vault-graphrag-projects and amends its task 3.4 in prose — see design D1. -->

## Impact

- **New:**
  - `scripts/delivery-flow/vault-recall.py`, `scripts/delivery-flow/scaffold-vault.py`;
  - `schemas/project-context.schema.json`;
  - `skills/vault-graphrag/references/delivery-recall.md`;
  - `skills/delivery-flow/references/vault-update.md` (the node prompt, uncertified);
  - `tests/delivery-flow/test_vault_recall.py` with a synthetic mini-vault fixture.
- **Modified:**
  - `skills/vault-graphrag/references/schema.md` (the new types, field and link vocabulary);
  - `skills/vault-graphrag/SKILL.md` (operations list, description triggers);
  - `skills/delivery-flow/references/config.md` (the binding keys);
  - `scripts/delivery-flow/flow-status.py` (the vault steps stop being inert when bound);
  - `skills/delivery-flow/SKILL.md`, `references/trace.md`, `docs/delivery-flow-handoff.md`.
- **Amends:** `extend-vault-graphrag-projects` task 3.4 — recall needs no Stage 3 certification
  because it is no longer a prompt. Its eval suite becomes the script's test suite, which is
  stricter: exact scores rather than a 95% pass rate.
- **Deferred:** the `iris` backend; certification of `vault-update`; seeding real decision notes
  from existing Olympus ADRs (task 5.2 of the parent change, which needs Calvin's judgement about
  which ADRs matter).
- **Non-breaking:** incident recall and the private defect-flow bindings are untouched; repos
  with `vault.binding: null` behave exactly as before.
