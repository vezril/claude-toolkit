# toolkit-archive

## ADDED Requirements

### Requirement: Archive a retired component with its documentation

The skill SHALL move a retired component's files verbatim into `archive/<name>/` and write an accompanying `RETIRED.md` recording what the component was, why it was retired, what replaced it (or explicitly nothing), and the absolute retirement date.

#### Scenario: Retire a skill with a successor

- **GIVEN** the skill `new-scala-service` exists with SKILL.md and bundled scripts
- **WHEN** toolkit-archive is invoked with `skills/new-scala-service` and successor `new-scala-pekko-service`
- **THEN** all files move unchanged to `archive/new-scala-service/`
- **AND** `archive/new-scala-service/RETIRED.md` names the successor and the retirement date

#### Scenario: Missing rationale is asked, not invented

- **WHEN** toolkit-archive is invoked without a retirement reason
- **THEN** the skill asks the human for the reason rather than fabricating one

### Requirement: Archived components leave the active surface

The skill SHALL remove the archived component from every active surface: the repo indexes (`README.md` skill/workflow entries) and any installed copies under `~/.claude/` — and SHALL report each removal.

#### Scenario: Installed copy removed

- **GIVEN** the component is also installed at `~/.claude/skills/<name>/`
- **WHEN** it is archived
- **THEN** the installed copy is deleted and the deletion is reported

### Requirement: Refuse to archive a still-referenced component

The skill SHALL search the repo's active components for references to the component being archived and SHALL stop and report the referrers instead of archiving when any exist.

#### Scenario: A workflow still calls the skill

- **GIVEN** `workflows/x.js` references skill `foo`
- **WHEN** toolkit-archive is invoked for `skills/foo`
- **THEN** nothing is moved and `workflows/x.js` is reported as a blocking referrer

### Requirement: No commit

The skill SHALL leave all changes uncommitted in the working tree; shipping is git-ship's responsibility.

#### Scenario: Archive then ship separately

- **WHEN** toolkit-archive completes
- **THEN** `git status` shows the moves and edits unstaged/uncommitted
