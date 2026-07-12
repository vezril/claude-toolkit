---
name: gcp-artifact-registry
description: "Google Cloud Artifact Registry — the universal package/container registry on *.pkg.dev: one repository per format (docker, maven, npm, python, apt, yum, go, generic) per location, in three modes (standard = your artifacts, remote = pull-through cache of Docker Hub/Maven Central/PyPI/etc., virtual = one endpoint aggregating upstreams with priorities against dependency confusion). Successor to Container Registry (gcr.io), which shut down 2025-03-18 — gcr.io URLs now resolve via gcr.io-domain repos hosted on Artifact Registry. Use when pushing/pulling images or packages on GCP, wiring gcloud auth configure-docker or npm/pip keyring auth, choosing repo mode/region, writing cleanup policies, migrating off gcr.io, or estimating storage/egress cost."
license: MIT
---

# gcp-artifact-registry

Artifact Registry is Google Cloud's single artifact store: container images and language/OS
packages behind IAM, VPC Service Controls, and Artifact Analysis vulnerability scanning, wired
into Cloud Build and deployable to GKE, Cloud Run, Compute Engine, and App Engine.

## The mental model

A **repository = one format + one mode + one location**, addressed on a format-specific host:

```
LOCATION-FORMAT.pkg.dev/PROJECT/REPOSITORY
us-central1-docker.pkg.dev/my-proj/my-repo/my-image:tag        # docker (also Helm/OCI)
https://us-central1-python.pkg.dev/my-proj/my-repo/simple/     # python (PEP 503 index)
https://us-central1-npm.pkg.dev/my-proj/my-repo/               # npm
```

Formats: `docker` (OCI images + Helm charts), `maven`, `npm`, `python`, `apt`, `yum`, `go`,
`generic` (plus Kubeflow pipeline templates). Locations are regions or multi-regions
(`us`, `europe`, `asia`); storage price is identical either way, but egress is not (below).
You cannot change a repo's format or location after creation — plan the layout, don't migrate.

Three **modes**:

- **Standard** — read/write storage for your own artifacts; the default; scanned by Artifact Analysis.
- **Remote** — read-only pull-through proxy that caches an upstream on first request
  (Docker Hub, Maven Central, PyPI, Debian/CentOS distros, npmjs, or another AR repo).
  Caching cuts latency, insulates you from upstream outages, and gets public deps scanned.
- **Virtual** — a single endpoint fronting multiple upstream repos (standard/remote) of the
  same format, resolved by explicit **priority**. Put your private standard repo above the
  remote public cache: that ordering is the built-in dependency-confusion defense.

Reference architecture: clients talk only to a virtual repo; behind it sit one standard repo
(your artifacts) and one remote repo (public cache). Virtual repos store nothing themselves
(and are not billed for storage, and can't have cleanup policies).

## Auth and push/pull shapes

Everything authenticates as a Google identity with `artifactregistry.reader`/`.writer` roles.

**Docker** — configure the credential helper per registry host, then plain docker commands:

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev   # comma-separate multiple hosts
docker push us-central1-docker.pkg.dev/my-proj/my-repo/app:1.2.0
```

Alternatives, in descending preference: standalone `docker-credential-gcr` (faster, no gcloud
needed — good for CI), a 60-minute access token piped to
`docker login -u oauth2accesstoken --password-stdin`, and (discouraged) a long-lived service
account key with `docker login`.

**Python** — install `keyring` + `keyrings.google-artifactregistry-auth`; point pip/twine at
`https://LOCATION-python.pkg.dev/PROJECT/REPO/simple/` (pip.conf `index-url` / `.pypirc`).
The keyring backend resolves Application Default Credentials first, then gcloud user creds.

**npm** — `gcloud artifacts print-settings npm --project=… --repository=… --location=… --scope=@myorg`
emits the `.npmrc` lines (`@myorg:registry=https://LOCATION-npm.pkg.dev/PROJECT/REPO/`);
`npx google-artifactregistry-auth` refreshes the token (valid ~1 hour) before installs/publishes.

The same `gcloud artifacts print-settings FORMAT` pattern exists for maven/apt/yum. Never
hand-roll auth in CI when a credential helper exists.

## Gotchas

- **Region choice is a cost decision.** Same-location transfer is free, and so is
  region↔multi-region on the same continent — but us-east1→us-west1 is $0.01/GiB, intra-Europe
  $0.02, intra-Asia $0.05, cross-continent $0.08, Oceania $0.15 (2026-07 list). Put the repo in
  the region where GKE/Cloud Run pulls happen; a multi-region repo is not automatically cheaper.
- **The gcr.io redirect era.** Container Registry shut down 2025-03-18. `gcr.io`,
  `us.gcr.io`, `eu.gcr.io`, `asia.gcr.io` URLs (including Google-owned images) still work, but
  they are served by Artifact Registry **gcr.io-domain repositories**. For backward
  compatibility keep those repos; for new work use `pkg.dev` names.
- **Cleanup policies are eventually-applied and keep-wins.** Delete policies (by tag state,
  tag/version/package prefix, age, keep-most-recent count) run as background jobs — effects land
  "within approximately one day", max 10 policies/repo. Keep policies override delete policies.
  Always start with dry run (`validateOnly`; results appear in Cloud Logging audit logs ~1 day
  later). Immutable-tags repos won't delete tagged artifacts; virtual repos can't have policies.
- **Remote repos have upstream rate ceilings** (per org, per region, per minute): Docker Hub
  600, Maven Central 3,000, npmjs 1,800, PyPI 1,200 — plus a 9.9 GB max per upstream fetch.
- **Pricing shape** (2026-07): storage $0.000136986/GiB-hour ≈ **$0.10/GiB-month** after a
  **0.5 GiB free tier per billing account** (not per project); ingress free; egress per the
  table above; vulnerability scanning billed separately via Artifact Analysis once the
  Container Scanning or On-Demand Scanning API is enabled. Storage cost is why cleanup
  policies exist — untagged image layers accrete fast under CI.

## vs siblings

- **vs Container Registry (gcr.io)** — deprecated, shut down 2025-03-18; no new writes.
  Artifact Registry is the successor with per-repo IAM (CR had only bucket-level ACLs),
  regional placement, non-Docker formats, remote/virtual modes, and cleanup policies.
  Anything still pushing to gcr.io is really writing to an AR gcr.io-domain repo.
- **vs Cloud Storage for blobs** — use a **generic** repo when you want versioned, immutable,
  IAM-per-repo artifact semantics (installers, tarballs, firmware) next to your other
  artifacts; use GCS when you need object-storage features (lifecycle classes, signed URLs,
  website hosting, huge objects, streaming).
- **Artifact Analysis** ([[gcp-artifact-analysis]]) is the scanning/metadata layer on top;
  [[gcp-cloud-build]] is the usual producer; [[gcp-cloud-run]]/[[gcp-gke]] the usual consumers.

## Related

[[gcp-artifact-analysis]], [[gcp-cloud-build]], [[gcp-cloud-run]], [[gcp-gke]],
[[gcp-cloud-functions]], [[gcp-app-engine]], [[gcp-buildpacks]], [[gcp-cloud-code]],
[[gcp-cloud-sdk]], [[gcp-iam]], [[gcp-vpc-service-controls]], [[gcp-cloud-storage]],
[[docker]], [[github-actions]], [[devops]]

Sources: https://docs.cloud.google.com/artifact-registry/docs/overview,
https://docs.cloud.google.com/artifact-registry/docs/repositories,
https://docs.cloud.google.com/artifact-registry/docs/supported-formats,
https://docs.cloud.google.com/artifact-registry/docs/docker/authentication,
https://docs.cloud.google.com/artifact-registry/docs/python/authentication,
https://docs.cloud.google.com/artifact-registry/docs/nodejs/authentication,
https://docs.cloud.google.com/artifact-registry/docs/repositories/cleanup-policy,
https://docs.cloud.google.com/artifact-registry/docs/transition/transition-from-gcr,
https://docs.cloud.google.com/artifact-registry/quotas,
https://cloud.google.com/artifact-registry/pricing (fetched 2026-07).
