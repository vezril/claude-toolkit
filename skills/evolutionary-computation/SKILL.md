---
name: evolutionary-computation
description: "Meta/overview skill for evolutionary computation — the entry point and router for the toolkit's four EC skills, plus the decision gate that should run before any of them. Explains the cluster and points to the right one: the generic loop, the dialects (GA, Evolution Strategies/CMA-ES, Evolutionary Programming, Differential Evolution), the operators, the applications and the practical defaults (evolutionary-algorithms); Pareto optimisation with NSGA-II/NSGA-III/SPEA2/MOEA/D, the quality indicators and the benchmark suites (evolutionary-multiobjective); evolving programs and expressions — closure and sufficiency, bloat, grammatical/linear/Cartesian GP, lexicase selection, symbolic regression (genetic-programming); and what is actually proven versus folklore — the schema theorem, the building-block hypothesis, No Free Lunch, runtime analysis, fitness landscapes and the field's metaphor/rigour problem (evolutionary-computation-theory). Use as the starting point for any task involving genetic algorithms, evolution strategies, CMA-ES, differential evolution, genetic programming, neuroevolution, NEAT, multi-objective or Pareto optimisation, derivative-free or black-box optimisation, metaheuristics, quality-diversity, or LLM-guided program search such as FunSearch and AlphaEvolve — when unsure which EC skill fits, when a task spans several, and above all when deciding whether an evolutionary algorithm is the right tool at all, since usually it is not. Also use when checking a claim about this field: the schema theorem, the building-block hypothesis and No Free Lunch are the three most frequently misstated results in it. From any EC task, defer to the specific skill for detail."
---

# Evolutionary computation (overview / meta)

The map for this toolkit's **evolutionary computation** skills. This meta skill is the router and the gate — for real work, **read the specific skill** linked below.

It exists for two reasons. First, the four skills are large and split along non-obvious lines, so pointing at the right one saves a lot of reading. Second, and more usefully: **this is a field where the default answer is "don't."** An evolutionary algorithm is a derivative-free, population-based, stochastic last resort. Most problems people reach for one on are better served by a gradient method, a Bayesian optimiser, an exact solver, or random search — and the literature is full of papers that never checked. The gate below runs before the router.

## Run the gate first

Before reaching for any of these, answer these. If you cannot answer them, that is itself the answer.

1. **Is there a usable gradient?** If yes, use it. Adjoint and automatic differentiation beat population methods by orders of magnitude where they apply.
2. **Is the problem convex, linear, or a known combinatorial class?** Then an exact solver or a MIP formulation will probably beat any metaheuristic and come with a bound.
3. **What is the evaluation budget?** Under a few hundred evaluations, Bayesian optimisation generally wins. Above tens of thousands, EAs become competitive. The crossover point is the whole decision.
4. **Have you run random search as a baseline?** If not, do that first. It is the baseline that most often embarrasses the proposed method, and it is free.
5. **Is the real requirement a *set* of trade-off solutions rather than one optimum?** Then go straight to [[evolutionary-multiobjective]] — this is the one area where evolutionary methods are clearly state of the art rather than merely adequate.
6. **Are you optimising a *program or expression* rather than a vector?** Then [[genetic-programming]], and read its bloat section before you start, not after.

`references/when-to-use-one.md` in [[evolutionary-algorithms]] is the long form of this gate, including the head-to-head comparisons and the Bergstra & Bengio random-search result stated correctly.

## Which skill to reach for

**The algorithms themselves**
- **[[evolutionary-algorithms]]** — the hub, and the largest skill in the cluster. The generic loop as a six-slot template; the dialects and what actually separates them (GA, Evolution Strategies and CMA-ES, Evolutionary Programming, Differential Evolution, **and a substantial genetic-programming section**) plus the boundary cases; operators and representation; the when-to-use decision; the applications that earn the name; theory and fitness landscapes; multi-objective; and the practical defaults, libraries and benchmarking hygiene. Its references are `dialects.md`, `operators-and-representation.md`, `when-to-use-one.md`, `applications.md`, `practice.md`, `theory.md`, `landscapes-and-rigour.md` and `multi-objective.md`. *Start here for anything single-objective, and for the library and parameter defaults whatever you are doing.*

**Many objectives at once**
- **[[evolutionary-multiobjective]]** — Pareto dominance and non-dominated sorting; NSGA-II, NSGA-III, SPEA2, MOEA/D and the indicator-based family with full algorithm detail; hypervolume, IGD/IGD+ and the unary-indicator impossibility theorem; the ZDT/DTLZ/WFG suites with the authors' own criticisms of each other; and constraint handling. *Use whenever the answer is a trade-off front rather than a point — and note this is the subfield with the strongest claim to being the right tool.*

**Evolving programs**
- **[[genetic-programming]]** — closure and sufficiency; Koza's tableau with its provenance; bloat with all four theories and every parsimony remedy; grammatical evolution, linear GP, Cartesian GP, PushGP, geometric semantic GP; lexicase and epsilon-lexicase selection; symbolic regression and SRBench. *Use when the genotype is a tree, a grammar derivation, or source code.*

**What is actually true**
- **[[evolutionary-computation-theory]]** — the schema theorem in both forms with all six conditions; the building-block hypothesis as stated and as attacked; No Free Lunch with every precondition quoted from the paper, and the closure-under-permutation sharpening; runtime analysis of the `(1+1)` EA on OneMax, LeadingOnes, Trap and friends; fitness landscapes, deception, epistasis and NK models; and the field's rigour problem (Sörensen, Weyland, the Bestiary, the benchmarking consensus). *Use before asserting anything theoretical about this field, and whenever a claim sounds too clean.*

## How they fit together (a typical flow)

Run the gate above. If an EA still looks right, take the loop, the representation and the operator choices from **[[evolutionary-algorithms]]**, and its `references/practice.md` for the library, the default parameters and the benchmarking protocol. If the objective is a vector, switch to **[[evolutionary-multiobjective]]** for the algorithm and, critically, for how to *compare* results defensibly — indicator choice is not a detail. If the thing being evolved is a program, **[[genetic-programming]]** replaces the operator chapter wholesale and adds bloat control. Consult **[[evolutionary-computation-theory]]** whenever you are about to explain *why* something works, or to repeat a claim you did not derive.

The frontier case spans three of them: **LLM-guided evolutionary program search** (FunSearch, AlphaEvolve) is genetic programming with a language model as the mutation operator, run over an island model with a quality-diversity archive. The applications reference in [[evolutionary-algorithms]] covers it in detail; [[genetic-programming]] supplies the program-evolution frame.

## Always-apply notes

- This is a **router and a gate** — defer to the specific skill for algorithms, parameters and code; don't try to recall the detail here.
- **The three most-misstated results in the field are the schema theorem, the building-block hypothesis, and No Free Lunch.** All three are routinely stated without their preconditions, which is what makes the misstatements sound authoritative. [[evolutionary-computation-theory]] carries each with its conditions attached. If you are about to invoke one, read it there first.
- **Folklore is marked as folklore.** These skills separate proven results from received wisdom, and flag what could not be verified rather than smoothing it over. Preserve that distinction when quoting them; an unhedged version of a hedged claim is a new error.
- **Report distributions, not best-of-N.** Equal evaluation budgets, fixed seeds, a stated statistical test. The benchmarking-hygiene section exists because the published literature frequently does none of this.
- **A biological metaphor is not a mechanism.** The rigour critique in [[evolutionary-computation-theory]] is about exactly this: several widely cited "novel" metaheuristics have been shown to be relabelled versions of older algorithms.

## Related

- [[evolutionary-algorithms]], [[evolutionary-multiobjective]], [[genetic-programming]], [[evolutionary-computation-theory]] — the four skills this routes among.
- [[information-theory]] — Kolmogorov complexity and description length are what break No Free Lunch's closure condition.
- [[python]] — `pymoo`, `DEAP`, `cma` and `PySR` are the reference implementations; the practice reference gives versions, licences and maintenance verdicts.
- [[compiler-construction]] — trees, grammars and type systems are the same objects genetic programming manipulates.
- [[procedural-generation]], [[game-ai]] — where quality-diversity and neuroevolution show up in practice.
- [[diagnosing-bugs]] — automated program repair (GenProg) and the critique that reframed it.
