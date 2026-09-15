## Why

`vault-graphrag` only models defects: incident, entity, pattern and lesson notes, with recall asking "have we seen this bug before?". Delivery work needs a different question: "what have we already decided, built and learned **in this project**?" There is no notion of a project, no note type for a decision or a delivered feature, and no recall aimed at solutioning or implementation. The new `delivery-flow` pipeline (change `add-delivery-flow`) needs that memory to avoid re-deciding settled questions and repeating past mistakes across multi-repo projects such as the Olympus constellation.

## What Changes

- **Project scoping:** a new `entity_type: project`. An optional `project:` frontmatter field on incident, delivery, decision and lesson notes, plus a `project:` link on service/component entities, so a service belongs to a project.
- **New `decision` note type:** a short ADR-style record (context, decision, consequences, status: proposed/accepted/superseded), keyed by a kebab-case slug. It links to the authoritative ADR, OpenSpec change or PR in the repo and never copies its content.
- **New `delivery` note type:** one delivered feature, bug fix or task, keyed by tracker item key. It is the delivery counterpart of `incident`, with one-line retrieval fields (`goal`, `approach`, `outcome`), `domains`, `status`, and links to decisions, services and PR.
- **New recall operation `delivery-recall`,** run at two points:
  - **before solutioning:** decisions, related deliveries, patterns and lessons for the item's project and services, with same-project hits weighted above other projects;
  - **before implementation:** lessons and patterns for the story's kinds of work.
  - It emits a compact `project-context.md` output file with a mandatory search-coverage section, using the same deterministic, frontmatter-only scoring style as incident recall.
- **Extended update operation:** after delivery, upsert the delivery note, stub missing project/service entities, and link or create decision notes. Minting rules mirror the pattern and lesson rules.
- **Strictly additive:** existing notes, the incident recall algorithm and its output format are unchanged. The defect-flow bindings (`vault-recall`, `vault-update` in the private repo) keep passing their eval suites without edits.

## Capabilities

### New Capabilities
- `vault-project-memory`: the schema additions (project entity type, the `project:` field, the decision and delivery note types, their frontmatter contracts, naming and minting rules, link vocabulary) and the extended update operation that writes them.
- `vault-delivery-recall`: the delivery recall algorithm (inputs, project-scoped scoring, the two call points, the `project-context.md` output format, coverage and empty-result rules).

### Modified Capabilities

<!-- none: vault-graphrag predates OpenSpec in this repo and has no spec; incident recall behavior is unchanged -->

## Impact

- **Modified:**
  - `skills/vault-graphrag/SKILL.md` (model paragraph, operations list, description triggers);
  - `skills/vault-graphrag/references/schema.md` (new types, field, link-vocabulary rows).
- **New:**
  - `skills/vault-graphrag/references/delivery-recall.md`;
  - an eval suite `evals/vault-delivery-recall/` with a synthetic mini-vault fixture (project with two services, decisions, deliveries, one cross-project decoy).
- **Consumers:** `delivery-flow`'s optional recall and update steps (change `add-delivery-flow`). The private defect-flow repo is unaffected, verified by re-running its `vault-recall` and `vault-update` suites.
- **Open input:** Olympus's answer to question 8.2 in the vault note `+/Stage 4 - What I need from Olympus.md` (what `iris-service` already writes to the vault) may adjust folder layout or field names before implementation.
- **No infrastructure:** still plain `rg` plus YAML parsing, no embeddings.
