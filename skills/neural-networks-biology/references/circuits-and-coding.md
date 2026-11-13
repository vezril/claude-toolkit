# Circuits, networks and coding

The cortical microcircuit and its interneuron classes, the cortical-column dispute, E/I
balance and inhibitory stabilization, the hippocampal circuit, neural coding, the
CNN–ventral-stream correspondence *and* its mismatches, oscillations, connectomics, network
topology, energy, and neuromorphic hardware.

⚠️ marks a claim that is unverified, disputed, or folklore. Where two sources disagree, both
are recorded and **not** reconciled.

---

## 1. The cortical microcircuit

### 1.1 Scale, and the framing that replaced "layer = cell type"

Primary source read in full: **Harris & Shepherd, "The neocortical circuit: themes and
variations," *Nat Neurosci* 18(2):170–181 (2015), PMC4889215.**

Their framing: cortical areas are **serially homologous** — *"Different cortical areas are
similar in the same way that hands are similar to feet, or different bones are similar within
the vertebral column."* Differences between areas are *"typically quantitative."* And they argue
explicitly for a shift of emphasis:

> *"**lamination is not the sole or even primary organizing principle of neocortex.** Instead,
> what different regions share is their **hodology**: the patterns of connection between
> different genetically defined cell classes."* — adding that these rules *"are of course not
> immutable laws."*

**Scale, for 1 mm³ of rodent neocortex spanning the layers:**

| | |
|---|---|
| Neurons | ~10⁵ |
| Axon | **~4 km** |
| Dendrite | ~0.4 km |
| Potential connections | ~10¹⁰ |
| **Actual synapses** | **~10⁹ — i.e. ~10% of potential connections are realised** |
| Fraction of local synapses that are **extrinsic** | *">50% in one estimate"* |
| Synapses per connected pair | *"e.g. 4–5"* |
| Excitatory–excitatory connectivity (paired recordings) | *"low in general, rising to **10–20% or higher** only for specific pre- and postsynaptic cells, such as functionally co-tuned neurons in V1"* |

**Excitatory cell classes by *axonal projection*, not by layer** — the modern replacement for the
old scheme. Excitatory cells are *"~80% or more of cortical neurons"*:

| Class | Where | Projects to |
|---|---|---|
| **IT** — intratelencephalic | layers 2–6 | Neocortex, striatum, corticoid structures. **The only ECs that project to contralateral cortex.** L4 ITs are a hodologically distinct subclass |
| **PT** — pyramidal tract / subcerebral | L5B (*"L5B is traditionally defined as the layer containing these neurons"* — a convention, not a finding) | Brainstem, spinal cord, midbrain; also ipsilateral cortex, striatum, thalamus |
| **CT** — corticothalamic | L6 | Primarily ipsilateral thalamus. ⚠️ Harris & Shepherd state their role in the cortical circuit is *"still largely uncertain"* |

⚠️ **The nuance they insist on: laminar distributions overlap.** L5B has intermingled IT and PT
neurons; L6 has intermingled IT and CT. **So "layer 5 cell" is not a cell type.**

**And the strongest published warning against the textbook cartoon**, verbatim:

> The sequential organisation *"does not constrain the flow of information to a single linear,
> feedforward pathway: because all EC classes receive external inputs, there are **multiple entry
> points** into this circuit; and, because ECs are usually projection neurons, there are also
> **multiple exit points** — **a key principle of cortical circuit organization often lost in
> simplified schematics**."*

**Thalamocortical input is not a fixed constant either.** **Core**-type relay neurons project
topographically to primary sensory cortex, chiefly L4 and also *"(with areal and species
variability)"* to L3 and L5B/6. **Matrix**-type neurons project to L1 but **avoid L4** of primary
sensory cortex — and *"the information conveyed by matrix-type afferents is poorly understood."*

### 1.2 The three interneuron families

Read in full: **Tremblay, Lee & Rudy, *Neuron* 91(2):260–292 (2016), PMC4980915**; and **Rudy,
Fishell, Lee & Hjerling-Leffler, *Dev Neurobiol* 71(1):45–61 (2011), PMC3556905.**

> *"neurons expressing three markers — the Ca²⁺-binding protein **parvalbumin (PV)**, the
> neuropeptide **somatostatin (SST)**, and the ionotropic serotonin receptor **5HT3aR** — account
> for **nearly 100%** of neocortical interneurons."*

| Group | Share | Contains |
|---|---|---|
| **PV** | **~40%** | Fast-spiking **basket** cells and **chandelier** cells (basket cells *"numerically dominant"*) |
| **SST** | **~30%** | **Martinotti** cells (mainly L2/3 and L5/6) and a set of neurons specifically targeting L4 |
| **5HT3aR** | **~30%** | *"thought to be more heterogeneous."* **VIP** is in ~40% of these (so **VIP ≈ 12% of all interneurons**); **non-VIP 5HT3aR ≈ 60% of these and ~90% of all L1 interneurons**, including **neurogliaform cells** and **CCK basket cells** |

⚠️ **Scope limit, stated by the authors: these fractions are established for *mouse primary
somatosensory cortex*. Do not quote them as human or primate numbers.**

**What each subtype targets, and the functional division of labour:**

- **Perisomatic + proximal dendrites:** PV fast-spiking basket cells and CCK basket cells.
- **Axon initial segment:** PV **chandelier / axo-axonic** cells — *"All postsynaptic boutons of chandelier INs have been reported to target **exclusively** the axon initial segment."*
- **Dendrites:** *"The two major IN subtypes targeting dendrites are **Sst Martinotti cells and non-Vip 5HT3aR neurogliaform cells**."*
- The division, verbatim: *"Due to their perisomatic bias, **PV synaptic contacts are well suited to control the timing of individual sodium spikes** while **dendritic-biased Sst neuron synapses gate dendritic integration, calcium spikes and burst generation**."*

⚠️ **Two complications to the clean picture:** GABAergic synapses at the AIS have a
**depolarized** reversal potential relative to somatic ones, because intracellular chloride is
higher at the AIS — **so axo-axonic "inhibition" may not be purely inhibitory.** And *"a
significant fraction of chandelier cells … express PV protein weakly or perhaps not at all"* — so
**"PV cell" ≠ "basket + chandelier" cleanly.**

### 1.3 Disinhibition — with the authors' own operational caution

Their definition, and it matters: *"disinhibition is considered as the principle by which the main
function of an interneuron type in a given context is to inhibit another GABAergic type **more
potently than principal cells**."* And the warning: ⚠️ ***"the mere presence of an
interneuron-to-interneuron connection does not imply disinhibition."*** They explicitly say PV
basket cells, despite connecting to other interneurons, are **not** plausibly a disinhibitory type
because their connectivity to principal cells is so strong.

**The canonical motif:** *"**VIP INs show high target selectivity for Sst INs** which results in
disinhibition of the dendrites of pyramidal cells… It therefore seems that the VIP to Sst
disinhibitory connection is a **general principle in the superficial layers** of neocortex."*

**Drivers of VIP cells:** cortico-cortical **feedback** from higher-order cortex (motor
cortex → barrel cortex VIP is the strongest such input of any cell type); basal-forebrain
cholinergic input during locomotion (**all** 5HT3aR cells are strongly depolarised by nicotinic
agonists); and reinforcement/aversive signals.

**VIP→SST is not the only disinhibitory circuit:** L4 SST cells preferentially target local PV
cells and so disinhibit L4 principal cells; and an L1 interneuron, nicotinically activated by a
conditioning foot shock, inhibits L2/3 PV cells — with *"pharmacological or optogenetic block of
the disinhibition **abolished fear learning**."*

### 1.4 ⚠️ The interneuron taxonomy is a mouse taxonomy

The authors' own caveat: *"it is not clear to what extent the markers define **the same IN
subtypes in these species** as they do in rodents."* They cite reported electrophysiological
differences between rat and monkey for the same nominal types. And **"horsetail" and
double-bouquet cells are primate features — the double-bouquet cell has no clear rodent
homologue.**

### 1.5 The canonical microcircuit — the claim, then the caveats

⚠️ **None of the three Douglas & Martin papers (1989, 1991, 2004) was read** — bibliographic
records only, plus Martin restating his own position in da Costa & Martin 2010 (read in full).

**The claim, as the proponents state it:** *"We suggest that in the concept of a 'canonical
circuit' we may find the means to reconcile the structure of neocortex with its functional
architecture. The canonical microcircuit respects the known connectivity of the neocortex, and it
is **flexible enough to change transiently the architecture of its network** in order to perform
the required computations."*

> **i.e. the canonical-microcircuit claim is *not* "every cortical area has the same wiring
> diagram." It is the weaker claim that a single recurrent motif — thalamic drive amplified by
> strong recurrent excitation, held in check by inhibition — recurs, and that its *effective*
> architecture is reconfigurable.**

**How canonical is it really?** (a) The organisation is serially homologous — *"variations on a
theme"* — and differences are quantitative, but those quantitative differences *"can allow
serially homologous structures to **serve very different functions**."* (b) ⚠️ Harris & Shepherd's
own stated scope is *"primarily … data on excitatory neurons of **rodent** sensory and motor
cortex"* — **the modern canonical circuit is largely a rodent circuit.** (c) Thalamic laminar
targeting varies with area and species. (d) Each top-level class *"contains distinct subclasses,
for which the correspondence between the different classification criteria is **not yet clear**."*
(e) And most pointedly, from Martin's own later paper: ***"no one has 'seen' the anatomy of a
column … in fact much of the anatomical data seems to challenge it."*** ⚠️ (f) Rodent motor cortex
lacks a cytoarchitectonic L4 — a direct counterexample to a six-layer template — but **no primary
on rodent M1 agranularity was opened.**

> **The "canonical microcircuit" is a real and useful abstraction about recurrence and
> amplification. It is not the claim that all cortex shares one laminar wiring diagram, and its
> own principal author says the anatomical column that usually accompanies it in textbooks has
> never been seen.**

---

## 2. The cortical column — an unresolved dispute

### 2.1 What Mountcastle actually claimed, with the uncertainty intact

⚠️ Mountcastle 1957 (*J Neurophysiol* 20(4):408–434) and 1997 (*Brain* 120:701–722) were **not
read**; the content below is quoted via da Costa & Martin 2010, read in full.

The 1957 observation: although successive cells in a penetration came from the same receptive-field
location, light touch and light skin pressure were represented independently within *"narrow
vertical columns or cylinders extending from layer II through layer VI."*

⚠️ **The dimensions were guesses.** *"Mountcastle (1957) thought that his cortical 'minicolumns'
had dimensions 30–50 μ in diameter… The dimensions of the functional columns in the cat **were
guessed at between one cell and 0.5 mm in diameter, because Mountcastle and his colleagues had
great difficulty in finding their electrode tracks in histological sections**."* **Note the honesty
of the uncertainty at the origin of the concept.**

**Reception:** Mountcastle later reminisced that *"the report was met with disbelief by many
neuroanatomists."* **Priority:** he credited **Lorente de Nó (1949)** — though da Costa & Martin
judge that *"Lorente de Nó's data were far from convincing"*, and note the tissue he studied was
**misidentified** (he thought mouse "acoustic" cortex; it was somatosensory).

### 2.2 Hubel & Wiesel showed "column" is a misnomer — on their own data

⚠️ None of the Hubel & Wiesel primaries were read; quotations are via da Costa & Martin 2010.

- **ODC discovery was accidental**, via artificial divergent squint in kittens. In squint kittens *"virtually all cells were monocular"*; in normal controls *"**85% of the cells were binocular**."*
- Hubel & Wiesel 1998, quoted: *"The grouping of the cells into separate eye domains was almost as surprising as the fact they were monocular, for **until then we had only been vaguely aware** of the division of the cortex into left-eye and right-eye domains."* At first they called it *"a 'system of parcellation by ocular dominance' rather than ocular dominance columns."*
- ⚠️ **ODC and orientation preference are uncorrelated — so "the cortical column" already means two incompatible things between S1 and V1:** *"every neuron in the visual cortex was a member of **both** columnar systems, whereas neurons in the somatosensory cortex responded to light **or** deep touch, but not both."*
- **Dimensions (cat):** ODC ~0.5 mm; orientation column ~0.1 mm.
- ⚠️ **The awkward 1962 observation:** even *within* an iso-orientation column, successive units showed *"apparently random staggering of receptive field positions"* and could change eye dominance, with *"large variations in the size of the receptive field even in radial penetrations."*
- **The misnomer, verbatim:** *"What Hubel and Wiesel could show in the visual cortex, but Mountcastle for the somatosensory cortex could not, was that **their description of 'column' was a misnomer. What the anatomical and physiological methods showed was that the columns were not Greek pillars, but swirling slabs. But by the time their revisionist discovery hit the presses, the term 'column' was indelible**."*
- Even the famous squirrel-monkey penetration was puzzling: striate cortex *"seemed to contain regions where orientation columns were orderly, and regions where they were not"*, with **"no hint of such differences structurally."**

### 2.3 Horton & Adams: "a structure without a function"

⚠️ **Complete abstract read; full text not open access.** Horton & Adams, *Phil Trans R Soc B*
360(1456):837–862 (29 April 2005), PMC1569491. ⚠️ **Their own registered keywords include
"spandrel"** — the Gould & Lewontin sense: an architectural by-product, not an adaptation.

Written for the 50th anniversary of Mountcastle's discovery, they *"come to the disappointing
realization that the column may have no function."* Their argument:

1. **Concept creep.** Originally a discrete structure containing cells responsive to a single modality. *"Subsequently, examples of columns have been uncovered in numerous cortical areas, expanding the original concept to embrace a variety of different structures and principles. **A 'column' now refers to cells in any vertical cluster that share the same tuning for any given receptive field attribute**."* ⇒ **The term has been defined into near-vacuity.**
2. **Species inconsistency:** *"**Unaccountably**, ocular dominance columns are present in some species, but not others."*
3. **The decisive test failed:** *"In principle, it should be possible to determine their function by searching for species differences in visual performance that correlate with their presence or absence. Unfortunately, this approach has been to no avail; **no visual faculty has emerged that appears to require ocular dominance columns**."*
4. **Within-species and within-individual variability:** ODC expression *"can be highly variable among members of the same species, or even in **different portions of the visual cortex in the same individual**. These observations deal a **fatal blow** to the idea that ocular dominance columns serve a purpose."*
5. **Verdict:** *"Although the column is an attractive concept, **it has failed as a unifying principle for understanding cortical function**. Unravelling the organization of the cerebral cortex will require a painstaking description of the circuits, projections and response properties peculiar to cells in each of its various areas."*

⚠️ **The commonly repeated species list (mouse/rat "salt-and-pepper" V1, grey squirrel lacking
orientation columns) cannot be verified from this abstract** — it asserts species inconsistency for
**ocular dominance** columns and names no species. **Treat the species list as unchecked.**

**And da Costa & Martin 2010 (read in full) — note which species the robust finding covers:**
*"All we know is that when we record through the cortex of **primates, ungulates, and carnivores**
in a trajectory perpendicular to its surface there is a remarkable constancy in the receptive field
properties of the neurons regarding one set of stimulus features. **There is no obvious
morphological analog** for this functional architecture, in fact much of the anatomical data seems
to challenge it."* **Rodents are conspicuously absent from that list.**

Their rhetorical framing: *"**Columns are fatally attractive**."* And on the industrial
consequences: *"vast resources in human and machine time … are being devoted to defining every
element and every connection in the cortical column so that a facsimile can be recreated 'in
silico'."*

**The question in their title is the point.** There are multiple incompatible referents:
Mountcastle's 30–50 µm minicolumn, his functional modality column (up to 0.5 mm), the ~0.5 mm ODC
slab, the ~0.1 mm iso-orientation domain, the barrel, the CO blob, the V2 stripe. **"The cortical
column" is not one object.**

### 2.4 State of the dispute

**For:** radial constancy of tuning in primate/carnivore/ungulate sensory cortex is a robust,
repeatedly replicated fact; radial fascicles are a real histological observation; periodic
anatomical projections (CO blobs, V2 stripes, ODC slabs) are real.

**Against:** no single structural referent; the term has broadened to near-vacuity; ODCs present in
some species and absent in others with no identified behavioural correlate; expression varies
between conspecifics and within one individual's V1; no demonstrated function; **the anatomy of a
column has never been seen.**

> ⚠️ **Neither critical paper claims radial organisation is absent. Both claim "the column" is not a
> functional unit of computation. That distinction is routinely lost in secondary sources. Do not
> write "columns don't exist" — write "no demonstrated function, and no single referent."** The
> dispute is **open** as of the sources read.

---

## 3. E/I balance and inhibitory stabilization

### 3.1 ⚠️ "80/20" is not one number

**Monkey** (Hendry, Schwark, Jones & Yan, *J Neurosci* 7(5):1503–19, 1987; abstract read; GABA
immunoreactivity counted in 50-µm columns through the full thickness, in 10 areas, with the
protocol **explicitly optimised to maximise stained cells**):

- In **8 of 10 areas**: 34–43 GABA+ cells per column = **25% of total neurons**
- **Area 17 (V1) differed:** 50% more GABA+ cells but **more than twice** the total neuron count, *"so that the GABA cells made up **less than 20%**"*
- ⚠️ **Area 3b differed inconsistently *between animals*:** 19–22% in three monkeys, **24–26% in two others** — the paper itself reports between-animal disagreement
- **Within** an area, GABA+ cells per column varied *"as much as **30%**"*
- Laminar distribution is strongly non-uniform — every area has large proportions in layer II

**Rodent:** interneurons *"represent a minority of all cortical neurons (**10–15% in rodents**)"*
(Tremblay et al. 2016). Harris & Shepherd: excitatory cells are *"~80% **or more**."*

> **Write it as: "roughly 80/20, but the GABAergic fraction is ~15% in rodent cortex and ~20–25% in
> monkey cortex, varies by area and layer, and varies between individual animals."** ⚠️ **Method
> dependence is the likely driver** — GABA immunoreactivity vs GAD67 mRNA vs stereology count very
> different things.

⚠️ **And flag a frequent conflation:** the Beaulieu & Colonnier line of evidence often cited for
~84/16 is about **synapse type** (round-asymmetric vs flat-symmetric), **not cell counts** — a
different quantity. Neither of those papers was read.

**One verified structural asymmetry that matters more than the ratio:** **inhibition is dense and
blanket; excitation is sparse and local.** Pyramid→pyramid connection probability falls
**0.09 → 0.01** over 25–200 µm, while pyramid↔fast-spiking-interneuron probability is **0.5–0.75
and nearly distance-independent.**

### 3.2 Inhibitory stabilization — and a paradoxical response is not a unique signature

⚠️ van Vreeswijk & Sompolinsky 1996 was **not readable** (Science 403); the balanced-state claim
(strong excitation nearly cancelled by strong inhibition, settling into irregular asynchronous
firing with near-Poisson statistics and fast response) is **recollection as to the paper's wording
and its 1/√K scaling argument.**

**The V1 evidence** — Ozeki, Finn, Schaffer, Miller & Ferster, *Neuron* 62(4):578–592 (2009),
PMC2691725, full text read. Intracellular current-clamp in anesthetized adult **cat** V1; 67 cells;
conductances in 34 surround-suppressed cells.

**The key result: a surround grating at the preferred orientation reduced *both* excitatory *and*
inhibitory conductances — by ~51% and ~38%.** Membrane-potential suppression tracked the **drop in
excitation (r = 0.80)**, not any rise in inhibition (**r = 0.08**). Geniculate suppression was
weaker (~20%) and less orientation-tuned, so LGN input cannot account for it.

> **Classical lateral inhibition predicts *more* inhibition during surround suppression. The data
> show *less*. Surround suppression is a *withdrawal of recurrent excitation*, not added
> inhibition** — which only makes sense if recurrent excitation is the dominant drive. ⚠️ Their own
> limit: the data do not establish whether the network is in the same regime **at rest**.

**The optogenetic test** — Sanzeni et al., *eLife* 9:e54875 (2020), PMC7324160, full text read.
Driving inhibitory cells in mouse V1: *"**most inhibitory cells paradoxically decrease their firing
rates**, with 5 (9%) increasing."* The effect is preserved across unit-isolation thresholds,
waveform classification, pharmacological classification and SNR.

⚠️ **Two findings that cut against over-reading any single experiment:**

1. ***"Average paradoxical effects result only with transgenic, not viral, opsin expression in parvalbumin-positive neurons."*** PV-Chronos recordings with otherwise identical procedures showed **no** average paradoxical effect. ⇒ **Any single optogenetic negative result may be an expression artefact. That cuts both ways.**
2. **A paradoxical response is not a unique ISN signature.** They record the disagreement themselves — several studies found **non-paradoxical** effects in mouse V1, A1 and S1; and one study observing paradoxical changes in A1 *"found that those paradoxical effects were **not produced via the ISN mechanism**, but instead mediated by a circuit where L4 inhibitory cells suppressed L2/3 inhibitory cells."* ⇒ **A two-population inhibitory circuit can mimic it.**

Their conclusion is scoped: *"one piece of evidence that an ISN model is a good description of **the
upper layers** of primary visual cortex."*

⚠️ **A real tension to record:** the recurrent-amplification story requires recurrence to dominate,
but Harris & Shepherd report *">50% in one estimate"* of local synapses come from **extrinsic**
axons. **The recurrent-dominance and extrinsic-dominance estimates are in tension.** And ⚠️ the
classic "thalamic synapses are only a few percent of excitatory synapses on an L4 spiny cell" figure
was **not verified — do not state a percentage.**

---

## 4. The hippocampal circuit

### 4.1 The loop — and the neuron numbers in every model are legacy

The trisynaptic loop: **EC layer II → dentate granule cells** (perforant path) **→ CA3** (mossy
fibres) **→ CA1** (Schaffer collaterals) **→ back to EC.** In parallel, **EC layer III → CA1
directly** (temporoammonic path) — **which makes "trisynaptic" an abbreviation rather than a
description.**

⚠️ **The most important correction here.** Arellano & Rakic, "Updated Neuronal Numbers of the Rat
Hippocampal Formation: Redesigning the Hippocampal Model," *Hippocampus* 36(1):e70070, online
**18 January 2026**, PMC12812505 (full text read). A systematic review: 166 studies found, 87–89
retained as using reliable stereology, yielding **264 stereological estimates.** ⚠️ **~80% of the
data are from males.**

**Male rat:**

| Region | Neurons |
|---|---|
| Dentate granule cell layer | 1,000,000 |
| Dentate hilus | 50,000 |
| **CA3** | **210,000** |
| CA2 | ~30,000 |
| **CA1** | **350,000** |
| Subiculum | ~300,000 |
| **EC layer II** | **108,000** |
| EC layer III | 270,000 |
| EC layer V/VI | 340,000 |

**Their headline finding:** *"Most of those estimates are **significantly different from those
traditionally used in hippocampal models** (e.g., **~2-fold difference in EC layer II**), revealing
an updated architecture."*

The legacy source is **Amaral, Ishizuka & Claiborne, *Prog Brain Res* 83:1–11 (1990)** ⚠️ (not open
access, not read), which Arellano & Rakic say was *"based on the limited studies available at the
time"* while *"serving as a reference for numerous models up to the present"* — they list a dozen
such models by name, from Treves & Rolls 1992 to papers from 2023–2024. Their illustration of why it
matters: *"it is hard to compare a model with 1 million GCs, 160,000 CA3/CA2 neurons and 250,000 CA1
pyramidal cells with another with the same number of GCs but **double the number of CA3 neurons**
(330,000) and almost **70% more CA1 neurons** (420,000)."*

> **Any figure you have seen for "CA3 = 250,000 rat neurons" or "EC layer II = 200,000" is from the
> 1990 literature and is superseded. CA3 is ~210,000; EC II is ~108,000 — about *half* the
> traditional figure.** ⚠️ **And these are rat numbers. Do not transfer to mouse or human.**

⚠️ **The connectivity integers are *not* verified.** The classic mossy-fibre figures — ~14–15 large
boutons per granule cell, ~50 mossy inputs per CA3 cell, ~10⁴ recurrent inputs per CA3 cell — trace
to Amaral et al. 1990, which was unreadable, and Arellano & Rakic give **neuron counts only.**
**What is safe to say: the mossy-fibre projection is sparse-and-strong (few, very large "detonator"
synapses per CA3 cell) while the CA3 recurrent collateral system is the most extensively recurrent
excitatory network known in mammalian brain. The architectural claim is safe; the integers are
not.**

Historical note: **Lorente de Nó's defining feature of CA2 is the *absence* of mossy-fibre input.**

### 4.2 ⚠️ The Hopfield 0.138N capacity is not Hopfield's, and not a fact about CA3

Hopfield 1982 reported ~0.15N from **simulations** ⚠️ (recollection — the paper was not read). **The
exact value α_c ≈ 0.138 is a statistical-mechanics result due to Amit, Gutfreund & Sompolinsky
(1985 ×2, 1987), not to Hopfield.** ⚠️ Which of the three states it to three digits, and whether the
value is 0.138 / 0.1379 / 0.14, was **not verified** — none of the three was read.

**The conditions that are always dropped when 0.138N is quoted, and must not be:** full
(all-to-all) connectivity; **symmetric weights**; random, uncorrelated, **unbiased** patterns;
Hebbian outer-product learning; the **zero-temperature limit**; and "capacity" defined as the point
of **catastrophic breakdown** rather than error-free recall (error-free recall scales as N/(2 ln N)
⚠️ — unverified here). ⚠️ **Sparse patterns change the answer entirely and upward.**

> **0.138N is not a fact about CA3. It is a fact about a specific, biologically false model.**

### 4.3 How established is the attractor story?

**Well established:** the trisynaptic architecture; the **DG expansion** (1,000,000 granule cells
from ~108,000 EC layer II cells ≈ **10:1**); the sparse strong mossy-fibre projection; the extensive
CA3 recurrent system; and place cells and grid cells, *"among the most replicated findings in
systems neuroscience."*

**Inferred, not demonstrated:**

- **That CA3 implements an autoassociative attractor memory in the Hopfield sense is a theoretical interpretation fitted to the anatomy. The anatomy is permissive, not probative.**
- **"Pattern separation" in DG** is measured as **decorrelation** of population activity under small input changes — a real phenomenon, but **decorrelation is not the same as the orthogonalisation a Marr/Hopfield architecture requires**, and the measured effects are **graded rather than all-or-none.**
- **"Pattern completion" in CA3** is inferred from recall-from-partial-cue behaviour and morph experiments showing abrupt transitions — but **abrupt transitions can also arise from non-attractor mechanisms** (input-driven switching, behavioural state changes).
- ⚠️ **Do not put "pattern separation" and "pattern completion" in Marr's mouth** — Marr 1971 was not read, and that standard pair is largely later usage (McNaughton & Morris 1987; Treves & Rolls; O'Reilly & McClelland 1994).

---

## 5. Neural coding

### 5.1 Rate vs temporal codes — both sides, neither primary read

⚠️ **The case for timing** rests on Thorpe, Fize & Marlot, *Nature* 1996 (**not read**): a
go/no-go animal-detection task produces a differential ERP by ~150 ms; given ~10 processing stages,
each has only ~10 ms, too short to emit and integrate many spikes — so each neuron contributes
roughly one spike and the code is **which cells fire and when.** ⚠️ **The 150 ms latency and the
stage count are unverified.**

⚠️ **The case against fine temporal coding** rests on Shadlen & Newsome, *J Neurosci* 1998 (**not
read**): cortical spike trains are too variable for millisecond-precision codes to survive
integration.

**What *is* verified, from the neurons reference:** firing rates are **lognormal over 3–4 orders of
magnitude**, most neurons are nearly silent most of the time, and **<5% of neurons exceed 20
spikes/s at any instant.** Any coding claim has to live with that distribution.

### 5.2 Sparse and efficient coding

**Olshausen & Field's contribution is usually mis-stated.** ⚠️ **Decorrelation/PCA alone does *not*
yield oriented localized filters — sparseness is what closes the gap.** And note their 1997
follow-up title **ends in a question mark.**

⚠️ **Barlow 1961 is "Possible Principles Underlying the *Transformations* of Sensory Messages"
(plural)** — the singular is a common citation error.

### 5.3 ⚠️ Quiroga's concept cells are explicitly *not* grandmother cells — per Quiroga

He published *"**Sparse but not 'grandmother-cell' coding** in the medial temporal lobe"*: *"we give
several arguments that make such an extreme interpretation unlikely."* **And the recording site is
MTL — a memory structure, not visual cortex.**

---

## 6. The CNN–ventral-stream correspondence, and the mismatches

### 6.1 What Yamins et al. 2014 actually claimed

⚠️ **Abstract and Significance read; the Results body could not be retrieved** (PMC XML carries
front matter only; pnas.org returned 403). Yamins, Hong, Cadieu, Solomon, Seibert & DiCarlo,
*PNAS* 111(23):8619–24.

**The real contribution — performance predicts predictivity:** *"within a class of biologically
plausible hierarchical neural network models, there is a **strong correlation between a model's
categorization performance and its ability to predict individual IT neural unit response
data**."* And crucially, **the model was selected by task performance, not fitted to neural
data:** *"**Although not explicitly constrained to match neural data**, this model turns out to be
highly predictive of neural responses in both the V4 and inferior temporal cortex."* Their
interpretive leap: *"these results **suggest** that a process of biological performance optimization
directly shaped neural mechanisms."* **Note "suggest."**

⚠️ ***The variance-explained numbers are unverified.*** The figures in wide circulation —
~48–50% of explainable variance in IT and ~50–52% in V4, beating V1-like, V2-like, HMAX, SIFT and
pixel controls — are **not verified here**, nor is the number of recorded sites (commonly given as
168 IT and 128 V4). **Do not quote these digits from this dossier.**

**And the headline claim must be qualified even on the paper's own terms:** the metric is explained
variance of **single-site** responses to **static, centrally-presented, isolated objects**, after
**linear regression** from model features to neural responses, normalised by a **noise ceiling.**
**Each of those four qualifiers does load-bearing work.**

### 6.2 Supervision matters — with the authors' own hedge

**Khaligh-Razavi & Kriegeskorte, "Deep supervised, but not unsupervised, models *may* explain IT
cortical representation," *PLoS Comput Biol* 10(11):e1003915.** The method is representational
similarity analysis; the finding is the **supervised/unsupervised asymmetry** — category-supervised
deep nets approach the IT geometry; unsupervised models of the same depth do not. ⚠️ **Per-model
correlation numbers and noise-ceiling values were not extracted — quote none.**

⚠️ **And the same authors later published an addendum about the noise ceiling** (Storrs,
Khaligh-Razavi & Kriegeskorte, bioRxiv 2020). **The existence of that addendum is itself the
point: the headline "model X explains Y% of IT" is extremely sensitive to how the ceiling is
computed, and the original authors revisited theirs.**

### 6.3 Brain-Score — and why you cannot quote a number from here

⚠️ **The original Brain-Score paper (Schrimpf et al., bioRxiv 10.1101/407007, posted 5 Sep 2018)
appears never to have been published in a peer-reviewed venue under that title. Cite it as a
preprint with its posting date.** The peer-reviewed companion is Schrimpf et al., *Neuron* 2020
(⚠️ paywalled, not read).

⚠️ **Brain-Score 2.0 was released 1 December 2024** (verified from brain-score.org, fetched
2026-11-13). ⚠️ **No current leaderboard number could be obtained** — the leaderboard is
client-side rendered. **If you need a Brain-Score number, fetch it with a real browser and record
the date *and the suite version*, because the suite composition changes and scores are not
comparable across versions.**

**The critics' positions** (recorded as positions, not as papers read): the score is an **average
over heterogeneous benchmarks** with different noise ceilings and stimulus counts, and the
weighting is a choice; **linear-regression readout is extremely permissive** — a high score can be
achieved by a model whose internal features bear little resemblance to cortical ones, because **the
regression does the work**; and **ranking models on a benchmark creates an optimisation target —
improving Brain-Score is not the same as improving a theory.**

### 6.4 ⚠️ Texture bias is now contested

**Geirhos, Rubisch, Michaelis, Bethge, Wichmann & Brendel, "ImageNet-trained CNNs are biased
towards texture; *increasing shape bias improves accuracy and robustness*," arXiv:1811.12231,
ICLR 2019 (oral).** ⚠️ **Note the full title — the commonly used short form drops the second
clause.** Cue-conflict images pitting texture against shape; *"ImageNet-trained CNNs are strongly
biased towards recognising textures rather than shapes"*, unlike humans. The human comparison scale
is exact: *"nine psychophysical experiments with **97 observers and 48,560 trials**."* ResNet-50
trained on Stylized-ImageNet learns shape-based representations, better matches human behaviour,
and gains **better object detection and greater distortion robustness.**

⚠️ **And a published challenge exists:** Burgert, Stoll, Rota & Demir, **"ImageNet-trained CNNs are
*not* biased towards texture: Revisiting feature reliance through controlled suppression,"
NeurIPS 2025**, pp. 67668–67689. ⚠️ **Not read — the title directly negates Geirhos et al. on
methodological grounds (cue-conflict stimuli may not isolate feature reliance). Do not present
texture bias as settled.**

### 6.5 The broad critique — Bowers et al.

**Bowers, Malhotra, Dujmović et al., "Deep problems with neural network models of human vision,"
*Behav Brain Sci* 46:e385** (2023; first published online 1 Dec 2022). Abstract read in full.

They name the **three** findings the "best model of vision" claim rests on: (1) DNNs are most
accurate at classifying images; (2) DNNs best predict the pattern of **human errors**; (3) DNNs
best predict **brain signals**. Their objection, verbatim:

> *"these behavioral and brain datasets **do not test hypotheses regarding what features are
> contributing to good predictions** and we show that **the predictions may be mediated by DNNs
> that share little overlap with biological vision**."*
>
> *"More problematically, we show that **DNNs account for almost no results from psychological
> research**. This contradicts the common claim that DNNs are good, let alone the best, models of
> human object recognition."*
>
> *"theorists need to build models that explain the results of experiments that **manipulate
> independent variables** designed to test hypotheses rather than compete on making the best
> predictions."*

> **The methodological point generalises far beyond vision: prediction-score leaderboards and
> hypothesis tests are different activities.**

⚠️ **BBS articles are published with open peer commentary and an author response. The commentaries,
several of which are rebuttals, were not read. This is a dispute with the dissenting side unread.**

### 6.6 Where the correspondence holds and where it breaks

**Holds:** task-optimised deep hierarchies are, as of the sources read, the **best available
encoding models for V4 and IT responses to isolated static objects**, and the correspondence was
**not** obtained by fitting to neural data. **Category supervision matters.** And the qualitative
progression simple → complex → parts → objects maps onto early → middle → late CNN layers.

**Breaks:** the metric is **permissive** (a linear readout can rescue a model whose features are
unlike cortical ones); **psychological phenomena are largely unexplained**; **cue reliance diverges
from human cue reliance** (though now itself contested); **adversarial fragility has no human
analogue** ⚠️ (real and uncontested, but no primary read here and no numbers); and **the scope is
narrow** — static, isolated, foveated objects, in anaesthetised or passively fixating macaques, in
V4 and IT. **Dynamics, feedback, eye movements, clutter, and everything above IT are outside the
tested domain.**

---

## 7. Oscillations and synchrony

⚠️ **Buzsáki & Draguhn 2004 (*Science*) and *Rhythms of the Brain* (2006) were not readable.** The
band parcellation is therefore stated here without a read primary.

### 7.1 ⚠️ Gamma is not a clock

- **Gamma frequency rises monotonically with contrast**, and assemblies **as little as 400 µm apart run at different gamma frequencies** — *"a poor candidate for binding or communication, at least in V1."*
- **This is in direct tension with Fries's communication-through-coherence**, which requires the attended input to have a **higher** gamma frequency.
- **And there is a measurement problem on top of the mechanistic one:** Ray & Maunsell 2015 showed **spike waveforms contaminate the LFP in the gamma band**, making gamma phase estimation unreliable — **fatal to *measuring* a phase mechanism.**

> **Binding-by-synchrony and CTC are live proposals, not settled mechanisms, and the strongest
> objections are about whether gamma can be measured and whether it has a stable frequency at
> all.**

---

## 8. Connectomics — the circulating numbers are wrong in specific ways

### 8.1 *C. elegans*

⚠️ **"The *C. elegans* connectome is one worm" is false.** Cook et al. 2019 state the connectomes
are *"assembled from **multiple animals** and gaps are filled by **extrapolation**"*, and since
Durbin 1987 synapse **locations** are only **~75% reproducible between animals.** **The male neuron
count is disputed three ways (381 / 383 / 385).**

⚠️ **And edges ≠ synapses:** **4,887 chemical *edges* vs ~6,400 chemical *synapses* are different
quantities, routinely conflated.**

### 8.2 *Drosophila* FlyWire (2024)

⚠️ **The paper gives three irreconcilable synapse figures** — abstract *"~5 × 10⁷"*; main text
**54.5 million**; elsewhere *"~130 million"* — **and does not reconcile them.**

**Cite: "~54.5 M synapses among 139,255 neurons, dataset version 783, published 2 Oct 2024."**
⚠️ **~56% of those neurons are in the optic lobes.** ⚠️ **No numeric neurotransmitter-prediction
accuracy is given.**

> ⚠️ **The most under-reported result in connectomics:** in the Schlegel et al. 2024 companion,
> **about one-third of hemibrain cell types could not be reliably reidentified in FlyWire** despite
> near-complete morphological matching — and **the cell-type count nearly doubled between preprint
> (4,552) and publication (8,453). You must state the version.**

### 8.3 Mouse MICrONS (2025)

⚠️ **It is not 1 mm³ and not 200,000 neurons.** In-vivo dimensions **1.3 × 0.87 × 0.82 mm ≈
0.93 mm³**; *">200,000 **cells**"* but the segmented **neuron** count is **84,035**; **~523 M
synapses at 96% precision / 89% recall**; **n = 1**, a single 65-day-old male mouse; and ⚠️ **only
85 excitatory neurons have fully proofread axons *and* dendrites.**

### 8.4 ⚠️ Human DTI "connectomes" are a far weaker class of object

Of the 64 bundles systematically recovered by the majority of 20 groups, **64% were absent from the
ground truth**, and **half the invalid bundles recur systematically across groups** — so
**cross-group reproducibility does not establish validity.** **False positives persist even when
tracking ground-truth fibre orientations, so it is not a data-quality problem.** **Every
small-worldness statistic computed on a DTI connectome inherits this.**

### 8.5 What a connectome does not tell you

⚠️ **The *C. elegans* lesson:** the wiring diagram has been available since **1986** and **forty
years later there is still no complete account of its behaviour.**

**And the sharpest published argument — Jonas & Kording, "Could a neuroscientist understand a
microprocessor?" (2017) — is the best available indictment of LFP-oscillation inference, and nobody
cites it that way.** Their 6502, **which has no oscillatory mechanism whatsoever**, produced
power-law LFP spectra and region-specific "rhythms" readable as self-organized criticality.
Modelling the chip as coupled oscillators *"would make little sense."* And **forcing transistors on
produced apparent "Donkey Kong transistors"** — **1,560 broke all games, 186 broke only one** — a
direct indictment of lesion/knockout logic.

### 8.6 ⚠️ Dale's principle is misstated in a way that isn't even the same kind of claim

**"One neuron, one transmitter" and "a neuron is either excitatory or inhibitory" were stated by
neither Dale nor Eccles** (Otsuka 1988, PMID 2901390). **Sign is a postsynaptic receptor
property** — and **GABA's sign differs *by subcellular compartment within one pyramidal cell***
(axon-initial-segment synapses have a depolarized reversal potential vs somatic ones, §1.2).

> **The stable abstraction-level point survives the dispute: in cortex, excitatory and inhibitory
> cells are distinct populations with distinct transcriptomes and distinct synapse morphologies.
> Sign is a cell-type property. Networks that flip weight signs freely are not implementing
> anything a brain does. But do not state "Dale's law says one neuron, one transmitter" as settled
> fact — that reading is a misattribution.**

### 8.7 ⚠️ Small-worldness is near-vacuous

Published in *Brain Structure and Function*'s **"Brain Mythology"** section: **nearly every real
network passes σ > 1**, the coefficient *"might not faithfully capture the small-world property as
originally described by Watts and Strogatz"*, and it is **entirely null-model dependent.**

**Cortical microcircuits are small-world but explicitly *not* scale-free**, and **the motif
statistics were later attributed to neuron *geometry*.**

---

## 9. Energy — and why the brain-vs-GPU comparison is refused here

### 9.1 The artificial side

⚠️ **The GPT-3 "1287 MWh" is an estimate, not a measurement, and not an OpenAI disclosure.** It is
**Patterson et al. 2021, Table 4**; the **330 W per-accelerator figure came from OpenAI** but **the
PUE (1.10) and the US-average carbon intensity (0.429 kg/kWh) are the authors' own assumptions.**
Their own table notes it equals **0.01055% of Google's 2019 energy use.**

⚠️ **The "5 car lifetimes" headline is a neural-architecture-search row, not a training row — and
it was wrong by 18.7×.** Strubell's **Transformer-big training** row is **192 lbs = 0.0015 car
lifetimes.** Patterson's 88× reduction decomposes as **18.7× methodological + ~4.7×
Google-specific** — **quote 18.7× for a generic cloud and 88× only for Google's own run.** And
⚠️ **Strubell reports no energy figure at all for GPT-2 — anyone quoting one invented it.**

### 9.2 ⚠️ Why the comparison is refused

Seven numbered reasons, all from the dossier:

1. **No agreed FLOP-equivalent** — published "brain compute" spans **10¹³–10²⁸ op/s** depending on the unit chosen.
2. **Per-spike energy is unsettled by ~4 orders of magnitude *within* neuroscience** (see the neurons reference).
3. **No common task normaliser.**
4. **The brain's 20 W excludes ~20 years of development metabolism.**
5. **Asymmetric measurement boundaries.**
6. **Silent unit swaps** — W vs Wh, **8-bit TOPS vs FP16 FLOPS vs synaptic-ops/s**, gross vs net CO₂e, lbs vs tonnes.
7. **And the 20 W itself is a derived figure with no primary measurement in watts** (see the neurons reference).

> **State the measurements, in their own units, with their own error bars. Do not compute a ratio.**

---

## 10. Neuromorphic computing

### 10.1 The honest verdict, in a peer-reviewed sentence

> *"on ANN-oriented workloads, **SNNs fail to beat their ANN counterparts**; while on SNN-oriented
> workloads, SNNs can fully perform better"* — and *"the straightforward workload porting from ANNs
> to SNNs is **unwise**"* (Deng et al. 2020).

**The verified SNN win is on event-camera optical flow — natively sparse temporal data, exactly
where theory predicts.**

⚠️ **And note the state of the field's own self-assessment: Intel's neuromorphic lab director
published "Benchmarks for progress in neuromorphic computing" in 2019, and the field was *still*
publishing focus issues on benchmarks in November 2024.**

### 10.2 The hardware claims, with whose claim is whose

| Claim | The correction |
|---|---|
| "TrueNorth is ~70 mW" | ⚠️ **It is 63 mW, and that is conditional on a specific workload** (400×240 @ 30 fps). **There is no single "TrueNorth power."** |
| "NorthPole is 25× better than a GPU" | ⚠️ **That is an iso-process comparison** — *"compared with a GPU built on a **comparable 12 nm process**."* **Against a 4 nm GPU, IBM gives no multiplier.** And ⚠️ **NorthPole is not a spiking chip** — it is a low-precision dataflow accelerator, **routinely miscategorised as neuromorphic.** |
| "Hala Point: 1.15 bn neurons at 2,600 W" | Announced **17 April 2024**: 1,152 Loihi 2 chips, 1.15 bn neurons, 128 bn synapses, *"a maximum of 2,600 watts"* — ⚠️ **all Intel's claims, from an Intel-chosen network, in 8-bit integer TOPS, not comparable to FP16 FLOPS/W.** Intel's **"100× less energy, 50× faster" has no named benchmark, no named baseline GPU and no citation.** And the arithmetic: **128 bn / 1.15 bn ≈ 111 synapses per neuron — ~2 orders below cortical fan-in.** |

⚠️ **A citability problem worth knowing: Intel's Loihi 2 announcement URL is now a 301 to Intel's
404 redirector, and SpiNNcloud's site now redirects to a 404. Several commonly-cited neuromorphic
specs are no longer citable at all.**

---

## Sources

Research compiled **2026-11-13** from primary literature via NCBI E-utilities, Europe PMC REST and
ar5iv/arXiv. ⚠️ **Access failures that shape this file:** NCBI Bookshelf is behind reCAPTCHA (**no
Purves citation appears anywhere**); Kandel, Koch, Dayan & Abbott and Bear were unobtainable;
science.org, nature.com, royalsocietypublishing.org, sciencedirect.com and pnas.org return 403.

**Read in full text:** Harris & Shepherd 2015 (PMC4889215); Tremblay, Lee & Rudy 2016 (PMC4980915);
Rudy et al. 2011 (PMC3556905); da Costa & Martin 2010 (PMC2904586); Ozeki et al. 2009 (PMC2691725);
Sanzeni et al. 2020 (PMC7324160); Arellano & Rakic 2026 (PMC12812505); Khaligh-Razavi &
Kriegeskorte 2014 (PMC4222664, text held; numbers not extracted).

**Abstract or record only (flagged inline):** Horton & Adams 2005 (PMC1569491 — complete abstract);
Hendry et al. 1987; Yamins et al. 2014 (abstract + Significance only — **Results body
unavailable**); Bowers et al. 2023; Geirhos et al. 2019 (arXiv abstract page); Mountcastle 1957 and
1997; all Hubel & Wiesel primaries; Douglas, Martin & Whitteridge 1989; Douglas & Martin 1991/2004;
Binzegger et al. 2004; Marr 1971; Hopfield 1982; Amit, Gutfreund & Sompolinsky 1985/1987; O'Keefe &
Dostrovsky 1971; Hafting et al. 2005; Leutgeb et al. 2007; Wills et al. 2005; van Vreeswijk &
Sompolinsky 1996; Tsodyks et al. 1997; Thorpe et al. 1996; Shadlen & Newsome 1998; Buzsáki &
Draguhn 2004; Burgert et al. 2025; Schrimpf et al. 2020; Amaral, Ishizuka & Claiborne 1990;
Beaulieu & Colonnier 1985; O'Kusky & Colonnier 1982; Felleman & Van Essen 1991; Brunel 2000; Renart
et al. 2010; Xue, Atallah & Scanziani 2014; Treves & Rolls; O'Reilly & McClelland 1994; Szegedy et
al. 2014 and Goodfellow et al. 2015.

**Date discrepancies recorded, not harmonised:** Hafting et al. 2005 (online 19 June vs print
11 August); Bowers et al. (Crossref 1 Dec 2022, printed volume year 2023).

---

## Related

- [[neural-networks-biology]] — the parent skill.
- [[neural-networks-ml]] — the CNN side of §6, and the architectures whose cortical correspondence is assessed there.
- [[self-organizing-maps]] — Kohonen's map was motivated by the topographic organisation whose status §2 examines.
- [[information-theory]] — the efficient-coding and sparse-coding arguments in §5 are information-theoretic claims.
