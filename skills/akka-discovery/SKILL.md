---
name: akka-discovery
description: Akka Discovery (Akka Core 2.10.x, akka-discovery) in Scala and Java — a pluggable service-discovery SPI that decouples endpoint lookup from configuration, with built-in DNS, config, and aggregate methods (and Kubernetes/AWS/Consul via Akka Management). Use whenever resolving service endpoints at runtime, configuring how an app finds other services across environments, setting up Akka Cluster Bootstrap (automatic seed-node discovery), or pointing an Akka gRPC / Alpakka Kafka client at a discovered service — even if "discovery" isn't named but service location, DNS SRV lookup, or cluster bootstrap are involved.
---

# Akka Discovery

A small, pluggable **service-discovery SPI** (`akka-discovery`) that decouples *how* you find a service's endpoints from your code, so the same code resolves differently per environment. Built-in methods: **config** (static HOCON), **DNS** (A/AAAA + SRV), and **aggregate** (try several in order). [[akka]] Management adds Kubernetes, AWS EC2/ECS, Consul, and Marathon implementations. It underpins **Cluster Bootstrap** ([[akka-cluster]] formation without hardcoded seed-nodes) and is used by [[akka-grpc]] and [[alpakka]] Kafka clients.

Dependency: `"com.typesafe.akka" %% "akka-discovery" % AkkaVersion`. Cross-links: [[akka]] (meta), [[akka-cluster]], [[akka-grpc]], [[alpakka]].

## API

Load the `Discovery` extension to get a `ServiceDiscovery`, then `lookup`:

```scala
import akka.discovery.{Discovery, Lookup, ServiceDiscovery}
import scala.concurrent.duration._
val sd: ServiceDiscovery = Discovery(system).discovery
val resolved: Future[ServiceDiscovery.Resolved] =
  sd.lookup(Lookup("my-service").withPortName("remoting").withProtocol("tcp"), resolveTimeout = 3.seconds)
// or just: sd.lookup("my-service", 1.second)
// resolved.serviceName, resolved.addresses -> Seq[ResolvedTarget(host, port, address)]
```
```java
ServiceDiscovery sd = Discovery.get(system).discovery();
CompletionStage<ServiceDiscovery.Resolved> resolved =
  sd.lookup(Lookup.create("my-service").withPortName("remoting").withProtocol("tcp"), Duration.ofSeconds(3));
```

A `Lookup` has a mandatory `serviceName` and optional `portName`/`protocol` (used when one service exposes multiple ports). A `Resolved` holds a list of `ResolvedTarget(host, port, address)`.

## Methods (HOCON)

```hocon
# DNS — async-dns resolver; all three Lookup fields set => SRV query `_portName._protocol.serviceName`,
# otherwise an A/AAAA query on serviceName.
akka.discovery.method = akka-dns

# Config — static endpoints; ignores all Lookup fields but serviceName.
akka.discovery {
  method = config
  config.services {
    service1.endpoints = [ { host = "host1", port = 1233 }, { host = "host2", port = 1234 } ]
  }
}

# Aggregate — try methods in order, falling back when one yields nothing.
akka.discovery {
  method = aggregate
  aggregate.discovery-methods = ["akka-dns", "config"]
}
```

## When to use it

- **Cluster Bootstrap** — instead of hardcoding `akka.cluster.seed-nodes`, let Cluster Bootstrap (Akka Management) use Discovery (Kubernetes API, DNS SRV, etc.) to find the initial contact points and form the cluster. The main reason this module matters in production.
- **Client endpoint resolution** — point an [[akka-grpc]] client (`GrpcClientSettings.usingServiceDiscovery(...)`) or [[alpakka]] Kafka (`bootstrap.servers` via discovery) at a service by name.
- **Environment portability** — start with `config` in dev, switch to `kubernetes-api`/`aws-api` in prod by config alone, no code change.

## Gotchas

- A discovery method config entry must point to a config location under `akka.discovery` with at least a `class` (FQCN) property (since Akka Management 1.0.0; older bare-class-name form is incompatible).
- DNS discovery always uses Akka's native **async-dns** resolver regardless of `akka.io.dns.resolver`.
- SRV terminology mapping: SRV *service* = your `portName`, SRV *protocol* = `protocol`, SRV *name* = `serviceName`; Akka adds the `_` prefixes. SRV weights are currently ignored.

## Related

- [[akka]] — meta skill and module map.
- [[akka-cluster]] — Cluster Bootstrap uses Discovery to form a cluster automatically.
- [[akka-grpc]], [[alpakka]] — clients can resolve services via Discovery.
- Source: Akka Core docs, https://doc.akka.io/libraries/akka-core/current/discovery/index.html (v2.10.x).
