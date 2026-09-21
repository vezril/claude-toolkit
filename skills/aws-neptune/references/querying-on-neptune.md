# Querying Neptune: Gremlin, openCypher, SPARQL

For language fundamentals and cross-language translation, see [[graph-databases]] `references/query-languages.md`. This file covers only what's Neptune-specific.

## Transports

| Language | Endpoint | Notes |
|---|---|---|
| Gremlin | `wss://host:8182/gremlin` (drivers), `https://host:8182/gremlin` (HTTP POST `{"gremlin": "…"}`) | TinkerPop GLV drivers default to GraphBinary, so leave that alone. Over HTTP, prefer `application/vnd.gremlin-v3.0+json;types=false`. Gryo is gone |
| openCypher | `https://host:8182/openCypher` (form or JSON `query=`, `parameters=`), or **Bolt** on 8182 | Neptune follows the openCypher 9 spec. Use Bolt read-write sessions only when you need them, because they run all queries at mutation isolation on the writer |
| SPARQL | `https://host:8182/sparql` | SPARQL 1.1 Query and Update. `SERVICE` federation is supported. `UPDATE LOAD` from a URI works only inside the VPC (S3 needs a VPC endpoint) |

With IAM auth on, every request must be SigV4-signed (`service=neptune-db`). See `security.md`.

## Gremlin on Neptune: differences that bite

- **Text scripts only contain Gremlin.** Every statement starts with `g`. There's no Groovy or Java: no `x = 1; g.V(x)`, no `1+1`, no `System.nanoTime()`, no Java method calls. Multiple statements are separated by `;` or a newline, and all but the last need `.iterate()` or `.next()`. **Bytecode** (GLV) submissions aren't restricted this way.
- **No variables, bindings or parameterization** in scripts, and no need for them. Neptune parses with the ANTLR grammar, so the Gremlin Server advice about plan-cache parameterization doesn't apply. It's safe to inline literals (still validate untrusted input so users can't alter the traversal; see [[secure-coding]]).
- **Enum arguments use short forms:** `single`, `set`, `asc`, `desc`, `local`, `global`, `keys`, `values`, `IN`, `OUT`, `BOTH`. Fully qualified Java class names aren't accepted.
- **IDs are strings.** You can supply your own (`g.addV('person').property(id, 'p-123')`). Otherwise Neptune generates a non-RFC UUID-shaped string. A vertex and an edge may share an ID. `addV` with an existing ID fails, *unless* the label is new, in which case it **adds the label** to the existing vertex (`label1::label2`).
- **Multiple labels** use `::` (`g.addV('Person::Employee')`). You can't match `hasLabel('A::B')`.
- **Vertex property cardinality defaults to `set`.** `property('age', 30)` then `property('age', 31)` leaves **both** values. Use `property(single, 'age', 31)` to replace. `list` cardinality isn't supported, and edge properties are always single. When one graph is also queried with openCypher (single-valued properties), write with `single` consistently.
- **Transactions:** one traversal is one transaction, and a multi-statement script is one transaction. There's no `tx.commit()` or `tx.rollback()` for scripts. **Sessions** are capped at **10 minutes** and run reads at mutation isolation on the writer.
- **Unsupported:** lambda steps, `program()`, `io()` writes (reads work, via a presigned S3 HTTPS URL), `materializeProperties` (elements come back as references with id and label only, so project properties explicitly with `valueMap()`, `elementMap()` or `project()`), meta-properties, and `graph`/`Computer` features.
- **DFE engine:** `neptune_dfe_query_engine=viaQueryHint` (the default) means Gremlin uses DFE only with `g.with('Neptune#useDFE', true)`. Profile both ways before switching globally.

## openCypher on Neptune vs Neo4j

Production-ready since engine **1.1.1.0**. It always runs on the DFE engine.

| Neo4j habit | On Neptune |
|---|---|
| `LOAD CSV` | Use the **bulk loader** (`format: opencypher`), or AWS Glue/ETL then the loader |
| APOC procedures | Not available. Rewrite in openCypher or Gremlin (AWS has a rewrites guide), use AWS services (Glue, OpenSearch), or use Neptune Analytics for algorithms |
| Custom procedures or UDFs | Not supported. Do it in the application |
| `CREATE CONSTRAINT` / indexes | Not available. The **only constraint is ID uniqueness**. Put business keys in the ID (`~id`), with composites like `'123_SEA'` |
| Multi-database, Fabric | **One graph per cluster**. No property-graph federation. SPARQL `SERVICE` exists for RDF only |
| RBAC | IAM policies with `neptune-db:*` actions and condition keys |
| Bookmarks / causal consistency | Not available. Send read-your-writes to the **writer** |
| Geospatial types | Not native. Pair with Amazon OpenSearch |
| Graph Data Science | **Neptune Analytics** |
| Neo4j Browser / Bloom | graph-notebook (Jupyter), Graph Explorer and third-party tools |
| Spring Data Neo4j | Not compatible. The Neo4j Spark connector works over Bolt |

- Neptune node and relationship IDs are strings, reachable as `id(n)` or with the special `~id` property in patterns (`MATCH (n {`~id`: 'p-1'})`).
- Always use parameters (`parameters={"name": "Alice"}`) for untrusted input.
- AWS's migration tooling includes `neo4j-to-neptune` (export and convert), plus the "Rewriting Cypher queries to run in openCypher on Neptune" guide.

## SPARQL notes

- The default graph is `http://aws.amazon.com/neptune/vocab/v01/DefaultNamedGraph` unless a quad or named graph is given.
- Multiple update operations in one POST (separated by `;`) form **one atomic transaction**.
- There's no automatic RDFS/OWL inference engine, so materialize the inferences you need, or use query-time property paths.

## Transactions, isolation and retries

| Query kind | Isolation | Where |
|---|---|---|
| Read-only (SPARQL SELECT/ASK/CONSTRUCT/DESCRIBE; Gremlin without mutating steps; openCypher reads) | **Snapshot isolation** (MVCC, no locks, never blocks writers) | writer or replicas |
| Mutation (Gremlin with `addV`/`addE`/`property`/`drop`; SPARQL INSERT/DELETE; openCypher writes) | **READ COMMITTED plus range locks**, which prevent non-repeatable and phantom reads | writer only |
| Gremlin sessions, Bolt read-write sessions | mutation isolation for every query | writer |

- **Conflicts:** a writer that hits another transaction's lock waits up to **60 s** and then rolls back. A detected **deadlock** rolls back one transaction immediately (the one with fewer inserted or deleted records).
- **False conflicts:** gap locks cover gaps between index records, so unrelated inserts can collide. So can a retry that races the rollback of its own previous attempt. AWS cites **3–4% of writes** failing this way under high load.
- **Retry pattern:** catch `ConcurrentModificationException` (and timeouts), back off exponentially with jitter, and **make writes idempotent** (use `MERGE` in openCypher, or `fold().coalesce(unfold(), addV(...))` in Gremlin, with supplied IDs) so a retry can't duplicate data.
- **Reduce contention:** keep write batches small (a few hundred to a few thousand elements per transaction), avoid many writers touching the same hot vertex (a supernode: see [[graph-databases]]), and run bulk mutations off-peak or through the bulk loader.
- **Diagnose:** in slow-query log `debug` mode (≥ 1.4.5.0), `sharedLocksWaitTimeMillis` and `exclusiveLocksWaitTimeMillis` show lock waits. If they're close to `overallRunTimeMs`, the bottleneck is contention, not compute.

## Performance checklist

- Start traversals from an ID (`g.V('id')`, `MATCH (n {`~id`: $id})`) or a selective label and property. Neptune has no user-defined secondary indexes, so broad property scans are expensive.
- Bound repetition (`times()`, `*1..4`), `LIMIT` exploratory queries, and project only the properties you need.
- Use `explain` and `profile` (Gremlin `/gremlin/profile`, openCypher and SPARQL explain modes) before tuning anything.
- Separate workloads with **custom endpoints** (analytics readers vs app readers).
- For whole-graph algorithms, export to **Neptune Analytics**. Don't run them as giant OLTP traversals.
