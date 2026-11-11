# LVQ variants, derivations and implementations

## Chronology, with its real uncertainties

| Variant | Date | Confidence |
|---|---|---|
| LVQ1 | 1986, TR TKK-F-A601 | ⚠️ **unverified — no online record found at all.** Conventional, not checked |
| — | 1988 | *Neural Networks* 1(Suppl. 1):303, a one-page INNS abstract. **The earliest confirmed journal trace** |
| LVQ2 | 1988 | Kohonen, Barna & Chrisley, IEEE ICNN 1988, pp. 61–68. Second-hand attribution |
| LVQ2.1, LVQ3 | 1990 | Kohonen, IJCNN 1990, pp. 545–550. Second-hand attribution |
| OLVQ1 | ? | Not confidently dateable; present in LVQ_PAK by 1991–92 |

**LVQ_PAK release history** (from `README-LVQ.txt` in the `github.com/hynde/som_lvq_pak` mirror): v1.0 1991-12-19; v1.1 1991-12-31; v2.0 1992-01-31 (*"major algorithm modifications"*); v2.1 1992-10-09; v3.0 1995-03-01; v3.1 1995-04-07. Implements LVQ1, LVQ2.1, LVQ3, OLVQ1. © 1991–1995 "LVQ Programming Team," Helsinki University of Technology, Laboratory of Computer and Information Science; free for scientific use, commercial use by written permission.

The Report A30 manual (Kohonen, Hynninen, Kangas, Laaksonen & Torkkola, 1996) **could not be read** — `cis.hut.fi` fails its TLS certificate and the Aalto mirror 404s. This is why the *algorithms* below are verified from the C source but Kohonen's *recommendations* are not.

## Vector quantization roots

A codebook `{w₁..w_M}` induces a **Voronoi tessellation** of the input space; the encoder transmits only the index of the nearest codevector.

```
rate       = log₂(M)/d  bits per dimension
distortion = E‖x − w_{j(x)}‖²
```

Classic lossy compression for speech and image, with the rate–distortion trade-off as the design knob — see [[information-theory]].

- **LBG** — Linde, Buzo & Gray, "An Algorithm for Vector Quantizer Design," *IEEE Trans. Communications* 28(1):84–95, Jan 1980, doi:10.1109/TCOM.1980.1094577. Generalises Lloyd's scalar quantizer design to vectors and to empirical training data. **Under Euclidean distortion it *is* batch k-means** (the Lloyd iteration).
- **Lloyd** — written as a Bell Labs memo in 1957, published as "Least squares quantization in PCM," *IEEE Trans. Inf. Theory* 28(2):129–137, 1982.
- **MacQueen** — *Proc. 5th Berkeley Symposium*, 1967: the online/sequential version, and the source of the name "k-means."

## LVQ2.1 — the window rule, verbatim

From Sato & Yamada's review section:

> "Starting with properly defined initial values, the reference vectors are updated as follows by the LVQ2.1 algorithm:
>
> **wᵢ(t+1) = wᵢ(t) − α(t)(x − wᵢ(t))**  (1)
> **wⱼ(t+1) = wⱼ(t) + α(t)(x − wⱼ(t))**  (2)
>
> where 0 < α(t) < 1, and α(t) may decrease monotonically with time. The two reference vectors wᵢ and wⱼ are the nearest to x; x and wⱼ belong to the same class, while x and wᵢ belong to different classes. Furthermore, x must fall into the 'window,' which is defined around the midplane of wᵢ and wⱼ. That is, if the following condition is satisfied, wᵢ and wⱼ are updated:
>
> **min( dᵢ/dⱼ , dⱼ/dᵢ ) > s**  (3)
>
> where dᵢ = |x − wᵢ|, dⱼ = |x − wⱼ|."

With `s = (1 − w)/(1 + w)` for relative window width w. The condition means x lies between two **Apollonian spheres**.

**The failure, verbatim:**

> "The LVQ2.1 algorithm is based on the idea of shifting the decision boundaries toward the Bayes limits with attractive and repulsive forces from x. However, **no attention is given to what might happen to the location of the w_k, so the reference vectors diverge in the long run.**"

## LVQ3, from the source

Verified against the LVQ_PAK C source. Identical to LVQ2.1 when the two nearest prototypes have different labels (window test included). **If both nearest prototypes have the correct class, both move toward x** at the reduced rate `talpha * epsilon`. Otherwise no update.

⚠️ **Wikipedia shows the same-class update as repulsion** (`w_j ← w_j − εα(x − w_j)`), contradicting the source. The source moves both prototypes toward the sample.

Sato & Yamada on LVQ3:

> "LVQ3 has been proposed to ensure that the reference vectors continue approximating the class distributions, but it must be noted that **if only one reference vector is assigned to each class, LVQ3 is the same as LVQ2.1, and the problem of reference vector divergence remains unsolved.**"

## OLVQ1, from the source

Verified against `olvq1_training`:

```
correct (c(w_j*) == y):   w_j* ← w_j* + α_j[x − w_j*] ;   α_j ← α_j / (1 + α_j)
wrong   (c(w_j*) != y):   w_j* ← w_j* − α_j[x − w_j*] ;   α_j ← α_j / (1 − α_j)   [capped]

combined:   α_j(t) = α_j(t−1) / (1 + s(t)·α_j(t−1)),   s(t) = +1 correct, −1 wrong
```

**The cap** is operationally "keep `α_j ≤ α_initial`" — never above the user-supplied global α. LVQ_PAK's default initial `α_j` is **0.3** when none is supplied.

The rationale (second-hand): `α_j` is chosen so each prototype's cumulative influence from the samples it has won is statistically balanced, which is why OLVQ1 converges far faster than LVQ1.

## GLVQ — the full derivation

Sato & Yamada, *NIPS 8* (NIPS 1995), pp. 423–429, NEC Information Technology Research Laboratories. Read in full.

**Abstract:**

> "We propose a new learning method, 'Generalized Learning Vector Quantization (GLVQ),' in which reference vectors are updated based on the steepest descent method in order to minimize the cost function. The cost function is determined so that the obtained learning rule satisfies the convergence condition. **We prove that Kohonen's rule as used in LVQ does not satisfy the convergence condition and thus degrades recognition ability.** Experimental results for printed Chinese character recognition reveal that GLVQ is superior to LVQ in recognition ability."

**The relative distance difference** (eq. 4), with `w₁` the nearest same-class and `w₂` the nearest different-class prototype:

```
μ(x) = (d₁ − d₂)/(d₁ + d₂)
```

> "μ(x) ranges between −1 and +1, and **if μ(x) is negative, x is classified correctly**; otherwise, x is classified incorrectly. In order to improve error rates, μ(x) should decrease for all input vectors."

**Cost and update** (eqs. 5–6):

```
S = Σ_{i=1}^{N} f(μ(xᵢ))        f monotonically increasing
wᵢ ← wᵢ − α ∂S/∂wᵢ ,  i = 1,2
```

**Exact gradients** with squared Euclidean `dᵢ = |x − wᵢ|²` (eqs. 7–8):

```
∂S/∂w₁ = −(∂f/∂μ) · 4d₂/(d₁+d₂)² · (x − w₁)
∂S/∂w₂ = +(∂f/∂μ) · 4d₁/(d₁+d₂)² · (x − w₂)
```

**The learning rule** (eqs. 9–10, factor 4 absorbed into α):

```
w₁ ← w₁ + α (∂f/∂μ) · d₂/(d₁+d₂)² · (x − w₁)      ATTRACT, scaled by d₂
w₂ ← w₂ − α (∂f/∂μ) · d₁/(d₁+d₂)² · (x − w₂)      REPEL,   scaled by d₁
```

**The annealed margin.** In their experiments `∂f/∂μ = f(μ,t){1 − f(μ,t)}` with `f(μ,t) = 1/(1+e^{−μt})` a sigmoid in learning time t. This *"has a single peak at μ = 0, and the peak width becomes narrower as t increases, so the input vectors that affect learning are gradually restricted to those around the decision boundaries."*

**Classic LVQ as a degenerate case.** Set `μ = d₁` for `d₁ < d₂`, `μ = −d₂` for `d₁ > d₂`, and `f(μ) = μ`. Then `S = Σ_{d₁<d₂} d₁ − Σ_{d₁>d₂} d₂` and the updates reduce to LVQ's. The paper's point: *"f(μ) should be a **non-linear** monotonically increasing function"* — the non-linearity is the improvement.

## Metric-learning extensions

**GRLVQ** — Hammer & Villmann, "Generalized relevance learning vector quantization," *Neural Networks* 15(8–9):1059–1068, Oct 2002, doi:10.1016/S0893-6080(02)00079-5.

```
d_λ(x,w) = Σᵢ λᵢ(xᵢ − wᵢ)²,     λᵢ ≥ 0,  Σλᵢ = 1
```

Both prototypes and λ trained by GLVQ-style gradient descent. Result: an adaptive **diagonal** metric, i.e. supervised feature weighting and selection as a by-product.

**GMLVQ** — Schneider, Biehl & Hammer, *Neural Computation* 21(12):3532–3561, Dec 2009, doi:10.1162/neco.2009.11-08-908.

```
d_Λ(x,w) = (x − w)ᵀ Λ (x − w),     Λ = ΩᵀΩ  ⟹  Λ ⪰ 0 by construction
```

Ω trained alongside the prototypes on the GLVQ cost.

**Reading Λ:**

- **diagonal** → per-feature relevance
- **off-diagonal** → feature correlations/interactions the classifier exploits
- **low-rank Ω** → supervised dimensionality reduction, giving a discriminative 2-D projection you can plot

**LGMLVQ** uses a separate Λ per prototype or per class (local metrics). Related: Schneider, Biehl & Hammer, "Metric Learning for Prototype-Based Classification," 2009, doi:10.1007/978-3-642-04003-0_8.

**RSLVQ** — Seo & Obermayer, "Soft Learning Vector Quantization," *Neural Computation* 15(7):1589–1604, July 2003, doi:10.1162/089976603321891819. A likelihood-ratio cost under a Gaussian mixture with soft/probabilistic assignment replacing the hard winner.

**Margin theory** — Crammer, Gilad-Bachrach, Navot & Tishby, "Margin Analysis of the LVQ Algorithm," NIPS 2002. ⚠️ **Unverified — the page could not be fetched.** Reportedly gives a generalisation bound in terms of the *hypothesis margin* that is independent of input dimension. Verify before citing. Related and verified: Gilad-Bachrach, Navot & Tishby, "Margin based feature selection," ICML 2004, doi:10.1145/1015330.1015352.

**Border-sensitive line** — Villmann, Kaden, Saralajew et al., "Border-sensitive learning in generalized learning vector quantization: an alternative to support vector machines," *Soft Computing* 19(9):2423–2434, doi:10.1007/s00500-014-1496-1. And the honest-advocacy survey "Can Learning Vector Quantization be an Alternative to SVM and Deep Learning?", *J. Artif. Intell. Soft Comput. Res.* 7(1):65–81, doi:10.1515/jaiscr-2017-0005.

## Relationships

- **Nearest Class Mean (NCM)** = one prototype per class = degenerate LVQ. scikit-learn's `sklearn.neighbors.NearestCentroid`, including the shrunken-centroid variant; its docs honestly warn it *"suffers on non-convex classes, as well as when classes have drastically different variances."* NCM with shared spherical covariance and equal priors is equivalent to LDA.
- **k-medoids / k-medians** — prototypes constrained to be data points, unlike LVQ's.
- **RBF networks** — centres play the prototype role but with a soft weighted readout instead of a hard nearest-prototype rule; LVQ is the winner-take-all limit of that family.
- **ESL §13.2.2, p. 462** — about one page, between K-means (§13.2.1, p. 460) and Gaussian Mixtures (§13.2.3, p. 463), in ch. 13 "Prototype Methods and Nearest-Neighbors" (p. 459). Good evidence for the "respected but marginal" status claim.

## Modern prototype revival

- **Prototypical Networks** — Snell, Swersky & Zemel, arXiv:1703.05175 (v1 15 Mar 2017), NIPS 2017. Nearest-class-mean on learned deep features.
- **ProtoPNet** — Chen, Li, Tao, Barnett, Su & Rudin, "This Looks Like That," arXiv:1806.10574, NeurIPS 2019. Clinical follow-up: Barnett et al., *Nature Machine Intelligence* 3(12):1061–1070, 2021, doi:10.1038/s42256-021-00423-x.
- **Adversarial robustness** — Saralajew, Holdijk, Rees & Villmann, "Robustness of Generalized Learning Vector Quantization Models Against Adversarial Attacks," WSOM 2019, pp. 189–199, doi:10.1007/978-3-030-19642-4_19.
- ⚠️ Li, Liu, Chen & Rudin, "Deep Learning for Case-Based Reasoning through Prototypes," AAAI 2018, and Saralajew et al., "Classification-by-Components," NeurIPS 2019 — **unverified**.
- ⚠️ "Deep LVQ" as a named method has **no citable source** — it is an informal description of the ProtoTorch line, not a method name.

## Implementations

Status checks dated 2026-11-11.

| Package | Algorithms | Status |
|---|---|---|
| **sklearn-lvq** (`github.com/MrNuggelz/sklearn-lvq`, BSD-3) | GLVQ, GRLVQ, GMLVQ, LGMLVQ, RSLVQ, MRSLVQ, LMRSLVQ | **Dormant** but the best-maintained option. PyPI 1.1.1 (2020-10-09); last `stable` commit 2020-10-29; no GitHub releases; README still mentions Python 2.7 and Travis CI. Derived from Biehl/Schneider/Bunte MATLAB code |
| **prototorch** (`github.com/si-cim/prototorch`) | GPU LVQ toolbox on PyTorch `nn` | **Slowing but alive.** PyPI 0.7.6 (2023-10-04), first release 2020-04-06, 327 commits, no archive notice |
| **neupy** | LVQ, LVQ2, LVQ21, LVQ3 (unverified — docs site has a TLS error) | **Dormant.** Last release 0.8.2, 2019-04-04 |
| **R `class`** (v7.3-23) | `lvq1`, `lvq2`, `lvq3`, `olvq1`, `lvqinit`, `lvqtest` | **Maintained** — ships with the MASS/Venables–Ripley suite. `lvq1(x, cl, codebk, niter = 100*nrow(codebk$x), alpha = 0.03)`. **The only well-maintained classic-LVQ implementation** |
| **LVQ_PAK v3.1** (C, 1995) | LVQ1, LVQ2.1, LVQ3, OLVQ1 | Historical. Original site fails TLS; mirrors at `github.com/hynde/som_lvq_pak` and `github.com/wyim-pgl/librf_lvq_pak-3.1`. **Still the authoritative source for the exact classical update rules** |
| **MATLAB `lvqnet`** | `learnlv1`, `learnlv2` | **Deprecated** — marked "To be removed" |
| **scikit-learn** | — | **None.** Only `NearestCentroid` (the degenerate case) |

**Initialization options:** LVQ_PAK provides `eveninit` (even allocation per class) and `balance`; R provides `lvqinit(x, cl, size)`. Common practice is random per-class samples, class-wise k-means, or a SOM. Prototype budget per class is often set proportional to class prior or variance. ⚠️ The "≈30–50 prototypes per class" figure has **no traceable source**.

## Sources

Sato & Yamada, *NIPS 8*, 1996 — read in full; all GLVQ equations and quotations verbatim. LVQ_PAK v3.1 C source via the `hynde/som_lvq_pak` mirror — LVQ1/LVQ3/OLVQ1 rules, signs and the OLVQ1 cap. R `class` 7.3-23 documentation. Crossref records for Kohonen 1988 (*Neural Networks* 1 Suppl. 1:303), Kohonen/Barna/Chrisley ICNN 1988, Kohonen IJCNN 1990, Kohonen *Proc. IEEE* 78(9) 1990, Kohonen ch. 6 of *Self-Organizing Maps* 3rd ed. 2001, LVQPAK IJCNN 1992, Hammer & Villmann 2002, Schneider/Biehl/Hammer 2009 (both papers), Seo & Obermayer 2003, Nova & Estévez 2014, Biehl/Hammer/Villmann 2016, Villmann et al. 2015, Saralajew et al. 2019, Barnett et al. 2021. scikit-learn PR #9778 and issue thread. PyPI, CRAN and GitHub release data. ESL section and page numbers from the official TOC. All fetches 2026-11-11.

**Not readable, so second-hand throughout:** Kohonen's *Self-Organizing Maps* book, the LVQ_PAK Report A30 manual, and the 1986 TKK-F-A601 report (no record found).
