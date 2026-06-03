# Cluster Singleton, Distributed Data & Distributed Pub-Sub

Akka Cluster (2.10.x). Dependency `akka-cluster-typed`. Source: doc.akka.io/libraries/akka-core/current/typed/{cluster-singleton,distributed-data,distributed-pub-sub}.html

## Cluster Singleton

Exactly one instance of an actor runs cluster-wide (or per role), on the **oldest** member; on graceful leave there's a hand-over to the new oldest. Use **sparingly** — it's a bottleneck and a single point of failure, and a split brain (no SBR) produces **one singleton per partition**. Add a **Lease** for extra safety against duplicates.

```scala
val singleton = ClusterSingleton(system)
val proxy: ActorRef[Counter.Command] = singleton.init(
  SingletonActor(Behaviors.supervise(Counter()).onFailure[Exception](SupervisorStrategy.restart), "GlobalCounter"))
proxy ! Counter.Increment
```
```java
ClusterSingleton singleton = ClusterSingleton.get(system);
ActorRef<Counter.Command> proxy = singleton.init(SingletonActor.of(Counter.create(), "GlobalCounter"));
proxy.tell(Counter.Increment.INSTANCE);
```
`init` returns a proxy that routes to the current instance and buffers messages while it's unavailable (at-most-once — add your own ack/retry). Use `.withStopMessage(...)` so the instance can finish/close resources during hand-over. Lease: `akka.cluster.singleton.use-lease` (for typed, set the lease name programmatically via `ClusterSingletonSettings.withLeaseSettings`).

## Distributed Data — replicated CRDTs

Shares **eventually-consistent** data across nodes using **CRDTs** (conflict-free replicated data types) that always merge deterministically. Tunable read/write consistency. Not for big data: ≤ ~100k top-level entries, all in memory.

CRDT types: `GCounter` (grow-only), `PNCounter` (inc/dec), `GSet`, `ORSet` (observed-remove, add-wins), `ORMap`/`ORMultiMap`/`PNCounterMap`/`LWWMap`, `LWWRegister` (last-writer-wins, needs synced clocks), `Flag`.

```scala
import akka.cluster.ddata._
import akka.cluster.ddata.typed.scaladsl.{DistributedData, Replicator}
implicit val node: SelfUniqueAddress = DistributedData(system).selfUniqueAddress
val Key = ORSetKey[String]("cart")
// update (modify fn must be PURE — runs in the Replicator):
replicatorAdapter.askUpdate(
  replyTo => Replicator.Update(Key, ORSet.empty[String], Replicator.WriteMajority(5.seconds), replyTo)(_ :+ item),
  InternalUpdateResponse.apply)
// read:
replicatorAdapter.askGet(replyTo => Replicator.Get(Key, Replicator.ReadMajority(5.seconds), replyTo), …)
```

**Consistency levels** — Write: `WriteLocal`, `WriteTo(n)`, `WriteMajority`, `WriteMajorityPlus`, `WriteAll`; Read: `ReadLocal`, `ReadFrom(n)`, `ReadMajority`, `ReadMajorityPlus`, `ReadAll`. A read is strongly consistent iff `writeNodes + readNodes > N`; you always read your own writes. Subscribe with `Replicator.Subscribe(key, ...)` → `Changed`. **Durable storage** is off by default (memory + replication); enable LMDB via `akka.cluster.distributed-data.durable.keys = ["*"]`. Beware tombstones from deleted keys (use expiry / ORSet add-remove).

## Distributed Pub-Sub — `Topic`

Publish/subscribe across the cluster. The `Topic` API is in `akka-actor-typed` but only distributes when clustered. **At-most-once** delivery; subscriber registry is eventually consistent; one network hop per node regardless of subscriber count.

```scala
import akka.actor.typed.pubsub.{PubSub, Topic}
val pubSub = PubSub(system)
val topic: ActorRef[Topic.Command[Msg]] = pubSub.topic[Msg]("my-topic")
topic ! Topic.Subscribe(subscriber)
topic ! Topic.Publish(Msg("hi"))
// TTL: pubSub.topic[Msg]("t", 3.minutes) stops the topic if idle
```
```java
PubSub pubSub = PubSub.get(system);
ActorRef<Topic.Command<Msg>> topic = pubSub.topic(Msg.class, "my-topic");
topic.tell(Topic.subscribe(subscriber));
topic.tell(Topic.publish(new Msg("hi")));
```
Scales to tens of thousands of topics (each = one Receptionist key). For at-least-once cross-node delivery use Alpakka Kafka ([[alpakka]]) or Reliable Delivery.
