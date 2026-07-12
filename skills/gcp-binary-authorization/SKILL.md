---
name: gcp-binary-authorization
description: "Google Cloud Binary Authorization: the deploy-time attestation gate that only lets container images meeting policy actually run. Covers the project-singleton policy (default rule + per-cluster/per-service admission rules), evaluationMode (REQUIRE_ATTESTATION / ALWAYS_ALLOW / ALWAYS_DENY) and enforcementMode (ENFORCED_BLOCK_AND_AUDIT_LOG vs DRYRUN_AUDIT_LOG_ONLY), attestors + attestations (signed digest statements verified against public keys), admission allowlists, GKE admission-controller and Cloud Run enforcement, Cloud Build / Artifact Analysis supply-chain wiring, check-based platform policies (SLSA / simple-signing / vulnerability / freshness) and continuous validation, plus dry-run rollout, break-glass, and the digest-not-tag rule. Use when gating deploys on signed provenance, writing or debugging a Binary Authorization policy, creating attestors, rolling out enforcement safely, or designing supply-chain admission control on GCP."
license: MIT
---

# GCP Binary Authorization

Binary Authorization is the deploy-time gate between "this image exists in a registry" and "this
image runs in production." It is a policy-enforcement service for **GKE, Cloud Run, and Distributed
Cloud** that, at admission, refuses to start any container image that does not satisfy the project's
policy. It answers a different question than a vulnerability scanner: not "is this image healthy?"
but "is this exact image *allowed to be deployed here*, can we prove where it came from?" API
`binaryauthorization.googleapis.com`; CLI `gcloud container binauthz`.

## The mental model

**One policy per project.** Each Google Cloud project has exactly **one** policy (the
project-singleton policy) — a set of rules governing image deployment. A policy is:

- a **`defaultAdmissionRule`** — applies to any deployment that matches no more specific rule; plus
- zero or more **specific rules** — `clusterAdmissionRule` entries keyed by cluster
  (`location.CLUSTER_NAME`), and equivalent per-service rules on Cloud Run — that override the
  default for their target.

**A rule = an evaluation mode + an enforcement mode.** The `evaluationMode` decides *what* is
required: `ALWAYS_ALLOW` (let anything through), `ALWAYS_DENY` (block everything), or
`REQUIRE_ATTESTATION` (the image digest must carry attestations from the listed
`requireAttestationsBy` attestors). The `enforcementMode` decides *what happens on failure*:
`ENFORCED_BLOCK_AND_AUDIT_LOG` blocks the deploy and audit-logs it, while `DRYRUN_AUDIT_LOG_ONLY`
**lets the non-conformant image deploy but writes the violation to Cloud Audit Logs** — this pairing
of two orthogonal knobs is the whole safety story (see rollout below).

**Attestors and attestations.** An **attestation** is a signed statement "digest sha256:… passed
check X" — a record containing the image's registry path and digest, digitally signed with a
signer's private key, stored as an `ATTESTATION` occurrence in Artifact Analysis (backed by a
**note**). An **attestor** is the Binary Authorization resource that verifies those attestations at
deploy time: it wraps an Artifact Analysis note plus one or more **public keys** (Cloud KMS
asymmetric keys, or local PKIX / PGP keys). At admission the platform resolves the deploying image's
**digest**, looks up its attestations, and checks that each required attestor's public key validates
one of them — otherwise the image is denied (or allowlisted, below).

## Supply-chain wiring

Binary Authorization is the enforcement end of GCP's supply chain — it verifies metadata that other
services produce:

- **Cloud Build** builds/tests/pushes the image, then (typically via a Cloud KMS signing step)
  creates the **attestation** for the digest — often with the `gcr.io/PROJECT/binauthz-attestation`
  builder step in `cloudbuild.yaml` (`--artifact-url`, `--attestor`). It also writes SLSA **build
  provenance** as `BUILD` occurrences. See [[gcp-cloud-build]].
- **Artifact Analysis** ([[gcp-artifact-analysis]]) is the metadata store: notes and
  attestation/provenance/vulnerability occurrences that attestors and check-based policies read. Its
  vulnerability findings drive the **vulnerabilityCheck** in a platform policy.

## Enforcement points

- **GKE** — an in-cluster **admission-controller webhook** intercepts every Pod create and evaluates
  the project policy before the Pod is scheduled; a blocked Pod never starts. Enabled by creating
  the cluster with `--binauthz-evaluation-mode=PROJECT_SINGLETON_POLICY_ENFORCE` (or updating an
  existing cluster).
- **Cloud Run** — enforcement is per-service: `gcloud run services update SERVICE
  --binary-authorization=default` (and `gcloud run jobs update … --binary-authorization=…`). Once
  on, it enforces *every* update; a violating revision fails with "uses an unauthorized container
  image … is not authorized by policy."
- **Continuous validation (CV)** — separate from admission: it periodically re-checks the images of
  **already-running Pods** (at least every 24 h) against a **check-based platform policy**
  (`projects.platforms.policies`) and writes a Cloud Logging entry per violated policy per Pod.
  Legacy attestation-based CV is deprecated (May 2025); platform-policy checks are **SLSA
  provenance**, **simple signing attestation**, **Sigstore signature**, **image freshness** (max days
  since upload), and **vulnerability** (max fixable/unfixable severity, allow/block CVEs). Platform
  policies are platform-specific and only monitor — they do **not** enforce at admission.

## Verified shapes

Export / edit / import the singleton policy (the normal way to change it):

```bash
gcloud container binauthz policy export > policy.yaml   # edit, then:
gcloud container binauthz policy import policy.yaml
```

The enforce-vs-dryrun toggle lives in the YAML rule:

```yaml
defaultAdmissionRule:
  evaluationMode: REQUIRE_ATTESTATION          # or ALWAYS_ALLOW / ALWAYS_DENY
  enforcementMode: DRYRUN_AUDIT_LOG_ONLY       # flip to ENFORCED_BLOCK_AND_AUDIT_LOG when ready
  requireAttestationsBy:
    - projects/PROJECT_ID/attestors/prod-attestor
admissionWhitelistPatterns:
  - namePattern: gcr.io/my-trusted/*           # exempt images (supports * / ** and @sha256:)
globalPolicyEvaluationMode: ENABLE             # exempt Google-maintained system images
```

Create an attestor (note first, then attestor, then public key) and let the deployer verify it:

```bash
gcloud container binauthz attestors create prod-attestor \
  --attestation-authority-note=NOTE_ID --attestation-authority-note-project=PROJECT_ID
gcloud container binauthz attestors public-keys add --attestor=prod-attestor \
  --keyversion-project=… --keyversion-location=… --keyversion-keyring=… \
  --keyversion-key=… --keyversion=1                        # or --pkix-public-key-file / --pgp-public-key-file
gcloud container binauthz attestors add-iam-policy-binding prod-attestor \
  --member="serviceAccount:…" --role=roles/binaryauthorization.attestorsVerifier
```

## Safe rollout

1. Set the default rule to `DRYRUN_AUDIT_LOG_ONLY` and enable enforcement on the cluster/service.
2. Read the **audit-log denials** (Cloud Audit Logs) to see exactly what *would* have been blocked —
   catch base images, sidecars, and Google system images you forgot.
3. Add allowlist patterns / attestations until dry-run is clean, then flip to
   `ENFORCED_BLOCK_AND_AUDIT_LOG`.

**Break-glass** is the emergency bypass. On GKE, add the break-glass label/annotation to the Pod spec
(older `alpha.image-policy.k8s.io/break-glass` annotations still work); on Cloud Run,
`gcloud run services update SERVICE --breakglass=JUSTIFICATION`. It deploys the image even if it
violates policy **and always writes a single break-glass event to Cloud Audit Logs** — auditable and
alertable, never silent.

## Gotchas

- **Digest, not tag.** Attestations and policy lookups key on the image **digest**. An image
  referenced by tag can't be resolved to a signed digest and will violate the policy (CV first
  checks exemptions, then fails a tag-only image because there is no digest to look up). Deploy by
  `@sha256:…`.
- **Allowlist patterns** (`admissionWhitelistPatterns.namePattern`) exempt images entirely — support
  `*` / `**` wildcards and `@sha256:` matches; keep them tight (a broad `gcr.io/**` guts the gate).
- **System-image exemption**: `globalPolicyEvaluationMode: ENABLE` skips a Google-maintained list of
  system images (kube-system, GKE add-ons) so the control plane isn't blocked — leave it on.
- **Multi-project attestor sharing**: attestors and their notes can live in a central project and be
  referenced by many deployer projects; grant `roles/binaryauthorization.attestorsVerifier` on the
  attestor to each deployer's service agent, and IAM on the note.
- **Pricing shape** (verify current numbers): GKE enforcement is a flat **per-cluster/hour** fee
  (order of ~$0.016/cluster-hour, size-independent) with a monthly billing-account credit covering
  roughly one cluster; Cloud Run enforcement and Preview-stage CV carry no separate charge. You still
  pay for the underlying Artifact Analysis scanning, Cloud KMS signing, and compute.

## Related

- [[gcp-cloud-build]] — produces build provenance and creates attestations in CI
- [[gcp-artifact-analysis]] — the notes/occurrences store attestors and checks read; [[gcp-artifact-registry]] holds the digest-addressed images
- [[gcp-gke]], [[gcp-cloud-run]] — the enforcement points (admission controller / per-service gate)
- [[gcp-iam]] — attestor verifier roles and the notes-vs-deployer project split
- [[gcp-cloud-logging]] — where dry-run, break-glass, and CV violations land; [[secure-coding]], [[devops]]

Sources: https://docs.cloud.google.com/binary-authorization/docs/overview,
https://docs.cloud.google.com/binary-authorization/docs/key-concepts,
https://docs.cloud.google.com/binary-authorization/docs/creating-attestors-cli,
https://docs.cloud.google.com/binary-authorization/docs/cloud-build,
https://docs.cloud.google.com/binary-authorization/docs/run/enabling-binauthz-cloud-run,
https://docs.cloud.google.com/binary-authorization/docs/overview-cv,
https://docs.cloud.google.com/binary-authorization/docs/using-breakglass,
https://cloud.google.com/binary-authorization/pricing (fetched 2026-07).
