# Proposal: add-gcp-developer-agent

## Why

The toolkit has 53 GCP product skills but no agent that composes them into a role. The Google **Professional Cloud Developer** certification defines a concrete, authoritative competency map for "build and configure scalable, secure cloud-native apps on GCP" — the ideal spec for the toolkit's first cloud-role agent. Mapping the exam guide against the existing skills surfaced three developer-core products the guide names but the toolkit lacks a skill for; building those first means the agent binds a complete syllabus with no holes.

## What Changes

- **Three new GCP skills** filling the exam-named gaps (same house style + `references/` discipline as the existing 53):
  - `gcp-firestore` — Firestore in **Native mode** (the document database the guide names for unstructured data in 1.3/4.1; distinct from the existing `gcp-datastore` = Datastore mode).
  - `gcp-cloud-kms` — Cloud Key Management Service (encryption keys, envelope encryption, CMEK; distinct from `gcp-secret-manager`'s secrets).
  - `gcp-binary-authorization` — deploy-time attestation gate for GKE/Cloud Run (named in 1.2 and 2.2; currently only a mention inside `gcp-artifact-analysis`).
- **One new agent** `gcp-developer` (`agents/gcp-developer.md`): an active build agent whose competencies mirror the exam's four sections and whose `skills:` list binds the exam-named GCP skills PLUS the toolkit's engineering-craft skills (tdd, test-strategy, clean-code, secure-coding, docker) so it develops like a professional, not recites like a flashcard.
- **Docs:** README indexed (new skills into the GCP group; agent into the agents list); `gcp-artifact-analysis` gets a cross-link to the new `gcp-binary-authorization`.

## Capabilities

### New Capabilities
- `gcp-firestore`: Firestore Native document database — data model, queries/indexes, real-time/offline, security rules, the Native-vs-Datastore-mode decision.
- `gcp-cloud-kms`: key management — key rings/keys/versions, symmetric/asymmetric/HSM/EKM, envelope encryption, CMEK integration, rotation/IAM.
- `gcp-binary-authorization`: deploy-time policy — attestors, policies, allowlists, Cloud Build provenance, GKE/Cloud Run enforcement, dry-run/break-glass.
- `gcp-developer-agent`: the agent's competency map, skill bindings, working method, and boundaries.

### Modified Capabilities
<!-- none — gcp-artifact-analysis gets a cross-link only, no requirement change -->

## Impact

- New: 3 skill folders under `skills/`, 1 agent file under `agents/`.
- `README.md` (skill index + agent list); `agents/README.md` mirror; one cross-link in `skills/gcp-artifact-analysis/SKILL.md`.
- No changes to existing skill content or the SDLC/agent machinery.
- Coverage note recorded in design: the lower-priority exam-named products without skills (Identity Platform, Cloud Service Mesh, Security Command Center/Web Security Scanner, Cloud Workstations, Gemini Cloud Assist, Cloud Shell) are handled as agent-prose references now, candidates for a follow-on batch.
