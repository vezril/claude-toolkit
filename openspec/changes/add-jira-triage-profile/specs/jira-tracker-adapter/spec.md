## ADDED Requirements

### Requirement: Jira implements the tracker adapter contract
`scripts/delivery-flow/adapters/jira.py` SHALL implement `fetch <key>`, `comment <key>
--body-file <path>`, `related <key>` and `transition <key> <state>`, emitting the same JSON
shapes as the existing adapters, and SHALL be selected by `tracker.kind: jira` in
`.delivery-flow.yaml`. It SHALL contain no LLM call of any kind, and SHALL NOT be implemented
through an MCP tool, because MCP tools are invocable only by a model and an adapter must be a
script the flow can run without one.

#### Scenario: Fetch emits a valid item

- **WHEN** `jira.py fetch ABC-123` runs against a reachable Jira
- **THEN** it prints JSON conforming to `schemas/item.schema.json` on stdout and exits 0

#### Scenario: No model in the adapter

- **WHEN** the adapter source is inspected
- **THEN** it makes HTTP calls to the Jira REST API only, with no model invocation and no MCP dependency

### Requirement: The Jira field mapping is explicit and minimal
The adapter SHALL map Jira fields onto `item.schema.json` as: `summary` → `title`, the rendered
description → `body`, issue type name → `type_hint`, status name → `status`, the browse URL →
`url`, the literal `jira` → `source`, labels and component names → `labels`, and issue links plus
the epic or parent key → `links`. Site-specific `customfield_*` values SHALL NOT be mapped in v1.
The mapping SHALL be documented in `skills/delivery-flow/references/adapters.md`.

#### Scenario: Components and labels merge into one list

- **GIVEN** a Jira issue with labels `["dlq"]` and components `["ingest"]`
- **WHEN** the adapter fetches it
- **THEN** `labels` contains both values and the item validates against its schema

#### Scenario: Custom fields are omitted, not guessed

- **GIVEN** a Jira issue carrying story points in a site-specific `customfield_*`
- **WHEN** the adapter fetches it
- **THEN** no story-point field appears in `item.json`, and the item still validates

### Requirement: A referenced GitHub issue is followed and its body inlined
Where a Jira description references a GitHub issue or pull request by URL, the adapter SHALL
fetch that issue's title and body and append them to `body` under a labelled delimiter, and
SHALL record each reference in a `references` array of `{url, repo, number, kind, title}`. The
real requirement lives at the far end of such a link, and an item whose `body` is only a URL
gives the triage node nothing to triage. Following SHALL use the same `gh` path as the GitHub
adapter, SHALL involve no model, and `--no-follow` SHALL disable it. `links` SHALL continue to
carry Jira issue keys only, so a GitHub number can never be mistaken for a tracker key.

#### Scenario: A stub ticket gains the linked issue's requirement

- **GIVEN** a Jira issue whose entire description is `github reference: https://github.com/o/r/issues/579`
- **WHEN** `jira.py fetch ABC-1` runs
- **THEN** `body` contains the Jira description followed by the referenced issue's title and body under a labelled delimiter, and `references` names that URL

#### Scenario: Referenced content is fenced and attributed

- **WHEN** a referenced body is inlined
- **THEN** it appears under a delimiter naming its origin and marking it as unverified external content, so no node reads it as the client's own requirement

#### Scenario: An unfetchable reference fails rather than thinning the body

- **GIVEN** a referenced GitHub issue that cannot be fetched
- **WHEN** `jira.py fetch ABC-1` runs
- **THEN** it exits 3 naming the URL and writes no item, because a body that silently varies with network state would break the determinism contract

#### Scenario: Following is suppressible

- **WHEN** `jira.py fetch ABC-1 --no-follow` runs
- **THEN** `body` is the Jira description alone, `references` still names the URLs found, and the exit code is 0 even if the reference is unreachable

### Requirement: Credentials come from the environment and failures are typed
The adapter SHALL read `JIRA_BASE_URL`, `JIRA_EMAIL` and `JIRA_API_TOKEN` from the environment
and SHALL NOT read credentials from any committed file. A missing or malformed environment SHALL
exit 2 with the required variables named on stderr; an authentication, authorization or network
failure SHALL exit 3 with the remote's message on stderr. Neither case SHALL write a partial
`item.json`.

#### Scenario: Missing token is a usage error

- **GIVEN** `JIRA_API_TOKEN` is unset
- **WHEN** `jira.py fetch ABC-123` runs
- **THEN** it exits 2 naming the missing variables and writes nothing

#### Scenario: Rejected credential is a remote failure

- **GIVEN** a token Jira rejects
- **WHEN** `jira.py fetch ABC-123` runs
- **THEN** it exits 3 and no artifact is created

### Requirement: Fetch output is deterministic
Two fetches of an unchanged issue SHALL produce byte-identical output. Collections SHALL be
emitted in a stable order, and values that vary per request without reflecting issue state SHALL
be excluded. Fixture tests SHALL assert this without network access.

#### Scenario: Repeated fetch is byte-identical

- **WHEN** the adapter fetches the same unchanged issue twice from a recorded fixture
- **THEN** the two outputs are byte-identical

### Requirement: Outward writes refuse while a punch-out is open
`comment` and `transition` SHALL refuse with exit 2 while an unresolved punch-out exists for the
item, and `comment` SHALL refuse without a signed decision when `tracker.external` is true. This
check SHALL be made by the adapter in addition to the blocking hook.

#### Scenario: Comment refused during an open punch-out

- **GIVEN** an unresolved punch-out for `ABC-123`
- **WHEN** `jira.py comment ABC-123 --body-file summary.md` runs
- **THEN** it exits 2 naming the open punch-out and posts nothing

#### Scenario: External tracker needs a decision

- **GIVEN** `tracker.external: true` and no signed decision for the post
- **WHEN** `comment` runs
- **THEN** it exits 2 and posts nothing
