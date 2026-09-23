# Conversion, file I/O, generators and drawing

## Converting in memory

The graph constructor guesses the input type through `to_networkx_graph`, so `nx.DiGraph(data)` works for most inputs. The explicit functions:

| Format | To NetworkX | From NetworkX | Notes |
|---|---|---|---|
| dict of dicts | `from_dict_of_dicts(d, create_using, multigraph_input)` | `to_dict_of_dicts(G, nodelist, edge_data)` | `{0: {1: {'w': 2}}}` |
| dict of lists | `from_dict_of_lists` | `to_dict_of_lists` | no edge data |
| edge list | `from_edgelist` | `to_edgelist` | |
| NumPy | `from_numpy_array(A, parallel_edges=False, create_using=None, edge_attr='weight', nodelist=None, nonedge=0)` | `to_numpy_array(G, nodelist=None, dtype=None, weight='weight', nonedge=0.0, multigraph_weight=sum)` | see below |
| SciPy sparse | `from_scipy_sparse_array` | `to_scipy_sparse_array(G, nodelist, dtype, weight, format='csr')` | use it for large graphs |
| pandas adjacency | `from_pandas_adjacency(df)` | `to_pandas_adjacency(G)` | |
| pandas edge list | `from_pandas_edgelist(df, source='source', target='target', edge_attr=None, create_using=None, edge_key=None)` | `to_pandas_edgelist(G, source, target, nodelist, dtype, edge_key)` | see below |
| PyGraphviz / pydot | `nx.nx_agraph.from_agraph`, `nx.nx_pydot.from_pydot` | `to_agraph`, `to_pydot` | |

**Matrix rules:**
- **Order.** Rows and columns follow `nodelist`, or else `G.nodes()` order. Always pass `nodelist` when you need to map rows back to nodes.
- **Non-edges.** They're `0`, so a zero-weight edge and a missing edge look the same. Use `nonedge=np.nan` in both directions (3.7 completes the round trip).
- **Direction.** `A[i, j]` is the edge i → j. `from_numpy_array` needs `create_using=nx.DiGraph` for directed input, and for an undirected multigraph only the upper triangle is read.
- **Missing weight** counts as 1. **Parallel edges** are summed (`multigraph_weight=sum`; pass `min` for distances).
- **Self-loops** put the weight on the diagonal once, not doubled.
- A partial `nodelist` gives the matrix of the induced subgraph.
- `from_numpy_array(A, parallel_edges=True, create_using=nx.MultiGraph)` with an integer A reads entries as edge counts.
- Structured dtypes map named fields to edge attributes (not for multigraphs).

**pandas rules:**
- `from_pandas_edgelist` defaults to `nx.Graph`. Duplicate (source, target) rows **overwrite each other** (the last row wins; checked). Use `create_using=nx.MultiGraph()` (plus `edge_key=` for your own keys) to keep them all.
- `edge_attr=True` copies every other column.
- Rows are read via `DataFrame.values`, so an all-numeric row mixing ints and floats becomes floats.
- Node attributes from a second frame: `G.add_nodes_from((n, dict(d)) for n, d in df_nodes.set_index('id').iterrows())`, or `nx.set_node_attributes(G, df_nodes.set_index('id').to_dict('index'))`.

## Files

| Format | Read / write | Keeps attributes | Traps |
|---|---|---|---|
| Edge list | `read_edgelist(path, comments='#', delimiter=None, create_using=None, nodetype=None, data=True)`, `write_edgelist`, `read_weighted_edgelist`, `parse_edgelist` | edge attrs as a dict literal, or `data=[('weight', float)]` | nodes are **strings** unless `nodetype=int`. Isolated nodes are lost. A file handle must be opened `'rb'`. `.gz`/`.bz2` are handled transparently |
| Adjacency list | `read_adjlist` / `write_adjlist`, `*_multiline_adjlist` | no (the multiline form keeps edge data) | same string-node issue |
| **GraphML** | `read_graphml(path, node_type=str)`, `write_graphml(G, path, infer_numeric_types=False, named_key_ids=False, edge_id_from_attribute=None)` | yes: typed attributes (int, float, bool, string) | no mixed, hyper or nested graphs. Values must be scalars, so serialise lists yourself. Good for Gephi and Cytoscape |
| **GML** | `read_gml(path, label='label', destringizer=None)`, `write_gml(G, path, stringizer=None)` | int, float, str, dict, list | attribute names can't contain `_`. Reserved names are ignored (graph: directed, multigraph, node, edge; node: id, label; edge: source, target, key). Other types need `literal_stringizer`/`literal_destringizer`. 7-bit ASCII |
| GEXF | `read_gexf`, `write_gexf` | yes, including dynamic/time attributes | GEXF 1.3 is recognised (3.6+). 3.7 adds description and keywords |
| **JSON node-link** | `nx.node_link_data(G, *, source, target, name='id', key, edges='edges', nodes='nodes')` → dict. `nx.node_link_graph(data, directed=False, multigraph=True, …)` | yes (attribute keys become strings) | the default key is `"edges"` since 3.6 (it was `"links"`), so read old files with `edges="links"`. **No `"multigraph"` key means you get a MultiGraph.** Keyword names must match on both sides |
| JSON other | `adjacency_data`/`adjacency_graph`, `cytoscape_data`/`cytoscape_graph` (Cytoscape.js), `tree_data`/`tree_graph` | | |
| DOT | `nx.nx_agraph.read_dot` / `write_dot` (pygraphviz), or the `nx.nx_pydot` equivalents | yes, as strings | pydot's `read_dot` returns a MultiGraph or MultiDiGraph |
| Pajek | `read_pajek` / `write_pajek` | some | returns a multigraph |
| Graph6 / Sparse6 | `read_graph6`, `to_graph6_bytes`, … | no | compact, for simple undirected graphs |
| Matrix Market | via `scipy.io.mmread` / `mmwrite` with the SciPy conversions | weights | |
| LEDA | `read_leda` | | read only |
| Text art | `nx.write_network_text(G)`, `generate_network_text` | | quick tree or forest printouts in a terminal |

- JSON round trip: `json.dumps(nx.node_link_data(G))` → `nx.node_link_graph(json.loads(s))`. Tuple node IDs survive it in 3.7 (checked). Attribute *values* must still be JSON-serialisable.
- **Pickle** (`pickle.dump(G, f)`) preserves everything, including node types, but it's Python-only and unsafe to load from untrusted sources.
- `p2g` is deprecated in 3.7.

## Generators (all return new graphs)

- Pass `create_using=nx.DiGraph` (and similar) where it's accepted. Random generators accept `create_using` since 3.4.
- **Classic**: `complete_graph`, `path_graph`, `cycle_graph`, `star_graph`, `wheel_graph`, `empty_graph(n)`, `null_graph()`, `trivial_graph`, `balanced_tree(r, h)`, `full_rary_tree`, `binomial_tree`, `barbell_graph`, `lollipop_graph`, `ladder_graph`, `circulant_graph`, `turan_graph`, `complete_multipartite_graph`, `kneser_graph`, `tadpole_graph`.
- **Lattices**: `grid_2d_graph(m, n)` (nodes are `(i, j)` tuples), `grid_graph(dim)`, `hypercube_graph`, `triangular_lattice_graph`, `hexagonal_lattice_graph`.
- **Random graphs** (all take `seed=`):
  - `gnp_random_graph` / `erdos_renyi_graph` / `binomial_graph`. `fast_gnp_random_graph` is faster for sparse p.
  - `gnm_random_graph`, `dense_gnm_random_graph`.
  - `watts_strogatz_graph`, `newman_watts_strogatz_graph`, `connected_watts_strogatz_graph`.
  - `barabasi_albert_graph`, `dual_barabasi_albert_graph`, `extended_barabasi_albert_graph`, `powerlaw_cluster_graph`.
  - `random_regular_graph`, `random_k_lift` (3.7).
  - `random_geometric_graph`, `soft_random_geometric_graph`, `waxman_graph`, `geographical_threshold_graph`, `navigable_small_world_graph`.
  - Trees: `random_labeled_tree`, `random_unlabeled_tree`, … (`random_tree` was removed).
- **Degree sequences**:
  - `configuration_model(deg_seq)` returns a **MultiGraph with self-loops**. Clean it with `nx.Graph(G)` then `G.remove_edges_from(nx.selfloop_edges(G))`.
  - Also `directed_configuration_model`, `expected_degree_graph`, `havel_hakimi_graph`, `random_degree_sequence_graph`, `joint_degree_graph`.
- **Communities**: `stochastic_block_model(sizes, p, seed)`, `planted_partition_graph`, `random_partition_graph`, `gaussian_random_partition_graph`, `caveman_graph`, `connected_caveman_graph`, `relaxed_caveman_graph`, `ring_of_cliques`, `windmill_graph`, and LFR (`LFR_benchmark_graph`).
- **Directed**: `gn_graph`, `gnr_graph`, `gnc_graph`, `scale_free_graph` (a MultiDiGraph), `random_k_out_graph`.
- **Small and named**: `petersen_graph`, `karate_club_graph`, `davis_southern_women_graph`, `florentine_families_graph`, `les_miserables_graph`, `graph_atlas(i)` (every graph up to 7 nodes), `sudoku_graph`, and more.
- **Derived**: `ego_graph(G, n, radius=1, undirected=False, distance=None)`, `line_graph`, `inverse_line_graph`, `mycielskian`, `visibility_graph` (time series), `interval_graph`, `stochastic_graph`, `prefix_tree`.

## Drawing

The docs are explicit: NetworkX is for **analysis**, and drawing may move to an add-on package. For anything serious, export to a dedicated tool: **Gephi**, **Cytoscape** (GraphML), **Graphviz**, or TikZ via `nx.to_latex`. **iplotx** and **hiveplotlib** accept NetworkX graphs directly.

**Quick plots with Matplotlib:**
```python
import matplotlib.pyplot as plt
pos = nx.spring_layout(G, seed=42)                      # always seed layouts
nx.draw_networkx(G, pos, node_size=50, with_labels=False)
nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "weight"))
plt.axis("off"); plt.savefig("g.png", dpi=200)
```

- **`nx.display(G, canvas=None, **kwargs)`** (3.5+) is the attribute-driven API. It reads per-node and per-edge styles from attributes: `pos`, `color`, `size`, `label`, `shape`, `alpha`, `visible`, …. You can rename which attribute holds each style with kwargs. With no `pos`, it computes `spring_layout`.
- **Save positions on the graph.** Layouts take `store_pos_as="pos"` (3.5+, checked) and then `nx.display(G)` uses them.
- Other helpers: `draw`, `draw_networkx_nodes`, `draw_networkx_edges`, `draw_networkx_labels`, `draw_circular`, `draw_kamada_kawai`, `draw_spring`, `draw_shell`, `draw_spectral`, `draw_planar`, `draw_bipartite`, `apply_matplotlib_colors`.
- **Layouts** return `{node: array([x, y])}`:
  - `spring_layout(G, k=None, pos=None, fixed=None, iterations=50, weight='weight', seed=None, method='auto')`. Weight means **attraction**, so bigger pulls nodes closer.
  - `kamada_kawai_layout` (needs SciPy; weight means distance), `forceatlas2_layout`, `arf_layout`, `spectral_layout`, `circular_layout`, `shell_layout(nlist=…)`, `bipartite_layout`, `multipartite_layout(subset_key='subset')` (for DAG layers, set each node's `subset` attribute from `topological_generations`), `bfs_layout`, `planar_layout`, `spiral_layout`, `random_layout`, `rescale_layout(_dict)`.
  - Coordinates span `[center − scale, center + scale]`. For `random_layout` it's `[0, scale]`. Most layouts are only tested in 2-D.
- **Graphviz layouts**: `nx.nx_agraph.graphviz_layout(G, prog='dot'|'neato'|'sfdp')`. pygraphviz 3.7-era wheels bundle Graphviz, so `pip install pygraphviz` usually just works now. The alternative is `nx.nx_pydot.graphviz_layout`.
- **LaTeX**: `nx.to_latex(G, pos, caption=…)`, `to_latex_raw`, `write_latex`. Styles come from attributes or dicts, and a list of graphs gives subfigures.
- **Big graphs**: don't plot 10⁵ nodes with Matplotlib. Aggregate (communities, `quotient_graph`), filter (k-core, the largest component), or use a GPU or web tool.
