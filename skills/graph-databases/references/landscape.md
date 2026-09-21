# Graph database landscape (verified 2026-09)

This market changes fast. Treat this table as a starting point and re-check anything load-bearing (license, status, language support) against the vendor before recommending it.

## Property-graph databases

| Product | Storage / deployment | Languages | License | Notes |
|---|---|---|---|---|
| **Neo4j** | Native; self-managed or AuraDB (cloud) | Cypher (Cypher 25 moving toward GQL), Bolt protocol | Community GPLv3; Enterprise commercial | Calendar versions since 2025.01. Graph Data Science library for OLAP |
| **Amazon Neptune** | Managed AWS; Neptune Database (OLTP) and Neptune Analytics (algorithms + vector search) | Gremlin, openCypher over the same property graph; SPARQL for RDF graphs | Proprietary service | Property-graph and RDF data are separate |
| **Google Spanner Graph** | Graph layer over Spanner tables, globally distributed | ISO GQL + SQL/PGQ | Proprietary service | Graph DML is table-based SQL only |
| **Memgraph** | Native, in-memory | Cypher (openCypher) | Source-available / commercial | Streaming and real-time analytics focus |
| **JanusGraph** | Non-native over Cassandra / HBase / ScyllaDB / Bigtable | Gremlin | Apache 2.0 | Distributed. You run the backend and index (Elasticsearch/Solr) |
| **TigerGraph** | Native, distributed (MPP) | GSQL (proprietary) | Proprietary | Deep-link analytics at scale |
| **NebulaGraph** | Distributed, shared-nothing | nGQL (proprietary) | Apache 2.0 | |
| **FalkorDB** | Redis module, sparse-matrix engine | Cypher subset | Source-available (SSPL) | Fork and successor of **RedisGraph** (EOL: no new licenses from 2023-07-05, support ended 2025-01-31). Reads RedisGraph RDB files |
| **Apache AGE** | PostgreSQL extension | openCypher inside SQL (`cypher()` function) | Apache 2.0 | The graph option on Postgres today. Available on Azure Database for PostgreSQL |
| **ArangoDB** | Multi-model (document + graph + KV) | AQL (proprietary) | BSL / community license | |
| **Microsoft SQL Server / Azure SQL** | Node and edge tables in the relational engine | T-SQL `MATCH` | Proprietary | Since SQL Server 2017 |
| **Oracle Database 23ai** | Property graphs over relational tables | SQL/PGQ (and PGQL in Oracle Graph) | Proprietary | |
| **Azure Cosmos DB (Gremlin API)** | Multi-model, distributed | Gremlin (subset) | Proprietary service | |

## RDF / triple stores

| Product | Notes |
|---|---|
| **Ontotext GraphDB** | SPARQL; reasoning; free and commercial editions |
| **Stardog** | SPARQL; virtual graphs over relational sources; reasoning |
| **AllegroGraph** | SPARQL; also document and vector features |
| **Apache Jena (TDB2 / Fuseki)** | Open source (Apache 2.0) Java stack; a good default for self-hosting |
| **OpenLink Virtuoso** | Hosts many public linked-data endpoints (DBpedia) |
| **Amazon Neptune (RDF mode)**, **Oracle RDF Graph** | Managed or enterprise options |

## Recent status changes worth knowing

- **Kuzu** (embedded, columnar property graph, Cypher) was **archived 2025-10-10** with a final 0.11.3 release after its company was acquired. Community forks exist (e.g. LadybugDB, Bighorn). Don't start new projects on upstream Kuzu.
- **RedisGraph** is end of life. Migrate to FalkorDB, or to another Cypher store.
- **PostgreSQL 19** shipped *without* SQL/PGQ. It was committed during the cycle and then reverted on 2026-09-07 (commit `b1f106c`). The earliest return is PG 20. Use Apache AGE or recursive CTEs in the meantime.
- **Neo4j** moved to calendar versioning (2025.01+) and introduced Cypher 25 (with 2025.06). Cypher 5 gets fixes only.
- **Apache TinkerPop** stable is 3.8.x (3.8.2, 2026-09-01). 4.0 is in beta (4.0.0-beta.3, 2026-07).
- **RDF 1.2** is a Candidate Recommendation (2026-04-07). **SPARQL 1.2** is a Working Draft.

## Selection checklist

1. **Model:** LPG (application graph) or RDF (shared vocabularies, integration, inference)? If you truly need both, check whether one product serving both is worth separate data.
2. **Language:** prefer a standard (GQL/Cypher, SQL/PGQ, SPARQL, Gremlin). A proprietary language is lock-in, so price it in.
3. **Where the data already lives:** already on Postgres, Spanner, Oracle or SQL Server? Try the in-database graph layer (AGE, Spanner Graph, SQL/PGQ, SQL graph tables) before adding a new database.
4. **Workload:** OLTP traversal, OLAP algorithms, or both? Check for an analytics companion (GDS, Neptune Analytics) or plan an export pipeline.
5. **Scale shape:** does it fit on one machine with read replicas (most graphs do), or do you genuinely need a distributed graph? Distributed graph stores pay for cross-partition hops.
6. **Operations:** managed vs self-hosted, backups, HA, security (row or property-level access), and the tooling your team already knows.
7. **License and status:** open source vs source-available vs commercial, and whether the project is still maintained (see the status changes above).
8. **Proof:** run your top 3–5 queries on realistic, skewed data before committing.
