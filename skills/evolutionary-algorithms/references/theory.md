# EA theory: what is proven, and what is folklore

This field has an unusual amount of material that is taught as foundational while being much weaker than advertised. The organizing principle here is to state each classical result precisely, then state what it does not say, with primary sources for both.

Every citation was checked against Crossref, OpenAlex or the arXiv API. ⚠️ marks claims that could not be verified and are therefore not asserted.

---

# Part 1 — The schema theorem

**Primary source:** John H. Holland, *Adaptation in Natural and Artificial Systems*, University of Michigan Press 1975; 2nd ed. MIT Press 1992. ⚠️ The book itself was not read; page references below come from secondary sources.

## Definitions

A **schema** H is a string of length l over {0,1,\*}, with \* a wildcard. A bitstring x is an *instance* of H iff it matches in every non-\* position. A schema denotes a hyperplane of {0,1}^l.

- **order** `o(H)` = the number of fixed (non-\*) positions.
- **defining length** `d(H)` = the distance between the first and last fixed positions = the number of one-point-crossover cut points that can disrupt H.
- `m(H,t)` = the number of instances of H in the population at generation t.
- `f(H,t)` = the average **observed** fitness of population members matching H at t; `f̄(t)` = the population average.

**Counts worth knowing:** there are `3^l` schemata but `2^(2^l)` subsets of the search space, so **most subsets are not schemata.** One string of length l matches `2^l` schemata.

## The inequality

Two legitimate forms circulate; the difference is whether mutation survival is kept exact or linearised.

**Exact-mutation form:**

```
E[m(H,t+1)] ≥ m(H,t) · f(H,t)/f̄(t) · [1 − p_c·d(H)/(l−1)] · (1 − p_m)^o(H)
```

**Linearised form** (first-order expansion of `(1−p_m)^o(H)`, valid for small p_m), as usually quoted from Goldberg 1989:

```
E[m(H,t+1)] ≥ m(H,t) · f(H,t)/f̄(t) · [1 − p_c·d(H)/(l−1) − o(H)·p_m]
```

## The conditions — all six are genuine

1. **Fitness-proportionate (roulette-wheel) selection.** This is what produces the `f(H,t)/f̄(t)` factor. **The theorem does not hold in this form for tournament, rank or truncation selection** — i.e. not for what practitioners actually use.
2. **One-point crossover** with probability p_c and a uniform cut point, giving the disruption term `p_c·d(H)/(l−1)`.
3. **Independent per-bit mutation** with probability p_m.
4. **Non-overlapping generations, random mating**, and (in the dynamical-systems version) **infinite population**.
5. **`f(H,t)` is the *observed* average fitness** of H's representatives in the current population, **not** the static average of H over the search space. *This distinction is load-bearing and is where most misreadings happen.*
6. **The ≥ is there because Holland counted only destructive effects**, pessimistically assuming every crossover inside the defining length destroys H. It ignores *constructive* effects — crossover creating new instances of H.

## What it is, and is not

It is **a one-generation lower bound on an expected count.** It is not a long-run dynamical result.

- **It cannot be iterated.** It is an inequality over an expectation, so compounding it over t generations loses information at every step and the bound degrades to vacuity.
- **`f(H,t)` is itself a random variable** that changes as selection biases the population. "The average fitness of a schema is only relevant in the first few generations of a run."
- **Exact versions exist**, which makes the inequality's role clear. Stephens & Waelbroeck, "Schemata Evolution and Building Blocks," *Evolutionary Computation* 7(2):109–124, 1999, doi:10.1162/evco.1999.7.2.109; Poli's exact schema theorems for GP (2000–01); Alden H. Wright, "The Exact Schema Theorem," arXiv:1105.3538.
- **It extends to arbitrary subsets of the search space and arbitrary operators**, which destroys the idea that schemata are privileged objects. Credited by Altenberg to Grefenstette (FOGA 1, 1989), Radcliffe (*Complex Systems* 5(2):183–205, 1991) and Vose (*Artificial Intelligence* 50(3):385–396, 1991). Altenberg's own Theorem 4 is stated for "any subset H of the search space."

Survey with both forms stated verbatim: **White, "An Overview of Schema Theory," arXiv:1401.2651**, which notes its version "is slightly more general than Holland's original version because it factors in mutation fully rather than assuming p_m is approximately zero," and that "the proof is an exercise in elementary probability."

---

# Part 2 — Implicit parallelism and the n³ claim

**Terminology:** Holland originally called it "intrinsic parallelism" (1975, p. 74) and later renamed it "implicit parallelism" (1992).

**The claim:** a population of n strings can usefully process on the order of **n³ schemata per generation**.

**The argument:** let φ be the number of instances required before a schema counts as "sampled," and θ the highest order represented at that frequency. Then `θ = log₂(n/φ)`, and the number of order-θ schemata present is `2^θ · C(l,θ) ≥ n³`.

**⚠️ THE STATED RANGE OF VALIDITY, which is almost always omitted:** "This result holds when **64 ≤ n ≤ 2^20 and l ≥ 64**." **It is an arithmetic coincidence over a parameter window, not an asymptotic theorem.** Present n³ as folklore with a narrow numerical justification.

Key references:

- Bertoni & Dorigo, "Implicit parallelism in genetic algorithms," *Artificial Intelligence* 61(2):307–314, 1993, doi:10.1016/0004-3702(93)90071-I. ⚠️ Content unverified (no abstract deposited); it is the standard citation for re-deriving the counting argument and showing n³ depends on the parameter choices.
- Grefenstette & Baker, "How genetic algorithms work: a critical look at implicit parallelism," ICGA-3, pp. 20–27, 1989. ⚠️ Content unverified; the argument is that the GA does *not* allocate trials to schemata according to their static average fitness, because sampling is biased by the evolving population.
- Grefenstette, "Conditions for Implicit Parallelism," FOGA 1, pp. 252–261, doi:10.1016/B978-0-08-050684-5.50019-7.
- Vose & Wright, "Form Invariance and Implicit Parallelism," *Evolutionary Computation* 9(3):355–370, 2001.
- **Wright, Vose & Rowe, "Implicit Parallelism," GECCO 2003, LNCS 2724, pp. 1505–1517, doi:10.1007/3-540-45110-2_22.** ⚠️ **This paper has three authors, not four — Christopher Stephens is not among them** (both Crossref and OpenAlex agree; the error comes from conflating it with the Stephens & Waelbroeck exact-schema line). It argues the informal n³ reading does not survive formalisation in the Vose framework.

---

# Part 3 — The building-block hypothesis

**Primary source:** David E. Goldberg, *Genetic Algorithms in Search, Optimization, and Machine Learning*, Addison-Wesley, 1989.

⚠️ **The book could not be obtained, so Goldberg's exact wording is unverified.** The widely quoted p. 41 sentence — "Short, low order, and highly fit schemata are sampled, recombined, and resampled to form strings of potentially higher fitness" — **should not be printed as a verified quotation.**

What *is* verified:

- **The standard formal statement** (White, arXiv:1401.2651): "**Definition 2.** A building block is a short, low order schema with above average fitness." / "**Hypothesis 1 (Building Block Hypothesis).** Good genetic algorithms combine building blocks to form better solutions."
- **Mitchell, Holland & Forrest's own statement**, verbatim from their NIPS paper: "The Building Block Hypothesis (Holland, 1975/1992) states that the GA works well when instances of low-order, short schemas ('building blocks') that confer high fitness can be recombined to form instances of larger schemas that confer even higher fitness."
- **The stronger version the critical literature actually attacks** (Grefenstette's formulation, via White): "**Hypothesis 2 (Static Building Block Hypothesis).** Given any schema partition, a genetic algorithm is expected to converge to the class with the best static average fitness." **This is the one deception is defined against.**
- **Holland's metaphysical backing** (via Burjorjee): his "building block thesis" "holds that most of what we know about the world pivots on descriptions and mechanisms constructed from elementary building blocks," with building blocks being parts that "(i) must be easy to identify… and (ii) must be readily recombined to form a wide variety of structures."

---

# Part 4 — The criticisms

## Mühlenbein

Verbatim as quoted by Altenberg: the schema theorem "**is almost a tautology, only describing proportional selection**," and "the question of why the genetic algorithm builds better and better substrings by crossing-over is ignored." (FOGA 1, 1991, pp. 316–337.)

## Radcliffe's three objections

Verbatim via Altenberg, from Radcliffe, "Non-linear genetic representations," PPSN 2, 1992, pp. 259–268:

1. "The Schema Theorem holds **even with random representations, which cannot be expected to perform better than random search**, whereas it has been used to claim that GAs perform better than random search";
2. "The Schema Theorem holds **even when the schemata defined by a representation may not capture the properties that determine fitness**"; and
3. "The Schema Theorem extends to arbitrary subsets of the search space regardless of the kind of genetic operators, not merely the subsets defined by Holland schemata."

## Grefenstette — "Deception Considered Harmful"

**Grefenstette, "Deception Considered Harmful," FOGA 2, pp. 75–91, Morgan Kaufmann, 1993, doi:10.1016/B978-0-08-094832-4.50011-8** (with a footnote "With apologies to Edsger Dijkstra"). ⚠️ Content unverified — Elsevier, DTIC and OpenAlex all withheld the text.

The argument, as corroborated by the secondary literature: **the formal notion of "deception" presupposes the Static Building Block Hypothesis**, which is false, because a GA does not sample schemata uniformly — it samples from a biased, evolving distribution. Consequently **deception is neither necessary nor sufficient for GA-hardness.** ⚠️ That phrasing is the field's standard summary, not a verified quotation.

## Altenberg and Price's Theorem — the strongest single critique

**Lee Altenberg, "The Schema Theorem and Price's Theorem," FOGA 3, pp. 23–49, Morgan Kaufmann, 1995.** Full text at `dynamics.org/Altenberg/FILES/LeeSTPT.pdf`, read in full.

**The abstract's load-bearing sentence:** "dissenting arguments are reviewed and elaborated upon, explaining **why the Schema Theorem has no implications for how well a GA is performing.**"

**The central claim:** "The Schema Theorem, in short, **does not address the search component of genetic algorithms on which performance depends, and cannot distinguish genetic algorithms that are performing well from those that are not.**"

**The hidden assumption:** "The common interpretation of the Schema Theorem implicitly assumes that any member of an above-average schema is likely to produce offspring of above-average fitness, i.e. that there is a correlation between membership in an above-average schema and production of fitter offspring. **But the existence of such correlations is logically independent of the validity of the Schema Theorem.**" And on the usual gloss: "the phrase '**promising regions of the search space**' is a construct through which hidden assumptions are introduced which are not implied by the Schema Theorem."

**The needle-in-a-haystack counterexample.** One genotype (the needle) has high fitness, all others equally low. Once the needle is in the population it increases by selection while recombination "will most likely generate more 'hay'." Verbatim: "**The Schema Theorem will still be seen to operate**, in that short schemata with above-average fitness (those schemata containing the needle) will increase in frequency, **even though the fitness of new instances of the schemata (more hay) will not be any more likely to have the high fitness of the needle.**"

**A second, sharper one:** take the fitness distribution to be the one-sided stable distribution of index 1/2, which generates needles in haystacks on all length scales. "A GA with this fitness function will generically have schemata that obey (10), **even though it is still random search.**"

**The technical contribution.** He uses **Price's Covariance and Selection Theorem** (Price 1970, 1972) as the general one-generation machinery, with a *measurement function* extracting a population statistic. Choosing a schema indicator yields the Schema Theorem; choosing a fitness-threshold indicator yields his **Local Performance Theorem**, which governs the upper tail of the fitness distribution. The structural point, verbatim: "the covariance term… `Cov[I(x,H), f(x)]`, and the covariance term… `Cov[T(...), f(x)]`, **are independently defined. So conditions that produce growth in the frequencies of different schemata are independent of conditions that produce growth in the upper tails of the fitness distribution.**" Therefore "the inability of the Schema Theorem to distinguish GA performance can be seen simply as **the consequence of the measurement function that was chosen.**"

**"Schema processing is not a requirement":** "In the process of deriving results that relate the parent-offspring correlations to the performance of the GA under a generalized transmission function, **schemata disappear as pertinent entities.** Therefore, 'schema processing' is not a requirement for performance in evolutionary algorithms in general."

**He is not an anti-schema partisan — he reconstructs what the BBH would have to assert.** His Theorem 5, derived using Geiringer's (1944) recombination-distribution representation, makes schemata *reappear* when you specialise to recombination operators, and makes the BBH's real content explicit: "(1) that the recombination operator determines which schemata are being recombined; and (2) that **there needs to be a correlation between complementary schemata of high fitness and the fitness distributions of their recombinant offspring** in order for the GA to increase the chance of sampling fitter individuals." He calls this "a quantitative expression to the Building Blocks Hypothesis."

**His positive proposal: evolvability** — "the ability to produce individuals fitter than any existing" — and the transmission function in the fitness domain, as the right performance statistic.

## Vose's dynamical-systems programme

- **Nix & Vose, "Modeling genetic algorithms with Markov chains," *Annals of Mathematics and Artificial Intelligence* 5(1):79–88, 1992**, doi:10.1007/BF01530781. Models the finite-population simple GA as an exact finite Markov chain over population vectors, with the infinite-population limit a deterministic map.
- **Michael D. Vose, *The Simple Genetic Algorithm: Foundations and Theory*, MIT Press, 1999**, doi:10.7551/mitpress/6229.001.0001.

**Vose's preface, verbatim:** "The rigor of mathematics is employed **so as not to inadvertently repeat myths or recount folklore.**"

**And the rhetorical point writes itself.** The verified chapter structure: Random Heuristic Search 5–20; The Simple Genetic Algorithm 21–38; The Walsh Transform 49–66; Basic Examples 77–92; Focused Heuristics 105–118; Perturbation Arguments 129–138; Transient Behavior 139–150; Asymptotic Behavior 151–168; Hyperbolicity 169–174; Quotients 185–198; Models 199–210; **Schemata 211–218**; Appendix 219–232. **In the field's most rigorous monograph, schemata occupy eight pages near the end, after the entire dynamical-systems development.**

**Structural limitation of the exact chain:** its state space has `C(n+2^l−1, n)` states for population size n and string length l — exact but uncomputable. A verified illustration of where exact Markov-chain analysis *is* feasible: Mühlenthaler, Raß, Schmitt & Wanka, *Natural Computing* 21(4):651–677, 2022 — a discrete PSO on sorting and OneMax. That is the ceiling.

## Burjorjee — the assumption-level critique

**Keki M. Burjorjee, "The Fundamental Problem with the Building Block Hypothesis," arXiv:0810.3356, 2008.** He extracts the two contingent-fitness-structure assumptions the BBH must make:

> "**Abundant Basic Building Blocks:** A large number of basic building blocks exist."
> "**Hierarchical Synergism:** Antagonistic intersections between the building blocks of any level are rare, whereas synergistic intersections between small collections of lower level building blocks are common."

His verdict: "It seems to us that **the number of ways in which these assumptions can be satisfied is vastly outnumbered by the number of ways in which they will not be satisfied.**" He also records that Goldberg dismisses such critiques as "[a] favorite parlor game in genetic and evolutionary computation."

Survey of the criticism: **Reeves & Rowe, *Genetic Algorithms — Principles and Perspectives: A Guide to GA Theory*, Kluwer 2002/2003, §3.3**, book doi:10.1007/b101880.

## One concrete failed prediction

Holland's **principle of minimal alphabets** — the schema-theoretic argument that binary encodings are optimal — was, per White, "an informal argument" for which "detractors produced convincing arguments for why larger alphabets are optimal for certain problems."

---

# Part 5 — The Royal Road: the empirical refutation, by the BBH's own proponents

This is the single best-documented failure of the BBH as a *predictive* claim.

**The three papers:**

1. Mitchell, Forrest & Holland, "The royal road for genetic algorithms: Fitness landscapes and GA performance," ECAL 1992, pp. 245–254, MIT Press.
2. Forrest & Mitchell, "Relative building-block fitness and the building-block hypothesis," **FOGA 2**, pp. 109–126, 1993. (Same volume as Grefenstette's "Deception Considered Harmful" — **FOGA 2 is where the BBH took both barrels.**)
3. **Mitchell, Holland & Forrest, "When will a genetic algorithm outperform hill climbing?", NIPS 6, pp. 51–58, 1994.** Full text read from the NeurIPS archive.

Companion: Forrest & Mitchell, "What Makes a Problem Hard for a Genetic Algorithm? Some Anomalous Results and Their Explanation," *Machine Learning* 13(2–3):285–319, 1993, doi:10.1007/BF00993046 — *the title is itself the finding.*

## R1, defined exactly

l = 64. Eight order-8 schemata s₁..s₈, where sᵢ has ones in positions 8(i−1)+1 .. 8i and \* everywhere else; each has coefficient cᵢ = 8. `R1(x) = Σᵢ cᵢ·δᵢ(x)` with δᵢ(x) = 1 if x ∈ sᵢ. So R1(111...1) = 64.

## Their expectations, in their own words

> "Given this hypothesis, we initially expected that the building-block structure of R1 would lay out a 'royal road' for the GA to follow to the optimal string. We also expected that simple hill-climbing schemes would perform poorly since a large number of bit positions must be optimized simultaneously… **However both these expectations were overturned.**"

## The numbers — 200 runs on R1, function evaluations to the optimum

- "while the GA found the optimum on R1 in an average of **61,334** function evaluations, neither SAHC nor NAHC ever found the optimum within the maximum of 256,000."
- "However, **RMHC found the optimum on R1 in an average of 6179 function evaluations — nearly a factor of ten faster than the GA.**"

RMHC (random mutation hill climbing, suggested to them by Richard Palmer): pick a random string; mutate one uniformly chosen locus; "If the mutation leads to an equal or higher fitness, the new string replaces the old string"; iterate.

Their own reaction: "This striking difference on landscapes **originally designed to be 'royal roads' for the GA** underscores the need for a rigorous answer to the question posed earlier."

## The diagnosis — hitchhiking

> "the simple GA… optimized R1 quite slowly, at least in part because of '**hitchhiking**': once an instance of a higher-order schema is discovered, its high fitness allows the schema to spread quickly in the population, **with 0s in other positions in the string hitchhiking along with the 1s** in the schema's defined positions. This slows down the discovery of schemas in the other positions… **Hitchhiking can in general be a serious bottleneck for the GA.**"

And: "One major impediment was hitchhiking, which **limited implicit parallelism** by fixing certain schema regions suboptimally."

## The analysis

For N adjacent blocks of K ones each (R1: N = K = 8):

- **RMHC:** time to find one block is "slightly larger than 2^K"; for K = 8, E(K,1) = 301.2. Once a block is found, mutations inside it are wasted, so `E(K,N) = E(K,1)·N·(1 + 1/2 + … + 1/N) ≈ E(K,1)·N·(ln N + γ)`. For K = N = 8 that gives **6549**, against the measured 6179 — "agrees reasonably well."
- **The Idealized GA (IGA)**, a *lower bound* on what any GA could do: it knows the target schemata, samples a fresh uniform random string each step, sequesters the first containing a desired schema, and instantaneously crosses in each newly discovered one. `E_N ≈ 2^K(log N + 1)`.

**The punchline, verbatim:** "The major point is that the IGA gives an expected time that is on the order of **2^K log N**, where RMHC gives an expected time that is on the order of **2^K N log N**, a factor of N slower."

**Why:** "the IGA **perfectly implements implicit parallelism**: each new string is completely independent of the previous one, so new samples are given independently to each schema region. In contrast, RMHC moves in the space of strings by single-bit mutations from an original string, so each new sample has all but one of the same bits as the previous sample. **Thus each new string gives a new sample to only one schema region.**" The IGA "'cheats' on each function evaluation, since it knows exactly the desired schemas, but in this way it gives a lower bound."

**The four design conditions they extract** for a real GA to approximate the IGA: independent samples (large population, slow selection, enough mutation that no locus fixes); sequestering (selection strong enough to preserve found schemata but slow enough to prevent hitchhiking); effectively instantaneous crossover; and N large enough for the factor-N speedup to matter. **They note these are not mutually compatible:** "high mutation works against sequestering schemas."

## The partial rehabilitation — the story does not end in defeat

They engineered **R4**: the same level structure with 16 base schemata over **128-bit** strings, no introns; population 500, mutation rate 0.005, multipoint crossover with the number of points Poisson(2.816). Result over 37 runs: "the time to reach level one is comparable for the two algorithms, but **the GA is much faster at reaching levels 2 and 3. Further, the GA discovers level 3 approximately twice as often as RMHC.**" Neither reached level 4.

Their own framing, which is admirably honest: "Our modified Royal Road landscape R4, like R1, **is not meant to be a realistic example of a problem to which one might apply a GA.**"

Independent replication: Belding, "The Distributed Genetic Algorithm Revisited," arXiv adap-org/9504007, ICGA 1995 — 500 runs on R1–R4 on a 64-processor KSR1, reporting "these disappointing results."

## The modern rigorous resolution

**Dirk Sudholt, "How Crossover Speeds up Building Block Assembly in Genetic Algorithms," *Evolutionary Computation* 25(2):237–274, 2017, doi:10.1162/evco_a_00171.**

On royal-road functions and OneMax, "using crossover makes every (μ+λ) genetic algorithm **at least twice as fast** as the fastest evolutionary algorithm using only standard bit mutation, up to small-order terms and for moderate μ and λ." Mechanism: "crossover is able to **repair the disruptive effects of mutation in later generations**," which "makes multibit mutations more useful" and shifts the optimal OneMax mutation rate upward.

**So there is a rigorous, provable sense in which crossover assembles building blocks — but the constant is a factor of ~2, not the dramatic speedup the BBH rhetoric promised, and it was established 28 years after Goldberg 1989.**

---

# Part 6 — No Free Lunch

**Wolpert & Macready, "No free lunch theorems for optimization," *IEEE Transactions on Evolutionary Computation* 1(1):67–82, April 1997, doi:10.1109/4235.585893.** ~14,700 citations. Full text obtained. Earlier TR version: SFI-TR-95-02-010, 1995.

**Abstract, load-bearing sentence:** "A number of 'no free lunch' (NFL) theorems are presented which establish that **for any algorithm, any elevated performance over one class of problems is offset by performance over another class.**"

## The preconditions, verbatim — this is where the misuse happens

**(a) Finite search space.** "We restrict attention to combinatorial optimization in which the search space X, though perhaps quite large, is **finite**."

**(b) Finite codomain.** "We further assume that the space of possible 'cost' values Y is also finite. These restrictions are automatically met for optimization algorithms run on digital computers where typically Y is some 32 or 64 bit representation of the real numbers." **This is the clause that kills the claim that NFL applies to continuous optimization: it applies to the floating-point discretisation, a different object from ℝⁿ.**

**(c) The function class is everything.** "An optimization problem f… is represented as a mapping f: X → Y and **F = Y^X indicates the space of all possible problems.**" The uniform average is over all of F.

**(d) Non-repeating, and performance measured on the sequence of visited points** — the most frequently dropped condition. "we have elected to circumvent the problem entirely by comparing algorithms based on the number of **distinct** function evaluations they have performed." An algorithm is "a mapping from previously visited sets of points to a single new (i.e., **previously unvisited**) point in X."

Two riders they state explicitly:

- The sample must include everything the oracle was asked, not just what the algorithm kept: "because a sample contains all the previous points at which the oracle was consulted, it includes the Y values of **all the neighbors** of the current point, and not only the lowest cost one that the algorithm moves to." *So steepest-ascent hill climbing pays for every neighbour it evaluated.*
- "**Note that measures of performance based on factors other than `d_m^y` (e.g., wall clock time) are outside the scope of our results.**"

**(e) Which algorithms are covered.** "our definition of an algorithm includes all common black-box optimization techniques like simulated annealing and evolutionary algorithms. (**Techniques like branch and bound are not included since they rely explicitly on the cost structure of partial solutions.**)"

**(f) Deterministic/stochastic equivalence.** Results extend to nondeterministic algorithms, because a randomised strategy is a probability distribution over the finitely many deterministic ones, so its expected cost is a weighted average of identical costs.

**(g) The prior.** "A crucial factor in the probabilistic framework is the distribution P(f)… **P(f) is thus a prior specification of the class of the optimization problem at hand.**" **NFL is the statement about the *uniform* P(f).**

## The theorem

```
Σ_{f ∈ F} P(d_m^y | f, m, a_1) = Σ_{f ∈ F} P(d_m^y | f, m, a_2)
```

The paper's own gloss: "P(d_m^y | f, m, a) **is independent of a when averaged over all cost functions.**" And the corollary: "for any performance measure Φ(d_m^y), the average over all f… is independent of a. **The precise way that the sample is mapped to a performance measure is unimportant.**"

**Worth flagging: Wolpert & Macready's own paper (§V-A) contains *a priori* head-to-head minimax distinctions between algorithms** — "distinctions that result **despite** the NFL theorems' enforcing of a type of uniformity over all algorithms." Even the founding paper shows algorithms are not all equivalent under non-average comparisons.

## The sharpened NFL — the result that makes NFL usable

**Schumacher, Vose & Whitley, "The no free lunch and description length," GECCO 2001, pp. 565–570.** ⚠️ Spelling note: some reference lists give "Schuhmacher."

**Their result: NFL results hold for a subset F of all possible functions *if and only if* F is closed under permutation (c.u.p.).** An **iff** — necessary *and* sufficient — which makes "**is this class c.u.p.?**" the right question to ask of any claimed NFL application.

**Definition** (Igel & Toussaint): "A set F ⊆ F is said to be closed under permutation (c.u.p.) if for any permutation π of X and any function f ∈ F the function f ∘ π is also in F."

**The reproof with a clean generalised statement.** Droste, Jansen & Wegener, "Optimization with randomized search heuristics — the (A)NFL theorem, realistic scenarios, and difficult functions," *Theoretical Computer Science* 287(1):131–144, 2002, doi:10.1016/S0304-3975(02)00094-4.

> "**Theorem 1 (Generalized NFL Theorem).** Let H be an arbitrary (randomized or deterministic) search heuristic for functions f ∈ F ⊆ F_{A,B} where F is closed under permutations. Let r(H) be the average… of the expected runtimes of H on F. Then r(H) is a value independent of H."

Their proof is a short induction plus the randomised-to-deterministic averaging argument, and they say so: "The simplicity of the proof also implies that '**there is no secret or myth**' behind the NFL theorem."

**Their one-sentence intuition, which is the thing to remember:** "**If a class of functions does not change by any permutation on the input space, there is no structure which can be used for search.** Hence, all search strategies show the same behavior."

## What NFL does not imply

### It does not apply to practically relevant function classes — quantitatively

**Igel & Toussaint, "On classes of functions for which No Free Lunch results hold," *Information Processing Letters* 86(6):317–321, 2003**, doi:10.1016/S0020-0190(03)00222-9 (preprint arXiv:cs/0108011, read in full).

- There exist `2^(|Y|^|X|) − 1` non-empty subsets of F.
- "**Theorem 2.** The number of non-empty subsets of Y^X that are c.u.p. is given by `2^C(|X|+|Y|−1, |X|) − 1`."
- "The fraction decreases for increasing |X| as well as for increasing |Y|. **Already for small |X| and |Y| the fraction almost vanishes, e.g., for a Boolean function f: {0,1}³ → {0,1} the fraction is ≪ 10⁻¹⁷⁰.**"

**Three bits in, two values out. That is the whole argument in one number.**

### Structure destroys closure — the constructive half

- "**Theorem 3.** A non-trivial neighborhood on X is not invariant under permutations of X." (Proof is two lines: pick a non-adjacent pair and an adjacent pair and permute one onto the other.)
- "**Corollary 1.** If the maximum **steepness** of every function in a non-empty subset F is constrained to be smaller than the maximal possible, then F is not c.u.p." (Steepness is their formalisation of *strong causality*.)
- "**Corollary 2.** If the number of **local minima** of every function in F is constrained to be smaller than the maximal possible, then F is not c.u.p." With the concrete bound: for pseudo-Boolean functions under Hamming-1 adjacency, "the maximum number of local minima is 2^(n−1)."

**Their conclusion, which is the money quote for the whole section:** "we have shown that the statement '**I'm only interested in a subset F of all possible functions, so the NFL theorems do not apply**' **is true with a probability close to one**… Further, the statements 'In my application domain, functions with maximum number of local minima are not realistic' and 'For some components, the objective functions under consideration will not have the maximal possible steepness' lead to scenarios where NFL does not hold."

### Complexity restrictions

Droste, Jansen & Wegener set up four scenarios and argue NFL is irrelevant to the realistic ones:

- **Scenario 2 (One Shot):** "This is the real life situation. However, in black box optimization we do not know f. Theory in the one shot scenario is not possible, since there is an algorithm with runtime 1 (the difficulty is to find this algorithm)."
- **Scenario 4 (Restricted Black Box Optimization):** F restricted by evaluation time, representation size, or Kolmogorov complexity.

**The scale argument:** "The class of functions F_{A,B} contains |B|^|A| functions. The situation of A = {0,1}^100 is not unusual. Assuming… that B contains the set of 20-bit integers, the number of functions equals 2^(20·2^100) and, for each coding, **only a tiny fraction of all functions can be described or evaluated with available resources. Search heuristics are meaningless if it is too expensive to evaluate the given function.**"

**Their conjecture and its honest limit:** "Our conjecture is that no such scenario where the restriction is not a trivial one allows an NFL theorem. **The problem with a proof is that nobody is able to discuss the class of functions with bounds like t(n) = n, s(n) = n, c(n) = n, or even c(n) = O(log(n))… There are no average case results known for such classes of functions.**" What they could do was exhaustively inspect very small classes, and "for all non-trivial situations considered they have proved that there is no NFL theorem. However, the advantages of the better algorithms are small… **This has led to the claim that there is at least a 'free appetizer' in restricted black box optimization**" (Droste, Jansen & Wegener, GECCO '99, pp. 833–839).

Also useful, via Bartz-Beielstein et al., quoting **Culberson (1998)**: "In the context of search problems, the NFL theorem strictly only applies if arbitrary search landscapes are considered, while **the instances of basically any search problem of interest have compact descriptions and therefore cannot give rise to arbitrary search landscapes.**"

### ⚠️ The ANFL theorem — the result that cuts the other way

This is the one people forget, and it is the honest answer to "so I can just restrict the function class and win."

> "**Theorem 2 (Almost No Free Lunch (ANFL) Theorem).** Let H be a randomized search strategy and f: {0,1}^n → {0,1,...,N−1}. Then there exist at least **N^(2^(n/3)) − 1** functions f\* which agree with f on all but at most 2^(n/3) inputs such that H does find the optimum of f\* within 2^(n/3) steps with a probability bounded above by **2^(−n/3)**. **Exponentially many of these functions have the additional property that their evaluation time, circuit size representation, and Kolmogorov complexity is only by an additive term of O(n) larger** than the corresponding complexity of f."

Proof idea: partition {0,1}^n into the 2^(2n/3) subcubes indexed by the first 2n/3 bits; since H can evaluate at most 2^(n/3) points in 2^(n/3) steps, pigeonhole gives a subcube with probability ≤ 2^(−n/3); hide a new optimum there.

**The moral, verbatim:** "a search strategy has to **pay for its success for some functions f with its bad behavior on many functions which are not much more complex than f.** Hence, each search strategy bears some intuition in mind how functions for optimization look like."

Their demolition of a cute trick is worth keeping: Trap differs from OneMax only at 0^n, and "Whitley (1997) has discussed for each search heuristic H the variant H\* [which also evaluates the bitwise complement]. If H is efficient on OneMax_n then H\* is efficient (losing at most a factor of 2) on Trap_n." But for the *class* of trap functions, "the proof of the ANFL theorem implies that each search heuristic fails on most of the trap functions. **This proves that Whitley's idea only helps in very special situations.**"

### Coevolutionary free lunches — with the caveat attached

**Wolpert & Macready, "Coevolutionary Free Lunches," *IEEE TEC* 9(6):721–735, 2005**, doi:10.1109/TEVC.2005.856205.

> "In contrast to the traditional optimization case where the NFL results hold, we show that **in self-play there are free lunches**: in coevolution some algorithms have better performance than other algorithms, averaged across all possible problems."
>
> "**However, in the typical coevolutionary scenarios encountered in biology, where there is no champion, the NFL theorems still hold.**"

**The free lunch is specifically about self-play producing a champion who is then externally evaluated, not about coevolution in general.** Anyone citing "coevolution escapes NFL" without the champion/no-champion distinction is overclaiming.

### Continuous domains

⚠️ NFL does not hold in the continuous domain. Camacho-Villalón, Dorigo & Stützle state the theorems "do not hold for multi-objective problems or continuous domains," citing **Auger & Teytaud, "Continuous Lunches Are Free Plus the Design of Optimal Optimization Algorithms," *Algorithmica* 57(1):121–146, 2010**. ⚠️ The Auger & Teytaud papers were not independently fetched; treat the exact statement and pagination as unverified.

### The "NFL licenses new algorithms" fallacy

**NFL's single largest real-world harm.** Camacho-Villalón, Dorigo & Stützle quote the offenders verbatim:

- **Grey Wolf Optimizer** (Mirjalili et al. 2014, pp. 46–47): "Obviously, the No Free Lunch theorem makes this field of study highly active which results in enhancing current approaches and proposing new meta-heuristics every year. **This also motivates our attempts to develop a new meta-heuristic** with inspiration from grey wolves."
- **Antlion Optimizer** (Mirjalili 2015, p. 81): "…the so-called **No Free Lunch theorem allows researchers to propose new algorithms.**"

Their abstract names it: the rationale "is based on a **wrong understanding of the no-free-lunch theorems for optimization.**" **Note the irony: three of the six algorithms they dissect are continuous optimisers, where NFL as stated does not even apply.**

## Summary: what NFL does and does not license

**Does:** for a uniform prior over a permutation-closed function class, with non-repeating black-box algorithms scored on the sequence of distinct cost values visited, all algorithms have identical average performance. Also: head-to-head minimax distinctions survive, and self-play coevolution has genuine free lunches.

**Does not:** say anything about any class that is not permutation-closed — which is essentially every class with a neighbourhood structure, a steepness bound, a bound on the number of local optima, or a bounded description length. Does not apply to continuous domains, to multi-objective problems, to algorithms exploiting partial-solution cost structure (branch and bound is explicitly excluded), or to performance measures outside the visited cost sequence. **And it does not license inventing a new metaheuristic — but the ANFL theorem also denies you the opposite comfort.**

## Further reading

Whitley & Rowe, "Focused no free lunch theorems," GECCO 2008, pp. 811–818, doi:10.1145/1389095.1389254; and their tutorial "A 'No Free Lunch' Tutorial: Sharpened and Focused No Free Lunch," in Auger & Doerr (eds.), *Theory of Randomized Search Heuristics*, World Scientific 2011, pp. 255–287, doi:10.1142/9789814282673_0009 — **the best single survey entry point.** Wolpert's retrospective: "What Is Important About the No Free Lunch Theorems?", Springer 2021, doi:10.1007/978-3-030-66515-9_13.

---

# Part 7 — Rigorous runtime analysis: where the real results are

Primary source read in full: **Ingo Wegener, "Methods for the Analysis of Evolutionary Algorithms on Pseudo-Boolean Functions," in *Evolutionary Optimization*, Kluwer 2002, pp. 349–369, doi:10.1007/0-306-48041-7_14.** Theorem numbers marked "Wegener Thm n" are from it. Second key source: **Hwang, Panholzer, Rolin, Tsai & Chen, "Probabilistic Analysis of the (1+1)-Evolutionary Algorithm," *Evolutionary Computation* 26(2):299–345, 2018**, doi:10.1162/evco_a_00212 (arXiv:1409.4955).

## The (1+1) EA

```
1. Choose x ∈ {0,1}^n uniformly at random
2. Repeat:
     create y by flipping each bit of x independently with probability p
     replace x by y iff f(y) ≥ f(x)
```

Standard p = 1/n. Note the **≥**: ties are accepted, which is what lets it traverse plateaus. "Runtime" = the number of fitness evaluations until an optimum is first evaluated.

## The results table

| Function | Expected time | Source |
|---|---|---|
| **OneMax** | **Θ(n log n)**; tightly `e·n·ln n − 1.8925n + (e/2)ln n + 0.598 + O(log n/n)` | Wegener Thm 4 (upper: `e·n·(ln n + 1)`); Hwang et al. 2018 for the exact expansion |
| **Any linear function, non-zero weights** | **Θ(n log n)**, tightly `e·n·ln n + O(n)`; **p = 1/n provably optimal** | Droste/Jansen/Wegener 2002 for O(n log n); **Witt 2013** for the tight form |
| **LeadingOnes** | **Θ(n²)**; upper `e·n²`, lower `n²/6 − o(n²)` | Wegener Thms 6, 7 |
| Unimodal with N+1 distinct values | ≤ `e·n·N` | Wegener Thm 6 |
| Degree-k with N positive weights | ≤ `e·n^k·N` | Wegener Thm 6 |
| Plateau of path length l | `O(n·l²)`; increasing path `Θ(n·l)`; SPP `O(n³)` | Wegener Thm 5 |
| **Shortcut-free long paths** | **Ω(l·n)**, exponential — *and the function is unimodal* | Wegener Thm 7 |
| Shortcut-admitting long paths | polynomial | Rudolph 1996 |
| **Trap** | **Θ(n^n)** — worse than exhaustive search | Wegener Thm 9 |
| Needle | exponential | ⚠️ exact form unverified; cite DJW 2002, *TCS* 276:51–81 |
| **Every pseudo-Boolean function** | ≤ `n^n` (universal upper bound) | Wegener, citing DJW 1998b |
| **Jump_m, m = ⌈log n⌉** | `n^Ω(log n)` without crossover; **`O(n³ log n)`** for a steady-state GA with population n and `p_c = 1/(n log n)` uniform crossover | Wegener Thm 10 = Jansen & Wegener 2002 |

The **e = 2.718…** factor throughout is the price of flipping each bit with probability 1/n rather than exactly one bit: `(1−1/n)^(n−1) → 1/e` is the probability a useful 1-bit mutation is not accompanied by a disruption.

## Witt 2013 — the field's most satisfying result

**Carsten Witt, "Tight Bounds on the Optimization Time of a Randomized Search Heuristic on Linear Functions," *Combinatorics, Probability and Computing* 22(2):294–318, 2013**, doi:10.1017/S0963548312000600. Verbatim:

> "We improve the previously best known bound… from (1.39+o(1))en ln n to **en ln n + O(n)** in expectation and with high probability, which is tight up to lower-order terms… **As a consequence, the standard mutation probability p = 1/n is optimal for all linear functions, and the (1+1) EA is found to be an optimal mutation-based algorithm.** Furthermore, the algorithm turns out to be surprisingly robust since the large neighbourhood explored by the mutation operator does not disrupt the search."

**The potential-function trick**, which is the pedagogically important bit (Wegener): "The asymptotically exact bound for linear functions has been obtained only by using a so-called **potential function** where it is quite likely that the value of the potential decreases in some steps… the (1+1)EA uses the fitness function f in order to decide whether the old search point is replaced with its mutant; **the people analyzing the (1+1)EA use the potential function p to measure the progress.**"

**And remarkably, one universal choice works for every linear function:** "Surprisingly, there is one special linear function serving as a potential function for all linear functions. This function is `p(x) = 2·(x_1 + ... + x_(n/2)) + 1·(x_(n/2+1) + ... + x_n)`. This potential function is somehow **a compromise between equal weights (ONEMAX) and very different weights (BV)**." He describes the proof as "involved and tedious."

## Why Trap is Θ(n^n) — the instructive part

The naive guess is wrong, and Wegener says why: "the initial search point has approximately n/2 ones and the probability that mutation creates the global optimum is approximately n^(−n/2). The expected waiting time… is approximately **n^(n/2) — only the square root of n^n.**" The three-phase "typical run" argument shows the algorithm is **driven away** from the n/2 region (it is optimising n − OneMax) before it can get lucky, reaching 0^n, from which only 1^n is accepted at probability n^(−n).

Also verified: "functions with Θ(n^n) expected time complexity for (1+1)-EA were constructed… while **a naive complete search requires only [O(2^n)]**." The (1+1) EA can be exponentially worse than exhaustive search.

## Unimodality buys nothing

Wegener Thm 7 gives **Ω(l·n)** for long path functions with `l = O(n^(1/2)·2^(n^(1/2)))` admitting no shortcuts, with the punchline: "Such a long path function… has been defined **proving that unimodal functions can be hard for the (1+1)EA**." Expected progress per step is bounded by `2/n + 2^(−Ω(n^(1/2) log n))`. **So the property that there is always an improving 1-bit move buys you nothing against an exponentially long path.**

The positive counterpart: **Rudolph, "How Mutation and Selection Solve Long-Path Problems in Polynomial Expected Time," *Evolutionary Computation* 4(2):195–205, 1996**, doi:10.1162/evco.1996.4.2.195 — "unimodal binary long-path problems can be solved by mutation and elitist selection in a polynomially bounded number of trials on average," because mutation can shortcut the path by flipping several bits at once. ⚠️ **Note the year and volume: 4(2), 1996 — Wegener's own text miscites it as "Rudolph (1997)."**

## Proof techniques

**The fitness-level method.** Wegener's Lemma 1: for a <_f-partition A₁ <_f … <_f A_m with `s_i` the minimum probability of escaping level i upward,

```
E(X_f) ≤ Σ_{1≤i≤m−1} s_i^(−1)
```

His own assessment: "The proof of Lemma 1 is very simple… Nevertheless, this result is **surprisingly powerful. However, it is crucial to choose an appropriate <_f-partition.**"

The matching lower-bound version (Lemma 2) uses the *maximum* escape probability, and he is honest about its weakness: "Lemma 2 is **less powerful** than Lemma 1. The reason is that we usually do not reach a global optimum from A_i." *That asymmetry is why tight lower bounds needed drift analysis and Sudholt's general lower-bound machinery.* Tail-bound extension: Witt, *Information Processing Letters* 114(1–2):38–41, 2014.

**Drift analysis** — the bridge from "converges" to a quantitative hitting time. Into EC via **He & Yao, "Drift analysis and average time complexity of evolutionary algorithms," *Artificial Intelligence* 127(1):57–85, 2001**, doi:10.1016/S0004-3702(01)00058-3 (**cite the erratum too**: 140(1–2):245–248, 2002). Then **multiplicative drift** (Doerr, Johannsen & Winzen, *Algorithmica* 64(4):673–697, 2012 — "This allows easier analyses in those settings where the optimization progress is roughly proportional to the current distance to the optimum"), variable drift and tail bounds (Doerr/Fouz/Witt GECCO 2011; Lehre & Witt, *CPC* 30(4):550–569, 2020). Modern treatment: **Lengler, "Drift Analysis," in Doerr & Neumann (eds.), *Theory of Evolutionary Computation*, Springer 2020, pp. 89–131.** ⚠️ The origin outside EC is Hajek's 1982 simulated-annealing work; the citation could not be verified.

**The "typical run" method.** Wegener on why expectations alone are not enough: "The behavior within one step or a few steps has a large uncertainty… The idea is to investigate search phases of well-chosen lengths… Runs of the (1+1)EA fulfilling the aims of all phases are called 'typical'. **The essential point is to prove an upper bound on the failure probability**, i.e., the probability of a non-typical run."

**The free-riders argument** for LeadingOnes lower bounds: once LO(x) = i, the suffix is a *random string*, so you get "free-riders" when its leading bits happen to be ones; a Chernoff bound shows more than 2n/3 free-riders during n/3 fitness-increasing steps has exponentially small probability, so you must wait for ≥ n/3 improving steps each of probability ≤ 1/n.

## Where crossover provably helps

**Jansen & Wegener, "The Analysis of Evolutionary Algorithms — A Proof That Crossover Really Can Help," *Algorithmica* 34(1):47–66, 2002**, doi:10.1007/s00453-002-0940-2.

The mechanism: "Uniform crossover on two individuals which have m zeros each and the zeros at different positions has a probability of exactly 2^(−2m) ≥ 1/n² to produce the global optimum 1^n… The expected waiting time increases to O(n³ log n) because of the small crossover probability. **This small probability simplifies the control of the hitchhiking effect.**"

**Note how weak the crossover rate has to be: `p_c = 1/(n log n)`.** The proof needs crossover to be *rare* so the population stays diverse — close to the opposite of GA folklore (p_c ≈ 0.6–0.9). And the hard part of the proof is exactly the diversity question: "Crossover and selection destroy the independency of the individuals of the initial population. It gets more likely that individuals share zeros."

Follow-ups: Jansen & Wegener, *Discrete Applied Mathematics* 149(1–3):111–125, 2005 ("where crossover provably is essential"); Watson & Jansen, GECCO 2007; and recently Opris, Sonntag & Sudholt, "A Royal Road Function for Permutation Spaces: an Example Where Order Crossover is Provably Essential," GECCO 2025, pp. 1631–1640.

**The (1+(λ,λ)) GA — a super-constant crossover speedup on a *natural* function.** Doerr, Doerr & Ebel, "From black-box complexity to designing new genetic algorithms," *Theoretical Computer Science* 567:87–104, 2015, doi:10.1016/j.tcs.2014.11.028.

The algorithm: from one parent, generate λ offspring by mutating at a *higher* rate k/n, pick the best as a "winner," then generate λ offspring by biased uniform crossover between parent and winner (bias 1/k), and take the best. **Mutation finds the right *number* of flips; crossover filters which flips were the good ones.**

Bound: `O(max{n log n/λ, λn})`, so λ = √(log n) gives O(n√(log n)) — **asymptotically better than the Θ(n log n) every mutation-only algorithm needs.** Since Witt 2013 proved the (1+1) EA optimal among *mutation-based* algorithms, the speedup must come from crossover. Doerr's own framing (arXiv:1604.01088): "**one of the few algorithms for which a super-constant speed-up through the use of crossover could be proven.**"

Tight version (Doerr & Doerr, arXiv:1506.05937, GECCO 2015): optimal `λ = Θ(√(log n · log log n / log log log n))` giving `Θ(n√(log n · log log log n / log log n))`. ⚠️ The widely cited result that a **self-adjusting λ** (one-fifth success rule) gives linear expected time Θ(n) on OneMax is from *Algorithmica* 80(5):1658–1709, 2018 — the paper is verified, the Θ(n) claim is not.

---

# Part 8 — Convergence results, and why they are nearly vacuous

**Günter Rudolph, "Convergence analysis of canonical genetic algorithms," *IEEE Transactions on Neural Networks* 5(1):96–101, 1994**, doi:10.1109/72.265964. ~1,500 citations. **The abstract states both results precisely, so quote it rather than paraphrasing:**

> "It is proved by means of homogeneous finite Markov chain analysis that **a CGA will never converge to the global optimum regardless of the initialization, crossover, operator and objective function.** But **variants of CGA's that always maintain the best solution in the population, either before or after selection, are shown to converge to the global optimum** due to the irreducibility property of the underlying original nonconvergent CGA."

**The negative result:** the canonical GA *without* elitism does not converge, for any initialisation, crossover operator or objective function. The chain is irreducible and aperiodic, so it has a unique stationary distribution with full support — the population keeps moving and there is always positive probability of leaving any state, including the optimal one.

**The positive result:** add elitism and you get convergence with probability 1, and the proof *uses* the irreducibility of the non-convergent chain — mutation gives every point positive probability, so the optimum is hit eventually, and elitism makes that absorbing.

**The general conditions:** elitism (the best-so-far is never lost) **plus** strictly positive mutation probability of reaching any point from any point (which bit-flip mutation with 0 < p_m < 1 gives, since `P(x → y) = p_m^H(x,y)(1−p_m)^(n−H(x,y)) > 0`).

## Why this is nearly vacuous in practice

**Those same two hypotheses are satisfied by pure random search with the best kept, and by random-restart hill climbing, and by essentially anything that can reach anywhere with positive probability.** Convergence-in-the-limit is therefore **not a discriminating property**: it separates "elitist with full-support mutation" from "not that," and nothing finer. No rate, no dependence on n, no comparison between algorithms.

That is precisely why the field moved to runtime analysis. **Θ(n log n) vs Θ(n²) vs Θ(n^n) are statements that *distinguish* algorithms and problems, and all three of those "converge."**

⚠️ This paragraph is a synthesis; no single quotable source states it. The honest supporting observation is structural: **the entire Doerr/Neumann/Witt/Jansen book literature is about expected runtime, not convergence, and Wegener's methods paper never mentions convergence-in-the-limit at all.**

## The continuous side

- **Rudolph, "Local convergence rates of simple evolutionary algorithms with Cauchy mutations," *IEEE TEC* 1(4):249–258, 1997** — a useful anti-folklore result, verbatim: "**the order of local convergence is identical for Gaussian and spherical Cauchy distributions, whereas nonspherical Cauchy mutations lead to slower local convergence.**" Heavy-tailed mutation does not by itself improve the local convergence order.
- **Jägersküpper** on the (1+1) ES with the 1/5-rule: ICALP 2003, LNCS pp. 1068–1079; FOGA 2005, LNCS 3469:260–281 (ellipsoidal landscapes); *Theoretical Computer Science* 361(1):38–56, 2006 (positive definite quadratic forms). ⚠️ **All texts were blocked and the exact results are unverified.** The attributed claim: on the sphere `f(x) = ‖x‖²` in ℝⁿ the (1+1) ES with the 1/5th success rule achieves **linear convergence order**, needing **Θ(n) evaluations per halving** of the distance to the optimum, hence Θ(n·log(1/ε)) for relative precision ε. **Present as attributed-but-unverified.**

**The structural contrast worth drawing:** on the continuous sphere the (1+1) ES with step-size adaptation is *linearly* convergent — a constant factor of progress per O(n) evaluations — whereas on discrete OneMax the (1+1) EA needs Θ(n log n) total because the last bits take Θ(n) attempts each (a coupon-collector tail). **Continuous and discrete runtime theory are genuinely different mathematical subjects**, and the 1/5 rule is one of the few folklore heuristics with a rigorous justification.

---

# Part 9 — Why EAs are hard to analyse

The locus classicus is **Beyer, Schwefel & Wegener, "How to analyse evolutionary algorithms," *Theoretical Computer Science* 287(1):101–130, 2002**, doi:10.1016/S0304-3975(02)00137-8. ⚠️ **Closed access, no abstract — content unverified. Do not put words in its mouth.**

**The one survey that could be read and quoted: Doerr & Neumann, "A Survey on Recent Progress in the Theory of Evolutionary Algorithms for Discrete Optimization," *ACM TELO* 1(4):1–43, 2021**, doi:10.1145/3472304; arXiv:2006.16709. Verbatim obstacle statements:

- **Distribution-valued state (EDAs):** "Due to the complicated nature of the underlying mathematical objects (**a random process taking probability distributions as states**), for a long time the theoretical understanding of these algorithms was very limited." And "lower bound proofs for EDAs are often very difficult."
- **Populations:** "The main line of works on upper bounds defines an **extremely complicated potential function on the populations** that is, most likely, not easy to transfer to problems not covered by these results." And in their Final Words: "**our understanding of the impact of populations, crossover operators, and diversity mechanisms still lags behind their practical success.**"
- **Dependence structure:** a first analysis of discrete differential evolution indicates "**our current methods cannot cope well with the complicated stochastic dependencies arising in this optimization process.**"
- **Adaptive parameters:** "the challenge is to define a suitable potential function on **the cross product of populations… and parameter values**" — only five works are known to do it.
- **§7.3 is literally headed "Challenge: Finding the Right Potential Function":** "What is less understood, and often still a challenge, is defining the right [potential function]… **this might be the biggest challenge in** [drift analysis]."
- **Constraints:** "understanding the behavior of evolutionary algorithms for linear functions even very special simple constraints is still a challenging task."

**The historical explanation**, verbatim from Sörensen, Sevaux & Glover: "The development of heuristic optimization algorithms… **is guided by experience, not theory. Early attempts to firmly ground the development of metaheuristics in theory have not delivered upon their promises.** Understanding the behavior of metaheuristics on a fundamental level has proven to be a difficult task."

⚠️ Two obstacles in common circulation have **no quotable verified source** and should be flagged as folklore-level claims: "stochastic process over an astronomically large state space" (though the structural evidence is real — Nix & Vose's exact chain has `C(n+2^l−1, n)` states) and "dependence on representation/encoding" (though Altenberg 1995/1997 and Jones 1995 on operator-dependent landscapes are the rigorous version of the point).

---

# The standard reference books

- **Neumann & Witt, *Bioinspired Computation in Combinatorial Optimization*, Springer 2010**, doi:10.1007/978-3-642-16544-3.
- **Auger & Doerr (eds.), *Theory of Randomized Search Heuristics*, World Scientific 2011**, doi:10.1142/7438 — contains the Whitley & Rowe NFL tutorial, pp. 255–287.
- **Jansen, *Analyzing Evolutionary Algorithms: The Computer Science Perspective*, Springer 2013**, doi:10.1007/978-3-642-17339-4.
- **Doerr & Neumann (eds.), *Theory of Evolutionary Computation*, Springer 2020**, doi:10.1007/978-3-030-29414-4 — chapters: 1 Doerr, Probabilistic Tools, 1–87; 2 Lengler, Drift Analysis, 89–131; 3 C. Doerr, Complexity Theory for Discrete Black-Box Optimization, 133–212; 6 Doerr & Doerr, Theory of Parameter Control, 271–321; 8 Sudholt, Benefits of Population Diversity, 359–404; 9 Krejca & Witt, Theory of EDAs, 405–442.
- **Doerr & Neumann, *ACM TELO* 1(4):1–43, 2021** — the best open-access survey.
- **Eiben & Smith, *Introduction to Evolutionary Computing*, 2nd ed., Springer 2015** — the theory chapter is **Ch. 16, pp. 231–244**.
