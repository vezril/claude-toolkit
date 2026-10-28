## ADDED Requirements

### Requirement: The update node upserts one delivery note per item
`vault-update` SHALL upsert a `delivery` note keyed by the item key, writing `goal`, `approach`
and `outcome` as one-line retrieval fields, with `domains`, `status`, and links to the project,
the services touched and the PR. Re-running SHALL edit fields in place and SHALL NOT create a
second note for the same key.

#### Scenario: A second run does not duplicate the note

- **WHEN** the update step runs twice for the same item
- **THEN** one delivery note exists for that key, with its fields updated

#### Scenario: The retrieval fields are one line each

- **WHEN** the note is written
- **THEN** `goal`, `approach` and `outcome` are single-line values, because recall shows them verbatim

### Requirement: Stubs may be minted, decisions may not be invented
The step MAY create missing `project` and service entity stubs that its links require. It SHALL
NOT create a `decision` note unless the item's proposal recorded an accepted design decision, and
SHALL link to the proposal or PR rather than copying its content.

#### Scenario: A missing service entity is stubbed

- **GIVEN** the delivery links a service with no entity note
- **THEN** a stub entity is created for it

#### Scenario: No decision note without a decision

- **GIVEN** an item whose proposal recorded no design decision
- **THEN** no decision note is created

### Requirement: The update step is declared uncertified
`vault-update` SHALL be listed in `allow_uncertified`, SHALL trace `certified: false`, and its
runs SHALL be excluded from the certified-only end-to-end rate until it carries a `prompt-edd`
package.

#### Scenario: It runs but does not count

- **WHEN** the update step runs under `allow_uncertified`
- **THEN** the trace records `certified: false` and the certified-only rate excludes the item
