PART 4 — FITNESS LANDSCAPES, AND THE FIELD'S RIGOUR PROBLEM
Source-verified research notes for a reference document on evolutionary algorithms
Research conducted 2026-11-11. All fetch dates 2026-11-11 unless stated.
Verification convention: [VERIFIED — <artifact actually read>] / [UNVERIFIED]

## 1. FITNESS LANDSCAPES: THE FORMAL DEFINITION, AND WHY IT MATTERS

## 1.1 The definition

A FITNESS LANDSCAPE is a triple

    L = ( X , N , f )

where
  - X is the search space (the set of candidate solutions / genotypes);
  - N : X → 2^X is a NEIGHBOURHOOD STRUCTURE — for each x ∈ X a set N(x) ⊆ X of
    points reachable from x in one application of the SEARCH OPERATOR
    (equivalently: a graph on X, or a topology/distance on X);
  - f : X → R is the fitness (or cost) function.

Equivalently: the "landscape graph" with vertex set X, edges given by N, and
vertices labelled by f. Where the operator is stochastic, N is replaced by a
transition kernel and the landscape is a weighted graph. Note what this means
concretely: the (1+1) EA with standard bit mutation induces a COMPLETE weighted
graph on {0,1}^n (every point reachable from every point, with weight depending
on Hamming distance), NOT the Hamming hypercube — so the (1+1) EA and a
single-bit-flip hill climber on the same objective function are searching two
different landscapes.

## 1.2 The crucial consequence

*** A LANDSCAPE IS A PROPERTY OF THE OPERATOR, NOT OF THE OBJECTIVE FUNCTION
ALONE. *** Everything anyone says about "the fitness landscape of problem P" is
strictly ill-formed until the operator is named. Concretely:

  - LOCAL OPTIMA ARE OPERATOR-RELATIVE. x is a local optimum iff f(x) >= f(y)
    for all y ∈ N(x). Change N and the set of local optima changes. The number
    of local optima of a TSP instance under 2-opt differs from its number under
    3-opt or Lin–Kernighan; "the number of local optima of this instance" is not
    a well-formed quantity.
  - RUGGEDNESS, SMOOTHNESS, MODALITY, BASIN STRUCTURE, PLATEAUS — all
    operator-relative, for the same reason.
  - UNIMODAL DOES NOT IMPLY EASY. Long k-path functions (Part 3 §3.4) are
    unimodal with respect to the 1-bit-flip neighbourhood and still require
    superpolynomial time for a 1-bit-flip hill climber, while being polynomial
    for the (1+1) EA, whose operator induces a different landscape. The cleanest
    demonstration that landscape and objective are different objects.
  - THE BUILDING-BLOCK CRITIQUE IS THE SAME POINT. "Short, low-order schemata"
    are short and low-order with respect to a particular ordering of loci and a
    particular crossover operator. Scramble the encoding: the objective function
    is unchanged, the optima are unchanged, and the building blocks vanish.
    (Part 1 §4.2.)
  - AND IT UNDERLIES THE NFL ESCAPE. Igel & Toussaint's Theorem 5 — "a
    non-trivial neighborhood relation on X is not invariant under permutations
    of X" [VERIFIED verbatim; see Part 2 §5.5] — says exactly that permuting X
    destroys the landscape while preserving the function. NFL averages over the
    function; practice exploits the landscape. The whole of Part 2 is a corollary
    of §1.2.

The canonical EC formalisation is usually attributed to Stadler ("Landscapes and
their correlation functions", *Journal of Mathematical Chemistry* 20:1–45, 1996
[UNVERIFIED]) and to Terry Jones ("Evolutionary algorithms, fitness landscapes
and search", PhD thesis, University of New Mexico, 1995 [UNVERIFIED]), who
stated the operator-dependence point most forcefully: there is one landscape PER
OPERATOR, so a GA with both mutation and crossover searches two landscapes
simultaneously, and there is no single object to analyse.

Biological origin: Sewall Wright, "The roles of mutation, inbreeding,
crossbreeding and selection in evolution", *Proceedings of the Sixth
International Congress of Genetics* 1:356–366, 1932 — the "adaptive landscape".
[UNVERIFIED metadata.]

## 2. DECEPTION

## 2.1 The minimal deceptive problem

Goldberg's MINIMAL DECEPTIVE PROBLEM (MDP) is the smallest instance exhibiting
schema-theoretic deception: a function on 2 bits (4 points) with fitnesses
assigned so that the global optimum is at 11 while the order-1 schema averages
favour 0 at both positions:

    f(0*) > f(1*)   and   f(*0) > f(*1),   but   f(11) = max.

Canonically f(11) > f(00) > f(01) >= f(10) ("type I") or f(00) > f(01) ("type
II"), subject to the order-1 averages pointing away from 11. A GA reading only
low-order schema averages is led to 00. It is "minimal" because no 1-bit problem
can be deceptive.

  David E. Goldberg, "Simple genetic algorithms and the minimal deceptive
  problem", in L. Davis (ed.), *Genetic Algorithms and Simulated Annealing*,
  Morgan Kaufmann, 1987, pp. 74–88. [UNVERIFIED metadata.] Developed in Goldberg
  1989 [UNVERIFIED — I could not reach Goldberg 1989; see Part 1 §4.1].

## 2.2 Trap functions

A TRAP generalises the MDP to n bits: fitness increases toward one attractor
(usually 0^n) over most of the space while the global optimum sits at the
opposite corner (1^n). The standard parameterised form, with u(x) = the number
of 1-bits:

    TRAP(x) = { (a/z)·(z − u(x))         if u(x) <= z
              { (b/(n − z))·(u(x) − z)   if u(x) > z

with b > a, where z is the slope-change location, a the local optimum's fitness
at u = 0 and b the global optimum's at u = n. Variants: the FULLY DECEPTIVE
trap (every schema average of every order below n points to the local optimum)
and CONCATENATED k-TRAPS (a sum of m independent k-bit traps — the standard hard
benchmark for EDAs and linkage-learning GAs, because the sub-traps are
separable but each is internally deceptive).

The (1+1) EA on a trap needs Θ(n^n) expected time (Part 3 §3.3) — WORSE than
exhaustive search's 2^n. Traps are the extremal demonstration that selection can
be actively harmful, not merely unhelpful.

## 2.3 The verdict on deception as a difficulty measure

### NEGATIVE

Grefenstette's "Deception considered harmful" (FOGA 2, 1993 — see
Part 1 §5.1 for the citation and its UNVERIFIED status) argues that deception is
defined in terms of STATIC schema averages the GA never observes, and exhibits
deceptive-but-easy and non-deceptive-but-hard functions. Deception is therefore
neither necessary nor sufficient for GA-hardness. It survives as a useful
CONSTRUCTION technique for hard benchmarks; it is dead as a predictor.

## 3. EPISTASIS AND EPISTASIS VARIANCE

## 3.1 Epistasis, and its clean formalisation

EPISTASIS, borrowed from genetics, is interaction between loci: one gene's
fitness contribution depends on other genes' values. A function on {0,1}^n is
NON-EPISTATIC (separable / linear / additively decomposable) iff
f(x) = Σ_i g_i(x_i); any deviation from additivity is epistasis.

The right formalisation is the WALSH DECOMPOSITION (Bethke 1980; Goldberg 1989):
expand f in the orthonormal basis of Walsh functions ψ_j(x) = (−1)^(j·x) for
j ∈ {0,1}^n,

    f(x) = Σ_j w_j · ψ_j(x) ,

where the ORDER of coefficient w_j is the number of 1-bits in index j. Order 0
is the mean; order 1 captures additive effects; order k >= 2 captures k-way
interactions. f is non-epistatic iff all coefficients of order >= 2 vanish. Every
measure below is an approximation to "how much mass sits in orders >= 2".

[Albert D. Bethke, "Genetic algorithms as function optimizers", PhD thesis,
University of Michigan, 1980. UNVERIFIED metadata.]

## 3.2 The epistasis-variance measures

Both due to Davidor:

  - EPISTASIS VARIANCE. Fit the best additive (first-order) approximation f_lin
    to f by least squares over the search space (or a sample), then set
        epistasis variance = Var( f − f_lin ) ,
    usually normalised by Var(f) to lie in [0,1]. Zero = perfectly additive. In
    Walsh terms it is exactly the fraction of total variance carried by
    coefficients of order >= 2.
  - EPISTASIS CORRELATION. The correlation between f and its additive
    approximation — a monotone transform of the same information.

  Yuval Davidor, "Epistasis variance: A viewpoint on GA-hardness", in
  G. J. E. Rawlins (ed.), *Foundations of Genetic Algorithms (FOGA 1)*, Morgan
  Kaufmann, 1991, pp. 23–35. [UNVERIFIED metadata.]

## 3.3 The honest verdict: UNRELIABLE — with a wording caveat

  Bart Naudts and Leila Kallel, "A comparison of predictive measures of problem
  difficulty in evolutionary algorithms", *IEEE Transactions on Evolutionary
  Computation* 4(1):1–15, April 2000. DOI: 10.1109/4235.843491

*** CITATION VERIFIED *** [Crossref bibliographic search executed 2026-11-11
against https://api.crossref.org/works returns: title "A comparison of
predictive measures of problem difficulty in evolutionary algorithms"; authors
Naudts; Kallel; container-title "IEEE Transactions on Evolutionary Computation";
volume 4; issue 1; pages 1-15; issued 2000-04; DOI 10.1109/4235.843491. Every
bibliographic element confirmed.]

*** THE WORDING: I COULD NOT VERIFY IT — FLAGGED AS YOU ASKED. *** You asked me
to check whether Naudts & Kallel "call them unreliable" and to verify the
wording. I cannot. I queried the Crossref record directly and the ABSTRACT FIELD
IS ABSENT (the API returns no abstract for this DOI), and IEEE Xplore returns 403
to automated fetches, so I did not reach a single sentence of the paper.
[UNVERIFIED]

What I believe the paper contains, stated as my own knowledge and flagged
[UNVERIFIED]: Naudts & Kallel survey the predictive difficulty measures of the
1990s — epistasis variance, epistasis correlation, fitness-distance correlation,
the "sitewise optimisation" measure, and others — and systematically construct
COUNTEREXAMPLES: functions with low epistasis variance that are hard for an EA,
and functions with high epistasis variance that are easy. Their conclusion is
that these measures are not reliable predictors of EA performance, and more
generally that the single-number-difficulty-predictor programme is misconceived
because any such measure can be defeated by construction.

*** RECOMMENDATION: do NOT put "unreliable" in quotation marks and attribute it
to Naudts & Kallel on my authority. Write the verdict in your own words —
"Naudts & Kallel's systematic comparison found these measures to be unreliable
predictors of EA difficulty, defeating each with explicit counterexamples" — and
check the paper if you want a quotation. ***

The structural reason the programme fails does NOT depend on the citation, and
you can state it safely: a difficulty measure that is a function of f ALONE
cannot predict the difficulty of a LANDSCAPE, because difficulty is a property of
(X, N, f) and not of f (§1.2). Epistasis variance is computed from f with no
reference to any operator. It is therefore in exactly the same position as
deception (§2.3) and FDC (§5): a statistic about the objective function being
asked to predict a property of an algorithm–landscape pair. Three independent
attempts, three refutations by construction; the PATTERN is the real finding.

## 4. RUGGEDNESS: AUTOCORRELATION AND CORRELATION LENGTH

## 4.1 The random-walk autocorrelation function

RUGGEDNESS is operationalised via the autocorrelation of fitness along a RANDOM
WALK on the landscape graph. Take a simple random walk (x_0, x_1, ...) on (X, N),
record f(x_t), and define the autocorrelation at lag s:

    r(s) = [ E_t( f(x_t)·f(x_{t+s}) ) − E_t f(x_t) · E_t f(x_{t+s}) ] / Var(f)

estimated from a walk of length m by

    r̂(s) = Σ_{t=1}^{m−s} (f(x_t) − f̄)(f(x_{t+s}) − f̄) / Σ_{t=1}^{m} (f(x_t) − f̄)²

Smooth landscape: r(s) decays slowly. Rugged: fast. Maximally rugged (random):
r(s) ≈ 0 for all s >= 1. Note this is explicitly a measure of the LANDSCAPE, not
of f — the walk is taken on N. Contrast §§3 and 5.

## 4.2 Correlation length

For landscapes that are (approximately) ISOTROPIC / ELEMENTARY, r(s) decays
geometrically, r(s) ≈ r(1)^s, and ruggedness is summarised by one number, the
CORRELATION LENGTH:

    ℓ = − 1 / ln( r(1) )     (Stadler)    or    ℓ = 1 / ( 1 − r(1) )   (Weinberger)

[The two agree to leading order as r(1) → 1 and both appear in print, so SAY
WHICH YOU USE.] Large ℓ = smooth; ℓ near 1 = rugged. Interpretation: ℓ is the
distance over which fitness information stays useful, so local search should take
steps comparable to ℓ, and a landscape whose ℓ is far below the search-space
diameter has many effectively independent basins.

Primary sources [both UNVERIFIED metadata — I reached neither]:
  - Edward D. Weinberger, "Correlated and uncorrelated fitness landscapes and
    how to tell the difference", *Biological Cybernetics* 63(5):325–336, 1990.
  - Peter F. Stadler, "Landscapes and their correlation functions", *Journal of
    Mathematical Chemistry* 20:1–45, 1996. Stadler's deeper contribution is the
    SPECTRAL theory: on a regular graph a landscape's autocorrelation is
    determined by the decomposition of f into graph-Laplacian eigenvectors, and
    an ELEMENTARY landscape is one whose f is (up to a constant) a single
    eigenvector. For elementary landscapes r(s) is EXACTLY geometric, and many
    classical combinatorial landscapes (symmetric TSP under 2-opt, graph
    colouring) are elementary or nearly so — which makes correlation length
    principled rather than merely heuristic.

Caveat worth printing: correlation length is an AVERAGE over a random walk, so it
is blind to heterogeneity — a landscape smooth in one region and rugged in
another has a correlation length describing neither. Same averaging failure that
defeats FDC (§5.3).

## 5. FITNESS-DISTANCE CORRELATION

## 5.1 The measure

  Terry Jones and Stephanie Forrest, "Fitness distance correlation as a measure
  of problem difficulty for genetic algorithms", in *Proceedings of the Sixth
  International Conference on Genetic Algorithms (ICGA-95)*, Morgan Kaufmann,
  1995, pp. 184–192. [UNVERIFIED metadata — ICGA-95 is not in Crossref and I did
  not reach a copy. Authors, title, venue and year are from my own knowledge; the
  PAGE RANGE should be checked.]

FDC is the sample correlation between a point's fitness and its distance to the
nearest global optimum. For a sample of N points with fitnesses f_i and
distances d_i:

    FDC = Cov(f, d) / (σ_f · σ_d)
        = [ (1/N) Σ_i (f_i − f̄)(d_i − d̄) ] / (σ_f · σ_d)

For MAXIMISATION, a useful landscape has fitness rising as distance to the
optimum falls, i.e. FDC close to −1.

## 5.2 The conventional thresholds

The classification Jones & Forrest proposed, which became conventional:

  - FDC <= −0.15        : "STRAIGHTFORWARD" — fitness guides search toward the
                          optimum.
  - −0.15 < FDC < 0.15  : "DIFFICULT" — essentially no correlation; fitness
                          gives no guidance.
  - FDC >= 0.15         : "MISLEADING" / deceptive — fitness increases with
                          distance FROM the optimum, so it actively misleads.

[UNVERIFIED — the ±0.15 thresholds are the figures universally reported as
Jones & Forrest's and I am confident in them, but I did not reach the paper.
Note that signs flip in sources treating the problem as minimisation, and some
papers use the opposite sign convention outright. STATE YOUR CONVENTION.]

Jones & Forrest also introduced the FITNESS-DISTANCE SCATTER PLOT as the primary
diagnostic, with the coefficient as a summary — worth preserving, since the
coefficient alone discards the structure the plot reveals. [UNVERIFIED]

## 5.3 The counterexample: Altenberg 1997

  Lee Altenberg, "Fitness distance correlation analysis: An instructive
  counterexample", in *Proceedings of the Seventh International Conference on
  Genetic Algorithms (ICGA-97)*, Morgan Kaufmann, 1997, pp. 57–64.

[UNVERIFIED metadata — ICGA-97 is not in Crossref and I did not reach a copy.
Title and author are from my own knowledge. IMPORTANT NEGATIVE RESULT FROM MY
SEARCH: a Crossref bibliographic search for this title (executed 2026-11-11)
returned only LATER, DIFFERENT counterexample papers — namely Vanneschi,
Tomassini, Collard & Clergue, "Fitness distance correlation in genetic
programming: a constructive counterexample", *CEC 2003*, pp. 289–296 Vol. 1,
DOI 10.1109/cec.2003.1299587 (VERIFIED record), and Tomassini, Vanneschi,
Collard & Clergue, "A study of fitness distance correlation as a difficulty
measure in genetic programming", *Evolutionary Computation* 13(2):213–239, 2005,
DOI 10.1162/1063656054088549 (VERIFIED record). These are GP-specific
descendants of Altenberg's argument — useful corroborating citations, but NOT
the Altenberg paper. Do not substitute one for the other.]

*** WHAT THE COUNTEREXAMPLE SHOWS — FLAGGED AS UNVERIFIED. *** I did not reach
the paper and am reporting my understanding. As I understand it, Altenberg
constructs a function on which FDC is "straightforward" by the thresholds above
— strongly negative, so FDC predicts an easy problem — yet which is in fact HARD
for a GA. The mechanism: FDC is a GLOBAL AVERAGE over the whole search space and
is therefore blind to where the search actually goes. A landscape can have an
excellent overall fitness–distance trend while the region the GA is actually
confined to (after selection has concentrated the population) has no useful
gradient, or has a barrier the GA cannot cross. FDC is computed over a uniform
sample; the GA's population is anything but uniform; the two can be arbitrarily
decoupled.

The STRUCTURAL critique does NOT depend on the citation, and you can state all
three parts of it safely in your own voice:

  (a) FDC REQUIRES KNOWING THE OPTIMUM. You must know the global optimum (or all
      of them) to compute d_i. So FDC can never predict the difficulty of a
      problem you have not already solved. It is a post-hoc explanatory
      statistic masquerading as a predictive one.
  (b) FDC IS A LINEAR CORRELATION, so it measures only the linear component of
      the fitness–distance relation and is destroyed by monotone nonlinearity
      that a search algorithm handles perfectly well. Two landscapes with
      identical level sets and identical search behaviour can have very
      different FDC.
  (c) FDC NEEDS A DISTANCE, and it is almost always Hamming distance — the
      neighbourhood of SINGLE-BIT MUTATION, not the neighbourhood of the
      operator actually in use (§1.2). FDC for a GA with uniform crossover,
      computed under Hamming distance, is measuring the wrong landscape.

Same verdict as §2.3 and §3.3.

## 6. NEUTRALITY AND NEUTRAL NETWORKS

## 6.1 The biological root: Kimura's neutral theory

  Motoo Kimura, "Evolutionary rate at the molecular level", *Nature*
  217(5129):624–626, 1968. And: Motoo Kimura, *The Neutral Theory of Molecular
  Evolution*, Cambridge University Press, 1983. [BOTH UNVERIFIED metadata.]

Kimura's claim: most molecular-level evolutionary change is driven not by
positive selection but by random DRIFT of mutations that are selectively NEUTRAL
(or nearly so). The rate of neutral substitution equals the neutral mutation rate
and is independent of population size — the "molecular clock".

The transplant into EC: large regions of genotype space can map to identical
fitness, and a population can move freely through them by drift. So "no fitness
improvement" does not mean "no progress": genotypic change without phenotypic
change is the mechanism by which a population relocates to a part of the space
from which a NEW improvement becomes accessible. This reframes stagnation as
possible positioning.

## 6.2 Neutral networks in RNA landscapes

  Martijn A. Huynen, Peter F. Stadler and Walter Fontana, "Smoothness within
  ruggedness: The role of neutrality in adaptation", *Proceedings of the
  National Academy of Sciences USA* 93(1):397–401, 1996.
  Peter Schuster, Walter Fontana, Peter F. Stadler and Ivo L. Hofacker, "From
  sequences to shapes and back: A case study in RNA secondary structures",
  *Proceedings of the Royal Society B* 255(1344):279–284, 1994.
  [BOTH UNVERIFIED metadata — I did not reach either paper.]

The findings that matter for EC [UNVERIFIED]:
  - The genotype→phenotype map (RNA sequence → secondary structure) is massively
    REDUNDANT: vastly more sequences than structures.
  - The set of sequences folding to a given structure forms a NEUTRAL NETWORK —
    a connected (or nearly connected) subgraph of sequence space, typically
    PERCOLATING through the whole space rather than forming a local blob.
  - Neutral networks of different structures are INTERTWINED: from almost any
    point on one network, a small number of mutations reaches a point on many
    other networks ("shape space covering"). So a population drifting on a
    neutral network has continual access to new phenotypes.
  - Hence the Huynen/Stadler/Fontana title, which is the slogan of the whole
    area: "SMOOTHNESS WITHIN RUGGEDNESS". A landscape that looks rugged in its
    fitness values can be navigable because of neutral connectivity.

## 6.3 Barnett: the NKp model and the netcrawler

  Lionel Barnett, "Ruggedness and neutrality — the NKp family of fitness
  landscapes", in *Proceedings of the Sixth International Conference on
  Artificial Life (ALIFE VI)*, MIT Press, 1998, pp. 18–27. [UNVERIFIED]
  Lionel Barnett, "Netcrawling — optimal evolutionary search with neutral
  networks", in *Proceedings of the 2001 Congress on Evolutionary Computation
  (CEC 2001)*, IEEE, pp. 30–37. [UNVERIFIED]
  (Also his DPhil thesis, University of Sussex, 2003. [UNVERIFIED])

THE NKp MODEL [UNVERIFIED]: Kauffman's NK landscape (§7) with TUNABLE NEUTRALITY
added alongside NK's tunable ruggedness. In standard NK each contribution-table
entry is drawn uniformly from [0,1). In NKp, each entry is independently set to
ZERO with probability p and drawn from [0,1) otherwise; zeroed contributions make
many configurations fitness-equivalent at that locus, creating neutrality. p = 0
recovers standard NK; p → 1 gives maximal neutrality. The key property: p tunes
NEUTRALITY while K independently tunes RUGGEDNESS, so the two vary ORTHOGONALLY —
exactly what is needed to test claims about neutrality's effect without
confounding them with ruggedness.

THE NETCRAWLER [UNVERIFIED]: a mutation-only hill climber that ACCEPTS NEUTRAL
MOVES and so performs a random walk along the current neutral network, taking an
improving move whenever one appears. The analytical point: the OPTIMAL MUTATION
RATE for a netcrawler is substantially HIGHER than for a standard hill climber,
because on a neutral network there is no gradient to follow and all that matters
is the rate at which you encounter portals to higher-fitness networks — so you
want to move fast. Barnett shows the netcrawler outperforming both a standard
hill climber and a conventional EA on NKp landscapes with substantial neutrality.

[Note the structural kinship with the (1+1) EA's ties-accepted convention
(Part 3 §1) and with Jansen & Wegener's plateau results (Part 3 §3.5): accepting
equal-fitness offspring is what turns stagnation into a productive random walk.
The netcrawler is the deliberate, tuned version of the same idea — and
Jansen & Wegener's result that REJECTING equal-fitness strings is sometimes
provably better is its counterweight. Both are true; which applies depends on
whether the plateau is a neutral network with portals or a trap.]

## 6.4 Related EC work on neutrality

Names only, UNVERIFIED unless marked: Ebner, Shackleton and Shipman on redundant
representations; Yu and Miller on neutrality in Cartesian Genetic Programming
(where neutral "inactive" genes are a designed feature, not an accident);
Vassilev and Miller on neutrality in digital-circuit evolution landscapes. And:

  Riccardo Poli and Edgar Galván-López, "On the effects of bit-wise neutrality on
  fitness distance correlation, phenotypic mutation rates and problem hardness",
  *FOGA 2007*, LNCS, pp. 138–164, DOI 10.1007/978-3-540-73482-6_9. [VERIFIED
  record — returned by my Crossref search, 2026-11-11, with those authors, title,
  page range and DOI.] Useful because it connects §5 and §6 directly: adding
  neutrality changes FDC without changing the underlying problem — another
  refutation of FDC, by a different route.

## 7. NK LANDSCAPES

## 7.1 Kauffman's formulation, exactly

  Stuart A. Kauffman and Simon Levin, "Towards a general theory of adaptive
  walks on rugged fitness landscapes", *Journal of Theoretical Biology*
  128(1):11–45, 1987. And: Stuart A. Kauffman, *The Origins of Order:
  Self-Organization and Selection in Evolution*, Oxford University Press, 1993.
  [BOTH UNVERIFIED metadata.]

A genotype is x = (x_1, ..., x_N) ∈ {0,1}^N. Two parameters:
  - N : number of loci (string length).
  - K : the number of OTHER loci on which each locus's fitness contribution
        depends, 0 <= K <= N − 1. This is the TUNABLE EPISTASIS knob.

For each locus i fix a set of K epistatic partners Π(i) ⊆ {1..N} \ {i} with
|Π(i)| = K. Two standard choices, and the distinction MATTERS (§7.2):
  - ADJACENT-NEIGHBOURS model: Π(i) = the K loci nearest i on a ring.
  - RANDOM-NEIGHBOURS model: Π(i) drawn uniformly at random.

For each locus i define a fitness-contribution function

    f_i : {0,1}^(K+1) → [0, 1)

by drawing each of its 2^(K+1) table entries INDEPENDENTLY AND UNIFORMLY from
[0,1) — one entry per joint configuration of x_i together with x_{Π(i)}. The
total fitness is the AVERAGE of contributions:

    F(x)  =  (1/N) · Σ_{i=1}^{N} f_i ( x_i , x_{Π(i)} )

PROPERTIES — the point of the model:
  - K = 0 : each f_i depends only on x_i, so F is ADDITIVE. Exactly one local
    optimum (= the global one, found by setting each locus independently);
    adaptive walks have expected length N/2. The smooth extreme, like OneMax.
  - K = N − 1 : every locus depends on every other, so the 2^N fitness values are
    effectively independent uniform draws — MAXIMALLY RUGGED. Expected number of
    local optima 2^N/(N+1); expected adaptive-walk length ≈ ln N. Kauffman's
    "COMPLEXITY CATASTROPHE": as K grows, local optima proliferate AND their
    fitness regresses to the mean, so a highly epistatic system cannot be
    improved by local adaptation.
  - INTERMEDIATE K : tunably rugged — the single knob that made NK the standard
    test bed.
  - Autocorrelation (§4) under the single-bit neighbourhood is approximately
    r(s) = (1 − (K+1)/N)^s, giving ℓ ≈ N/(K+1). [UNVERIFIED but standard, and a
    nice consistency check: K = 0 gives ℓ = N, K = N−1 gives ℓ = 1.]

## 7.2 The complexity result — *** TWO CORRECTIONS / FLAGS ***

  "The computational complexity of N-K fitness functions", *IEEE Transactions on
  Evolutionary Computation* 4(4):373–379, 2000. DOI: 10.1109/4235.887236

*** BIBLIOGRAPHIC RECORD VERIFIED *** [Crossref bibliographic search executed
2026-11-11 against https://api.crossref.org/works returns: title "The
computational complexity of N-K fitness functions"; container-title "IEEE
Transactions on Evolutionary Computation"; volume 4; issue 4; pages 373-379;
issued 2000; DOI 10.1109/4235.887236. YOUR VOLUME, ISSUE, PAGES AND YEAR ARE
EXACTLY RIGHT.]

*** WARNING — DOI CONFUSION IN THIS ISSUE. *** 10.1109/4235.887234 (one digit
different, same issue) is a DIFFERENT paper: Freisleben & Merz on QAP landscapes
(see §8.1). I verified both records separately. This is almost certainly how
these two get swapped in bibliographies; sanity-check your reference list.

*** THE AUTHOR ORDER: I COULD NOT RESOLVE IT, AND YOU SHOULD CHECK BY HAND. ***
Crossref returns the author list in the order **Jian Zhang; Thompson; Wright**
— i.e. ZHANG FIRST. You gave it as "Wright, Thompson & Zhang / Zhang", and my
own recollection is that the paper is by **Alden H. Wright, Richard K. Thompson
and Jian Zhang** — i.e. WRIGHT FIRST. I could not settle it: IEEE Xplore returns
403 to automated fetches, and Semantic Scholar's API returned HTTP 429
(rate-limited) on every attempt I made. Crossref's author ORDERING for legacy
IEEE records of this vintage is known to be unreliable, which is why I am not
simply deferring to it.
*** ACTION: open the IEEE Xplore page for DOI 10.1109/4235.887236 and read the
byline before printing the author list. My best guess remains Wright, Thompson &
Zhang, but it is a guess, and the one hard datum I hold says otherwise. ***

*** THE K THRESHOLD: UNVERIFIED — BUT YOUR CORRECTION IS THE ONE I'D BET ON. ***
You stated that NK optimisation is NP-complete for K >= 2, not K >= 3. I could
not verify this; I did not reach the paper's abstract or text. What I can report:
  - The result's standard form as I understand it: finding a global optimum of an
    NK landscape is NP-COMPLETE for the RANDOM-NEIGHBOURS model with K >= 2,
    while it is solvable in POLYNOMIAL TIME for the ADJACENT-NEIGHBOURS model
    for ANY CONSTANT K (by dynamic programming along the ring, since the
    interaction graph then has bounded pathwidth), and trivially for K = 0 and
    K = 1 in either model.
  - *** THE NEIGHBOURHOOD-MODEL DISTINCTION IS AT LEAST AS IMPORTANT AS THE EXACT
    THRESHOLD. *** "NK optimisation is NP-complete" is FALSE without specifying
    the neighbourhood model, because the adjacent model is tractable for every
    constant K. Any statement of the result that omits the model is wrong.
  - So the claim to print is: NP-complete for K >= 2 in the RANDOM-NEIGHBOURS
    model; polynomial for the ADJACENT-NEIGHBOURS model for any constant K.
    [BOTH PARTS UNVERIFIED. Verify against the paper.]

## 7.3 Why NK landscapes remain useful

Despite being artificial, NK landscapes are the one landscape family in which
ruggedness is a KNOB rather than an observation — which makes them the only
setting where "does ruggedness cause difficulty?" can be asked as a CONTROLLED
experiment rather than a correlation study. That is their whole value, and it is
why the descendants matter: NKp for neutrality (§6.3), NKq for discretised
fitness values, and MAX-k-SAT as the structured, real-problem relative.

## 8. BIG VALLEYS, FUNNELS, AND LOCAL OPTIMA NETWORKS

## 8.1 The big-valley hypothesis

Empirical observation, originally from the TSP: in many combinatorial landscapes
the LOCAL OPTIMA are not scattered independently but are themselves organised
into a globally convex "BIG VALLEY" — better local optima tend to lie closer (in
solution-space distance) to the global optimum and to each other. The
fitness-distance scatter plot OF THE LOCAL OPTIMA shows a clear trend even when
the raw landscape is rugged.

  Kenneth D. Boese, Andrew B. Kahng and Sudhakar Muddu, "A new adaptive
  multi-start technique for combinatorial global optimizations", *Operations
  Research Letters* 16(2):101–113, 1994. [UNVERIFIED metadata.]

  The companion QAP result: Bernd Freisleben and Peter Merz, "Fitness landscape
  analysis and memetic algorithms for the quadratic assignment problem", *IEEE
  Transactions on Evolutionary Computation* 4(4):337–352, 2000.
  DOI: 10.1109/4235.887234. [VERIFIED RECORD — retrieved from
  https://api.crossref.org/works/10.1109/4235.887234, 2026-11-11, confirming
  every field. Content UNVERIFIED.] Its reported finding [UNVERIFIED]: QAP
  landscapes show much WEAKER big-valley structure than TSP landscapes, which is
  why memetic algorithms need different diversification there.

### WHY IT MATTERS

the big valley is the structural property that justifies iterated
local search, memetic algorithms and path-relinking — i.e. searching in the SPACE
OF LOCAL OPTIMA rather than the space of solutions. If local optima form a big
valley, a search that hops between them has a gradient to follow. If not, the
whole family of methods loses its rationale.

## 8.2 Funnels

Later work showed the big-valley picture is too simple for many instances, which
instead have MULTIPLE FUNNELS — several distinct clusters of local optima, each
internally big-valley-like, separated by barriers that local-optima-hopping
cannot cross. A multi-funnel landscape defeats iterated local search in a way a
single big valley does not, and the NUMBER OF FUNNELS is a far better difficulty
predictor than any single-number statistic in §§3–5 — precisely because it is a
structural property of the OPERATOR-INDUCED landscape rather than an average over
the objective function.

  [Principally Ochoa, Veerapen, Whitley and Hains — e.g. Ochoa, Veerapen,
  Whitley & Burke, "The multi-funnel structure of TSP fitness landscapes: A
  visual exploration", *Artificial Evolution (EA 2015)*, LNCS 9554:1–13, 2015;
  and Hains, Whitley & Howe, "Revisiting the big valley search space structure in
  the TSP", *Journal of the Operational Research Society* 62(2):305–312, 2011.
  BOTH UNVERIFIED metadata.] The term is borrowed from the protein-folding
  energy-landscape literature (Frauenfelder; Wolynes; Onuchic).

## 8.3 Local optima networks (LONs)

  Gabriela Ochoa, Marco Tomassini, Sébastien Vérel and Christian Darabos, "A
  study of NK landscapes' basins and local optima networks", in *Proceedings of
  the 10th Annual Conference on Genetic and Evolutionary Computation (GECCO
  2008)*, ACM, pp. 555–562. [UNVERIFIED metadata.]
  Sébastien Vérel, Gabriela Ochoa and Marco Tomassini, "Local optima networks of
  NK landscapes with neutrality", *IEEE Transactions on Evolutionary
  Computation* 15(6):783–797, 2011. [UNVERIFIED metadata.]

THE CONSTRUCTION — I state this with confidence as a definition:
  - NODES: the LOCAL OPTIMA of the landscape under a given local search operator
    — one node per local optimum, or (in the neutral version) one node per
    PLATEAU / neutral network of local optima, giving "compressed" LONs.
  - EDGES: weighted and directed, encoding transitions between basins. Two
    standard definitions:
      * BASIN-TRANSITION edges: w_ij = the probability that a mutation applied
        to a solution in basin i yields a solution in basin j (summed over the
        basin), giving a weighted complete digraph.
      * ESCAPE / "D-escape" edges: i → j exists iff a perturbation of strength
        at most D applied to local optimum i, followed by local search, lands in
        j. Sparser and more interpretable; used in most later work.
  - The result is a weighted directed graph that COMPRESSES the landscape to the
    scale at which a local-search-based metaheuristic actually operates.

*** AND THIS IS THE METHODOLOGICAL POINT OF THE WHOLE SECTION. *** The LON is
defined RELATIVE TO a specific local search and a specific perturbation
operator. It is therefore HONEST about being operator-relative, in a way that
epistasis variance (§3), correlation length (§4) and FDC (§5) are not. That is
why LON statistics — clustering coefficient, assortativity, average path length
to the global optimum, out-degree distribution, modularity/community structure
(which is where funnels come from, §8.2) — turn out to predict metaheuristic
performance far better than the earlier one-number measures. The lesson is not
"network science is powerful"; it is that §1.2 was the whole problem all along,
and the measures that respect it work while the measures that ignore it fail.

## 9. THE FIELD'S RIGOUR PROBLEM

## 9.1 Why EAs are genuinely hard to analyse

Before any accusation of laziness, the honest technical reasons:

  (a) STOCHASTIC IN SEVERAL PLACES AT ONCE: initialisation, mutation, crossover
      point selection, parent selection, sometimes survivor selection. The object
      of study is a random process, not a trajectory, so every statement is
      about a distribution. "It found the optimum in 3,000 evaluations" is one
      sample from a heavy-tailed distribution.
  (b) THE POPULATION IS COUPLED. Individuals are not independent: selection makes
      each one's survival depend on all the others' fitnesses, and crossover
      makes each offspring depend on two parents. The state space is the space of
      POPULATIONS — C(N + 2^n − 1, N) states (Part 1 §5.5) — and nothing
      factorises. The single biggest obstacle, and the reason that, in the
      field's own words, verbatim: "since few of these techniques apply
      effortlessly to population-based EAs, MOST TIME-COMPLEXITY RESULTS CONCERN
      SIMPLIFIED EAs, SUCH AS THE (1+1) EA." [VERIFIED verbatim from the abstract
      of Corus, Dang, Eremeev & Lehre, arXiv:1407.7663, retrieved via the arXiv
      API 2026-11-11.]
  (c) NON-MARKOVIAN IN THE USEFUL VARIABLES. The full population IS a Markov
      chain, but it is intractable. Every tractable analysis projects onto a
      low-dimensional summary (number of ones, distance to optimum, best fitness,
      diversity) — and those projections are NOT Markov. The whole
      drift-analysis apparatus (Part 3 §4.2) exists to extract bounds from
      non-Markovian projections via supermartingale arguments, precisely because
      the Markov property is unavailable where you want it.
  (d) THE LANDSCAPE IS OPERATOR-DEPENDENT (§1.2). There is no single "problem
      structure" to analyse: changing the mutation operator changes the object of
      study, and an algorithm with both mutation and crossover searches two
      landscapes at once.
  (e) NO CONVEXITY TO LEAN ON. The whole apparatus of continuous optimisation
      theory — convexity, gradients, Lipschitz constants, duality — is
      unavailable: discrete unstructured space, black-box objective, and the
      algorithm is not a descent method. What remains is combinatorics and
      concentration inequalities, which is why the proofs are long and the
      results narrow.
  (f) THE INTERESTING REGIME IS THE TRANSIENT, NOT THE LIMIT. Convergence theory
      (Part 3 §7) is comparatively easy and nearly vacuous; the useful question
      is the hitting time — a transient property of a non-reversible chain with
      no detailed balance.

These are real difficulties, and they explain why the rigorous results concern
the (1+1) EA on OneMax rather than a real GA on a real problem. They do not
excuse what follows.

## 9.2 The "novel metaheuristic" publication problem

(i) SÖRENSEN: THE METAPHOR EXPOSED

  Kenneth Sörensen, "Metaheuristics—the metaphor exposed", *International
  Transactions in Operational Research* 22(1):3–18, 2015 (online 2013-02-08).
  DOI: 10.1111/itor.12001

*** DOI AND CITATION VERIFIED *** [Crossref API record retrieved at
https://api.crossref.org/works/10.1111/itor.12001, 2026-11-11, confirming every
field above. YOUR DOI IS EXACTLY RIGHT. Note the date discrepancy: Crossref's
"issued" date is the 2013 online-first publication, while the journal issue is
22(1), 2015. The literature cites it as 2015 with this DOI; do the same.]

*** THE ARGUMENT AND A MEMORABLE LINE: VERIFIED FROM THE ABSTRACT. *** You
anticipated Wiley being blocked, and the full text WAS blocked (Wiley returns
403 to automated fetches; I also tried two University of Antwerp repository
preprint locations, which returned HTTP 410 Gone and HTTP 404). But Crossref
stores the complete abstract, which I retrieved verbatim:

  "In recent years, the field of combinatorial optimization has witnessed a TRUE
   TSUNAMI OF 'NOVEL' METAHEURISTIC METHODS, most of them based on a metaphor of
   some natural or man-made process. The behavior of virtually any species of
   insects, the flow of water, musicians playing together — IT SEEMS THAT NO
   IDEA IS TOO FAR-FETCHED TO SERVE AS INSPIRATION TO LAUNCH YET ANOTHER
   METAHEURISTIC. In this paper, we will argue that this line of research is
   THREATENING TO LEAD THE AREA OF METAHEURISTICS AWAY FROM SCIENTIFIC RIGOR. We
   will examine the historical context that gave rise to the increasing use of
   metaphors as INSPIRATION AND JUSTIFICATION for the development of new
   methods, discuss the reasons for the VULNERABILITY of the metaheuristics field
   to this line of research, and point out its FALLACIES. At the same time, truly
   innovative research of high quality is being performed as well. We conclude
   the paper by discussing some of the properties of this research and by
   pointing out some of the most promising research avenues for the field of
   metaheuristics."

[VERIFIED verbatim — retrieved from the Crossref record's stored abstract for DOI
10.1111/itor.12001, 2026-11-11. Capitalisation of emphasised phrases is mine;
the words are Sörensen's.]

So the argument has four parts in his own terms: (1) a historical account of how
metaphor came to serve as both INSPIRATION AND JUSTIFICATION; (2) a diagnosis of
why the metaheuristics field in particular is VULNERABLE; (3) identification of
specific FALLACIES; (4) a positive programme. The memorable line is "A TRUE
TSUNAMI OF 'NOVEL' METAHEURISTIC METHODS", with "no idea is too far-fetched to
serve as inspiration to launch yet another metaheuristic" as runner-up. The
sharpest claim, and the one to quote, is that this line of research "is
threatening to lead the area of metaheuristics away from scientific rigor."

*** THE ATTRIBUTION WARNING YOU ASKED FOR. *** Sörensen's paper is a field-level,
historical and methodological critique. The HARMONY-SEARCH-IS-A-REBRANDED-
EVOLUTION-STRATEGY identification is NOT HIS — IT IS WEYLAND'S. Do not attribute
it to Sörensen. (Sörensen discusses harmony search as an example; the formal
correspondence and the argument are Weyland's.) See (ii).

(ii) WEYLAND: HARMONY SEARCH IS A SPECIAL CASE OF EVOLUTION STRATEGIES

  Dennis Weyland, "A rigorous analysis of the harmony search algorithm: How the
  research community can be misled by a 'novel' methodology", *International
  Journal of Applied Metaheuristic Computing (IJAMC)* 1(2):50–60, April 2010.
  DOI: 10.4018/jamc.2010040104

*** VERIFIED, WITH A TITLE NOTE *** [Crossref bibliographic search executed
2026-11-11 returns: title "A Rigorous Analysis of the Harmony Search Algorithm";
author Dennis Weyland; container-title "International Journal of Applied
Metaheuristic Computing"; volume 1; issue 2; pages 50-60; issued 2010-04-01; DOI
10.4018/jamc.2010040104. Crossref's title string omits the subtitle, but the FULL
title including "How the research community can be misled by a 'novel'
methodology" is confirmed INDEPENDENTLY: the EC Bestiary's recommended-reading
list, whose raw README I read in full on 2026-11-11, gives it as "A rigorous
analysis of the harmony search algorithm: How the research community can be
misled by a 'novel' methodology" linked to exactly that DOI. There is also a
book-chapter reprint: Weyland, "A Rigorous Analysis of the Harmony Search
Algorithm", in *Modeling, Analysis, and Applications in Metaheuristic
Computing*, IGI Global, pp. 72–83, DOI 10.4018/978-1-4666-0270-0.ch005 —
VERIFIED record from the same search.]

*** THE CORE CLAIM: VERIFIED FROM THE ABSTRACT, VERBATIM. ***

  "In recent years a lot of novel (mostly naturally inspired) search heuristics
   have been proposed. Among those approaches is Harmony Search. After its
   introduction in 2000, positive results and improvements over existing
   approaches have been reported. In this paper, the authors give a review of the
   developments of Harmony Search during the past decade and perform a rigorous
   analysis of this approach. This paper compares Harmony Search to the
   well-known search heuristic called Evolution Strategies. HARMONY SEARCH IS A
   SPECIAL CASE OF EVOLUTION STRATEGIES in which the authors give compelling
   evidence for the thesis that RESEARCH IN HARMONY IS FUNDAMENTALLY MISGUIDED.
   The overarching question is HOW SUCH A METHOD COULD BE INACCURATELY PORTRAYED
   AS A SIGNIFICANT INNOVATION WITHOUT CONFRONTING A RESPECTABLE CHALLENGE OF ITS
   CONTENT OR CREDENTIALS. The authors examine possible answers to this question,
   and implications for evaluating other procedures by disclosing the way in
   which LIMITATIONS OF THE METHOD HAVE BEEN SYSTEMATICALLY OVERLOOKED."

[VERIFIED verbatim — retrieved from the Crossref record's stored abstract for DOI
10.4018/jamc.2010040104, 2026-11-11. Emphasis mine; the words are Weyland's. The
abstract's slightly garbled syntax ("research in Harmony is fundamentally
misguided") is as published.]

*** THE FORMAL PARAMETER CORRESPONDENCE: PARTIALLY UNVERIFIED — FLAGGED. *** You
asked for "the formal parameter correspondence he establishes". VERIFIED is the
headline: "HARMONY SEARCH IS A SPECIAL CASE OF EVOLUTION STRATEGIES". What I
could NOT verify is the specific identification with the **(μ+1) EVOLUTION
STRATEGY** and the term-by-term mapping of harmony-search parameters (Harmony
Memory Size HMS, Harmony Memory Considering Rate HMCR, Pitch Adjusting Rate PAR,
bandwidth bw) onto ES parameters: IGI Global's full text is paywalled and I did
not reach it. My understanding, ALL UNVERIFIED:

  - The "harmony memory" of HMS solution vectors IS a population of size
    μ = HMS; one new solution per iteration means λ = 1; replacing the WORST
    memory member if better is PLUS-SELECTION — hence a (μ+1) strategy.
  - Each coordinate of the new solution is, with probability HMCR, copied from a
    randomly chosen memory member (= DISCRETE/UNIFORM multi-parent
    RECOMBINATION) and otherwise sampled uniformly from its domain (= a large
    mutation); if copied, with probability PAR it is perturbed within bandwidth
    bw (= MUTATION with step size bw).
  So: Harmony Search = a (μ+1) ES with μ = HMS, per-coordinate discrete
  multi-parent recombination at rate HMCR, uniform re-initialisation at rate
  (1 − HMCR), and mutation of step size bw applied with probability PAR.

*** [THE ENTIRE MAPPING ABOVE IS MY RECONSTRUCTION AND IS UNVERIFIED. The (μ+1)
designation in particular — the thing you flagged as needing to be got right — I
could NOT confirm in Weyland's own words. Print the verified "special case of
Evolution Strategies" and attribute the detailed correspondence to Weyland only
after checking the paper.] ***

### THE EMPIRICAL REFUTATION AND THE FOLLOW-UP

  Dennis Weyland, "A critical analysis of the harmony search algorithm—How not to
  solve sudoku", *Operations Research Perspectives* 2:97–105, December 2015.
  DOI: 10.1016/j.orp.2015.04.001

*** CITATION VERIFIED, CONTENT NOT *** [Crossref API record retrieved at
https://api.crossref.org/works/10.1016/j.orp.2015.04.001, 2026-11-11. Returns:
title "A critical analysis of the harmony search algorithm—How not to solve
sudoku"; author Dennis Weyland; container-title "Operations Research
Perspectives"; volume 2; pages 97-105; issued 2015-12. The record carries NO
ABSTRACT, and ScienceDirect returned 403 to my automated fetch, so I read none
of the paper.]

Content, from my own knowledge [UNVERIFIED]: a published harmony-search paper
claimed to solve Sudoku puzzles; Weyland shows the method performs WORSE than a
trivial baseline — that a simple random-restart or brute-force approach
dramatically outperforms the reported harmony-search results — and that the
original paper's experimental claims do not withstand examination. The rhetorical
force is in the title. The 2010 paper is the STRUCTURAL half of the refutation
(it is an old algorithm); this is the EMPIRICAL half (and it does not work).
*** FLAG: do not report any specific performance numbers from this paper on my
authority — I have none. ***

(iii) CAMACHO-VILLALÓN, DORIGO & STÜTZLE: INTELLIGENT WATER DROPS

  Christian Leonardo Camacho-Villalón, Marco Dorigo and Thomas Stützle, "The
  intelligent water drops algorithm: why it cannot be considered a novel
  algorithm", *Swarm Intelligence* 13(3–4):173–192, 2019.
  DOI: 10.1007/s11721-019-00165-y

*** VERIFIED *** [Crossref API record retrieved at
https://api.crossref.org/works/10.1007/s11721-019-00165-y, 2026-11-11,
confirming every field above. Your citation is exactly right. The record carries
NO ABSTRACT and I did not reach the full text.]

WHICH EXISTING METHOD IT IS [UNVERIFIED — from my own knowledge; I could not read
the paper's conclusion]: the Intelligent Water Drops (IWD) algorithm, proposed by
Shah-Hosseini, is shown to be a variant of ANT COLONY OPTIMIZATION —
specifically a construction-graph-based constructive metaheuristic in which the
"soil" on an edge plays exactly the role of ACO's pheromone (decreasing where
drops pass, so an inverted pheromone), the "velocity" and soil-removal rules
reproduce ACO's pheromone update, and the drop's probabilistic edge choice
reproduces ACO's random-proportional rule. The authors' conclusion, as I
understand it: IWD introduces no algorithmic component not already present in
ACO, and the water metaphor contributes nothing but new vocabulary.
*** FLAG: VERIFY. I could not read the paper and am reporting the mapping from
memory. ***

(iv) CAMACHO-VILLALÓN, DORIGO & STÜTZLE: THE SIX BESTIAL METAPHORS

  Christian L. Camacho-Villalón, Marco Dorigo and Thomas Stützle, "Exposing the
  grey wolf, moth-flame, whale, firefly, bat, and antlion algorithms: six
  misleading optimization techniques inspired by *bestial* metaphors",
  *International Transactions in Operational Research* 30(6):2945–2971, 2023
  (online 2022-07-26). DOI: 10.1111/itor.13176

*** VERIFIED *** [Crossref API record retrieved at
https://api.crossref.org/works/10.1111/itor.13176, 2026-11-11, confirming every
field above ("bestial" is italicised in the source markup). So: ITOR
30(6):2945–2971, 2022 online / 2023 issue.]

*** THE ABSTRACT: VERIFIED VERBATIM *** [retrieved from the Crossref record,
2026-11-11]:

  "We present a rigorous, COMPONENT-BASED analysis of six widespread
   metaphor-based algorithms for tackling continuous optimization problems. In
   addition to deconstructing the six algorithms into their components and
   relating them with EQUIVALENT COMPONENTS PROPOSED IN WELL-ESTABLISHED
   TECHNIQUES, SUCH AS PARTICLE SWARM OPTIMIZATION AND EVOLUTIONARY ALGORITHMS,
   we analyze the use of the metaphors that inspired these algorithms to
   understand whether their usage has brought any novel and useful concepts to
   the field of metaheuristics. OUR RESULT IS THAT THE IDEAS PROPOSED IN THE SIX
   STUDIED ALGORITHMS HAVE BEEN IN THE LITERATURE OF METAHEURISTICS FOR YEARS AND
   THAT THE ONLY NOVELTY IN THESE SELF-PROCLAIMED *NOVEL* ALGORITHMS IS SIX
   DIFFERENT TERMINOLOGIES DERIVED FROM THE USE OF NEW METAPHORS. We discuss the
   reasons why the metaphors that inspired these algorithms are MISLEADING AND
   ULTIMATELY USELESS as a source of inspiration to design effective optimization
   tools. Finally, we discuss the rationale often presented by the authors of
   metaphor-based algorithms as their motivation to propose more algorithms of
   this type, WHICH IS BASED ON A WRONG UNDERSTANDING OF THE NO-FREE-LUNCH
   THEOREMS FOR OPTIMIZATION."

[VERIFIED verbatim. Emphasis mine; words are the authors'. That final sentence is
the direct textual link back to Part 2 §3 (misreading M2) and is the single best
citation for "NFL is misused as a licence to publish".]

*** WHICH EXISTING METHOD EACH OF THE SIX IS: PARTIALLY UNVERIFIED — FLAGGED. ***
VERIFIED is the COLLECTIVE answer: all six deconstruct into components
"equivalent to" components of PARTICLE SWARM OPTIMIZATION and EVOLUTIONARY
ALGORITHMS, and the "only novelty" is terminology. The PER-ALGORITHM mapping is
not in the abstract and I could not reach the full text — Wiley returns 403, and
both IRIDIA technical-report URLs I tried resolved to the WRONG document (I
fetched TR/IRIDIA/2020-010, which turned out to be Birattari's "Notes on the
Estimation of the Expected Performance of Automatic Methods for the Design of
Control Software for Robot Swarms" — not this paper; my TR-number guess was
wrong). My understanding of the individual findings, ALL UNVERIFIED:

  - GREY WOLF OPTIMIZER (GWO) — a PSO variant: the three "leader" wolves
    (alpha/beta/delta) act as PSO attractors and the position update reduces to a
    PSO-style weighted move toward a combination of best-so-far positions. The
    pack-hierarchy metaphor adds nothing algorithmic.
  - MOTH-FLAME OPTIMIZATION (MFO) — also a PSO-like update toward stored best
    solutions, the "spiral" being a reparameterised attraction term.
  - WHALE OPTIMIZATION ALGORITHM (WOA) — PSO-like: the "bubble-net" spiral is
    again reparameterised attraction to the best-so-far, and "encircling" is
    linear interpolation toward it.
  - FIREFLY ALGORITHM (FA) — a PSO variant with a distance-decayed attraction
    term; "light intensity" is just fitness.
  - BAT ALGORITHM (BA) — explicitly a PSO with velocity and frequency terms; the
    "echolocation" variables map onto PSO's inertia and acceleration
    coefficients.
  - ANTLION OPTIMIZER (ALO) — a random-walk-plus-elitism scheme whose components
    correspond to standard EA mutation and selection.

*** [ALL SIX MAPPINGS UNVERIFIED. They are consistent with the verified abstract
("particle swarm optimization and evolutionary algorithms") and with the field's
general understanding, but I did not read the paper's per-algorithm conclusions.
DO NOT PRINT THE PER-ALGORITHM MAPPINGS AS THE AUTHORS' FINDINGS without
checking. The paper is reportedly available as an IRIDIA technical report —
search iridia.ulb.ac.be for the 2022 TR by Camacho-Villalón.] ***

The same group has a companion paper on cuckoo search, which the EC Bestiary's
reading list cites: "An analysis of why cuckoo search does not bring any novel
ideas to optimization", DOI 10.1007/978-3-030-60376-2_10. [VERIFIED that this
title and DOI appear in the Bestiary README, whose raw text I read in full
2026-11-11; the paper's own metadata is UNVERIFIED.]

(v) ARANHA ET AL.: THE ELEPHANT IN THE ROOM

  Claus Aranha, Christian L. Camacho Villalón, Felipe Campelo, Marco Dorigo,
  Rubén Ruiz, Marc Sevaux, Kenneth Sörensen and Thomas Stützle, "Metaphor-based
  metaheuristics, a call for action: the elephant in the room", *Swarm
  Intelligence* 16(1):1–6, 2022 (online 2021-11-30).
  DOI: 10.1007/s11721-021-00202-9

*** VERIFIED *** [Crossref API record retrieved at
https://api.crossref.org/works/10.1007/s11721-021-00202-9, 2026-11-11,
confirming the title, the full eight-author list in that order, and every other
field above. YOUR CITATION IS EXACTLY RIGHT. The record carries NO ABSTRACT and
I did not reach the full text, so the paper's specific recommendations are
UNVERIFIED.]

*** YOUR NOTE IS CONFIRMED: I found no Natural Computing paper titled "where are
we now? where are we going?", and this is the paper to use. *** It is an
editorial in Swarm Intelligence co-signed by senior figures across the ACO/swarm,
metaheuristics and scheduling communities — note that the author list spans
several journals' editorships, which is what gives it institutional weight: it
is not a critique from outside the field but a position statement by the people
who run its venues. The "elephant in the room" is the volume of metaphor-based
papers the field keeps publishing while declining to discuss it. [Content
UNVERIFIED.]

Worth citing alongside it, and fully verified:

  Felipe Campelo and Claus Aranha, "Lessons from the *Evolutionary Computation
  Bestiary*", *Artificial Life* 29(4):421–432, 2023. DOI: 10.1162/artl_a_00402

*** VERIFIED, ABSTRACT READ VERBATIM *** [Crossref API record retrieved at
https://api.crossref.org/works/10.1162/artl_a_00402, 2026-11-11, giving those
authors, title, journal, volume, issue, pages and year. The stored abstract,
verbatim:]

  "The field of metaheuristics has a long history of finding inspiration in
   natural systems, starting from evolution strategies, genetic algorithms, and
   ant colony optimization in the second half of the 20th century. In the last
   decades, however, the field has experienced AN EXPLOSION OF
   METAPHOR-CENTERED METHODS claiming to be inspired by increasingly absurd
   natural (and even supernatural) phenomena — several different types of birds,
   mammals, fish and invertebrates, soccer and volleyball, reincarnation,
   zombies, and gods. Although metaphors can be powerful inspiration tools, THE
   EMERGENCE OF HUNDREDS OF BARELY DISCERNIBLE ALGORITHMIC VARIANTS UNDER
   DIFFERENT LABELS AND NOMENCLATURES HAS BEEN COUNTERPRODUCTIVE TO THE
   SCIENTIFIC PROGRESS OF THE FIELD, as it NEITHER IMPROVES OUR ABILITY TO
   UNDERSTAND AND SIMULATE BIOLOGICAL SYSTEMS NOR CONTRIBUTES GENERALIZABLE
   KNOWLEDGE OR DESIGN PRINCIPLES FOR GLOBAL OPTIMIZATION APPROACHES. In this
   article we discuss some of the possible causes of this trend, its negative
   consequences for the field, and some efforts aimed at moving the area of
   metaheuristics toward a better balance between inspiration and scientific
   soundness."

This is the best single statement of the TWO-SIDED failure: the metaphor papers
are bad biology AND bad optimisation. Nobody gains.

## 9.3 The Evolutionary Computation Bestiary

  URL: https://github.com/fcampelo/EC-Bestiary
  Zenodo DOI badge present (concept record https://zenodo.org/badge/54759561).
  Maintained by Felipe Campelo and Claus Aranha.

*** FULLY VERIFIED, WITH A CURRENT COUNT. *** [I downloaded the raw README from
https://raw.githubusercontent.com/fcampelo/EC-Bestiary/master/README.md on
2026-11-11 (HTTP 200, 108,448 bytes) and read it in full.]

  - THE README'S OWN DATE STAMP: "Updated 2026-07-01". [VERIFIED verbatim.]

  - *** CURRENT CATALOGUED COUNT: 343 ENTRIES. *** [VERIFIED BY DIRECT COUNT: I
    parsed the README and counted the top-level list items in the A–Z
    "## The Bestiary" section (between the "## The Bestiary" heading and the
    "### Maintainers" heading), each of which is one catalogued method formatted
    as "- **<u>Name</u>**: <citation>". The count is 343. The alphabetically
    first entry is "African Buffalo" (Odili & Kahar 2016, DOI
    10.1155/2016/1510256); the last is "Zombies" (Nguyen & Bhanu, "Zombie
    Survival Optimization: A swarm intelligence algorithm inspired by zombie
    foraging", ICPR 2012). There is at least one entry under every letter of the
    alphabet, including X, Y and Z. NOTE: this is the count as of the README's
    2026-07-01 revision, read 2026-11-11. It grows; re-check before publication
    and state the as-of date.]

  - THE PURPOSE, verbatim from the Introduction [VERIFIED]:
    "The field of meta-heuristic search algorithms has a long history of finding
     inspiration in natural systems. Starting from classics such as Genetic
     Algorithms and Ant Colony Optimization, the last two decades have witnessed
     an explosion of natural (and sometimes supernatural) heuristics - from Birds
     and Bees to Zombies and Reincarnation.
     The goal of the Evolutionary Computation Bestiary is to catalog the,
     ermm... exuberance of the meta-heuristic 'eco-system'. We try to keep a list
     of the many different animals, plants, microbes, natural phenomena and
     supernatural activities that can be spotted in the wild lands of the
     metaphor-based computation literature."

  - THE KEY DISCLAIMER, verbatim [VERIFIED] — quote this, because the Bestiary is
    routinely misrepresented as a blacklist:
    "While we personally believe that the literature could do with MORE
     MATHEMATICS AND LESS MARSUPIALS, and that we, as a community, should grow
     past this metaphor-rich phase in our field's history (A BIT LIKE CHEMISTRY
     OUTGREW ALCHEMY), please note that THIS LIST MAKES NO CLAIMS ABOUT THE
     SCIENTIFIC QUALITY OF THE PAPERS LISTED. The EC Bestiary puts classic and
     well-validated works of the metaheuristics literature (e.g., GAs, ACO) and
     some that describe their methods in mostly metaphor-free language (e.g.,
     JTF, CFO) side by side with others for which the scientific rigor is, to put
     it mildly, lacking. In short, IT IS NOT A HALL OF FAME OF ALGORITHMS - think
     of it more as The island of Doctor Moreau: a place with a few good
     creatures, but which are vastly outnumbered by mindless beasts."
    ("more mathematics and less marsupials" and "a bit like chemistry outgrew
    alchemy" are the two most quotable phrases in this entire literature.)

  - THE EPIGRAPH, verbatim [VERIFIED]: "Till now, madness has been thought a
    small island in an ocean of sanity. I am beginning to suspect that it is not
    an island at all but a continent." — Machado de Assis, *The Psychiatrist*.
    (It also carries a blunt warning telling authors who ask to have their own
    paper added that they are "publicly acknowledging that you have absolutely
    no idea what you're doing with your academic life" — VERIFIED verbatim.)

  - THE README'S OWN RECOMMENDED READING LIST [VERIFIED verbatim — the
    maintainers' own canon, and an independent cross-check on all of §9.2]: it
    opens with Sörensen's "Metaheuristics: The Metaphor Exposed", Aranha et al.
    (DOI 10.1007/s11721-021-00202-9), Campelo & Aranha (DOI 10.1162/artl_a_00402),
    Weyland's harmony-search paper (DOI 10.4018/jamc.2010040104), and the
    six-bestial-metaphors paper (DOI 10.1111/itor.13176) — i.e. exactly the
    papers in §9.2 — then adds "An analysis of why cuckoo search does not bring
    any novel ideas to optimization" (DOI 10.1007/978-3-030-60376-2_10), the
    intelligent-water-drops paper (DOI 10.1007/s11721-019-00165-y), "Analytical
    and numerical comparisons of biogeography-based optimization and genetic
    algorithms" (DOI 10.1016/j.ins.2010.12.006), "How novel is the 'novel' black
    hole optimization approach?" (DOI 10.1016/j.ins.2014.01.026), "Grasshopper
    Optimization Algorithm (GOA): A Novel Algorithm or A Variant of PSO?" (DOI
    10.1007/978-3-031-70932-6_7), and an entry on exposing the chimp optimization
    algorithm (truncated in my read).

## 9.4 Journal policies that resulted

*** FLAGGED CLEARLY, AS YOU ASKED: I COULD NOT REACH THE JOURNAL OF HEURISTICS
POLICY TEXT AND CANNOT QUOTE IT. ***

I tried three routes on 2026-11-11, all failed:
  - https://link.springer.com/journal/10732/submission-guidelines — HTTP 303
    redirect to a Springer identity-provider authorisation endpoint
    (idp.springer.com/authorize?...), i.e. behind a cookie/auth redirect that
    WebFetch will not follow cross-host.
  - https://www.journals.elsevier.com/journal-of-heuristics — HTTP 302 to a
    generic ScienceDirect browse page. (The journal is Springer's, not
    Elsevier's; this URL was my error.)
  - ScienceDirect article pages generally — HTTP 403.

WHAT I BELIEVE THE POLICY SAYS — UNVERIFIED RECOLLECTION, NOT TO BE QUOTED: the
guidelines contain a section headed roughly "Metaphors of nature", whose
substance is (a) the journal does NOT accept papers whose only contribution is a
new metaphor; (b) any proposed method must be described in STANDARD OPTIMISATION
TERMINOLOGY, independent of the metaphor, so it can be compared with existing
methods; (c) novelty must be DEMONSTRATED against the existing literature rather
than asserted via the metaphor.

*** DO NOT PRINT ANY OF THAT AS A QUOTATION. *** Open
https://link.springer.com/journal/10732/submission-guidelines in a browser and
quote the metaphors section directly. It is short, highly quotable, and it is the
best single piece of evidence that the critiques in §9.2 had INSTITUTIONAL rather
than merely rhetorical consequences — worth the manual check.

Other policy responses worth verifying by hand [ALL UNVERIFIED]: *Swarm
Intelligence* (the Aranha et al. editorial, §9.2(v), IS the journal's position
statement, co-signed by its leadership); ACM TELO and *Evolutionary Computation*
have both tightened expectations around baselines and novelty claims; GECCO and
PPSN review forms now ask reviewers explicitly whether a proposed method is
distinguishable from existing methods.

## 9.5 Benchmarking: the constructive response

  Thomas Bartz-Beielstein, Carola Doerr, Daan van den Berg, Jakob Bossek, Sowmya
  Chandrasekaran, Tome Eftimov, Andreas Fischbach, Pascal Kerschke, William La
  Cava, Manuel Lopez-Ibanez, Katherine M. Malan, Jason H. Moore, Boris Naujoks,
  Patryk Orzechowski, Vanessa Volz, Markus Wagner and Thomas Weise,
  "Benchmarking in Optimization: Best Practice and Open Issues",
  arXiv:2007.03488.

*** FULLY VERIFIED *** [arXiv API record retrieved from
https://export.arxiv.org/api/query?id_list=2007.03488, 2026-11-11. Title
"Benchmarking in Optimization: Best Practice and Open Issues"; the complete
SEVENTEEN-author list exactly as given above, in that order; first published
2020-07-07T14:20:26Z. No DOI is registered on the arXiv record, so cite it by
arXiv ID.]

THE ABSTRACT, verbatim [VERIFIED — read in full from the arXiv API response]:

  "This survey compiles ideas and recommendations from more than a dozen
   researchers with different backgrounds and from different institutes around
   the world. Promoting best practice in benchmarking is its main goal. The
   article discusses EIGHT ESSENTIAL TOPICS IN BENCHMARKING: CLEARLY STATED
   GOALS, WELL-SPECIFIED PROBLEMS, SUITABLE ALGORITHMS, ADEQUATE PERFORMANCE
   MEASURES, THOUGHTFUL ANALYSIS, EFFECTIVE AND EFFICIENT DESIGNS,
   COMPREHENSIBLE PRESENTATIONS, AND GUARANTEED REPRODUCIBILITY. The final goal
   is to provide well-accepted guidelines (rules) that might be useful for
   authors and reviewers. As benchmarking in optimization is an active and
   evolving field of research this manuscript is meant to CO-EVOLVE OVER TIME BY
   MEANS OF PERIODIC UPDATES."

Those eight topics are the right checklist to reproduce, because they are the
OPERATIONAL answer to the problem §9.2 diagnoses: the metaphor papers fail at
nearly every one — vague goals, hand-picked problems, no suitable baseline,
performance reported as a mean of thirty runs with no statistics, and no
reproducibility. (Note also "co-evolve over time by means of periodic updates":
cite the arXiv version you actually read, with its version number and date.)

## 9.6 The synthesis

The rigour problem is NOT that EC lacks rigorous results — Part 3 shows it has
excellent ones. It is a TWO-TIER STRUCTURE:

  TIER 1: a small, genuinely rigorous theory community proving tight runtimes for
  simple algorithms on artificial functions, which almost nobody outside it
  reads.
  TIER 2: a very large applied community publishing new metaphors, which almost
  nobody inside Tier 1 reads.

And the gap has a MECHANISM worth naming: because the honest theory cannot yet
reach the algorithms people run (§9.1), a paper proposing a new algorithm cannot
be refuted theoretically; and because benchmarking practice was for a long time
weak (§9.5), it could not easily be refuted empirically either. A metaphor then
functions as a substitute for both — it supplies a NARRATIVE justification where
a proof or a controlled comparison should be. Sörensen's phrase is exact:
metaphor serves as "inspiration AND JUSTIFICATION" [VERIFIED verbatim].

What actually closed the gap, in the three cases where it closed:
  - WEYLAND on harmony search: show the new algorithm IS an old algorithm, by
    exhibiting the parameter correspondence. (§9.2(ii))
  - CAMACHO-VILLALÓN, DORIGO & STÜTZLE: component-based deconstruction — take
    the algorithm apart and name each piece's prior art. (§9.2(iii),(iv))
  - NEUMANN & WITT on ACO, SUDHOLT & WITT on PSO: prove the new algorithm's
    ANALYSIS reduces to the (1+1) EA's, so that — verbatim — "all results for
    (1+1)-EA translate directly into those for the ACO algorithm". [VERIFIED
    verbatim; see Part 3 §8.] This is the strongest form of the argument, and it
    comes from Tier 1.

The common structure: NOVELTY IS A CLAIM ABOUT THE ALGORITHM, NOT ABOUT ITS
METAPHOR, AND IT IS REFUTED BY EXHIBITING A REDUCTION. That is the methodological
lesson, and it is exactly what the Journal of Heuristics policy (§9.4) tries to
institutionalise by requiring metaphor-free descriptions: a method described
without its metaphor can be compared; a method described only through its
metaphor cannot.

### APPENDIX

CORRECTIONS TO THE BRIEF, AND WHAT I COULD NOT VERIFY (ALL 4 PARTS)

### CORRECTIONS TO THE BRIEF AS GIVEN
  - Hwang et al. is *Evolutionary Computation* 26(2):299–345, 2018, DOI
    10.1162/evco_a_00212, and the expansion carries two more terms than
    "+ O(log n)": + (e/2) ln n + c_2 + O(n^(−1) log n). (Part 3 §2.1)
  - Witt 2013 is *Combinatorics, Probability and Computing* 22(2):294–318, DOI
    10.1017/S0963548312000600 — NOT Algorithmica or TCS. (Part 3 §3.2)
  - Sudholt 2017's DOI is 10.1162/evco_a_00171 (your vol/issue/pages were right).
  - Igel & Toussaint 2005's DOI is 10.1007/s10852-005-2586-y (a duplicate
    Kluwer-era DOI 10.1023/b:jmma.0000049381.24625.f7 also exists). (Part 2 §5.1)
  - The NK complexity paper's DOI is 10.1109/4235.887236; 10.1109/4235.887234 is
    a DIFFERENT paper (Freisleben & Merz, QAP landscapes), same issue. (§7.2,§8.1)
  - Camacho-Villalón et al.'s ITOR paper: 30(6):2945–2971, DOI 10.1111/itor.13176.
  - Sörensen's ITOR paper carries a 2013 online-first date against a 2015 issue.
  - EC Bestiary: 343 entries as of its 2026-07-01 revision. (§9.3)
  - ALL THREE ROYAL ROAD FIGURES YOU GAVE (61,334 / 6179 / 256,000) ARE CORRECT
    VERBATIM. But attribute them to Mitchell, Holland & Forrest's own R1
    experiments, NOT to Forrest & Mitchell 1993, which used a variant, R2.
    (Part 1 §6.5)
  - Your notes on Aranha et al. 2022 (and the non-existence of a Natural
    Computing "where are we now?" paper) and on Wright/Vose/Rowe NOT including
    Stephens are both CONFIRMED; the warnings are preserved. (§9.2(v); Pt1 §3.3)

NUMBERS I COULD NOT VERIFY — DO NOT PRINT THESE:
  - The 10^-170 c.u.p. fraction. NOT FOUND in the artifact I read. Use the
    VERIFIED formula instead, or the values derived from it. (Part 2 §5.4)
  - The LeadingOnes leading constant (≈0.859 n²) and optimal rate (≈1.5936/n).
  - Sudholt's golden-ratio mutation rate (≈1.618/n) and the ≈1.19 n ln n runtime.
    The VERIFIED claim is "at least twice as fast [as] the fastest evolutionary
    algorithm using only standard bit mutation". (Part 3 §5.2)
  - Any ES-on-the-sphere convergence or progress rate. SECTION FLAGGED AS A
    RESEARCH TO-DO, not a finding. (Part 3 §7.4)
  - The Journal of Heuristics policy wording. NOT REACHED. (§9.4)

DISPUTED / NEEDS A HUMAN DECISION:
  - NK complexity paper AUTHOR ORDER: Crossref says Zhang, Thompson, Wright; my
    recollection and your brief say Wright, Thompson, Zhang. UNRESOLVED. (§7.2)
  - NK NP-completeness threshold K >= 2 vs K >= 3: unverified — and the
    neighbourhood model (random vs adjacent) matters at least as much. (§7.2)
  - Hwang et al.'s c_1: the arXiv PDF prints a POSITIVE numeral for a manifestly
    NEGATIVE closed-form expression. Resolved in favour of a negative
    n-coefficient of magnitude ≈1.8925 on three internal grounds; check the
    published EC 26(2) version before printing the closed form. (Part 3 §2.1)

CITATION ITSELF UNVERIFIED (one item): Schumacher, Vose & Whitley, "The no free
lunch and problem description length", GECCO 2001 — no Crossref record;
Semantic Scholar's API returned HTTP 429 on every attempt. The RESULT is
verified indirectly via Igel & Toussaint's full text. (Part 2 §6)

TEXT NOT REACHED, SO CONTENT UNVERIFIED (citations mostly sound): Holland 1975;
Goldberg 1989 (the BBH quotations — FLAGGED HARD, Part 1 §4.1); Grefenstette
FOGA 2 1993; Grefenstette & Baker ICGA 1989; Stephens & Waelbroeck 1999;
Wright/Vose/Rowe GECCO 2003; Altenberg FOGA 3 1995; Altenberg ICGA 1997 (the FDC
counterexample); Vose 1999; Nix & Vose 1992; Jones & Forrest ICGA 1995 (the
±0.15 thresholds); Naudts & Kallel 2000 (the "unreliable" wording); Wolpert &
Macready 1997 (the §2 preconditions) and 2005; Droste/Jansen/Wegener 2002 (ANFL's
exact statement); Witt 2013; Jansen & Wegener 2002; Doerr/Doerr/Ebel 2015;
Rudolph 1994; all four reference books (Part 3 §6); Camacho-Villalón et al. 2019
and 2022/23 (the PER-ALGORITHM mappings); Weyland 2010 (the (μ+1)-ES designation
and parameter correspondence) and 2015; Kimura; Huynen/Stadler/Fontana;
Schuster et al.; Barnett (NKp, netcrawler); Kauffman; Stadler; Weinberger;
Boese/Kahng/Muddu; Ochoa/Tomassini/Vérel; Aranha et al. 2022 (content only).
