# Operators and representation, with their real trade-offs

Choose the representation first, then derive operators that respect the problem's **heritable units**. Operators must also be able to reach any point in the space (ergodicity) if you want the only available convergence guarantee. Eiben & Smith ch. 5 (pp. 49–78) and ch. 6 (pp. 79–98) are the reference.

⚠️ marks what could not be verified against a source actually read. **This material was unusually hard to verify**: FOGA and ICGA proceedings from 1985–1997 are not in Crossref and the Morgan Kaufmann volumes are not openly hosted. What carried the work was Crossref's **publisher-deposited reference lists** (the single best lever for pre-DOI citations), K10plus library MARC records, Semantic Scholar's DBLP-derived pagination, archived DBLP tables of contents via the Wayback Machine, and author homepages. Several canonical operators below therefore have **verified citations but unverified mechanisms** — which is itself worth knowing.

---

## Binary, the Hamming cliff, and the Gray-coding result that runs backwards

In standard binary, adjacent integers can be maximally far apart in Hamming distance: the canonical example is **7 = 0111 and 8 = 1000**, which differ in all four bits, so moving between them requires four simultaneous flips — probability `p_m^4` under per-bit mutation. That discontinuity in the induced neighbourhood is the **Hamming cliff**. A **Gray code** guarantees consecutive integers differ in exactly one bit, so single-bit-flip mutation induces a locally connected neighbourhood over the integers.

**But Gray coding does not uniformly help, and the proven result is the opposite of what is usually stated.**

**Whitley, "A Free Lunch Proof for Gray versus Binary Encodings," GECCO 1999, pp. 726–733** (read in full, recovered as PostScript from `cs.colostate.edu/~genitor/1999/gecco99a.ps.gz`). The abstract, verbatim:

> *"A measure of complexity is proposed that counts the number of local minima in any given problem representation. A special class of functions with the **maximum possible number of optima** is also defined. A proof is given showing that **reflected Gray code induces MORE optima than Binary over this special class of functions**; by the No Free Lunch principle, **reflected Gray codes therefore induce FEWER optima over all other remaining functions**."*

So the **proven** direction is: Gray is *worse* on the maximally-multimodal class, and the NFL accounting then *forces* it to be better over everything else. The restricted class is the whole point, and the paper is explicit that there is no contradiction with NFL: *"over all functions in F, both Gray and Binary encodings produce all possible representations in R"*, with the identity `C(G,F_Q) + C(G,F̄_Q) = C(B,F_Q) + C(B,F̄_Q)`.

Definitions: `F̂` = wrapping neighbourhood (mod 2^L − 1, endpoints adjacent), `F` = non-wrapping; `F_Q` = functions with ≤ Q optima; `MAX = 2^(L−1)` is the maximum number of minima. Earlier results quoted from Whitley & Rana, "Representation, search and genetic algorithms," AAAI-97:

- **Theorem 1 (the Gray-Compactness Theorem)**: *"Let X be the number of local optima induced by a local neighborhood search operator over the bits in any Gray coded representation of any function in F. Let Y be the number of local optima induced under the neighborhood of the same function in F or F̂: **X <= Y**."*
- **Theorem 3**: for Q = 1, Gray induces fewer total minima than Binary over `F_Q` — with the corollary that **Binary is better over `F̄_Q` when Q = 1.**
- **The paper's own new result, Theorem 4**: *"For all discrete functions in F with bit representation of any length L, for **Q = MAX−1**, the set obtained using any Reflected Gray Coded representation for functions in F_Q induce fewer total minima than the set obtained using the Binary coded representation for functions in F_Q; this holds for both neighborhoods F and F̂."* Plus a conjecture: *"For every individual string in F^max the Gray code for that individual string induces more optima than the corresponding Binary encoding"* (proven empirically for L = 3, constructively for L = 4).

**The exhaustive 3-bit data (Table 1), verified as printed** — all 8! = 40,320 functions, wrapping case: K = 1 → 512 functions, Gray 512 minima vs Binary 960, Gray wins 448, Binary 0, ties 64; K = 4 → 2,176 functions, Gray 7,936 vs Binary 2,944, Gray wins 0, Binary 2,160, ties 16; **column sums both exactly 80,640** (the NFL identity), with **Gray winning 13,920 one-to-one comparisons vs Binary's 11,040, ties 15,360.** The paper calls this a **"MiniMax" difference** that Wolpert & Macready had speculated was possible: *"Gray can be somewhat better on many functions, while being much worse than Binary on a few functions."*

⚠️ **The paper never mentions the Hamming cliff** (grep-verified). Hamming-cliff claims belong elsewhere — the paper's own pointer is **Mathias & Whitley, "Transforming the Search Space with Gray Coding," IEEE ICEC 1994, pp. 513–518.** Also relevant: Whitley & Rowe, "Gray, Binary and Real Valued Encodings: Quad Search and Locality Proofs," 2005, doi:10.1007/11513575_2; and Whitley, Rana, Dzubera & Mathias, "Evaluating evolutionary algorithms," *Artificial Intelligence* 85(1–2):245–276, 1996, doi:10.1016/0004-3702(95)00124-7 (⚠️ its conclusions on Gray-vs-binary and its separability critique were not read; note Crossref's deposited author order differs from Whitley's own page — use Crossref).

---

## The general principle: locality

**Rothlauf, *Representations for Genetic and Evolutionary Algorithms*, 2nd ed., Springer 2006**, doi:10.1007/3-540-32444-5. The substantive readable text is Rothlauf, "On the Locality of Representations," Working Paper 1/2003, University of Mannheim (the peer-reviewed version is a 2-page GECCO 2003 poster).

**Definition**, verbatim: *"**The locality of a representation describes how well neighboring genotypes correspond to neighboring phenotypes.** … high if all neighboring genotypes correspond to neighboring phenotypes … low if some neighboring genotypes do not correspond to neighboring phenotypes."* Formalised as `d_m = Σ_{d^p(x_i,x_j) = d^p_min} |d^g(x_i,x_j) − d^g_min|`, with `d_m = 0` = perfect locality.

**Locality is not a property of the mapping alone** — metrics must be fixed on *both* spaces, and the genotypic metric is **induced by the search operator**. This matters: "low locality" is a statement about a (representation, operator) pair.

**The claim**, verbatim: *"**high-locality representations do not change problem difficulty. In contrast, low-locality representations randomize the search process and make problems that are easy for mutation-based search more difficult and difficult problems more easy.** Although low-locality representations increase the performance of local search on difficult, deceptive problems this is not relevant for real-world problems…"* Two caveats: the analysis is explicitly **mutation-based** search, and the mechanism is a three-class scheme (1 = easy/guiding, 2 = uncorrelated, 3 = deceptive) where low locality pushes **both** 1 → 2 and 3 → 2. His canonical low-locality example: **Prüfer numbers**.

**Redundancy** — Rothlauf & Goldberg, "Redundant Representations in Evolutionary Computation," *Evolutionary Computation* 11(4):381–415, 2003, doi:10.1162/106365603322519288: *"Representations are redundant if the number of genotypes exceeds the number of phenotypes… **synonymously redundant if the genotypes that represent the same phenotype are very similar to each other. Non-synonymously redundant representations do not allow genetic operators to work properly and result in a lower performance**"*; with synonymously redundant representations, performance depends on the modification of the initial supply, modelled as `O(2^{k_r}/r)` for population size and generations. *"The synonymity of redundant representations is related to the locality of non-redundant representations."*

⚠️ **Treat "the three elements are redundancy, scaling and locality" as unverified.** The theory chapter (Rothlauf, "Three Elements of a Theory of Representations," pp. 33–96) has no OA copy and neither 2003 working paper mentions scaling.

Variable-length representations raise the **positional / competing-conventions problem**, which is exactly what NEAT's innovation numbers solve (see `applications.md`).

---

## Permutation crossovers

**The problem:** one-point, k-point and uniform crossover on a permutation produce offspring with duplicated and missing elements — not permutations at all.

**The distinction that determines which operator to use:** **order-based** problems (e.g. scheduling, where *position* matters) vs **adjacency-based** problems (e.g. symmetric TSP, where *edges* matter). The right crossover differs, and conflating them is the commonest mistake.

Proceedings volumes, all verified from archived DBLP tables of contents: **1st ICGA 1985**, Pittsburgh, ed. Grefenstette, Lawrence Erlbaum, ISBN 0-8058-0426-9; **2nd ICGA 1987**, Cambridge MA, ed. Grefenstette, Erlbaum; **3rd ICGA 1989**, George Mason University, ed. Schaffer, Morgan Kaufmann; **4th ICGA 1991**, UC San Diego, eds. Belew & Booker, Morgan Kaufmann; **7th ICGA 1997**, East Lansing MI, ed. Bäck, Morgan Kaufmann.

### PMX (Partially Mapped Crossover)

Goldberg & Lingle Jr., "Alleles, Loci, and the Traveling Salesman Problem," 1st ICGA 1985, **pp. 154–159** (pages confirmed from the archived DBLP ToC). ⚠️ **Mechanism unverified** — the paper is not online and the 1st-ICGA volume is not scanned. The standard account, offered unverified: choose two cut points; copy the segment from parent 1 into the child **in place**; then for each element in parent 2's corresponding segment not yet in the child, place it at the position its displaced counterpart occupied, following the mapping chain defined by the two segments; fill remaining positions from parent 2 in order. **So PMX transmits position/order rather than edges.**

### OX / OX1 (Order Crossover) — resolved, and more interesting than either usual attribution

The IJCAI paper was read directly: **Davis (Texas Instruments), "Applying Adaptive Algorithms to Epistatic Domains," IJCAI-85, pp. 162–164** — pages established from the scan's running heads, which **contradicts ijcai.org's own index metadata ("162-163"); the scan wins.**

**The paper is about bin packing and graph colouring, not TSP, and the phrase "order crossover" never appears.** What it introduces is `MODIFIED-CROSSOVER`, verbatim: *"takes the first part of a solution, broken at random, and orders the rest of its members in accordance with their order in another solution. The list (3 1 2 6 4 5), for example, broken after its second member and crossed over with the list (4 1 6 5 2 3), yields the list (3 1 4 6 5 2)."*

**So the order-preserving principle is introduced here in one-cut-point form under the name MODIFIED-CROSSOVER; the two-cut-point OX/OX1 is its generalisation.** And the 1991 *Handbook of Genetic Algorithms* (Davis, Van Nostrand Reinhold, ISBN 0-442-00173-8) **cannot** be the original, because it postdates Oliver et al. 1987.

⚠️ **Flag the live attribution mess:** OX is variously credited to Davis 1985, Goldberg 1989 and Davis 1991. What Oliver/Smith/Holland themselves attribute to whom is unverified. Also worth naming: OX2 / order-based and position-based crossover (Syswerda 1991).

### CX (Cycle Crossover)

⚠️ **Note the initials: I. M. Oliver, D. J. Smith, J. R. C. Holland — NOT John Holland.** "A Study of Permutation Crossover Operators on the Traveling Salesman Problem," 2nd ICGA 1987, **pp. 224–230** (citation verified twice).

Mechanism (from a secondary source — Ellingsen et al., arXiv:2005.01113v1, which derives CX and cites Oliver et al.): CX works on **absolute positions** — compute the **cycles** of the permutation mapping parent a to parent b; for each cycle the offspring takes its positions entirely from a or entirely from b, so every city retains the absolute position it held in one parent and validity is automatic.

⚠️ **Their comparative PMX/OX/CX finding is unverified** — no DOI, no OA copy, and the Internet Archive scan's search-inside API returns 403. **The widely repeated "OX beat PMX by ~11% and CX by ~15%" could not be confirmed; do not print it as coming from the paper.**

### ERX (Edge Recombination)

Whitley, Starkweather & Fuquay, "Scheduling Problems and Traveling Salesmen: The Genetic Edge Recombination Operator," 3rd ICGA 1989, **pp. 133–140** (citation verified three ways). ⚠️ Whitley's *own* publication list omits this paper — its only 1989 entry is GENITOR. He does list the fuller account: Whitley, Starkweather & Shaner, "The Traveling Salesman and Sequence Scheduling: Quality Solutions Using Genetic Edge Recombination," in *The Handbook of Genetic Algorithms*, pp. 350–372, 1991.

⚠️ **Mechanism unverified** — neither text is online, and none of Whitley's three accessible survey PDFs describes edge recombination. Standard account, offered unverified: build an **edge/adjacency table** listing for each city the cities adjacent to it in *either* parent; grow one tour, at each step removing the current city from all adjacency lists and moving to the neighbour with the **fewest remaining unused edges**, ties broken randomly, with edges shared by both parents preferred in the enhanced variant; if the current list empties early the operator **fails locally** and must insert a "foreign edge" present in neither parent. **The design rationale is the important part: for TSP the edges are the meaningful heritable units, not the positions.**

⚠️ **Citation correction:** the 1991 comparison is Starkweather, McDaniel, Mathias, C. Whitley & D. Whitley, **"A Comparative Study of Genetic Sequencing Operators,"** 4th ICGA 1991, pp. 69–76 — *not* "A comparison of genetic sequencing operators." How "enhanced" ERX differs is unverified.

### EAX (Edge Assembly Crossover) — the one that is genuinely state of the art

Nagata & Kobayashi, "Edge Assembly Crossover: A High-Power Genetic Algorithm for the Travelling Salesman Problem," 7th ICGA 1997, **pp. 450–457**.

Mechanism, from a strong **Whitley-co-authored** secondary analysis (Heins, Whitley & Kerschke, arXiv:2505.00803v1, 2025): form the multigraph `G_AB = (V, E_A ∪ E_B)`; an **AB-cycle** is a cycle whose edges **alternate** between `E_A` and `E_B` (EAX generates them by randomly tracing alternating paths until one closes); an **E-set** is a set of AB-cycles applied to parent A, giving `E_C = (E_A \ (E_A ∩ E_AB^c)) ∪ (E_B ∩ E_AB^c)`. **The result need not be Hamiltonian** (*"may produce two or more disconnected subtours"*), so EAX **repairs** it — starting from the **smallest subtour**, delete one of its edges plus a nearby edge of another subtour and reconnect the four endpoints by the length-minimising pairing, with candidate partners restricted to the **10 nearest neighbours**, repeating until one tour remains. Stage I uses a single AB-cycle per offspring; Stage II combines several, classifying vertices A-/B-/**C- ("portals")**, with subtour count `m <= #C/2`, and runs a **tabu search (terminating after 20 iterations)** to drive `#C` down to 2.

Journal version: **Nagata & Kobayashi, *INFORMS Journal on Computing* 25(2):346–363, 2013**, doi:10.1287/ijoc.1120.0506. Abstract-level result: the GA *"outperforms state-of-the-art heuristic algorithms in finding very high-quality solutions on instances with up to 200,000 cities"* and *"achieves top performance **without using an LK-based algorithm**"*, via (i) localisation of EAX, (ii) local search inside EAX to pick good building-block combinations, (iii) a diversity-preserving selection model at negligible cost. ⚠️ Specific instance names, run times and success rates are unverified — the tables were unreachable (the paper is closed, no green copy anywhere, and the journal's supplementary code is gone per the author's own README). But see `applications.md` for the decisive verified fact: **Nagata's GA-EAX holds the World TSP record as of 17 October 2025.**

Also worth naming: the **inver-over** operator (Tao & Michalewicz 1998), and matrix / precedence-preserving crossovers for scheduling.

---

## Inversion is exactly a 2-opt move — a clean theorem

**Lin, "Computer Solutions of the Traveling Salesman Problem," *Bell System Technical Journal* 44(10):2245–2269, 1965**, doi:10.1002/j.1538-7305.1965.tb04146.x (free scan + OCR read at archive.org).

λ-optimality is defined as the impossibility of *"obtain[ing] a tour with smaller cost by replacing any lambda of its links by any other set of lambda links"* — so **a 2-opt move is by definition an exchange of exactly two edges.**

> **Theorem 3, verbatim:** *"The following properties of a tour are equivalent: (a) The tour is 2-optimal. (b) The tour is optimal relative to INVERSION; where by inversion we mean REVERSING THE ORDER OF A SET OF NEIGHBORING CITIES IN THE TOUR. (c) The tour does not intersect itself…"*

And in §III: *"Since the inversion-free tours are just the 2-opt tours…"*

**Symmetric scope is explicit** in Lin's own abstract: *"Two algorithms for solving the **(symmetric distance)** traveling salesman problem have been programmed…"* Lin credits the move to Croes: *"In his paper, 'A Method for Solving Traveling Salesman Problems', G. A. Croes applied a simple transformation, called 'inversion'…"* — Croes, *Operations Research* 6(6):791–812, 1958, doi:10.1287/opre.6.6.791.

Second citable source: Johnson & McGeoch, "The Traveling Salesman Problem: A Case Study in Local Optimization," in Aarts & Lenstra (eds.), *Local Search in Combinatorial Optimization*, Wiley 1997, pp. 215–310: *"The 2-Opt algorithm was first proposed by Croes [1958], although the basic move had already been suggested by Flood [1956]. **This move deletes two edges, thus breaking the tour into two paths, and then reconnects those paths in the other possible way.**"* And: *"a 2-Opt move may be viewed as **breaking the current tour into two segments, reversing one, and then gluing the tour back together**."*

⚠️ **"A swap of two cities changes up to four edges" is unverified as a quotation.** None of the sources read states the edge count. It is arithmetically plain (for non-adjacent i, j the four edges `(prev(i),i), (i,next(i)), (prev(j),j), (j,next(j))` are replaced; **for adjacent cities only three change**). The closest verified supporting quote is Johnson & McGeoch on the swap neighbourhood: *"Cerny [1985] also considered the simpler move in which the positions of two cities are interchanged but the segment between them is left unchanged, but experiments demonstrated that this was not as effective an approach."* The usual citation for the four-edge framing is Larrañaga, Kuijpers, Murga, Inza & Dizdarevic, *Artificial Intelligence Review* 13(2):129–170, 1999, doi:10.1023/A:1006529012972 — ⚠️ which could not be read (the sole green copy serves an Anubis challenge; no Wayback snapshot).

**Asymmetric-TSP subtlety — confirmed analytically, not sourced:** in an ATSP every internal arc of a reversed segment **flips direction**, so the cost delta involves `O(segment length)` terms rather than two, and **the inversion ⟺ 2-opt equivalence fails.** Lin's theorem is stated for the symmetric problem, which is the strongest textual support found. The standard citation, Kanellakis & Papadimitriou, *Operations Research* 28(5):1086–1099, 1980, is paywalled and its abstract does not state the reversal issue.

---

## Selection

### Fitness-proportionate / roulette wheel, and why it lost

`p_i = f_i / Σ_j f_j`. **The three real problems:**

1. **Premature convergence** when one individual's fitness dominates — a "super-individual" takes over the mating pool.
2. **Stagnation** when fitnesses are all similar late in the run: selection becomes nearly uniform random, so **selection pressure vanishes exactly when you need it.**
3. **It is not invariant to fitness transposition.** Adding a constant to every fitness **changes** the selection probabilities, so behaviour depends on the arbitrary scale and offset of your fitness function. **This is the deepest objection and the reason rank-based schemes won.**

Hence the fitness-scaling fixes: windowing, **sigma scaling** (`f'_i = max(f_i − (f̄ − c·σ_f), 0)` with `c ≈ 2`), linear scaling, power-law scaling. (Sigma scaling is what the Royal Road experiments used, at 1.5 maximum expected offspring.)

**The verdict to state: proportionate selection is scale-dependent and should generally be avoided.** Goldberg & Deb's own conclusion, p. 93: *"Proportionate selection is found to be significantly slower than the other three types"*; and p. 86: *"Other than the proportionate scheme, the methods compared in this paper all converge in something like O(log n) generations."* ECJ's Koza parameter file puts it more bluntly: *"We use Tournament selection instead of Koza-style Fitness-proportionate selection because fitness-proportionate selection, well, is kinda icky."*

### Linear rank selection

Eiben & Smith's parameterisation: `p(i) = (2 − s)/μ + 2i(s − 1)/(μ(μ − 1))` with `s ∈ (1, 2]`. Baker's citation: "Adaptive selection methods for genetic algorithms," ICGA 1985. An alternative printed form: `P(R_i) = (1/n)(sp − (2sp − 2)(i−1)/(n−1))`, where sp runs *"between 1.0 (no selection pressure) and 2.0 (high selection pressure)."* Exponential ranking: `P(i) = w^(n−i) / Σ_k w^(n−k)`, `0 <= w <= 1`.

### Tournament selection, and why it is the practical default

Pick k individuals uniformly at random (with or without replacement) and take the best; optionally with probability `p < 1`. **Three reasons it won, and they are all structural:**

1. **Selection pressure is tuned by a single intuitive integer k.**
2. **It only needs pairwise fitness *comparisons*,** so it is invariant to any strictly monotonic transformation of the fitness and **needs no scaling.** This is exactly the property proportionate selection lacks.
3. **It is O(1) per selection**, needs no global sort and no global sum, and parallelises and distributes trivially. (Goldberg & Deb's Table 3 complexity: roulette-wheel O(n²), stochastic universal O(n), **tournament O(n)**, Genitor with binary search O(n log n).)

### Takeover time — the actual results

**Goldberg & Deb, "A Comparative Analysis of Selection Schemes Used in Genetic Algorithms," in Rawlins (ed.), *Foundations of Genetic Algorithms*, Morgan Kaufmann, 1991, pp. 69–93**, doi:10.1016/B978-0-08-050684-5.50008-2 (full chapter scan read). FOGA-1 is the 1991 book of the 1990 workshop (*"FOGA/CS-90, held July 15-18, 1990, Indiana University, Bloomington"*).

**Table 2, "A Comparison of Takeover Time Values" (p. 86) — verified as printed:**

| Scheme | t* |
|---|---|
| Proportionate, x^c | `(1/c)(n ln n − 1)` |
| Proportionate, e^(cx) | `(1/c) n ln n` |
| Linear ranking, c₀ = 2 | `log n + log(ln n)` |
| Linear ranking (diff. eq.) | `(2/(c₀ − 1)) log(n − 1)` |
| Tournament, p | same as linear ranking with `c₀ = 2p` |
| **Tournament, s** | **`(1/ln s)[ln n + ln(ln n)]`** |
| Genitor | `(1/c₀) ln(n − 1)` |

- **Tournament**: the formula is verified exactly (their eq. 30), s = tournament size, n = population size, derived from `Q_{i,t+1} = Q_{i,t}^s ⟹ Q_{i,t} = Q_{i,0}^(s^t)`; described as *"an asymptotic expression that improves with increasing n."* Binary tournament is equivalent to linear ranking in expectation (`2p = c₀`).
- **Fitness-proportionate**: **O(n log n) is verified**, and it is O(n log n) for *both* assumed distributions — *"both a polynomially distributed function and an exponentially distributed function have the same computational speed of convergence."*
- **Linear ranking**: `a(x) = c₀ − c₁x` with `c₁ = 2(c₀ − 1)`; for `c₀ = c₁ = 2`, `t* = log n + log(ln n)` with — their own note — **log base 2 and ln natural.**
- Bonus: Table 1 growth ratios (tournament-s: early `φ = s`, late `φ = 2(1 − 2^(−s))`).

⚠️ **(μ,λ) truncation is NOT in this paper. The commonly quoted `t* = ln n / ln(λ/μ)` must not be attributed to Goldberg & Deb 1991.** The full text was grepped for "truncat", "mu", "lambda", "Schwefel", "Bäck": zero hits. The paper's own four schemes are *"1. proportionate reproduction; 2. ranking selection; 3. tournament selection; 4. **Genitor** (or 'steady state') selection"* — the fourth Table-2 row is **Genitor**, not truncation. The (μ,λ) takeover times are **Bäck's**: Bäck, "Selective pressure in evolutionary algorithms," ICEC'94, pp. 57–62; and Bäck, "Generalized convergence models for tournament- and (mu,lambda)-selection," ICGA'95. ⚠️ The formula itself is unverified — neither Bäck paper was readable.

### Selection intensity and loss of diversity — the better framework

**Blickle & Thiele, "A comparison of selection schemes used in evolutionary algorithms," *Evolutionary Computation* 4(4):361–394, 1996**, doi:10.1162/evco.1996.4.4.361. ⚠️ The typeset article is closed; what was read is **the authors' own final manuscript** (`ECfinal.ps`, "TeX output 1996.12.27", 77 pp, recovered from the Wayback Machine), cross-checked against Blickle's ETH dissertation No. 11894, Ch. 4. TIK-Report Nr. 11 (1995) was not read, so any 1995-vs-1996 differences are unverified.

**Definitions.** **Loss of diversity** D = *"the proportion of individuals of a population that is not selected"* (Baker's reproduction rate `RR = 100(1−D)`). **Selection intensity** `I = (M* − M)/σ`, standardised as the expected average fitness after applying the scheme to a Gaussian(0,1) population — **valid only for scale/translation-invariant schemes, i.e. all except fitness-proportionate.**

Closed forms (their Table 2):

```
Tournament             I_T(t) ≈ sqrt(2(ln t − ln sqrt(4.14 ln t)))
Truncation             I_Γ(T) = (1/T)(1/sqrt(2π)) e^(−f_c²/2),  f_c the (1−T) normal quantile
Linear ranking         I_R(η−) = (1 − η−)(1/sqrt(π))
Exponential ranking    I_E(κ) ≈ ln κ / (−2.548 − 1.086 sqrt(κ) + 0.4028 ln κ)
Fitness-proportionate  I_P = σ̄ / M̄
```

Exact tournament values (solvable only for `t <= 5`): `I_T(1)=0`; `I_T(2)=1/sqrt(π)`; `I_T(3)=3/(2 sqrt(π))`; `I_T(4)=(6/(π sqrt(π))) arctan sqrt(2)`; `I_T(5)=(10/sqrt(π))((3/(2π)) arctan sqrt(2) − 1/4)`. Approximation error *"less than **2.4%** for t in [2,5]"*, *"less than **1%**"* for t > 5. The exponential-ranking fit error is *"less than **1.81%**"*, and **was obtained by GP symbolic regression**. Linear ranking is parameterised `η− ∈ [0,1]` with `η+ = 2 − η−`, so its **maximum selection intensity is `I_R(0) = 1/sqrt(π) ≈ 0.56`** — **it cannot reach a tournament of size ≥ 3.**

**And the truncation equivalence, verbatim:** *"This method is equivalent to (mu, lambda)-selection used in evolution strategies with T = mu/lambda (Bäck, 1995)."*

**The selection-intensity-vs-tournament-size table (their Table 3), verified** — this is the table people actually want:

| I | 0.34 | 0.56 | 0.84 | 1.03 | 1.16 | 1.35 | 1.54 | 1.87 | 2.16 |
|---|---|---|---|---|---|---|---|---|---|
| tournament size t | – | 2 | 3 | 4 | 5 | 7 | 10 | 20 | 40 |
| linear ranking η− | 0.4 | 0 | – | – | – | – | – | – | – |
| truncation T | 0.8 | 0.66 | 0.47 | 0.36 | 0.30 | 0.22 | 0.15 | 0.08 | 0.04 |
| exp. ranking κ | 0.29 | 0.12 | 0.032 | 9.8e-3 | 3.5e-3 | 4.7e-4 | 2.5e-5 | 1e-9 | 2.4e-18 |

**Loss of diversity** (their Table 4): `D_T(t) = t^(−1/(t−1)) − t^(−t/(t−1))`; **`D_Γ(T) = 1 − T`**; `D_R(η−) = (1 − η−)/4` (max 1/4); `D_E(κ) = [1 − ln((κ−1)/(κ ln κ))]/ln κ − κ/(κ−1)`. *"About half the population is lost at tournament size t = 5"*; **tournament's D is independent of the initial fitness distribution.** Headline comparative claim, verbatim: *"**To achieve the same selection intensity more bad individuals are replaced using truncation selection than using tournament selection or one of the ranking selection schemes**"*; and *"Tournament and exponential ranking behave almost identical."* Their **Theorem 6.1**: linear ranking with `η− = 1/N` and tournament with `t = 2` have **identical expected fitness distributions** — sharper than Goldberg & Deb, who *"have also shown this result, but only for the behavior of the best fit individual."*

### The rest

**Truncation (μ, λ)**: take the top μ of λ. The response-to-selection / selection-intensity framework is Mühlenbein & Schlierkamp-Voosen, "Predictive models for the breeder genetic algorithm I," *Evolutionary Computation* 1(1):25–49, 1993 (the "breeder GA"). Common practice: sort by fitness and select the top 10%–50%.

**Stochastic universal sampling (SUS)**. Baker, "Reducing bias and inefficiency in the selection algorithm," ICGA 1987. **One** random offset in `[0, 1/λ)`, then λ **equally spaced pointers** over the cumulative fitness line. Same expectation as roulette but **minimum variance** — each individual gets either the floor or the ceiling of its expected count. *"Minimal spread and no bias."* Cost O(n).

**Boltzmann selection**: `p_i ∝ exp(f_i / T)` with a cooling T — **explicit annealing of selection pressure**: temperature starts high (low pressure) and is lowered, increasing pressure over the run while keeping diversity early. de la Maza & Tidor 1993; Mahfoud's analysis. ⚠️ Mechanism verified in outline only; no formula recovered from a primary source.

**Lexicase selection** — see `dialects.md`; it is the most interesting modern alternative, it needs only per-case comparisons, and it is the one scheme that deliberately selects **specialists**.

---

## Crossover

### Binary, and the two biases

- **One-point**: a random cut; bits to its right are swapped.
- **k-point / two-point**: *"two-point crossover is equivalent to performing two single-point crossovers at different points."*
- **Uniform**: each bit comes from either parent, typically `p = 0.5` per locus. Syswerda, "Uniform crossover in genetic algorithms," ICGA 1989.

**The real trade-off.** **One-point crossover has strong positional bias**: loci close together on the chromosome are much less likely to be separated, so **the arbitrary ordering of your genes on the string matters** — and that is also exactly why the schema theorem's `d(H)/(l−1)` term privileges "short" schemata, making **"building block" a property of the representation rather than of the problem.** **Uniform crossover has no positional bias but maximum distributional bias / disruption**: it separates every pair of loci with probability 1/2 regardless of distance. k-point sits between them.

### Real-valued

**Arithmetic / intermediate recombination** (whole, simple, single), and its **critical flaw**: it contracts the population into the **interior of the convex hull**, so variance collapses and the search cannot explore outside the initial convex hull. The standard fix is to let the mixing coefficient range **outside [0,1]**: *"alpha_i = alpha_{i,P1} · beta_i + alpha_{i,P2} · (1 − beta_i), with beta_i in [−d, 1 + d] drawn uniformly at random per gene i"*, with **d = 0.25 recommended**, citing Mühlenbein & Schlierkamp-Voosen (1993), *"because d = 0 tends to shrink allele values. The interval extends beyond the parents' range, so offspring can fall outside the hyperbody they span."* Intermediate recombination *"is used as a standard in evolution strategies"* (Schwefel 1995).

**BLX-α (Blend crossover).** Eshelman & Schaffer, "Real-Coded Genetic Algorithms and Interval-Schemata," in Whitley (ed.), *Foundations of Genetic Algorithms 2*, Morgan Kaufmann, **1993, pp. 187–202**, doi:10.1016/B978-0-08-094832-4.50018-0. ⚠️ **Year caveat:** Crossref and the IA catalogue say **1993** (*"2nd Workshop: Revised papers"*); Semantic Scholar and DBLP file it under 1992 (the workshop year). Cite the 1993 book.

⚠️ **The chapter itself could not be obtained. Everything below is secondary.** Operator definition from Herrera, Lozano & Verdegay, "Tackling Real-Coded Genetic Algorithms," *Artificial Intelligence Review* 12:265–319, 1998, verbatim: *"An offspring is generated: H = (h_1,…,h_i,…,h_n), where h_i is a randomly (uniformly) chosen number of the interval **[c_min − I·alpha, c_max + I·alpha]**, c_max = max(c¹_i, c²_i), c_min = min(c¹_i, c²_i), **I = c_max − c_min**."* The usual formulation (child uniform on `[min(p1,p2) − α·d, max(p1,p2) + α·d]` with `d = |p1 − p2|`) **matches this exactly**, including `α·d` on both sides — their symbol for the spread is I, not d. ⚠️ Whether the chapter itself writes it this way is unverified. They also note **BLX-0.0 = flat crossover** and **BLX-0.25 = Mühlenbein's extended intermediate crossover.**

**α = 0.5 and the reason** — the rationale is canonical and *is* verified as appearing in print, but ⚠️ not as the chapter's own wording. Herrera et al., p. 316: *"**Only when alpha = 0.5 a balanced relationship between the convergence (exploitation) and divergence (exploration) is reached, since the probability that an offspring shall lie outside its parents becomes equal to the probability that it shall lie between its parents.**"* The arithmetic is trivially checkable: at α = 0.5 the sampling interval has width 2I of which the parental sub-interval is I, so `P(inside) = P(outside) = 1/2`. ⚠️ Note the printed sentence begins *"all values alpha < 0.0 will demonstrate a tendency…"*, almost certainly a typo for α < 0.5 — reported as printed and flagged. ⚠️ **"α = 0.5 is the value they found best" is unverified**: no source read states that Eshelman & Schaffer experimentally *ranked* α values, and their test functions and baselines are entirely unverified — **do not print a function list for this paper.**

**SBX (Simulated Binary Crossover).** Deb & Agrawal, "Simulated Binary Crossover for Continuous Search Space," *Complex Systems* 9(2):115–148, 1995 (free PDF at `content.wolfram.com/sites/13/2018/02/09-2-2.pdf`). The abstract describes the Hamming cliff and limited precision of binary GAs, defines a crossover operator's **"search power"** as the probability of creating an arbitrary child from a pair of parents, and proposes SBX as *"a real-coded operator whose search power resembles single-point crossover in binary GAs"*, reporting that real-coded GAs with SBX performed as well as or better than binary GAs with single-point crossover, and that SBX *"is especially useful for problems with multiple optima and narrow global basins, or where the optimum's bounds are unknown."*

The **unbounded form** (the one usually quoted): spread factor `β_q = (2u)^(1/(η_c+1))` if `u <= 0.5`, else `(1/(2(1−u)))^(1/(η_c+1))`; children `c_{1,2} = 0.5[(1 ∓ β_q)p1 + (1 ± β_q)p2]`.

**The bounded form actually shipped**, verified from pymoo's source (`pymoo/operators/crossover/sbx.py`, read 2026-11-11) — **this is what every modern implementation does and it differs from the textbook formula.** For each variable with parent values `y1 < y2` and `δ = y2 − y1`:

1. compute a bound-aware spread β: for the lower child `β = 1 + 2(y1 − xl)/δ`; for the upper child `β = 1 + 2(xu − y2)/δ`.
2. `α = 2 − β^−(η+1)`; draw u uniform; then `β_q = (u·α)^(1/(η+1))` if `u <= 1/α`, else `β_q = (1/(2 − u·α))^(1/(η+1))`.
3. children `c1 = 0.5[(y1 + y2) − β_q·δ]`, `c2 = 0.5[(y1 + y2) + β_q·δ]`.
4. with probability `prob_bin`, swap the child assignments; clamp both to `[xl, xu]`.

Crossover is **skipped** for variables whose bounds are identical or whose parent values differ by `<= 1e-14`.

Behaviour of `η_c`: **large η_c ⟹ children near the parents**; `η_c ≈ 2–5` is exploratory; 15–20 is the usual default. **And the defaults disagree between libraries — see `practice.md`.**

Also: **UNDX**, **SPX**, **PCX** (parent-centric crossover, Deb et al.), and DE-style difference-vector recombination as the modern alternative (`dialects.md`).

### Does crossover actually help? The state of the argument

**The case against / for mutation-only:**

- The EP tradition rejects recombination **on principle** (`dialects.md`).
- Fogel & Atmar, "Comparing genetic operators with gaussian mutations in simulated evolutionary processes using linear systems," *Biological Cybernetics* 63(2):111–114, 1990, doi:10.1007/BF00203032. ⚠️ **Findings unverified from the primary text** — the abstract is elided by the publisher in both Crossref and S2, SpringerLink blocks non-JS clients, and it is not in PubMed. As read **from citing literature only**: the test problems were linear-equation solving, and the field reads it as "crossover does not have any competitive advantage over mutation except *when the degree of interactivity is zero*." **Mark that as secondary.**
- **Terry Jones — venue resolved, and the folklore reading of him is wrong.** From Jones's own archived publications page: "Crossover, Macromutation and Population-based Search," in **L. J. Eshelman, ed., *Genetic Algorithms: Proceedings of The Sixth International Conference* (ICGA 1995), Morgan Kaufmann, pp. 73–80.** ⚠️ **Not GP-95**; and the "SFI working paper" hypothesis is refuted — his 1995 SFI TRs are different papers. **ICGA proceedings have no DOIs — do not invent one.** An extended version is Part 3 (38 pp) of his dissertation, *Evolutionary Algorithms, Fitness Landscapes and Search*, PhD, University of New Mexico, March 1995 (supervisor Forrest).

  **What he actually claimed**, verbatim from his own abstract page: *"A simple method for testing the usefulness of crossover **for a particular problem instance** is presented. This allows the **identification of situations in which** crossover is apparently useful but is actually only producing gains that could be obtained, or exceeded, with macromutation and no population."*

  **So his contribution is a per-instance diagnostic, and the abstract contains no blanket claim that crossover is useless. Flag the folklore reading as wrong.** ⚠️ The exact operator construction, test suite and concluding sentences are unverified — the paper body was unobtainable. Well-attested secondary consensus on the construction: **one parent is taken from the current population, the other is generated at random from the whole search space.** ⚠️ The term "random respectful recombination"/"R3" was not found in ~100 citation contexts — **do not assert Jones used it.**
- ⚠️ **"Headless chicken" is Angeline's term, not Jones's.** From the Field Guide p. 16: *"Subtree mutation is sometimes implemented as crossover between a program and a newly generated random program; this operation is also known as 'headless chicken' crossover (**Angeline, 1997**)."* That citation: **Angeline, "Subtree crossover: building block engine or macromutation?", *Genetic Programming 1997: Proceedings of the Second Annual Conference*, pp. 9–17, Morgan Kaufmann** (no DOI; **Morgan Kaufmann, not MIT Press**). Do not conflate with the distinct Angeline, "Comparing subtree crossover with macromutation," *Evolutionary Programming VI*, pp. 101–111, 1997, doi:10.1007/BFb0014804.
- Eshelman & Schaffer's crossover-hillclimbing work; and the plain fact that ES practitioners regard **mutation** as primary and get excellent results.
- **NEAT's own ablation found crossover contributed least** of its four mechanisms: Nonmating 5,557 evals / 0% failure vs full NEAT 3,600 / 0%, against No-Growth 30,239 / 80% and Nonspeciated 25,600 / 25%.

**The case for:**

- **Jansen & Wegener's proof** that crossover helps on the Real Royal Road functions (*Algorithmica* 34(1):47–66, 2002) — but note this is an **existence proof on a constructed function**, not evidence about practical problems. The operator-level point worth carrying: **how weak the crossover rate has to be — `p_c = 1/(n log n)`** — because the proof needs crossover to be *rare* so the population stays diverse. That is close to the **opposite** of GA folklore (`p_c ≈ 0.6–0.9`).
- **Sudholt, "How crossover speeds up building-block assembly in genetic algorithms," *Evolutionary Computation* 25(2):237–274, 2017**, doi:10.1162/evco_a_00171. Headline, verbatim: on royal-road functions and OneMax, *"using crossover makes every (mu+lambda) genetic algorithm **at least twice as fast** as the fastest evolutionary algorithm using only standard bit mutation, up to small-order terms and for moderate mu and lambda."* The mechanism is the operator-level insight: *"**crossover is able to repair the disruptive effects of mutation in later generations**"*, which *"makes multibit mutations more useful"* and **shifts the optimal OneMax mutation rate upward.** So there *is* a rigorous, provable sense in which crossover assembles building blocks — **but the constant is a factor of ~2, not the dramatic speedup the BBH rhetoric promised, and it was established 28 years after Goldberg 1989.** ⚠️ The golden-ratio optimal mutation rate (~1.618/n) and the ~1.19 n ln n figure are unverified — elided as "[Formula: see text]" in the only reachable abstract, and 1.19 would imply ~2.28×, so it needs checking.
- **The (1+(λ,λ)) GA**, where crossover acts as a **repair mechanism** licensing a higher mutation rate — Doerr, Doerr & Ebel, *Theoretical Computer Science* 567:87–104, 2015.

**The practitioner synthesis: crossover pays when the problem genuinely decomposes into semi-independent sub-solutions AND the representation puts those sub-solutions in recombinable units** — which is why the success stories are linkage learning, EDAs, and EAX for TSP — **and is near-useless or harmful otherwise.**

### Linkage learning — the constructive response

- **Thierens & Bosman, "Optimal mixing evolutionary algorithms," GECCO 2011, pp. 617–624**, doi:10.1145/2001576.2001661. ⚠️ **Nuance:** it introduces **two** algorithms — **ROMEA** (Recombinative Optimal Mixing EA, *one* donor for all subsets) and **GOMEA** (Gene-pool Optimal Mixing EA, *a fresh donor per subset*). Do not write it as if GOMEA were the sole contribution.
- **The GOM operator**, from a description co-authored by Thierens and Bosman themselves (Dushatskiy, Virgolin, Bouter, Thierens & Bosman, *Evolutionary Computation* 32(4):371–397, 2024, doi:10.1162/evco_a_00338, §III.B): GOM *"integrates selection and variation and has many similarities with greedy search algorithms"* — it loops over the FOS (family-of-subsets) linkage subsets, and for each subset **overwrites** that subset's variables from a donor drawn at random from the population; *"**If this overwriting action does not cause the fitness of the solution to become worse, the copy action is accepted. Otherwise, the donor material is rejected and the action is undone.**"* The all-variables root of a linkage tree is skipped. Variants: Exhaustive Donor Search; a **Forced Improvements** phase (donor forced to be the elitist) when no subset produced a change.
- Reference chain, all Crossref-verified: the linkage tree model — Thierens, "The Linkage Tree Genetic Algorithm," PPSN XI, pp. 264–273; **the commonly benchmarked "LT-GOMEA" is Bosman & Thierens, "Linkage neighbors, optimal mixing and forced improvements in genetic algorithms," GECCO 2012, pp. 585–592**, doi:10.1145/2330163.2330247 (per Hsu & Yu: *"LT-GOMEA stands for the version with forced improvements, implemented by the inventors of GOMEA"*); Thierens & Bosman, GECCO 2013, pp. 877–884; **RV-GOMEA** = Bouter, Alderliesten, Witteveen & Bosman, GECCO 2017, pp. 705–712.
- ⚠️ **DSMGA-II title resolved:** Hsu & Yu, "Optimization by Pairwise Linkage Detection, Incremental Linkage Set, and Restricted / Back Mixing: DSMGA-II," GECCO 2015, **pp. 519–526**, doi:**10.1145/2739480.2754737** (Crossref stores "DSMGA-II" as the *subtitle*). "A optimization approach for the dependency structure matrix genetic algorithm" corresponds to **no record found** — drop it.
- **One concrete verified performance claim — use this one.** From Hsu & Yu's Table 1 / §4.2: on **concatenated deceptive trap, k = 5, l = 400 bits** (80 trap-5 subfunctions), measuring function evaluations at the NFE-minimising population size, requiring 10 consecutive successful hits of the global optimum, averaged over 100 runs: **DSMGA-II ≈ 54,000 NFE** (~36,000 under a 1-hit criterion) vs **P3 ≈ 71,000 NFE**. Same table: **folded trap (bipolar, k = 6), l = 240 → DSMGA-II 134k vs P3 6,831k (~51×)**; cyclic trap k = 5, l = 400 → 125k vs 143k; NK-S1 l = 400 → 877k vs 1,900k. ⚠️ **Any O(n^1.x) scaling exponent is unverified** — the paper reports log-log plots, not fitted exponents. **Do not state one.**
- Head-to-head (Dushatskiy et al. Tables 3/5, median NFE over 50 runs, /10⁵, Trap55): at l = 640 — GOMEA 4.02, **DSMGA-II 1.30**, GOMEA_BEST 1.16; at l = 1280 with population management — P3 2.72, **DSMGA-II 31.10**, CGOMEA-P3BEST 1.61 (~19× for CGOMEA). ⚠️ This is the 2021 arXiv v1 and may differ from the 2024 journal version.
- Theory bonus: Qiao & Gallagher, GECCO 2024 Companion, arXiv:2407.08335 — GOMEA **with a truthful linkage model** solves concatenated trap in **O(m³ 2^k)** w.h.p. vs **O(ln(m)(mk)^k)** for the (1+1) EA. ⚠️ Third-party, and it **assumes** the marginal-product FOS is given — say so when quoting.

---

## Mutation

### Bit-flip and the 1/L rule

`p_m = 1/L` (L = string length) gives on average **one flipped bit per offspring**. **This one has genuine theoretical backing, unlike most EA folklore.**

- Droste, Jansen & Wegener, "On the analysis of the (1+1) evolutionary algorithm," *Theoretical Computer Science* 276(1–2):51–81, 2002 — the (1+1) EA with mutation rate 1/n optimises OneMax and every linear function in `Θ(n log n)` expected evaluations.
- The tight result: **Witt, "Tight Bounds on the Optimization Time of a Randomized Search Heuristic on Linear Functions," *Combinatorics, Probability and Computing* 22(2):294–318, 2013** (⚠️ **not** *Algorithmica*), whose abstract states verbatim: *"**As a consequence, the standard mutation probability p = 1/n is OPTIMAL for all linear functions, and the (1+1) EA is found to be an optimal mutation-based algorithm.**"* **That is as good as parameter advice gets in this field.**

⚠️ Earlier empirical arguments for 1/L — Mühlenbein, PPSN II 1992, and Bäck, ICGA 1993 — are unverified; neither is in Crossref (pre-DOI proceedings).

**The modern refinement: a non-static, heavy-tailed rate is better in general.** Doerr, Le, Makhmara & Nguyen, "Fast Genetic Algorithms," GECCO 2017, arXiv:1703.03334. The paper argues *"the standard mutation rate of 1/n is not always best for multimodal functions"*, shows that for the (1+1) EA on jump functions **larger** rates greatly reduce runtime, and proposes a **heavy-tailed rate α/n with α drawn from a power-law distribution**. Verified claims: for `jump_{m,n}`, *"any mutation rate between 2/n and m/n gives a speed-up at least **exponential in m** over the standard 1/n"*; the rate `m/n` gives the best asymptotic runtime, a **super-exponential** speed-up in m, *"but it is very sensitive. A small (1±eps) change in the rate can cause a slowdown exponential in m"*; and with the heavy-tailed rate the (1+1) EA finds the optimum of **any** `jump_{m,n}` *"in time only a small polynomial factor in m above the optimal fixed rate's time"*, with similar speed-ups for **vertex cover** in bipartite graphs and **matching** in general graphs. ⚠️ **The paper does not state a value for the power-law exponent β** — the commonly cited β = 1.5 is unverified from this source.

Also: the self-adjusting 1/5-rule-style rate of Doerr, Gießen, Witt & Yang, "The (1+λ) Evolutionary Algorithm with Self-Adjusting Mutation Rate," *Algorithmica* 81(2):593–631, 2018.

### Real-valued

- **Uniform** mutation.
- **Gaussian / normal**: `x' = x + N(0, σ)`, and the whole step-size problem that the 1/5 rule, self-adaptation and CMA-ES exist to solve.
- **Cauchy**: fat tails for escaping local optima. Yao, Liu & Lin, *IEEE TEVC* 3(2):82–102, 1999 — the FEP result. **But note the anti-folklore counterpoint:** Rudolph, "Local convergence rates of simple evolutionary algorithms with Cauchy mutations," *IEEE TEVC* 1(4):249–258, 1997: *"The results show that **the order of local convergence is IDENTICAL for Gaussian and spherical Cauchy distributions, whereas nonspherical Cauchy mutations lead to SLOWER local convergence.**"* **So heavy-tailed mutation does not by itself improve the local convergence order.**
- **Polynomial mutation** (Deb & Goyal 1996; Deb & Deb 2014) with distribution index `η_m`. The formula **as shipped**, from pymoo's source (`pymoo/operators/mutation/pm.py`): with `δ1 = (x − xl)/(xu − xl)`, `δ2 = (xu − x)/(xu − xl)`, `mut_pow = 1/(η + 1)`, and r uniform on [0,1]:

  ```
  if r <= 0.5:  δq = (2r + (1 − 2r)(1 − δ1)^(η+1))^mut_pow − 1
  else:         δq = 1 − (2(1−r) + 2(r − 0.5)(1 − δ2)^(η+1))^mut_pow
  ```

  then `y = x + δq(xu − xl)`, clipped to `[xl, xu]`; variables with `xl == xu` are never mutated. Defaults `prob=0.9, eta=20` — **see `practice.md` for the important subtlety about what that `prob` means.**

### Permutation

Swap/exchange, insert/move, scramble, and **inversion/reversal**.

**The crucial point, and it is a theorem** (above): for a symmetric TSP with a path/array representation, **reversing a contiguous subsequence changes exactly two edges and is therefore precisely a 2-opt move** (Lin 1965, Theorem 3), whereas a swap of two cities changes up to four. **So inversion is the natural mutation for adjacency-based problems and swap for order-based ones — the same distinction that governs the crossover choice.**

GP: subtree mutation, point/node mutation, hoist (child always smaller), shrink, permutation — see `dialects.md`.

---

## Parameter control — the taxonomy, with two corrections

**Eiben, Hinterding & Michalewicz, "Parameter control in evolutionary algorithms," *IEEE TEVC* 3(2):124–141, 1999**, doi:10.1109/4235.771166 — winner of the 2001 IEEE TEC Outstanding Paper Award. ⚠️ Full text read in the author's **preprint** (it contains "INSERT FIGURE 1 HERE"), so do not cite page numbers from it; the published scan is at `macs.hw.ac.uk/~dwcorne/Teaching/param.pdf`.

**Top-level distinction**, verbatim: *"we distinguish two major forms of setting parameter values: **parameter tuning** and **parameter control**. By parameter tuning we mean … finding good values for the parameters BEFORE the run … which remain FIXED during the run. … Parameter control … amounts to starting a run with initial parameter values which are CHANGED DURING THE RUN."*

**The three control categories**, verbatim:

- **Deterministic** — *"the value of a strategy parameter is altered by some deterministic rule … WITHOUT USING ANY FEEDBACK FROM THE SEARCH"*, usually a time-varying schedule.
- **Adaptive** — *"there is SOME FORM OF FEEDBACK FROM THE SEARCH that is used to determine the direction and/or magnitude of the change"*, possibly involving credit assignment.
- **Self-adaptive** — *"the parameters to be adapted are ENCODED INTO THE CHROMOSOMES and undergo mutation and recombination"*, so better values propagate by selection.

The paper itself offers the cleaner labels: *"the terms 'adaptive' and 'self-adaptive' could be replaced by the equally meaningful **'explicitly adaptive' and 'implicitly adaptive'**."* It also concedes *"it is not determinism that matters, but the fact that the parameter-altering transformations take no input variables related to the progress of the search … The name **'fixed' parameter control** might form an alternative."*

⚠️ **Correction 1: what is adapted is SIX components, not five** — verbatim: *"representation, evaluation function, variation operators (mutation and recombination), **SELECTION, REPLACEMENT**, and population."* **Parent selection and survivor/environmental selection are separate entries.** (Their survey has 7 subsections only because variation is split into mutation and recombination *"purely by the amount of work."*)

⚠️ **Correction 2, a nuance usually lost in secondary accounts: the paper explicitly demotes scope/level and evidence from the taxonomy.** On scope: *"the scope/level feature is a SECONDARY one, usually depending on the given component and its actual implementation … the notion of scope can be ill-defined and very complex."* On evidence: *"this is a meaningful distinction, [but] it appears ONLY IN ADAPTIVE parameter control … we have NOT INCLUDED IT as a major classification criterion."* Final statement, verbatim: *"**Our classification is thus two-dimensional: the type of control and the component of the evolutionary algorithm which incorporates the parameter.** The type and component entries are **orthogonal**."*

### The 2015 follow-up, and its verdict is negative

**Karafotias, Hoogendoorn & Eiben, "Parameter control in evolutionary algorithms: trends and challenges," *IEEE TEVC* 19(2):167–187, 2015**, doi:10.1109/TEVC.2014.2308294 (full text read).

On the 1999 taxonomy: it *"presented a unifying vision, a clear taxonomy … that were **quickly adopted and became the de facto standard in the field**"*, restated crisply as *"**Deterministic methods are uninformed … Adaptive methods are informed … Self-adaptive methods encode parameter values in the genome**."* They float one re-framing: *"**shift the main 'water shed' from tuning vs. control to blind (tuning and deterministic) vs. informed (adaptive and self-adaptive)**."*

**Headline conclusion, verbatim, and it is negative:** *"we can note a **disappointing lack of impact**. … **no parameter control method or strategy has been widely adopted by the community or has became part of the common practice toolkit** … Perhaps this is caused by the **lack of convincing evidence of the added value** … All too often, such a paper (including ours!) has a limited scope."* And: *"**controlling EA parameters on-the-fly is still a rather esoteric option, with self-adaptation in evolution strategies being the exception that confirms the rule.**"* Bibliometrically, variation operators get by far the most attention; population parameters less; selection least.

**Open challenges (§VII.B):** (1) the **"patchwork problem"** — *"little is known about the joint effects of control mechanisms"*, so any multi-parameter mix is ad hoc; (2) identify relevant EA behaviour descriptors/observables; (3) characterise the **niche** for control vs tuning — *"a lack of experimental data … and – even more importantly – a lack of a decent research methodology"*, with the tentative answer that **tuning pays for repetitive problems and control is the choice for one-off problems, dynamic fitness functions, and on-line adaptation** e.g. robotics; (4) agree on sound measures of **effort** (tuning cost is pre-run, control overhead is in-run, and evaluation counters hide the controller's own work); (5) benchmarking baselines — including **a blind controller that varies parameters randomly**; (6) study the parameters **of** the control mechanisms — *"there is little real evidence to back up [the] belief [that the extended system is less sensitive], with the sigmas and taus in evolution strategies being the only well-known exception"*; (7) understand **why** mechanisms work; (8) borrow from reactive/local search. Their taxonomy of adaptive mechanisms actually in use: feedback formulas, event/threshold rules, fuzzy controllers, adapted value sets, **multi-armed bandits** (Adaptive Operator Selection), and full RL.

---

## Survivor selection, elitism, and the comma/plus consequences

**Generational** (whole population replaced; generational gap = 1) vs **steady-state** (one or a few replaced per step). Replacement policies: replace-worst, replace-oldest (FIFO), replace-random, replace-parent, and **deterministic crowding / restricted tournament replacement** (replace the most **similar**), which is the diversity-preserving option.

### Elitism

Without it the best-so-far can be **lost** and the algorithm has no monotonicity at all; De Jong's observation stands: *"it is quite possible for the best individual to never appear or appear and then disappear from the population forever."* **And it is a precondition of the only non-trivial convergence guarantee available**: an elitist EA with everywhere-positive mutation converges to the global optimum with probability 1, whereas the canonical GA **without** elitism does not — **Rudolph, "Convergence analysis of canonical genetic algorithms," *IEEE Trans. Neural Networks* 5(1):96–101, 1994**, doi:10.1109/72.265964 (both directions proved).

**The cost:** elitism raises selection pressure and can accelerate premature convergence. Practical rule: **1–2 elites, not 20% of the population.** Also note that the standard way of *using* a GA as an optimiser is itself a form of **external** elitism — keep a hall-of-fame of the globally best individual regardless of whether it is in the current population, treating *"the population as a database (an accumulating world model) of samples."*

### (μ + λ) vs (μ, λ)

**Plus** is elitist and monotone, but (a) can get stuck, and (b) **cannot discard a bad self-adapted step size**: an individual carrying a maladapted σ survives as long as its objective value is good, because plus-selection never asks about σ. **Comma** is non-elitist: it can walk away from a local optimum, it **forgets**, and it is the standard choice when step sizes are self-adapted.

**And the often-missed point: under noise, plus-selection latches onto lucky over-estimates. The literature has a name for it — overvaluation.**

**Arnold & Beyer, "Local performance of the (1+1)-ES in a noisy environment," *IEEE TEVC* 6(1):30–41, 2002**, doi:10.1109/4235.985690 ("overvaluation" is one of its four keywords). Verbatim from §2.1:

> *"With selection based on **perceived fitness** rather than on **ideal fitness**, a parent with a perceived fitness that is much higher than its ideal fitness is **likely to persist for many generations**. Conversely, an offspring with a perceived fitness that is lower than its ideal fitness is likely not to be accepted at all … As a consequence, after several iterations of the mutation-selection mechanism, the **perceived fitness of the parent is likely to be higher than its ideal fitness**. The discrepancy … is in what follows referred to as the **degree of overvaluation**."*

On scope: *"systematic overvaluation is a phenomenon resulting from the **failure to reevaluate the parental fitness**, and … qualitatively similar effects can be observed … **if noisy fitness values can survive for more than a single generation**."*

⚠️ **Important caveat — do not cite this paper for "elitism is harmful."** On the infinite-dimensional noisy sphere it concludes the **opposite**: *"the strategy which does not reevaluate the parent **achieves a greater expected fitness gain per generation and prevents the deterioration of the quality of the solution for high noise strengths**"*; *"**positive overvaluation raises the bar for an offspring to be accepted, preventing the strategy from making steps purely due to noise**."* The genuine costs it identifies are **reduced success probabilities, long periods of stagnation, and the breakdown of success-probability-based step-size adaptation** (i.e. **the 1/5 rule stops working**), with **occasional reevaluation preferable to either extreme.**

The generalised statement of the harm, in Arnold & Beyer's own words (Dortmund SFB 531 report "Noisy Optimization with Evolution Strategies"): *"**Those candidate solutions that have a measured fitness that exceeds their ideal fitness are more likely to survive selection than those that are undervalued. In the course of the search, overvaluation builds up and can lead to stagnation of the search** … **The same effect can be observed for all optimization strategies where search points can persist indefinitely. Periodic reevaluation of surviving candidate solutions may be required for achieving stochastic linear convergence.**"*

The cleanest short published sentence in the avoid-elitism framing: **Hansen, Niederberger, Guzzella & Koumoutsakos, *IEEE TEVC* 13(1):180–197, 2009**, doi:10.1109/TEVC.2008.924423, §III-A: *"CMA-ES is a **non-elitist** … algorithm. **Non-elitism avoids systematic fitness overvaluation on noisy objective functions [5], because even solutions with (erroneously) exceptionally good fitness values survive only one generation.**"*

**Honest nuance to carry: "elitism is harmful under noise" is the downstream practitioner's reading (Hansen et al.) of a source result (Arnold & Beyer 2002) that is genuinely two-sided.** ⚠️ Candidates whose content stayed unverified: Beyer, "Evolutionary algorithms in noisy environments," *CMAME* 186(2–4):239–267, 2000 — the most likely home for an explicit "avoid elitist selection under noise" recommendation; and Jin & Branke, *IEEE TEVC* 9(3):303–317, 2005.

### Two classical algorithms still worth knowing

**CHC** — Eshelman, "The CHC Adaptive Search Algorithm: How to Have Safe Search When Engaging in Nontraditional Genetic Recombination," in Rawlins (ed.), *Foundations of Genetic Algorithms*, Morgan Kaufmann, 1991, **pp. 265–283**, doi:10.1016/B978-0-08-050684-5.50020-3 (whole 19-page chapter read). The paper's own keyword line: *"cross-generational competition, elitist selection, implicit parallelism, uniform crossover, incest prevention, restarts."*

⚠️ **Correction worth flagging: the chapter never expands the acronym "CHC."** Grepping the full text for "cross generational elitist", "heterogeneous" and "cataclysmic" returns **zero hits**. The familiar gloss (Cross-generational elitist selection / Heterogeneous recombination / Cataclysmic mutation) is a **later back-formation** — do not attribute it to FOGA 1991. The paper calls the crossover **HUX**, the restart *"divergence/reinitialization"*, and the selection *"population-elitist selection."*

1. **Cross-generational elitist selection**, verbatim: *"**the members of P(t−1) and C'(t) are merged and ranked according to fitness, and P(t) is created by selecting the best M … members of the merged population.** (In cases where a member of P(t−1) and a member of C'(t) have the same fitness, the member of P(t−1) is ranked higher.) I shall call this procedure … **population-elitist selection** since it guarantees that the best M individuals seen so far shall always survive."* Mating is **unbiased** — every parent is copied to the mating pool and randomly paired. And crucially: *"**mutation is not performed at the recombination stage.** Rather, diversity is maintained (or more precisely, reintroduced) by partial population randomization whenever convergence is detected (restarts)."*
2. **HUX**, verbatim: *"CHC uses a modified version of UX, HUX, that **crosses over exactly half the non-matching alleles** (what Booker (1987) calls the reduced surrogate), **where the bits to be exchanged are chosen at random without replacement**. HUX guarantees that the children are always the maximum Hamming distance from their two parents."*
3. **Incest prevention**, verbatim: *"the Hamming distance between potential parents is calculated, and if **half that distance** … does not exceed a **difference threshold**, they are not mated … (**The difference threshold is set at the beginning of the run to L/4** — half the expected Hamming distance between two randomly generated strings.) … **Whenever no children are accepted into the parent population … the difference threshold is decremented.**"*
4. **Restart / 35% divergence**, verbatim: *"**The population is reinitialized by using the best individual found so far as a template** … Each new individual is created by **flipping a fixed proportion (e.g., 35%) of the template's bits chosen at random without replacement. One instance of the best individual is added unchanged to the new population.**"* Trigger: *"mutation [is introduced] only when the population has converged or search has stagnated."* Parameters used: *"a population size of 50 and a divergence rate of 35%."* ⚠️ **Extra detail most accounts omit** — the Appendix pseudocode **resets the threshold after a restart** to `d = r(1.0 − r)L`, i.e. with r = 0.35 that is **0.2275·L, not back to L/4.** Sensitivity: mean evaluations 7196 / 6207 / 6170 for divergence rates 0.35 / 0.25 / 0.15.

   Empirical setup: 10 functions from Schaffer et al. (1989), with the GA given its 5 best of 840 tuned parameter sets per function vs CHC's single setting — **the paper itself flags *"a methodological bias in favor of the traditional GA"*** — CHC 50/50 on F1–F8; and **it names two classes where CHC loses**: functions easy for a robust hillclimber, and tightly ordered (benign) deceptive functions.

**GENITOR** — Whitley, "The GENITOR Algorithm and Selection Pressure: Why Rank-Based Allocation of Reproductive Trials is Best," in Schaffer (ed.), *Proc. 3rd ICGA*, 1989, **pp. 116–121** (citation verified three independent ways). ⚠️ **Title-variant note:** Whitley's own publications page says "Selective Pressure"; the paper's title page says "Selection Pressure" — use the latter. Text read from the author's 2000 re-typeset PostScript, so quotes cannot be mapped to printed pages.

Mechanism, verbatim: *"GENITOR is an acronym for **GENetic ImplemenTOR** … One major difference is the explicit use of ranking. The second difference is that GENITOR abandons the generational approach and **reproduces new genotypes on an individual basis** … in such a way that parents and offspring can and typically do co-exist."* *"GENITOR **only produces one new genotype at a time**."* Crossover used: *"the '**reduced surrogate**' 2-point recombination operator developed by Booker (1987)"*; probabilistic crossover is deliberately **eliminated**.

⚠️ **Caution: "replaces the worst individual" is not stated in this paper.** Grepping for "replac", "delet", "worst", "least fit", "poorest" finds nothing of the kind. That detail presumably belongs to **Whitley & Kauth, "GENITOR: a different genetic algorithm," Proc. Rocky Mountain Conf. on AI, pp. 118–130, 1988.** Don't attribute it to ICGA'89.

**Bias parameter**, verbatim — the 1.5–2.0 recollection is right with a nuance: *"**For a bias up to and including 2.0, a linear function is used to allocate reproductive trials.** … In the neural net experiments reported here **a selective bias of 1.5 was found to give the best overall results. Selective pressures above 1.5 lead to premature convergence, while values below this failed to drive the search hard enough** … A bias of 1.5 implies that the top ranked individual … is **1.5 times more likely to reproduce** … than the median individual. For selective pressures greater than 2.0 a nonlinear allocation of trials is used."* Appendix One's linear scheme as a formula: `index = N(bias − sqrt(bias² − 4(bias−1)U)) / (2(bias−1))`, `U ~ U(0,1)`, default **bias = 1.5**, defined for `bias ∈ (1.0, 2.0]`.

His five numbered conclusions, verbatim: (1) *"The value returned by an evaluation function should not be considered an 'exact' measure of fitness"*; (2) ranking *"prevents scaling problems, since ranking automatically introduces a uniform scaling across the population"*; (3) ranking *"provides a means for **directly** controlling selective pressure"*; (4) *"Ranking, coupled with one-at-a-time reproduction gives the search greater focus … less prone to 'wander' … This also removes the need for 'Probabilistic Crossover'"*; (5) ranking *"can be used to **speed up** genetic search"* — **the explicit contrast with Baker, who *"used ranking to SLOW DOWN convergence."*** Core thesis: *"there are only two primary factors (and perhaps only two factors) in genetic search: **population diversity and selective pressure**."* Schema-theorem reconciliation: *"Instead of using I_f/P_f to calculate the fitness ratio, FR = Rank(I_f) can be substituted without changing the intent of the schema theorem."*

Cross-check from Goldberg & Deb (pp. 84–85): they model Genitor as *"a simple combination of block death and birth via ranking"*, early growth ratio between e and e², takeover time `(1/c₀)ln(n−1)`, and argue Whitley's convergence results *"may be most easily explained by"* its higher growth ratio — **reproducible with exponential scaling, larger tournaments or nonlinear ranking.**

---

## Diversity preservation

**Fitness sharing.** Goldberg & Richardson, "Genetic algorithms with sharing for multimodal function optimization," *Proc. 2nd ICGA*, pp. 41–49, 1987. ⚠️ ICGA '87 is not in Crossref; the pagination could not be confirmed. `f'_i = f_i / Σ_j sh(d_ij)` with `sh(d) = 1 − (d/σ_share)^α` for `d < σ_share`, else 0. **Its main weakness is that it requires choosing the niche radius σ_share — which requires knowing the number and spacing of the optima, which is what you were trying to find out.**

**Crowding.** De Jong's 1975 crowding factor ⚠️ (dissertation unreachable); **deterministic crowding** and probabilistic crowding from Mahfoud, "Niching Methods for Genetic Algorithms," PhD diss., UIUC, IlliGAL Report 95001, 1995 ⚠️ (Crossref only returns Mahfoud's *Handbook of Evolutionary Computation* chapter "Niching methods," doi:10.1887/0750308958/b386c54 — cite the handbook chapter if you want a DOI); also Mahfoud, "Crowding and preselection revisited," PPSN 1992; restricted tournament selection (Harik 1995); **clearing** (Pétrowski 1996). **The advantage over sharing: replacement-based niching avoids the σ_share problem entirely by making offspring compete only with their most similar parent.**

**Speciation.** Explicit species by genotypic/phenotypic distance thresholds. **NEAT's speciation is the canonical worked example** (see `applications.md`): a compatibility distance built on innovation numbers, plus explicit fitness sharing within species, **specifically so that a structural innovation — which is initially a fitness *loss* — gets time to be optimised.**

**Island / coarse-grained parallel models.** Subpopulations with periodic migration. The parameters that matter: number of islands, migration **topology**, **interval**, **size**, and the selection/replacement policy for migrants. It both parallelises **and** preserves diversity. ⚠️ **Too-frequent migration collapses the islands into one population and buys nothing.** Citations: Whitley, Rana & Heckendorn, "The island model genetic algorithm," *J. Computing and Information Technology* 7:33–47, 1999; Tomassini, *Spatially Structured Evolutionary Algorithms*, Springer 2005; Cantú-Paz, *Efficient and Accurate Parallel Genetic Algorithms*, 2000; Mühlenbein, "Evolution in Time and Space," FOGA 1, pp. 316–337, 1991. Also **cellular / fine-grained EAs** (Alba & Dorronsoro). ⚠️ **The "island model is better even on one processor" claim is contested; state it as contested.** Note its practical reach: it is what Koza's 1,000-node cluster ran (a 25×40 toroidal grid), what FunSearch uses for its programs database, and what AlphaEvolve combines with MAP-Elites.

### Restarts — the cheapest diversity mechanism, and the most under-used

IPOP-CMA-ES (Auger & Hansen, CEC 2005, pp. 1769–1776) and BIPOP; both built into `cma.fmin2` via `restarts`, `incpopsize=2` and `bipop=True`, with the docs' own recommendation of `restarts <= 9` and a **callable `x0`** so each restart gets a fresh random start.

**The theoretical backbone for restart scheduling: Luby, Sinclair & Zuckerman, "Optimal speedup of Las Vegas algorithms," *Information Processing Letters* 47(4):173–180, 1993**, doi:10.1016/0020-0190(93)90029-9 (full text read in the authors' manuscript; **all logarithms in the paper are base 2**).

- **Known distribution.** For the constant-cutoff strategy `S_t`, **Lemma 1**: `T(S_t) = l(t)` where `l(t) = (1/q(t))(t − Σ_{t'<t} q(t'))`, q the CDF. With `l = inf_{t<∞} l(t)` attained at `t*`, **Theorem 3**: *"For any distribution p, the strategy S_{t*} = (t*, t*, t*, …) is an optimal strategy for p, and T(S_{t*}) = l_p."* **Theorem 4**: this remains optimal even against probabilistic **mixed** strategies.

  ⚠️ **Important correction to the folklore:** the simpler `L(t) = t/q(t)` with `L_p = inf L(t)` satisfies **`l_p <= L_p <= 4 l_p`** — so "expected time ≈ t*/q(t*)" is only correct **within a factor 4**; the theorem is about `l_p`. Also `l_p <= E[p]` always, and **there exist distributions with `t* = ∞`.**
- **Universal schedule**: `S^univ = (1,1,2,1,1,2,4,1,1,2,1,1,2,4,8,1,…)` with `t_i = 2^(k−1)` if `i = 2^k − 1`, else `t_i = t_{i − 2^(k−1) + 1}` for `2^(k−1) <= i < 2^k − 1`. Prose gloss: *"all run lengths are powers of two, and … each time a pair of runs of a given length has been completed, a run of twice that length is immediately executed."*
- **Guarantee, Theorem 5**: *"For all distributions p, **T(S^univ, p) <= 192 l_p (log(l_p) + 5)**."* Their own disclaimer: *"little attempt has been made to minimize the constant 192 … the true behavior of S^univ is obviously much better than stated."*
- **The log factor is provably necessary. Theorem 7**: *"For any strategy S, **sup_{p : l_p = l} T(S, p) >= (1/8) l log(l)**."* Bonus **Theorem 6** (tail): `P[S^univ runs > t steps] <= exp{−t / (64 l_p log t)}`.

### Explicitly optimising for diversity instead of patching it

**Quality-diversity** (MAP-Elites / CMA-ME / CMA-MAE via pyribs) reframes the problem so you ask for an **archive** of diverse high-performing solutions rather than one optimum, and **premature convergence stops being a failure mode because diversity is in the objective.** See `applications.md` for the hexapod result and the honest scoping of novelty search — it is an argument about **deceptive** objectives and the **stepping-stone** structure of search, **not** a claim that objectives are always bad.
