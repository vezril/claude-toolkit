---
name: alpakka
description: Alpakka (current) and Alpakka Kafka in Scala and Java — Reactive Streams connectors that integrate external systems as Akka Streams Sources/Flows/Sinks (the backpressure-aware alternative to Camel). Covers the connector model and the breadth of connectors (Kafka, AWS S3/SQS/SNS/Kinesis/DynamoDB, Cassandra, Slick/JDBC, File, CSV, JSON, Google Cloud/Pub-Sub, MQTT, AMQP, FTP, Elasticsearch, …) and goes deep on Alpakka Kafka (ConsumerSettings/ProducerSettings, Consumer.plainSource/committableSource/atMostOnceSource/partitioned sources, Committer.sink + batched commits, Producer.plainSink/flexiFlow/committableSink, at-least-once vs at-most-once vs transactional exactly-once, rebalance handling, DrainingControl). Use whenever integrating an external system as a stream, consuming/producing Kafka from Akka, building reactive data pipelines, or choosing delivery semantics for Kafka — even if "Alpakka" isn't named but stream connectors, Kafka consumers/producers, or reactive integration in an Akka app are involved. Built on akka-streams.
---

# Alpakka & Alpakka Kafka

Alpakka is a library of **Reactive Streams connectors** built on [[akka-streams]] — each external technology is exposed as `Source`s (ingest), `Flow`s (round-trip), and `Sink`s (emit), all backpressure-aware. It's the modern, type-safe alternative to Apache Camel for streaming integration. **Alpakka Kafka** is the most-used connector and gets the deep treatment here.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Cross-links: [[akka]] (meta), [[akka-streams]], [[akka-cluster]], [[akka-projections]].

**Dependency gotcha:** Alpakka connectors are `com.lightbend.akka %% akka-stream-alpakka-<name>`, but **Alpakka Kafka is `com.typesafe.akka %% akka-stream-kafka`**. Keep all `akka-*` versions aligned.

## The connector model

Every connector is a set of Akka Streams stages plus a `Settings` object (programmatic `.withX(...)` + HOCON defaults in each JAR's `reference.conf`). Materialization needs an `ActorSystem`. Examples: `FileTailSource.lines(...)`, `CsvParsing.lineScanner()`, `S3.getObject(bucket, key)` (`Source[ByteString, …]`) / `S3.multipartUpload(...)` (`Sink`), `Slick.source(query)` / `Slick.sink(toStmt)` / `Slick.flowWithPassThrough(...)`.

```scala
Source.single(ByteString("a,b,c\n1,2,3\n"))
  .via(CsvParsing.lineScanner())
  .via(CsvToMap.toMapAsStrings())
  .runWith(Sink.seq)   // Seq(Map("a"->"1", "b"->"2", "c"->"3"))
```

**Notable connectors:** Kafka, AWS (S3, SQS, SNS, Kinesis/Firehose, DynamoDB, Lambda, EventBridge), Google Cloud (Storage, BigQuery, Pub/Sub, Pub/Sub gRPC, FCM), Azure Storage, Cassandra, Slick/JDBC, MongoDB, Couchbase, Elasticsearch/OpenSearch, Solr, HBase, InfluxDB, AMQP (RabbitMQ), MQTT, JMS, Pulsar, File, FTP/SFTP, HDFS, Avro Parquet, UDP, and data transforms (CSV, JSON framing, XML, compression, text).

## Alpakka Kafka — always-apply defaults

1. **`enable.auto.commit` defaults to false** in Alpakka Kafka — manage offsets explicitly (`committableSource` + `Committer.sink`).
2. **Batch commits** via `Committer.sink`/`CommitterSettings` (per-message commits are slow); larger batches mean more reprocessing on failure.
3. **Use `mapAsync` (ordered), never `mapAsyncUnordered`, before committing** — committing out of order can skip un-processed offsets.
4. **Pick delivery semantics deliberately:** `committableSource` + `Committer` = at-least-once (idempotent handler); `atMostOnceSource` = at-most-once; `Transactional.*` = exactly-once but only consume→produce within **one** Kafka cluster (no external side effects).
5. **Use `Consumer.DrainingControl`** (`DrainingControl.apply` / `Consumer::createDrainingControl` in `toMat`) and `drainAndShutdown()` for clean shutdown; set `stop-timeout = 0`.
6. **Prefer `CooperativeStickyAssignor`** (Kafka 3.0+) to avoid stop-the-world rebalances.

## Alpakka Kafka — core patterns

```scala
val consumerSettings = ConsumerSettings(system.settings.config.getConfig("akka.kafka.consumer"),
    new StringDeserializer, new ByteArrayDeserializer)
  .withBootstrapServers("localhost:9092").withGroupId("group1")

// at-least-once: process then batch-commit
Consumer.committableSource(consumerSettings, Subscriptions.topics("topic"))
  .mapAsync(10) { msg => business(msg.record.key, msg.record.value).map(_ => msg.committableOffset) }
  .toMat(Committer.sink(CommitterSettings(system)))(DrainingControl.apply)
  .run()
```
```java
Consumer.committableSource(consumerSettings, Subscriptions.topics("topic"))
  .mapAsync(1, msg -> business(msg.record().key(), msg.record().value()).thenApply(d -> msg.committableOffset()))
  .toMat(Committer.sink(CommitterSettings.create(system)), Consumer::createDrainingControl)
  .run(system);
```

Consumer sources: `plainSource` (external offset storage / auto-commit), `committableSource` (manual commit → at-least-once), `atMostOnceSource` (commit before process), `committablePartitionedSource` (per-partition substreams for parallelism), `sourceWithOffsetContext`. Producer stages: `Producer.plainSink`, `Producer.flexiFlow` (envelope `single`/`multi`/`passThrough` + pass-through value), `Producer.committableSink` (produce **and** commit source offsets — the consume-transform-produce at-least-once pipeline). Transactions: `Transactional.source` → `Transactional.sink` (exactly-once consume→produce; forces `read_committed` + idempotent producer; wrap in `RestartSource.onFailuresWithBackoff` for recovery).

Full detail (settings, partitioned sources, at-least-once subtleties, transactions, rebalance handling, cluster integration) in **`references/kafka.md`**.

## Anti-patterns (flag in review)

- Relying on Kafka auto-commit when you need at-least-once; per-message commits in a hot path.
- `mapAsyncUnordered` before commit; committing the wrong offset for batched/multi-destination processing.
- Expecting `Transactional.*` to cover external DB writes or cross-cluster (it doesn't).
- Forgetting `DrainingControl` → lost in-flight commits on shutdown.
- Hand-rolling `committableSource` + `Committer` to build a CQRS read-side when [[akka-projections]] (Kafka source provider) is the idiomatic fit.

## Related

- [[akka]] — meta skill and module map.
- [[akka-streams]] — connectors are Sources/Flows/Sinks; all stream operators apply.
- [[akka-cluster]] — co-locate Kafka partition consumption with cluster-sharded entities; cluster-aware consumers.
- [[akka-projections]] — `akka-projection-kafka` consumes Kafka as a projection with offset tracking (preferred over hand-rolled commits for read-sides).
- Source: Alpakka docs https://doc.akka.io/libraries/alpakka/current/ and Alpakka Kafka https://doc.akka.io/libraries/alpakka-kafka/current/.
