# Neptune Analytics

A **memory-optimized graph analytics engine**, separate from Neptune Database. It has its own API namespace, `neptune-graph` (`aws neptune-graph …`, `boto3.client('neptune-graph')`), and its own endpoint, `https://<graphId>.<region>.neptune-graph.amazonaws.com`. It loads a whole graph into memory, then runs **built-in algorithms, openCypher queries and vector search** on it.

## Database or Analytics?

| Need | Use |
|---|---|
| App traffic: request-time traversals, transactional writes, high availability, multi-region | **Neptune Database** |
| Whole-graph algorithms (PageRank, Louvain, WCC, shortest paths from many sources), exploration, data science | **Neptune Analytics** |
| Vector similarity *combined with* graph traversal (GraphRAG, "similar products bought by my network") | **Neptune Analytics** |
| Periodic scoring (fraud ring IDs, influence scores) fed back into the app | Analytics computes, then write back to Database (or the app store) |

Analytics can load **from a Neptune Database cluster or snapshot**, or **from S3**, so the usual pattern is: Database for OLTP, then snapshot or import into Analytics, run algorithms, write results back or export them.

## Capacity and lifecycle

- Sized in **m-NCUs**: 1 m-NCU is about **1 GB of memory** plus proportional compute and network, billed per hour. The smallest sizes are now **32 and 64 m-NCU** (previously 128). Size to fit the graph in memory with headroom for algorithm working sets. Check the console or pricing page for the current maximum.
- Optional **replicas** for availability, plus **snapshots**. A graph can be restored from a snapshot, so you can create a graph, analyse, snapshot or delete it, and restore later instead of paying for idle memory.
- Connectivity is **private endpoints** (VPC) and/or an opt-in **public endpoint**. Either way, requests are **SigV4-signed with `service=neptune-graph`**.

## Querying

- The language is **openCypher**, with algorithms exposed as procedures via `CALL neptune.algo.<name>(…) YIELD …`.
- Call it through the SDK `ExecuteQuery` (`aws neptune-graph execute-query --language open_cypher`) or `awscurl --service neptune-graph` against `/opencypher`.
- For loading more data into a running graph: `CALL neptune.load({...})` (batch load from S3), or import tasks.

```cypher
// Top 10 most important airports in a region
MATCH (n:airport {region: 'US-AK'})
CALL neptune.algo.pageRank(n, {edgeLabels: ['route'], numOfIterations: 10})
YIELD rank
RETURN n.code, rank ORDER BY rank DESC LIMIT 10
```

## Algorithm catalogue (25+)

| Category | Algorithms |
|---|---|
| Pathfinding | BFS, single-source shortest path, top-K source shortest path, source-target shortest path, EgoNet |
| Centrality | Degree, PageRank, Closeness |
| Similarity | Common Neighbors, Total Neighbors, Jaccard, Overlap |
| Community / clustering | Weakly Connected Components, Strongly Connected Components, Label Propagation, Louvain |
| Vector similarity (HNSW, approximate nearest neighbours) | distance, top-K (`topKByEmbedding`, `topKByNode`-style calls) |
| Miscellaneous | property-graph summary, schema, degree distribution |

Many algorithms also have **`.mutate` variants** that write the result (a rank or a component ID) back as a node property instead of returning it, which makes it available to later queries. Algorithms that take different input shapes are exposed as separate procedures. Check the exact name and signature in the algorithm reference.

## Vector search

- **One vector index per graph**, with a **fixed dimension from 1 to 65,535**, and **it can only be defined when the graph is created**. Pick the embedding model and its dimension before creating the graph.
- Loading embeddings:
  - a CSV column with header `embedding:vector`, values separated by `;` (nodes need at least one label or property; no NaN or ±Inf)
  - or `CALL neptune.algo.vectors.upsert(node, [..])`
  - Embeddings **can't be loaded from Neptune Database or a snapshot**, only from S3 files or upserts. With no index, embedding columns are silently ignored.
- **Vector updates are not atomic or isolated.** An embedding write becomes durable and visible immediately, even if the surrounding query later fails. So:
  1. don't update one node's embedding concurrently
  2. make upserts **idempotent** (`MATCH` existing nodes, then upsert; not `CREATE`, then upsert) and retry on failure
  3. keep vector updates in their own simple queries, not chained with other writes
- A wrong dimension fails the load with a `ParsingException`.

## GraphRAG with Amazon Bedrock

**Amazon Bedrock Knowledge Bases GraphRAG** (GA 2025-03-07) uses Neptune Analytics as its graph and vector store. It extracts entities and relationships from your documents, stores embeddings and the entity graph in Neptune Analytics, and at retrieval time combines vector similarity with graph traversal for multi-hop context. You don't need existing graph infrastructure, because Bedrock creates and maintains the graph. It's only available in regions where both Bedrock Knowledge Bases and Neptune Analytics exist. For a do-it-yourself GraphRAG, use the same primitives directly: a vector top-K to find entry nodes, then a bounded openCypher expansion for context. See [[vault-graphrag]] for the concepts.
