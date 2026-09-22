---
name: python-networkx
description: "NetworkX, the Python graph and network-analysis library, distilled from the NetworkX 3.7 reference (networkx.org, 2026-09; Python >= 3.12) and checked by running 3.7. Covers the data model (dict-of-dict-of-dict adjacency, any hashable node except None, attribute dicts on graph/nodes/edges) and choosing Graph vs DiGraph vs MultiGraph vs MultiDiGraph; live read-only views (G.nodes, G.edges, G.adj, G.degree, .data()) and the copy/view/subgraph semantics that cause aliasing bugs; the algorithm catalogue by task (shortest paths including the Dijkstra/Bellman-Ford/BFS choice, traversal, components, centrality, link analysis, communities including Louvain and the new native Leiden, clustering, DAGs, flows and cuts, matching, trees/MST, cliques, coloring, isomorphism with VF2++, similarity, approximation, bipartite); generators; conversion to and from NumPy, SciPy sparse, pandas and dicts; reading and writing edge lists, GraphML, GML, GEXF, JSON node-link and DOT; drawing (the 3.5+ nx.display API, layouts with store_pos_as, and the advice to use dedicated visualisation tools); randomness and seed semantics; exceptions; and backend dispatch (backend=, nx.config.backend_priority, NETWORKX_* env vars, the conversion cache, nx-parallel/nx-cugraph/nx-arangodb/nx-neptune). Flags the traps: inconsistent weight defaults (shortest_path and betweenness ignore weights unless asked, while dijkstra, pagerank and louvain read 'weight'), Dijkstra silently returning wrong answers with negative weights, subgraph views sharing attributes, node_link_graph defaulting to MultiGraph, generators you must materialise, and O(n!) path enumeration. Use when writing, reviewing or speeding up Python code that builds or analyses graphs or networks with NetworkX, or picking the right NetworkX function for a graph problem, even if the user just says 'import networkx' or describes a network question in Python. Complements the python skill."
license: MIT
---

# NetworkX (Python)

NetworkX is the standard pure-Python library for building and analysing graphs. This skill covers **NetworkX 3.7** (the stable release as of 2026-09, requiring Python ≥ 3.12). It's distilled from the official reference at networkx.org, and every behaviour flagged below was **checked by running 3.7**. It sits alongside [[python]], which covers general idioms. This skill is about the library.

Cross-links:
- [[python]]: idioms, typing, packaging, testing.
- [[graph-databases]]: when the graph belongs in a database rather than in memory.
- [[opencypher]] / [[gremlin]]: querying graphs stored in a database.
- [[nx-neptune]]: the NetworkX backend that runs algorithms on Amazon Neptune Analytics.
- [[aws-neptune]]: the Neptune service itself.

## The mental model

```
G = nx.Graph()                    # or DiGraph / MultiGraph / MultiDiGraph
G._adj  = {u: {v: {attr: val}}}   # dict-of-dict-of-dict ("dictionaries all the way down")
          MultiGraph: {u: {v: {key: {attr: val}}}};  DiGraph: G._succ + G._pred
G.graph = {...}                   # graph attributes
G.nodes[n] -> attr dict           # node attributes
G[u][v] == G.edges[u, v] -> attr dict   (multigraph: G.edges[u, v, key])

Methods on G  = building and reporting (add_*, remove_*, views, copy, subgraph)
Functions nx.* = everything else: nx.shortest_path(G, ...), nx.pagerank(G), nx.community.louvain_communities(G)
```

- **Nodes** can be any hashable object except `None` (`None` raises `ValueError`). Use ints, strings or tuples, and put rich data in attributes rather than in the node object.
- **Views** (`G.nodes`, `G.edges`, `G.adj`, `G.degree`) are live, read-only and cheap. They reflect later changes. Don't mutate `G` while iterating one: use `list(G.edges)` first.
- **Many functions return iterators or generators** (`connected_components`, `all_simple_paths`, `shortest_path` with no source or target, `bfs_edges`). Materialise them with `list()`/`dict()`, and only once.

## Which graph class

| Class | Directed | Parallel edges | Self-loops | Use when |
|---|---|---|---|---|
| `Graph` | no | no | yes | symmetric relationships (default) |
| `DiGraph` | yes | no | yes | direction matters (follows, depends-on, flows) |
| `MultiGraph` | no | yes | yes | several distinct links per pair (e.g. road segments) |
| `MultiDiGraph` | yes | yes | yes | directed multi-relations (transactions, flights) |

Re-adding an existing edge on a `Graph`/`DiGraph` **merges** its attributes: `add_edge(1, 2, weight=4)` after `weight=3, color='r'` gives `{'weight': 4, 'color': 'r'}`. On a multigraph it **adds another edge**, unless you pass `key=`. Many algorithms don't accept multigraphs. Collapse parallel edges yourself first (for example, keep the minimum weight). Some weighted-path functions accept multigraphs and use the lightest parallel edge.

## Non-negotiables

1. **Pass `weight=` explicitly. The defaults disagree.** In 3.7:
   - **Default `weight=None`** (weights ignored): `shortest_path`, `shortest_path_length`, `average_shortest_path_length`, `betweenness_centrality`, `clustering`, `eigenvector_centrality`, `greedy_modularity_communities`, `diameter`/`eccentricity`, `closeness_centrality` (`distance=None`).
   - **Default `weight='weight'`**: `dijkstra_*`, `astar_path`, `pagerank`, `louvain_communities`, `leiden_communities`, `minimum_spanning_tree`, and `spring_layout`.
   - When weights are used, a missing attribute counts as **1**.
   - Also know what a weight *means* for each algorithm. Path algorithms treat it as a **distance**, lower being better. PageRank, Louvain, Leiden and spring layout treat it as **strength**, higher being stronger. Invert or rename the attribute when you mean the other one.
2. **Dijkstra doesn't check for negative weights.** A single negative edge can make it return a **wrong answer silently**. Checked in 3.7: `s→a (1), s→b (2), b→a (−5)` gives Dijkstra `1`, Bellman-Ford `−3`. With negative weights, use `bellman_ford_*`, `johnson`, or `shortest_path(..., method='bellman-ford')`, and test with `negative_edge_cycle(G)`. Betweenness also needs weights > 0, and float weights can give wrong counts, so scale to integers.
3. **Subgraphs are views that share attribute dicts.** `H = G.subgraph(nodes)` is read-only in structure (`add_edge` raises `Frozen graph can't be modified`). But `H.nodes[n]['x'] = 1` **writes into G**, and removing an edge from G removes it from H. Use `G.subgraph(nodes).copy()` for an independent graph. Stacking views (view of a view of a view…) gets slow after about 15 levels.
4. **Copies are shallow.** `G.copy()` / `nx.Graph(G)` create new attribute dicts, but containers inside them (lists, dicts) are shared. Use `copy.deepcopy(G)` for full independence. `DiGraph.to_undirected()` *does* deep-copy, and when both `(u, v)` and `(v, u)` exist it keeps **one arbitrary** set of attributes. Checked: `w=1` and `w=2` became `w=2`. Merge them yourself if that matters.
5. **`set_node_attributes(G, [], 'tags')` shares one list across every node.** A scalar value is applied as the same object to all nodes. Pass a dict keyed by node for per-node values. Keys that aren't nodes in G are **silently ignored**.
6. **Reading a graph changes node types.** `read_edgelist` returns **string** node labels unless `nodetype=int`. `from_pandas_edgelist` keeps only the **last** row for duplicate pairs unless `create_using=nx.MultiGraph`, and all-numeric rows mixing ints and floats come out as floats. `node_link_graph` returns a **MultiGraph** when the JSON has no `"multigraph"` key (default `multigraph=True`). JSON written by NetworkX ≤ 3.5 uses the key `"links"`, and 3.6+ fails to read it with `KeyError: 'edges'` unless you pass `edges="links"`. `from_numpy_array` treats `0` as "no edge" (pass `nonedge=np.nan` to keep zero-weight edges) and builds an undirected `Graph` unless you pass `create_using=nx.DiGraph`.
7. **Path enumeration explodes.** `all_simple_paths`, `simple_cycles` and `all_topological_sorts` can produce O(n!) results. Always pass `cutoff`/`length_bound`, check `has_path` first, and consume lazily (`itertools.islice`). `shortest_simple_paths` yields in order, so take the first k.
8. **Check the preconditions, because functions don't.** DAG functions assume acyclicity without checking it (`is_directed_acyclic_graph` first). `diameter`/`radius`/`eccentricity` raise on disconnected graphs, so run them per component. `is_connected` raises `NetworkXNotImplemented` on directed graphs (use `is_weakly_connected`/`is_strongly_connected`). Many functions are `@not_implemented_for('directed')` or `('multigraph')`.
9. **Seed everything that's random.** Louvain, Leiden, label propagation, `spring_layout`, random generators and sampled betweenness (`k=`) all take `seed=`. Passing an int makes the call reproducible. `seed=None` uses global RNG state. See `references/backends-config-randomness.md`.
10. **NetworkX is pure Python.** It's fine up to roughly 10⁵–10⁶ edges for linear algorithms. All-pairs and betweenness are O(nm) or worse. For heavy work, sample (`betweenness_centrality(G, k=500, seed=0)`), restrict to a component or a k-core, or dispatch to a backend (`backend="parallel"`, `"cugraph"`, `"neptune"`) without rewriting code. Don't write `G[u][v]['w'] = x` directly on a graph with backend conversions cached: that write doesn't clear `G.__networkx_cache__`. Use `G.add_edge(u, v, w=x)`.

## Quick reference

| Task | Code |
|---|---|
| Build weighted | `G.add_weighted_edges_from([('a', 'b', 0.3), ...])`, or `G.add_edge(u, v, weight=w)` |
| From pandas | `nx.from_pandas_edgelist(df, 'src', 'dst', edge_attr=['w'], create_using=nx.DiGraph)` |
| Node attrs from a df | `G.add_nodes_from((n, d.to_dict()) for n, d in df_nodes.set_index('id').iterrows())` |
| Iterate edges with data | `for u, v, w in G.edges(data='weight', default=1):` |
| Degree (weighted) | `dict(G.degree(weight='weight'))`. Cache it if G won't change |
| Neighbours | `G[n]` / `G.neighbors(n)`; directed: `G.successors(n)`, `G.predecessors(n)` |
| Shortest path | `nx.shortest_path(G, s, t, weight='weight')` (Dijkstra) / no weight → BFS |
| Path + length at once | `dist, path = nx.single_source_dijkstra(G, s, t, weight='weight')` |
| Nearest of many targets | add a sentinel node joined to each target with weight 0, then path to the sentinel |
| Components | `max(nx.connected_components(G), key=len)`; directed: `nx.strongly_connected_components` / `weakly_...` |
| Largest component as a graph | `G.subgraph(max(nx.connected_components(G), key=len)).copy()` |
| Centrality | `nx.pagerank(G)`, `nx.betweenness_centrality(G, k=..., seed=0)`, `nx.degree_centrality(G)` |
| Communities | `nx.community.leiden_communities(G, seed=0)` or `louvain_communities(G, seed=0)`; score with `nx.community.modularity(G, parts)` |
| DAG order | `list(nx.topological_sort(G))`, `nx.topological_generations(G)`, `nx.dag_longest_path(G)` |
| Cycles | `nx.find_cycle(G)` (raises `NetworkXNoCycle`), `nx.simple_cycles(G, length_bound=6)` |
| MST | `nx.minimum_spanning_tree(G, weight='weight')` |
| Max flow / min cut | `val, flow = nx.maximum_flow(G, s, t, capacity='capacity')`; `nx.minimum_cut(...)` |
| Store results | `nx.set_node_attributes(G, nx.pagerank(G), 'pagerank')` |
| Summary | `nx.describe(G)` (3.6+, prints a report, returns `None`) |
| Draw quickly | `nx.display(G)` (3.5+ attribute-driven API), or `nx.draw(G, pos=nx.spring_layout(G, seed=0), with_labels=True)` |
| To matrix | `nx.to_numpy_array(G, nodelist=order, weight='weight')`, `nx.to_scipy_sparse_array(G)` |
| Save / load | `nx.write_graphml(G, 'g.graphml')`; JSON: `json.dumps(nx.node_link_data(G))` → `nx.node_link_graph(data)` |
| Relabel to ints | `H = nx.convert_node_labels_to_integers(G, label_attribute='orig')` |

## Namespaces

- Most algorithms are top-level (`nx.pagerank`).
- These subpackages are reached as attributes, and their functions **aren't** top-level:
  - `nx.community.*`
  - `nx.approximation.*` (the docs show `from networkx.algorithms import approximation`)
  - `nx.bipartite.*`
  - `nx.algorithms.node_classification`
  - `nx.isomorphism` (matchers, VF2++)
  - `nx.flow`
  - `nx.utils`
- Name collisions: `nx.bipartite.maximum_matching` isn't the general `nx.max_weight_matching`, and `nx.approximation.diameter` is a lower-bound estimate, not `nx.diameter`.

## Recent changes to know (3.4 → 3.7)

- **3.7.**
  - Native `leiden_communities` / `leiden_partitions`, plus `constant_potts_model`.
  - VF2++ gains subgraph isomorphism and monomorphism.
  - ISMAGS supports directed graphs and multigraphs.
  - `maximal_independent_set` now returns a **set**.
  - `pygraphviz` ships wheels that bundle Graphviz.
  - `bfs_predecessors` is proposed for deprecation. The `p2g` module is deprecated.
- **3.6.**
  - `nx.describe`.
  - `nx.Graph(backend=...)` class dispatch.
  - The node-link JSON default key changed from `"links"` to `"edges"`, and the `link=` keyword was removed. Read or write the old format with `edges="links"`.
  - `random_lobster` → `random_lobster_graph`.
  - `metric_closure` deprecated.
- **3.5.**
  - New attribute-driven drawing API, `nx.display`.
  - Layouts can save positions on the graph with `store_pos_as=`.
  - `k_core` and related functions raise on multigraphs.
  - `d_separated` expired. Use `is_d_separator`.
- **3.4.**
  - Backend conversion caching on by default.
  - `nx.config` works as a context manager.
  - Node-link functions gained the `edges=` keyword. The default key stayed `"links"` until 3.6.

## References

- `references/graph-classes-and-views.md`: building graphs, attributes, every view and what it yields, copy / view / subgraph / to_directed semantics, relabeling, freezing, graph operators, subclassing and memory.
- `references/algorithms-catalogue.md`: a task-to-function index across every algorithm family, with the shortest-path decision table, centrality and community guidance, and per-family preconditions and gotchas.
- `references/io-conversion-drawing.md`: converting to and from dicts, NumPy, SciPy and pandas; the file formats and their traps; JSON node-link; generators; drawing, layouts and external visualisation tools.
- `references/backends-config-randomness.md`: backend dispatch and configuration, env vars, the conversion cache, logging, known backends, seed semantics, the exception hierarchy, and the utilities.
