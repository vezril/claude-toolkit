# Design: add-gcp-developer-agent

## The exam → skill map (the agent's backbone)

The Professional Cloud Developer guide (exam guide 042426, retrieved 2026-07) has four scored sections. Each competency binds to skills:

| Exam section (~weight) | Named products → skills |
|---|---|
| **1. Design scalable/secure/reliable apps (~32%)** | compute: `gcp-cloud-run` `gcp-gke` `gcp-compute-engine`; APIs: `gcp-api-gateway` `gcp-apigee`; async: `gcp-eventarc` `gcp-pubsub` `gcp-workflows` `gcp-cloud-tasks` `gcp-cloud-scheduler`; LB/cache: `gcp-load-balancing` `gcp-memorystore-redis`; security: `gcp-iap` `gcp-secret-manager` **`gcp-cloud-kms`** `gcp-iam` **`gcp-binary-authorization`** `gcp-artifact-analysis`; data: `gcp-alloydb` `gcp-spanner` `gcp-bigtable` **`gcp-firestore`** `gcp-cloud-sql` `gcp-cloud-storage` `gcp-bigquery` |
| **2. Build and test (~23%)** | `gcp-cloud-build` `gcp-artifact-registry` `gcp-cloud-code` `gcp-cloud-sdk`; craft: `tdd` `test-strategy` |
| **3. Configure for deployment (~24%)** | `gcp-cloud-run` `gcp-gke` `gcp-eventarc` `gcp-pubsub` `gcp-apigee` `gcp-docker` |
| **4. Integrate with GCP services (~21%)** | datastores + messaging (above); `gcp-iam` (service accounts); observability: `gcp-cloud-logging` `gcp-cloud-monitoring` `gcp-cloud-trace` `gcp-error-reporting` |

Bold = the three skills this change creates.

## Decisions

**The exam guide is the spec, not my taste.** The agent's competency headings mirror the four sections and their weights; a reviewer can diff the agent against the guide. Where the guide names a language-agnostic practice (unit/integration testing, error handling with exponential backoff, least privilege), the agent binds the toolkit's craft skills rather than restating them — that's the "exam-faithful + dev craft" choice.

**Three new skills, built to the established pattern.** Same frontmatter (strict-YAML quoted description, `license: MIT`), same body shape (identity → mental model → verified shapes → gotchas/pricing → vs-siblings → Related → dated Sources), 90–180 lines, `references/` only if a product's surface demands it. Each fetched from live `cloud.google.com` docs (2026-07), date-stamping any renames.

- `gcp-firestore` must draw the **Native vs Datastore mode** line explicitly and cross-link `gcp-datastore` (the toolkit's existing Datastore-mode skill) — same product family, different API, one-mode-per-project, and the guide uses Firestore for the *unstructured/document* role.
- `gcp-cloud-kms` must draw the **KMS vs Secret Manager** line (keys that wrap data vs stored secret payloads) and cover envelope encryption + CMEK, since the guide pairs them in 1.2.
- `gcp-binary-authorization` must connect to `gcp-cloud-build` (provenance/attestations) and `gcp-artifact-analysis` (vuln findings feeding policy), the two skills the guide names alongside it.

**The agent is active (writes code), not advisory.** A developer agent builds — so `tools` include Write/Edit/Bash, unlike the read-only reviewer agents. Its guardrails: confirm before outward-facing/irreversible GCP actions (deploys, key destruction, IAM changes), never echo secrets/keys, prefer ADC/attached service accounts/WIF over exported keys (the guide's own 1.2 doctrine), and defer to the bound skills for API-level detail rather than inventing flags.

**Model + binding hygiene.** `model: opus` for the breadth; `skills:` uses the `claude-toolkit:<name>` form. Binding all ~35 relevant skills would bloat the list — bind the **high-frequency core** (the products every developer path touches) and have the body instruct the agent to reach for the sibling GCP skills by name as the task narrows. This keeps the frontmatter legible while the body carries the full map.

**Coverage honesty.** The lower-priority exam-named products without skills (Identity Platform, Cloud Service Mesh, Security Command Center + Web Security Scanner, Cloud Workstations, Gemini Cloud Assist, Cloud Shell) are named in the agent's body as "reach for the docs / follow-on skill pending" rather than pretended-covered. This is recorded so a follow-on change can pick them up.

## Risks

- Skill-list drift vs the exam guide when Google revises it: mitigated by the date-stamp and the exam-section-mirrored structure (easy to re-diff).
- Over-binding making the agent unfocused: mitigated by core-bind + body-map-the-rest.
- The three new skills are net-new surface to validate: same strict-YAML + cross-link-resolves gates the 53-skill batch passed.
