# Tasks: add-gcp-developer-agent

## 1. The three gap-filling skills (build to the established GCP-skill pattern, from live docs 2026-07)

- [x] 1.1 `skills/gcp-firestore/SKILL.md` — Native mode: document model, queries/composite indexes, real-time/offline, Security Rules, transactions; explicit Native-vs-Datastore-mode line + cross-link `gcp-datastore`; vs-siblings vs Bigtable/Spanner/AlloyDB/Cloud SQL
- [x] 1.2 `skills/gcp-cloud-kms/SKILL.md` — key rings/keys/versions, software/HSM/EKM, symmetric/asymmetric, envelope encryption, CMEK, rotation, IAM; explicit KMS-vs-Secret-Manager line + cross-link `gcp-secret-manager`
- [x] 1.3 `skills/gcp-binary-authorization/SKILL.md` — policies/attestors/attestations, GKE + Cloud Run enforcement, Cloud Build provenance + Artifact Analysis integration, dry-run + break-glass; cross-link `gcp-cloud-build` + `gcp-artifact-analysis`
- [x] 1.4 Add a reciprocal cross-link to `gcp-binary-authorization` in `skills/gcp-artifact-analysis/SKILL.md` Related section

## 2. The agent

- [x] 2.1 `agents/gcp-developer.md` — frontmatter (`name: gcp-developer`, trigger description, active `tools` incl. Write/Edit/Bash, `model: opus`, `skills:` = core GCP + craft in `claude-toolkit:` form); body = competency map mirroring the exam's 4 sections with the skill routes, the working method, the safety guardrails (irreversible-action gate, credential hygiene, keyless-auth-by-default, defer-to-skills), and the honestly-named coverage gaps

## 3. Wiring + verification

- [x] 3.1 README: index the 3 new skills into the GCP group; add `gcp-developer` to the agents list
- [x] 3.2 `agents/README.md`: add `gcp-developer` to the agent list
- [x] 3.3 Validation sweep: strict-YAML across all frontmatters (skills + agent); every `[[gcp-*]]` cross-link (incl. the 3 new + the reciprocal) resolves; agent's `skills:` entries all resolve to real skills; new skills carry Sources + Related + license
- [x] 3.4 Coverage re-diff: confirm every exam-guide-named product either binds a skill or is named as a gap in the agent body
- [x] 3.5 Ship via git-ship (gated)
