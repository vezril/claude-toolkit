# NetworkX backend

## How dispatch works

NetworkX 3.x has a backend dispatch mechanism. When you install `nx_neptune`, two entry points register it:

```toml
[project.entry-points."networkx.backends"]
neptune = "nx_neptune.interface:BackendInterface"
[project.entry-points."networkx.backend_info"]
neptune = "nx_plugin:get_info"
```

`nx.pagerank(G, backend="neptune")` goes to `nx_neptune`. Every wrapped algorithm has the `@configure_if_nx_active()` decorator. Each call does the following:

1. `validate_config()` checks `nx.config.backends.neptune`. It raises `ValueError` on bad combinations (see below).
2. **Setup.**
   - If `graph_id` is set (from config or `NETWORKX_GRAPH_ID`), it connects and optionally imports from `import_s3_bucket`.
   - Otherwise, if `create_new_instance` is `True` or a dict, it creates a graph (a few minutes), optionally imports, and stores the new id in the config.
3. **Sync.** Unless `skip_graph_reset=True`, it runs **`MATCH (n) DETACH DELETE n`**. Then it pushes every local node, in batches of `batch_update_node_size` (20,000), and every edge, in batches of `batch_update_edge_size` (10,000). An empty local graph skips the sync entirely, including the clear.
4. Runs the openCypher `CALL neptune.algo.…` and converts the result to NetworkX's shape.
5. **Teardown** (only when `graph_id` is set). It optionally exports to `export_s3_bucket` and optionally deletes the instance (`destroy_instance`).

It works from inside a running event loop (Jupyter). The decorator spins up a thread to run its own `asyncio.run`.

Plain algorithm calls are synchronous. The SessionManager API is async.

## `NeptuneConfig` (`nx.config.backends.neptune`)

This is a global config object. It isn't thread-safe across concurrent callers.

| Field | Default | Meaning |
|---|---|---|
| `graph_id` | env `NETWORKX_GRAPH_ID` | Existing graph to use |
| `s3_iam_role` | env `NETWORKX_S3_IAM_ROLE_ARN` | Role Neptune assumes for S3 import/export. The docs' `NETWORKX_ARN_IAM_ROLE` is not what the code reads |
| `skip_graph_reset` | `False` | `True` = don't clear the graph before syncing, and allow S3 import into a non-empty graph |
| `create_new_instance` | `False` | `True`, or a boto3 `create_graph` kwargs dict (`{"provisionedMemory": 32, "publicConnectivity": False, "tags": {...}}`) |
| `import_s3_bucket` | `None` | S3 CSV to load before the call |
| `restore_snapshot` | `None` | **Not implemented.** Raises |
| `export_s3_bucket` | `None` | Export the graph as CSV after the call |
| `save_snapshot` | `False` | **Not implemented.** Raises |
| `reset_graph` | `False` | **Not implemented.** Raises |
| `destroy_instance` | `False` | Delete the graph after the call |
| `batch_update_node_size` / `_edge_size` | 20000 / 10000 | Upload chunking |

`validate_config()` rejects the following:
- no `graph_id` and `create_new_instance=False`
- `graph_id` together with `create_new_instance=True`
- `import_s3_bucket` or `export_s3_bucket` without `s3_iam_role`
- both `import_s3_bucket` and `restore_snapshot`
- `graph_id` + `import_s3_bucket` without `skip_graph_reset=True`
- both `destroy_instance` and `reset_graph`

A mutate-style call with `destroy_instance=True` and no `export_s3_bucket` is also rejected, because the written properties would be lost.

### Ephemeral-graph pattern

```python
import networkx as nx
cfg = nx.config.backends.neptune
cfg.graph_id = None
cfg.create_new_instance = {"provisionedMemory": 16, "publicConnectivity": False}
cfg.destroy_instance = True           # delete after the call

scores = nx.pagerank(G, backend="neptune")
```

The first call creates the graph. Teardown then deletes it and resets `graph_id` to `None`, so the **next call creates a new graph**, which takes minutes each time. For several algorithms, create once, leave `destroy_instance=False`, and delete yourself at the end.

### Reusing a pre-loaded graph

```python
cfg.graph_id = "g-abc123"
cfg.skip_graph_reset = True           # don't wipe it
r = nx.pagerank(nx.DiGraph(), backend="neptune",   # empty local graph => nothing pushed
                vertex_label="Person", edge_labels=["KNOWS"])
```

Passing an empty graph skips the sync, and the algorithm runs over what is already in Neptune. This pattern follows from the decorator's code. The docs don't document it, so check the result shape on your version.

## Algorithms

Each wrapped algorithm maps to a Neptune Analytics procedure. Every one accepts `vertex_label`, `edge_labels` and `concurrency` (thread count, 0 = all). Most also accept `write_property`, and many accept `traversal_direction`. "Ignored" means the parameter is accepted, logs a warning, and has **no effect**.

### Traversal

| Function | Neptune proc | Key params | Returns |
|---|---|---|---|
| `bfs_edges(G, source, reverse=False, depth_limit=None, …)` | BFS standard | `reverse`, `depth_limit`; `sort_neighbors` **ignored** | yields edges |
| `descendants_at_distance(G, source, distance, …)` | BFS levels | `traversal_direction` | `set` of nodes |
| `bfs_layers(G, sources, …)` | BFS levels | `traversal_direction` | yields lists of nodes per level |

### Link analysis

`pagerank(G, alpha, personalization, max_iter, tol, nstart, weight, dangling, …)` maps to PageRank.
- Supported: `alpha`, `max_iter`, `tol`.
- **Ignored:** `personalization`, `nstart`, `weight`, `dangling`.
- Neptune equivalents: `source_nodes` + `source_weights` (personalized PageRank) and `edge_weight_property` + `edge_weight_type` (weighted). Also `traversal_direction` and `write_property`.
- Returns `{node: score}`, or `{}` when `write_property` is set.

### Link prediction

`jaccard_coefficient(G, ebunch=None, edge_labels=None, vertex_label=None, traversal_direction=None)` maps to Jaccard similarity.
- Returns an iterator of `(u, v, p)`.
- With `ebunch=None`, the library computes all **non-edges locally** and sends them explicitly. That's O(n²) pairs, so always pass `ebunch` for real graphs.
- `traversal_direction` accepts `"both"`.
- Neptune has no mutate variant, so there's no `write_property`.

### Centrality

| Function | Returns | Notes |
|---|---|---|
| `degree_centrality`, `in_degree_centrality`, `out_degree_centrality` | `{node: degree}` | Neptune "Degree". The values are **raw degree counts per the docs**, not NetworkX's normalized `degree/(n-1)`. Normalize yourself if you compare with local results |
| `closeness_centrality(G, u=None, distance=None, wf_improved=True, num_sources=None, …)` | `{node: score}` | `distance` **ignored**; `num_sources` = approximate from N sources (omit for exact); `u` limits to one node |

### Community

| Function | Returns | Notes |
|---|---|---|
| `louvain_communities(G, weight, resolution, threshold, max_level, seed, …)` | list of sets | `resolution` and `seed` **ignored**. Neptune params: `edge_weight_property`/`_type`, `max_iterations`, `level_tolerance`, `write_property` |
| `label_propagation_communities(G, …)` | community → members | `vertex_weight_property`/`_type`, `edge_weight_property`/`_type`, `max_iterations`, `traversal_direction`, `write_property` |
| `fast_label_propagation_communities`, `asyn_lpa_communities` | same | same params plus `weight`, `seed` |
| `weakly_connected_components(G, …)` | list of sets (`{}` with `write_property`) | Neptune WCC |

Louvain without a fixed `seed` is nondeterministic both locally and on Neptune. Don't write tests that compare community IDs.

### Anything else

Algorithms outside the wrapped 14 (shortest paths, betweenness, SCC, triangle count, vector similarity, and so on) aren't dispatched. With `backend="neptune"` NetworkX will fail or fall back, depending on its dispatch settings. Call them directly as openCypher on the graph: `CALL neptune.algo.<name>(...)`. The catalogue and `.mutate` variants are in [[aws-neptune]] `references/neptune-analytics.md`.

## Data conversion

- Node IDs become the Neptune `~id`. Node attributes become properties.
- **Every synced node gets the label `Node`, and every synced edge gets the type `RELATES_TO`.** A NetworkX attribute named `label` or `type` doesn't change this. So on a graph that came from a sync, `vertex_label="Person"` or `edge_labels=["KNOWS"]` (the docs' own example) matches **nothing**. Use the label filters only on graphs loaded by SessionManager or S3 import, where `~label` came from your projection.
- For an **undirected** `nx.Graph`, each edge is written in **both directions** (`(a)->(b)` and `(b)->(a)`). A `DiGraph` writes one direction. Neptune stores only directed edges, which matters when you set `traversal_direction`.
- Results come back keyed by `~id` strings. If your local node IDs were ints, map them back.

## Failure checklist

| Symptom | Cause |
|---|---|
| `ValueError: Configuration error: create_new_instance is False and graph_id is None` | `NETWORKX_GRAPH_ID` unset in *this* process (Jupyter needs `%env`, or a kernel restart after export) |
| Remote graph suddenly empty or replaced | The sync cleared it. See non-negotiable 1 |
| Results differ from local NetworkX | An ignored parameter, raw vs normalized degree, undirected edges doubled, or a Louvain seed |
| Empty result with `vertex_label` / `edge_labels` | Synced data is all `Node` / `RELATES_TO` |
| `AccessDeniedException` | Missing `neptune-graph:ReadDataViaQuery` / `WriteDataViaQuery` / `DeleteDataViaQuery`. The sync needs write and delete even for a "read-only" algorithm |
| Very slow first call | `create_new_instance` provisioning (minutes), or a large upload in 10k-edge batches |
| `Not implemented yet (workflow: …)` | `restore_snapshot`, `save_snapshot` or `reset_graph` in the backend config |
