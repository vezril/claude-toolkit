# Graph classes, attributes, views and copies

## Building

```python
import networkx as nx

G = nx.Graph(name="demo")                 # graph attrs as kwargs -> G.graph
G.add_node(1, time="5pm")                 # node + attrs
G.add_nodes_from([2, 3], role="leaf")     # shared attrs
G.add_nodes_from([(4, {"color": "red"})]) # (node, attrdict) pairs
G.add_edge(1, 2, weight=4.7)              # endpoints are auto-added
G.add_edges_from([(1, 3), (3, 4)], color="red")
G.add_edges_from([(1, 2, {"color": "blue"})])      # merges into the existing (1, 2)
G.add_weighted_edges_from([("a", "b", 0.3)])       # sets 'weight' (weight="…" to rename)
nx.add_path(G, [5, 6, 7]); nx.add_cycle(G, [7, 8, 9]); nx.add_star(G, [0, 10, 11])
```

- Adding a node or edge that already exists isn't an error. On `Graph`/`DiGraph` the attributes are **merged**.
- Constructors accept edge lists, dict-of-dicts, dict-of-lists, another graph, 2-D NumPy arrays, SciPy sparse arrays and PyGraphviz graphs, all through `to_networkx_graph`. `nx.DiGraph(a)` calls `from_numpy_array` for you.
- Removing: `remove_node(n)` (also removes its edges), `remove_nodes_from`, `remove_edge(u, v[, key])`, `remove_edges_from`, `clear()`, `clear_edges()`.
- Multigraph `add_edge(u, v, key=None, **attr)` **returns the key**. Keys default to the lowest unused integer. Passing an existing `key=` **updates** that edge instead of adding another.

## Attributes

| Level | Read / write | Bulk helpers |
|---|---|---|
| Graph | `G.graph['k'] = v` | — |
| Node | `G.nodes[n]['k'] = v` (the node must exist), `del G.nodes[n]['k']` | `nx.set_node_attributes(G, values, name)`, `nx.get_node_attributes(G, name, default=None)` |
| Edge | `G.edges[u, v]['k'] = v`, `G[u][v]['k'] = v`; multigraph `G.edges[u, v, key]['k']` | `nx.set_edge_attributes`, `nx.get_edge_attributes` |

- `G.edges` itself is read-only, but the attribute dicts it hands back are **writable**. Use two sets of brackets.
- `set_node_attributes(G, values, name)` behaves in three ways:
  - scalar or object: the **same object** goes on every node, so a list is shared
  - dict `{node: value}` with `name`
  - dict of dicts `{node: {attr: value}}` with no `name`
  - Nodes that aren't in G are silently ignored. (The argument order changed between 1.x and 2.x. Old snippets have it backwards.)
- `nx.is_weighted(G, weight='weight')` and `nx.is_negatively_weighted(G)` are cheap checks before choosing an algorithm.
- Attribute keys can be any hashable. Non-string keys need subscript access.

## Views (live, read-only, cheap)

| View | Iterates | Lookup | Extras |
|---|---|---|---|
| `G.nodes` / `G.nodes()` | nodes | `G.nodes[n]` → attr dict | set operations (`G.nodes & H.nodes`), `n in G.nodes` |
| `G.nodes(data=True)` | `(n, dict)` | — | full, **writable** dicts |
| `G.nodes(data='color', default='red')` / `G.nodes.data('color', default=…)` | `(n, value)` | — | |
| `G.edges` | `(u, v)`; multigraph `(u, v, key)` | `G.edges[u, v]` | set operations, `(u, v) in G.edges` |
| `G.edges()` (called) | `(u, v)`, **even for multigraphs** | | |
| `G.edges(data=True)` / `(data='w', default=1)` | `(u, v, dict)` / `(u, v, value)` | | membership, no set operations |
| `G.edges(keys=True, data=True)` | multigraph `(u, v, key, dict)` | | |
| `G.edges(nbunch)` | edges incident to nbunch | | |
| `G.adj` / `G[u]` | neighbour → edge-attr dict | `G[u][v]` | `G.adjacency()` iterates `(n, nbrdict)` |
| `G.degree` / `G.degree(nbunch, weight=…)` | `(n, deg)` | `G.degree[n]` | directed: `in_degree`, `out_degree`. No set operations |
| DiGraph `G.succ` / `G.pred` | | | `successors(n)`, `predecessors(n)`; `neighbors` = successors |

- Views reflect later changes to the graph. **Don't add or remove while iterating.** Snapshot with `list(...)` or `dict(...)` first.
- Degree is **computed on every call**, not stored. In hot loops: `deg = dict(G.degree)`.
- For undirected edge set operations, `(0, 1)` and `(1, 0)` are the same edge, but a set you compare against may contain both forms and produce duplicates.
- Reporting order is dict insertion order on CPython ≥ 3.6. Subgraphs **don't** promise to keep the original order.
- Shortcuts: `n in G`, `len(G)`, `for n in G`, `G.number_of_nodes()`, `G.number_of_edges()`, `G.number_of_edges(u, v)` (parallel count), `G.has_edge(u, v)`, `G.has_node(n)`, `G.size(weight='w')` (total weight).

## Copies, views and conversions

| Call | Result | Attribute dicts | Containers inside attrs |
|---|---|---|---|
| `G.copy()` / `nx.Graph(G)` / `G.__class__(G)` | independent graph | new dicts | **shared** (shallow) |
| `copy.deepcopy(G)` | independent | new | new |
| `G.copy(as_view=True)` | read-only view | shared | shared |
| `G.subgraph(nodes)` / `nx.induced_subgraph(G, nodes)` | **view**, structure frozen | **shared, writes go through to G** | shared |
| `G.subgraph(nodes).copy()` | independent induced subgraph | new | shared |
| `G.edge_subgraph(edges)` / `nx.edge_subgraph` | view induced by edges | shared | shared |
| `nx.restricted_view(G, nodes, edges)` | view hiding those nodes and edges | shared | shared |
| `nx.subgraph_view(G, filter_node=f, filter_edge=g)` | filtered view | shared | shared |
| `G.reverse(copy=True)` / `nx.reverse_view(G)` | reversed copy / view | | |
| `G.to_directed()` | DiGraph with both directions | **deep copy** | |
| `D.to_undirected(reciprocal=False)` | Graph. If both directions exist, **one arbitrary** attribute set is kept | deep copy | |
| `nx.to_directed(G)` / `nx.to_undirected(G)` (functions) | **views** | shared | |
| `nx.create_empty_copy(G, with_data=True)` | nodes only, no edges | | |
| "Fresh" structure only | `H = G.__class__(); H.add_nodes_from(G); H.add_edges_from(G.edges)` | none | |

- A subgraph of a subgraph is short-cut to the root graph (checked: `H.subgraph(…)._graph is G`). Filtered and restricted views still chain, and chains get slow after about 15 levels. Prefer `.copy()`.
- `D.to_undirected(reciprocal=True)` keeps only edges that exist in both directions.
- Subclass warning: `to_directed`/`to_undirected` create plain NetworkX classes unless you set the `to_directed_class` / `to_undirected_class` class attributes.

## Freezing

`nx.freeze(G)` blocks structural changes. Attribute edits still work. `nx.is_frozen(G)` tests it. To unfreeze, copy into a new graph: `H = nx.Graph(G)`. Views are already frozen in structure.

## Relabeling

- `nx.relabel_nodes(G, mapping, copy=True)`:
  - `mapping` is a dict (a partial mapping is fine, and keys that aren't nodes are ignored) or a **function**.
  - `copy=True` (the default) returns a new graph and leaves G alone.
  - `copy=False` relabels in place, ordering the renames so they don't collide (a→b, b→c renames b first). A **circular** mapping (a→b, b→a) raises in place, so use `copy=True`.
  - Mapping several nodes to one merges them. In a multigraph, colliding `(u, v, key)` get new integer keys. For predictable merging use `nx.contracted_nodes` / `nx.quotient_graph`.
- `nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute='orig')` is handy before matrix work, keeping the original label in an attribute.

## Graph-level functions (`nx.*`)

`density`, `degree_histogram`, `is_directed`, `is_empty`, `number_of_selfloops`, `selfloop_edges(G, data=…)`, `nodes_with_selfloops`, `non_edges`, `non_neighbors`, `common_neighbors`, `all_neighbors`, `is_path(G, path)`, `path_weight(G, path, weight)`, `nx.utils.graphs_equal`, `nx.describe(G)` (3.6+, prints a summary and returns None).

## Operators (build new graphs)

- **Binary**: `union` (node sets must be disjoint unless you pass `rename=`), `disjoint_union` (relabels to ints), `compose` (overlay, where H's attributes win), `intersection`, `difference`, `symmetric_difference`, `full_join`.
- `*_all` versions take many graphs: `compose_all`, `union_all`, `disjoint_union_all`, `intersection_all`.
- **Unary**: `complement`, `reverse`, `power(G, k)`.
- **Products**: `cartesian_product`, `tensor_product`, `strong_product`, `lexicographic_product`, `rooted_product`, `corona_product`, `modular_product`.
- **Minors**: `contracted_nodes`, `contracted_edge`, `identified_nodes`, `quotient_graph(G, partition)`, `equivalence_classes`.

## Custom classes and memory

- The dict factories are class attributes you can override: `node_dict_factory`, `node_attr_dict_factory`, `adjlist_outer_dict_factory`, `adjlist_inner_dict_factory`, `edge_attr_dict_factory`, `graph_attr_dict_factory`.
- The reference's `ThinGraph` example shares one edge-attribute dict across all edges to save memory, at the cost of losing per-edge attributes.
- Memory is dominated by the dicts. For millions of edges, keep attributes minimal, use integer nodes (`convert_node_labels_to_integers`), or move to a backend or a sparse matrix representation.
