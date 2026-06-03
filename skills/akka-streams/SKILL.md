---
name: akka-streams
description: Akka Streams (Akka Core 2.10.x) in Scala and Java — bounded-memory, back-pressured stream processing built on Reactive Streams. Covers the core blueprint types (Source, Flow, Sink, RunnableGraph, BidiFlow), materialization and materialized values (Keep), the back-pressure model, the operator catalog (map/mapAsync/filter/scan/grouped, throttle/buffer/conflate for rate, flatMapConcat/groupBy substreams, fan-in/out), the GraphDSL for non-linear topologies, error handling (recover, RestartSource, supervision strategies), streaming IO & framing, StreamRefs, dynamic streams (hubs, KillSwitch), actor interop (ask-in-stream, ActorSource/ActorSink, Source.queue), custom GraphStages, and the stream testkit. Use whenever building stream-processing pipelines, transforming/aggregating data with backpressure, integrating IO/Kafka/HTTP as streams, doing async/parallel processing, building graphs, handling stream errors/restarts, or bridging actors and streams — even if "Akka Streams" isn't named but Source/Flow/Sink, backpressure, materialization, or reactive streaming are involved. Underpins akka-http, akka-grpc, alpakka, and akka-persistence query.
---

# Akka Streams

Process potentially unbounded sequences of elements with **bounded memory** and **back-pressure** — never an `OutOfMemoryError` from a fast producer outrunning a slow consumer. Akka Streams is a founding implementation of **Reactive Streams** (and JDK 9 `java.util.concurrent.Flow`); you build an immutable **blueprint** and *materialize* it to run. It underpins [[akka-http]], [[akka-grpc]], [[alpakka]], and [[akka-persistence]] query.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Cross-links: [[akka]] (meta), [[akka-actors]], [[alpakka]], [[functional-programming]].

Dependency: `"com.typesafe.akka" %% "akka-stream" % AkkaVersion` (+ `akka-stream-testkit % Test`). Scala DSL `akka.stream.scaladsl._`, Java DSL `akka.stream.javadsl.*`.

## The model

- **`Source[Out, Mat]`** (1 output), **`Sink[In, Mat]`** (1 input), **`Flow[In, Out, Mat]`** (1 in, 1 out), **`BidiFlow`** (2+2), **`RunnableGraph[Mat]`** (fully connected, ready to `run()`). All are **immutable, reusable blueprints** — `source.map(f)` returns a *new* source; assign/run it.
- **`Mat`** is the *materialized value* produced when you run the blueprint (e.g. `NotUsed`, `Future[Done]`/`CompletionStage<Done>`, `Future[IOResult]`, a `KillSwitch`, an `ActorRef`). Combine with **`Keep.left/right/both/none`**; `runWith` keeps the Source's/Sink's value.
- **Back-pressure** is built into every operator: a downstream signals demand (`request(n)`), upstream never emits more than demanded — switching dynamically between push (slow producer) and pull (slow consumer), all non-blocking.
- **No `null` elements** (Reactive Streams rule) — use `Option`/`Optional`.

```scala
val sum: Future[Int] =
  Source(1 to 10).map(_ * 2).filter(_ > 5).runWith(Sink.fold(0)(_ + _))
val toFile: Sink[String, Future[IOResult]] =
  Flow[String].map(s => ByteString(s + "\n")).toMat(FileIO.toPath(path))(Keep.right)
```
```java
CompletionStage<Integer> sum =
  Source.range(1, 10).map(i -> i * 2).filter(i -> i > 5).runWith(Sink.fold(0, Integer::sum), system);
```

## Always-apply defaults

1. **Let back-pressure do the work** — don't add unbounded buffers or `Source.actorRef`/`Sink.actorRef` (no backpressure) when a back-pressured option exists (`Source.queue`, `*WithBackpressure`).
2. **Use `mapAsync(parallelism)(f: => Future)` for async/IO steps** (ordered, bounded in-flight = parallelism); `mapAsyncUnordered` only when order doesn't matter. Never block inside an operator — offload to a dedicated dispatcher.
3. **Insert `.async` boundaries deliberately** — operators are fused (one actor, sequential) by default; `.async` enables pipeline parallelism at a thread-crossing cost.
4. **Handle failures explicitly** — `recover`/`recoverWithRetries` for graceful endings, `RestartSource/Flow/Sink.withBackoff` for transient resource failures (with a `randomFactor` to avoid thundering herds), or a per-operator supervision strategy (`resume`/`restart`/`stop`).
5. **Consume or discard every entity/stream** — a partially-consumed substream or HTTP entity stalls the pipeline.
6. **Tie stream lifecycle to a `KillSwitch`** or normal completion rather than relying on abrupt actor-bound materializer termination.
7. **Prefer the operator catalog and GraphDSL over custom `GraphStage`s** — drop to a `GraphStage` only as a last resort.

## Anti-patterns (flag in review)

- Blocking inside `map`/`mapAsync` on the default dispatcher → thread starvation.
- Unbounded buffering, or `Source.actorRef`/`Sink.actorRef` where backpressure is needed.
- `Source.single(req).via(pool).runWith(Sink.head)` per request (materializes a stream each time) — feed a long-lived stream/queue instead.
- `mapAsyncUnordered` before a commit/ordered side effect (see [[alpakka]] Kafka at-least-once).
- Naive feedback cycles in a graph (bounded buffers → deadlock); break with `buffer(n, dropHead)` or `MergePreferred`.
- Reaching for a custom `GraphStage` when an operator/`GraphDSL`/`statefulMap` would do.
- Putting mutable state in a `GraphStage` (it must live in the per-materialization `GraphStageLogic`).

## How to use this skill

Detail lives in three references:

- **`references/basics-and-operators.md`** — the core types, materialized values & `Keep`, materialization/fusing/`.async`/ordering, and the **operator catalog** (simple, async `mapAsync`, rate-aware, substreams).
- **`references/graphs-rate-error.md`** — the **GraphDSL** (fan-in/out junctions, partial graphs, `BidiFlow`, cycles), **rate** operators (`buffer`/`conflate`/`expand`/`throttle`), **error handling** (`recover`, `RestartSource`, supervision), and **pipelining & parallelism** (`.async`, `Balance`/`Merge`).
- **`references/io-dynamic-actor-custom-testing.md`** — streaming **IO** (FileIO, TCP, Framing), **StreamRefs**, **dynamic** streams (`MergeHub`/`BroadcastHub`/`PartitionHub`, `KillSwitch`), **actor interop** (`ask` in a stream, `ActorSource`/`ActorSink`, `Source.queue`), custom **`GraphStage`**, and the **testkit** (`TestSource`/`TestSink`).

## Related

- [[akka]] — meta skill and module map.
- [[akka-actors]] — actor↔stream interop; the materializer runs on actors.
- [[alpakka]] — stream connectors (Kafka, S3, JDBC, …) built as Sources/Flows/Sinks.
- [[akka-http]], [[akka-grpc]] — HTTP/gRPC entities and bodies are streams.
- [[akka-persistence]] — Persistence Query exposes journals as `Source`s; [[akka-projections]] consume them.
- [[functional-programming]] — streams are pure, composable, value-based pipelines.
- Source: Akka Core docs, https://doc.akka.io/libraries/akka-core/current/stream/index.html (v2.10.x).
