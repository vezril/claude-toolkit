# Provider dialects: the same Gremlin, different answers

A query that works on TinkerGraph is portable Gremlin *syntax*. Whether it gives the same *results* and *performance* depends on the provider. Check these first.

## Comparison

| Behaviour | TinkerGraph | Amazon Neptune | Azure Cosmos DB (Gremlin API) | JanusGraph |
|---|---|---|---|---|
| Submission | bytecode + scripts | bytecode + ANTLR-parsed scripts (no Groovy) | **scripts only** (no bytecode) | bytecode + scripts |
| Serializer | GraphBinary / GraphSON | GraphBinary / GraphSON (Gryo removed) | **GraphSON v2 only** | GraphBinary / GraphSON |
| Recommended driver line | match the server | match the engine's TinkerPop version | **3.4.13** (3.5/3.6 have known issues) | match the server |
| IDs | any, configurable | **strings** (user-supplied or generated) | strings, unique with the partition key | long by default (custom configurable) |
| Default cardinality | `single` | **`set`** | **`list`** (`set` unsupported) | per-schema (`SINGLE` default) |
| Lambdas | yes (embedded/Groovy) | no | no | yes via Groovy scripts (don't) |
| `mergeV`/`mergeE`, string and date steps | per TinkerPop version | per engine version (check the engine release notes for its TinkerPop version) | **no** (old step set; use `fold/coalesce/unfold`) | per TinkerPop version |
| `match()` | yes | yes | **no** | yes |
| Transactions | TinkerTransactionGraph only | one traversal = one tx; bytecode `tx()`; 10-minute sessions | **none**; use optimistic concurrency | yes (backend-dependent) |
| Indexing | none by default (`createIndex` on TinkerGraph) | automatic internal indexes; anchor on IDs or labels plus properties | **everything auto-indexed** | explicit composite, mixed and vertex-centric indexes |
| Execution order | depth-first | depth-first-ish, with a DFE engine for some queries | **breadth-first** | depth-first |

## Amazon Neptune

The details are in [[aws-neptune]]. The ones that change query results:
- `property('k', v)` **adds** a value (set cardinality). Write `property(single,'k',v)` for scalars.
- Multiple labels are written `Label1::Label2`. `hasLabel('A::B')` matches nothing.
- An `addV` with an existing ID and a *new* label adds the label to the existing vertex instead of failing.
- There's no `materializeProperties`, so project properties explicitly.
- `io()` is read-only. `program()` and lambdas aren't supported.
- Mutations can throw `ConcurrentModificationException` under contention, so retry idempotent writes.

## Azure Cosmos DB for Apache Gremlin

- **Scripts only**, GraphSON v2, drivers on 3.4.x. Build query strings safely, and prefer parameter bindings where your driver supports them against Cosmos.
- **Partitioned graphs:** every vertex carries the partition key property. Include it in lookups (`g.V(['pk','id'])` or `has('pk', …)`) or the query fans out across partitions. Edges live with their source vertex's partition.
- Old step set: no `mergeV`/`mergeE`, no string or date steps, no `match()`, no lambdas. `store()` is still listed, and Cosmos has its own `executionProfile()`.
- No `null` values, no object-valued properties, and no sorting by array properties.
- **Only the first `V()` in a traversal uses the index.** A mid-traversal `V()` doesn't, so wrap the second lookup in `map(__.V()…)` or `union(...)` instead.
- **Breadth-first execution**, so `limit()` placement and early-termination assumptions from depth-first engines may not save work.
- **No transactions.** Use the account's consistency level and optimistic concurrency (`_etag`-style) for conflicting writes. Cost is in **RUs**, so profile to keep queries index-served.
- Microsoft's own page now steers new high-scale work to Cosmos DB for NoSQL, and OLAP or Gremlin migrations to *Graph in Microsoft Fabric*. Check the service's roadmap before starting a new Cosmos Gremlin project.

## JanusGraph

- **You design the indexes**, and queries only use them if they match:
  - **Composite** indexes serve **equality only** on *all* their keys (`has('name','x').has('age',30)` for an index on `(name, age)`; not `has('age',30)` alone).
  - **Mixed** indexes (Elasticsearch, Solr or Lucene) serve ranges, full-text (`textContains`) and geo, in any key combination.
  - **Vertex-centric** indexes serve edge filters on dense vertices (`outE('battled').has('time', inside(10,50))`), respecting key order.
- Without a usable index, JanusGraph does a **full scan** and warns. Set `query.force-index=true` in production to make that an error.
- Index new keys *before* data arrives, or reindex. Define the schema (property keys with cardinality and data type, edge labels with multiplicity) up front, with `schema.default=none` to stop accidental auto-creation.
- Transactions are real but backend-dependent (Cassandra/ScyllaDB are eventually consistent). Use JanusGraph locking or consistency modifiers where uniqueness matters.

## TinkerGraph

- The in-memory reference graph: correct semantics and full step support. Use it for query logic and unit tests.
- Default cardinality `single`, any ID type (configurable ID managers). `TinkerTransactionGraph` (3.7+) adds transactions.
- There are no indexes unless you `createIndex(key, Vertex.class)`, so performance on TinkerGraph says nothing about production performance.

## Porting checklist

1. Driver and serializer versions match the target.
2. IDs: type and generation strategy (string vs long; user-supplied allowed?).
3. Cardinality: add `single`/`list` explicitly everywhere.
4. Steps: remove lambdas, check `mergeV`, string and date steps, `match()`, `io()` and `subgraph()` support.
5. Transactions: one-traversal-per-transaction is the safe assumption, plus retries.
6. Indexing: the anchors hit the target's indexes (JanusGraph schema, Cosmos partition key, Neptune IDs).
7. Re-run `profile()` (or the provider's equivalent) on real data volumes.
