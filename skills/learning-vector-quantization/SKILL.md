---
name: learning-vector-quantization
description: "Learning Vector Quantization (LVQ) — Kohonen's supervised, prototype-based classifier, where the model is a small set of labelled vectors in the input space that you can print, plot and hand to a domain expert. Covers the supervision distinction everyone gets wrong (VQ / LBG / k-means / SOM are unsupervised and minimise distortion; LVQ is supervised and shapes the decision boundary), the attract/repel update rule for LVQ1, OLVQ1's per-prototype adaptive rate, the LVQ2/2.1 window rule and its documented divergence failure, LVQ3's stabilising same-class case, and the principled reformulations that fixed classic LVQ's central theoretical defect — GLVQ (Sato & Yamada 1995) deriving the update from a differentiable cost, GRLVQ learning per-feature relevances, GMLVQ learning a full discriminative Mahalanobis-like metric you can read for feature interactions, and RSLVQ's likelihood route. Honest about status: LVQ is not in the mainstream 2026 toolchain (scikit-learn rejected it; MATLAB deprecated it), and where it still lives is interpretability-critical work plus the prototype revival in few-shot learning (Prototypical Networks) and explainable deep models (ProtoPNet). Use when a classifier must be inspectable in the data's own units, when choosing a prototype-based method, when you need supervised feature weighting or a learned metric, when working on small-n/high-d biomedical or spectroscopic data, or when reasoning about prototype/case-based approaches to interpretable ML."
---

# Learning Vector Quantization

**LVQ learns a small set of labelled prototype vectors, and classifies by nearest prototype.** At test time it *is* 1-NN — but over M learned prototypes instead of n stored training points, with M ≪ n.

The reason to care is interpretability of an unusually direct kind. The model's parameters are vectors **in the input space, in the data's own units**. You can print them, plot them, and say to a domain expert: *"these three vectors are what the classifier considers a typical case of X."* No saliency map, no SHAP values, no post-hoc attribution whose faithfulness is itself contested — the parameters are the explanation.

## The one thing people get wrong

**LVQ is supervised. Its unsupervised relatives are not.** This distinction is the whole point of the method and is constantly blurred.

| | Reads labels? | Objective |
|---|---|---|
| VQ / LBG / k-means | **No** | minimise quantization distortion `E‖x − w_BMU‖²` |
| SOM ([[self-organizing-maps]]) | **No** | quantize *and* preserve lattice topology |
| **LVQ** | **Yes** | place prototypes to shape the **decision boundary** |

The consequence worth spelling out: **k-means puts a prototype where the data mass is; LVQ puts one where the boundary needs defending.** The repulsion term has no analogue in any unsupervised method.

Kohonen's own recommended pipeline uses both: SOM or k-means to find the structure, then LVQ to sharpen the boundary.

⚠️ **Wikipedia's LVQ article states that LVQ "is a precursor to self-organizing maps (SOM)." This is chronologically backwards.** SOM is 1982; LVQ is 1986/88.

## The algorithm

Prototypes `w_j ∈ ℝ^d`, `j = 1..M`, each with a **fixed** class label `c(w_j)`. Training sample `(x, y)`.

```
BMU (winner):    j* = argmin_j ‖x − w_j‖

LVQ1 — only the winner moves:
  if c(w_j*) == y :   w_j* ← w_j* + α(t)·[x − w_j*]      ATTRACT
  else            :   w_j* ← w_j* − α(t)·[x − w_j*]      REPEL
  all other prototypes unchanged
```

with `0 < α(t) < 1` decreasing monotonically.

**Why the learning rate must decay.** Same reason as any stochastic-approximation scheme — the Robbins–Monro conditions `Σα = ∞` and `Σα² < ∞`. With α fixed, every new sample yanks the winner by a constant fraction and the prototypes jitter forever around their targets without settling.

**OLVQ1** gives each prototype its *own* rate, which is why it converges much faster:

```
correct:   w_j* ← w_j* + α_j[x − w_j*] ;   α_j ← α_j / (1 + α_j)
wrong:     w_j* ← w_j* − α_j[x − w_j*] ;   α_j ← α_j / (1 − α_j)   [capped]

combined:  α_j(t) = α_j(t−1) / (1 + s(t)·α_j(t−1)),   s(t) = ±1
```

The cap keeps `α_j` at or below the user's initial global α.

## The variants, and what each fixes

**LVQ2/2.1 — the window rule.** Update the two nearest prototypes when one is correct and one is wrong, but *only* if the sample falls in a window around their midplane:

```
w_wrong   ← w_wrong   − α(t)(x − w_wrong)
w_correct ← w_correct + α(t)(x − w_correct)

only if   min(dᵢ/dⱼ, dⱼ/dᵢ) > s        with  s = (1−w)/(1+w)
```

Geometrically the condition puts x between two Apollonian spheres. **Its documented failure**, in Sato & Yamada's words: *"no attention is given to what might happen to the location of the w_k, so the reference vectors diverge in the long run."*

**LVQ3** adds the stabilising case: if **both** nearest prototypes have the correct class, **both move toward x** at a reduced rate `ε·α`. That same-class attraction is what keeps prototypes anchored to their class mass rather than drifting.

⚠️ **Wikipedia's LVQ3 same-class update has the wrong sign** — it shows repulsion. The LVQ_PAK source moves both prototypes *toward* the sample. Trust the source.

Sato & Yamada's verdict on LVQ3 is worth keeping too: *"if only one reference vector is assigned to each class, LVQ3 is the same as LVQ2.1, and the problem of reference vector divergence remains unsolved."*

## The theoretical defect, and GLVQ fixing it

**Classic LVQ1/2/2.1/3 are heuristics with no cost function they provably minimise.** No objective means no convergence guarantee, no principled way to set the prefactors, and no way to extend the method by differentiating something. This was the central theoretical objection.

**GLVQ** (Sato & Yamada, NIPS 1995) fixed it. From their abstract: *"We prove that Kohonen's rule as used in LVQ does not satisfy the convergence condition and thus degrades recognition ability."*

Let `w₁` be the nearest prototype of the **same** class as x and `w₂` the nearest of a **different** class, with distances `d₁, d₂`. Define the **relative distance difference**:

```
μ(x) = (d₁ − d₂)/(d₁ + d₂)          ∈ [−1, +1],  negative ⟺ correctly classified
S = Σᵢ f(μ(xᵢ))                     f monotonically increasing
```

Gradient descent on S with squared Euclidean distance gives:

```
w₁ ← w₁ + α·(∂f/∂μ)·d₂/(d₁+d₂)²·(x − w₁)      ATTRACT, scaled by d₂
w₂ ← w₂ − α·(∂f/∂μ)·d₁/(d₁+d₂)²·(x − w₂)      REPEL,   scaled by d₁
```

Two things to notice. It is **the same attract/repel shape as LVQ, but with derived prefactors** — attraction on the correct prototype is weighted by the *wrong* prototype's distance and vice versa. And `∂f/∂μ` acts as a per-sample gain: with a sigmoid `f` sharpening over training time, it *"has a single peak at μ = 0, and the peak width becomes narrower as t increases, so the input vectors that affect learning are gradually restricted to those around the decision boundaries."* That is an annealed margin, and it is genuinely elegant.

Classic LVQ falls out as a degenerate special case when `f` is linear — **the non-linearity of `f` is the whole improvement**.

## Learning the metric — the part that is still interesting

Once there is a cost function you can differentiate anything, including the distance.

- **GRLVQ** (Hammer & Villmann 2002) learns per-feature relevances `λᵢ ≥ 0` in `d_λ(x,w) = Σᵢ λᵢ(xᵢ − wᵢ)²`. You get **supervised feature weighting and selection for free**, and `λ` reads off directly as "how much does this feature matter."
- **GMLVQ** (Schneider, Biehl & Hammer 2009) learns a **full** positive-semidefinite relevance matrix:

  ```
  d_Λ(x,w) = (x − w)ᵀ Λ (x − w),     Λ = ΩᵀΩ   (so Λ ⪰ 0 by construction)
  ```

  **How to read Λ** — this is the selling point. The **diagonal** gives per-feature relevance; the **off-diagonal** entries give the feature *correlations* the classifier exploits. It is a Mahalanobis-like metric learned **discriminatively** rather than estimated from the marginal covariance, which is the precise upgrade over plain Mahalanobis in [[k-nearest-neighbours]]. A low-rank Ω gives supervised dimensionality reduction — a discriminative 2-D projection you can plot. **LGMLVQ** uses a separate Λ per prototype or class.
- **RSLVQ** (Seo & Obermayer 2003) takes the other principled route: a likelihood-ratio cost under a Gaussian mixture, with soft assignment replacing the hard winner. GLVQ gives you a margin-like cost; RSLVQ gives you a generative likelihood.

## Where it sits among its neighbours

- **vs kNN** — kNN stores *everything* and performs no abstraction; there is no "typical case," only all cases. Memory `n·d` vs `M·d`; prediction `O(nd)` vs `O(Md)`.
- **vs neural networks** — opaque weights needing post-hoc attribution.
- **vs k-medoids and CNN subsets** — **LVQ prototypes need not be real data points.** They are averaged vectors that may occur nowhere in the dataset. This is a genuine double edge: true abstraction and smoother boundaries, but a prototype can be physically meaningless (an "average face," a chemically impossible spectrum). State both halves.
- **Nearest Class Mean** is the degenerate LVQ — one prototype per class, implemented as scikit-learn's `NearestCentroid`.

LVQ is also **naturally multi-class** (no one-vs-rest machinery), **naturally online**, and **cheap at inference** — all three of which matter for embedded and streaming deployment.

## Honest status

**LVQ is not part of the mainstream ML toolchain in 2026.** The evidence, not the opinion:

- **scikit-learn has no LVQ**, and the decision is documented. PR #9778 ("[MRG] GLVQ implementation," opened 2017-09-15, closed unmerged 2018-02-19): maintainer `jnothman` called it *"formally mature and popular enough"* but was *"not immediately convinced"* on maintainability, objecting that *"<500 citations for a 1996 paper does not require us maintaining a thousand lines of minimally-tested code."* `agramfort` replied *"+1 for scikit-learn-contrib project."* **That PR is the origin of `sklearn-lvq`** — and the cleanest single citation for "respected, but has not cleared the mainstream-adoption bar."
- **MATLAB's `lvqnet` is marked "To be removed."**
- *The Elements of Statistical Learning* gives it **one page** (§13.2.2, p. 462), sandwiched between K-means and Gaussian mixtures.
- `sklearn-lvq`'s last release was 2020-10-09; `neupy`'s was 2019-04-04.

**Where it genuinely lives:** the groups of **Michael Biehl** (Groningen), **Barbara Hammer** (Bielefeld) and **Thomas Villmann** (Mittweida), with the WSOM workshop series as the community venue; and — reportedly, though this is not independently verified here — biomedical and clinical data (interpretability plus small-n/high-d), spectroscopy and chemometrics, mass spectrometry, and regulated settings where an inspectable model is a requirement rather than a preference.

**The prototype *idea*, though, is thoroughly alive** — it just moved from the raw input space to a learned one:

- **Prototypical Networks** (Snell, Swersky & Zemel, NIPS 2017) classify by distance to a class-mean prototype **in a learned embedding space** — nearest-class-mean on deep features. This is the single best exhibit.
- **ProtoPNet** (Chen, Li, Tao, Barnett, Su & Rudin, NeurIPS 2019), "This Looks Like That," with a clinical follow-up in *Nature Machine Intelligence* 3(12):1061–1070, 2021.
- Saralajew et al. on **GLVQ robustness against adversarial attacks** (WSOM 2019).

## Always-apply

1. **Say whether you mean supervised or unsupervised.** If labels are not being read, it is VQ/k-means/SOM, not LVQ.
2. **Reach for GLVQ or GMLVQ, not LVQ1.** The classic rules are heuristics with a known divergence failure; the cost-function versions are strictly better founded and barely harder.
3. **Scale the features** — LVQ inherits every distance-based pathology from [[k-nearest-neighbours]].
4. **Decay the learning rate**, or the prototypes never settle. Prefer OLVQ1 for the rough pass.
5. **Inspect the prototypes, and sanity-check them against the domain.** A prototype that is physically impossible is telling you something about the representation.
6. **With GMLVQ, read Λ's off-diagonal** — the feature interactions are half the value and are routinely ignored.
7. **Justify the choice on interpretability or deployment size**, not accuracy. If you need raw accuracy on tabular data, gradient boosting will usually win; LVQ's case is that you can explain it and ship it small.
8. **Check implementation maintenance before depending on it** — most of this ecosystem is dormant.

## How to use the references

- **`references/variants-and-implementations.md`** — the full variant chronology with its genuine citation uncertainties, the verbatim LVQ2.1 window rule and the GLVQ derivation, GRLVQ/GMLVQ/RSLVQ in more depth, the implementation table with maintenance status, and the citation hazards in the secondary literature.

## Sources

Kohonen, "Learning vector quantization," *Neural Networks* 1(Suppl. 1):303, 1988, doi:10.1016/0893-6080(88)90334-6 — a one-page INNS meeting abstract, and the **earliest journal-indexed LVQ trace that could be confirmed**. ⚠️ **The canonical "Kohonen 1986, Technical Report TKK-F-A601" citation could not be verified** — no online record was found at all. Treat 1986 as the conventional date, not a checked one. Kohonen, Barna & Chrisley, IEEE ICNN 1988, pp. 61–68, doi:10.1109/ICNN.1988.23829 (reportedly LVQ2's first appearance in print). Kohonen, "Improved versions of learning vector quantization," IJCNN 1990, pp. 545–550, doi:10.1109/IJCNN.1990.137622 (the usual attribution point for LVQ2.1 and LVQ3). Kohonen, "Learning Vector Quantization," ch. 6 of *Self-Organizing Maps*, Springer Series in Information Sciences vol. 30, 3rd ed. 2001, pp. 245–261 — **the reference for LVQ1/2/2.1/3/OLVQ1, but it was not readable for this file**, so anything attributed to "the book" is second-hand. Kohonen, Kangas, Laaksonen & Torkkola, "LVQPAK," IJCNN 1992, pp. 725–730. **LVQ_PAK v3.1 C source** (mirror `github.com/hynde/som_lvq_pak`) — the update rules, sign conventions and the OLVQ1 cap are verified from this source; the original `cis.hut.fi` host now fails its TLS certificate, so Kohonen's own *recommendations* (window widths, prototype budgets, learning-rate advice) remain unread. Sato & Yamada, "Generalized Learning Vector Quantization," *NIPS 8*, MIT Press 1996 (NIPS 1995), pp. 423–429 — read in full; all GLVQ equations and quotations are verbatim. Hammer & Villmann, *Neural Networks* 15(8–9):1059–1068, 2002. Schneider, Biehl & Hammer, "Adaptive Relevance Matrices in Learning Vector Quantization," *Neural Computation* **21(12):3532–3561**, Dec 2009, **doi:10.1162/neco.2009.11-08-908**. Seo & Obermayer, *Neural Computation* 15(7):1589–1604, 2003. Nova & Estévez, "A review of learning vector quantization classifiers," *Neural Computing and Applications* 25(3–4):511–524, 2014. Biehl, Hammer & Villmann, "Prototype-based models in machine learning," *WIREs Cognitive Science* 7(2):92–111, 2016 — the best single entry point. scikit-learn PR #9778; PyPI, CRAN and GitHub release data, fetched 2026-11-11.

**Citation hazard, corrected here.** Wikipedia's LVQ article cites GMLVQ as *"Neural Computation 21(10):3532–3561, doi:10.1162/neco.2009.10-08-892"* with the authors in the wrong order. **That DOI belongs to a different paper** — Schneider, Biehl & Hammer, "Distance Learning in Discriminative Vector Quantization," *Neural Computation* 21(10):2942–2969, 2009. Use 21(12):3532–3561 / doi:10.1162/neco.2009.11-08-908.

Learning-rate figures in circulation (α ≈ 0.03 for LVQ1, α ≈ 0.3 for OLVQ1, w ∈ [0.2, 0.3], ε ∈ [0.1, 0.5], "30–50 prototypes per class") are **code defaults and secondary sources, not Kohonen's prose**: 0.03 is the R `class` default, 0.3 is the LVQ_PAK default, and the prototype-budget figure has no traceable source at all.

## Related

- [[k-nearest-neighbours]] — the ancestor. LVQ is what you get when "store every training point" becomes "learn a few well-placed labelled prototypes."
- [[self-organizing-maps]] — Kohonen's other algorithm, and LVQ's unsupervised sibling; the standard pipeline is SOM to initialise, LVQ to sharpen.
- [[information-theory]] — vector quantization's rate–distortion roots.
- [[clean-code]] / [[software-design]] — the interpretability argument here is a close cousin of the "a model you can read" argument for code you can read.
- [[python]] — implementation context.
