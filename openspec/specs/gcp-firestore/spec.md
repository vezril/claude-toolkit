# gcp-firestore Specification

## Purpose
TBD - created by archiving change add-gcp-developer-agent. Update Purpose after archive.
## Requirements
### Requirement: Firestore Native mode skill

The toolkit SHALL provide a `gcp-firestore` skill covering Firestore in **Native mode**: the document/collection data model, queries and composite indexes, real-time listeners and offline persistence, Security Rules, transactions, and the operational model — distilled from live `cloud.google.com` docs (date-stamped), in the established GCP-skill house style (strict-YAML quoted description, mental model, verified shapes, gotchas + pricing shape, vs-siblings, Related, dated Sources).

#### Scenario: Native vs Datastore mode is explicit

- **WHEN** the skill explains the product
- **THEN** it draws the Native-mode vs Datastore-mode distinction, states one-mode-per-project, and cross-links `gcp-datastore`

#### Scenario: Positioned among data siblings

- **WHEN** the skill's vs-siblings section is read
- **THEN** it honestly places Firestore against Bigtable, Spanner, AlloyDB, and Cloud SQL for the document/unstructured use case

