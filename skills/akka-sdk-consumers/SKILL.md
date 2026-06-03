---
name: akka-sdk-consumers
description: Akka SDK Consumers (Java) — components that consume a stream of events/changes (from Event Sourced Entities, Key Value Entities, Workflows, another Akka service's stream, or a Kafka/Google Pub-Sub topic) and optionally produce to a topic or service stream. Covers defining a Consumer (extend Consumer, @Consume.FromEventSourcedEntity/FromKeyValueEntity/FromWorkflow/FromTopic/FromServiceStream, the effects().produce/done/ignore API), producing out (@Produce.ToTopic/ToServiceStream), brokerless service-to-service eventing, at-least-once delivery and the need for deduplication, CloudEvents metadata, and testing. Use to react to entity/workflow changes, integrate with Kafka/PubSub, propagate events between services, or build projections to external systems in an Akka SDK service. Part of the Akka SDK (Java); see akka-sdk for the model and akka-sdk-views for in-service read models.
---

# Akka SDK — Consumers

A **Consumer** consumes a stream of events/changes and optionally **produces** to a topic or service stream. Sources: [[akka-sdk-event-sourced-entities]] journals, [[akka-sdk-key-value-entities]] state changes, [[akka-sdk-workflows]] state, another Akka service's stream, or a **Kafka / Google Pub-Sub** topic. The way to react to changes, do eventing in/out, and propagate events between services. Part of the [[akka-sdk]] (Java).

Cross-links: [[akka-sdk]] (meta), [[akka-sdk-views]] (in-service read models), [[alpakka]] (the Core Kafka library), [[akka-projections]].

## Defining a consumer

```java
@Component(id = "counter-events-consumer")
@Consume.FromEventSourcedEntity(CounterEntity.class)
public class CounterEventsConsumer extends Consumer {
  public Effect onEvent(CounterEvent event) {
    return switch (event) {
      case CounterEvent.ValueIncreased v  -> { /* side effect via ComponentClient/HttpClient */ yield effects().done(); }
      case CounterEvent.ValueMultiplied v -> effects().ignore();   // skip this one
    };
  }
}
```

Effect API: `effects().done()` (processed OK), `effects().ignore()` (skip), `effects().produce(payload[, metadata])` (publish, when annotated `@Produce.*`). Every consumer needs `@Component(id)`. Sources:
- `@Consume.FromEventSourcedEntity(X.class)` — handle events (exceptions → redelivery; add `@SnapshotHandler` to start from snapshots on long histories).
- `@Consume.FromKeyValueEntity(X.class)` — receive the **most recent** state (not necessarily every change); optional `@DeleteHandler`.
- `@Consume.FromWorkflow(X.class)` — workflow state changes.
- `@Consume.FromTopic("name")` — broker messages (CloudEvents; handler chosen by `ce-type`; `byte[]` param for binary).
- `@Consume.FromServiceStream(service = "...", id = "...")` — another Akka service's published stream.

## Producing out

```java
@Component(id = "counter-journal-to-topic")
@Consume.FromEventSourcedEntity(CounterEntity.class)
@Produce.ToTopic("counter-events")
public class CounterToTopic extends Consumer {
  public Effect onEvent(CounterEvent e) { return effects().produce(e); }
}
```
- `@Produce.ToTopic("name")` publishes to Kafka/PubSub; set the CloudEvent subject (`ce-subject`) in metadata to preserve per-entity ordering.
- `@Produce.ServiceStream(id = "...")` + `@Acl(allow = @Acl.Matcher(service = "*"))` does **brokerless service-to-service eventing** (no Kafka needed): transform internal events to a public API type, `ignore()` what you don't expose; consumers use `@Consume.FromServiceStream`.

## Always-apply defaults

1. **All delivery is at-least-once → handle duplicates** — the SDK does **not** dedup automatically; make updates idempotent or track sequence numbers.
2. **Transform internal events to public types when producing** (don't leak internal models across a service boundary); `ignore()` events you don't expose.
3. **For per-entity ordering in a topic**, set `ce-subject` from `messageContext().eventSubject()` in the produced metadata.
4. **Use a [[akka-sdk-views]] view, not a consumer, for in-service queryable read models**; use consumers to project to *external* systems or other services.
5. **Don't fail on events you don't care about** — `ignore()` them; only let real processing errors propagate (they trigger redelivery).
6. **Externalize source/topic names** with `${VAR}` where they vary by environment (changing a resolved name restarts the consumer from the start of the stream).

## Anti-patterns (flag in review)

- Assuming exactly-once / no duplicates (it's at-least-once — dedup yourself); non-idempotent side effects without dedup.
- Relying on a KV-entity consumer to observe every intermediate change (only the latest is guaranteed).
- Publishing internal event/state types to a topic or other service; building an in-service query model with a consumer instead of a [[akka-sdk-views]] view.

## Testing

`TestKitSupport` with `TestKit.Settings.DEFAULT.withTopicIncomingMessages("...").withTopicOutgoingMessages("...")`; publish via `testKit.getTopicIncomingMessages(name).publish(cmd, subjectId)` and assert with `getTopicOutgoingMessages(name).expectOneTyped(Type.class)`. Or run the Google Pub-Sub emulator for ITs. Run topic tests sequentially / clear between tests.

## Related

- [[akka-sdk]] · [[akka-sdk-event-sourced-entities]] · [[akka-sdk-key-value-entities]] · [[akka-sdk-workflows]] · [[akka-sdk-views]]
- [[alpakka]] (Core Kafka connector) · [[akka-projections]] (Core projections / read sides).
- Source: https://doc.akka.io/sdk/consuming-producing.html
