---
name: apache-tinkerpop
description: "Apache TinkerPop and the Gremlin graph traversal language, distilled from the TinkerPop reference, upgrade notes and recipes at tinkerpop.apache.org (fetched 2026-09; stable 3.8.2, maintenance 3.7.7, 4.0.0-beta.3). Covers the architecture: the Structure API that providers implement vs the Process API users write against; the Gremlin traversal machine embedded, behind Gremlin Server, or inside a remote provider; OLTP traversals vs OLAP GraphComputer. Covers the property graph model (vertex properties with cardinality single/set/list and meta-properties) and how a traversal works: traversal source g, lazy traversers, map/flatMap/filter/sideEffect/branch steps, anonymous __ traversals, by()/as()/option() modulators, barriers, path, sack. Includes the step catalogue (navigation, has/where/is with P and TextP predicates, project/select/valueMap/elementMap, group/groupCount/fold/unfold, repeat/until/emit/times, choose/coalesce/optional/union, mergeV/mergeE upserts with Merge.onCreate/onMatch/outV/inV, explain/profile), traversal strategies (PartitionStrategy, SubgraphStrategy, ReadOnlyStrategy, SeedStrategy), and the Gremlin Language Variants (Java, Python, JavaScript, .NET, Go) connecting with DriverRemoteConnection. Also covers GraphBinary vs GraphSON, embedded vs remote transactions (g.tx()), why lambdas are discouraged, recipes and anti-patterns, the 3.8.0 breaking changes (Java 11, repeat/choose/local semantics, removed store() and aggregate(Scope)), and 4.0 (HTTP-only server, GremlinLang strings replacing bytecode, sessions removed, transactions defaulting to rollback, Groovy off by default). Use when writing, reviewing, debugging or optimizing Gremlin queries, choosing or connecting a TinkerPop-enabled database (JanusGraph, Neptune, Cosmos DB, Aerospike Graph, ArcadeDB), configuring Gremlin Server, upgrading across 3.7/3.8/4.0, or translating between Gremlin and Cypher/SPARQL."
license: MIT
---

# Apache TinkerPop and Gremlin

TinkerPop is a **vendor-neutral graph computing framework**. Its query language, **Gremlin**, is a functional, data-flow traversal language: you describe a walk through the graph as a chain of steps, and the **Gremlin traversal machine** executes it. Any database that implements TinkerPop's interfaces (a *provider*) runs the same Gremlin, which is the portability pitch. Each provider supports a slightly different subset and set of defaults, which is the portability catch. Distilled from `tinkerpop.apache.org` (reference, upgrade notes, recipes, providers), fetched 2026-09.

Cross-links:
- [[gremlin]]: writing queries day to day (cookbook, semantics pitfalls, per-language syntax, provider dialects). This skill is the framework around it.
- [[graph-databases]]: model and language choices, and Gremlin vs Cypher/GQL/SPARQL.
- [[aws-neptune]]: the most common managed Gremlin target, and its documented deviations.
- [[functional-programming]]: Gremlin's lazy, composable pipeline style.
- [[secure-coding]]: script submission and injection.

## Versions (as of 2026-09)

| Line | Latest | Status |
|---|---|---|
| **3.8.x** | 3.8.2 (2026-09-01) | Current stable. **Java 11+**; experimental JDK 21/25 |
| **3.7.x** | 3.7.7 (2026-09-01) | Maintenance |
| **4.0** | 4.0.0-beta.3 (2026-07-20) | Public preview. Protocol and API breaking, see `references/server-drivers-and-versions.md` |

Match the **driver version to the server/provider's TinkerPop version**. Most "weird serialization error" bugs are a version mismatch.

## Architecture in one screen

```
Structure API (providers implement)   Graph · Vertex · Edge · VertexProperty · Property · Features
Process API   (users write)           GraphTraversalSource g  →  GraphTraversal (steps)  →  traversers

Where the traversal machine runs:
  embedded        JVM app with the graph in-process (e.g. TinkerGraph); lambdas allowed
  Gremlin Server  remote over WebSocket or HTTP (4.0: HTTP only); drivers send traversals, get results
  remote provider managed service speaking the Gremlin protocol (Neptune, Cosmos DB, …)

OLTP: traversals from a few start points, real time
OLAP: GraphComputer / VertexProgram over the whole graph (e.g. SparkGraphComputer via Hadoop-Gremlin)
```

**TinkerGraph** is the in-memory reference graph. Use it for tests, prototypes and teaching. Its default vertex-property cardinality is `single` (`gremlin.tinkergraph.defaultVertexPropertyCardinality`).

## How to think in Gremlin

- A traversal is **lazy**. Nothing runs until a **terminal step**: `toList()`, `next()`, `iterate()`, `hasNext()`, `tryNext()`. Mutations with no terminal step silently do nothing, so end write traversals with `iterate()`.
- **Traversers** carry an object plus metadata (path, loop count, sack, bulk) through the steps. Steps come in five shapes:
  - **map** (1→1): `values`, `id`, `project`
  - **flatMap** (1→many): `out`, `properties`, `unfold`
  - **filter** (1→0 or 1): `has`, `where`, `is`, `dedup`
  - **sideEffect** (passes through): `aggregate`, `property`, `drop`
  - **branch**: `choose`, `union`, `coalesce`, `repeat`
- **Modulators** configure the step before them:
  - `by()`: which key or traversal to use for `order`, `group`, `project`, `path`, `dedup`
  - `as()`: labels a step for `select` and `where`
  - `option()`: cases for `choose`, and create/match behaviour for `mergeV`/`mergeE`
- **Anonymous traversals** `__.out()` (plain `out()` in most GLVs once statically imported) are the child traversals inside `where()`, `repeat()`, `coalesce()` and so on.
- **Barriers** (`fold`, `count`, `order`, `group`, `aggregate`, `dedup` in some positions) collect everything before continuing, which matters for memory on large traversals.

```groovy
// Top 5 people Marko's friends know that Marko doesn't
g.V().has('person','name','marko').as('m').
  out('knows').aggregate('friends').
  out('knows').where(neq('m')).where(without('friends')).
  groupCount().by('name').
  order(local).by(values, desc).limit(local, 5)
```

## Non-negotiables

1. **Anchor every traversal.** Start from an ID (`g.V(id)`) or a **label plus indexed property** (`g.V().has('person','email',x)`). A bare `g.V().has('name',x)` is a full scan on most providers (an anti-pattern in TinkerPop's recipes).
2. **Bound every loop:** `repeat(...).times(n)` or `until(...)` together with `simplePath()` or `loops().is(lt(n))`. Cycles plus an unbounded `repeat` equals a runaway.
3. **Upsert with `mergeV`/`mergeE`** (3.6+). Use `fold().coalesce(unfold(), addV(...))` only on providers older than that. Plain `addV` in a retry loop creates duplicates.
4. **Don't use lambdas** (`map{ it.get()... }`, `filter{}`). They reduce portability, can't be optimized, and are refused by most remote providers and by 4.0's default server. There's almost always a step-based equivalent.
5. **Send traversals, not string scripts.** Build traversals with a GLV. If you must send strings, never splice user input into them. Pass it as parameters, or validate it: a script is code.
6. **Know your provider's deviations:** ID types, default cardinality, supported steps, transaction model, and max request size. For example, Neptune uses string IDs and defaults to `set` cardinality with no lambdas (see [[aws-neptune]]). Check the provider's `Features` or compatibility doc before porting.
7. **Treat `profile()` as the performance tool.** `explain()` shows how strategies rewrote the traversal. `profile()` shows where the time and traverser counts went.
8. **Pin the version and read the upgrade notes.** 3.8.0 changed `repeat()`, `choose()`, `local()`, `mergeV`/`mergeE` mid-traversal output, and date and float defaults. 4.0 changes the wire protocol. "Same query, different results" after an upgrade usually has a documented cause.

## References

- `references/gremlin-steps.md`: the step catalogue by category, predicates (`P`, `TextP`), cardinality, `mergeV`/`mergeE` in full, string, date and number steps, terminal steps, and strategies.
- `references/patterns-and-anti-patterns.md`: recipes (get-or-create, shortest path, cycles, pagination, recommendation, trees, duplicate detection), the official anti-patterns, performance habits, and Gremlin ↔ Cypher translation.
- `references/server-drivers-and-versions.md`: GLV connection code (Java, Python, JS, .NET, Go), serialization, embedded vs remote transactions, Gremlin Server configuration, the provider landscape, the 3.8.0 breaking changes, and the 4.0 migration.
