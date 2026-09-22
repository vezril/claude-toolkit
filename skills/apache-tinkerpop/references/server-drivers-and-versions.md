# Drivers, Gremlin Server, providers and versions

## Gremlin Language Variants (GLVs)

Official GLVs exist for **Java, Python, JavaScript, .NET and Go**. They all build traversals natively and send them to a server with `DriverRemoteConnection`. The 3.8 reference uses `traversal().with(...)`, where older code has `withRemote(...)`:

```java
// Java
GraphTraversalSource g = traversal().with(DriverRemoteConnection.using("localhost", 8182, "g"));
```
```python
# Python (gremlinpython). with_remote works across 3.x; check your version's docs for the newer form
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
g = traversal().with_remote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))
```
```javascript
// JavaScript (gremlin npm)
const g = traversal().with(new DriverRemoteConnection('ws://localhost:8182/gremlin'));
```
```csharp
// .NET (Gremlin.Net)
var g = Traversal().With(new DriverRemoteConnection(new GremlinClient(new GremlinServer("localhost", 8182))));
```

- Close connections on shutdown, and reuse one client per process (they're pooled).
- Over a remote connection, returned vertices and edges are **references** (id and label only). Use `valueMap`, `elementMap`, `project` or `values` to get properties.
- **Lambdas** are for embedded or Groovy-script use only. Most remote providers refuse them, and 4.0's server disables Groovy by default.

## Serialization

- **GraphBinary** is the compact binary default for the drivers. Prefer it.
- **GraphSON** (v1–v3, typed or untyped JSON) is for HTTP clients, debugging and interchange. For readable HTTP results, use untyped GraphSON 3 (`application/vnd.gremlin-v3.0+json;types=false`).
- **Gryo** (Kryo-based) was removed in 3.6.0.
- Client and server must agree on the serializer and version. Mismatches cause most "cannot deserialize" errors.

## Transactions

- **Embedded (JVM):** transactions are ThreadLocal. `g.tx().commit()` / `rollback()`. You can configure `onReadWrite` (AUTO/MANUAL) and `onClose` (COMMIT/ROLLBACK/MANUAL).
- **Remote:** by default **one traversal is one transaction**, committed on success. For multi-traversal transactions, where the provider supports them:
  ```java
  GraphTraversalSource gtx = g.tx().begin();
  try {
    gtx.addV("person").property("name", "ada").iterate();
    gtx.addV("person").property("name", "grace").iterate();
    gtx.tx().commit();
  } catch (Exception e) { gtx.tx().rollback(); }
  ```
- Check `graph.features().graph().supportsTransactions()`. TinkerGraph's plain in-memory graph doesn't support transactions (a transactional variant exists in newer versions). Providers differ: Neptune, for example, supports bytecode transactions but not `tx()` on text scripts.

## Gremlin Server

The standalone server that hosts graphs and runs traversals for remote clients. It's configured in YAML (`conf/gremlin-server.yaml`). The keys you'll touch most:
- `host`, `port` (8182)
- `graphs` (name → properties file)
- `scriptEngines` (in 4.0 these act as an allowlist, and Groovy is off by default)
- `serializers`
- `evaluationTimeout` (renamed `timeoutMillis` in 4.0)
- `channelizer` (WebSocket and/or HTTP in 3.x)
- `authentication` / `authorization`
- SSL settings

Deployment hygiene:
- Enable authentication and TLS.
- Restrict or disable script engines, because arbitrary Groovy is remote code execution.
- Set a timeout.
- Put `ReadOnlyStrategy` on read-only traversal sources.

**Gremlin Console** is the interactive Groovy REPL. It works locally (TinkerGraph, with `TinkerFactory.createModern()` for the classic "modern" toy graph) or remotely (`:remote connect tinkerpop.server conf/remote.yaml`, then `:>` to submit).

**3.8 additions:** a Gremlin **MCP server** (and a Gremlint MCP server for formatting queries), the **Air Routes** sample dataset, and `propertyMap()`.

## Providers (TinkerPop-enabled systems)

Listed on tinkerpop.apache.org/providers (the listing isn't an endorsement):
- **OLTP databases:** JanusGraph (distributed OLTP and OLAP over Cassandra, HBase, ScyllaDB and others), **Amazon Neptune**, Azure Cosmos DB (Gremlin API), Aerospike Graph, ArcadeDB, ArangoDB, OrientDB, Alibaba Graph Database, HGraphDB (HBase), ChronoGraph (versioned), Bitsy, OverflowDB, Sqlg (SQL-backed)
- **Reference and OLAP:** TinkerGraph (in-memory), Hadoop-Gremlin with SparkGraphComputer
- Neo4j-Gremlin is **deprecated**

Before choosing or porting, check each provider's supported TinkerPop version, ID types, default cardinality, meta-property and multi-property support, transaction model, step coverage, and whether it accepts scripts, bytecode or both.

## 3.8.0 breaking changes (2025-11-12)

- **Java 11 minimum.**
- **Removed:** `store()`, `aggregate(Scope)`, `has(key, traversal)`, `P.getOriginalValue()`.
- **`repeat()`:** consistent global-children semantics, and `limit`/`skip`/`range` inside it count per iteration. `cap()` and `inject()` are no longer allowed inside `repeat()`.
- **`choose()`:** only the first matching option runs, and unmatched traversers pass through.
- **`local()`:** splits bulked traversers for true per-object semantics.
- **`group`, `groupCount`, `tree`, `subgraph`** are now local barriers.
- **Mid-traversal `mergeV`/`mergeE`** output the created or matched element.
- **Type defaults:** `OffsetDateTime` replaces `java.util.Date`, and floats default to `Double`. `dateDiff()` returns milliseconds. `split("")` returns characters. `asString()` rejects `null`. `range`/`limit`/`tail` with `local` scope always return collections.
- **Grammar:** `new` is optional, `withoutStrategies()` is supported, and there are restrictions on `Map` keys.

Re-run your test suite against 3.8 before upgrading a provider or driver, especially traversals that use `repeat`, `choose` or `local`.

## 4.0 (beta, 4.0.0-beta.3, 2026-07-20)

- **HTTP only.** WebSockets are gone from Gremlin Server.
- **`Bytecode` is replaced by `GremlinLang`:** each GLV produces a **canonical Gremlin string plus named parameters**, parsed server-side by the same ANTLR grammar. Payloads become human-readable.
- **Sessions are removed.** Remote **transactions are explicit over HTTP** in all GLVs: `begin()` (idempotent, replaces `open()`) and managed blocks like `g.executeInTx(...)`. **Closing a transaction now defaults to rollback**, not commit.
- **Groovy is disabled by default.** Server initialization is declarative YAML, and script engines are an allowlist.
- **Renames:** "bindings" become "parameters", and `evaluationTimeout` becomes `timeoutMillis`. GLV connection options are standardized (`maxConnections`, `connectTimeoutMillis` (default 5 s), `readTimeoutMillis`, compression on by default). Custom serializers move from `CustomTypeSerializer` to `@ProviderDefined`.
- Multi-label vertices are optional for providers (TinkerGraph supports them).

**Migration posture:** 4.0 is a preview. Managed providers move on their own schedule, so stay on the provider's supported 3.x line until it announces 4.0 support. New code can get ready now: avoid lambdas and Groovy scripts, use parameters instead of string concatenation, and write explicit transaction handling that doesn't assume commit-on-close.
