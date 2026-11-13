---
name: genetic-programming
description: "Genetic programming — evolving executable programs rather than parameter vectors — distilled from Koza's *Genetic Programming* (MIT Press, 1992) and its sequels, Poli, Langdon & McPhee's free *A Field Guide to Genetic Programming* (2008), and the primary literature, with every claim marked verified or flagged. Covers the tree representation over a function set and terminal set and the two requirements Koza named: **closure** (type consistency plus evaluation safety, hence protected division and the trick that makes it generate the constants 0 and 1) and **sufficiency** (the primitive set must be able to express a solution at all), with strongly typed GP as the alternative to closure; Koza's default tableau as actually stated (90% crossover / 10% reproduction, 51 generations, max depth 17, max initial depth 6, ramped half-and-half, the 90%-internal/10%-leaf crossover-point bias) and the correction that population 500 was never a fixed default; **bloat** — program growth without fitness return — with its four competing theories (replication accuracy, removal bias, the nature of program search spaces, and crossover bias pushing the size distribution toward a Lagrange distribution of the second kind) and the honest verdict that the field has no accepted unifying theory; the parsimony-pressure remedies (size and depth limits and the pathology of naive implementations, linear and covariant parsimony pressure with its closed-form coefficient Cov(l,f)/Var(l), lexicographic parsimony pressure, double tournament, the Tarpeian method, operator equalisation); the variants (grammatical evolution and its locality criticism, linear GP, Cartesian GP and the evidence that over 95% inactive genes maximises evolvability, PushGP, geometric semantic GP and its exponential growth, lexicase and epsilon-lexicase selection); the state of the art in symbolic regression from the SRBench benchmarks, where four of the top five black-box methods are GP-based; and how Koza's 'human-competitive results' claims actually held up (76 instances, 31 patent-related, per his own 2010 paper). Use whenever the thing being evolved is a program, expression, circuit, heuristic, grammar or symbolic model rather than a vector — symbolic regression, automatic heuristic design, evolving controllers or classifiers or circuits — when someone mentions GP, bloat, symbolic regression, PySR, Cartesian GP, grammatical evolution or lexicase selection, or when designing a primitive set and wondering what closure and sufficiency demand. Also the right background for LLM-guided program search (FunSearch, AlphaEvolve), which is structurally GP with a language model as the mutation operator."
---

# Genetic Programming

Evolving **executable programs** — syntax trees over a function set and a terminal set — rather than fixed-length parameter vectors. The representation change is the whole point: the output is a *readable artefact* you can inspect, simplify and learn from, which is why GP remains competitive in symbolic regression and heuristic design while most of evolutionary computation lost ground to gradients.

Part of the [[evolutionary-algorithms]] family. It is also the right background for [[evolutionary-algorithms]]'s LLM-guided frontier: FunSearch and AlphaEvolve are structurally GP with a language model as the mutation operator.

## Overlap with the evolutionary-algorithms hub — read this first

[[evolutionary-algorithms]] contains a **substantial genetic-programming section inside** `references/dialects.md` (~168 dense lines) covering closure and sufficiency, Koza's tableau, bloat and the four theories, the parsimony remedies and the variant landscape. **This skill is the deeper treatment, not a replacement** — markedly so on lexicase and epsilon-lexicase selection, symbolic regression and SRBench, and PySR. Use the hub's section for orientation and this skill when working in GP proper.

## The two requirements Koza named

**Closure** — "most function sets are required to have an important property known as closure (Koza, 1992), which can in turn be broken down into the properties of **type consistency** and **evaluation safety**."

- *Type consistency*: any subtree must be usable in any argument position of any function, because subtree crossover will eventually generate that combination. Usually enforced by making everything return the same type.
- *Evaluation safety*: commonly used functions fail at runtime — division by zero, `MOVE FORWARD` into a wall. Hence protected operators. The canonical protected division `%` returns 1 when the divisor is 0, and the Field Guide notes this is *deliberate*: it gives GP a cheap way to build the constant 1 via `(% x x)`, pairing with `(- x x)` for 0.

**Sufficiency** — the primitive set must be able to express a solution. `{AND, OR, NOT, x1..xN}` is always sufficient for Boolean induction; `{+, -, *, /, x, 0, 1, 2}` is *insufficient* because it cannot represent `exp(x)`. Sufficiency "can be guaranteed only for those problems where theory, or experience with other methods, tells us that a solution can be obtained." Adding a few unnecessary primitives costs little, "although there are cases where it can bias the system in unexpected ways."

**Strongly typed GP** (Montana, *Evolutionary Computation* 3(2):199–230, 1995) is the principled alternative to closure's type-consistency demand: the operators consult type information and never build an ill-typed tree.

## Koza's defaults, and one correction

Verified from Koza's own 1994 *Statistics and Computing* paper, which explicitly calls these his 1992 defaults: **90% crossover, 10% fitness-proportionate reproduction**; crossover points chosen **90% internal / 10% leaf** (his fix for crossover degenerating into leaf-swapping); **maximum depth 17** for crossover offspring and **6** for initial random programs; **51 generations** (generation 0 plus 50); ramped half-and-half initialisation at depth 2–6; fitness-proportionate selection throughout.

**Population 500 was not a fixed default.** Koza treats `M` as a *major, problem-specific* parameter and uses 300, 500, 1,000, 4,000, 8,000 and 10,000 across problems. The Field Guide says only "normally, the population size should be at least 500."

A nice illustration of received wisdom versus practice: ECJ's Koza parameter file reproduces the 90/10, depth-17 and ramped-2–6 values but refuses the selection scheme — "We use Tournament selection instead of Koza-style Fitness-proportionate selection because fitness-proportionate selection, well, is kinda icky."

## Bloat — and the honest state of its theory

**Bloat** is program growth *without significant return in fitness* — not growth as such. It matters because large programs are expensive to evolve and run, hard to interpret, and generalise poorly.

Any theory must satisfy the **size evolution equation**: for symmetric subtree-swapping crossover, "the mean program size evolves as if selection only was acting on the population." The four contenders:

1. **Replication accuracy** (McPhee & Miller 1995 — *not* Blickle & Thiele or Nordin & Banzhaf, who belong to the related introns strand): success depends on producing offspring functionally similar to the parent, so GP evolves bloated representations that raise replication accuracy.
2. **Removal bias** (Soule & Foster 1998): inactive code sits low in the tree, so excising it takes a smaller-than-average subtree while the inserted one is average — offspring keep parental fitness and grow.
3. **Nature of program search spaces** (Langdon & Poli 1997): above a threshold size the fitness distribution stops varying with size, and there are vastly more long programs, so drift favours growth.
4. **Crossover bias** (Dignum & Poli 2007; Poli, Langdon & Dignum 2007, EuroGP best paper): repeated subtree crossover pushes the size distribution toward a **Lagrange distribution of the second kind**, which puts heavy mass on very small programs; small programs are unfit, so selection against them raises the mean size.

**No theory has won.** The Field Guide: "we still lack a single, universally-accepted unifying theory to explain the broad range of empirical observations." Poli & McPhee, more bluntly: "While the jury remains out on the causes of bloat, practitioners still have the practical problem of combating bloat in their runs." What you *can* say is that crossover bias is the newest, the only one derived from and provably consistent with the exact size-evolution equation, and the one the 2012 survey of record foregrounds.

The remedy with the cleanest result is **covariant parsimony pressure** (Poli & McPhee, GECCO 2008): setting the penalty coefficient to **`c(t) = Cov(l, f) / Var(l)`** provably holds mean program size constant, and the paper demonstrates control within a single generation. The proof assumes fitness-proportionate selection; that it works unchanged under tournament selection is empirical.

## Where GP is actually state of the art

**Symbolic regression.** SRBench (La Cava et al., NeurIPS 2021 Datasets & Benchmarks, arXiv:2107.14351) assessed 14 SR methods and 7 ML methods on 252 problems. On the 122 black-box problems, **Operon is significantly most accurate, SBP-GP and FEAT rank second and third, four of the top five methods and six of the top ten are GP-based** — and the top SR models are one to three orders of magnitude *smaller* than the ensemble tree models they beat. On the ground-truth physics problems AI-Feynman recovers exact solutions 53% of the time with no noise, but **four other methods beat it above 0.01 noise**, suggesting it is brittle on real data. SRBench is alive and now has a 2025 edition with 25 methods.

**Automatic heuristic design** — and this is where the lineage runs into the present. FunSearch evolves a `priority` function and beat best-fit and first-fit on online bin packing; AlphaEvolve evolves marked regions of real codebases. Both are GP with an LLM as the variation operator (see [[evolutionary-algorithms]]).

## How Koza's "human-competitive" claims held up

His own 2010 open-access paper (GPEM 11:251–284) settles the counts: **76** human-competitive instances in Table 1 (the table has 77 rows, one subsumed), **31** recognised by the GECCO "Humies" awards, and **31** patent-related instances — 1 nineteenth-century, 21 twentieth-century, 7 twenty-first-century, plus **2 patentable new inventions**. GP IV (2003) claimed a different, smaller breakdown; attribute each number to its own source.

The honest assessment: GP is a real and in places leading tool in symbolic regression and heuristic design, but the "automated invention machine" framing did not become mainstream engineering practice, and the patent claims rest on a counting exercise by the method's principal advocate rather than on independent adoption. Note the pattern that recurs elsewhere: where GP-produced artefacts *were* independently scrutinised — GenProg's patches — most turned out to be functionality deletion.

## When to reach for this skill

When the thing being evolved is a **program, expression, circuit, heuristic, grammar or symbolic model** rather than a vector: symbolic regression, automatic heuristic or algorithm design, evolving controllers, classifiers or circuits. When someone mentions GP, bloat, symbolic regression, PySR, Operon, Cartesian GP, grammatical evolution, PushGP or lexicase selection. When designing a primitive set and wondering what closure and sufficiency actually demand. And as background whenever LLM-guided program search comes up.

## How to use this skill

- **`references/gp-core.md`** — the full reference: Koza's books and precursors; closure and sufficiency with verbatim definitions; the default tableau with its provenance and the population-size correction; the GP III/IV cluster hardware; bloat with all four theories, their citations and the size evolution equation; every parsimony remedy including covariant parsimony pressure's derivation and the Tarpeian method; the variants (grammatical evolution and the three corrections to its locality criticism, linear GP, Cartesian GP with the >95%-inactive-genes result and its four caveats, PushGP, geometric semantic GP with its doubling-per-generation growth and the pointer-based remedy, lexicase and epsilon-lexicase with their measured success rates); SRBench and the GECCO SR competitions; PySR; and the human-competitive counts.

## Related

- [[evolutionary-computation]] — the meta/router skill for this cluster, and the when-to-use gate that should run before any of it.
- [[evolutionary-algorithms]] — the generic loop and operators; and the FunSearch/AlphaEvolve frontier, which is GP with an LLM mutation operator.
- [[evolutionary-multiobjective]] — multi-objective size-vs-error is a standard bloat control.
- [[evolutionary-computation-theory]] — Poli's exact schema theory is what the size evolution equation comes from.
- [[compiler-construction]] — trees, grammars and type systems are the same objects GP manipulates.
- [[diagnosing-bugs]] — automated program repair (GenProg) and its critique are covered in the applications reference of [[evolutionary-algorithms]].
- Primary sources: Koza, *Genetic Programming: On the Programming of Computers by Means of Natural Selection* (MIT Press, 1992, ISBN 0-262-11170-5); Poli, Langdon & McPhee, *A Field Guide to Genetic Programming* (2008, ISBN 978-1-4092-0073-4) — free PDF mirror at `www0.cs.ucl.ac.uk/staff/W.Langdon/ftp/papers/poli08_fieldguide.pdf`, since `gp-field-guide.org.uk` is HTTP-only and often unreachable; Koza, GPEM 11:251–284, 2010 (DOI 10.1007/s10710-010-9112-3, open access); La Cava et al., arXiv:2107.14351. All web sources fetched 2026-11-11.
