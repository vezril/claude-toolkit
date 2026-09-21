# Graph data models and storage

## Labeled property graph (LPG)

- **Nodes** have zero or more **labels** (`:Person`, `:Employee`) and a property map.
- **Relationships (edges)** are **directed**, have exactly one **type** (`:WORKS_AT`), a start and an end node, and their own property map (`since: 2021`).
- The direction is stored, but queries can traverse either way or ignore it (`-[:KNOWS]-`).
- Usually schema-optional. Products add constraints (uniqueness, existence, type). ISO GQL adds **graph types**, which declare node and edge types for a closed schema.
- Multi-edges are allowed: two nodes can have many relationships of the same type, for example repeated purchases.

This is the model behind Neo4j, Memgraph, Neptune (property-graph mode), JanusGraph, TigerGraph, FalkorDB, Apache AGE, Spanner Graph and SQL/PGQ.

## RDF (Resource Description Framework)

- Everything is a **triple**: `subject predicate object`. Subjects and predicates are **IRIs**. An object is an IRI, a **literal** (typed or language-tagged), or a **blank node**.
- An "attribute" is just another triple (`:alice foaf:age 42`), so there's no separate property map.
- **Quads** add a fourth element, the **named graph**, used for provenance, versioning and access partitions.
- **Global identifiers** are the superpower. Two datasets that use the same IRI merge by union, with no key mapping. That's why RDF dominates linked open data, life sciences, publishing and enterprise knowledge graphs.
- **Semantics** come from a stack on top: **RDFS**/**OWL** ontologies (classes, subclassing, inference), and **SHACL** for validating shapes.
- **Statements about statements** (where an LPG would use an edge property): classic RDF needs reification, which takes four triples per statement. **RDF 1.2** adds **triple terms**: a triple can be the object of another triple (this is the RDF-star work, standardized). RDF 1.2 Concepts reached **Candidate Recommendation on 2026-04-07**. Check your store's support.
- Queried with **SPARQL**, and stored in triple or quad stores (Ontotext GraphDB, Stardog, AllegroGraph, Apache Jena TDB, Virtuoso, Neptune in RDF mode, Oracle RDF).

### LPG ↔ RDF, quickly

| Need | LPG | RDF |
|---|---|---|
| Property on a relationship | edge property | reification, or an RDF 1.2 triple term |
| Two edges of the same type between the same nodes | natural | the same triple twice is one triple; needs an intermediate node |
| Merge datasets from other organizations | key mapping and ETL | shared IRIs, union |
| Inference ("every Manager is an Employee") | application code | RDFS/OWL reasoner |
| Developer ergonomics for app backends | usually better | steeper |

Neptune stores both models, but in **separate** graphs with separate languages. Choosing a model is still a real decision.

## Hypergraphs and multi-model stores

- A **hypergraph** edge connects any number of nodes. Few products expose this directly (TypeDB models n-ary relations natively). In an LPG you model it by promoting the relationship to a node, which is also the usual advice for rich relationships.
- **Multi-model** stores (ArangoDB, OrientDB, Cosmos DB, SurrealDB, MarkLogic) put graph traversal next to documents or key-value data in one engine. They're convenient when graph queries are a minority of the workload. Check traversal performance at your depth before assuming it's native-grade.

## Native vs non-native storage

- **Native**: storage laid out for the graph. Node and relationship records point directly at each other (**index-free adjacency**), so a hop dereferences a pointer or offset instead of doing an index lookup. Examples: Neo4j, Memgraph (in-memory), TigerGraph.
- **Non-native**: a graph model over another engine: key-value or wide-column (JanusGraph on Cassandra, HBase or ScyllaDB), document (ArangoDB edges are documents with `_from`/`_to`), or relational (Apache AGE, SQL/PGQ, SQL Server graph tables). Each hop is an index lookup, typically O(log n), but it inherits the host's replication, backup, tooling and transactions.

### What index-free adjacency does and doesn't buy

- **It does:** per-hop cost independent of total graph size, so a 4-hop neighbourhood query costs about the same on 10M or 10B nodes *if the neighbourhood is the same size*.
- **It doesn't:** fix fan-out. Cost is proportional to **edges touched**, and 3 hops through nodes with 1,000 neighbours each is 10⁹ edges on any engine.
- **It doesn't:** win set-oriented or global work. Scans, aggregates, and joins between large sets favour columnar or relational engines with hash joins. Wikipedia cites studies where an RDBMS matched graph engines on graph queries.
- **It's not free:** sharding a pointer-linked structure is hard. Native stores traditionally scale reads by replication and writes vertically. Distributed products (TigerGraph, JanusGraph, Spanner Graph, NebulaGraph, Neptune's managed storage) pay with network hops on cross-partition edges.

## OLTP graph database vs OLAP graph compute

| | Graph database (OLTP) | Graph compute / analytics (OLAP) |
|---|---|---|
| Work | Local traversals from known entry points, transactional writes | Whole-graph algorithms: PageRank, community detection (Louvain), connected components, centrality, similarity, embeddings |
| Latency | ms, per request | seconds to hours, batch |
| Examples | Neo4j, Neptune Database, Memgraph, Spanner Graph | Neo4j Graph Data Science, Neptune Analytics (algorithms plus vector search), Spark GraphFrames, TigerGraph's algorithm library, NetworkX/igraph for small graphs |

Common pattern: compute scores offline (a fraud-risk score, a community id), write them back as node properties, and use them in OLTP queries.

## Short history (context for "why so many languages")

- **1960s:** navigational databases. IBM IMS (hierarchical), then CODASYL's network model (Network Database Language, 1969): graph-shaped data before the relational model.
- **1980s–90s:** labeled-graph and object database research. ODMG object database standards (published 2000).
- **Mid-to-late 2000s:** commercial ACID graph databases (Neo4j, Oracle Spatial and Graph).
- **2010s:** Gremlin and TinkerPop (2009 onward); Cypher (2011), opened as openCypher in 2015; SPARQL 1.1 (2013); horizontally scalable and multi-model stores; managed cloud offerings (Neptune in 2018, Neo4j AuraDB).
- **2020s:** standardization. SQL/PGQ (2023) and GQL (2024). Cloud databases add graph layers (Spanner Graph). RDF 1.2 is in progress.
