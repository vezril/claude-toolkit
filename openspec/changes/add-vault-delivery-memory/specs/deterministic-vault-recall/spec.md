## ADDED Requirements

### Requirement: Recall is a deterministic script, not a node
Delivery recall SHALL be implemented as a script containing no model invocation, and SHALL NOT
appear in `skills/delivery-flow/steps.yaml`. Two runs over an unchanged vault SHALL produce
byte-identical output. It SHALL read frontmatter only and SHALL NOT read note body text.

#### Scenario: Reruns are identical

- **WHEN** recall runs twice over the same vault and the same item
- **THEN** both `project-context.json` files are byte-identical

#### Scenario: Body text never reaches the output

- **GIVEN** a matching delivery note with a long body narrative
- **THEN** the output carries its `goal`, `approach` and `outcome` lines and its wikilink, and no body text

#### Scenario: Not a certified step

- **WHEN** `check-certification.py --all` runs
- **THEN** `project-memory` is not reported as an uncertified step, because it is a script step

### Requirement: The specified scoring, thresholds and caps
Each candidate SHALL score 3 per same project, 3 per shared service or component link, 2 per
shared domain in solutioning mode and 3 in implementation mode, and 1 per keyword hit in its
payload lines. Candidates scoring below 3 SHALL be dropped. Ties SHALL break by date, newest
first. Results SHALL cap at 5 decisions, 5 deliveries, 3 lessons and 3 patterns.

#### Scenario: Same-project decision outranks a cross-project one

- **GIVEN** two accepted decisions sharing one keyword with the item, one in the item's project and one in another project with no shared services
- **THEN** the same-project decision scores 4 and appears, and the cross-project one scores 1 and is dropped

#### Scenario: Cross-project hit through a shared service

- **GIVEN** a delivery in another project linking a service the item also touches, matching one keyword
- **THEN** it scores 4 and appears under related deliveries

#### Scenario: Caps are applied after sorting

- **GIVEN** eight decisions above the threshold
- **THEN** the five highest-scoring appear and the coverage section records three dropped to the cap

#### Scenario: Domains weigh more during implementation

- **GIVEN** a lesson sharing one domain and no keywords
- **THEN** it scores 2 and is dropped in solutioning mode, and scores 3 and is kept in implementation mode

### Requirement: Keyword extraction is defined
Keywords SHALL be derived from the item's title and summary: lowercased, split on
non-alphanumeric characters, with a documented stop list applied and tokens shorter than four
characters dropped, deduplicated. The set used SHALL appear in the output's coverage section.

#### Scenario: The keyword set is reported

- **WHEN** recall runs
- **THEN** the coverage section lists the exact keywords used

#### Scenario: Short and stopped tokens are excluded

- **GIVEN** a title "Add the DLQ retry cap"
- **THEN** `the` and `add` are excluded and `retry` is included

### Requirement: Only accepted decisions are in force
Only decisions with `status: accepted` SHALL appear under decisions in force. A superseded
decision that would otherwise have matched SHALL appear only in the coverage section, naming its
replacement.

#### Scenario: Superseded decision redirected

- **GIVEN** a matching decision with `status: superseded` and a `superseded_by` link
- **THEN** it is absent from decisions in force and the coverage section lists it with its replacement

### Requirement: Both call points
Recall SHALL support a `solutioning` call keyed on the item and an `implementation` call keyed on
a story, writing `project-context.json` and `project-context-<story>.json` respectively. The
implementation call SHALL NOT overwrite the solutioning output.

#### Scenario: Per-story output

- **WHEN** recall runs in implementation mode for story S1 of DEM-12
- **THEN** it writes `project-context-S1.json` and leaves `project-context.json` untouched

### Requirement: The output is a contract plus a rendering
Recall SHALL write `project-context.json` conforming to `schemas/project-context.schema.json`
with its sentinel, and an equivalent `project-context.md` of at most 80 lines for a human. The
JSON SHALL be what downstream steps consume.

#### Scenario: The markdown stays within its cap

- **WHEN** recall writes its output
- **THEN** `project-context.md` is at most 80 lines

#### Scenario: No step consumes the markdown

- **WHEN** the schemas and step inputs are inspected
- **THEN** no step declares `project-context.md` as an input

### Requirement: Facts, not recommendations
The output SHALL contain graph facts only, and SHALL NOT state what the item should do. Because
the producer is a script with no generative step, this holds by construction.

#### Scenario: An accepted decision is reported without advice

- **GIVEN** recall finds an accepted decision relevant to the item
- **THEN** the output lists its payload lines and does not say the item should follow or change it
