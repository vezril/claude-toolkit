---
name: evolutionary-multiobjective
description: "Evolutionary multi-objective optimisation (EMO/MOEA) — the one area where evolutionary algorithms are genuinely state of the art, because a single run returns an approximation of the whole Pareto front rather than one point. Built from the primary papers read in full, with every claim marked verified or flagged. Covers Pareto dominance (weak, ordinary, strict, and the set-level 'is better than' relation), the Pareto-optimal set vs the Pareto front, ideal and nadir points, non-dominated sorting, and the precise geometric reason weighted-sum scalarization cannot reach concave portions of a front (plus the Tchebycheff and achievement-scalarizing alternatives that can); NSGA-II's actual algorithm (fast non-dominated sorting with domination counts and dominated sets at O(MN^2), crowding distance and its cuboid interpretation, the crowded-comparison operator, the elitist 2N loop) and the known breakdown of crowding distance beyond two or three objectives; NSGA-III (Das-Dennis structured reference points with H = C(M+p-1, p), adaptive hyperplane normalisation, reference-point niching) and the many-objective problem that motivates it — about 94% of a random population of 100 is already mutually non-dominated at ten objectives; SPEA2 (strength, raw fitness, k-th-nearest-neighbour density, the truncation rule that preserves boundary solutions); MOEA/D (decomposition into scalar subproblems, weighted-sum vs Tchebycheff vs penalty-based boundary intersection, neighbourhood mating and replacement, and the weight-vector mismatch on irregular fronts); the indicator-based family (SMS-EMOA's least-hypervolume-contributor rule, IBEA, HypE's Monte-Carlo ranking) with hypervolume's strict Pareto compliance and its #P-hardness in the number of objectives; the performance indicators (hypervolume and its reference-point sensitivity, IGD and IGD+, the additive epsilon indicator, spread) and the unary-indicator impossibility theorem stated correctly; the benchmark suites (ZDT, DTLZ, WFG) with their published flaws, including that DTLZ5/6 are not actually degenerate above three objectives and that most DTLZ/WFG fronts are triangular, which flatters decomposition methods; and constraint handling (Deb's constraint-domination, stochastic ranking's P_f ~ 0.45, the epsilon-constrained method, repair, two-archive methods). Use whenever a problem has two or more competing objectives, when someone mentions Pareto fronts or NSGA-II/NSGA-III/MOEA/D/SPEA2/hypervolume/IGD, when choosing or comparing multi-objective algorithms, when designing a many-objective study, or when a trade-off surface rather than a single optimum is wanted — and also to decide when EMO is the WRONG tool (convex problems with gradients, or very expensive evaluations where multi-objective Bayesian optimisation wins)."
---

# Evolutionary Multi-Objective Optimisation

The strongest case for evolutionary computation. With two or more competing objectives there is no single optimum — there is a **Pareto front** of mutually non-dominated trade-offs — and a population-based method returns an approximation of the whole front **in one run**, with no differentiability requirement, handling discrete and mixed variables, and letting the decision maker choose a trade-off *after* seeing what is achievable rather than by guessing weights beforehand.

Part of the [[evolutionary-algorithms]] family; see that skill for the generic loop, operators and the general decision criteria.

## Overlap with the evolutionary-algorithms hub — read this first

[[evolutionary-algorithms]] contains its own `references/multi-objective.md` (~86 KB) covering the same ground at survey depth. **This skill is the deeper treatment, not a replacement**: it carries full algorithm detail with pseudocode and complexities for NSGA-II, NSGA-III, SPEA2 and MOEA/D, the indicator-based family with hypervolume's compliance results, and a second reference devoted entirely to indicators and benchmark suites. Use the hub's chapter for orientation and this skill when you are actually choosing or implementing an algorithm, or defending a comparison.

## Pareto dominance, precisely

Minimising all `M` objectives, for `u, v ∈ R^M`:

- **Weak dominance** `u ⪯ v` ⟺ `u_i ≤ v_i` for all `i`.
- **Dominance** `u ≺ v` ⟺ `u_i ≤ v_i` for all `i` **and** `u_j < v_j` for at least one `j`.
- **Strict dominance** `u ≺≺ v` ⟺ `u_i < v_i` for **all** `i`.

Ordering: `≺≺ ⇒ ≺ ⇒ ⪯`. None is a total order — two vectors can be mutually **incomparable**, which is the whole reason the field exists. At the *set* level the relation that matters is **`A ⊲ B` ("A is better than B")**: `A ⪯ B` and not `B ⪯ A`. Zitzler et al. call this "the one implicitly used in most papers in the field."

The **Pareto-optimal set** lives in decision space; the **Pareto front** is its image in objective space. The **nadir** point is the componentwise worst value *over the Pareto-optimal set* — not over the whole feasible set. Conflating those is a common error.

## Why weighted-sum scalarization fails, geometrically

A weighted-sum minimiser is exactly a point of the attainable set `Y` at which the hyperplane with normal `λ` **supports** `Y + R^M_+`. Supporting hyperplanes touch only the boundary of the **convex hull**. So:

> Weighted-sum optima lie only on the boundary of `conv(Y + R^M_+)`. **Any Pareto-optimal point in a concave portion of the front is strictly inside that hull and unreachable by any non-negative weights.** Worse, the weight→solution map is *discontinuous* across a concavity, so an evenly spaced weight grid gives a clumped, gap-ridden set of points even on fronts that are convex but unevenly curved.

The fix is `L_∞` geometry: **weighted Tchebycheff** and the **achievement scalarizing function** have box-shaped level sets, so their supporting set is a cone corner rather than a flat face and they *can* touch concave regions. Tchebycheff is provably complete — for every Pareto-optimal point there exists a weight making it optimal.

## The four algorithms you actually need

**NSGA-II** (Deb et al., IEEE TEVC 6(2):182–197, 2002) — fast non-dominated sorting via domination counts `n_p` and dominated sets `S_p` at **O(MN²)** (versus the original NSGA's O(MN³)); **crowding distance** as the average side length of the largest cuboid enclosing a point with no other point inside, with boundary solutions given infinite distance; a crowded-comparison operator that ranks first and breaks ties toward the *less* crowded; and an elitist loop over the combined `2N` parent-plus-offspring pool, so no non-dominated parent can be lost. Its celebrated virtue is needing **no niche-radius parameter**.

**NSGA-III** (Deb & Jain, 2014) replaces crowding-distance truncation with **reference-direction niching**, because crowding distance breaks down beyond two or three objectives (it sums per-objective sorts that stop agreeing). The motivating fact is stark: at ten objectives, roughly **94% of a random population of 100 is already mutually non-dominated**, so Pareto dominance has no discriminating power left. It uses Das–Dennis points on the unit simplex (`H = C(M+p−1, p)`), a two-layer scheme to dodge the combinatorial blow-up, and adaptive hyperplane normalisation every generation — and, unusually, **no explicit mating selection at all**.

**MOEA/D** (Zhang & Li, 2007) decomposes the problem into `N` scalar subproblems, one per weight vector, solved *simultaneously* with mating and replacement restricted to a weight-vector neighbourhood. It scales to many objectives because selection pressure comes from scalar comparisons against fixed weights, not from dominance. Its weakness is geometric: a uniform weight simplex only maps to a uniform front sample when the front is itself roughly simplex-like.

**SMS-EMOA / IBEA / HypE** — indicator-based selection. Hypervolume is the only popular unary indicator that is **strictly Pareto compliant**, and SMS-EMOA's rule (discard the individual contributing least hypervolume) provably never decreases it. The catch: exact hypervolume is **#P-hard in the number of objectives**, and even *deciding* whether a point is the least contributor is #P-hard — hence HypE's insight that only the induced *ranking* matters, so Monte-Carlo estimates suffice.

## Comparing multi-objective algorithms is itself hard

This is the part practitioners skip, and it invalidates a lot of published comparison.

- **Hypervolume needs a reference point, and is sensitive to it.** It prefers knee regions and is biased toward convex over concave regions; the optimal finite point distribution depends on the front's slope. HV is **incomparable across papers unless the reference point and normalisation are both stated.**
- **IGD needs a reference *front*, and is unstable in it.** A worked example: two sets swap places depending on whether a *third* algorithm's results were included in the union used to build the reference set. Never build a reference set from the union of competitors' runs.
- **IGD+ fixes compliance, not reference sensitivity.** Its modified distance counts only the components in which a point is *worse* than the reference, which is exactly what buys weak Pareto compliance — but it is weakly, not strictly, compliant, and remains reference-set sensitive.
- **The impossibility theorem, stated correctly.** Zitzler et al. 2003, Theorem 1: there exists **no comparison method based on a finite combination of unary quality indicators that is both `⊲`-compatible and `⊲`-complete.** Their gloss: "the number of criteria that determine what a good approximation set is is infinite." This does *not* say unary indicators are useless — it says no finite set of unary numbers is an exact oracle for set dominance. The corollary usually omitted: such a method *does* exist with infinitely many indicators, which is the formal argument for **empirical attainment functions** over a single number.

## When to reach for this skill

Whenever a problem has two or more competing objectives; when choosing, implementing or comparing multi-objective algorithms; when someone names Pareto fronts, NSGA-II/III, MOEA/D, SPEA2, hypervolume or IGD; when designing a many-objective study and wondering why dominance stopped discriminating; or when a trade-off surface rather than a single answer is the deliverable.

Reach for it equally to rule EMO *out*: on convex, smooth, gradient-available problems scalarization is complete and an NLP solver gives machine precision plus certificates; and when evaluations are very expensive, multi-objective Bayesian optimisation (ParEGO, MOEA/D-EGO, qEHVI, qNEHVI) wins — with the nice irony that those methods optimise exactly the hypervolume indicator used here for selection, and inherit the same #P-hardness and reference-point sensitivity.

## How to use this skill

- **`references/algorithms.md`** — the dominance vocabulary and set relations; the scalarization geometry and its alternatives; NSGA-II's full algorithm with pseudocode, complexities and the crowding-distance breakdown; NSGA-III (Das–Dennis counts, adaptive normalisation, association and niching, complexity); SPEA2 (strength, raw fitness, density, archive truncation); MOEA/D (the three aggregations with formulas, neighbourhood structure, the main loop, the diversity-loss mechanism, variants); and the indicator-based family with hypervolume's compliance results and complexity bounds.
- **`references/indicators-and-benchmarks.md`** — hypervolume, GD/IGD/GD+/IGD+ with formulas, the epsilon indicator, spread; reference-point and reference-set sensitivity with worked numbers; the unary-indicator impossibility theorem and its two usually-omitted corollaries; a practical checklist for a defensible comparison; ZDT, DTLZ and WFG with the authors' own criticisms of each other's suites; the RE real-world suite; and constraint handling (Deb's constraint-domination and its weakness, stochastic ranking, epsilon-constraint, repair, penalties, two-archive methods).

## Related

- [[evolutionary-computation]] — the meta/router skill for this cluster, and the when-to-use gate that should run before any of it.
- [[evolutionary-algorithms]] — the generic loop, operators (SBX and polynomial mutation are the EMO defaults), and the general when-to-use decision.
- [[evolutionary-computation-theory]] — why dominance-based selection degrades with dimension, and the landscape framing behind front geometry.
- [[genetic-programming]] — multi-objective size-vs-error is one of the standard bloat controls.
- [[python]] — `pymoo` is the reference implementation for essentially everything here.
- Primary sources, read in full: Deb, Pratap, Agarwal & Meyarivan, IEEE TEVC 6(2):182–197, 2002 (DOI 10.1109/4235.996017); Deb & Jain, IEEE TEVC 18(4):577–601, 2014; Zitzler, Laumanns & Thiele, SPEA2, TIK-Report 103, 2001; Zhang & Li, IEEE TEVC 11(6):712–731, 2007; Zitzler, Thiele, Laumanns, Fonseca & Grunert da Fonseca, IEEE TEVC 7(2):117–132, 2003; Huband, Hingston, Barone & While, IEEE TEVC 10(5):477–506, 2006; Blank & Deb, "pymoo", IEEE Access 8:89497–89509, 2020. All web sources fetched 2026-11-11.
