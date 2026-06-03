# Artery remoting, Split Brain Resolver, Coordination & Reliable Delivery

Akka Cluster (2.10.x). Source: doc.akka.io/libraries/akka-core/current/{remoting-artery,remote-security,split-brain-resolver,coordination,typed/reliable-delivery}.html

## Artery remoting

Cluster is built on Artery remoting (use Cluster, not raw remoting). Location-transparent: a remote `ActorRef` is used exactly like a local one. Transports (`akka.remote.artery.transport`): `tcp` (default), `tls-tcp` (TLS), `aeron-udp` (high-throughput/low-latency, no encryption). Every node needs a unique, globally reachable `canonical.hostname:port` (part of its address); for NAT/Docker also set `bind.*`.

Delivery: at-most-once for normal messages (dropped during partitions/overflow). **System messages** (remote death-watch, deployment) are exactly-once; if undeliverable the association is **quarantined** (recover only by restarting that ActorSystem). Cluster members aren't quarantined merely by the failure detector (that can heal).

**TLS** (firewall first; never expose plain remoting to untrusted networks):
```hocon
akka.remote.artery {
  transport = tls-tcp
  ssl.config-ssl-engine {
    key-store = "/path/keystore.jks"
    trust-store = "/path/truststore.jks"
    key-store-password = ${SSL_KEY_STORE_PASSWORD}
    protocol = "TLSv1.2"
    enabled-algorithms = [TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256]
    hostname-verification = on
  }
}
```
Mutual authentication is on by default; every node needs both key- and trust-store. (See [[akka-serialization]] — enable a non-Java serializer, and security applies there too.)

## Split Brain Resolver (SBR) — required

Partitions and crashes are indistinguishable (also from GC pauses). Naive "auto-down on timeout" on both sides forms **two clusters** → duplicate singletons and duplicate persistent entities writing the same stream (fatal). Akka by default does *not* auto-remove unreachable nodes, so you **must** configure a downing provider:

```hocon
akka.cluster.downing-provider-class = "akka.cluster.sbr.SplitBrainResolverProvider"
akka.cluster.split-brain-resolver {
  active-strategy = keep-majority
  stable-after = 20s          # wait for stable membership before deciding (size to cluster)
}
akka.coordinated-shutdown.exit-jvm = on
```
Always pair SBR with auto-restart of downed nodes (SBR may down more nodes than strictly necessary, even all).

**Strategies:**
- **`keep-majority`** (default) — keep the majority side; ties broken by lowest address. Best for dynamic node counts.
- **`static-quorum`** — keep the side with ≥ `quorum-size` reachable nodes; for **fixed** node counts. Don't exceed `quorum-size*2 - 1` total members.
- **`keep-oldest`** — keep the partition with the oldest member (where the ShardCoordinator/singleton runs); `down-if-alone` handles the isolated-oldest case.
- **`lease-majority`** — only the side that acquires a distributed **lease** (e.g. Kubernetes lease) survives. Safest (external arbiter) but adds an infra dependency.
- **`down-all`** — down everyone (for very unstable networks; not for clusters > 10).

Also: `down-all-when-indirectly-connected` (handles partial connectivity), `down-all-when-unstable`, and `akka.cluster.down-removal-margin` (defaults to `stable-after`; ensures a new singleton/shard isn't started before the old is stopped — critical for single-writer persistence). Expected failover ≈ detection (~5s) + `stable-after` + `down-removal-margin` (~45s with 100-node defaults; ~25s for ~10 nodes).

## Coordination — Lease

`akka-coordination` is a pluggable distributed-lock API: same lease name = same lease, one owner at a time, reentrant for that owner. Used by SBR (`lease-majority`), Cluster Singleton, and Cluster Sharding.

```scala
val lease = LeaseProvider(system).getLease("my-lease", "akka.coordination.lease.kubernetes", ownerName)
val acquired: Future[Boolean] = lease.acquire()
if (lease.checkLease()) doCriticalThing()    // synchronous check
lease.release()
```
```java
Lease lease = LeaseProvider.get(system).getLease("my-lease", "akka.coordination.lease.kubernetes", owner);
CompletionStage<Boolean> acquired = lease.acquire();
```
Tune `heartbeat-timeout` (> max JVM pause), `heartbeat-interval`, `lease-operation-timeout`. Implementation today: Kubernetes API lease.

## Reliable Delivery

Adds at-least-once / effectively-once delivery **plus consumer-driven flow control** (the producer never outruns consumer demand → no mailbox-overflow OOM). Confirmation is a business concern (the consumer confirms after processing). Three patterns:

- **Point-to-point** — `ProducerController` ↔ `ConsumerController` (producer/consumer must be local to their controllers). Producer gets `RequestNext` (permission to send one), consumer gets `Delivery` and replies `Confirmed`.
- **Work pulling** — one `WorkPullingProducerController` → many dynamically-registered workers (via a `ServiceKey`); order must not matter.
- **Sharding** — `ShardingProducerController` (one per node) → `ShardingConsumerController` (one per entity); send to any `entityId`. Module `akka-cluster-sharding-typed`.

Semantics: no crashes → effectively-once; with a **durable producer queue** (`EventSourcedProducerQueue` from `akka-persistence-typed`) → at-least-once across producer restarts; consumer/worker crash or shard rebalance → unconfirmed messages redelivered. Large messages can be chunked (point-to-point only).
