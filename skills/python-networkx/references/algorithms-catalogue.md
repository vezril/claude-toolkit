# Algorithm catalogue (NetworkX 3.7)

Organised by task. Functions are top-level `nx.*` unless a namespace is shown. "gen" means the function returns a generator. Check `@not_implemented_for` restrictions in each docstring. Common ones are noted.

## Shortest paths

**Choosing:**

| Situation | Use | Cost |
|---|---|---|
| Unweighted, fewest hops | `shortest_path(G, s, t)` (BFS; bidirectional when both ends are given) | O(V+E) |
| Non-negative weights | `shortest_path(G, s, t, weight='w')` or `dijkstra_path`, `bidirectional_dijkstra` | O((V+E) log V) |
| Negative weights, no negative cycle | `bellman_ford_path`, `shortest_path(..., method='bellman-ford')`, `goldberg_radzik` | O(VE) |
| All pairs, sparse, negative OK | `johnson(G, weight)` | O(V(V+E) log V) |
| All pairs, dense | `floyd_warshall`, `floyd_warshall_numpy`, `floyd_warshall_tree` (3.7) | O(V³) |
| Heuristic available (grids, geo) | `astar_path(G, s, t, heuristic=h, weight='w')` | |
| Several sources | `multi_source_dijkstra(G, sources, target)` | |
| Nearest of many targets | sentinel node: join each target to `T` at weight 0, path to `T`, `path[-2]` is the target (subtract 1 from the length when unweighted) | |
| Everything toward one target | `single_target_shortest_path(_length)`, or reverse the graph | |

- **`shortest_path` / `shortest_path_length`** default to `weight=None`, and `method` is only used when weights are. The return shape depends on which of source and target you pass:
  - both → a list
  - source only → `{target: path}`
  - target only → `{source: path}`
  - neither → an **iterator** of `(source, {target: path})`
- **Errors.** `NodeNotFound` for a missing source or target. `NetworkXNoPath` when target isn't reachable. `has_path(G, s, t)` is a cheap check.
- **Weights** can be an attribute name or a function `w(u, v, d)`. The function may return **`None` to hide an edge**: `weight=lambda u, v, d: 1 if d['color'] == 'red' else None` finds the shortest red path. Use it to mix in node weights too.
- **Multigraphs.** Dijkstra uses the lightest parallel edge (checked).
- Both path and length: `single_source_dijkstra(G, s, t)` returns `(length, path)`. `single_source_dijkstra(G, s)` returns `(dists, paths)`.
- Predecessors: `dijkstra_predecessor_and_distance`, `bellman_ford_predecessor_and_distance`, `floyd_warshall_predecessor_and_distance`, `reconstruct_path`.
- Negative cycles: `negative_edge_cycle(G)`, `find_negative_cycle(G, s)`. Floyd-Warshall raises on a negative cycle (3.7).
- **Dijkstra never checks for negative weights** and can return wrong answers silently (see SKILL.md).
- All shortest paths: `all_shortest_paths` (gen), `single_source_all_shortest_paths`, `all_pairs_all_shortest_paths`.
- Averages: `average_shortest_path_length(G)` raises on a disconnected graph.
- Enumerating paths, from `simple_paths`:
  - `all_simple_paths(G, s, t, cutoff=k)` (gen, O(n!) worst case; target may be several nodes)
  - `all_simple_edge_paths`
  - `shortest_simple_paths(G, s, t, weight)` (gen, yields in increasing length, so take the first k)
  - `is_simple_path`

## Traversal

- **DFS**: `dfs_edges`, `dfs_tree`, `dfs_preorder_nodes`, `dfs_postorder_nodes`, `dfs_predecessors`, `dfs_successors`, `dfs_labeled_edges` (tree/back/forward/nontree labels). All take `depth_limit`.
- **BFS**: `bfs_edges`, `bfs_tree`, `bfs_layers(G, sources)`, `descendants_at_distance(G, s, d)`, `bfs_successors`, `bfs_predecessors` (proposed for deprecation in 3.7), `bfs_labeled_edges`, `generic_bfs_edges(G, s, neighbors=…)`, `bfs_beam_edges(G, s, value, width)`.
- **Edge traversals** that respect multigraph keys and orientation: `edge_dfs`, `edge_bfs` (`orientation='original'|'reverse'|'ignore'`).

## Connectivity and structure

- **Components**:
  - Undirected: `connected_components` (gen of sets), `number_connected_components`, `node_connected_component(G, n)`, `is_connected`. These raise on directed graphs.
  - Directed: `strongly_connected_components`, `kosaraju_strongly_connected_components`, `weakly_connected_components`, `condensation(G)` (the SCC DAG), `attracting_components`, `is_semiconnected`.
- **Robustness**:
  - `articulation_points`, `biconnected_components`, `bridges`, `has_bridges`, `local_bridges`, `chain_decomposition`.
  - `node_connectivity` / `edge_connectivity` (optionally s–t), `minimum_node_cut`, `minimum_edge_cut`, `stoer_wagner` (global min cut), `k_components`, `k_edge_components`, `k_edge_augmentation`, `node_disjoint_paths`, `edge_disjoint_paths`, `all_node_cuts`.
- **Cores**: `core_number`, `k_core`, `k_shell`, `k_crust`, `k_corona`, `k_truss`, `onion_layers`. These raise on multigraphs (3.5+) and don't allow self-loops. Remove them with `G.remove_edges_from(nx.selfloop_edges(G))`.
- **Distance measures** (connected graphs only): `eccentricity`, `diameter`, `radius`, `center`, `periphery`, `barycenter`/`centroid` (3.7 alias), `resistance_distance`, `effective_graph_resistance`, `kemeny_constant`, `harmonic_diameter` (tolerates disconnection).
- **Cuts and expansion**: `cut_size`, `volume`, `conductance`, `normalized_cut_size`, `edge_expansion`, `node_expansion`, `boundary_expansion`, `mixing_expansion`, `node_boundary`, `edge_boundary`.
- **Isolates**: `isolates`, `number_of_isolates`, `is_isolate`.
- **Efficiency**: `global_efficiency`, `local_efficiency`, `efficiency(G, u, v)`.
- **Assortativity**: `degree_assortativity_coefficient`, `attribute_assortativity_coefficient`, `numeric_assortativity_coefficient`, `average_neighbor_degree`, `average_degree_connectivity`, mixing matrices.
- **Other structure**: `reciprocity` / `overall_reciprocity`, `rich_club_coefficient` (3.7 adds `n_samples`), small-world `sigma`/`omega` (expensive), `s_metric`, `non_randomness`, `flow_hierarchy`, `dominating_set`, `dominance_frontiers`, `immediate_dominators`, `voronoi_cells`, `wiener_index`, `number_of_walks`, `random_walk` (3.7).

## Centrality and link analysis

| Question | Function | Notes |
|---|---|---|
| Most connections | `degree_centrality` (in/out variants) | normalized by n−1. Star centre = 1.0 |
| Brokers on shortest paths | `betweenness_centrality(G, k=None, normalized=True, weight=None, endpoints=False, seed=None)` | Brandes O(nm), O(nm + n² log n) weighted. **Sample with `k`** on big graphs. Weights must be > 0, and float weights can miscount |
| Edge brokers | `edge_betweenness_centrality` | drives `girvan_newman` |
| Close to everyone | `closeness_centrality(G, distance=None, wf_improved=True)`, `harmonic_centrality` (fine when disconnected) | |
| Influence via neighbours | `eigenvector_centrality` / `_numpy`, `katz_centrality` / `_numpy` | power iteration can raise `PowerIterationFailedConvergence` (checked on a 2-node DiGraph). Use the `_numpy` variant or raise `max_iter` |
| Web-style ranking | `pagerank(G, alpha=0.85, personalization=None, max_iter=100, tol=1e-6, weight='weight', dangling=None)`, `google_matrix` | undirected input is treated as two directed edges. Stops at `len(G)*tol`, so if `len(G)*tol >= 2` it "converges" after one step. Lower `tol` for big graphs |
| Hubs vs authorities | `hits(G)` returns `(hubs, authorities)` | |
| Spreaders | `voterank`, `percolation_centrality`, `laplacian_centrality`, `second_order_centrality`, `load_centrality` | |
| Current-flow (electrical) | `current_flow_betweenness_centrality`, `current_flow_closeness_centrality`/`information_centrality`, approximate variants | connected undirected graphs, needs SciPy |
| Groups | `group_betweenness_centrality`, `group_closeness_centrality`, `group_degree_centrality`, `prominent_group` | |
| Other | `subgraph_centrality`, `estrada_index`, `communicability_betweenness_centrality`, `dispersion`, `local_reaching_centrality`/`global_reaching_centrality`, `trophic_levels` | |

Store results for later with `nx.set_node_attributes(G, scores, 'pagerank')`.

## Link prediction

`jaccard_coefficient`, `adamic_adar_index`, `resource_allocation_index`, `preferential_attachment`, `common_neighbor_centrality`, and community-aware variants (`cn_soundarajan_hopcroft`, `ra_index_soundarajan_hopcroft`, `within_inter_cluster`). All take `ebunch=` (node pairs) and return a **generator of `(u, v, score)`**. With no ebunch they score **all non-edges**, which is O(n²), so always pass candidates. Undirected only.

## Communities (`nx.community`)

| Method | Call | Notes |
|---|---|---|
| **Leiden** (3.7, native) | `leiden_communities(G, weight='weight', resolution=1.0, max_level=None, seed=None, metric='cpm', theta=0.01)`, `leiden_partitions` | guarantees well-connected communities, which Louvain doesn't. **Default metric is CPM**, not modularity, so set `metric='modularity'` for Louvain-comparable output. CPM's resolution scale differs from modularity's |
| Louvain | `louvain_communities(G, weight='weight', resolution=1, threshold=1e-7, max_level=None, seed=None)`, `louvain_partitions` (every level) | resolution > 1 gives smaller communities. Self-loops are read as already-merged communities, so remove them first unless that's what they mean. Pass a seed for reproducibility (checked) |
| Greedy modularity (Clauset–Newman–Moore) | `greedy_modularity_communities(G, weight=None, resolution=1, cutoff=1, best_n=None)` | deterministic. **weight defaults to None** |
| Label propagation | `label_propagation_communities` (semi-synchronous, undirected), `asyn_lpa_communities(G, weight, seed)`, `fast_label_propagation_communities` | fast, unstable between runs |
| Fixed number k | `asyn_fluidc(G, k, seed)` (connected, undirected), `edge_betweenness_partition(G, k)`, `kernighan_lin_bisection` (k = 2), `spectral_modularity_bipartition`, `greedy_node_swap_bipartition` | |
| Divisive hierarchy | `girvan_newman(G)` (gen of successively finer partitions; each step recomputes edge betweenness, so it's slow) | |
| Overlapping | `k_clique_communities(G, k)` | |
| Local, around seeds | `greedy_source_expansion(G, source=…)` | |
| Trees | `lukes_partitioning(G, max_size)` | exact optimal |
| **Quality** | `modularity(G, communities, weight, resolution)`, `constant_potts_model`, `overlapping_modularity`, `partition_quality` → `(coverage, performance)`, `is_partition`, `is_cover` | Barber's bipartite modularity: `nx.bipartite.modularity` (3.7) |

Most return a **list or generator of sets**. Map to `{node: community_id}` with `{n: i for i, c in enumerate(parts) for n in c}`.

## Clustering, triangles and cliques

- **Clustering**: `triangles` (undirected), `all_triangles` (gen, 3.6), `transitivity`, `clustering(G, nodes=None, weight=None)` (the directed variant exists), `average_clustering` (`count_zeros=True`), `square_clustering`, `generalized_degree`. Bipartite has its own `nx.bipartite.clustering`.
- **Cliques** (maximal cliques are exponential in the worst case):
  - `find_cliques(G)` (gen of maximal cliques, undirected), `find_cliques_recursive`, `enumerate_all_cliques`, `max_weight_clique(G, weight)`, `node_clique_number`, `number_of_cliques`, `make_max_clique_graph`.
  - Approximate: `nx.approximation.max_clique`, `large_clique_size`.

## DAGs

Most DAG functions **don't check acyclicity**. Call `is_directed_acyclic_graph(G)` first, or catch `NetworkXUnfeasible` / `HasACycle` where they raise.

- **Ordering**: `topological_sort` (gen; raises on a cycle when consumed), `topological_generations` (layers, good for parallel scheduling), `lexicographical_topological_sort(G, key=…)` (deterministic), `all_topological_sorts` (exponential).
- **Reachability**: `ancestors(G, n)`, `descendants(G, n)`, `transitive_closure(G, reflexive=False)`, `transitive_closure_dag`, `transitive_reduction` (drops attributes; copy them back if needed).
- **Paths**: `dag_longest_path(G, weight='weight', default_weight=1)` and its length (critical path), `dag_to_branching`.
- **Other**: `antichains`, `antichain_width` (3.7), `is_aperiodic`, `lowest_common_ancestor(G, a, b)`, `all_pairs_lowest_common_ancestor`, `colliders`, `v_structures`, d-separation (`is_d_separator`, `is_minimal_d_separator`, `find_minimal_d_separator`), `moral_graph`.
- **Cycles in general graphs**:
  - `find_cycle(G, source=None, orientation=None)` returns the edge list and raises `NetworkXNoCycle`.
  - `simple_cycles(G, length_bound=None)` (gen, directed or undirected), `cycle_basis(G)` (undirected), `minimum_cycle_basis`, `chordless_cycles`, `girth`.

## Trees and spanning trees

- **Tests**: `is_tree`, `is_forest`, `is_arborescence`, `is_branching`.
- **Spanning trees**: `minimum_spanning_tree(G, weight='weight', algorithm='kruskal'|'prim'|'boruvka')`, `maximum_spanning_tree`, `minimum_spanning_edges` (gen), `SpanningTreeIterator` (in weight order), `number_of_spanning_trees`, `random_spanning_tree`.
- **Directed**: `minimum_spanning_arborescence`, `maximum_branching`, `ArborescenceIterator`.
- **Encodings**: `to_prufer_sequence` / `from_prufer_sequence`, `to_nested_tuple` / `from_nested_tuple`, `join_trees`, `junction_tree`.
- **Other**: `nx.approximation.steiner_tree`. Tree isomorphism: `tree_isomorphism`, `rooted_tree_isomorphism`.

## Flows and cuts (`nx.*`, with algorithms in `nx.flow`)

- **Max flow**: `maximum_flow(G, s, t, capacity='capacity', flow_func=None)` returns `(value, flow_dict)`. Also `maximum_flow_value`, `minimum_cut` → `(cut_value, (S, T))`, `minimum_cut_value`.
  - **An edge without a capacity attribute has infinite capacity.** If an s–t path is made entirely of such edges, the call raises `NetworkXUnbounded` (checked).
  - `capacity` can be a callable (3.7).
- **Choosing `flow_func`**: `nx.flow.preflow_push` (the default), `edmonds_karp`, `shortest_augmenting_path`, `dinitz`, `boykov_kolmogorov`. Build once with `nx.flow.build_residual_network` to reuse it.
- **Min-cost flow**: `network_simplex(G, demand='demand', capacity, weight)` → `(cost, flow)`. Also `min_cost_flow`, `min_cost_flow_cost`, `max_flow_min_cost(G, s, t)`, `capacity_scaling`, `cost_of_flow`. Node `demand`s must sum to 0, or `NetworkXUnfeasible` is raised. `NetworkXUnbounded` means a negative-cost cycle with infinite capacity. Use integer weights.
- **Other**: `gomory_hu_tree(G)` (all-pairs min cuts, undirected), `stoer_wagner`.

## Matching, covering, independence and coloring

- **Matching**: `max_weight_matching(G, maxcardinality=False, weight='weight')`, `min_weight_matching`, `maximal_matching`, `is_matching`, `is_maximal_matching`, `is_perfect_matching`.
- **Bipartite**: `nx.bipartite.maximum_matching` (Hopcroft–Karp), `eppstein_matching`, `minimum_weight_full_matching` (needs SciPy), `to_vertex_cover`.
- **Independence**: `maximal_independent_set(G, nodes=None, seed=None)` returns a **set** in 3.7 (a list before). The approximate maximum is `nx.approximation.maximum_independent_set`.
- **Covers**: `min_edge_cover`, `is_edge_cover`, `nx.approximation.min_weighted_vertex_cover`, dominating sets.
- **Coloring**: `greedy_color(G, strategy='largest_first'|'smallest_last'|'DSATUR'|'connected_sequential_bfs'|…, interchange=False)` returns `{node: color}`. Also `equitable_color(G, num_colors)`. Polynomials: `chromatic_polynomial`, `tutte_polynomial` (SymPy).

## Isomorphism and similarity

- **Quick filters**: `could_be_isomorphic` (3.7 removed the old aliases `fast_…`/`faster_…`). `weisfeiler_lehman_graph_hash(G, node_attr=…, edge_attr=…)` gives the same hash for isomorphic graphs, so it's a fast inequality check, but equal hashes don't prove isomorphism.
- **Exact**:
  - `is_isomorphic(G1, G2, node_match=…, edge_match=…)`. Build matchers with `nx.isomorphism.categorical_node_match('label', None)` and `numerical_edge_match('w', 1)`.
  - **VF2++** (preferred): `vf2pp_is_isomorphic`, `vf2pp_isomorphism`, `vf2pp_all_isomorphisms`, plus 3.7's `vf2pp_subgraph_is_isomorphic` / `vf2pp_subgraph_isomorphism` / `vf2pp_all_subgraph_isomorphisms` and monomorphism variants.
  - Classic `nx.isomorphism.GraphMatcher` / `DiGraphMatcher` (`subgraph_is_isomorphic` = induced, `subgraph_is_monomorphic` = not induced).
  - **ISMAGS** handles symmetry and supports directed graphs and multigraphs (3.7).
- **Similarity**:
  - `graph_edit_distance` (exponential; set `timeout=`), `optimize_graph_edit_distance` (gen of improving upper bounds), `optimal_edit_paths`.
  - `simrank_similarity`, `panther_similarity`, `panther_vector_similarity`.

## Approximation (`nx.approximation`)

- **Connectivity**: `node_connectivity`, `local_node_connectivity`, `all_pairs_node_connectivity`, `k_components`.
- **Hard problems**: `max_clique`, `clique_removal`, `maximum_independent_set`, `min_weighted_vertex_cover`, `min_weighted_dominating_set`, `min_edge_dominating_set`, `min_maximal_matching`, `densest_subgraph`, `randomized_partitioning`, `one_exchange` (max-cut), `treewidth_min_degree` / `treewidth_min_fill_in`.
- **Estimates**: `diameter` (a **lower bound**, unlike `nx.diameter`), `average_clustering` (sampled).
- **TSP**: `traveling_salesman_problem(G, weight='weight', nodes=None, cycle=True, method=None)` (None picks an algorithm to suit the graph type), `christofides`, `greedy_tsp`, `simulated_annealing_tsp`, `threshold_accepting_tsp`, `asadpour_atsp`. Christofides needs a complete metric undirected graph. `traveling_salesman_problem` builds the metric closure for you.
- **Steiner tree**: `steiner_tree`.

## Bipartite (`nx.bipartite`)

- There's **no bipartite graph class**. Mark the sides with a node attribute, conventionally `bipartite=0/1`, and pass node sets explicitly.
- `nx.bipartite.sets(G)` raises `AmbiguousSolution` on disconnected graphs.
- Functions: `is_bipartite`, `is_bipartite_node_set`, `color`, `density`, `degrees`.
- **Projections**: `projected_graph`, `weighted_projected_graph`, `collaboration_weighted_projected_graph`, `overlap_weighted_projected_graph`, `generic_weighted_projected_graph`.
- Bipartite versions of the centralities, clustering, matchings (above), `birank`, `butterflies` (3.7), `spectral_bipartivity`, `node_redundancy`.
- Matrix and generators: `biadjacency_matrix` / `from_biadjacency_matrix`, generators (`random_graph`, `configuration_model`, `complete_bipartite_graph`, …), and its own `read_edgelist` / `write_edgelist`.

## Other families

- **Euler**: `is_eulerian`, `eulerian_circuit`, `eulerian_path`, `has_eulerian_path`, `eulerize`.
- **Planarity**: `is_planar`, `check_planarity` → `(bool, PlanarEmbedding)`, `planar_layout`.
- **Chordal**: `is_chordal`, `chordal_graph_cliques`, `complete_to_chordal_graph`.
- **Special classes**: `is_perfect_graph`, `is_at_free`, `is_threshold_graph`, `is_distance_regular`, `is_k_regular` / `k_factor`.
- **Tournaments**: `nx.tournament.*`. **Triads**: `triadic_census`, `triad_type`.
- **Graphical sequences**: `is_graphical(seq, method='eg'|'hh')`, `is_digraphical`, `is_multigraphical`.
- **Structural holes**: `constraint`, `effective_size`. **Vitality**: `closeness_vitality`.
- **Graph editing**: `double_edge_swap` / `connected_double_edge_swap` / `directed_edge_swap` (degree-preserving randomisation), `spanner`, summarisation (`snap_aggregation`, `dedensify`).
- **Node classification** (`nx.algorithms.node_classification`): `harmonic_function`, `local_and_global_consistency`, both semi-supervised from a `label` attribute.
- **Linear algebra** (needs SciPy):
  - Matrices: `adjacency_matrix`, `incidence_matrix`, `laplacian_matrix`, `normalized_laplacian_matrix`, `directed_laplacian_matrix`, `magnetic_laplacian_matrix` (3.7), `modularity_matrix`, `bethe_hessian_matrix`.
  - Spectra: `*_spectrum`.
  - Spectral tools: `algebraic_connectivity`, `fiedler_vector`, `spectral_ordering`, `spectral_bisection`.
  - Attribute matrices: `attr_matrix`.
  - Laplacians use **out-degree**. For in-degree, use `G.reverse(copy=False)` and transpose.

## Common errors

| Exception | Usual cause |
|---|---|
| `NetworkXNotImplemented` | wrong graph type (directed or multigraph) for this function |
| `NetworkXNoPath` / `NodeNotFound` | unreachable target / label typo or type mismatch (`'1'` vs `1` after reading a file) |
| `NetworkXError` | general misuse: disconnected input to diameter, modifying a frozen view |
| `NetworkXPointlessConcept` | the null graph (0 nodes) passed where it makes no sense |
| `NetworkXUnfeasible` / `HasACycle` | cycle in a DAG function, flow demands that don't balance |
| `NetworkXUnbounded` | an unbounded optimisation (negative cycle) |
| `PowerIterationFailedConvergence` | pagerank / eigenvector / hits didn't converge in `max_iter` |
| `AmbiguousSolution` | e.g. bipartite sets of a disconnected graph |
| `ExceededMaxIterations` | an iteration bound was hit |
