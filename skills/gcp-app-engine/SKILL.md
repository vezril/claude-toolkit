---
name: gcp-app-engine
description: "Google App Engine (GAE): the original fully managed PaaS — standard (sandboxed, scale-to-zero, instance-hour billing) vs flexible (Docker on Compute Engine VMs, min 1 instance) environments, the app → services → versions → instances model, app.yaml as the deployment contract, automatic/basic/manual scaling, traffic splitting/migration between versions, runtime deprecation cycles, and legacy bundled services (memcache, task queues, NDB, users API). Use when deploying or debugging an App Engine app, writing/reviewing app.yaml, choosing standard vs flexible, splitting traffic between versions, maintaining a legacy GAE estate (Python 2/Java 8 era apps, bundled-services code, runtime end-of-support migrations), or deciding whether to stay on GAE vs move to Cloud Run."
license: MIT
---

# Google App Engine

The original PaaS (2008) and still a fully managed, serverless app platform: you
deploy source (standard) or a container (flexible), Google runs and scales it.
Its strategic position today is honest maintenance mode for new work: Google's own
migration docs state "For new Google Cloud users, we recommend using Cloud Run as
the preferred alternative over App Engine" (docs, as of 2026-07). App Engine is not
deprecated — runtimes keep getting new GA versions (Python 3.14, Java 25, Go 1.26,
Node 24, PHP 8.5, Ruby 4.0 as of 2026-07) — but new projects should default to
Cloud Run; this skill matters mostly for running, evolving, and eventually migrating
existing GAE estates.

## The mental model

One **application** per Google Cloud project, pinned forever to one region. The app
contains **services** (microservices; there is always a `default` service), each
service holds **versions** (every deploy creates one), and each version runs on
**instances**. Traffic is routed per-service, split or migrated between versions.
URLs: `https://PROJECT_ID.REGION_ID.r.appspot.com`, with service- and version-level
URLs exposed automatically (unlike Cloud Run, where revision URLs need tags).

Two environments, one choice that shapes everything:

- **Standard**: language sandbox (no Docker), startup in seconds, scales to zero,
  billed per instance-hour. Only supported runtimes (Go, Java, Node.js, PHP, Python,
  Ruby). No SSH, no background processes, no WebSockets, writes only to `/tmp`.
  Built for spiky traffic and free-tier/low-cost apps.
- **Flexible**: your Docker container on Compute Engine VMs. Custom runtimes,
  SSH, background processes, WebSockets, 60-minute request timeout — but startup
  and deploys take minutes, it **never scales below 1 instance**, and it bills like
  VMs (vCPU + memory + persistent disk).

**app.yaml is the contract.** Per service, it declares `runtime`, `service`,
`entrypoint`, `instance_class`, `env_variables`, `handlers` (URL routing with
`script` and `static_files` — static serving is built in), `inbound_services`,
`vpc_access_connector`, and exactly one scaling block:

- `automatic_scaling` (F-class instances): `min_instances`, `max_instances`,
  `min_idle_instances`, `target_cpu_utilization`, `max_concurrent_requests`.
- `basic_scaling` (B-class): `max_instances`, `idle_timeout` — instances start on
  request, die when idle. Good for intermittent workloads.
- `manual_scaling` (B-class): fixed `instances` count — "resident" instances that
  keep state and run indefinitely.

Companion YAMLs, deployed separately: `cron.yaml` (scheduled hits), `dispatch.yaml`
(routing rules across services), `index.yaml` (Datastore indexes).

## Deploy and traffic (verified commands)

```sh
gcloud app deploy                                   # deploy service in cwd, promote to 100%
gcloud app deploy --version v2 --no-promote         # deploy without shifting traffic
gcloud app deploy --project PROJECT_ID
gcloud app deploy service1/app.yaml service2/app.yaml   # multiple services at once
gcloud app deploy cron.yaml dispatch.yaml index.yaml    # companion configs
gcloud app browse                                   # open the deployed app

# Split traffic between versions (canary / A/B):
gcloud app services set-traffic SERVICE \
  --splits v1=0.9,v2=0.1 --split-by cookie          # ip | cookie | random

# "Migrate" = split 100% to one version:
gcloud app services set-traffic SERVICE --splits v2=1
```

Splitting mechanics: `cookie` (the `GOOGAPPUID` cookie, ~0.1% precision, sticky per
user) beats `ip` (mobile IPs shift; server-to-server traffic from Google infra hashes
to few IPs and lands on one version). Set `Cache-Control` headers so cached assets
from one version don't poison another.

## Gotchas

- **One app per project, region immutable.** You cannot delete an App Engine app
  (only disable it) and cannot change its region — a wrong region means a new project.
- **Runtime deprecation is a treadmill.** Each runtime version has end-of-support →
  deprecation → decommission dates (e.g. Node.js 20: end of support 2026-04-30,
  decommission 2027-04-30; first-gen Java 8: decommission 2027-01-31 — dates as of
  2026-07). Decommissioned runtimes eventually stop deploying and can stop serving.
  Check the runtime support schedule as part of routine maintenance, not as a fire drill.
- **Legacy bundled services** (memcache, task queues, NDB/Datastore, users, mail,
  blobstore, URL fetch, search) are available on second-gen runtimes via SDKs like
  `appengine-python-standard`, but they are legacy and GAE-only — they are the #1
  lock-in blocker to a Cloud Run migration. New code should use Memorystore, Cloud
  Tasks, the Cloud Datastore/Firestore client, IAP, etc.
- **Flexible's cost floor**: minimum 1 VM per version *with traffic allocated*, per
  service, always on. Stale flexible versions with traffic splits quietly burn money;
  standard's stopped versions don't.
- **Old versions pile up.** Every deploy without `--version` mints a new version;
  projects hit version-count limits. Delete stale versions.
- **Standard's sandbox** bites native dependencies (no arbitrary binaries), long
  request handling (timeout depends on runtime/scaling type), and WebSockets.
- **Instance classes**: F1 (384 MB/600 MHz, default) → F2 → F4 → F4_1G for automatic
  scaling; B1–B8 for basic/manual. An F4 bills as four F1 instance-hours.

**Pricing shape**: standard bills instance-hours by class (free tier: 28 F1
instance-hours/day, 9 B1 instance-hours/day, first 1 GB/day egress free) — so
idle-but-warm `min_idle_instances` cost real money and scale-to-zero apps can be
free. Flexible bills vCPU + memory + persistent disk per second, no free tier, plus
egress. Ancillary services (Datastore, Cloud Storage, Cloud Build minutes for
deploys) bill separately.

## vs siblings

- **Cloud Run** is the successor in all but name: same serverless contract, but
  container-native, per-request or instance-based billing, revision URLs via tags,
  no one-app-per-project or region lock. GAE service → Cloud Run service; GAE
  version → Cloud Run revision. New workloads: Cloud Run, per Google's own docs.
  Existing GAE standard apps with no bundled-services usage migrate readily;
  bundled-services code needs rework first.
- **For existing GAE estates**: staying put is legitimate — standard's free tier,
  built-in static file serving, cron/dispatch, and version URLs are conveniences
  Cloud Run makes you assemble. The forcing functions are runtime decommission
  dates and flexible-environment cost.
- **GKE** is for teams that need Kubernetes-level control (sidecars, stateful sets,
  custom networking) and accept cluster operations. GAE flexible occupies an awkward
  middle — most of its use cases are better served by Cloud Run today.
- **Cloud Functions (Cloud Run functions)** is for single-purpose event handlers,
  not whole apps.

## Related

[[gcp-cloud-run]], [[gcp-cloud-functions]], [[gcp-gke]], [[gcp-compute-engine]],
[[gcp-cloud-tasks]], [[gcp-cloud-scheduler]], [[gcp-datastore]],
[[gcp-memorystore-redis]], [[gcp-cloud-build]], [[gcp-cloud-sdk]], [[gcp-iap]],
[[gcp-vpc]], [[gcp-cloud-logging]], [[gcp-cloud-monitoring]]

Sources: https://docs.cloud.google.com/appengine/docs,
https://docs.cloud.google.com/appengine/docs/the-appengine-environments,
https://docs.cloud.google.com/appengine/docs/standard/an-overview-of-app-engine,
https://docs.cloud.google.com/appengine/docs/standard/reference/app-yaml,
https://docs.cloud.google.com/appengine/docs/standard/runtimes,
https://docs.cloud.google.com/appengine/docs/standard/splitting-traffic,
https://docs.cloud.google.com/appengine/docs/standard/testing-and-deploying-your-app,
https://docs.cloud.google.com/appengine/docs/standard/python3/services/access,
https://docs.cloud.google.com/appengine/docs/standard/quotas,
https://docs.cloud.google.com/appengine/migration-center/run/compare-gae-with-run
(fetched 2026-07).
