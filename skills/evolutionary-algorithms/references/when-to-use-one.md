# When to actually use an EA

The honest version of this question is not "is evolution cool" but "what else would I run, and what does it cost me." ⚠️ marks what could not be verified against a source actually read.

---

## Conditions that favour an EA — with the mechanism, not the slogan

1. **No usable gradient.** The objective is a black box, a simulation, a legacy binary, a physical experiment, non-differentiable, discontinuous, or defined only by a ranking. EAs need only a **comparison** between candidates, never a derivative. MOEA/D's authors make the point explicitly for a non-smooth aggregation: the Tchebycheff function's non-smoothness *"can still be used in the EA framework proposed in this paper since our algorithm does not need to compute the derivative of the aggregation function."*
2. **Mixed / categorical / structured / variable-length search spaces** where no continuous relaxation exists. Permutations, trees, graphs, programs, circuits, molecules, variable-length genomes. **Multi-objective mixed-integer nonlinear programming is brutal for exact methods; EAs degrade gracefully.** Concrete evidence the gap is real: Tanabe & Ishibuchi built 4 of their 16 real-world RE problems as mixed-integer specifically because *"there are only a few (multi-objective) mixed-integer optimization problems for benchmarking."*
3. **Multiple competing objectives where you want the trade-off surface, not one point.** This is the strongest case — see `multi-objective.md`.
4. **Multimodal landscapes where you want a diverse portfolio** rather than one optimum. **Quality-diversity (MAP-Elites, CMA-ME, novelty search) has no gradient analogue at all**; MAP-Elites' authors call it an **illumination** algorithm, not an optimisation algorithm, and note that illumination algorithms are *"a superset of optimization algorithms."* This is a genuine capability, not a consolation prize — see the hexapod damage-recovery result in `applications.md`.
5. **Noisy or stochastic objectives.** Two mechanisms: population averaging gives some robustness, and rank-based selection is invariant to any monotone distortion of the fitness scale. **Arnold & Beyer, "On the Benefits of Populations for Noisy Optimization," *Evolutionary Computation* 11(2):111–127, 2003**, doi:10.1162/106365603766646799, verified: under noise *"there exists an optimal truncation ratio that depends on the population size as well as on the noise strength"*, *"the optimal truncation ratio increases as the noise strength increases"*, *"above a certain noise strength substantial performance gains can be achieved by retaining more than the (seemingly) best candidate solution"*, and *"retaining about 20% of the total number of candidate solutions … almost universally yields near-optimal performance."* **Baseline contrast:** *"on the noise-free sphere the performance of the (mu,lambda)-ES with mu > 1 is never superior to that of the (1,lambda)-ES."* ⚠️ Note the scope: the paper is about `(μ,λ)` **comma** selection with μ > 1 and **no recombination**, on a linear one-dimensional model, by a moment-based population-variance analysis — the sphere appears only as the high-dimensional corollary. See also **overvaluation** in `operators-and-representation.md`: under noise, **non**-elitism is the safer default, which is why CMA-ES is non-elitist.
6. **Constraints easier to repair than to express analytically.** Deb's constraint-domination needs **no penalty coefficient at all**, because *"in no case constraints and objective function values are compared with each other."* Repair operators, decoders and feasibility-preserving operators are all natural in an EA and awkward in a solver.
7. **Evaluation cheap enough to afford 10³–10⁷ of them. This is the hard gate.** Calibration points, all verified: **CEC competitions specify a budget of 10,000 × D function evaluations** (100,000 at D=10 up to 1,000,000 at D=100); the WFG authors ran NSGA-II for **25,000 generations × 100 individuals = 2.5M evaluations** and still saw poor coverage on WFG1; **PMO caps molecular design at 10,000 oracle calls** and finds that *"within a realistic oracle budget of hundreds of experiments … 'state-of-the-art' methods often fail."*
8. **An embarrassingly parallel evaluation budget** — see the last section here.

---

## Conditions that rule one out — state these bluntly

### (a) Gradients are available and the problem is smooth

**Use them.** The quantitative reason, and it is a theorem: **Duchi, Jordan, Wainwright & Wibisono, "Optimal rates for zero-order convex optimization: the power of two function evaluations," arXiv:1312.2139**, 34 pp. For d-dimensional problems, if **pairs** of function values are available, gradient estimates built from random perturbations *"suffer a factor of at most sqrt(d) in convergence rate over traditional stochastic gradient methods."* It covers smooth and non-smooth cases, **sharpens** earlier analyses that suggested worse dimension dependence, and extends to m ≥ 2 evaluations.

**So the honest statement is: derivative-free methods pay a factor of at most √d in rate, and that bound is information-theoretically sharp — not "a factor of n," which overstates it.** Related: Nesterov & Spokoiny, *Foundations of Computational Mathematics* 17:527–566, 2017 ⚠️; Jamieson, Nowak & Recht, NIPS 2012 ⚠️.

The CMA-ES literature's own concession is the sharpest practical version: on *"nearly convex-quadratic functions with low or moderate Hessian condition number … BFGS, NEWUOA or SLSQP are at least ten times faster"*, and on problems solvable within about 10n evaluations NEWUOA or Multilevel Coordinate Search may be faster.

### (b) The problem is convex, or is an LP / QP / MILP / SDP

**Use a proper solver. You get a certificate of optimality; an EA can never give you one.**

For multi-objective problems that are convex and smooth with gradients, **the geometric objection to scalarization evaporates entirely**: on a convex problem the whole Pareto front **is** the boundary of `conv(Y + R^M_+)`, so weighted-sum scalarization is **complete** (Geoffrion 1968, doi:10.1016/0022-247X(68)90201-1) and every front point is reachable by some weight vector. Use weighted-sum or weighted-Tchebycheff plus an NLP solver (interior point, SQP) per weight vector, **warm-starting along the weight path** — the continuation idea MOEA/D's own authors credit: *"a solution obtained in the previous problem is set as a starting point for solving the next problem since its aggregation objective is just slightly different"* — or **Normal-Boundary Intersection** (Das & Dennis, *SIAM J. Optimization* 8(3):631–657, 1998) for even spacing. You get machine-precision front points, local optimality certificates, and convergence rates, **none of which a MOEA offers.**

Multi-gradient descent (MGDA-style common-descent directions) is right when you want a single Pareto-stationary point or a short Pareto path from gradients, especially in high decision dimension. ⚠️ MGDA citation unresolved — the usual one is Désidéri, *C. R. Acad. Sci. Paris*, 2012.

### (c) The problem has known structure with an exact or approximation algorithm

Shortest path, matching, max-flow, minimum spanning tree, LP. **Do not evolve these.**

**The TSP case, with a genuinely important nuance.**

- **Concorde** (exact branch-and-cut) — Applegate, Bixby, Chvátal & Cook, *The Traveling Salesman Problem: A Computational Study*, Princeton, 2006; `math.uwaterloo.ca/tsp/`. Verified from the primary site: **pla85900 (85,900 cities, a VLSI instance) has optimal tour length 142,382,641 units**; the milestone page lists it under **2006**, solved by *"D. Applegate, R. Bixby, V. Chvátal, W. Cook, Daniel Espinoza, Marcos Goycoolea and K. Helsgaun"*, with the computation *"carried out in 2005/06."* The milestone sequence: pla7397 (1994), usa13509 (1998), d15112 (2001), sw24978 (2004), pla85900 (2006) — **pla85900 remains the largest instance ever solved to proven optimality.** ⚠️ The CPU-years/processor count is on an unfetched subpage.
- **LKH** (Lin–Kernighan–Helsgaun) — Helsgaun, *EJOR* 126(1):106–130, 2000, doi:10.1016/S0377-2217(99)00284-2; plus LKH-2 and LKH-3 reports. ⚠️ **The LKH home page refused the connection on 2026-11-11**, so LKH's current version and its own record list are unverified. Note possible unavailability if you link it.
- **EAX — and this is stronger than the usual framing.** Nagata & Kobayashi, ICGA 1997, pp. 450–457; and *INFORMS Journal on Computing* 25(2):346–363, 2013, doi:10.1287/ijoc.1120.0506 (⚠️ INFORMS 403'd, so its instance-by-instance tables are unverified). Abstract-level result: the GA *"outperforms state-of-the-art heuristic algorithms in finding very high-quality solutions on instances with up to 200,000 cities"* and *"achieves top performance **without using an LK-based algorithm**."*

  **The decisive, primary-source-verified fact**, from `math.uwaterloo.ca/tsp/world/` fetched 2026-11-11: **the best tour ever found for the World TSP instance (1,904,711 cities) has length 7,515,755,912, and it was found by Yuichi Nagata on 17 October 2025.** The page describes the method: Nagata added the previous record tour (7,515,755,956) into a population generated by his **GA-EAX** heuristic and continued the GA-EAX search, **improving the record by 44 metres**. The best known **lower bound is 7,512,218,268, established by Concorde with CPLEX on 5 June 2007**, giving a gap of **0.0471%**.

  **So the correct statement is: a generic off-the-shelf genetic algorithm is not remotely competitive on TSP — but a GA with a domain-specific recombination operator is literally the current record holder on the largest well-known TSP instance, and Concorde (exact) holds the complementary lower bound.** EAX is not a historical curiosity. **This is about as clean a demonstration as the literature offers that the operator, not the metaheuristic, is where the power lives.** Nagata has an analogous GA for CVRP, and Vidal's HGS-CVRP is the same story for routing.
- Context: the 8th DIMACS Implementation Challenge (TSP) is the standard shared benchmarking effort. ⚠️ Specific results unverified.

### (d) Evaluations are expensive and few (tens to low hundreds)

Use Bayesian optimisation or a surrogate — see below for the crossover region and the specific methods.

### (e) You need guarantees

Optimality, feasibility, bounds, or reproducibility for certification. **An EA gives you none of these.** The only non-trivial theoretical guarantee available (elitist convergence in the limit) **is shared with blind random search and carries no rate.**

### (f) Very high dimension with no exploitable structure

Plain CMA-ES is `O(n²)` memory and time per sample; population methods generally scale poorly in n, where gradient or surrogate methods win.

### (g) Many objectives with no preference information

At M ≳ 10 Pareto dominance is vacuous (**94% of a random population of 100 is already non-dominated at M = 10**), the front needs exponentially many points to cover, visualisation fails, and the indicators themselves become expensive or meaningless. The NSGA-III authors concede the visualisation/metric difficulty *"cannot be avoided."* **The right move is to elicit preferences and reduce the problem, not to run a bigger MOEA**: reference-point/preference-based variants (R-NSGA-II, R-NSGA-III, PI-NSGA-II, all in pymoo), objective-reduction analysis, or interactive methods.

### (h) Separable functions, especially multimodal or high-dimensional — for CMA-ES specifically

Its own literature says DE may do better and that *"CMA-ES may fail to find comparable solutions on separable functions."*

### (i) n < 5 — again for CMA-ES specifically

The downhill simplex method or kriging-with-expected-improvement may do better.

---

## The direct head-to-head comparisons

### EA vs gradient descent / adjoint methods

The √d bound above is the general statement. **The sharpest practical case is aerodynamic shape optimisation, where adjoint methods dominate and the structural reason is clean: one adjoint solve gives the gradient with respect to *all* design variables at roughly the cost of one flow solve, so cost is nearly independent of dimensionality — whereas a population method needs O(population × generations) full CFD solves.** Citation: **Jameson, "Aerodynamic design via control theory," *Journal of Scientific Computing* 3(3):233–260, 1988**, doi:10.1007/BF01061285. Modern production/open tooling in this lineage: SU2, ADflow, Martins' MDO Lab work.

⚠️ **No paper was found quantifying the order-of-magnitude function-evaluation gap between EA and adjoint for a specific design problem.** If you want that number it needs a dedicated search.

**The same point for topology optimisation, and it includes a naming trap:**

- ⚠️ **ESO/BESO is NOT an evolutionary algorithm.** Xie & Steven, "A simple evolutionary procedure for structural optimization," *Computers & Structures* 49(5):885–896, 1993, doi:10.1016/0045-7949(93)90035-C; their book *Evolutionary Structural Optimization*, Springer 1997; plus Huang & Xie's bi-directional BESO. **It is a deterministic iterative hard-kill element-removal heuristic** — it removes low-stress elements from a mesh each iteration. **No population, no genome, no variation operators, no selection among competing individuals.** Calling it "evolutionary" is a naming accident and grouping it with GAs would be an error. There is a published refutation: **Zhou & Rozvany, "On the validity of ESO type methods in topology optimization," *Structural and Multidisciplinary Optimization* 21(1):80–83, 2001**, doi:10.1007/s001580050170 — a counterexample on which ESO converges to a demonstrably non-optimal design. Broader critique: Rozvany, *SMO* 37:217–237, 2009.
- **What actually dominates: SIMP, which is gradient-based with adjoint sensitivities.** Bendsøe, *Structural Optimization* 1(4):193–202, 1989, doi:10.1007/BF01650949; Bendsøe & Sigmund, *Topology Optimization*, Springer; Sigmund, "A 99 line topology optimization code written in Matlab," *SMO* 21(2):120–127, 2001; Andreassen et al. (2011) 88-line successor; Ferrari & Sigmund, *SMO* 62(4):2211–2228, 2020.
- **Where EAs legitimately belong in this space**: multimodal problems where gradients find only the nearest local optimum; genuine multi-objective trade-off fronts; discrete or topological design changes that break differentiability; coarse early-stage concept exploration; and cases where **no adjoint exists** (legacy solvers, coupled multiphysics, experimental loops).
- ⚠️ **On "generative design" marketing: no well-sourced engineering account of an EA-designed, manufactured production part was found.** The honest line is that most publicly cited examples (GE brackets, the Airbus partition) are **gradient/SIMP-based topology optimisation and/or lattice generation presented as "generative design"**, and that **press releases should not be cited as evidence of EA use.**

### EA vs Bayesian optimisation / GP surrogates — the evaluation-budget question

**The regimes.** BO is the right tool when one evaluation is a CFD run, a wet-lab experiment, or a full model training — tens to low thousands of evaluations, low-to-moderate dimension. EAs overtake as the budget grows and as dimension grows. **The crossover is roughly 10²–10³ evaluations, though this is a practitioner's rule rather than a theorem.**

- **Turner, Eriksson, McCourt, Kiili, Laaksonen, Xu & Guyon, "Bayesian Optimization is Superior to Random Search for Machine Learning Hyperparameter Tuning: Analysis of the Black-Box Optimization Challenge 2020," arXiv:2104.10201.** It analyses the NeurIPS 2020 challenge, which evaluated derivative-free optimisers for ML hyperparameter tuning on **hidden** objective functions, with baselines being the default settings of several open-source black-box packages plus random search. ⚠️ **The actual performance data and winning methods were not exposed, so the specific margins are unverified. The title asserts the conclusion; cite it for that and for the challenge's existence and design.**
- **TuRBO**, for high-dimensional BO and the "BO struggles" diagnosis: **Eriksson, Pearce, Gardner, Turner & Poloczek, "Scalable Global Optimization via Local Bayesian Optimization," NeurIPS 2019 (spotlight)**, arXiv:1910.01739. Its diagnosis is the useful part: BO *"struggles on high-dimensional problems with several thousand observations and is often not competitive on difficult problems"*, attributed to *"the homogeneity of global probabilistic models and overemphasized exploration from global acquisition."* TuRBO *"fits a collection of local models"* with *"a principled global allocation of samples across these models"* through an implicit bandit approach. ⚠️ Its specific comparisons against CMA-ES and DE, and the dimensionalities and budgets, are unverified.
- **Multi-objective BO**, where the methods are named and verified:
  - **ParEGO** (Knowles, *IEEE TEVC* 10(1):50–66, 2006, doi:10.1109/TEVC.2005.851274) — randomly draws an **augmented-Tchebycheff** weight vector each iteration, fits a GP to that scalarisation, maximises single-objective EI; one evaluation per iteration, cheap and surprisingly strong.
  - **MOEA/D-EGO** (Zhang, Liu, Tsang & Virginas, *IEEE TEVC* 14(3):456–474, 2010) — fits GPs, builds N scalar subproblems with EI acquisitions, and uses MOEA/D to optimise them all at once, **so it proposes a batch per iteration.**
  - **qEHVI** (Daulton, Balandat & Bakshy, NeurIPS 33, 2020, arXiv:2006.05078): *"qEHVI is an exact computation of the joint EHVI of q new candidate points (up to Monte-Carlo integration error). Whereas previous EHVI formulations rely on gradient-free acquisition optimization or approximated gradients, we compute exact gradients of the MC estimator via auto-differentiation … outperforms state-of-the-art multi-objective BO algorithms at a fraction of their wall time."*
  - **qNEHVI**, the noisy/parallel successor and the one to prefer (arXiv:2105.08195, NeurIPS 2021): *"qNEHVI, that reduces computational complexity of parallel EHVI from EXPONENTIAL TO POLYNOMIAL with respect to the batch size. qNEHVI is one-step Bayes-optimal for hypervolume maximization in both noisy and noiseless environments … substantially more robust to observation noise than existing MOBO approaches."* ⚠️ **The exponential-to-polynomial-in-q claim belongs to qNEHVI, not qEHVI**; qEHVI's own complexity in q and M was not stated in the abstract, so **do not quote an exponent for it.** Both are implemented in BoTorch.
- **The irony worth printing: the dominant expensive-budget method, qEHVI/qNEHVI, optimises exactly the hypervolume indicator that SMS-EMOA and HypE use for selection — and inherits the same #P-hardness in M and the same reference-point sensitivity. The indicator theory is shared; only the sample budget differs.**

**Surrogate-assisted EAs as the hybrid**: Jin, "Surrogate-assisted evolutionary computation: Recent advances and future challenges," *SWEVO* 1(2):61–70, 2011, doi:10.1016/j.swevo.2011.05.001.

**The model-management problem, stated concretely — this is the part people skip.** A surrogate (Kriging/GP, RBF, polynomial, neural net) is accurate only where you have sampled, **and an EA's whole job is to *leave* the sampled region.** So the optimiser will reliably find and exploit the surrogate's extrapolation errors — **the surrogate becomes, by construction, a fitness function that rewards the wrong thing.** Model management is the set of policies that stop this:

1. **How often** to re-evaluate on the true objective (generation-based vs individual-based control).
2. **Which** individuals to re-evaluate (best-predicted = exploitation, highest-uncertainty = exploration, or an acquisition function balancing them — **which is exactly where surrogate-assisted EC and BO meet**).
3. **Local vs global** surrogates (a global model with few points is useless in high dimension).
4. **Multi-fidelity** — cheap coarse simulation to rank, expensive fine simulation to confirm, with the fidelity schedule itself a design choice.
5. **Evolution control with an explicit trust region** that shrinks when the surrogate's prediction error on new true evaluations exceeds a threshold.

**Practical rule: never let a surrogate-assisted run report a surrogate-*predicted* value as a result. Report only true-evaluated fitness, and report the number of *true* evaluations as the budget. The single most common error in this literature is a budget axis that counts surrogate calls.**

Tooling: pycma ships `cma/fitness_models.py` and `fmin_lq_surr`/`fmin_lq_surr2`; for a Bayesian alternative, botorch 0.18.1 / ax-platform 1.3.1 / Optuna's `GPSampler`.

### EA vs random search — and the Bergstra & Bengio result, with a correction

**Bergstra & Bengio, "Random Search for Hyper-Parameter Optimization," *JMLR* 13:281–305.** Submitted 3/11, revised 9/11, **published 2/2012**. Editor: Léon Bottou. (Full text read.)

**The actual argument**, verbatim: *"In this work we show that random search is more efficient than grid search in high-dimensional spaces because functions Psi of interest have a LOW EFFECTIVE DIMENSIONALITY; essentially, Psi of interest are more sensitive to changes in some dimensions than others… if a function f of two variables could be approximated by another function of one variable (f(x1,x2) ≈ g(x1)), we could say that f has a low effective dimension."*

And the key asymmetry, verbatim: *"on different data sets, different subspaces are important, and to different degrees. A grid with sufficient granularity to optimizing hyper-parameters for all data sets must consequently be inefficient for each individual data set because of the curse of dimensionality: THE NUMBER OF WASTED GRID SEARCH TRIALS IS EXPONENTIAL IN THE NUMBER OF SEARCH DIMENSIONS THAT TURN OUT TO BE IRRELEVANT for a particular data set. In contrast, random search thrives on low effective dimensionality. Random search has the same efficiency in the relevant subspace as if it had been used to search only the relevant dimensions."*

**The probabilistic statement as the paper actually makes it** (§4), verbatim: *"The expected probability of finding the target is 1.0 minus the probability of missing the target with every single one of T trials in the experiment. If the volume of the target relative to the unit hypercube is (v/V = 0.01) and there are T trials, then this probability of finding the target is 1 − (1 − v/V)^T = 1 − 0.99^T."*

⚠️ **Correction, and it matters: the famous "60 trials gives a 95% chance of landing in the top 5% of the space" line is NOT in this paper.** The full text was grepped for "60", "quantile", "5%", "0.95" and the only probabilistic statement is the one above, instantiated at a **1%** target volume, not 5%. The 60-trials claim is a trivially true **corollary** (`1 − 0.95^n >= 0.95 ⟺ n >= 59`) that entered circulation through secondary expositions. **If you state it, state it as a corollary of Bergstra & Bengio's reasoning rather than as a quotation** — and note that **n = 59 is strictly the threshold** (0.95^58 → 94.89%; 0.95^59 → 95.15%), so "60" is a rounding.

**What the paper actually compared**, verbatim from the abstract: *"Compared with neural networks configured by a pure grid search, we find that random search over the same domain is able to find models that are as good or better within a small fraction of the computation time. … Compared with deep belief networks configured by a thoughtful combination of manual search and grid search, purely random search over the same 32-dimensional configuration space found statistically equal performance on four of seven data sets, and superior performance on one of seven."* ⚠️ **It compared against grid search and manual search. It did NOT compare against an EA.**

Their effective-dimensionality measurement, via GP regression: *"Even in this simple 7-d problem, Psi has a much lower effective dimension of between 1 and 4"*, with the lowest-effective-dimension datasets easiest to optimise.

**And their own honest negative**, verbatim: on mnist basic, 4–8 random trials often matched much larger experiments, but on mnist-rotated-background-images and convex *"even with 16 or 32 random trials, there is considerable variation"*, and for 3-layer DBNs *"even experiments with larger numbers of trials (64 and larger) feature significant variability. This indicates that the regions of the search space with the best performance are small, and randomly chosen i.i.d. trials do not reliably find them."*

**The wider lesson: random search is the correct null hypothesis any EA paper must beat, and it is a surprisingly hard one.** Two verified reinforcements:

- **Li & Talwalkar, "Random Search and Reproducibility for Neural Architecture Search," UAI 2019**, arXiv:1902.07638 (full text read): *"on PTB, random search with early-stopping reaches test perplexity of 56.4 compared to the published result for ENAS"*; on CIFAR-10, random search with weight sharing *"achieves a test error of 2.85%, whereas the published result for ENAS is 2.89%."*
- Such et al.'s deep-GA paper found **random search on 4M-parameter networks beat DQN on 3 Atari games, ES on 3, and A3C on 6 of 13** — see `applications.md`.

Also note **Hyperband's honest framing: its guarantees are *relative to random search*** — it is a smarter **allocator** of a random-search budget and degrades gracefully to random search, **which is exactly why it is such a hard baseline.** Li, Jamieson, DeSalvo, Rostamizadeh & Talwalkar, *JMLR* 18(185):1–52, 2018, arXiv:1603.06560. And **BOHB** keeps Hyperband's bandit budget allocation but replaces its *random* configuration sampling with a TPE-style multivariate-KDE Bayesian model, getting Hyperband's anytime behaviour and BO's final performance: Falkner, Klein & Hutter, ICML 2018, arXiv:1807.01774 ⚠️ (numbers unverified).

### EA vs simulated annealing

SA is **single-point**: no parallel evaluation, no diversity mechanism, very low per-step overhead, and a genuine but unusable convergence guarantee (Geman & Geman's logarithmic cooling). **The (1+1)-EA is structurally SA at T = 0.** In practice SA remains competitive on combinatorial problems with a cheap, well-understood local move and no useful notion of recombination; **EAs win where recombination can assemble partial solutions (TSP via EAX being the extreme case) or where you want parallelism or diversity.**

### EA vs problem-specific heuristics

**A well-designed problem-specific heuristic almost always beats a generic metaheuristic, and the metaheuristic's value is precisely when you do not have one or cannot afford to build one.**

The corollary that matters for honesty: **the comparison baseline for a new EA on a classic problem is the best known specialist solver, not another metaheuristic.** This is one of the named failures in the metaphor-critique literature's methodological checklist (*"the exclusive use of very similar algorithms (i.e., other metaphor-based methods) as comparison baselines, instead of state-of-the-art methods"*).

The GuacaMol authors make the same point with a baseline that is almost comic in its simplicity and which several published models fail to beat: **"Best of Dataset"** — simply picking the best molecules already in ChEMBL — *"is a useful baseline, since it actually corresponds to a strategy based on virtual [screening]."*

### EA vs mixed-integer programming

If the problem can be modelled as a MILP of tractable size, a modern solver with presolve, cuts and branching will usually dominate, **and gives a bound.**

### EA vs reinforcement learning for policy search

See `applications.md`. **The short verdict is that evolution bought wall-clock and parallel scaling, not data efficiency, and the field's compute economics moved toward environments where samples rather than cores are scarce.**

---

## Parallelism as a genuine structural advantage

Fitness evaluation is **embarrassingly parallel** across the population. A generational EA with λ offspring gets near-linear speedup up to λ workers with only a synchronisation barrier per generation; asynchronous / steady-state and island models remove even that barrier. Contrast:

- **Gradient descent** on a single objective is inherently sequential in the iteration.
- **Sequential BO** is inherently sequential in the acquisition maximisation, and parallelising it at all requires dedicated batch machinery — q-EI, q-EHVI, qNEHVI, local penalisation — **which is an active research area precisely because it is hard.** (And the verified qNEHVI result above is specifically about reducing the parallel-batch complexity from exponential to polynomial in q.)

**The extreme case, fully verified: OpenAI ES's seed trick.** *"if we synchronize random seeds between workers before optimization, each worker knows what perturbations the other workers used, so each worker only needs to communicate a single scalar to and from each other worker to agree on a parameter update. ES thus requires extremely low bandwidth, in sharp contrast to policy gradient methods, which require workers to communicate entire gradients."* Measured speedup: MuJoCo 3D Humanoid to score 6,000 took **657 minutes on 18 cores** and **10 minutes on 80 machines / 1,440 CPU cores** (median of 7 repeats) — *"reducing experiment turnaround time by two orders of magnitude… ES is able to achieve linear speedup in the number of CPU cores."* ⚠️ No absolute bandwidth figure in bytes/s is given in the paper.

Models to name: master-worker, island / coarse-grained, cellular / fine-grained. Implementations: DEAP's pluggable `map` (one-line swap to multiprocessing or SCOOP); LEAP's synchronous **and asynchronous** Dask evaluation with `DistributedIndividual`; ECJ's asynchronous island models over TCP/IP and master/slave evaluation; pymoo's `StarmapParallelization` and `DaskParallelization` (single-machine only); pygmo/pagmo2's island model.

⚠️ **The caveat that must accompany all of this: wall-clock speedup is not a better algorithm. Comparisons must still be by evaluation count. An EA that needs 10× the evaluations and runs on 100× the cores has not beaten anything; it has bought latency with hardware. State both axes.**
