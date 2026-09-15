## Context

`vault-graphrag` treats an Obsidian vault as a graph:
- notes are nodes, frontmatter wikilinks are typed edges;
- `rg` plus YAML parsing is the query engine;
- four note types: incident, entity, pattern, lesson;
- one recall operation (incident recall → `prior-incidents.md`) and one update operation.

It is consumed today by the private defect-flow repo's `vault-recall` and `vault-update` bindings, both with passing promptfoo suites. The vault is `/Users/cference/Mindmap`, graph root `Atlas/RAG`.

The new `delivery-flow` pipeline (change `add-delivery-flow`) needs project-scoped memory of decisions, delivered work and lessons at two points: before solutioning and before implementation. Olympus is multi-repo (a service plus its UI plus shared contracts), so "project" spans repositories. A service entity has to know which project it belongs to.

Constraints (from the existing schema):
- basenames globally unique;
- one graph per vault, never parallel folder trees;
- frontmatter carries the retrieval payload;
- no hand-maintained backlink lists;
- do not add fields ad hoc.

## Goals / Non-Goals

**Goals:**
- Scope any note to a project and let services/components belong to one.
- Record decisions and deliveries as first-class, recallable notes.
- Deterministic delivery recall with same-project weighting and mandatory search coverage.
- Keep every existing note, algorithm and output format valid unchanged.

**Non-Goals:**
- Embeddings or any index (the v2 escalation path in `recall.md` stays as-is).
- Copying ADRs, specs or PR content into the vault; the repo stays the source of truth.
- Changing incident recall's scoring or `prior-incidents.md`.
- Syncing with `iris-service`. Its role is pending Olympus's answer 8.2, and a later change may make it a writer.

## Decisions

### D1. Project is an entity type, not a folder or a vault
Add `project` to `entity_type`. Scoping is a `project: "[[olympus]]"` link.
- *Alternatives:* folder-per-project (rejected: the schema forbids parallel trees; shared entities would fork); reusing `client` (rejected: `client` separates engagements, while a single engagement or personal constellation has many projects).
- `project` is a single link, not a list. A service shared by two projects links the one that owns it, and cross-project reuse surfaces through recall's lower weight.

### D2. `decision` note type, ADR-lite and link-first
- Basename: kebab-case statement of the decision (≤6 words, e.g. `grpc-bff-for-operator-consoles`), in `decisions/`.
- Frontmatter:
  - `type: decision`, `title`, `date`, `status: proposed | accepted | superseded`, `superseded_by` (link, required when superseded), `project`, `services[]`, `domains[]`;
  - one-line payload fields `context`, `decision`, `consequences`;
  - `refs` (adr / openspec / pr URLs or repo paths).
- Body: short prose, which must point to the authoritative ADR or OpenSpec design when one exists.
- Minting rules mirror patterns and lessons: search existing decisions and aliases first; extend rather than duplicate; supersede rather than edit history.
- *Alternative:* store decisions only in repos and scan repos at recall time. Rejected: cross-repo scanning is slow and non-uniform, and the vault note is a pointer with a one-line payload, not a copy.

### D3. `delivery` note type, the counterpart of incident
- Basename: the tracker item key, in `deliveries/`. On a basename collision with an existing incident note (the same key handled by both flows), the delivery note takes `<KEY> (delivery)` and adds the key to `aliases`, per the existing collision rule.
- Frontmatter:
  - `type: delivery`, `item`, `kind: feature | bug | task`, `title`, `date`, `status: delivered | in-review | punched-out | abandoned`, `project`, `services[]`, `domains[]`, `decisions[]`, `patterns[]`;
  - one-line payload fields `goal`, `approach`, `outcome`;
  - `refs` (tracker, pr, openspec).
- *Alternative:* extend `incident` with a `kind` field. Rejected: incident's payload (symptom/root_cause/resolution) doesn't fit features, and changing it risks the defect-flow suites.

### D4. Additive optional fields on existing types
- `incident`, `lesson` and service/component `entity` gain an optional `project` link.
- `lesson` gains optional `domains[]`.
- Nothing becomes required, and incident recall ignores the new fields. That is why the defect-flow suites need no edits; the tasks still re-run them as proof.

### D5. Delivery recall: deterministic, project-weighted, two call points
- Inputs: `item.json` plus `triage.md` (solutioning call) or a story file (implementation call), and the binding (`vault.path`, `graph_root`, `project`, entity vocabulary).
- Candidate sets: services/components matched against the binding vocabulary and aliases (as in incident recall); keywords (3–6 concrete words from title/goal); domains (from triage or the story).
- Scan `decisions/`, `deliveries/`, `lessons/` and `patterns/`.
- Score:

```
score = 3 × same project
      + 3 × shared service/component links
      + 2 × shared domains            (implementation call: ×3)
      + 1 × keyword hits in payload lines (context/decision/goal/approach/outcome/title)
```

- Drop anything below 3. Cross-project candidates can still qualify through shared services, domains and keywords.
- Decisions: `accepted` only in Matches; `superseded` ones are listed only in coverage, pointing at their replacement.
- Caps: decisions 5, deliveries 5, lessons 3, patterns 3. Tie-break by date, newest first.
- The solutioning call emphasizes decisions and deliveries; the implementation call emphasizes lessons and patterns for the story's domains (via the domain weight).
- Output `project-context.md` (≤80 lines):
  - sections: Decisions in force, Related deliveries, Lessons, Patterns, and a **mandatory** Search coverage section (entities, keywords, domains, notes scanned per folder, dropped counts, superseded decisions skipped);
  - payload lines copied verbatim from frontmatter; never note bodies.
- *Alternative:* reuse incident recall with more folders. Rejected: different payload fields and weighting; one algorithm with flags would make the defect-flow contract fragile.

### D6. Delivery update operation
After a delivery-flow item ends, upsert its `delivery` note by key (never duplicate), stub missing `project`/service entities from the binding vocabulary, and link existing decisions.
- New decision notes are minted only for decisions recorded in the item's accepted OpenSpec design or ADRs, never inferred.
- Status transitions edit in place. No human decision point, consistent with the existing update operation (local, diffable).

### D7. Filesystem recall by default; Iris as an optional read backend (Olympus answer 8.2)
`iris-service` (phase 1) is a **read-only** bridge. It mirrors the vault into Postgres and serves `GET /notes`, `GET /notes?path=`, but it writes nothing, and no service authors project notes today. Project knowledge currently lives in `codex/docs/*.md` design notes, `codex/docs/session-coordination.md`, and per-repo Claude memory.
- **Recall backend:** `vault.backend: filesystem` (default: `rg` over the local vault, works on either Mac via Obsidian Sync) or `iris` (query Iris's API for frontmatter, the same scoring). The `iris` backend is specified here but implemented in a follow-up once Iris exposes frontmatter filtering. v1 must not depend on the cluster being reachable.
- **Write location:** delivery and decision notes are written by Claude sessions through the filesystem into the one graph root (`Atlas/RAG/decisions/`, `Atlas/RAG/deliveries/`), per the one-graph rule. Iris phase 2's service write confinement (`Atlas/Olympus/<Service>/`) governs *services*, not these sessions. If Iris phase 2 later writes project notes, they should be `delivery`/`decision` typed so recall picks them up wherever they live; recall scans by `type`, not folder, when `scan: by-type` is set.
- **Seeding:** the first real decision notes come from existing `codex/docs/*.md` design notes and archived OpenSpec `design.md` files (linked, not copied), which gives recall a non-empty graph on day one.

## Risks / Trade-offs

- **[Decision notes drift from repo ADRs]** → payload is one line each plus a mandatory `refs` link; the body points to the source; `superseded` workflow instead of edits; recall shows `refs` so the reader goes to the authority.
- **[Keyword matching misses synonyms]** → same known weakness as incident recall; services and domains carry most of the score; the v2 embedding path remains available without schema change.
- **[Over-minting decisions]** → minting only from accepted design/ADR files, plus search-first rules.
- **[Delivery/incident key collisions]** → the existing suffix + alias rule; recall matches by `item` field, not basename.
- **[iris-service already writes a different structure]** → open question gated on Olympus answer 8.2; implementation waits for it before finalizing folder names.

## Migration Plan

No migration: existing notes remain valid. Create `decisions/` and `deliveries/` folders under the graph root on first write. Optionally backfill `project:` on existing service entities by hand. Rollback: revert the reference docs; new notes are plain markdown and harmless if unused.

## Open Questions

- ~~Does `iris-service` already produce per-project notes?~~ Answered 2026-09-15: no, phase 1 is read-only (see D7). Open: when Iris phase 2 lands, should it write typed `delivery`/`decision` notes?
- Should `project` entities carry a `repos[]` list so recall can map a repo path to a project without the binding? (Leaning yes, as an optional field.)
- Recall threshold 3 is a starting point; tune from the eval fixture and the first real items.
