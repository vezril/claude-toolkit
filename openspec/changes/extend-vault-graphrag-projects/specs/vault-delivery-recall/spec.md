## ADDED Requirements

### Requirement: Two call points
Delivery recall SHALL support a `solutioning` call (inputs: `item.json`, `triage.md`, binding) and an `implementation` call (inputs: one story file plus the same). Both SHALL emit `project-context.md` in the calling pipeline's directory, the implementation call suffixed per story (`project-context-<story>.md`).

#### Scenario: Implementation call per story
- **WHEN** recall runs in `implementation` mode for story 2.1 of DEM-12
- **THEN** it writes `delivery/DEM-12/project-context-2.1.md` and does not overwrite `project-context.md`

### Requirement: Deterministic project-weighted scoring
Recall SHALL scan `decisions/`, `deliveries/`, `lessons/` and `patterns/` under the graph root using plain-text tooling and frontmatter only. It SHALL score each candidate as 3 per same project, plus 3 per shared service/component link, plus 2 per shared domain (3 in implementation mode), plus 1 per keyword hit in payload lines. It SHALL drop candidates scoring below 3, break ties by date (newest first), and cap results at 5 decisions, 5 deliveries, 3 lessons and 3 patterns.

#### Scenario: Same-project decision outranks a cross-project one
- **WHEN** two accepted decisions share one keyword with the item, one in the item's project and one in another project with no shared services
- **THEN** the same-project decision scores 4 and appears, and the cross-project one scores 1 and is dropped

#### Scenario: Cross-project hit through a shared service
- **WHEN** a delivery in another project links a service the item also touches and matches one keyword
- **THEN** it scores 4 and appears under Related deliveries

### Requirement: Only accepted decisions are presented as in force
Recall SHALL list only `accepted` decisions under "Decisions in force". Superseded decisions that would have matched SHALL appear only in Search coverage, naming their replacement.

#### Scenario: Superseded decision redirected
- **WHEN** a matching decision has `status: superseded` and `superseded_by: [[grpc-bff-for-operator-consoles]]`
- **THEN** it is absent from Decisions in force, and Search coverage lists it with its replacement

### Requirement: Output format
`project-context.md` SHALL be at most 80 lines with sections: Decisions in force, Related deliveries, Lessons, Patterns, and a mandatory Search coverage section (entities, keywords and domains used, notes scanned per folder, candidates dropped, superseded decisions skipped). Each match SHALL show its payload lines verbatim from frontmatter plus its wikilink, and SHALL NOT include note body text.

#### Scenario: Payload lines only
- **WHEN** a matching delivery note has a long body narrative
- **THEN** the output shows only its `goal`, `approach` and `outcome` lines and its `[[link]]`

### Requirement: Honest empty result
When no candidate reaches the threshold, recall SHALL still write the output file with the Search coverage section and a single line stating that nothing in the vault matched this project context.

#### Scenario: Empty project
- **WHEN** recall runs for a project with no decision, delivery or lesson notes
- **THEN** the file contains the coverage section and the one-line empty statement, and no invented matches

### Requirement: Recall reports facts, not recommendations
Recall output SHALL contain graph facts only and SHALL NOT suggest designs, fixes or conclusions.

#### Scenario: No advice in output
- **WHEN** recall finds an accepted decision relevant to the item
- **THEN** the output lists the decision's payload lines and does not state that the item should follow or change it

### Requirement: Eval suite with a synthetic mini-vault
The change SHALL ship `evals/vault-delivery-recall/` with a synthetic mini-vault fixture containing:
- one project with two services;
- accepted and superseded decisions;
- deliveries;
- lessons with domains;
- a cross-project decoy.

It SHALL use deterministic asserts on section presence, match membership and exclusion, and the ≤80-line cap.

#### Scenario: Decoy excluded
- **WHEN** the suite runs recall for an item in the fixture project
- **THEN** the assert confirms the cross-project decoy (no shared services, one keyword) is absent and the superseded decision appears only in coverage
