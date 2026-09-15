## ADDED Requirements

### Requirement: Story Domains field
The story file format SHALL accept an optional `Domains:` line listing one or more kinds of work (comma-separated, kebab-case). `lint-story.py` SHALL accept stories without it by default and SHALL reject stories without it, or with duplicate labels, when run with `--require-domains`. The story schema reference and the linter SHALL change together.

#### Scenario: Existing stories stay valid
- **WHEN** `lint-story.py` runs without `--require-domains` on a story that has no `Domains:` line
- **THEN** the missing field produces no error

#### Scenario: Delivery-flow requires domains
- **WHEN** `lint-story.py --require-domains` runs on a story without a `Domains:` line
- **THEN** the linter exits 1 and names the missing field

### Requirement: Domains on OpenSpec task groups for the quick path
For quick-path items without story files, a `tasks.md` group heading SHALL be able to declare its kinds of work with an HTML comment (`<!-- domains: ux, contracts -->`), and `resolve-roster.py` SHALL accept a `tasks.md` path plus a group number in place of a story file.

#### Scenario: Quick path without stories
- **WHEN** `resolve-roster.py openspec/changes/add-watched-state/tasks.md --group 2` runs and group 2's heading declares `domains: backend`
- **THEN** it prints the dispatch plan for `backend`

### Requirement: Roster as data
The plugin SHALL ship a default `roster.yaml` mapping each kind of work to `architect`, `skills`, `reviewers` and optional `deploy`. A repository SHALL be able to override entries through `.delivery-flow.yaml`, where an overridden kind of work replaces the default entry wholesale.

#### Scenario: Repo override replaces an entry
- **WHEN** the default roster maps `backend` to Java skills and the repo config overrides `backend` with `skills: [scala, akka]`
- **THEN** the resolved roster's `backend` entry has exactly `skills: [scala, akka]` and inherits no default skills

### Requirement: Deterministic resolution and validation
`resolve-roster.py <story>` SHALL exit 1 when any label is not in the resolved roster, and otherwise SHALL print a JSON dispatch plan: the union of skills, the de-duplicated reviewers, the architect(s), and deploy agents for the story's kinds of work.

#### Scenario: Unknown label rejected
- **WHEN** a story declares `Domains: backend, blockchain` and the roster has no `blockchain` entry
- **THEN** `resolve-roster.py` exits 1 naming `blockchain` and prints no dispatch plan

#### Scenario: Multi-domain plan
- **WHEN** a story declares `Domains: ux, contracts`
- **THEN** the plan contains the union of both entries' skills and the de-duplicated union of their reviewers

### Requirement: Single dev pair with skill injection
Implementation SHALL use the existing test-writer and implementer agents for every kind of work, with the plan's skills injected per story. No new implementer or test-writer variants SHALL be introduced. `validate-artifact.py implementation` SHALL fail a story receipt when the traced Skill tool calls do not cover the plan's skills.

#### Scenario: Missing skill load fails validation
- **WHEN** the plan for story 2.1 requires `nextjs` and the trace shows the implementer never loaded it
- **THEN** implementation validation for story 2.1 exits non-zero naming `nextjs`

### Requirement: Evidence-based labeling
The story-planner SHALL propose `Domains:` from evidence (paths the story's tasks touch, manifests, the change's design) and record that evidence in the story's Dev Notes.

#### Scenario: Labels cite evidence
- **WHEN** the story-planner labels a story `infra`
- **THEN** the story's Dev Notes cite at least one infra path (e.g. a Helm chart or Terraform file) or design section supporting the label
