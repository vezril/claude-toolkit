# Alpakka Kafka — deep reference

Alpakka Kafka 8.0.x (kafka-clients 4.x). Source: doc.akka.io/libraries/alpakka-kafka/current/{producer,consumer,atleastonce,transactions}.html. Dependency `com.typesafe.akka %% akka-stream-kafka`.

## Settings

Built from a `Config` section + programmatic `.withX`. Consumer config in code: deserializers, `groupId`; cluster-wide bits via `application.conf` config inheritance.

```scala
val consumerSettings = ConsumerSettings(cfg, new StringDeserializer, new ByteArrayDeserializer)
  .withBootstrapServers("localhost:9092").withGroupId("group1")
  .withProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest")
val producerSettings = ProducerSettings(pcfg, new StringSerializer, new StringSerializer)
  .withBootstrapServers("localhost:9092")
```
Key consumer config: `enable.auto.commit = false` (default), `stop-timeout` (set 0 with DrainingControl), `commit-timeout`, recommend `partition.assignment.strategy = CooperativeStickyAssignor`. `CommitterSettings`: `maxBatch = 1000`, `maxInterval = 10s`, `parallelism = 100`.

## Consumer sources

- `plainSource` — raw `ConsumerRecord`, no Kafka offset support. Pair with `Subscriptions.assignmentWithOffset(tp -> offset)` to resume from externally stored offsets (true exactly-once if offset+result stored atomically in your DB), or `enable.auto.commit = true`.
- `committableSource` — emits `CommittableMessage` (`.record`, `.committableOffset`); process then commit via `Committer.sink`/`flow` → **at-least-once**.
- `atMostOnceSource` — commits before processing; emits the value → **at-most-once** (slow; prefer plainSource+auto-commit for relaxed needs).
- `committablePartitionedSource` / `plainPartitionedSource` — emit `(TopicPartition, Source)`; merge (`flatMapMerge`) or run a stream per partition for parallelism (substream completes on revoke).
- `sourceWithOffsetContext` — offset carried in the stream context (use with `Committer.sinkWithOffsetContext`).

All materialize a `Consumer.Control`; use `DrainingControl` (`DrainingControl.apply` / `Consumer::createDrainingControl`) and `drainAndShutdown()`.

## Producer stages

Envelopes (`ProducerMessage`): `single(record, passThrough)`, `multi(records, passThrough)`, `passThrough(passThrough)` (commit without producing). `passThrough` typically carries the `CommittableOffset`.

- `Producer.plainSink(producerSettings)` — consume raw `ProducerRecord`, materialize `Future[Done]`.
- `Producer.flexiFlow(producerSettings)` — consume `Envelope`, emit `Results` (continue the stream); supports a shared producer + pass-through.
- `Producer.committableSink(producerSettings, committerSettings)` — produce **and** commit the source offsets (the consume-transform-produce at-least-once pipeline).

```scala
Consumer.committableSource(consumerSettings, Subscriptions.topics("in"))
  .map(msg => ProducerMessage.single(new ProducerRecord("out", msg.record.key, msg.record.value), msg.committableOffset))
  .toMat(Producer.committableSink(producerSettings, committerSettings))(DrainingControl.apply).run()
```
Share a `KafkaProducer` (thread-safe) across streams via `producerSettings.withProducer(p)` (faster; set `close-on-producer-stop = false`; cannot share with transactions).

## At-least-once subtleties

- **Multiple effects per message** → use `MultiMessage` and commit only after all produced.
- **Batches** (`grouped`/`groupedWithin`) → commit the `CommittableOffsetBatch` only after the whole batch; associate it with the *last* message.
- **Multiple destinations / side effects** → chain in series or `alsoTo`+`zip` to rejoin, committing only after all complete.
- **Ordering** → `mapAsync` (preserves order), never `mapAsyncUnordered`; `groupBy`+`mergeSubstreams` reorders. Prefer `mapAsyncPartitioned`.
- **Bad messages** → consume as `byte[]`, deserialize in a `map`, emit `PassThroughMessage(offset)` to skip without producing (can't early-commit bad offsets — earlier good ones may be in flight).

## Transactions (exactly-once)

`Transactional.source` → `Transactional.flow`/`sink` give exactly-once for consume-transform-produce **within one Kafka cluster** (KIP-98). The source emits `TransactionalMessage` (carries `.partitionOffset`); the framework handles commits (not the user). Forces `isolation.level = read_committed` and `enable.idempotence = true`. On rebalance the consumer drains + commits in `onPartitionsRevoked`. **Cannot share the producer.**

```scala
val control = Transactional.source(consumerSettings, Subscriptions.topics("in"))
  .via(businessFlow)
  .map(msg => ProducerMessage.single(new ProducerRecord("out", msg.record.key, msg.record.value), msg.partitionOffset))
  .toMat(Transactional.sink(producerSettings))(DrainingControl.apply).run()
```
Recovery: transient errors (network, `ProducerFencedException`) abort the txn and tear down the stream — wrap in `RestartSource.onFailuresWithBackoff` (lift the `Control` out via an `AtomicReference`). Caveat: EOS does **not** cover external DB writes or other side effects, nor cross-cluster.

## Rebalance & cluster integration

Partitioned sources auto-track assignment; react to assign/revoke via the rebalance listener (a classic `ActorRef` receiving `TopicPartitionsAssigned`/`Revoked`). Integrate with [[akka-cluster]] sharding (align Kafka partitions with shard allocation via a custom `ShardingMessageExtractor`) and with [[akka-projections]] (`akka-projection-kafka`'s `KafkaSourceProvider` — offsets in the projection offset store, the idiomatic CQRS read-side). Defer `bootstrap.servers` to [[akka-discovery]] via `service-name`.
