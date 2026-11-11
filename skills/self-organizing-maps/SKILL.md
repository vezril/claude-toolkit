---
name: self-organizing-maps
description: "Self-Organizing Maps (SOM / Kohonen maps) — the unsupervised competitive-learning algorithm that is a nonlinear dimensionality reduction, a clustering/vector quantization and a visualization method in one model. Covers the algorithm (a fixed lattice of codebook vectors, the best-matching unit, and the decaying neighbourhood kernel over LATTICE distance that is what actually produces topology preservation), why that makes it k-means-with-smoothed-centroids rather than a different family, the ordering and convergence phases, how to read the outputs (U-matrix for cluster boundaries, component planes for per-feature structure, hit histograms, quantization vs topographic error and why they trade off), the hyperparameters that matter, and an honest comparison with PCA, t-SNE and UMAP that does not oversell it. Precise about the theory: Erwin, Obermayer & Schulten (1992) proved the standard online rule is NOT gradient descent on any single global energy function, though a set of per-neuron potentials exists, and Heskes's modified winner rule restores a genuine energy; ordering is proved only in 1-D despite essentially all practical use being 2-D. Flags the folklore (the 5√n map-size rule is a MATLAB SOM Toolbox default whose own code comment calls it a guess). Covers variants (Neural Gas, Growing Neural Gas, GTM as the principled probabilistic alternative) and real applications including FlowSOM in cytometry, which is where SOM is genuinely still standard. Use when exploring high-dimensional data, choosing between SOM and UMAP/t-SNE/k-means, reading or building a SOM, clustering cytometry or expression data, or wanting a persistent interpretable prototype grid rather than a one-off embedding."
---

# Self-Organizing Maps

**A SOM fits a fixed grid of prototype vectors to your data such that grid-adjacent prototypes end up responding to similar inputs.** You then read the data by looking at the grid.

Two spaces are in play, and the whole method lives in the relationship between them: the **lattice** (a 2-D rectangular or hexagonal grid of units, with fixed positions) and the **input space** (where each unit's codebook vector lives, in the data's own units and dimensions).

Kohonen's SOM is the unsupervised sibling of [[learning-vector-quantization]], and came first — 1982 against LVQ's 1986/88.

## The algorithm

```
BMU (winner):   c(x) = argmin_i ‖x − m_i‖

online update — ALL units move:
   m_i(t+1) = m_i(t) + α(t) · h_{ci}(t) · [x(t) − m_i(t)]      for every i

neighbourhood (a function of LATTICE distance, not input-space distance):
   Gaussian:  h_{ci}(t) = exp( −‖r_c − r_i‖² / (2σ(t)²) )
   Bubble:    h_{ci}(t) = 1 if ‖r_c − r_i‖ ≤ σ(t), else 0
```

Both `α(t)` and the radius `σ(t)` decay monotonically.

**The key conceptual point.** The neighbourhood coupling *is* the mechanism that produces topology preservation. Because the BMU drags its **lattice** neighbours toward x, lattice-adjacent units acquire nearby codebook vectors and therefore respond to similar inputs. **Nearby nodes ⟹ similar inputs.** That is the entire point, and exactly what distinguishes a SOM from k-means.

**Batch SOM** is deterministic and needs no learning rate — a neighbourhood-weighted mean:

```
m_i = Σ_x h_{c(x),i} · x / Σ_x h_{c(x),i}
```

Faster, reproducible, and what Kohonen advocated for practical work in his later writing.

### It really is k-means with smoothed centroids

State this precisely, because it is the honest framing:

- With **σ → 0** only the winner updates, and online SOM degenerates to online competitive learning — MacQueen-style online k-means with a decaying step.
- **Batch SOM with σ → 0 is exactly Lloyd/batch k-means.**
- For a Gaussian kernel at any σ > 0 it is *not* exactly k-means. **SOM is k-means whose centroids are smoothed along a lattice.**

A scikit-learn maintainer put it the same way when declining to add it: SOM is *"very close to the mini batch k-means."*

## Two phases

| Phase | σ | α | Steps | Buys |
|---|---|---|---|---|
| **Ordering / rough** | large (a good fraction of the map side) | large (~0.5–0.9) | relatively few | the map **unfolds and becomes globally ordered** |
| **Convergence / fine** | small (down to ≈1) | small (~0.01–0.02) | many more | local accuracy, low quantization error |

**PCA/linear initialization starts the map already nearly ordered**, so the ordering phase can be shortened or skipped — and runs become reproducible.

⚠️ The widely-repeated **"fine phase ≥ 500 × the number of map units"** rule is attributed to Kohonen's book but could not be verified for this file. Treat it as empirical at best.

## How to read the outputs

A SOM is three things at once, and this is its real distinguishing claim: a **nonlinear dimensionality reduction**, a **clustering/vector quantization**, and a **visualization**, in one model.

- **U-matrix (unified distance matrix).** Each cell shows the distance between neighbouring units' weight vectors. **Ridges = cluster boundaries, valleys = clusters.** This is what makes a SOM a cluster-*discovery* tool rather than just a projection. In MiniSom it is `distance_map()`.
- **Component planes.** One map per input variable, showing that variable's codebook value at every unit. Reading two planes side by side reveals **correlation structure localized to regions of the map** — "in this corner feature A is high and B is low." **This is the genuinely distinctive SOM output; t-SNE and UMAP have no equivalent.**
- **Hit histogram.** BMU counts per unit = data density on the map. Zero-hit units are interpolating units sitting in low-density gaps.
- **Two quality measures, and they trade off against each other:**
  - **Quantization error** = mean `‖x − m_BMU(x)‖`. Falls as the map grows or σ shrinks.
  - **Topographic error** = fraction of samples whose **first and second BMUs are not lattice-adjacent** (Kiviluoto, ICNN'96).
  - A smaller neighbourhood lowers QE and raises TE, and vice versa. **There is no single accepted scalar quality measure for a SOM** — an honest limitation, and a downstream consequence of having no cost function.
  - Others: the topographic product (Bauer & Pawelzik 1992), trustworthiness/continuity (Venna & Kaski 2001).

## Hyperparameters that matter

**Map size.** The **5√n rule is resolved, and it is folklore with a traceable origin.** It is the MATLAB SOM Toolbox default:

```matlab
munits = ceil(5 * dlen^0.5); % this is just one way to make a guess...
```

That code comment is the authors' own assessment. **There is no theoretical basis**, and Kohonen's book gives no such formula. Use it to pick a starting point, not as a rule.

**Aspect ratio** — this one *is* a principled-ish heuristic, from the same source: side-length ratio = **√(λ₁/λ₂)** of the data autocorrelation matrix (note the **square root**, commonly mis-stated as the plain ratio), with a `√0.75` correction for hexagonal lattices. An elongated data cloud gets an elongated map, which reduces folding.

**Topology.** **Hexagonal is preferred** — 6 equidistant neighbours, so less directional bias than a rectangular lattice's 4-or-8 neighbours at unequal distances.

**Neighbourhood radius.** Initial σ a large fraction of the map; final σ ≈ 1. ⚠️ **MiniSom's defaults (`sigma=1, learning_rate=0.5`) give essentially no ordering phase** — fine for a 6×6 toy example, wrong for a 20×20 map. Always set σ relative to map size.

**Initialization.** Random weights, random data samples, or **PCA/linear** — the last gives a nearly ordered start and reproducible results.

## Honest comparison with PCA, t-SNE and UMAP

**What SOM uniquely gives — the real five:**

1. **A fixed, finite, interpretable grid of prototypes.** New data maps on by a single BMU lookup: cheap, deterministic, stable across runs once trained. Good for dashboards and production monitoring.
2. **A persistent model, not just an embedding.** Codebook vectors live **in the original feature space**, so every prototype is readable in the data's own units. UMAP gives you coordinates; SOM gives you coordinates *plus* interpretable prototypes.
3. **Component planes** tying the 2-D layout back to individual features.
4. **Quantization and projection in one pass**, so cost scales with the number of units rather than n. A big map compresses a huge dataset and downstream clustering runs on K prototypes instead of N points — exactly how FlowSOM gets its speed.
5. A **regular grid** suitable for stable, comparable, repeated-report visuals.

**Where t-SNE and UMAP simply beat it, stated plainly:** visual cluster separation; preservation of local neighbourhood structure; speed and scalability on large high-dimensional data (UMAP especially); **much stronger theoretical grounding** (an explicit objective function, which SOM lacks); and a far larger, more active ecosystem.

⚠️ **Do not claim out-of-sample projection as SOM's unique advantage.** t-SNE lacks a `transform`, but **UMAP has one** (`umap-learn.transform`, plus parametric UMAP). Over-claiming this is the most common way SOM advocacy goes wrong.

**Bottom line for 2026: for pure exploratory 2-D visualization, UMAP or t-SNE is the default and SOM is a niche choice.** SOM's live case is the five properties above, plus cytometry.

## The cost-function problem, stated correctly

The slogan "SOM has no cost function" is over-simplified. The precise result is **Erwin, Obermayer & Schulten (1992)**, who studied the formation of a topographic representation of `[0,1]` by a linear chain of neurons:

> "**We prove that the learning dynamics cannot be described by a gradient descent on a single energy function, but may be described using a set of potential functions, one for each neuron, which are independently minimized following a stochastic gradient descent.** We derive the correct potential functions for the one- and multi-dimensional case, and show that the energy functions given by Tolat (1990) are an approximation which is no longer valid in the case of highly disordered maps or steep neighborhood functions."

So, correctly:

1. The standard online SOM update is **not** SGD on any **single** global energy function.
2. It **is** describable as **one potential function per neuron**, each independently minimized by SGD. *This is the nuance almost always dropped — there are potentials, just not one.*
3. They *strengthen* existing convergence results, extending Kohonen's and Cottrell & Fort's ordering proofs to **any monotonically decreasing** neighbourhood function.
4. They **refute** a previously claimed energy function (Tolat 1990).

The obstruction is the argmin winner rule combined with a continuous input density: the natural candidate energy is discontinuous in the weights at Voronoi boundaries where the winner flips, and the SOM update matches its gradient only *within* each piece.

**The companion paper is the citable reason the neighbourhood schedule matters so much.** Erwin, Obermayer & Schulten, *Biol. Cybern.* 67(1):35–45, 1992, show convergence time *"may vary over several orders of magnitude depending on the range and also the shape of the neighborhood function"*; prove that **for neighbourhood functions convex over the chain length there exist NO metastable states**, while for all others metastable states exist and **can trap the algorithm**; and that the Gaussian has a width threshold above which metastable states cannot exist. Their practical upshot: *"Fastest convergence is achieved using neighborhood functions which are 'convex' over a large range around the winner neuron and yet have large differences in value at neighboring neurons."*

**The fix exists.** Heskes (1999) modifies the winner selection to `c = argmin_i Σ_j h_{ij}‖x − m_j‖²` — choose the unit minimising the *neighbourhood-summed* error rather than the plain nearest — and the resulting rule **does** descend a well-defined energy. Useful contrast: **Neural Gas minimizes an explicit cost; Heskes-SOM minimizes an explicit cost; standard Kohonen SOM does not.**

## Other known problems

- **Border effects.** Edge units have fewer lattice neighbours, so they are under-pulled; the map **contracts at its borders** and systematically under-represents the distribution's tails.
- **Magnification.** The map's unit density does **not** match the data density. The often-quoted `p(x)^{2/3}` holds only in the 1-D asymptotic narrow-neighbourhood limit; the general exponent is `d/(d+2)`, the same as plain VQ, and it depends on neighbourhood width. Do not state 2/3 unconditionally.
- **Sensitivity to initialization** and, for online SOM, **to sample presentation order**. Mitigated by PCA init and batch SOM.
- **Topology and size must be chosen a priori** — guess wrong and you get folding or wasted units. Growing Neural Gas grows instead.
- **Folding/twisting (topological defects)** and metastable trapping.
- **Ordering is only proved in 1-D.** General ordering and convergence in ≥2 lattice dimensions is **not established** — striking, given that essentially all practical use is 2-D. Say it.

## Variants

- **Neural Gas** (Martinetz & Schulten 1991; Martinetz, Berkovich & Schulten 1993) — **rank-based** neighbourhood `h_λ(k) = exp(−k/λ)` where k is the unit's *rank* by distance to x. **No fixed lattice at all**, and it **provably descends an explicit cost function**, unlike SOM.
- **Growing Neural Gas** (Fritzke 1995) — grows units where error accumulates; learns the topology instead of assuming it.
- **GTM** (Bishop, Svensén & Williams, *Neural Computation* 10(1):215–234, 1998) — the authors explicitly present it as *"a principled alternative to Kohonen's self-organizing map."* **This is the right "what SOM should have been" comparison.** It gives an explicit probabilistic density and log-likelihood objective, **monotone EM convergence**, a smooth parametric mapping from a latent grid (so ordering is enforced by the mapping's smoothness rather than a hand-tuned schedule), no neighbourhood schedule to tune, and closed-form magnification factors. What it does *not* fix: still local optima, still a fixed latent grid chosen a priori, generally more cost per iteration. State both halves.
- **GHSOM**, **ViSOM**, soft/probabilistic topographic VQ, batch SOM.

## Real applications

- **WEBSOM** — document maps. The headline number: **6,840,568 patent abstracts mapped onto a 1,002,240-node SOM** (Kohonen et al., *IEEE TNN* 11(3):574–585, 2000). A genuinely impressive 2000-era result and the best demonstration of the quantize-while-projecting property.
- **Gene expression** — Tamayo et al., *PNAS* 96(6):2907–2912, 1999, with the GENECLUSTER software. Historically how a generation of biologists first met clustering.
- **FlowSOM — the strongest evidence SOM is still live.** Van Gassen et al., *Cytometry Part A* 87(7):636–645, 2015: a SOM followed by consensus meta-clustering of the SOM nodes, visualized as star charts on a minimum spanning tree. The two-stage design is exactly the "compress to K prototypes, then cluster the prototypes" property, which is why it is fast. The independent benchmark (Weber & Robinson, *Cytometry Part A* 89(12):1084–1096, 2016) found *"Several methods performed well, including FlowSOM, X-shift, PhenoGraph, Rclusterpp, and flowMeans"*, with FlowSOM additionally having **very fast runtimes, suitable for interactive exploration on a laptop**. **This is the honest headline for SOM in 2026: a standard clustering step in high-dimensional flow and mass cytometry pipelines.**
- **Component-plane exploration of welfare/economic indicators** (Kaski & Kohonen's "poverty map") is the classic illustration, though the exact venue and figures could not be verified here.

## Always-apply

1. **Say which space you mean.** The neighbourhood is a function of **lattice** distance; the BMU is found by **input-space** distance. Confusing the two is the commonest conceptual error.
2. **Scale the features.** SOM is distance-based and inherits every pathology from [[k-nearest-neighbours]].
3. **Set σ relative to map size, and give it a real ordering phase.** Library defaults are tuned for toy maps.
4. **Prefer PCA initialization and batch SOM** when you want reproducibility.
5. **Report both quantization and topographic error.** Either alone is gameable, and they trade off.
6. **Do not say "SOM has no cost function"** — say no *single global energy* for the standard online rule, and note Heskes's fix and Neural Gas as the alternatives that do have one.
7. **Justify SOM over UMAP on the specific properties** — interpretable input-space prototypes, component planes, a persistent grid, or prototype compression before clustering. If you only need a 2-D picture, use UMAP.
8. **Treat the 5√n rule as a guess**, because its own authors did.

## How to use the references

- **`references/theory-and-practice.md`** — the Erwin/Obermayer/Schulten abstracts verbatim and the mechanism behind them, the magnification results and their conditions, the SOM Toolbox source for the size and aspect-ratio heuristics, the quality measures with citations, the variant family in depth, the application record with verified figures, and the implementation table with maintenance status and the documented scikit-learn rejection.

## Sources

Kohonen, "Self-organized formation of topologically correct feature maps," *Biological Cybernetics* 43(1):59–69, 1982, doi:10.1007/BF00337288 — ⚠️ **the abstract text could not be retrieved** (Springer redirects to login; not PubMed-indexed; publisher-elided on Semantic Scholar), so nothing is quoted from it here. Kohonen, "The self-organizing map," *Proc. IEEE* 78(9):1464–1480, 1990, doi:10.1109/5.58325 — the survey of record. Kohonen, *Self-Organizing Maps*, Springer Series in Information Sciences vol. 30, 1st ed. 1995 / 3rd ed. 2001 — **not readable for this file**, so anything attributed to "the book" is second-hand. Kohonen, "Essentials of the self-organizing map," *Neural Networks* 37:52–65, 2013, doi:10.1016/j.neunet.2012.09.018. Precursors: Willshaw & von der Malsburg, *Proc. R. Soc. Lond. B* 194(1117):431–445, 1976, doi:10.1098/rspb.1976.0087; von der Malsburg, *Kybernetik* 14:85–100, 1973. Erwin, Obermayer & Schulten, "Self-organizing maps: ordering, convergence properties and energy functions," *Biol. Cybern.* 67(1):47–55, 1992, doi:10.1007/BF00201801 (erratum 68(3):285, 1993) and "…stationary states, metastability and convergence rate," *Biol. Cybern.* 67(1):35–45, 1992, doi:10.1007/BF00201800 — abstracts read verbatim via PubMed. Heskes, "Energy functions for self-organizing maps," in Oja & Kaski (eds.), *Kohonen Maps*, Elsevier 1999, pp. 303–315, doi:10.1016/B978-044450270-4/50024-3. Kiviluoto, "Topology preservation in self-organizing maps," ICNN'96 1:294–299, doi:10.1109/ICNN.1996.548907. Bauer & Pawelzik, *IEEE TNN* 3(4):570–579, 1992. Cottrell, Fort & Pagès, *Neurocomputing* 21(1–3):119–138, 1998. Bishop, Svensén & Williams, *Neural Computation* 10(1):215–234, 1998, doi:10.1162/089976698300017953. Martinetz, Berkovich & Schulten, *IEEE TNN* 4(4):558–569, 1993. Villmann & Claussen, *Neural Computation* 18(2):446–469, 2006. Kohonen et al., *IEEE TNN* 11(3):574–585, 2000, doi:10.1109/72.846729. Tamayo et al., *PNAS* 96(6):2907–2912, 1999. Van Gassen et al., *Cytometry A* 87(7):636–645, 2015, doi:10.1002/cyto.a.22625. Weber & Robinson, *Cytometry A* 89(12):1084–1096, 2016, doi:10.1002/cyto.a.23030. MATLAB SOM Toolbox source `som/som_topol_struct.m` via `github.com/ilarinieminen/SOM-Toolbox`. MiniSom 2.3.6, `kohonen` 3.0.13, and the scikit-learn issue/PR threads (#2892, #19842), all fetched 2026-11-11.

**Folklore flagged above:** the **5√n map-size rule** (a SOM Toolbox default whose code comment calls it *"just one way to make a guess"*), the **500× fine-phase rule** (unverified), the unconditional **p(x)^{2/3}** magnification claim (1-D asymptotic only), and **out-of-sample projection as SOM-unique** (UMAP has it).

## Related

- [[learning-vector-quantization]] — Kohonen's supervised sibling; the standard pipeline is SOM to find structure, LVQ to sharpen the boundary.
- [[k-nearest-neighbours]] — the same "find the nearest prototype" core; SOM's codebook is what you get when you learn prototypes without labels.
- [[information-theory]] — vector quantization and the rate–distortion framing.
- [[neural-networks-biology]] — cortical topographic maps (retinotopy, somatotopy, tonotopy) are the real biological inspiration, and that skill is where the honest bounds on the analogy live.
- [[python]] — implementation context.
