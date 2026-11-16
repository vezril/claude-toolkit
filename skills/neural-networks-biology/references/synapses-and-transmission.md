# Synaptic transmission

Release machinery, the quantal and probabilistic nature of transmission, receptor
kinetics, the NMDA receptor as a coincidence detector, dendritic nonlinearity, gap
junctions, and neuromodulation — with the numbers people reuse checked against their
sources.

⚠️ marks a claim that is unverified, disputed, or folklore. Where two sources disagree,
both are recorded and **not** reconciled.

---

## 1. Release

### 1.1 The active zone

| Quantity | Value | Status |
|---|---|---|
| Active-zone area, hippocampal synapse | 0.060 µm² | model value from ultrastructural analysis (Gallimore et al., *Sci Adv* 2025, PMC12118552) |
| Docking sites per active zone | 8, each initially occupied | ⚠️ **model parameter** chosen inside literature ranges, justified by RIM1-Munc13 cluster counts — **not a direct measurement** |
| Ca²⁺ channels per active zone | 4 Cav2.1 | same, model value |
| Ca²⁺-channel-to-vesicle distance | typically **<100 nm** from docked vesicles | Südhof, *Neuron* 2013, PMC3866025 (attributing to Eggermann et al. 2011) |
| Calyx of Held | **~550 active zones** per terminal; tens of thousands of vesicles; in vivo quantal content **<~20 vesicles per active zone** | Denker & Rizzoli, *Front Synaptic Neurosci* 2010, PMC3059705 |
| Physical scale of the apposition | calyx of Held **~20 µm** across; parallel-fibre→molecular-layer-interneuron **~1 µm** | Wang & Dudko, *eLife* 2021, PMC8776255 |

### 1.2 Vesicle pools — and the labs disagree

Definitions (Denker & Rizzoli 2010): the **readily releasable pool** is the docked and
primed subset released immediately; the **recycling pool** recycles under physiological
stimulation; the **reserve pool** is reluctant, recruited only at high frequency after
the recycling pool depletes.

- recycling pool **~10–20%** of all vesicles in the terminal
- cultured hippocampal neurons: **≥~50% of vesicles are resting / non-releasable**
- frog and *Drosophila* NMJ: under **strong** stimulation virtually all vesicles recycle; under **mild** stimulation **50–80% remain unused**
- frog NMJ: **~30% of vesicles labelled "recycling" lost that status after several minutes of rest** — i.e. **pool identity is not a fixed label**
- surface pool (vesicle protein already on the plasma membrane): ~2% (vGlut1) to ~24% (synaptotagmin, synaptobrevin) depending on the protein and the tool

⚠️ **Denker & Rizzoli give no absolute RRP size for any preparation and no total vesicle
count for frog NMJ or hippocampal boutons. Anyone quoting a crisp "RRP = N vesicles" is
quoting a model or a single prep, not a consensus.**

**Open disagreements they record:** whether a **separate spontaneously-recycling pool**
exists (yes: Sara 2005, Chung 2010, Fredj & Burrone 2009; no: Groemer & Klingauf 2007) —
they explicitly conclude it is **unresolved**; a **dye artefact** (FM 2-10 used at 400 µM
vs FM 1-43 at ≤10 µM; the dyes act as detergents); and **fusion mode** — kiss-and-run vs
full collapse plus clathrin-mediated endocytosis, **still disputed**.

⚠️ **Retrieval timing is unsettled by ~2 orders of magnitude.** Gallimore et al. model a
mean retrieval of **6.8 s** (experimental hippocampal mean quoted as ~5–40 s, endocytosis
lag ~2–3 s). Watanabe et al., *Nature* 2013 (PMC3957339) report **"ultrafast
endocytosis"** — fusion within **~30 ms** and compensatory endocytosis within
**50–100 ms**. These are different measurements (flash-and-freeze EM vs pHluorin/dye
retrieval, different temperatures and stimulation). **Do not average them.**

### 1.3 The Ca²⁺ trigger — and the cooperativity exponent is not 4

| Quantity | Value | Status |
|---|---|---|
| [Ca²⁺] step that triggers fast release | **~10 µM** depletes most of the available pool within **3 ms** (calyx of Held, Ca²⁺ uncaging) | ⚠️ Schneggenburger & Neher, *Nature* 2000 — abstract only, paywalled |
| Sensitivity range | **~1 µM** already evokes release; **>30 µM** depletes the releasable pool in **<0.5 ms** | ⚠️ Bollmann, Sakmann & Borst, *Science* 2000 — abstract only |
| Residual Ca²⁺ after an AP | tens to a few hundred **nM** | Wang & Dudko 2021 |
| Presynaptic Ca²⁺ transient width | **~1–10 ms** | Wang & Dudko 2021 |

⚠️ **Südhof 2013 gives no microdomain Ca²⁺ concentration in µM. Do not attribute one to
him.**

**The cooperativity exponent, carefully:**

- **~4–5** for synaptotagmin-dependent **synchronous** release at the calyx of Held
- **~1–2** for **asynchronous** release in Syt2-knockout calyx synapses
- **~2** for spontaneous minis in Syt1-knockout hippocampal neurons, versus **~4** for normal minis
- the classic 4th-power law traces to Dodge & Rahamimoff 1967 ⚠️ (not opened)
- **Wang & Dudko 2021 state flatly that the exponent *"is not a universal number (e.g., 4)"*** and report fits to some calyx-of-Held data giving **n_Ca > 5**

> **"The Ca²⁺ cooperativity of release is 4" is a reasonable shorthand for synchronous,
> synaptotagmin-1/2-driven release at the calyx of Held and the frog NMJ.** It is not a
> constant, it is not ~4 for asynchronous release, and at least one open-access analysis
> puts it above 5 for some calyx data. **The exponent is a property of the sensor and the
> release mode.**

### 1.4 SNARE machinery

All from Südhof 2013 (PMC3866025, full text); inner attributions are his.

- **Synaptobrevin/VAMP2** — the vesicular SNARE, **~70 copies per vesicle**
- **Syntaxin-1 and SNAP-25** — the plasma-membrane SNAREs. Syntaxin-1 begins **closed** and must be opened before assembly can proceed
- **Munc18-1** (SM protein) binds closed syntaxin-1 and is **essential** for synaptic fusion. ⚠️ Südhof flags its proposed lipid-mixing role as a **hypothesis**, not established
- **Munc13** — priming factor; converts syntaxin-1 closed → open
- **Complexin** — ~130 residues; has priming, activating **and clamping** roles
- **Synaptotagmin-1** — the Ca²⁺ sensor. **The cleanest argument:** a mutation that lowered Syt1 C2-domain Ca²⁺ affinity ~2-fold also lowered the Ca²⁺ affinity of **release** ~2-fold. ⚠️ Südhof gives **no absolute Syt1 K_d** — do not quote one to him
- **Syt2 is the fastest** synaptotagmin, **Syt9 the slowest**, with kinetics matched to the synapses expressing them. **Syt7 is a facilitation sensor**, distinct from the fast synchronous sensor
- **RIM/RIM-BP** dock and prime vesicles and recruit Ca²⁺ channels to release sites

**How many SNARE complexes per fusion event? The field has no agreed number.** Südhof:
fusion can be driven by **1–3** complexes (minimum sufficient). Wang & Dudko: best fit is
**N = 2 independent SNARE super-assemblies** per vesicle, **~6 SNAREs** total, with each
additional SNARE in a super-assembly raising the release rate **~100-fold**. These are
different kinds of claim.

**Ca²⁺ raises the release rate ~10⁶-fold over baseline.** Spontaneous fusion averages
**~0.004 Hz per excitatory synapse**.

**Speed:** release occurs in **under a millisecond**; Ca²⁺ triggers release *"within a few
hundred microseconds"* and can trigger fusion in **under 100 µs**. Two independent reviews
converge, both tracing it to Katz & Miledi 1965 / Sabatini & Regehr 1996 ⚠️ (neither
primary opened). Note Südhof himself calls this time window *"the least compelling
argument"* for SNARE pre-assembly — **he does not treat sub-100-µs fusion as settling the
mechanism.**

⚠️ The 2013 Nobel Prize to Rothman, Schekman and Südhof is **recollection only here** — no
source was opened for the prize citation, and **no Rothman or Schekman paper was read.**

---

## 2. Quantal release — and what it does to the "weight" abstraction

### 2.1 The Katz papers

⚠️ **Metadata only for all three** (*J Physiol* 1952/1954 are not in PMC):

- Fatt & Katz, "Spontaneous subthreshold activity at motor nerve endings," *J Physiol* 1952;117:109–128
- del Castillo & Katz, "Quantal components of the end-plate potential," *J Physiol* 1954;124:**560–573**
- del Castillo & Katz, "Statistical factors involved in neuromuscular facilitation and depression," *J Physiol* 1954;124:**574–585**

**The two 1954 papers are back to back in the same volume. Citations that merge them into
one paper are wrong.**

⚠️ The content claim (that Fatt & Katz reported spontaneous miniature end-plate potentials
and del Castillo & Katz established integer multiples of the miniature unit) is
**recollection only** — the papers were not readable. Do not upgrade it without opening
them.

### 2.2 The verified anchor: a central synapse at physiological Ca²⁺

Optical quantal analysis with iGluSnFR at hippocampal CA3→CA1 Schaffer collateral
boutons, organotypic slice, 33 °C (Durst et al., *Nat Commun* 2022, PMC9576736, full text):

| Quantity | Value |
|---|---|
| Readily releasable vesicles per bouton, **N** | **median 3** (IQR 2–4). ⚠️ Range stated as **1–8 in Results and "1–9" in Discussion — the paper's own two statements disagree by one.** Only 2 of 27 boutons had a single docked vesicle |
| **p_ves** at 1 mM external Ca²⁺ | **median 0.08** (IQR 0.04–0.12), n = 27; Discussion gives the range as 0.01–0.23 |
| **p_ves** at 4 mM external Ca²⁺ | median **0.79** (IQR 0.55–0.94); median fold-change **9.9×** |
| Synapse-level **p_syn** | **0.26 ± 0.03 at 1 mM (≈74% failures)**, CV 0.61; **0.87 ± 0.04 at 4 mM** (≈13% failures). At 2 mM, p_syn spanned **0.17 to 0.99 across boutons** |
| Quantal size **q** | binomial-fit median 0.84 (IQR 0.63–1.18); CV across boutons 0.33 |
| **What sets strength** | At 1 mM, **p_ves alone explains R² = 0.85** and **N is uncorrelated**. At 4 mM, N (R² = 0.28) and p_ves (R² = 0.42) jointly determine it. **q barely matters either way** |

**Release probability also varies along the dendrite** — it **increases** toward distal
dendrites, boosting high-frequency signal transfer (⚠️ Jensen et al., *eLife* 2021,
PMC7837677 — record only).

**Cortical connections are heterogeneous by target:** L5 thick-tufted pyramid→pyramid has
*"high initial probability of release"* (⚠️ no number given in the review read), while
connections onto **Martinotti cells have low p and facilitate** and those onto **basket
cells have high p and depress** (Ramaswamy & Markram, *Front Cell Neurosci* 2015,
PMC4481152).

⚠️ **No NMJ quantal content was verifiable here.** The commonly quoted frog/mammalian NMJ
quantal content of order 10² quanta per end-plate potential and mEPP amplitude of order
0.5–1 mV is **recollection only. Do not quote an NMJ quantal content from this file.**

> **The order-of-magnitude point:** the vertebrate NMJ is built never to fail — one
> presynaptic AP releases many quanta across a large end-plate. **A central
> cortical/hippocampal synapse releases at most a handful of vesicles from a handful of
> docked vesicles and fails most of the time at physiological Ca²⁺.** The Durst numbers
> are the verified anchor for the central half of that claim; the NMJ half is unverified.
>
> Also note the **calyx of Held is an auditory relay designed for reliability** — ~550
> active zones. **Its numbers should not be generalized to cortex.**

### 2.3 Consequence for "weight"

1. A cortical synapse's strength is **p_ves · N · q**, with N of order 1–8 and p of order 0.1–0.3 at physiological Ca²⁺.
2. At low p, strength is **almost entirely p_ves** (R² = 0.85) and almost not at all N or q — so **the quantity an ML "weight" stands in for is mostly a presynaptic release probability, not a postsynaptic gain.**
3. p is not a fixed scalar: it changes ~10-fold with external Ca²⁺, varies along the dendrite, and changes within a spike train.

> **A single scalar weight is a statement about the mean of a stochastic,
> history-dependent, few-vesicle process.** That is a modelling choice, not a measured
> property.

### 2.4 Short-term plasticity — the Tsodyks–Markram parameters everyone reuses

Model: resources partition into effective (E), inactive (I) and recovered (R) fractions;
each AP activates a fraction **U_SE** of R; τ_inact is a few ms, τ_rec ~1 s. Higher U_SE →
faster depression.

Fitted values as printed:

| Figure | τ_inact | τ_rec | U_SE | A_SE | τ_mem |
|---|---|---|---|---|---|
| 1B | 3 ms | 800 ms | 0.67 | 250 pA | 50 ms |
| 1C | 3 ms | 450 ms | 0.55 | 530 pA | 30 ms |
| 3B | 3 ms | 700 ms | 0.40 | — | 25 ms |

⚠️ **Across 33 connections, U_SE ranged 0.1 to 0.95. There is no single "the" U_SE.**
Pairing raised it from 0.50 ± 0.23 to 0.69 ± 0.18 (18 connections).

⚠️ **The preparation, usually omitted when the model is cited:** synapses between **layer
5 pyramidal neurons in the somatosensory neocortex of 13–15-day-old Wistar rats**, dual
whole-cell patch, 30–32 °C. **The authors state they studied only immature synapses**,
while asserting adult behaviour is similar.

**Limiting frequency:** above it, stationary EPSP amplitude falls as **1/f**. Measured
limiting frequencies were **10–25 Hz** in the 11 synapses tested; higher U_SE gives a
lower limiting frequency.

**The core claim:** beyond the limiting frequency the average depolarization does **not**
depend on release probability; changing p instead **redistributes** synaptic efficacy
between spikes in a train. **High U_SE favours temporal coding, low U_SE favours rate
coding.** Verified: Tsodyks & Markram, *PNAS* 1997;94(2):719–723, PMC19580 (full text).

⚠️ **Abbott, Varela, Sen & Nelson, *Science* 1997 (the "cortical gain control" paper) was
not readable** — and its Europe PMC record gives pages 220–224 while the DOI suffix
encodes ".221". **Cite with care.** The 1/f steady-state phenomenon it is cited for *is*
independently verified from Tsodyks & Markram; the specific Abbott–Varela treatment is
not.

**Two mechanistic corrections:**

- ⚠️ **Residual Ca²⁺ alone cannot account for facilitation.** Residual-Ca²⁺-only models give a paired-pulse-ratio upper bound of **~1.02**. This is a real constraint on the textbook "residual calcium" story (Wang & Dudko 2021). The facilitation sensor is **synaptotagmin-7**.
- An alternative on the record: progressive **overfilling of the readily releasable pool** underlies short-term facilitation at recurrent L2/3 prefrontal synapses (⚠️ Shin et al., *eLife* 2026, PMC12890252 — record only).

---

## 3. Receptors

Primary source throughout §3A: **Hansen et al., "Structure, Function, and Pharmacology of
Glutamate Receptor Ion Channels," *Pharmacol Rev* 2021;73(4):298–487, PMC8626789.** ⚠️
Read as selected 100-kchar chunks of a 3.4-Mchar document (Table 1 in full, sections
IV–VI.E, parts of X) — **not the whole review.**

| Family | Subunits | Genes |
|---|---|---|
| AMPA | GluA1–GluA4 | GRIA1–4 |
| Kainate | GluK1–GluK5 | GRIK1–5 |
| NMDA | GluN1; GluN2A–D; GluN3A–B | GRIN1; GRIN2A–D; GRIN3A/B |
| Delta | GluD1–GluD2 | GRID1–2 |

### 3.1 AMPA

From Table 1 (rat, glutamate), the pattern that matters: **FLOP variants desensitize 2–5×
faster than FLIP**, and **recovery from desensitization is the slowest step by 1–2 orders
of magnitude** (6–155 ms vs 1–10 ms for deactivation and desensitization). Running text:
AMPA receptors without auxiliary subunits **deactivate in 1–5 ms**; desensitization onset
for AMPA and kainate is **under 20 ms**.

⚠️ The **GluA4 FLOP glutamate EC50 of 56 µM** is a ~20–30× outlier against every other
AMPA row (450–1970 µM) — **reported as printed and flagged as suspicious**; it may be a
different measurement condition.

**Single-channel conductance.** Hansen et al. state AMPA receptors open to **four**
conductance levels but the pS values were not in the chunks read. One direct measurement
*was* verified: GluA2-γ2 in a planar lipid bilayer at −60 mV with cyclothiazide gives
**O1 = 8.2, O2 = 18.8, O3 = 27.0, O4 = 37.0 pS**, with O1 dominating at 20 µM glutamate
and O2 at 10 mM (Yelshanskaya et al., *Nature* 2022, PMC9068512). ⚠️ **But this is a
fusion construct in a reconstituted bilayer with a desensitization blocker — not "the
native AMPA receptor conductance in a neuron." The familiar textbook ~8–10 pS for native
AMPA channels is unverified here.**

**The GluA2 Q/R editing story.** The Q/R site is **>99% edited in vivo**; editing
substitutes Arg for Gln in the M2 pore loop, making the channel **Ca²⁺-impermeable** and
insensitive to intracellular polyamines (hence loss of double rectification). So most
forebrain AMPA receptors are Ca²⁺-impermeable, and AMPA receptors **lacking** GluA2 are
Ca²⁺-permeable and inwardly rectifying. ⚠️ **The "most AMPARs contain GluA2" step is the
standard inference; no numeric GluA2-occupancy fraction was read. Treat the fraction as
unverified.**

⚠️ **Kainate Q/R editing numbers disagree within the same review:** one section gives
GluK1 ~40% edited and GluK2 *"under 5% to 75%"*; another (hippocampus-specific) gives
GluK1 ~50% and GluK2 70–85%. **The spread is real** — GluK2 editing is developmentally and
regionally variable and the literature does not agree.

### 3.2 Kainate — functionally almost always off

**Kainate receptors recover from desensitization in 0.9–3.8 *seconds*, 1–2 orders of
magnitude slower than AMPA receptors (6–155 ms).** One homomeric row shows a
steady-state/peak ratio of **0.003–0.008**, i.e. **>99% desensitized at steady state.**

### 3.3 NMDA — a 50-fold range in open probability, and a >100-fold range in kinetics

Running-text summary values (the clean ones to quote):

| Subunit combination | Deactivation | Open probability | P_Ca/P_monovalent | Glutamate EC50 |
|---|---|---|---|---|
| GluN1/2A | **~35 ms** | **~0.5** | ~4 | 1.8–7.7 µM |
| GluN1/2B | **~200 ms** | ~0.1 | ~4 | 0.9–4 µM |
| GluN1/2C | ~200 ms | **0.01** | ~2.5 | 1.0 µM |
| GluN1/2D | **several seconds** (1700–4400 ms) | **0.01** | ~2.5 | **0.4 µM** |

**NMDA receptors activate in several milliseconds** — the rise is slow too, not just the
decay. Triheteromers are intermediate (GluN1/2A/2B: 57–143 ms). The **GluN1-1b splice
cassette** (exon 5) makes receptors deactivate **faster** than GluN1-1a.

> **Open probability ranges 0.01 to ~0.5 — a 50-fold range — and deactivation 35 ms to
> ~4 s. A "GluN2D synapse" and a "GluN2A synapse" are not the same computational device.**
> This is routinely flattened by the phrase "the NMDA receptor."

Single-channel conductance: **20–50 pS** in neurons; GluN1/2A and GluN1/2B ~50 pS main
level with a ~40 pS subconductance (<10% of openings); GluN1/3A native weighted mean
**6 pS**. Pore size 0.55–0.8 nm. Peak cleft glutamate ⚠️ **~1.1 mM — an estimate stated in
the review, not an in-situ measurement.**

⚠️ **The "0.28–42" steady-state/peak entry printed for GluN1/2A is almost certainly a
column misalignment in the converted table. Do not propagate "42."**

### 3.4 The NMDA receptor as a coincidence detector — and the complications

**The four requirements:**

1. **Voltage-dependent Mg²⁺ block, relieved by depolarization.** Hansen et al. attribute this to **Mayer et al. 1984** and **Nowak et al. 1984**. ⚠️ **Neither paper was opened, and Hansen et al. give no numeric Mg²⁺ affinity, IC50 or voltage-dependence parameter in any chunk read. The commonly quoted Mg²⁺ IC50 of ~10–30 µM at −70 mV, and the figure that block is relieved over roughly −70 to −20 mV, are recollection only. Do not quote a magnesium IC50 from this file.**
2. **The dual ligand + voltage requirement** — the AND-gate. Verified in substance. ⚠️ **But the AND-gate is not instantaneous in either direction:** activation takes several ms and deactivation 35 ms (GluN2A) to seconds (GluN2D). **The coincidence window is set by the GluN2 subunit and is tens to hundreds of ms, not microseconds** — which is why NMDARs can detect coincidence across a behaviourally meaningful window at all.
3. **The glycine/D-serine co-agonist requirement.** Verified; glycine EC50 falls 0.86 µM (GluN1/2A) → 0.12 µM (GluN1/2D), and is **48–81 µM for GluN1/3A because GluN1/3 receptors are glycine-*gated*, not glutamate-gated.** ⚠️ **The usual "Johnson & Ascher 1987" citation could not be verified** — the chunks read state the co-agonist requirement without citing it, and no bibliographic record was retrieved. **Do not cite Johnson & Ascher from this file.** D-serine specifically is required for dendritic NMDA spikes, so **NMDA spikes depend on the timing and spatial distribution of co-agonist along the dendrite** — not just of glutamate.
4. **Ca²⁺ permeability and slow kinetics.** P_Ca/P_monovalent ~4 (2A/2B), ~2.5 (2C/2D) — i.e. **Ca²⁺ permeability is also subunit-dependent.** NMDAR current *"persists for tens to hundreds of milliseconds."*

**A nice, under-quoted structural fact:** swapping the GluN1 pore "N site" Asn for Gln
strongly alters **Ca²⁺ permeability** but only weakly affects **Mg²⁺ block**; the same
change at the GluN2 N site does the reverse. **Ca²⁺ permeation and Mg²⁺ block are
structurally separable.**

**Why this makes it a Hebbian detector** (each premise verified separately; the synthesis
is the dossier's): presynaptic activity supplies glutamate; postsynaptic activity supplies
the depolarization that relieves Mg²⁺ block; only their **conjunction** admits Ca²⁺; and
the slow decay sets a tens-to-hundreds-of-ms tolerance for "coincidence."

**Three complications to state alongside it:**

- **Subunit heterogeneity defeats a single story** (above).
- ⚠️ **Extrasynaptic NMDARs** — the claim that they couple preferentially to pro-death signalling (the Hardingham & Bading dichotomy) is **recollection only here; no source opened.**
- ⚠️ **NMDAR-independent plasticity exists** — MK-801 left *"a small NMDAR-independent potentiation"* of high-frequency-stimulation LTP in adults (Babiec et al., *J Neurosci* 2014, PMC3983804, full text).

### 3.5 The metabotropic-NMDAR dispute — unresolved, and record it as unresolved

**Claim (Nabavi et al., *PNAS* 2013, PMC3593861, full text read):** ligand binding to
NMDARs is **sufficient** to induce LTD; neither ion flow nor a Ca²⁺ rise is required.
D-APV (glutamate-site antagonist) blocked LFS-LTD; **MK-801 (open-channel blocker) did
not**; 7-chlorokynurenate (glycine-site) did not. Both MK-801 and 7CK blocked
NMDAR-mediated responses by **>99%** during LFS. NMDA-induced p38 phosphorylation was
blocked by D-APV but **not** by MK-801. Rat, 2–3 weeks old.

**Counter-claim (Babiec et al., *J Neurosci* 2014, PMC3983804, full text read):** MK-801
at **2–10× lower concentration** blocked 1 Hz LFS-LTD in both adult and young **mice**,
blocked chemical LTD, **and blocked NMDA-induced p38-MAPK activation and GluA1
dephosphorylation** — the direct contradiction of Nabavi's p38 result. Conclusion: *"the
induction of LTD in the hippocampal CA1 region is dependent on ionotropic, rather than
metabotropic, NMDAR signaling."*

They consider three explanations and reject the first two (incomplete block in their own
hands; insensitive assays in Nabavi's), leaving **species — rat vs mouse** — which they
find *"surprising"* for so fundamental a property. The Malinow lab's reply exists in print
(Nabavi et al., *Phil Trans R Soc B* 2014, PMC3843877) ⚠️ but was not read.

> **Two well-equipped labs, a published exchange, a rat-vs-mouse confound, and directly
> contradictory p38-MAPK results. Do not present ion-flux-independent ("metabotropic")
> NMDAR signalling as established, and do not present it as refuted.**

### 3.6 Other ionotropic receptors

**GABA_A** — 19 subunits; heteropentamer, commonest arrangement 2α + 2β + 1γ, ordered
γ2-β2-α1-β2-α1 counterclockwise from outside. **Synaptic (phasic)** compositions use
mainly α1–3, β1–3, γ2; **extrasynaptic (tonic)** use mainly α4–6, β2/3, δ. α2, α3 and β3
receptors are **~100× more concentrated at synapses** than extrasynaptically.

⚠️ **The source read gives no single-channel conductance in pS, no E_Cl, and no IPSC decay
time constants.** Farrant & Nusser's canonical tonic-vs-phasic review is paywalled and was
not read — **any specific tonic-current amplitude or ambient-GABA concentration attributed
to it is unverified here.**

One verified point on **sign**: *"Tonic excitation or inhibition is set by GABA(A)
conductance in hippocampal interneurons"* (Song, Savtchenko & Semyanov, *Nat Commun* 2011,
PMC3144593) — **the title itself makes the point that tonic GABA_A conductance can be
excitatory.**

**Glycine receptors** — the cleanest conductance numbers anywhere in this dossier.
Main-state single-channel conductance, homomeric (with β co-expressed in parentheses):
**α1 = 86 pS (44), α2 = 111 pS (54), α3 = 105 pS (48)**. ⚠️ **Including β roughly halves
the conductance, and native receptors are α-β heteromers — so quoting the homomeric number
as "the glycine receptor conductance" overstates it ~2×.** (α4/GLRA4 is **a pseudogene in
humans**.)

**Nicotinic ACh receptors** — P_Ca/P_Na by subtype: fetal muscle 0.16–0.2; adult muscle
0.65–1.38; α3β4 0.78–1.1; α4β2 1.65; **α7 6.6–20**.

> **Homomeric α7 is 4–100× more Ca²⁺-permeable than every other nicotinic subtype and
> ~4× more Ca²⁺-permeable than an NMDA receptor.** "Nicotinic receptors are Na⁺/K⁺
> channels" is wrong for α7. **Muscle nicotinic receptors are the least Ca²⁺-permeable.**

⚠️ No nAChR single-channel conductances or kinetic constants were in the chunk read; the
familiar ~20–50 pS / sub-ms burst figures are **unverified here.**

### 3.7 Metabotropic receptors — and an honest limit

⚠️ **Only the 5-HT1/5-HT2 and β-adrenoceptor sections of the Concise Guide 2025/26 GPCR
volume were read. The dopamine, muscarinic and mGlu sections were not.** What *is*
verified: all 5-HT receptors are GPCRs **except 5-HT3**, a ligand-gated ion channel; and
**RNA editing of 5-HT2C produces isoforms differing in the efficiency and specificity of
Gq/11 coupling** — the same gene yielding receptors with different G-protein coupling.
β1/β2/β3 all couple to Gs; β2 and β3 can also activate Gi; β2 additionally signals through
β-arrestin. mGlu and GABA_B both sit in the **glutamate (class C)** GPCR family.

⚠️ **Unverified recollection, stated as such and not as citations:** mGlu group I (mGlu1,
5) Gq/11-coupled and postsynaptic; group II (2, 3) and group III (4, 6, 7, 8) Gi/o-coupled
and largely presynaptic; GABA_B a GABA_B1+B2 heterodimer, Gi/o-coupled, presynaptically
inhibiting Ca²⁺ channels and postsynaptically opening GIRK/Kir3 for a slow IPSP; dopamine
D1-like (D1, D5) → Gs/Golf, D2-like (D2, D3, D4) → Gi/o; muscarinic M1/M3/M5 → Gq/11,
M2/M4 → Gi/o; α1 → Gq/11, α2 → Gi/o. **These are standard and probably right, but they are
not sourced here.**

**The one verified timescale anchor** — fitted PSC decays in a rat neocortex model:

| | Synaptic | Volume |
|---|---|---|
| ACh | 241.2 ± 15.5 ms | 608.6 ± 109.7 ms |
| DA | 220.2 ± 41 ms | 400 ± 100 ms |
| 5-HT | 440 ± 30 ms (all target classes) | |

⚠️ **These are model PSC decay parameters, not direct measurements.** But the *order* is
the point and it is sound: **metabotropic effects decay over 200–600 ms, ~10× slower than
a GluN2A NMDA current and ~500× slower than an AMPA current. That ratio is the
computationally important fact.**

---

## 4. EPSPs, reversal potentials, shunting, integration

### 4.1 Unitary EPSP amplitudes — and the confounds are the point

Compiled from ~50 primary studies by de Kock & Feldmeyer, *Front Synaptic Neurosci* 2023,
PMC10508294 (full text, Tables 1–2).

**Summary:** median uEPSP **0.5 mV**, IQR 0.4–1.0 mV; range of cell-type-connection medians
0.1–1.4 mV. For L2/3 pyramid→pyramid across all species: **median 0.46 mV (mouse 0.43, rat
0.57, macaque 0.45, human 0.48).** Total L2/3 span across studies **0.18–2.01 mV**.

> ⚠️ **The 11-fold spread tracks [Ca²⁺]_o (1.3 vs 2 vs 3 mM), temperature (23–37 °C), and
> median-vs-mean reporting at least as much as it tracks species.** The three highest human
> values (1.12, 1.56, 2.01 mV) were all at 34–37 °C and the highest at 3 mM Ca²⁺; the
> lowest human value (0.18 mV) was at 31–33 °C and 1.3 mM Ca²⁺. **Any "human synapses are
> stronger than mouse synapses" claim read off these tables is confounded** — the authors'
> own species medians (0.43–0.57 mV) show essentially **no** species difference once
> connection type is matched.

⚠️ **What their tables do not contain:** no failure rates, no release probabilities, no
contact counts per connection, no CVs, no rise/decay constants, no paired-pulse ratios.

**One verified set with full kinetics** — L5 thick-tufted pyramid pairs: amplitude
0.15–5.5 mV, **mean 1.3 ± 1.1 mV**; onset latency **1.7 ± 0.9 ms**; 20–80% rise time
2.6 ± 2.3 ms; decay τ **40 ± 18 ms**; ~4–8 putative contacts per connection (mean
5.5 ± 1.1); connection probability ~10%. ⚠️ **The 1.7 ms onset latency is axonal conduction
+ synaptic delay + EPSP onset, soma to soma. Do not quote it as a synaptic delay.**

### 4.2 Reversal potentials — zero verified values

> ⚠️ **Not a single canonical reversal-potential value was verified in this dossier.**
> Stated loudly, because these are exactly the numbers people assume are free.

Recollection only, standard mammalian central neuron: E_Na ~ +50 to +60 mV; E_K ~ −90 to
−100 mV; E_Cl ~ −70 to −80 mV in a mature neuron; E_AMPA/E_NMDA ~ 0 mV; E_GABA_A ≈ E_Cl
with a small HCO₃⁻ contribution, typically quoted −60 to −75 mV.

⚠️ The **one** quantitative thing verified is a chloride *concentration*, not a reversal
potential: steady-state [Cl⁻]ᵢ of **30 mM in immature rat Cajal–Retzius cells**. And it is
worth noting how surprising the gap is: **a dedicated review of CNS chloride homeostasis
(Watanabe & Fukuda, PMC4585146) does not print the reversal potentials at any stage.**

### 4.3 The developmental E_Cl shift — and its published dispute

Timecourse (Watanabe & Fukuda 2015): neonatal rat cortex has NKCC1 (Cl⁻ loader) highly
expressed and **KCC2 (extruder) at only ~5–15% of adult levels**; KCC2 mRNA rises sharply
**after the first postnatal week**; hippocampal KCC2 and NKCC1 both reach adult levels at
**~P15**; regional order is spinal cord / hypothalamus / thalamus → limbic → neocortex.

⚠️ **Internal disagreements the review itself flags:** rat spinal cord GABA switch placed
at **~E17–E19** by two groups but at **P4–P5** by another — a **~2–3 week** discrepancy;
hypothalamic KCC2 mRNA as early as E14.5 yet electrophysiology shows **excitatory GABA**
after birth; plus unresolved conflicts on GABA-driven KCC2 upregulation and on
BDNF-dependence.

**The dispute, as a dispute.** **Bregestovski & Bernard 2012** argue depolarizing GABA in
the immature brain is *"a correct observation but an experimental artifact"* — on grounds of
**energy substrates** (adding β-hydroxybutyrate, lactate or pyruvate to glucose-perfused
slices made GABA hyperpolarizing) and **slicing damage** (Dzhala et al. 2012). **Ben-Ari et
al. 2012 (PMC3428604, full text read) reply** with nine counters, including: multiple
groups report **no** substrate effect; the effects were attributed to intracellular **pH**
rather than metabolism; the pyruvate concentrations used were **~20–40× physiological**;
GABA excites immature neurons in **intact** preparations, not only slices; **axotomized**
mitral cells were *hyper*polarized while non-axotomized granule cells were *de*polarized at
similar depths — the opposite of what damage predicts; and the challenge is **internally
inconsistent**, since if slices were energy-deprived *and* surface neurons damaged, deep
neurons should also be depolarized.

⚠️ **A real asymmetry to state whenever this is cited: only the reply was read.** The
challenge's case is known here **only through its opponents' summary.**

### 4.4 Shunting inhibition — the widely repeated claim is wrong as stated

**Holt & Koch, "Shunting inhibition does not have a divisive effect on firing rates,"
*Neural Computation* 1997;9(5):1001–1013** (⚠️ abstract read; full text not in PMC). Their
argument: the spiking mechanism holds the somatic membrane potential well **above** rest,
so the current through a shunting conductance stays roughly **constant** across firing
rates — **a constant current subtraction, not a gain change.** At distal synapses the effect
is also largely subtractive when excitatory conductance is not small relative to
inhibitory. Their conclusion: adjusting passive membrane conductance is **not** an adequate
way to normalize or scale a cell's output.

> **The "conductance-based inhibition is divisive, current-based inhibition is subtractive"
> formula that circulates in computational neuroscience is at best a statement about
> *subthreshold voltage*, and is contradicted for *firing rate* by Holt & Koch. The
> subthreshold-vs-rate distinction is the crux and is usually elided.**

**And in vivo the question is live on both sides:**

- **Against shunting as the gain mechanism:** contrast gain control in auditory cortex occurs **independently of both PV-interneuron activity and shunting inhibition**; PV manipulation changed overall gain but not *contrast* gain control; and *"no increase in membrane conductance was observed during high-contrast stimulation"* (⚠️ Cooke et al., *J Neurophysiol* 2020, PMC7191518 — abstract only; scope is auditory cortex, not divisive inhibition in general).
- **For divisive effects:** shunting inhibition drives divisive normalization in fly vision (⚠️ Gur et al., *Nat Commun* 2024); GABA produces mainly **divisive** gain changes in prefrontal pyramidal cells (⚠️ Lucaci et al., *J Neurosci* 2023). Both abstract-level only.
- **And location matters:** "Location-dependent effects of inhibition on local spiking in pyramidal neuron dendrites" (⚠️ Jadi, Polsky, Schiller & Mel, *PLoS Comput Biol* 2012) — **the title alone establishes that divisive-vs-subtractive is not a single answer per cell.**

### 4.5 Integration — what is and is not verified

| Verified | |
|---|---|
| Membrane time constant | τ_m = R_m·C_m. Time constants for equalization **along** a cylinder are typically **2–10× smaller** than τ_m; **around** the circumference, *"typically about ten thousand times smaller"* (Rall, *Biophys J* 1969;9(12):1509–41, PMC1367650) |
| Cortical τ_m, actually fitted | **25, 30 and 50 ms** in three figures of Tsodyks & Markram 1997 — so **25–50 ms** is defensible for immature rat neocortical pyramids at 30–32 °C |
| Dendritic attenuation | EPSPs attenuate **up to 40-fold** from basal dendrites to soma at ~140 µm; somatic voltage attenuation of dendritic responses **~85%** at P28 |
| Channel gradients | **I_h (HCN) density increases >50-fold** from soma to distal apical dendrites; AIS Na⁺ density **~30–50× somatic** |
| Axonal conduction in an L5 pyramid | **~300 µm/ms (0.3 m/s)** |

⚠️ **Not verified: the length constant λ and the electrotonic length L.** Rall's 1969
paper on potential distributions **does not define L** — it cites a **companion** paper
(*Biophys J* 1969;9(12):1483–1508) which was not retrieved. **The two are back to back in
the same issue and people routinely cite the wrong one for L.** Also unverified: input
resistance in MΩ (the source read gives none), the Rall **3/2 power law**, and temporal and
spatial summation quantitatively.

**One verified datum on linearity**, from simulation: in a human L2/3 model, human-type
synapses shifted from **sublinear to supralinear summation at about 35 activated
synapses**, whereas rat-type and hybrid synapses stayed **linear below about 50**. ⚠️
**Simulated, not recorded.** The authors' mechanism: *"the stronger voltage-dependent NMDA
conductance, together with the steeper NMDA voltage dependence"* — **supralinearity is
NMDA-driven.**

---

## 5. The dendrite is not a passive summator

### 5.1 Dendritic spikes and BAC firing

From Ledergerber & Larkum, *PLoS ONE* 2012;7(3):e33146, PMC3302831 (full text):

Dendritic spikes initiate in the apical dendrite with a **fast Na⁺ component followed by a
slower Ca²⁺-dependent component.** In **L5** the Ca²⁺ component is particularly pronounced
and typically drives a **burst** of somatic APs; in **L6** the distal spike is reduced
relative to L5 and in **L2/3** reduced further — in L6 and L2/3, dendritic spikes add
somatic depolarization but **do not necessarily trigger axonal firing.**

Dendritic spike threshold (dendritic current injection, pA), baseline → with a
backpropagating AP:

| Layer | Baseline | With bAP |
|---|---|---|
| L2/3 | 1142 ± 419 (n=12) | 858 ± 350 |
| **L5** | **2011 ± 553 (n=9)** | **1144 ± 480 — a 41 ± 7% reduction, the largest of the three** |
| L6 | 770 ± 192 (n=5) | 500 ± 100 |

The **L5 coincidence window is the widest** and includes a **negative component** (EPSP
before AP), which the authors suggest reflects EPSPs influencing the backpropagating AP
itself.

⚠️ **The numeric window boundaries are not in the paper's text** — they exist only in a
figure that could not be read. **Anyone quoting a "BAC coincidence window = 10–20 ms" is
not quoting this paper's text.**

**Critical frequency** for regenerative Ca²⁺ spikes in apical and basal dendrites:
**~100 Hz**. Somatic bursts contain 2–3 APs at P28 and 2–4 at P42–P56.

### 5.2 NMDA spikes / plateau potentials

From Augusto & Gambino, *Front Mol Neurosci* 2019;12:238, PMC6777373 (full text):

- **Duration:** NMDAR current *"persists for tens to hundreds of milliseconds"*, and spike duration increases **linearly** with glutamatergic stimulation intensity — hence "plateau potential."
- **Threshold:** in distal dendrites an NMDA spike can be evoked by **~10 clustered spines**, or **~20 sparsely distributed inputs** along a longer dendrite. Depolarization lowers the threshold **two ways** — it reduces the glutamate needed to bind NMDARs, and it relieves Mg²⁺ block of nearby NMDARs.
- **Location:** NMDA spikes occur in **thin** dendrites, where most spines are; Ca²⁺ spikes occur in **thick** dendrites.
- **In vivo:** whisker deflection produced NMDAR-mediated plateau potentials in L2/3 tuft dendrites of barrel cortex **without somatic spiking**, and these plateaus triggered potentiation **that does not require action potentials.**

⚠️ **This review gives no NMDA-spike amplitude in mV and no specific duration in ms. The
commonly quoted "~20–40 mV, 50–200 ms" figures are unverified here.**

### 5.3 "A cortical neuron is a 5–8 layer deep network" — four problems

**(a) Poirazi & Mel.** The 2003 *Neuron* paper "Pyramidal neuron as two-layer neural
network" is bibliographically verified ⚠️ but **not read**; its contents (an L5 pyramid's
input–output function better fitted by a two-layer sum-of-sigmoidal-subunits model) are
**recollection only here.** ⚠️ **And "Poirazi & Mel 2001 *Neuron*" could not be found** —
a targeted Europe PMC search did not return it. **Do not cite it from this dossier.**

**(b) Beniaguev, Segev & London 2021** — *Neuron* 109(17):2727–2739.e3. ⚠️ **Not in PMC,
paywalled, not read.** What is verified, and from where:

| | |
|---|---|
| **Depth — preprint** | *"a **seven-layer** temporally convolutional network"* (bioRxiv abstract, verified) |
| **Depth — published** | *"**five to eight** layers"* (verified from the authors' own code-repository README quoting the published abstract) |
| **What it was fit to** | ⚠️ **A realistic but *simulated* L5 compartmental model (Hay et al. 2011), in NEURON — not a recorded cell.** This is the single most important caveat and it is routinely dropped |
| **The NMDA dependence** | **With NMDA receptors removed, "a fully connected neural network with one hidden layer" was sufficient.** The preprint abstract agrees the complexity *"mainly comes from local NMDA-based nonlinear dendritic conductances"* |

> **The preprint says seven layers; the published abstract says five to eight. The depth
> claim is a claim about NMDA nonlinearity, not about dendritic morphology.** ⚠️ **Any
> specific temporal filter size (the ~35 ms or 128 ms figures that circulate) is unverified
> here. Do not quote one.**

**(c) The 2026 follow-up from the same group** — Aizenbud, Yoeli et al. (Beniaguev a
coauthor, not first author), *PNAS* 2026, PMC13367794, **read in full.** 24 biophysical
pyramidal models (12 rat, 12 human; three per layer), all sharing identical passive
dendritic properties; a **three-layer TCN of 128 units per layer**; a "functional
complexity index" (FCI) from AUC of spike prediction at 1 ms resolution.

Results: mean FCI **0.3803 (human) vs 0.2244 (rat)**, P = 9.8 × 10⁻¹². With **rat**
synapses applied to **all** morphologies, human morphologies still scored higher
(P = 0.022) — **morphology contributes independently of synapse type.** A human L5 model
with **passive** dendrites scored higher than a rat L5 model with **active** dendrites.
Total dendritic area alone explained **R² = 0.74** of FCI variance.

⚠️ **Their own caveats, unusually candid:** all FCI values come from biophysical model
neurons driven by simulated input; the main models **omit active dendritic conductances**
(and supplementary rat tests show active channels **raise** FCI, so the human effect is
unknown); **human NMDA conductance was *assumed* ~3-fold higher** with a steeper voltage
dependence, taken from another study — **and they cite conflicting work (Testa-Silva et
al.) finding a *higher* NMDA-spike threshold in human L2/3 neurons**; FCI depends on the
chosen network (overly expressive networks compress differences, underexpressive ones
inflate them); input rates were tuned so all models fired at ~1 spike/s, i.e. **one
operating regime**; and reconstructed dendrite diameters were **edited** so none fell below
0.3 µm.

> **Note the tension with (b): the 2021 headline was "5–8 layers needed"; this 2026 paper
> from the same group uses a *three*-layer TCN as standard and reports results stable at
> depth 3. Depth is a property of the fitting objective and tolerance, not an invariant of
> the neuron.**

**(d) Gidon et al. 2020 — dendritic XOR in human L2/3.** ⚠️ **The paper (*Science* 2020,
doi:10.1126/science.aax6239) is not in PMC and was not read.** Its abstract states the
dendritic calcium spikes *"enabled the dendrites of individual human neocortical pyramidal
neurons to classify linearly nonseparable inputs."*

The commentary **was** read — Fişek & Häusser, "Are Human Dendrites Different?" *Trends
Cogn Sci* 2020, PMC7903140:

- Human L2/3 dendrites are **more** excitable than rodent L2/3 — ⚠️ **which contrasts with Beaulieu-Laroche et al., who reported human L5 dendrites are *less* excitable than rat L5.**
- **The XOR claim, precisely:** the spikes showed **biphasic** sensitivity — amplitude **fell** *"with higher levels of stimulation."* The authors then built a **simplified model** in which such dendrites could **in principle** implement exclusive-or. Fişek & Häusser present this as *"a model-based possibility, not as demonstrated computation in intact tissue."*
- Their caveats: not shown in vivo; results across studies are not fully consistent; **discrepancies in membrane capacitance and dendritic excitability *"will need to be carefully verified"***; human tissue is hard to standardize (disease state, area, cell type, pharmacological history, patient age).
- A model-based follow-up qualifies the mechanism: raising **sodium conductance and membrane capacitance weakens** XOR while potassium conductance has little effect — **so other conductances and capacitance matter, not only calcium** (Li, Zhang & Sun, *Cogn Neurodyn* 2024, PMC11655932). **This bears directly on Fişek & Häusser's flagged capacitance discrepancy.**

> **No formal technical comment or rebuttal to Gidon et al. was found.** The honest status:
> **the measurement is uncontested in what was read; the *computational interpretation* is
> explicitly flagged by the commentators as model-based and not demonstrated in intact
> tissue.**

---

## 6. Electrical synapses — and "they synchronize" is not a general answer

### 6.1 Connexin 36

Cx36 is the main synaptic connexin in the mammalian brain; humans have 21 connexin genes
(others neuronal: Cx45, Cx57, Cx30.2, Cx50). **Cx36 expression is restricted to neurons**
apart from microglia, pancreatic β cells and chromaffin cells. ⚠️ **The human gene symbol
GJD2 is recollection only — neither review read printed it. Do not cite GJD2 from here.**

**Voltage (in)dependence — an important negative:** Cx36 junctional conductance is nearly
insensitive to transjunctional voltage up to ±30 mV and falls to only ~60% over a 90 mV
range, and **its gating takes hundreds of milliseconds to seconds to reach steady state**,
so Curti & O'Brien judge **Cx36 synapses unlikely to be voltage-gated during normal
spiking.** By contrast Cx45 is more voltage-sensitive (half-maximal reduction at 13.4 mV).

**Modulation:** Cx36 coupling is regulated by phosphorylation via cAMP/PKA, NO/PKG and
Ca²⁺/CaMKII; phosphorylation state tracks tracer-transfer coupling **almost linearly**;
coupling changes over **milliseconds to days.**

### 6.2 Coupling coefficients

Definition: C = V₂/V₁, equivalently R₂/(R₂ + R_j).

⚠️ **Neither review read prints a single numeric coupling coefficient or junctional
conductance.** Stated loudly: the reviews define the quantity and never give a value.

The numbers had to come from a primary — cerebellar Golgi cell network, mouse (Vervaeke et
al., *Neuron* 2010, PMC2954316):

- **mean coupling coefficient across all 174 pairs: 8.2% ± 0.4%** (threshold for "coupled" CC > 1%); individual pairs ran ~12–28%
- **asymmetric within the same pair** — 28.2% one way vs 15.4% the other
- CC falls off **exponentially with somatic distance, space constant ~70 µm**
- **~10.5 ± 0.6 coupled neighbours per Golgi cell** — ⚠️ possibly an underestimate, since some dendrites were truncated in slices
- Cx36-knockout mice showed **no** coupling; wild-type littermates showed 83% pair connection probability

> The defensible general statement: **CNS interneuron electrical coupling coefficients are
> of order 1–30% with a population mean near 8%, distance-dependent and often asymmetric.
> A single "coupling coefficient" per cell type is a fiction.**

### 6.3 Filtering, delay, rectification

- **Low-pass**, set by the **postsynaptic** RC circuit — and the resulting **phase lag *is* the "synaptic delay" of an electrical synapse.**
- **No measurable delay**, in contrast to the 1–2 ms historically used to identify chemical transmission. The best verified comparison: in the Mauthner cell, glycinergic **chemical** inhibition follows the **electrical** component by **~0.5 ms**, same cell, same input. ⚠️ The often-quoted "chemical synaptic delay 0.5–1 ms" is consistent but not independently verified here.
- **Sign-conserving and bidirectional**, but transmission is more efficient from the **lower**-input-resistance cell to the **higher**-input-resistance one; symmetric communication requires similar input resistances.
- ⚠️ **Rectification is mainly an invertebrate/teleost and heterotypic phenomenon** — Curti & O'Brien describe mammalian CNS contacts as **non-rectifying**, while Faber & Pereda detail steep rectification at crayfish giant fibre synapses. **The two reviews are consistent, but a reader of only one would get the wrong impression.**
- ⚠️ **Band-pass, not just low-pass:** coupling between mesencephalic trigeminal (MesV) neurons **peaks near 80 Hz** (50–100 Hz range), from resonance due to A-type K⁺ and persistent Na⁺ currents; 4-AP makes the response resemble a plain low-pass filter. **A real exception to "gap junctions are low-pass."**

### 6.4 The synchrony inversion

> **Coupling potentials after spikes are often *hyperpolarizing***, because the spike
> afterhyperpolarization is slower than the spike and therefore survives low-pass filtering
> better. In cerebellar Golgi cells the ~0.4 ms action potential is strongly filtered so the
> slow (~100 ms) afterhyperpolarization propagates preferentially — **making the coupling
> effectively inhibitory, and *desynchronizing* the population.**

⚠️ **And note the direct conflict in titles on the same brain region:** Vervaeke et al.
2010, *"Rapid **desynchronization** of an electrically coupled interneuron network"*
(cerebellar Golgi cells) vs Hoehne, McFadden & DiGregorio, *eLife* 2020, *"Feed-forward
recruitment of electrical synapses **enhances synchronous spiking** in the mouse cerebellar
cortex."* **Whether electrical coupling synchronizes or desynchronizes depends on cell
type, afterpotential shape and input statistics. Do not state a general answer.**

### 6.5 Ephaptic / field-effect transmission

Mauthner cell: the antidromic **extracellular** spike reaches ~−40 mV and the intracellular
spike ~+50 mV, giving a transmembrane height near **+90 mV**. The extrinsic hyperpolarizing
potential can reach **~20 mV**, with a single interneuron contributing **~0.4 mV per
spike** — so roughly **50 synchronously discharging interneurons** are needed. ⚠️ (Faber &
Pereda give these figures **without a citation** — flagged.) In cerebellum, very weak fields
from **one** basket cell spike reduce the firing rate of an active Purkinje cell.

---

## 7. Neuromodulation

### 7.1 Source nuclei — the counts that are verified, and the one that is not

Rat (Colangelo et al., *PLoS Comput Biol* 2026, PMC13345462):

| System | Count |
|---|---|
| **Acetylcholine**, nucleus basalis of Meynert | **7,312** cholinergic neurons |
| **Dopamine**, VTA | **2,651** cells |
| **Serotonin**, dorsal raphe | **11,500** serotonergic cell bodies, of which ~12% project to S1 |
| **Noradrenaline**, locus coeruleus | ⚠️ **not reported.** The commonly quoted ~1,500 LC neurons per side in rat and ~50,000 in human are **recollection only** |

A second, independent source: **~1,000,000 dopamine neurons in humans, ~200,000 in
monkeys, ~20,000 in rats** (Schultz, *Dialogues Clin Neurosci* 2016, PMC4826767, full
text). ⚠️ **Do not merge these with Colangelo's figure** — Schultz's ~20,000 is the whole
rat midbrain DA population; Colangelo's 2,651 is a VTA subpopulation estimate.

⚠️ **No verified SNc count**, and the standard claim that SNc projects to dorsal striatum
while VTA projects to ventral striatum/PFC is **recollection only** — no source read states
the projection anatomy.

### 7.2 Projection density — and a laminar asymmetry worth keeping

Rat P14 hindlimb S1, axon length (µm) and varicosities per 1000 µm³, by layer:

| Layer | ChAT len | TH len | 5-HT len |
|---|---|---|---|
| 1 | 7.30 ± 1.29 | 5.36 ± 1.08 | **0.74 ± 0.17** |
| 3 | 9.27 ± 2.55 | 3.57 ± 0.70 | 0.20 ± 0.04 |
| 5 | 9.55 ± 2.72 | 3.38 ± 0.56 | **0.10 ± 0.04** |
| 6 | 10.63 ± 2.40 | 3.20 ± 0.29 | 0.13 ± 0.04 |

**Order of density: cholinergic > catecholaminergic > serotonergic.** And the pattern:
**5-HT axon length in layer 1 is ~6× that in layer 5, whereas ChAT is nearly uniform across
layers. 5-HT innervation is strongly superficial-biased; ACh is not.**

⚠️ **TH labelling includes noradrenergic fibres, so the "TH" rows are not pure dopamine** —
the source states this.

### 7.3 Volume vs wired transmission

Modelled "sphere of influence" R_max: **ACh 5 µm, DA 2 µm, 5-HT 3 µm**, with peak
concentration scaled from 1 at the release site to 0.1 at R_max; volume transmission
described as taking **hundreds of milliseconds.**

⚠️ **Every number here is a model parameter with a literature justification, not a
measurement** — and the "DA radius = 2 µm" figure is derived from **striatal** hotspot
sizes, not measured in cortex. ⚠️ The paper also describes the concentration falloff as
**both "inverse" and "linear"** with distance in different places — an internal
inconsistency, recorded as found. **No absolute concentrations (nM/µM) are given anywhere.**

**A recent complication to the "dopamine is pure volume transmission" picture:**
*"Synapse-like specializations at dopamine release sites orchestrate efficient and precise
neuromodulatory signaling"* (⚠️ Bulumulla et al., *Sci Adv* 2026, PMC13632744 — record
only). **The title alone is the claim: dopamine transmission may be more "wired" than the
volume picture allows.**

### 7.4 Network-level effects — simulation, and an honest gap

Verified **as simulation results** in a biophysical rat-neocortex microcircuit:
**ACh suppresses slow oscillations and promotes desynchronization; DA and 5-HT
desynchronize by inhibiting delta; 5-HT additionally induces theta.**

⚠️ **The standard functional vocabulary is entirely unverified here** — that ACh increases
signal-to-noise and mediates attention, that noradrenaline/LC sets gain and arousal (the
Aston-Jones & Cohen adaptive-gain account), that serotonin sets patience/time horizon, and
that dopamine sets learning rate or exploration. A Europe PMC search for a review covering
all four systems with source nuclei, volume transmission and network gain **found none.**
**These are the claims most often imported into ML analogies, and they are the least
sourced.**

### 7.5 Dopamine as reward prediction error — and how to state the dispute honestly

⚠️ **The foundational citation — Schultz, Dayan & Montague, "A neural substrate of
prediction and reward," *Science* 1997;275(5306):1593–1599 — is not open access and was
not read.** Only the bibliographic record is confirmed.

**Two things usually dropped from the canonical story**, both from Schultz's own 2016
review (PMC4826767, full text):

- **Schultz's own RPE signal has two components** — the first an **unselective salience
  response that fires for punishers too.**
- **The arithmetic is subtractive, not divisive.**

**The complications, stated at their actual strength:**

- ⚠️ **Hamid et al. 2021 is *not* a refutation of dopamine-RPE** — the authors explicitly write their findings *"do not directly refute"* it.
- ⚠️ **Howe et al. 2013 reports no nM concentrations and no trial durations in seconds** — so *"ramps of X nM over Y s"* **cannot be sourced to it.**
- **Berke's sharpest point, usually skipped:** **value and RPE are mathematically confusable, so baseline subtraction can manufacture an apparent RPE.**

---

## 8. Numbers

### 8.1 The synaptic cleft is wider than the textbook number

⚠️ **"The synaptic cleft is ~20 nm" is a dehydrated-tissue number.** In vitrified hydrated
tissue: cleft **23.8 ± 2.0 nm**, vesicles **37.7 ± 5.2 nm**; the same authors'
plastic-embedded controls gave **19.3–19.6 nm**. **A 2021 modelling paper still repeats
"~30 nm" — the correction has not propagated.**

### 8.2 Energy — the expensive thing is receiving, not sending

The revised cortical signalling budget (Howarth, Gleeson & Attwell 2012, PMC3390818) —
which **exists because Attwell & Laughlin 2001's spike cost was an overestimate**:

| Process | Share |
|---|---|
| **Postsynaptic glutamate receptors** | **50%** |
| Action potentials | 21% |
| Resting potentials | 20% |
| Presynaptic release | 5% |
| Recycling | 4% |

> **This undercuts the usual energy argument for sparse *spiking*.** The dominant cost is
> postsynaptic.

⚠️ **"ATP per action potential" is unsettled by four to five orders of magnitude**
(~3,000 to 10¹⁰ across two secondary readings of the **same** primary paper), and neither
states whether the denominator is per synapse or per neuron. **Never quote it without the
denominator.**

### 8.3 What this dossier does *not* verify

Stated explicitly so nothing is invented: **reversal potentials** (E_Na, E_K, E_Cl,
E_AMPA, E_GABA_A — zero verified values); the **Mg²⁺ block IC50**; **transmitter molecules
per vesicle**; **NMJ quantal content**; most **single-channel conductances and open
times** (the glycine-receptor values are the exception); **nAChR kinetics**; **input
resistance in MΩ**; the **length constant λ**; **NMDA-spike amplitude and duration**;
**Johnson & Ascher 1987** (not retrieved); **Poirazi & Mel 2001 *Neuron*** (not found);
and the **Beniaguev et al. 2021 temporal filter size**.

---

## Sources

Research compiled **2026-11-13** from primary literature via NCBI E-utilities, Europe PMC
REST and ar5iv/arXiv. ⚠️ **Access failures that shape this file:** NCBI Bookshelf is behind
reCAPTCHA, so **Purves was never consulted and no Purves citation appears**; Kandel, Koch,
Dayan & Abbott and Bear were unobtainable; PMC gates article HTML behind a SHA-256
proof-of-work; nature.com, science.org, royalsocietypublishing.org, sciencedirect.com and
pnas.org returned 403.

**Read in full text (or full XML chunks):** Südhof, *Neuron* 2013 (PMC3866025); Denker &
Rizzoli 2010 (PMC3059705); Gallimore et al., *Sci Adv* 2025 (PMC12118552); Wang & Dudko,
*eLife* 2021 (PMC8776255); Durst et al., *Nat Commun* 2022 (PMC9576736); Tsodyks & Markram,
*PNAS* 1997 (PMC19580); Ramaswamy & Markram 2015 (PMC4481152); Hansen et al., *Pharmacol
Rev* 2021 (PMC8626789, selected chunks incl. all of Table 1); Concise Guide to PHARMACOLOGY
2023/24 Ion channels (PMC11339754) and 2025/26 GPCRs (PMC13242166, partial); Ghit et al.
2021 (PMC8380214); Yelshanskaya et al., *Nature* 2022 (PMC9068512); Nabavi et al., *PNAS*
2013 (PMC3593861); Babiec et al., *J Neurosci* 2014 (PMC3983804); de Kock & Feldmeyer 2023
(PMC10508294); Watanabe & Fukuda 2015 (PMC4585146); Ben-Ari et al. 2012 (PMC3428604);
Ledergerber & Larkum 2012 (PMC3302831); Augusto & Gambino 2019 (PMC6777373); Aizenbud,
Yoeli et al., *PNAS* 2026 (PMC13367794); Fişek & Häusser 2020 (PMC7903140); Curti &
O'Brien 2016 (PMC4896238); Faber & Pereda 2018 (PMC6276723); Vervaeke et al., *Neuron* 2010
(PMC2954316); Colangelo et al. 2026 (PMC13345462); Schultz 2016 (PMC4826767).

**Not read, flagged inline:** Fatt & Katz 1952; both del Castillo & Katz 1954 papers;
Schultz, Dayan & Montague 1997; Beniaguev, Segev & London 2021; Gidon et al. 2020; Poirazi,
Brannon & Mel 2003; Holt & Koch 1997 (abstract only); Schneggenburger & Neher 2000 and
Bollmann et al. 2000 (abstracts only); Abbott et al. 1997; Farrant & Nusser 2005; Rivera et
al. 1999; Rall's companion 1969 paper on electrotonic length; Bregestovski & Bernard 2012
and Dzhala et al. 2012 (so the GABA-polarity challenge is known **only through its
opponents' summary**).

---

## Related

- [[neural-networks-biology]] — the parent skill.
- [[neural-networks-ml]] — where the scalar-weight and single-summation-node abstractions this file complicates actually live.
- [[information-theory]] — for the coding consequences of unreliable, probabilistic transmission.
