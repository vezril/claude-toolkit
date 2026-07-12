---
name: gcp-cloud-build
description: "Google Cloud Build — GCP's serverless CI/CD service that runs builds as a series of containerized steps sharing a /workspace volume. Covers the cloudbuild.yaml build config schema (steps, name/args/entrypoint/env/dir/id/waitFor/script, images, artifacts, options, substitutions, availableSecrets, timeout/queueTtl, serviceAccount), triggers (GitHub/GitLab/Bitbucket push/PR/tag, manual, webhook, Pub/Sub, Developer Connect repos), default pool vs private pools (VPC peering, static IPs, VPC-SC, higher concurrency), SLSA build provenance, caching and speed-up patterns, the 2024 default-service-account change, quotas (300 steps, 600 triggers, 30 concurrent default-pool builds) and per-build-minute pricing. Use when writing or debugging a cloudbuild.yaml, wiring repo triggers, choosing machine types or private pools, fixing substitution/quoting or service-account/logging errors, running gcloud builds submit, or deciding between Cloud Build, GitHub Actions, and Cloud Deploy."
license: MIT
---

# GCP Cloud Build

Google Cloud's managed CI/CD build service: it pulls source (GitHub, GitLab, Bitbucket, Cloud Storage), runs your build, and produces artifacts (container images, JARs, anything). Serverless — no build fleet to manage; you pay per build-minute.

## The mental model

**A build = a sequence of Docker containers sharing one disk.** Each step in `steps:` is a container image (`name:`) run with `args:`; every step mounts the same `/workspace` volume, so files written by step N are visible to step N+1. That's the whole trick — "install deps" and "run tests" are separate containers cooperating through the filesystem. Steps run sequentially by default; `waitFor:` + `id:` gives you a DAG (`waitFor: ['-']` = start immediately, parallel to everything before it). Env vars do NOT persist across steps (containers are separate) — only `/workspace` and declared `volumes:` do.

**Triggers fire builds from events.** Push/PR/tag triggers on connected repos (GitHub, GitHub Enterprise, GitLab/GitLab EE, Bitbucket Cloud/Server/DC, Developer Connect-linked repos), plus manual triggers (schedulable via Cloud Scheduler), webhook triggers, and Pub/Sub triggers. Triggers inject substitutions (`$COMMIT_SHA`, `$BRANCH_NAME`, `$TAG_NAME`, `$_YOUR_CUSTOM`) and can require human approval before running. Cloud Source Repositories is dead for new customers (since 2024-06-17) — connect external repos instead.

**Pools are where workers live.** The **default pool** is Google-managed shared infra: public egress, ~5 e2 machine types, up to 30 concurrent builds per region. **Private pools** are dedicated managed workers you create in a region: peer into your VPC (reach private IPs, databases, internal registries), disable public IPs, static IPs, VPC Service Controls, ~64 machine types, 100+ concurrency. Builds run in the pool's region.

## Real shapes

```yaml
# cloudbuild.yaml
steps:
  - id: build
    name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/app:$SHORT_SHA',
           '--cache-from', '${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/app:latest', '.']
  - id: test
    name: 'python:3.12-slim'          # any public image works as a step
    entrypoint: 'bash'
    args: ['-c', 'pip install -r requirements.txt && pytest']
    waitFor: ['-']                     # runs in parallel with 'build'
  - id: deploy
    name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    script: |                          # script: replaces entrypoint/args
      gcloud run deploy app --image=${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/app:$SHORT_SHA --region=${_REGION}
    automapSubstitutions: true         # substitutions become env vars in script
    waitFor: ['build', 'test']
images: ['${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/app:$SHORT_SHA']  # pushed after steps; build FAILS if not produced
substitutions:
  _REGION: us-central1
  _REPO: my-repo
timeout: 1200s                         # default 3600s, max 24h
options:
  machineType: E2_HIGHCPU_8            # default is e2-standard-2
  logging: CLOUD_LOGGING_ONLY          # required shape when using a non-legacy service account (or set logsBucket)
  # pool: { name: projects/$PROJECT_ID/locations/us-central1/workerPools/my-pool }  # private pool
```

```bash
gcloud builds submit --config=cloudbuild.yaml --region=us-central1 .   # respects .gcloudignore
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJ/repo/app .  # no yaml: docker build+push shortcut
gcloud builds triggers create github --name=main-push \
  --repo-owner=me --repo-name=app --branch-pattern='^main$' \
  --build-config=cloudbuild.yaml --region=us-central1
gcloud builds log BUILD_ID --region=us-central1
```

**Secrets and non-image artifacts**:

```yaml
availableSecrets:
  secretManager:
    - versionName: projects/$PROJECT_ID/secrets/npm-token/versions/latest
      env: NPM_TOKEN
steps:
  - name: 'node:22'
    entrypoint: 'bash'
    args: ['-c', 'echo "//registry.npmjs.org/:_authToken=$$NPM_TOKEN" > .npmrc && npm ci']
    secretEnv: ['NPM_TOKEN']           # secrets are opt-in per step, never global by accident
artifacts:
  objects:                             # non-container outputs -> Cloud Storage
    location: gs://my-bucket/builds/$BUILD_ID/
    paths: ['dist/*.jar']
```

Built-in substitutions you'll actually use: `$PROJECT_ID`, `$PROJECT_NUMBER`, `$BUILD_ID`, `$LOCATION`, and from repo triggers `$COMMIT_SHA`, `$SHORT_SHA`, `$BRANCH_NAME`, `$TAG_NAME`, `$REPO_NAME`, `$REF_NAME`. `$BRANCH_NAME` and `$TAG_NAME` are mutually empty (a push is one or the other), and manual `gcloud builds submit` from a local dir has **no** commit-derived values at all — a `cloudbuild.yaml` that tags images `:$SHORT_SHA` builds `image:` (empty tag) when submitted manually unless you pass `--substitutions=SHORT_SHA=$(git rev-parse --short HEAD)`.

## Gotchas

- **Substitution quoting**: `$PROJECT_ID` is substituted by Cloud Build *before* the step runs; to pass a literal `$` to bash inside a step, write `$$VAR`. Custom substitutions must start with `_` (`$_FOO`). Trigger builds default to `ALLOW_LOOSE` (missing substitution → empty string, silently); manual `gcloud builds submit` defaults to `MUST_MATCH` (missing → error). `options.dynamicSubstitutions: true` enables bash parameter expansion (`${_TAG%%-*}`) in substitution values.
- **Service-account change (rolled out 2024-05/06)**: new projects no longer get the legacy `PROJECT_NUMBER@cloudbuild.gserviceaccount.com` SA as default — builds run as the *Compute Engine default SA*, and triggers now require you to pick a service account. With any non-legacy SA, a build with no logging config **fails immediately** ("build.service_account requires...") — set `options.logging: CLOUD_LOGGING_ONLY`, `options.defaultLogsBucketBehavior: REGIONAL_USER_OWNED_BUCKET`, or an explicit `logsBucket`. The invoker also needs `iam.serviceAccounts.actAs` on the build SA.
- **Timeouts**: build default 3600s (silent kill at 1h — the classic "big Docker build died at exactly 60 minutes"), max 24h; per-step `timeout` must fit inside it. `queueTtl` (default 3600s) expires builds that sit queued too long.
- **Default machine is small**: e2-standard-2 (2 vCPU / 8 GB). Slow builds usually want `machineType: E2_HIGHCPU_8/32` (note: bigger VMs add startup latency) or a private pool. `diskSizeGb` up to 4000.
- **No layer cache between builds**: workers are ephemeral. Use `--cache-from` after pulling `:latest` (`|| exit 0` so first build survives), kaniko, or copy dependency caches to/from Cloud Storage. `--cache-from` only helps up to the first changed layer.
- **Env doesn't cross steps**: pass state via `/workspace` files or `volumes:`; `env:` and `secretEnv:` are per-step (or global under `options:`).
- **`dir:` is relative to `/workspace`**; absolute paths escape the shared context.
- **Provenance**: `options.requestedVerifyOption: VERIFIED` makes Cloud Build generate signed SLSA build provenance for images listed in `images:` — the input to Binary Authorization / supply-chain policy (pairs with [[gcp-artifact-analysis]]).

**Quotas** (defaults, per project): 300 steps/build, 700 images/build, 600 triggers, 100 `args` per step, 200 substitutions, 10–30 concurrent default-pool builds per region (not raisable past 30 — use another region or a private pool; private-pool CPU quotas are adjustable, excess builds queue).

**Pricing shape**: per build-minute, by machine type × region × pool type, SSD billed separately; queue time is free. Order of magnitude (2026-07): e2-medium ≈ $0.003–0.005/min, e2-standard-2 ≈ $0.006/min, e2-highcpu-32 ≈ $0.06–0.10/min. Free tier: 2,500 default-pool e2-standard-2 build-minutes per month per billing account. Regional per-machine rates were restructured 2025-11-01 — check the pricing page for your region.

## When to use vs siblings

- **vs GitHub Actions**: if your code lives on GitHub and doesn't touch private GCP resources, Actions usually wins on ecosystem (marketplace actions, PR UX) and zero-setup. Cloud Build wins when builds need VPC-internal access (private pools), GCP-native IAM (no long-lived cloud keys in CI — though Actions + Workload Identity Federation narrows this), SLSA provenance enforced by Binary Authorization, or Pub/Sub/webhook-driven builds. Many teams run both: Actions for CI checks, Cloud Build for the image build+deploy leg.
- **vs Cloud Deploy**: not competitors — Cloud Build *builds and can deploy imperatively* (a `gcloud run deploy` step); Cloud Deploy is a managed *delivery pipeline* (progressive promotion dev→staging→prod, approvals, rollbacks) that itself uses Cloud Build workers for renders/deploys. CI in Cloud Build, CD in Cloud Deploy is the intended pairing.
- **Output goes to [[gcp-artifact-registry]]** (gcr.io is legacy); deploy targets are typically [[gcp-cloud-run]], [[gcp-gke]], [[gcp-cloud-functions]], [[gcp-app-engine]].
- **No Dockerfile?** [[gcp-buildpacks]] (`pack` / `gcloud builds submit --pack`) builds images straight from source.

## Related

[[gcp-artifact-registry]], [[gcp-artifact-analysis]], [[gcp-cloud-run]], [[gcp-gke]], [[gcp-cloud-functions]], [[gcp-app-engine]], [[gcp-buildpacks]], [[gcp-cloud-sdk]], [[gcp-secret-manager]], [[gcp-iam]], [[gcp-pubsub]], [[gcp-cloud-scheduler]], [[gcp-eventarc]], [[gcp-vpc]], [[gcp-vpc-service-controls]], [[gcp-cloud-storage]], [[gcp-cloud-logging]], [[github-actions]], [[docker]], [[devops]], [[terraform]]

Sources: https://docs.cloud.google.com/build/docs, https://docs.cloud.google.com/build/docs/build-config-file-schema, https://docs.cloud.google.com/build/docs/triggers, https://docs.cloud.google.com/build/docs/private-pools/private-pools-overview, https://docs.cloud.google.com/build/docs/optimize-builds/speeding-up-builds, https://docs.cloud.google.com/build/docs/cloud-build-service-account-updates, https://docs.cloud.google.com/build/quotas, https://cloud.google.com/build/pricing, https://cloud.google.com/build/pricing-update (fetched 2026-07).
