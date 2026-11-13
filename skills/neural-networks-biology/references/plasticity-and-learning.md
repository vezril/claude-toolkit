# Plasticity and learning

Hebb's actual postulate, LTP/LTD, STDP and how little of it generalizes, three-factor
rules and behavioural-timescale plasticity, homeostasis, structural plasticity, the adult
neurogenesis dispute, critical periods, consolidation — and the biological-plausibility-of-
backpropagation literature with real benchmark numbers.

⚠️ marks a claim that is unverified, disputed, or folklore. Where two sources disagree, both
are recorded and **not** reconciled.

---

## 1. Hebb 1949 — and almost everyone misquotes it

### 1.1 The postulate, and the two renderings disagree

⚠️ **Honest provenance: the 1949 book was never opened** — not a facsimile, not a scan. The
wording below is what the peer-reviewed secondary literature *reports* Hebb wrote at p. 62.
**Do not upgrade this.**

**Rendering A** (majority; the only one carrying a page number):

> *"When an axon of cell A is near enough to excite a cell B and **repeatedly or
> persistently** takes part in firing it, some growth process or metabolic **change takes**
> place in one or both cells such that A's efficiency, **as one of the cells firing B**, is
> increased."*

Verified in Brown, *Front Behav Neurosci* 2021;15:732195, PMC8566713 (full text), quoted
verbatim with *"(Hebb, 1949, p. 62)"* attached; and independently in Markram, Gerstner &
Sjöström, *Front Synaptic Neurosci* 2011;3:4, PMC3187646, which also supplies the preceding
sentence: *"Let us assume that the persistence or repetition of a reverberatory activity (or
'trace') tends to induce lasting cellular changes that add to its stability."*

**Rendering B** — from the LTP field's own founders (Abraham, Bliss, Collingridge & Morris,
*Phil Trans R Soc B* 2024, PMC11343267, footnote 1):

> *"…and **repeatedly and persistently** takes part in firing it, some growth process or
> metabolic **changes takes** place in one or both cells such that A's efficiency **in firing
> B** is increased."*

**The three differences:** *"repeatedly **and**"* vs *"repeatedly **or**"* — conjunction vs
disjunction; a singular/plural slip; and — **not cosmetic** — *"A's efficiency **in firing
B**"* vs *"A's efficiency, **as one of the cells firing B**."* **Hebb's longer phrasing frames
A as one of *several* cells firing B, already carrying convergent cooperative input. The short
form erases that.**

> **Two sources disagree with a third about the exact wording. 2:1 favours Rendering A, and
> only A came with p. 62. Anyone quoting Hebb should check a physical copy of the 1949 first
> edition.** Even the LTP field's founders are among those whose rendering differs.

### 1.2 "Cells that fire together wire together" is not Hebb — and the attribution is contested

The slogan appears in **neither** rendering, and neither historical review attributes it to
the 1949 book. **Two rival 1992 attributions are live:**

| Attribution | Evidence |
|---|---|
| **Löwel & Singer 1992**, *Science* 255(5041):209–212 | ⚠️ **Abstract read only** (paywalled). Kittens with induced strabismus to decorrelate the eyes; tangential intracortical fibres preferentially connected cell groups driven by the **same** eye. **Their own summary formula is *"the selection criterion is the correlation of activity"* — the catchphrase is not in the abstract.** A 2022 paper (PMC9449457) credits them. ⚠️ Whether the phrase occurs in the body text **could not be checked** |
| **Shatz 1992**, *Sci Am* 267(3):60–67 | ⚠️ **Bibliographic details only; the Sci Am text was not readable.** A 2025 paper (PMC11873734) credits her: *'Carla Shatz proposed that "cells that fire together are wired together"… She also proposed "out-of-sync, lose your link"'* |

> **The phrase is definitely not Hebb's. A 2022 paper credits Löwel & Singer; a 2025 paper
> credits Shatz. They disagree.** The catchy couplet (with "out-of-sync, lose your link") is
> Shatz-flavoured; Löwel & Singer 1992 is the empirical result most often cited alongside it.
> ⚠️ **Neither 1992 text was read — no winner is picked here.**

### 1.3 What Hebb did not claim

- **No synaptic weakening.** The postulate is one-directional (*"…is increased"*); there is no depression clause. Depression is credited to **Stent (1973)**. And note the **Konorski 1948** co-credit — Hebb was not first; PMC8566713 is an entire paper on pre-Hebb synaptic theories.
- **No timing window, no millisecond precision.** *"Near enough to excite," "repeatedly or persistently," "takes part in firing it"* = **causal participation, not a signed pre→post latency.** Bi & Poo's own abstract treats the window as an **addition** to Hebb: their results *"suggest that Hebb's rule may need to incorporate a quantitative consideration of spike timing."*
- **No synapse-specific scalar weight.** *"Some growth process or metabolic change … **in one or both cells**"* is compatible with presynaptic change, postsynaptic change, intrinsic excitability change, or structural growth. **Δw_ij ∝ x_i·y_j is a later formalisation.**
- **No rate dependence, no normalisation, no competition, no ceiling.**
- **What he *did* introduce:** the **cell assembly** (pp. 69–74) and the **phase sequence** (pp. 79–106). PMC8566713 judges the cell assembly *"may be his most lasting legacy"* while the Hebb synapse is *"better known than Donald Hebb himself."*
- **He disclaimed originality**, verbatim: *"The general idea is an old one, that any two cells or systems of cells that are repeatedly active at the same time will tend to become 'associated,' so that activity in one facilitates activity in the other."*

### 1.4 Pure Hebbian learning is unstable — and the fixes

**The problem:** Δw ∝ x·y with y = Σw·x gives dw/dt ∝ Cw, i.e. unbounded growth along the
leading eigenvector of the input covariance, and no competition for a shared resource.
*"Hebbian plasticity alone is unstable, leading to runaway neuronal activity, and therefore
requires stabilization"* (Zenke, Gerstner & Ganguli, *Curr Opin Neurobiol* 2017).

**Fix 1 — Oja's rule.** ⚠️ The 1982 primary is paywalled and unopened; the formalism below is
verified from **Scholarpedia 3(3):3612, curated by Oja himself**:

```
plain Hebb:  Δw_i = α x_i y
Oja:         Δw_i = α (x_i y − y² w_i)      vector: Δw = α(xy − y²w)
convergence: Cw − (wᵀCw)w = 0   ⇒  w → an eigenvector of C
```

Oja's own framing: plain Hebb *"has a severe problem: there is nothing there to stop the
connections from growing all the time"*; the fix makes the forgetting term *"proportional, not
only to the value of the weight, but also to the square of the output."* Result: the neuron
*"becomes a principal component analyzer."* Side effect: implicit **multiplicative**
normalisation, ‖w‖ → 1; extracts the **top PC only**.

**Fix 2 — BCM theory, the sliding threshold.** Bienenstock, Cooper & Munro 1982. ⚠️ Abstract
only (*J Neurosci* blocked); formalism from **Scholarpedia 3(3):1570, curated by Leon Cooper**:

```
y       = Σ_i w_i x_i
dw_i/dt = y (y − θ_M) x_i − ε w_i
θ_M     = E^p[(y / y_0)]
```

Three postulates: (1) dw_i/dt ∝ x_i; (2) dw_i/dt ∝ a **non-monotonic** φ(y) — negative for low
y, positive for larger y, crossing over at θ_M; (3) **θ_M is a super-linear function of the
history of postsynaptic activity.**

The stabilisation claim, verbatim: *"this 'sliding threshold' provides a mechanism for incoming
patterns, as opposed to converging afferents, to compete."* **Why super-linear:** if θ_M grows
faster than linearly in ⟨y⟩, an over-active cell raises its own LTP threshold faster than its
activity rises, giving a stable fixed point; with θ_M ∝ ⟨y⟩ it does not.

⚠️ **Scholarpedia's own caution:** *"BCM as specified by the three postulates … is
under-determined: there are many mathematical forms which satisfy them."* The 1982 equations
themselves were not read; symbol conventions may differ.

**Fix 3 — subtractive vs multiplicative normalisation.** ⚠️ **Miller & MacKay 1994 is paywalled
and unopened.** The claim usually credited to it — that **subtractive** constraints give
saturated/selective solutions while **multiplicative** give graded ones, and that this choice
(**not** the Hebbian rule) decides whether a model segregates like ocular dominance — is
**recollection only here.** What *is* verified is the contrast: **BCM's distinctive claim is
that it gets competition without either kind of afferent normalisation.**

**Fix 4 — hard weight bounds. Necessary but not sufficient, and this is the usually-skipped
point.** For the pair-based rule, *"the coefficient of δw is always positive, so individual
weights will drift away from the mean **for any choice of parameters**"*; and with Pfister &
Gerstner's published triplet parameter sets *"the distribution of synaptic weights is unstable,
so that **all the synaptic weights cluster around the upper bound**. In addition, **no
competition takes place** between correlated and uncorrelated synapses with these parameter
sets"* (*PLoS Comput Biol* 2016, PMC4777380, full text). **Bounds prevent divergence; they do
not produce competition or a non-degenerate distribution.**

**Fix 5 — homeostasis.** Real, but argued to be **too slow** — see §5.4.

---

## 2. LTP and LTD

### 2.1 Priority, and the untidy real history

⚠️ Lømo's 1966 conference abstract (*Acta Physiol Scand* 68 Suppl. 277:128) is not
PubMed-indexed and no copy was found. Lømo's own first-person account (*Phil Trans R Soc B*
2003, PMC1693150, abstract): in 1966, in Per Andersen's Oslo lab, studying perforant
path → dentate granule cells in anaesthetized rabbits, he observed that brief stimulus trains
increased transmission efficiency *"that could last for hours"*; Bliss arrived in 1968.

A corrective to the tidy textbook story — Lømo 2016 notes *"the unexpected difficulties of
reproducing the first discovery"* and that LTP *"took many years to become generally
recognized."*

### 2.2 Bliss & Lømo 1973 reports no single effect size

⚠️ Abstract (the verbatim numbered summary) read; body not retrievable.

- **Prep:** rabbits anaesthetized with **urethane**; extracellular electrodes; perforant path → dentate.
- **Conditioning, exact:** *"one or more conditioning trains at **10–20/sec for 10–15 sec, OR 100/sec for 3–4 sec**."* **Two distinct regimes** — the first is not what "tetanus" normally connotes.
- **Hit rate / duration:** **15 of 18 rabbits** potentiated, *"for periods ranging from 30 min to 10 hr."*
- **Three measures, and the breakdown:** all three potentiated in **29%** of experiments; **latency reduction was the commonest sign, in 57%**; population EPSP increased in **43%**; population spike in **40%**.
- **Their own interpretation names two mechanisms:** *"(a) an increase in the efficiency of synaptic transmission …; (b) **an increase in the excitability of the granule cell population**."*

> **Two corrections.** (1) **The original LTP paper reports no single percentage effect size for
> "LTP"** — it reports the *fraction of experiments* in which each of three measures changed.
> (2) **The commonest sign was a latency reduction, and the authors explicitly invoked a
> cell-excitability component. "LTP = pure synaptic weight increase" is a later
> simplification.**

**And in the awake companion paper** (Bliss & Gardner-Medwin 1973): long-lasting potentiation
on **26% of occasions** (41% of those with good frequency potentiation), *"lasting from 1 hr to
3 days"*; a further 20% shorter-lasting; and **8% gave short-lasting *depression*.**

> **Longest duration in either 1973 paper: 3 days (awake), 10 hours (anaesthetized). Claims of
> weeks or months of LTP are not from these papers. And LTP was not reliably inducible
> awake — 26%.**

### 2.3 NMDAR dependence — the clean dissociation

Collingridge, Kehl & McLennan 1983, *J Physiol* 334:33–46 (abstract). Verbatim: *"The selective
NMA antagonist, DL-2-amino-5-phosphonovalerate (APV) applied in doses which abolished responses
to NMA, **had no effect on the e.p.s.p. but prevented long term potentiation**."* Their
conclusion: *"Although NMA receptors do not appear to be involved in normal synaptic
transmission in this pathway they may play a role in synaptic plasticity."*

Often forgotten: in 1983 the AMPA receptor was not yet so named — they wrote that the synaptic
receptor *"may be of the kainate or quisqualate type."*

### 2.4 Early vs late LTP, and the published challenge to protein-synthesis dependence

⚠️ **The standard CaMKII cascade account is textbook recollection; no primary was opened for it
as a whole. Do not cite a paper for it from here.** Verified anchors for pieces: spine
enlargement *"is dependent on NMDA receptors, calmodulin and actin polymerization"* and
*"long-lasting spine enlargement also requires Ca²⁺/calmodulin-dependent protein kinase II"*
(Matsuzaki et al., *Nature* 2004, abstract).

**The challenge.** Routtenberg & Rekart, *Trends Neurosci* 2005 (abstract): *"there are enough
instances of memory storage in the virtual absence of protein synthesis to prompt consideration
of alternative models"*; their conclusion is that *"the translational mechanism is **exclusively
a permissive, replenishment step**"*, with **post-translational modification** of proteins
already at the synapse as the instructive mechanism.

⚠️ The anisomycin methodological caveats the critique rests on (independent effects on
catecholamine metabolism and gene superinduction; neurotoxicity at the doses used; ~80–90% not
100% translation inhibition; time-limited, recoverable amnesia) are **recollection only** — no
methodological primary was opened. **The Routtenberg & Rekart *position* is verified; these
specifics are not.**

**A verified data point supporting the challenge.** Ryan, Roy, Pignatelli, Arons & Tonegawa,
*Science* 2015 (abstract): increased synaptic strength and spine density were found specifically
in consolidated engram cells; *"Although these properties are **lacking** in engram cells under
protein synthesis inhibitor-induced amnesia, **direct optogenetic activation of these cells
results in memory retrieval**, and this correlates with retained engram cell-specific
connectivity."*

> **Under protein-synthesis blockade the strengthening is absent but the memory is retrievable —
> a direct blow to "L-LTP-style strengthening *is* the memory," and support for the "permissive"
> framing.**

### 2.5 Synaptic tagging and capture — a cell-wide gate on a synapse-specific rule

Frey & Morris, *Nature* 1997 (abstract). The puzzle: protein synthesis is somatic while LTP is
input-specific. The proposal: LTP creates a short-lasting, protein-synthesis-independent
**synaptic tag** that sequesters plasticity-related proteins. The evidence: weak tetanic
stimulation, **or** repeated tetanisation under protein-synthesis inhibitors, each yields
protein-synthesis-dependent **late** LTP — *provided* repeated tetanisation has already been
applied at **another input to the same cell population.** **Exact timescale: *"The synaptic tag
decays in less than three hours."***

Their 1998 companion adds **"variable persistence"** — the same activation pattern gives short-
or long-lasting LTP *"as a function of the history of activation of the neuron"* — and notes
*"the requirement for aminergic activation to induce late LTP."*

> **STC is a heterosynaptic, cell-wide, 1–3 h gate sitting on top of a synapse-specific
> induction rule. Any model treating Δw_ij as a function of (i, j) alone misses it.**

### 2.6 Three independent preparations, same answer: weak synapses potentiate, strong ones do not

- **Matsuzaki et al. 2004:** two-photon photolysis of caged glutamate at single CA1 spines gives *"a rapid and selective enlargement of stimulated spines that is **transient in large mushroom spines but persistent in small spines**."* Their conclusion: *"spines individually follow Hebb's postulate"*; *"**small spines are preferential sites for long-term potentiation induction**, whereas large spines might represent physical traces of long-term memory."*
- **Bi & Poo 1998:** *"Significant LTP occurred only at synapses with relatively low initial strength."*
- **BTSP (Milstein et al. 2021):** sign depends on current weight — **weak inputs potentiate, strong inputs depress** (§4.4).

Also verified: **Engert & Bonhoeffer 1999** — after **long-lasting** (but not short-lasting)
functional enhancement, **new spines** appear on the postsynaptic dendrite, with no growth in
control regions of the same dendrite or when LTP was blocked.

### 2.7 "LTD" is not one phenomenon

| Family | What it is | Key dissociation |
|---|---|---|
| **(a) NMDAR-dependent** | The de-potentiating counterpart of NMDAR-LTP | *"NMDAR-LTD is associated with a decrease in the **size** of quantal EPSCs"*; blocked by the phosphatase inhibitor microcystin-LR; **"NMDAR-LTD was capable of reversing LTP"** |
| **(b) mGluR-dependent** | Coexists at the **same** synapse | *"no change in quantal size, but a large decrease in the **frequency** of events"* — i.e. **presynaptic**; blocked by Ni²⁺ and a PKC inhibitory peptide; **did not interact with LTP** |
| **(c) Endocannabinoid-dependent** | Retrograde, presynaptically expressed | Striatal LTD requires CB1; postsynaptic anandamide loading produced presynaptic depression — the endocannabinoid is *"released postsynaptically as a **retrograde messenger**"* |
| **(d) Cerebellar (PF→PKC)** | The canonical **supervised / error-driven** biological rule — the climbing fibre is a teaching signal; heterosynaptic and anti-Hebbian in sign | ⚠️ Ito's own hedge: *"there are **two alternative models** proposed for VOR adaptation."* **"Cerebellar LTD = motor learning" has been challenged in print (LTD-blockade mutants that still learn); do not state it as settled** |

**Two consequences worth stating:** models treating LTD as "negative LTP" cover **(a) only**.
And ⚠️ **if LTD induction needs a *presynaptic* NMDA receptor and/or astrocytic signalling** —
both reported — **then "the LTD half of the STDP window" is not a postsynaptic coincidence
computation at all.**

⚠️ The standard AMPAR-endocytosis expression mechanism (Ca²⁺ → calcineurin/PP1 → GluA1 S845
dephosphorylation → clathrin-mediated internalisation) is **recollection**; no primary opened.

### 2.8 What engram optogenetics does and does not establish

**Does:** a sparse learning-tagged ensemble is **sufficient** to drive the behavioural readout
(Liu et al. 2012 — ChR2-labelled DG neurons reactivated in a *different* context produced
freezing, with three reported controls); a fear memory can be created for a context in which
*"a foot shock was **never** delivered"* (Ramirez et al. 2013); and the readout **dissociates
from measurable synaptic strengthening** (Ryan et al. 2015).

**Does not: identify LTP as the storage mechanism.** None of these papers manipulates a
plasticity rule — **they manipulate cells.** "Engram" is defined operationally by
immediate-early-gene labelling, which tags cells that were **active**, not cells that
**changed**. A sufficiency result over an activity-tagged ensemble is consistent with many
substrates — weights, intrinsic excitability, or **connectivity pattern** (Ryan et al.'s own
preferred reading: *"a specific **pattern of connectivity** of engram cells may be crucial for
memory information storage"*), or something post-translational. **Nor does it establish that
artificial reactivation reproduces the natural representation rather than a caricature
sufficient to pass a freezing assay.**

⚠️ Martin, Grimwood & Morris's four criteria (detectability, mimicry, anterograde alteration,
retrograde alteration) are the standard framework but the 2000 review was **not opened.** The
verified pointer to the state of play: PMC11343267 (2024) is the **editorial of a whole theme
issue** on LTP's role in memory — i.e. **after 50 years the role-in-memory question is framed as
an open programme, not a closed result.**

---

## 3. Spike-timing-dependent plasticity — and how little of it generalizes

### 3.1 The founding experiments, with the protocols that are usually dropped

**Markram, Lübke, Frotscher & Sakmann 1997**, *Science* 275(5297):213–215. ⚠️ **Abstract only;
body paywalled.** The abstract contains **no Δt values, no percentages, no pairing frequency, no
species, no layer.**

⚠️ **Headline correction on the pairing frequency.** It is widely stated as **10 Hz**. The
open-access source actually read (Table 1 of Inglebert & Debanne 2021, PMC8488271) says
**20 Hz, 10 pairings, in 2:2 / 5:5 / 10:10 pre:post configurations, at 2 mM Ca²⁺.** Both figures
are recorded; **the OA source is the better evidence.**

> **And "2:2 / 5:5 / 10:10" means Markram et al. paired *bursts*, not single spikes.** That
> matters for §3.5 and §3.8.

⚠️ The commonly quoted magnitudes (~+70–100% at Δt ≈ +10 ms, ~−50% at Δt ≈ −10 ms) are
**recollection only. Do not cite them to Markram 1997.**

**Bi & Poo 1998**, *J Neurosci* 18(24):10464–72 (abstract). Dissociated rat hippocampal
cultures. Postsynaptic spiking **within 20 ms after** presynaptic activation → LTP; **within
20 ms before** → LTD. Protocol from the OA review: **60 pairings at 1 Hz, 1:1, in 3 mM
extracellular Ca²⁺.** **The 3 mM is the most important and least-quoted number in all of
STDP — see §3.9.**

**Two verified findings that get dropped:** (1) **STDP is cell-type specific and absent at
GABAergic postsynaptic targets** — the canonical window is an exc→exc rule only. (2) **LTD
required L-type VGCCs**, so **the two halves of "the window" have different Ca²⁺ sources** —
which is why they dissociate when [Ca²⁺]ₑ changes or the synapse moves.

**The time constants, and whose fit they are.** The modelling literature universally uses
**τ₊ = 16.8 ms, τ₋ = 33.7 ms** for the Bi & Poo window. ⚠️ **Whether Bi & Poo themselves report
these fits in their Figure 7, or whether they are Pfister & Gerstner's (2006) fit to Bi & Poo's
data points, could not be settled** (jneurosci.org returns 403; Europe PMC returns 500 for
PMC6793365). **Safe formulation: "τ₊ ≈ 17 ms and τ₋ ≈ 34 ms are the time constants in standard
use for the Bi & Poo (1998) hippocampal-culture window, as parameterised in Pfister & Gerstner
(2006)."**

⚠️ **The widely reproduced peak percentages (+90–100% at Δt ≈ +10 ms, −40 to −50% at
Δt ≈ −10 ms, with the sign flip occupying only a few ms) are recollection of Figure 7, not read.
The abstract gives only the ±20 ms boundaries and no percentages. Do not publish these
magnitudes as quoted from Bi & Poo.**

**The other founding experiments:**

- **Debanne, Gähwiler & Thompson 1999** — numbers the STDP literature rarely quotes: LTP of **multi**-unitary EPSPs *"never resulted in greater than twofold increases"* (mean 175%), whereas maximal LTP of **unitary** EPSPs *"was as great as **13-fold**"* (mean 250%); *"LTP could not be induced in **24% of unitary EPSPs**"*, of which 37% showed LTD and 63% neither, **despite a pharmacologically identified NMDAR-mediated EPSP component**; *"the first evidence for the coexistence of **potentiatable and nonpotentiatable synapses on individual postsynaptic neurons**."* ⇒ **A single Δw(Δt) curve is a population average over qualitatively different synapses.**
- **Zhang, Tao, Holt, Harris & Poo 1998** — the same ±20 ms, **in vivo**, but in developing **Xenopus** tectum, and framed as **heterosynaptic cooperation/competition**, not isolated pairwise weight change.
- **Feldman 2000** — LTP in a *"narrow temporal window"*, LTD in a *"significantly broader"* one: *"**This long LTD window is unusual among timing-based learning rules** and causes EPSPs that are **uncorrelated** with postsynaptic APs to become **depressed**."* ⇒ With a broad LTD tail **the default for an uncorrelated input is depression** — the source of pairwise STDP's implicit normalisation.
- **Sjöström, Turrigiano & Nelson 2001** — *"rate, timing, and cooperativity **jointly** determine"* plasticity, revealing *"a complex dependence of LTP and LTD on rate and timing."* ⚠️ The famous crossover frequency is **unverified** (paywalled); only the qualitative claim is sourced.

### 3.2 Pairwise STDP is not the "first law" — four model-side results

- **Pfister & Gerstner 2006:** *"those paired-based STDP models **cannot account for the dependence on the repetition frequency** of the pairs of spike… cannot reproduce recent triplet and quadruplet experiments."* Their triplet rule fits both visual-cortex slice and hippocampal culture — **with separate parameter sets, itself the admission that there is no one STDP rule.** With stochastic spike trains it *"can be mapped to a Bienenstock–Cooper–Munro learning rule."*
- **Clopath, Büsing, Vasilaki & Gerstner 2010:** changes depend on *"presynaptic spike arrival and the **postsynaptic membrane potential**, filtered with two different time constants."* ⇒ **Postsynaptic voltage, not the postsynaptic spike, is the plasticity variable.** (Note the published title is *"Connectivity reflects coding: a model of voltage-based STDP with homeostasis"* — not "…voltage-based spike-timing-dependent plasticity".)
- **Graupner & Brunel 2012:** a calcium-threshold model *"gives rise to **a large diversity of spike timing-dependent plasticity curves, most of which have been observed experimentally in different systems**"*, and predicts *"that differences in plasticity outcomes in different studies are due to **differences in parameters defining the calcium dynamics**."* ⇒ **The zoo of published STDP curves is one mechanism with different Ca²⁺ parameters** — the frame that makes §3.9 a prediction rather than an anomaly. It also predicts a **second LTD window at Δt ≈ +20–30 ms**, also seen experimentally.
- **Shouval, Wang & Wittenberg 2010** — the sharpest published indictment, verbatim: *"Although such models are appealing for their simplicity, **they can fail dramatically. For example, the measured single-spike learning rule between hippocampal CA3 and CA1 pyramidal neurons does not predict the existence of long-term potentiation** — one of the best-known forms of synaptic plasticity. Layers of complexity have been added to the basic STDP model to repair predictive failures, **but they have been outstripped by experimental data**."*

### 3.3 The sign depends on where the synapse is

- **Letzkus, Kampa & Stuart 2006** — ***the strongest single result against a universal STDP curve.*** L2/3→L5 synapses: low-frequency pairing at **positive** times gives *"a distance-dependent **shift to LTD** at distal inputs"*; at proximal sites that LTD *"could be **converted to LTP** by dendritic depolarizations suprathreshold for BAC-firing or by high-frequency AP bursts"*; and during bursts, *"**distal synapses display novel timing rules: they potentiate when inputs are activated AFTER burst onset (negative timing) but depress when activated BEFORE burst onset (positive timing)**."* **At distal dendrites the window is inverted.** Their conclusion: *"synapses undergo plasticity according to **local rather than global** learning rules."*
- **Froemke, Poo & Dan 2005:** at the distal dendrite *"the magnitude of LTP is smaller, and the window … for LTD is broader"*, with NMDAR **suppression** underlying LTD induction. And in a sibling protocol, **with 5:5 bursts the *sign* depends on burst frequency.**
- **Froemke & Dan 2002 — the result that invalidates linear superposition of pairs:** *"each pair's contribution depends not only on the interval between the pair, **but also on the timing of preceding spikes. The efficacy of each spike in synaptic modification was suppressed by the preceding spike in the same neuron**"*; and *"for natural spike trains, **the timing of the first spike in each burst is dominant**."* ⇒ **This single result invalidates the linear-superposition-of-pairs assumption on which essentially every pairwise STDP simulation rests.**
- **Sjöström, Rancz, Roth & Häusser 2008:** *"the electrical properties of the dendritic tree are **not static**, but can be altered by neuromodulators and by synaptic activity itself, … **learning rules may be dynamically shaped by tuning dendritic function**."*

### 3.4 The sign is not even determined at the time of the spikes

- **Pawlak & Kerr 2008**, striatum. Exact timings: *"single APs occurring **30 ms before** the cortically evoked EPSP induced LTD, whereas APs occurring **10 ms after** the EPSP induced LTP."* And: *"**blocking dopamine D1/D5 receptors prevented both LTD and LTP induction**."* Their conclusion: *"the timing of APs relative to cortical inputs **alone is not enough** … **ongoing activity does not affect synaptic strength unless dopamine receptors are activated**."* ⇒ **In striatum, STDP is not a two-factor rule at all. Three-factor, hard gate.**
- **Seol et al. 2007:** the rules *"are **not rigid**, but shaped by neuromodulator receptors coupled to adenylyl cyclase and phospholipase C signaling cascades"*, which phosphorylate glutamate receptors at *"specific 'tags' for LTP and LTD."* Cholinergic and adrenergic tone *"associated with the **behavioral state** of the animal can control the gating and the **polarity**."*
- **Brzosko et al. 2017:** dopamine *"**broadens the time window** for synaptic potentiation and modulates the outcome of hippocampal STDP **even when applied AFTER the plasticity induction protocol**"*; and *"**acetylcholine biases STDP toward synaptic depression, whilst subsequent application of dopamine converts this depression into potentiation**."*

> **The sign is not determined at the time of the spikes. It is determined later, by
> neuromodulator sequence.**

### 3.5 Lisman & Spruston: the backpropagating spike is neither necessary nor sufficient

**Lisman & Spruston 2005** (*Nat Neurosci*, three-sentence abstract): *"New experimental work
suggests … that **backpropagating action potentials may be neither necessary nor sufficient for
synaptic plasticity in vivo**."*

**Lisman & Spruston 2010** (*Front Synaptic Neurosci*, abstract): *"**Most investigations of this
process have been done under conditions in which the spike is evoked by postsynaptic current
injection. Under more realistic conditions, in which the spike is evoked by the EPSP, the
results do not generally support STDP**."* Specifics: low-frequency stimulation of a group of
synapses *"can cause **LTD, not the LTP** predicted by the pre-before-post sequence"*; with
stronger stimulation LTP appears at the same timing, but then *"**block of Na⁺ spikes does not
necessarily prevent LTP induction**."* The alternative depolarising events they name — dendritic
Ca²⁺ spikes, the AMPAR-mediated EPSP, and NMDAR-mediated EPSPs or spikes — *"often appear to be
**more important than the Na⁺ spike**."* Conclusion: *"**we thus feel that it is premature to
accept STDP-like processes as the major determinant of LTP/LTD**."*

> **The methodological bite: evoking the postsynaptic spike by somatic current injection produces
> a dendritic voltage waveform that does not occur under synaptic drive. The experiment's own
> manipulation creates the phenomenon it measures.**

### 3.6 ⚠️ The headline: STDP largely disappears at physiological calcium

**Inglebert, Aljadeff, Brunel & Debanne 2020**, "Synaptic plasticity rules with physiological
calcium levels," *PNAS* 117(52):33639–48, PMC7777146. ⚠️ *(Note the preprint carries a **different
title** — "Altered spike timing-dependent plasticity rules in physiological calcium." Do not
conflate them.)*

Their claims, verbatim:

> *"**All previous studies used an abnormally high concentration of extracellular calcium.**"*
>
> *"**The classic STDP rule in which pairs of single pre- and postsynaptic action potentials
> induce synaptic modifications is not valid in the physiological Ca²⁺ range.**"*
>
> *"these pairs of single stimuli are **unable to induce any synaptic modification in 1.3 and
> 1.5 mM calcium and lead to depression in 1.8 mM**."*
>
> *"Plasticity can only be recovered when **bursts** of postsynaptic spikes are used, or when
> neurons fire at **sufficiently high frequency**."*

The dose–response, with the Ca²⁺/Mg²⁺ ratio held constant, at CA3→CA1:

| [Ca²⁺]ₑ | Result |
|---|---|
| **3.0 mM** | classic Hebbian STDP (LTP Δt>0, LTD Δt<0) |
| **1.8 mM** | **LTD only — for *both* positive and negative timing** |
| **1.5 mM** | **no plasticity** |
| **1.3 mM** | **no plasticity** |

**What physiological actually is, vs what the literature used**, verbatim: *"Most, if not all, in
vitro studies of STDP have used **non-physiological** extracellular calcium concentrations …
**commonly between 2 and 3 mM**. But physiological [Ca²⁺]ₑ is **about 2 to 3 times lower**, i.e.
ranging from **1.3–1.8 mM** in young rodent."*

The calcium used by each founding study: **Bi & Poo 1998 → 3.0 mM** (the canonical window);
Debanne 1994 → 2.8; Campanac & Debanne 2008 → 3.0; Sjöström 2001 → 2.5; Froemke 2006 → 2.5;
Pawlak & Kerr 2008 → 2.5; Markram 1997 → 2.0; Wittenberg & Wang 2006 → 2.0; Inglebert 2020 →
1.3–1.8.

**And the retrospective diagnosis of a long-standing contradiction**, verbatim: *"The same
protocol in the hippocampus could lead to a **radically different STDP curve** (Wittenberg and
Wang, 2006; Campanac and Debanne, 2008) and **the only obvious difference was the concentration
of extracellular calcium used (2 vs. 3 mM)**."*

**The rescue**, verbatim: *"adjusting the protocol by **increasing the pairing frequency from 0.3
to 5–10 Hz, or the number of postsynaptic APs from 1 to 3–4**, allows to restore classical
Hebbian STDP."*

> **Plainly: the canonical ±20 ms asymmetric STDP window was measured in 3 mM extracellular
> calcium, ~2.3× the physiological value, and it does not survive at physiological calcium with
> single-spike pairing.**

Two further verified points: **awake vs anaesthetized animals differ in [Ca²⁺]ₑ by ~0.2 mM**;
and with background synaptic noise, STDP-induced changes last **only a few minutes at high Ca²⁺
vs ~1 hour at physiological Ca²⁺** — **the high-Ca²⁺ condition distorts persistence too, not
just inducibility.**

**Be fair to STDP about what this does *not* show.** It does not show timing is irrelevant.
Single-spike pairing at low frequency is simply **below threshold** at physiological Ca²⁺, and
bursts or higher rates **restore** a Hebbian timing dependence. **Timing still matters — inside a
regime that also requires rate and burst structure.** That is Sjöström 2001's and Letzkus 2006's
conclusion by another route, and exactly what Graupner & Brunel predict. ⚠️ **Scope: one
laboratory, one synapse, young rodents, slices. Whether independent replications at other
synapses exist as of 2026-11 is unverified.**

### 3.7 Say the preparation out loud

Bi & Poo 1998 = **dissociated cultures** (not a circuit); Debanne 1999 = **slice cultures**;
Markram 1997, Sjöström 2001, Letzkus 2006, Froemke 2002/2005 = **acute rodent slices**; Zhang
1998 = in vivo but **Xenopus tadpole**, developing; Inglebert 2020 = rat/mouse slices with the
authors' own caution that *"These results obtained **in young animals** need to be confirmed by
further studies in the adult."*

> **The canonical STDP curve is a measurement made overwhelmingly in juvenile rodent slice or
> culture, in artificial CSF with elevated Ca²⁺, with the postsynaptic spike evoked by somatic
> current injection, without neuromodulatory tone, often with inhibition blocked. Every one of
> those conditions has been shown above to matter.**
>
> ⚠️ **No systematic survey of STDP in adult animals, in vivo, in primates, or in human tissue
> was found. If someone claims the pairwise window has been confirmed in awake adult cortex, ask
> for the citation.**

---

## 4. Three-factor plasticity, eligibility traces, and BTSP

**The problem:** reward arrives seconds after the firing pattern that earned it; the pattern is
gone and every synapse has been active meanwhile (temporal credit assignment).

### 4.1 Theory

- **Izhikevich 2007:** STDP is triggered on a millisecond timescale but *"slow kinetics of subsequent synaptic plasticity is sensitive to changes in the extracellular DA concentration during the critical period of a few seconds."* **The usually-omitted contribution:** *"**random firings during the waiting period to the reward do not affect STDP**"* — noise immunity, *"the key feature that distinguishes our approach from previous theoretical studies, which implicitly assume that the network be quiet during the waiting period."*
- **Frémaux & Gerstner 2016:** *"neo-Hebbian three-factor learning rules that depend on presynaptic activity, postsynaptic variables as well as the influence of neuromodulators."* They also note neuromodulators carry **novelty** information and so help decide *"**when**"* to create memories — a gating-of-encoding function, not only an RL function. Canonical form: **dw/dt = η·M(t)·e(t)**, with e a synapse-local eligibility trace and M a global third factor.

### 4.2 The eligibility trace is a hard biochemical window, not a vague decay

**Yagishita et al., *Science* 2014** (abstract): striatal medium spiny neurons, dopaminergic and
glutamatergic inputs stimulated separately and optically. **Exact window: dopamine promoted spine
enlargement *"only during a narrow time window (0.3 to 2 seconds) after the glutamatergic
inputs."*** Mechanism: rapid cAMP regulation in thin distal dendrites, with PKA *"activated only
within the time window **because of a high phosphodiesterase activity**."*

> **The eligibility trace is a phosphodiesterase-imposed biochemical low-pass filter with a hard
> cutoff.**

**He et al., *Neuron* 2015** — *"the first experimental demonstration of eligibility traces in
cortical synapses"*: **distinct traces for LTP and LTD**, each *"timing-dependent[ly]
transform[ed] into lasting changes by **specific monoaminergic receptors** anchored to
postsynaptic proteins."* ⇒ **The third factor is not a scalar: at least two neuromodulator
channels address two distinct traces.** ⚠️ Trace durations are **unverified** (paywalled).

### 4.3 BTSP — and it is not "slow STDP"

**Bittner et al., *Science* 2017** (abstract): *"a synaptic potentiation **notably different from
Hebbian plasticity**. Place fields could be produced **in vivo in a single trial** by potentiation
of input that arrived **seconds before and after** complex spiking. **The potentiated synaptic
input was not initially coincident with action potentials or depolarization.** This rule …
abruptly modifies inputs that were **neither causal nor close in time** to postsynaptic
activation. In slices, **five pairings** of subthreshold presynaptic activity and Ca²⁺ **plateau
potentials** produced a large potentiation with an asymmetric **seconds-long** time course."* The
postsynaptic trigger is a **dendritic Ca²⁺ plateau potential, not a somatic Na⁺ spike.**

**Milstein et al., *eLife* 2021** (full text read): BTSP is *"a **non-Hebbian** form of
**bidirectional** synaptic plasticity that operates over a **seconds-long** timescale."* The
depression component is time-delimited — **absent when the interval between plateau onset and the
initial place-field ramp exceeded 4–5 s.** **The sign rule:** modelling and Vm manipulation showed
the apparent proximity effect *"actually **results from a dependence on current synaptic weight
such that weak inputs potentiate and strong inputs depress**."* Their network claim: BTSP
*"enables **population activity, rather than pairwise neuronal correlations**, to drive neural
adaptations to experience."*

**The contrast, plainly:**

| | STDP | BTSP |
|---|---|---|
| Window | ±~20 ms (τ₊ ≈ 17, τ₋ ≈ 34 ms) | **seconds**; depression gone beyond ~4–5 s |
| Repetitions | 60–100+ pairings | **one trial in vivo, five pairings in slice** |
| Coincidence | **required** | potentiated input explicitly *"not initially coincident"* |
| Sign set by | spike **order** (Δt) | **current synaptic weight** (weak → potentiate, strong → depress) |
| Trigger | somatic Na⁺ spike | **dendritic Ca²⁺ plateau** |
| Preparation | juvenile slice/culture at 2–3 mM Ca²⁺ | **in vivo, awake behaving mice** |

> **~2–3 orders of magnitude in time and ~1–2 in repetitions — and the sign rules differ in
> kind: STDP's sign is a function of Δt, BTSP's of w. BTSP is not "slow STDP"; Milstein et al.
> explicitly call it non-Hebbian, and its timescale is the one that matches behaviour.**

⚠️ **Caveat: established at one class of synapse (entorhinal/CA3 → CA1 pyramidal), one region, by
one group plus close collaborators. Whether a BTSP-like rule exists in neocortex is unverified.**

⚠️ **And note the direct tension with pairwise STDP: reverse replay (§6) should produce LTD under
a pairwise rule.**

---

## 5. Homeostatic plasticity — and two corrections

### 5.1 Synaptic scaling

**Turrigiano et al., *Nature* 1998** (abstract): *"a new form of synaptic plasticity that increases
or decreases the strength of **all** of a neuron's synaptic inputs as a function of activity."* Rat
visual-cortical dissociated cultures; chronic TTX blockade **increased** mEPSC amplitude *"without
changing their kinetics"*; disinhibition initially raised firing rates but *"**over a 48-hour
period** mEPSC amplitudes decreased and firing rates returned to close to control values."*
Changes were *"at least partly due to postsynaptic alterations … and **apparently** affected each
synapse in proportion to its initial strength."*

**Why multiplicativity is the whole point:** multiplying every synapse by the same α renormalises
the cell's gain while **preserving relative weights** — the stored information. **Additive scaling
would erase the memory.** Note the founding paper's own hedge: *"**apparently** affected each
synapse in proportion…"*

⚠️ Drug concentrations (commonly cited as 1 µM TTX, 20 µM bicuculline) are **unverified** —
methods paywalled. **Do not quote concentrations.**

### 5.2 ⚠️ Correction: scaling is not multiplicative

**Methodological:** Kim, Tsien & Alger 2012 — *"It is crucial for this hypothesis that **all
synapses be affected identically**, but whether or not this actually occurs is difficult to
determine directly … **the accuracy of the test procedure has not been fully validated**. We now
show that the existence of an amplitude threshold for empirical detection of miniature synaptic
currents **limits the use of the most common method**."*

**Empirical:** Hanes et al., *J Neurosci* 2020 — the observed shift *"**cannot be reproduced by
simulation of uniform multiplicative scaling**, with or without the distortion caused by applying
a detection threshold."* And explicitly: *"**the scaling factor is not uniform but is close to 1
for small mEPSCs, and increases with increasing mEPSC amplitude** across a substantial portion of
the data. **This pattern was also observed for previously published data** from dissociated mouse
hippocampal neurons and dissociated rat cortical neurons."* Their conclusion: *"homeostatic
signaling molecules are likely to be **differentially expressed across synapses**."*

> **"Synaptic scaling is multiplicative" is contradicted by re-analysis of three independent
> datasets including previously published ones. The information-preservation argument for scaling
> does not go through as usually stated.**

### 5.3 Homeostasis is not purely neuronal, and not only about weights

- **Stellwagen & Malenka 2006:** scaling after prolonged blockade *"is mediated by the pro-inflammatory cytokine **tumour-necrosis factor-alpha**"*, and with wild-type/TNF-α-deficient mixtures, *"**glia are the source** of the TNF-alpha that is required."* ⇒ **A homeostatic set-point signal that is not neuronal at all.**
- **Desai, Rutherford & Turrigiano 1999:** neurons respond to prolonged blockade *"by **modulating their balance of inward and outward currents** to become more sensitive to synaptic input"*; exogenous BDNF **prevented** and a TrkB-IgG fusion **reproduced** the change. ⇒ **Homeostasis acts on the input–output curve — channel expression, f-I gain, threshold — not only on weights. A weight-only model cannot express this.**
- ⚠️ Turrigiano's own 2012 review: *"dozens of molecular pathways have now been implicated … [but] **a clear picture of how homeostatic feedback is structured at the molecular level has not yet emerged**."*

### 5.4 ⚠️ Correction: homeostasis is too slow to do the job

Hebbian/STDP induction: **seconds to minutes.** BTSP: **one trial, seconds.** Synaptic scaling:
**hours to days** (measured over 48 h). **A feedback controller 10³–10⁵ times slower than the
instability it must suppress cannot suppress it.** That is the **temporal paradox**.

Zenke, Gerstner & Ganguli 2017, verbatim: *"Traditionally, a diversity of homeostatic plasticity
phenomena found in neural circuits is thought to play this role. However, **recent modelling work
suggests that the slow evolution of homeostatic plasticity, as observed in experiments, is
insufficient to prevent instabilities originating from Hebbian plasticity.** To remedy this
situation, we suggest that homeostatic plasticity is complemented by **additional rapid
compensatory processes**."*

> **Candidate fast stabilisers — heterosynaptic plasticity on seconds, short-term plasticity,
> inhibitory plasticity, rapid metaplasticity. The identity of the fast stabiliser is an open
> problem.**

### 5.5 Metaplasticity — and a warning almost never repeated

Abraham & Bear 1996: metaplasticity *"is **not necessarily expressed as a change in the efficacy
of normal synaptic transmission**. Instead, it is manifest as a change in the **ability to induce
subsequent synaptic plasticity** … a **higher-order** form."* And the warning: *"**the induction of
metaplasticity complicates the interpretation of many commonly studied aspects of synaptic
plasticity, such as saturation and biochemical correlates**."*

**BCM's sliding threshold *is* a metaplasticity rule** — an activity-history-dependent change in
the inducibility and sign of plasticity, with no change in current efficacy.

---

## 6. Structural plasticity, neurogenesis, development, consolidation

### 6.1 ⚠️ Two back-to-back 2002 *Nature* papers reached opposite conclusions

Both in *Nature* 420(6917), 19–26 December 2002, **with a joint News & Views** — the clearest
signal that the field itself treated this as a disagreement. Trachtenberg et al. (mouse barrel
cortex, repeated imaging over weeks) report *"**spine lifetimes vary greatly**"*; the companion
reached a different conclusion about spine stability in adult cortex.

**Also verified:** ⚠️ **synaptic turnover sets a floor on memory noise** — structural turnover is
not a detail but a constraint on how long any weight-based trace can persist.

### 6.2 Adult human hippocampal neurogenesis is a genuine, unresolved dispute

**Both sides are in print and neither has conceded:**

- **Against:** Sorrells et al. 2018 — adult human neurogenesis is absent or vanishingly rare.
- **For:** Moreno-Jiménez et al. 2019 — abundant adult neurogenesis.

**The methodological crux** is tissue fixation and processing protocol, and it is not settled.
**State it as a dispute. Do not pick a side.** (And note this matters for ML analogies: whether
a brain adds *units* in adulthood is not a settled fact.)

### 6.3 Critical periods

- **Hubel & Wiesel's monocular deprivation** is the founding result.
- **Ocular dominance and horizontal connections are activity-dependent** — Löwel & Singer 1992 (§1.2) is the key experiment, and **its own summary formula is about *correlation of activity*, with specificity attained by *pruning*.**
- **Spontaneous activity (retinal waves) sculpts circuits before experience** — *"internally generated spontaneous activity sculpts circuits on the basis of the brain's**"* own patterns, not the world's.
- **GABA maturation gates critical-period onset** (Fagiolini & Hensch 2000) — *"the level of inhibition within the visual cortex may thus trigger, **once in life**, an"* opening.

### 6.4 Consolidation, sleep and replay

- **Standard consolidation model vs multiple trace theory** — both on the record, not reconciled.
- **Hippocampal replay**, and **causal disruption of sharp-wave ripples impairs learning** — the strongest causal link.
- **The synaptic homeostasis hypothesis (SHY)** for sleep's function.
- ⚠️ **Published skepticism about sleep-consolidation effect sizes exists** — do not present the sleep-consolidation literature as uniformly strong.

> ⚠️ **And the tension worth naming: reverse replay is in direct conflict with pairwise STDP** — a
> reversed sequence should produce LTD under a pairwise rule, not strengthen the sequence.

---

## 7. The biological plausibility of backpropagation

### 7.1 Why exact backprop is held implausible — and the Crick quotation nobody should use

⚠️ **The founding objection is Crick 1989, *Nature* 337(6203):129–132 — and its entire published
abstract is two sentences:** *"The remarkable properties of some recent computer algorithms for
neural networks seemed to promise a fresh approach to understanding the computational properties
of the brain. Unfortunately most of these neural nets are unrealistic in important respects."*

> ⚠️ **That is the whole abstract. The famous content — that backprop requires a neuron to know
> its downstream partners' synaptic weights, and that real axons do not run backwards — is in the
> paywalled body, which was not read. Do not attribute a quoted sentence to Crick 1989 on this
> dossier's authority.** ⚠️ Likewise, the attribution of the *term* "weight transport problem" to
> Grossberg 1987 is **recollection** — that paper was unobtainable.

**The objections, enumerated:**

| # | Objection | Verified statement of it |
|---|---|---|
| 1 | **Weight transport / symmetry** — the backward pass needs Wᵗ | Akrout et al. 2019: *"Current algorithms for deep learning probably cannot run in the brain because they rely on **weight transport, where forward-path neurons transmit their synaptic weights to a feedback path**, in a way that is likely impossible biologically"* |
| 2 | **A separate backward phase with different dynamics** | Lillicrap et al. 2020: *"**although feedback connections are ubiquitous in the cortex, it is difficult to see how they could deliver the error signals required by strict formulations of backpropagation**"* |
| 3 | **Non-locality of the update** | Whittington & Bogacz 2017: *"**the change in synaptic weights is a complex function of weights and activities of neurons not directly connected with the synapse being modified**, whereas the changes in biological synapses are determined only by the activity of presynaptic and postsynaptic neurons"* |
| 4 | **f′(z) must be available at each unit** | Baldi, Sadowski & Lu: random-backprop variants work *"almost as well as backpropagation, and … **multiplication by the derivatives of the activation functions is important**"* — i.e. it is load-bearing empirically |
| 5 | **Precise, signed, real-valued errors** vs non-negative noisy spike rates | Hwang, Lee et al. 2023: the two *"**are not directly comparable because of the difference in encoding (scalar value vs. spikes)** and the questionable existence of mandatory symmetric backward connections"* |
| 6 | **Carrying gradients through the spike discontinuity** (surrogate gradients are an ML workaround, not a mechanism) | ⚠️ no primary read |
| 7 | **Update locking / sequential layer updates** | Launay et al. 2020: backprop *"**is no panacea. It enforces sequential layer updates**, thus preventing efficient parallelization"* |
| 8 | **Credit assignment across time** — BPTT needs the full activity history stored and replayed backwards | biological counterpart: eligibility traces (§4) |
| 9 | **The "no teacher" problem** — and even granting a reward signal, a **scalar** reward is far weaker than a per-unit error vector | — |

**What the problem really is**, Lillicrap et al. 2020: *"In the cortex, synapses are embedded
within multilayered networks, **making it difficult to determine the effect of an individual
synaptic modification on the behaviour of the system**. The backpropagation algorithm solves this
problem in deep artificial neural networks, but historically it has been viewed as biologically
problematic."*

### 7.2 Feedback alignment — what it establishes, and what it does not

**Lillicrap, Cownden, Tweed & Akerman 2016**, *Nat Commun* 7:13276 (full text read). Replace Wᵗ
with a **fixed random** matrix B; the forward weights learn to align with Bᵗ so the random
feedback becomes a positively-aligned descent direction. **No weight transport.**

| Result | Number |
|---|---|
| MNIST, nonlinear 1-hidden-layer, mean of 20 runs | **FA 2.1% vs backprop 2.4%** test error |
| **50% of W and B elements randomly removed** (so 25% chance of reciprocal connection) | **FA still matches backprop: 2.4%** |
| Stochastic/spiking network (3 hidden layers × 1,500 stochastic binary units, no interruption of activity or plasticity between phases) | **1.8% final test error** |

**Establishes:** weight **symmetry** is not necessary; the signal survives 50% synapse-level
sparsification; and it works in a stochastic spiking-like network.

**Falls short:** MNIST with a shallow fully-connected net is **not a test of deep credit
assignment.**

### 7.3 ⚠️ The key negative result: Bartunov et al. 2018

NeurIPS 2018 (arXiv:1807.04587), full text read incl. Tables 1–2. Crucially, they test
**locally-connected** architectures — convolutional receptive-field structure **without weight
sharing**, because weight sharing is itself implausible: *"To implement convolutions in biology,
**many neurons would need to share the values of their weights precisely — a requirement with no
empirical support**."*

**ImageNet test error (%), 1000 classes, resized 224×224:**

| Method | Top-1 | Top-5 |
|---|---|---|
| DTP, parallel | **98.34** | 94.56 |
| DTP, alternating | **99.36** | 97.28 |
| SDTP, parallel | **99.28** | 97.15 |
| **Feedback alignment** | **93.08** | 82.54 |
| **Backpropagation** | **71.43** | 49.07 |
| Backpropagation, ConvNet | 63.93 | 40.17 |

> **Target-propagation variants sit at 98–99% top-1 error — essentially chance (99.9%).** FA
> reaches 93.08%, clearly better than chance and better than TP, against **71.43% for BP in the
> same locally-connected architecture.** **Gap between the best bio-motivated algorithm and plain
> BP on the same architecture: ~21.7 pp top-1 / ~33.5 pp top-5.**

**Their own verdict** — the wording is the finding: *"Overall, **our results are largely negative**.
That is, **we find that none of the tested algorithms are capable of effectively scaling up to
training large networks on ImageNet**. There are three possible interpretations … (1) Existing
algorithms need to be modified… (2) research should continue into new physiologically realistic
learning algorithms that can scale-up, or (3) **we need to appeal to other adaptive capacities** to
account for the fact that humans are able to perform well on this task."*

**Their fairness caveat:** *"**it would be premature to conclude that TP cannot perform adequately
on ImageNet.** We can conclude though, that **out-of-the-box application** of this class of
algorithms does not provide a straightforward solution to real data on even moderately large
networks."*

**A practical finding that is itself a biological argument: DFA could not be run at ImageNet
scale** — *"due to practical necessity of maintaining **a large fully-connected feedback layer of
weights from the output layer to each intermediate layer** … **practically intractable**: on a GPU
with 16GB of onboard memory, we encountered out-of-memory errors."* ⇒ **The DFA feedback pathway
is an all-to-all projection from the output layer to every neuron — a biologically awkward object,
not just a memory problem.**

⚠️ **Do not compare these numbers to the ImageNet leaderboard.** Their own note: *"both our BP
results and our TP and FA results are considerably worse than convolutional neural nets"* —
because weight sharing is excluded by design. Also: *"**BP is the most stable algorithm.** TP
methods proved to be **the most sensitive to the choice of hyperparameters**."*

### 7.4 ⚠️ The correction to "no plausible rule has matched backprop at scale"

**Akrout, Wilson, Humphreys, Lillicrap & Tweed 2019**, "Deep Learning without Weight Transport,"
NeurIPS 2019 (arXiv:1904.05391), full text read. Two mechanisms — **weight mirrors** and
**Kolen–Pollack** — let initially random feedback weights **learn** appropriate values without
weight transport.

**ImageNet top-1 test error (standard errors in parentheses):**

| Method | ResNet-18 | ResNet-50 |
|---|---|---|
| **Weight mirrors** | **30.2(7)%** | **23.4(5)%** |
| **Kolen–Pollack** | **29.2(4)%** | **23.9(7)%** |
| Feedback alignment | **97.4(2)%** | **98.9(1)%** |
| Sign-symmetry | 39.2(4)% | 33.8(3)% |
| **Backprop** | **30.1(4)%** | **22.9(4)%** |

> **Kolen–Pollack at 29.2% slightly *beat* backprop's 30.1% on ResNet-18, and both
> learned-feedback methods are within ~0.5–1.0 pp of backprop on ResNet-50. Meanwhile plain
> feedback alignment is at 97.4% and 98.9% — near chance, independently corroborating Bartunov's
> negative FA result. So: FA does not scale, but *learning* the feedback does.**

**The honest caveats, from their own text:**

1. **Kolen–Pollack works by transporting *updates* rather than weights:** *"we don't have to transport weights if we can transport **changes** in weights … at each time step t they undergo **identical adjustments** A(t) and apply **identical weight-decay factors** λ."* ⇒ **Requiring each forward/feedback synapse *pair* to receive the same update increment and the same decay is itself a non-trivial coordination demand; it relocates Crick's objection rather than dissolving it.**
2. **The weight mirror uses a distinct "mirror mode"** in which the network's dynamics change — one layer *"fires noisily"* and cross-projections are rerouted. ⇒ **A separate phase — objection (2) reintroduced.**
3. ⚠️ **These are ResNets, i.e. convolutional — they use weight *sharing*, which Bartunov et al. explicitly excluded as implausible.** So this result removes weight **transport** while retaining weight **sharing. The two papers are not strictly comparable, and neither alone settles the scaling question.**
4. **Their own framing is *"learn ImageNet about as well as backprop does"* / *"nearly match backprop"* — not "match."**

> **So the defensible claim is narrower than "no biologically-plausible rule has matched backprop
> at scale." It is: no rule that is *simultaneously* local, phase-free, spike-compatible,
> weight-sharing-free AND transport-free has matched backprop at ImageNet scale. Each individual
> implausibility has been removed by some method; none has removed them all at once.**

### 7.5 Direct feedback alignment — and the configuration that works uses weight transport

**Nøkland 2016** (arXiv:1609.01596): the error is propagated through *"fixed random feedback
connections **directly from the output layer to each hidden layer**."* **1.45% error on
permutation-invariant MNIST with dropout.** Note his careful wording: *"almost as good … **for
fully connected networks**"*, and the convolutional claim is about **training** error.

**Launay, Poli, Boniface & Krzakala 2020**, "Direct Feedback Alignment Scales to Modern Deep
Learning Tasks and Architectures," NeurIPS 2020, full text read. Abstract: DFA *"successfully
trains a large range of state-of-the-art deep learning architectures, with performance close to
fine-tuned backpropagation. At variance with common beliefs, our work supports that challenging
tasks **can be tackled in the absence of weight transport**."*

**The numbers that qualify it — Table 7, best validation perplexity, Transformer on WikiText-103
(lower is better):**

| | Baseline | +Adam | +β₂=0.999 | +LR schedule |
|---|---|---|---|---|
| **BP** | 34.4 | | **29.8** | |
| **DFA Macro** | 95.0 | 77.1 | 55.0 | **52.0** |
| **DFA Micro** | 182 | 166 | 99.9 | **93.3** |

**And from the same table caption, verbatim:** *"In **Macro** the feedback is applied after every
transformer layer, **implying weight transport at the layer-scale**, while in **Micro** the
feedback is applied after every sub-layer."*

> **The configuration that gets within ~1.7× of BP perplexity (52.0 vs 29.8) still uses weight
> transport at the layer scale. The genuinely transport-free configuration (Micro) lands at 93.3
> vs BP's 29.8 — more than 3× worse. The title is correct that DFA "scales to modern tasks and
> architectures"; it does not mean DFA matches backprop without weight transport on those tasks.**

Other verified caveats from their text: *"**DFA fails to train more classic 2D image convolutional
layers**"* — so the ImageNet/ConvNet gap of §7.3 is **not** closed, the paper moves to other
architectures. NeRF-DFA shows a novel artefact *"unique to NeRF-DFA … possibly due to the
alignment process. Indeed, **DFA creates a bias on the weights**."* Their own conclusion: *"**DFA
still requires an implausible global feedback pathway**; however, local training has already been
demonstrated at scale. **The next step towards biologically-compatible learning is a local method
without weight transport.**"* And: *"**a significant downside of moving from BP to DFA is a far
more limited understanding of how to train models and how the trained models behave**."*

### 7.6 Target propagation — and its failure mode is informational

**Lee, Zhang, Fischer & Bengio 2015**, "Difference Target Propagation." Backprop *"relies on
infinitesimal effects (partial derivatives)"*; the idea is *"to compute **targets** rather than
gradients, at each layer"*, relying on *"**auto-encoders at each layer**"* rather than a backwards
network with symmetric weights, and *"it **can be applied even when units exchange stochastic
bits** rather than real numbers."* **Biological payoff: no f′ required, no weight transport in the
naive formulation, and it works with stochastic binary units — objections (1), (4) and (6) at
once.**

**The scaling limit, and Bartunov et al.'s diagnosis:** SDTP without weight sharing *"perform much
worse than DTP, **likely because of impoverished output targets**"*; and *"it is not clear whether
**targets for the penultimate layer will be diverse enough (given low entropy classification
targets) or precise enough** (given the inevitable poor performance of the learned inverse for
this layer)."*

> **The failure mode is informational: a one-hot label carries log₂(1000) ≈ 10 bits, which must be
> inverted into a useful target for a high-dimensional penultimate layer.**

### 7.7 ⚠️ Predictive coding equals backprop only under an assumption that dissolves the gain

**Whittington & Bogacz 2017:** a predictive-coding network *"can efficiently perform supervised
learning fully autonomously, employing only simple local Hebbian plasticity. Furthermore, **for
certain parameters**, the weight change in the predictive coding model **converges** to that of the
backpropagation algorithm."* **Note the original hedges: *"for certain parameters,"* and
*"An Approximation"* in the title. The paper never claimed exact equivalence in general.**

**Millidge, Tschantz & Buckley:** predictive coding *"converges asymptotically (and in practice,
rapidly) to **exact** backprop gradients on arbitrary computation graphs using only local learning
rules"*, with PC CNNs, RNNs and LSTMs that *"perform equivalently to backprop on challenging
machine learning benchmarks while using only local and **(mostly)** Hebbian plasticity."* **The
parenthesis is theirs.**

**⚠️ The correction — Rosenbaum, *PLoS One* 2022;17(3):e0266102, full text read. The wording is
the finding:**

> *"modifying predictive coding by a **'fixed prediction assumption'** leads to an algorithm that
> produces the **exact same parameter updates as backpropagation**."*
>
> *"**Predictive coding under the fixed prediction assumption is algorithmically equivalent to a
> direct implementation of backpropagation, which raises the question of whether it should be
> interpreted as more biologically plausible than backpropagation.**"*
>
> Section heading: *"**A strict interpretation of predictive coding does not accurately compute
> gradients.**"*
>
> On the strict version: *"Predictive coding and backpropagation give similar accuracies, but **the
> parameter updates are less similar**."*

> **"Predictive coding implements backprop with local Hebbian plasticity" is true only under the
> fixed-prediction assumption, under which the algorithm *is* a direct implementation of
> backpropagation — so the plausibility gain is illusory; and the strict dynamics do not
> accurately compute gradients. Cite Rosenbaum 2022 whenever this claim is made.**

### 7.8 Equilibrium propagation

**Scellier & Bengio 2017:** *"**only one kind of neural computation**, performed in both the first
phase … and the second phase of training … it **does not need a special computation or circuit for
the second phase**… the output units are **slightly nudged** toward their target in the second
phase … the signal 'back-propagated' during this second phase … **encodes the gradient of the
objective function, when the synaptic update corresponds to a standard form of spike-timing
dependent plasticity**. … **the only local difference between the two phases is whether synaptic
changes are allowed or not**."* Scope in 2017: recurrent nets with 1–3 hidden layers on
**permutation-invariant MNIST**.

> ⚠️ **EP explicitly ties its update to *"a standard form of spike-timing dependent plasticity"* —
> an assumption that §3.3–3.6 shows is not safe.** This cross-link between the plasticity
> literature and the plausibility literature is rarely drawn and is the sharpest thing in this
> file.

**Laborieux et al. 2020/2021 — the scaling fix, with numbers:** *"**the standard implementation of
equilibrium propagation does not scale to visual tasks harder than MNIST** … **a bias in the
gradient estimate** … inherent in the use of finite nudging, is responsible … greatly reduced by
using **symmetric nudging**."* Results on **CIFAR-10 test error**:

| Configuration | Test error |
|---|---|
| EP, symmetric nudging | **11.7%** |
| EP, standard same-sign nudging | **86%** (near chance = 90%) |
| EP, unidirectional forward/backward connections | **13.2%** |

⚠️ *"Approaches the one achieved by BPTT"* — **the BPTT baseline is not in the abstract and the
body was not read, so no BP reference number is quoted.** Note the arXiv v1 says *"asymmetric"*
where the journal version says *"unidirectional"* — same experiment, differently worded.

> **CIFAR-10 at ~12% error is real progress and weight-transport-relaxed, but two benchmark
> generations behind the ImageNet question.** ⚠️ **No EP result on ImageNet was found.**

### 7.9 Dendritic-compartment and microcircuit models — the biology supplies the substrate

- **Guerguiev, Lillicrap & Richards 2017**, *eLife* 6:e22901: *"Like neocortical pyramidal neurons, neurons in our model receive sensory information and higher-order feedback in **electrotonically segregated compartments**. Thanks to this segregation, neurons in different layers of the network **can coordinate synaptic weight updates**."* ⚠️ **The task is MNIST and the abstract gives no accuracy figure. The bar cleared is "deep beats shallow on MNIST," not "matches backprop."** **Biological content: segregation of apical (feedback) from basal (feedforward) input in an L5 pyramidal neuron lets one cell hold both a prediction and a target without mixing — a concrete answer to objection (2) using known morphology.**
- **Sacramento, Ponte Costa, Bengio & Senn 2018:** *"**in contrast to previous work our model does not require separate phases** and synaptic learning is driven by **local dendritic prediction errors continuously in time**. Such errors originate at apical dendrites and occur due to a **mismatch between predictive input from lateral interneurons and activity from actual top-down feedback**… our model can represent **both error and normal activity within a pyramidal neuron**."* ⇒ **The most circuit-specific proposal, making testable predictions about interneuron plasticity.** ⚠️ Small-scale regression and classification; no ImageNet-scale result claimed, and no accuracy number verified.
- **Payeur, Guerguiev, Zenke, Richards & Naud 2021**, *Nat Neurosci* 24(7):1010–19: *"models that rely **solely on pre- and postsynaptic activity** … have, so far, **not been able to account for learning complex tasks that demand credit assignment in hierarchical networks**. Here we show that **if synaptic plasticity is regulated by high-frequency bursts of spikes**, then pyramidal neurons higher in a hierarchical circuit can coordinate the plasticity of lower-level connections."* **The mechanism: a single axon multiplexes the *event rate* (feedforward) and the *burst fraction* (feedback/credit), and short-term plasticity at the receiving synapse demultiplexes them.** An elegant answer to objections (2), (3) and (5) at once — one channel, one dynamics, local updates, and **a signed signal encoded as a deviation of burst fraction from baseline, so "negative error" = fewer bursts than baseline and no negative firing rates are needed.** ⚠️ **The abstract gives no benchmark or number and the body is paywalled. For benchmarks and accuracies, read the paper.** (Note Zenke is a co-author — the same person who published "homeostasis is too slow.")

### 7.10 NGRADs — the organising idea

**Lillicrap, Santoro, Marris, Akerman & Hinton 2020**, *Nat Rev Neurosci* 21(6):335–346. ⚠️
**Abstract only; the review body is paywalled and was not read.** The argument, verbatim: *"here we
build on past and recent developments to argue that **feedback connections may instead induce
neural activities whose differences can be used to locally approximate these signals** and hence
drive effective learning in deep networks in the brain."*

⚠️ **The acronym is not expanded in the abstract.** The expansion and gloss are quoted from a 2023
open-access review (PMC10336230), **not from the 2020 review itself**: *"a hypothetical learning
algorithm class, **'neural gradient representation by activity differences (NGRAD)'** … which
states that the information of activity difference is reflected as synaptic change."*

> **The idea restated: do not transmit an explicit error vector. Let top-down feedback nudge each
> layer's activity toward a better configuration, and let each synapse read the *difference*
> between its postsynaptic unit's nudged and un-nudged activity as its local learning signal. The
> activity difference stands in for the gradient.**
>
> **Every member of this family — target prop, equilibrium prop, contrastive Hebbian learning,
> recirculation, dendritic microcircuits, predictive coding — is an NGRAD in this sense. This is
> the most useful single organising idea in the literature: it recasts "how does the brain do
> backprop?" as "how does the brain compute and use activity differences?"**

### 7.11 Other approaches, and their honest ceilings

- ⚠️ **Forward-forward (Hinton 2022) never claimed to scale.** His own first sentence: the aim is *"to demonstrate that it works **well enough on a few small problems** to be worth further investigation"*, and the title is *"Some **Preliminary** Investigations."* **Architecturally, each layer has its own local objective, so FF is greedy-layerwise — it does not solve deep credit assignment, it avoids needing to. That is both its appeal and its ceiling. Anybody citing FF as a solved alternative to backprop is overstating the paper.**
- **Local greedy / layerwise learning** — the same structural point. Launay et al.: *"local training has already been demonstrated at scale"* while insisting *"the next step … is a local method **without weight transport**."* ⇒ **Local learning scales; local learning that *also* does multi-layer credit assignment is the unsolved part.**
- **Perturbation learning** (node/weight perturbation, REINFORCE) is **maximally plausible** — a global scalar plus a local activity record, i.e. a neuromodulator plus an eligibility trace. ⚠️ **The variance-scaling objection (estimate variance grows with the number of perturbed parameters, so samples needed scale badly with network size) is recollection — no primary quantifying it was opened. Do not cite a scaling exponent.**
- **Roelfsema & Holtmaat 2018** propose a **four-factor** rule — presynaptic × postsynaptic × a global neuromodulatory RPE × **a top-down attentional feedback signal tagging the responsible units**, so the attentional factor substitutes for the backward pass, carrying *"which units mattered"* rather than *"by how much the loss changes."* ⚠️ **Abstract only; the four-factor formalism as stated is unverified.** (Note there is a **published exchange** about this review in *Nat Rev Neurosci* 19(10).)
- ⚠️ **Recirculation (Hinton & McClelland 1988)** — a historical NGRAD predating the term by 32 years. **Not PubMed-indexed, no copy found; bibliographic details and content are recollection only.**

### 7.12 ⚠️ Two refereed statements in tension — record both

**Whittington & Bogacz 2019** (*Trends Cogn Sci*, abstract, in full): *"**Computational models
implementing these theories achieve learning as efficient as artificial neural networks**, but
they use simple synaptic plasticity rules based on activity of presynaptic and postsynaptic
neurons."*

**Bartunov et al. 2018** — published the **previous year**, at NeurIPS, **with Hinton and Lillicrap
as co-authors**: *"none of the tested algorithms are capable of effectively scaling up to training
large networks on ImageNet."*

> **These can be partly reconciled — Whittington & Bogacz describe efficiency on the benchmarks
> those models were tested on, i.e. MNIST-scale; Bartunov describes ImageNet. But as written they
> give a reader opposite impressions, and the reconciliation is exactly the benchmark-selection
> issue Bartunov et al. existed to expose. Record both; do not harmonise.**

### 7.13 The honest verdict

**What is settled:**

1. **Exact backprop, as formulated for ANNs, is not implemented in cortex.** Nobody in this literature argues otherwise, **including Hinton** (co-author of both Bartunov et al. 2018 and Lillicrap et al. 2020).
2. **Weight symmetry is not necessary** for a learning signal to be useful (Lillicrap et al. 2016). **This retires the strongest form of the weight-transport objection.**
3. **Weight transport can be removed at ImageNet scale without a large accuracy cost — provided the feedback path *learns*** (Akrout et al. 2019). **This is the strongest positive result in the area and it materially softens the usual pessimism.**
4. **The family of viable proposals is named and unified: NGRADs.**
5. **Cortical biology supplies plausible substrate for the missing pieces** — segregated apical vs basal compartments, interneuron-computed apical prediction errors, burst-multiplexed dual channels on one axon, and eligibility traces with second-scale constants (0.3–2 s).

**What is not settled:** whether any rule that is *simultaneously* local, phase-free,
spike-compatible, weight-sharing-free and transport-free can match backprop at scale; whether
the plasticity rules these models assume (notably pairwise STDP) exist at physiological calcium
in adult tissue; and ⚠️ **no 2024–2026 primary paper on backprop plausibility was found, so the
state of the art stated here is "as of ~2023."**

---

## Sources

Research compiled **2026-11-13** from primary literature via NCBI E-utilities, Europe PMC REST
and ar5iv/arXiv. ⚠️ **Access failures that shape this file:** NCBI Bookshelf is behind reCAPTCHA
(**no Purves citation appears anywhere**); Kandel, Koch, Dayan & Abbott and Bear were
unobtainable; **Hebb's 1949 book was never opened by anyone in this chain, including this
dossier**; *jneurosci.org* returns 403 and Europe PMC returns 500 for several *J Neurosci*
records; nature.com, science.org, sciencedirect.com and pnas.org return 403.

**Read in full text:** Brown 2021 (PMC8566713); Markram, Gerstner & Sjöström 2011 (PMC3187646);
Abraham, Bliss, Collingridge & Morris 2024 (PMC11343267); Inglebert & Debanne 2021 (PMC8488271,
incl. Table 1); Oja's and Cooper's own Scholarpedia entries; *PLoS Comput Biol* 2016 (PMC4777380);
Milstein et al. 2021 (PMC8776257); Lillicrap et al. 2016 (PMC5105169); Bartunov et al. 2018 (via
ar5iv, incl. Tables 1–2); Akrout et al. 2019 (via ar5iv, incl. results); Launay et al. 2020 (via
ar5iv, incl. Table 7); Rosenbaum 2022 (PMC8970408); Hwang, Lee et al. 2023 (PMC10336230).

**Abstract or record only (flagged inline):** Markram et al. 1997; Bi & Poo 1998; Bliss & Lømo
1973; Bliss & Gardner-Medwin 1973; Collingridge et al. 1983; Matsuzaki et al. 2004; Engert &
Bonhoeffer 1999; Frey & Morris 1997/1998; Routtenberg & Rekart 2005; Ryan et al. 2015; Liu et al.
2012; Ramirez et al. 2013; Nicoll, Oliet & Malenka 1998; Gerdeman et al. 2002; Ito 2002; Debanne
et al. 1999; Zhang et al. 1998; Feldman 2000; Sjöström et al. 2001; Pfister & Gerstner 2006;
Clopath et al. 2010; Graupner & Brunel 2012; Shouval et al. 2010; Letzkus et al. 2006; Froemke et
al. 2002/2005; Sjöström et al. 2008; Pawlak & Kerr 2008; Seol et al. 2007; Brzosko et al. 2017;
Lisman & Spruston 2005/2010; Inglebert et al. 2020; Izhikevich 2007; Frémaux & Gerstner 2016;
Yagishita et al. 2014; He et al. 2015; Bittner et al. 2017; Turrigiano et al. 1998; Kim et al.
2012; Hanes et al. 2020; Stellwagen & Malenka 2006; Desai et al. 1999; Zenke et al. 2017; Abraham
& Bear 1996; Nøkland 2016; Lee et al. 2015; Whittington & Bogacz 2017/2019; Millidge et al.;
Scellier & Bengio 2017; Laborieux et al.; Guerguiev et al. 2017; Sacramento et al. 2018; Payeur et
al. 2021; Lillicrap et al. 2020; Hinton 2022; Roelfsema & Holtmaat 2018.

**Not obtained at all:** Hebb 1949; Löwel & Singer 1992 body; Shatz 1992; Oja 1982; Bienenstock,
Cooper & Munro 1982 body; Miller & MacKay 1994; Lømo 1966; **Crick 1989 body (so no Crick
quotation appears here)**; Grossberg 1987; Hinton & McClelland 1988; Martin, Grimwood & Morris
2000.

---

## Related

- [[neural-networks-biology]] — the parent skill.
- [[neural-networks-ml]] — where backprop, the learning rule this file assesses, actually lives.
- [[evolutionary-algorithms]] — the other biologically-inspired learning paradigm, and the one whose folklore has been checked the same way.
