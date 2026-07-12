---
name: gcp-app-hub
description: "Google Cloud App Hub — the application-centric registry that organizes infrastructure resources into applications made of services (network/API interfaces) and workloads (compute running your code). Covers the mental model (management/host project, folder vs single-project vs legacy host-project boundaries, discovered vs registered vs detached components), setup shapes, which resource types are discoverable, regional-vs-global application constraints, attributes (criticality/environment/owners), quotas, and how App Hub feeds Gemini Cloud Assist and application monitoring. Use when organizing GCP resources into applications, setting up App Hub boundaries or host projects, registering services/workloads, or debugging why a resource isn't discoverable."
license: MIT
---

# GCP App Hub

App Hub is the foundational data model and central registry for applications on
Google Cloud. It inverts the usual lens: instead of a pile of per-project
infrastructure resources, you get **applications** — logical groupings that
deliver a business function — and every application-centric surface (Cloud Hub
operational views, Gemini Cloud Assist, application monitoring in Cloud
Observability) reads from this registry. App Hub itself provisions nothing; it
catalogs what already exists and layers ownership, criticality, and environment
metadata on top.

## The mental model

Three nouns, one boundary:

- **Application** — a named grouping of services + workloads delivering one
  business function. Created empty, then components are registered into it
  (or created from Application Design Center templates).
- **Service** — a network or API interface that exposes functionality: a load
  balancer forwarding rule, a Pub/Sub topic, a Cloud Run service, a Vertex AI
  endpoint. Services are **exclusive** (one application only) or **shared**
  (registerable to multiple applications — e.g., a GKE cluster).
- **Workload** — compute where your binaries run: a GKE Deployment /
  StatefulSet / DaemonSet / CronJob, a Compute Engine MIG, a Cloud Run job.

The **application management boundary** is the set of projects/folders whose
resources App Hub can see. A **management project** (called the **host
project** in the legacy model) centralizes App Hub APIs, IAM, billing, and
quota for the boundary. Within the boundary, supported resources are
auto-ingested as **discovered** services/workloads; you then **register** them
into an application. If the underlying resource is deleted or its project
leaves the boundary, the component goes **detached** — registered but no
longer manageable.

Properties (project, location, exclusive/shared, functional type) are
immutable and auto-discovered. **Attributes** are yours to set per component
and per application: owners (developer / operator / business), criticality
(mission-critical → low), environment (production / staging / development /
test). Attributes cannot be set on shared services.

## Setup shapes

Three boundary models, in increasing setup effort:

1. **Single project** (Preview) — the project is its own boundary. Fastest
   onboarding, reduced feature surface. Fine for small apps or first contact.
2. **App-enabled folder** (recommended) — a folder is the boundary; every
   descendant project is automatically included, and new projects join by
   being created/moved under the folder. IAM for applications is granted on
   the folder's management project. Aligns boundaries with org structure.
3. **Legacy host project** — for components scattered across projects with no
   common folder. Designate a host project, then manually attach each service
   project (`gcloud apphub service-projects add`). Nothing is implicit.

Then create applications and register discovered components — via the console
(App Hub / Cloud Hub), `gcloud apphub applications ...`, or the REST/RPC API.

## Gotchas

- **A service project attaches to exactly one host project at a time.**
  Re-homing a project means detaching it first — and its registered
  components go detached in the old boundary.
- **Location is a hard registration filter.** A *regional* application can
  only contain components in its own region; global or multi-region resources
  (e.g., multi-region Cloud Storage buckets) must go in a *global*
  application. Pick application location deliberately — a "regional app +
  global load balancer" registration simply won't offer the LB.
- **Only supported resource types are discoverable.** The list is broad —
  Cloud Run services/jobs, GKE cluster + K8s workload kinds, MIGs, forwarding
  rules/backend services, Cloud SQL, Spanner, AlloyDB, Firestore, Bigtable,
  BigQuery, Memorystore, Pub/Sub, Eventarc, Workflows, Cloud Storage buckets,
  Vertex AI endpoints/models/jobs, API Gateway, Cloud Deploy, Dataproc,
  Dataform — but anything not on the supported-resources page silently never
  appears as discovered. Absence from the discovered list usually means
  unsupported type, wrong boundary, or wrong location, in that order.
- **Registration is batched at 10** — max 10 services/workloads registered in
  one operation; loop for large applications.
- **Quotas**: 25 service projects per host project; 100 applications per
  region (and 100 global) per management project; 500 registered services and
  500 registered workloads per application; 12,000 API requests/min/project.
  Application monitoring metrics scopes cap included projects (375–3,500) —
  huge app-enabled folders can exceed this and drop metrics from views.
- App Hub metadata is only as useful as its attributes — downstream views
  (Cloud Hub incident/ops pages, Gemini Cloud Assist troubleshooting) key off
  criticality/environment/owners. Empty attributes = generic answers.

## Consuming surfaces

App Hub is mostly read *through* other products: Gemini Cloud Assist uses the
application model for design and troubleshooting context; Google Cloud
Observability renders application-scoped monitoring dashboards (telemetry
grouped by application, not project); Cloud Hub shows alerts and health per
application. If those views look empty, fix App Hub registration first.

## Related

[[gcp-cloud-monitoring]], [[gcp-cloud-logging]], [[gcp-cloud-run]],
[[gcp-gke]], [[gcp-compute-engine]], [[gcp-load-balancing]],
[[gcp-pubsub]], [[gcp-iam]], [[site-reliability-engineering]], [[devops]]

Sources: https://docs.cloud.google.com/app-hub/docs,
https://docs.cloud.google.com/app-hub/docs/overview,
https://docs.cloud.google.com/app-hub/docs/key-concepts,
https://docs.cloud.google.com/app-hub/docs/set-up-app-hub,
https://docs.cloud.google.com/app-hub/docs/supported-resources,
https://docs.cloud.google.com/app-hub/docs/quotas,
https://docs.cloud.google.com/app-hub/docs/locations (fetched 2026-07).
