# gcp-binary-authorization Specification

## Purpose
TBD - created by archiving change add-gcp-developer-agent. Update Purpose after archive.
## Requirements
### Requirement: Binary Authorization skill

The toolkit SHALL provide a `gcp-binary-authorization` skill covering the deploy-time attestation gate: policies, attestors and attestations, the default/cluster-specific/allowlist rules, enforcement on GKE and Cloud Run, integration with Cloud Build provenance and Artifact Analysis findings, and dry-run + break-glass — from live docs (date-stamped), in the established GCP-skill house style.

#### Scenario: Positioned in the supply chain

- **WHEN** the skill explains the product
- **THEN** it connects to `gcp-cloud-build` (provenance/attestations) and `gcp-artifact-analysis` (vulnerability findings), and states enforcement points (GKE, Cloud Run)

#### Scenario: Safe rollout path

- **WHEN** the skill covers adoption
- **THEN** it presents dry-run mode before enforcement and the break-glass escape hatch

