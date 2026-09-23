---
name: aws-neptune
description: "Amazon Neptune, AWS's managed graph database family, distilled from docs.aws.amazon.com (fetched 2026-09). Covers the two products and when to use which: Neptune Database (OLTP; one writer + up to 15 read replicas on a shared 3-AZ cluster volume up to 128 TiB; provisioned or Serverless in NCUs up to 128/256 GB; Standard vs I/O-Optimized storage; Global Database with up to 5 secondary regions) and Neptune Analytics (in-memory, sized in m-NCUs, 25+ openCypher-callable algorithms, one HNSW vector index per graph, the store behind Bedrock Knowledge Bases GraphRAG). Also covers the data models and languages (property graph via Gremlin and openCypher over the same data, RDF via SPARQL, never mixed); Neptune's Gremlin quirks (string IDs only, set cardinality by default, no lambdas or Groovy, no variables or bindings, 10-minute sessions); openCypher vs Neo4j gaps (no APOC, LOAD CSV, schema constraints beyond ID uniqueness, or custom procedures; one graph per cluster); transaction semantics (snapshot isolation for reads, range-locked READ COMMITTED for mutations, 60 s lock-wait, ConcurrentModificationException retries); the S3 bulk loader (Gremlin CSV, openCypher CSV, RDF formats, 64 queued jobs); Neptune Streams (1–90 day change log, no native Lambda trigger); VPC-only TLS 1.2 access with IAM SigV4 auth and neptune-db ReadDataViaQuery/WriteDataViaQuery/DeleteDataViaQuery actions; parameters like neptune_query_timeout (default 120 s); and engine lifecycle (1.4.8.0 latest; all 1.2.x and 1.1.1.0 end of life 2026-12-04). Use when designing, building, loading, querying, securing, operating, or costing a Neptune deployment, migrating from Neo4j, choosing Neptune Database vs Analytics, wiring GraphRAG on AWS, or debugging Neptune errors (ConcurrentModificationException, timeouts, loader failures, connection limits)."
license: MIT
---

# Amazon Neptune

Neptune is **two products under one name**. **Neptune Database** is a transactional graph database built like Aurora: one writer, read replicas, and a shared multi-AZ storage volume. **Neptune Analytics** is a separate, in-memory engine for whole-graph algorithms and vector search. Most Neptune confusion comes from treating them as one thing, or from assuming Neptune behaves like Neo4j or a stock Gremlin Server. It doesn't, in documented ways. Distilled from `docs.aws.amazon.com`, fetched 2026-09.

Cross-links:
- [[graph-databases]]: model and language fundamentals. Read it first if "should this be a graph?" is still open.
- [[apache-tinkerpop]]: standard Gremlin, which this skill describes the Neptune deviations from.
- [[opencypher]]: standard openCypher, which Neptune's openCypher deviates from (see the Neo4j gaps below).
- [[aws-s3]]: bulk-load source.
- [[aws-lambda]]: Streams consumers, which poll because there's no native trigger.
- [[aws-aurora]]: the same cluster, replica and endpoint mental model.
- [[aws-rds]]: shared account limits.
- [[nx-neptune]]: the awslabs Python library that drives Neptune Analytics from NetworkX or from data-lake tables via Athena.
- [[secure-coding]]: the IAM and KMS posture.
- [[vault-graphrag]]: GraphRAG concepts.

## The mental model

```
Neptune Database  (OLTP, VPC-only, HTTPS/WSS on port 8182)
  cluster = 1 primary (read/write) + up to 15 replicas (read-only)
            └─ all share ONE cluster volume: 3 AZs, grows to 128 TiB
  endpoints: cluster (writer) · reader (load-balanced replicas) · instance · custom
  data: property graph  ── Gremlin  (/gremlin, WebSocket or HTTP)
                        └─ openCypher (/openCypher HTTPS, or Bolt)   ← same data, both languages
        OR RDF          ── SPARQL (/sparql)                          ← separate; never shared with PG
  compute: provisioned db.r*/x2g/t* instances, or Serverless (NCUs), mixable per instance
  extras: bulk /loader from S3 · Streams change log · Global Database · Neptune ML · full-text search via OpenSearch

Neptune Analytics  (OLAP/exploration, in-memory, separate service "neptune-graph")
  one graph = memory sized in m-NCUs (1 m-NCU ≈ 1 GB); load from S3 or a Neptune Database
  openCypher + CALL neptune.algo.*  (pathfinding, centrality, similarity, community, vectors)
  one vector index per graph (HNSW, fixed dimension ≤ 65,535, set at creation)
  optional public endpoint · backs Amazon Bedrock Knowledge Bases GraphRAG
```

## Non-negotiables

1. **Pick the product by workload.** Request-time traversals and transactional writes go to **Database**. PageRank, Louvain, connected components, or vector similarity over the whole graph go to **Analytics**. Neptune Database has no in-engine algorithm library, and Analytics is not a system of record for OLTP.
2. **Pick the data model once, per cluster.** Gremlin and openCypher share one property graph. SPARQL sees only RDF. You can't query property-graph data with SPARQL, or the reverse. There's also **one graph per cluster**: multi-tenancy means a `tenantId` property that every query must include, or one cluster per tenant (Serverless makes that practical).
3. **It's VPC-only and TLS 1.2-only**, on port 8182. Nothing outside the VPC connects without a bastion, VPN, load balancer or proxy. The DB subnet group needs subnets in at least 2 AZs; use 3.
4. **Turn on IAM database authentication.** Neptune has no username/password auth. Without IAM auth, anything that reaches the endpoint on the network can query it. With IAM auth, every request is SigV4-signed (`--service neptune-db`). Scope permissions with `ReadDataViaQuery` / `WriteDataViaQuery` / `DeleteDataViaQuery`. Any `property()` step or openCypher `SET` needs all three.
5. **Retry mutations.** Mutations take **range (gap) locks**. A blocked transaction waits up to **60 s** and then rolls back, and a detected deadlock rolls one side back immediately. AWS says about **3–4% of writes can fail from false conflicts under high load**. Handle `ConcurrentModificationException` with exponential backoff and keep write transactions small.
6. **Send read-your-writes to the writer.** Replicas run snapshot isolation and are eventually consistent (usually under 100 ms, but not guaranteed). A read that must see a just-committed write goes to the **cluster endpoint**.
7. **Set `neptune_query_timeout` deliberately.** The default is 120,000 ms. An unbounded traversal on a **Serverless** instance scales compute up while it runs, so a high timeout plus a runaway query is a billing incident. Bound every variable-length path.
8. **Gremlin on Neptune is not Gremlin Server.** IDs are **strings only**. Vertex properties default to **set** cardinality, so use `property(single, 'k', v)` to overwrite. There are no lambdas, no Groovy, no script variables or bindings, no `tx.commit()`, and `io()` is read-only. Scripts parse with the ANTLR grammar, so you don't need to parameterize for plan caching.
9. **openCypher on Neptune is not Neo4j.** It lacks APOC, `LOAD CSV`, custom procedures, geospatial types, and schema constraints beyond ID uniqueness. Load through the bulk loader. Encode composite uniqueness into the ID (`'123_SEA'`).
10. **Mind the engine lifecycle.** All **1.2.x and 1.1.1.0 reach end of life on 2026-12-04**. After that, clusters are force-upgraded in a maintenance window. The current line is 1.4.x, and 1.4.8.0 (2026-07-27) is the latest release.

## Quick reference

| Item | Value |
|---|---|
| Read replicas per cluster | 15 (16 in a Global Database secondary) |
| Cluster volume max | 128 TiB (64 TiB in China and GovCloud) |
| Storage replication | 3 AZs in one region |
| Global Database | up to 5 secondary regions, typically under 1 s lag, writes only in the primary |
| Serverless | engine ≥ 1.2.0.1; up to 128 NCU = 256 GB; scales in 0.5 NCU steps; no lookup cache |
| Storage types | Standard (pay per I/O) vs I/O-Optimized (`iopt1`, engine ≥ 1.3.0.0, no I/O charges, higher instance and storage price); switch at most once per 30 days |
| HTTP request payload max | 150 MB (Gremlin and SPARQL over HTTP; not WebSockets) |
| Property/label value max | 55 MB; no null characters in strings |
| WebSocket connections | 32,768 on large and serverless instances, 512 on t3/t4g.medium; idle close after 20–25 min; IAM-auth sockets dropped after ~10 days |
| Gremlin sessions | 10 minutes max |
| `neptune_query_timeout` | 10 ms – 2³¹-1 ms, default 120,000 ms |
| Lock-wait timeout | 60 s |
| Bulk loader | 64 queued jobs; tracks the last 1,024 jobs; 10,000 errors per job; the loader is **non-ACID** |
| Streams retention | default 7 days, 1–90 via `neptune_streams_expiry_days` (≥ 1.2.0.0) |
| Neptune Analytics vector index | 1 per graph, dimension 1–65,535, defined at graph creation |

## References

- `references/database-architecture-and-ops.md`: clusters, endpoints, instance classes, Serverless, storage types and billing, Global Database, backups, parameters, logs, engine versions and upgrades, cost levers.
- `references/querying-on-neptune.md`: the HTTP/Bolt/WebSocket endpoints, Gremlin differences, openCypher vs Neo4j and migration rewrites, SPARQL notes, transaction isolation, locks and retry patterns, DFE engine, explain and profile.
- `references/loading-streams-and-integration.md`: the bulk loader (formats, CSV headers, parameters, modes, failure handling), Neptune Streams, full-text search via OpenSearch, export, and AWS integrations.
- `references/security.md`: VPC and TLS posture, IAM database auth and SigV4 clients, data-access actions and policies, KMS encryption, audit logs.
- `references/neptune-analytics.md`: when to use it, m-NCU sizing, loading, the algorithm catalogue and `CALL` syntax, vector search and its non-atomic updates, and Bedrock Knowledge Bases GraphRAG.
