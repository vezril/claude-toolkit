# gcp-cloud-kms Specification

## Purpose
TBD - created by archiving change add-gcp-developer-agent. Update Purpose after archive.
## Requirements
### Requirement: Cloud KMS skill

The toolkit SHALL provide a `gcp-cloud-kms` skill covering Cloud Key Management Service: key rings / keys / key versions, protection levels (software / HSM / external EKM), symmetric vs asymmetric keys, envelope encryption (DEK/KEK), CMEK integration with other GCP services, rotation, and IAM on keys — from live docs (date-stamped), in the established GCP-skill house style.

#### Scenario: KMS vs Secret Manager is explicit

- **WHEN** the skill explains the product
- **THEN** it draws the keys-vs-secrets distinction and cross-links `gcp-secret-manager`

#### Scenario: Envelope encryption + CMEK covered

- **WHEN** the skill's mental model is read
- **THEN** it explains envelope encryption (KEK wrapping DEKs) and how CMEK plugs KMS keys into services like Cloud Storage / BigQuery

