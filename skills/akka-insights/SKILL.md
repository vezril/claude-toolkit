---
name: akka-insights
description: Akka Insights (Cinnamon, formerly Lightbend Telemetry) — intelligent monitoring and observability purpose-built for Akka. A JVM agent collects metrics, events, and traces from Akka internals (actors, mailboxes, dispatchers/thread pools, remoting, cluster, sharding, persistence, streams, projections, HTTP, gRPC, Futures) and exports them to backends (Prometheus, OpenTelemetry, Datadog, StatsD, Elasticsearch) with Grafana/Datadog dashboards and Jaeger/Zipkin tracing. Covers how it's added (sbt/Maven plugin + javaagent + commercial credentials), what it instruments, the metrics/events/traces model, backends and visualizations, and that it is a commercial/licensed product. Use when setting up production monitoring/observability for an Akka application, diagnosing actor/cluster/sharding/persistence/stream performance, or choosing what Akka metrics to watch. Commercial; complements akka-diagnostics.
---

# Akka Insights (Cinnamon)

Intelligent monitoring/observability **purpose-built for Akka** (a.k.a. **Cinnamon**, formerly Lightbend Telemetry). A **JVM agent** in your application process collects **metrics, events, and traces** from Akka internals and exports them to monitoring backends with ready-made dashboards. It is a **commercial / licensed product** (requires an Akka subscription). Complements the free [[akka-diagnostics]] (which is startup-time checks, not continuous telemetry).

Cross-links: [[akka]] (meta), [[akka-diagnostics]], [[akka-cluster]], [[akka-persistence]], [[akka-streams]].

## How it's added

A **Cinnamon Agent** (`-javaagent`) attaches at JVM startup and instruments based on your config. In a cluster it runs on **each node**, each reporting independently. Setup (sbt example; Maven/Gradle equivalent):

```scala
// project/plugins.sbt — needs Akka commercial resolvers/credentials
addSbtPlugin("com.lightbend.cinnamon" % "sbt-cinnamon" % "2.22.x")
// build.sbt
lazy val app = (project in file(".")).enablePlugins(Cinnamon)
run / cinnamon := true
test / cinnamon := true
libraryDependencies ++= Seq(
  Cinnamon.library.cinnamonAkka,          // instrument Akka (required)
  Cinnamon.library.cinnamonAkkaTyped,
  Cinnamon.library.cinnamonAkkaPersistence,
  Cinnamon.library.cinnamonAkkaCluster,
  Cinnamon.library.cinnamonAkkaStream,
  Cinnamon.library.cinnamonPrometheus)    // a backend (required to export)
```
Both **`cinnamonAkka` and a backend** (`cinnamonPrometheus`/`cinnamonCHMetrics`/…) are required to instrument Akka. Actor telemetry is **off by default** (apps may have tens of thousands of actors) — opt in per actor path in `application.conf`:
```hocon
cinnamon.akka.actors { "/user/*" { report-by = class } }
```

## What it instruments & the model

- **Instrumentations:** Akka Actors, **Remoting**, **Cluster**, **Persistence**, **Cluster Sharding**, **Streams**, **Projections**, **HTTP** (server/endpoint/client), **gRPC**, and **Scala/Java Futures**.
- **Three instrument kinds:** **Metrics** (counters/gauges/rates — actors, mailbox sizes, dispatcher/thread-pool utilization, cluster membership, shard counts, persistence latencies, stream throughput, HTTP latencies), **Events** (errors, unhandled messages, dead letters), **Traces** (follow async/distributed message flows). **Extensions** add OpenTracing/SLF4J-MDC context propagation, custom metrics/events, and JMX/JVM importers.
- **Backends (exporters, multiple can run at once):** OpenTelemetry, **Prometheus**, Datadog, Coda Hale Metrics, StatsD, Elasticsearch, SLF4J events, Telegraf; tracing reporters **Jaeger**, **Zipkin**, Datadog. **Visualizations:** Grafana and Datadog dashboards, Vizceral.
- A **developer sandbox** (Elasticsearch+Kibana+Grafana, or OpenTelemetry/Prometheus variants) lets you try it without existing monitoring infra.

## Always-apply defaults

1. **It's commercial** — needs an Akka subscription and the Akka commercial resolvers/credentials (don't commit credential URLs). For free *checks* (config/starvation) use [[akka-diagnostics]] instead; for raw metrics you can also use the Core libraries' own metric hooks.
2. **Enable `cinnamonAkka` + one backend**; add per-toolkit modules (persistence/cluster/sharding/streams/http) matching what you run.
3. **Don't instrument every actor** — actor telemetry is off by default; select meaningful paths (`report-by = class` to group) to avoid metric explosion.
4. **Watch the Akka-specific signals** that matter operationally: dispatcher/thread-pool saturation and mailbox growth (ties to [[akka-diagnostics]] starvation), cluster membership/unreachable, shard distribution, persistence/recovery latency, stream backpressure, and HTTP latency.
5. **Export to your existing stack** (Prometheus/Grafana or OpenTelemetry) and add tracing (Jaeger/Zipkin) for cross-node message flows.

## Anti-patterns (flag in review)

- Instrumenting all actors (metric/cardinality explosion); shipping without a backend module (nothing exported).
- Treating Insights as a substitute for [[akka-diagnostics]]' config/starvation checks (they're complementary); ignoring mailbox/dispatcher metrics that signal blocking.

## Related

- [[akka-diagnostics]] (free startup checks) · [[akka-cluster]] / [[akka-persistence]] / [[akka-streams]] (the subsystems it instruments) · [[akka]] (meta).
- Source: https://doc.akka.io/libraries/akka-insights/current/
