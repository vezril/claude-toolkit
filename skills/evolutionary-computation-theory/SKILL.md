---
name: evolutionary-computation-theory
description: "The theory of evolutionary computation — what is actually proven versus what is folklore — because this field has an unusual amount of the latter, and the schema theorem / building-block hypothesis / No Free Lunch trio is especially often misstated. Built from primary sources with every claim marked verified or flagged. Covers **Holland's schema theorem** stated formally with order, defining length and every condition it assumes, then why it is weak: a one-generation lower-bound inequality on expected counts that cannot be iterated, becomes vacuous precisely as the algorithm succeeds, and credits nothing to the *construction* of new schemata — which is the very thing the building-block hypothesis needs; the exact schema theorem (Stephens & Waelbroeck) that replaces the inequality with an equality; **implicit parallelism** and the O(n^3) claim's narrow numerical justification; the **building-block hypothesis** and the serious criticisms (Grefenstette's 'Deception considered harmful', Grefenstette & Baker on implicit parallelism, Radcliffe's three objections, Altenberg showing the schema theorem is a special case of Price's theorem and therefore privileges schemata for no reason, Vose's exact Markov-chain and dynamical-systems model, Burjorjee's assumption-level critique); the **Royal Road** story in full, including the measured reversal where random-mutation hill climbing found the optimum in 6,179 evaluations against the GA's 61,334 on a landscape designed to be a royal road *for the GA*; the **No Free Lunch theorems** with their preconditions quoted and, more importantly, what they do NOT imply — the sharpened iff result that NFL holds exactly when the function class is closed under permutation, the proof that any non-trivial neighbourhood relation is not permutation-invariant, and the counting result that the fraction of permutation-closed subsets vanishes double-exponentially; the Almost No Free Lunch theorem that denies the opposite comfort; coevolutionary free lunches and their champion-seeking caveat; **rigorous runtime analysis** as the modern strand ((1+1) EA on OneMax at Theta(n log n) with the sharp constant, LeadingOnes at Theta(n^2), linear functions tight with p = 1/n provably optimal, Trap at Theta(n^n) — worse than exhaustive search, plateaus, long paths, the fitness-level method, drift analysis, and where crossover provably helps); convergence results and their conditions (Rudolph 1994 in both directions) and why convergence in the limit is near-vacuous; **fitness landscapes** (the landscape is a property of the operator, not the objective; deception, epistasis, ruggedness, fitness-distance correlation and Altenberg's counterexample, neutrality, NK landscapes, big valleys and local optima networks) and the honest finding that every single-number difficulty predictor proposed in the 1990s has a published counterexample; and the field's **rigour problem** — Sorensen's 'Metaheuristics—the metaphor exposed', Weyland's formal proof that harmony search is a special case of evolution strategies, the IRIDIA group's per-algorithm exposure of the grey wolf, moth-flame, whale, firefly, bat, antlion, cuckoo and intelligent-water-drops algorithms as renamed PSO and ES variants, the Evolutionary Computation Bestiary's 343 catalogued metaphors, and the journal policies that resulted. Use when evaluating a theoretical claim about an EA, when someone invokes the schema theorem or building blocks or No Free Lunch (especially as a licence to publish another metaheuristic), when asked why EAs are hard to analyse, when reasoning about problem difficulty or landscape structure, or when assessing whether a 'novel' nature-inspired algorithm is actually novel."
---

# Evolutionary Computation Theory

What is **proven**, what is merely **true but weak**, and what is **folklore**. This matters more here than in most fields: evolutionary computation's best-known theoretical results are routinely overstated, and its publication culture has a well-documented problem with rebranded methods. This skill is organised around separating the three.

Part of the [[evolutionary-algorithms]] family; see that skill for the algorithms themselves.

## Overlap with the evolutionary-algorithms hub — read this first

[[evolutionary-algorithms]] contains its own `references/theory.md` (~59 KB) and `references/landscapes-and-rigour.md` (~64 KB). **This skill is the deeper treatment, not a replacement**: it splits the material four ways and goes further on the schema theorem's six conditions, No Free Lunch with every precondition quoted from the paper, rigorous runtime analysis, and the landscape measures. Use the hub's chapters for orientation and this skill before asserting anything theoretical.

## The three most-misstated results

**The schema theorem is true and nearly useless as a theory of why GAs work.** It is a *one-generation lower bound on an expected count*, under fitness-proportionate selection, one-point crossover and per-bit mutation:

```
E[m(H,t+1)] ≥ m(H,t) · (f(H)/f̄) · [1 − p_c·d(H)/(l−1) − o(H)·p_m]
```

Four reasons it cannot carry the weight placed on it: it **cannot be iterated** (chaining conditional expectations with data-dependent multipliers is not licensed); it becomes **vacuous exactly when the GA succeeds**, because success raises `f̄` and drives the multiplier toward 1 while the survival bracket is strictly below 1; `f(H)` is a *selection-biased sample* average, not a property of the schema; and — decisively — **it credits nothing to construction**. It bounds only the survival of schemata already present. The building-block hypothesis is a claim about *assembling* schemata that were not there. A theorem that bounds only loss cannot support a hypothesis about gain.

**The building-block hypothesis does not follow from it, and was falsified on its own home ground.** The Royal Road functions were built from the ground up to satisfy the BBH's premises — an explicit, gap-free, uniformly weighted hierarchy of short low-order schemata composable into the optimum. The 1992 results looked like vindication. Then: on R1 over 200 runs, the GA found the optimum in a mean of **61,334** evaluations while **random-mutation hill climbing took 6,179** — nearly ten times faster — and steepest-ascent and next-ascent hill climbing never found it within 256,000. The diagnosed mechanism was **hitchhiking**: once a high-order schema is found its fitness spreads it fast, dragging zeros along in the other positions, which is precisely the selection-biased-sampling failure the schema theorem cannot see.

**No Free Lunch is a demand for specificity, not a licence.** Wolpert & Macready's theorem requires a finite search space and codomain, performance measured only on the sequence of *distinct* points visited, non-revisiting algorithms, and uniform averaging over **all** functions from the space to the codomain. The sharpened version is an **iff**: NFL holds over a function class exactly when that class is **closed under permutation** of the search space. And Igel & Toussaint proved that **any non-trivial neighbourhood relation is not permutation-invariant** — so any class defined by smoothness, bounded steepness, a bound on local optima, separability, or bounded description length is *not* closed under permutation, and NFL simply does not apply to it. The fraction of subsets that *are* closed vanishes double-exponentially; for Boolean `f: {0,1}³ → {0,1}` it is already below 10⁻¹⁷⁰.

So the correct reading: **NFL kills the claim that some optimiser is universally superior. It says nothing against the claim that a given algorithm is better on a structured class — which is every class anyone cares about.** The Almost No Free Lunch theorem denies the opposite comfort too: for every heuristic there are exponentially many barely-more-complex functions on which it fails.

## What rigorous theory looks like now

The field's rigorous wing abandoned both schema analysis and the exact dynamical model — the former too weak, the latter exact but uncomputable — in favour of **runtime analysis**: proving expected optimisation times for specific algorithms on specific function classes. Representative verified results for the `(1+1)` EA with mutation rate `1/n`:

| Function | Expected runtime |
|---|---|
| OneMax | `Θ(n log n)`, tightly `e·n·ln n − 1.8925n + (e/2)ln n + 0.598` |
| Any linear function | `Θ(n log n)`, tightly `e·n·ln n + O(n)`; **`p = 1/n` is provably optimal** |
| LeadingOnes | `Θ(n²)` |
| Unimodal, `N+1` values | `≤ e·n·N` |
| Plateau of path length `l` | `O(n·l²)` |
| Shortcut-free long path | `Ω(l·n)` — exponential, **and the function is unimodal** |
| Trap | `Θ(n^n)` — **worse than exhaustive search** |

These *distinguish* algorithms and problems, which is exactly what convergence results do not. Rudolph 1994 proves both directions — the canonical GA **without** elitism does not converge to the global optimum for any initialisation, crossover or objective; an elitist variant with everywhere-positive mutation does, with probability 1 — but that pair of hypotheses is also satisfied by random search with the best kept. Convergence in the limit is not a discriminating property.

Crossover *does* provably help, in narrow and honest senses: Jansen & Wegener's Real Royal Road functions (an existence proof on a constructed function, needing crossover to be *rare* at `p_c = 1/(n log n)`), Sudholt's factor-of-two on OneMax and royal roads, and the `(1+(λ,λ))` GA where biased crossover acts as a repair mechanism licensing a higher mutation rate.

## Landscapes, and why difficulty measures failed

A fitness landscape is a **triple**: search space, a neighbourhood *induced by the search operator*, and fitness. The consequence is the one most landscape analysis ignores — **a change of operator defines a new landscape**, so any difficulty measure computed from the objective function alone is measuring the wrong object.

Every single-number difficulty predictor proposed in the 1990s has a published counterexample: deception (Grefenstette showed it is neither necessary nor sufficient for GA-hardness), epistasis variance, ruggedness/autocorrelation (Altenberg's two counterexamples), and fitness-distance correlation (Altenberg's GA-easy function with *exactly zero* FDC and zero additive effects at every locus). Naudts & Kallel found sampled estimates "completely unreliable and entirely uncorrelated" to actual GA performance. What survived is operator-aware statistics (evolvability) and graph-theoretic global structure (local optima networks, funnels) — plus the runtime analysis above, which abandons difficulty measures entirely.

## The rigour problem — and why it belongs in a theory skill

The field's weak theoretical foundations produced a publication culture that the field's own leaders have attacked in print. Sörensen's "Metaheuristics—the metaphor exposed" (ITOR 22(1):3–18, 2015) names "a true tsunami of 'novel' metaheuristic methods, most of them based on a metaphor" and argues "this line of research is threatening to lead the area of metaheuristics away from scientific rigor." Weyland then *proved* harmony search is a special case of evolution strategies under the exact parameter mapping `mu = HMS`, `p1 = PAR`, `p2 = 1 − HMCR` — and refuted a published sudoku result whose reported success he bounded at probability ≤ 4.83 × 10⁻¹⁰⁰, confirming it with 720 independent runs that found the solution zero times.

The IRIDIA group (Camacho-Villalón, Dorigo & Stützle) then did it per-algorithm: grey wolf, moth-flame, whale, firefly and bat are PSO variants, antlion is a `(mu+lambda)` ES, cuckoo search is ES plus differential evolution, and intelligent water drops is ACO with the pheromone sign inverted. Their verdict — "the only novelty in these self-proclaimed novel algorithms is six different terminologies derived from the use of new metaphors" — and their observation that the motivation for proposing more of them "is based on a wrong understanding of the no-free-lunch theorems for optimization." The **Evolutionary Computation Bestiary** catalogues **343** such metaphors.

This is not gossip. It is the reason a reference skill must mark claims verified or unverified, and the reason the right baseline for a new method is the best specialist solver rather than another metaheuristic.

## When to reach for this skill

When evaluating a theoretical claim about an EA. When someone invokes the schema theorem, building blocks, or No Free Lunch — especially when NFL is being used as a licence to propose another method. When asked why EAs are hard to analyse. When reasoning about problem difficulty, deception, epistasis or landscape structure. When assessing whether a "novel" nature-inspired algorithm is actually novel. And when you need the honest answer to "is this proven, or is this folklore?"

## How to use this skill

- **`references/schema-and-building-blocks.md`** — the schema theorem in both its multiplicative and linearised forms with all six conditions; the exact schema theorem; implicit parallelism and the O(n³) claim's narrow validity window; the building-block hypothesis as stated and attacked; the criticisms from Grefenstette, Grefenstette & Baker, Mühlenbein, Radcliffe, Altenberg/Price, Vose and Burjorjee; and the Royal Road story with verified figures, the RMHC analysis, and the Idealized GA that gives the honest formal content of "implicit parallelism helps".
- **`references/no-free-lunch.md`** — Wolpert & Macready's framework with every precondition quoted from the paper's own Section 2; the sharpened closure-under-permutation iff; the counting result and the neighbourhood/steepness/local-optima corollaries; the Almost No Free Lunch theorem verbatim; the restricted-black-box scenarios and the "free appetizer"; coevolutionary free lunches with the champion/no-champion caveat; and a consolidated list of what NFL does and does not license.
- **`references/runtime-and-convergence.md`** — the `(1+1)` EA defined; the benchmark function definitions; OneMax, LeadingOnes, linear functions, Trap, Needle, plateaus and long paths with their bounds and the proof techniques (fitness levels, drift analysis, the typical-run method); where crossover provably helps; the four standard reference books; convergence results with their conditions and why they are near-vacuous; and ES convergence rates.
- **`references/landscapes-and-rigour.md`** — the formal landscape definition and operator-dependence; deception, epistasis, ruggedness, FDC with Altenberg's counterexample and its success table, neutrality, NK landscapes with exact results and the NP-completeness threshold, big valleys, funnels and local optima networks; then the rigour problem — Sörensen, Weyland's formal mapping and refutation, the IRIDIA per-algorithm exposures, the open letter, the Bestiary, editorial policies, Hooker on competitive testing, and the benchmarking best-practice consensus document.

## Related

- [[evolutionary-computation]] — the meta/router skill for this cluster, and the when-to-use gate that should run before any of it.
- [[evolutionary-algorithms]] — the algorithms these results are about, and the practice reference that operationalises the benchmarking critique.
- [[evolutionary-multiobjective]] — the unary-indicator impossibility theorem is the same kind of result, in the multi-objective setting.
- [[genetic-programming]] — Poli's exact schema theory yields the size evolution equation that constrains every bloat theory.
- [[information-theory]] — Kolmogorov complexity and description length are what break NFL's closure condition.
- Primary sources include: Holland (1975); Goldberg (1989); Wolpert & Macready, IEEE TEVC 1(1):67–82, 1997 (DOI 10.1109/4235.585893); Mitchell, Holland & Forrest, NIPS 1993; Altenberg, FOGA 3, 1995; Vose, *The Simple Genetic Algorithm* (MIT Press, 1999); Droste, Jansen & Wegener, TCS 276:51–81, 2002 and TCS 287:131–144, 2002; Witt, CPC 22(2):294–318, 2013; Rudolph, IEEE TNN 5(1):96–101, 1994; Doerr & Neumann (eds), *Theory of Evolutionary Computation* (Springer, 2020); Sörensen, ITOR 22(1):3–18, 2015 (DOI 10.1111/itor.12001); Camacho-Villalón, Dorigo & Stützle, ITOR 30(6):2945–2971; Bartz-Beielstein et al., arXiv:2007.03488. All web sources fetched 2026-11-11.
