# The dialects, and what actually distinguishes them

An EA is a template with six slots. The "dialects" are conventional fillings of those slots, and the honest framing is that the labels have become misleading rather than that the dialects merged.

Standard reference for all terminology: **Eiben & Smith, *Introduction to Evolutionary Computing*, 2nd ed., Springer Natural Computing Series, 2015**, doi:10.1007/978-3-662-44874-8 (ch. 4 "What Is an Evolutionary Algorithm?" pp. 25–48; ch. 7 "Popular Evolutionary Algorithm Variants" pp. 99–116).

⚠️ marks what could not be verified against a source actually read.

---

## The generic loop and the six slots

```
initialise population P(0)        <- REPRESENTATION + initialisation
evaluate each individual          <- FITNESS FUNCTION
repeat until TERMINATION:
    select parents from P(t)      <- PARENT SELECTION (mating selection)
    recombine selected parents    <- RECOMBINATION / CROSSOVER
    mutate the offspring          <- MUTATION
    evaluate offspring            <- FITNESS FUNCTION
    select survivors -> P(t+1)    <- SURVIVOR SELECTION (replacement)
```

Plus population size, offspring count and the termination condition.

**Genotype vs phenotype.** The genotype is the encoded representation the operators act on; the phenotype is the decoded candidate the fitness function scores. The map between them *is* the representation, and its properties (locality, redundancy) are a first-class design concern — see `operators-and-representation.md`. **Selection operates on phenotype fitness; variation operates on genotypes.** Everything that makes EAs hard to reason about lives in that gap.

**The exploration/exploitation axis organises the whole field.** Exploitation rises with selection pressure (tournament size, truncation ratio, elitism, generation gap) and falls with variation strength (mutation rate and step size, crossover disruption, population size, migration, niching). Every operator parameter is a position on that dial, and the recurring failure mode is too much exploitation — premature convergence.

---

## Genetic algorithms

- Holland, *Adaptation in Natural and Artificial Systems*, Michigan 1975; 2nd ed. MIT Press 1992. ⚠️ Book not read.
- Goldberg, *Genetic Algorithms in Search, Optimization, and Machine Learning*, Addison-Wesley 1989, ISBN 0-201-15767-5. ⚠️ **Do not print the famous "magnificent fortresses … juxtaposition of short, low-order, high-performance schemata" sentence as a quotation** without a library check; the book could not be reached and Crossref carries only the *Choice Reviews* record.
- De Jong, "An Analysis of the Behavior of a Class of Genetic Adaptive Systems," PhD diss., Michigan 1975 — the source of the De Jong F1–F5 test functions. ⚠️ Not online.

Precursors worth naming: Fraser's 1957 simulations of genetic systems, Bremermann, Bledsoe, Box's evolutionary operation (EVOP, 1957), Friedberg's 1958–59 program-evolution attempts.

**The canonical GA** is binary strings + fitness-proportionate (roulette) selection + one-point crossover at high rate + bit-flip mutation at low rate + generational replacement. **This is a textbook object, not a recommendation** — essentially every component has been superseded in practice by tournament selection, real-valued or problem-specific representations, elitism, and steady-state replacement.

### Holland's project was adaptation, not optimisation

This is verified in full and it is the most useful framing point in the GA literature. **De Jong, "Genetic Algorithms Are NOT Function Optimizers," FOGA 2, pp. 5–17, 1993**, doi:10.1016/b978-0-08-094832-4.50006-4 (read in full at `mli.gmu.edu/papers/91-95/92-12.pdf`; GMU MLI report 92-12).

His thesis, verbatim: *"There is a subtle but important difference between 'GAs as function optimizers' and 'GAs are function optimizers'."* On what the algorithm is: *"The algorithm in question wasn't designed to solve any particular problem … Rather, it is a high level simulation of a biologically motivated adaptive system, namely evolution."* On the origin: *"The motivating context that led to Holland's initial GA work was the design and implementation of robust adaptive systems."*

Why the canonical GA is not an optimiser, verbatim: *"populations do not in general converge to dynamic steady states containing multiple copies of the global optimum. In fact it is quite possible for the best individual to never appear or appear and then disappear from the population forever."* What it is doing instead, per Holland: *"optimizing a sequential decision process involving uncertainty"* — maximising cumulative payoff under a limited trial budget.

The practical bridge, verbatim: *"The standard way of using GAs as function optimizers … is to keep track of the (globally) best individual produced so far regardless of whether that individual exists in the current population. That is, the population is viewed as a database (an accumulating world model) of samples."*

And his memorable symptom: GAs *"frequently don't exhibit a 'killer instinct' in the sense that, although they rapidly locate the region in which a global optimum exists, they don't locate the optimum with similar speed."* Hence the memetic turn — see below.

A closing claim worth carrying: *"A GA that satisfies the Schema Theorem does not necessarily make it a good optimizer. Conversely, when we add scaling, introduce ranking and/or elitist strategies … there is no a priori reason to believe that it continues to solve sequential decision problems effectively."* You can have one or the other guarantee, not both.

### Community infrastructure

ICGA (1985–) and FOGA; *Evolutionary Computation* from 1993; *IEEE TEVC* from 1997.

The reference work of the era: **Bäck, Fogel & Michalewicz (eds), *Handbook of Evolutionary Computation*, jointly IOP Publishing and Oxford University Press, 1997**, 1130 pp., doi:10.1887/0750308958. Its 2000 two-volume derivative (*Evolutionary Computation 1/2*, doi:10.1887/0750306645 and doi:10.1887/0750306653) is described by the publisher itself as *"Culling material from the Handbook of Evolutionary Computation"* — a repackaging, not a new edition. The *Handbook of Natural Computing* (Rozenberg, Bäck & Kok, Springer 2012, doi:10.1007/978-3-540-92910-9) does **not** supersede it: EC occupies roughly 360 of 2052 pages in about 11 survey chapters. Call the 1997 Handbook "the field's major reference work of the late 1990s"; ⚠️ "landmark" or "*the* standard reference" is editorial.

---

## Evolution strategies

### History

TU Berlin, mid-1960s: Peter Bienert, Ingo Rechenberg, Hans-Paul Schwefel. Verbatim from **Beyer, "Evolution strategies," *Scholarpedia* 2(8):1965, 2007**, doi:10.4249/scholarpedia.1965: *"Its roots date back to the mid 1960s when P. Bienert, I. Rechenberg, and H.-P. Schwefel at the Technical University of Berlin, Germany, developed the first bionics-inspired schemes for evolving optimal shapes of minimal drag bodies in a wind tunnel using Darwin's evolution principle."* ⚠️ Bienert's specific role (the automatic experimenter / *Versuchsautomat*) is unverified.

**The two-phase Laval nozzle is the best-documented early application**, and Schwefel's own first-person account is quotable (*"Evolving Solutions for Design and Management Tasks on Computers,"* Reihe Computational Intelligence 71, Universität Dortmund, doi:10.17877/DE290R-15258). The nozzle *"was solved with a simple (1+1) ES using binomially distributed mutations and decreasing variance during two weeks of experimenting with hot water at the power station of the Technical University of Berlin"*; it was *"formed by conically bored brass segments of 1 cm width … with diameters varying from 6 mm at the throat to a maximum of 36 mm in steps of 2 mm"*; *"Just 300 experiments had been sufficient to do the job"*; and the length evolved too — *"By imitating gene duplication and gene deletion, both the convergent as well as the divergent parts became variable in length … the best nozzle turned out to be much longer than expected."* Primary: Klockgether & Schwefel, "Two-phase nozzle and hollow core jet experiments," *Proc. 11th Symp. Engineering Aspects of Magnetohydrodynamics*, pp. 141–148, Caltech, March 1970.

⚠️ **The jointed-plate experiment could not be sourced.** The closest verified wording is Beyer's "minimal drag bodies in a wind tunnel."

⚠️ **Date conflicts worth flagging rather than resolving silently.** Rechenberg's RAE Library Translation 1122 is dated 1965 in all three deposited reference lists checked (the "1964/1965" hedge comes from elsewhere). Schwefel's Diplomarbeit is 1965 per his own reference list, 1964 per Rudolph 2012. Rechenberg's dissertation: the K10plus catalogue's field 502 reads "Diss., 1970" while Beyer & Schwefel 2002 and Schwefel both say 1971; the book is *Evolutionsstrategie*, Frommann-Holzboog 1973, with an afterword by Manfred Eigen.

Later books: Schwefel, *Numerische Optimierung von Computer-Modellen mittels der Evolutionsstrategie*, Birkhäuser 1977 (English: *Numerical Optimization of Computer Models*, Wiley 1981); Schwefel, *Evolution and Optimum Seeking*, Wiley 1995. D.B. Fogel (ed.), *Evolutionary Computation: The Fossil Record*, IEEE Press 1998, is the useful primary-source anthology.

### The notation, precisely

| Form | Meaning |
|---|---|
| `(1+1)-ES` | one parent, one offspring; offspring replaces parent iff at least as good |
| `(μ, λ)` | **comma**: the μ best of the **λ offspring only** become next parents. Parents always die. **Non-elitist.** Requires λ ≥ μ |
| `(μ + λ)` | **plus**: the μ best of the **union** survive. **Elitist and monotone.** λ = 1 is the steady-state case |
| `(μ/ρ, λ)`, `(μ/ρ + λ)` | ρ is the **mixing number** — parents per offspring, ρ ≤ μ |

Verbatim (Beyer): *"Here mu denotes the number of parents, rho <= mu the mixing number (i.e., the number of parents involved in the procreation of an offspring), and lambda the number of offspring."*

Subscripts `ρ_I` / `ρ_W` denote intermediate / weighted recombination; intermediate is assumed when unsubscripted (**Hansen, Arnold & Auger, "Evolution Strategies," *Springer Handbook of Computational Intelligence*, pp. 871–898, 2015**, doi:10.1007/978-3-662-43505-2_44). The notation generalises to `(μ, κ, λ)` with maximum age κ: **plus-selection is κ = ∞, comma-selection is κ = 1** (Schwefel & Rudolph, "Contemporary evolution strategies," ECAL 1995).

**Two corrections.** (a) ρ = 1 meaning "no recombination" is *implied*, not stated verbatim in either authoritative source. (b) Per Beyer, **multi-recombination means ρ > 2, not ρ = μ**; "global" recombination is ρ = μ.

**The λ/μ ≈ 7 ratio** is ⚠️ unverified from primary — Bäck & Schwefel, *Evolutionary Computation* 1(1):1–23, 1993, is the usual attribution and is paywalled on every route. What *is* verified and partly tensions with it: Beyer gives *"Typical truncation ratios mu/lambda in strategies with comma-selection in continuous search spaces are in the range from 1/7 to 1/2"*; Hansen/Arnold/Auger's σ-self-adaptive ES recommends λ ≥ 5n, μ ≈ λ/4 (ratio 1/4, chosen so μ ≥ 1.25n keeps σ-self-adaptation reliable); sphere theory gives optimal μ/λ = 0.27; and Bäck & Hammel's worked illustration is a (15,100)-ES, λ/μ = 6.67. **So 7 is the strong end of a recommended band, not a law.**

**Why comma is preferred with self-adaptation.** An individual carrying a maladapted (e.g. far too small) step size can be retained forever under plus-selection, because plus-selection only ever asks whether the *objective* value is good. Eiben & Smith's own wording: *"(mu,lambda)-selection is preferred for: Better in leaving local optima; Better in following moving optima; Using the + strategy bad sigma values can survive in <x,sigma> too long if their host x is very fit."* Beyer pushes the other way for other reasons: plus-selection with a reachability-respecting mutation *"guarantees stochastic convergence to the global optimizer"* (an infinite-time result only), and *"Using plus-selection is recommended for combinatorial optimization problems."* The noise-domain version of the latching hazard has its own name — **overvaluation** (see `operators-and-representation.md`).

### The 1/5th success rule (Rechenberg 1973)

**Origin of the figure**, verbatim from Hansen/Arnold/Auger §3.1: *"Rechenberg investigated two simple but quite different functions, the corridor function … and the sphere function …. He found optimal success rates for the (1+1)-ES with isotropic mutation to be ≈ 0.184 > 1/6 and ≈ 0.270 < 1/3, respectively (for n → infinity). This leads to approximately 1/5 as being the success value where to switch between decreasing and increasing the step-size."* Optimality here means *"the largest expected approach of the optimum in a single generation."*

**Do not write that 1/5 is the "average" of 0.184 and 0.270** — their mean is 0.227. The argument is that 1/5 *lies between* the two, bracketed as 1/6 < 0.184 and 0.270 < 1/3.

A pleasing corroboration from the same chapter: for large λ the optimal truncation ratio of the (μ/μ,λ)-ES is μ/λ = 0.27 with progress per offspring 0.202, and *"those values are identical to the optimal success probability and resulting normalized progress rate of the (1+1)-ES"* (Beyer's *The Theory of Evolution Strategies*, Springer 2001, for exactness). The optimal normalised step size of the (1+1)-ES is 1.224.

**The modern update convention** (Hansen/Arnold/Auger Algorithm 1):

```
given n,  d ≈ sqrt(n) + 1
σ  <-  σ · exp^(1/d)( 1{f(x_1) <= f(x)} − 1/5 )
```

so `log σ` is stationary iff the expected success indicator equals 1/5. Implementation credited to Kern, Müller, Hansen, Büche, Ocenasek & Koumoutsakos, *Natural Computing* 3(1):77–112, 2004. A similar rule was found independently earlier in **Schumer & Steiglitz, "Adaptive step size random search," *IEEE Trans. Automatic Control* 13(3):270–276, 1968.**

⚠️ **The multiplier c (0.817 or 0.85) and the 10n window could not be sourced anywhere.** Eiben & Smith's own slides give the rule with a *range* `0.8 ≤ c ≤ 1` and "every k iterations" with no k; Eiben, Hinterding & Michalewicz 1999 state it qualitatively with no constant. Suggestive but explicitly an inference, not a source: 1/1.224 = 0.8170, and 1.224 is the verified optimal normalised step size. To close this properly, check Schwefel 1977 / the 1981 Wiley translation / Bäck, *Evolutionary Algorithms in Theory and Practice* (Oxford 1996).

And state the scope honestly: **1/5 is derived from the optimal progress rate on the sphere and corridor models.** It is model-specific, not universal.

### Self-adaptation

Exact constants, read in Bäck & Hammel 1998 eq. (9) with **Schwefel 1995** as the attributed source:

```
σ'_i = σ_i · exp[ τ' · N(0,1) + τ · N_i(0,1) ]
x'_i = x_i + σ'_i · N_i(0,1)
```

*"Die Notation N_i(0,1) zeigt an, daß die Zufallszahlen für jede Komponente i neu gezogen werden. Für die sogenannten Lernraten tau', tau wird tau' ∝ 1/sqrt(2n) und tau ∝ 1/sqrt(2·sqrt(n)) empfohlen [Sch95]."*

Note these are **proportionalities (∝), not equalities**, and the attribution chain runs to Schwefel 1995, not to the paywalled Bäck & Schwefel 1993.

The single-σ log-normal update is verified twice: Beyer's eq. (I), `σ_l <- <σ> e^(τ N_l(0,1))`, with *"Empirical as well as theoretical investigations suggest to choose it proportional to 1/sqrt(n), e.g., tau = 1/sqrt(2n)"*; and Hansen/Arnold/Auger's (μ/μ,λ)-σSA-ES: *"given n, lambda >= 5n, mu ≈ lambda/4, tau ≈ 1/sqrt(n), tau_i ≈ 1/n^(1/4)."*

**Order matters.** Mutate σ **first**, then x — *"Reversing mutation order this would not work"* — because *"new sigma is evaluated twice — Primary: x' is good if f(x') is good; Secondary: sigma' is good if the x' it created is good."* Mutations are unbiased in that `E[log σ_k] = log σ`, but **Hansen, "An analysis of mutative σ-self-adaptation on linear fitness functions," *Evolutionary Computation* 14(3):255–275, 2006**, shows mutation plus recombination on σ *"introduces a moderate bias such that sigma tends to increase under neutral selection."*

**Correlated mutation** uses `n(n−1)/2` rotation angles, so chromosomes are `<x_1..x_n, σ_1..σ_n, α_1..α_k>`. Why it scales badly: **Rudolph (1992) showed adapting the full orientation requires a population size growing quadratically in n**, so it suits only small n; for smaller populations with similarly scaled variables, collapse to a single global σ. Hansen et al. attribute correlated mutations to Schwefel 1977. Derandomised self-adaptation (Ostermeier, Gawelczyk & Hansen 1994) is the bridge to CMA-ES.

### CMA-ES

- Hansen & Ostermeier, "Completely Derandomized Self-Adaptation in Evolution Strategies," *Evolutionary Computation* 9(2):159–195, 2001, doi:10.1162/106365601750190398.
- **Hansen, "The CMA Evolution Strategy: A Tutorial," arXiv:1604.00772** — v1 4 Apr 2016, v2 10 Mar 2023. Cite the version; everything below is from v2.

It samples `x_k = m + σ·B D z_k` with `z_k ~ N(0,I)`, i.e. from `N(m, σ² C)`, and adapts **both** a full covariance matrix C and a global step size σ by three mechanisms:

1. **Rank-μ update** — add the weighted empirical covariance of the μ selected steps, `c_μ · Σ_i w_i y_{i:λ} y_{i:λ}^T`. Learns the *shape* of successful steps but **throws away their sign**.
2. **Rank-one update from the evolution path** `p_c`, which cumulates consecutive steps: `p_c <- (1−c_c) p_c + h_σ sqrt(c_c(2−c_c) μ_eff) <y>_w`, then add `c_1 p_c p_c^T`. Consecutive correlated steps add up while anti-correlated ones cancel, so this is a momentum term that **recovers exactly the direction information the rank-μ update discards** — the single most important ingredient on ill-conditioned ridges.
3. **Cumulative step-size adaptation (CSA / path-length control)** — maintain a conjugate path `p_σ` and compare `‖p_σ‖` to its expectation under random selection. Too long ⟹ successive steps are correlated, so take bigger steps; too short ⟹ they are anti-correlated, so shrink. `σ <- σ·exp((c_σ/d_σ)(‖p_σ‖/E‖N(0,I)‖ − 1))`.

**Default parameters, verbatim from Table 1** (the 2016 setting, with negative recombination weights on by default — "active" CMA, aCMA-ES):

```
λ       = 4 + floor(3 ln n)                      "can be increased"
μ       = floor(λ/2) = |{w_i > 0}|
w'_i    = ln((λ+1)/2) − ln i,  i = 1..λ          (preliminary convex shape)
c_m     = 1
c_σ     = (μ_eff + 2) / (n + μ_eff + 5)
d_σ     = 1 + 2 max(0, sqrt((μ_eff−1)/(n+1)) − 1) + c_σ
c_c     = (4 + μ_eff/n) / (n + 4 + 2 μ_eff/n)
c_1     = α_cov / ((n+1.3)² + μ_eff),            α_cov = 2
c_μ     = min(1 − c_1, α_cov (1/4 + μ_eff + 1/μ_eff − 2) / ((n+2)² + α_cov μ_eff/2))
μ_eff   = (Σ_{i<=μ} w_i²)^{-1}
```

**Initial σ**, verbatim: *"The optimum should presumably be within the initial cube m ± 3 sigma (1,…,1)^T. If the optimum is expected to be in the initial search interval [a,b]^n we may choose the initial search point m, uniformly randomly in [a,b]^n, and sigma = 0.3(b−a)."* Note **0.3, i.e. ≈ range/3**, not the often-repeated "quarter of the range" — though pycma's docstring gives the 3σ₀ form, so range/4 to range/6 is also defensible.

Hansen's own guidance, verbatim: *"We do not recommend to change this setting, apart from increasing the population size lambda … and possibly decreasing alpha_cov on noisy functions."* And: *"Decreasing lambda is not recommended. Too small values have strong adverse effects on the performance."* Increasing λ *"usually improves the global search capability and the robustness of the CMA-ES, at the price of a reduced convergence speed"*, and *"The convergence speed (per function evaluation) decreases at most linearly with lambda."*

**Invariances are the real reason it works.** Invariant to strictly increasing transformations of f (only rankings are used); scale invariant; rotation invariant under orthogonal transformations given a suitably transformed initial mean, and under general linear transformations if C is chosen to match. Hence insensitive to ill-conditioning and non-separability. On a convex quadratic with Hessian H, C adapts toward `H^{-1}` up to a scalar — **proven only for μ = 1 on a static quadratic model** (Shir & Yehudayoff 2020).

**Cost**, verbatim from §B.2: *"In practice, the re-calculation of B and D needs to be done not until about max(1, floor(1/(10 n (c_1 + c_mu)))) generations. For reasonable c_1 + c_mu values, this reduces the numerical effort due to the eigendecomposition from O(n³) to O(n²) per generated search point."* A dated but concrete figure: *"On a Pentium 4, 2.5 GHz processor the overall strategy internal time consumption is roughly 3 × (n+5)² × 10^-8 seconds per function evaluation."* So memory and per-sample time are **O(n²)**, and plain CMA-ES becomes impractical somewhere in the hundreds-to-low-thousands of dimensions. Large-scale variants: sep-CMA-ES (Ros & Hansen, PPSN X 2008), LM-CMA (Loshchilov), VD-CMA/VkD-CMA (Akimoto & Hansen), Cholesky-factor variants.

**When CMA-ES is outperformed — and this list comes from the CMA-ES literature itself**, which is unusually candid:

| Regime | Better choice |
|---|---|
| n < 5 | downhill simplex, or surrogates such as kriging with expected improvement |
| separable functions, especially multimodal or high-dimensional | differential evolution; *"CMA-ES may fail to find comparable solutions"* |
| nearly convex-quadratic with low/moderate Hessian condition number | BFGS, NEWUOA, SLSQP — *"at least ten times faster"* |
| solvable within ≈ 10n evaluations | NEWUOA or Multilevel Coordinate Search |

The counterweight from the same source: Hansen et al., "Comparing results of 31 algorithms from the black-box optimization benchmarking BBOB-2009," GECCO 2010 Companion — CMA-ES outranked 31 other algorithms, especially on difficult functions and larger search spaces.

CMA-ES is designed for unimodal/moderately multimodal problems and **relies on restarts for rugged landscapes**: IPOP-CMA-ES (Auger & Hansen, "A Restart CMA Evolution Strategy With Increasing Population Size," CEC 2005, pp. 1769–1776, doi:10.1109/CEC.2005.1554902) and BIPOP-CMA-ES (Hansen, GECCO 2009 Companion).

**Natural evolution strategies / information geometry** is the bridge to the OpenAI-ES line (see `applications.md`): Wierstra, Schaul, Glasmachers, Sun, Peters & Schmidhuber, "Natural Evolution Strategies," *JMLR* 15:949–980, 2014; Akimoto, Nagata, Ono & Kobayashi, PPSN 2010; Ollivier, Arnold, Auger & Hansen, "Information-geometric optimization algorithms," *JMLR* 18:1–65, 2017. The content: **CMA-ES's updates coincide with, or closely approximate, natural gradient ascent on the parameters of the search distribution.**

---

## Evolutionary programming

Lawrence J. Fogel, from 1960/1962; the book is **L.J. Fogel, A.J. Owens & M.J. Walsh, *Artificial Intelligence through Simulated Evolution*, Wiley 1966**. The original object of evolution was **finite state machines used as sequence predictors**. Mutation only, **no recombination**, with a stochastic q-tournament survivor selection over the parent+offspring union. Later: David B. Fogel's extension to continuous parameter optimisation (*Evolutionary Computation: Toward a New Philosophy of Machine Intelligence*, IEEE Press 1995) and meta-EP/Rmeta-EP self-adaptation of variances. Fast EP with Cauchy mutation: Yao, Liu & Lin, "Evolutionary programming made faster," *IEEE TEVC* 3(2):82–102, 1999.

### The convergence claim, stated correctly

The authoritative source is **Bäck, Hammel & Schwefel, "Evolutionary computation: comments on the history and current state," *IEEE TEVC* 1(1):3–17, 1997**, doi:10.1109/4235.585888 (read in full).

**Important correction: this paper never uses the word "dialects," never claims mathematical equivalence, and never proposes a unified framework** (grep-verified for "dialect", "equivalenc", "unif").

What it *does* say is the load-bearing sentence (§IV-A): *"The actual development of the field is characterized by a progressing integration of the different approaches, such that the utilization of the common labels 'genetic algorithm,' 'evolution strategy,' and 'evolutionary programming' might be sometimes even misleading."*

But §IV still insists the three are distinguishable: *"As mentioned, at least three variants of evolutionary algorithms have to be distinguished …. Their main differences lie in: * The representation of individuals. * The design of the variation operators (mutation and/or recombination). * The selection / reproduction mechanism."* And §I: *"somewhat surprisingly, the researchers in the various disciplines of evolutionary computation remained isolated from each other until the meetings in the early 1990s."*

The specific technical near-equivalences it *does* assert:

- **ES ≈ EP self-adaptation.** Citing Beyer, EP's self-adaptation equation *"is obtained from the corresponding equation for evolution strategies with one self-adaptable step size by Taylor expansion breaking off after the linear term, such that both methods behave equivalently for small settings of the learning rates tau and phi, when tau = phi. This prediction was confirmed perfectly by an experiment."*
- **EP selection ≈ (μ+λ).** EP's q-tournament is *"a probabilistic version of (mu+lambda)-selection which becomes more and more deterministic as the number q of competitors is increased"* — the paper calls this *"a minor difference."*
- Both comma and plus are instances of `(μ, κ, λ)`.
- **"EP has no recombination" is called "a rash statement"**: *"a rash statement based on the common understanding of the contending structures as individuals would be to claim that evolutionary programming simply does not use recombination. Rather than focusing on the mechanism of sexual recombination, however, Fogel argues that one may examine and simulate its functional effect…"*
- GA selection operators are portable across all three, and *"self-adaptation has only recently been introduced in genetic algorithms"* — migration ran both ways.

**So write the claim as "the labels can mislead because the approaches have progressively integrated," not as "the dialects converged into one algorithm," and never as an equivalence result.** The one surviving *conceptual* difference: EP treats the phenotype/species as the unit of variation, so recombination is rejected **on principle** (there are no "genes" between which to recombine) rather than for measured performance. For real-valued optimisation, modern EP is in practice a (μ+μ) ES without recombination.

---

## Genetic programming

- **Koza, *Genetic Programming: On the Programming of Computers by Means of Natural Selection*, MIT Press 1992**, ISBN 0-262-11170-5, xiv+819 pp.
- Sequels: *GP II* (1994, automatically defined functions/ADFs); *GP III* (Morgan Kaufmann 1999, 1100 pp.); *GP IV: Routine Human-Competitive Machine Intelligence* (Kluwer 2003).
- Precursors: Cramer, ICGA 1985; Forsyth's BEAGLE; Friedberg 1958.
- **The free standard reference: Poli, Langdon & McPhee, *A Field Guide to Genetic Programming*, 2008**, ISBN 978-1-4092-0073-4, CC BY-NC-ND, with Koza as a contributing author. ⚠️ `gp-field-guide.org.uk` is HTTP-only and was unreachable; the working mirror is `http://www0.cs.ucl.ac.uk/staff/W.Langdon/ftp/papers/poli08_fieldguide.pdf`.

### Representation: closure and sufficiency

Expression trees over a **function set** and a **terminal set**. Both requirements below are Koza's own 1992 terms, quoted from the Field Guide §3.2.

**Closure** = *"type consistency and evaluation safety."*

- *Type consistency*: *"it is necessary that any subtree can be used in any of the argument positions for every function in the function set, because it is always possible that subtree crossover will generate that combination. It is thus common to require that all the functions be type consistent, i.e., they all return values of the same type, and that each of their arguments also have this type."*
- *Evaluation safety*: *"required because many commonly used functions can fail at run time. An evolved expression might, for example, divide by 0, or call MOVE FORWARD when facing a wall or precipice."* Hence protected operators — and the canonical protected division `%` returns **1** when the divisor is 0, deliberately: *"The decision to return the value 1 provides the GP system with a simple way to generate the constant 1, via an expression of the form (% x x). This combined with a similar mechanism for generating 0 via (- x x) ensures that GP can easily construct these two important constants."*

**Sufficiency**: *"Sufficiency means it is possible to express a solution to the problem at hand using the elements of the primitive set. Unfortunately, sufficiency can be guaranteed only for those problems where theory, or experience with other methods, tells us that a solution can be obtained by combining the elements of the primitive set."* Their examples: `{AND, OR, NOT, x1..xN}` is always sufficient for Boolean induction; `{+, −, *, /, x, 0, 1, 2}` is **insufficient** because it cannot represent `exp(x)`. Practical rider: *"Adding a few unnecessary primitives in an attempt to ensure sufficiency does not tend to slow down GP overmuch, although there are cases where it can bias the system in unexpected ways."*

**Strongly typed GP** is the alternative to closure's type-consistency demand: **Montana, "Strongly Typed Genetic Programming," *Evolutionary Computation* 3(2):199–230, 1995**, doi:10.1162/evco.1995.3.2.199 — *"in its standard form, there is no way to restrict the programs it generates to those where the functions operate on appropriate data types …. STGP is an enhanced version of genetic programming that enforces data-type constraints and whose use of generic functions and generic data types makes it more powerful than other approaches to type-constraint enforcement."*

### Koza's default tableau

⚠️ The 1992 book is lending-gated, but almost all of the tableau is verified from Koza's own later paper, which says its secondary parameters are *"the same default values as we have used on numerous other problems [Koza 1992a]"*: **Koza, "Genetic Programming as a Means for Programming Computers by Natural Selection," *Statistics and Computing* 4(2):87–112, 1994** (full PDF at `genetic-programming.com/jkpdf/scjournallong.pdf`, read in full). Verbatim:

> *"each new generation is created from the preceding generation by applying the fitness proportionate reproduction operation to 10% of the population and by applying the crossover operation to 90% of the population (with both parents selected with a probability proportionate to fitness). In selecting crossover points, 90% were internal (function) points of the tree and 10% were external (terminal) points of the tree. For the practical reason of avoiding the expenditure of large amounts of computer time on an occasional oversized programs, the depth of initial random programs was limited to 6 and the depth of programs created by crossover was limited to 17. … Spousal selection was also fitness proportionate."*

Verified: `p_c = 0.90`; reproduction 0.10; fitness-proportionate selection for both parents; max tree depth **17** for crossover offspring; max initial depth **6**; the 90%/10% internal/leaf crossover-point bias (also Field Guide p. 17: *"To counter this, Koza (1992) suggested the widely used approach of choosing functions 90% of the time and leaves 10% of the time"*); **51 generations** (*"N_gen was 51 throughout this article"*); ramped half-and-half initialisation (partially — Koza 1994 describes the effect, *"generated so as to obtain a wide variety of different sizes and shapes"*, without naming the method; the Field Guide names it as Koza's with the usual depth range 2–6).

⚠️ **Population 500 is NOT verified as a default — soften this.** Koza treats M as a *major, problem-specific* parameter: *"The two major parameters that are used to control the process are the population size M and the maximum number of generations N_gen."* The same paper uses 500, 1,000, 4,000, 8,000 and 10,000 on different problems. The 1990 precursor (Stanford CS TR-1314) standardises on **300**, max depth 15, max initial depth 4 — useful if you want to show the defaults *moving* between 1990 and 1992. The Field Guide says only *"normally, the population size should be at least 500."*

Koza's 1990 rationale for the 90/10 point bias: it *"promotes the recombining of larger structures than would be the case with a uniform distribution over all points (which may do an inordinate amount of mere swapping of terminals from tree to tree in a manner more akin to point mutation as opposed to true recombining of 'building block' substructures)."*

**The hardware**, from `genetic-programming.com/machine1000.html`: a *"1,000-Pentium Beowulf-Style Cluster Computer for Genetic Programming"* — *"a server and 1,000 Pentium II 350-MHz processors"*, all COTS, 64 MB RAM each (64 GB total), 1,000 CPUs on 500 dual-CPU Tyan Tiger 100 motherboards, no disk/monitor/keyboard, Red Hat Linux 6.0, run as a **25 × 40 toroidal grid island/deme model**. Capacity statement (not a run setting): *"A 1,000-node system can therefore accommodate a population of 10,000,000 3,000-byte individuals."* ⚠️ **GP IV reports results from more than one machine** (its ch. 17.1 lists both an Alpha and a Pentium system), so don't attribute the Pentium cluster to GP IV wholesale. The GP III-era Alpha machine: Bennett, Koza, Shipman & Stiffelman, GECCO 1999, pp. 1484–1490 — a *"10-node Beowulf-style parallel computer system for $18,000"*, each node a 533 MHz Alpha, *"sufficient to yield solutions (within a couple of days per problem) to 14 published problems."* ⚠️ GP III and GP IV population sizes are unverified.

### Bloat

**Definition** (Field Guide §11.3): *"very often the average size (number of nodes) of the programs in a population, after a certain number of generations in which it was largely static, at some point would start growing at a rapid pace. Typically the increase in program size was not accompanied by any corresponding increase in fitness."* And crucially: *"we should NOT equate growth with bloat and we should define bloat as program growth without (significant) return in terms of fitness."* Why it matters: *"large programs are computationally expensive to evolve and later use, can be hard to interpret, and may exhibit poor generalisation."*

**The constraint every theory must satisfy — the size evolution equation** (§11.3.1): `E[μ(t+1)] = Σ_l l·p(l,t)`, hence `E[μ(t+1) − μ(t)] = Σ_l l(p(l,t) − Φ(l,t))`, where μ is mean program size, `p(l,t)` the probability of **selecting** programs of size l and `Φ(l,t)` their **proportion**. Valid *"for a GP system with selection and any form of symmetric subtree crossover."* Consequence: *"for symmetric subtree-swapping crossover operators, the mean program size evolves as if selection only was acting on the population."* Derived from Poli's exact schema theory.

**The four theories:**

1. **Replication accuracy.** ⚠️ **Citation correction:** the theory the literature *calls* "replication accuracy" is attributed by the Field Guide to **McPhee & Miller, "Accurate Replication in Genetic Programming," ICGA95, pp. 303–309** — not to Blickle & Thiele or Nordin & Banzhaf: *"The replication accuracy theory (McPhee and Miller, 1995) states that the success of a GP individual depends on its ability to have offspring that are functionally similar to the parent. As a consequence, GP evolves towards (bloated) representations that increase replication accuracy."* The two commonly-cited papers are real and *are* about redundancy causing growth — cite them as the **intron/protective-code strand**: Blickle & Thiele, "Genetic Programming and Redundancy," MPI-I-94-241, pp. 33–38, 1994 (*"Empirical analyses show that large parts of those trees are never used or evaluated … explain the size problem"*; the authors' own mechanism, from the GP mailing list, 22 Mar 1995: *"more redundant trees have a higher probability to survive crossover"*), and Nordin & Banzhaf, "Complexity Compression and Evolution," ICGA95, pp. 310–317 — back-to-back pages with McPhee & Miller in the same volume.
2. **Removal bias.** Soule & Foster, IEEE ICEC 1998, pp. 781–786, doi:10.1109/ICEC.1998.700151. *"inactive code in a GP tree tends to be low in the tree, residing, therefore, in smaller-than-average-size subtrees. Crossover events excising inactive subtrees produce offspring with the same fitness as their parents. On average the inserted subtree is bigger than the excised one, so such offspring are bigger than average while retaining the fitness of their parent."*
3. **Nature of program search spaces.** *"predicts that above a certain size, the distribution of fitnesses does not vary with size. Since there are more long programs, the number of long programs of a given fitness is greater than the number of short programs of the same fitness. Over time GP samples longer and longer programs simply because there are more of them."* Langdon & Poli, "Fitness Causes Bloat," 1997/1998, doi:10.1007/978-1-4471-0427-8_2; Langdon, Soule, Poli & Foster, "The Evolution of Size and Shape," *Advances in GP 3*, 1999; Langdon & Poli, *Foundations of Genetic Programming*, Springer 2002.
4. **Crossover bias** — the most recent, and the technical claim checks out at three independent levels of source. Poli, Langdon & Dignum, EuroGP 2007, pp. 193–204, **EuroGP 2007 Best Paper**: *"standard sub-tree crossover with uniform selection of crossover points pushes a population of a-ary GP trees towards a distribution of tree sizes of the form Pr{n} = (1 − ap) C_n^{an+1} (1−p)^{(a−1)n+1} p^n."* Dignum & Poli, GECCO 2007, pp. 1588–1595, generalises it to mixed arities and shows *"a distinct bias towards the sampling of shorter programs"*, explicitly covering *"the traditional 0.90-function 0.10-terminal crossover node selection policy"* — **the result survives Koza's 90/10 bias.** The phrase "Lagrange distribution of the **second kind**" is verified in Dignum & Poli, EuroGP 2010, p. 42. The synthesis (Field Guide §11.3.1): *"On average, each application of subtree crossover removes as much genetic material as it inserts; consequently crossover on its own does not produce growth or shrinkage. While the mean program size is unaffected, however, higher moments of the distribution are. … crossover generates a very high proportion of single-node individuals. In virtually all problems of practical interest, however, very small programs have no chance of solving the problem. As a result, programs of above average size have a selective advantage over programs of below average size, and the mean program size increases."* A nice downstream consequence: seeding the initial population *with* the crossover-preferred distribution makes bloat **worse** — "Lagrange initialisation."

⚠️ **Which theory is best supported: none, and the Field Guide says so.** This is the most important correction in the GP material. Verbatim (§11.3): *"Over the years, many theories have been proposed to explain various aspects of bloat, and while great strides have been made, we still lack a single, universally-accepted unifying theory to explain the broad range of empirical observations."* It presents the first three as *"three of the oldest ones"*, notes *"The explanations for bloat provided by these three theories are largely qualitative"*, and introduces crossover bias as *"a recent explanation"* that *"is based on and is consistent with the size evolution equation"* — a statement of theoretical standing, not empirical victory. Poli & McPhee (GECCO 2008) are blunter: *"we still lack a single unifying theory to explain the broad range of empirical observations"*, and *"While the jury remains out on the causes of bloat, practitioners still have the practical problem of combating bloat in their runs."*

What you *can* say: crossover bias is the most recent of the four, the only one derived from and provably consistent with the exact size-evolution equation, and the one that generated a working control method. **Silva, Dignum & Vanneschi, "Operator equalisation for bloat free genetic programming and a survey of bloat control methods," *GPEM* 13(2):197–238, 2012**, doi:10.1007/s10710-011-9150-5, frames it that way: *"Particular attention is then given to the new Crossover Bias theory and the bloat control method it inspired, Operator Equalisation."* That is endorsement-by-emphasis from the survey of record — not "the winner."

### Parsimony-pressure remedies

**Size and depth limits, and the pathology of the naive implementation** (§11.3.2): *"Many implementations of this idea (e.g., (Koza, 1992)) apply a genetic operator and then check whether the offspring is beyond the size or depth limit… If the offspring exceeds the limit, ONE OF THE PARENTS IS RETURNED. Obviously, this implementation does not allow programs to grow too large. However, there is a serious problem… parent programs that are more likely to violate a constraint will tend to be copied (unaltered) more often than programs that don't. That is, the population will tend to be filled up with programs that nearly infringe the constraint."* Concretely: *"depth thresholds lead to the population filling up with very bushy programs … size limits produce populations of stringy programs."* Fixes: return the oversize offspring with fitness 0, or declare the operation failed and retry. Rule of thumb: *"estimate the size of the minimum possible solution… and add some percentage (e.g. 50-200%) as a safety margin."* ⚠️ The Field Guide does **not** mention the depth-17 limit anywhere (grep-verified).

**Linear parsimony pressure**: *"the new fitness function is f(x) − c·l(x), where l(x) is the size of program x … and c is a constant known as the PARSIMONY COEFFICIENT."* Cited to Koza 1992; Zhang & Mühlenbein 1993, 1995. Essential footnote: *"While the new fitness is used to guide evolution, one still needs to use the original fitness function to recognise solutions and stop runs."*

**Covariant parsimony pressure** — **Poli & McPhee, "Parsimony Pressure Made Easy," GECCO 2008, pp. 1267–1274**, doi:10.1145/1389095.1389340 (read in full). Absence of growth, `E[Δμ] = 0`, holds iff `Cov(l,g) = Cov(l,f)`; with `g = c(t)l(x)` this gives:

```
c(t) = Cov(l, f) / Var(l)
```

*"Note that c is a function of t because both numerator and denominator can change from generation to generation."* Power-law form: for `g = c(t)l(x)^k`, `c(t) = Cov(l,f)/Cov(l,l^k)`. A drift-*correcting* variant pulls mean size back to its initial value: `c(t) = [Cov(l,f) − (μ(0)−μ(t))f̄] / [Cov(l,l^k) − (μ(0)−μ(t))E[l^k]]`. The paper rewrites the size evolution equation *"in a form that shows its direct relationship to Price's theorem"*, giving `E[Δμ] = Cov(l,f)/f̄`, and demonstrates *"almost complete control over the dynamics of the mean program size … in a single generation."*

⚠️ **The caveat, verbatim:** *"while much of this theory assumes the use of fitness proportionate selection, Equation (6) is valid in general… As we will see in the experiments, however, the penalty coefficients estimated using the theory developed for fitness proportionate selection actually work very well without any modification in systems based on other forms of selection, such as tournament selection."* **The proof is for fitness-proportionate selection; the tournament result is empirical.**

**Lexicographic parsimony pressure** — **Luke & Panait, GECCO 2002, pp. 829–836**: *"Lexicographic parsimony pressure modifies selection to prefer smaller trees ONLY WHEN FITNESSES ARE EQUAL (or equal in rank). This technique is simple to implement and is not affected by specific differences in fitness values, but only by their relative ranking."* Variants in the paper: plain, **direct bucketing** and **ratio bucketing**. The Field Guide notes it is *"in fact a form of MOO with lexicographic ordering"* and credits Ryan (1994) alongside. ⚠️ **Citation correction: "double tournament" is NOT in the GECCO 2002 paper.** Luke & Panait, PPSN VII 2002, introduces *"Direct and Proportional Tournament"*; **double tournament** appears in Luke & Panait, "A Comparison of Bloat Control Methods for Genetic Programming," *Evolutionary Computation* 14(3):309–344, 2006 — the only systematic nine-way comparison, whose abstract reports *"the combination of depth limiting with such a punitive method is generally more effective than either alone"* and *"an unexpected winner in the cross-platform category."* ⚠️ The identity of that winner is unverified; only the abstract was read.

**The Tarpeian method** — Poli, EuroGP 2003, pp. 204–217: *"based on the idea of strategically and dynamically creating fitness 'holes' in the fitness landscape which repel the population. In particular we create holes by ZEROING THE FITNESS OF A CERTAIN PROPORTION OF THE OFFSPRING THAT HAVE ABOVE AVERAGE LENGTH. Unlike other methods where all individuals are penalised when length constraints are violated, here we randomly penalise only a fixed proportion."* Practical bonus: *"the programs whose fitness is zeroed are never executed, thereby speeding up runs."* Caution from Mahler, Robilliard & Fonlupt, EuroGP 2005: *"The results are contrasted, showing that it can either increase or reduce the generalization power of GP hypotheses, depending on the problem at hand. This suggest[s] that a blind use of TC is not safe."*

**Multi-objective size-vs-error** — *"recent methods also include the use of multi-objective optimisation to control bloat. This typically involves the use of a modified selection based on the Pareto criterion"* (Ekárt & Németh 2001; de Jong, Watson & Pollack 2001), with the Field Guide's own caution that *"without diversity enhancement (given by modern MOO methods)"* it does not work well.

**Operator equalisation** — the method crossover-bias theory directly motivated. Dignum & Poli, EuroGP 2008, pp. 110–121: *"a novel and simple technique, which we call Operator Equalisation, to control how GP will sample certain length classes … completely freeing GP from bloat."* Silva & Dignum, EuroGP 2009, pp. 159–170, adds *"the ability to automatically determine and follow the ideal length distribution for each stage of the run."* One-liner: **OpEq imposes a target distribution over program-length classes and accepts or rejects new individuals by which length bin they fall into**; the self-adaptive version derives the target each generation from the fitness observed in each bin. Silva et al. 2012 report GP using OpEq is *"essentially bloat free"*, and also note *"the unexpected effect of OpEq on overfitting."*

**Anti-bloat operators**: size-fair crossover and mutation (Langdon 2000; Crawford-Marks & Spector 2002) — *"the crossover point in the first parent is selected randomly … Then the size of the subtree to be excised is calculated. This is used to constrain the choice of the second crossover point so as to guarantee that the subtree chosen from the second parent will not be 'unfairly' big."* Also **hoist mutation** (Kinnear 1994 — the new subtree is drawn from *within* the subtree being removed, so the child is always smaller) and **shrink mutation** (Angeline 1996).

### GP variants

**Grammatical evolution** (Ryan, Collins & O'Neill, EuroGP 1998; O'Neill & Ryan, *IEEE TEVC* 5(4):349–358, 2001). A variable-length binary genome read as **8-bit codons**; the mapping expands the **leftmost** non-terminal, consuming one codon per choice via the **mod rule** `Rule = c % r`. *"Typically, eight bit codons are used, so each can encode 256 different choices (2^8), the number is moded by the number of legal choices. This results in a situation where every codon can legally be applied to every choice."* **Wrapping**: *"the individual is wrapped, that is, one starts reading from the start once more. There is an upper limit on the number of wrapping events, which, when exceeded an individual is aborted. This upper limit is usually set to ten, although newer algorithms in the Grammatical Evolution family don't employ wrapping"* — PonyGE2 (arXiv:1703.08535) confirms wrapping is **off by default** in modern implementations because it *"does come at the cost of introducing functional dependencies between codons that would not otherwise arise."* GE's "intrinsic polymorphism": the same codon value selects different productions depending on which non-terminal is current.

**The GE locality criticism needs three fixes.** Rothlauf & Oetzel, EuroGP 2006, pp. 320–330: *"the representation used in GE has problems with locality as many neighbouring genotypes do not correspond to neighbouring phenotypes. Experiments with a simple local search strategy reveal that the GE representation leads to lower performance FOR MUTATION-BASED SEARCH APPROACHES in comparison to standard GP representations."*

1. The performance claim is scoped to **mutation-based search with a simple local-search strategy** — not a general claim about GE with crossover.
2. The dominant measured effect is **redundancy, not jumping**: ⚠️ (second-hand via Medvet, EuroGP 2017) *"in 90% of cases a mutation does not change the phenotype and, in the remaining 10% of cases, a significant fraction corresponds to mutations causing heavy changes in the phenotype."* So ~90% neutral, most of the rest big jumps, almost no small phenotypic steps.
3. **Do not attribute "ripple" to Rothlauf & Oetzel, and do not attach it to mutation.** The ripple effect / ripple crossover is a **crossover** phenomenon named by the GE authors (Keijzer, Ryan, O'Neill, Cattolico & Babovic, EuroGP 2001; O'Neill, Ryan, Keijzer & Cattolico, *GPEM* 2003). What *is* true for mutation is **positional dependence**: because the mapping is leftmost-first, changing an early codon re-interprets every codon after it.
4. A follow-up from the same group complicates the headline — Thorhauer & Rothlauf, PPSN XIII 2014: *"Both standard GE and GP search operators suffer from low locality … Furthermore, THE LOCALITY OF STANDARD GE SEARCH OPERATORS IS HIGHER THAN THAT OF STANDARD GP SEARCH OPERATORS, which allows more focused search in GE."* **Do not present "GE has bad locality, GP has good locality" as settled.**

**Linear GP** (Brameier & Banzhaf, *Linear Genetic Programming*, Springer 2007). From Brameier's thesis abstract: *"linear genetic programming (LGP), a machine learning approach that evolves computer programs as SEQUENCES OF IMPERATIVE INSTRUCTIONS. Two fundamental differences to the more common tree-based variant (TGP) may be identified. These are the GRAPH-BASED FUNCTIONAL STRUCTURE of linear genetic programs, on the one hand, and the existence of STRUCTURALLY NONEFFECTIVE CODE, on the other hand."* Programs are register-machine instruction sequences; data flow through registers makes the *effective* program a DAG rather than a tree; and instructions whose results are never read are **structurally** non-effective introns, detectable and removable in linear time — which is why LGP is the natural setting for intron and neutral-variation studies.

**Cartesian GP** (Miller & Thomson, EuroGP 2000; best readable source: **Miller, "Cartesian genetic programming: its status and future," *GPEM* 21(1–2):129–168, 2020**, doi:10.1007/s10710-019-09360-6, open access, read in full). A grid of `n_c` columns × `n_r` rows, `n_n = n_c·n_r` computational nodes. Each node carries a function index plus connection genes that are **integer addresses**: *"The program data inputs are given the absolute data addresses 0 to n_i − 1… The data outputs of nodes in the genotype are given addresses sequentially, column by column."* Arity is the max over the function table; surplus genes *"are ignored."* *"Nodes in columns cannot be connected to each other"*, and the graph is *"directed and feed-forward."* **Levels-back** `l` *"constrains which columns a node can get its inputs from. If l = 1, a node can get its inputs only from a node in the column on its immediate left or from a primary input… If one wishes to allow nodes to connect to any nodes on their left, then l = n_c."* With `n_r = 1` and `l = n_c`, *"the genotype can represent any bounded directed graph."* **Fixed genotype length** `L_cgp = n_n(a+1) + n_o`.

The neutrality point, verbatim: *"Non-coding genes arise in CGP when the outputs of nodes are not referenced in the flow of data from program inputs to program outputs. It is this which leads to both variable length phenotypes and EVOLUTIONARY NEUTRAL DRIFT in the genotype."* Standard CGP searches with a 1+λ ES in which *"An offspring that has a fitness BETTER OR EQUAL to the parent becomes the new parent"* — the "or equal" is precisely what permits neutral drift.

Evidence that neutrality helps, and the headline number: **Miller & Smith, "Redundancy and Computational Efficiency in Cartesian Genetic Programming," *IEEE TEVC* 10(2):167–174, 2006**: *"It has been demonstrated that this junk has a useful role and is very beneficial in evolutionary search. … It is found that THE MOST EVOLVABLE REPRESENTATIONS OCCUR WHEN THE GENOTYPE IS EXTREMELY LARGE AND IN WHICH OVER 95 PERCENT OF THE GENES ARE INACTIVE."* Also Miller & Thomson 2000 on the Santa Fe ant (*"The neutral search proves to be much more effective"*) and Vassilev & Miller, ICES 2000, on the three-bit multiplier.

**Four caveats so that claim does not read as naive** (all from Miller 2020): **not monotone** — Turner et al. *"found that the relationship was approximately QUADRATIC with a clear optimum value for n_n. Often the optimum number of nodes was quite large (hundreds or thousands of nodes)"*; **why it helps is contested** — Goldman & Punch *"suggested also that the advantage of large amounts of inactive nodes is purely that they provide mutation with random nodes for exploratory purposes"*, consistent with *"the author's unpublished finding that randomising inactive genes prior to mutation appears not to cause any performance impact"*; **a domain where it does not help** — Vašíček's "zero neutrality" result on 100 industrial-sized circuit problems was *"statistically indistinguishable"* from standard CGP, which Miller calls *"the surprising result that there is no need to utilise inactive nodes in CGP when optimising fully functional digital circuits!"*; and **the neutral-drift explanation for CGP's lack of bloat has been disproved** — *"when NGD is disallowed in CGP bloat still does not occur."*

**PushGP** (Spector & Robinson, *GPEM* 3(1):7–40, 2002): *"PushGP is a genetic programming system that evolves Push programs to solve computational problems. Pushpop, an autoconstructive evolution system, also evolves Push programs but does so while simultaneously evolving its own evolutionary mechanisms."* "Stack-based" is verified (Helmuth & Spector, GECCO 2013 Companion). ⚠️ The finer detail — multiple separately typed stacks including a CODE stack that makes Push self-modifying — is unverified.

**Geometric semantic GP** (**Moraglio, Krawiec & Johnson, PPSN XII, pp. 21–31**, doi:10.1007/978-3-642-32937-1_3, read in full). Definitions verbatim: *"A search operator CX is a GEOMETRIC crossover w.r.t. the metric d if for any choice of parents p1 and p2, any of their offspring o = CX(p1,p2) is in the metric SEGMENT between parents. A search operator M is a GEOMETRIC epsilon-mutation w.r.t. d if for any choice of the parent p, any of its offspring o = M(p) is in the metric BALL of radius epsilon centered in the parent."* Semantic distance is `SD(h1,h2) = D(O(h1),O(h2))` over the training-case output vectors; note **SD is only a pseudometric**.

**The cone-landscape claim**, verbatim: *"The semantic fitness landscape seen by an evolutionary algorithm with semantic geometric operators has a nice shape by construction: from the definition of semantic distance, the fitness of a solution is its distance in the search space to the optimum (CONE LANDSCAPE). This observation is remarkably general, as it holds for any domain of application of GP … and for any choice of metric for the error function."* For Boolean functions *"semantic GP search is equivalent to GA search on binary strings on ONEMAX of dimension N."* Moraglio's own code README: *"The fitness landscape seen by Geometric Semantic operators is always unimodal. A hill climber can reach the optimum."*

**Precision fix on the operator** (Definition 2, verbatim): *"Given two parent functions T1, T2: R^n → R, the recombinations SGXE and SGXM return the real function T3 = (T1*TR) + ((1−TR)*T2) where TR is a random real CONSTANT in [0,1] (SGXE), or a random real FUNCTION with codomain [0,1] (SGXM)."* Theorem 2: SGXE and SGXM are geometric for **Euclidean** and **Manhattan** distances respectively — random constant → Euclidean, random function → Manhattan. Boolean: `T3 = (T1 AND TR) OR (NOT TR AND T2)`, geometric w.r.t. Hamming. Quotable line: *"the offspring is not only the effect of crossover, it is also the description of how to crossover its parents."*

**The drawback and its exact rate.** From §3 "Simplification": *"As the syntax of the offspring of semantic crossover contains both parents, THE SIZE OF INDIVIDUALS GROWS EXPONENTIALLY WITH THE NUMBER OF GENERATIONS."* The rate, from Martins et al., GECCO 2018, arXiv:1804.06808: *"the geometric semantic mutation and crossover operators induce, respectively, LINEAR and EXPONENTIAL growth"*, with `E[GSX_E, g] = 2^g E[P0] + (2^g − 1)b` — **size doubles every generation** under geometric semantic crossover.

The standard remedy (Vanneschi, Castelli, Manzoni & Silva, EuroGP 2013): *"these operators, by construction, always produce offspring that are larger than their parents, causing an exponential growth in the size of the individuals, WHICH ACTUALLY RENDERS THEM USELESS IN PRACTICE. In this paper we overcome this limitation by presenting a new efficient implementation"* — store **pointers** to the parent trees and compute semantics from parents' values. **Caveat worth carrying:** *"if we want to access the final individual or if new data is presented after the training stage, an assembling step is needed to generate the complete individual from the pointers, which still presents an exponential size."* The remedy makes GSGP **runnable**; it does **not** make the model small or interpretable.

**Lexicase selection** (Spector, GECCO 2012 Companion; **Helmuth, Spector & Matheson, "Solving Uncompromising Problems With Lexicase Selection," *IEEE TEVC* 19(5):630–643, 2015**, read in full). Mechanism, verbatim from Fig. 1:

```
1) Initialize:
   a) Set `candidates` to be the entire population.
   b) Set `cases` to be a list of all of the test cases IN RANDOM ORDER.
2) Loop:
   a) Set `candidates` to be the subset of the current `candidates` that have
      EXACTLY THE BEST PERFORMANCE of any individual currently in `candidates`
      for the first case in `cases`.
   b) If `candidates` contains just a single individual then return it.
   c) If `cases` contains just a single test case then return a RANDOMLY SELECTED
      individual from `candidates`.
   d) Otherwise remove the first case from `cases` and go to Loop.
```

⚠️ **Discrepancy:** Spector's 2012 Fig. 1 returns *"the FIRST individual in candidates"*; Helmuth et al. 2015 and La Cava et al. 2016 return a **random** one. If you say "pick randomly," cite 2015/2016, not 2012.

Cost (La Cava 2016 §2): *"a theoretical worst-case time complexity of O(|P|² N), compared to O(|P| N) for tournament selection… this worst-case complexity is only reached if every individual passes every test case during selection; in practice, lexicase selection normally uses a small number of cases for each selection and therefore incurs only a small amount of overhead."*

**The target class.** An *"uncompromising problem"* is one *"for which any acceptable solution must perform as well on each test case as it is possible to perform on that test case; that is… it is not acceptable for a solution to perform sub-optimally on any one test case in exchange for good performance on others."* Four problems, with results: discriminator terms in finite algebras — *"sets of runs using lexicase selection succeeded nearly 100% of the time whereas runs using tournament selection, with tournament sizes ranging from 2 to 10, succeeded between 0% and 26% of the time"*; 3-bit digital multiplier (PushGP, population 5,000, 100 runs/condition) — lexicase success rate **1.0**, **every** tournament condition **0**, Fisher's exact p < 0.0001; factorial — lexicase 0.51, all others 0 except one at 0.01; Unix `wc` — lexicase 0.055, all others 0, with their own hedge *"the effect … is likely small but nonetheless meaningful, particularly since it appears to be difference between 'no successes' and 'occasional successes.'"* Cost (Table IX): lexicase slowest per generation everywhere — ~2× tournament on finite algebras, up to ~3× on `wc`, ~7× on the 3-bit multiplier at population 5,000 — *"But many of the lexicase runs actually finished faster than the other runs, since they found successful programs earlier."*

Why it preserves diversity: *"Lexicase selection may select individuals that perform very poorly on some test cases if they excel on a combination of others. As such, lexicase often selects 'SPECIALIST' individuals that solve parts of the problem extremely well."* A sharp detail from Spector's Table 1 (5 individuals, 4 cases): every individual is Pareto-elite, yet selection probabilities are 0.250, **0.000**, 0.333, 0.208, 0.208 — **one Pareto-elite individual has zero chance of selection**; *"it samples the subset of the population's Pareto front that has the best fitness value in the population with respect to at least one fitness case. But it does not do so with a uniform distribution."* Honest negatives the authors report: *"we have yet to find a biasing scheme that outperforms the standard form of lexicase selection"*, and *"we do not expect lexicase selection to provide a 'free lunch' over all problems (even all uncompromising problems)."*

**ε-lexicase for continuous errors** (La Cava, Spector & Danai, GECCO 2016, pp. 741–748 — read via arXiv:1905.13266, a **corrected** version whose own footnote reads *"Equations 2 and 5 have been corrected to indicate that the pass conditions … are defined relative to the best error IN THE POPULATION on that training case, NOT IN THE SELECTION POOL"*; and La Cava, Helmuth, Spector & Moore, *Evolutionary Computation* 27(3):377–402, 2019). Why needed: plain lexicase *"fails to produce such benefits when applied to continuous symbolic regression problems, due to its method of selecting test case elitism"* — requiring `e_t(i) = e*_t` exactly is far too stringent when *"exact solutions to test cases can only be expected for synthetic problems."* The fix uses the **median absolute deviation**: *"Given the high sensitivity of sigma to outliers, however, we opt for a more robust estimation of variability by using the median absolute deviation (MAD)"*, giving `e_t(i) < e*_t + λ(e_t)`. Rationale: *"As the performance on each training case improves across the population, epsilon SHRINKS, thereby modulating the selectivity of a case based on how difficult it is."* The 2019 paper adds three implementations — *"static, which is the version originally proposed; semi-dynamic, in which the elite error is defined relative to the current selection pool; and dynamic, in which both the elite error and epsilon are defined relative to the current selection pool"* — derives *"an analytical formula that gives the expected probabilities of selection"*, and shows lexicase *"select[s] individuals on the boundaries of Pareto fronts in high-dimensional space."*

### Symbolic regression: the current state of the art

**La Cava, Orzechowski, Burlacu, de França, Virgolin, Jin, Kommenda & Moore, "Contemporary Symbolic Regression Methods and their Relative Performance," NeurIPS 2021 Datasets and Benchmarks Track, arXiv:2107.14351** (read in full). *"We assess 14 symbolic regression methods and 7 machine learning methods on a set of 252 diverse regression problems."* Split: 122 black-box problems from PMLB v1.0 (21 algorithms, 5-fold halving grid-search CV, *"47 to 1 million instances, and two to 124 features"*, including *"46 'real-world' problems"*) and 130 ground-truth problems from the Feynman database and the ODE-Strogatz repository.

**Black-box result**, verbatim: *"the models generated by OPERON are significantly more accurate than any other method's models in terms of test set R² (p <= 6.5e-05). SBP-GP and FEAT rank second and third …. We note that FOUR OF THE TOP FIVE METHODS (Operon, SBP-GP, FEAT, EPLEX) AND SIX OF THE TOP TEN METHODS (GP-GOMEA, ITEA) ARE GP-BASED SR METHODS. The other top methods are ensemble tree-based methods, including … XGBoost and LightGBM; Random Forest; and AdaBoost… Operon, FEAT and SBP-GP significantly outperform LightGBM (p <= 1.3e-07) and Operon and SBP-GP outperform XGBoost (p <= 1.3e-04)… the models produced by the top five SR methods (aside from SBP-GP) are 1-3 ORDERS OF MAGNITUDE SMALLER than models produced by the ensemble tree-based approaches."* The accuracy-vs-simplicity Pareto front *"is composed of three methods: Operon, GP-GOMEA, and DSR."*

**Ground-truth result, with the noise caveat**, verbatim: *"On average, when the target is free of noise, we observe that AIFeynman identifies exact solutions 53% of the time, nearly twice as often as the next closest method (GP-GOMEA, 27%). However, AT NOISE LEVELS ABOVE 0.01, FOUR OTHER METHODS RECOVER EXACT SOLUTIONS MORE OFTEN: DSR, gplearn, AFP_FE, and AFP. Taken together … AIFeynman may be brittle in application to real-world and/or noisy data …. We note that the best method on real-world data, Operon, struggles to recover solutions to these problems, despite finding many candidate solutions with near perfect test set scores."*

Their own headline: *"the best performing methods for real-world regression combine genetic algorithms with parameter estimation and/or semantic search drivers. When tasked with recovering exact equations in the presence of noise, we find that deep learning and genetic algorithm-based approaches perform similarly."*

**SRBench is alive and has a newer edition.** `github.com/cavalab/srbench`, 333 stars, not archived, last push 2026-10-15. It now advertises **"SRBench 2025": 25 SR methods, Docker containers, hyperparameter tuning, 30 independent runs per dataset** over 24 PMLB datasets plus first-principles problems, including all 14 original methods. It labels the 2021 NeurIPS edition "v2.0" and Orzechowski, La Cava & Moore (GECCO 2018) "v1.0". Cite the current edition as Imai Aldeia, Zhang, Bomarito, Cranmer, Fonseca, Burlacu, La Cava & de França, "Call for Action: towards the next generation of symbolic regression benchmark," GECCO 2025 Companion, pp. 2529–2538, doi:10.1145/3712255.3734309. **The site says the 2025 edition should be used for choosing baselines, while the project website still displays the 2021 results** — so quote 2021 numbers with that caveat.

**GECCO SRBench competitions, 2022 and 2023 both exist.** 2022 "Interpretable Symbolic Regression for Data Science," Boston, 13 official competitors, 9 after filtering, two tracks; the real-world track required interpretable models forecasting 14-day COVID-19 counts in New York State with a subject expert assigning *"trust ratings"*. Synthetic: 1. QLattice (6.23), 2. PySR (5.26), 3. uDSR (4.67). Real-world: 1. uDSR (5.75), 2. QLattice (5.21), 3. geneticengine (4.99). Report: de França et al., arXiv:2304.01117. 2023: Track 1 Performance (10 entrants) — 1. **TPSR** (6.308), 2. NewTonSR++ (6.225), 3. RILS (6.136); Track 2 Interpretability (4 entrants) — 1. SR-Forest (3.25), 2. PFGP (2.83), 3. gplearn (2.25). **Pattern worth remarking: PySR and QLattice dominated 2022 while a transformer-based method topped 2023's performance track.**

**PySR** (Cranmer, arXiv:2305.01582): *"PySR's internal search algorithm is a MULTI-POPULATION EVOLUTIONARY ALGORITHM, which consists of a unique evolve-simplify-optimize loop, designed for optimization of unknown scalar constants in newly-discovered empirical expressions. PySR's backend is the extremely optimized Julia library SymbolicRegression.jl … capable of fusing user-defined operators into SIMD kernels at runtime, performing automatic differentiation, and distributing populations of expressions to thousands of cores across a cluster."* Current version **PySR 2.7.2, released 2026-10-19**, requires Python ≥ 3.10.

**Eureqa**: Schmidt & Lipson, "Distilling Free-Form Natural Laws from Experimental Data," *Science* 324(5923):81–85, 2009, doi:10.1126/science.1165893.

### Koza's "human-competitive results," and how they held up

The counts are now pinned precisely, from **Koza, "Human-competitive results produced by genetic programming," *GPEM* 11:251–284, 2010**, doi:10.1007/s10710-010-9112-3, open access:

- **76** human-competitive instances in Table 1. The text notes the table has **77 items** because one award is subsumed. *(This resolves the 76-vs-77 discrepancy that circulates, e.g. on Wikipedia, which gives both.)*
- **31** instances recognised by the Human Competitive Awards ("Humies") programme, which has run since 2004.
- **31** instances that duplicated, infringed or created patentable inventions — **1 from the 19th century, 21 from the 20th, 7 from the 21st, and 2 patentable new inventions**.

**The counts grew across editions, so attribute each number to its own source.** GP IV's 2003 blurb claims *"15 instances where GP has created an entity that either infringes or duplicates the functionality of a previously patented 20th-century invention, 6 instances … with respect to post-2000 patented inventions, 2 instances where GP has created a patentable new invention, and 13 other human-competitive results."* GP III's blurb cites 14 human-competitive results and 10 patent rediscoveries.

**The honest assessment.** GP is a real and in places leading tool in symbolic regression (the SRBench evidence is strong — four of the top five black-box methods are GP) and in heuristic design (FunSearch and AlphaEvolve are, structurally, GP with an LLM as the variation operator — see `applications.md`). But the "automated invention machine" framing did not become mainstream engineering practice, and **the patent-rediscovery claims rest on a counting exercise by the method's own principal advocate rather than on independent engineering adoption**. The field's own retrospective is O'Neill, Vanneschi, Gustafson & Banzhaf, "Open issues in genetic programming," *GPEM* 11:339–363, 2010. Note also the critique pattern that recurs in `applications.md`: where GP-produced artefacts *were* independently scrutinised — GenProg's patches — most turned out to be functionality deletion.

---

## Differential evolution

- **Storn & Price, "Differential Evolution — A Simple and Efficient Heuristic for Global Optimization over Continuous Spaces," *Journal of Global Optimization* 11(4):341–359, 1997**, doi:10.1023/A:1008202821328. Earlier: ICSI TR-95-012, Berkeley, 1995.
- Price, Storn & Lampinen, *Differential Evolution: A Practical Approach to Global Optimization*, Springer 2005, doi:10.1007/3-540-31306-0.
- Das & Suganthan, "Differential Evolution: A Survey of the State-of-the-Art," *IEEE TEVC* 15(1):4–31, 2011, doi:10.1109/TEVC.2010.2059031; updated as Das, Mullick & Suganthan, *SWEVO* 27:1–30, 2016. ⚠️ Both closed access; contents unverified.

### DE/rand/1/bin, exactly

For each target vector `x_i` in a population of NP:

1. pick distinct random indices `r1, r2, r3`, all ≠ i
2. **mutation (difference vector)**: `v = x_r1 + F·(x_r2 − x_r3)`
3. **binomial crossover**: draw `j_rand` uniformly from `{1..D}`; for each component j, `u_j = v_j` if `rand_j < CR` or `j = j_rand`, else `u_j = x_{i,j}`. The forced index guarantees `u` differs from `x_i` in at least one component.
4. **greedy one-to-one selection**: `x_i <- u` iff `f(u) <= f(x_i)`

Constraints: `NP >= 4`, `CR in [0,1]`, `F in [0,2]`. Typical settings quoted: `NP = 10n`, `CR = 0.9`, `F = 0.8`.

### The DE/x/y/z convention

`x` = base-vector selection scheme; `y` = number of difference vectors; `z` = crossover type. Vocabulary from a source actually read — **Tanabe & Fukunaga, "Reviewing and Benchmarking Parameter Control Methods in Differential Evolution," *IEEE Trans. Cybernetics*** §II: *"eight representative mutation strategies for DE (rand/1, rand/2, best/1, best/2, current-to-rand/1, current-to-best/1, current-to-pbest/1, and rand-to-pbest/1)"*; *"The scale factor F … controls the magnitude of the differential mutation."* On z: *"Binomial crossover (bin) and exponential crossover (exp) are most commonly used in DE. However, THE PERFORMANCE OF A DE ALGORITHM USING EXPONENTIAL CROSSOVER SIGNIFICANTLY DEPENDS ON THE ORDERING OF VARIABLE INDICES. Shuffled exponential crossover (sec), which applies exponential crossover after shuffling the variable indices of parent individuals, addresses this issue."* That last clause is independently useful: a published statement that **exponential crossover is coordinate-order dependent**, the same family of objection as the rotational-invariance point below.

⚠️ Cite Das & Suganthan 2011 and Price/Storn/Lampinen 2005 as the standard references for the convention, but put **no quotation marks** around anything attributed to them — neither was readable.

### Why DE works

The difference vectors are drawn **from the population itself**, so the mutation distribution's scale and orientation automatically track the population's current spread and correlation structure — self-referential, contour-matching step sizes with no explicit adaptation machinery and nothing to schedule. As the population converges, the difference vectors align with the landscape's principal directions. **This is the whole trick, and it is why DE is close to parameter-free in practice.**

### The CR direction question — settled, and usually stated backwards

**High CR (≈0.9–1.0) for non-separable / rotated / parameter-dependent problems; low CR for separable ones.**

Two independent routes:

**(a) The mechanism follows from the operator definition**, so it needs no paywalled source. Binomial crossover copies each component of the mutant with probability CR (plus one forced), so the expected number of changed coordinates is ≈ `CR·D + 1`.

- `CR → 0`: the trial differs from its parent in ≈ one coordinate, so the search takes **axis-aligned, coordinate-wise steps** — right for separable/decomposable objectives.
- `CR → 1`: nearly all coordinates change together, so the step is essentially the full difference vector — needed for non-separable objectives with correlated/rotated variables, where axis-aligned moves cannot follow the valley. **At CR = 1 there is effectively no crossover and the trial vector IS the mutant, restoring full rotational invariance.**

**(b) An explicit published statement.** ⚠️ Novák, Bezděk, Zelinka, **Das** & Beseda, "A Longitudinal Analysis of the CEC Single-Objective Competitions (2010–2024)…," arXiv:2603.24140, §3.2 — note that Swagatam Das, co-author of the DE survey, is an author here, which makes it about as close to the survey's own position as reachable. **It is an unrefereed preprint.** Verbatim: *"The defining characteristic of the CEC 2014 suite was the widespread application of DENSE ROTATION MATRICES … DESTROYING SEPARABILITY … THIS LED TO REDUCED EFFECTIVENESS OF COORDINATE-WISE SEARCH STRATEGIES. … DIFFERENTIAL EVOLUTION EMERGED AS THE DOMINANT PARADIGM IN THIS PHASE PRIMARILY BECAUSE ITS DIFFERENCE VECTOR MUTATION IS ROTATIONALLY INVARIANT. This invariance is not merely a static property but a dynamic one: as the population converges, the difference vectors naturally align with the principal eigen-directions of the landscape's contour. … WHILE THE BINOMIAL CROSSOVER TYPICALLY BREAKS THIS INVARIANCE by swapping parameters along axis-aligned coordinates, the success of the L-SHADE lineage stems from its ability to ADAPTIVELY SAMPLE CROSSOVER RATES (CR) NEAR 1.0."*

Supporting: the same source's CEC 2010 LSGO ranking table lists two baselines, *"Classic DE (CR=0.9)"* at rank 9 and *"Classic DE (CR=0.0)"* at rank 10 — **the organisers themselves treated CR as the one knob worth varying.** And from the L-SHADE paper on the low-CR end: locking CR to 0 *"caus[es] the algorithm to enforce a 'change-one-parameter-at-a-time' policy, which tends to slow down convergence, and is effective on multimodal problems."*

⚠️ The paper usually cited for the explicit numeric bands (separable `CR ∈ [0, 0.2]`; non-separable `CR ∈ [0.9, 1]`) is Rönkkönen, Kukkonen & Price, CEC 2005, pp. 506–513 — **its text could not be read**, so state the direction and mechanism from the above and say the specific bands are the DE literature's conventional advice rather than a quotation. Also: **Pedersen, "Good Parameters for Differential Evolution," Hvass Laboratories HL1002, 2010, is effectively lost** — its URL 404s, it is in neither Crossref nor Semantic Scholar, and its (NP, F, CR) tuples are unverified. Storn's own parameter page is also dead.

### Modern adaptive DE — reach for these rather than hand-tuning

**jDE** (Brest, Greiner, Bošković, Mernik & Žumer, *IEEE TEVC* 10(6):646–657, 2006). Each individual carries its own `F_i` and `C_i`; at t = 1 all are F = 0.5, C = 0.9; each generation `F^trial_i = randu[0.1, 1]` if `randu[0,1] < τ_F` else `F_i`, and likewise for C, with *"tau_F = tau_C = 0.1 is the recommended setting"*; and *"When the trial is a success, each individual uses F^trial and C^trial in the next iteration… Otherwise, each individual keeps using F_i and C_i."* **That is the whole of jDE: parameters ride along with the individual, are randomly re-rolled with probability 0.1, and the roll survives only if it produced an improvement.** No meta-parameters to learn.

**JADE** (Zhang & Sanderson, *IEEE TEVC* 13(5):945–958, 2009). Three mechanisms:

1. **current-to-pbest/1**: `v_i = x_i + F_i(x_pbest − x_i) + F_i(x_r1 − x_r2)`, where `x_pbest` is *"randomly selected from"* the top p fraction — so p trades off greediness; `p → 1/NP` recovers current-to-best/1.
2. **The optional archive of inferior solutions**, verbatim from the L-SHADE paper: *"Parent vectors x_i,G which were worse than the trial vectors u_i,G (and are not selected for survival in the standard DE) are preserved. When the archive is used, x_r2,G … is selected from P ∪ A …. Whenever the size of the archive exceeds the predefined archive size |A|, randomly selected elements are deleted."* So the archive supplies **historically defeated** solutions as the second difference-vector term, widening the direction distribution without slowing convergence.
3. **Cauchy for F, normal for CR**: *"two adaptive meta-parameters mu_F in (0,1] and mu_C in [0,1] … both initialized to 0.5 … F_i,t = randc(mu_F, 0.1) and C_i,t = randn(mu_C, 0.1). When F > 1 it is truncated to 1. When F <= 0, the new F is repeatedly generated… successful F and C are stored into sets S_F and S_C … mu_F = (1−c) mu_F + c mean_L(S_F) and mu_C = (1−c) mu_C + c mean_A(S_C)"*, `mean_L` the **Lehmer** mean. So **F is drawn from a heavy-tailed Cauchy** (preserving the chance of a big jump) with its location updated by the Lehmer mean (which biases toward larger successful F), CR from a normal with an arithmetic mean, both with exponential forgetting at rate c. `c = 0.1` is verified; ⚠️ the `p = 0.05` default is not, though 0.2 is verified as the maximum of the suggested range.

**SHADE** (Tanabe & Fukunaga, CEC 2013, pp. 71–78). *"SHADE 1.1 maintains a HISTORICAL MEMORY WITH H ENTRIES for both of the DE control parameters CR and F, M_CR, M_F… In the beginning, the contents … are all initialized to 0.5. In each generation G, the control parameters CR_i and F_i used by each individual x_i are generated by RANDOMLY SELECTING AN INDEX r_i FROM [1, H]."* Update uses the **weighted Lehmer mean** with weights `w_k = Δf_k / Σ_l Δf_l` and `Δf_k = |f(u_k) − f(x_k)|` — **the size of the fitness improvement weights how much each success counts.** The write index cycles 1..H; *"when all individuals in generation G fail … the memory is not updated."* There is also a terminal value ⊥: once set, CR locks to 0 *"until the end of the search,"* which is *"effective on multimodal problems."* So **SHADE = JADE's distributions, but with a bank of H remembered successful settings sampled at random instead of a single running mean**, which lets diverse parameter regimes coexist. Verified settings: N = H = 100; per-individual greediness `p_i = rand[p_min, 0.2]` with `p_min = 2/N`; the H sweep found 30 and 50 slightly better than 100, {5,10} roughly equivalent, monotone degradation above 100.

**L-SHADE** (Tanabe & Fukunaga, CEC 2014, pp. 1658–1665, read in full). **Linear population size reduction (LPSR)**:

```
N_{G+1} = round[ ((N^min − N^init) / MAX_NFE) · NFE + N^init ]
```

*"N^min is set to the smallest possible value such that the evolutionary operators can be applied — in the case of L-SHADE, N^min = 4 because the current-to-pbest mutation operator requires 4 individuals. … Whenever N_{G+1} < N_G, the (N_G − N_{G+1}) worst-ranking individuals are deleted."* **Note the schedule is driven by function evaluations consumed, not generations** — budget-aware by construction. It is *"a simplified, special case of Simple Variable Population Sizing"* with τ = 1, ρ = 0.

Parameters, from Table II (ParamILS-tuned; defaults in parentheses):

| Parameter | Range | Default | Tuned |
|---|---|---|---|
| `r^{N_init}` (N^init = round(D·r)) | 15–25 | 20 | **18** |
| `r_arc` (\|A\| = round(N^init·r_arc)) | 1.0–3.0 | 2.0 | **2.6** |
| `p` (current-to-pbest/1) | 0.05–0.15 | 0.1 | **0.11** |
| `H` (historical memory size) | 2–10 | 5 | **6** |

Evaluated on all 30 CEC2014 functions at D = 10, 30, 50, 100, budget D × 10,000, 51 runs. **An honest caveat the paper itself reports:** its ablation against a deterministic-step variant shows *"L-SHADE clearly outperforms D-SHADE for 10 and 30 dimensions. However, L-SHADE performs similarly to D-SHADE for D = 50 and is outperformed for 100"* — **linear is not universally the best reduction schedule.**

**L-SHADE is also a model of tuning honesty, and the disclosure pattern is worth copying** (see `practice.md`): the authors state outright that they tuned with ParamILS capped at 1,000 configurations, taking *"approximately 4 hours"*, report both the pre-tuning defaults and the tuned values, note the tuned version is only *"slightly better"*, and publish a corrected implementation with the warning that the originally submitted CEC2014 code *"had a bug in the archive update mechanism which resulted in a slight performance degradation."*

### The CEC competition record — with several corrections

⚠️ Source: Novák, Bezděk, Zelinka, Das & Beseda, arXiv:2603.24140 (2026), read in full, Tables 1–4. **It is an unrefereed preprint**, though it cites each winner's own paper. No refereed source tabulating the whole record was found.

| Year | Winner | Family |
|---|---|---|
| 2010 (LSGO) | MA-SW-Chains | memetic |
| 2011 (RW) | GA-MPC | GA |
| 2013 | ICMAES-ILS | IPOP-CMA-ES + iterated local search |
| **2014** | **L-SHADE** | DE |
| 2015 | SPS-L-SHADE-EIG | DE |
| 2016 | LSHADE-EpSin | DE |
| 2017 | **EBOwithCMAR** | DE/CMA-ES hybrid |
| 2018 | **HS-ES** | ES — the one non-DE exception |
| 2019 (100-D) | jDE100 | DE |
| 2020 | **IMODE** | DE ensemble |
| 2021 | **NL-SHADE-RSP** | DE |
| 2022 | **EA4eigN100** | DE/CMA-ES ensemble |
| 2024 | **L-SRTDE** | DE |

**Corrections to the commonly-repeated candidate list:**

- L-SHADE **did** win CEC 2014. Plain L-SHADE also placed 4th in 2015 and 5th in 2016.
- **jSO did NOT win 2017.** Rank 1 was EBOwithCMAR; jSO 2nd, LSHADE-SPACMA 3rd, LSHADE-cnEpSin 4th. (jSO later placed 5th in CEC 2024.)
- **AGSK did NOT win 2020.** Rank 1 was IMODE; AGSK 2nd, j2020 3rd.
- **MadDE did not win 2021.** Rank 1 was NL-SHADE-RSP; jDE21 2nd, APGSK_IMODE 3rd, DEDMNA 4th, MadDE 5th.
- EA4eig won 2022 (as EA4eigN100) and L-SRTDE won 2024 — both confirmed.
- No 2012 or 2023 entry in their dataset; 2013 split into Niching and Real-Parameter tracks.

**The summary claim "adaptive DE variants and DE/CMA-ES hybrids have dominated these competitions for over a decade" is fair and well supported.** The paper's framing: *"The most statistically significant trend in our dataset is the dominance of the L-SHADE family… This dominance was cemented between 2014 and 2016 …. This success solidified LPSR and Success-History Adaptation as common components for any competitive solver."* On the hybrid half: *"Eigenvector Crossover, utilized by recent top-performers such as EA4eigN100 and L-SRTDE, explicitly incorporates covariance learning. These methods periodically perform Principal Component Analysis (PCA) on the superior archive to extract eigen-coordinates, effectively BORROWING THE ROTATIONAL INVARIANCE OF CMA-ES … without incurring the full computational cost of matrix adaptation."* And the pre-2014 counterpoint: CEC 2013's real-parameter track *"was dominated by CMA-ES hybrids. … Despite this dominance of hybrid methods, the fourth-ranked algorithm proved most significant for future developments. SHADE, a pure DE variant building on JADE, demonstrated competitive performance without complex hybridization. This marked a turning point."*

**Two caveats that protect the claim from overreach:**

1. **Complexity inflation**: *"this shift toward ensembles has introduced a challenge of Complexity Inflation, where algorithms accumulate redundant components to minimize the risk of failure on specific outlier functions… it raises concerns regarding structural efficiency as concluded in a rigorous ablation study by Biedrzycki."*
2. **Benchmark overfitting**: Piotrowski *"identified a SIGNIFICANT NEGATIVE CORRELATION between performance on modern synthetic benchmarks (CEC 2020) and classical real-world problems (CEC 2011). While over-parameterized hybrids often dominate recent competitions, they frequently UNDERPERFORM on the CEC 2011 set … modern solvers appear increasingly hyper-tuned to the specific topographies of high-budget synthetic suites."*

**So: "DE has dominated the CEC competitions" is true; "therefore adaptive DE is the best general-purpose real-parameter optimizer" is contested in the same literature.**

---

## The boundary cases

### Particle swarm optimization

Kennedy & Eberhart, *Proc. IEEE ICNN 1995*, vol. IV, pp. 1942–1948, doi:10.1109/ICNN.1995.488968.

```
v[i,d] <- w·v[i,d] + φ_p·r_p·(p[i,d] − x[i,d]) + φ_g·r_g·(g[d] − x[i,d])
x[i]   <- x[i] + v[i]
```

with `p_i` the particle's best known position, `g` the neighbourhood best, `w` the inertia weight, `φ_p` cognitive and `φ_g` social coefficients, and `r_p, r_g ~ U(0,1)` drawn **per dimension**. Inertia and constriction: Shi & Eberhart 1998; Eberhart & Shi, CEC 2000; Clerc & Kennedy, *IEEE TEVC* 6(1):58–73, 2002. *"To prevent divergence ('explosion') the inertia weight must be smaller than 1."* ⚠️ The specific constriction figures `χ ≈ 0.7298` with `φ_1 = φ_2 = 2.05` could not be verified in the source read.

**Honest classification note: there is no selection in the Darwinian sense and no death of individuals** — every particle persists for the whole run and is only re-positioned. **PSO is population-based stochastic search but not an EA in the strict sense**; it is conventionally filed under swarm intelligence. Note that three of the six algorithms dissected in the metaphor-critique literature (`landscapes-and-rigour.md`) are PSO variants.

### Ant colony optimization

Dorigo, PhD thesis, Politecnico di Milano, 1992 (ant system proposed 1991); Dorigo, Maniezzo & Colorni, *IEEE TSMC-B* 26(1):29–41, 1996; Dorigo & Gambardella, *IEEE TEVC* 1(1):53–66, 1997; Stützle & Hoos, "MAX-MIN Ant System," *FGCS* 16:889–914, 2000.

Constructive, probabilistic solution building: the probability ant k moves from x to y is proportional to `(τ_xy)^α · (η_xy)^β`, normalised over allowed destinations, with τ the pheromone, η the heuristic desirability (typically `1/d_xy`). Global update: decay each transition by `(1 − ρ)`, then add all m ants' deposits; for TSP ant k deposits `Q/L_k` on each edge of its tour.

**Model-based search framing.** ACO *"shares some similarities with estimation of distribution algorithms"* and *"from a broader perspective … performs a model-based search"*; in 2004 Zlochin and colleagues *"showed ACO-type algorithms are closely related to stochastic gradient descent, the cross-entropy method, and EDAs. They proposed 'model-based search' as an umbrella term"* — Zlochin, Birattari, Meuleau & Dorigo, *Annals of Operations Research* 131:373–395, 2004.

### Estimation of distribution algorithms

Replace crossover and mutation with an **explicit probabilistic model**: *"Unlike most evolutionary algorithms, which generate new candidates through implicit distributions defined by variation operators, EDAs use an explicit distribution, such as a Bayesian network or a multivariate normal distribution."* Also called probabilistic model-building GAs. Loop: initialise `M(0)` uniform; sample N candidates from `M(t)`, evaluate, `M(t+1) := adjust_model(P, F, M(t))`. A noted side benefit: *"the learned models can reveal problem structure that is useful for local search, for biasing future runs, or for building computational models of the problem."*

Taxonomy by model complexity:

- **Univariate** — UMDA (Mühlenbein 1997); PBIL (Baluja 1994), implicit population, model moved toward selected solutions at rate γ; cGA (Harik, Lobo & Goldberg, *IEEE TEVC* 3(4):287–297, 1999), implicit population from two sampled individuals, γ typically 1/N.
- **Bivariate** — MIMIC (De Bonet, Isbell & Viola 1996), a chain factorisation minimising KL divergence; BMDA (Pelikan & Mühlenbein 1999), a forest of dependency trees.
- **Multivariate** — ECGA (Harik 1997), linkage learning via Model Complexity and Compressed Population Complexity; BOA (Pelikan, Goldberg & Cantú-Paz 1999), Bayesian networks with structure learned by adding edges that improve BIC or BDe; hBOA (Pelikan, Springer 2005); LTGA (Thierens 2010), which *"models only a linkage tree, not a probability distribution; uses optimal mixing that accepts only improving moves."*
- **Continuous** — EMNA, EGNA, real-coded PBIL, SHCLVND. ⚠️ Names verified, descriptions not.

Surveys: Larrañaga & Lozano (eds) 2002; Hauschild & Pelikan, *SWEVO* 1(3):111–128, 2011. Theory: Krejca & Witt, in Doerr & Neumann (eds) 2020, pp. 405–442.

⚠️ **The source read does not say CMA-ES is an EDA** — it lists CMA-ES under "Related," alongside the cross-entropy method and ACO, without describing the relationship. "CMA-ES is effectively a continuous Gaussian EDA plus evolution paths" is a fair structural reading but unsourced.

The state of an EDA is **distribution-valued**, which is exactly why Doerr & Neumann's survey says *"Due to the complicated nature of the underlying mathematical objects (a random process taking probability distributions as states), for a long time the theoretical understanding of these algorithms was very limited"*, and *"lower bound proofs for EDAs are often very difficult."*

### Simulated annealing

Kirkpatrick, Gelatt & Vecchi, *Science* 220(4598):671–680, 1983, doi:10.1126/science.220.4598.671; independently Černý 1985. Metropolis acceptance `exp(−Δ/T)` with a cooling schedule. **Geman & Geman's 1984 logarithmic-cooling convergence guarantee (`T_k ∝ c/log(1+k)`) exists and is practically useless** — the schedule is far too slow to run.

**State plainly: SA is single-point, not population-based, and therefore not an EA.** It is the standard comparison point because it is the other canonical general-purpose stochastic metaheuristic, and because **the (1+1)-EA is structurally SA at temperature 0**. Its practical profile: very low overhead, no parallel evaluation, no diversity mechanism, and a genuine (if unusable) convergence guarantee. SciPy ships `scipy.optimize.dual_annealing` as a zero-install baseline.

### Memetic algorithms and hybrids

**Origin.** Pablo Moscato, 1989 — Technical Report 826, "On Evolution, Search, Optimization, Genetic Algorithms and Martial Arts: Towards Memetic Algorithms," Caltech Concurrent Computation Program. Moscato's own framing: *"a marriage between a population-based global search and the heuristic local search"* performed by each individual.

**Lamarckian** — the chromosome is *updated* to match the improved solution; **Baldwinian** — the chromosome stays unchanged and only the improved *fitness* is used. *"Lamarckian updating can promote premature convergence. Structured populations are one way to mitigate this."*

**The five design questions:** (1) which learning method/meme — *"strongly affects results and may be deterministic or stochastic, continuous or combinatorial"*; (2) learning **frequency** — *"trades exploration against exploitation under a fixed budget"*; (3) **which** individuals receive learning; (4) learning **intensity** — the budget per learning step; (5) Lamarckian or Baldwinian.

Key citations: Ong & Keane, *IEEE TEVC* 8(2), 2004 (meta-Lamarckian learning); Krasnogor 2002 PhD thesis; Ong et al., *IEEE TSMC-B* 36(1), 2006; Chen et al., *IEEE TEVC* 15(5), 2011; Smith, *IEEE TSMC-B* 37(1), 2007; Hart 1994 PhD thesis; Whitley, Gordon & Mathias, PPSN III 1994; Neri, Cotta & Moscato (eds), *Handbook of Memetic Algorithms*, Springer 2012. Note that the memetic-algorithm literature itself cites Wolpert & Macready 1997 as *"the theoretical basis for MAs."*

**The empirical fact to state: for most combinatorial problems the competitive EAs are memetic.** The strongest single demonstration is vehicle routing — **Vidal, "Hybrid genetic search for the CVRP: Open-source implementation and SWAP* neighborhood," *Computers & Operations Research* 140:105643, 2022**, doi:10.1016/j.cor.2021.105643. HGS-CVRP adds a **SWAP\*** neighbourhood (exchanging two customers between different routes *without* an insertion-in-place restriction); *"an efficient exploration of SWAP* moves significantly contributes to the performance of local [search]"*; it *"[matches] the solution quality of the original HGS algorithm … in a fraction of its computational time"*, and on the Uchoa et al. (2017) instances *"HGS still stands as a leading metaheuristic."* ⚠️ Whether HGS won the DIMACS VRP Implementation Challenge is unverified. The TSP analogue is EAX.

**Brief placements.** Tabu search (Glover) — memory-based local search, not population-based. GRASP and Iterated Local Search — randomised-restart constructive and local-search schemes. Nelder–Mead and pattern search — the non-evolutionary derivative-free baselines, and per the CMA-ES literature the right choice below ~5 dimensions. Bayesian optimisation — the sample-efficient alternative when evaluations are expensive (`practice.md`).
