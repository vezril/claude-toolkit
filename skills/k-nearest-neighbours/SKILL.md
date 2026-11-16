---
name: k-nearest-neighbours
description: "k-nearest neighbours (kNN) — the lazy, instance-based classifier and regressor where the model *is* the training set. Covers the theory that makes it respectable (Fix & Hodges 1951 consistency; the Cover & Hart 1967 bound R* ≤ R ≤ 2R*(1−R*), and why it is strictly asymptotic), the decision rule and distance weighting, choosing a distance metric (Euclidean/Manhattan/Minkowski/Mahalanobis/cosine/Hamming/Gower) and why feature scaling is mandatory rather than cosmetic, choosing k by cross-validation (and why the √n rule is folklore), the curse of dimensionality done properly (Beyer et al. 1999 distance concentration *and* the authors' own conditions under which it does not apply; Aggarwal et al. 2001 on L₁ beating L₂ in high dimensions), making it fast (k-d trees, ball trees, LSH, HNSW, product quantization — i.e. that vector databases and RAG embedding retrieval *are* approximate kNN), prototype selection by condensing and editing (Hart 1968, Wilson 1972) as the bridge to LVQ, and the scikit-learn specifics and gotchas. Use when choosing or tuning a nearest-neighbour model, picking a distance metric, setting k, debugging why kNN performs badly (usually scaling, irrelevant features, or dimensionality), reasoning about approximate nearest-neighbour search / vector indexes / embedding retrieval, or wanting an honest baseline — even if 'kNN' is not named but the problem is 'find the most similar records' or 'search these embeddings'."
---

# k-Nearest Neighbours

**kNN classifies a point by looking at the k stored examples closest to it and taking a vote** (or, for regression, an average). It has no training phase — only storage, and optionally index construction. Every bit of computation is deferred to query time.

That single structural fact drives every strength and weakness in this file. There is nothing to fit, so adding data is free and the decision boundary can be arbitrarily irregular. But the model *is* the dataset, so memory and latency scale with n, and the algorithm has no mechanism whatsoever for ignoring a feature that does not matter.

It is also, unexpectedly, one of the most-executed primitives in production machine learning: **embedding retrieval is approximate kNN**. Every vector-database query and every RAG lookup is "find the k nearest vectors to this one." A 1951 algorithm runs behind a great deal of 2026 infrastructure.

## The theory that makes it respectable

**Fix & Hodges (1951)** established consistency of the k_n-NN rule for sequences with k→∞ and k/n→0. (This is theirs, not Stone's — a common misattribution. Stone 1977 is the universal-consistency result for weighted-average *regression*.)

**Cover & Hart (1967)** proved the bound everyone quotes. For M classes, with R the 1-NN error and R\* the Bayes error:

```
R* ≤ R ≤ R*(2 − (M/(M−1))·R*)        M classes
R* ≤ R ≤ 2R*(1 − R*)                 two classes
```

so 1-NN is **at worst twice the Bayes error**. In their words: *"half the classification information in an infinite sample set is contained in the nearest neighbor."*

Three things people drop when quoting it:

1. **It is asymptotic (n → ∞) and says nothing about finite n.** "kNN is at most twice as bad as Bayes" is routinely over-claimed.
2. **The bounds are metric-independent** — the nearest neighbour converges to the query point under any metric on a separable metric space.
3. The k-NN bounds **decrease monotonically in k** toward R\*, so 1-NN is asymptotically the *worst* member of the family — yet 1-NN is admissible at finite n (no k ≠ 1 beats it against every distribution).

## Distance is the model

| Metric | Use it when |
|---|---|
| **Euclidean** L₂ | the default; isotropic, low-dimensional continuous data |
| **Manhattan** L₁ | high dimensions (see below), grid/count data, outlier-robust |
| **Minkowski** L_p | the general family; `p < 1` is not a metric |
| **Chebyshev** L_∞ | worst-case-per-coordinate reasoning |
| **Mahalanobis** | **correlated or differently-scaled features** — it is Euclidean after whitening, so it quotients out scale *and* correlation |
| **Cosine** | text, TF-IDF, embeddings — when magnitude is uninformative |
| **Hamming** | categorical / binary |
| **Gower** | **mixed** numeric + categorical, and missing values |

Two facts worth keeping: cosine is **not** a metric (angular distance is), and for L2-normalised vectors `‖x−y‖² = 2(1−cos)`, so **Euclidean and cosine give the identical neighbour ranking after normalisation** — which is why embedding search uses them interchangeably.

**Feature scaling is mandatory, and the reason is mechanical.** The distance is a sum over features, so a feature with a large numeric range contributes a large term **regardless of its predictive relevance**. Income in dollars (range ~10⁵) against age in years (range ~10²) makes age invisible: you have fitted a univariate income classifier without noticing. Scaling is not cosmetic — it changes which model you fit. Scaling is really the degenerate case of feature weighting (a diagonal metric with weights 1/σ); the non-degenerate versions are feature selection and metric learning ([[learning-vector-quantization]] learns exactly these).

## Choosing k

Small k = low bias, high variance, jagged boundary. Large k = smoother and more biased; k = n returns the global majority class for everything. The useful shorthand is that the **effective number of parameters is ≈ n/k** (ESL §2.3.3).

**Cross-validate.** That is the method; everything else is a way to centre the grid.

- **Odd k** for binary classification is a convention that prevents *vote* ties. It does nothing for *distance* ties at the k-th neighbour (where scikit-learn's result depends on training-data order), and it does not generalise past two classes.
- The theoretically optimal regression rate is **k ∝ n^{4/(d+4)}**.
- ⚠️ **The k ≈ √n rule is folklore.** No primary source, no textbook derivation, absent from scikit-learn's docs. It coincides with the proven rate only at d = 4. Use it to centre a CV grid, never as a rule.
- Under **class imbalance**, large k lets majority votes swamp minority regions and collapses minority recall.

## The curse of dimensionality, done properly

**Beyer, Goldstein, Ramakrishnan & Shaft (1999)** proved that under broad conditions — *much* broader than i.i.d. dimensions — as dimensionality grows, **the distance to the nearest point approaches the distance to the farthest point**, so "nearest" stops meaning anything. Their empirical finding: this *"can occur for as few as 10-15 dimensions."* The real hypothesis is that **the relative variance of the distance distribution vanishes**, not that the data is i.i.d. across dimensions.

**The part that is always dropped, and dropping it turns a theorem into a slogan.** The authors devote a section to when their result does *not* apply, opening: *"it should **not** be interpreted to mean that high-dimensional indexing is never useful."* Specifically it does not bite when:

- the data falls into **well-separated clusters and the query is guaranteed to land inside one** — *"the perfectly classical classification problem."* (With their own caveat: if the query might fall outside every cluster, the theorem just reapplies to the choice of nearest *cluster*.)
- the **intrinsic dimensionality is much lower** than the ambient dimensionality.
- the query is an exact or approximate match (if some point matches exactly, DMIN = 0).

**Aggarwal, Hinneburg & Keim (2001)** then showed the norm matters: contrast `DMAX − DMIN` grows as **d^{1/k − 1/2}** for L_k. So **L₁ contrast grows as √d, L₂ is bounded, and L_k for k > 2 vanishes** — Manhattan is consistently preferable to Euclidean in high dimensions. Their Table 2: L₁ gives better relative contrast than L₂ in **95.6% of cases at d = 10, 97.1% at d = 20, 98.2% at d = 100**.

The geometric picture (ESL §2.5) is just as sobering: to capture 1% of the data in a hypercubical neighbourhood in 10 dimensions you need an edge spanning **63% of each coordinate's range**. "Local" is a fiction. And nearest neighbours sit near the *boundary* of the sample, so kNN extrapolates rather than interpolates.

**kNN's sharpest practical weakness follows from this:** it cannot down-weight an irrelevant feature. Every useless column adds pure distance noise. Fix it with dimensionality reduction, feature selection, supervised metric learning (NCA, LMNN), or learned embeddings.

## Making it fast

| Method | Where it fits |
|---|---|
| **Brute force** | O(nd) per query. Wins for small n (log n ≈ n below ~30) and when you will issue few queries |
| **k-d trees** (Bentley 1975) | axis-aligned splits, Minkowski metrics only; scikit-learn: *"very fast for low-dimensional (D < 20)"* and its `auto` switches away at **D > 15** |
| **Ball trees** | nested hyperspheres pruned by the triangle inequality; needs only a *metric*, so it supports Mahalanobis/Haversine/Hamming where k-d trees cannot |
| **LSH** (Indyk & Motwani 1998) | sublinear O(n^ρ) approximate search |
| **HNSW** (Malkov & Yashunin) | proximity-graph ANN; current state of the art |
| **Product quantization** (Jégou et al. 2011) + **IVF** | compress vectors into subspace codebooks; the basis of billion-scale search |

⚠️ **The "n ≫ 2^d" rule for when k-d trees stop paying is folklore** — untraceable. Cite scikit-learn's actual numbers (D < 20 in prose, D > 15 in the `auto` heuristic) and label them as empirical implementation thresholds.

**The modern headline:** FAISS, pgvector, Pinecone, Weaviate, Milvus, Qdrant and OpenSearch kNN are all approximate-kNN engines. If you are doing RAG, you are doing kNN.

## Shrinking the stored set — the bridge to LVQ

- **Condensing** (Hart 1968, CNN) finds a subset that still 1-NN-classifies the whole training set: keeps boundary points, discards redundant interior ones. Order-dependent.
- **Editing** (Wilson 1972, ENN) removes points *misclassified by their own neighbours* — strips noise and smooths the boundary.
- **Tomek links** (1976), **IB2/IB3** (Aha et al. 1991) refine both.

All of these are **prototype selection**: they choose among real data points. [[learning-vector-quantization]] takes the next step to **prototype generation** — synthesising a few well-placed labelled vectors that need not be data points at all. That is exactly the step from kNN to LVQ.

## When it is the right choice in 2026

**Yes:** embedding retrieval / RAG / semantic search (the standard, not merely viable); a baseline you need today; recommenders and collaborative filtering; irregular boundaries with no parametric story; case-based reasoning where the neighbours *are* the deliverable; anomaly detection by k-th-NN distance; online settings where "training" on new data is just an append.

**No:** large n under a latency budget; high-dimensional *raw* features; many irrelevant features; heavy class imbalance; you need a **compact deployable artifact** (the model is the dataset — a hard blocker on-device); you need **calibrated probabilities** (vote fractions are coarse multiples of 1/k and uncalibrated); non-stationary data where the stored set silently rots.

**Emphasise the baseline role.** `make_pipeline(StandardScaler(), KNeighborsClassifier())` with CV over k is five lines and sets a floor that a surprising number of elaborate models fail to clear. If a gradient-boosted ensemble cannot beat tuned kNN, the problem is the features, not the model.

## Always-apply

1. **Scale the features, inside a `Pipeline`, fit per CV fold.** scikit-learn's kNN does no scaling internally. Unscaled kNN is a different model than the one you think you are fitting.
2. **Cross-validate k.** Do not use √n as anything but a grid centre.
3. **Choose the metric from the data's type**, not by default: Mahalanobis for correlated features, cosine for embeddings, Gower for mixed types, L₁ when d is large.
4. **Count your irrelevant features before blaming the algorithm.** kNN cannot ignore them.
5. **Check the intrinsic dimensionality before invoking the curse** — Beyer's own exceptions (separated clusters, low intrinsic dimension) cover a lot of real classification problems.
6. **Do not trust `predict_proba`** without calibration.
7. **Compare index choices by measured recall@k and latency**, not by reputation; `algorithm='auto'` already encodes sensible thresholds.

## How to use the references

- **`references/theory-and-dimensionality.md`** — the Cover & Hart machinery in full (the posterior vector, the asymptotic conditional risk, when the bound is attained and why the "no-information experiment" attains it), Fix & Hodges and Stone, the k-NN bound hierarchy, Beyer et al.'s theorem and its exact hypotheses, Aggarwal et al.'s contrast result, and the geometric/sample-complexity view.
- **`references/indexes-and-sklearn.md`** — exact complexity for each index, the full `algorithm='auto'` decision procedure, which metrics work with which tree, HNSW/PQ/IVF and the ANN library landscape, the condensation and editing algorithms, and the scikit-learn gotchas (zero-distance weighting collapsing the vote, sparse input forcing brute force, `KNeighborsTransformer`'s self-neighbour counting, `leaf_size`, `n_jobs`).

## Sources

Fix & Hodges, *Discriminatory analysis, nonparametric discrimination*, USAF School of Aviation Medicine, Project 21-49-004, Report 4, Feb 1951 (report number taken from Cover & Hart's own reference list, which is the reliable source — DTIC is inaccessible). Cover & Hart, "Nearest neighbor pattern classification," *IEEE Trans. Information Theory* 13(1):21–27, 1967, doi:10.1109/TIT.1967.1053964 — read in full. Stone, "Consistent Nonparametric Regression," *Ann. Statist.* 5(4):595–620, 1977. Beyer, Goldstein, Ramakrishnan & Shaft, "When Is 'Nearest Neighbor' Meaningful?", ICDT'99, LNCS 1540:217–235 — quotations here are from the near-identical tech-report version (UW–Madison TR #1377, June 1998), which is openly available; re-check against the LNCS text before quoting it as ICDT. Aggarwal, Hinneburg & Keim, "On the Surprising Behavior of Distance Metrics in High Dimensional Space," ICDT 2001, LNCS 1973:420–434 — read in full. Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning*, 2nd ed. (§2.3.2 p.14, §2.3.3 p.16, §2.5 p.22, §13.4 p.475) — section and page numbers verified against the official table of contents; the verbatim sentences were not readable. Bentley, *CACM* 18(9):509–517, 1975. Indyk & Motwani, STOC'98. Malkov & Yashunin, *IEEE TPAMI* 42(4):824–836, April 2020 (online-first Dec 2018; arXiv:1603.09320) — cite as TPAMI 2020, not 2018. Jégou, Douze & Schmid, *IEEE TPAMI* 33(1):117–128, 2011. Hart, *IEEE Trans. IT* 14(3):515–516, 1968. Wilson, *IEEE Trans. SMC* SMC-2(3):408–421, 1972. Aha, Kibler & Albert, *Machine Learning* 6(1):37–66, 1991. scikit-learn 1.9.1 documentation and `sklearn/neighbors/_base.py` source, fetched 2026-11-11.

Two claims in circulation are flagged folklore above because no primary source could be found for either: **k ≈ √n**, and **n ≫ 2^d** for k-d tree viability.

## Related

- [[learning-vector-quantization]] — the supervised prototype-*generation* descendant; where kNN stores everything, LVQ learns a few labelled prototypes.
- [[self-organizing-maps]] — the unsupervised sibling; same "find the nearest prototype" core, different second step.
- [[information-theory]] — Cover co-authored both this bound and *Elements of Information Theory*; the metric-independence argument is information-theoretic in spirit.
- [[python]] / [[python-networkx]] — implementation context.
- [[vault-graphrag]] — embedding retrieval in practice, i.e. approximate kNN with a different name.
