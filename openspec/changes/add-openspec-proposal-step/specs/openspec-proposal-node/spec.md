## ADDED Requirements

### Requirement: The propose step produces an OpenSpec change and a structured contract
The `propose` step SHALL create `openspec/changes/<change-id>/` containing `proposal.md`,
`design.md`, at least one delta spec under `specs/`, and `tasks.md`, and SHALL write
`delivery/<ITEM-KEY>/proposal.json` conforming to `schemas/proposal.schema.json` together with
its sentinel. The step SHALL replace `solutioning`, and `spec-ready.json` SHALL no longer appear
in the routing table.

#### Scenario: A proposal produces both artifacts

- **WHEN** the propose step runs for an item whose breakdown has been challenged
- **THEN** the change directory holds the four artifacts, and `proposal.json` plus its sentinel exist

#### Scenario: Prose alone does not satisfy the step

- **WHEN** the change directory exists but no `proposal.json` is written
- **THEN** the step has not produced its artifact and the flow does not advance

### Requirement: The proposal edge checks the JSON against the change directory
The edge for `proposal.json` SHALL verify that the JSON and the change directory describe the
same change, and SHALL record any failure as an edge failure reported to the model. The checks
are enumerated in the scenarios below.

#### Scenario: The change directory holds its four artifacts

- **WHEN** the edge runs
- **THEN** it verifies `proposal.md`, `design.md`, `tasks.md` and at least one delta spec exist

#### Scenario: Task ids close in both directions

- **WHEN** the edge runs
- **THEN** it verifies every task id in `proposal.json` appears in `tasks.md` and the reverse

#### Scenario: Named specs and task paths are checked

- **WHEN** the edge runs
- **THEN** it verifies every named delta spec exists on disk, every task file path resolves inside the repository, and no task has an empty description or file list

#### Scenario: A task in the JSON but not the markdown

- **GIVEN** `proposal.json` lists task `T3` and `tasks.md` does not
- **THEN** the edge fails naming `T3` and the direction of the mismatch

#### Scenario: A task in the markdown but not the JSON

- **GIVEN** `tasks.md` lists a task absent from `proposal.json`
- **THEN** the edge fails, because a contract that omits planned work understates the change

#### Scenario: A named spec that does not exist

- **GIVEN** `proposal.json` names a delta spec with no file on disk
- **THEN** the edge fails naming the missing spec path

#### Scenario: A file path outside the repository

- **GIVEN** a task whose files include an absolute path outside the repo, or one escaping it with `..`
- **THEN** the edge fails naming that path

#### Scenario: A missing change directory

- **GIVEN** `proposal.json` names a `change_id` with no directory under `openspec/changes/`
- **THEN** the edge fails naming the expected path

### Requirement: `openspec validate` is an additional layer, and its absence is visible
When the `openspec` CLI is on PATH the edge SHALL additionally run `openspec validate <change-id>
--strict` and record its result. When the CLI is absent the edge SHALL record that the layer was
skipped and SHALL NOT fail for its absence. The edge's own deterministic checks SHALL NOT depend
on the CLI.

#### Scenario: CLI present and the change is invalid

- **GIVEN** `openspec` is on PATH and reports a non-zero exit for the change
- **THEN** the edge fails and the trace carries the validator's output

#### Scenario: CLI absent

- **GIVEN** `openspec` is not installed
- **WHEN** the edge runs
- **THEN** the deterministic checks still run, the edge passes on their result, and the trace records the layer as skipped rather than passed

### Requirement: The brief carries the proposed change
`summary.md` SHALL gain a "What will change" section rendered from `proposal.json`: the change
id, the task count, the number and names of files touched, the dependencies added, and the flags
raised. Its coverage edge SHALL additionally verify that every task id in `proposal.json` appears
in the brief. Where no proposal exists the section SHALL be present and state that no change has
been proposed, keeping the brief's shape identical across profiles.

#### Scenario: Every task reaches the page

- **GIVEN** a proposal with 6 tasks
- **WHEN** the brief renders and its edge runs
- **THEN** all 6 task ids appear in the brief and the edge passes

#### Scenario: A brief that hides half the change fails

- **GIVEN** a proposal with 6 tasks and a brief naming 3
- **THEN** the edge fails naming the omitted task ids

#### Scenario: The triage profile's brief is unchanged

- **GIVEN** an item run under `profile: triage`, where no proposal exists
- **THEN** the "What will change" section states that no change has been proposed, and every other section is byte-identical to its output before this change

### Requirement: The propose step is declared uncertified
`propose` SHALL be listed in `allow_uncertified` in the repository's configuration until it
carries a `prompt-edd` package. Every run SHALL record `certified: false` in the trace, and such
runs SHALL be excluded from the certified-only end-to-end rate.

#### Scenario: An uncertified step runs but does not count

- **WHEN** the propose step runs under `allow_uncertified`
- **THEN** the trace records `certified: false` and `delivery-report.py` excludes the item from the certified-only rate while still reporting it in the profile's own rate

#### Scenario: Removing the declaration blocks the step

- **GIVEN** `propose` is removed from `allow_uncertified` and has no registry entry
- **THEN** the step is blocked by the certification check rather than running uncertified
