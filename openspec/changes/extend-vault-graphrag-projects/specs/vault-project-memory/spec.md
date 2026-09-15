## ADDED Requirements

### Requirement: Project entity and project scoping
The schema SHALL add `project` to the entity `entity_type` vocabulary. Incident, lesson, decision and delivery notes, and service/component entities, SHALL accept an optional single `project` wikilink field. Projects SHALL NOT be modeled as folders or separate graphs.

#### Scenario: Service belongs to a project
- **WHEN** the entity note `demeter-service` has `project: "[[olympus]]"`
- **THEN** it is a valid entity note and `olympus` resolves to a note with `type: entity` and `entity_type: project`

#### Scenario: Existing notes stay valid
- **WHEN** an incident note has no `project` field
- **THEN** it remains schema-valid and incident recall treats it exactly as before

### Requirement: Decision note type
The schema SHALL define `type: decision` notes in `decisions/` with a kebab-case basename (≤6 words) and frontmatter `title`, `date`, `status` (`proposed | accepted | superseded`), `project`, `services`, `domains`, one-line `context`, `decision` and `consequences`, and `refs`. A `superseded` decision SHALL carry `superseded_by` linking to its replacement. Decision history SHALL be changed by superseding, never by rewriting the decision field.

#### Scenario: Superseding a decision
- **WHEN** a new accepted decision replaces `rest-bff-for-consoles`
- **THEN** `rest-bff-for-consoles` gets `status: superseded` and `superseded_by` pointing to the new note, and its `decision` line is unchanged

#### Scenario: Superseded without replacement is invalid
- **WHEN** a decision note has `status: superseded` and no `superseded_by`
- **THEN** it fails schema conformance

### Requirement: Decision notes point to authoritative sources
A decision note SHALL include at least one `refs` entry (ADR path, OpenSpec change, or PR) when an authoritative source exists, and SHALL NOT copy that source's body content.

#### Scenario: Minted from an OpenSpec design
- **WHEN** the update operation mints a decision recorded in an accepted OpenSpec change's `design.md`
- **THEN** the note's `refs` includes that change and its body is at most a short summary pointing to it

### Requirement: Delivery note type
The schema SHALL define `type: delivery` notes in `deliveries/`, keyed by tracker item key, with frontmatter `item`, `kind` (`feature | bug | task`), `title`, `date`, `status` (`delivered | in-review | punched-out | abandoned`), `project`, `services`, `domains`, `decisions`, `patterns`, one-line `goal`, `approach` and `outcome`, and `refs`. When the basename collides with an existing note, the delivery note SHALL be named `<KEY> (delivery)` and list the key in `aliases`.

#### Scenario: Key collision with an incident
- **WHEN** a delivery update runs for `DEM-7` and `incidents/DEM-7.md` already exists
- **THEN** the delivery note is created as `deliveries/DEM-7 (delivery).md` with `aliases: [DEM-7]` and `item: DEM-7`

### Requirement: Additive optional fields on lessons
Lesson notes SHALL accept optional `project` and `domains` fields, with no new required fields on any existing type.

#### Scenario: Lesson scoped to domains
- **WHEN** a lesson note declares `domains: [infra]`
- **THEN** it is schema-valid and eligible for domain-weighted delivery recall

### Requirement: Delivery update operation
After a delivery-flow item ends, the update operation SHALL:
- upsert the delivery note by item key (never creating a duplicate);
- create stubs for missing project and service entities from the binding vocabulary;
- link existing decisions;
- mint new decision notes only for decisions recorded in the item's accepted design or ADR files;
- write the receipt `vault-updated.md` in the calling pipeline's directory.

#### Scenario: Re-run updates in place
- **WHEN** the delivery update runs twice for `DEM-12`, the second time with status `delivered` instead of `in-review`
- **THEN** exactly one delivery note for `DEM-12` exists and its `status` is `delivered`

#### Scenario: No inferred decisions
- **WHEN** the item's artifacts discuss an approach that no accepted design or ADR records as a decision
- **THEN** no new decision note is minted

### Requirement: Backward compatibility with defect-flow bindings
The change SHALL NOT alter incident recall's algorithm or the `prior-incidents.md` contract. The private defect-flow `vault-recall` and `vault-update` eval suites SHALL pass without edits after the change.

#### Scenario: Regression suites pass
- **WHEN** the private repo's `evals/vault-recall` and `evals/vault-update` suites run against the updated public skill
- **THEN** both pass with no change to their configs or fixtures
