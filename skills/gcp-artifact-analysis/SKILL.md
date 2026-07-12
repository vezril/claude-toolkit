---
name: gcp-artifact-analysis
description: "Google Cloud Artifact Analysis (formerly Container Analysis): vulnerability scanning and software-composition metadata for containers and language packages. Covers the Grafeas notes/occurrences model, automatic scan-on-push to Artifact Registry vs on-demand scanning, SBOM generation (SPDX 2.3), VEX statements, continuous re-analysis windows, and the Binary Authorization / Cloud Build provenance supply-chain wiring. Use when enabling or debugging image scanning, querying vulnerability occurrences, gating CI/CD on scan severity, exporting SBOMs, or designing supply-chain policy on GCP."
license: MIT
---

# GCP Artifact Analysis

Artifact Analysis is Google Cloud's software-composition-analysis and metadata service: it scans
container images and language packages for vulnerabilities and stores the results — plus build
provenance, attestations, SBOMs, and VEX — as structured, queryable metadata. It was renamed from
**Container Analysis** (2023) as the scope grew beyond containers; the rename changed no APIs, so the
metadata API is still `containeranalysis.googleapis.com` and client libraries still say
"Container Analysis". The scanning APIs are separate: `containerscanning.googleapis.com` (automatic)
and `ondemandscanning.googleapis.com` (on-demand).

## The mental model

**Grafeas notes and occurrences.** Artifact Analysis implements the open-source Grafeas metadata
model. A **note** is a provider-owned definition of a fact ("CVE-2024-1234 exists", "this builder
produces provenance") — editable only by its owner, usually living in the provider's project. An
**occurrence** is that note instantiated on a specific artifact ("image sha256:abc contains
CVE-2024-1234 in libssl 3.0.2"). Your project holds occurrences; Google's (or your tooling's)
project holds the notes they reference. Kinds: `VULNERABILITY`, `BUILD` (provenance, written by
Cloud Build), `PACKAGE`, `DISCOVERY` (scan status — check this first when "nothing is showing up"),
`ATTESTATION` (Binary Authorization), `VULNERABILITY_ASSESSMENT` (VEX), `SBOM_REFERENCE`, plus
image/deployment kinds. The recommended access pattern is notes and occurrences in separate
projects for fine-grained IAM. Pub/Sub topics emit events on note/occurrence creation for
event-driven reactions.

**Two scanning modes, one metadata store.**
- **Automatic (registry) scanning** — enable the Container Scanning API and every *new* image
  pushed to Artifact Registry in that project is scanned on push, keyed by digest. Results land as
  occurrences and are *continuously refreshed* against new CVE data — no re-push needed.
- **On-demand scanning** — a one-shot `gcloud` scan of a local or remote image, no Artifact
  Registry required. Results are ephemeral (gone after **48 hours**) and are *not* updated as new
  CVEs appear. This is the CI-gate tool, not the monitoring tool.

## How-to shapes

**Enable automatic scanning** (project-wide switch, per-repo toggles):

```bash
gcloud services enable containerscanning.googleapis.com
# Per-repository override (needed for Maven/npm/Python repos, which default OFF):
gcloud artifacts repositories update REPO --location=LOC --allow-vulnerability-scanning
```

Docker-format repositories (standard and remote) scan by default once the API is on;
Maven, npm, and Python repositories require the per-repo flag. Virtual repositories are
never scanned. Existing images are NOT scanned retroactively — push again to trigger a scan.

**On-demand scan + CI gate** (the canonical Cloud Build pattern — build, scan, check severity,
push only if clean):

```bash
gcloud artifacts docker images scan IMAGE_URI --format='value(response.scan)'   # returns SCAN_ID
gcloud artifacts docker images list-vulnerabilities SCAN_ID \
  --format='value(vulnerability.effectiveSeverity)'
# fail the build if output contains CRITICAL|HIGH, then docker push
```

Roles: `roles/ondemandscanning.admin` on the Cloud Build service account.

**Query results** (automatic scanning):

```bash
gcloud artifacts docker images list REPO_URI --show-occurrences        # summary
gcloud artifacts docker images describe IMAGE_URI --show-package-vulnerability
# Raw Grafeas: GET v1/projects/PROJECT/occurrences?filter=kind="VULNERABILITY" AND resourceUrl="..."
```

**SBOMs**: with container scanning enabled, Artifact Analysis generates SBOMs in **SPDX 2.3**,
stores them in a Cloud Storage bucket in your project, and writes an `SBOM_REFERENCE` occurrence
carrying the GCS location, hash, and a DSSE signature. `gcloud artifacts sbom export/list` drives
it. You can also upload SBOMs you built elsewhere. Generation only works for images in Artifact
Registry Docker repos covered by the Container Scanning API.

## Gotchas

- **Coverage is Linux-only.** Windows Server containers are not scanned. For multi-arch manifest
  lists, only one image is analyzed (linux/amd64 preferred).
- **What gets scanned**: OS packages (Alpine, Debian, Ubuntu, RHEL, CentOS, Rocky, SUSE, ...) plus
  language packages — Go, Java, Python, Node.js, PHP, Ruby, Rust, .NET — matched against the GitHub
  Advisory Database. Language-package findings inside container images historically differed
  between automatic and on-demand scanning; verify which mode covers your ecosystem before relying
  on it as a gate.
- **Freshness windows**: automatic scanning keeps re-analyzing an image only while it has been
  pushed or pulled within the last **30 days**. After that, vulnerability metadata goes stale (the
  UI flags it); after **90 days** it is archived and only retrievable via the API. Pull or re-push
  to reactivate. A `DISCOVERY` occurrence with `analysisStatus` tells you where a scan stands.
- **Digest-keyed dedup**: scans key on digest, so re-tagging never triggers or bills a scan. But
  package (non-container) scanning has **no dedup** — the same package pushed to N repositories is
  billed N times.
- **Pricing shape** (verify current numbers): **$0.26 per scanned image/package** for automatic
  scanning — charged once per digest on first push, all subsequent continuous re-analysis of that
  digest free; **$0.26 per on-demand scan** (every invocation bills, no dedup). Billing starts the
  moment you enable the Container Scanning API. The metadata API itself (notes/occurrences CRUD)
  is not the billed unit; SBOM files accrue ordinary Cloud Storage costs. GKE's "advanced
  vulnerability insights" tier ($0.04/cluster-hour) is deprecated, shutdown June 16, 2026.
- Enabling the scanning API does nothing for images already in the registry, and disabling it
  stops new scans but existing occurrences remain readable.

## Supply-chain context

Artifact Analysis is the metadata backbone of GCP's software-supply-chain story: Cloud Build
writes SLSA build-provenance as `BUILD` occurrences; scanners and humans write `ATTESTATION`
occurrences; **Binary Authorization** evaluates those attestations at deploy time to admit or
block images on GKE/Cloud Run. Vendors' VEX statements upload as `VULNERABILITY_ASSESSMENT`
notes to suppress non-exploitable findings. The end-to-end gate is: scan on push → attest if
clean → Binary Authorization enforces the attestation at deploy. Security Command Center can
aggregate the findings across projects.

## Related

- [[gcp-artifact-registry]] — the registry whose pushes trigger automatic scanning
- [[gcp-cloud-build]] — on-demand scan gates and SLSA provenance generation
- [[gcp-binary-authorization]] — consumes these findings as check-based deploy-gate policy
- [[gcp-gke]], [[gcp-cloud-run]] — where Binary Authorization enforces attestations
- [[gcp-cloud-storage]] — where generated SBOMs live
- [[gcp-pubsub]] — notifications on new notes/occurrences
- [[gcp-iam]] — notes-vs-occurrences project split for access control
- [[secure-coding]], [[docker]], [[devops]]

Sources: https://docs.cloud.google.com/artifact-analysis/docs,
https://docs.cloud.google.com/artifact-analysis/docs/artifact-analysis,
https://docs.cloud.google.com/artifact-analysis/docs/container-scanning-overview,
https://docs.cloud.google.com/artifact-analysis/docs/metadata-storage,
https://docs.cloud.google.com/artifact-analysis/docs/enable-container-scanning,
https://docs.cloud.google.com/artifact-analysis/docs/ods-cloudbuild,
https://docs.cloud.google.com/artifact-analysis/docs/sbom-overview,
https://cloud.google.com/artifact-analysis/pricing (fetched 2026-07).
