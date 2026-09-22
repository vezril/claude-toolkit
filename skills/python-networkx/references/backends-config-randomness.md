# Backends, configuration, randomness, exceptions and utilities

## Backend dispatch

- Most NetworkX functions are wrapped in `@nx._dispatchable`, which can route a call to a separately installed **backend**.
- A backend registers entry points named `networkx.backends`, plus optionally `networkx.backend_info`. They're discovered at **install**, not import.
- Naming convention: backend `parallel` = package `nx-parallel` = module `nx_parallel`.

**Backends listed as known to work with 3.7:**

| Backend | What it does |
|---|---|
| `parallel` (nx-parallel) | joblib-parallel versions of CPU-heavy algorithms (betweenness, all-pairs, …) |
| `cugraph` (nx-cugraph) | GPU acceleration with RAPIDS cuGraph (NVIDIA) |
| `arangodb` (nx-arangodb) | ArangoDB as a persistence layer behind NetworkX graphs |
| `neptune` (nx-neptune) | offloads to Amazon Neptune Analytics. See [[nx-neptune]]: its backend **clears the target graph** on every call unless `skip_graph_reset` is set |

**Three ways to use one:**
1. **Per call**: `nx.betweenness_centrality(G, k=10, backend="parallel")`. It converts G, caches the conversion, and runs the backend version. Backend-specific kwargs pass straight through (`get_chunks=…` for parallel). It raises if the backend doesn't implement the function.
2. **Backend graph object**: `H = nx_parallel.ParallelGraph(G)` or `nx.Graph(backend="cugraph")` (3.6+). Passing H to a function uses that backend with no conversion.
3. **Automatic, by configuration.** Conversion is always opt-in:

| Config | Env var | Effect |
|---|---|---|
| `nx.config.backend_priority` (= `.algos`) | `NETWORKX_BACKEND_PRIORITY` / `NETWORKX_BACKEND_PRIORITY_ALGOS` | list of backends to try, in order, for functions that **don't return graphs** (pagerank, …). NetworkX graphs are converted and cached |
| `nx.config.backend_priority.generators` | `NETWORKX_BACKEND_PRIORITY_GENERATORS` | functions that **return graphs** (`from_pandas_edgelist`, `empty_graph`, …) return backend graphs, avoiding conversion. The backend graph may not behave exactly like a NetworkX graph |
| `nx.config.backend_priority.classes` | `NETWORKX_BACKEND_PRIORITY_CLASSES` | `nx.Graph(data)` builds a backend graph |
| `nx.config.fallback_to_nx` (default False) | `NETWORKX_FALLBACK_TO_NX` | when a backend graph reaches a function its backend doesn't implement: convert to NetworkX and run, instead of raising |
| `nx.config.cache_converted_graphs` (default True) | `NETWORKX_CACHE_CONVERTED_GRAPHS` | cache conversions in `G.__networkx_cache__` |
| `nx.config.warnings_to_ignore` | `NETWORKX_WARNINGS_TO_IGNORE` | e.g. `{"cache"}` silences the cached-value warning |
| `nx.config.backends.<name>` | backend-specific | e.g. `nx.config.backends.parallel.n_jobs`, `nx.config.backends.neptune.graph_id` |

- **Env vars are read at `import networkx`.** Setting `os.environ[...]` afterwards does nothing. Set them in the shell, or set `nx.config` in code.
- `nx.config` is a global Mapping (attribute or bracket access) and a **context manager**: `with nx.config(backend_priority=["parallel"]): …`. Don't rely on it across threads.
- **The cache can go stale.** `G.add_edge(u, v, weight=x)` clears it. A direct write like `G[u][v]['weight'] = x` **doesn't**. After direct writes, call `G.__networkx_cache__.clear()`.
- Before converting, dispatch asks each backend `can_run(name, args, kwargs)` and `should_run(...)`. A backend may decline small inputs where NetworkX would be faster.
- **Introspection**:
  - `nx.betweenness_centrality.backends` gives the installed backends implementing a function.
  - `help(fn)` lists backend notes and extra parameters.
  - To log dispatch decisions:
    ```python
    import logging
    nxl = logging.getLogger("networkx"); nxl.addHandler(logging.StreamHandler()); nxl.setLevel(logging.DEBUG)
    ```
- `@not_implemented_for` type checks run **before** dispatch, so a backend can't bypass them.

**Writing a backend (summary):**
- Expose an interface object with `convert_from_nx(G, edge_attrs, node_attrs, preserve_*_attrs, name, graph_name)` and `convert_to_nx(result)`. `can_run`, `should_run` and `on_start_tests` are optional.
- Your graph class needs `__networkx_backend__ = "name"`, `is_directed()` and `is_multigraph()`.
- Register it:
  ```toml
  [project.entry-points."networkx.backends"]
  name = "pkg.interface:BackendInterface"
  [project.entry-points."networkx.backend_info"]
  name = "pkg:get_info"   # must not import your package
  ```
- `get_info()` returns `backend_name`, `project`, `package`, `url`, `short_summary`, `default_config` and `functions` (per-function `url`, `additional_docs`, `additional_parameters`).
- Test against the NetworkX suite: `NETWORKX_TEST_BACKEND=<name> NETWORKX_FALLBACK_TO_NX=True pytest --pyargs networkx`. Unimplemented functions xfail when fallback is off.
- The developer interface changes often. Watch the NetworkX dispatch meetings.

## Randomness

NetworkX uses both Python's `random` and `numpy.random`. They're "dangerously similar", and **each function prefers one**. The `seed=` argument decides which RNG is used:

| `seed=` | Behaviour |
|---|---|
| `None` (default) | the **global** RNG of the function's preferred package, so not reproducible unless you've seeded that global |
| `int` | a **local** RNG seeded with it, for this call and anything it calls, then discarded. Reproducible |
| `numpy.random` | force NumPy's global RNG, even in a function written for `random` |
| `np.random.RandomState(42)` / `np.random.default_rng(42)` | your RNG object, reused across calls, and shareable with scikit-learn and others |
| `random.Random(42)` | works in `random`-based functions. NumPy-based functions may not accept it |

- To seed globally, set **both**: `random.seed(246); np.random.seed(4812)`.
- For one RNG across a whole project, create a NumPy Generator and pass it everywhere.
- Helpers: `nx.utils.create_random_state`, `create_py_random_state`, and the `@np_random_state` / `@py_random_state` decorators for your own functions.

## Exceptions (all subclass `nx.NetworkXException`)

`NetworkXError`, `NetworkXPointlessConcept` (null graph), `NetworkXAlgorithmError`, `NetworkXUnfeasible`, `NetworkXNoPath`, `NetworkXNoCycle`, `NodeNotFound`, `HasACycle`, `NetworkXUnbounded`, `NetworkXNotImplemented`, `AmbiguousSolution`, `ExceededMaxIterations`, `PowerIterationFailedConvergence` (has `.num_iterations`).

- `NodeNotFound` subclasses `NetworkXException`, not `KeyError`. Catch it by name.
- The **null graph** has 0 nodes. An **empty graph** has n nodes and 0 edges (`nx.empty_graph(n)`). Algorithms treat them differently.

## Utilities (`nx.utils`, not top-level)

- **Helpers**: `pairwise(iterable, cyclic=False)` (turns a node path into edges), `arbitrary_element`, `flatten`, `groups` (many-to-one into one-to-many), `make_list_of_ints`, `dict_to_numpy_array`, `nodes_equal`, `edges_equal(…, directed=)`, `graphs_equal`.
- **Data structures**: `UnionFind` (`uf.union(a, b)`, `uf[x]`, `uf.to_sets()`), `MappedQueue` (a heap with updatable priorities).
- **Sequences**: `powerlaw_sequence`, `discrete_sequence`, `zipf_rv`, `cumulative_distribution`, `random_weighted_sample`, `weighted_choice`.
- **Decorators** for writing your own graph functions:
  - `@not_implemented_for("directed")` / `("multigraph")`
  - `@nodes_or_number(0)` (accepts n or an iterable of nodes)
  - `@open_file(path_arg, mode)` (accepts a path or file handle, handles `.gz`/`.bz2`)
  - `@np_random_state` / `@py_random_state`, `@argmap`
- **Bandwidth reduction**: `cuthill_mckee_ordering`, `reverse_cuthill_mckee_ordering` (reorder nodes before building sparse matrices).

## Performance checklist

1. Integer node labels and minimal attributes cut memory and hashing cost.
2. Cache `dict(G.degree)` and neighbour sets. Don't recompute them inside loops.
3. Avoid building views inside tight loops. Iterate `G.adj.items()` once and keep what you need.
4. Build big graphs in bulk (`add_edges_from` with a generator), not one edge at a time in Python loops with lookups.
5. Sample (`betweenness_centrality(k=…)`, `nx.approximation.average_clustering`) or restrict (`k_core`, the largest component) before expensive analysis.
6. Move linear-algebra work to SciPy sparse (`to_scipy_sparse_array`) and dense all-pairs work to `floyd_warshall_numpy`.
7. Beyond that, use a backend (`parallel` for CPUs, `cugraph` for GPUs, `neptune` for managed scale), or a compiled library for the hot path. Keep NetworkX as the API.
