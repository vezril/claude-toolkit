# Multi-objective optimisation

**Treat this as first-class: this is where EAs are genuinely state of the art.** Everything else in the EA literature has a strong non-evolutionary competitor; approximating a whole Pareto front in one run of a black-box problem does not.

⚠️ marks what could not be verified against a source actually read. PDFs read in full for this file: NSGA-II (KanGAL preprint), NSGA-III Part I (accepted preprint), MOEA/D (IEEE typeset), SPEA2 TIK-Report 103, Zitzler et al. 2003 performance assessment, ZDT 2000, IBEA 2004, HypE TIK-Report 286, the WFG toolkit, SMS-EMOA's EMO-2005 precursor, the Guerreiro/Fonseca/Paquete hypervolume survey, Li & Yao's indicator survey, Liang et al.'s constrained-MO survey, Tanabe & Ishibuchi's RE suite. ScienceDirect, the ETH Research Collection and IEEE Xplore HTML all return 403 to automated fetching.

---

## Foundations

### Pareto dominance

Minimising all M objectives, `f: X → R^M`. For `u, v ∈ R^M`:

- **Weak dominance** `u ≼ v ⟺ u_i <= v_i` for all i. (Reflexive.)
- **Dominance** `u ≺ v ⟺ u_i <= v_i` for all i **and** `u_j < v_j` for at least one j.
- **Strict/strong dominance** `u ≺≺ v ⟺ u_i < v_i` for **all** i.

Ordering: `u ≺≺ v ⟹ u ≺ v ⟹ u ≼ v`. **None is a total order**; two vectors can be mutually non-dominated (**incomparable**). *That incomparability is the whole reason the field exists.*

Zitzler et al. 2003 lift these to **sets** and add a fourth relation — this four-relation vocabulary is what the indicator literature uses. Verbatim: *"we will distinguish four relations in this paper as defined in Table I: strictly dominates, dominates, **is better than**, and weakly dominates. Note that there is a natural ordering again among the relations."* For sets:

- `A ≼ B`: every `b ∈ B` is weakly dominated by some `a ∈ A`.
- **`A ⊲ B` ("A is better than B")**: `A ≼ B` and not `B ≼ A`. The paper: *"if A weakly dominates B, then either A is better than B or they are equal."* **This ⊲ is "the one implicitly used in most papers in the field."**
- `A ≺ B`: every `b ∈ B` is dominated by some `a ∈ A`.
- `A ≺≺ B`: every `b ∈ B` is strictly dominated by some `a ∈ A`.

### Pareto-optimal set vs Pareto front — decision space vs objective space

- **Pareto-optimal set** `PS = {x ∈ X : ∄ x' ∈ X, f(x') ≺ f(x)}` — in **decision** space.
- **Pareto front** `PF = f(PS) ⊆ R^M` — in **objective** space.

**The front is the image; the set is the preimage.** Different decision vectors can map to the same objective vector — the WFG paper's term is **"Pareto many-to-one"**, which it notes holds for most DTLZ problems.

### Ideal and nadir points

- **Ideal** `z*` with `z*_i = min_{x ∈ X} f_i(x)`. Generally infeasible when objectives conflict.
- **Nadir** `z^nad_i = max_{x ∈ PS} f_i(x)` — the componentwise worst value **over the Pareto-optimal set**, not over the whole feasible set. ⚠️ **The componentwise max over all of X is the (larger, easier, different) "worst point"; conflating them is a common error.**

NSGA-III estimates the ideal point per generation as `z^min_j = min_{s ∈ S_t} f_j(s)` and estimates the nadir implicitly via hyperplane intercepts.

### Non-dominated sorting

Partition a population P into fronts `F_1, F_2, …` where `F_1` is the non-dominated subset of P, `F_2` the non-dominated subset of `P \ F_1`, etc. The index is the **non-domination rank**.

### The two goals of EMO, and they conflict

1. **Convergence** — drive the approximation set toward PF.
2. **Diversity / spread** — cover PF broadly and evenly so the decision maker sees the whole trade-off surface.

The literature treats the tension explicitly: Bosman & Thierens, "The balance between proximity and diversity in multiobjective evolutionary algorithms," *IEEE TEVC* 7(2):174–188, 2003, doi:10.1109/TEVC.2003.810761. Deb's framing in NSGA-II: *"along with convergence to the Pareto-optimal set, it is also desired that an EA maintains a good spread of solutions."*

### Why weighted-sum scalarization fails on non-convex fronts — the geometric reason

The scalarization `min_x Σ_i λ_i f_i(x)`, `λ_i >= 0`, `Σ λ_i = 1`, has a purely geometric characterisation: **a minimiser is exactly a point of the attainable objective set `Y = f(X)` at which the hyperplane with normal λ *supports* Y** (more precisely, supports `Y + R^M_+`). Supporting hyperplanes of a set touch only points on the boundary of its **convex hull**. Therefore:

> **Weighted-sum optima lie only on the boundary of `conv(Y + R^M_+)`. Any Pareto-optimal point lying in a concave portion of PF is strictly *inside* that convex hull and is therefore unreachable by any choice of non-negative weights.**

Worse, **the weight→solution map is discontinuous across a concavity**: as λ sweeps, the minimiser *jumps* from one convex end of the concave region to the other, so an evenly spaced grid of weights yields a clumped, gap-ridden set of front points **even on fronts that are convex** but unevenly curved.

Primary-source confirmation (Zhang & Li 2007 §II-A): *"If the PF is concave (convex in the case of minimization), this approach could work well. **However, not every Pareto optimal vector can be obtained by this approach in the case of nonconcave PFs.**"*

Supporting theory: **Geoffrion, "Proper efficiency and the theory of vector maximization," *J. Math. Anal. Appl.* 22(3):618–630, 1968**, doi:10.1016/0022-247X(68)90201-1 — the classical link between positive-weight scalarization and **properly efficient** points; weighted-sum solutions are properly efficient, and **in the convex case the converse holds.** Textbook: Miettinen, *Nonlinear Multiobjective Optimization*, Kluwer 1998/1999, doi:10.1007/978-1-4615-5563-6 — reference [1] of the MOEA/D paper.

### The alternatives that *can* reach non-convex regions

**Weighted Tchebycheff / Chebyshev (weighted L_∞):**

```
minimise g^te(x | λ, z*) = max_{1<=i<=M} λ_i · |f_i(x) − z*_i|
```

Because the level sets are axis-aligned L_∞ "boxes" rather than hyperplanes, **the supporting set is a cone corner, not a flat face** — so it can touch concave portions of the front. Completeness property (Zhang & Li §II-B): *"for each Pareto optimal point x* there exists a weight vector lambda such that x* is the optimal solution of (3) and each optimal solution of (3) is a Pareto optimal solution of (1)."* (Technically it finds *weakly* Pareto-optimal points in degenerate cases; augmented/ε-perturbed Tchebycheff fixes that.) The cost: *"One weakness with this approach is that its aggregation function is **not smooth** for a continuous MOP"* — fine inside an EA, which never differentiates it.

**Achievement scalarizing function (ASF), Wierzbicki:**

```
ASF(x | z̄, w) = max_{1<=i<=M} (f_i(x) − z̄_i) / w_i
                 (+ optional augmentation ρ · Σ_i (f_i − z̄_i)/w_i)
```

Wierzbicki, "The Use of Reference Objectives in Multiobjective Optimization," LNEMS 177, pp. 468–486, 1980, doi:10.1007/978-3-642-48782-8_32. Same L_∞ geometry, so the same ability to reach concave regions; and `z̄` can be an **aspiration** (preference) point. The augmented form guarantees proper efficiency. **This is exactly the function NSGA-III uses to locate its extreme points**, and pymoo ships `ASF` and `AASF` as decomposition objects.

**PBI (penalty-based boundary intersection)** — below; also reaches non-convex fronts, and derives from Das & Dennis's Normal-Boundary Intersection (doi:10.1137/S1052623496307510).

---

## NSGA-II — the actual algorithm

**Deb, Pratap, Agarwal & Meyarivan, "A fast and elitist multiobjective genetic algorithm: NSGA-II," *IEEE TEVC* 6(2):182–197, 2002**, doi:10.1109/4235.996017 (DOI verified: exactly this title, these four authors, vol 6, issue 2, pp. 182–197).

⚠️ **Provenance caveat:** the free full text read is the KanGAL preprint. It is substantively the same algorithm but **differs from the published TEVC version in two places**, both flagged below.

### Fast non-dominated sort

The published TEVC version's bookkeeping — the canonical form:

- For each `p ∈ P` compute **`n_p`** = the **domination count**, the number of solutions that dominate p; and **`S_p`** = the **dominated set**, the set p dominates. This first pass is `O(MN²)`.
- All p with `n_p = 0` form `F_1`.
- For each p in the current front `F_i`, visit each `q ∈ S_p` and **decrement `n_q`**; any q reaching `n_q = 0` joins `F_{i+1}`. Each `S_p` is traversed once in total, so the front-peeling phase is `O(N²)` overall and **never re-does domination tests.**
- **Total `O(MN²)`**, with `O(N²)` extra memory for the `S_p` lists.

⚠️ **The `n_p`/`S_p` formulation is not in the preprint verified.** The preprint gives instead a `find-nondominated-front(P)` **incremental-insertion** routine (grow a set P', inserting p and deleting any member it dominates), called repeatedly on the residue. The `n_p`/`S_p` version is almost certainly what the published paper contains — it is the universally reproduced form, and DEAP's docs cite "Deb et al.'s fast nondominated sorting" at `O(MN²)` — but **treat it as high-confidence-but-not-directly-fetched.**

Complexities, quoted from the verified preprint:

- A single domination test costs M objective comparisons; finding the first non-dominated front naively is `O(MN²)`.
- *"the worst case (when there exists only one solution in each front) the complexity of this algorithm **without any book-keeping is O(MN³)**."* **That is the complexity of the original NSGA (Srinivas & Deb 1994)** — the paper also notes of SPEA: *"in [24] is O(MN³), with proper book-keeping the complexity of SPEA can be reduced to O(MN²)."*
- They **empirically validated** the quadratic claim: on random populations with objectives uniform in [0,1], fitting the comparison count gave **`25.354·N^1.1248` for M=4, `8.145·N^1.248` for M=10, `9.772·N^2.0032` for M=20** — i.e. *"as the number of objective functions increase, the exponent increases to approximately two."* **A rarely-quoted detail: for few objectives the practical cost is nowhere near N².**

### Crowding distance

Verbatim: *"The crowding distance computation requires sorting of the population according to each objective function value in their ascending order of magnitude. Thereafter, for each objective function, the **boundary solutions** (solutions with smallest and largest function values) **are assigned an infinite distance value**. All other intermediate solutions are assigned a distance value equal to the absolute difference in the function values of two adjacent solutions. … The overall crowding distance value is calculated as the **sum of individual distance values corresponding to each objective**."*

```
crowding-distance-assignment(I):
  l = |I|
  for each i:  I[i].distance = 0
  for each objective m:
     I = sort(I, m)
     I[1].distance = I[l].distance = infinity   # boundary points always kept
     for i = 2 to (l-1):
        I[i].distance = I[i].distance + ( I[i+1].m - I[i-1].m )
```

Interpretation: `d_i` is *"an estimate of the size of the largest **cuboid** enclosing the point i without including any other point in the population"* — the average side length of that cuboid.

⚠️ **Normalisation flag.** The published TEVC version **divides each term by the objective's range**, i.e. `+ (I[i+1].m − I[i−1].m) / (f_m^max − f_m^min)`. The preprint read shows the **un-normalised** difference. The normalised form is what every modern implementation uses and **is necessary for objectives on different scales.** Treat the normalisation as present in the published paper but verified only indirectly.

Cost: *"Since M independent sorting of at most N solutions … are involved, the above algorithm has **O(M N log N)** computational complexity."*

### Crowded-comparison operator `<_n`

Each individual carries a non-domination rank and a crowding distance. Then

```
i <_n j  ⟺  i_rank < j_rank  OR  (i_rank = j_rank AND i_distance > j_distance)
```

**Rank first; ties broken in favour of the larger crowding distance** (the *less* crowded individual). Used both in binary tournament mating selection and in truncating the splitting front. The point of crowding distance over NSGA's fitness sharing, verbatim: *"the new approach does not require any user-defined parameter for maintaining diversity"* — **no `σ_share`** — and it replaces sharing's `O(N²)` cost.

### The elitist loop

```
R_t = P_t ∪ Q_t                       # parents + offspring, size 2N
F = fast-non-dominated-sort(R_t)
P_{t+1} = empty ; i = 1
while |P_{t+1}| + |F_i| <= N:
    crowding-distance-assignment(F_i)
    P_{t+1} = P_{t+1} ∪ F_i ; i += 1
# F_i is now the "splitting" front
crowding-distance-assignment(F_i)
sort F_i descending by <_n
P_{t+1} = P_{t+1} ∪ F_i[1 : (N − |P_{t+1}|)]
Q_{t+1} = make-new-pop(P_{t+1})   # binary tournament on <_n, SBX, polynomial mutation
```

**Elitism is implicit and total: every parent competes against every offspring in one combined pool, so no non-dominated parent can be lost.**

Overall complexity, verbatim: *"1. Non-dominated sorting is O(M(2N)²), 2. Crowding distance assignment is O(M(2N) log(2N)), and 3. Sorting on <_n is O(2N log(2N)). … the **overall complexity of the above algorithm is O(MN²)**, which is governed by the non-dominated sorting part."*

### The known weakness of crowding distance at M > 2–3

**This motivates everything that follows.** Crowding distance is computed **per objective independently and then summed.** In 2D, consecutive-neighbour ordering along `f_1` and along `f_2` agree (reversed), so the cuboid genuinely measures local neighbourhood. **For M ≥ 3 the per-objective sorts disagree**, and the "nearest neighbour in objective m" is typically not a spatial neighbour at all: **the summed cuboid stops measuring local density.**

Documented consequences:

- A solution far from everything in **one** objective but crowded in all others can get a **large** distance and survive — dominance-resistant / "extremal" solutions survive preferentially.
- The crowding operator loses its diversity-maintaining effect and **can actively push the population toward the boundary of objective space.**
- Deb & Jain motivate NSGA-III partly on this: *"implementation of a diversity-preservation operator (such as the crowding distance operator [5] or clustering operator [6]) becomes a computationally expensive operation [in many objectives]."*
- The deeper problem is **dominance resistance**, addressed by shift-based density estimation: Li, Yang & Liu, "Shift-Based Density Estimation for Pareto-Based Algorithms in Many-Objective Optimization," *IEEE TEVC* 18(3):348–365, 2014, doi:10.1109/TEVC.2013.2262178.

---

## NSGA-III and the many-objective problem

**Deb & Jain, "An Evolutionary Many-Objective Optimization Algorithm Using Reference-Point-Based Nondominated Sorting Approach, Part I: Solving Problems With Box Constraints," *IEEE TEVC* 18(4):577–601, 2014**, doi:10.1109/TEVC.2013.2281535. **Part II**: Jain & Deb, pp. 602–622, doi:10.1109/TEVC.2013.2281534. ⚠️ Note Part II drops the hyphen in "Reference-Point Based" and **the author order reverses to Jain & Deb.**

### The many-objective motivation, in the authors' own words

> *"First and foremost, **the proportion of non-dominated solutions in a randomly chosen set of objective vectors becomes exponentially large with an increase of number of objectives.** Since the non-dominated solutions occupy most of the population slots, any elite-preserving EMO faces a difficulty in accommodating adequate number of new solutions in the population. This slows down the search process considerably."*

Then: *"Second, implementation of a diversity-preservation operator … becomes a computationally expensive operation. Third, visualization of a large-dimensional front becomes a difficult task … the performance metrics (such as hyper-volume measure or other metrics) are either computationally too expensive or may not be meaningful."* They define **"many-objective" as four or more** objectives.

### Actual numbers for the non-dominated fraction

⚠️ **The NSGA-III paper gives no numbers here**, and the Ishibuchi/Tsukamoto/Nojima CEC 2008 review has no free full text. **These were generated by Monte-Carlo simulation rather than guessed** — N = 100 points, objectives i.i.d. U(0,1), minimisation, 40 independent trials, mean fraction of the population that is non-dominated:

| M | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 15 | 20 |
|---|---|---|---|---|---|---|---|---|---|
| fraction | 0.052 | 0.149 | 0.277 | 0.426 | 0.614 | 0.836 | **0.938** | 0.998 | 1.000 |

**At M = 10 with a typical population of 100, ~94% of a random population is already mutually non-dominated**; at M = 15, ~99.8%; at M = 20, essentially all of it. **Pareto dominance has no discriminating power left and non-dominated sorting degenerates to "everything is rank 1" — selection pressure comes entirely from the secondary diversity criterion, which is precisely the criterion that also breaks down in high M.** This is the whole motivation for reference-point niching, decomposition, and indicator-based selection.

The rigorous asymptotic behind it: **Bentley, Kung, Schkolnick & Thompson, "On the Average Number of Maxima in a Set of Vectors and Applications," *JACM* 25(4):536–543, 1978**, doi:10.1145/322092.322095 — ⚠️ **note the author list is four names including Schkolnick, often mis-cited as "Bentley, Kung & Thompson."** The expected number of maxima among n vectors with independent continuous components in d dimensions is **`Θ((ln n)^{d−1} / (d−1)!)`**.

⚠️ **Caveat on using this formula at small n — a trap several secondary sources fall into:** it is an `n → ∞` asymptotic valid for `n >> e^d`. Evaluating it at n = 100 gives fractions 0.046 (M=2), 0.106 (M=3), 0.187 (M=5), **0.026 (M=10)** — the M=10 value is **wildly below** the simulated 0.938 because `100 << e^10`. **Use the simulation numbers, not the asymptotic, for realistic population sizes.**

### What changed from NSGA-II

The elitist shell is **unchanged**. **The crowding-distance truncation of the splitting front `F_l` is entirely replaced by reference-point/reference-direction niching.** Skeleton (Algorithm 1):

```
 4: (F1,F2,...) = Non-dominated-sort(R_t)
 5: repeat  S_t = S_t ∪ F_i ; i = i+1   until |S_t| >= N
 8: last front to be included: F_l = F_i
 9: if |S_t| = N then P_{t+1} = S_t ; break
12:   P_{t+1} = ∪_{j=1}^{l-1} F_j
13:   K = N - |P_{t+1}|                        # points still needed from F_l
14:   Normalize objectives and create reference set Z^r
15:   [π(s), d(s)] = Associate(S_t, Z^r)       # π(s): closest ref point; d: distance
16:   ρ_j = Σ_{s ∈ S_t \ F_l} (π(s) = j ? 1 : 0)   # niche counts from accepted members
17:   Niching(K, ρ_j, π, d, Z^r, F_l, P_{t+1})
```

**Also notable and usually omitted: NSGA-III uses no explicit mating selection at all.** Verbatim: *"In NSGA-III, we have already performed a careful elitist selection of solutions … For all these reasons, we do not employ any explicit selection operation with NSGA-III. The population Q_{t+1} is constructed by applying the usual crossover and mutation operators by **randomly picking parents** from P_{t+1}."* They also recommend *"a relatively larger value of distribution index in the SBX operator"* to keep offspring near parents.

### Das–Dennis structured reference points, and the combinatorial blow-up

Verbatim: *"in this paper we use Das and Dennis's systematic approach that places points on a normalized hyper-plane — a (M−1)-dimensional unit simplex — which is equally inclined to all objective axes and has an intercept of one on each axis. **If p divisions are considered along each objective, the total number of reference points (H) in an M-objective problem is given by: H = C(M + p − 1, p)**. For example, in a three-objective problem … If four divisions (p = 4) are chosen for each objective axis, H = C(6,4) **or 15 reference points** will be created."*

Underlying method: **Das & Dennis, "Normal-Boundary Intersection," *SIAM J. Optimization* 8(3):631–657, 1998**, doi:10.1137/S1052623496307510.

**The paper's actual numbers, and the two-layer workaround:**

| M | configuration | H |
|---|---|---|
| 3 | p = 12 | 91 |
| 5 | p = 6 | 210 |
| 8 | **two layers**: boundary p = 3 (120 pts) + inside p = 2 (36) | 156 |
| 10 | two layers | 275 |
| 15 | two layers | 135 |

Verbatim on why: *"Note that as long as p >= M is not chosen, **no intermediate point will be created** by Das and Dennis's systematic approach. For eight-objective problems, even if we use p = 8 (to have at least one intermediate reference point), **it requires 5,040 reference points.** To avoid such a situation, we use two layers of reference points with small values of p."* Also: *"for a computationally fast procedure, we have set **N almost equal to H**"* — **one niche per population slot.**

From pymoo's reference-direction docs: Das–Dennis *"cannot produce an arbitrary number of points desired,"* and in higher dimensions most points land on the simplex **boundary**; for `p > M` the number of interior points is `C(p−1, p−M)`. pymoo therefore also ships a **Riesz s-energy** generator (minimises a Riesz energy with `s = M²`, via Adam + gradient projection onto the simplex) which *"can produce any number of well-spaced points in any dimension"*, plus `multi-layer`, `layer-energy` and `incremental`.

### Adaptive normalisation — the part people skip, and it matters

Algorithm 2:

1. **Ideal point**: `z^min_j = min_{s ∈ S_t} f_j(s)`.
2. **Translate**: `f'_j(s) = f_j(s) − z^min_j`.
3. **Extreme points via ASF**: for each axis direction j, `z^{j,max} = argmin_{s ∈ S_t} ASF(s, w^j)` where `ASF(x, w) = max_i f'_i(x)/w_i`, and `w^j = (ε,…,ε)^T` with **ε = 10⁻⁶** except `w^j_j = 1`. (Verbatim: *"For w_i = 0, we replace it with a small number 10^{-6}."*)
4. **Hyperplane and intercepts**: the M extreme vectors *"are then used to constitute a M-dimensional linear hyper-plane"*; compute its intercept `a_i` on each axis — **one M × M matrix inversion.**
5. **Normalise**: `f^n_i(x) = (f_i(x) − z^min_i) / (a_i − z^min_i)`. *"Note that the intercept on each normalized objective axis is now at f^n_i = 1 and a hyper-plane constructed with these intercept points will make Σ_i f^n_i = 1"* — **so the Das–Dennis points already lie on it and need no re-mapping.**

**This runs every generation using the extreme points found so far, which is what makes NSGA-III scale-invariant without user-supplied bounds.**

### Association and niching

**Associate** (Algorithm 3): the reference **line** for reference point z is `w = z` through the origin; for each s compute the **perpendicular** distance to every reference line, `d_perp(s, w) = ‖s − (wᵀs)w/‖w‖²‖`; then `π(s) = argmin_{w ∈ Z^r} d_perp(s, w)` and `d(s) = d_perp(s, π(s))`.

**Niching** (Algorithm 4) — the exact rule:

```
k = 1
while k <= K:
    J_min = { j : argmin_{j ∈ Z^r} ρ_j }      # least-crowded reference points
    j̄ = random(J_min)                         # tie-break at random
    I_j̄ = { s : π(s) = j̄, s ∈ F_l }
    if I_j̄ nonempty:
        if ρ_j̄ = 0:  P_{t+1} ∪= { argmin_{s ∈ I_j̄} d(s) }   # closest to the line
        else:        P_{t+1} ∪= random(I_j̄)
        ρ_j̄ += 1 ; F_l = F_l \ s ; k += 1
    else:
        Z^r = Z^r \ { j̄ }     # no candidate: drop this reference point this generation
```

**The asymmetry is deliberate:** an **unoccupied** reference direction (ρ = 0) gets the `F_l` member **closest to its line** (push toward the direction); an **already-occupied** one gets a **random** associate (no extra convergence pressure where a niche is already filled).

### NSGA-III complexity

Verbatim (§III-G): non-dominated sorting of 2N M-dimensional vectors *"require O(N log^{M−2} N) computations"* (**Jensen's divide-and-conquer sort, not the `O(MN²)` NSGA-II sort**); ideal point `O(MN)`; translation `O(MN)`; **extreme points `O(M²N)`**; intercepts *"one matrix inversion of size M × M, requiring **O(M³)**"*; normalisation `O(N)`; mapping aspiration points `O(MH)`; association `O(MNH)`; niching *"larger of O(L²) or O(LH)"* with `L = |F_l| <= 2N`. **Conclusion, verbatim: "the overall worst-case complexity of one generation of NSGA-III is O(N² log^{M−2} N) or O(N² M), whichever is larger."**

### Relatives worth naming

**U-NSGA-III** (unifies single-, multi- and many-objective) — Seada & Deb, *IEEE TEVC* 20(3):358–369, 2016, doi:10.1109/TEVC.2015.2459718. **RVEA** (reference-vector guided, angle-penalised distance, adaptive reference vectors) — Cheng, Jin, Olhofer & Sendhoff, *IEEE TEVC* 20(5):773–791, 2016, doi:10.1109/TEVC.2016.2519378. **AGE-MOEA** (adapts to the front's **non-Euclidean** geometry rather than assuming a simplex) — Panichella, GECCO 2019, pp. 595–603, doi:10.1145/3321707.3321839; AGE-MOEA2 in GECCO 2022, pp. 565–573.

---

## SPEA2

**Zitzler, Laumanns & Thiele, "SPEA2: Improving the Strength Pareto Evolutionary Algorithm," TIK-Report 103, ETH Zurich, 2001**, doi:10.3929/ethz-a-004284029 (the actual TIK report read). Notation: `P_t` = population (size N), `P̄_t` = archive (size N̄), `M = N + N̄`. **Fitness is minimised in SPEA2.**

**Strength value**: `S(i) = |{ j | j ∈ P_t + P̄_t AND i dominates j }|`, *"representing the number of solutions it dominates"*, where `+` is multiset union. **Computed over population and archive together** (unlike SPEA, where only archive members counted).

**Raw fitness**: `R(i) = Σ_{j ∈ P_t + P̄_t, j dominates i} S(j)` — *"the raw fitness is determined by the **strengths of its dominators** in both archive and population, as opposed to SPEA where only archive members are considered."* Key property: *"fitness is to be **minimized** here, i.e., **R(i) = 0 corresponds to a nondominated individual**, while a high R(i) value means that i is dominated by many individuals (which in turn dominate many individuals)."* **The design rationale: summing dominators' *strengths* (rather than just counting dominators) stops individuals dominated by the same archive member from all getting identical fitness.**

**Density estimate — k-th nearest neighbour**: *"an adaptation of the k-th nearest neighbor method (Silverman 1986) … for each individual i the distances (in objective space) to all individuals j in archive and population are calculated and stored in a list. After sorting the list in increasing order, the k-th element gives the distance sought, denoted as σ^k_i. As a common setting, we use **k equal to the square root of the sample size**, thus, **k = sqrt(N + N̄)**."*

```
D(i) = 1 / (σ^k_i + 2)
```

*"In the denominator, **two is added to ensure that its value is greater than zero and that D(i) < 1**."* **That `D(i) < 1` bound is the whole point:** since `R(i)` is a non-negative integer and `R(i) = 0 ⟺` non-dominated, adding a sub-1 density term can **never** let a dominated individual beat a non-dominated one.

**Final fitness: `F(i) = R(i) + D(i)`.**

Runtime, verbatim: *"The run-time of the fitness assignment procedure is dominated by the density estimator (**O(M² log M)**), while the calculation of the S and R values is of complexity **O(M²)**."*

**Fixed-size archive.** Two properties distinguish it from SPEA — *"i) the number of individuals contained in the archive is **constant over time**, and ii) the truncation method **prevents boundary solutions being removed**."*

Step 1 — copy all non-dominated individuals: `P̄_{t+1} = { i : F(i) < 1 }` (which is exactly `R(i) = 0` by the `D(i) < 1` bound). Then:

- `|P̄_{t+1}| = N̄` → done.
- **`< N̄` (fill)**: *"the best N̄ − |P̄_{t+1}| **dominated** individuals in the previous archive and population are copied … by **sorting the multiset P_t + P̄_t according to the fitness values** and copy the first N̄ − |P̄_{t+1}| individuals i with F(i) >= 1."*
- **`> N̄` (truncate)**: iteratively remove the i for which `i ≼_d j` for **all** j, where `i ≼_d j :⟺ ∀ 0 < k < |P̄_{t+1}| : σ^k_i = σ^k_j` OR `∃ 0 < k : (∀ 0 < l < k : σ^l_i = σ^l_j) AND σ^k_i < σ^k_j`. Verbatim gloss: *"the individual which has the **minimum distance to another individual** is chosen at each stage; if there are several individuals with minimum distance the **tie is broken by considering the second smallest distances and so forth**."* **This lexicographic-on-the-sorted-distance-vector rule is exactly what guarantees boundary solutions survive** (they have large nearest-neighbour distances). Cost: *"the worst run-time complexity of the truncation operator is **O(M³)** …, on average the complexity will be lower (**O(M² log M)**)."*

One more SPEA2 difference, verbatim: *"**only members of the archive participate in the mating selection process.**"* Mating selection is binary tournament with replacement on the archive.

---

## MOEA/D

**Zhang & Li, "MOEA/D: A Multiobjective Evolutionary Algorithm Based on Decomposition," *IEEE TEVC* 11(6):712–731, 2007**, doi:10.1109/TEVC.2007.892759 (typeset IEEE PDF read). ⚠️ Its displayed equations are in math fonts that do not text-extract, so the formulas below are the **standard forms cross-checked against the surrounding prose and the extractable footnotes** (which did reveal the PBI `d1`/`d2` definitions).

**The core idea:** decompose the problem of approximating PF into **N scalar subproblems**, one per weight vector `λ¹..λ^N`, and solve them **simultaneously** with a single population of N individuals — individual i is the best solution found so far for subproblem i. Verbatim: *"At each generation, the population is composed of the best solution found so far (i.e. since the start of the run of the algorithm) for each subproblem. … Each subproblem … is optimized in MOEA/D by using information only from its **neighboring subproblems**."*

**The justification**, verbatim: *"the optimal solution of g^te(x|lambda^i) should be close to that of g^te(x|lambda^j) if lambda^i and lambda^j are close to each other. Therefore, any information about these g's with weight vectors close to lambda^i should be helpful for optimizing g^te(x|lambda^i). **This is a major motivation behind MOEA/D.**"*

### The three standard aggregations

**(A) Weighted sum**: `g^ws(x|λ) = Σ_i λ_i f_i(x)`. Limitation as above.

**(B) Tchebycheff**: `g^te(x|λ,z*) = max_i λ_i |f_i(x) − z*_i|`.

**(C) PBI — penalty-based boundary intersection.** The BI idea is the constrained problem `min d s.t. F(x) − z* = −d·λ/‖λ‖`, i.e. find where the line through `z*` with direction λ hits the attainable set's boundary. The equality constraint is awkward in an EA, so they penalise it:

```
minimise g^pbi(x|λ,z*) = d1 + θ · d2
  d1 = ‖(F(x) − z*)ᵀλ‖ / ‖λ‖        (distance ALONG the reference line)
  d2 = ‖F(x) − (z* + d1·λ/‖λ‖)‖     (PERPENDICULAR distance)
```

**Penalty value used: θ = 5.** Verbatim: *"In our experiment, the penalty factor theta in g^pbi is set to be 5."*

PBI's advantages, verbatim: *"In the case of more than two objectives, let both the PBI approach and the Tchebycheff approach use the same set of evenly distributed weight vectors, **the resultant optimal solutions in the PBI should be much more uniformly distributed than those obtained by the Tchebycheff approach**, particularly when the number of weight vectors is not large."* And: *"If F(x) dominates F(y), it is still possible that g^te(x) = g^te(y), while it is rare for g^pbi."* Its cost, verbatim: *"these benefits come with a price. **One has to set the value of the penalty factor.**"*

### Neighbourhood structure and the main loop

*"a **neighborhood of weight vector lambda^i is defined as a set of its several closest weight vectors**."* Step 1.2: *"**Compute the Euclidean distances between any two weight vectors** and then work out the T closest weight vectors to each weight vector."* Note *"lambda^i's closest vector is itself, and then i is in B(i)."* **T is the niching / neighbourhood size and is an input parameter.**

State: population `x¹..x^N`; `FV^i = F(x^i)`; `z` the best-so-far value for each objective (verbatim: *"Since it is often very time-consuming to find the exact reference point z*, we use z … as a substitute"*); and an external population EP of non-dominated solutions.

```
Step 2) Update: for i = 1..N do
  2.1) Reproduction: randomly select two indexes k, l from B(i), and generate a
       new solution y from x^k and x^l by using genetic operators.
  2.2) Improvement: apply a problem-specific repair/improvement heuristic on y
       to produce y'.
  2.3) Update of z: for each j, if z_j > f_j(y') then z_j = f_j(y').
  2.4) Update of Neighboring Solutions: for each index j in B(i),
       if g(y'|λ^j, z) <= g(x^j|λ^j, z) then x^j = y' and FV^j = F(y').
  2.5) Update of EP: remove from EP all vectors dominated by F(y');
       add F(y') to EP if no vectors in EP dominate F(y').
Step 3) Stop if the criterion is met, output EP; else go to Step 2.
```

**Two things to note precisely:** (1) **mating is restricted to the neighbourhood** — both parents come from `B(i)`, not the whole population. (2) **Replacement is also neighbourhood-scoped and is a many-slot replacement**: one offspring `y'` is tested against **every** subproblem `j ∈ B(i)` and can replace the incumbent in **all** of them. **This is the known source of MOEA/D's diversity loss — one strong offspring can flood a whole neighbourhood** — which later variants fix with a replacement cap `n_r`.

### Why it scales better to many objectives

**Selection pressure comes from scalar comparisons against fixed weight vectors, not from Pareto dominance, so it does not degrade as M grows** (compare the 94%-non-dominated-at-M=10 figure above). And per-generation cost is lower: the paper claims *"MOEA/D has lower computational complexity than NSGA-II at each generation"*, noting *"the computational complexity of each generation in NSGA-II is O(mN²)."* ⚠️ The exact symbolic expression for MOEA/D's own per-generation complexity is in a math-font equation that did not text-extract. **The standard value `O(mNT)` is reconstructed from the verified structure of Step 2, not quoted.**

### Weaknesses

1. **Performance depends on the aggregation function and the front's geometry.** Weighted sum cannot reach non-convex fronts at all; Tchebycheff gives non-uniform spread in high M; PBI needs θ tuned.
2. **Weight-vector distribution mismatch for irregular fronts.** A uniform simplex of weights maps to a uniform set of front points **only when the front is itself roughly simplex-like** (a "regular/triangular" front). On inverted, degenerate, disconnected, badly scaled or strongly curved fronts, many weight vectors collapse onto the same front region or point at nothing at all, and **the effective population shrinks.** The definitive demonstration: **Ishibuchi, Setoguchi, Masuda & Nojima, "Performance of Decomposition-Based Many-Objective Algorithms Strongly Depends on Pareto Front Shapes," *IEEE TEVC* 21(2):169–190, 2017**, doi:10.1109/TEVC.2016.2587749. **And the corroborating indictment of the benchmarks**, verbatim from Tanabe & Ishibuchi 2020: *"some decomposition-based EMOAs (e.g., MOEA/D and NSGA-III) work well on the DTLZ and WFG problems even with many objectives. **This is because most DTLZ and WFG problems have triangular shape Pareto fronts.**"* — i.e. **the benchmarks have been flattering decomposition methods.**
3. Neighbourhood-wide replacement can collapse diversity (above).

**Variants:** **MOEA/D-DE** (DE reproduction + polynomial mutation, a probability δ of mating **outside** the neighbourhood, and a cap `n_r` on how many neighbours one offspring may replace — the two fixes for the diversity problem) — **Li & Zhang, "Multiobjective Optimization Problems With Complicated Pareto Sets, MOEA/D and NSGA-II," *IEEE TEVC* 13(2):284–302, 2009**, doi:10.1109/TEVC.2008.925798 (authors Hui Li & Qingfu Zhang, in that order). **MOEA/D-AWA** (adaptive weight adjustment, for irregular fronts) — Qi et al., *Evolutionary Computation* 22(2):231–264, 2014. **MOEA/D-EGO** (surrogate-assisted) — Zhang, Liu, Tsang & Virginas, *IEEE TEVC* 14(3):456–474, 2010.

---

## The indicator-based family

### SMS-EMOA

**Beume, Naujoks & Emmerich, "SMS-EMOA: Multiobjective selection based on dominated hypervolume," *European Journal of Operational Research* 181(3):1653–1669, 2007**, doi:10.1016/j.ejor.2006.08.008. ⚠️ The EJOR text is behind Elsevier with no OA copy; **what was verified instead is the EMO-2005 precursor by the same three authors, which introduces exactly the SMS-EMOA scheme** (Emmerich, Beume & Naujoks, EMO 2005, LNCS 3410). Everything quoted below is from the 2005 paper.

Verbatim: *"a **steady-state (mu+1)-EMOA**, the so-called **S metric selection EMOA** (SMS-EMOA)… It is a steady-state evolutionary algorithm with **constant population size** that firstly uses non-dominated sorting as a ranking criterion and secondly the **hypervolume measure as selection criterion to discard that individual, which contributes least hypervolume to the worst-ranked Pareto-optimal front**."*

The `Reduce` operator: *"First, the Pareto fronts … are computed using the **fast-nondominated-sort-algorithm** [= NSGA-II's]. Afterwards, one individual is discarded from the **worst ranked front**. If this front comprises |R_I| > 1 individuals, the individual s in R_I is eliminated that minimizes `ΔS(s, R_I) := S(R_I) − S(R_I \ {s})`."*

**For two objectives there is a closed form**: sort the worst-ranked front ascending by `f1` (which, since the points are mutually non-dominated, also sorts descending by `f2`); then

```
ΔS(s_i, R_I) = ( f1(s_{i+1}) − f1(s_i) ) · ( f2(s_{i−1}) − f2(s_i) )
```

(boundary points get infinity via the reference point).

Complexity, verbatim: *"The runtime complexity of the hypervolume procedure in the case of two objective functions is governed by the sorting algorithm. It is **O(mu log mu)** … For the case of more than two objectives, we suggest to use the algorithm of Fleischer … the runtime complexity of SMS-EMOA is governed by the calculation of the hypervolume and is **O(mu³ n²)**."*

**The theoretical pay-off**, verbatim: *"By greedily discarding the individual that minimizes ΔS(s, R_I), it is guaranteed that the subset which covers the **maximal hypervolume** compared to all |R_I| possible subsets remains in the population (for a proof we refer to Knowles and Corne). With regard to the replacement operator this also implies that the covered hypervolume of a population **cannot decrease** by application of the Reduce operator, i.e. … S(P_t) <= S(P_{t+1})."*

One nice detail, verbatim: *"Our method of determining the solution contributing least to the hypervolume is actually **independent from the choice of the reference point**. The reference point is only needed to calculate the hypervolume of extremal points of a front"* — i.e. **SMS-EMOA's *selection* is largely reference-point-robust even though the *indicator* is not.**

pymoo's implementation computes **exact** hypervolume contributions for **up to five objectives** via the `moocore` library, and **switches to an approximation automatically above five.**

### IBEA

**Zitzler & Künzli, "Indicator-Based Selection in Multiobjective Search," PPSN VIII, LNCS 3242, pp. 832–842, 2004**, doi:10.1007/978-3-540-30217-9_84.

The thesis, verbatim: *"first define the optimization goal in terms of a **binary performance measure (indicator)** and then **directly use this measure in the selection process**. … IBEA can be adapted to the preferences of the user and moreover **does not require any additional diversity preservation mechanism** such as fitness sharing."*

The naive fitness is `F'(x1) = Σ_{x2 ∈ P\{x1}} I({x2},{x1})` — *"a measure for the 'loss in quality' if x1 is removed from the population."* But IBEA actually uses an **exponentially amplified** form, to be **maximised**:

```
F(x1) = Σ_{x2 ∈ P \ {x1}}  −e^{ −I({x2},{x1}) / κ }
```

with `κ > 0` *"a scaling factor depending on I and the underlying problem."* Rationale: *"the **influence of small indicator values contributes much more to the overall fitness than large values**"* (exploiting that for a dominance-preserving indicator, `I({x1},{x2}) < I({x2},{x1})` when x1 dominates x2).

**Theorem 1, verbatim: "Let I be a binary quality indicator. If I is dominance preserving, then it holds that x1 dominates x2 ⟹ F(x1) > F(x2)."** — the fitness scheme is Pareto-dominance compliant.

Environmental selection: *"Iterate the following three steps until the size of population P does not exceed alpha: 1. Choose an individual x* in P with the **smallest** fitness value… 2. Remove x* from the population. 3. **Update the fitness values of the remaining individuals**, i.e. F(x) = F(x) + e^{−I({x*},{x})/κ}."* **The incremental update is exact — this is the cheap part of IBEA.** Indicators used: the **additive ε-indicator** and the **binary hypervolume indicator `I_HD`**; on the latter's cost, *"calculation of the I_HD(A,B)-values is computationally expensive for approximations containing several decision vectors, it is of order **O(n)** if two decision vectors are compared."*

### Hypervolume's theoretical appeal — the exact statements

**(i) The strict-monotonicity claim**, verbatim from HypE's abstract (Bader & Zitzler, TIK-Report 286, 2008): *"In the field of evolutionary multi-criterion optimization, **the hypervolume indicator is the only single set quality measure that is known to be strictly monotonic with regard to Pareto dominance: whenever a Pareto set approximation entirely dominates another one, then also the indicator value of the former will be better.**"*

**(ii) The formal definitions**, from Li & Yao's survey. **Pareto compliance (= monotonicity)**, assuming a smaller result is preferable: `∀A,B : A ≼ B ⟹ I(A) <= I(B)`. Verbatim: *"Pareto compliance guarantees that a QI does not contradict the order of solution sets induced by the weak Pareto dominance relation."* **Strict Pareto compliance**: `∀A,B : A ⊲ B ⟹ I(A) < I(B)`, attributed to Zitzler, Brockhoff & Thiele 2007. Verbatim: *"The strict Pareto compliance implies that only the Pareto front achieves a unique optimal value for a problem. So far, **the HV indicator (and its variants) is the only popular unary QI having this property.**"* Citation: **Zitzler, Brockhoff & Thiele, "The Hypervolume Indicator Revisited," EMO 2007, LNCS 4403, pp. 862–876**, doi:10.1007/978-3-540-70928-2_64.

**(iii) The precise formal statement**, from the Guerreiro/Fonseca/Paquete survey (arXiv:2005.00515; published as *ACM Computing Surveys* 54(6), Article 119, 2021, doi:10.1145/3453474): *"Given a binary relation R on point sets, a set-quality indicator I (to be maximized) is said to be **weakly R-monotonic** if ARB implies I(A) >= I(B) …, and it is **strictly R-monotonic** if ARB implies I(A) > I(B). … The hypervolume indicator is well acknowledged by its properties. **It is scaling independent and it is strictly ≺-monotonic** … **This implies that this indicator is maximal for the Pareto front** and that scaling objectives does not affect the order imposed on point sets."* Also: *"Ulrich and Thiele showed that the hypervolume indicator is a **submodular** function."*

**(iv) The other canonical citation, and its statement is more cautious than the "strictly monotonic" framing** — worth quoting exactly. **Zitzler, Thiele, Laumanns, Fonseca & Grunert da Fonseca, "Performance assessment of multiobjective optimizers: an analysis and review," *IEEE TEVC* 7(2):117–132, 2003**, doi:10.1109/TEVC.2003.810758: *"**The hypervolume indicator is the only unary indicator we are aware of that is capable of detecting that A is NOT WORSE than B for all pairs (A,B).** … We notice that from A ⊲ B follows that I_H(A) > I_H(B) …. **This observation implies both ≼-compatibility and ⊲-completeness.**"*

**The two are consistent but say different things: hypervolume lets you *infer* "B is not better than A" from `I_H(A) > I_H(B)`; it does not let you *certify* "A is better than B."** Zitzler 2003's conclusion: *"Existing unary indicators **at best allow to infer that an approximation set is not worse than another**."*

⚠️ **A paper titled "Why quality indicators are better than Pareto-dominance-based set measures" (Zitzler et al.) appears not to exist** — OpenAlex was searched twice with the full title and with partial phrasings and no such work surfaced. **Do not cite it.** The correct citations are Zitzler et al. 2003 for the unary-indicator limitation and ≼-compatibility, and Zitzler, Brockhoff & Thiele 2007 for strict Pareto compliance.

### Computational cost of hypervolume — the precise claims

**#P-hardness.** **Bringmann & Friedrich, "Approximating the volume of unions and intersections of high-dimensional geometric objects," *Computational Geometry* 43(6–7):601–610, 2010**, doi:10.1016/j.comgeo.2010.03.004; arXiv:0809.0835. From the abstract: *"While showing that this problem is **#P-hard already for very simple bodies (i.e., axis-parallel boxes)**, we give a fast FPRAS … This implies that **Klee's measure problem and the hypervolume indicator can be approximated efficiently even though they are #P-hard and hence cannot be solved exactly in time polynomial in the number of dimensions unless P=NP.** For the analogous problem of the **intersection** … we prove #P-hardness for boxes and show that **there is no multiplicative polynomial-time 2^{d^{1−ε}}-approximation** for certain boxes unless NP=BPP."*

⚠️ **Note the precision: #P-hardness is in the number of objectives d (the dimension), not in n.** For **fixed d, polynomial exact algorithms exist.** And **the `2^{d^{1−ε}}` inapproximability result is for *intersections*, not for the hypervolume (union)** — a commonly mis-attributed detail.

**Least-contributor hardness** — and this is the one that matters for SMS-EMOA and HypE, because the least-contributor problem is exactly what steady-state hypervolume selection needs. **Bringmann & Friedrich, "Approximating the least hypervolume contributor: NP-hard in general, but fast in practice," *Theoretical Computer Science* 425:104–116, 2012**, doi:10.1016/j.tcs.2010.09.026; arXiv:0812.2636: *"We show that **exact calculation of the hypervolume contribution is #P-hard while its approximation is NP-hard.** The same holds for the calculation of the minimal contribution. We also prove that it is **NP-hard to decide whether a solution has the least hypervolume contribution.** Even deciding whether the contribution of a solution is at most (1+eps) times the minimal contribution is NP-hard. This implies that it is **neither possible to efficiently find the least contributing solution (unless P = NP) nor to approximate it (unless NP = BPP).** Nevertheless … we present a fast approximation algorithm … [that] solves very large problem instances which are intractable for exact algorithms (e.g., **10000 solutions in 100 dimensions**) within a few seconds."*

Corroboration from the Guerreiro/Fonseca/Paquete survey: *"the Hypervolume and OneContribution problems are known to be **#P-hard**. **Even deciding if a point is the least contributor is #P-hard**. Moreover, HSSP [hypervolume subset selection] was recently shown to be **NP-hard** for d >= 3"* (Bringmann, Cabello & Emmerich, SoCG 2017).

**Exact algorithm complexities by dimension**, from the same survey:

- **d = 2, 3**: `Θ(n log n)` (HV3D / HV3D+ for d = 3, with `O(n)` space).
- **d ≥ 4**: **Chan's algorithm, `O(n^{d/3} polylog n)`** — *"currently the best time complexity to compute Hypervolume for d >= 4"* (Chan, "Klee's Measure Problem Made Easy," FOCS 2013).
- **The WFG algorithm** (the fastest **in practice** for d > 7): originally reported `O(2^{n+1})`, tightened by Lacour et al. to an `O(n^{d−1})` upper bound with an `Ω(n^{d/2} log n)` lower bound. The survey recommends Chan's for best asymptotics *"but, because [of large constants, in practice other algorithms win]."*
- ⚠️ Lower-bound citation: Beume, Fonseca, López-Ibáñez, Paquete & Vahrenhold, *IEEE TEVC* 13(5):1075–1082, 2009 — **this paper was not read**; the commonly quoted `Ω(n log n)` lower bound for d ≥ 2 and the Klee's-measure reduction are attributed to it but only its bibliographic record was verified.

**HypE** — the practical answer. **Bader & Zitzler, "HypE: An Algorithm for Fast Hypervolume-Based Many-Objective Optimization," *Evolutionary Computation* 19(1):45–76, 2011**, doi:10.1162/EVCO_a_00009. The key idea, verbatim: *"the high computational effort required for hypervolume calculation has so far prevented to fully exploit the potential of this indicator … This paper … proposes a fast search algorithm that uses **Monte Carlo simulation to approximate the exact hypervolume values. The main idea is that NOT THE ACTUAL INDICATOR VALUES ARE IMPORTANT, BUT RATHER THE RANKINGS OF SOLUTIONS induced by the hypervolume indicator.**"* **Because only the ranking matters, a coarse estimate suffices — which is what makes hypervolume-based selection viable at M >> 3.**

**R2 / IGD-based selection.** R2 (and R1, R3) integrates a **set of scalarising (utility) functions** over the approximation set; Li & Yao: *"the R family and IPF … both integrate over a set of utility functions."* This makes R2 an attractive cheap proxy for hypervolume (weakly Pareto compliant, near-linear cost). ⚠️ The Hansen & Jaszkiewicz 1998 attribution was verified **only** via Li & Yao's reference table; it is a Technical University of Denmark report (IMM-REP-1998-7), which typically has no DOI. IGD-based selection: Sun, Yen & Zhang, *IEEE TEVC* 23(2):173–187, 2019.

---

## Performance indicators — and why comparison is itself hard

### Hypervolume (HV, a.k.a. the S metric)

Definition, verbatim from Li & Yao: *"Given a solution set A and a reference point r, **HV(A) = λ( ∪_{a ∈ A} { x | a ≺ x ≺ r } )** where λ denotes the **Lebesgue measure**."* Higher is better. **Needs only a reference *point*, not a reference *front* — its main practical advantage over IGD.**

**Reference-point sensitivity is the real problem.** Verbatim from Li & Yao:

- *"there are few studies/theoretical guidelines on the choice of the reference point in HV, except for a few in particular situations."*
- *"Ishibuchi et al. (2017, 2018a) have demonstrated a clear difference of specifying the proper reference point for problems with a **simplex-like Pareto front** and an **inverted simplex-like Pareto front**. They have also shown experimentally that **a slightly worse reference point than the nadir point is not always appropriate**, especially for the case of many-objective optimisation and/or a small population size."*
- *"the HV indicator **prefers the knee regions, and is biased to convex regions over concave regions**. As proven in Auger et al. (2009b), **the distribution of a set of solutions that achieves the maximum HV value depends largely on the slope of the Pareto front.**"*
- The reference-point citation to use: **Ishibuchi, Imada, Setoguchi & Nojima, "How to Specify a Reference Point in Hypervolume Calculation for Fair Performance Comparison," *Evolutionary Computation* 26(4):411–440, 2018**, doi:10.1162/EVCO_a_00226.
- **Optimal μ-distributions** (what a finite HV-maximal set actually looks like), from Guerreiro et al.: *"the exact location of the points in an optimal subset of a given size mu is known only for **continuous linear fronts**. In this case, there is a unique optimal subset where all points are on the Pareto front and uniformly spaced between two outer points, the position of which depends both on the reference point and on the two extreme points of the Pareto front. … **not much is known about optimal mu-distributions** [in three objectives]."*

**Practical rule: HV is incomparable across papers unless the reference point and the normalisation are both stated. State them.**

### GD, IGD, GD+, IGD+

From pymoo's indicator docs — with Z the reference front and A the obtained set, all for minimisation:

```
GD(A)   = (1/|A|) · ( Σ_{a_i ∈ A} d_i^p )^{1/p}      p = 2;  d_i = min_{z ∈ Z} ‖a_i − z‖
IGD(A)  = (1/|Z|) · ( Σ_{z_i ∈ Z} d̂_i^p )^{1/p}      p = 2;  d̂_i = min_{a ∈ A} ‖z_i − a‖
GD+(A)  = (1/|A|) · ( Σ_{a_i ∈ A} (d_i^+)² )^{1/2}
IGD+(A) = (1/|Z|) · ( Σ_{z_i ∈ Z} (d_i^+)² )^{1/2}
```

where the **modified distance** is, for minimisation,

```
d^+(a, z) = ‖ ( max{a_1 − z_1, 0}, …, max{a_M − z_M, 0} ) ‖
```

i.e. **only the components in which `a` is worse than `z` contribute.** **That single change is what buys Pareto compliance**: if a dominates a', then `d+(a, z) <= d+(a', z)` for every z, so the indicator can never rank a dominated set better. Lower is better for all four; GD/IGD need a **reference front**; IGD is the standard convergence+diversity scalar in the field.

⚠️ **A trap: the NSGA-III paper uses `IGD(A,Z) = (1/|Z|) Σ_i min_j d(z_i, a_j)` — the p = 1 average form, not pymoo's p = 2 form. The IGD you compute is not the IGD someone else computed unless p, normalisation and Z all match.**

The IGD+ citation: **Ishibuchi, Masuda, Tanigaki & Nojima, "Modified Distance Calculation in Generational Distance and Inverted Generational Distance," EMO 2015, LNCS 9019, pp. 110–125**, doi:10.1007/978-3-319-15892-1_8. ⚠️ The chapter's full text could not be obtained; the compliance claim is verified from **two independent secondary sources**: pymoo's docs — IGD+ is *"weakly Pareto compliant whereas the original IGD is not"* — and Li & Yao: *"Many widely-used QIs are **Pareto non-compliant, such as GD, SP, MS, and IGD**. … **The studies in Ishibuchi et al. (2015) are an example along these lines, where GD and IGD are transformed into two Pareto compliant indicators GD+ and IGD+.**"*

**Two important nuances from Li & Yao.** IGD+ is **weakly** compliant, **not strictly** — *"Pareto compliant QIs may not fully distinguish between solution sets subject to the 'better' relation. That is, when A ⊲ B, a Pareto compliant indicator I may return I(A) = I(B)."* And **IGD+ does not fix reference-set sensitivity** — *"This particularly applies to a QI that is sensitive to the reference set's distribution, **such as IGD and IGD+**."* What IGD+ **does** fix is dominance-resistant solutions in the reference set — *"**IGD+ is insensitive to the DRSs**."* Useful special case: GD and IGD can be compliant *"when used for a **bi-objective problem with a continuous Pareto front**"* (Schütze et al. 2012).

### Additive and multiplicative ε-indicator

From Zitzler et al. 2003 — the **binary** `I_ε` is the paper's own contribution and its headline positive result. For minimisation:

- **Additive**: `I_{ε+}(A,B) = inf_{ε ∈ R} { ∀ b ∈ B, ∃ a ∈ A : a_i − ε <= b_i ∀ i }` — **the smallest additive amount by which A must be shifted to weakly dominate B.**
- **Multiplicative**: `I_ε(A,B) = inf_{ε > 0} { ∀ b ∈ B, ∃ a ∈ A : a_i <= ε·b_i ∀ i }` (requires strictly positive objectives).
- **`I_{ε+}(A,B) <= 0 ⟺ A ≼ B`.** Verbatim conclusion: *"The binary epsilon-indicator proposed in this paper, e.g., **is capable of detecting whether an approximation set is better than another.**"* And: *"it has a clear interpretation — in contrast to, e.g., the coverage and the hypervolume indicators"* and, unlike hypervolume, **it is cheap.**
- **The unary variant `I_{ε+}(A, R)` against a fixed reference set R is what most papers actually report; it is weakly compliant but loses the "better than" detection power.**
- It is notably **reference-set-robust**: *"**the epsilon-indicator and PCI … are able to work with the reference set having any distribution and location**."*

### Spread / Δ

The Δ diversity metric is from the NSGA-II paper itself:

```
Δ = ( d_f + d_l + Σ_{i=1}^{N−1} |d_i − d̄| ) / ( d_f + d_l + (N−1) d̄ )
```

where `d_i` are the N−1 consecutive Euclidean distances along the obtained front, `d̄` their mean, and `d_f, d_l` *"the Euclidean distances between the extreme solutions [of the true PF] and the boundary solutions of the obtained non-dominated set."* Δ = 0 is ideal. ⚠️ **Caveat: it is a 2-objective construction** (it needs a well-defined *consecutive ordering* along the front) and **does not extend cleanly past M = 2.**

Related: Maximum Spread MS is from Zitzler et al. 2000, and Li & Yao note it *"does not touch on the convergence of the set"* — **pure-diversity indicators are almost all Pareto non-compliant.** Verbatim: *"This is particularly true for QIs that measure the diversity … **since they rarely take into account the closeness of solution sets**. DCI is the only known diversity QI that is compliant with Pareto dominance when comparing two sets. But if more sets are involved, DCI does not guarantee the Pareto compliance property."*

### The unary-indicator impossibility result — stated correctly

**This is the most-misquoted result in the field.** Verbatim from Zitzler et al. 2003.

First the machinery. A **comparison method** `C_{I,E}` combines a set of indicators I with an **interpretation function** E mapping indicator values to a Boolean. **Definition 4 (Compatibility and Completeness)**: C is **⊲-compatible** if a `true` outcome *implies* the dominance relation holds (no false positives), and **⊲-complete** if whenever the relation holds the outcome is `true` (no false negatives).

> **Theorem 1, verbatim:** *"Suppose an optimization problem with [k >= 2] objectives, where the objective space is [Z ⊆ R^k]. Then, THERE EXISTS NO COMPARISON METHOD C_{I,E} BASED ON A FINITE COMBINATION OF UNARY QUALITY INDICATORS THAT IS ⊲-COMPATIBLE AND ⊲-COMPLETE AT THE SAME TIME."*

And the paper's own gloss: *"for any combination of a finite number of unary quality indicators, we cannot find an interpretation function E such that the corresponding comparison method is ⊲-compatible and ⊲-complete. Or in other words: **the number of criteria that determine what a good approximation set is is infinite.**"* Also: *"Note that Theorem 1 also holds: 1) if we only assume that Z contains an open hypercube … and 2) if we consider **any other relation from Table I**."* And in the Conclusions: *"Unary quality indicators … are in general not capable of indicating whether an approximation set is better than another — **also if several of them are used. This even holds if we consider approximation sets containing a single objective vector only.**"*

**Two corollaries that matter and are usually omitted:**

- **The result is about *finite* combinations.** Verbatim: *"such a comparison method exists if we allow an **infinite** number of indicators. The empirical attainment function, when applied to single approximation sets, can be understood as a combination of |Z| unary indicators … On its basis, a ⊲-compatible and ⊲-complete comparison method can be constructed."* **This is the formal argument for using empirical attainment functions / attainment surfaces rather than a single number.**
- **Corollary 1** shows a unary indicator *can* be constructed that detects "better than" for approximation sets of **bounded size** — but it is a pathological digit-interleaving construction. Verbatim: *"The corollary, however, is rather of theoretical than of practical use. **The indicator constructed in the proof is able to indicate whether A is better than B, but it does not express HOW MUCH better it is.**"*

**What the theorem does not say:** it does **not** say unary indicators are useless, nor that hypervolume is uninformative. **It says no finite set of unary numbers is an exact oracle for the set-dominance relation.** The practical reading: use at least one Pareto-compliant unary indicator (hypervolume, IGD+, ε), report the reference point/front, and supplement with a **binary** indicator or attainment-function plots when you need to claim "better than." The paper's own recommendation: *"**Binary indicators … in principle do not possess the theoretical limitations of unary indicators.** … However … the number of indicator values to be considered is **not linear but quadratic** in the number of approximation sets."*

The complementary set-based framing: **Zitzler, Thiele & Bader, "On Set-Based Multiobjective Optimization," *IEEE TEVC* 14(1):58–79, 2010**, doi:10.1109/TEVC.2009.2016569.

### Reference-set dependence — the worked example that should end a bad practice

From Li & Yao: *"When comparing A with B, if the reference set is composed of these two sets, we will have A evaluated better than B (**IGD(A) ≈ 1.41 < IGD(B) ≈ 2.12**). But if adding another set C which has the similar distribution pattern to B into the evaluation, and now the reference set is composed of the three sets, we will have A worse than B (**IGD(A) ≈ 1.82 > IGD(B) ≈ 1.72**)."*

**The same two sets swap places depending on which third algorithm you happened to include in the comparison. So: do not build a reference set from the union of all competitors' results.**

Also on the ideal point: *"it is **crucial to not underestimate the ideal point** … it is advised to use a reference point slightly better than the ideal point, say **ref_j = ideal_j − l_j/(2N − 2)** in a bi-objective scenario, where l_j is the range of objective j and N is the size of the solution set."*

### Practical checklist for a defensible EMO comparison

1. State the **reference point** for HV and the **normalisation** used.
2. State the **reference front** Z for IGD/IGD+ **and how it was generated** (analytic PF, **not** the union of runs).
3. State **p** for GD/IGD.
4. Use at least one **Pareto-compliant** indicator (HV, IGD+, ε).
5. Report distributions over ≥ 25–31 independent runs with a non-parametric test and a multiple-comparison correction.
6. Prefer **attainment-function / EAF plots** when claiming one set is *better than* another.

⚠️ Items 1–4 are directly supported by the sources above; items 5–6 are standard community convention rather than a quotation.

---

## Benchmark suites

### ZDT

**Zitzler, Deb & Thiele, "Comparison of Multiobjective Evolutionary Algorithms: Empirical Results," *Evolutionary Computation* 8(2):173–195, 2000**, doi:10.1162/106365600568202.

All problems follow one template: minimise `f_1(x_1)` and `f_2 = g(x_2..x_n)·h(f_1, g)`. *"The function f_1 is a function of the first decision variable only, g is a function of the remaining n−1 variables, and the parameters of h are the function values of f_1 and g."*

| Problem | Authors' own feature label | front | pymoo n |
|---|---|---|---|
| **ZDT1** | *"has a **convex** Pareto-optimal front"* | convex | 30 |
| **ZDT2** | *"the **nonconvex** counterpart to T1"* | concave | 30 |
| **ZDT3** | *"represents the **discreteness** feature … **noncontiguous convex parts** … **However, there is no discontinuity in the parameter space**"* | 5 disconnected convex arcs | 30 |
| **ZDT4** | *"contains [many] local Pareto-optimal fronts … tests for the EA's ability to deal with **multimodality**"* | convex | 10 |
| **ZDT5** | *"describes a **deceptive** problem … **x_i represents a binary string**"* | convex | 11 decoded vars (30 bits + 10 × 5) |
| **ZDT6** | *"**two difficulties caused by the nonuniformity** … Pareto-optimal solutions are **nonuniformly distributed** … **density of the solutions is lowest near the Pareto-optimal front and highest away from the front**"* | concave, non-uniform | 10 |

**The known criticism is best stated by the WFG authors themselves** (Huband et al. 2006): the ZDT suite, *"despite being an immensely popular test suite, … has **numerous shortcomings**: It only has problems with **two objectives**. **None** of its problems has fitness landscapes with **flat regions**. Its only **deceptive** problem is **binary encoded**. **None** of its problems has a **degenerate** Pareto optimal front. **None** of its problems is **nonseparable**. **Only the number of distance parameters is scalable.**"* And: *"Although the ZDT test suite is popular, **by itself it is far from** [adequate]."*

Beyond that: **modern algorithms solve ZDT1–3 and ZDT6 to near-optimality in a few thousand evaluations, so ZDT discriminates almost nothing in 2026 except as a smoke test**; and ZDT5's binary encoding means most real-coded libraries cannot run it without special handling.

### DTLZ

**Deb, Thiele, Laumanns & Zitzler, "Scalable Test Problems for Evolutionary Multiobjective Optimization," in *Evolutionary Multiobjective Optimization*, Springer, pp. 105–145, 2005**, doi:10.1007/1-84628-137-7_6. The earlier conference version is CEC 2002; **the original technical report had nine problems.**

⚠️ **Numbering caution — this bites people.** Verbatim from the WFG paper, footnote 3: *"In fact, **the number of DTLZ problems depends on which paper is being referred to.** … [a version] also exists, in which **only seven of the original nine problems were reproduced (DTLZ5 and DTLZ9 from the original paper were dropped). As a result, DTLZ6 from the original technical report is DTLZ5 in the conference paper, DTLZ7 is DTLZ6 in the conference paper, and DTLZ8 is DTLZ7 in the conference paper.**"* **So "DTLZ7" means different problems in different papers.** Modern libraries (pymoo, jMetal) use the seven-problem numbering.

Front geometries, with `x_M` carrying `k = n − M + 1` distance variables:

- **DTLZ1**: **linear** hyperplane, `Σ_i f_i = 0.5`. Tests convergence past `(11^k − 1)` local fronts.
- **DTLZ2**: **unit sphere** in the first octant (`Σ_i f_i² = 1`) — spherical/concave. Baseline; tests scaling to many objectives.
- **DTLZ3**: same spherical front; convergence past `(3^k − 1)` parallel local fronts.
- **DTLZ4**: same spherical front, with an **α = 100** variable mapping. Tests **maintaining spread** — solutions crowd near the `f_M`–`f_1` plane.
- **DTLZ5**: a **curve** (degenerate). Convergence to a curve; easy 2D visualisation.
- **DTLZ6**: same curve-type front, optimum at `x_M = 0`. Harder; *"NSGA-II and SPEA2 struggle"*; `|x_M| = 10` fixed.
- **DTLZ7**: **2^{M−1} disconnected** Pareto-optimal regions; *"generally consists of convex components, with some mixed convexity/concavity."* Tests keeping sub-populations alive across separate regions.

DTLZ8 and DTLZ9 have side constraints (the WFG paper omits them for that reason).

**The known DTLZ flaws, from the WFG paper:**

- ⚠️ **DTLZ5/DTLZ6 are not actually degenerate for M > 3.** Verbatim: *"**DTLZ5 and DTLZ6 are both claimed to be problems with degenerate Pareto optimal fronts** … **Unfortunately, this is not true with DTLZ5 or DTLZ6**: it is possible to have [solutions that dominate the supposed front]."* They give an explicit four-objective counterexample.
- **Multiple global optima / Pareto many-to-one.** *"the objective functions of DTLZ1–DTLZ4 have multiple global optima since terms such as [cos(…)] can evaluate to zero … [most] of the DTLZ problems are Pareto many-to-one."*
- **Fixed number of position parameters** — *"**The DTLZ test suite uses a fixed (relative to the number of objectives) number of position parameters**"* — so you can scale distance variables but **not** position variables.
- **Triangular-front bias** — Tanabe & Ishibuchi 2020 on why decomposition methods look good here.

### WFG

**Huband, Hingston, Barone & While, "A Review of Multiobjective Test Problems and a Scalable Test Problem Toolkit," *IEEE TEVC* 10(5):477–506, 2006**, doi:10.1109/TEVC.2005.861417.

The contribution is a **toolkit**: a problem is built as a vector of **transition functions** applied to parameters classified as **position-related** (k of them, which move you *along* the front) vs **distance-related** (l of them, which move you *toward or away from* it), composed with a **shape function** that sets the front's geometry. **Both k and l are independently scalable, and M is scalable.** WFG1–9 is the example suite instantiated from it.

What it fixes about DTLZ, verbatim: *"the WFG test suite exceeds the functionality of previous existing test suites. In particular, it includes a number of problems that exhibit properties not evident in the commonly-used DTLZ test suite. These include: **nonseparable problems, deceptive problems, a truly degenerate problem, a mixed shape Pareto front problem, problems scalable in the number of position-related parameters, and problems with dependencies between position- and distance-related parameters.**"* Also: *"We recommend that all distance-related parameters be subjected [to transformations that] encourage EAs to normalize fitness values"* — i.e. **deliberately badly scaled objectives.**

The individual problems' character, verbatim: *"**WFG1** skews the relative significance of different parameters by employing **dissimilar weights in its weighted sum reduction**; only **WFG1 and WFG7 are both separable and unimodal**; the **nonseparable reduction of WFG6 and WFG9 is more difficult** than that of WFG2 and WFG3; the **multimodality of WFG4** has larger 'hill sizes' … than that of WFG9; the **deceptiveness of WFG5** is more difficult than that of WFG9; [the position-related] parameters of **WFG7** are dependent on its distance-related parameters; the distance-related parameters of **WFG8** are dependent on its position-related [ones]."* Also: **WFG2 is disconnected**; **WFG3 is the degenerate one**; WFG2 and WFG3 require l to be a multiple of two; and **k must be divisible by M−1.**

**And the calibration figure worth carrying into any budget discussion:** they ran NSGA-II, 35 runs, population 100, for **25,000 generations (= 2.5M evaluations)**, saving fronts at 250 / 2,500 / 25,000 generations, noting that *"a population size of 100 for 250 generations is a common [setting] in the literature"* and that **NSGA-II still hadn't converged on several WFG problems at 25,000 generations.** *"On WFG1, for example, NSGA-II shows poor coverage"* — **WFG1's bias remains hard for NSGA-II today.**

### Real-world: the RE suite

**Tanabe & Ishibuchi, "An easy-to-use real-world multi-objective optimization problem suite," *Applied Soft Computing* 89:106078, 2020**, doi:10.1016/j.asoc.2020.106078; arXiv:2009.12867. Verbatim: *"a problem suite consisting of **16 bound-constrained real-world problems** … various problems in terms of **the number of objectives, the number of decision variables, the shape of the Pareto front, and the type of design variables. 4 out of the 16 problems are multi-objective mixed-integer optimization problems.** We provide **Java, C, and Matlab source codes** … In addition to the 16 problems, we present **8 constrained** multi-objective real-world problems."*

**Their honest accounting of the trade-off** (their Table 1 scores synthetic problems on easiness, clearness, scalability and RE problems on non-artificiality, easiness): *"we believe that the RE problems do not have the above-mentioned unrealistic properties (e.g., the triangular Pareto front). **We do not claim that real-world problems (including the RE problems) must always be better than synthetic test problems** … they have **two disadvantages**: Similar to other real-world problems, **the properties of the RE problems are unclear. All the RE problems are not scalable** with respect to the number of objectives M and design variables D."* Definitions are *"given by simple equations or surrogate models"* — cheap to evaluate, which is the point.

jMetalPy ships both **RE** and **RWA** suites; ⚠️ **pymoo does not ship RE as of 0.6.2** (its real-world-flavoured problems are BNH, OSY, TNK, Truss2D, Welded Beam, plus MODAct).

### CEC MOEA competitions

⚠️ **This is the weakest-sourced item in this file. The CEC MO competition record could not be verified directly.** What *was* checked: Suganthan's GitHub profile lists `2021-RW-MOP` (real-world multi-objective problems, 2021) plus single-objective/constrained benchmark repos — so the 2021 real-world MO benchmark is confirmed to exist as a **release**, but the page does not label it a CEC competition.

The historically important one, which could **not** be verified: the **CEC 2009 Special Session and Competition on Performance Assessment of Unconstrained/Constrained Multi-Objective Optimization Algorithms**, whose **UF1–UF10** and **CF1–CF10** instances remain widely used, defined in Zhang, Zhou, Zhao, Suganthan, Liu & Tiwari, Technical Report CES-487, 2008. ⚠️ **Treat the author list, report number and year as unverified.** The UF/CF instances' distinguishing feature (per the MOEA/D-DE paper) is **complicated Pareto *sets*** — nonlinear variable linkages in **decision** space, which DTLZ/WFG largely lack and which break algorithms that assume simple PS geometry.

---

## Constraint handling in MOEAs

### Deb's constraint-domination principle (CDP)

The primary source is the NSGA-II paper itself, §VI:

> ***Definition 1**: A solution i is said to **constrained-dominate** a solution j, if any of the following conditions is true: 1. Solution i is **feasible** and solution j is not. 2. Solutions i and j are **both infeasible**, but solution i has a **smaller overall constraint violation**. 3. Solutions i and j are **feasible** and solution i **dominates** solution j.*

Consequences, verbatim: *"**any feasible solution has a better non-domination rank than any infeasible solution.** … among two infeasible solutions, the solution with a smaller constraint violation has a better rank. Moreover, **this modification in the non-domination principle does not change the computational complexity of NSGA-II.**"*

**The crucial design virtue**, verbatim: *"Since in no case constraints and objective function values are compared with each other, **there is no need of having any penalty parameter**, a matter which makes the proposed constrained handling approach useful and attractive."* The overall constraint violation is the **sum of normalised violations** of the violated constraints. The single-objective ancestor: Deb, "An efficient constraint handling method for genetic algorithms," *CMAME* 186(2–4):311–338, 2000, doi:10.1016/S0045-7825(99)00389-8. Characterisation in the modern survey: *"**CDP … is most commonly used due to its simplicity and ease of implementation.**"*

**CDP's weakness**, verbatim from Liang et al.: *"The operation of CDP is relatively simple, but **it prefers feasible solutions, which will cause the population to fall into some local feasible regions when CMOPs have discrete feasible regions or infeasible barriers.**"*

Unpacked: **CDP imposes a strict lexicographic priority of feasibility over objective quality. Infeasible individuals carry no usable objective information** — they are ranked purely by violation. So when the feasible region is **disconnected**, or when the path to the global constrained PF runs **through** an infeasible barrier, CDP's population gets pinned in whichever feasible pocket it first found and has no mechanism to cross. It also wastes the information in "slightly infeasible but objectively excellent" solutions, which in many engineering problems sit right against the **active** constraint boundary where the constrained optimum lives.

### The alternatives

Liang et al. group CDP, ε-constraint and stochastic ranking as the "feasibility-rule / separate-handling" family.

**ε-constraint method**, verbatim: *"proposed by **Takahama and Sakai**, which **uses a parameter epsilon to relax constraints. epsilon is gradually reduced, and when the constraint violation degree of an individual is less than epsilon, it is considered as a feasible solution. Obviously, when epsilon is reduced to 0, the epsilon constrained method is the same as CDP.** When comparing individuals A and B …: 1. If CV(A) <= ε, CV(B) <= ε, and A Pareto dominates B, then A is selected. 2. If CV(A) <= ε, CV(B) > ε, then A is selected. 3. If CV(A) > ε, CV(B) > ε, and CV(A) < CV(B), then A is selected."* Citation: Takahama & Sakai, IEEE CEC 2006, doi:10.1109/CEC.2006.1688283. **The point: early on ε is large, so near-feasible solutions compete on objective quality and the population can traverse infeasible regions; as ε → 0 the method anneals into CDP and converges to feasibility.** ε-DE variants won several CEC constrained competitions.

**Stochastic ranking (SR)** — the cleanest idea in the area. Verbatim from Liang et al.: *"a probability parameter p_f is introduced. When two individuals are compared, **the probability with p_f only compares their objective function value, and the probability with (1−p_f) compares their constraint violation degree.**"* Citation: **Runarsson & Yao, "Stochastic ranking for constrained evolutionary optimization," *IEEE TEVC* 4(3):284–294, 2000**, doi:10.1109/4235.873238.

The mechanism in full: instead of choosing *either* objective-based *or* violation-based comparison, **you randomise the comparison criterion per pairwise comparison.** Run a bubble-sort-like sweep; for each adjacent pair draw `u ~ U[0,1]` and **compare by objective value if `u < P_f`, otherwise by constraint violation** (with the refinement that two *feasible* individuals are always compared by objective). **The paper's recommended `P_f ≈ 0.45`** — deliberately just *below* 0.5, so violation comparisons dominate slightly and the population drifts toward feasibility while still being able to traverse infeasible regions. **The elegance: it interpolates continuously between "pure feasibility-first" (P_f = 0) and "ignore constraints" (P_f = 1) with one dimensionless parameter and no problem-dependent scaling — exactly the thing penalty coefficients get wrong.** Implemented in pymoo as **SRES** and **ISRES**.

**Repair.** Problem-specific projection of infeasible individuals back into the feasible set. MOEA/D has a hook for exactly this (Step 2.2). ⚠️ **Caveat: repair biases the search distribution toward the constraint boundary and is not generic.** Also decide explicitly whether you write the repaired genotype back (**Lamarckian**) or only use its fitness (**Baldwinian**) — they behave very differently.

**Penalty functions.** Static penalties *"remain unchanged in the early and late stages of evolution, which is not conducive to the balance between the objectives and constraints"*; dynamic/adaptive penalties adjust by generation number or by *"the feasibility proportion in the current population."* **Why the coefficient is hard, stated precisely:**

- **Too small** and the global optimum of the penalised objective is **infeasible**, so the search converges to an infeasible point and you get a **better-than-optimal reported value** — the most common and most embarrassing bug in constrained-EC papers.
- **Too large** and the penalty term dominates, the feasible interior's gradient information is swamped, and the search degenerates into a feasibility search that stops at the first feasible point.
- The coefficient has to be **scale-matched to f**, so it is not transferable between problems, and when constraints are **active** at the optimum (the usual case) the right coefficient depends on the **Lagrange multipliers**, which you do not know.
- **Death penalty** additionally fails whenever the feasible region is small or disconnected — you may never sample a feasible point at all, and it discards the only information that would tell you which way feasibility lies.

**Multi-population / two-archive methods** — the current state-of-the-art direction: maintain one archive driving convergence and one exploring infeasible space. **C-TAEA: Li, Chen, Fu & Yao, "Two-Archive Evolutionary Algorithm for Constrained Multiobjective Optimization," *IEEE TEVC* 23(2):303–315, 2019**, doi:10.1109/TEVC.2018.2855411 — ⚠️ **Crossref gives the authors as Li, Chen, Fu, Yao; the frequently seen "Li, Chen, Min, Zhang" attribution is wrong.** Also **push-and-pull search (PPS)** and **ACDP** (angle-based CDP, reusing infeasible-solution information, embedded in MOEA/D).

Survey for the whole area: **Liang, Ban, Yu, Qu, Qiao, Yue, Chen & Tan, "A Survey on Evolutionary Constrained Multiobjective Optimization," *IEEE TEVC* 27(2):201–221, 2023**, doi:10.1109/TEVC.2022.3155533. Single-objective side: Michalewicz & Schoenauer, *Evolutionary Computation* 4(1):1–32, 1996; Coello Coello, *CMAME* 191(11–12):1245–1287, 2002. Coello Coello still runs the GECCO tutorial — GECCO '24 doi:10.1145/3638530.3648406 and GECCO '25 doi:10.1145/3712255.3716509.

**Practical notes.** `cma` 4.5.0 ships `cma/constraints_handler.py` with an **augmented-Lagrangian** nonlinear-constraints handler, plus `boundary_handler.py` — so you do not need to hand-roll penalties with CMA-ES. pymoo's constrained support: NSGA2, RNSGA2, PINSGA2, NSGA3, UNSGA3, RNSGA3, CTAEA, SMSEMOA, SPEA2, OmniOptimizer, CMOPSO, MOPSO_CD, DNSGA2, KGB, NSDE, GDE3, NSDER all support constraints; ⚠️ **MOEAD, AGEMOEA, AGEMOEA2, RVEA and CMAES are marked as NOT supporting constraints.**

---

## Why EAs are genuinely state of the art here — and where they are not

### The genuine strengths

1. **One run returns a whole front approximation.** This is *the* structural advantage. A scalarization-based pipeline runs one NLP solve per weight vector and must choose the weights **in advance**; a population-based MOEA maintains N candidate trade-offs that **co-evolve and mutually inform** each other. MOEA/D makes the connection explicit: *"any information about these g's with weight vectors close to lambda^i should be helpful for optimizing g^te(x|lambda^i)."* **That is information *sharing* across subproblems, which independent scalarized solves do not get.**
2. **No differentiability needed.** Only a ranking of candidates. Black-box simulators, non-smooth aggregations (Tchebycheff is explicitly non-smooth), discontinuous objectives, and simulation codes that return only a number are all fine.
3. **Discrete, mixed and structured variables.** pymoo documents binary, discrete, permutation, mixed and custom variable types with a TSP example; Tanabe & Ishibuchi built 4 of their 16 RE problems as mixed-integer specifically because *"there are only a few (multi-objective) mixed-integer optimization problems for benchmarking."* **Multi-objective mixed-integer nonlinear programming is brutal for exact methods.**
4. **A-posteriori preference articulation — the real argument.** Choosing weights *before* you have seen the front means committing to a trade-off rate you cannot yet evaluate, in units you may not understand, with a mapping (weights → front location) that is nonlinear, geometry-dependent and **discontinuous across front concavities.** An a-posteriori workflow inverts this: approximate the whole front, *then* let the decision maker pick a point by inspecting actual achievable trade-offs. This is why library tooling matters — pymoo ships the decision layer explicitly: **pseudo-weights, compromise programming, high trade-off points**, plus visualisation for M > 3 (parallel coordinates, Radviz, petal, radar, heatmap). ⚠️ **But note the honest caveat from the NSGA-III paper:** *"the third difficulty related to **visualization and performance measures** mentioned above **cannot be avoided**"* in many objectives — **a-posteriori articulation gets harder exactly where many-objective methods are needed.** (See also Tušar & Filipič, *IEEE TEVC* 19(2):225–245, doi:10.1109/TEVC.2014.2313407.)
5. **Hypervolume gives a principled optimisation target.** Because hypervolume is strictly ≺-monotonic, maximising it is a **sound** surrogate for approximating the front: SMS-EMOA's Reduce operator **provably never decreases it** and converges to a local optimum of the S metric whose points are *"well distributed."* **Very few metaheuristic design choices come with a guarantee that clean.**

### Where EMO is *not* the right tool

1. **Convex multi-objective problems with available gradients.** On a convex problem the whole front *is* the boundary of `conv(Y + R^M_+)`, so the weighted-sum objection evaporates, **scalarization is complete** (Geoffrion 1968), and you should use scalarization + a proper NLP solver with warm-starting along the weight path, or Normal-Boundary Intersection for even spacing. Machine-precision front points, local optimality certificates, convergence rates — **none of which a MOEA offers.**
2. **Very expensive evaluations.** A MOEA needs 10³–10⁵ evaluations (the WFG authors' 2.5M-evaluation run still showed poor WFG1 coverage). Use multi-objective Bayesian optimisation: ParEGO, MOEA/D-EGO, qEHVI, qNEHVI — see `practice.md`, with the irony that **they optimise exactly the hypervolume indicator used here for selection, and inherit the same #P-hardness in M and the same reference-point sensitivity.**
3. **High decision dimensionality** — population methods scale poorly in n, where gradient or surrogate methods win. **And many objectives with no preference information** — at M ≳ 10 Pareto dominance is vacuous (94% non-dominated at M = 10, N = 100), the front needs exponentially many points to cover, visualisation fails, and the indicators become expensive or meaningless. The NSGA-III authors concede the third difficulty *"cannot be avoided."* **At that point the right move is to elicit preferences and reduce the problem** — reference-point/preference-based variants (R-NSGA-II, R-NSGA-III, PI-NSGA-II, all in pymoo), objective-reduction analysis, or interactive methods.
