## ADDED Requirements

### Requirement: A story consumed by a node is schema-backed data

The artifact a downstream node consumes SHALL be `story.json`, valid against
`schemas/story.schema.json`. Markdown with agreed section headings SHALL NOT be the contract
between nodes. `story.md` SHALL be generated from `story.json` for human readers and SHALL NOT be
parsed by any node or check.

#### Scenario: A node consumes the data, not the prose

- **GIVEN** a story set with both `story.json` and a rendered `story.md`
- **WHEN** `test-writer` or `implementer` is delegated the story
- **THEN** it is handed `story.json`, and no step parses `story.md`

#### Scenario: A malformed story fails the schema

- **GIVEN** a `story.json` missing a required field
- **WHEN** the readiness edge runs
- **THEN** it records a failed verdict naming the schema violation, and the orchestrator does not
  advance

### Requirement: The renderer and the checker share one definition

The story template and its coverage checks SHALL live in one module imported by both the renderer
and the edge check, so a renderer and a checker cannot disagree about what a story is.

#### Scenario: Renderer and checker agree by construction

- **GIVEN** a change to what counts as a complete story
- **WHEN** the shared module is edited
- **THEN** both the rendered `story.md` and the edge check reflect it without either being
  edited separately

### Requirement: Semantic checks a schema cannot express are still enforced

`lint-story.py` SHALL keep its name and CLI and SHALL enforce, beyond schema validity:
Given/When/Then grammar on acceptance criteria, task-to-AC closure, resolvable references, and
FR/CAP traceability. A non-zero exit SHALL short-circuit the readiness gate back to the
story-planner, bounded to roughly three iterations before escalating to a human.

#### Scenario: Schema-valid but semantically incomplete

- **GIVEN** a `story.json` that validates against the schema but has a task referencing no
  acceptance criterion
- **WHEN** `lint-story.py` runs
- **THEN** it exits non-zero naming the unreferenced task

#### Scenario: Bounded rewrite loop

- **GIVEN** a story set failing the lint
- **WHEN** the gate has short-circuited to the story-planner three times without passing
- **THEN** the run escalates to a human rather than looping further

### Requirement: Existing markdown stories are migrated, not silently broken

A one-shot migration SHALL convert existing markdown story files to `story.json` and SHALL report
every file it could not convert rather than failing silently or producing a partial artifact.

#### Scenario: Unconvertible story is reported

- **GIVEN** a markdown story the migration cannot parse into the schema
- **WHEN** the migration runs
- **THEN** that file is listed in the report as unconverted and no `story.json` is written for it

### Requirement: The story-schema reference and the linter change together

`skills/spec-driven-development/references/story-schema.md`, `schemas/story.schema.json` and
`scripts/lint-story.py` SHALL be updated in the same change, as the normative format and its
enforcement.

#### Scenario: Drift is not permitted

- **GIVEN** a change to the normative story format
- **WHEN** it lands without a corresponding change to the schema or the linter
- **THEN** the change is incomplete

### Requirement: The story set is rendered from the challenged breakdown, not re-decomposed
Where a work item arrives through `delivery-flow`, `story.json` SHALL be rendered
deterministically from `breakdown.json` by a script, one story per
`epics[].stories[]`, carrying `id`, `statement`, `domains` and `acceptance_criteria` across
unchanged. No node SHALL re-decompose a breakdown that `challenge-breakdown` has already
attacked. Each rendered story SHALL carry a `sources` array naming the artifacts it derives
from, so an implementer reads the context rather than a node's summary of it. The renderer and
the story validator SHALL share one module, so they cannot disagree about what a story is.
`story-planner` remains the entry point for work that does not arrive through `delivery-flow`.

#### Scenario: Every breakdown story becomes exactly one story

- **GIVEN** a `breakdown.json` with 1 epic, 3 stories and 6 acceptance criteria
- **WHEN** the renderer runs
- **THEN** 3 `story.json` artifacts exist, their ids and acceptance criteria match the breakdown exactly, and none carries a criterion the breakdown did not contain

#### Scenario: The renderer invents nothing

- **WHEN** the rendered story set is compared against `breakdown.json`
- **THEN** no story, criterion or domain appears that is absent from the breakdown, and the comparison is enforced by the shared module rather than by review

#### Scenario: Sequencing is a stated gap, not a guess

- **WHEN** stories are rendered
- **THEN** they are presented in breakdown order, and the brief states that dependency ordering has not been determined — rather than implying an order the breakdown never expressed

#### Scenario: Work without a tracker item still has a path

- **GIVEN** a requirement written directly into the repository with no `breakdown.json`
- **WHEN** the implementation phase begins
- **THEN** `story-planner` produces the story set, and the rendered-from-breakdown path is not required
