# gcp-developer-agent Specification

## Purpose
TBD - created by archiving change add-gcp-developer-agent. Update Purpose after archive.
## Requirements
### Requirement: Competency map mirrors the certification

The `gcp-developer` agent SHALL structure its competencies to mirror the Professional Cloud Developer exam guide's four scored sections (design; build & test; configure for deployment; integrate), so its coverage is auditable against the source guide.

#### Scenario: Sections are traceable

- **WHEN** the agent file is reviewed against the exam guide
- **THEN** each of the guide's four sections maps to a competency area in the agent, and each area names the GCP skills that cover it

### Requirement: Skill bindings cover the exam-named products plus dev craft

The agent SHALL bind (via `skills:` and by name in its body) the GCP skills for the products the exam guide names, PLUS the toolkit's engineering-craft skills (`tdd`, `test-strategy`, `clean-code`, `secure-coding`, `docker`) for the guide's language-agnostic practices. No exam-named product with a corresponding skill SHALL be omitted from the map.

#### Scenario: Named product resolves to a bound skill

- **GIVEN** a product named in the exam guide that has a toolkit skill (e.g. Firestore, Cloud KMS, Binary Authorization, Cloud Run, Pub/Sub)
- **WHEN** the agent handles a task involving it
- **THEN** the agent's map routes to that skill by name

#### Scenario: Gaps are named honestly

- **WHEN** the agent covers an exam-named product with no toolkit skill yet (Identity Platform, Cloud Service Mesh, Security Command Center, Cloud Workstations, Gemini Cloud Assist)
- **THEN** the agent names it as docs-reach / follow-on rather than implying a bound skill exists

### Requirement: Active build agent with safety guardrails

The agent SHALL be an active developer (able to write code, run builds, and invoke gcloud) — not advisory-only — and SHALL: confirm before outward-facing or irreversible GCP actions (deploys, key destruction, IAM changes); never echo secrets or key material; prefer ADC / attached service accounts / Workload Identity Federation over exported service-account keys; and defer to the bound skills for API-level detail rather than inventing flags.

#### Scenario: Irreversible action gate

- **WHEN** the agent is about to deploy, destroy a key, or change IAM
- **THEN** it states the exact action and target and gets confirmation first

#### Scenario: Credential hygiene

- **WHEN** the agent handles auth
- **THEN** it uses keyless auth patterns by default and never prints secret/key values

### Requirement: Frontmatter validity and README wiring

The agent file SHALL have strict-YAML-valid frontmatter (`name: gcp-developer`, a trigger-focused `description`, `tools`, `model`, `skills` in `claude-toolkit:<name>` form) and SHALL be indexed in both `README.md` and `agents/README.md`.

#### Scenario: Discoverable and valid

- **WHEN** the repo's frontmatter is validated and the READMEs are checked
- **THEN** the agent frontmatter parses and the agent is listed in both indexes

