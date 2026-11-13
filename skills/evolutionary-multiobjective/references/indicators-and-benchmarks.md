# Multi-objective indicators, benchmarks and constraint handling
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

## 3.6 PERFORMANCE INDICATORS — AND WHY COMPARISON IS ITSELF HARD
HYPERVOLUME (HV, a.k.a. the S metric). Definition, verbatim from Li & Yao [VFT]:
"Given a solution set A and a reference point r, **HV(A) = lambda( UNION_{a in A}
{ x | a < x < r } )** where lambda denotes the **Lebesgue measure**. ... the HV value
of a set can be seen as the volume of the union of the hypercubes determined by each of
its solutions and the reference point." Higher is better. *** NEEDS ONLY A REFERENCE
POINT, NOT A REFERENCE FRONT — its main practical advantage over IGD. ***
REFERENCE-POINT SENSITIVITY — the real problem. Verbatim from Li & Yao:
- "there are few studies/theoretical guidelines on the choice of the reference point in
  HV, except for a few in particular situations (Auger et al. 2009b; Cao et al. 2015)."
- "Recently, Ishibuchi et al. (2017, 2018a) have demonstrated a clear difference of
  specifying the proper reference point for problems with a **simplex-like Pareto
  front** and an **inverted simplex-like Pareto front**. They have also shown
  experimentally that **a slightly worse reference point than the nadir point is not
  always appropriate**, especially for the case of many-objective optimisation and/or a
  small population size."
- "the HV indicator **prefers the knee regions, and is biased to convex regions over
  concave regions** (Zitzler and Thiele 1998). As proven in Auger et al. (2009b), **the
  distribution of a set of solutions that achieves the maximum HV value depends largely
  on the slope of the Pareto front.** For example, HV may be in favour of very
  non-uniform solution sets on a highly non-linear Pareto front."
- The reference-point citation to use: **Ishibuchi, Imada, Setoguchi & Nojima, "How to
  Specify a Reference Point in Hypervolume Calculation for Fair Performance
  Comparison", *Evolutionary Computation* 26(4):411-440, 2018, DOI
  10.1162/EVCO_a_00226 — DOI V.**
- OPTIMAL mu-DISTRIBUTIONS (what a finite HV-maximal set actually looks like), from
  Guerreiro et al. verbatim: "the exact location of the points in an optimal subset of a
  given size mu is known only for **continuous linear fronts**. In this case, there is a
  unique optimal subset where all points are on the Pareto front and uniformly spaced
  between two outer points, the position of which depends both on the reference point
  and on the two extreme points of the Pareto front. ... **not much is known about
  optimal mu-distributions** [in three objectives]."
**PRACTICAL RULE: HV IS INCOMPARABLE ACROSS PAPERS UNLESS THE REFERENCE POINT AND THE
NORMALISATION ARE BOTH STATED. STATE THEM.**

GD, IGD, GD+, IGD+. From pymoo's indicator docs [V, fetched 2026-11-11] — with Z the
reference front and A the obtained set, all for minimisation:
    GD(A)   = (1/|A|) * ( SUM_{a_i in A} d_i^p )^{1/p}   with p = 2; d_i = min_{z in Z} ||a_i - z||
    IGD(A)  = (1/|Z|) * ( SUM_{z_i in Z} d-hat_i^p )^{1/p}  with p = 2; d-hat_i = min_{a in A} ||z_i - a||
    GD+(A)  = (1/|A|) * ( SUM_{a_i in A} (d_i^+)^2 )^{1/2}
    IGD+(A) = (1/|Z|) * ( SUM_{z_i in Z} (d_i^+)^2 )^{1/2}
where the **MODIFIED DISTANCE** is, for minimisation,
    **d^+(a, z) = || ( max{a_1 - z_1, 0}, ..., max{a_M - z_M, 0} ) ||**
i.e. **ONLY THE COMPONENTS IN WHICH `a` IS WORSE THAN `z` CONTRIBUTE.** *** That single
change is what buys Pareto compliance: if a dominates a', then d+(a, z) <= d+(a', z)
componentwise for every z, so the indicator can never rank a dominated set better. ***
Lower is better for all four. GD/IGD need a REFERENCE FRONT; IGD is the standard
convergence+diversity scalar in the field.
*** AND A TRAP: the NSGA-III paper uses **IGD(A,Z) = (1/|Z|) SUM_i min_j d(z_i, a_j)**
— the **p = 1 AVERAGE** form, NOT pymoo's p = 2 form. THE IGD YOU COMPUTE IS NOT THE
IGD SOMEONE ELSE COMPUTED unless p, normalisation and Z all match. ***
THE IGD+ CITATION: **Ishibuchi, Masuda, Tanigaki & Nojima, "Modified Distance
Calculation in Generational Distance and Inverted Generational Distance", *EMO 2015*,
LNCS 9019, pp. 110-125, 2015, DOI 10.1007/978-3-319-15892-1_8 — DOI VERIFIED.**
*** [FLAG] The EMO-2015 chapter's full text could not be obtained. The compliance claim
is verified from TWO INDEPENDENT SECONDARY SOURCES: (1) pymoo's own indicator docs,
verbatim — IGD+ is "**weakly Pareto compliant whereas the original IGD is not**"; and
for IGD, "IGD is not weakly Pareto compliant, as IGD+ is." (2) Li & Yao's ACM CSUR
survey [VFT], verbatim: "Many widely-used QIs are **Pareto non-compliant, such as GD,
SP, MS, and IGD**. ... some non-compliant QIs, after modifications, can become Pareto
compliant. **The studies in Ishibuchi et al. (2015) are an example along these lines,
where GD and IGD are transformed into two Pareto compliant indicators GD+ and IGD+.**"
***
TWO IMPORTANT NUANCES from Li & Yao: IGD+ is WEAKLY compliant, **NOT STRICTLY** —
verbatim, "Pareto compliant QIs may not fully distinguish between solution sets subject
to the 'better' relation. That is, when A ⊲ B, a Pareto compliant indicator I may
return I(A) = I(B)." And: **IGD+ DOES NOT FIX REFERENCE-SET SENSITIVITY** — verbatim:
"This particularly applies to a QI that is sensitive to the reference set's
distribution, **such as IGD and IGD+**." What IGD+ DOES fix is dominance-resistant
solutions in the reference set — "**IGD+ is insensitive to the DRSs**." A useful special
case: "GD and IGD [can be compliant] when used for a **bi-objective problem with a
continuous Pareto front** (Schutze et al. 2012)."

### ADDITIVE AND MULTIPLICATIVE EPSILON-INDICATOR

From Zitzler et al. 2003 [VFT] — the
BINARY I_eps is the paper's own contribution and its headline POSITIVE result. For
minimisation:
- **ADDITIVE**: I_{eps+}(A,B) = inf_{eps in R} { for all b in B, exists a in A :
  a_i - eps <= b_i for all i } — the smallest additive amount by which A must be
  SHIFTED to weakly dominate B.
- **MULTIPLICATIVE**: I_eps(A,B) = inf_{eps > 0} { for all b in B, exists a in A :
  a_i <= eps * b_i for all i } (requires strictly positive objectives).
- **I_{eps+}(A,B) <= 0 <=> A <= B.** VERBATIM CONCLUSION: "The binary epsilon-indicator
  proposed in this paper, e.g., **is capable of detecting whether an approximation set
  is better than another.**" And: "it has a clear interpretation — in contrast to, e.g.,
  the coverage and the hypervolume indicators" and, unlike hypervolume, it is CHEAP.
- The UNARY variant I_{eps+}(A, R) against a fixed reference set R is what most papers
  actually report; it is weakly compliant but LOSES the "better than" detection power.
- Li & Yao's table confirms attribution: "Epsilon indicator (epsilon-indicator)
  **Zitzler et al. (2003)**". It is also notably REFERENCE-SET-ROBUST: verbatim, "**the
  epsilon-indicator and PCI ... are able to work with the reference set having any
  distribution and location**."

SPREAD / DELTA. The Delta diversity metric is from the NSGA-II paper itself [VFT,
eq. 1]:
    **Delta = ( d_f + d_l + SUM_{i=1}^{N-1} |d_i - d-bar| ) / ( d_f + d_l + (N-1) d-bar )**
where d_i are the N-1 consecutive Euclidean distances along the obtained front, d-bar
their mean, and d_f, d_l "the Euclidean distances between the extreme solutions [of the
true PF] and the boundary solutions of the obtained non-dominated set". Delta = 0 is
ideal (perfectly uniform spacing reaching both extremes). *** CAVEAT: it is a
2-OBJECTIVE construction (it needs a well-defined CONSECUTIVE ORDERING along the front)
and does not extend cleanly past M=2. *** Related: Maximum Spread MS / M*_3 is from
Zitzler et al. 2000, and Li & Yao note it "does not touch on the convergence of the
set" — pure-diversity indicators are almost all Pareto NON-compliant. Verbatim: "This
is particularly true for QIs that measure the diversity ... **since they rarely take
into account the closeness of solution sets**. DCI is the only known diversity QI that
is compliant with Pareto dominance when comparing two sets. But if more sets are
involved, DCI does not guarantee the Pareto compliance property."

*** THE UNARY-INDICATOR IMPOSSIBILITY RESULT — STATED CORRECTLY. This is the
most-misquoted result in the field. *** Verbatim from Zitzler et al. 2003 [VFT].
First the machinery. A **COMPARISON METHOD** C_{I,E} combines a set of indicators I
with an **INTERPRETATION FUNCTION** E that maps the indicator values to a Boolean.
**Definition 4 (Compatibility and Completeness)**: a comparison method C is
**⊲-COMPATIBLE** if a `true` outcome IMPLIES the dominance relation holds (no false
positives), and **⊲-COMPLETE** if whenever the relation holds the outcome is `true` (no
false negatives).
**THEOREM 1, verbatim: "Suppose an optimization problem with [k >= 2] objectives, where
the objective space is [Z subset of R^k]. Then, THERE EXISTS NO COMPARISON METHOD
C_{I,E} BASED ON A FINITE COMBINATION OF UNARY QUALITY INDICATORS THAT IS
⊲-COMPATIBLE AND ⊲-COMPLETE AT THE SAME TIME, i.e., [C_{I,E}(A,B) = true <=> A ⊲ B] for
any approximation sets A, B."**
And the paper's own gloss, verbatim: "That is, for any combination of a finite number of
unary quality indicators, we cannot find an interpretation function E such that the
corresponding comparison method is ⊲-compatible and ⊲-complete. Or in other words:
**the number of criteria that determine what a good approximation set is is
infinite.**"
Also verbatim: "Note that Theorem 1 also holds: 1) if we only assume that Z contains an
open hypercube ... and 2) if we consider **any other relation from Table I**." And in
the Conclusions: "Unary quality indicators ... are in general not capable of indicating
whether an approximation set is better than another — **also if several of them are
used. This even holds if we consider approximation sets containing a single objective
vector only.**"
*** TWO COROLLARIES THAT MATTER AND ARE USUALLY OMITTED: ***
- The result is about **FINITE** combinations. Verbatim: "such a comparison method
  exists if we allow an **infinite** number of indicators. The empirical attainment
  function, when applied to single approximation sets, can be understood as a
  combination of |Z| unary indicators ... On its basis, a ⊲-compatible and
  ⊲-complete comparison method can be constructed." **THIS IS THE FORMAL ARGUMENT FOR
  USING EMPIRICAL ATTAINMENT FUNCTIONS / ATTAINMENT SURFACES rather than a single
  number.**
- **Corollary 1** shows a unary indicator CAN be constructed that detects "better than"
  for approximation sets of BOUNDED SIZE — but it is a pathological digit-interleaving
  construction. Verbatim: "The corollary, however, is rather of theoretical than of
  practical use. **The indicator constructed in the proof is able to indicate whether A
  is better than B, but it does not express HOW MUCH better it is** — this is one of the
  motives for using quality indicators."
**WHAT THE THEOREM DOES NOT SAY:** it does NOT say unary indicators are useless, nor
that hypervolume is uninformative. It says NO FINITE SET OF UNARY NUMBERS IS AN EXACT
ORACLE FOR THE SET-DOMINANCE RELATION. The practical reading: use at least one
Pareto-compliant unary indicator (hypervolume, IGD+, epsilon), report the reference
point/front, and supplement with a BINARY indicator or attainment-function plots when
you need to claim "better than." The paper's own recommendation, verbatim: "**Binary
indicators, which assign real numbers to ordered pairs of approximation sets, in
principle do not possess the theoretical limitations of unary indicators.** ... However,
it has to be mentioned that the greater inferential power comes along with additional
complexity: in contrast to unary indicators, the number of indicator values to be
considered is **not linear but quadratic** in the number of approximation sets."
The complementary set-based framing: **Zitzler, Thiele & Bader, "On Set-Based
Multiobjective Optimization", IEEE TEVC 14(1):58-79, February 2010, DOI
10.1109/TEVC.2009.2016569 — DOI V.**

*** REFERENCE-SET DEPENDENCE — the worked numerical example that should end the
practice of building a reference set from the union of all competitors' results. ***
From Li & Yao [VFT]: "When comparing A with B, if the reference set is composed of these
two sets, we will have A evaluated better than B (**IGD(A) ~= 1.41 < IGD(B) ~= 2.12**).
But if adding another set C which has the similar distribution pattern to B into the
evaluation, and now the reference set is composed of the three sets, we will have A
worse than B (**IGD(A) ~= 1.82 > IGD(B) ~= 1.72**)."
**THE SAME TWO SETS SWAP PLACES DEPENDING ON WHICH THIRD ALGORITHM YOU HAPPENED TO
INCLUDE IN THE COMPARISON.**
Also from Li & Yao, on the ideal point for ideal-point-based indicators: "it is
**crucial to not underestimate the ideal point** as this may lead to solutions that are
non-dominated with the estimated ideal point not to contribute fully to the evaluation
results. ... it is advised to use a reference point slightly better than the ideal
point, say **ref_j = ideal_j - l_j/(2N - 2)** in a bi-objective scenario, where l_j is
the range of objective j and N is the size of the solution set."
**PRACTICAL CHECKLIST FOR A DEFENSIBLE EMO COMPARISON:** (1) state the reference point
for HV and the normalisation used; (2) state the reference front Z for IGD/IGD+ AND HOW
IT WAS GENERATED (analytic PF, NOT the union of runs); (3) state p for GD/IGD; (4) use
at least one Pareto-compliant indicator (HV, IGD+, epsilon); (5) report distributions
over >= 25-31 independent runs with a non-parametric test and a multiple-comparison
correction; (6) prefer attainment-function/EAF plots when claiming one set is BETTER
THAN another. *** Items 1-4 are directly supported by the sources above; items 5-6 are
standard community convention rather than a quotation. ***

## 3.7 BENCHMARK SUITES
**ZDT.** Zitzler, Deb & Thiele, "Comparison of Multiobjective Evolutionary Algorithms:
Empirical Results", *Evolutionary Computation* 8(2):173-195, June 2000. **DOI
10.1162/106365600568202 — DOI V.** [VFT]
All problems follow one template [VFT]: minimise f_1(x_1) and f_2 = g(x_2..x_n) *
h(f_1, g). "The function f_1 is a function of the first decision variable only, g is a
function of the remaining n-1 variables, and the parameters of h are the function
values of f_1 and g. The test functions differ in these three functions as well as in
the number of variables and in the values the variables may take."
Six problems, with the authors' own feature labels (verbatim) and pymoo's default
dimensions [V, docs fetched 2026-11-11]:
- **ZDT1** (T1): "has a **convex** Pareto-optimal front". Convex. pymoo n = 30.
- **ZDT2** (T2): "the **nonconvex** counterpart to T1". Concave. n = 30.
- **ZDT3** (T3): "represents the **discreteness** feature; its Pareto-optimal front
  consists of several **noncontiguous convex parts** ... The introduction of the sine
  function in h causes **discontinuity in the Pareto-optimal front. However, there is no
  discontinuity in the parameter space.**" 5 disconnected convex arcs. n = 30.
- **ZDT4** (T4): "contains [many] local Pareto-optimal fronts and, therefore, tests for
  the EA's ability to deal with **multimodality**". Convex. n = 10.
- **ZDT5** (T5): "describes a **deceptive** problem and distinguishes itself from the
  other test functions in that **x_i represents a binary string** ... u(x_i) gives the
  number of ones in the bit vector (unitation) ... The global Pareto-optimal front as
  well as the local ones are convex." pymoo: 11 decoded vars — x_1 uses 30 bits,
  x_2..x_11 use 5 bits each.
- **ZDT6** (T6): "includes **two difficulties caused by the nonuniformity** of the
  search space: first, the Pareto-optimal solutions are **nonuniformly distributed along
  the global Pareto front** (the front is biased for solutions for which f_1 is near
  one); second, the **density of the solutions is lowest near the Pareto-optimal front
  and highest away from the front** ... and is nonconvex". Concave, non-uniform. n = 10.
*** THE KNOWN CRITICISM — and it is best stated by the WFG authors themselves [VFT,
Huband et al. 2006, verbatim]: the ZDT suite, "despite being an immensely popular test
suite, ... has **numerous shortcomings**: It only has problems with **two objectives**.
**None** of its problems has fitness landscapes with **flat regions**. Its only
**deceptive** problem is **binary encoded**. **None** of its problems has a
**degenerate** Pareto optimal front. **None** of its problems is **nonseparable**.
**Only the number of distance parameters is scalable.** All except ZDT4's distance
parameters are **extremal** parameters, and even those are **medial** parameters." And:
"Although the ZDT test suite is popular, **by itself it is far from** [adequate]."
BEYOND THAT: modern algorithms solve ZDT1-3 and ZDT6 to near-optimality in a few
thousand evaluations, so ZDT discriminates almost nothing in 2026 except as a smoke
test; and ZDT5's binary encoding means most real-coded libraries cannot run it without
special handling. ***

**DTLZ.** Deb, Thiele, Laumanns & Zitzler, "Scalable Test Problems for Evolutionary
Multiobjective Optimization", in *Evolutionary Multiobjective Optimization* (Abraham,
Jain & Goldberg, eds.), Springer, pp. 105-145, 2005. **DOI 10.1007/1-84628-137-7_6 —
DOI V.** The earlier conference version is CEC 2002; the original technical report had
**NINE** problems.
*** NUMBERING CAUTION — THIS BITES PEOPLE. Verbatim from the WFG paper [VFT, footnote
3]: "In fact, **the number of DTLZ problems depends on which paper is being referred
to.** In this paper, we are using the nine DTLZ problems from the original [technical]
report ... [a version] also exists, in which **only seven of the original nine problems
were reproduced (DTLZ5 and DTLZ9 from the original paper were dropped). As a result,
DTLZ6 from the original technical report is DTLZ5 in the conference paper, DTLZ7 is
DTLZ6 in the conference paper, and DTLZ8 is DTLZ7 in the conference paper.**" SO
"DTLZ7" MEANS DIFFERENT PROBLEMS IN DIFFERENT PAPERS. Modern libraries (pymoo, jMetal)
use the SEVEN-problem numbering. ***
Front geometries and purposes, from pymoo's DTLZ docs [V], with the g-function structure
x_M carrying k = n - M + 1 distance variables:
- **DTLZ1**: **LINEAR** hyperplane, SUM_i f_i = 0.5. Tests convergence past **(11^k - 1)**
  local fronts.
- **DTLZ2**: **UNIT SPHERE** in the first octant (SUM_i f_i^2 = 1) — spherical/concave.
  Tests scaling to many objectives; baseline convergence.
- **DTLZ3**: same spherical front, reached at g* = 0. Convergence past **(3^k - 1)**
  parallel local fronts.
- **DTLZ4**: same spherical front, with an **alpha = 100** variable mapping. Tests
  **maintaining spread** — solutions crowd near the f_M-f_1 plane.
- **DTLZ5**: a **CURVE** (degenerate — dimension M-2 lower than the front should be).
  Convergence to a curve; easy 2D visualisation.
- **DTLZ6**: same curve-type front, optimum at x_M = 0. Harder convergence; "NSGA-II and
  SPEA2 struggle"; |x_M| = 10 fixed.
- **DTLZ7**: **2^{M-1} DISCONNECTED** Pareto-optimal regions; "generally consists of
  convex components, with some mixed convexity/concavity" (WFG paper). Tests keeping
  sub-populations alive across separate regions.
DTLZ8 and DTLZ9 have side constraints (the WFG paper omits them for that reason).
*** THE KNOWN DTLZ FLAWS, from the WFG paper [VFT, verbatim]: ***
- **DTLZ5/DTLZ6 ARE NOT ACTUALLY DEGENERATE FOR M > 3.** Verbatim: "**DTLZ5 and DTLZ6
  are both claimed to be problems with degenerate Pareto optimal fronts** ...
  **Unfortunately, this is not true with DTLZ5 or DTLZ6**: it is possible to have
  [solutions that dominate the supposed front]. ... As a result, **the nature of DTLZ5
  and DTLZ6's Pareto** [optimal fronts is not as advertised]." They give an explicit
  four-objective counterexample.
- **MULTIPLE GLOBAL OPTIMA / PARETO MANY-TO-ONE.** Verbatim: "the objective functions of
  DTLZ1-DTLZ4 have multiple global optima since terms such as [cos(...)] can evaluate to
  zero, thereby allowing flexibility in the selection of other [parameters] ... [most]
  of the DTLZ problems are Pareto many-to-one."
- **FIXED NUMBER OF POSITION PARAMETERS.** Verbatim footnote: "**The DTLZ test suite
  uses a fixed (relative to the number of objectives) number of position parameters**" —
  so you can scale distance variables but NOT position variables.
- **TRIANGULAR-FRONT BIAS** — see §3.4: Tanabe & Ishibuchi 2020 [VFT] on why
  decomposition methods look good here.

**WFG.** Huband, Hingston, Barone & While, "A Review of Multiobjective Test Problems and
a Scalable Test Problem Toolkit", IEEE TEVC 10(5):477-506, October 2006. **DOI
10.1109/TEVC.2005.861417 — DOI V.** [VFT]
The contribution is a **TOOLKIT**: a problem is built as a vector of **TRANSITION
FUNCTIONS** applied to parameters classified as **POSITION-RELATED** (k of them, which
move you ALONG the front) vs **DISTANCE-RELATED** (l of them, which move you TOWARD or
away from it), composed with a **SHAPE FUNCTION** that sets the front's geometry. Both k
and l are INDEPENDENTLY scalable, and M is scalable. WFG1-9 is the example suite
instantiated from it.
WHAT IT FIXES ABOUT DTLZ, verbatim: "the WFG test suite exceeds the functionality of
previous existing test suites. In particular, it includes a number of problems that
exhibit properties not evident in the commonly-used DTLZ test suite. These include:
**nonseparable problems, deceptive problems, a truly degenerate problem, a mixed shape
Pareto front problem, problems scalable in the number of position-related parameters,
and problems with dependencies between position- and distance-related parameters.** The
WFG test suite provides a truer means of assessing the performance of optimization
algorithms on a wide range of different problems." Also verbatim: "We recommend that all
distance-related parameters be subjected [to transformations that] encourage EAs to
normalize fitness values" — i.e. DELIBERATELY BADLY SCALED OBJECTIVES.
The individual problems' character, verbatim: "**WFG1** skews the relative significance
of different parameters by employing **dissimilar weights in its weighted sum
reduction**; only **WFG1 and WFG7 are both separable and unimodal**; the **nonseparable
reduction of WFG6 and WFG9 is more difficult** than that of WFG2 and WFG3; the
**multimodality of WFG4** has larger 'hill sizes' (and is thus more difficult) than that
of WFG9; the **deceptiveness of WFG5** is more difficult than that of WFG9; [the
position-related] parameters of **WFG7** are dependent on its distance-related
parameters; the distance-related parameters of **WFG8** are dependent on its
position-related [ones]." Also: **WFG2 is disconnected**; **WFG3 is the degenerate
one**; **WFG2 and WFG3 require l to be a multiple of two** "due to the nature of their
nonseparable reductions"; and **k must be divisible by M-1**. Optimality condition for
WFG1-WFG7: a solution is Pareto optimal iff all distance parameters take a fixed value;
WFG8 and WFG9 have more involved conditions, "making WFG8 a difficult problem."
THEIR OWN EMPIRICAL POINT, verbatim: "**The results demonstrate that the WFG suite
presents a more comprehensive set of challenges**" than DTLZ. *** And the calibration
figure worth carrying into Section 4's budget discussion: they ran NSGA-II, 35 runs,
population 100, for **25,000 generations** (= 2.5M evaluations), saving fronts at 250 /
2500 / 25,000 generations, noting that "a population size of 100 for 250 generations is
a common [setting] in the literature" and that **NSGA-II STILL HADN'T CONVERGED on
several WFG problems at 25,000 generations.** "On WFG1, for example, NSGA-II shows poor
coverage" — WFG1's bias remains hard for NSGA-II today. ***

**REAL-WORLD: THE RE SUITE.** Tanabe & Ishibuchi, "An easy-to-use real-world
multi-objective optimization problem suite", *Applied Soft Computing* 89:106078, April
2020. **DOI 10.1016/j.asoc.2020.106078 — DOI V. arXiv:2009.12867.** [VFT]
Verbatim from the abstract: "a problem suite consisting of **16 bound-constrained
real-world problems**. The problem suite includes various problems in terms of **the
number of objectives, the number of decision variables, the shape of the Pareto front,
and the type of design variables. 4 out of the 16 problems are multi-objective
mixed-integer optimization problems.** We provide **Java, C, and Matlab source codes**
of the 16 problems... In addition to the 16 problems, we present **8 constrained**
multi-objective real-world problems."
*** THEIR HONEST ACCOUNTING OF THE TRADE-OFF (their Table 1 scores synthetic problems on
EASINESS, CLEARNESS, SCALABILITY and RE problems on NON-ARTIFICIALITY, EASINESS),
verbatim: "we believe that the RE problems do not have the above-mentioned unrealistic
properties (e.g., the triangular Pareto front). **We do not claim that real-world
problems (including the RE problems) must always be better than synthetic test
problems** ... they have **two disadvantages**: Similar to other real-world problems,
**the properties of the RE problems are unclear. All the RE problems are not scalable**
with respect to the number of objectives M and design variables D." *** They partly
mitigate the first by analysing each problem's front shape. Definitions are "given by
simple equations or surrogate models" — cheap to evaluate, which is the point.
jMetalPy ships both **RE** and **RWA** suites; pymoo does NOT ship RE as of 0.6.2 (its
real-world-flavoured problems are BNH, OSY, TNK, Truss2D, Welded Beam, plus MODAct).

**CEC MOEA COMPETITIONS.** *** [FLAG — THIS IS THE WEAKEST-SOURCED ITEM IN THIS
SECTION.] The CEC competition record could not be verified directly. What WAS checked:
Suganthan's GitHub profile (fetched 2026-11-11) lists `2021-RW-MOP` (real-world
multi-objective problems, 2021) plus single-objective/constrained benchmark repos
(`CEC2017-BoundConstrained`, `CEC2019` 100-Digit, `2020-RW-Constrained-Optimisation`,
`2022-SO-BO`) — so the 2021 real-world MO competition is confirmed to exist as a
benchmark release, but the page does not label it a CEC competition. ***
The historically important one, which could NOT be verified: the **CEC 2009 Special
Session and Competition on Performance Assessment of Unconstrained/Constrained
Multi-Objective Optimization Algorithms**, whose **UF1-UF10** (unconstrained) and
**CF1-CF10** (constrained) instances remain widely used, defined in **Zhang, Zhou, Zhao,
Suganthan, Liu & Tiwari, "Multiobjective optimization test instances for the CEC 2009
special session and competition", University of Essex / Nanyang Technological
University, Technical Report CES-487, 2008.** *** This report has no DOI and could not
be fetched; treat the author list, report number and year as UNVERIFIED. *** The UF/CF
instances' distinguishing feature (per the MOEA/D-DE paper, DOI V) is **COMPLICATED
PARETO *SETS*** — nonlinear variable linkages in DECISION space, which DTLZ/WFG largely
lack and which break algorithms that assume simple PS geometry.

## 3.8 CONSTRAINT HANDLING IN MOEAs
**DEB'S CONSTRAINT-DOMINATION PRINCIPLE (CDP)** — and the primary source is the NSGA-II
paper itself, §VI [VFT, verbatim]:
  "**Definition 1** A solution i is said to **constrained-dominate** a solution j, if
  any of the following conditions is true: 1. Solution i is **feasible** and solution j
  is not. 2. Solutions i and j are **both infeasible**, but solution i has a **smaller
  overall constraint violation**. 3. Solutions i and j are **feasible** and solution i
  **dominates** solution j."
Consequences, verbatim: "**any feasible solution has a better non-domination rank than
any infeasible solution.** All feasible solutions are ranked according to their
non-domination level based on the objective function values. But, among two infeasible
solutions, the solution with a smaller constraint violation has a better rank. Moreover,
**this modification in the non-domination principle does not change the computational
complexity of NSGA-II.**"
*** THE CRUCIAL DESIGN VIRTUE, verbatim: "Since in no case constraints and objective
function values are compared with each other, **there is no need of having any penalty
parameter**, a matter which makes the proposed constrained handling approach useful and
attractive." *** The overall constraint violation is the SUM OF NORMALISED VIOLATIONS of
the violated constraints. The single-objective ancestor: **Deb, "An efficient constraint
handling method for genetic algorithms", *Computer Methods in Applied Mechanics and
Engineering* 186(2-4):311-338, June 2000, DOI 10.1016/S0045-7825(99)00389-8 — DOI V.**
Characterisation in the modern survey [VFT]: "**CDP was proposed by Deb et al., which is
most commonly used due to its simplicity and ease of implementation.**"
**CDP'S WEAKNESS**, verbatim from Liang et al. [VFT]: "The operation of CDP is
relatively simple, but **it prefers feasible solutions, which will cause the population
to fall into some local feasible regions when CMOPs have discrete feasible regions or
infeasible barriers.**"
UNPACKED: CDP imposes a STRICT LEXICOGRAPHIC PRIORITY of feasibility over objective
quality. Infeasible individuals carry NO usable objective information — they are ranked
purely by violation. So when the feasible region is DISCONNECTED, or when the path to
the global constrained PF runs THROUGH an infeasible barrier, CDP's population gets
pinned in whichever feasible pocket it first found and has no mechanism to cross. It also
wastes the information in "slightly infeasible but objectively excellent" solutions,
which in many engineering problems sit right against the ACTIVE constraint boundary
where the constrained optimum lives.
THE ALTERNATIVES, from Liang et al., which groups CDP, epsilon-constraint and stochastic
ranking as the "feasibility-rule / separate-handling" family [VFT, verbatim: "mainly
including the CDP, epsilon constrained method, and stochastic ranking (SR)"]:
**EPSILON-CONSTRAINT METHOD**, verbatim: "This method was proposed by **Takahama and
Sakai**, which **uses a parameter epsilon to relax constraints. epsilon is gradually
reduced, and when the constraint violation degree of an individual is less than epsilon,
it is considered as a feasible solution. Obviously, when epsilon is reduced to 0, the
epsilon constrained method is the same as CDP.** When comparing individuals A and B, the
epsilon constrained method uses the following criteria: 1. If CV(A) <= epsilon,
CV(B) <= epsilon, and A Pareto dominates B, then A is selected. 2. If CV(A) <= epsilon,
CV(B) > epsilon, then A is selected. 3. If CV(A) > epsilon, CV(B) > epsilon, and
CV(A) < CV(B), then A is selected." Citation: **Takahama & Sakai, "Constrained
Optimization by the epsilon Constrained Differential Evolution with Gradient-Based
Mutation and Feasible Elites", IEEE CEC 2006, pp. 1-8, DOI 10.1109/CEC.2006.1688283 —
DOI V.** *** THE POINT: early on epsilon is large, so NEAR-FEASIBLE solutions compete on
OBJECTIVE quality and the population can TRAVERSE infeasible regions; as epsilon -> 0 the
method anneals into CDP and converges to feasibility. *** Follow-ups: Takahama & Sakai,
CEC 2010, DOI 10.1109/CEC.2010.5586484; and *Studies in Computational Intelligence*,
2009, DOI 10.1007/978-3-642-00619-7_3. epsilon-DE variants won several CEC constrained
competitions.
**STOCHASTIC RANKING (SR)** — and this is worth stating mechanically because it is the
cleanest idea in the area. Verbatim from Liang et al.: "a probability parameter p_f is
introduced. When two individuals are compared, **the probability with p_f only compares
their objective function value, and the probability with (1-p_f) compares their
constraint violation degree.** This method is able to use the information of the
objective function to some extent." Citation: **Runarsson & Yao, "Stochastic ranking for
constrained evolutionary optimization", IEEE TEVC 4(3):284-294, 2000, DOI
10.1109/4235.873238 — DOI V.**
THE MECHANISM IN FULL: instead of choosing EITHER objective-based OR violation-based
comparison, you RANDOMISE THE COMPARISON CRITERION PER PAIRWISE COMPARISON. Concretely,
run a bubble-sort-like sweep over the population; for each adjacent pair draw u ~ U[0,1]
and **compare by objective value if u < P_f, otherwise compare by constraint violation**
(with the refinement that two FEASIBLE individuals are always compared by objective).
**P_f is the probability of using the objective-function comparison, and the paper's
recommended value is P_f ~= 0.45** — deliberately just BELOW 0.5, so that violation
comparisons dominate slightly and the population drifts toward feasibility while still
being able to traverse infeasible regions. *** THE ELEGANCE: it interpolates continuously
between "pure feasibility-first" (P_f = 0) and "ignore constraints" (P_f = 1) with ONE
DIMENSIONLESS PARAMETER AND NO PROBLEM-DEPENDENT SCALING — which is exactly the thing
penalty coefficients get wrong. *** Implemented in pymoo as **SRES** and **ISRES** (the
improved variant with differential variation).
**REPAIR.** Problem-specific projection of infeasible individuals back into the feasible
set. MOEA/D has a hook for exactly this (Step 2.2, verbatim: "Apply a problem-specific
repair/improvement heuristic on y to produce y'"; and "a problem-specific heuristic is
used to repair y in the case when y invalidates any constraints"). Survey example,
verbatim: "Saha and Ray proposed an **equality constraint repair method** based on
probability points, which combines CDP and clustering methods to repair infeasible
solutions." *** CAVEAT: repair biases the search distribution toward the constraint
boundary and is not generic. Also decide explicitly whether you write the repaired
genotype back (Lamarckian) or only use its fitness (Baldwinian) — they behave very
differently. ***
**PENALTY FUNCTIONS.** The survey's first family. Static penalties "remain unchanged in
the early and late stages of evolution, which is not conducive to the balance between
the objectives and constraints"; dynamic/adaptive penalties adjust the coefficient by
generation number or by "the feasibility proportion in the current population". Needs a
penalty parameter — the thing CDP was designed to avoid. *** WHY THE COEFFICIENT IS HARD,
STATED PRECISELY: too small and the global optimum of the penalised objective is
INFEASIBLE, so the search converges to an infeasible point and you get a
BETTER-THAN-OPTIMAL reported value — the most common and most embarrassing bug in
constrained-EC papers; too large and the penalty term dominates, the feasible interior's
gradient information is swamped, and the search degenerates into a feasibility search
that stops at the first feasible point. The coefficient also has to be SCALE-MATCHED to
f, so it is not transferable between problems, and when constraints are ACTIVE at the
optimum (the usual case) the right coefficient depends on the Lagrange multipliers, which
you do not know. DEATH PENALTY additionally fails whenever the feasible region is small
or disconnected — you may never sample a feasible point at all, and it discards the only
information that would tell you which way feasibility lies. ***
**MULTI-POPULATION / TWO-ARCHIVE METHODS** — the current state-of-the-art direction:
maintain one archive driving convergence and one exploring infeasible space. **C-TAEA:
Li, Chen, Fu & Yao, "Two-Archive Evolutionary Algorithm for Constrained Multiobjective
Optimization", IEEE TEVC 23(2):303-315, April 2019, DOI 10.1109/TEVC.2018.2855411 — DOI
V** *** (note: Crossref gives the authors as Li, Chen, Fu, Yao — the frequently seen
"Li, Chen, Min, Zhang" attribution is WRONG). *** Also **push-and-pull search (PPS)**,
and **ACDP** (angle-based CDP, integrating angle information into CDP and reusing
infeasible-solution information, embedded in MOEA/D).
SURVEY TO CITE FOR THE WHOLE AREA: **Liang, Ban, Yu, Qu, Qiao, Yue, Chen & Tan, "A
Survey on Evolutionary Constrained Multiobjective Optimization", IEEE TEVC
27(2):201-221, 2022/2023, DOI 10.1109/TEVC.2022.3155533 — DOI V.** [VFT]
Also useful general surveys for the single-objective side: Michalewicz & Schoenauer,
"Evolutionary Algorithms for Constrained Parameter Optimization Problems", *Evolutionary
Computation* 4(1):1-32, 1996, DOI 10.1162/evco.1996.4.1.1 [V]; Coello Coello,
"Theoretical and numerical constraint-handling techniques used with evolutionary
algorithms: a survey of the state of the art", *CMAME* 191(11-12):1245-1287, 2002, DOI
10.1016/S0045-7825(01)00323-1 [V]. Coello Coello still runs the GECCO tutorial — the
2024 and 2025 versions are citable and current: DOI 10.1145/3638530.3648406 (GECCO '24,
pp. 1261-1283) and 10.1145/3712255.3716509 (GECCO '25, pp. 1767-1790). [V]
PRACTICAL NOTE FOR THE pycma USER: `cma` 4.5.0 ships `cma/constraints_handler.py` (56 KB)
with an **AUGMENTED-LAGRANGIAN** nonlinear-constraints handler, plus
`boundary_handler.py` for bounds — so you do not need to hand-roll penalties with
CMA-ES. [V]
pymoo's constrained-algorithm support [V, algorithm list fetched 2026-11-11]: NSGA2,
RNSGA2, PINSGA2, NSGA3, UNSGA3, RNSGA3, CTAEA, SMSEMOA, SPEA2, OmniOptimizer, CMOPSO,
MOPSO_CD, DNSGA2, KGB, NSDE, GDE3, NSDER all support constraints; *** MOEAD, AGEMOEA,
AGEMOEA2, RVEA and CMAES are marked as NOT supporting constraints. ***

## 3.9 WHY EAs ARE GENUINELY STATE OF THE ART HERE — AND WHERE THEY ARE NOT
THE GENUINE STRENGTHS:
1. **ONE RUN RETURNS A WHOLE FRONT APPROXIMATION.** This is the structural advantage. A
   scalarization-based pipeline runs one NLP solve per weight vector and must choose the
   weights IN ADVANCE; a population-based MOEA maintains N candidate trade-offs that
   CO-EVOLVE AND MUTUALLY INFORM each other. MOEA/D makes the connection explicit and
   shows why the population helps rather than merely parallelising [VFT]: "any
   information about these g's with weight vectors close to lambda^i should be helpful
   for optimizing g^te(x|lambda^i). This is a major motivation behind MOEA/D." That is
   information SHARING across subproblems, which independent scalarized solves do not
   get.
2. **NO DIFFERENTIABILITY NEEDED.** Only a ranking of candidates. Black-box simulators,
   non-smooth aggregations (Tchebycheff is explicitly non-smooth), discontinuous
   objectives, and simulation codes that return only a number are all fine. The MOEA/D
   authors make exactly this point.
3. **DISCRETE, MIXED AND STRUCTURED VARIABLES.** pymoo documents binary, discrete,
   permutation, mixed and custom variable types with a TSP example; Tanabe & Ishibuchi
   built 4 of their 16 RE problems as mixed-integer specifically because "there are only
   a few (multi-objective) mixed-integer optimization problems for benchmarking." [V]
   Multi-objective mixed-integer nonlinear programming is brutal for exact methods.
4. **A-POSTERIORI PREFERENCE ARTICULATION — the real argument.** Choosing weights BEFORE
   you have seen the front means committing to a trade-off rate you cannot yet evaluate,
   in units you may not understand, with a mapping (weights -> front location) that is
   nonlinear, geometry-dependent, and DISCONTINUOUS across front concavities (§3.1). An
   a-posteriori workflow inverts this: approximate the whole front, THEN let the decision
   maker pick a point by inspecting actual achievable trade-offs. This is why the library
   tooling matters — pymoo ships the a-posteriori decision layer explicitly: **pseudo-
   weights, compromise programming, high trade-off points**, plus visualisation for
   M > 3 (parallel coordinates, Radviz, petal, radar, heatmap). *** NOTE THE HONEST
   CAVEAT from the NSGA-III paper [VFT]: "the third difficulty related to
   **visualization and performance measures** mentioned above **cannot be avoided**" in
   many objectives — a-posteriori articulation gets HARDER exactly where many-objective
   methods are needed. *** (See also Tušar & Filipič, "Visualization of Pareto Front
   Approximations in Evolutionary Multiobjective Optimization: A Critical Review and the
   Prosection Method", IEEE TEVC 19(2):225-245, DOI 10.1109/TEVC.2014.2313407 [bib V].)
5. **HYPERVOLUME GIVES A PRINCIPLED OPTIMISATION TARGET.** Because hypervolume is
   strictly <-monotonic (§3.5), maximising it is a SOUND surrogate for approximating the
   front: SMS-EMOA's Reduce operator PROVABLY never decreases it (S(P_t) <= S(P_{t+1}),
   [VFT]) and converges to a local optimum of the S metric whose points are "well
   distributed." *** Very few metaheuristic design choices come with a guarantee that
   clean. ***
WHERE EMO IS **NOT** THE RIGHT TOOL — state this plainly:
(a) **CONVEX MULTI-OBJECTIVE PROBLEMS WITH AVAILABLE GRADIENTS.** See Section 4.2(b):
    on a convex problem the whole front IS the boundary of conv(Y + R^M_+), so the
    §3.1 objection evaporates, weighted-sum scalarization is COMPLETE (Geoffrion 1968),
    and you should use scalarization + a proper NLP solver with warm-starting along the
    weight path, or Normal-Boundary Intersection for even spacing. Machine-precision
    front points, local optimality certificates, convergence rates — none of which a
    MOEA offers.
(b) **VERY EXPENSIVE EVALUATIONS.** A MOEA needs 10^3-10^5 evaluations (the WFG authors'
    2.5M-evaluation run still showed poor WFG1 coverage). Use multi-objective Bayesian
    optimisation: ParEGO, MOEA/D-EGO, qEHVI, qNEHVI — all detailed in Section 4.3(b),
    with the irony that they optimise exactly the hypervolume indicator used here for
    selection, and inherit the same #P-hardness in M and the same reference-point
    sensitivity.
(c) **HIGH DECISION DIMENSIONALITY** — population methods scale poorly in n, where
    gradient or surrogate methods win. And **MANY OBJECTIVES WITH NO PREFERENCE
    INFORMATION** — at M >~ 10 Pareto dominance is vacuous (94% non-dominated at M=10,
    N=100), the front needs exponentially many points to cover, visualisation fails, and
    the indicators become expensive or meaningless. The NSGA-III authors concede the
    third difficulty "cannot be avoided." At that point the right move is to ELICIT
    PREFERENCES AND REDUCE THE PROBLEM — reference-point/preference-based variants
    (R-NSGA-II, R-NSGA-III, PI-NSGA-II, all in pymoo), objective-reduction analysis, or
    interactive methods.
