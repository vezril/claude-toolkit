# Genetic Programming — full reference
Source-verified notes. Fetches 2026-11-11. [V] = verified against an artifact
actually read; [U] = unverified, flagged.

## 1.4 GENETIC PROGRAMMING

- John R. Koza, *Genetic Programming: On the Programming of Computers by Means
  of Natural Selection*, MIT Press, Cambridge MA, 1992, ISBN 0-262-11170-5,
  xiv+819 pp. [V bibliographically via the GP Bibliography, key `koza:book`.]
- Sequels: *Genetic Programming II: Automatic Discovery of Reusable Programs*
  (1994, automatically defined functions/ADFs); Koza, Andre, Bennett III &
  Keane, *Genetic Programming III: Darwinian Invention and Problem Solving*,
  Morgan Kaufmann, April 1999, ISBN 1-55860-543-6, 1100 pp. [V]; Koza, Keane,
  Streeter, Mydlowec, Yu & Lanza, *Genetic Programming IV: Routine
  Human-Competitive Machine Intelligence*, Kluwer, 2003, ISBN 1-4020-7446-8,
  xxviii+591 pp. [V]
- Precursors: Cramer, "A representation for the adaptive generation of simple
  sequential programs", ICGA 1985; Forsyth's BEAGLE; Friedberg 1958.
- The free standard reference: Riccardo Poli, William B. Langdon & Nicholas F.
  McPhee, *A Field Guide to Genetic Programming*, with contributions by John R.
  Koza, March 2008, ISBN 978-1-4092-0073-4, self-published via Lulu.com, CC
  BY-NC-ND 2.0 UK. [V from the book's own title page.] *** gp-field-guide.org.uk
  is HTTP-only and was unreachable; the WORKING mirror, verified (3,767,321
  bytes, read in full), is
  http://www0.cs.ucl.ac.uk/staff/W.Langdon/ftp/papers/poli08_fieldguide.pdf ***

### REPRESENTATION

expression trees over a FUNCTION SET and a TERMINAL SET. Both
requirements are Koza's own 1992 terms. [V — definitions from the Field Guide
§3.2, which cites Koza 1992 and has Koza as a contributing author.]
- CLOSURE, verbatim: "most function sets are required to have an important
  property known as closure (Koza, 1992), which can in turn be broken down into
  the properties of TYPE CONSISTENCY and EVALUATION SAFETY."
  Type consistency, verbatim: "it is necessary that any subtree can be used in
  any of the argument positions for every function in the function set, because
  it is always possible that subtree crossover will generate that combination.
  It is thus common to require that all the functions be type consistent, i.e.,
  they all return values of the same type, and that each of their arguments also
  have this type."
  Evaluation safety, verbatim: "required because many commonly used functions
  can fail at run time. An evolved expression might, for example, divide by 0, or
  call MOVE FORWARD when facing a wall or precipice." Hence protected operators —
  and the canonical protected division `%` returns 1 when the divisor is 0,
  deliberately: "The decision to return the value 1 provides the GP system with a
  simple way to generate the constant 1, via an expression of the form (% x x).
  This combined with a similar mechanism for generating 0 via (- x x) ensures
  that GP can easily construct these two important constants."
- SUFFICIENCY, verbatim: "Sufficiency means it is possible to express a solution
  to the problem at hand using the elements of the primitive set. Unfortunately,
  sufficiency can be guaranteed only for those problems where theory, or
  experience with other methods, tells us that a solution can be obtained by
  combining the elements of the primitive set." Their examples: {AND, OR, NOT,
  x1..xN} is always sufficient for Boolean induction; {+, -, *, /, x, 0, 1, 2} is
  INsufficient because it cannot represent exp(x). Practical rider: "Adding a few
  unnecessary primitives in an attempt to ensure sufficiency does not tend to
  slow down GP overmuch, although there are cases where it can bias the system in
  unexpected ways."
- STRONGLY TYPED GP is the alternative to closure's type-consistency demand:
  David J. Montana, "Strongly Typed Genetic Programming", *Evolutionary
  Computation* 3(2):199-230, June 1995, DOI 10.1162/evco.1995.3.2.199. [V via
  Crossref, abstract verbatim: "in its standard form, there is no way to restrict
  the programs it generates to those where the functions operate on appropriate
  data types .... Strongly typed genetic programming (STGP) is an enhanced
  version of genetic programming that enforces data-type constraints and whose
  use of generic functions and generic data types makes it more powerful than
  other approaches to type-constraint enforcement."]

### KOZA'S DEFAULT TABLEAU

I could not read the 1992 book (archive.org
lending-gated), but almost all of it is verified from Koza's own later paper,
which explicitly says its secondary parameters are "the same default values as
we have used on numerous other problems [Koza 1992a]":
Koza, "Genetic Programming as a Means for Programming Computers by Natural
Selection", *Statistics and Computing* 4(2):87-112, 1994, full PDF at
genetic-programming.com/jkpdf/scjournallong.pdf. [V — read in full.] Verbatim:
  "each new generation is created from the preceding generation by applying the
  fitness proportionate reproduction operation to 10% of the population and by
  applying the crossover operation to 90% of the population (with both parents
  selected with a probability proportionate to fitness). In selecting crossover
  points, 90% were internal (function) points of the tree and 10% were external
  (terminal) points of the tree. For the practical reason of avoiding the
  expenditure of large amounts of computer time on an occasional oversized
  programs, the depth of initial random programs was limited to 6 and the depth
  of programs created by crossover was limited to 17. ... Spousal selection was
  also fitness proportionate."
  Item by item: p_c = 0.90 [V]; reproduction 0.10 [V]; fitness-proportionate
  selection for both parents [V]; max tree depth 17 for crossover offspring [V];
  max initial depth 6 [V]; the 90%/10% internal/leaf crossover-point bias [V,
  twice — also the Field Guide p.17: "To counter this, Koza (1992) suggested the
  widely used approach of choosing functions 90% of the time and leaves 10% of
  the time."]; 51 generations [V — "N_gen was 51 throughout this article"; "we
  terminate a given run either after 51 generations"]; ramped half-and-half
  initialisation [PARTIALLY V — Koza 1994 describes the effect ("generated so as
  to obtain a wide variety of different sizes and shapes") without naming the
  method; the Field Guide names it as Koza's and gives the usual depth range
  2-6].
  *** POPULATION 500 IS NOT VERIFIED AS A DEFAULT — soften this. *** Koza treats
  M as a MAJOR, problem-specific parameter: "The two major parameters that are
  used to control the process are the population size M and the maximum number of
  generations N_gen"; the worked 11-multiplexer example uses M = 4,000, and
  elsewhere in the same paper "Population size was 500 here", "The population
  size is 1,000 here", "The population size is 10,000 here", and a parity run at
  4,000 raised to 8,000. The 1990 precursor (Stanford CS TR-1314, read in full)
  standardises on 300, with max depth 15 and max initial depth 4 — useful if you
  want to show the defaults MOVING between 1990 and 1992. The Field Guide says
  only "normally, the population size should be at least 500."
  Recommended phrasing: 500 is the population size Koza most often used in the
  1992 book's problems, not a fixed default; 51 generations, 0.90/0.10, depth
  17/6 and the 90/10 point bias genuinely are his stated defaults.
  Koza's 1990 rationale for the 90/10 point bias, verbatim: it "promotes the
  recombining of larger structures than would be the case with a uniform
  distribution over all points (which may do an inordinate amount of mere
  swapping of terminals from tree to tree in a manner more akin to point mutation
  as opposed to true recombining of 'building block' substructures)."

### THE HARDWARE

[V — genetic-programming.com/machine1000.html] A
"1,000-Pentium Beowulf-Style Cluster Computer for Genetic Programming": "a
server and 1,000 Pentium II 350-MHz processors", all COTS parts; 64 MB RAM per
processor (64 GB total); 1,000 CPUs on 500 dual-CPU Tyan Tiger 100 motherboards,
no disk/monitor/keyboard; Red Hat Linux 6.0; 25 hubs of 40 processors feeding two
16-port switches; run as a 25 x 40 TOROIDAL GRID island/deme model, each node
talking only to the server and its four toroidal neighbours. Capacity statement
(not a run setting): "A 1,000-node system can therefore accommodate a population
of 10,000,000 3,000-byte individuals."
  CORRECTION/NUANCE on which book used what: GP IV's own table of contents
  (genetic-programming.com/gpbook4toc.html [V]) has ch. 17.1 "Computer Systems
  Used for Work" with 17.1.1 "Alpha Parallel Computer System" and 17.1.2
  "Pentium Parallel Computer System", plus ch. 18.1 "Five Computer Systems Used
  in...". So GP IV reports results from MORE THAN ONE machine. The Alpha machine
  is the GP III-era one: Bennett, Koza, Shipman & Stiffelman, GECCO 1999, vol. 2,
  pp. 1484-1490 [V abstract]: "how to build a 10-node Beowulf-style parallel
  computer system for $18,000 that delivers about a half peta-flop ... per day on
  runs of genetic programming. Each of the 10 nodes ... contains a 533 MHz Alpha
  processor and runs with the Linux operating system. This amount of
  computational power is sufficient to yield solutions (within a couple of days
  per problem) to 14 published problems where genetic programming has produced
  results that are competitive with human-produced results."
  GP III and GP IV POPULATION SIZES: [U] — not reachable. Do not assert one.

### BLOAT
DEFINITION, [V — Field Guide §11.3]: "very often the average size (number of
nodes) of the programs in a population, after a certain number of generations in
which it was largely static, at some point would start growing at a rapid pace.
Typically the increase in program size was not accompanied by any corresponding
increase in fitness." And crucially: "we should NOT equate growth with bloat and
we should define bloat as program growth without (significant) return in terms
of fitness." Why it matters: "large programs are computationally expensive to
evolve and later use, can be hard to interpret, and may exhibit poor
generalisation."

THE CONSTRAINT EVERY THEORY MUST SATISFY — the SIZE EVOLUTION EQUATION, [V,
Field Guide §11.3.1]: E[mu(t+1)] = SUM_l l * p(l,t), hence
E[mu(t+1) - mu(t)] = SUM_l l (p(l,t) - Phi(l,t)), where mu is mean program size,
p(l,t) the probability of SELECTING programs of size l and Phi(l,t) their
PROPORTION. Valid "for a GP system with selection and any form of symmetric
subtree crossover." Consequence: "for symmetric subtree-swapping crossover
operators, the mean program size evolves as if selection only was acting on the
population", so bloat requires "some small l's for which p(l,t) < Phi(l,t) and
also some bigger l's for which p(l,t) > Phi(l,t)". Derived from Poli's exact
schema theory.

### THE FOUR THEORIES
(a) REPLICATION ACCURACY / protective code / introns. *** CITATION CORRECTION:
    the theory the literature CALLS "replication accuracy" is attributed by the
    Field Guide to McPhee & Miller, NOT to Blickle & Thiele or Nordin & Banzhaf.
    [V verbatim:] "The replication accuracy theory (McPhee and Miller, 1995)
    states that the success of a GP individual depends on its ability to have
    offspring that are functionally similar to the parent. As a consequence, GP
    evolves towards (bloated) representations that increase replication
    accuracy."
    - McPhee & Miller, "Accurate Replication in Genetic Programming", ICGA95
      (*Genetic Algorithms: Proceedings of the Sixth International Conference*,
      ed. Eshelman), Morgan Kaufmann, pp. 303-309, ISBN 1-55860-370-0. [V]
    The two commonly-cited papers are real and ARE about redundancy/introns
    causing growth — they are just not the canonical "replication accuracy"
    citation. Cite them as the INTRON/PROTECTIVE-CODE strand:
    - Blickle & Thiele, "Genetic Programming and Redundancy", in *Genetic
      Algorithms within the Framework of Evolutionary Computation* (Workshop at
      KI-94, Saarbrücken), MPI-I-94-241, pp. 33-38, 1994. [V, with abstract:]
      "Empirical analyses show that large parts of those trees are never used or
      evaluated ... the conclusions drawn from that description among others
      explain the size problem which denotes the phenomenon that the average size
      of trees in the population grows with time." And the authors' own mechanism
      from the GP mailing list, 22 Mar 1995, quoted in the GP bibliography:
      "bloating is a property of GP that arises from the fact that more redundant
      trees have a higher probability to survive crossover. As a result, the
      redundant part of the trees grow bigger and bigger because the increased
      proportion of redundant cut-sites in the tree again lead to a higher
      probability to survive crossover."
    - Nordin & Banzhaf, "Complexity Compression and Evolution", ICGA95, Morgan
      Kaufmann, pp. 310-317. [V — back-to-back pages with McPhee & Miller in the
      same volume. Abstract:] "there is an inherent compression pressure towards
      short, elegant and general solutions ... This pressure becomes visible if
      the size or complexity of solutions are measured without non-effective code
      segments called introns."
(b) REMOVAL BIAS. Soule & Foster, "Removal bias: a new cause of code growth in
    tree based evolutionary programming", IEEE ICEC 1998 (WCCI), pp. 781-786,
    DOI 10.1109/ICEC.1998.700151. [V via Crossref.] Mechanism, [V verbatim from
    the Field Guide]: "inactive code in a GP tree tends to be low in the tree,
    residing, therefore, in smaller-than-average-size subtrees. Crossover events
    excising inactive subtrees produce offspring with the same fitness as their
    parents. On average the inserted subtree is bigger than the excised one, so
    such offspring are bigger than average while retaining the fitness of their
    parent."
(c) NATURE OF PROGRAM SEARCH SPACES. [V verbatim:] "the nature of program search
    spaces theory (Langdon and Poli, 1997; Langdon, Soule, Poli, and Foster,
    1999) predicts that above a certain size, the distribution of fitnesses does
    not vary with size. Since there are more long programs, the number of long
    programs of a given fitness is greater than the number of short programs of
    the same fitness. Over time GP samples longer and longer programs simply
    because there are more of them."
    - Langdon & Poli, "Fitness Causes Bloat", tech report CSRP-97-09, University
      of Birmingham, 1997; published in *Soft Computing in Engineering Design and
      Manufacturing*, Springer London, pp. 13-22, ISBN 3-540-76214-0, DOI
      10.1007/978-1-4471-0427-8_2. [V — Crossref dates the chapter 1998; cite
      "1997/1998" or just the DOI.] Companion: Langdon & Poli, "Fitness Causes
      Bloat: Mutation", EuroGP 1998, LNCS 1391, pp. 37-48, DOI
      10.1007/BFb0055926.
    - Langdon, Soule, Poli & Foster, "The Evolution of Size and Shape", in
      *Advances in Genetic Programming 3*, MIT Press, 1999, pp. 163-190, DOI
      10.7551/mitpress/1110.003.0012. [V]
    - Langdon & Poli, *Foundations of Genetic Programming*, Springer, 2002, ISBN
      3-540-42451-2, DOI 10.1007/978-3-662-04726-2. [V]
(d) CROSSOVER BIAS — the most recent, and the technical claim checks out at
    three independent levels of source.
    - Poli, Langdon & Dignum, "On the Limiting Distribution of Program Sizes in
      Tree-Based Genetic Programming", EuroGP 2007, LNCS 4445, pp. 193-204, DOI
      10.1007/978-3-540-71605-1_18 — **EuroGP 2007 Best Paper award**. [V]
      Abstract verbatim: "We provide strong theoretical and experimental evidence
      that standard sub-tree crossover with uniform selection of crossover points
      pushes a population of a-ary GP trees towards a distribution of tree sizes
      of the form Pr{n} = (1 - ap) C_n^{an+1} (1-p)^{(a-1)n+1} p^n, where n is
      the number of internal nodes in a tree and p is a constant."
    - Dignum & Poli, "Generalisation of the limiting distribution of program
      sizes in tree-based genetic programming and analysis of its effects on
      bloat", GECCO 2007, vol. 2, pp. 1588-1595, DOI 10.1145/1276958.1277277.
      [V] Abstract verbatim: "standard sub-tree crossover with uniform selection
      of crossover points, in the absence of fitness pressure, pushes a
      population of GP trees towards a LAGRANGE DISTRIBUTION of tree sizes ...
      the same distribution is also applicable to the more general case where the
      function set includes functions of mixed arities .... Both predicted and
      observed results show a distinct bias towards the sampling of shorter
      programs irrespective of the mix of function arities used." It explicitly
      treats "the applicability of the theory to the traditional 0.90-function
      0.10-terminal crossover node selection policy" — i.e. the result survives
      Koza's 90/10 bias.
    - The phrase "Lagrange distribution of the SECOND KIND" is [V] in Dignum &
      Poli, "Sub-tree Swapping Crossover and Arity Histogram Distributions",
      EuroGP 2010, DOI 10.1007/978-3-642-12148-7_4, p. 42: "This equation (4) has
      now become a multivariate Lagrange distribution of the second kind."
    - THE SYNTHESIS, [V verbatim, Field Guide §11.3.1]: "On average, each
      application of subtree crossover removes as much genetic material as it
      inserts; consequently crossover on its own does not produce growth or
      shrinkage. While the mean program size is unaffected, however, higher
      moments of the distribution are. In particular, crossover pushes the
      population towards a particular distribution of program sizes, known as a
      Lagrange distribution of the second kind, where small programs have a much
      higher frequency than longer ones. For example, crossover generates a very
      high proportion of single-node individuals. In virtually all problems of
      practical interest, however, very small programs have no chance of solving
      the problem. As a result, programs of above average size have a selective
      advantage over programs of below average size, and the mean program size
      increases. Because crossover will continue to create small programs, which
      will then be ignored by selection (in favour of the larger programs), the
      increase in average size will continue generation by generation."
    - A nice downstream consequence, [V, Field Guide §5.1.2]: seeding the initial
      population WITH the crossover-preferred distribution makes bloat WORSE —
      "It has been shown (Dignum and Poli, 2007) that when the initial population
      is created with the size distribution preferred by crossover, bloat is more
      marked... This is known as LAGRANGE INITIALISATION."

*** WHICH THEORY IS BEST SUPPORTED: NONE, AND THE FIELD GUIDE SAYS SO. This is
the most important correction in the GP material. [V verbatim, §11.3]: "Over the
years, many theories have been proposed to explain various aspects of bloat, and
while great strides have been made, we still lack a single, universally-accepted
unifying theory to explain the broad range of empirical observations." It
presents replication accuracy, removal bias and nature-of-search-spaces as
"three of the oldest ones", notes "The explanations for bloat provided by these
three theories are largely qualitative", and introduces crossover bias as "a
recent explanation" that "is based on and is consistent with the size evolution
equation" — a statement of theoretical standing, not empirical victory. Poli &
McPhee's GECCO 2008 paper says the same in blunter words [V, read at
gpbib.cs.ucl.ac.uk/gecco2008/docs/p1267.pdf]: "we still lack a single unifying
theory to explain the broad range of empirical observations", and "While the jury
remains out on the causes of bloat, practitioners still have the practical
problem of combating bloat in their runs."
  What you CAN say, sourced: crossover bias is the most recent of the four, is
  the only one derived from and provably consistent with the exact size-evolution
  equation, and is the one that generated a working bloat-control method
  (operator equalisation). The bloat survey of record frames it exactly that way
  — Silva, Dignum & Vanneschi, "Operator equalisation for bloat free genetic
  programming and a survey of bloat control methods", *Genetic Programming and
  Evolvable Machines* 13(2):197-238, 2012, DOI 10.1007/s10710-011-9150-5 [V],
  abstract: "Particular attention is then given to the new Crossover Bias theory
  and the bloat control method it inspired, Operator Equalisation (OpEq)." That
  is endorsement-by-emphasis from the survey authors — write it as "the most
  recent and most theoretically grounded, and the one the 2012 survey of record
  foregrounds", NOT as "the winner". ***

### PARSIMONY-PRESSURE REMEDIES
- SIZE AND DEPTH LIMITS, and the pathology of the naive implementation, [V, Field
  Guide §11.3.2]: "Many implementations of this idea (e.g., (Koza, 1992)) apply a
  genetic operator and then check whether the offspring is beyond the size or
  depth limit... If the offspring exceeds the limit, ONE OF THE PARENTS IS
  RETURNED. Obviously, this implementation does not allow programs to grow too
  large. However, there is a serious problem... parent programs that are more
  likely to violate a constraint will tend to be copied (unaltered) more often
  than programs that don't. That is, the population will tend to be filled up
  with programs that nearly infringe the constraint." Concretely: "depth
  thresholds lead to the population filling up with very bushy programs where
  most branches reach the depth limit (being effectively full trees). On the
  contrary, size limits produce populations of stringy programs which tend to all
  approach the size limit." Fixes: return the oversize offspring with fitness 0,
  or declare the operation failed and retry. Rule of thumb: "estimate the size of
  the minimum possible solution... and add some percentage (e.g. 50-200%) as a
  safety margin." *** Note the Field Guide does NOT mention the depth-17 limit
  anywhere (grep-verified). ***
- LINEAR PARSIMONY PRESSURE, [V]: "the new fitness function is f(x) - c*l(x),
  where l(x) is the size of program x ... and c is a constant known as the
  PARSIMONY COEFFICIENT." Cited to Koza 1992; Zhang & Mühlenbein 1993, 1995.
  Essential footnote: "While the new fitness is used to guide evolution, one still
  needs to use the original fitness function to recognise solutions and stop
  runs."
- COVARIANT PARSIMONY PRESSURE — Poli & McPhee, "Parsimony Pressure Made Easy",
  GECCO 2008, pp. 1267-1274, DOI 10.1145/1389095.1389340. [V — read in full.]
  The closed form is exactly as expected. From eq. (13)-(14): absence of growth,
  E[Delta mu] = 0, is obtained iff Cov(l, g) = Cov(l, f); with g = c(t) l(x) this
  gives Cov(l,g) = c(t) Var(l), hence
      *** c(t) = Cov(l, f) / Var(l) ***
  "Note that c is a function of t because both numerator and denominator can
  change from generation to generation." General power-law form (eq. 15): for
  g = c(t) l(x)^k, c(t) = Cov(l,f)/Cov(l,l^k). A drift-CORRECTING variant (eq.
  20) actively pulls mean size back to its initial value:
  c(t) = [Cov(l,f) - (mu(0)-mu(t)) fbar] / [Cov(l,l^k) - (mu(0)-mu(t)) E[l^k]].
  Theoretical frame: the paper rewrites the size evolution equation "in a form
  that shows its direct relationship to Price's theorem", giving
  E[Delta mu] = Cov(l,f)/fbar. It demonstrates "almost complete control over the
  dynamics of the mean program size, and control can be obtained in a single
  generation", including schemes where target mean size follows an arbitrary
  trajectory.
  *** THE CAVEAT, verbatim: "while much of this theory assumes the use of fitness
  proportionate selection, Equation (6) is valid in general... As we will see in
  the experiments, however, the penalty coefficients estimated using the theory
  developed for fitness proportionate selection actually work very well without
  any modification in systems based on other forms of selection, such as
  tournament selection." So the PROOF is for fitness-proportionate selection and
  the tournament result is EMPIRICAL. *** Experiments: 6-MUX, populations 100 /
  1,000 / 10,000, 100 runs each, 500 generations.
- LEXICOGRAPHIC PARSIMONY PRESSURE — Luke & Panait, "Lexicographic Parsimony
  Pressure", GECCO 2002, Morgan Kaufmann, pp. 829-836, ISBN 1-55860-878-8. [V —
  PDF read.] Abstract verbatim: "Lexicographic parsimony pressure modifies
  selection to prefer smaller trees ONLY WHEN FITNESSES ARE EQUAL (or equal in
  rank). This technique is simple to implement and is not affected by specific
  differences in fitness values, but only by their relative ranking. In two
  experiments we show that lexicographic parsimony pressure reduces tree size
  while maintaining good fitness values, particularly when coupled with
  Koza-style maximum tree depth limits." Variants in the paper: plain
  lexicographic, DIRECT BUCKETING (fitnesses binned so "equal in rank" becomes
  coarser) and RATIO BUCKETING (higher-fitness individuals occupy smaller
  buckets). The Field Guide notes it is "in fact a form of MOO with lexicographic
  ordering" and credits Ryan (1994) alongside.
  *** CITATION CORRECTION: "double tournament" is NOT in the GECCO 2002 paper.
  Luke & Panait, "Fighting Bloat with Nonparametric Parsimony Pressure", PPSN VII,
  LNCS 2439, pp. 411-421, DOI 10.1007/3-540-45712-7_40 [V] introduces "two new
  kinds of non-parametric parsimony pressure, Direct and Proportional
  Tournament". DOUBLE TOURNAMENT appears in Luke & Panait, "A Comparison of Bloat
  Control Methods for Genetic Programming", *Evolutionary Computation*
  14(3):309-344, 2006, DOI 10.1162/evco.2006.14.3.309 [V], whose keyword list
  reads "...Lexicographic Parsimony, Double and Proportional Tournament, Death by
  Size, Waiting Room". Its abstract: "the combination of depth limiting with such
  a punitive method is generally more effective than either alone... we augment
  depth limiting with NINE bloat control methods and compare them ... and
  discover an unexpected winner in the cross-platform category." The identity of
  that winner is [U] — only the abstract was read; the full text at
  cognet.mit.edu/system/cogfiles/journalpdfs/evco.2006.14.3.309.pdf is worth
  chasing, since it is the only systematic nine-way comparison. ***
- THE TARPEIAN METHOD — Poli, "A Simple but Theoretically-motivated Method to
  Control Bloat in Genetic Programming", EuroGP 2003, LNCS 2610, pp. 204-217,
  DOI 10.1007/3-540-36599-0_19. [V] Author's abstract verbatim: "based on the
  idea of strategically and dynamically creating fitness 'holes' in the fitness
  landscape which repel the population. In particular we create holes by ZEROING
  THE FITNESS OF A CERTAIN PROPORTION OF THE OFFSPRING THAT HAVE ABOVE AVERAGE
  LENGTH. Unlike other methods where all individuals are penalised when length
  constraints are violated, here we randomly penalise only a fixed proportion of
  all the constraint-violating offspring." Test problems: Poly-10 and even-10
  parity. The Field Guide adds the practical bonus [V]: "An advantage of the
  method is that the programs whose fitness is zeroed are never executed, thereby
  speeding up runs." Follow-ups: Poli, "Covariant Tarpeian Method for Bloat
  Control in Genetic Programming", 2010, DOI 10.1007/978-1-4419-7747-2_5; and a
  generalisation caution — Mahler, Robilliard & Fonlupt, "Tarpeian Bloat Control
  and Generalization Accuracy", EuroGP 2005, LNCS 3447, pp. 203-214, DOI
  10.1007/978-3-540-31989-4_18 [V]: "The results are contrasted, showing that it
  can either increase or reduce the generalization power of GP hypotheses,
  depending on the problem at hand. This suggest[s] that a blind use of TC is not
  safe."
- MULTI-OBJECTIVE SIZE-VS-ERROR, [V, Field Guide §9.2.1/§11.3.2]: "recent methods
  also include the use of multi-objective optimisation to control bloat. This
  typically involves the use of a modified selection based on the Pareto
  criterion." Cited: Ekárt & Németh 2001; de Jong, Watson & Pollack 2001; with
  the Field Guide's own caution that "without diversity enhancement (given by
  modern MOO methods)" the approach does not work well.
- OPERATOR EQUALISATION — the method crossover-bias theory directly motivated.
  Antecedents [V]: Dignum & Poli, "Operator Equalisation and Bloat Free GP",
  EuroGP 2008, LNCS 4971, pp. 110-121, DOI 10.1007/978-3-540-78671-9_10 — "we
  introduce a novel and simple technique, which we call Operator Equalisation, to
  control how GP will sample certain length classes. This allows us to finely and
  freely bias the search towards shorter or longer programs ... This gives the
  user total control on the program length distribution, thereby completely
  freeing GP from bloat." And Silva & Dignum, "Extending Operator Equalisation:
  Fitness Based Self Adaptive Length Distribution for Bloat Free GP", EuroGP
  2009, LNCS 5481, pp. 159-170, DOI 10.1007/978-3-642-01181-8_14 — "By filtering
  which individuals are allowed in the population ... the ability to
  automatically determine and follow the ideal length distribution for each stage
  of the run, unconstrained by a fixed maximum limit." One-liner: OpEq imposes a
  target DISTRIBUTION OVER PROGRAM-LENGTH CLASSES and accepts or rejects new
  individuals by which length bin they fall into; the self-adaptive version
  derives the target each generation from the fitness observed in each bin. Silva,
  Dignum & Vanneschi 2012 report "Genetic Programming using OpEq is essentially
  bloat free", and also "the unexpected effect of OpEq on overfitting".
- ANTI-BLOAT OPERATORS, [V]: size-fair crossover and size-fair mutation (Langdon
  2000; Crawford-Marks & Spector 2002) — "In size-fair crossover... the crossover
  point in the first parent is selected randomly ... Then the size of the subtree
  to be excised is calculated. This is used to constrain the choice of the second
  crossover point so as to guarantee that the subtree chosen from the second
  parent will not be 'unfairly' big." Also hoist mutation (Kinnear 1994 — the new
  subtree is drawn from WITHIN the subtree being removed, so the child is always
  smaller) and shrink mutation (Angeline 1996 — subtree replaced by a random
  terminal).

VARIANTS (compressed; full detail in the source file).
- GRAMMATICAL EVOLUTION: Ryan, Collins & O'Neill, "Grammatical evolution: Evolving
  programs for an arbitrary language", EuroGP 1998, LNCS 1391, pp. 83-96, DOI
  10.1007/BFb0055930; O'Neill & Ryan, "Grammatical evolution", IEEE TEVC
  5(4):349-358, 2001, DOI 10.1109/4235.942529. [both citations V; full texts
  closed.] Mechanism [V from the same authors' readable sources — the GP'98
  steady-state paper, their GECCO 2002 "How to do Anything With Grammars", and
  PonyGE2 (arXiv:1703.08535)]: a variable-length binary genome read as 8-BIT
  CODONS; mapping expands the LEFTMOST non-terminal, consuming one codon per
  choice via the MOD RULE `Rule = c % r` (c the codon value, r the number of
  productions for the current non-terminal). "Typically, eight bit codons are
  used, so each can encode 256 different choices (2^8), the number is moded by
  the number of legal choices. This results in a situation where every codon can
  legally be applied to every choice." WRAPPING, verbatim: "the individual is
  wrapped, that is, one starts reading from the start once more. There is an
  upper limit on the number of wrapping events, which, when exceeded an
  individual is aborted. This upper limit is usually set to ten, although newer
  algorithms in the Grammatical Evolution family don't employ wrapping".
  PonyGE2 confirms wrapping is OFF by default in modern implementations and that
  it "does come at the cost of introducing functional dependencies between codons
  that would not otherwise arise". GE's "intrinsic polymorphism": the same codon
  value selects different productions depending on which non-terminal is current.
  THE LOCALITY CRITICISM, and it needs three fixes: Rothlauf & Oetzel, "On the
  Locality of Grammatical Evolution", EuroGP 2006, LNCS 3905, pp. 320-330, DOI
  10.1007/11729976_29. [V, abstract verbatim:] "the representation used in GE has
  problems with locality as many neighbouring genotypes do not correspond to
  neighbouring phenotypes. Experiments with a simple local search strategy reveal
  that the GE representation leads to lower performance FOR MUTATION-BASED SEARCH
  APPROACHES in comparison to standard GP representations."
  (i) The performance claim is scoped to MUTATION-BASED search with a simple
  local-search strategy — not a general claim about GE with crossover.
  (ii) The dominant measured effect is REDUNDANCY, not jumping. [V second-hand
  via Medvet, "A Comparative Analysis of Dynamic Locality and Redundancy in
  Grammatical Evolution", EuroGP 2017, DOI 10.1007/978-3-319-55696-3_21]: they
  "use the Hamming distance for genotypes and the tree edit distance for
  phenotypes", apply "one-bit flip mutations", and "The result is twofold: in 90%
  of cases a mutation does not change the phenotype and, in the remaining 10% of
  cases, a significant fraction corresponds to mutations causing heavy changes in
  the phenotype." So ~90% neutral, most of the rest big jumps, almost no small
  phenotypic steps. These figures are second-hand-verified only.
  (iii) DO NOT attribute "ripple" to Rothlauf & Oetzel, and do not attach it to
  mutation. The RIPPLE EFFECT / ripple crossover is a CROSSOVER phenomenon named
  by the GE authors: Keijzer, Ryan, O'Neill, Cattolico & Babovic, "Ripple
  Crossover in Genetic Programming", EuroGP 2001, pp. 74-86, DOI
  10.1007/3-540-45355-5_7; O'Neill, Ryan, Keijzer & Cattolico, "Crossover in
  Grammatical Evolution", GPEM, pp. 67-93, 2003, DOI 10.1023/a:1021877127167.
  [both V] What IS true for mutation is POSITIONAL DEPENDENCE: because the mapping
  is leftmost-first, changing an early codon re-interprets every codon after it.
  (iv) A follow-up from the same group complicates the headline — Thorhauer &
  Rothlauf, "On the Locality of Standard Search Operators in Grammatical
  Evolution", PPSN XIII 2014, LNCS 8672, pp. 465-475, DOI
  10.1007/978-3-319-10762-2_46 [V, abstract verbatim]: "Both standard GE and GP
  search operators suffer from low locality ... Furthermore, THE LOCALITY OF
  STANDARD GE SEARCH OPERATORS IS HIGHER THAN THAT OF STANDARD GP SEARCH
  OPERATORS, which allows more focused search in GE." So do not present "GE has
  bad locality, GP has good locality" as settled.
- LINEAR GP: Brameier & Banzhaf, *Linear Genetic Programming*, Springer, 2007,
  ISBN 978-0-387-31029-9, DOI 10.1007/978-0-387-31030-5 [V]; earlier Brameier &
  Banzhaf, "A comparison of linear genetic programming and neural networks in
  medical data mining", IEEE TEVC 5(1):17-26, 2001, DOI 10.1109/4235.910462 [V];
  also Brameier & Banzhaf, "Evolving Teams of Predictors with Linear Genetic
  Programming", GPEM 2(4):381-407, 2001, DOI 10.1023/A:1012978805372 [V].
  MECHANISM, [V from Brameier's thesis abstract, *On Linear Genetic Programming*,
  Universität Dortmund, Feb 2004, DOI 10.17877/DE290R-253]: "linear genetic
  programming (LGP), a machine learning approach that evolves computer programs as
  SEQUENCES OF IMPERATIVE INSTRUCTIONS. Two fundamental differences to the more
  common tree-based variant (TGP) may be identified. These are the GRAPH-BASED
  FUNCTIONAL STRUCTURE of linear genetic programs, on the one hand, and the
  existence of STRUCTURALLY NONEFFECTIVE CODE, on the other hand." I.e. programs
  are register-machine instruction sequences; data flow through registers makes
  the EFFECTIVE program a DAG rather than a tree; and instructions whose results
  are never read are STRUCTURALLY non-effective introns, detectable and removable
  in linear time — which is why LGP is the natural setting for intron and
  neutral-variation studies.
- CARTESIAN GP: Miller & Thomson, "Cartesian Genetic Programming", EuroGP 2000,
  LNCS 1802, pp. 121-132, DOI 10.1007/978-3-540-46239-2_9 [V]; Miller (ed.),
  *Cartesian Genetic Programming*, Springer Natural Computing Series, 2011, DOI
  10.1007/978-3-642-17310-3 [V]. Best readable source: Miller, "Cartesian genetic
  programming: its status and future", GPEM 21(1-2):129-168, 2020, DOI
  10.1007/s10710-019-09360-6, OPEN ACCESS [V — read in full].
  REPRESENTATION, [V verbatim §2.1]: a grid of n_c columns x n_r rows, so
  "the maximum number of computational nodes allowed: n_n = n_c * n_r". Each node
  carries a function index plus connection genes that are INTEGER ADDRESSES: "The
  program data inputs are given the absolute data addresses 0 to n_i - 1... The
  data outputs of nodes in the genotype are given addresses sequentially, column
  by column, starting from n_i to n_i + n_n - 1." Arity is the max over the
  function table; surplus genes "are ignored". "Nodes in columns cannot be
  connected to each other", and the graph is "directed and feed-forward".
  LEVELS-BACK l "constrains which columns a node can get its inputs from. If
  l = 1, a node can get its inputs only from a node in the column on its
  immediate left or from a primary input... If one wishes to allow nodes to
  connect to any nodes on their left, then l = n_c." With n_r = 1 and l = n_c,
  "the genotype can represent any bounded directed graph." FIXED GENOTYPE LENGTH
  (eq. 1): L_cgp = n_n (a + 1) + n_o.
  THE NEUTRALITY POINT, verbatim: "Non-coding genes arise in CGP when the outputs
  of nodes are not referenced in the flow of data from program inputs to program
  outputs. It is this which leads to both variable length phenotypes and
  EVOLUTIONARY NEUTRAL DRIFT in the genotype." Standard CGP searches with a
  1+lambda ES in which "An offspring that has a fitness BETTER OR EQUAL to the
  parent becomes the new parent" — the "or equal" is precisely what permits
  neutral drift.
  EVIDENCE THAT NEUTRALITY HELPS: (i) Miller & Thomson 2000's own abstract [V]:
  "A neutral search strategy that allows the fittest genotype to be replaced by
  another equally fit genotype (a neutral genotype) is examined and compared with
  non-neutral search for the Santa Fe ant problem. The neutral search proves to
  be much more effective." (Effort figures [U].) (ii) Vassilev & Miller, "The
  Advantages of Landscape Neutrality in Digital Circuit Evolution", ICES 2000,
  pp. 252-263, DOI 10.1007/3-540-46406-9_25 [V abstract]: studies the three-bit
  binary multiplier, evolving extrinsically on an array of logic cells, and "It
  is argued that landscape neutrality is beneficial for digital circuit
  evolution." Details [U]. (iii) THE HEADLINE NUMBER — Miller & Smith,
  "Redundancy and Computational Efficiency in Cartesian Genetic Programming",
  IEEE TEVC 10(2):167-174, 2006, DOI 10.1109/TEVC.2006.871253 [V, abstract
  verbatim]: "It has been demonstrated that this junk has a useful role and is
  very beneficial in evolutionary search. ... It is found that THE MOST EVOLVABLE
  REPRESENTATIONS OCCUR WHEN THE GENOTYPE IS EXTREMELY LARGE AND IN WHICH OVER 95
  PERCENT OF THE GENES ARE INACTIVE."
  FOUR CAVEATS so the claim does not read as naive, all [V from Miller GPEM 2020]:
  not monotone — "Turner et al. ... found that the relationship was approximately
  QUADRATIC with a clear optimum value for n_n. Often the optimum number of nodes
  was quite large (hundreds or thousands of nodes)"; WHY it helps is contested —
  Goldman & Punch "suggested also that the advantage of large amounts of inactive
  nodes is purely that they provide mutation with random nodes for exploratory
  purposes", consistent with "the author's unpublished finding that randomising
  inactive genes prior to mutation appears not to cause any performance impact";
  a domain where it does NOT help — Vašíček's "zero neutrality" result on 100
  industrial-sized circuit-optimisation problems was "statistically
  indistinguishable" from standard CGP, which Miller calls "the surprising result
  that there is no need to utilise inactive nodes in CGP when optimising fully
  functional digital circuits!"; and the neutral-drift explanation for CGP's lack
  of bloat has been DISPROVED — "when NGD is disallowed in CGP bloat still does
  not occur."
- PushGP: Spector & Robinson, "Genetic Programming and Autoconstructive Evolution
  with the Push Programming Language", GPEM 3(1):7-40, 2002, DOI
  10.1023/A:1014538503543. [V, abstract verbatim:] "PushGP is a genetic
  programming system that evolves Push programs to solve computational problems.
  Pushpop, an autoconstructive evolution system, also evolves Push programs but
  does so while simultaneously evolving its own evolutionary mechanisms."
  "Stack-based" is [V] (Helmuth & Spector, GECCO 2013 Companion, pp. 1627-1634,
  DOI 10.1145/2464576.2466814). The finer detail — multiple separately typed
  stacks including a CODE stack that makes Push self-modifying — is [U].
- GEOMETRIC SEMANTIC GP: Moraglio, Krawiec & Johnson, "Geometric Semantic Genetic
  Programming", PPSN XII (part 1), LNCS 7491, pp. 21-31, DOI
  10.1007/978-3-642-32937-1_3. [V — primary paper read in full.]
  THE GUARANTEE, authors' own definitions verbatim: "A search operator CX is a
  GEOMETRIC CROSSOVER w.r.t. the metric d if for any choice of parents p1 and p2,
  any of their offspring o = CX(p1,p2) is in the metric SEGMENT between parents. A
  search operator M is a GEOMETRIC epsilon-MUTATION w.r.t. d if for any choice of
  the parent p, any of its offspring o = M(p) is in the metric BALL of radius
  epsilon centered in the parent." Semantic distance is SD(h1,h2) = D(O(h1),O(h2))
  where O(h) is the output vector over training cases; note SD is only a
  PSEUDOmetric.
  THE CONE-LANDSCAPE CLAIM, verbatim: "The semantic fitness landscape seen by an
  evolutionary algorithm with semantic geometric operators has a nice shape by
  construction: from the definition of semantic distance, the fitness of a
  solution is its distance in the search space to the optimum (CONE LANDSCAPE).
  This observation is remarkably general, as it holds for any domain of
  application of GP ... and for any choice of metric for the error function." For
  Boolean functions "semantic GP search is equivalent to GA search on binary
  strings on ONEMAX of dimension N." Moraglio's own code README puts it bluntly:
  "The fitness landscape seen by Geometric Semantic operators is always unimodal.
  A hill climber can reach the optimum."
  *** PRECISION FIX on the operator, Definition 2 verbatim: "Given two parent
  functions T1, T2: R^n -> R, the recombinations SGXE and SGXM return the real
  function T3 = (T1*TR) + ((1-TR)*T2) where TR is a random real CONSTANT in [0,1]
  (SGXE), or a random real FUNCTION with codomain [0,1] (SGXM)." Theorem 2: SGXE
  and SGXM are geometric for EUCLIDEAN and MANHATTAN distances RESPECTIVELY. So:
  random constant -> Euclidean; random function -> Manhattan. *** Boolean
  crossover SGXB: T3 = (T1 AND TR) OR (NOT TR AND T2), TR a random Boolean
  "crossover mask", geometric w.r.t. Hamming. Program crossover SGXP: IF COND_R
  THEN T1 ELSE T2. Arithmetic mutation SGMR: T_M = T + ms(T_R1 - T_R2). Quotable
  line: "the offspring is not only the effect of crossover, it is also the
  description of how to crossover its parents."
  THE DRAWBACK AND ITS RATE. [V in the original §3 "Simplification"]: "As the
  syntax of the offspring of semantic crossover contains both parents, THE SIZE OF
  INDIVIDUALS GROWS EXPONENTIALLY WITH THE NUMBER OF GENERATIONS." The explicit
  rate is [V] from Martins, Oliveira, Miranda, Casadei & Pappa, "Solving the
  Exponential Growth of Symbolic Regression Trees in Geometric Semantic Genetic
  Programming", GECCO 2018, arXiv:1804.06808: "the geometric semantic mutation
  and crossover operators induce, respectively, LINEAR and EXPONENTIAL growth",
  with E[GSX_E, g] = 2^g E[P0] + (2^g - 1) b — i.e. SIZE DOUBLES EVERY GENERATION
  under geometric semantic crossover, linear under mutation.
  THE STANDARD REMEDY: Vanneschi, Castelli, Manzoni & Silva, "A New Implementation
  of Geometric Semantic GP and its Application to Problems in Pharmacokinetics",
  EuroGP 2013, LNCS 7831, pp. 205-216, DOI 10.1007/978-3-642-37207-0_18. [V,
  abstract verbatim:] "these operators, by construction, always produce offspring
  that are larger than their parents, causing an exponential growth in the size of
  the individuals, WHICH ACTUALLY RENDERS THEM USELESS IN PRACTICE. In this paper
  we overcome this limitation by presenting a new efficient implementation."
  Mechanism: store POINTERS to the parent trees and compute the semantics of new
  individuals from their parents' values. *** CAVEAT WORTH CARRYING: "if we want
  to access the final individual or if new data is presented after the training
  stage, an assembling step is needed to generate the complete individual from the
  pointers, which still presents an exponential size." So the remedy makes GSGP
  RUNNABLE; it does NOT make the model small or interpretable. ***
- LEXICASE SELECTION: Spector, "Assessment of problem modality by differential
  performance of lexicase selection in genetic programming: a preliminary
  report", GECCO 2012 Companion, pp. 401-408, DOI 10.1145/2330784.2330846 [V];
  Helmuth, Spector & Matheson, "Solving Uncompromising Problems With Lexicase
  Selection", IEEE TEVC 19(5):630-643, 2015, DOI 10.1109/TEVC.2014.2362729 [V —
  full text read].
  MECHANISM, [V verbatim, Helmuth et al. Fig. 1]: "1) Initialize: a) Set
  `candidates` to be the entire population. b) Set `cases` to be a list of all of
  the test cases IN RANDOM ORDER. 2) Loop: a) Set `candidates` to be the subset of
  the current `candidates` that have EXACTLY THE BEST PERFORMANCE of any
  individual currently in `candidates` for the first case in `cases`. b) If
  `candidates` contains just a single individual then return it. c) If `cases`
  contains just a single test case then return a RANDOMLY SELECTED individual from
  `candidates`. d) Otherwise remove the first case from `cases` and go to Loop."
  *** DISCREPANCY: Spector's 2012 Fig. 1 returns "the FIRST individual in
  candidates"; Helmuth et al. 2015 and La Cava et al. 2016 return a RANDOM one. If
  you say "pick randomly", cite 2015/2016, not 2012. ***
  COST, [V, La Cava 2016 §2]: "Lexicase selection has a theoretical worst-case
  time complexity of O(|P|^2 N), compared to O(|P| N) for tournament selection...
  this worst-case complexity is only reached if every individual passes every test
  case during selection; in practice, lexicase selection normally uses a small
  number of cases for each selection and therefore incurs only a small amount of
  overhead."
  THE TARGET CLASS, verbatim: an "UNCOMPROMISING PROBLEM" is one "for which any
  acceptable solution must perform as well on each test case as it is possible to
  perform on that test case; that is... it is not acceptable for a solution to
  perform sub-optimally on any one test case in exchange for good performance on
  others." Four problems, with results [all V]: discriminator terms in finite
  algebras — "sets of runs using lexicase selection succeeded nearly 100% of the
  time whereas runs using tournament selection, with tournament sizes ranging from
  2 to 10, succeeded between 0% and 26% of the time"; 3-bit digital multiplier
  (PushGP, population 5,000, 100 runs/condition) — lexicase success rate 1.0,
  EVERY tournament condition 0, Fisher's exact p < 0.0001; factorial (100
  runs/condition) — lexicase 0.51, all tournament/normalised/IFS conditions 0
  except normalised size 8 at 0.01; Unix `wc` (200 runs/condition) — lexicase
  0.055 (11 programs with zero error on training AND withheld test sets), all
  others 0, with their own hedge "the effect ... is likely small but nonetheless
  meaningful, particularly since it appears to be difference between 'no
  successes' and 'occasional successes.'" COST (Table IX): lexicase slowest per
  generation everywhere — ~2x tournament/IFS on finite algebras, up to ~3x on
  `wc`, ~7x on the 3-bit multiplier at population 5,000 — "But many of the
  lexicase runs actually finished faster than the other runs, since they found
  successful programs earlier."
  WHY IT PRESERVES DIVERSITY, verbatim: "Lexicase selection may select individuals
  that perform very poorly on some test cases if they excel on a combination of
  others. As such, lexicase often selects 'SPECIALIST' individuals that solve
  parts of the problem extremely well." They measure behavioural diversity as "the
  percent of distinct behavior vectors in the population" and find lexicase
  highest after the first 15-25 generations. A sharp detail from Spector's Table 1
  (5 individuals, 4 cases): every individual is Pareto-elite, yet selection
  probabilities are 0.250, 0.000, 0.333, 0.208, 0.208 — ONE PARETO-ELITE
  INDIVIDUAL HAS ZERO CHANCE OF SELECTION; "it samples the subset of the
  population's Pareto front that has the best fitness value in the population with
  respect to at least one fitness case. But it does not do so with a uniform
  distribution." Honest negatives they report: "we have yet to find a biasing
  scheme that outperforms the standard form of lexicase selection", and "we do not
  expect lexicase selection to provide a 'free lunch' over all problems (even all
  uncompromising problems)."
  EPSILON-LEXICASE for continuous errors: La Cava, Spector & Danai,
  "Epsilon-Lexicase Selection for Regression", GECCO 2016, pp. 741-748, DOI
  10.1145/2908812.2908898 [V, read via arXiv:1905.13266, a CORRECTED version —
  its own footnote: "Equations 2 and 5 have been corrected to indicate that the
  pass conditions ... are defined relative to the best error IN THE POPULATION on
  that training case, NOT IN THE SELECTION POOL"]; and La Cava, Helmuth, Spector &
  Moore, "A Probabilistic and Multi-Objective Analysis of Lexicase Selection and
  epsilon-Lexicase Selection", *Evolutionary Computation* 27(3):377-402, 2019, DOI
  10.1162/evco_a_00224 [V]. Why needed, verbatim: plain lexicase "fails to produce
  such benefits when applied to continuous symbolic regression problems, due to
  its method of selecting test case elitism"; "For individual i to pass case t,
  lexicase requires that e_t(i) = e*_t" — far too stringent when "exact solutions
  to test cases can only be expected for synthetic problems". The fix uses the
  MEDIAN ABSOLUTE DEVIATION: "Given the high sensitivity of sigma to outliers,
  however, we opt for a more robust estimation of variability by using the median
  absolute deviation (MAD) of e_t, defined as MAD(e_t) = lambda(e_t) =
  median_j |e_tj - median_k(e_tk)|", giving eps_elambda: e_t(i) < e*_t +
  lambda(e_t). Rationale: "As the performance on each training case improves
  across the population, epsilon SHRINKS, thereby modulating the selectivity of a
  case based on how difficult it is." The 2019 paper adds three implementations —
  "static, which is the version originally proposed; semi-dynamic, in which the
  elite error is defined relative to the current selection pool; and dynamic, in
  which both the elite error and epsilon are defined relative to the current
  selection pool." Conclusions: 2016 — "epsilon-lexicase selection, especially
  with automatic threshold adaptation ..., performs the best on the regression
  problems studied here", "producing better fit models compared to other
  techniques such as tournament selection and age-fitness Pareto optimization",
  with wall-clock "comparable to tournament selection"; 2019 — "we derive an
  analytical formula that gives the expected probabilities of selection under
  lexicase selection", and lexicase "select[s] individuals on the boundaries of
  Pareto fronts in high-dimensional space", with an explanation of "why it has
  been shown to perform more poorly in continuous error spaces".

SYMBOLIC REGRESSION — THE CURRENT STATE OF THE ART. [V — full text read:]
La Cava, Orzechowski, Burlacu, de França, Virgolin, Jin, Kommenda & Moore,
"Contemporary Symbolic Regression Methods and their Relative Performance",
NeurIPS 2021 Datasets and Benchmarks Track, arXiv:2107.14351 (submitted
2021-07-29; the arXiv comment confirms the venue).
  SCALE, verbatim: "We assess 14 symbolic regression methods and 7 machine
  learning methods on a set of 252 diverse regression problems." Split: 122
  black-box problems (from PMLB v1.0, 21 algorithms, 5-fold halving grid-search CV
  tuning, "47 to 1 million instances, and two to 124 features", including "46
  'real-world' problems") and 130 ground-truth problems (14 algorithms,
  hyperparameters reused) from "the Feynman Symbolic Regression Database, and the
  ODE-Strogatz repository".
  BLACK-BOX RESULT, verbatim: "the models generated by OPERON are significantly
  more accurate than any other method's models in terms of test set R^2
  (p <= 6.5e-05). SBP-GP and FEAT rank second and third and attain similar
  accuracies, although the models produced by FEAT are significantly smaller
  (p = 9.2e-22). We note that FOUR OF THE TOP FIVE METHODS (Operon, SBP-GP, FEAT,
  EPLEX) AND SIX OF THE TOP TEN METHODS (GP-GOMEA, ITEA) ARE GP-BASED SR METHODS.
  The other top methods are ensemble tree-based methods, including ... XGBoost and
  LightGBM; Random Forest; and AdaBoost... Operon, FEAT and SBP-GP significantly
  outperform LightGBM (p <= 1.3e-07) and Operon and SBP-GP outperform XGBoost
  (p <= 1.3e-04)... the models produced by the top five SR methods (aside from
  SBP-GP) are 1-3 ORDERS OF MAGNITUDE SMALLER than models produced by the ensemble
  tree-based approaches (p <= 1.3e-21)." The accuracy-vs-simplicity Pareto front
  "is composed of three methods: Operon, GP-GOMEA, and DSR". And AIFeynman does
  BADLY here: "we note that AIFeynman performs poorly on these problems,
  suggesting that not many of them exhibit the qualities of physical systems ...
  that AIFeynman was designed to exploit."
  GROUND-TRUTH RESULT, with the noise caveat, verbatim: "On average, when the
  target is free of noise, we observe that AIFeynman identifies exact solutions
  53% of the time, nearly twice as often as the next closest method (GP-GOMEA,
  27%). However, AT NOISE LEVELS ABOVE 0.01, FOUR OTHER METHODS RECOVER EXACT
  SOLUTIONS MORE OFTEN: DSR, gplearn, AFP_FE, and AFP. Taken together ... AIFeynman
  may be brittle in application to real-world and/or noisy data .... On the
  Strogatz datasets, AIFeynman's performance is not significantly different than
  other methods .... We note that the best method on real-world data, Operon,
  struggles to recover solutions to these problems, despite finding many candidate
  solutions with near perfect test set scores."
  Their own headline: "the best performing methods for real-world regression
  combine genetic algorithms with parameter estimation and/or semantic search
  drivers. When tasked with recovering exact equations in the presence of noise,
  we find that deep learning and genetic algorithm-based approaches perform
  similarly."
  SRBench IS ALIVE AND HAS A NEWER EDITION. [V — GitHub API + site, 2026-11-11]:
  repo github.com/cavalab/srbench, site cavalab.org/srbench/, 333 stars, NOT
  archived, last push 2026-10-15. It now advertises **"SRBench 2025": 25 SR
  methods, Docker containers, hyperparameter tuning, 30 independent runs per
  dataset**, over 24 PMLB datasets plus first-principles problems, including all
  14 original methods. It labels the 2021 NeurIPS edition "v2.0" and Orzechowski,
  La Cava & Moore, "Where are we now? A large benchmark study of recent symbolic
  regression methods", GECCO 2018, as "v1.0". Citation for the current edition:
  Imai Aldeia, Zhang, Bomarito, Cranmer, Fonseca, Burlacu, La Cava & de França,
  "Call for Action: towards the next generation of symbolic regression benchmark",
  GECCO 2025 Companion, pp. 2529-2538, DOI 10.1145/3712255.3734309 [V]. The site
  says the 2025 edition should be used for choosing baselines, while the project
  website still displays the 2021 results.
  GECCO SRBENCH COMPETITIONS — 2022 AND 2023 BOTH EXIST [V]:
  2022 "Interpretable Symbolic Regression for Data Science", GECCO 2022 Boston, 13
  official competitors, 9 after filtering, two tracks. Synthetic track judged on
  re-discovery of exact expressions, feature selection, resistance to local
  optima, extrapolation, sensitivity to noise. Real-world track required
  interpretable models forecasting 14-day COVID-19 case/hospitalisation/death
  counts in New York State, with a subject expert assigning "trust ratings".
  Synthetic: 1. QLattice (6.23), 2. PySR (5.26), 3. uDSR (4.67). Real-world:
  1. uDSR (5.75), 2. QLattice (5.21), 3. geneticengine (4.99). Report: de França
  et al., "Interpretable Symbolic Regression for Data Science: Analysis of the 2022
  Competition", arXiv:2304.01117 ("submitted to IEEE TEVC"; whether it appeared
  there is [U] — cite the arXiv id).
  2023 "Symbolic Regression GECCO Competition": Track 1 Performance (10 entrants)
  — 1. TPSR (6.308), 2. NewTonSR++ (6.225), 3. RILS (6.136). Track 2
  Interpretability (4 entrants) — 1. SR-Forest (3.25), 2. PFGP (2.83),
  3. gplearn (2.25). Pattern worth remarking: PySR and QLattice dominated 2022
  while a TRANSFORMER-based method (TPSR) topped 2023's performance track.
  PySR: Cranmer, "Interpretable Machine Learning for Science with PySR and
  SymbolicRegression.jl", arXiv:2305.01582 (sole author, submitted 2023-05-02).
  [V] Abstract: "PySR's internal search algorithm is a MULTI-POPULATION
  EVOLUTIONARY ALGORITHM, which consists of a unique evolve-simplify-optimize
  loop, designed for optimization of unknown scalar constants in newly-discovered
  empirical expressions. PySR's backend is the extremely optimized Julia library
  SymbolicRegression.jl, which can be used directly from Julia. It is capable of
  fusing user-defined operators into SIMD kernels at runtime, performing automatic
  differentiation, and distributing populations of expressions to thousands of
  cores across a cluster." Current version: **PySR 2.7.2, released
  2026-10-19T19:37:45Z** [V — PyPI JSON API], requires Python >= 3.10. The
  canonical GitHub URL is [U] (the API returned null for MilesCranmer/PySR,
  suggesting a rename or transfer).
  Eureqa: Schmidt & Lipson, "Distilling Free-Form Natural Laws from Experimental
  Data", *Science* 324(5923):81-85, 2009, DOI 10.1126/science.1165893. [V — every
  field confirmed via Crossref, including the issue number.]

KOZA'S "HUMAN-COMPETITIVE RESULTS" — AND HOW THEY HELD UP.
The counts are now pinned precisely. [V — Koza, "Human-competitive results
produced by genetic programming", *Genetic Programming and Evolvable Machines*
11:251-284, 2010, DOI 10.1007/s10710-010-9112-3, OPEN ACCESS, published 25 May
2010; read.]
- **76** human-competitive instances in Table 1. The text notes the table has
  **77 items** because one award is subsumed by other entries. (This resolves the
  76-vs-77 discrepancy that circulates, e.g. on Wikipedia, which gives both.)
- **31** instances recognised by the Human Competitive Awards ("Humies") program,
  which has run since 2004.
- **31** instances that duplicated, infringed or created patentable inventions,
  broken down as **1 from the 19th century, 21 from the 20th century, 7 from the
  21st century, and 2 patentable new inventions**.
- The abstract's own framing: many results used developmental processes and native
  engineering representations; the best early-generation individuals often have
  few working parts; most results that duplicated patented functionality were
  NOVEL solutions rather than infringing ones; and the number and complexity of
  results track growth in computing power, following Moore's law, with the author
  predicting continuation.
- GP IV's own blurb (2003) claims a DIFFERENT and earlier breakdown [V from the GP
  bibliography]: "15 instances where GP has created an entity that either
  infringes or duplicates the functionality of a previously patented 20th-century
  invention, 6 instances ... with respect to post-2000 patented inventions, 2
  instances where GP has created a patentable new invention, and 13 other
  human-competitive results." GP III's blurb cites 14 human-competitive results
  and 10 patent rediscoveries. So the counts GREW across GP III (1999) -> GP IV
  (2003) -> the 2010 paper; attribute each number to its own source.
- Koza's eight criteria for human-competitiveness are his own; the Humies
  competition operationalises them.
HOW IT HELD UP — the honest assessment. GP is a real and in places leading tool in
symbolic regression (the SRBench evidence above is strong: four of the top five
black-box methods are GP) and in heuristic design (FunSearch and AlphaEvolve in
Section 5 are, structurally, GP with an LLM as the variation operator). But the
"automated invention machine" framing did not become mainstream engineering
practice, and the patent-rediscovery claims rest on a counting exercise by the
method's own principal advocate rather than on independent engineering adoption.
The field's own retrospective is O'Neill, Vanneschi, Gustafson & Banzhaf, "Open
issues in genetic programming", GPEM 11:339-363, 2010 [citation as given, content
U]. Note also the critique pattern that recurs in Section 5: where GP-produced
artefacts WERE independently scrutinised — GenProg's patches — most turned out to
be functionality deletion.
