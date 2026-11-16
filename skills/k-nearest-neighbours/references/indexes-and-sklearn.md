# kNN indexes, prototype selection, and scikit-learn

## The decision rule, written out

```
classification   ŷ(x) = argmax_c  Σ_{i ∈ N_k(x)} wᵢ · 1[yᵢ = c]
regression       ŷ(x) = Σ wᵢyᵢ / Σ wᵢ
```

Weights `wᵢ`: uniform; inverse distance `1/d`; `1/d²`; or a kernel `K(d/h)` — which in the limit is Nadaraya–Watson regression.

**Two distinct tie problems, worth separating:**

1. **Vote ties** — equal class counts. Mitigated by odd k in binary problems.
2. **Distance ties at the k-th neighbour** — if neighbours k and k+1 are equidistant but differently labelled, **the result depends on training-data order** (scikit-learn's own documented warning). Odd k does nothing for this.

## Index structures

### Brute force

O(nd) to compute distances per query, plus O(n log k) with a heap or O(n) expected with quickselect. scikit-learn notes query time grows as O[DN], is unaffected by data structure, and is *"largely unaffected by the value of k."*

Wins when: n is small (below ~30, log n ≈ n); you will issue few queries so index build does not amortise; the metric is exotic; input is sparse.

### k-d trees

Bentley, "Multidimensional binary search trees used for associative searching," *CACM* 18(9):509–517, Sept 1975, doi:10.1145/361002.361007.

Axis-aligned recursive splits. Average query O(log N) for randomly distributed points; worst case O(d·N^{1−1/d}).

**On the breakdown point, stated with real numbers rather than folklore:**

- scikit-learn's documented prose: the KD tree is *"very fast for low-dimensional (D < 20) neighbors searches"* but degrades as D grows; cost is roughly O[D log N] for *"D < 20 or so"*, rising toward O[DN] for larger D, at which point tree overhead makes it **slower than brute force**.
- scikit-learn's `algorithm='auto'` switches to brute force at **D > 15**.
- ⚠️ The widely-repeated **"n ≫ 2^d"** rule is folklore — no primary source found. Use the numbers above and label them as empirical implementation thresholds, not theorems.

### Ball trees

Omohundro, "Five Balltree Construction Algorithms," ICSI TR-89-063, 1989; Uhlmann, "Satisfying general proximity/similarity queries with metric trees," *Inf. Process. Lett.* 40(4):175–179, 1991.

Nested hyperspheres pruned by the triangle inequality. **Needs only a metric, not axis-aligned coordinates** — which is exactly why it supports Mahalanobis, Haversine and Hamming where k-d trees cannot. scikit-learn: *"can out-perform a KD-tree in high dimensions, though the actual performance is highly dependent on the structure of the training data."*

### LSH

Indyk & Motwani, "Approximate nearest neighbors: towards removing the curse of dimensionality," STOC'98, pp. 604–613, doi:10.1145/276698.276876. Gionis, Indyk & Motwani, VLDB 1999. Andoni & Indyk, *CACM* 51(1):117–122, 2008.

Query cost O(n^ρ) with ρ = 1/c for Hamming/L₁ and ≈1/c² for L₂ in the Andoni–Indyk construction.

### HNSW — proximity graphs, the current state of the art

Malkov & Yashunin, "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs."

**Get the citation right:** arXiv:1603.09320 (v1 30 Mar 2016, v4 14 Aug 2018); journal of record ***IEEE TPAMI* 42(4):824–836, April 2020**, doi:10.1109/TPAMI.2018.2889473. The DOI carries a 2018 stamp because it was online-first in Dec 2018 — **cite it as TPAMI 2020 (online 2018)**, not "TPAMI 2018."

Predecessor: Malkov, Ponomarenko, Logvinov & Krylov, "Approximate nearest neighbor algorithm based on navigable small world graphs," *Information Systems* 45:61–68, 2014, doi:10.1016/j.is.2013.10.006.

### Quantization

Jégou, Douze & Schmid, "Product Quantization for Nearest Neighbor Search," *IEEE TPAMI* 33(1):117–128, Jan 2011, doi:10.1109/TPAMI.2010.57.

Split each vector into m subvectors and quantize each with its own small codebook; combine with an **inverted file (IVF)** for coarse partitioning → IVFADC. ScaNN adds anisotropic quantization (Guo et al., arXiv:1908.10396).

### Libraries and benchmarks

FAISS (Johnson, Douze & Jégou, arXiv:1702.08734), Annoy, hnswlib, ScaNN. Benchmark suite: Aumüller, Bernhardsson & Faithfull, "ANN-Benchmarks," *Information Systems* 87, 2020.

**Production systems that are approximate-kNN engines:** FAISS, pgvector (Postgres; HNSW and IVFFlat indexes), Pinecone, Weaviate, Milvus, Qdrant, Elasticsearch/OpenSearch kNN. Per-vendor index details change often — verify individually.

## Prototype selection — condensing and editing

The step before [[learning-vector-quantization]]. Both families reduce the stored set by choosing among **real data points**.

| Method | What it removes | Effect |
|---|---|---|
| **CNN** (Hart 1968) | redundant interior points | finds a *consistent subset* — one that correctly 1-NN-classifies the whole training set. Order-dependent. Keeps boundary points. **Shrinks memory.** |
| **ENN** (Wilson 1972) | points misclassified by their own k neighbours | strips noise and borderline points. **Smooths the boundary.** |
| **Tomek links** (1976) | mutual-nearest-neighbour pairs of opposite class | cleans the boundary. Now better known as an imbalanced-learning undersampler. |
| **IB2 / IB3** (Aha et al. 1991) | IB2: stores only misclassified instances. IB3: adds a significance filter to reject noisy ones | incremental condensing |

**The conceptual distinction to carry forward:** *editing* cleans the boundary, *condensing* shrinks memory, and both are **prototype selection**. LVQ is **prototype generation** — it synthesises new vectors that need not exist in the data.

Citations: Hart, *IEEE Trans. IT* 14(3):515–516, May 1968, doi:10.1109/TIT.1968.1054155. Wilson, *IEEE Trans. SMC* SMC-2(3):408–421, July 1972, doi:10.1109/TSMC.1972.4309137. Tomek, *IEEE Trans. SMC* SMC-6(11):769–772, 1976. Aha, Kibler & Albert, *Machine Learning* 6(1):37–66, 1991, doi:10.1007/BF00153759.

## scikit-learn specifics

All from version 1.9.1 documentation and source, fetched 2026-11-11.

```python
KNeighborsClassifier(n_neighbors=5, *, weights='uniform', algorithm='auto',
                     leaf_size=30, p=2, metric='minkowski',
                     metric_params=None, n_jobs=None)
```

Also available: `KNeighborsRegressor`, `RadiusNeighborsClassifier`/`Regressor`, `NearestNeighbors` (exposing `kneighbors` and `radius_neighbors`), `KNeighborsTransformer`, `NeighborhoodComponentsAnalysis`, `NearestCentroid`.

### The `algorithm='auto'` decision procedure, exactly

Choose **brute** if any of:

- input is sparse
- `metric='precomputed'`
- **D > 15**
- **k ≥ N/2**
- the effective metric is not in the chosen tree's `valid_metrics`

Otherwise pick the first of `kd_tree`, `ball_tree` whose `VALID_METRICS` includes the metric.

Documented assumptions behind the heuristic: the number of query points is at least the same order as the number of training points; `leaf_size` is near its default of 30; and *"for D > 15 the intrinsic dimensionality is generally too high for tree-based methods."*

### Which metrics work with which structure

This is the gotcha that bites people.

- **KDTree:** `euclidean`/`l2`, `minkowski`, `p`, `manhattan`/`cityblock`/`l1`, `chebyshev`/`infinity`. **Minkowski family only.**
- **BallTree:** all of the above **plus** `seuclidean`, `mahalanobis`, `hamming`, `canberra`, `braycurtis`, `jaccard`, `dice`, `rogerstanimoto`, `russellrao`, `sokalmichener`, `sokalsneath`, `haversine`, `pyfunc`.
- **Brute:** anything in `sklearn.metrics.pairwise.PAIRWISE_DISTANCE_FUNCTIONS` plus scipy metrics. **`cosine` is brute-only** — it routes through `cosine_distances`.

### The zero-distance behaviour, from the source

`_get_weights` in `sklearn/neighbors/_base.py` carries this comment:

```
# if user attempts to classify a point that was zero distance from one
# or more training points, those training points are weighted as 1.0
# and the other points as 0.0
```

Mechanically it computes `1.0/dist` under `np.errstate(divide="ignore")`, then for any row containing an `inf` replaces the **entire row** with the inf-mask. So with `weights='distance'`, **an exact duplicate of the query point gets weight 1 and every other neighbour weight 0** — the prediction collapses to the duplicates. Duplicated training points override the vote entirely.

### Gotchas

- **No internal scaling.** Always `make_pipeline(StandardScaler(), KNeighborsClassifier())` so the scaler is fit inside each CV fold rather than on the full data.
- **Sparse input silently overrides `algorithm`** and forces brute force.
- `leaf_size` affects build and query speed and memory; storage is roughly training-set size / `leaf_size`; unused by brute force.
- `n_jobs` parallelises neighbour *search*, not `fit`.
- Large k relative to N destroys tree pruning — hence the `k ≥ N/2` → brute rule.
- For small N (≲30), brute force wins outright. If you will issue few queries, do not build a tree.
- `KNeighborsTransformer` **counts each training point as its own neighbour** in `n_neighbors`; with `mode='distance'` it computes one extra neighbour for compatibility. Include one extra neighbour in custom downstream estimators.
- `predict_proba` returns raw (possibly weighted) neighbour-vote fractions — **not calibrated**. Wrap in `CalibratedClassifierCV` if you need probabilities.
- `NeighborhoodComponentsAnalysis` stores an n_samples² pairwise matrix; per-iteration cost O(n_components · n_samples · min(n_samples, n_features)).

## Sources

scikit-learn 1.9.1 documentation and `sklearn/neighbors/_base.py`, fetched 2026-11-11. Bentley *CACM* 1975; Omohundro ICSI TR-89-063 1989; Uhlmann *IPL* 1991; Indyk & Motwani STOC'98; Andoni & Indyk *CACM* 2008; Malkov & Yashunin *IEEE TPAMI* 42(4), 2020; Malkov et al. *Information Systems* 45, 2014; Jégou/Douze/Schmid *IEEE TPAMI* 33(1), 2011; Hart 1968; Wilson 1972; Tomek 1976; Aha/Kibler/Albert 1991. Bibliographic records verified via Crossref. ScaNN's ICML 2020 venue and FAISS's *IEEE Trans. Big Data* 7(3) 2021 venue do not appear on the respective arXiv landing pages and are unverified.
