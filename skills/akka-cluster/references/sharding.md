# Cluster Sharding & Sharded Daemon Process

Akka Cluster (2.10.x). Dependency `akka-cluster-sharding-typed`. Source: doc.akka.io/libraries/akka-core/current/typed/{cluster-sharding,cluster-sharding-concepts,cluster-sharded-daemon-process}.html

## Cluster Sharding

Distributes **entities** (actors identified by a stable id) across cluster nodes; you interact by id without knowing where the entity lives. The standard home for [[akka-persistence]] aggregates — sharding guarantees a **single active instance per entityId** (the single-writer principle event sourcing needs). Use it when you have more stateful actors than fit on one machine, or need that single-writer guarantee.

**Concepts:** a `ShardRegion` runs on each (matching-role) node. Messages are grouped into **shards** (by `shardId`); the **ShardCoordinator** (a Cluster Singleton on the oldest node) decides which region hosts each shard. First message to a shard consults the coordinator; afterward routing is direct. `number-of-shards` is fixed (≈10× max nodes), identical on all nodes.

**Init (call on every node):**
```scala
import akka.cluster.sharding.typed.scaladsl.{ClusterSharding, Entity, EntityTypeKey}
val TypeKey = EntityTypeKey[Counter.Command]("Counter")
val sharding = ClusterSharding(system)
val region = sharding.init(Entity(TypeKey)(ctx => Counter(ctx.entityId)))
```
```java
EntityTypeKey<Counter.Command> typeKey = EntityTypeKey.create(Counter.Command.class, "Counter");
ClusterSharding sharding = ClusterSharding.get(system);
sharding.init(Entity.of(typeKey, ctx -> Counter.create(ctx.getEntityId())));
```
The behavior factory is local-only → safe to inject node-local refs / non-serializable objects. Restrict to nodes with a role via `Entity(TypeKey)(...).withRole("backend")`.

**Send messages — via `EntityRef` (preferred) or a `ShardingEnvelope`:**
```scala
val ref: EntityRef[Counter.Command] = sharding.entityRefFor(TypeKey, "counter-1")
ref ! Counter.Increment
val res: Future[Counter.Value] = ref.ask(Counter.GetValue(_))(askTimeout)
// or: region ! ShardingEnvelope("counter-1", Counter.Increment)
```
```java
EntityRef<Counter.Command> ref = sharding.entityRefFor(typeKey, "counter-1");
ref.tell(Counter.Increment.INSTANCE);
```
Commands and `EntityRef`s must be serializable; an `EntityRef` needs a custom serializer (serialize `entityId` + `typeKey.name`).

**Passivation** — stop idle entities to save memory; messages arriving during passivation are buffered and redelivered to the new incarnation. Automatic by default (idle strategy; the recommended `default-strategy` is active-entity-limit based). Manual: set a stop message and have the entity request passivation:
```scala
ClusterSharding(system).init(Entity(TypeKey)(ctx =>
  Counter(ctx.shard, ctx.entityId)).withStopMessage(Counter.GoodBye))
// inside entity, on idle: ctx.shard ! ClusterSharding.Passivate(ctx.self)
```

**Remember entities** — auto-restart entities after rebalance/crash (without it, an entity restarts only on its next message). Enabling **disables automatic passivation**. Store modes: `ddata` (default; LMDB on disk) or `eventsourced` (for disk-less envs like k8s without PVs). Entity *state* is restored only if the entity is persistent.

**Shard allocation & rebalancing** — default `shardId = abs(entityId.hashCode) % number-of-shards`; default `LeastShardAllocationStrategy` rebalances toward new/under-loaded nodes (tune `rebalance-absolute-limit`/`rebalance-relative-limit`). On handoff, entities are stopped (via `stopMessage`) and recreated on the new node — **state is not migrated, so make it persistent**. Alternatives: `ExternalShardAllocationStrategy` (e.g. co-locate with Kafka partitions), `ConsistentHashingShardAllocationStrategy` (co-locate related entity types).

**Stores:** the mandatory **state store** (shard locations) is `ddata` by default. **Lease** (`akka.cluster.sharding.use-lease`) adds extra safety against duplicate shards. Inspect with `GetShardRegionState`/`GetClusterShardingStats` (monitoring only). Message ordering is preserved per ShardRegion (at-most-once); for at-least-once use Reliable Delivery.

```hocon
akka.cluster.sharding {
  number-of-shards = 1000
  passivation.default-idle-strategy.idle-entity.timeout = 2 minutes
}
```

## Sharded Daemon Process

Runs a **fixed number N of actors** (ids `0..N-1`), kept alive and balanced across the cluster by keep-alive pings from a singleton. The standard way to run a set of long-lived workers — e.g. N tagged projection workers for CQRS read-sides ([[akka-persistence]], [[akka-projections]]).

```scala
ShardedDaemonProcess(system).init("TagProcessors", tags.size, id => TagProcessor(tags(id)))
```
```java
ShardedDaemonProcess.get(system).init(
  TagProcessor.Command.class, "TagProcessors", tags.size(), id -> TagProcessor.create(tags.get(id)));
```
Same `init` on every node; address the workers via the Receptionist. `initWithContext` returns an `ActorRef[ShardedDaemonProcessCommand]` that accepts `ChangeNumberOfProcesses` for dynamic rescaling. Settings: `keep-alive-interval`, `role`. Scales to thousands of processes.
