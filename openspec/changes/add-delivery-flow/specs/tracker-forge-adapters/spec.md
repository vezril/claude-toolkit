## ADDED Requirements

### Requirement: Adapter CLI contract
Every tracker adapter SHALL implement `fetch <key>`, `comment <key> --body-file <path>`, `transition <key> <state>` and `related <key>`. Every forge adapter SHALL implement `open-pr --head --base --title --body-file` and `ci-status <ref>`. All subcommands SHALL emit JSON on stdout and use exit codes 0 (ok), 2 (usage/contract error) and 3 (remote or auth failure, with a remediation message on stderr).

#### Scenario: Auth failure is explicit
- **WHEN** `github-issues fetch 42` runs with `gh` unauthenticated
- **THEN** the adapter exits 3 and prints the `gh auth login` remediation, and emits no partial `item.json`

### Requirement: Normalized item format
`fetch` SHALL emit an item object with at least `key`, `title`, `body`, `type_hint` (or null), `labels`, `status`, `url`, `links` and `source` (adapter kind). Identifier values SHALL be strings. The flow SHALL write it verbatim as `item.json`, and `validate-artifact.py item` SHALL verify the shape.

#### Scenario: GitHub issue normalizes
- **WHEN** `github-issues fetch 42` reads an issue labeled `bug`
- **THEN** the emitted item has `key: "42"`, `type_hint: "bug"`, `source: "github-issues"`, and passes `validate-artifact.py item`

### Requirement: Adapters perform no LLM calls
Adapters SHALL be deterministic scripts. Any summarizing of item content SHALL happen in a separate LLM step that reads `item.json`.

#### Scenario: Same input, same output
- **WHEN** `local-markdown fetch DEM-3` runs twice against an unchanged backlog file
- **THEN** both runs emit byte-identical JSON

### Requirement: Local markdown backlog adapter
The `local-markdown` adapter SHALL treat each `### <KEY>: <title>` heading in the configured backlog file as an item, reading `Type:` and `Status:` lines beneath it. `comment` SHALL append a dated comment block under the item, and `transition` SHALL rewrite its `Status:` line. It SHALL provide `import` to convert an unkeyed bullet backlog into keyed items once, writing a new file rather than rewriting the source in place.

#### Scenario: Import leaves the source untouched
- **WHEN** `local-markdown import "+/Feature for Olympus.md" --prefix OLY --out backlog.md` runs
- **THEN** `backlog.md` contains one keyed item per bullet under its service heading and the source file is unchanged

### Requirement: Outward adapter actions refuse while a punch-out is open
Adapter subcommands that act outwardly (`open-pr`, `comment`, `transition`) SHALL exit 2 without making a remote call when the item has an unresolved punch-out, or when posting to a tracker configured `external: true` without a resolved decision for that post, independently of the PreToolUse hook.

#### Scenario: Adapter refuses during a punch-out
- **WHEN** `github-pr open-pr` is invoked for DEM-12 while `delivery/DEM-12/punch-out-1.md` has no matching decision
- **THEN** the adapter exits 2 naming the open punch-out and makes no remote call
