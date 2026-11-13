# Multi-objective algorithms — NSGA-II, NSGA-III, SPEA2, MOEA/D, indicator-based
Treat as first-class: this is where EAs are genuinely state of the art.
All DOIs below were resolved live against the Crossref REST API unless marked
otherwise. [VFT] = verified from full text actually downloaded and read.
Fetches 2026-11-11.
PDFs obtained and read in full: NSGA-II (KanGAL preprint), NSGA-III Part I
(accepted preprint), MOEA/D (IEEE typeset), SPEA2 TIK-Report 103, Zitzler et al.
2003 performance assessment, ZDT 2000, IBEA 2004, HypE TIK-Report 286, WFG
toolkit, SMS-EMOA's EMO-2005 precursor, Guerreiro/Fonseca/Paquete hypervolume
survey (arXiv:2005.00515), Li & Yao indicator survey, Liang et al. constrained-MO
survey, Tanabe & Ishibuchi RE suite (arXiv:2009.12867).
Note: sciencedirect.com, research-collection.ethz.ch and IEEE Xplore HTML all
return 403 to automated fetching.

## 3.1 FOUNDATIONS

PARETO DOMINANCE (minimising all M objectives; f: X -> R^M). For u, v in R^M:
- **WEAK DOMINANCE** u <= v  <=>  u_i <= v_i for all i. (Reflexive.)
- **DOMINANCE** u < v  <=>  u_i <= v_i for all i AND u_j < v_j for at least one j.
- **STRICT/STRONG DOMINANCE** u << v  <=>  u_i < v_i for ALL i.
- Ordering: u << v => u < v => u <= v. None is a total order; two vectors can be
  mutually non-dominated (INCOMPARABLE). This incomparability is the whole reason
  the field exists.
Zitzler et al. 2003 lift these to SETS and add a fourth relation — this
four-relation vocabulary is what the indicator literature uses. [VFT, verbatim]:
"we will distinguish four relations in this paper as defined in Table I: strictly
dominates, dominates, **is better than**, and weakly dominates. Note that there is a
natural ordering again among the relations." For sets:
- A <= B: every b in B is weakly dominated by some a in A.
- **A ⊲ B ("A is BETTER THAN B")**: A <= B and NOT B <= A. The paper: "if A weakly
  dominates B, then either A is better than B or they are equal." This ⊲ is "the one
  implicitly used in most papers in the field."
- A < B: every b in B is dominated by some a in A.
- A << B: every b in B is strictly dominated by some a in A.

PARETO-OPTIMAL SET vs PARETO FRONT — decision space vs objective space:
- **PARETO-OPTIMAL SET** PS = {x in X : not exists x' in X, f(x') < f(x)} — in
  DECISION space.
- **PARETO FRONT** PF = f(PS) subset of R^M — in OBJECTIVE space.
The front is the IMAGE; the set is the PREIMAGE. [VFT, MOEA/D's own phrasing: "the
set of all the Pareto optimal points is called the Pareto set (PS) ... [and the set]
of Pareto optimal vectors [the] PF."] Different decision vectors can map to the same
objective vector — the WFG paper's term is "PARETO MANY-TO-ONE", which it notes
holds for most DTLZ problems.

### IDEAL AND NADIR POINTS
- **IDEAL** z* with z*_i = min_{x in X} f_i(x). Generally infeasible when objectives
  conflict.
- **NADIR** z^nad_i = max_{x in PS} f_i(x) — the componentwise worst value **OVER
  THE PARETO-OPTIMAL SET**, NOT over the whole feasible set. *** The componentwise
  max over all of X is the (larger, easier, different) "worst point"; CONFLATING
  THEM IS A COMMON ERROR. ***
NSGA-III estimates the ideal point per generation as z^min_j = min_{s in S_t} f_j(s)
and estimates the nadir implicitly via hyperplane intercepts (§3.3). [VFT]

### NON-DOMINATED SORTING

partition a population P into fronts F_1, F_2, ... where F_1
is the non-dominated subset of P, F_2 the non-dominated subset of P \ F_1, etc. The
index is the NON-DOMINATION RANK.

THE TWO GOALS OF EMO, and they conflict:
1. **CONVERGENCE** — drive the approximation set toward PF.
2. **DIVERSITY / SPREAD** — cover PF broadly and evenly so the decision maker sees
   the whole trade-off surface.
The literature treats the tension explicitly: Bosman & Thierens, "The balance between
proximity and diversity in multiobjective evolutionary algorithms", IEEE TEVC
7(2):174-188, 2003, DOI 10.1109/TEVC.2003.810761. [DOI V] Deb's framing in NSGA-II
[VFT]: "along with convergence to the Pareto-optimal set, it is also desired that an
EA maintains a good spread of solutions."

*** WHY WEIGHTED-SUM SCALARIZATION FAILS ON NON-CONVEX FRONTS — state the geometric
reason, not just the fact. ***
The scalarization min_x SUM_i lambda_i f_i(x), lambda_i >= 0, SUM lambda_i = 1, has a
purely geometric characterisation: a minimiser is exactly a point of the attainable
objective set Y = f(X) at which the hyperplane with NORMAL lambda **SUPPORTS** Y
(more precisely, supports Y + R^M_+). Supporting hyperplanes of a set touch only
points on the boundary of its **CONVEX HULL**. Therefore:
  **Weighted-sum optima lie only on the boundary of conv(Y + R^M_+). Any
  Pareto-optimal point lying in a concave ("non-convex") portion of PF is strictly
  INSIDE that convex hull and is therefore UNREACHABLE by any choice of non-negative
  weights.** Worse, the weight->solution map is DISCONTINUOUS across a concavity: as
  lambda sweeps, the minimiser JUMPS from one convex end of the concave region to
  the other, so an evenly spaced grid of weights yields a clumped, gap-ridden set of
  front points EVEN ON FRONTS THAT ARE CONVEX but unevenly curved.
PRIMARY-SOURCE CONFIRMATION [VFT, Zhang & Li 2007 §II-A, on the weighted-sum
approach]: "If the PF is concave (convex in the case of minimization), this approach
could work well. **However, not every Pareto optimal vector can be obtained by this
approach in the case of nonconcave PFs.**"
Supporting theory: Geoffrion, "Proper efficiency and the theory of vector
maximization", *J. Math. Anal. Appl.* 22(3):618-630, 1968, DOI
10.1016/0022-247X(68)90201-1 [DOI V] — the classical link between positive-weight
scalarization and PROPERLY EFFICIENT points; weighted-sum solutions are properly
efficient, and in the convex case the converse holds. Textbook: Miettinen,
*Nonlinear Multiobjective Optimization*, Kluwer/Springer, 1998/1999, DOI
10.1007/978-1-4615-5563-6 [DOI V] — this is reference [1] of the MOEA/D paper.

THE ALTERNATIVES THAT **CAN** REACH NON-CONVEX REGIONS:
**WEIGHTED TCHEBYCHEFF / CHEBYSHEV (weighted L_inf):**
    minimise g^te(x | lambda, z*) = max_{1<=i<=M} lambda_i * |f_i(x) - z*_i|
Because the level sets are axis-aligned L_inf "boxes" rather than hyperplanes, the
supporting set is a CONE CORNER, not a flat face — so it can touch concave portions
of the front. PRIMARY-SOURCE COMPLETENESS PROPERTY [VFT, Zhang & Li §II-B]: "for
each Pareto optimal point x* there exists a weight vector lambda such that x* is the
optimal solution of (3) and each optimal solution of (3) is a Pareto optimal
solution of (1)." (Technically it finds WEAKLY Pareto-optimal points in degenerate
cases; augmented/epsilon-perturbed Tchebycheff fixes that.) The paper also records
the cost: "One weakness with this approach is that its aggregation function is **not
smooth** for a continuous MOP" — fine inside an EA, which never differentiates it.
**ACHIEVEMENT SCALARIZING FUNCTION (ASF), Wierzbicki:**
    ASF(x | z-bar, w) = max_{1<=i<=M} (f_i(x) - z-bar_i) / w_i
    (+ optional augmentation rho * SUM_i (f_i - z-bar_i)/w_i)
Wierzbicki, "The Use of Reference Objectives in Multiobjective Optimization", in
*Multiple Criteria Decision Making Theory and Application*, LNEMS 177, pp. 468-486,
1980, DOI 10.1007/978-3-642-48782-8_32. [DOI V] Same L_inf geometry, so the same
ability to reach concave regions; and z-bar can be an ASPIRATION (preference) point.
The augmented form guarantees proper efficiency. *** THIS IS EXACTLY THE FUNCTION
NSGA-III USES to locate its extreme points (§3.3), and pymoo ships `ASF` and `AASF`
as decomposition objects. ***
**PBI (penalty-based boundary intersection)** — §3.4; also reaches non-convex
fronts, and derives from Das & Dennis's Normal-Boundary Intersection (DOI
10.1137/S1052623496307510, V).

## 3.2 NSGA-II — THE ACTUAL ALGORITHM
**Deb, Pratap, Agarwal & Meyarivan, "A fast and elitist multiobjective genetic
algorithm: NSGA-II", IEEE Transactions on Evolutionary Computation 6(2):182-197,
April 2002. DOI 10.1109/4235.996017 — DOI VERIFIED** (Crossref returns exactly this
title, these four authors, vol 6, issue 2, pp. 182-197, 2002-04).
*** PROVENANCE CAVEAT: the free full text read is the KanGAL preprint "A Fast and
Elitist Multi-Objective Genetic Algorithm: NSGA-II" (same four authors). It is
substantively the same algorithm but differs from the published TEVC version in TWO
places, both flagged below. ***

(a) FAST NON-DOMINATED SORT.
THE PUBLISHED TEVC VERSION'S BOOKKEEPING — the canonical form:
- For each p in P compute **n_p** = the DOMINATION COUNT, the number of solutions
  that dominate p; and **S_p** = the DOMINATED SET, the set of solutions p
  dominates. This first pass is O(MN^2).
- All p with n_p = 0 form F_1.
- For each p in the current front F_i, visit each q in S_p and DECREMENT n_q; any q
  reaching n_q = 0 joins F_{i+1}. Each S_p is traversed once in total, so the
  front-peeling phase is O(N^2) overall and NEVER RE-DOES DOMINATION TESTS.
- **Total O(MN^2)**, with O(N^2) extra memory for the S_p lists.
*** [FLAG] The n_p/S_p formulation is NOT in the preprint verified. The preprint
gives instead a `find-nondominated-front(P)` INCREMENTAL-INSERTION routine (grow a
set P', inserting p and deleting any member it dominates), called repeatedly on the
residue. The n_p/S_p version is almost certainly what the published TEVC 2002 paper
contains — it is the universally reproduced form, and DEAP's docs cite "Deb et al.'s
fast nondominated sorting" at O(MN^2) — but it was not read in the published paper
itself. Treat the n_p/S_p detail as high-confidence-but-not-directly-fetched. ***
COMPLEXITIES, quoted from the verified preprint [VFT]:
- A single domination test costs M objective comparisons; finding the first
  non-dominated front naively is **O(MN^2)**.
- "the worst case (when there exists only one solution in each front) the complexity
  of this algorithm **without any book-keeping is O(MN^3)**." *** That is the
  complexity of the ORIGINAL NSGA (Srinivas & Deb 1994) *** — the paper also notes
  of SPEA: "in [24] is O(MN^3), with proper book-keeping the complexity of SPEA can
  be reduced to O(MN^2)."
- They EMPIRICALLY validated the quadratic claim: on random populations with uniform
  objectives in [0,1], fitting the comparison count gave **25.354*N^1.1248 for M=4,
  8.145*N^1.248 for M=10, 9.772*N^2.0032 for M=20** — i.e. "as the number of
  objective functions increase, the exponent increases to approximately two."
  (Table I; [VFT].) *** A nice, rarely-quoted detail: for FEW objectives the
  practical cost is nowhere near N^2. ***

(b) CROWDING DISTANCE.
Verbatim [VFT]: "The crowding distance computation requires sorting of the population
according to each objective function value in their ascending order of magnitude.
Thereafter, for each objective function, the **boundary solutions** (solutions with
smallest and largest function values) **are assigned an infinite distance value**.
All other intermediate solutions are assigned a distance value equal to the absolute
difference in the function values of two adjacent solutions. ... The overall crowding
distance value is calculated as the **sum of individual distance values corresponding
to each objective**."
PSEUDOCODE as printed:
    crowding-distance-assignment(I):
      l = |I|
      for each i:  I[i].distance = 0
      for each objective m:
         I = sort(I, m)
         I[1].distance = I[l].distance = infinity   # boundary points always kept
         for i = 2 to (l-1):
            I[i].distance = I[i].distance + ( I[i+1].m - I[i-1].m )
INTERPRETATION: d_i is "an estimate of the size of the largest **CUBOID** enclosing
the point i without including any other point in the population" — the average side
length of that cuboid.
*** [FLAG — NORMALISATION] The published TEVC version DIVIDES each term by the
objective's range, i.e. + (I[i+1].m - I[i-1].m) / (f_m^max - f_m^min). The preprint
read shows the UN-NORMALISED difference. The normalised form is what every modern
implementation uses and is NECESSARY for objectives on different scales. Treat the
normalisation as present in the published paper but verified only indirectly. ***
COST, quoted: "The complexity of this procedure is governed by the sorting algorithm.
Since M independent sorting of at most N solutions (when all population members are
in one front I) are involved, the above algorithm has **O(M N log N)** computational
complexity."

(c) CROWDED-COMPARISON OPERATOR <_n.
Each individual carries (1) non-domination rank i_rank and (2) crowding distance
i_distance. Then
    i <_n j  <=>  i_rank < j_rank  OR  (i_rank = j_rank AND i_distance > j_distance)
**RANK FIRST; TIES BROKEN IN FAVOUR OF THE LARGER CROWDING DISTANCE** (the LESS
crowded individual). Used both in binary tournament mating selection and in
truncating the splitting front. The point of crowding distance over NSGA's fitness
sharing, verbatim: "the new approach does not require any user-defined parameter for
maintaining diversity" — no sigma_share — and it replaces sharing's O(N^2) cost.

(d) THE ELITIST LOOP.
    R_t = P_t ∪ Q_t                       # parents + offspring, size 2N
    F = fast-non-dominated-sort(R_t)
    P_{t+1} = empty ; i = 1
    while |P_{t+1}| + |F_i| <= N:
        crowding-distance-assignment(F_i)
        P_{t+1} = P_{t+1} ∪ F_i ; i += 1
    # F_i is now the "splitting" front
    crowding-distance-assignment(F_i)
    sort F_i descending by <_n (i.e. by crowding distance)
    P_{t+1} = P_{t+1} ∪ F_i[1 : (N - |P_{t+1}|)]
    Q_{t+1} = make-new-pop(P_{t+1})   # binary tournament on <_n, SBX, polynomial mutation
*** ELITISM IS IMPLICIT AND TOTAL: every parent competes against every offspring in
one combined pool, so no non-dominated parent can be lost. ***
OVERALL COMPLEXITY, verbatim: "1. Non-dominated sorting is O(M(2N)^2), 2. Crowding
distance assignment is O(M(2N) log(2N)), and 3. Sorting on <_n is O(2N log(2N)). As
can be seen, the **overall complexity of the above algorithm is O(MN^2)**, which is
governed by the non-dominated sorting part of the algorithm."

*** KNOWN WEAKNESS OF CROWDING DISTANCE AT M > 2-3 — important, and it motivates
everything in §3.3-3.4. *** Crowding distance is computed PER OBJECTIVE
INDEPENDENTLY AND THEN SUMMED. In 2D, consecutive-neighbour ordering along f_1 and
along f_2 agree (reversed), so the cuboid genuinely measures local neighbourhood. For
M >= 3 the per-objective sorts DISAGREE, and the "nearest neighbour in objective m"
is typically not a spatial neighbour at all: the summed cuboid stops measuring local
density. Documented consequences:
- A solution far from everything in ONE objective but crowded in all others can get a
  LARGE distance and survive (dominance-resistant / "extremal" solutions survive
  preferentially).
- The crowding operator loses its diversity-maintaining effect and can actively push
  the population toward the BOUNDARY of objective space.
- Deb & Jain motivate NSGA-III partly on this [VFT]: "implementation of a
  diversity-preservation operator (such as the crowding distance operator [5] or
  clustering operator [6]) becomes a computationally expensive operation [in many
  objectives]."
- The deeper problem is DOMINANCE RESISTANCE, addressed by shift-based density
  estimation: Li, Yang & Liu, "Shift-Based Density Estimation for Pareto-Based
  Algorithms in Many-Objective Optimization", IEEE TEVC 18(3):348-365, 2014, DOI
  10.1109/TEVC.2013.2262178. [bibliographic data V via OpenAlex]

## 3.3 NSGA-III AND THE MANY-OBJECTIVE PROBLEM
**Deb & Jain, "An Evolutionary Many-Objective Optimization Algorithm Using
Reference-Point-Based Nondominated Sorting Approach, Part I: Solving Problems With
Box Constraints", IEEE TEVC 18(4):577-601, August 2014. DOI
10.1109/TEVC.2013.2281535 — DOI VERIFIED.**
**Part II: Jain & Deb, "... Part II: Handling Constraints and Extending to an
Adaptive Approach", IEEE TEVC 18(4):602-622, August 2014. DOI
10.1109/TEVC.2013.2281534 — DOI VERIFIED.** *** Note Part II drops the hyphen in
"Reference-Point Based" and the author order REVERSES to Jain & Deb. ***

THE MANY-OBJECTIVE MOTIVATION, in the authors' own words [VFT, Introduction]: "First
and foremost, **the proportion of non-dominated solutions in a randomly chosen set of
objective vectors becomes exponentially large with an increase of number of
objectives.** Since the non-dominated solutions occupy most of the population slots,
any elite-preserving EMO faces a difficulty in accommodating adequate number of new
solutions in the population. This slows down the search process considerably." Then:
"Second, implementation of a diversity-preservation operator ... becomes a
computationally expensive operation. Third, visualization of a large-dimensional
front becomes a difficult task ... the performance metrics (such as hyper-volume
measure or other metrics) are either computationally too expensive or may not be
meaningful." They define "many-objective" as **FOUR OR MORE** objectives.

*** ACTUAL NUMBERS FOR THE NON-DOMINATED FRACTION. [FLAG: the NSGA-III paper gives NO
numbers here; the Ishibuchi/Tsukamoto/Nojima CEC 2008 review (DOI
10.1109/CEC.2008.4631121, DOI V) has no free full text. So these were GENERATED by
Monte-Carlo simulation rather than guessed — N = 100 points, objectives i.i.d.
U(0,1), minimisation, 40 independent trials, mean fraction of the population that is
non-dominated:] ***
    M        2      3      4      5      6      8     10      15     20
    frac  0.052  0.149  0.277  0.426  0.614  0.836  **0.938**  0.998  1.000
So **at M = 10 with a typical population of 100, ~94% of a random population is
already mutually non-dominated**; at M = 15, ~99.8%; at M = 20, essentially all of
it. Pareto-dominance has no discriminating power left and non-dominated sorting
degenerates to "everything is rank 1" — selection pressure comes ENTIRELY from the
secondary diversity criterion, which is precisely the criterion that ALSO breaks
down in high M (§3.2). This is the whole motivation for reference-point niching,
decomposition, and indicator-based selection.
THE RIGOROUS ASYMPTOTIC BEHIND IT: Bentley, Kung, Schkolnick & Thompson, "On the
Average Number of Maxima in a Set of Vectors and Applications", *Journal of the ACM*
25(4):536-543, October 1978, DOI 10.1145/322092.322095. [DOI V — *** note the author
list is FOUR names including Schkolnick, often mis-cited as "Bentley, Kung &
Thompson". ***] The expected number of maxima among n vectors with independent
continuous components in d dimensions is **Theta((ln n)^{d-1} / (d-1)!)**.
*** CAVEAT ON USING THIS FORMULA AT SMALL n — this is a trap several secondary
sources fall into: it is an n -> infinity asymptotic valid for n >> e^d. Evaluating
it at n = 100 gives fractions 0.046 (M=2), 0.106 (M=3), 0.187 (M=5), **0.026
(M=10)** — the M=10 value is WILDLY BELOW the simulated 0.938 because 100 << e^10.
USE THE SIMULATION NUMBERS, NOT THE ASYMPTOTIC, FOR REALISTIC POPULATION SIZES. ***

### WHAT CHANGED FROM NSGA-II

The elitist shell is UNCHANGED: combine R_t = P_t ∪ Q_t,
non-dominated sort, fill fronts until |S_t| >= N; if it fills exactly, done. *** THE
CROWDING-DISTANCE TRUNCATION OF THE SPLITTING FRONT F_l IS ENTIRELY REPLACED BY
REFERENCE-POINT/REFERENCE-DIRECTION NICHING. *** Verbatim skeleton [VFT, Algorithm 1]:
     4: (F1,F2,...) = Non-dominated-sort(R_t)
     5: repeat  S_t = S_t ∪ F_i ; i = i+1   until |S_t| >= N
     8: last front to be included: F_l = F_i
     9: if |S_t| = N then P_{t+1} = S_t ; break
    12:   P_{t+1} = ∪_{j=1}^{l-1} F_j
    13:   K = N - |P_{t+1}|                        # points still needed from F_l
    14:   Normalize objectives and create reference set Z^r
    15:   [pi(s), d(s)] = Associate(S_t, Z^r)      # pi(s): closest ref point; d: distance
    16:   rho_j = SUM_{s in S_t \ F_l} (pi(s) = j ? 1 : 0)   # niche counts from accepted members
    17:   Niching(K, rho_j, pi, d, Z^r, F_l, P_{t+1})
*** ALSO NOTABLE AND USUALLY OMITTED: NSGA-III USES NO EXPLICIT MATING SELECTION AT
ALL. Verbatim: "In NSGA-III, we have already performed a careful elitist selection of
solutions ... For all these reasons, we do not employ any explicit selection
operation with NSGA-III. The population Q_{t+1} is constructed by applying the usual
crossover and mutation operators by **randomly picking parents** from P_{t+1}." They
also recommend "a relatively larger value of distribution index in the SBX operator"
to keep offspring near parents. ***

DAS-DENNIS STRUCTURED REFERENCE POINTS AND THE COUNT H [VFT, verbatim]: "in this
paper we use Das and Dennis's [48] systematic approach that places points on a
normalized hyper-plane — a (M-1)-dimensional unit simplex — which is equally inclined
to all objective axes and has an intercept of one on each axis. **If p divisions are
considered along each objective, the total number of reference points (H) in an
M-objective problem is given by:  H = C(M + p - 1, p)**  (eq. 3) For example, in a
three-objective problem (M = 3) ... If four divisions (p = 4) are chosen for each
objective axis, H = C(6,4) **or 15 reference points** will be created."
Underlying method: Das & Dennis, "Normal-Boundary Intersection: A New Method for
Generating the Pareto Surface in Nonlinear Multicriteria Optimization Problems",
*SIAM Journal on Optimization* 8(3):631-657, August 1998, DOI
10.1137/S1052623496307510. [DOI V]
*** THE COMBINATORIAL BLOW-UP AND THE TWO-LAYER WORKAROUND — the paper's actual
numbers [VFT]: ***
    M = 3    p = 12                                                  H = 91
    M = 5    p = 6                                                   H = 210
    M = 8    TWO LAYERS: boundary p = 3 (120 pts) + inside p = 2 (36)  H = 156
    M = 10   two layers (p = 3 / p = 2 class)                        H = 275
    M = 15   two layers                                              H = 135
Verbatim on why: "Note that as long as p >= M is not chosen, **no intermediate point
will be created** by Das and Dennis's systematic approach. For eight-objective
problems, even if we use p = 8 (to have at least one intermediate reference point),
**it requires 5,040 reference points.** To avoid such a situation, we use two layers
of reference points with small values of p." Also: "for a computationally fast
procedure, we have set **N almost equal to H**" (one niche per population slot).
ADDITIONAL NOTE from pymoo's own reference-direction docs [V, fetched 2026-11-11]:
Das-Dennis "cannot produce an arbitrary number of points desired," and in higher
dimensions most points land on the simplex BOUNDARY; for p > M the number of INTERIOR
points is C(p-1, p-M). pymoo therefore also ships a **RIESZ s-ENERGY** generator
(minimises a Riesz energy with s = M^2, via Adam + gradient projection onto the
simplex) which "can produce any number of well-spaced points in any dimension", plus
`multi-layer`, `layer-energy` (auto-optimised layer scalings from e.g. [3,2,1,1]) and
`incremental`.

ADAPTIVE NORMALISATION — the part people skip, and it matters [VFT, Algorithm 2]:

1. IDEAL POINT: z^min_j = min_{s in S_t} f_j(s), j = 1..M.

2. TRANSLATE: f'_j(s) = f_j(s) - z^min_j.

3. EXTREME POINTS VIA ASF: for each axis direction j,
   z^{j,max} = argmin_{s in S_t} ASF(s, w^j) where ASF(x, w) = max_{i} f'_i(x)/w_i,
   and w^j = (eps,...,eps)^T with **eps = 10^-6** except w^j_j = 1. (Verbatim: "For
   w_i = 0, we replace it with a small number 10^{-6}.")

4. HYPERPLANE AND INTERCEPTS: the M extreme vectors "are then used to constitute a
   M-dimensional linear hyper-plane"; compute its intercept a_i on each axis — ONE
   M x M MATRIX INVERSION.

5. NORMALISE: **f^n_i(x) = (f_i(x) - z^min_i) / (a_i - z^min_i)** (eq. 5). "Note that
   the intercept on each normalized objective axis is now at f^n_i = 1 and a
   hyper-plane constructed with these intercept points will make SUM_i f^n_i = 1" —
   so the Das-Dennis points ALREADY LIE ON IT and need no re-mapping.
*** THIS RUNS EVERY GENERATION using the extreme points found so far, which is what
makes NSGA-III scale-invariant WITHOUT user-supplied bounds. ***

ASSOCIATION AND NICHING [VFT].
ASSOCIATE (Algorithm 3): the reference LINE for reference point z is w = z through
the origin; for each s compute the PERPENDICULAR distance to every reference line,
    d_perp(s, w) = || s - (w^T s) w / ||w||^2 ||
    pi(s) = argmin_{w in Z^r} d_perp(s, w) ;  d(s) = d_perp(s, pi(s))
NICHING (Algorithm 4) — the exact rule:
    k = 1
    while k <= K:
        J_min = { j : argmin_{j in Z^r} rho_j }     # least-crowded reference points
        j-bar = random(J_min)                        # tie-break at random
        I_jbar = { s : pi(s) = j-bar, s in F_l }
        if I_jbar nonempty:
            if rho_jbar = 0:  P_{t+1} ∪= { argmin_{s in I_jbar} d(s) }  # closest to the line
            else:             P_{t+1} ∪= random(I_jbar)
            rho_jbar += 1 ; F_l = F_l \ s ; k += 1
        else:
            Z^r = Z^r \ { j-bar }     # no candidate: drop this reference point this generation
*** THE ASYMMETRY IS DELIBERATE: an UNOCCUPIED reference direction (rho = 0) gets the
F_l member CLOSEST TO ITS LINE (push toward the direction); an ALREADY-OCCUPIED one
gets a RANDOM associate (no extra convergence pressure where a niche is already
filled). ***

NSGA-III COMPLEXITY — verbatim [VFT, §III-G]: non-dominated sorting of 2N
M-dimensional vectors "require O(N log^{M-2} N) computations [49]" (Jensen's
divide-and-conquer sort, NOT the O(MN^2) NSGA-II sort); ideal point O(MN);
translation O(MN); **extreme points O(M^2 N)**; intercepts "one matrix inversion of
size M x M, requiring **O(M^3)**"; normalisation O(N); mapping aspiration points
O(MH); association O(MNH); niching "larger of O(L^2) or O(LH)" with L = |F_l| <= 2N.
CONCLUSION, VERBATIM: "**the overall worst-case complexity of one generation of
NSGA-III is O(N^2 log^{M-2} N) or O(N^2 M), whichever is larger.**" With N ~= H and
N > M in all their simulations.

RELATIVES WORTH NAMING, all DOIs V: **U-NSGA-III** (unifies single-, multi- and
many-objective) — Seada & Deb, "A Unified Evolutionary Optimization Procedure for
Single, Multiple, and Many Objectives", IEEE TEVC 20(3):358-369, 2016, DOI
10.1109/TEVC.2015.2459718. **RVEA** (reference-vector guided, angle-penalised
distance, adaptive reference vectors) — Cheng, Jin, Olhofer & Sendhoff, IEEE TEVC
20(5):773-791, 2016, DOI 10.1109/TEVC.2016.2519378. **AGE-MOEA** (adapts to the
front's NON-EUCLIDEAN geometry rather than assuming a simplex) — Panichella, GECCO
2019, pp. 595-603, DOI 10.1145/3321707.3321839 [note the DOI record's title uses
lowercase "non-euclidean"]; AGE-MOEA2 follows in GECCO 2022, pp. 565-573, DOI
10.1145/3512290.3528732.

## 3.4 SPEA2 AND MOEA/D
**SPEA2.** Zitzler, Laumanns & Thiele, "SPEA2: Improving the Strength Pareto
Evolutionary Algorithm", **TIK-Report 103**, Computer Engineering and Networks
Laboratory (TIK), ETH Zurich, 2001. ETH Research Collection DOI
**10.3929/ethz-a-004284029** [V via OpenAlex]. [VFT — the actual TIK report read.]
Notation: P_t = population (size N), P-bar_t = archive (size N-bar), M = N + N-bar.
*** FITNESS IS MINIMISED in SPEA2. ***
STRENGTH VALUE, verbatim: **S(i) = |{ j | j in P_t + P-bar_t AND i dominates j }|**,
"representing the number of solutions it dominates", where + is multiset union.
*** Computed over POPULATION AND ARCHIVE TOGETHER (unlike SPEA, where only archive
members counted). *** Footnote: this "slightly differs from the one presented in
(Bleuler, Brack, Thiele, and Zitzler 2001), where also individuals which have
identical objective values contribute to the strength."
RAW FITNESS, verbatim: **R(i) = SUM_{j in P_t + P-bar_t, j dominates i} S(j)** — "the
raw fitness is determined by the **strengths of its dominators** in both archive and
population, as opposed to SPEA where only archive members are considered." Key
properties, verbatim: "fitness is to be **minimized** here, i.e., **R(i) = 0
corresponds to a nondominated individual**, while a high R(i) value means that i is
dominated by many individuals (which in turn dominate many individuals)." THE DESIGN
RATIONALE: summing DOMINATORS' STRENGTHS (rather than just counting dominators) stops
individuals dominated by the same archive member from all getting identical fitness.
DENSITY ESTIMATE — k-th nearest neighbour, verbatim: "an adaptation of the k-th
nearest neighbor method (Silverman 1986) ... for each individual i the distances (in
objective space) to all individuals j in archive and population are calculated and
stored in a list. After sorting the list in increasing order, the k-th element gives
the distance sought, denoted as sigma^k_i. As a common setting, we use **k equal to
the square root of the sample size** (Silverman 1986), thus, **k = sqrt(N + N-bar)**."
    **D(i) = 1 / (sigma^k_i + 2)**
"In the denominator, **two is added to ensure that its value is greater than zero and
that D(i) < 1**." *** THAT D(i) < 1 BOUND IS THE WHOLE POINT: since R(i) is a
non-negative integer and R(i)=0 <=> non-dominated, adding a sub-1 density term can
NEVER let a dominated individual beat a non-dominated one. ***
FINAL FITNESS: **F(i) = R(i) + D(i)**.
RUNTIME, verbatim: "The run-time of the fitness assignment procedure is dominated by
the density estimator (**O(M^2 log M)**), while the calculation of the S and R values
is of complexity **O(M^2)**, where M = N + N-bar."
FIXED-SIZE ARCHIVE: two properties distinguish it from SPEA — "i) the number of
individuals contained in the archive is **constant over time**, and ii) the
truncation method **prevents boundary solutions being removed**."
Step 1 — copy all non-dominated individuals: P-bar_{t+1} = { i : F(i) < 1 } (which is
exactly R(i) = 0 by the D(i) < 1 bound). Then three cases:
- |P-bar_{t+1}| = N-bar -> done.
- **< N-bar (FILL)**: "the best N-bar - |P-bar_{t+1}| **dominated** individuals in the
  previous archive and population are copied to the new archive. This can be
  implemented by **sorting the multiset P_t + P-bar_t according to the fitness
  values** and copy the first N-bar - |P-bar_{t+1}| individuals i with F(i) >= 1."
- **> N-bar (TRUNCATE)**: iteratively remove individuals until the size is N-bar. At
  each iteration remove the i for which i <=_d j for ALL j, where
      i <=_d j :<=> for all 0 < k < |P-bar_{t+1}| : sigma^k_i = sigma^k_j
                    OR exists 0 < k : (for all 0 < l < k : sigma^l_i = sigma^l_j)
                                       AND sigma^k_i < sigma^k_j
  Verbatim gloss: "the individual which has the **minimum distance to another
  individual** is chosen at each stage; if there are several individuals with minimum
  distance the **tie is broken by considering the second smallest distances and so
  forth**." *** This LEXICOGRAPHIC-ON-THE-SORTED-DISTANCE-VECTOR rule is exactly what
  guarantees boundary solutions survive (they have large nearest-neighbour
  distances). *** TRUNCATION COST, verbatim: "the worst run-time complexity of the
  truncation operator is **O(M^3)** ..., on average the complexity will be lower
  (**O(M^2 log M)**) as individuals usually differ with regard to the second or third
  nearest neighbour."
ONE MORE SPEA2 DIFFERENCE, verbatim: "**only members of the archive participate in the
mating selection process.**" Mating selection is binary tournament with replacement on
the archive.

**MOEA/D.** Zhang & Li, "MOEA/D: A Multiobjective Evolutionary Algorithm Based on
Decomposition", IEEE TEVC **11(6):712-731, December 2007. DOI
10.1109/TEVC.2007.892759 — DOI VERIFIED.** [VFT — the typeset IEEE PDF read. *** Its
displayed equations are in math fonts that do not text-extract, so the formulas below
are the STANDARD FORMS cross-checked against the surrounding prose and the extractable
footnotes (which DID reveal the PBI d1/d2 definitions). ***]
THE CORE IDEA: decompose the problem of approximating PF into **N SCALAR SUBPROBLEMS**,
one per weight vector lambda^1..lambda^N, and solve them SIMULTANEOUSLY with a single
population of N individuals — individual i is the best solution found so far for
subproblem i. Verbatim: "At each generation, the population is composed of the best
solution found so far (i.e. since the start of the run of the algorithm) for each
subproblem. ... Each subproblem ... is optimized in MOEA/D by using information only
from its **neighboring subproblems**." THE JUSTIFICATION, verbatim: "the optimal
solution of g^te(x|lambda^i) should be close to that of g^te(x|lambda^j) if lambda^i
and lambda^j are close to each other. Therefore, any information about these g's with
weight vectors close to lambda^i should be helpful for optimizing g^te(x|lambda^i).
**This is a major motivation behind MOEA/D.**"
THE THREE STANDARD AGGREGATIONS (z* the ideal point for minimisation):
**(A) WEIGHTED SUM** (eq. 2): minimise g^ws(x|lambda) = SUM_i lambda_i f_i(x).
Limitation, verbatim: "not every Pareto optimal vector can be obtained by this
approach in the case of nonconcave PFs."
**(B) TCHEBYCHEFF** (eq. 3): minimise g^te(x|lambda,z*) = max_i lambda_i |f_i(x) -
z*_i|. Completeness and the non-smoothness caveat: see §3.1.
**(C) PBI — penalty-based boundary intersection** (eq. 5). The BI idea (eq. 4) is the
constrained problem min d s.t. F(x) - z* = -d*lambda/||lambda||, i.e. find where the
line through z* with direction lambda hits the attainable set's boundary. The equality
constraint is awkward in an EA, so they penalise it:
    minimise g^pbi(x|lambda,z*) = d1 + theta * d2
    where  d1 = ||(F(x) - z*)^T lambda|| / ||lambda||   (distance ALONG the ref line)
           d2 = ||F(x) - (z* + d1 * lambda/||lambda||)|| (PERPENDICULAR distance)
*** [V — footnote 6 of the paper extracts as: "In the case when the goal of (1) is
minimization, d1 = (F(x) - z*)^T lambda / ||lambda|| and d2 = ||F(x) - (z* +
d1 lambda)||"] *** with lambda normalised. theta > 0 is "a preset penalty parameter".
**PENALTY VALUE USED: theta = 5.** Verbatim: "In our experiment, the penalty factor
theta in g^pbi is set to be 5."
PBI'S ADVANTAGES, verbatim: "In the case of more than two objectives, let both the PBI
approach and the Tchebycheff approach use the same set of evenly distributed weight
vectors, **the resultant optimal solutions in the PBI should be much more uniformly
distributed than those obtained by the Tchebycheff approach**, particularly when the
number of weight vectors is not large." And: "If F(x) dominates F(y), it is still
possible that g^te(x) = g^te(y), while it is rare for g^pbi and other BI aggregation
functions." ITS COST, verbatim: "these benefits come with a price. **One has to set the
value of the penalty factor.** It is well-known that a too large or too small penalty
factor will worsen the performance of a penalty method."
NEIGHBOURHOOD STRUCTURE, verbatim: "a **neighborhood of weight vector lambda^i is
defined as a set of its several closest weight vectors** in {lambda^1..lambda^N}. The
neighborhood of the i-th subproblem consists of all the subproblems with the weight
vectors from the neighborhood of lambda^i." Step 1.2: "**Compute the Euclidean
distances between any two weight vectors** and then work out the T closest weight
vectors to each weight vector. For each i = 1..N, set B(i) = {i_1,...,i_T}". Note
"lambda^i's closest vector is itself, and then i is in B(i)." **T is the niching /
neighbourhood size** and is an INPUT PARAMETER.
THE MAIN LOOP (verbatim Step 2). State: population x^1..x^N; FV^i = F(x^i); z the
best-so-far value for each objective (a running substitute for the true ideal point —
verbatim: "Since it is often very time-consuming to find the exact reference point z*,
we use z ... as a substitute"); and an external population EP of non-dominated
solutions.
    Step 2) Update: for i = 1..N do
      2.1) Reproduction: randomly select two indexes k, l from B(i), and generate a
           new solution y from x^k and x^l by using genetic operators.
      2.2) Improvement: apply a problem-specific repair/improvement heuristic on y
           to produce y'.
      2.3) Update of z: for each j, if z_j > f_j(y') then z_j = f_j(y').
      2.4) Update of Neighboring Solutions: for each index j in B(i),
           if g(y'|lambda^j, z) <= g(x^j|lambda^j, z) then x^j = y' and FV^j = F(y').
      2.5) Update of EP: remove from EP all vectors dominated by F(y');
           add F(y') to EP if no vectors in EP dominate F(y').
    Step 3) Stop if the criterion is met, output EP; else go to Step 2.
*** TWO THINGS TO NOTE PRECISELY: (1) MATING IS RESTRICTED TO THE NEIGHBOURHOOD —
both parents come from B(i), not the whole population. (2) REPLACEMENT IS ALSO
NEIGHBOURHOOD-SCOPED AND IS A MANY-SLOT REPLACEMENT: one offspring y' is tested
against EVERY subproblem j in B(i) and can replace the incumbent in ALL of them.
Verbatim: "Step 2.4 considers all the neighbors of the i-th subproblem, it replaces
x^j with y' if y' performs better than x^j with regard to the j-th subproblem." THIS
IS THE KNOWN SOURCE OF MOEA/D'S DIVERSITY LOSS — one strong offspring can flood a
whole neighbourhood — which later variants fix with a replacement cap n_r. ***
WHY IT SCALES BETTER TO MANY OBJECTIVES: selection pressure comes from SCALAR
comparisons against FIXED weight vectors, not from Pareto dominance, so it does NOT
degrade as M grows (compare the 94%-non-dominated-at-M=10 figure in §3.3). And
per-generation cost is lower: the paper claims "MOEA/D has lower computational
complexity than NSGA-II at each generation", noting that "the computational complexity
of each generation in NSGA-II is O(mN^2)". *** [FLAG] The exact symbolic expression
for MOEA/D's own per-generation complexity is in a math-font equation that did not
text-extract. The standard value is O(mNT) (m objectives x N subproblems x T
neighbours), consistent with the structure of Step 2 as verified, but the symbols were
not read. Treat O(mNT) as RECONSTRUCTED, not quoted. ***
WEAKNESSES:

1. PERFORMANCE DEPENDS ON THE AGGREGATION FUNCTION AND THE FRONT'S GEOMETRY. Weighted
   sum cannot reach non-convex fronts at all; Tchebycheff gives non-uniform spread in
   high M; PBI needs theta tuned.
2. **WEIGHT-VECTOR DISTRIBUTION MISMATCH FOR IRREGULAR FRONTS.** A uniform simplex of
   weights maps to a uniform set of front points ONLY when the front is itself roughly
   simplex-like (a "regular/triangular" front). On inverted, degenerate, disconnected,
   badly scaled or strongly curved fronts, many weight vectors collapse onto the same
   front region or point at nothing at all, and the EFFECTIVE POPULATION SHRINKS. The
   definitive demonstration: **Ishibuchi, Setoguchi, Masuda & Nojima, "Performance of
   Decomposition-Based Many-Objective Algorithms Strongly Depends on Pareto Front
   Shapes", IEEE TEVC 21(2):169-190, 2017, DOI 10.1109/TEVC.2016.2587749** [bib V via
   OpenAlex]. *** AND THE CORROBORATING INDICTMENT OF THE BENCHMARKS, verbatim from
   Tanabe & Ishibuchi 2020 [VFT]: "some decomposition-based EMOAs (e.g., MOEA/D and
   NSGA-III) work well on the DTLZ and WFG problems even with many objectives. **This
   is because most DTLZ and WFG problems have triangular shape Pareto fronts.**" —
   i.e. THE BENCHMARKS HAVE BEEN FLATTERING DECOMPOSITION METHODS. ***

3. Neighbourhood-wide replacement can collapse diversity (above).
VARIANTS: **MOEA/D-DE** (DE reproduction + polynomial mutation, a probability delta of
mating OUTSIDE the neighbourhood, and a cap n_r on how many neighbours one offspring
may replace — the two fixes for the diversity problem) — **Li & Zhang,
"Multiobjective Optimization Problems With Complicated Pareto Sets, MOEA/D and
NSGA-II", IEEE TEVC 13(2):284-302, 2009, DOI 10.1109/TEVC.2008.925798 — DOI V**
(authors are Hui Li & Qingfu Zhang, in that order). **MOEA/D-AWA** (adaptive weight
adjustment, for irregular fronts) — Qi, Ma, Liu, Jiao, Sun & Wu, *Evolutionary
Computation* 22(2):231-264, 2014, DOI 10.1162/EVCO_a_00109. **MOEA/D-EGO**
(surrogate-assisted) — Zhang, Liu, Tsang & Virginas, IEEE TEVC 14(3):456-474, 2010,
DOI 10.1109/TEVC.2009.2033671. [all DOIs V]

## 3.5 THE INDICATOR-BASED FAMILY
**SMS-EMOA.** Beume, Naujoks & Emmerich, "SMS-EMOA: Multiobjective selection based on
dominated hypervolume", *European Journal of Operational Research* 181(3):1653-1669,
September 2007. **DOI 10.1016/j.ejor.2006.08.008 — DOI VERIFIED.**
*** [FLAG] The EJOR journal text is behind Elsevier (403; no OA copy per Unpaywall,
Semantic Scholar or OpenAlex). WHAT WAS VERIFIED INSTEAD is the EMO-2005 PRECURSOR by
the same three authors, which introduces exactly the SMS-EMOA scheme: Emmerich, Beume
& Naujoks, "An EMO Algorithm Using the Hypervolume Measure as Selection Criterion",
EMO 2005, LNCS 3410 [VFT]. Everything quoted below is from the 2005 paper. ***
Verbatim: "a **steady-state (mu+1)-EMOA**, the so-called **S metric selection EMOA**
(SMS-EMOA)". "It is a steady-state evolutionary algorithm with **constant population
size** that firstly uses non-dominated sorting as a ranking criterion and secondly the
**hypervolume measure as selection criterion to discard that individual, which
contributes least hypervolume to the worst-ranked Pareto-optimal front**."
THE `Reduce` OPERATOR, verbatim: "First, the Pareto fronts with respect to the
non-domination level (or rank) are computed using the **fast-nondominated-sort-
algorithm** [= NSGA-II's]. Afterwards, one individual is discarded from the
**worst ranked front**. If this front comprises |R_I| > 1 individuals, the individual
s in R_I is eliminated that minimizes
    **Delta S(s, R_I) := S(R_I) - S(R_I \ {s})**   (eq. 3)
FOR TWO OBJECTIVES THERE IS A CLOSED FORM: sort the worst-ranked front ascending by
f1 (which, since the points are mutually non-dominated, also sorts descending by f2);
then for R_I = {s_1..s_{|R_I|}},
    **Delta S(s_i, R_I) = ( f1(s_{i+1}) - f1(s_i) ) * ( f2(s_{i-1}) - f2(s_i) )**  (eq. 4)
(boundary points get infinity via the reference point).
COMPLEXITY, verbatim: "The runtime complexity of the hypervolume procedure in the case
of two objective functions is governed by the sorting algorithm. It is **O(mu log
mu)**, if all points lie on one non-dominated front. For the case of more than two
objectives, we suggest to use the algorithm of Fleischer ... the runtime complexity of
SMS-EMOA is governed by the calculation of the hypervolume and is **O(mu^3 n^2)**."
*** THE THEORETICAL PAY-OFF, verbatim: "By greedily discarding the individual that
minimizes Delta S(s, R_I), it is guaranteed that the subset which covers the **maximal
hypervolume** compared to all |R_I| possible subsets remains in the population (for a
proof we refer to Knowles and Corne). With regard to the replacement operator this also
implies that the covered hypervolume of a population **cannot decrease** by application
of the Reduce operator, i.e. ... S(P_t) <= S(P_{t+1})." *** They also note convergence
transfers from Knowles et al.'s AA_S archiving strategy, and that "the points of local
optima of the S metric are 'well distributed'."
ONE NICE DETAIL, verbatim: "Our method of determining the solution contributing least
to the hypervolume is actually **independent from the choice of the reference point**.
The reference point is only needed to calculate the hypervolume of extremal points of a
front" — i.e. SMS-EMOA's SELECTION is largely reference-point-robust even though the
INDICATOR is not.
pymoo's implementation [V, docs fetched 2026-11-11]: computes EXACT hypervolume
contributions for **up to five objectives** via the **`moocore`** library, and
**switches to an approximation automatically above five objectives.**

**IBEA.** Zitzler & Künzli, "Indicator-Based Selection in Multiobjective Search",
*PPSN VIII*, LNCS 3242, pp. 832-842, 2004. **DOI 10.1007/978-3-540-30217-9_84 — DOI
VERIFIED.** [VFT]
The thesis, verbatim from the abstract: "first define the optimization goal in terms of
a **binary performance measure (indicator)** and then **directly use this measure in
the selection process**. ... IBEA can be adapted to the preferences of the user and
moreover **does not require any additional diversity preservation mechanism** such as
fitness sharing."
The naive fitness is F'(x1) = SUM_{x2 in P \ {x1}} I({x2},{x1}) — "a measure for the
'loss in quality' if x1 is removed from the population." But IBEA actually uses an
EXPONENTIALLY AMPLIFIED form:
    **F(x1) = SUM_{x2 in P \ {x1}}  -e^{ -I({x2},{x1}) / kappa }**
to be MAXIMISED, with kappa > 0 "a scaling factor depending on I and the underlying
problem". Verbatim rationale: "the **influence of small indicator values contributes
much more to the overall fitness than large values**" (exploiting that for a
dominance-preserving indicator, I({x1},{x2}) < I({x2},{x1}) when x1 dominates x2).
**THEOREM 1, verbatim: "Let I be a binary quality indicator. If I is dominance
preserving, then it holds that x1 dominates x2 => F(x1) > F(x2)."** — i.e. the fitness
scheme is Pareto-dominance compliant.
ENVIRONMENTAL SELECTION, verbatim: "Iterate the following three steps until the size of
population P does not exceed alpha: 1. Choose an individual x* in P with the
**smallest** fitness value... 2. Remove x* from the population. 3. **Update the fitness
values of the remaining individuals**, i.e. F(x) = F(x) + e^{-I({x*},{x})/kappa} for all
x in P." *** The incremental update is EXACT — this is the cheap part of IBEA. ***
Mating selection: binary tournament with replacement. Indicators used: the **additive
epsilon-indicator I_{eps+}** and the **binary hypervolume indicator I_HD**. On I_HD's
cost, verbatim: "calculation of the I_HD(A,B)-values is computationally expensive for
approximations containing several decision vectors, it is of order **O(n)** if two
decision vectors are compared."

*** HYPERVOLUME'S THEORETICAL APPEAL — the exact statements and the right citations. ***
(i) THE STRICT-MONOTONICITY CLAIM, verbatim from the HypE report's abstract [VFT,
Bader & Zitzler, TIK-Report 286, 2008]: "In the field of evolutionary multi-criterion
optimization, **the hypervolume indicator is the only single set quality measure that
is known to be strictly monotonic with regard to Pareto dominance: whenever a Pareto
set approximation entirely dominates another one, then also the indicator value of the
former will be better.**"
(ii) THE FORMAL DEFINITIONS, from Li & Yao's survey [VFT]: **PARETO COMPLIANCE
(= monotonicity)**, "assuming that a smaller evaluation result is preferable":
`for all A,B : A <= B => I(A) <= I(B)` (their eq. 14). Verbatim: "Pareto compliance
guarantees that a QI does not contradict the order of solution sets induced by the weak
Pareto dominance relation ... if set A is evaluated better than set B, it would never
happen that B weakly Pareto dominates A." **STRICT PARETO COMPLIANCE**:
`for all A,B : A ⊲ B => I(A) < I(B)` (eq. 15), attributed to Zitzler, Brockhoff &
Thiele 2007. Verbatim: "The strict Pareto compliance implies that only the Pareto front
achieves a unique optimal value for a problem. So far, **the HV indicator (and its
variants) is the only popular unary QI having this property.**" Citation for strict
compliance: **Zitzler, Brockhoff & Thiele, "The Hypervolume Indicator Revisited: On the
Design of Pareto-compliant Indicators Via Weighted Integration", EMO 2007, LNCS 4403,
pp. 862-876, DOI 10.1007/978-3-540-70928-2_64 — DOI V.**
(iii) THE PRECISE FORMAL STATEMENT, from the Guerreiro/Fonseca/Paquete survey [VFT,
arXiv:2005.00515; published as ACM Computing Surveys 54(6), Article 119, pp. 1-42,
2021, DOI 10.1145/3453474 — DOI V]: "Given a binary relation R on point sets, a
set-quality indicator I (to be maximized) is said to be **weakly R-monotonic** if ARB
implies I(A) >= I(B) for any A, B subset of R^d, and it is **strictly R-monotonic** if
ARB implies I(A) > I(B). ... The hypervolume indicator is well acknowledged by its
properties. **It is scaling independent and it is strictly <-monotonic** ... **This
implies that this indicator is maximal for the Pareto front** and that scaling
objectives does not affect the order imposed on point sets." Also: "Ulrich and Thiele
showed that the hypervolume indicator is a **submodular** function."
(iv) THE OTHER CANONICAL CITATION, and its statement is MORE CAUTIOUS than the
"strictly monotonic" framing — worth quoting exactly: **Zitzler, Thiele, Laumanns,
Fonseca & Grunert da Fonseca, "Performance assessment of multiobjective optimizers: an
analysis and review", IEEE TEVC 7(2):117-132, April 2003, DOI 10.1109/TEVC.2003.810758
— DOI V** (Crossref author families: Zitzler, Thiele, Laumanns, Fonseca, da Fonseca).
[VFT] Verbatim: "**The hypervolume indicator is the only unary indicator we are aware
of that is capable of detecting that A is NOT WORSE than B for all pairs (A,B).** It
gives the hypervolume of that portion of the objective space that is weakly dominated
by an approximation set A. We notice that from A ⊲ B follows that I_H(A) > I_H(B); the
reason is that A must contain at least one objective vector that is not weakly
dominated by B, thus, a certain portion of the objective space is dominated by A but
not by B. **This observation implies both <=-compatibility and ⊲-completeness.**"
*** THE TWO ARE CONSISTENT BUT SAY DIFFERENT THINGS: hypervolume lets you INFER "B is
not better than A" from I_H(A) > I_H(B); it does NOT let you CERTIFY "A is better than
B". Zitzler 2003's conclusions, verbatim: "Existing unary indicators **at best allow to
infer that an approximation set is not worse than another**." ***
*** AND NOTE: a paper titled "Why quality indicators are better than Pareto-dominance-
based set measures" (Zitzler et al.) APPEARS NOT TO EXIST — OpenAlex was searched twice
with the full title and with partial phrasings and no such work surfaced. DO NOT CITE
IT. The correct citations for the claim are Zitzler et al. 2003 for the
unary-indicator limitation and the hypervolume's <=-compatibility, and Zitzler,
Brockhoff & Thiele 2007 for strict Pareto compliance. ***

COMPUTATIONAL COST OF HYPERVOLUME — the precise claims, because they are routinely
garbled.
**#P-HARDNESS.** Bringmann & Friedrich, "Approximating the volume of unions and
intersections of high-dimensional geometric objects", *Computational Geometry*
43(6-7):601-610, 2010, DOI 10.1016/j.comgeo.2010.03.004; arXiv:0809.0835 (conference
version ISAAC 2008, LNCS 5369, pp. 436-447). [DOI V; arXiv abstract read verbatim.]
From the abstract: "While showing that this problem is **#P-hard already for very
simple bodies (i.e., axis-parallel boxes)**, we give a fast FPRAS for all objects where
one can: (1) test whether a given point lies inside the object, (2) sample a point
uniformly, (3) calculate the volume of the object in polynomial time. ... This implies
that **Klee's measure problem and the hypervolume indicator can be approximated
efficiently even though they are #P-hard and hence cannot be solved exactly in time
polynomial in the number of dimensions unless P=NP.** For the analogous problem of the
**intersection** of high-dimensional geometric objects we prove #P-hardness for boxes
and show that **there is no multiplicative polynomial-time 2^{d^{1-eps}}-approximation**
for certain boxes unless NP=BPP, but give a simple additive polynomial-time
eps-approximation."
*** NOTE THE PRECISION: #P-hardness is IN THE NUMBER OF OBJECTIVES d (the dimension),
NOT in n. For FIXED d, polynomial exact algorithms exist. And the 2^{d^{1-eps}}
inapproximability result is for **INTERSECTIONS**, not for the hypervolume (union) — a
commonly mis-attributed detail. ***
**LEAST-CONTRIBUTOR HARDNESS** — and this is the one that matters for SMS-EMOA and
HypE, because the least-contributor problem is exactly what steady-state hypervolume
selection needs. Bringmann & Friedrich, "Approximating the least hypervolume
contributor: NP-hard in general, but fast in practice", *Theoretical Computer Science*
425:104-116, March 2012, DOI 10.1016/j.tcs.2010.09.026; arXiv:0812.2636 (conference
version EMO 2009, LNCS 5467, pp. 6-20). [DOI V; arXiv abstract read verbatim]: "We show
that **exact calculation of the hypervolume contribution is #P-hard while its
approximation is NP-hard.** The same holds for the calculation of the minimal
contribution. We also prove that it is **NP-hard to decide whether a solution has the
least hypervolume contribution.** Even deciding whether the contribution of a solution
is at most (1+eps) times the minimal contribution is NP-hard. This implies that it is
**neither possible to efficiently find the least contributing solution (unless P = NP)
nor to approximate it (unless NP = BPP).** Nevertheless ... we present a fast
approximation algorithm ... [that] calculates a solution with contribution at most
(1+eps) times the minimal contribution with probability at least (1-delta) ... [and]
solves very large problem instances which are intractable for exact algorithms (e.g.,
**10000 solutions in 100 dimensions**) within a few seconds."
CORROBORATION from the Guerreiro/Fonseca/Paquete survey [VFT]: "the Hypervolume [21]
and OneContribution [22] problems are known to be **#P-hard**. **Even deciding if a
point is the least contributor is #P-hard** [22]. Moreover, HSSP [hypervolume subset
selection] was recently shown to be **NP-hard** [20] for d >= 3." ([20] = Bringmann,
Cabello & Emmerich, "Maximum Volume Subset Selection for Anchored Boxes", SoCG 2017,
22:1-22:15.)
EXACT ALGORITHM COMPLEXITIES BY DIMENSION, from the same survey [VFT]:
- d = 2, 3: **Theta(n log n)** (HV3D / HV3D+ for d=3; "Theta(n log n) time complexity
  and O(n) space complexity").
- d >= 4: **Chan's algorithm, O(n^{d/3} polylog n)** — verbatim: "Chan's algorithm [33]
  has O(n^{d/3} polylog n) time complexity, which is **currently the best time
  complexity to compute Hypervolume for d >= 4**." (Chan, "Klee's Measure Problem Made
  Easy", FOCS 2013, pp. 207-218.)
- The **WFG algorithm** (the fastest IN PRACTICE for d > 7): originally reported
  O(2^{n+1}), tightened by Lacour et al. to an **O(n^{d-1})** upper bound with an
  **Omega(n^{d/2} log n)** lower bound. The survey's recommendation, verbatim: "For
  d >= 4, Chan's algorithms is recommended since it has the best time complexity, but,
  because [of large constants, in practice other algorithms win]."
- LOWER-BOUND CITATION: Beume, Fonseca, López-Ibáñez, Paquete & Vahrenhold, "On the
  Complexity of Computing the Hypervolume Indicator", IEEE TEVC 13(5):1075-1082,
  October 2009, DOI 10.1109/TEVC.2009.2015575. [bib V via OpenAlex. *** [FLAG] This
  paper was NOT read; the commonly quoted Omega(n log n) lower bound for d >= 2 and
  the Klee's-measure reduction are attributed to it but only its bibliographic record
  was verified, not its theorem statements. ***]
**HypE** — the practical answer. Bader & Zitzler, "HypE: An Algorithm for Fast
Hypervolume-Based Many-Objective Optimization", *Evolutionary Computation* 19(1):45-76,
Spring 2011, DOI 10.1162/EVCO_a_00009. [DOI V; tech-report version TIK-Report 286 read
in full.] The key idea, verbatim from the abstract: "the high computational effort
required for hypervolume calculation has so far prevented to fully exploit the
potential of this indicator; current hypervolume-based search algorithms are limited to
problems with only a few objectives. This paper ... proposes a fast search algorithm
that uses **Monte Carlo simulation to approximate the exact hypervolume values. The
main idea is that NOT THE ACTUAL INDICATOR VALUES ARE IMPORTANT, BUT RATHER THE
RANKINGS OF SOLUTIONS induced by the hypervolume indicator.**" Accuracy can be traded
against the number of samples, and because only the RANKING matters a coarse estimate
suffices — which is what makes hypervolume-based selection viable at M >> 3.
R2 / IGD-BASED SELECTION: R2 (and R1, R3) integrates a SET OF SCALARISING (utility)
FUNCTIONS over the approximation set; Li & Yao: "the R family and IPF [integrated
preference functional] ... both integrate over a set of utility functions (aka
scalarising functions)." This makes R2 an attractive cheap proxy for hypervolume
(weakly Pareto compliant, near-linear cost). *** [FLAG] The Hansen & Jaszkiewicz 1998
attribution was verified ONLY via Li & Yao's reference table; no DOI was resolved — it
is a Technical University of Denmark report (IMM-REP-1998-7), which typically has none.
*** IGD-based selection: Sun, Yen & Zhang, "IGD Indicator-Based Evolutionary Algorithm
for Many-Objective Optimization Problems", IEEE TEVC 23(2):173-187, 2019, DOI
10.1109/TEVC.2018.2791283. [bib V]
