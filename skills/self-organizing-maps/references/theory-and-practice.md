# SOM theory, heuristics and implementations

## Origin and the biological analogy, honestly bounded

**Kohonen 1982** — "Self-organized formation of topologically correct feature maps," *Biological Cybernetics* 43(1):59–69, doi:10.1007/BF00337288. ~8,500 citations. ⚠️ **The abstract could not be retrieved for this file** — Springer redirects to login, PubMed does not index 1982 *Biol. Cybern.*, and Semantic Scholar's abstract field is publisher-elided. Nothing is quoted from it. Second-hand description: a 1-D or 2-D array of adaptive threshold-logic-like units receiving signals from a "primary event space," with short-range lateral feedback between neighbours, automatically forms output responses carrying the same topological order as the primary events.

**Precursors.** von der Malsburg, "Self-organization of orientation sensitive cells in the striate cortex," *Kybernetik* 14:85–100, 1973, doi:10.1007/BF00288907. Willshaw & von der Malsburg, "How patterned neural connections can be set up by self-organization," *Proc. R. Soc. Lond. B* 194(1117):431–445, 12 Nov 1976, doi:10.1098/rspb.1976.0087. Kohonen's 1982 model is best described as a **computationally simplified version** of these: the winner-take-all step plus an imposed neighbourhood kernel replace explicit lateral-inhibition dynamics.

**The biological motivation is real but the model is a caricature — say both.** Cortex does contain genuine topographic maps: **retinotopy** (visual cortex), **somatotopy** (the cortical homunculus; Penfield & Rasmussen 1950), and **tonotopy** (cochlea through auditory cortex). SOM is a model of map *formation*, and that is a legitimate inspiration.

But instantaneous global winner selection, an externally imposed neighbourhood function, and hand-tuned decay schedules have **no cortical counterpart**, and real map development involves activity-dependent plasticity, genetic gradients and spontaneous retinal waves. Frame it as **"bio-inspired, then engineered"** — not "how cortex works." Kohonen himself returned to the question: "Physiological interpretation of the self-organizing map algorithm," *Neural Networks* 6(6):895–905, 1993.

See [[neural-networks-biology]] for the actual neuroscience.

## Batch SOM

```
m_i = Σ_x h_{c(x),i} · x  /  Σ_x h_{c(x),i}

per epoch:  m_i = Σ_j n_j h_{ji} x̄_j / Σ_j n_j h_{ji}
            j over units, n_j = #{samples whose BMU is j}, x̄_j = their mean
```

A neighbourhood-weighted mean. Deterministic given initialization, no α to tune, faster, reproducible. Theory: Cheng, "Convergence and ordering of Kohonen's batch map," *Neural Computation* 9:1667–1676, 1997.

## The energy-function result, verbatim

**Erwin, Obermayer & Schulten, "Self-organizing maps: ordering, convergence properties and energy functions," *Biological Cybernetics* 67(1):47–55, May 1992**, doi:10.1007/BF00201801, PMID 1606243. Erratum: *Biol. Cybern.* 1993;68(3):285 — rarely cited. Beckman Institute, University of Illinois at Urbana-Champaign.

**Abstract, verbatim:**

> "We investigate the convergence properties of the self-organizing feature map algorithm for a simple, but very instructive case: **the formation of a topographic representation of the unit interval [0, 1] by a linear chain of neurons.** We extend the proofs of convergence of Kohonen and of Cottrell and Fort to hold in any case where the neighborhood function, which is used to scale the change in the weight values at each neuron, is a monotonically decreasing function of distance from the winner neuron. **We prove that the learning dynamics cannot be described by a gradient descent on a single energy function, but may be described using a set of potential functions, one for each neuron, which are independently minimized following a stochastic gradient descent.** We derive the correct potential functions for the one- and multi-dimensional case, and show that the energy functions given by Tolat (1990) are an approximation which is no longer valid in the case of highly disordered maps or steep neighborhood functions."

**So the correct statement is five things, not one slogan:**

1. The standard online SOM update is **not** SGD on any **single** global energy function.
2. It **is** describable as **one potential function per neuron**, each independently minimized by SGD. This nuance is almost always dropped — there *are* potentials, just not one.
3. The proof setting is the 1-D chain mapping `[0,1]`; they derive the correct potentials for the 1-D **and multi-dimensional** cases.
4. They *strengthen* existing convergence results: Kohonen's and Cottrell & Fort's ordering proofs are extended to **any monotonically decreasing** neighbourhood function.
5. They **refute** a prior claimed energy function (Tolat 1990), valid only approximately and failing for highly disordered maps or steep neighbourhood functions.

**The mechanism.** The obstruction is the argmin winner rule combined with a continuous input density. The natural candidate energy `E = ½ Σ_x Σ_i h_{i,c(x)} ‖x − m_i‖²` is **discontinuous in the weights at Voronoi-cell boundaries** where the winner identity flips, and the SOM update matches its gradient only *within* each piece — it ignores the extra terms generated by the winner changing.

## The metastability companion paper

**Erwin, Obermayer & Schulten, "Self-organizing maps: stationary states, metastability and convergence rate," *Biol. Cybern.* 67(1):35–45, May 1992**, doi:10.1007/BF00201800, PMID 1606242.

From the abstract: convergence time *"may vary over several orders of magnitude depending on the range and also the shape of the neighborhood function"*; **for neighbourhood functions convex on the interval given by the chain length there exist NO metastable states**, while for all others metastable states exist and **can trap the algorithm**; and for the widely-used Gaussian there is a **width threshold above which metastable states cannot exist**.

Their practical conclusion, which is the real citable justification for fussing over the schedule:

> "Fastest convergence is achieved using neighborhood functions which are 'convex' over a large range around the winner neuron and yet have large differences in value at neighboring neurons."

## The fix: Heskes

**Heskes, "Energy functions for self-organizing maps," in Oja & Kaski (eds.), *Kohonen Maps*, Elsevier 1999, pp. 303–315**, doi:10.1016/B978-044450270-4/50024-3.

He modifies the **winner selection**:

```
c = argmin_i  Σ_j h_{ij} ‖x − m_j‖²
```

Choose the unit minimising the *neighbourhood-summed* error rather than the plain nearest. The resulting rule **does** descend a well-defined energy.

Also: Heskes, "Self-organizing maps, vector quantization, and mixture modeling," *IEEE Trans. Neural Networks* 12(6):1299–1305, 2001, doi:10.1109/72.963766 (open PDF at `repository.ubn.ru.nl`).

**The contrast to make:** Neural Gas minimizes an explicit cost. Heskes-SOM minimizes an explicit cost. Standard Kohonen SOM does not.

## Magnification — state the conditions

The map's unit density does not match the data density.

- 1-D asymptotic result: magnification follows **p(x)^{2/3}** (Ritter & Schulten, *Biol. Cybern.* 54:99–106, 1986).
- The general exponent is **d/(d+2)** (Ritter, *IEEE TNN* 2(1):173–175, 1991) — the same exponent as plain VQ (Zador).
- The exponent **depends on neighbourhood width** (Dersch & Tavan 1995).

**So the 2/3 figure holds only in the 1-D asymptotic narrow-neighbourhood limit.** Do not state it unconditionally.

Control methods: Villmann & Claussen, "Magnification Control in Self-Organizing Maps and Neural Gas," *Neural Computation* 18(2):446–469, 2006, doi:10.1162/089976606775093918.

## Ordering proofs

Cottrell & Fort, *Ann. Inst. Henri Poincaré* 23(1):1–20, 1987. Survey: **Cottrell, Fort & Pagès, "Theoretical aspects of the SOM algorithm," *Neurocomputing* 21(1–3):119–138, Nov 1998**, doi:10.1016/S0925-2312(98)00034-4.

**General ordering and convergence in ≥2 lattice dimensions is NOT established.** Essentially all practical use is 2-D. This is worth saying out loud.

## The size and aspect-ratio heuristics, resolved from source

Both read directly from `som/som_topol_struct.m` in `github.com/ilarinieminen/SOM-Toolbox`.

### Map size — the 5√n rule

```matlab
% first (if necessary) determine the number of map units (munits)
if isnan(munits),
  if ~isnan(dlen),
    munits = ceil(5 * dlen^0.5); % this is just one way to make a guess...
  else
    munits = 100; % just a convenient value
  end
end
```

with the documentation string: *"A heuristic formula of 'munits = 5*sqrt(dlen)' is used to calculate it."*

**Verdict: the source is the MATLAB SOM Toolbox** (Vesanto, Himberg, Alhoniemi & Parhankangas, Report A57, Helsinki University of Technology, 2000). It is an **arbitrary pragmatic default and the authors say so in their own code comment**. There is no theoretical justification, and Kohonen's book gives no such formula. The code comment is the perfect citation for flagging it.

### Aspect ratio — a real heuristic

```matlab
% initialize xdim/ydim ratio using principal components of the input
% space; the ratio is the square root of ratio of two largest eigenvalues
[V,S] = eig(A);  eigval = diag(S);  [y,ind] = sort(eigval);  eigval = eigval(ind);
if eigval(end)==0 || eigval(end-1)*munits<eigval(end),
  ratio = 1;
else
  ratio = sqrt(eigval(end)/eigval(end-1)); % ratio between map sidelengths
end
% in hexagonal lattice, the sidelengths are not directly proportional to the
% number of units since the units on the y-axis are squeezed together by sqrt(0.75)
if strcmp(sTopol.lattice,'hexa'),
  sTopol.msize(2) = min(munits, round(sqrt(munits / ratio * sqrt(0.75))));
else
  sTopol.msize(2) = min(munits, round(sqrt(munits / ratio)));
end
sTopol.msize(1) = round(munits / sTopol.msize(2));
```

Side-length ratio = **√(λ₁/λ₂)** of the data autocorrelation matrix, with a **√0.75** correction for hexagonal lattices. Rationale: an elongated data cloud gets an elongated map, reducing folding. **Note the square root** — commonly mis-stated as the plain eigenvalue ratio.

## Quality measures

- **Quantization error (QE)** = mean `‖x − m_BMU(x)‖`. Falls as the map grows or σ shrinks.
- **Topographic error (TE)** = fraction of samples whose first and second BMUs are **not lattice-adjacent**. Source: **Kiviluoto, "Topology preservation in self-organizing maps," ICNN'96, vol. 1, pp. 294–299**, doi:10.1109/ICNN.1996.548907.
- **They trade off.** A smaller neighbourhood lowers QE and raises TE. **There is no single accepted scalar quality measure for a SOM** — a direct consequence of having no global cost function.
- **Topographic product** — Bauer & Pawelzik, "Quantifying the neighborhood preservation of self-organizing feature maps," *IEEE TNN* 3(4):570–579, July 1992, doi:10.1109/72.143371.
- **Trustworthiness / continuity** — Venna & Kaski, "Neighborhood Preservation in Nonlinear Projection Methods," ICANN 2001, LNCS 2130:485–491, doi:10.1007/3-540-44668-0_68.
- MiniSom exposes `quantization_error`, `topographic_error`, `distortion_measure`.

## U-matrix and component planes

**U-matrix** — Ultsch & Siemon, "Kohonen's Self Organizing Feature Maps for Exploratory Data Analysis," *Proc. INNC-90*, Paris, Kluwer, 1990, pp. 305–308. ⚠️ **Not indexed in Crossref; page numbers and publisher unverified.** A later verifiable source: Ultsch, "Data Mining and Knowledge Discovery with Emergent Self-Organizing Feature Maps for Multivariate Time Series," in *Kohonen Maps*, Elsevier 1999, doi:10.1016/B978-044450270-4/50003-6.

Each cell shows the distance between neighbouring units' weight vectors: **ridges = cluster boundaries, valleys = clusters**. This is what makes a SOM a cluster-*discovery* tool rather than just a projection. MiniSom: `distance_map(scaling='sum')`.

**Component planes** — Vesanto, "SOM-based data visualization methods," *Intelligent Data Analysis* 3(2):111–126, 1999. One map per input variable. Reading two side by side reveals correlation structure **localized to regions of the map**. **No t-SNE or UMAP equivalent exists.**

## The alternatives, fairly

**PCA.** Linear, global, closed-form, unique. SOM is a discrete nonlinear relative, conceptually adjacent to principal curves and surfaces (Hastie & Stuetzle 1989) — though SOM is *not* the optimum of any principal-surface objective. Mulier & Cherkassky (1995) give a kernel-smoothing view.

**t-SNE** — van der Maaten & Hinton, *JMLR* 9:2579–2605, 2008. Objective: KL divergence between neighbour distributions. **No out-of-sample transform** in standard implementations (scikit-learn's `TSNE` has none; openTSNE and parametric t-SNE add one).

**UMAP** — McInnes, Healy & Melville, arXiv:1802.03426, 2018; *JOSS* 3(29):861. Fuzzy-topological construction with a cross-entropy objective. **`umap-learn` DOES have a `transform` method**, plus parametric UMAP.

⚠️ **"Out-of-sample projection" is not unique to SOM.** Over-claiming it is the most common way SOM advocacy goes wrong.

## Variants

- **Neural Gas** — Martinetz & Schulten, "A 'neural-gas' network learns topologies," *Artificial Neural Networks*, Elsevier 1991, pp. 397–402; **Martinetz, Berkovich & Schulten, *IEEE TNN* 4(4):558–569, July 1993**, doi:10.1109/72.238311. **Rank-based** neighbourhood `h_λ(k) = exp(−k/λ)` with k the unit's rank by distance to x — **no fixed lattice**. Key contrast: it **provably descends an explicit cost function**. Magnification exponent `d/(d+2)` in the small-λ limit.
- **Growing Neural Gas** — Fritzke, *NIPS 7*, pp. 625–632, 1995. Grows units where error accumulates. Also Growing Cell Structures (*Neural Networks* 7(9), 1994) and Growing Grid (*Neural Processing Letters* 2(5), 1995).
- **GTM** — **Bishop, Svensén & Williams, "GTM: The Generative Topographic Mapping," *Neural Computation* 10(1):215–234, 1 Jan 1998**, doi:10.1162/089976698300017953. The authors explicitly present it as *"a principled alternative to Kohonen's self-organizing map"* addressing many of its major limitations.

  **What it fixes:** an explicit probabilistic density over data space with a log-likelihood objective; **monotone EM convergence**; a smooth parametric mapping (e.g. an RBF network) from a latent grid into data space, so topographic ordering is **enforced by the mapping's smoothness** rather than a hand-tuned shrinking-neighbourhood schedule; **no neighbourhood schedule to tune**; closed-form magnification factors.

  **What it does not fix:** still local optima, still a fixed latent grid chosen a priori, generally more cost per iteration.

  This is the right "what SOM should have been" comparison — the same idea done with a likelihood.
- **GHSOM** — Dittenbach, Merkl & Rauber, IJCNN 2000; Rauber, Merkl & Dittenbach, *IEEE TNN* 13(6):1331–1341, 2002.
- **ViSOM** — Yin, *IEEE TNN* 13(1):237–243, 2002 (preserves inter-point distances, not just topology).
- **Soft/probabilistic topographic VQ** — Graepel, Burger & Obermayer, ICANN'97, doi:10.1007/BFb0020223.
- **The supervised sibling** is [[learning-vector-quantization]], not a SOM variant.

## Applications, with verified figures

- **WEBSOM** — Kaski, Honkela, Lagus & Kohonen, "WEBSOM — self-organizing maps of document collections," *Neurocomputing* 21(1–3):101–117, Nov 1998, doi:10.1016/S0925-2312(98)00039-3. Then **Kohonen, Kaski, Lagus, Salojärvi, Honkela, Paatero & Saarela, "Self organization of a massive document collection," *IEEE Trans. Neural Networks* 11(3):574–585, May 2000**, doi:10.1109/72.846729. **Verified scale: 6,840,568 patent abstracts onto a 1,002,240-node SOM.**
- **Gene expression** — **Tamayo, Slonim, Mesirov, Zhu, Kitareewan, Dmitrovsky, Lander & Golub, "Interpreting patterns of gene expression with self-organizing maps," *PNAS* 96(6):2907–2912, 16 Mar 1999**, doi:10.1073/pnas.96.6.2907. Software GENECLUSTER; applied to HL-60, U937, Jurkat and NB4 cell models over ~6,000 genes.
- **FlowSOM** — **Van Gassen, Callebaut, Van Helden, Lambrecht, Demeester, Dhaene & Saeys, "FlowSOM: Using self-organizing maps for visualization and interpretation of cytometry data," *Cytometry Part A* 87(7):636–645, 2015**, doi:10.1002/cyto.a.22625. A SOM followed by consensus meta-clustering of the SOM nodes, visualized as star charts on a minimum spanning tree.

  **The independent benchmark:** **Weber & Robinson, "Comparison of clustering methods for high-dimensional single-cell flow and mass cytometry data," *Cytometry Part A* 89(12):1084–1096, Dec 2016**, doi:10.1002/cyto.a.23030 (preprint doi:10.1101/047613). Their finding: *"Several methods performed well, including FlowSOM, X-shift, PhenoGraph, Rclusterpp, and flowMeans"*, and FlowSOM additionally had **very fast runtimes, suitable for interactive exploration on a laptop**.

  ⚠️ The claim that FlowSOM is used inside CATALYST / Seurat-adjacent pipelines was **not verified**; Bioconductor availability is second-hand.
- **The "poverty map"** — Kaski & Kohonen, "Exploratory data analysis by the self-organizing map: Structures of welfare and poverty in the world," in *Neural Networks in Financial Engineering*, World Scientific 1996, pp. 498–507. ⚠️ **Venue, pages and the country count are unverified.** Related and verifiable: Deboeck & Kohonen (eds.), *Visual Explorations in Finance with Self-Organizing Maps*, Springer 1998. Worth pinning down because it is the canonical component-planes illustration.
- ⚠️ **Industrial process monitoring, finance/economics maps, sensor/spatial data, music/audio maps** — nothing specific pinned. Omit or verify before asserting.

## Implementations

Status dated 2026-11-11.

**MiniSom** (`github.com/JustGlowing/minisom`, MIT, Giuseppe Vettigli) — **the de facto Python SOM, and actively maintained.** PyPI **2.3.6 (2026-02-11)**; prior 2.3.5/2.3.4 (2025-02-26), 2.3.3 (2024-08-23), 2.3.2 (2024-02-16), 2.3.1 (2023-03-02), 2.3.0 (2022-02-25).

```python
MiniSom(x, y, input_len, sigma=1, learning_rate=0.5,
        decay_function='asymptotic_decay', neighborhood_function='gaussian',
        topology='rectangular', activation_distance='euclidean',
        random_seed=None, sigma_decay_function='asymptotic_decay')
```

- Training: `train(data, num_iteration, random_order=False, verbose=False, use_epochs=False, fixed_points=None)`, `train_random`, `train_batch`, `train_batch_offline`, `train_batch_offline_fast` (needs numba — `pip install minisom[fast]`).
- Init: `random_weights_init`, `pca_weights_init`.
- Inspection: `winner`, `activate`, `quantization`, `quantization_error`, `topographic_error`, `distortion_measure`, **`distance_map(scaling='sum')` ← the U-matrix**, `activation_response` (hit histogram), `win_map`, `labels_map`, `get_weights`.
- `activation_distance ∈ {euclidean, cosine, manhattan, chebyshev, callable}`; `topology ∈ {rectangular, hexagonal}`; `neighborhood_function ∈ {gaussian, mexican_hat, bubble, triangle}`.
- ⚠️ **Gotcha:** the defaults `sigma=1, learning_rate=0.5` give essentially no ordering phase — fine for the README's 6×6 example, wrong for a 20×20 map. Always set σ relative to map size.

**Other Python.** **somoclu** — PyPI 1.7.6 (2023-02-18), GPLv3, parallel/GPU, Python+R+MATLAB bindings; paper Wittek, Gao, Lim & Zhao, *J. Stat. Softw.* 78(9), 2017; **last release over three years old**. ⚠️ **SOMPY, sklearn-som, susi, XPySom** exist but their maintenance was not verified — do not claim they are maintained.

**R.** **`kohonen`** — CRAN **3.0.13, published 2026-01-22**, maintained by Wehrens & Kruisselbrink. **Actively maintained; the best-maintained SOM package anywhere.** Papers: Wehrens & Buydens, "Self- and Super-organizing Maps in R: The kohonen Package," *JSS* 21(5), 2007, doi:10.18637/jss.v021.i05; Wehrens & Kruisselbrink, "Flexible Self-Organizing Maps in kohonen 3.0," *JSS* 87(7), 2018, doi:10.18637/jss.v087.i07. Also `som`, `popsom` (unchecked); **FlowSOM** on Bioconductor (second-hand).

**MATLAB.** SOM Toolbox (Helsinki; Vesanto, Himberg, Alhoniemi & Parhankangas, Report A57, 2000), v2.0 with a 2.1 update. The original Helsinki host `www.cis.hut.fi` now **fails its TLS certificate** — use the `ilarinieminen/SOM-Toolbox` GitHub mirror. Also MATLAB's own `selforgmap` in the Deep Learning Toolbox.

### scikit-learn has no SOM, and the decision is documented

Closed PRs and issues: #39 (2012), **#2892** (issue, closed 2014-04-14), #2996 (WIP PR, closed 2016), #9770 (PR, closed 2017), **#19842** ("Introducing Kohonen's Self-Organizing Maps," closed 2021-04-19).

**Two distinct arguments, both quotable:**

- **The 2014 thread — "nobody has shown it beats what we have."** Gaël Varoquaux: SOM *"is also getting old, and isn't used much anymore"*; someone *"would have to demonstrate that it produces useful results on data without too much work."* He later said he would be *"convinced in favor"* given a good example showing the benefit, and ruled out adopting an existing GPL implementation. Andreas Müller asked for an example showing a benefit over existing clustering and manifold learning — **a request apparently never satisfied.** `NelleV` noted SOM is *"very close to the mini batch k-means."*
- **The 2021 thread — scope, not quality.** `adrinjalali` said he loved SOMs but scikit-learn was not the right home, and that *"maintaining a high performance implementation in our `neural_network` module is really out of scope"*; `glemaitre`: *"our policy is to only maintain what we already have in our `neural_network` module without new addition."*

## Sources

Crossref and PubMed records for every citation above. Erwin/Obermayer/Schulten abstracts read verbatim via the PubMed E-utilities API after Springer, Semantic Scholar and direct fetch all failed. SOM Toolbox source read from the `ilarinieminen/SOM-Toolbox` GitHub mirror. MiniSom source and PyPI history, CRAN `kohonen` page, and the scikit-learn issue/PR threads, all fetched 2026-11-11.

**Not readable, so second-hand:** Kohonen's 1982 abstract, Kohonen's *Self-Organizing Maps* book (hence the two-phase guidance, the 500× rule, iteration counts and edition years), and the Ultsch & Siemon 1990 INNC proceedings.
