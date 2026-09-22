---
name: nx-neptune
description: "nx-neptune, the awslabs Python library (PyPI nx_neptune 0.6.0, Python ≥ 3.11, Alpha Preview) that runs graph analytics on Amazon Neptune Analytics, distilled from awslabs.github.io/nx-neptune and checked against the GitHub source (2026-09). Covers its two interfaces: the NetworkX backend (add backend=\"neptune\" to nx.pagerank, bfs_edges, bfs_layers, descendants_at_distance, degree/in/out/closeness centrality, louvain/label-propagation communities, weakly_connected_components, jaccard_coefficient; 14 algorithms total; configured via NETWORKX_GRAPH_ID and nx.config.backends.neptune) and the SessionManager \"graph over data lake\" workflow (create → import_from_table with Athena SQL projections using ~id/~label/~from/~to and name:Type columns → CALL neptune.algo.* openCypher → export_to_table back to S3 Tables Iceberg → destroy) across S3 Tables, S3 Vectors, Databricks, Snowflake, OpenSearch and other Athena federated sources. Also covers the IAM permissions, env vars, the CloudFormation SageMaker notebook stack, and the traps the docs don't state: each backend call wipes the target graph (MATCH (n) DETACH DELETE n) unless skip_graph_reset is set, unsupported NetworkX parameters are ignored with only a log warning, session names are prefix matches, CleanupTask only fires in a with-block and only for DESTROY, graphs default to public connectivity, and several doc examples don't match the real API. Use when running NetworkX algorithms on Neptune Analytics, projecting data-lake tables into a graph for Louvain/PageRank/centrality, writing SessionManager code, deploying the nx-neptune notebook stack, or debugging nx-neptune errors, even if the user just says \"NetworkX on AWS\" or \"graph analytics over my Iceberg tables\"."
license: MIT
---

# nx-neptune

nx-neptune is an awslabs Python library that sends graph algorithm work to **Amazon Neptune Analytics**. It has two separate interfaces over the same engine:

1. **NetworkX backend.** Keep ordinary NetworkX code and add `backend="neptune"` to a supported algorithm call. The library pushes your in-memory graph to a Neptune Analytics graph, runs the matching `neptune.algo.*` procedure, and converts the result back to NetworkX's return shape.
2. **SessionManager ("graph over data lake").** Define nodes and edges as Athena SQL over tables you already have. The library provisions a graph on demand, loads the projection, lets you run openCypher and algorithms, writes the annotated graph back to S3 Tables as Iceberg, and tears the graph down.

Distilled from `awslabs.github.io/nx-neptune` and checked against the `awslabs/nx-neptune` source, 2026-09 (PyPI `nx_neptune` **0.6.0**). The project calls itself **Alpha Preview, recommended for testing purposes only.** Where the docs and the code disagree, this skill follows the code and says so.

Cross-links:
- [[aws-neptune]]: Neptune Analytics itself (m-NCU sizing, the full `neptune.algo` catalogue, vector index, endpoints, IAM `neptune-graph` actions). Read its `references/neptune-analytics.md` for anything below the library.
- [[graph-databases]]: whether the problem is a graph problem at all.
- [[aws-s3]]: staging buckets, KMS, versioning.
- [[aws-cloudformation]] / [[aws-iam]]: the demo stack and its role.
- [[python]]: the 3.11+ runtime and packaging.
- [[python-networkx]]: NetworkX itself (algorithms, weight defaults, backend dispatch and `nx.config`).

## Which interface

| You have | Use |
|---|---|
| A NetworkX graph in memory that's too slow locally | NetworkX backend |
| Tables in S3 Tables / Databricks / Snowflake / OpenSearch / any Athena source, and questions about relationships | SessionManager |
| Results that must land back in the lake as tables | SessionManager `export_to_table` |
| An algorithm not in the 14 wrapped ones | Either interface, then `graph.execute_query("CALL neptune.algo.<name>(...)")` directly |

## Non-negotiables

1. **A backend call erases the target graph first.** Before every wrapped algorithm, the library runs `MATCH (n) DETACH DELETE n` on the graph named by `NETWORKX_GRAPH_ID`, then uploads your NetworkX graph in batches (20,000 nodes / 10,000 edges). The docs don't mention this. **Never point `NETWORKX_GRAPH_ID` at a graph holding data you want to keep.** To run against data already loaded, set `nx.config.backends.neptune.skip_graph_reset = True`, and be aware your local nodes and edges are still pushed on top.
2. **Every call re-uploads the whole graph.** There's no caching between calls. Three algorithms on a million-edge graph means three full uploads. For repeated analysis of big data, load once (SessionManager or an S3 import) and use `execute_query`.
3. **Unsupported NetworkX parameters are ignored, not rejected.** `pagerank(personalization=, nstart=, weight=, dangling=)`, `louvain_communities(resolution=, seed=)`, `closeness_centrality(distance=)` and `bfs_edges(sort_neighbors=)` only produce a log warning. You get a different computation than local NetworkX would give. Use the Neptune equivalents instead: `source_nodes`/`source_weights` for personalization, `edge_weight_property` + `edge_weight_type` for weights.
4. **`write_property` changes the return value.** With `write_property` set, results are persisted as a node property and the call returns an empty dict (or, raw in openCypher, just `success`). Read them back with a query.
5. **Session names are prefixes.** `SessionManager.session("fraud")` sees every graph whose name starts with `fraud`, including `fraud-prod-…`. `get_or_create_graph()` returns the **first AVAILABLE** match. With no session name, the session sees **every Neptune Analytics graph in the account and region**, so `destroy_all_graphs()` deletes them all. Always pass a specific session name.
6. **Don't trust `CleanupTask` to clean up. Destroy explicitly.** Only a synchronous `with` block's `__exit__` acts on it, and only for `DESTROY`. `STOP` and `RESET` are accepted and do nothing. `__exit__` never awaits the deletion future. In Jupyter, where a loop is running, the deletion gets scheduled. In a plain script, exit raises `RuntimeError: There is no current event loop` and **nothing is deleted**. Without `with`, the cleanup task never runs at all. The lifecycle methods (`destroy_graph`, `destroy_all_graphs`, `stop_all_graphs`, …) return an `asyncio.gather` future, so `await` them yourself in a `try/finally`. A graph left running bills by the m-NCU-hour.
7. **New graphs default to public connectivity.** Unless you pass a config, graphs are created with `publicConnectivity=True`, 16 m-NCU, 0 replicas, no deletion protection. Pass `config={"publicConnectivity": False, ...}` for anything with real data. SigV4 still applies, but a public endpoint may not be your posture.
8. **Pass the graph object, not its id.** `import_from_table`, `export_to_table`, `export_to_csv` and `create_snapshot` take the `NeptuneAnalyticsClient` returned by `get_or_create_graph()`. The blog's `graph["id"]` doesn't work, and the docs' `SessionManager(graph_id=..., region=..., iam_role_arn=...)` constructor doesn't exist. The real signature is `SessionManager(session_name=None, cleanup_task=None)`. Region and credentials come from the standard boto3 chain.
9. **Projection SQL has a contract.** Node queries must return `"~id"`. Edge queries must return `"~from"` and `"~to"`. `"~label"` is optional, but you should set it. Other columns become properties, typed with `"name:Type"` aliases (`"amount:Float"`). An embedding column must be named exactly `"embedding:vector"`. Quote the tilde aliases in Athena SQL. `SELECT *` skips validation.
10. **Know what gets deleted for you.** `import_from_table(remove_buckets=True)` (the default) deletes the staged CSVs after import. `export_to_table(remove_resources=True)` deletes the exported CSVs and drops the intermediate Athena CSV table. Source tables and the staging bucket itself are left alone.

## Quick reference

| Item | Value |
|---|---|
| Install | `pip install nx_neptune` (`"nx_neptune[jupyter]"` for notebooks) |
| Runtime | Python ≥ 3.11; networkx ≥ 3.4.2,<4; boto3 ≥ 1.37 |
| Backend registration | `networkx.backends` entry point `neptune = nx_neptune.interface:BackendInterface`; no import needed |
| Wrapped algorithms (14) | `bfs_edges`, `bfs_layers`, `descendants_at_distance`, `pagerank`, `degree_centrality`, `in_degree_centrality`, `out_degree_centrality`, `closeness_centrality`, `louvain_communities`, `label_propagation_communities`, `fast_label_propagation_communities`, `asyn_lpa_communities`, `weakly_connected_components`, `jaccard_coefficient` |
| Neptune extras (kwargs) | `vertex_label`, `edge_labels`, `concurrency` (0 = all threads), `traversal_direction` (`"outbound"`/`"inbound"`, `"both"` on Jaccard), `write_property`, `edge_weight_property`, `edge_weight_type` (`int`/`long`/`float`/`double`) |
| Backend config | `nx.config.backends.neptune` (`NeptuneConfig`); env `NETWORKX_GRAPH_ID`, `NETWORKX_S3_IAM_ROLE_ARN` |
| SessionManager env | `AWS_REGION`, `NETWORKX_S3_IMPORT_BUCKET_PATH`, `NETWORKX_S3_EXPORT_BUCKET_PATH`, `NETWORKX_STAGING_BUCKET`, plus `NETWORKX_S3_TABLES_CATALOG` / `_DATABASE` in the notebooks |
| Graph create defaults | 16 m-NCU, `publicConnectivity=True`, `replicaCount=0`, `deletionProtection=False`, tag `agent=nx-neptune`; name `{session_name}-{uuid}` |
| Algorithm call from SessionManager | `graph.execute_query('CALL neptune.algo.louvain.mutate({writeProperty:"community"}) YIELD success RETURN success')` |
| Demo stack | `./cloudformation-templates/deploy.sh [stack≤16 chars] [region] [build_wheel]`; `teardown.sh` removes the stack and all versions in the bucket |

## References

- `references/networkx-backend.md`: how dispatch works, the full `NeptuneConfig` (connect, create, import, export, destroy), every algorithm's signature, supported and ignored parameters, and return shapes.
- `references/session-manager.md`: the `SessionManager` API method by method, the projection SQL format, the fraud-ring walkthrough end to end, snapshots, CSV import/export and auto-resize, and the lifecycle and cost traps.
- `references/data-sources-and-deployment.md`: each Athena-backed source (S3 Tables, S3 Vectors, Databricks, Snowflake, OpenSearch) and its connector, IAM permissions, env vars, the CloudFormation SageMaker stack, and a table of doc-vs-source discrepancies.
