## ADDED Requirements

### Requirement: An unreachable vault fails; an empty one does not
Recall SHALL check the graph root is present, a directory, and readable before scanning. An
unreachable vault SHALL exit 3, write no artifact, and report the path it tried. A reachable
vault with no candidate above the threshold SHALL exit 0 and write an artifact with
`matched: false` and a populated coverage section.

#### Scenario: An unmounted volume is a failure, not an empty result

- **GIVEN** `vault.path` points at a volume that is not mounted
- **WHEN** recall runs
- **THEN** it exits 3 naming the path, writes no `project-context.json`, and the flow does not advance

#### Scenario: A cold start is not a failure

- **GIVEN** a reachable graph root containing no decision, delivery, lesson or pattern notes
- **WHEN** recall runs
- **THEN** it exits 0 and writes an artifact recording `matched: false` and what was scanned

#### Scenario: The two are distinguishable in the trace

- **WHEN** the trace is read for a run of each kind
- **THEN** the unreachable run shows the step failing with no artifact, and the cold-start run shows a successful step whose artifact reports nothing matched

#### Scenario: A file where the graph root should be

- **GIVEN** `vault.graph_root` resolves to a regular file
- **THEN** recall exits 3 rather than treating it as empty

### Requirement: Recall reports the clone's sync state and never reaches the network
The vault SHALL be a local git work tree, with the canonical bare repository hosted remotely.
Recall SHALL report, in `project-context.json` and the trace, the clone's `head`, `head_date`,
`dirty`, `upstream`, `remote`, `ahead`, `behind`, `last_sync` and `days_since_sync`, and SHALL
set `stale` when the days since the last fetch exceed `punch_out.vault_staleness_days`
(default 14; `null` disables the check). Staleness SHALL be measured from the last **fetch**,
not the last push. Recall SHALL make no network call of any kind. A vault that is not a git
work tree SHALL be reported as `tracked: false` with a note, and SHALL NOT be reported stale.

#### Scenario: A stale clone says so before it says anything else

- **GIVEN** a vault clone whose last fetch was 40 days ago and a ceiling of 14
- **WHEN** recall runs
- **THEN** the artifact sets `stale: true` with `days_since_sync` of at least 39, and the rendered markdown opens with a stale-memory warning above any recalled content

#### Scenario: A push is not a sync

- **GIVEN** a clone that pushed one hour ago but has never fetched
- **WHEN** recall runs
- **THEN** `last_sync` is null and a note records that whether another machine holds newer decisions is unknown, because a push sends without learning

#### Scenario: Unpushed work is reported as not yet durable

- **GIVEN** a clone with two local commits not on the remote
- **THEN** `ahead` is 2 and a note says they have not reached the remote

#### Scenario: No upstream is unknown, not agreement

- **GIVEN** a clone whose branch tracks no upstream
- **THEN** `ahead` and `behind` are null rather than 0, because reporting 0 would claim an agreement that was never observed

#### Scenario: Recall does not depend on the remote being up

- **WHEN** the remote host is unreachable
- **THEN** recall still exits 0, scans the local clone, and reports its sync state from local evidence

### Requirement: The binding locates the graph
`.delivery-flow.yaml` SHALL accept `vault.binding` (the project name), `vault.path` (the local
clone), `vault.graph_root` (the path within it), `vault.backend` (`filesystem`, with `iris`
reserved) and `vault.remote` (the canonical bare repository, informational). A binding naming a
backend other than `filesystem` SHALL exit 2 with a clear not-implemented message. Where
`vault.remote` disagrees with git's `origin`, recall SHALL report it rather than pick one. All
keys SHALL be documented in `skills/delivery-flow/references/config.md`.

#### Scenario: An unimplemented backend is refused clearly

- **GIVEN** `vault.backend: iris`
- **THEN** recall exits 2 stating that only the filesystem backend is implemented

#### Scenario: No binding skips the step

- **GIVEN** `vault.binding: null`
- **THEN** the vault steps are skipped as before and recall is never invoked

### Requirement: The scaffold can create the clone, and never pushes
`scaffold-vault.py --create` SHALL create the vault directory when it is absent; without that
flag a missing vault SHALL remain exit 3, because creating one where a mount was expected
produces two divergent vaults with no way to tell which is authoritative. `--git` SHALL make the
vault a git work tree with an initial commit and a `.gitignore` covering Obsidian's volatile
state, and `--remote <url>` SHALL set `origin` and imply `--git`. Neither SHALL push, and
neither SHALL overwrite an existing `.gitignore` or an existing `origin` that disagrees — a
disagreement SHALL be reported for a human to settle.

#### Scenario: A missing vault is still a failure by default

- **WHEN** the configured vault path does not exist and `--create` is absent
- **THEN** the scaffold exits 3 and creates nothing

#### Scenario: Creating the clone is one command

- **WHEN** `scaffold-vault.py --create --remote <url>` runs against an absent vault
- **THEN** the directory, the graph, a `.gitignore` and an initial commit exist, `origin` is set, and nothing was pushed

#### Scenario: Obsidian's churn is not tracked

- **WHEN** the scaffold writes `.gitignore`
- **THEN** it excludes `.obsidian/workspace.json` and the other volatile files, so `dirty` reports uncommitted notes rather than pane movements

#### Scenario: An existing origin is not silently replaced

- **GIVEN** `origin` already set to a different URL
- **WHEN** the scaffold runs with `--remote`
- **THEN** it leaves `origin` alone and reports the disagreement

### Requirement: The scaffold is additive and confined
`scaffold-vault.py` SHALL create the graph root, its folders, one `project` entity for the
binding, and the note templates. It SHALL leave every existing file byte-identical, SHALL report
what it skipped, SHALL be idempotent, and SHALL refuse to write any path that does not resolve
inside `vault.path`.

#### Scenario: Existing notes are untouched

- **GIVEN** a vault holding unrelated notes at its root
- **WHEN** the scaffold runs
- **THEN** those files are byte-identical afterwards and are reported as left alone

#### Scenario: Running it twice changes nothing

- **WHEN** the scaffold runs a second time
- **THEN** it writes nothing and reports every item as already present

#### Scenario: A path escaping the vault is refused

- **GIVEN** a graph root configured as `../elsewhere`
- **THEN** the scaffold exits 2 writing nothing
