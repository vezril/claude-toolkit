---
name: graph-databases
description: Graph databases — when a graph is the right data model and how to use one well. Covers the two data models (labeled property graph vs RDF triple/quad stores) and what separates them; index-free adjacency and native vs non-native storage (and why the O(1)-per-hop pitch is narrower than it sounds); graph OLTP databases vs graph compute/analytics engines; the query languages and where each stands in 2026 — Cypher/openCypher, ISO GQL (ISO/IEC 39075:2024), SQL/PGQ (ISO/IEC 9075-16:2023, graph queries over relational tables), Gremlin (Apache TinkerPop), SPARQL (W3C; RDF/SPARQL 1.2 still in progress); modeling (nodes vs properties vs relationships, reifying relationships into nodes, supernodes, edge direction, time), the honest graph-vs-relational decision; and the product landscape (Neo4j, Amazon Neptune, Spanner Graph, Memgraph, JanusGraph, ArangoDB, TigerGraph, FalkorDB, Apache AGE, RDF stores) with 2025–26 changes like the Kuzu archive and PostgreSQL 19's SQL/PGQ revert. Use when choosing a graph database or deciding whether you need one, modeling a domain as a graph, writing or translating Cypher/GQL/Gremlin/SPARQL/SQL-PGQ queries, reviewing a graph schema, or reasoning about knowledge graphs and GraphRAG storage — even if "graph database" isn't named but the problem is deep relationship traversal (social, fraud rings, recommendations, dependency/lineage, network topology, identity/access graphs).
---

# Graph Databases

A **graph database** stores data as **nodes** (entities), **edges** (relationships) and **properties** (attributes on either), and treats relationships as stored, first-class data rather than something you reconstruct at query time with joins. The payoff is multi-hop traversal ("friends of friends who bought X", "every service downstream of this one") that stays fast and readable as depth grows. The cost is a smaller, less standardized ecosystem, and weaker performance on bulk set-oriented work where relational engines excel.

Grounded in Wikipedia's *Graph database* article plus the primary sources listed at the bottom (fetched 2026-09). Cross-links: [[software-architecture]] (choosing a data store is an architecture decision; record it as an ADR), [[domain-driven-design]] (the domain model you're about to draw as nodes and edges), [[cqrs-event-sourcing]] (a graph is often a *read model* projected from events, not the system of record), [[vault-graphrag]] (a knowledge graph over notes: GraphRAG without a graph DB), [[gcp-spanner]] (Spanner Graph), [[aws-neptune]] (Neptune Database and Neptune Analytics in depth), [[apache-tinkerpop]] (Gremlin and the TinkerPop stack in depth), [[opencypher]] (writing Cypher 9 queries in depth, with the openCypher style guide), [[python-networkx]] (in-memory graph analysis in Python when you don't need a database), [[aws-rds]] (the relational baseline to beat).

## First question: do you actually need a graph database?

Reach for one when **the relationships are the query**: variable or unbounded depth (`-[:REPORTS_TO*]->`), path finding, pattern matching across many hops, a highly connected domain whose shape keeps changing. Typical fits are fraud rings, recommendations, identity and access graphs, network and IT topology, supply chain and lineage, knowledge graphs, and social graphs.

Stay relational when the data is **flat or shallow**, the work is **set-oriented** (aggregates over millions of rows, reporting), or one or two joins answer everything. Wikipedia's own criticism section says it plainly: studies found an RDBMS "comparable in performance" to graph engines on graph queries, and a graph database shouldn't be picked on model grounds alone. Demonstrate the win on your queries and data.

**The middle path, now standardized:** SQL/PGQ (ISO/IEC 9075-16:2023) lets you declare a property graph *over existing relational tables* and query it with `GRAPH_TABLE ( … MATCH … )` inside SQL. Supported in Oracle Database 23ai and Google Spanner Graph. **Not** in PostgreSQL 19: it was committed during the 19 cycle and then reverted on 2026-09-07 (commit `b1f106c`), with PG 20 (≈Sept 2027) the earliest return. On Postgres today, graph queries mean the **Apache AGE** extension (openCypher) or recursive CTEs.

## The two data models

| | Labeled property graph (LPG) | RDF (triple/quad store) |
|---|---|---|
| Unit | Nodes and directed, typed edges; both carry key-value properties; nodes carry labels | `subject – predicate – object` triples (quads add a named graph) |
| Identity | Internal IDs, application keys | Global IRIs, so it's built for merging data across sources |
| Attributes on a relationship | Native (edge properties) | Needs reification or RDF 1.2 triple terms |
| Schema/semantics | Optional, per product; GQL adds graph types | RDFS/OWL ontologies, inference, SHACL validation |
| Query | Cypher, GQL, Gremlin, SQL/PGQ | SPARQL |
| Pick when | Application graphs: operational traversal, paths, patterns | Linked data, shared vocabularies, ontologies and reasoning, integration across organizations |

Details, including hypergraphs and multi-model stores, are in `references/models-and-storage.md`.

## Storage in one paragraph

**Index-free adjacency** means each node physically points to its neighbours, so one hop costs about the same whatever the total graph size (a B-tree join costs O(log n) per hop). Query cost then scales with **the part of the graph you touch**, not the dataset. "Native" graph stores (Neo4j, Memgraph, TigerGraph) do this. Others put a graph model over a key-value, document, column or relational backend (JanusGraph on Cassandra/HBase, ArangoDB, Apache AGE on Postgres, Spanner Graph on Spanner tables). The distinction matters much less than vendors claim: a poorly planned deep traversal is slow everywhere, a supernode is a problem everywhere, and a good relational plan can beat a naive graph one. Also separate **graph databases (OLTP)** from **graph compute engines (OLAP)**: PageRank, community detection, and all-pairs algorithms over the whole graph belong in Neo4j GDS, Neptune Analytics, Spark GraphFrames and similar, not in per-request traversals.

## Query languages at a glance

The same question, "names of Alice's friends", in each:

```cypher
// Cypher / GQL
MATCH (:Person {name: 'Alice'})-[:KNOWS]->(f:Person) RETURN f.name
```
```groovy
// Gremlin (Apache TinkerPop)
g.V().has('Person', 'name', 'Alice').out('KNOWS').values('name')
```
```sparql
# SPARQL (RDF)
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name WHERE { ?a foaf:name "Alice" ; foaf:knows ?f . ?f foaf:name ?name }
```
```sql
-- SQL/PGQ (inside SQL, over relational tables)
SELECT * FROM GRAPH_TABLE (social
  MATCH (a IS person WHERE a.name = 'Alice') -[IS knows]-> (f IS person)
  COLUMNS (f.name AS friend_name));
```

- **GQL** (ISO/IEC 39075:2024, published 2024-04-12) is the first new ISO database language since SQL, and is heavily Cypher-derived. Wikipedia's "approved September 2019" refers to the *project* approval, not the standard.
- **Cypher** is Neo4j's language, opened as **openCypher** in 2015. Neo4j's **Cypher 25** (with Neo4j 2025.06) is moving toward GQL conformance; Neo4j now uses calendar versions (2025.01, …).
- **Gremlin** is imperative traversal steps, portable across TinkerPop-enabled stores. Stable line 3.8.x; 4.0 is in beta as of 2026-09.
- **SPARQL 1.1** is the W3C Recommendation. **RDF 1.2** reached Candidate Recommendation on 2026-04-07; **SPARQL 1.2** is still a Working Draft.

Syntax, variable-length paths, shortest path, and dialect traps are in `references/query-languages.md`.

## Modeling rules that matter most

1. **Model the questions, not the nouns.** Write the 5–10 traversals the system must answer first, then shape the graph so each one is a short pattern.
2. **Node, property or relationship?** If you'll traverse through it or it's shared, make it a node (a `City` node, not a `city` string on 10M people). If you only display or filter on it, keep it a property.
3. **Promote a relationship to a node when it has its own life:** multiple parties, its own relationships, or its own history (`(:Person)-[:PLACED]->(:Order)-[:CONTAINS]->(:Product)`, not a fat `BOUGHT` edge).
4. **Specific, verb-like relationship types** (`:REPORTS_TO`, `:DEPENDS_ON`) beat generic ones plus a `type` property. The type is what the engine traverses on.
5. **Watch supernodes.** A node with millions of edges (a `Country`, a celebrity, a `Status:Active` node) turns every traversal through it into a scan. Bucket, specialize relationship types, or keep that fact as a property.
6. **Pick one edge direction and query in either.** Don't store both directions for symmetric relationships.
7. **Time is modeling, not a feature.** Use validity properties on edges, or versioned state nodes, and decide which up front.
8. **Index your entry points** (unique constraints on keys). Every traversal starts with a lookup.

Worked patterns and anti-patterns are in `references/modeling-and-pitfalls.md`.

## Always-apply

1. Justify the graph with **traversal-shaped queries and measured numbers**, not with the model's elegance.
2. Choose the **model** (LPG vs RDF) from the integration and semantics needs, then the **language**, then the **product**.
3. Prefer **standard languages** (GQL/Cypher, SQL/PGQ, SPARQL) over proprietary ones (GSQL, nGQL, AQL) unless the product earns the lock-in.
4. Keep **OLTP traversal and OLAP graph algorithms** apart.
5. Bound every variable-length path (`*1..5`, not `*`) and put a `LIMIT` on exploratory queries.
6. **Check product status before recommending it**: this market moves (Kuzu archived 2025-10, RedisGraph EOL, PG 19's PGQ revert). The landscape file is dated; re-verify anything load-bearing.

## How to use the references

- **`references/models-and-storage.md`**: LPG vs RDF in depth, RDF 1.2 triple terms, hypergraphs, multi-model stores, native vs non-native storage, index-free adjacency caveats, OLTP vs OLAP, a short history.
- **`references/query-languages.md`**: Cypher/GQL, SQL/PGQ, Gremlin and SPARQL side by side: patterns, variable-length and quantified paths, shortest path, aggregation, writes, and translation traps.
- **`references/modeling-and-pitfalls.md`**: a modeling method, worked examples (fraud ring, org chart, dependency graph), supernodes, time, and graph-vs-relational anti-patterns.
- **`references/landscape.md`**: products by model, language and license, with 2025–26 status changes, and a selection checklist.

## Sources

Wikipedia, *Graph database* and *Graph Query Language* (2026-09). Neo4j Cypher Manual (GQL conformance, Cypher versions). AWS Neptune user guide. Google Cloud *Spanner Graph and ISO standards*. W3C RDF & SPARQL WG publications. Apache TinkerPop downloads. PostgreSQL commit `b1f106c` (revert of SQL/PGQ, 2026-09-07). Apache AGE docs. FalkorDB RedisGraph EOL guide. Reports of Kuzu's archive (2025-10-10). Wikipedia's product table has a known error: it lists RedisGraph's language as Gremlin, but RedisGraph used a Cypher subset.
