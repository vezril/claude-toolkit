# Fitness landscapes, difficulty measures, and the field's rigour problem

Two linked subjects. The first is a catalogue of 1990s attempts to predict problem difficulty from a single number, **every one of which has a published counterexample**. The second is why the field has a reputation problem and what the reform literature actually says.

⚠️ marks claims that could not be verified and are therefore not asserted.

---

# Part 1 — Fitness landscapes

## The definition, and the point that invalidates most naive analysis

A landscape is a **triple**: a search space X, a notion of adjacency/neighbourhood/accessibility on X, and a fitness function f: X → ℝ.

**Reidys & Stadler, "Combinatorial Landscapes," *SIAM Review* 44(1):3–54, 2002**, doi:10.1137/S0036144501395952, verbatim: "A fitness landscape is a mapping from a configuration space into the real numbers. **The configuration space is equipped with some notion of adjacency, nearness, distance, or accessibility.**"

**Biological origin:** Sewall Wright, "The roles of mutation, inbreeding, crossbreeding and selection in evolution," *Proc. Sixth International Congress of Genetics*, vol. 1, pp. 356–366, 1932. Altenberg's gloss: Wright "recognized a deep property of population genetic dynamics: when fitness interactions exist between genes, the genetic composition of a population can evolve into **multiple domains of attraction**… His was thus one of the earliest conceptions of a stochastic process for the optimization of multimodal functions."

**⚠️ THE OPERATOR-DEPENDENCE POINT — get this right, because it invalidates most naive landscape analysis.** Altenberg, verbatim: "The definition given by Kauffman for the NK landscape is simply a fitness function on a data structure. The genetic operators that manipulate these data structures in creating variants are not explicitly included… However, **nothing can be said about the evolutionary dynamics until the genetic operators are defined. A change in the genetic operator will effectively define a new adaptive landscape.**" (Citing Altenberg 1994a, 1995; Jones 1995a, 1995b — the latter being **Terry Jones, "Evolutionary Algorithms, Fitness Landscapes and Search," PhD thesis, University of New Mexico, March 1995.**)

**This is the structural reason the whole 1990s difficulty-measure programme failed: the measures are properties of the *fitness function*, while difficulty is a property of the *function plus operator*.**

## Deception

**Formal definition:** a problem is deceptive if, for some schema partition, the schema containing the global optimum does not have the best **static** average fitness (the average of f over all members of the schema *in the whole search space*). **That is exactly the negation of the Static Building Block Hypothesis** — see `theory.md` Part 3.

- ⚠️ Goldberg, "Simple genetic algorithms and the minimal deceptive problem," in Davis (ed.), *Genetic Algorithms and Simulated Annealing*, 1987, pp. 74–88. **Not in Crossref; the page range and the MDP definition are unverified.** The structure: a 2-bit problem where f(11) is maximal but f(0\*) > f(1\*) on static averages. It is "minimal" because deception in Goldberg's sense requires order ≥ 2.
- Deb & Goldberg, "Analyzing Deception in Trap Functions," **FOGA 2**, pp. 93–108, 1993, doi:10.1016/B978-0-08-094832-4.50012-X. ⚠️ Content unverified. *Note it sits immediately after Grefenstette's "Deception Considered Harmful" (pp. 75–91) in the same volume.* Follow-up: Deb & Goldberg, *Annals of Mathematics and AI* 10(4):385–408, 1994.
- The clean runtime-theoretic version is Wegener's TRAP, at **Θ(n^n)** for the (1+1) EA — the sharpest possible statement of "deception hurts."

**But deception is neither necessary nor sufficient for GA-hardness.** Grefenstette 1993 is the primary source; also Forrest & Mitchell, "What Makes a Problem Hard for a Genetic Algorithm? Some Anomalous Results and Their Explanation," *Machine Learning* 13(2–3):285–319, 1993 (the title is the finding), and Whitley, "Deception, dominance and implicit parallelism in genetic search," *Annals of Mathematics and AI* 5(1):49–78, 1992. ⚠️ The "neither necessary nor sufficient" phrasing is the field's standard summary, not a verified quotation.

**The sharpest *verified* related result** is the Droste/Jansen/Wegener demolition of Whitley's complement trick: Trap is easy for the heuristic H\* that evaluates each point *and its bitwise complement*, but "each search heuristic fails on most of the trap functions Trap_{n,b}." **So deception is a property of a single function relative to a single algorithm, not an intrinsic difficulty measure.**

## Epistasis

Non-additive interaction between loci — the fitness effect of changing one gene depends on the alleles at others. Altenberg's gloss: "the effect on fitness from altering one gene depends on the allelic state of other genes (Lush, 1935)."

**Measures:**

- **Epistasis variance** — Davidor, "Epistasis Variance: A Viewpoint on GA-Hardness," FOGA 1, pp. 23–35, 1991, doi:10.1016/B978-0-08-050684-5.50005-7. ⚠️ Content unverified. The construction: decompose f into its additive (first-order) part plus a residual; epistasis variance is the variance of the residual, i.e. the fraction of fitness variance *not* explained by independent per-locus effects.
- **ANOVA / experimental-design decomposition** — Reeves & Wright, "An Experimental Design Perspective on Genetic Algorithms," **FOGA 3, pp. 7–22, 1995**, doi:10.1016/B978-1-55860-356-1.50005-4. ⚠️ **Citation note: a commonly cited "Epistasis in genetic algorithms: An experimental design perspective, ICGA 1995" could not be confirmed; the FOGA 3 paper is the one in Crossref and is what Altenberg cites.** Also Reeves & Wright, "Genetic Algorithms and the Design of Experiments," IMA Volumes, pp. 207–226, 1999. The approach treats the representation as a factorial design and uses ANOVA to decompose fitness into main effects and interactions.

### The decisive negative result

**Naudts & Kallel, "A comparison of predictive measures of problem difficulty in evolutionary algorithms," *IEEE Transactions on Evolutionary Computation* 4(1):1–15, 2000**, doi:10.1109/4235.843491. **This is the single best citation for "these measures do not work."** Verbatim:

> "This paper studies a number of predictive measures of problem difficulty, among which **epistasis variance and fitness distance correlation** are the most widely known… We also point out **the need to further identify which functions are easy for a given class of evolutionary algorithms**… We finally restrict attention to the genetic algorithm (GA), and consider both GA-easy and GA-hard fitness functions, and **give experimental evidence that the values of the measures, based on random samples, can be completely unreliable and entirely uncorrelated to the convergence quality and convergence speed of GA instances** using either proportional or ranking selection."

### Why epistasis measures fail — four structural reasons

1. **They are defined on the fitness function alone and so ignore the operator**, which (per the operator-dependence point above) means they are measuring the wrong object.
2. **They are global averages over the whole space**, but search visits a tiny biased sample — hence Naudts & Kallel's experimental finding about sampled estimates.
3. **They are not invariant under monotone rescaling of fitness**, whereas rank-based selection is. Naudts & Kallel explicitly "construct a new predictive measure that is insensitive to nonlinear fitness scaling" to fix this.
4. **Zero additive variance does not imply hardness** — Altenberg's FDC counterexample (below) has *exactly zero* additive effects at every locus and is GA-easy.

## Ruggedness: autocorrelation and correlation length

**Weinberger, "Correlated and uncorrelated fitness landscapes and how to tell the difference," *Biological Cybernetics* 63(5):325–336, 1990**, doi:10.1007/BF00202749. ⚠️ Content unverified. The origin of the **random-walk autocorrelation** method: take a random walk, record the fitness time series, compute `r(s) = corr(f(x_t), f(x_{t+s}))`. The **correlation length** is `ℓ = −1/ln|r(1)|`. Short correlation length = rugged; long = smooth.

Companion Weinberger papers: *J. Theoretical Biology* 134(1):125–129, 1988; "Local properties of Kauffman's N-k model," *Physical Review A* 44(10):6399–6413, 1991; "Fourier and Taylor series on fitness landscapes," *Biological Cybernetics* 65:321–330, 1991; Weinberger & Stadler, "Why some fitness landscapes are fractal," *JTB* 163:255–275, 1993.

The Fourier/amplitude-spectrum formulation (elementary landscapes, Walsh decomposition, Laplacian eigenfunctions on the configuration graph) is Stadler's — see Reidys & Stadler 2002 and Stadler's "Fitness landscapes," *Lecture Notes in Physics* 585:183–204, 2002. For NK specifically: "with adjacent neighborhoods, only the first K+1 Fourier components contribute, while all contribute in the random neighborhood model."

The EC-side companion for operator-based parent-offspring correlation `ρ_po`: Manderick, de Weger & Spiessens, "The genetic algorithm and the structure of the fitness landscape," ICGA 1991.

### ⚠️ Altenberg's two counterexamples to ρ_po

Verbatim from FOGA 3, 1995, §4.2.1:

> "I give two constructed examples of landscapes in which ρ_po fails to predict GA performance… **1. One case with a maximal parent-offspring correlation, but which gives poor GA performance**, because parents never produce offspring fitter than what already exists, and **2. A second case with no correlation between the fitnesses of parents and their offspring, but which nevertheless gives excellent GA performance**, because the proportion of offspring that are fitter than their parents is a constant, even as the parental fitnesses increase."

The first is **blending inheritance**: offspring fitness = the mean of parental fitnesses, giving `ρ_po = 1` exactly, yet "the fittest member of the population will never be greater than the fittest in the first generation. Thus, although the mean fitness of the population will increase initially, **it has no evolvability.**"

His conclusion: "the autocorrelation statistics commonly used in landscape analysis do not [give quantitative estimates], and this is illustrated with **two examples of landscapes that give GA performance exactly contrary to that predicted by these statistics.**"

## Fitness-distance correlation, and the counterexample that killed it

**The proposal:** Terry Jones & Stephanie Forrest, "Fitness distance correlation as a measure of problem difficulty for genetic algorithms," ICGA-6, pp. 184–192, 1995.

**Definition** (via Altenberg): `ρ_FDC = Cov[F(x), d(x,x̂)] / (σ_F σ_D)` where `d(x,x̂)` is the Hamming distance to the global optimum, **with variances and covariances taken over the entire search space**.

**Jones's three conjectures, verbatim via Altenberg.** Note the sign convention — fitness is maximised and d is distance *to* the optimum, so the "good" case is *negative* correlation:

> "1. If there is a large positive fitness distance correlation (ρ ≥ 0.15), then the problem is **misleading** and the GA will be led away from the global optimum;
> 2. If there is a large negative fitness distance correlation (ρ ≤ −0.15), then the problem is **straightforward**…;
> 3. If the fitness distance correlation is near zero (−0.15 < ρ < 0.15), the prediction is **indeterminate**: (a) If the fitness-distance scatter plot shows no relationship… the problem is GA-difficult; (b) certain structures that appear in the scatter plot will indicate that the problem is straightforward, or misleading…"

**Jones's own warning**, verbatim via Altenberg: FDC's success is "both '**encouraging and alarming**' — encouraging since FDC appears to work, but alarming since '**distance' is defined without reference to the genetic operators**, the representation of the search space, or any of the dynamics of the genetic algorithm." *Jones himself recommended operator-based distances instead.*

### Altenberg's counterexample

**Lee Altenberg, "Fitness Distance Correlation Analysis: An Instructive Counterexample," ICGA-7, pp. 57–64, 1997.** Full text at `dynamics.org/Altenberg/FILES/LeeFDC.pdf`. He attacks conjecture 3(a) specifically and says so.

**The construction**, following Jones's own suggestion to use an operator-derived distance: the distance notion is **the number of single-point crossover events needed to reach the all-ones optimum**, along which "the number of discontinuities between 0 and 1 increases by one with each step." So the test function **decreases with the number of 0/1 switches along the bitstring**.

**The two properties that make it work, verbatim:**

> "1. Symmetry with respect to bit value, that is f(x) = f(x̄)… **Thus the fitness distance correlation coefficient will be zero.**"
> "2. The additive fitness components for individual bits will be zero… **all the non-zero fitness components will come from epistatic interactions between bits.** In other words, at any bit position, a 0 bit will have the same average fitness as a 1 bit."

And the scatter plot shows no structure either, so 3(b) does not rescue it: "it is difficult to discern any structure in which Hamming distance could be a guide to the GA search. In particular, **there are no points in the vicinity of the global optimum**… The next-fittest points are those of intermediate Hamming distance d(x) ≈ n/2."

**The result — it is GA-easy** (his Table 1: bits / population / max evals / mean evals in successful runs / success rate / fraction of space sampled):

| bits | pop | max evals | mean evals | success | fraction sampled |
|---|---|---|---|---|---|
| 24 | 2K | 300K | 56.3K | **100%** | 3×10⁻³ |
| 32 | 3K | 300K | 164K | **93%** | 4×10⁻⁵ |
| 50 | 10K | 2,000K | 10⁶ | **41%** | **10⁻⁹** |

**Note that the sampled fraction *shrinks* as the problem grows — which is the definition of efficient search.** His abstract: "a GA using only single-point crossover can find the global optimum with a sample on the order of 10⁻³ to 10⁻⁹ of the points in the search space, **an efficiency which increases with the size of the search space.**"

**His verdict, verbatim:** "**This result confirms the suspicion that predictors for genetic algorithm performance are vulnerable if they are based on arbitrary properties of the search space, and not the actual dynamics of the genetic algorithm.** The test function's solvability by a GA is accurately predicted, however, by another property — its **evolvability**, the probability that the genetic operator produces offspring that are fitter than their parents. It is also accurately predicted by FDC that uses **a distance measure defined by the crossover operator itself**, instead of Hamming distance."

He also notes *why* he had to engineer away all visible structure: "in the Liepins and Vose transformation, the FDC coefficient is zero because half of the search space has an FDC value of 1, while the other half has −1, and this is revealed by an '**X**' structure in the FD scatter plot."

**His list of better predictors:** "1. parent-offspring correlation ρ_po; 2. **evolvability**; 3. simulated dynamics; 4. analysis of variance for formae."

**A counterexample to conjecture 1 as well:** ⚠️ Quick, Rayward-Smith & Smith, "Fitness distance correlation and Ridge functions," PPSN V, pp. 77–86, 1998, doi:10.1007/BFb0056851 — content unverified; the known finding is that **ridge functions are GA-easy with misleadingly positive FDC.**

## Neutrality and neutral networks

**Biological root:** Motoo Kimura, "Evolutionary Rate at the Molecular Level," *Nature* 217(5129):624–626, 1968, doi:10.1038/217624a0; and *The Neutral Theory of Molecular Evolution*, CUP 1983.

### The empirical demonstration that neutral networks percolate

**Schuster, Fontana, Stadler & Hofacker, "From sequences to shapes and back: a case study in RNA secondary structures," *Proc. R. Soc. B* 255(1344):279–284, 1994**, doi:10.1098/rspb.1994.0040. Verbatim:

> "At fixed chain length the number of sequences far exceeds the number of structures… All common structures can be accessed from an arbitrary sequence by a number of mutations much smaller than the chain length. **The sequence space is percolated by extensive neutral networks connecting nearest neighbours folding into identical structures.** Implications for evolutionary adaptation… are evident: **finding a particular structure by mutation and selection is much simpler than expected.**"

**Huynen, Stadler & Fontana, "Smoothness within ruggedness: the role of neutrality in adaptation," *PNAS* 93(1):397–401, 1996**, doi:10.1073/pnas.93.1.397. ⚠️ **Note the subtitle: "in *adaptation*", not "in evolution."** Verbatim:

> "On such networks, evolving populations split into subpopulations, which diffuse independently in sequence space. **This demands a distinction between two mutation thresholds: one at which genotypic information is lost and one at which phenotypic information is lost. In between, diffusion enables the search of vast areas in genotype space while still preserving the dominant phenotype.** By this dynamic the success of phenotypic adaptation becomes much less sensitive to the initial conditions in genotype space."

**The two-threshold picture is the precise mechanism by which neutrality helps: between the thresholds you get free exploration at no phenotypic cost.**

Formal treatment: Reidys & Stadler, "Neutrality in fitness landscapes," *Applied Mathematics and Computation* 117(2–3):321–350, 2001.

### Does neutrality help? The literature is genuinely divided

- **Positive:** Huynen/Stadler/Fontana 1996 (above). And Vérel, Ochoa & Tomassini's LON study concludes "the network features studied confirmed that **neutrality, in landscapes with percolating neutral networks, may enhance heuristic search.**" *Note the two conditions in that sentence — percolating networks, and "may."*
- **Skeptical:** Knowles & Watson, "On the Utility of Redundant Encodings in Mutation-Based Evolutionary Search," PPSN VII, pp. 88–98, 2002, doi:10.1007/3-540-45712-7_9 — ⚠️ content unverified; the known finding is that redundant/neutral encodings did not help on the problems studied. ⚠️ Also the Rothlauf & Goldberg line on redundant representations (commonly *Evolutionary Computation* 11(4):381–415, 2003 — unverified).

**Netcrawling:** Barnett, "Netcrawling — optimal evolutionary search with neutral networks," CEC 2001, vol. 1, pp. 30–37, doi:10.1109/CEC.2001.934367. ⚠️ Content unverified. The netcrawler is a population-of-one hill-climber that *accepts equal-fitness moves* and so random-walks the neutral network. ⚠️ Barnett's "NKp family" paper (*Artificial Life VI*, 1998) could not be found in Crossref or OpenAlex. The NKp model itself is corroborated via Vérel/Ochoa/Tomassini: "two neutral variants of the well-known NK family… probabilistic (NKp), and quantified NK (NKq), in which the amount of neutrality can be tuned by a parameter."

## NK landscapes

Primary source read in full: **Lee Altenberg, "NK Fitness Landscapes" (§B2.7.2), in Bäck, Fogel & Michalewicz (eds.), *Handbook of Evolutionary Computation*, OUP/IOP 1997.** Original papers: **Kauffman & Levin, *J. Theoretical Biology* 128(1):11–45, 1987**, doi:10.1016/S0022-5193(87)80029-2; **Kauffman, *The Origins of Order*, OUP 1993.**

**The model, verbatim:** "The genotype's fitness is the average of N fitness components F_i contributed by each locus i. Each gene's fitness component F_i is determined by its own allele, x_i, and also the alleles at **K other epistatic loci**… `F(x) = (1/N)·Σᵢ Fᵢ(xᵢ; x_{i1},...,x_{iK})`."

Two neighbourhood schemes: **adjacent** (the K genes nearest on the chromosome, periodic boundaries) and **random**. Epistasis is a **"House of Cards"** model: "whenever an allele is changed at one locus, all of the fitness components with which the locus interacts are changed, **without any correlation to their previous values**." Implementation: a table of **2^(K+1)** uniform [0,1) numbers per fitness component. NK landscapes are spin glasses, with the resulting "frustration."

### Exact results

**K = 0** (the classical additive multi-locus model): a single globally attractive genotype; the adaptive walk reduces Hamming distance by 1 each step, so **the expected number of steps to the optimum is N/2**; neighbour fitnesses are highly correlated.

**K = N−1** (equivalent to random assignment of fitnesses):

- the probability a genotype is a local optimum is **1/(N+1)**;
- the expected number of local optima is **2^N/(N+1)**;
- the expected fraction of fitter neighbours **halves each step**;
- **the expected length of adaptive walks is approximately ln(N−1)**;
- the expected number of mutants tested is `Σ_{i=0}^{log₂(N−1)−1} 2^i`;
- as N increases, the expected fitness of the local optimum reached from a random start **decreases toward the mean fitness of the whole space, 0.5** — "Kauffman (1993) calls this the **complexity catastrophe**."

⚠️ **Correction worth noting: the expected adaptive-walk length for K = N−1 is ≈ ln(N−1), a *natural* log, not log₂(N). The log₂ appears in the *number of mutants tested*, because the fraction of fitter neighbours halves each step.** Both numbers circulate.

**Intermediate K:** for small K the highest local optima share many alleles, and that correlation falls away as K increases (faster for random than adjacent neighbourhoods). For large K, local-optimum fitnesses are asymptotically normal with mean ≈ `μ + σ√(2 ln(K+1)/(K+1))`. The average Hamming distance between local optima — roughly twice a typical walk length — is ≈ `N·log₂(K+1)/(2(K+1))`.

### Computational complexity — and the threshold is K ≥ 2, not K ≥ 3

Altenberg's §B2.7.2.5 lists Weinberger's results (adjacent solvable in O(2^K N), hence **in P**; random **NP-complete for K ≥ 3**) and then Thompson & Wright's sharpening (random K = 1 polynomial; **random K = 2 NP-complete**).

**The published version settles it: Zhang, Thompson & Wright, "The computational complexity of N-K fitness functions," *IEEE Transactions on Evolutionary Computation* 4(4):373–379, 2000**, doi:10.1109/4235.887236. Verbatim:

> "We give an algorithm to optimize adjacent-model N-K fitness functions, which is **polynomial in N**. We show that the decision problem corresponding to optimizing random-model N-K fitness functions is **NP-complete for K > 1, and is polynomial for K = 1.** If the restriction that the ith component function depends on the ith bit is removed, then the problem is **NP-complete, even for K = 1**."

⚠️ **So the correct threshold is K ≥ 2. The commonly cited "K ≥ 3" is Weinberger's weaker earlier result, superseded.** ⚠️ Also note the author order — Crossref and OpenAlex both put **Zhang** first, not Wright. Weinberger's own paper is SFI Working Paper 96-02-003, 1996, "first circulated in 1991."

## Big valley, funnels, and local optima networks

### The big valley hypothesis, and its refinement

**Boese, Kahng & Muddu, "A new adaptive multi-start technique for combinatorial global optimizations," *Operations Research Letters* 16(2):101–113, 1994**, doi:10.1016/0167-6377(94)90065-5. ⚠️ Content unverified. The finding: in the TSP under 2-opt, local optima are not scattered — their quality correlates with distance to the global optimum, so they form a single "**big valley**," and a multi-start method should restart near good solutions rather than uniformly.

**The refinement that matters: Hains, Whitley & Howe, "Revisiting the big valley search space structure in the TSP," *Journal of the Operational Research Society* 62(2):305–312, 2011**, doi:10.1057/jors.2010.116. Verbatim:

> "**while the big-valley structure does appear in much of the solution space, it breaks down around local optima that have solutions whose evaluation is very close to that of the global optimum; multiple funnels appear around local optima with evaluations close to the global optimum. The appearance of multiple funnels explains why certain iterated local search heuristics can quickly find high-quality solutions, but fail to consistently find the global optimum.**"

**So the big valley is real, but it fractures exactly where it matters — at the top.**

### The funnel picture

**Ochoa & Veerapen, "Mapping the global structure of TSP fitness landscapes," *Journal of Heuristics* 24(3):265–294, 2018**, doi:10.1007/s10732-017-9334-0. Verbatim:

> "**Our results reveal a much richer global structure than the suggestion of a 'big-valley' structure. Most landscapes of the tested instances have multiple valleys or funnels; and the number, disposition and interaction of these funnels seem to relate to search difficulty** on the studied landscapes. We also find that **the structured TSP instances feature high levels of neutrality, an observation not previously reported in the literature.**"

### Local optima networks (LONs)

Founding paper: Ochoa, Tomassini, Vérel & Darabos, "A study of NK landscapes' basins and local optima networks," GECCO 2008, pp. 555–562, doi:10.1145/1389095.1389204. ⚠️ Content unverified.

**The definition, verbatim** (Vérel, Ochoa & Tomassini): "a network based model that abstracts many details of the underlying landscape and compresses the landscape information into a weighted, oriented graph which we call the local optima network. **The vertices of this graph are the local optima of the given fitness landscape, while the arcs are transition probabilities between local optima basins.**"

**Vérel, Ochoa & Tomassini, "Local Optima Networks of NK Landscapes With Neutrality," *IEEE TEC* 15(6):783–797, 2011**, doi:10.1109/TEVC.2010.2046175, extends LONs to neutral landscapes via NKp and NKq. Findings: "**the features of neutral landscapes interpolate smoothly between landscapes with maximum neutrality and non-neutral ones**," and the neutrality-may-help conclusion quoted above.

**⚠️ Their honest methodological caveat, verbatim, and it is the limiting factor for the whole programme:** "**Our current methodology requires the exhaustive enumeration of the underlying search space. Therefore, sampling techniques should be developed before this analysis can have practical implications.**"

**Two edge definitions:** *basin-transition* edges (the original, weighted by the probability of moving between basins under the operator) and *escape* edges (Vérel, Daolio, Ochoa & Tomassini, *Artificial Evolution* EA 2011). Local-search-rule variant: Ochoa, Vérel & Tomassini, "First-Improvement vs. Best-Improvement Local Optima Networks of NK Landscapes," PPSN XI, pp. 104–113, 2010.

Scaled to real problems: QAP (Daolio et al., CEC 2010), MAX-SAT (Ochoa & Chicano), permutation flow-shop (Daolio et al.; Hernando et al.), QAPLIB (Iclanzan et al.), continuous landscapes (Adair, Ochoa & Malan, GECCO), multi-objective (Fieldsend & Alyahya), genetic-improvement landscapes (Veerapen et al.), feature selection (Mostert et al.).

**Which LON features predict difficulty:** (i) the number, size and interconnection of **funnels** (Ochoa & Veerapen 2018, quoted above); (ii) **PageRank centrality of the optimum** — Herrmann & Rothlauf, "Predicting Heuristic Search Performance with PageRank Centrality in Local Optima Networks"; (iii) shortest path to the global optimum, basin sizes, explicit funnel metrics. ⚠️ These are verified as the features the literature *uses*; the quantitative strength of their predictive power was not verified.

## Surveys to anchor this

- **Malan & Engelbrecht, "A survey of techniques for characterising fitness landscapes and some possible ways forward," *Information Sciences* 241:148–163, 2013**, doi:10.1016/j.ins.2013.04.015 — ⚠️ content unverified, but **the best entry point for the classical measures** (ruggedness, epistasis, FDC, neutrality, modality, deception).
- **Katherine Mary Malan, "A Survey of Advances in Landscape Analysis for Optimisation," *Algorithms* 14(2):40, 2021**, doi:10.3390/a14020040 — open access, read in full. A numbered catalogue of *post-2013* techniques, so use it for recent material and its bibliography. It also contains a useful observation that landscape analysis can *explain* a failure: an algorithm "performed poorly on a landscape that consisted of several suboptimal funnels that were disconnected from the global funnel."
- Ochoa & Malan, "Landscape Analysis of Optimisation Problems and Algorithms," GECCO 2024 Companion, pp. 984–1004; Vérel, "Fitness landscapes and graphs," GECCO 2013 Companion, pp. 591–616.
- For continuous sampling-based analysis: Malan & Engelbrecht, "A progressive random walk algorithm for sampling continuous fitness landscapes," CEC 2014, pp. 2507–2514.

## The synthesis

**Every single-number difficulty predictor proposed in the 1990s — deception, epistasis variance, ruggedness/autocorrelation, FDC — has a published counterexample**, and Naudts & Kallel (2000) found sampled estimates of them "completely unreliable and entirely uncorrelated" to actual GA performance.

**Two structural reasons, both stated clearly in the primary literature:**

1. They are properties of the *fitness function* while difficulty is a property of the *function plus operator* (Altenberg 1995/1997; Jones 1995).
2. They are *global averages* while search sees a biased, evolving sample.

**What has survived:**

- **operator-aware statistics** — evolvability, parent-offspring transmission in the fitness domain (Altenberg);
- **graph-theoretic global structure** — LONs, funnels, PageRank centrality (Ochoa, Tomassini, Vérel, Veerapen);
- and **rigorous runtime analysis** (see `theory.md` Part 7), which abandons difficulty measures entirely in favour of proving Θ-bounds for specific algorithm/function pairs.

---

# Part 2 — The rigour problem

## Sörensen — "Metaheuristics: the metaphor exposed"

**Kenneth Sörensen (sole author), "Metaheuristics—the metaphor exposed," *International Transactions in Operational Research* 22(1):3–18, January 2015**, doi:10.1111/itor.12001. **Published online 8 February 2013** — which is why the literature splits between "Sörensen (2013)" and "(2015)." ~1,140 citations.

⚠️ **The full text could not be retrieved** (bronze OA at Wiley only; every route 403'd, no repository copy exists). **Its section structure, internal taxonomy and verbatim sentences are therefore unverified, and specifically the claim that *Sörensen himself* maps Harmony Search onto a (μ+1) evolution strategy is unverified — that correspondence is Weyland's.**

**Abstract, verbatim:**

> "In recent years, the field of combinatorial optimization has witnessed **a true tsunami of 'novel' metaheuristic methods**, most of them based on a metaphor of some natural or man-made process. The behavior of virtually any species of insects, the flow of water, musicians playing together – **it seems that no idea is too far-fetched to serve as inspiration to launch yet another metaheuristic.** In this paper, we will argue that this line of research is **threatening to lead the area of metaheuristics away from scientific rigor.**… At the same time, truly innovative research of high quality is being performed as well."

### Use this instead if you need a quotable version

**Sörensen, Sevaux & Glover, "A History of Metaheuristics," in *Handbook of Heuristics*, Springer 2018, pp. 791–808**, doi:10.1007/978-3-319-07124-4_4; preprint arXiv:1704.00853. **Note that Glover is a co-author — the field's founding generation is on the same side.** Verbatim from §6, "The metaphor-centric period":

> "a metaphor is only a metaphor and always breaks down at a certain point… **Importantly, a metaphor is not enough to justify metaheuristic design choices or to create a foundation for completely new metaheuristics.**"

**Their sharpest test, which is the one to remember:**

> "One would expect that, at the very least, **the process that is to become the basis for a metaheuristic should optimize something** (e.g., an annealing process minimizes the energy level, natural evolution minimizes the discrepancy between the characteristics of a species and the requirements of this species' environment, ants minimize the distance between their nest and their source of food). Nevertheless, many metaheuristic frameworks can now be found based on processes that **by no stretch of imagination can be said to optimize anything, like fireworks, mine blasts, or cloud formation.**"

**The verdict:** "Both the causes and the consequences of this 'metaphor fallacy' have been extensively dealt with in a number of other publications **(short summary: it is not science)**… metaphor-based 'novel' metaheuristics take up a (dark) page in the history of metaheuristics. **A page that should be turned quickly.**"

**And on the theory side**, which bridges to `theory.md`: "Traditionally, the theoretical underpinning of heuristics and metaheuristics has not been on par with that of other areas in OR… **The development of heuristic optimization algorithms… is guided by experience, not theory. Early attempts to firmly ground the development of metaheuristics in theory have not delivered upon their promises.**"

Their reform list: adequate testing protocols; meta-analysis; **mandatory source-code disclosure**; general-purpose heuristic solvers; a heuristics-oriented modelling language; and "the change from a performance-driven community to a community in which scientific understanding is more important."

## Weyland on Harmony Search — the formal proof

**Dennis Weyland, "A critical analysis of the harmony search algorithm—How not to solve sudoku," *Operations Research Perspectives* 2:97–105, 2015**, doi:10.1016/j.orp.2015.04.001. Gold OA, read in full. (The earlier informal version: *IJAMC* 1(2):50–60, 2010, doi:10.4018/jamc.2010040104, subtitled "How the Research Community can be Misled by a 'Novel' Methodology.")

**Abstract, verbatim:**

> "We formally prove that **the harmony search algorithm is a special case of evolution strategies.** First, this implies that the harmony search algorithm itself does not offer any novelty, apart from using a different terminology. Second, the performance of the best harmony search algorithm is always bounded by the performance that can be obtained by evolution strategies… **In short, there is no reason for harmony search to exist as a separate metaheuristic framework.**… A theoretical investigation and a reimplementation… both reveal that **these results are fundamentally flawed.**"

### The exact mapping

HS parameters: HMS (harmony memory size), HMCR (harmony memory considering rate), PAR (pitch adjusting rate). The (μ+1)-ES: μ individuals; **global discrete recombination** (each variable taken from a uniformly chosen parent); mutation operator 1 applied per-variable with probability p₁ (add ±1); operator 2 with probability p₂ (resample uniformly); elitist replacement.

**Equivalence setting: μ = HMS, p₁ = PAR, p₂ = 1 − HMCR.** Under this the per-variable offspring distributions coincide exactly, and by induction the two algorithms induce **identical probability distributions over returned solutions.**

> "**Theorem 1. The harmony search algorithm is a special case of evolution strategies.** Moreover, the recombination and mutation operators used in this proof are common choices for such operators."

**The caveat he insists on:** "this does not mean that these two methods are equivalent. Instead… **for each harmony search algorithm, there exists an evolution strategy which produces the same results.** This means that evolution strategies are a **superset**… **Therefore, the only novelty of the harmony search algorithm is its metaphor, which can hardly be seen as an argument for more than 9000 publications.**" And: "Since harmony search is a special case of evolution strategies, **the best harmony search algorithm can never outperform the best evolution strategy.**"

Why he redid it formally: the 2010 paper's informality "was also criticized in the research commentary [Geem 2010]," so "we will derive these results in a strictly formal way, following the precise mathematical structure of theorem and proof." A footnote worth quoting: "we could not find an appropriate way for highlighting ironic passages. In any case, these passages should not be too difficult to identify."

Literature growth he reports: Google Scholar hits for "harmony search" ≈ **500 (2010) → 3,000 (2012) → >9,000 (end of 2014).**

### What he showed about the published experiments

Target: Geem, "Harmony search algorithm for solving sudoku," KES 2007, pp. 371–378.

1. **The objective function is wrong.** Geem's f sums |row-sum − 45| + |column-sum − 45| + |block-sum − 45|. Weyland shows by explicit construction that **the puzzle's unique solution is not the unique f = 0 point** — perturbing four cells by (+1,−1,−1,+1) gives another f = 0 solution. So the reported "optimal solutions found" cannot be interpreted.
2. **Theoretical success bounds.** 41 empty cells. P(the solution appears at initialisation) ≤ **10⁻³⁷**. Upper bounds on success within 10⁴ iterations at HMCR = 0.5: **2.8×10⁻⁷ / 5.2×10⁻⁸ / 9.9×10⁻¹²** for PAR = 0.01/0.1/0.5. **Geem reports all 12 runs at HMCR = 0.5 as successful; Weyland bounds the joint probability of that at ≤ 4.83×10⁻¹⁰⁰**, with the comparison: "an astronomically small probability. To get a feeling for how small this probability really is, we would like to refer to **the number of atoms in the visible universe, which is commonly estimated to be around 10⁸⁰.**" He also notes the irony that Geem reports the *worst* results exactly where the bound is most favourable.
3. **Reimplementation: 36 parameter settings × 20 runs = 720 runs, at 10⁶ iterations (100× Geem's).** Verbatim: "They are shocking and they are in stark contrast to the results reported in [20]. **None of the 720 runs could find the unique solution of the sudoku puzzle within the maximum number of 10⁶ iterations.**"
4. **Timing implausibility:** "While the computational time for a run with 10⁴ iterations of our algorithm on a customary laptop was just **0.02 s**, the computational times reported in [20] are all several seconds… our reimplementation was around **4 orders of magnitude faster.**"
5. And the obvious point: "such puzzles can usually be solved within a fraction of a second using problem specific algorithms. **It is therefore highly questionable, why a heuristic should be applied to this problem at all.**"

His reform agenda ends with the incentive diagnosis: "**It is obvious that the current system gives flawed incentives to researchers and other involved parties.**"

**The other side:** Zong Woo Geem, "Research Commentary: Survival of the Fittest Algorithm or the Novelest Algorithm?", *IJAMC* 1(4):75–79, 2010, doi:10.4018/jamc.2010100105 — the Harmony Search founder's reply to Weyland 2010. ⚠️ **Geem's text could not be fetched; his arguments are unverified beyond Weyland's characterisation**, which is that the substantive objection was *informality* — exactly why Weyland 2015 recast it as theorem-and-proof.

## Camacho-Villalón, Dorigo & Stützle (IRIDIA, ULB)

### The six bestial metaphors

**Camacho-Villalón, Dorigo & Stützle, "Exposing the grey wolf, moth-flame, whale, firefly, bat, and antlion algorithms: six misleading optimization techniques inspired by *bestial* metaphors," *International Transactions in Operational Research* 30(6):2945–2971**, doi:10.1111/itor.13176 (online 2022, issue 2023).

**Abstract, verbatim:** "We present a rigorous, component-based analysis of six widespread metaphor-based algorithms… Our result is that the ideas proposed in the six studied algorithms have been in the literature of metaheuristics for years and **that the only novelty in these self-proclaimed novel algorithms is six different terminologies derived from the use of new metaphors.**"

**Their three-part indictment:** (1) the metaphor introduces new terminology for already-known concepts; (2) the mathematical models derived from the metaphor are trivial and loosely connected to it — "**often the proposed algorithms do not match the mathematical models derived from the metaphor**"; (3) the motivation is "it has never been used before" rather than scientific.

**Per-algorithm results** — note these are specific structural identifications, not a lazy "it's just PSO":

| Algorithm | Identified as |
|---|---|
| **Grey Wolf Optimizer** | PSO. Its update "is the same as the computation of the center cᵢᵗ in SPSO-2011" — both build a hypertriangle per particle and use its centroid; GWO uses **the same three iteration-best solutions for every particle**, which is good for intensification but "prevents particles from exploring other regions." **GWO has no velocity term.** Its authors themselves found the first version "prone to stagnation in local solutions" and bolted on a decaying perturbation |
| **Moth-Flame** | "a variant of ePSO" — follows from ePSO's rule **by setting φ₁ᵗ = 0 and k₁ = 1**, with a rank-based model of influence |
| **Whale Optimization** | "a PSO algorithm that combines the mathematical models of SPSO-2011 and ePSO." **No velocity vector**; a random-neighbour rule is the diversity substitute |
| **Firefly** | "a variant of the SDPSs… using the extrapolation coefficients of ePSO and the fully informed model of FiPSO." **"The only difference is that FA scales the coefficient by Euclidean distance between particles whereas ePSO scales it by the difference in objective value"** |
| **Bat** | PSO + simulated annealing. **Setting ω = 1 and φ₁ = 0 reduces StdPSO's velocity rule to BA's**; BA's loudness/pulse-rate "plays the same role as parameter T in SA" |
| **Antlion** | **an evolution strategy.** Fitness-proportional selection + intermediate recombination + spherical mutation + elitist survival: "**it is virtually same as the (μ + λ)−ES (Schwefel, 1981), where the only difference is that, in ALO, mutation is applied before recombination**" |

**Conclusion, verbatim:** "**we consider it urgent that metaphor-based algorithms are not published anymore unless their authors (i) present the algorithms using the standard optimization terminology, and (ii) are able to show that the new behavior leads to new ideas that are useful in optimization.**"

### Intelligent Water Drops = Ant Colony Optimization

**Camacho-Villalón, Dorigo & Stützle, "The intelligent water drops algorithm: why it cannot be considered a novel algorithm," *Swarm Intelligence* 13(3–4):173–192, 2019**, doi:10.1007/s11721-019-00165-y.

**Abstract, verbatim:** "We demonstrate that **all main algorithmic components of IWD are simplifications or special cases of ant colony optimization (ACO)**, and therefore, IWD is simply a particular instantiation of ACO. We show that the natural metaphor of 'water drops flowing in rivers removing the soil from the riverbed' … is **unnecessary, misleading and based on unconvincing assumptions of river dynamics and soil erosion that lack a real scientific rationale.**"

**The component mapping:** *soil ↔ pheromone*, but **inverted** (good components have low soil, high pheromone), and "in IWD soil can become negative… while in ACO it is always strictly positive." **Solution construction:** "the transition rule of IWD **simplifies to the one of ACO by setting the parameters α = −1 and β = 0**" (β = 0 means IWD uses no heuristic information). **Local update** = a special case of Ant-Q's local reinforcement. **Global update** = a special case of Ant Colony System's global update, with ρ's interval redefined to [−1, 0]. "Water drop velocity" has no ACO counterpart and functionally just modulates exploration/exploitation.

Verbatim: "**all the modifications reviewed in this article have a direct correspondence with a specific modification proposed before for an ACO algorithm.**"

**Their three criteria**, reused in all their later papers: (i) the metaphor must bring new concepts genuinely related to the optimization process; (ii) its terminology must make those concepts *easier* to convey; (iii) the algorithmic ideas must be genuinely new, not a renaming.

**Their scale admission:** "adopting the approach presented in this paper to analyze all the metaphor-inspired metaheuristic algorithms that have not been rigorously analyzed yet, **which are in the order of hundreds**, would require an unreasonable amount of work and time."

### The rest of the group's output

- **"Grey Wolf, Firefly and Bat Algorithms: Three Widespread Algorithms that Do Not Contain Any Novelty," ANTS 2020, LNCS 12421, pp. 121–133.** Contains the cleanest one-sentence summary of Weyland anywhere: "**One of the first examples of this was provided in 2010 by Weyland in a rigorous analysis of the harmony search algorithm. In this analysis, Weyland found that this seemingly new method was the same as a particular evolutionary algorithm, called 'evolution strategy (μ + 1)', which was proposed about 30 years before the HS algorithm.**"
- **"An analysis of why cuckoo search does not bring any novel ideas to optimization," *Computers & Operations Research* 142:105747, 2022.** Identified as the **(μ + λ)-ES (1981)** and classic **differential evolution (1997)**. Killer finding: "**Surprisingly, we found that the algorithm the authors proposed for cuckoo search does not match the publicly available implementation they provided; moreover, neither of them really follows the metaphor of the cuckoos that inspired the algorithm.**" Context: the two main CS papers "have now been cited almost 8,700 times."
- **"Designing New Metaheuristics: Manual Versus Automatic Approaches," *Intelligent Computing* 2:0048, 2023** — the constructive counterpart.
- **"Beyond metaphors: rethinking metaphors in metaheuristics algorithm design," *npj Artificial Intelligence* 2(34), 2026**, doi:10.1038/s44387-026-00089-z. "We argue that **manually designing algorithms based on metaphors belongs to the past.**" And: "the metaheuristics landscape has become populated by algorithms inspired by almost every conceivable behavior—natural, artificial, and even supernatural—**to the point where pseudoscience seems to have a place in the field**, demonstrating poor scientific housekeeping and putting the reputation of the field at risk." It assesses the 2021 open letter as having failed to reverse the trend.
- The enabling framework that lets them say "X is PSO" rigorously: **"PSO-X: A Component-Based Framework for the Automatic Design of Particle Swarm Optimization Algorithms," *IEEE TEC* 26(3):402–416, 2022.**

## The open letter

⚠️ **There is no paper titled "Metaphor-based metaheuristics, where are we now? where are we going?" in *Natural Computing* (2022).** The intended item is:

**Aranha, Camacho Villalón, Campelo, Dorigo, Ruiz, Sevaux, Sörensen & Stützle, "Metaphor-based metaheuristics, a call for action: the elephant in the room," *Swarm Intelligence* 16(1):1–6, 2022**, doi:10.1007/s11721-021-00202-9. Open Access. **~221 citations** — the most-cited item in this cluster after Sörensen.

**Its four-part taxonomy of harms:**

1. **Useless metaphors** — "inventing a metaheuristic that loosely mimics a real-world process is a trivial exercise that does not in itself justify inclusion in the scientific body of literature." And: "**there are numerous examples of metaphor-based metaheuristics in which the metaphor, the mathematical model derived from the metaphor and the implementation of the algorithm are three (almost completely) different things.**"
2. **Lack of novelty** — "what is invariably new is the non-standard terminology," with three named harms: "(i) creating confusion in the literature, (ii) hindering our understanding…, and (iii) making extremely difficult to compare metaheuristics both theoretically and experimentally."
3. **Poor experimental validation** — "the so-called **apples to oranges comparison**, often comparing 'novel' metaphor-based metaheuristics run on recent computers against methods run on older computers"; baselines are other versions of the same metaphor. Also: "expressing an optimization method in the non-standard, metaphor-based vocabulary **only serves to obfuscate its functioning.**"
4. **Venue shopping** — the mechanism, verbatim: "if the metaphor is the mating behaviour of bats, authors will attempt to publish it in specialised journals on bats… If the metaphor is the spread of a virus, they will turn to journals on biomedical informatics. **The additional advantage of submitting a manuscript to what can only be considered an off-topic journal is that editors and reviewers might not be sufficiently knowledgeable in the specific field of optimization to evaluate the true merits of the paper.**"

**The exact policy text they ask every editor-in-chief to adopt, verbatim:**

> "This journal will not publish papers that propose 'novel' metaphor-based metaheuristics, unless the authors (i) present their method using the normal, standard optimization terminology; (ii) show that the new method brings useful and novel concepts to the field; (iii) motivate the use of the metaphor on a sound, scientific basis; and (iv) present a fair comparison with other state-of-the-art methods using state-of-the-art practices for benchmarking algorithms."

**Signatories: more than 90 researchers** (95 affiliation-bearing lines; the group's own 2026 comment says "more than 90," which is the safer phrasing).

## Editorial policies

**Journal of Heuristics — "Policies on Heuristic Search," policy text obtained verbatim.** Four sections (metaphor-based methodologies / competitive testing and the up-the-wall game / customized solutions / statistically valid experiments), with a reference list of Barr et al. 1995, Burke et al. 2009, Hooker 1995, Sörensen 2013.

> "**Proposing new paradigms is only acceptable if they contain innovative basic ideas**… The Journal of Heuristics avoids the publication of articles that repackage and embed old ideas in methods that are claimed to be based on metaphors of natural or manmade systems and processes. These so-called 'novel' methods employ analogies that range from **intelligent water drops, musicians playing jazz, imperialist societies, leapfrogs, kangaroos, all types of swarms and insects and even mine blast processes**… **Metaphors are cheap and easy to come by. Their use to 'window dress' a method is not acceptable.**"
>
> "Implementations should be explained by employing standard optimization terminology, **where a solution is called a 'solution' and not something else related to some obscure metaphor (e.g., harmony, flies, bats, countries, etc.). In short, the journal embraces a component-based view of heuristic search.**"
>
> "**Renaming existing concepts does not count as a contribution.**"
>
> On competitive testing: "**the ultimate goal of science is to understand**… **the journal finds no value in conclusions stating that procedure X outperformed procedure Y if there is no insight related as to why this happened. Competitive testing fails to yield insight in the performance of algorithms.**"
>
> "For procedures that require parameter tuning, the available data must be partitioned into a training and a test set. **Tuning should be performed in the training set only.**"

⚠️ The *Swarm Intelligence* (Dorigo 2016) and ACM TELO (2021) policies are cited in the letter but **their texts could not be retrieved.**

**The methodological ancestor:** **Hooker, "Testing heuristics: We have it all wrong," *Journal of Heuristics* 1(1):33–42, 1995**, doi:10.1007/BF02430364. Abstract verbatim:

> "The competitive nature of most algorithmic experimentation is a source of problems that are all too familiar… **Competitive testing tells us which algorithm is faster but not why.**… **a more scientific approach of controlled experimentation, similar to that used in other empirical sciences, avoids or alleviates these problems. We have confused research and development; competitive testing is suited only for the latter.**"

⚠️ Page-range discrepancy: Crossref and Springer give 33–42; the *Journal of Heuristics* policy page cites 33–44. Use 33–42. Also Hooker, "Needed: An Empirical Science of Algorithms," *Operations Research* 42(2):201–212, 1994. Companion: Barr, Golden, Kelly, Resende & Stewart, "Designing and Reporting on Computational Experiments with Heuristic Methods," *Journal of Heuristics* 1(1):9–32, 1995.

## The Evolutionary Computation Bestiary

**`github.com/fcampelo/EC-Bestiary`**, rendered at `fcampelo.github.io/EC-Bestiary`. Maintainers Felipe Campelo and Claus Aranha. CC BY-NC-SA 4.0. **688 stars.** Archived snapshot DOI 10.5281/zenodo.1293352 (points at the 2018 deposit, not the current README).

**⚠️ Count: the README says "Updated 2026-07-01" and states no total. An own count gives 343 entries across 31 alphabetical sections.** Historical figures from the papers: "around 260 unique entries" as of July 2021, against "as many as 360 unique metaphors" in Molina et al. (2020).

**Inclusion criteria, verbatim:** "1. the work must be in a peer reviewed publication (journal or conference); 2. the title or abstract must name the algorithm after the natural (or supernatural) metaphor on which it was based" — and "only the earliest known mention for each metaphor is included."

**Memorable README lines:** "**We do not endorse or recommend the use of any of the methods listed here. In fact, we find most if not all of them quite ridiculous**…" / "**While we personally believe that the literature could do with more mathematics and less marsupials**, and that we, as a community, should grow past this metaphor-rich phase in our field's history (a bit like chemistry outgrew alchemy)…" / "**it is not a Hall of Fame of algorithms** – think of it more as The island of Doctor Moreau: a place with a few good creatures, but which are vastly outnumbered by mindless beasts." Epigraph from Machado de Assis's *O alienista*: "Till now, madness has been thought a small island in an ocean of sanity. I am beginning to suspect that it is not an island at all but a continent."

### The paper

**Campelo & Aranha, "Lessons from the *Evolutionary Computation Bestiary*," *Artificial Life* 29(4):421–432, 2023**, doi:10.1162/artl_a_00402. (Workshop version: LIFELIKE 2021, CEUR vol. 3007.)

**Their framing:** Kekulé's ouroboros dream and Howe's cannibal-spear dream — inspiration is fine, but "it is clear to anyone who has gone through even a basic course in organic chemistry that **scientists do not discuss their work using snake anatomy terminology**, or try to come up with new compounds by carefully examining legendary reptiles."

Origin: "Inspired by a 'Cat Swarm Optimization' paper, in 2014 we started gathering examples of particularly absurd metaphors published in peer-reviewed venues."

**THE PUBLICATION-RATE CURVE — the single most useful number in this literature:**

| Period | Rate | Examples |
|---|---|---|
| 2000–2008 | a few per year | sheep flocks, musicians, plant saplings, parliamentarism, Big Bang |
| 2009–2013 | **more than 1/month** | intelligent water drops, group counselling, sports championships, fireflies, paddy fields, mountain climbers |
| after 2014 | **about 2 per month** | sharks, zombies, volleyball, reincarnation, four whale-based, three football-based, barnacles, chicken swarms, interior design and decoration |

**The fragmentation argument, verbatim:** "This explosion of metaphor-centered methods has led to an intense fragmentation of the literature into **tens, perhaps hundreds, of small, barely-discernible niches**… How should one compare the ability of a bird to drop a cuckoo egg from its nest to the behavior of a scouting bee? It takes a deeper reading to find out, for instance, that **these two completely different descriptions refer to the same underlying computational action, namely generating a new random solution when the search has stalled.**"

**Their methodological-failure checklist, verbatim:** "the almost exclusive focus on **competitive testing** rather than on the underlying working principles of algorithms; **overfitting** of algorithms and implementations to test problems; the **absence of well-defined underlying hypotheses**; the exclusive use of very similar algorithms… as comparison baselines, instead of state-of-the-art methods; **unbalanced tuning efforts**; and a general **lack of reproducibility.**"

**Causes:** "a structure of perverse incentives"; publish-or-perish producing a "**natural selection of bad science**"; the concentration statistics — "**the 6 author names that appear most often in the Bestiary entries have each created between six and ten different metaphor-based methods**" and "**There are at least 40 authors that have created two or more methods**"; "salami science"; and "a particular brand of '**cargo cult science**' (Feynman, 1974): work that emulates scientific practices… **without actually representing an actual scientific process of defining, testing and refining hypotheses.**"

**Venue colonization:** "optimization tracks of some application journals sometimes become '**colonized**' by cliques that keep publishing minute variations of bizarre methods with little oversight." Their worked example is a "**COVID-19 optimization algorithm**" in a high-impact biomedical journal, whose argument they reduce to "1. Covid-19 is overloading hospitals and causing death. 2. Covid-19 must be contained… 3. Therefore, we need an efficient optimizer capable of 'solving NP-hard… problems.'" → "This argument presents not only a clear **non sequitur**… but also suggests lack of understanding of basic aspects of computational complexity."

**Their recommendations:** raise awareness; **component/module-based frameworks** describing metaheuristics in metaphor-free common language; **similarity metrics** for metaheuristics "which can greatly simplify… the investigation of which algorithms can be seen as particular cases of others"; **automatic algorithm design/configuration**; and strict editorial policies — with a self-aware footnote that "the proposal of any standard framework for metaheuristics can raise its own issues, as illustrated in `https://xkcd.com/927/`."

**Their pessimism:** "our experience tells us that **change is still likely to be slow.** Even when metaheuristics journals cease to become a breeding ground for the metaphors, this change will take time to spread to application venues, where groups that have specialized into the regular publication of new metaphors managed to acquire a stronghold."

⚠️ **There is no paper titled "Evolutionary computation and the reinvention of the wheel."** The phrase "This pattern of reinventing the wheel" is a sentence *inside* both Campelo–Aranha papers.

## Benchmarking practice

**Bartz-Beielstein, C. Doerr, van den Berg, Bossek, Chandrasekaran, Eftimov, Fischbach, Kerschke, La Cava, López-Ibáñez, Malan, Moore, Naujoks, Orzechowski, Volz, Wagner & Weise (17 authors), "Benchmarking in Optimization: Best Practice and Open Issues," arXiv:2007.03488** (v1 7 July 2020, v2 16 Dec 2020). ⚠️ No journal version found.

Provenance: "This joint initiative was established during the **Dagstuhl seminar 19431 on Theory of Randomized Optimization Heuristics**, which took place in October 2019."

**The eight-item checklist, verbatim from §10 — their headline deliverable:**

> "1. **goals**: did the authors clearly state the reasons for this study? 2. **problems**: is the selection of problem instances well motivated and justified? 3. **algorithms**: do comparisons include relevant competitors? 4. **performance**: is the choice of the performance measure adequate? 5. **analysis**: are standards from statistics considered? 6. **design**: does the experimental setup enable efficient and fair experimentation? What measures are taken to avoid 'cherry-picking results'? 7. **presentation**: are the results well organized and explained? 8. **reproducibility**: data and code availability?"

**Their stance:** "it is not our intention to dictate specific test statistics, experimental designs, or performance measures. Instead, we claim that **publications in EC would improve, if authors explain, why they have chosen this specific measure, tool, or design.**"

**The best diagnosis quote in the whole literature (§1), verbatim:**

> "**Gent and Walsh (1994) stated that the empirical study of algorithms is a relatively immature field – and we claim that this situation has unfortunately not significantly changed in the last 25 years.**… EC has not agreed upon general methodology for performing benchmark studies like the fields of statistical Design of Experiments or data mining… **The question remains: why are minimum standards not considered in every paper submitted to EC conferences and journals?** One answer might be: **setting up a sound benchmark study is very complicated.**… Another answer might be: **practical guidelines are missing.**"

A nice internal detail: §1 carries a **Schwefel (1975)** PhD-thesis epigraph — "The extremely large and constantly increasing number of optimization methods inevitably leads to the question of the best strategy. There does not seem to be a clear answer. **Because, if there were an optimal optimization process, all other methods would be superfluous…**" — **a statement of the NFL intuition 22 years before Wolpert & Macready.**

## Other verified "it's not novel" papers

- Piotrowski, Napiorkowski & Rowinski, "How novel is the 'novel' black hole optimization approach?", *Information Sciences* 267:191–200, 2014 (Black Hole = simplified PSO).
- Melvin, Dodd & Groß, "Why 'GSA: a gravitational search algorithm' is not genuinely based on the law of gravity," *Natural Computing* 11(4):719–720, 2012.
- Simon, Rarick, Ergezer & Du, "Analytical and numerical comparisons of biogeography-based optimization and genetic algorithms," *Information Sciences*.
- Lones, "Mitigating Metaphors: A Comprehensible Guide to Recent Nature-Inspired Algorithms," *SN Computer Science* 1(1), 2020.
- Tzanetos & Dounias, "Nature inspired optimization algorithms or simply variations of metaheuristics?", *Artificial Intelligence Review* 54(3):1841–1862, 2021.
- Molina, Poyatos, Del Ser, García, Hussain & Herrera, "Comprehensive Taxonomies of Nature- and Bio-inspired Optimization," *Cognitive Computation* 12(5):897–939, 2020 — **the "as many as 360 metaphors" source.**
- Swan et al. (16 authors incl. Sörensen), "Metaheuristics 'In the Large'," *European Journal of Operational Research* 297(2):393–406, 2021 — the constructive research-agenda counterpart.
- **For the other side, presented fairly:** Del Ser, Osaba, Molina, Yang, Salcedo-Sanz, Camacho, Das, Suganthan, Coello Coello & Herrera, "Bio-inspired computation: Where we stand and what's next," *Swarm and Evolutionary Computation* 48:220–250, 2019 — the moderate, more sympathetic-to-bio-inspiration position.
