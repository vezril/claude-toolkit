## ADDED Requirements

### Requirement: Implementation marks the change's tasks complete
`close-openspec-change.py` SHALL tick the items in the change's `tasks.md` that
`implementation.json` records as done, matching by task id, and SHALL leave untouched any item
the implementation does not claim. It SHALL report which items it ticked and which it left.

#### Scenario: Shipped tasks are ticked

- **GIVEN** `implementation.json` records tasks `T1` and `T2` as done
- **WHEN** the closure script runs
- **THEN** those two items are checked in `tasks.md` and the rest are unchanged

#### Scenario: An unclaimed task stays open

- **GIVEN** `tasks.md` lists `T3` and `implementation.json` does not mention it
- **THEN** `T3` remains unchecked and is named in the report as left open

#### Scenario: A task id the markdown does not have

- **GIVEN** `implementation.json` claims a task id absent from `tasks.md`
- **THEN** the script exits non-zero naming the unknown id rather than silently ticking nothing

### Requirement: Archiving is human-only
The closure script SHALL NOT run `openspec archive`. It SHALL print the exact command for a
human to run. An agent attempting to archive SHALL be blocked by the enforcement hook.

#### Scenario: The script stops at the instruction

- **WHEN** the closure script completes
- **THEN** `openspec/changes/<change-id>/` still exists, nothing has been promoted into `openspec/specs/`, and the archive command is printed

#### Scenario: An agent cannot archive

- **WHEN** an agent attempts to run the archive command
- **THEN** the enforcement hook denies it

### Requirement: A change directory is never abandoned silently
`flow-status.py` SHALL report, for an item whose `proposal.json` names a change, whether that
change's `tasks.md` has unticked items outstanding, so a run that ends with work unmarked is
visible rather than implied complete.

#### Scenario: Outstanding tasks are surfaced

- **GIVEN** an item at the report step whose change has unticked tasks
- **THEN** the status output names the change and the count of items still open

#### Scenario: A fully ticked change reports clean

- **GIVEN** every item in the change's `tasks.md` is ticked
- **THEN** the status output says so and names the archive command as the remaining human step
