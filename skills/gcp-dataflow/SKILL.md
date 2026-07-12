---
name: gcp-dataflow
description: "Google Cloud Dataflow — managed Apache Beam runner for unified batch + streaming pipelines: PCollections through transforms, event time vs processing time, windowing + watermarks + triggers, horizontal/vertical autoscaling, Streaming Engine and Dataflow Shuffle service offload, classic vs flex templates and the Google-provided template catalog, update/drain/cancel job lifecycle, per-second worker + service-charge pricing. Use when building or operating a Beam/Dataflow pipeline, running a Google-provided template (Pub/Sub to BigQuery etc.), tuning autoscaling or streaming latency, choosing drain vs cancel, or deciding Dataflow vs BigQuery ELT vs Pub/Sub BigQuery export vs Dataproc/Spark."
license: MIT
---

# GCP Dataflow

Managed runner for Apache Beam pipelines — one programming model for batch and streaming.
You write the pipeline graph (Java/Python/Go Beam SDK) or launch a prebuilt template;
Dataflow provisions workers, autoscales them, rebalances stragglers, and offloads shuffle
and streaming state to backend services. Exactly-once processing by default; at-least-once
mode available for cheaper, lower-latency streaming that tolerates duplicates.

## The mental model

- **Beam is the model, Dataflow is a runner.** A pipeline is a DAG of **transforms** applied to
  **PCollections** (potentially distributed, multi-element datasets). Bounded PCollection →
  batch; unbounded → streaming; same code either way. The core transform is **ParDo**, which
  runs your `DoFn` on every element in parallel. Because it's Beam, the pipeline is portable
  to Flink/Spark runners — the Dataflow-specific part is service options, not pipeline logic.
- **Event time ≠ processing time.** Every element carries a timestamp (when the event
  happened); the pipeline observes it later. All correct streaming aggregation is built on
  this split.
- **Windows + watermarks + triggers** turn an infinite stream into finite answers.
  **Windowing** groups an unbounded PCollection by element timestamps; the **watermark** is
  the runner's moving estimate of "all data up to time T has arrived"; **triggers** decide
  when to emit a window's result (at watermark, early/speculatively, or late as stragglers
  arrive). Batch is the degenerate case: one global window, trigger fires when input ends.
- **Dataflow's job is elasticity.** Horizontal autoscaling adds/removes workers from live
  signals (CPU, backlog, parallelism); dynamic work rebalancing re-splits hot shards without
  restarts. **Streaming Engine** moves streaming shuffle + state storage off worker VMs into
  the service backend (smaller workers, faster and finer-grained autoscaling, in-place option
  updates); **Dataflow Shuffle** does the same for batch `GroupByKey`/`Join`. **Dataflow
  Prime** layers on vertical autoscaling (per-worker memory right-sizing) and right-fitting;
  Google-provided templates run on Prime by default since Aug 2025 (`enable_prime=false`
  opts out).
- **Jobs are immutable-ish.** You don't ssh in and patch a running pipeline. You **update**
  (replacement job with a compatibility check that migrates in-flight state), **drain** (stop
  ingesting, finish what's buffered), or **cancel** (stop now, drop in-flight data).

## Job shapes

Run a Google-provided template — no SDK, no build. Pub/Sub → BigQuery (flex template,
streaming; command shape verified against the gcloud reference):

```bash
gcloud dataflow flex-template run pubsub-to-bq-$(date +%Y%m%d-%H%M%S) \
  --template-file-gcs-location=gs://dataflow-templates-REGION/latest/flex/PubSub_to_BigQuery_Flex \
  --region=REGION \
  --parameters=inputTopic=projects/PROJECT_ID/topics/TOPIC,outputTableSpec=PROJECT_ID:DATASET.TABLE
```

Use `inputSubscription=projects/PROJECT_ID/subscriptions/SUB` instead of `inputTopic`
(one or the other, not both). `latest` pins to the newest template release; dated versions
(e.g. `2023-09-12-00_RC00`) pin builds. Classic templates (JSON-serialized job graph) launch
with `gcloud dataflow jobs run ... --gcs-location=gs://...`; flex templates (Docker image +
spec file, graph built at launch, no `ValueProvider` ceremony) are the recommended kind.

The catalog covers streaming (Pub/Sub→BigQuery, Kafka→BigQuery, Spanner change streams,
Datastream→BigQuery), batch (JDBC→BigQuery, GCS CSV→BigQuery, MongoDB→BigQuery), and
utility (bulk compress, file format conversion) shapes — check it before writing code.

Code-first path: write the pipeline with the Beam SDK (Java, Python, Go) and submit with
the Dataflow runner (`--runner=DataflowRunner --project=... --region=... --temp_location=gs://...`).
JupyterLab notebooks support iterative development. Package your own pipeline as a flex
template for parameterized, CI/CD-friendly, no-dev-environment launches.

## Operational knobs

- **Autoscaling** is on by default (batch always; streaming when on Streaming Engine — which
  Python ≥2.21 and Go ≥2.33 SDKs enable by default, and Python ≥2.45 can't disable; Java opts
  in with `--enableStreamingEngine`). Cap it with `--max-workers` (default ceiling 2,000),
  floor it with `--dataflow-service-options=min_num_workers`, kill it with
  `--autoscaling_algorithm=NONE` + `--num_workers`. Streaming Engine jobs accept **in-flight
  updates** to `min-num-workers` / `max-num-workers` / `worker-utilization-hint` — no restart.
- **Lifecycle:** `gcloud dataflow jobs drain JOB_ID` (streaming only — stops ingestion,
  finishes buffered data, no loss, can take a long time), `gcloud dataflow jobs cancel JOB_ID`
  (batch or streaming — immediate, in-flight data lost), `... cancel JOB_ID --force` (stuck
  jobs after ~30 min of failed cancel; may leak worker VMs you must clean up).
- **Update:** launch the replacement with `--update` (+ `--transform-name-mappings` when steps
  were renamed; map deleted transforms to `""`, use full `Parent/Child` paths for composites).
  Dataflow runs a compatibility check on coders, stateful ops, and the transform mapping;
  pass → old job stops, state migrates, same job name/new job ID; fail → old job keeps
  running untouched. Changing coders, removing stateful ops, adding/removing side inputs, or
  changing windowing usually fails the check — validate first with `graph_validate_only`.
  You can update a pipeline that is mid-drain to rescue a stuck drain.
- **Monitoring:** the console job page shows the execution graph, per-stage progress,
  autoscaling history, and data-freshness/backlog charts for streaming; CPU profiling helps
  find the hot `DoFn`.

## Gotchas + pricing shape

- **Worker startup is minutes, not milliseconds.** Every job (including template launches —
  flex templates boot a launcher VM first to build the graph) provisions VMs. Dataflow is not
  for interactive latency; for a tiny transform on a Pub/Sub→BigQuery path, prefer BigQuery
  subscriptions.
- **Fusion can starve parallelism.** Dataflow fuses adjacent steps; a high-fan-out step fused
  to its producer inherits the producer's (low) parallelism. Break fusion with a
  `Reshuffle`/group-by-key when fan-out matters.
- **Hot keys serialize.** `GroupByKey` on a skewed key pins one worker; autoscaling can't fix
  skew. Use `Combine` (combiner lifting), salt keys, or fan-out combines.
- **Drain vs cancel is a data-loss decision.** Cancel drops buffered/in-flight records;
  drain doesn't but leaves windows to fire with partial panes and can run long. Never cancel
  a production streaming job you could drain.
- **Exactly-once has a price.** At-least-once mode is cheaper and lower-latency when the sink
  dedupes or duplicates are tolerable.
- **Pricing shape:** per-second billing of worker resources (vCPU, memory, persistent disk,
  optional GPU) at streaming or batch rates, **plus** service charges — Streaming Engine
  (billed as Streaming Engine Compute Units under resource-based billing, or legacy
  data-processed GB), Dataflow Shuffle GB for batch, and Data Compute Units (DCUs) when on
  Prime. **FlexRS** (flexible resource scheduling with preemptible-style capacity, delayed
  start) discounts batch jobs that can wait. A streaming job never scales to zero — an idle
  24/7 pipeline still bills its minimum workers; that's the line item that surprises people.

## vs siblings

- **BigQuery ELT** — if source and sink are both BigQuery-reachable and SQL can express the
  transform, load raw and transform in [[gcp-bigquery]]; no cluster, no watermark theory.
  Dataflow earns its keep on streaming semantics, non-SQL logic, and multi-source/sink graphs.
- **Pub/Sub → BigQuery direct export** — [[gcp-pubsub]] BigQuery subscriptions stream
  messages into a table with no pipeline at all. If you need zero transformation, don't run
  the template; the template (or custom pipeline) wins once you need UDFs, dead-letter
  handling, or enrichment.
- **Dataproc / Spark** — managed Hadoop/Spark for existing Spark/Hive code and
  cluster-centric control. Dataflow is serverless and per-job; pick it for new pipelines,
  pick Dataproc to lift-and-shift a Spark estate (or run Beam on the Flink/Spark runner).
- **Cloud Run / Functions** — event-at-a-time compute with no shuffle, windowing, or
  cross-element state. The moment you aggregate across events over time, you want Beam.

## Related

[[gcp-pubsub]], [[gcp-bigquery]], [[gcp-cloud-storage]], [[gcp-bigtable]], [[gcp-spanner]],
[[gcp-lakehouse]], [[gcp-artifact-registry]], [[gcp-cloud-run]], [[gcp-cloud-functions]],
[[gcp-compute-engine]], [[gcp-cloud-monitoring]], [[gcp-cloud-logging]], [[gcp-iam]],
[[gcp-cloud-sdk]], [[gcp-eventarc]]

Sources: https://docs.cloud.google.com/dataflow/docs, https://docs.cloud.google.com/dataflow/docs/overview, https://docs.cloud.google.com/dataflow/docs/concepts/beam-programming-model, https://docs.cloud.google.com/dataflow/docs/concepts/dataflow-templates, https://docs.cloud.google.com/dataflow/docs/guides/templates/provided-templates, https://docs.cloud.google.com/dataflow/docs/guides/templates/provided/pubsub-to-bigquery, https://docs.cloud.google.com/dataflow/docs/horizontal-autoscaling, https://docs.cloud.google.com/dataflow/docs/streaming-engine, https://docs.cloud.google.com/dataflow/docs/guides/stopping-a-pipeline, https://docs.cloud.google.com/dataflow/docs/guides/updating-a-pipeline, https://cloud.google.com/dataflow/pricing (fetched 2026-07).
