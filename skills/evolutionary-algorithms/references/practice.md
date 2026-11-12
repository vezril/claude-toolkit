# Practice: libraries, defaults, hygiene, failure modes

All version numbers, dates and repo state fetched **2026-11-11** via the PyPI JSON API, the GitHub REST API, Maven Central `maven-metadata.xml`, project docs, and **library source code** wherever "shipped defaults" were the question. ⚠️ marks what could not be verified.

**Three corrections to commonly-cited URLs, up front:**

1. `cs.gmu.edu/~sean/…` and `cs.gmu.edu/~eclab/…` are **dead** (301 → the department homepage). The live URLs are **`people.cs.gmu.edu/~sean/book/metaheuristics/`** and **`people.cs.gmu.edu/~eclab/projects/ecj/`**.
2. COCO's canonical home is now **`https://coco-platform.org/`**. `numbbo.github.io/coco/` still resolves but banners *"New documentation pages for COCO (replacing all this here)"*. `coco.gforge.inria.fr` is dead (no DNS). **The monolithic `numbbo/coco` repo has been split** into `numbbo/coco-experiment` + `numbbo/coco-postprocess`.
3. **Nevergrad's own docs no longer recommend `NGOpt`** — they recommend **`NgIohTuned`** (*"should therefore be a good default"*).

---

## The libraries

### DEAP — assemble-it-yourself; the reference for custom representations and GP

- PyPI `deap` **1.4.4**, uploaded **2026-04-17**. **License LGPL-3.0.** GitHub DEAP/deap: 6,461 stars, last commit 2026-04-17, **292 open issues**, **no GitHub Releases**.
- **Maintenance verdict: alive but bursty and thin.** Commit history is clustered — 2025-05, 2025-11, then the 2026-04 1.4.4 burst (which notably **replaced DEAP's own C hypervolume extension with `moocore.hypervolume()`**, a Manuel López-Ibáñez contribution). Between bursts: nothing. **292 open issues against a ~6.5k-star project is the honest tell. Treat it as stable and unabandoned, not actively developed.**
- **Design:** two global pieces — `deap.creator` (a runtime class factory) and `deap.base.Toolbox` (a registry of named partials). **You write the algorithm**; `deap.algorithms` ships only four loops: `eaSimple`, `eaMuPlusLambda`, `eaMuCommaLambda`, `eaGenerateUpdate` (the generate-update loop CMA-ES plugs into).
- **What it actually supports** (verified by reading the modules, not the docs):
  - Selection: `selTournament`, `selRoulette`, **`selDoubleTournament`** (fitness+parsimony — a real GP feature), `selStochasticUniversalSampling`, **`selLexicase`**, **`selEpsilonLexicase`**, `selAutomaticEpsilonLexicase`.
  - Crossover: one/two-point, uniform, **PMX (`cxPartialyMatched`)**, `cxUniformPartialyMatched`, **`cxOrdered`**, `cxBlend`, `cxSimulatedBinary`, `cxSimulatedBinaryBounded`, `cxMessyOnePoint`, `cxESBlend`, `cxESTwoPoint`.
  - Mutation: `mutGaussian`, `mutPolynomialBounded`, `mutShuffleIndexes`, `mutFlipBit`, `mutUniformInt`, **`mutInversion`**, `mutESLogNormal`.
  - Multi-objective: `selNSGA2`, `selNSGA3` (+ `uniform_reference_points`), `selSPEA2`, `selTournamentDCD`, `sortNondominated` (docs: *"Deb et al.'s fast nondominated sorting … Complexity is O(MN²)"*), `sortLogNondominated` (*"the generalized reduced run-time algorithm from Fortin et al. (2013)"*), `ParetoFront` hall-of-fame.
  - CMA-ES: `Strategy`, `StrategyOnePlusLambda`, `StrategyActiveOnePlusLambda`, `StrategyMultiObjective` (= MO-CMA-ES, Voss et al. 2010). **`Strategy` defaults `lambda_ = int(4 + 3*log(dim))`, `mu = int(lambda_/2)` — DEAP ships the canonical CMA-ES population formula.**
  - GP: `PrimitiveSet`, **`PrimitiveSetTyped`** (strongly-typed GP), `genFull`/`genGrow`/`genHalfAndHalf`/`genRamped`, `cxOnePointLeafBiased`, the five standard mutations, and geometric-semantic ops `mutSemantic`/`cxSemantic`.
  - **Parallelism is a one-liner and genuinely pluggable**: `Toolbox.__init__` does `self.register("map", map)`; override with `toolbox.register("map", pool.map)` or `futures.map` (SCOOP).
- **What it lacks:** no benchmark/experiment harness worth using; no indicators beyond hypervolume (now delegated to `moocore`); no constraint-handling framework (`tools/constraint.py` is just feasibility decorators); no serious termination criteria; no parameter adaptation; no GPU. **Pickling + `creator` globals makes multiprocessing fragile on `spawn` platforms (macOS/Windows).**
- Citation: Fortin, De Rainville, Gardner, Parizeau & Gagné, "DEAP: Evolutionary Algorithms Made Easy," *JMLR* **13(70):2171–2175, 2012**. No DOI. ⚠️ **The URL printed in that paper's abstract, `http://deap.gel.ulaval.ca`, is dead.** Cite `github.com/DEAP/deap` / `deap.readthedocs.io`. ⚠️ The docs currently render "DEAP 1.4.3 documentation" — **they lag the 1.4.4 release.**

### pymoo — the multi-objective workhorse; the most actively maintained thing here

- PyPI `pymoo` **0.6.2**, uploaded **2026-06-28**. **License Apache-2.0.** `requires_python >= 3.10`. GitHub: 2,994 stars, **last commit 2026-11-11 (the day checked)**, **only 2 open issues**. ⚠️ **Repo note:** the docs link `github.com/anyoptimization/pymoo`, which now **301-redirects to `the-dual-space/pymoo`** — actively developed, repo recently moved/renamed, docs not yet updated.
- **Maintenance verdict: excellent — daily commits, near-zero issue backlog. This is the one to build on.**
- **Algorithms.** *Single-objective*: GA, BRKGA, DE, NelderMead, PSO, PatternSearch, ES, **SRES**, **ISRES**, CMAES, G3PCX, **NRBO**. *Multi-objective*: **NSGA2**, **RNSGA2**, **PINSGA2**, **SPEA2**, **OmniOptimizer**, **CMOPSO**, **MOPSO_CD**, **NSDE**, **GDE3**. *Many-objective*: **NSGA3**, **RNSGA3**, **UNSGA3**, **MOEAD**, **AGEMOEA**, **AGEMOEA2**, **RVEA**, **SMSEMOA**, **CTAEA**, **NSDER**. *Dynamic*: **DNSGA2**, **KGB**.
- **Indicators**: **GD, GD+, IGD, IGD+, Hypervolume (HV)**, and **KKTPM**. HV is implemented via **`moocore`**, citing Fonseca, Paquete & López-Ibáñez, IEEE CEC 2006, doi:10.1109/CEC.2006.1688440.
- **Constraints**: problems declare `n_ieq_constr` / `n_eq_constr` (⚠️ **these replaced `n_constr` in 0.6.0**); `_evaluate` fills `out["F"]`, `out["G"]` (≤0 feasible), `out["H"]` (=0 feasible). Strategies: **Feasibility First** (default), violation-as-penalty, violation-as-objective, ε-constraint, repair; SRES/ISRES handle constraints internally.
- **Decomposition objects**: weighted-sum, **ASF, AASF**, Tchebysheff, **PBI**.
- **Reference directions**: `uniform` (Das–Dennis), **`energy` (Riesz s-energy — can produce *any* number of points in *any* dimension, which Das–Dennis cannot)**, `multi-layer`, `layer-energy`, `incremental`.
- **Visualization**: Scatter, ParallelCoordinatePlot, Heatmap, Petal, Radar, Radviz, StarCoordinate, Video. **MCDM**: compromise programming, **pseudo-weights**, high trade-off points.
- **Lacks**: no GP / tree representation, no quality-diversity, no GPU/JAX backend, single-machine parallelism only.
- Citation: Blank & Deb, "pymoo: Multi-Objective Optimization in Python," *IEEE Access* **8:89497–89509, 2020**, doi:10.1109/ACCESS.2020.2990567.

### PyGAD — the "I need a GA in 20 lines" library

- PyPI `pygad` **3.9.2**, uploaded **2026-10-16**. **License BSD-3-Clause.** GitHub: 2,235 stars, last commit 2026-10-23, 46 open issues. **Maintenance verdict: actively maintained by essentially one author (Ahmed Gad). Single-maintainer risk is the real caveat.** ⚠️ Docs lag (they say 3.8.1).
- Niche: `pygad.GA(...)` plus a user `fitness_func` and you are done. The differentiating modules are the **ML bridges**: **`pygad.kerasga`** (`model_weights_as_vector`/`model_weights_as_matrix`), **`pygad.torchga`**, plus its own `nn`/`gann`/`cnn`/`gacnn`. Multi-objective: supported by returning a list/tuple/ndarray from the fitness function.
- **Lacks**: no GP/tree representation, no benchmarking harness, no adaptive-parameter implementations, no distributed execution beyond a `parallel_processing` kwarg. **The `pygad.nn`/`cnn` modules are pedagogical, not production.**
- Citation: Gad, "PyGAD: an intuitive genetic algorithm Python library," *Multimedia Tools and Applications* **83(20):58029–58042**, doi:10.1007/s11042-023-17167-y. ⚠️ **Year ambiguity:** Crossref's `issued` is **2023** (online-first) but volume/issue 83/20 is a **2024** issue. Cite as "2024 (online 2023)" or just give the DOI.

### `cma` (pycma) — the continuous black-box workhorse

- PyPI `cma` **4.5.0**, released **2026-09-13**. **License BSD-3-Clause.** Maintainer Nikolaus Hansen (authors: Hansen, Youhei Akimoto, Petr Baudis).
- API: **`cma.fmin2`** as a one-liner and **`cma.CMAEvolutionStrategy`** with an **ask-and-tell** interface; also `fmin_con2`. Covers restarts, **noise handling** (`noise_handler=True`), bounds, linear and nonlinear constraints, integer variables. ⚠️ The current page names `fmin2` and `fmin_con2`, **not** plain `fmin`.
- Citations: Hansen & Ostermeier, *Evolutionary Computation* 9(2):159–195, 2001; and the tutorial, Hansen, arXiv:1604.00772 — **cite the version**.
- Related: `cmaes` **0.13.1** (CyberAgent) is Optuna's CMA-ES backend; also `fcmaes`.

### Nevergrad (Meta) — portfolio / automatic algorithm selection

- PyPI `nevergrad` **1.0.12**, uploaded **2025-04-23**. **License MIT.** GitHub: 4,225 stars, last commit **2026-11-02**, **146 open issues**, last release 2025-04-23. ⚠️ **`CHANGELOG.md`'s newest entry is v0.11.0 (2023-07-25) — the changelog has been abandoned.**
- **Maintenance verdict: code moves, releases don't.** ~19 months with no PyPI release despite commits into Nov 2026. Fine to use; **pin a git SHA if you need recent fixes.**
- **The portfolio idea, verified from source, and the honest finding matters.** `nevergrad/optimization/optimizerlib.py` (7,755 lines). `NGOptBase` is documented in-code as *"Nevergrad optimizer **by competence map**."* Its `__init__` probes the parametrization (`has_noise`, `fully_continuous`, `has_discrete_not_softmax`, `_arity`, `num_workers`, `budget`) and subclasses override `_select_optimizer_cls()` with **hand-written threshold rules**. A real example from `NGOpt12`: `cma_vars = max(1, 4 + int(3*np.log(self.dimension)))`; if `not has_noise and fully_continuous and num_workers <= cma_vars and dimension < 100 and budget < dimension*50 and budget > min(50, dimension*5)` → return `MetaModel`, else fall through a chain. There is a whole lineage `NGOpt4 → … → NGOpt39`, with `class NGOpt(NGOpt39)`, plus `Wiz`, `NGOptRW`, `NgIoh`..`NgIoh7`.

  **It is a decision tree fitted to benchmark results, not a learned meta-model — worth saying plainly.**
- Registry size: `optimizerlib.py` alone has **93 `@registry.register` decorators and 262 `ConfiguredOptimizer(...).set_name(…, register=True)` calls**. ⚠️ The full total is unverified without importing; introspect with `sorted(ng.optimizers.registry.keys())`.
- **Recommended default per the docs: `NgIohTuned`** (*"adapts to the provided settings (budget, number of workers, parametrization)"*; delegates to DE for multi-objective). `NGOpt` is the older recommendation.
- Benchmark suite: `nevergrad/benchmark/`, driven by `python -m nevergrad.benchmark <experiment>`. The "Dagstuhloid" benchmark was added in v0.8.0. Nevergrad data is mirrored in IOHprofiler's `IOHdata`.
- Citation: Rapin & Teytaud, "Nevergrad — A gradient-free optimization platform," 2018 (software citation; no peer-reviewed paper). ⚠️ The README's BibTeX block was not fetched.

### LEAP — operator pipelines; distributed/asynchronous EAs via Dask

- PyPI `leap-ec` **0.8.2**, uploaded **2025-03-24**. **License AFL-3.0.** Requires Python ≥3.11. GitHub: 105 stars, **last commit 2026-06-30** (a dependency bump), 74 open issues. **Maintenance verdict: dormant/low-activity** — last substantive code change 2025-03-30.
- Niche: the **operator pipeline** — *"a simple list of functional operators to concisely express a metaheuristic algorithm's configuration as high-level code."* Entry points: `leap_ec.simple.ea_solve`, then `generational_ea` / `multi_population_ea`, plus `generalized_nsga_2`, parsimony pressure (`koza_parsimony`, `lexical_parsimony`), and cooperative coevolution. **Its real differentiator is "Distributed LEAP": synchronous *and asynchronous* fitness evaluation via Dask (`DistributedIndividual`) plus island migration — few Python EA libraries do async steady-state distribution honestly.**
- Citation: Coletti, Scott & Bassett, "Library for evolutionary algorithms in Python (LEAP)," GECCO '20 Companion, pp. 1571–1579, doi:10.1145/3377929.3398147.

### inspyred — dormant; historical/teaching interest only

PyPI `inspyred` **1.0.3** (2024-10-24), MIT. GitHub: 202 stars, last commit 2026-07-22 — ⚠️ **but every commit since 2024-04 is a Dependabot GitHub-Actions bump.** **Maintenance verdict: feature-dormant. The repo is kept green, not developed. Do not start new work here.** Its value today is the pedagogical clarity of its observer/terminator/variator/replacer/selector decomposition.

### Jenetics (Java) — immutable, type-safe, Java-Streams-native

- Version **9.1.0**, Maven Central **2026-09-02**. ⚠️ **`search.maven.org`'s Solr index is stale and still reports 8.2.0 — use `maven-metadata.xml`.** **License Apache-2.0.** **Compiles and runs with Java 25.** No runtime third-party dependencies. GitHub: 911 stars, last commit 2026-09-03, 32 open issues. **Maintenance verdict: healthy, single-author, steady annual majors.**
- Design: strict `Gene → Chromosome → Genotype → Phenotype → Population → Function` separation; **`EvolutionStream implements java.util.stream.Stream`**, so an EA is `engine.stream().limit(100).collect(EvolutionResult.toBestGenotype())`; **minimisation is an `Engine` configuration, not a fitness-function change**; the PRNG is pluggable through the standard `RandomGenerator`. **Genotypes are immutable and genes are type-parameterised (`Genotype<BitGene>`), which is the actual ergonomic difference from ECJ.**
- Modules: `jenetics` (base), `jenetics.ext` (**multi-objective**, grammatical evolution, tree structures), `jenetics.prog` (**genetic programming**), `jenetics.xml`, `jenetics.incubator`. ⚠️ NSGA-II class names are unverified.
- Citation: none designated. Cite the software + version + `https://jenetics.io`.

### ECJ (Java, Sean Luke / George Mason ECLab) — parameter-file configurability, strongest GP

- **ECJ 28** is current (the `v28` commit landed **2026-01-11**). ⚠️ **The newest GitHub *tag* is `v27` (2019-08-30) — tags lag badly; do not read the version off releases.** Not on Maven Central. GitHub: 133 stars, last commit 2026-01-11, 21 open issues. **License AFL 3.0.** **Maintenance verdict: slow but alive** — one commit burst per year or two from the original author; a 25+-year-old, genuinely stable codebase (*"has (fortunately) exhibited relatively few serious bugs over the years"*).
- Live URLs: **`people.cs.gmu.edu/~eclab/projects/ecj/`**, manual at `.../manual.pdf` (*"a really, really big manual"*).
- Strengths, as the project states them: *"nearly all classes (and all of their settings) **dynamically determined at runtime by a user-provided parameter file**"*, hierarchical parameter files, a GUI with charting, platform-independent checkpointing, multithreading, Mersenne Twister. EC features: **asynchronous island models over TCP/IP**; master/slave evaluation; generational and steady-state; **(μ,λ) and (μ+λ) ES**; a single-state package (hill-climbing, SA); **CMA-ES, AMaLGaM IDEA, PBIL, DOvs EDAs**; Ant System / ACS / GRASP; **NSGA-II, NSGA-III, SPEA2**; PSO; DE; spatially embedded EAs; meta-evolution; parsimony-pressure packages; **set-based strongly-typed GP.**
- Citation (the project's preferred form): Sean Luke, *ECJ Evolutionary Computation Library* (1998).
- **Essentials of Metaheuristics** — Sean Luke, Second Print Edition, "Online Version 2.4." Live page: **`people.cs.gmu.edu/~sean/book/metaheuristics/`** ⚠️ (PDF ~5 MB, **gated behind a short usage form**; there is no direct stable PDF link). He self-describes it as lecture notes: *"short and light on examples and theory."* **His definition of a metaheuristic is worth quoting: *"A common but unfortunate name for any stochastic optimization algorithm intended to be the last resort before giving up and using random or brute-force search."***

### jMetal (Java) / jMetalPy (Python)

- **jMetal (Java): 7.11**, Maven Central **2026-11-05**. ⚠️ search.maven.org's Solr still says 6.6 — **stale index again.** **License MIT.** GitHub: 562 stars, **last commit 2026-11-11**, 5 open issues, **no GitHub Releases** (Maven + tags only). **Maintenance verdict: very active** (Nebro's group). Modules: `jmetal-core`, `jmetal-algorithm`, `jmetal-problem`, **`jmetal-component`** (an algorithm-template/component framework — **a notable idea, since algorithms assembled from interchangeable components make fair ablation studies tractable**), **`jmetal-lab`** (experimentation + statistics). **Still the broadest MOEA catalogue anywhere.** Citation: Durillo & Nebro, "jMetal: A Java framework for multi-objective optimization," ***Advances in Engineering Software* 42(10):760–771, 2011**, doi:10.1016/j.advengsoft.2011.05.014. ⚠️ **Note the venue is *Advances in Engineering Software*, NOT a CEC paper.**
- **jMetalPy: 1.10.0**, PyPI **2026-11-06**. **License MIT.** Requires Python ≥3.11. GitHub: 617 stars, **10 open issues**. **Maintenance verdict: actively maintained.** Algorithms: **GDE3, HypE, IBEA, MOCell, MOEA/D, NSGA-II, NSGA-III, OMOPSO, SMPSO, SPEA2, SMS-EMOA.** ⚠️ **Notably it has HypE and IBEA, which pymoo does not.** Problems: ZDT, DTLZ, WFG, **ZCAT**, FDA (dynamic), LZ09, **RE**, **RWA** — **ZCAT and RE/RWA are more modern than pymoo's lineup; ZCAT is a recent scalable suite designed to avoid the triangular-front bias.** Indicators: Hypervolume, IGD, IGD+, ε, **average Hausdorff distance**. Citation: Benítez-Hidalgo, Nebro, García-Nieto, Oregi & Del Ser, *SWEVO* **51:100598, 2019**, doi:10.1016/j.swevo.2019.100598.

### Brief entries

| Library | Version (2026-11-11) | Licence | Purpose | Verdict |
|---|---|---|---|---|
| **EvoTorch** | `evotorch` 0.6.1, 2025-05-14 | Apache-2.0 | GPU/vectorised EC on PyTorch tensors; Ray-distributed; CMAES, PGPE, SNES, XNES, neuroevolution + Gym/Brax | **Dormant.** ~18 months quiet. (⚠️ `pushed_at` 2026-11-02 is a **non-default branch** — not activity.) Cite Toklu et al., arXiv:2302.12600 |
| **evosax** | `evosax` 0.3.2, 2026-10-11 | Apache-2.0 | Evolution strategies in **JAX**; ask/eval/tell under jit/vmap/lax.scan; **37 strategies** | **Actively maintained.** 804 stars, **1 open issue.** ⚠️ **0.3.x is an API rewrite — pre-0.3 code will not run.** Cite Lange, arXiv:2212.04180 |
| **EvoJAX** | `evojax` 0.2.17, 2024-06-18 | Apache-2.0 | Hardware-accelerated neuroevolution in JAX | ⚠️ **ARCHIVED** (`archived: true`). **Do not recommend — point users at evosax** |
| **QDax** | `qdax` 0.5.0, 2025-05-27 | MIT | Quality-Diversity + population-based RL in JAX; MAP-Elites, CMA-ME/MAE, PGA-ME, Brax | **Low activity / near-dormant.** Cite Chalumeau, Lim et al., *JMLR* 25(108):1–16, 2024 (arXiv:2202.01258) |
| **pyribs** | dist name **`ribs` 0.12.1**, **2026-11-07** ⚠️ (**the PyPI project `pyribs` is a dead 0.0.2 stub from 2023 — `pip install ribs`**) | MIT | "Bare-bones" quality-diversity: **Archive / Emitters / Scheduler** ask-tell; CMA-ME, CMA-MAE, DQD | **Actively maintained.** **5 open issues.** Cite Tjanaka et al., GECCO '23, doi:10.1145/3583131.3590374 |
| **Optuna** | `optuna` **5.0.0**, 2026-09-07 | MIT | Define-by-run hyperparameter optimisation with pruning, storage, dashboards | **Extremely active.** 15,037 stars |
| **scikit-opt** | 0.6.6, **2022-01-14** | MIT | Grab-bag: GA, PSO, SA, ACA, immune, AFSA, DE, TSP helpers | **Stale for releases.** 6,727 stars (**popularity >> activity**), 77 open issues, **~4 years without a PyPI release.** Teaching/quick scripts only |
| **mealpy** | 3.0.3, 2025-08-16 | MIT | "World's largest" metaheuristic collection — **233 algorithms** behind a uniform interface | **Slowing.** ⚠️ **Caveat worth printing: a library whose selling point is 233 nature-inspired metaheuristics is exactly the population the center-bias and metaphor critiques indict.** Cite Van Thieu & Mirjalili, doi:10.1016/j.sysarc.2023.102871 |
| **Platypus** | `platypus-opt` 1.4.1, **2024-10-07** | **GPL-3.0** (viral — matters commercially) | Pure-Python multi-objective EC with a clean `experimenter` | **Maintained, release-quiet.** **0 open issues**, but `pip install` gets you a 2024 build; pin from git. ⚠️ Algorithm list unverified |
| **SciPy** | `scipy` **1.18.1**, 2026-08-21 | BSD-3-Clause | **The zero-install baseline**: `differential_evolution` and `dual_annealing` | **Rock solid.** **Use as the control arm: "better than `scipy.optimize.differential_evolution` with its defaults" is the minimum bar a new method should clear** |

Adjacent: `pygmo` 2.20.0 (MPL-2.0; ESA) — C++/Python **island-model parallel** optimisation. `smac` **2.4.1** (BSD-3) — algorithm configuration. `botorch` 0.18.1, `ax-platform` 1.3.1 — Bayesian alternatives.

### Which to reach for

| Situation | Reach for | Why |
|---|---|---|
| Continuous black-box, ~2–100 dims, smooth-ish, no gradients | **pycma** (`cma` 4.5.0) | Invariance properties + the best-tuned defaults in the field; ask-and-tell for custom loops |
| Same, zero new dependencies, defensible baseline | **`scipy.optimize.differential_evolution`** | Ships with SciPy; `workers=-1` parallelism; constraints + integrality |
| "Just give me something that works" | **Nevergrad `NgIohTuned`** (per its own docs) or scipy DE | Automatic competence-map selection from (budget, workers, dimension, noise, discreteness) |
| Multi-objective / many-objective, indicators, constrained MOO | **pymoo 0.6.2** | Broadest documented MOEA set, indicators, constraint strategies, visualisation; most actively maintained |
| Multi-objective in Java, or a published experimental framework | **jMetal 7.11** / jMetalPy 1.10.0 | `jmetal-lab` experimenter + statistics; component-based templates; HypE/IBEA/ZCAT |
| GP, or any non-standard representation | **DEAP** (Python) or **ECJ 28** (Java) | DEAP for `PrimitiveSetTyped` + lexicase + double-tournament parsimony; ECJ for set-based strongly-typed GP, parameter-file experiments, island models. **Jenetics** for type-safe immutable Java with `jenetics.prog` |
| "A GA around this fitness function by lunchtime" | **PyGAD** | Smallest distance from idea to running GA; `kerasga`/`torchga` for NN weights |
| GPU / massive-population neuroevolution | **evosax** (JAX) or **EvoTorch** (PyTorch, dormant) | ⚠️ **Not EvoJAX — it is archived** |
| Quality-diversity / "a diverse archive, not one optimum" | **pyribs** (CPU) or **QDax** (JAX, low activity) | Archive/Emitter/Scheduler is the cleanest mental model |
| Hyperparameter tuning of an ML model | **Optuna 5.0.0** — *not* a hand-rolled EA | Pruning (ASHA/Hyperband/Wilcoxon), storage, resumption, dashboards, and `CmaEsSampler`/`NSGAIISampler` if you still want an evolutionary sampler |
| Tuning the parameters of *your own* algorithm | **irace** or **SMAC3 2.4.1** | Racing / model-based configuration with a declared, countable budget |
| Benchmarking a continuous optimiser for publication | **COCO** (`coco-experiment` + `cocopp`) and/or **IOHexperimenter (`ioh` 0.4.0)** | Below |

---

## Default starting configurations

### CMA-ES — verified by reading pycma master source

- **Population**: `popsize='4 + 3 * math.log(N)'` → **λ = 4 + floor(3 ln n)**. There is also a multiplier `popsize_factor='1'`. DEAP independently ships the same formula, and Nevergrad's NGOpt uses it as its parallelism threshold — **the formula is the field's common currency.**
- **Parents**: `CMA_mu='None  # default is popsize // 2'` → **μ = floor(λ/2)**.
- **Weights** (`cma/recombination_weights.py`): raw weights are **`w'_i = ln((λ+1)/2) − ln i`, for i = 1..λ**; the positive part is normalised to sum to **+1** and the negative part to **−1** (active/negative-weight CMA), with `finalize_negative_weights(dimension, c1, cmu)` guaranteeing positive-definiteness of C. ⚠️ **Correction worth making: the current default is `ln((λ+1)/2) − ln i`, NOT the older `ln(μ+0.5) − ln i` form from Hansen & Ostermeier (2001).** They are close but not identical; quote the implemented one.
- **Initial step size σ₀** — pycma's own docstring: *"initial standard deviation. The problem variables should have been scaled, such that **a single standard deviation on all variables is useful and the optimum is expected to lie within about `x0` ± `3*sigma0`**. Often one wants to check for solutions close to the initial point… In this case, a much smaller `sigma0` is advisable."* So **σ₀ ≈ range/4 to range/6**. The tutorial's box-initialisation rule is **σ = 0.3(b−a)**. ⚠️ **Scale your variables first: CMA-ES takes a *scalar* σ₀ (enforced with a ValueError) and learns the rest.**
- **Restarts — IPOP and BIPOP, both in `cma.fmin2`:** `restarts=0`, `incpopsize=2` (*"multiplied by a factor of two … like in IPOP-CMA-ES"*); `restarts` may be a dict with `maxrestarts=9`. `bipop=False` — *"BIPOP is a special restart strategy switching between two population sizings — small … and large (progressively increased as in IPOP)… **the recommended setting is `restarts <= 9` and `x0` passed as a `callable`** that generates randomized initial solutions."*

  **Practical recipe for multimodal problems:**

  ```python
  cma.fmin2(f, lambda: np.random.uniform(lo, hi, n), sigma0,
            {'bounds': [lo, hi]}, restarts=9, bipop=True)
  ```
- **Hansen's own advice**: do not change the strategy parameters; the only knobs are **increasing λ** and (on noisy functions) **decreasing `alpha_cov`**. **Decreasing λ is explicitly not recommended.**

### Differential evolution — shipped defaults, verified from source

- **`scipy.optimize.differential_evolution`** (SciPy 1.18.1): `strategy='best1bin'`, `maxiter=1000`, **`popsize=15`** — *"A multiplier for setting the total population size. The population has `popsize * (N − N_equal)` individuals"*, i.e. **15 × D by default**; **`mutation=(0.5, 1)`** — ⚠️ **a tuple means DITHERING: *"The mutation constant for that generation is taken from U[min, max)"*, so F ~ U[0.5, 1) *per generation***; **`recombination=0.7`** (= CR); `tol=0.01`, `init='latinhypercube'`, `updating='immediate'`, **`polish=True`** (an L-BFGS-B / trust-constr finisher — ⚠️ **note this means scipy's DE is a memetic algorithm by default**), `workers=1`, `integrality=None`. References include Storn & Price 1997 and **Lampinen 2002** for constraint handling.
- **`pymoo` DE**: `pop_size=100`, `variant="DE/best/1/bin"`; `Variant(selection="best", n_diffs=1, F=0.5, crossover="bin", CR=0.2, jitter=False, prob_mut=0.1)` with declared tuning ranges `F ∈ (0.4, 0.7)` and `CR ∈ (0.2, 0.8)`, plus a polynomial mutation `PM(at_least_once=True)` with `eta=20, prob=0.1` layered on.

  ⚠️ **Two things practitioners get bitten by: pymoo's default is DE/best/1/bin, NOT the textbook DE/rand/1/bin, and its default CR = 0.2 is LOW — if your variables interact, raise it.**
- ⚠️ **Storn & Price's own guidance** — NP between 5D and 10D, F = 0.5 as a good first choice with F ∈ [0.4, 1.0] and F > 1 rarely useful, CR = 0.9 or 1.0 for fast convergence — **is unverified here**: the paper is paywalled and Storn's classic parameter page now returns HTTP 403. **Cite the paper, not the dead page.** (The widely quoted "typical settings NP=10n, CR=0.9, F=0.8" *is* verified from a secondary source.)
- **Reach for L-SHADE-class defaults instead of hand-tuning F and CR**: `N^init = 18 × D` with linear reduction to 4, H = 6, p = 0.11, archive 2.6×, current-to-pbest/1/bin. If you must use plain DE: **NP = 10D, F = 0.5 (or dither U[0.5,1)), CR = 0.9 for non-separable / 0.1 for separable**, and **treat CR as the single most important knob.**

### Binary / combinatorial GA — be explicit about what is evidence and what is folklore

- ✅ **Has theoretical backing: `p_m = 1/L`** (one expected bit-flip per offspring). Droste, Jansen & Wegener, *TCS* 276(1–2):51–81, 2002 — the (1+1) EA with rate 1/n optimises OneMax and every linear function in `Θ(n log n)`. And **Witt 2013** proves **p = 1/n is optimal for the whole class of linear functions**. Tighten with Doerr, Johannsen & Winzen, "Multiplicative Drift Analysis," *Algorithmica* 64(4):673–697, 2012. ⚠️ Earlier empirical arguments (Mühlenbein PPSN II 1992; Bäck ICGA 1993) are unverified.
- ⚠️ **Received wisdom, repeated far more often than it is checked: population 50–200, tournament size 2–5, two-point or uniform crossover with `p_c ≈ 0.7–0.9`, elitism 1–2. These are reasonable starting points and nothing more; they come from a small number of 1970s–80s studies on tiny test suites (≤5 functions, 10–30 bits), and the field has repeatedly failed to reproduce "optimal" settings across problem classes. Say so.**
- **The classic parameter studies, and what could and could not be verified:**
  - ⚠️ **De Jong (1975)**, PhD diss., Michigan. The F1–F5 test bed and the commonly quoted settings (population 50–100, `p_c = 0.6`, `p_m = 0.001`, generation gap, elitism) are **unverified: the dissertation is not online in any reachable source.**
  - ⚠️ **Grefenstette, "Optimization of Control Parameters for Genetic Algorithms," *IEEE TSMC* 16(1):122–128, 1986**, doi:10.1109/TSMC.1986.289288 — **citation fully verified, but the paper is closed access** (OpenAlex: `oa_status: "closed"`) and the text could not be obtained. **The commonly quoted values (online: pop ~30, `p_c` ~0.95, `p_m` ~0.01; offline: a different larger-population/lower-crossover set) are unverified. Either obtain the PDF or publish the values with an explicit hedge.** **What *is* safe and important to state: Grefenstette's method was a meta-GA tuning a GA, and he found *different optima for the online and the offline performance measure*** — which is itself the methodological lesson: **there is no single "best" parameter set; the answer depends on what you are measuring.** (Compare De Jong 1993's point that the two objectives actively *trade off*: *"many of the strong sampling biases introduced into GA-based optimizers are known to negatively affect cumulative (online) payoff."*)
  - ⚠️ **Schaffer, Caruana, Eshelman & Das, ICGA '89, pp. 51–60.** Unverified (ICGA is not in Crossref). The commonly quoted conclusion — a factorial study over ~8,000 configurations recommending population 20–30, `p_c` 0.75–0.95, `p_m` 0.005–0.01 — is unverified. **The one robust, often-cited finding worth repeating is that small populations with relatively high mutation did surprisingly well**, which contradicted the then-prevailing schema-theory advice for large populations.
  - Selection pressure, properly cited: Goldberg & Deb, FOGA 1, pp. 69–93, 1991. Takeaway: **tournament size k sets the takeover time**; k = 2 is gentle, k = 7 is aggressive (ECJ's default), and roulette selection is scale-dependent and should generally be avoided.
- ⚠️ **A reference point from a real implementation that should puncture the folklore: ECJ's `simple.params` ships `pop.subpop.0.size = 1024`** and `select.tournament.size = 7` (both verified from source) — **a useful reminder that "50–200" is folklore, not consensus.**

### Multi-objective (NSGA-II) — actual shipped defaults, and they disagree between libraries

| | **pymoo 0.6.2** | **jMetal 7.x** (`NSGAIIRunner.java`) | Deb et al. 2002 as commonly reported |
|---|---|---|---|
| Population | `pop_size=100` | `populationSize = 100` | 100 |
| Crossover | **`SBX(eta=15, prob=0.9)`** | **`SBXCrossover(0.9, 20.0)`** | SBX, `p_c = 0.9`, `η_c = 20` |
| Mutation | `PM(eta=20)` | `PolynomialMutation(1.0/numberOfVariables(), 20.0)` | polynomial, `p_m = 1/n`, `η_m = 20` |
| Selection | binary tournament, `tournament_type="comp_by_dom_and_crowding"` (falls back to crowding distance when domination is indecisive; compares by CV first if either is infeasible) | `BinaryTournamentSelection(RankingAndCrowdingDistanceComparator)` | binary tournament on (rank, crowding) |
| Survival | `RankAndCrowding()` (crowding func `"cd"`) | ranking + crowding distance | ditto |
| Budget in the shipped example | `DefaultMultiObjectiveTermination()` | **`setMaxEvaluations(25000)`** | 25,000 |

⚠️ **The η_c discrepancy is real: pymoo defaults to η_c = 15; jMetal defaults to η_c = 20.** Both are inside the usual 15–20 band, **but if you compare pymoo's NSGA-II against jMetal's you are not comparing the same algorithm. State the operator parameters in any paper.**

⚠️ **And pymoo's mutation probability is subtler than it looks, and is widely misread.** `PolynomialMutation.__init__(self, prob=0.9, eta=20, at_least_once=False)`; that `prob=0.9` goes to `Mutation.__init__` and is **the probability that an individual is mutated at all** (`mut = random_state.random(size=n_mut) <= prob`). The **per-variable** probability comes from `Mutation.get_prob_var`: `prob_var = self.prob_var if self.prob_var is not None else min(0.5, 1/problem.n_var)` — **i.e. pymoo's effective per-variable mutation probability is `min(0.5, 1/n)`, matching the canonical 1/n, but each individual is only mutated at all with probability 0.9.** `SimulatedBinaryCrossover` separately defaults `prob_var=0.5, eta=15, prob_exch=1.0, prob_bin=0.5`.

**Recipe:** NSGA-II, **population 100, SBX `p_c = 0.9` with `η_c = 20`, polynomial mutation `p_m = 1/n` with `η_m = 20`, binary tournament on (rank, crowding), 25,000 evaluations** is the canonical configuration, and **jMetal's shipped example implements it exactly.** For > 3 objectives switch to NSGA-III/U-NSGA-III or MOEA/D and choose reference directions deliberately.

### Genetic programming — Koza's tableau as actually implemented

Verified from ECJ's `ec/gp/koza/koza.params`, the closest thing to an executable transcription of Koza (1992).

- Breeding pipeline: `source.0 = ec.gp.koza.CrossoverPipeline, prob = 0.9`; `source.1 = ec.breed.ReproductionPipeline, prob = 0.1`. **90% crossover / 10% reproduction, confirmed.**
- **`gp.koza.xover.maxdepth = 17`** and `gp.koza.mutate.maxdepth = 17` — **the famous depth-17 limit, confirmed as "the default for Koza and lil-gp."** `gp.koza.xover.tries = 1` with the comment *"This is the default for Koza and lil-gp, though it's a little wimpy."*
- Initialisation: `HalfBuilder` with **`min-depth = 2`, `max-depth = 6`, `growp = 0.5`** — **ramped half-and-half, depth 2–6, 50/50 grow/full, confirmed.**
- Node selection: **`gp.koza.ns.terminals = 0.1`, `nonterminals = 0.9`, `root = 0.0`** — Koza's fix for crossover degenerating into leaf-swapping.
- Subtree-mutation builder: `gp.koza.grow.min-depth = max-depth = 5` — *"the Koza-standard subtree mutation GROW values… which I don't like very much, but hey, that's the standard."*
- ⚠️ **Selection: ECJ deliberately deviates.** File header: *"We use Tournament selection instead of Koza-style Fitness-proportionate selection because fitness-proportionate selection, well, is kinda icky."* `select.tournament.size = 7`. **So Koza's tableau specifies fitness-proportionate selection and the leading implementation refuses to ship it. That is a good, quotable illustration of "received wisdom vs what practitioners actually do."**
- Population: Koza's tableau says **500**; ECJ's `simple.params` ships **1024**; generations: Koza's 51 (= gen 0 + 50).

**What the Field Guide actually recommends** (Poli, Langdon & McPhee 2008, §3.4), verbatim:

- *"The most important control parameter is the population size."*
- *"**It is impossible to make general recommendations for setting optimal parameter values, as these depend too much on the details of the application.** However, genetic programming is in practice robust, and it is likely that many different parameter values will work."*
- *"It is common to create the initial population randomly using **ramped half-and-half … with a depth range of 2-6**."*
- *"**Traditionally, 90% of children are created by subtree crossover. However, the use of a 50-50 mixture of crossover and a variety of mutations … also appears to work well.**"*
- *"one prefers to have the largest population size that your system can handle gracefully; **normally, the population size should be at least 500, and people often use much larger populations.**"*
- *"**Typically, the number of generations is limited to between ten and fifty**; the most productive search is usually performed in those early generations."*
- *"The folk wisdom on population size is to make it as large as possible, but there are those who suggest using many runs with much smaller populations instead."*

⚠️ **And note: the Field Guide does not mention the depth-17 limit anywhere.** It *does* warn that hard limits applied by returning a parent are harmful, and its recommended fix is: **don't return the parent — either return the oversize offspring with fitness 0, or declare the operation failed and retry.** ⚠️ **Its own worked example tableau (Table 4.1, p. 31) is deliberately tiny** — population 4, 50% crossover / 25% reproduction / 25% subtree mutation, ramped half-and-half depth 1–2, fitness-proportionate non-elitist. **Do not mistake it for a recommendation.**

### When to add local search (memetic)

Whenever a cheap, effective local improver exists. **For most combinatorial problems the competitive EAs *are* memetic**, and note that `scipy.optimize.differential_evolution` is memetic by default (`polish=True`).

---

## How not to fool yourself

### Repetitions and seeds — the actual conventions

Verified from the primary technical reports (downloaded from P. N. Suganthan's GitHub and text-extracted):

- **CEC 2017 bound-constrained**, §2.1, verbatim: *"Problems: **30 minimization problems**"*; *"Dimensions: **D=10, 30, 50, 100**"*; *"**Runs / problem: 51** (Do not run many 51 runs to pick the best run)"*; *"**MaxFES: 10000*D**"*; *"**Search Range: [-100,100]^D**"*; *"Termination: Terminate when reaching MaxFES or the error value is smaller than **10^-8**."* Record error at 14 checkpoints per run; report **best, worst, mean, median, std** over the 51 runs. *"All test functions are **shifted** to o and scalable."*
- **CEC 2022**, §2.1: *"Problems: **12 minimization problems**"*; *"Dimensions: **D = 10 and 20**"*; *"**Runs / problem: 30**"*; *"**MaxFES: 200,000** (D=10) / **1,000,000** (D=20)"*; **1000 pre-generated uniform random seeds in `input_data/Rand_Seeds.txt`**. ⚠️ **Note the trend: the competition itself moved toward fixed, published seeds. Do the same.**
- **COCO/BBOB**: **15 instances** per function per dimension. ⚠️ **Instances are randomised shifts/rotations, so "15 instances" plays the role of "15 independent runs" *while also varying the problem* — a strictly better design than 15 runs on one fixed instance.** Dimensions 2, 3, 5, 10, 20, 40.
- **30 runs** is the common journal default; **it is a convention, not a derivation.** Prescription: **report the number of runs, the seeding scheme, and the budget in the same sentence**, and pick repetitions from the precision you need on the statistic you report.
- **Pin and publish seeds.** Mechanically: `rng = np.random.default_rng(seed)` per run with `seed = base + run_index`. **pymoo 0.6.2 threads an explicit `random_state` through every operator (`@default_random_state`, `algorithm.random_state`) precisely so this is possible — use it.**

### Report distributions, not best-of-N

Report **median and IQR** (or the five-number summary — CEC's own template asks for best, worst, mean, median, std), **box plots**, and **ECDFs of runtime** (the COCO convention: the fraction of (function, target, instance) triples solved within x evaluations). Quantile bands over the convergence curve beat a single mean curve.

**Why best-of-N is a biased, budget-inflating estimator:** the maximum of N i.i.d. draws is a biased estimate of the distribution's location — `E[max of N] > E[X]`, and it increases **monotonically in N**, so "best of 50" and "best of 10" are **not comparable quantities**, and **the bias grows with the *variance* of the algorithm, which rewards erratic algorithms.** Worse, if you ran N restarts to get it, your true budget was `N × per-run budget`, so you are comparing N·B evaluations of method A against B of method B. **If restarts are genuinely part of your method, say so and count them in the budget** — which is exactly what ERT / simulated restarts do correctly in COCO. **This is the failure mode the CEC'17 TR tried to pre-empt with "do not run many 51 runs to pick the best run."**

### Fair budget: count fitness evaluations

- **Count function evaluations, not generations.** Generations are not comparable across algorithms with different population sizes (λ = 4+3 ln n for CMA-ES vs 100 for pymoo's NSGA-II vs 15D for scipy's DE — **a "generation" differs by an order of magnitude**), nor across algorithms with **population-size adaptation** (L-SHADE's linear reduction, IPOP/BIPOP restarts).
- **Do not use wall-clock as the primary axis**: it confounds implementation language (C++ vs pure Python vs JAX-on-GPU), vectorisation, and parallelism, **none of which is a property of the algorithm.** Both CEC and COCO measure in evaluations.
- ⚠️ **The honest caveat:** when evaluation is **cheap**, per-evaluation algorithm overhead is a real cost and **evaluation-count comparison flatters heavy algorithms** (full-covariance CMA-ES is `O(n²)` per sample and `O(n³)` amortised for the eigendecomposition; surrogate-assisted methods can spend more time on the model than on the objective). **Report both**: evaluations as the primary axis, plus wall-clock **and** the hardware/language. **CEC's TRs institutionalise this with the algorithm-complexity protocol**: `T0` = a fixed arithmetic loop, `T1` = 200,000 raw evaluations of F18, `T̂2` = mean over 5 runs of the algorithm doing 200,000 evaluations; report **`(T̂2 − T1)/T0`** per dimension — verified in the CEC'17 TR and in the L-SHADE paper, which reports exactly that table.

### Statistical testing

- **Two algorithms, same problems (paired): Wilcoxon signed-rank test.** Wilcoxon, *Biometrics Bulletin* **1(6):80–83, 1945**, doi:10.2307/3001968.
- **Two algorithms, independent runs on one problem (unpaired): Mann–Whitney U / Wilcoxon rank-sum.** This is what the DE literature uses per-function: L-SHADE's table caption reads *"using the Wilcoxon rank-sum test (significantly, p < 0.05)."*
- **Many algorithms over many problems: Friedman test** on per-problem ranks, then post-hoc **Nemenyi** (all-pairs) or **Holm / Hochberg** (one control vs rest), with critical-difference diagrams. **Demšar, "Statistical Comparisons of Classifiers over Multiple Data Sets," *JMLR* 7(1):1–30, 2006.** ⚠️ **Demšar's own recommendation is the non-parametric route, and he is explicit that Holm/Hochberg *dominate* Nemenyi when there is a control method.**
- The EC-specific tutorial: **Derrac, García, Molina & Herrera, *SWEVO* 1(1):3–18, 2011**, doi:10.1016/j.swevo.2011.02.002. Updates: Carrasco, García, Rueda, Das & Herrera, *SWEVO* **54:100665, 2020**; LaTorre, Molina, Osaba, Poyatos et al., *SWEVO* **67:100973, 2021**.
- **Effect sizes, and the SBSE standard: Vargha & Delaney, *Journal of Educational and Behavioral Statistics* 25(2):101–132, 2000**, doi:10.3102/10769986025002101. **`Â12 = P(A > B) + 0.5·P(A = B)`**; 0.5 = no effect, conventional thresholds **0.56 / 0.64 / 0.71** for small / medium / large. **Â12 is the right default for EC because it is a probability of superiority over runs, needs no normality, and is invariant to monotone transforms of the fitness scale — which matters enormously when fitness is log-distributed error.**
- The SBSE guides, with titles corrected: **Arcuri & Briand, "A practical guide for using statistical tests to assess randomized algorithms in software engineering," ICSE '11, pp. 1–10**, doi:10.1145/1985793.1985795; extended as **"A Hitchhiker's guide to statistical tests for assessing randomized algorithms in software engineering," *STVR* 24(3):219–250**, doi:10.1002/stvr.1486 — ⚠️ Crossref dates it 2012 (online first); issue 24(3) is 2014. **Cite as "2014 (online 2012)."**

**The community consensus document, and the single best citation for this whole section: Bartz-Beielstein, Doerr, van den Berg, Bossek, Chandrasekaran, Eftimov, Fischbach, Kerschke, La Cava, López-Ibáñez, Malan, Moore, Naujoks, Orzechowski, Volz, Wagner & Weise (17 authors), "Benchmarking in Optimization: Best Practice and Open Issues," arXiv:2007.03488.** ⚠️ **No journal version found — OpenAlex has only the preprint.**

Abstract, verbatim: *"This survey compiles ideas and recommendations from more than a dozen researchers …. The article discusses eight essential topics in benchmarking: **clearly stated goals, well-specified problems, suitable algorithms, adequate performance measures, thoughtful analysis, effective and efficient designs, comprehensible presentations, and guaranteed reproducibility.**"* Provenance: *"This joint initiative was established during the **Dagstuhl seminar 19431 on Theory of Randomized Optimization Heuristics**, which took place in October 2019."*

**The checklist (verbatim, §10) — their headline deliverable:** *"1. **goals**: did the authors clearly state the reasons for this study? 2. **problems**: is the selection of problem instances well motivated and justified? 3. **algorithms**: do comparisons include relevant competitors? 4. **performance**: is the choice of the performance measure adequate? 5. **analysis**: are standards from statistics considered? 6. **design**: does the experimental setup enable efficient and fair experimentation? What measures are taken to avoid 'cherry-picking results'? 7. **presentation**: are the results well organized and explained? 8. **reproducibility**: data and code availability?"*

Their stance: *"it is not our intention to dictate specific test statistics, experimental designs, or performance measures. Instead, we claim that **publications in EC would improve, if authors explain, why they have chosen this specific measure, tool, or design.**"*

**The best diagnosis quote in the whole literature** (§1), verbatim: *"**Gent and Walsh (1994) stated that the empirical study of algorithms is a relatively immature field – and we claim that this situation has unfortunately not significantly changed in the last 25 years.** … EC has not agreed upon general methodology for performing benchmark studies like the fields of statistical Design of Experiments (DOE) or data mining. … **The question remains: why are minimum standards not considered in every paper submitted to EC conferences and journals?** … One answer might be: **setting up a sound benchmark study is very complicated.** … Another answer might be: **practical guidelines are missing.**"*

A nice internal detail: §1 contains a **Schwefel (1975) PhD-thesis epigraph** — *"The extremely large and constantly increasing number of optimization methods inevitably leads to the question of the best strategy. There does not seem to be a clear answer. Because, if there were an optimal optimization process, all other methods would be superfluous…"* — **i.e. a 1975 statement of the NFL intuition, 22 years before Wolpert & Macready.**

**Prescription:** (a) pre-register the comparison (which problems, which budget, how many runs) **before** looking at results; (b) use the **paired** test when runs are paired and the unpaired test otherwise; (c) **always** correct for multiplicity when you run a test per function (Holm is cheap and uniformly better than Bonferroni); (d) **always** publish an effect size next to every p-value — **with 51 runs a p < 0.05 can correspond to an Â12 of 0.57, i.e. nothing**; (e) say explicitly what the significance test is testing (usually "this algorithm beats that one on *these* functions at *this* budget", which is **not** "this algorithm is better").

### Tuning on the test problem

**The rule: the tuning budget counts against the algorithm.** If you spent 1,000 configuration evaluations × 10,000 evaluations each to find your F and CR, your method cost `10⁷ + B`, not B. **An untuned competitor at budget B is not a fair comparison.**

✅ **L-SHADE is the model of honesty here:** Tanabe & Fukunaga state outright that they tuned `N^init`, `r_arc`, `p` and `H` with **ParamILS**, capped at **1,000 configurations evaluated**, taking *"approximately 4 hours"*, and they report **both** the pre-tuning defaults **and** the tuned values — then note the tuned version is only *"slightly better"* than the defaults. **Copy that disclosure pattern.**

Also: tune on a **training** set of problems/instances and report on a **held-out** set; report performance at a budget you did not tune on; and **never tune per-function and then present a per-function table as if one algorithm produced it.**

Citations: **Eiben & Smit, "Parameter tuning for configuring and analyzing evolutionary algorithms," *SWEVO* 1(1):19–31, 2011**, doi:10.1016/j.swevo.2011.02.001 — ⚠️ **title correction: "Generalist vs specialist" is a *different* paper** (Smit & Eiben, EvoApplications 2010, doi:10.1007/978-3-642-12239-2_56). **irace**: López-Ibáñez, Dubois-Lacoste, Pérez Cáceres, Birattari & Stützle, *Operations Research Perspectives* **3:43–58, 2016**, doi:10.1016/j.orp.2016.09.002 — repo **actively maintained, last commit 2026-11-10.** **SMAC3**: Lindauer et al., *JMLR* 23(54):1–9, 2022; PyPI `smac` **2.4.1** (2026-09-10), **maintained**. ⚠️ **SPOT** (Bartz-Beielstein's Sequential Parameter Optimization Toolbox) and **ParamILS** (Hutter, Hoos, Leyton-Brown & Stützle, *JAIR* 36:267–306, 2009) — current versions / canonical citations not independently fetched.

### Reproducibility checklist

Pin seeds and publish them; publish exact budgets (**evaluations**, not generations) and the termination condition **including the target precision**; publish the library **version** and ideally a lockfile; publish the code and the **raw per-run data**, not just summary tables (COCO's and IOH's data formats exist for this and both have public archives you can deposit into); state the hardware and language when you report any timing.

⚠️ **And the reason the version matters — verified examples from this very fetch:** pymoo renamed `n_constr` → `n_ieq_constr`/`n_eq_constr` in 0.6.0; **pymoo threads an explicit `random_state` through operators in 0.6.2, so old seeded scripts produce different sequences**; evosax 0.3.x is a wholesale API rewrite; DEAP 1.4.4 swapped its hypervolume implementation to `moocore`; Nevergrad's CHANGELOG stopped being updated at v0.11.0 (2023) while the code kept changing; the latest `iohexperimenter` PyPI project is a 2021 fossil and the live package is `ioh`; and the COCO repo split in two. **A result that does not record the library version is not reproducible, no matter how good the seed hygiene.**

---

## Benchmark suites

### BBOB / COCO

- Citation: **Hansen, Auger, Ros, Mersmann, Tušar & Brockhoff, "COCO: A platform for comparing continuous optimizers in a black-box setting," *Optimization Methods and Software* 36(1):114–144, 2021**, doi:10.1080/10556788.2020.1808977. (Crossref's `issued` year is 2020 — online-first.)
- Live URLs: **`https://coco-platform.org/`**; data archive `coco-platform.org/data-archive`; GitHub org `github.com/numbbo`.
- **Current software releases** (both released the day of the fetch): **`coco-experiment` 2.8.4** (the C/Python experiment side; module `cocoex`) and **`cocopp` 2.9.2**, both BSD-3-Clause. ⚠️ **The old monolithic `numbbo/coco` repo's last tagged release is v2.6.3 (2023-04-06) — cite the split repos, not `numbbo/coco`.**
- **The `bbob` suite**, verbatim: *"24 noiseless, single-objective and scalable test functions. Each function is provided in dimensions **(2, 3, 5, 10, 20, 40)** and in **15 instances**."* The five groups:
  1. **Separable**: f1 Sphere, f2 Separable Ellipsoidal, f3 Rastrigin, f4 Büche-Rastrigin, f5 Linear Slope
  2. **Low or moderate conditioning**: f6 Attractive Sector, f7 Step Ellipsoidal, f8 Rosenbrock original, f9 Rosenbrock rotated
  3. **High conditioning and unimodal**: f10 Ellipsoidal, f11 Discus, f12 Bent Cigar, f13 Sharp Ridge, f14 Different Powers
  4. **Multi-modal with adequate global structure**: f15 Rastrigin, f16 Weierstrass, f17 Schaffer's F7, f18 Schaffer's F7 moderately ill-conditioned, f19 Composite Griewank-Rosenbrock F8F2
  5. **Multi-modal with weak global structure**: f20 Schwefel, f21 Gallagher's Gaussian 101-me Peaks, f22 Gallagher's Gaussian 21-hi Peaks, f23 Katsuura, f24 Lunacek bi-Rastrigin

  The page notes: *"Only f1 and f5 are purely convex quadratic (f1) or purely linear in the domain of interest **[-5,5]^D** (f5)."*
- Other suites: `bbob-noisy`, `bbob-biobj`, `bbob-biobj-mixint`, `bbob-boxed`, `bbob-constrained`, `bbob-largescale`, `bbob-mixint`.
- **Performance methodology — the right citation is the dedicated document, not the OMS paper**: Hansen, Auger, Brockhoff, Tušar & Tušar, "COCO: Performance Assessment," **arXiv:1605.03560**. Its abstract states the method exactly: *"an any-time performance assessment … based on **runtimes measured in number of objective function evaluations** to reach one or several quality indicator target values."* Practically: **runtime = the number of evaluations to *first* reach a target precision**; unsuccessful runs are handled by **ERT (expected running time)**, computed by **simulated restarts** over the instances; results are presented as **ECDFs of runtime** aggregated over targets × functions × instances. **The design means you report an anytime curve, not a final-value table.**
- ⚠️ **The single most underused feature: `cocopp` can fetch and compare against hundreds of officially registered algorithm data sets (`cocopp.archiving`) — you get free, correctly-measured baselines instead of re-running other people's code.**

### CEC suites — and the methodological indictment

Settings verified above. Other suites in the family (repos verified under `github.com/P-N-Suganthan`): `CEC2005`, `CEC2006`, `CEC2010-Constrained`, `CEC-2010-LSGO`, `CEC2013`, `CEC2014`, `CEC2015`, `CEC2017`, `CEC2019` (100-digit), `2020-Bound-Constrained-Opt-Benchmark`, `2021-SO-BCO`, `2022-SO-BO`, `2024-CEC`, `2025-CEC`, `2026-CEC`. ⚠️ The CEC'13 LSGO report (Li, Tang, Omidvar, Yang & Qin, RMIT Technical Report, 2013) is unverified — it could not be fetched and is not in Crossref.

**The criticism: Kudela, "A critical problem in benchmarking and analysis of evolutionary computation methods," *Nature Machine Intelligence* 4(12):1238–1245**, published **2022-12-12**, doi:10.1038/s42256-022-00579-0 (Crossref-verified: single author, 43 references; 119 citations per Semantic Scholar).

⚠️ **The full text is paywalled and not open access** (Unpaywall: `is_oa: false`; Semantic Scholar's abstract is *"elided by the publisher"*), **so the paper's own statement of its experiment could not be read.** What *can* be stated from a primary source is the author's framing in his follow-up:

**Kudela, "The Evolutionary Computation Methods No One Should Use," arXiv:2301.01984**, abstract verbatim: *"The **center-bias (or zero-bias) operator** has recently been identified as one of the problems plaguing the benchmarking of evolutionary computation methods. **This operator lets the methods that utilize it easily optimize functions that have their respective optima in the center of the feasible set.** In this paper, we describe a simple procedure that can be used to identify methods that incorporate a center-bias operator and use it to investigate **90 evolutionary computation methods** that were published between 1987 and 2022. We show that **more than half (47 out of the 90)** of the considered methods have the center-bias problem. We also show that the center-bias is a relatively new phenomenon (with the first identified method being from 2012), but its inclusion has become extremely prevalent in the last few years."*

**The mechanism is mechanically obvious once stated:** most CEC-family suites use the symmetric domain **[−100,100]^D** and place the shifted optimum relatively near 0; **an operator that (even incidentally) pulls candidates toward the domain centre — e.g. averaging/contraction toward the midpoint, or a "best + random" update that regresses to the mean of the box — gets free progress that has nothing to do with the objective.** Hence **a trivially center-biased algorithm can beat published metaheuristics on these suites.**

⚠️ **Pending full-text access: the exact list of suites the NMI paper indicts and the exact construction of its demonstration algorithm. State the center-bias claim, cite the NMI paper for it, cite arXiv:2301.01984 for the 47/90 figure — do not invent experimental detail.**

**Practical consequence: a CEC-only evaluation is not sufficient evidence.** Report BBOB/COCO (whose functions are randomly shifted **per instance** and whose optima are **not** centred), or at minimum re-run with a random shift/offset of the domain and show the result survives. (And recall the Piotrowski finding: a significant **negative** correlation between performance on CEC 2020 and on the classical real-world CEC 2011 set.)

### IOHprofiler / IOHexperimenter

- Project: **`https://iohprofiler.github.io/`**; hosted analyzer **`https://iohanalyzer.liacs.nl/`**.
- Components: **IOHexperimenter** (suite generation + data production), **IOHanalyzer** (statistics + visualisation, fixed-target **and** fixed-budget, web UI + R API), **IOHproblem**, **IOHdata** (datasets, **including BBOB/COCO and Nevergrad data**), **IOHalgorithm**.
- Current software: PyPI **`ioh` 0.4.0**, uploaded **2026-11-02** — ⚠️ **this is the modern package; the old `iohexperimenter` PyPI project is frozen at 0.2.9.2 from 2021 — don't cite that one.** GitHub: 72 stars, last commit **2026-11-09**, BSD-3-Clause. **Maintenance verdict: actively developed.**
- Suites: **PBO** — 25 pseudo-Boolean problems `f: {0,1}^d → R` (OneMax, LeadingOnes, W-model transformations, Ising, MaxCut, NK-landscapes, LABS…); **BBOB** — the same 24 continuous functions, re-implemented; plus submodular and real-world additions. ⚠️ **The PBO suite is IOH's real differentiator: COCO has no discrete/pseudo-Boolean counterpart, so if your algorithm is combinatorial, IOH is the platform.**
- Citations: general/profiler — **Doerr, Wang, Ye, van Rijn & Bäck, "IOHprofiler: A Benchmarking and Profiling Tool for Iterative Optimization Heuristics," arXiv:1810.05281** ⚠️ (**note the exact title — this is NOT the IOHexperimenter paper**); experimenter — **de Nobel, Ye, Vermetten, Wang, Doerr & Bäck, *Evolutionary Computation* 32(3):205–210, 2024**, doi:10.1162/evco_a_00342; analyzer — **Wang, Vermetten, Ye, Doerr & Bäck, *ACM TELO* 2(1):1–29, 2022**, doi:10.1145/3510426.

### Combinatorial and multi-objective suites

⚠️ All four hosts below were **not** fetched — verify URLs before publishing.

- **TSPLIB** — Reinelt, "TSPLIB — A Traveling Salesman Problem Library," *ORSA Journal on Computing* 3(4):376–384, 1991. Host: `comopt.ifi.uni-heidelberg.de/software/TSPLIB95/` (it has moved before).
- **OR-Library (ORLIB)** — Beasley, *JORS* 41(11):1069–1072, 1990. Host: `people.brunel.ac.uk/~mastjjb/jeb/info.html`.
- **MaxSAT Evaluations** and the **Pseudo-Boolean (PB) Competition** — annual, with public instance archives; the right venues for discrete-optimisation comparisons.
- Multi-objective: ZDT, DTLZ, WFG, RE/RWA, ZCAT — see `multi-objective.md`. pymoo, jMetal/jMetalPy and Platypus all ship the classics, and reference fronts are provided (`get_problem("zdt1").pareto_front()` in pymoo; `resources/referenceFronts/*.csv` in jMetal).

---

## Common failure modes

### Premature convergence

**Detection — instrument these, don't eyeball the best-fitness curve:**

- **Population fitness variance / std** → near-zero while far from the target means the population has **collapsed**, not converged. Cheap, and the first thing to log.
- **Mean pairwise genotypic distance** (Hamming for binary, Euclidean for real, tree-edit for GP) → distinguishes **genotypic** collapse from a legitimately converged-but-diverse population. ⚠️ **Fitness variance alone cannot: neutral networks give you identical fitness with intact diversity.**
- **Allele-frequency entropy** per locus, `Σ −p log p` over the population → entropy collapse at a locus means that bit is **fixed** and crossover can no longer recover it. The classic mechanism is **hitchhiking** — a deleterious allele fixed because it rode along with an early strong building block (**exactly what the Royal Road experiments diagnosed**).
- **For GP specifically**, the Field Guide gives a usable threshold: *"[if the number of distinct individuals in] the population falls below 90% of the population size, this may indicate that there is a problem. However, a high variety does not mean the opposite."*
- **For CMA-ES**, σ and the condition number of C are the natural instruments: pycma triggers `tolfun`, `tolfunhist`, `tolx`, **`tolstagnation`** (`int(100 + 100*N**1.5/popsize)` iterations without improvement), `tolupsigma`, `conditioncov_alleviate`. ⚠️ **A run stopped by `tolstagnation` with σ *not* small is the stagnation signature, and that is exactly when you want a restart.**
- **Takeover time**: measure how many generations until one genotype's share exceeds, say, 90%, and compare against the selection-scheme prediction. ⚠️ **If takeover happens much faster than your mutation can generate novelty, you have too much selection pressure, full stop.**

**Remedies, roughly in order of "try this first":**

1. **Lower selection pressure** — tournament size 7 → 2, or drop fitness-proportionate selection entirely. **Cheapest, most reliable intervention.**
2. **Restarts, with increasing population** — **the single most effective and most under-used remedy**, and the one with competition evidence behind it: IPOP-CMA-ES and BIPOP, both built into `cma.fmin2`. ⚠️ **Restarts also convert a premature-convergence problem into a budget-allocation problem, which is much easier to reason about — and Luby's universal schedule is the theoretical backbone.**
3. **Larger population** — see below for why the required size is a **computable quantity**, not a guess.
4. **Island / multi-deme models with migration** — ECJ ships asynchronous island models over TCP/IP, LEAP ships island migration + async Dask, DEAP has `deap/tools/migration.py`. Knobs: topology, interval, rate. ⚠️ **Too-frequent migration collapses the islands into one population and buys nothing.**
5. **Fitness sharing** — with the caveat that it requires choosing `σ_share`, which requires knowing the number/spacing of optima, which you don't.
6. **Crowding / deterministic crowding / restricted tournament selection** — replacement-based niching, which avoids the `σ_share` problem entirely.
7. **Explicitly optimise for diversity instead of patching it** — quality-diversity (MAP-Elites / CMA-ME / CMA-MAE via pyribs) reframes the problem so you ask for an **archive** of diverse high-performing solutions, and **premature convergence stops being a failure mode because diversity is in the objective.**

### A fitness function that rewards the wrong thing

This is the richest failure mode and it has a citable catalogue — **Lehman, Clune, Misevic et al. (50 authors), "The Surprising Creativity of Digital Evolution," *Artificial Life* 26(2):274–306, 2020**, doi:10.1162/artl_a_00319; preprint arXiv:1803.03453. See `applications.md` for the eight verified anecdotes in retellable detail (and the two commonly **mis**-attributed to that paper).

The wider vocabulary: Krakovna's "Specification gaming examples in AI — master list" (blog, 2018-04-02, with a live canonical spreadsheet); **Amodei, Olah, Steinhardt, Christiano, Schulman & Mané, "Concrete Problems in AI Safety," arXiv:1606.06565** — **the paper that gave EC's old folk knowledge a vocabulary ML adopted**; and OpenAI's "Faulty Reward Functions in the Wild" (Dec 2016) with the CoastRunners boat circling to farm reward targets (⚠️ that URL 403s to automated fetches; cite Krakovna's description).

**The prescription: write the fitness function, run 30 generations, then look at the best individual's *behaviour*, not its score.** Validate on a held-out condition the optimiser could not see. If the objective is a proxy, add the cheapest possible sanity constraint — **and expect the optimiser to find the next-cheapest exploit.** ⚠️ **And note the structural identity with the surrogate-model-management problem: a surrogate *is*, by construction, a fitness function that rewards the wrong thing.**

### Ignoring constraint handling

Full treatment in `multi-objective.md` (it applies identically to single-objective problems). The three families in one line each:

- **Penalty** (static / dynamic / adaptive / death) — needs a scale-matched coefficient you cannot know in advance, and **too-small gives you a better-than-optimal *infeasible* answer, the most embarrassing bug in the literature.**
- **Repair / decoders / feasibility-preserving operators** — decoders make infeasibility unrepresentable (random-key encodings for permutations, pymoo's BRKGA, Prüfer sequences for spanning trees), ⚠️ **but they change the search landscape: a many-to-one decoder creates plateaus and can destroy locality, trading one failure mode for another.**
- **Comparison-based rules** (Deb's feasibility rules, stochastic ranking, ε-constraint) — **need no coefficient at all and are therefore the right default.**

Practical note: `cma` 4.5.0 ships an **augmented-Lagrangian** nonlinear-constraints handler (`cma/constraints_handler.py`, 56 KB) plus `boundary_handler.py` — **you do not need to hand-roll penalties with CMA-ES.**

### Population too small

**The point to make: required population size is a computable quantity that grows with problem size, with the number of building blocks, and with fitness noise — not a number you pick from a table.** Under-sizing produces **decision errors**: the GA makes the wrong call between competing building blocks early, **and no amount of later search recovers it.**

- **Harik, Cantú-Paz, Goldberg & Miller, "The Gambler's Ruin Problem, Genetic Algorithms, and the Sizing of Populations," *Evolutionary Computation* 7(3):231–253, 1999**, doi:10.1162/evco.1999.7.3.231. Models the competition between a building block and its competitor as a **one-dimensional random walk (gambler's ruin)**; the probability of converging to the right building block depends on the initial advantage (~ population size) and the per-decision signal-to-noise ratio, giving, in the usual rendering, **`n ∝ (σ_BB/d) · 2^k · sqrt(m) · ln(1/α)`** — **population grows with the square root of the number of building blocks m, exponentially in building-block order k, and with the noise-to-signal ratio σ_BB/d.**
- Goldberg's population-sizing lineage: **Goldberg, Deb & Clark, "Accounting for Noise in the Sizing of Populations," FOGA 2, pp. 127–140, 1993**, doi:10.1016/B978-0-08-094832-4.50014-3 — ⚠️ the companion *Complex Systems* 6:333–362 paper is unverified, not in Crossref. Follow-up: Cantú-Paz, 2001, doi:10.1007/978-1-4615-4369-5_2.
- **Operational prescription:** (a) if your fitness is **noisy**, either enlarge the population or **average repeated evaluations** — the models say the required size scales with noise, and averaging k times costs k evaluations but reduces σ by √k, **so there is a real optimum**; (b) **run a population-size sweep** (2×, 4×, 8× your guess at a **fixed total evaluation budget**) before you tune anything else — ⚠️ **this one experiment usually dominates every other parameter choice**; (c) for CMA-ES this is literally the documented procedure — increase `popsize` (or let IPOP double it on restart) when the landscape is multimodal or the fitness is noisy; (d) **for L-SHADE the answer is built in** — start at 18D and let LPSR shrink it, giving large-population robustness early and small-population exploitation late.

### Expensive fitness → surrogate-assisted EAs

Full treatment in `when-to-use-one.md`, including the five model-management policies and the rule that **you must report only true-evaluated fitness and count only true evaluations as the budget.** Citation: Jin, *SWEVO* 1(2):61–70, 2011, doi:10.1016/j.swevo.2011.05.001.
