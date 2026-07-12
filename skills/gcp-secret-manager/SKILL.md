---
name: gcp-secret-manager
description: "Google Cloud Secret Manager — stores API keys, passwords, certs, and other sensitive strings as immutable secret VERSIONS inside named SECRET containers; pin `latest` or a number/alias; access gated by per-secret IAM (secretmanager.versions.access); replication policy (automatic vs user-managed regions) chosen at creation and immutable; envelope-encrypted, optional CMEK; rotation schedules fire Pub/Sub notifications (Secret Manager notifies, YOU rotate); inject into Cloud Run (--set-secrets env/volume), GKE (CSI SecretProviderClass), Cloud Build. Use when storing/retrieving secrets, wiring app credentials, setting up rotation, choosing replication, or debugging secret access/IAM on GCP."
license: MIT
---

# GCP Secret Manager

Managed store for sensitive strings (API keys, passwords, certificates, connection
strings) on Google Cloud. Encrypted at rest (AES-256) and in transit (TLS), fine-grained
IAM per secret, versioned, auditable via Cloud Audit Logs. It stores secrets; it is not
a key store (that is Cloud KMS) and not general config (that is env vars / Parameter Manager).

## The mental model

- A **secret** is a container + metadata (name, labels, annotations, replication policy,
  rotation schedule, IAM policy). It holds no payload itself.
- A **secret version** is an immutable payload. You never edit a version — you *add a new
  one*. Old versions stay for rollback/audit until you disable or destroy them.
- You reference a version by **number** (`1`, `2`, …), by the built-in alias **`latest`**
  (highest enabled version), or by a **custom version alias** you attach.
- **Access is IAM per secret** (or per project). The one permission that reads payloads is
  `secretmanager.versions.access` (role `roles/secretmanager.secretAccessor`). Managing
  versions ≠ reading them — grant `secretVersionManager` to rotate without read access.
- **Replication policy is chosen at creation and is immutable.** `automatic` (Google picks
  regions, billed as one location) vs `user-managed` (you list regions, billed per region).
  You cannot change it later — recreate the secret to change.

## Core shapes (verified against docs)

```bash
# Create (global, automatic replication)
gcloud secrets create SECRET_ID --replication-policy="automatic"
# user-managed: --replication-policy="user-managed" --locations="us-east1,us-west1"

# Add a version — NEVER put the secret on the command line (leaks to ps + shell history).
gcloud secrets versions add SECRET_ID --data-file="/path/to/secret.txt"   # from a file
printf %s "$SECRET" | gcloud secrets versions add SECRET_ID --data-file=-  # from stdin

# Access the payload (prints raw bytes; latest or a specific version)
gcloud secrets versions access latest --secret=SECRET_ID
gcloud secrets versions access 3      --secret=SECRET_ID
```

REST: `POST …/secrets/SECRET_ID:addVersion` with `{"payload":{"data":"<base64>"}}`;
`GET …/secrets/SECRET_ID/versions/VERSION:access` returns `payload.data` **base64-encoded**
(decode with `jq -r .payload.data | base64 --decode`). Version states: **enabled**,
**disabled** (blocks access, reversible), **destroyed** (payload gone, irreversible).

```bash
# Cloud Run: as env var (read once at instance start; startup fails if unreadable)
gcloud run deploy SVC --image IMG --set-secrets=DB_PASS=SECRET_ID:latest
# Cloud Run: as a mounted file (read at runtime; a volume mount tracks 'latest')
gcloud run deploy SVC --image IMG --set-secrets=/secrets/db=SECRET_ID:latest
```

GKE (managed add-on, GKE 1.27.14+): declare a `SecretProviderClass`
(`provider: gke`, `resourceName: projects/…/secrets/…/versions/…`) and mount it via CSI
driver `secrets-store-gke.csi.k8s.io`; the pod's Kubernetes ServiceAccount authenticates
through Workload Identity Federation and needs `roles/secretmanager.secretAccessor`.
Cloud Build: reference secrets in `availableSecrets` and consume via `$$SECRET` env in steps.

## Operational

- **Rotation is notify-only.** Set `--rotation-period` (seconds) + `--next-rotation-time`
  (ISO 8601) + `--topics` (a Pub/Sub topic). At the scheduled time Secret Manager publishes
  a `SECRET_ROTATE` message — **it does NOT create a new version.** Your subscriber (e.g. a
  Cloud Run service or Cloud Function) generates the new credential, calls `versions add`,
  and redeploys. Same channel also emits events for version add/enable/disable/destroy.
- **Version lifecycle:** add → (enable/disable to gate access) → destroy. Prefer disable to
  test a rollback before destroying; destroy is permanent.
- **CMEK:** encrypt at rest with your own Cloud KMS key instead of Google-managed keys; for
  user-managed replication each region needs a key in that region. Optional, for compliance.
- **Regional secrets** (if data residency is required): stored in a single region with a
  regional endpoint (`secretmanager.LOCATION.rep.googleapis.com`); global secrets use the
  replication model above. Pick regional when data must not leave a region.

## Gotchas

- **Payload size limit is 64 KiB per version.** Store references/pointers, not large blobs.
- **Never echo a secret.** No `echo "$SECRET" | …` (echo adds a trailing newline and the
  value hits `ps`/history); use `--data-file=<file>` or `printf %s | --data-file=-`.
- **`latest` is resolved at read time, then cached by your app.** A newly added version is
  not seen until the app re-reads. Cloud Run *env-var* injection reads once at startup — a
  rotation needs a new revision; a *volume* mount re-reads and tracks `latest`.
- **Replication policy and (for global) region set are fixed at creation.** Plan regions up
  front; changing means recreating the secret.
- **Cost shape:** billed per *active secret version per replica location per month* + per
  *access operations* (per 10,000) + per *rotation notification* — user-managed replication
  multiplies storage cost by region count. Destroy stale versions and avoid re-fetching on
  every request (cache with a TTL) to keep access charges down. Access quota ~90,000/min per
  project. Confirm current numbers on the pricing page.

## vs siblings

- **vs environment variables / config:** env vars are plaintext in the deployment manifest
  and process env, unversioned, no IAM — fine for non-secret config, wrong for credentials.
- **vs Cloud KMS:** KMS manages *cryptographic keys* and does encrypt/sign operations; it
  does not hand back arbitrary payloads. Secret Manager stores the *secret material*; it can
  use a KMS key for CMEK. Different jobs.
- **vs Parameter Manager:** Parameter Manager holds structured, non-sensitive app config
  (and can *reference* a Secret Manager secret for the sensitive parts) — use it for config
  bundles, Secret Manager for the secret values themselves.

## Related

[[gcp-iam]] · [[gcp-cloud-run]] · [[gcp-cloud-build]] · [[gcp-gke]] · [[gcp-cloud-functions]] · [[gcp-pubsub]] (rotation notifications) · [[gcp-compute-engine]] · [[gcp-cloud-sql]] (DB credentials) · [[gcp-vpc-service-controls]] (exfiltration perimeter) · [[gcp-cloud-logging]] (audit access) · [[secure-coding]] · [[cryptography]]

Sources: https://docs.cloud.google.com/secret-manager/docs , /docs/overview , /docs/creating-and-accessing-secrets , /docs/add-secret-version , /docs/access-secret-version , /docs/rotation-recommendations , /docs/secret-rotation , /docs/manage-access-to-secrets , /docs/secret-manager-managed-csi-component , /docs/choosing-between-regional-secrets-global-secrets , /secret-manager/quotas , https://docs.cloud.google.com/run/docs/configuring/services/secrets , https://cloud.google.com/secret-manager/pricing (fetched 2026-07).
