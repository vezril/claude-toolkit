---
name: gcp-application-integration
description: "Google Cloud Application Integration — the serverless iPaaS: a visual drag-and-drop designer where an integration = triggers + tasks + edges + data mappings, with Integration Connectors bridging to Salesforce/ServiceNow/SAP/databases via entity CRUD and actions. Use when connecting business systems on GCP with low-code workflows, wiring API/Pub/Sub/Schedule/Salesforce triggers, configuring the Connectors or Data Mapping tasks, reasoning about execution/payload limits, pricing (executions + connection nodes + data processed), or choosing Application Integration vs Workflows vs Eventarc."
license: MIT
---

# Application Integration

Google Cloud's Integration-Platform-as-a-Service (iPaaS): serverless, auto-scaling, fully
managed, and built around a **visual integration editor** rather than code. Where
Workflows orchestrates *your services* with YAML, Application Integration connects
*business systems* — Salesforce, ServiceNow, SAP, databases — with drag-and-drop flows,
built-in transformation functions, and a large connector library. Its audience is the
integration developer / enterprise architect, not the backend engineer.

## The mental model

An **integration** is a graph:

- **Triggers** start an execution: API trigger (invoke over REST), Cloud Pub/Sub,
  Cloud Scheduler (cron), Salesforce events, webhooks, and more. One integration can have
  several triggers, each rooting its own path.
- **Tasks** are the nodes — units of work: Call REST Endpoint, Connectors, Data Mapping,
  JavaScript, Send Email, Approval (human-in-the-loop), While/For Each loops, call
  sub-integrations, and per-service Google Cloud tasks.
- **Edges** wire tasks together; **edge conditions** branch the flow on variable values.
- **Variables** carry state: inputs (entry payload), outputs (returned/exposed results),
  and locals scoped to the run. Everything downstream reads and writes these.
- **Data Mapping task** is the transformation workhorse: a visual editor mapping source
  fields to target variables through chainable/nestable functions, executed top-to-bottom
  (earlier rows feed later ones). The newer **Data Transformer task** (preview) does the
  same with Jsonnet in diagram or script mode.

### Integration Connectors: the third-party bridge

Connectors are not part of Application Integration itself — they live in **Integration
Connectors**, a separate (and separately billed) Google Cloud product. You create a
**connection** (connector type + region + auth credentials + service account), and the
**Connectors task** inside an integration uses it two ways:

- **Entities** — the connector exposes the backend's data objects for CRUD: List (paged,
  default 25 records, up to 50,000 pages), Get, Create, Update, Delete.
- **Actions** — connector-specific operations, e.g. "Execute custom query" on SQL
  connectors.

Connections can be created inline from the Connectors task editor. Auth is normally baked
into the connection (service account + IAM roles), but connectors can allow a dynamic
auth override at runtime via input variables or headers.

## Authoring and publishing

- Create an integration in a **provisioned region**, then build in the editor: drop a
  trigger, add tasks, connect edges, define variables and mappings.
- Integrations are **versioned**: you edit a *draft*, test it (test cases and manual test
  runs from the editor), then **publish** a version to make it live; unpublish or roll to
  another version to change what runs. Up to 100 versions per integration.
- Executions can be **replayed**, and every run is inspectable in execution logs; Cloud
  Logging and Cloud Monitoring integration is built in.
- Integrations upload/download as JSON, which is how you move them between projects or
  put them under version control.

## Gotchas and limits (the shape)

- **Sync vs async**: synchronous executions time out at **2 minutes**; asynchronous at
  **10 minutes**; a Connector task call at 3 minutes. But a *suspended* integration
  (Approval task, callbacks) can live up to **31 days** — long waits are fine, long
  computation is not.
- **Payload budget**: 30 MB cumulative for all integration data per run; 8 MB per
  connection round-trip; 20 MB per JSON/string variable; 100k elements per mapped array.
  Big-data movement belongs in Dataflow, not here.
- 1,000 integrations per project, 100 tasks per integration, default 50 concurrent
  executions (adjustable) — For Each Parallel fan-out draws from that same pool.
- Failed executions still count as billable executions.

**Pricing shape** (three plans): a **free tier** (~400 executions + 20 GiB connection
data/month + first 2 Google-service connection nodes); **pay-as-you-go** billed on three
drivers — *integration executions* (per-1,000, success or failure), *connection nodes*
(per node-hour; Google-service nodes cheaper than third-party-app nodes, first two Google
nodes free, suspended connections free), and *data processed through connections* (per
GiB past the free 20 GiB) — plus networking; and a **subscription** plan (fixed annual
integration-call and connection-unit bundles). The cost surprise is usually idle
third-party connection nodes, billed per hour whether or not traffic flows.

## vs siblings

The docs' own split: choose **Application Integration** to "connect, map, transform, and
integrate data between business systems" — differing schemas, heavy data mapping, visual
low-code, real-time or small-batch business transactions. Choose **Workflows** to
orchestrate *services* you built (YAML/JSON, developer-oriented, lightweight sequencing,
orchestration logic separated from business logic). They compose: Workflows can call
Application Integration through a dedicated connector when an orchestration step must
touch a third-party business system. **Eventarc** is neither — it's the event *router*
that gets a CloudEvent to a destination; an Eventarc-routed Pub/Sub message can trigger
an integration, but Eventarc runs no logic itself. Rough cut: business-system glue with
data transformation → Application Integration; service orchestration in code →
Workflows; event delivery → Eventarc.

## Related

- [[gcp-workflows]] — code-first service orchestration; the docs' explicit comparison
- [[gcp-eventarc]] — event routing that can feed an integration's Pub/Sub trigger
- [[gcp-cloud-scheduler]] — the clock behind Schedule triggers
- [[gcp-cloud-tasks]] — demand-driven task queues, a different async primitive
- [[gcp-pubsub]] — trigger source and common task target
- [[gcp-cloud-run]] / [[gcp-cloud-functions]] — endpoints the REST task calls
- [[gcp-cloud-sql]] / [[gcp-bigquery]] — common connector destinations
- [[gcp-iam]] — service accounts behind connections and integration governance
- [[gcp-cloud-logging]] / [[gcp-cloud-monitoring]] — execution logs and metrics

Sources: https://docs.cloud.google.com/application-integration/docs/overview, https://docs.cloud.google.com/application-integration/docs/choose-application-integration-or-workflows, https://docs.cloud.google.com/application-integration/docs/configure-connectors-task, https://docs.cloud.google.com/application-integration/docs/create-integrations, https://docs.cloud.google.com/application-integration/docs/data-mapping-overview, https://docs.cloud.google.com/application-integration/docs/quotas, https://cloud.google.com/application-integration/pricing (fetched 2026-07).
