## ADDED Requirements

### Requirement: The story contract is markdown governed by one normative reference

The contract for a story SHALL be the markdown format pinned by
`skills/spec-driven-development/references/story-schema.md` and enforced by
`scripts/lint-story.py`. There SHALL NOT be a second, schema-backed story format rendered
alongside it.

#### Scenario: The retired alternative stays retired

- **GIVEN** this change originally proposed a `story.json` rendered from `breakdown.json` by
  `render-stories.py`, which froze a story set before the challenge findings that `propose`
  resolves — on AN-3631 `propose` folded S5 into S1 and dropped S6 while the rendered six still
  listed both
- **WHEN** the story contract is read
- **THEN** the renderer is absent, `schemas/story.schema.json` is absent, and no mirror offers
  `story.json` as a format a writer could target

#### Scenario: One story format, not two

- **GIVEN** a story set produced for a change
- **WHEN** `test-writer` or `implementer` is delegated a story
- **THEN** it is handed the markdown story governed by `story-schema.md`, and no `story.json` is
  rendered, parsed or required

#### Scenario: A malformed story fails the gate

- **GIVEN** a story file that violates `story-schema.md`
- **WHEN** the readiness edge check runs
- **THEN** `lint-story.py` exits non-zero, the edge records the failure naming the violated rule,
  and the orchestrator does not advance

### Requirement: The handoff into implementation is the OpenSpec change

The artifact that carries readiness into implementation SHALL be the OpenSpec change — its
`proposal.md` and `tasks.md`, with `tasks.md` referencing the story files. No step SHALL produce
a second decomposition of work already decomposed and challenged upstream.

#### Scenario: Work arriving through delivery-flow is not re-decomposed

- **GIVEN** a work item whose `breakdown.json` has been attacked by `challenge-breakdown`
- **WHEN** the change is proposed
- **THEN** `proposal.md` and `tasks.md` are the handoff, and no node re-decomposes the breakdown
  into a parallel story set that could disagree with it

#### Scenario: Work without a tracker item still has a path

- **GIVEN** a requirement written directly into the repository with no `breakdown.json`
- **WHEN** the readiness segment runs
- **THEN** `story-planner` produces the story set from the PRD and architecture

### Requirement: Semantic checks a schema cannot express are enforced

`lint-story.py` SHALL keep its name and CLI and SHALL enforce: the required section structure,
Given/When/Then grammar on acceptance criteria, task-to-AC closure in both directions,
resolvable `[Source: path#anchor]` references, and FR/CAP traceability. A non-zero exit SHALL
fail the readiness edge and return the report to the story-planner.

#### Scenario: Substance stays with the reviewer

- **GIVEN** a vacuous but well-formed criterion ("given the system, when used, then it works")
- **WHEN** `lint-story.py` runs
- **THEN** it passes, by design, and catching it is the reviewer node's job

#### Scenario: Well-formed but semantically incomplete

- **GIVEN** a story whose structure is complete but whose task references no acceptance criterion
- **WHEN** `lint-story.py` runs
- **THEN** it exits non-zero naming the unreferenced task

#### Scenario: Bounded rewrite loop

- **GIVEN** a story set failing the lint
- **WHEN** the gate has returned to the story-planner three times without passing
- **THEN** the run escalates to a human rather than looping further

### Requirement: The story-schema reference and the linter change together

`skills/spec-driven-development/references/story-schema.md` and `scripts/lint-story.py` SHALL be
updated in the same change, as the normative format and its enforcement. Every other file that
narrates the gate's mechanism — `skills/spec-driven-development/SKILL.md`,
`agents/story-planner.md` and the sdlc mirrors — SHALL be updated with them, and a test SHALL
enforce that rather than a review.

#### Scenario: Drift is not permitted

- **GIVEN** a change to the normative story format or to who runs the linter
- **WHEN** it lands without the reference, the linter and the narrating mirrors agreeing
- **THEN** `tests/workflow/test_documentation_mirrors.py` fails
