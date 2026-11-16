---
name: neural-networks-biology
description: "Biological neural networks — real neurons, synapses, plasticity and circuits, with the numbers checked against their primary sources and the folklore flagged. Covers the neuron (and why the action potential starts ~35 µm down the axon, not at the hillock), the resting potential with Nernst/GHK as Hodgkin & Katz actually printed them, and Hodgkin–Huxley 1952 read off the page: the inverted sign convention, the published parameter table including the two 'parameters' that are not measurements, HH's own refusal to defend the gating mechanism, and why threshold is a moving boundary in a 4-D state space rather than a voltage. The famous numbers audited: 86.1 ± 8.1 billion neurons (not 100 billion, which has no primary source), the 10:1 glia:neuron ratio as refuted and arithmetically self-refuting, the glia ratio spanning 0.05 to 160 across structures, synapses-per-neuron as 6,500–9,500 in mouse cortex with no defensible total, lognormal firing rates spanning four decades with most neurons nearly silent, and the 20 W power budget as a derived figure nobody published in watts. Synaptic transmission as a stochastic few-vesicle process (median 3 docked vesicles, ~74% failures at physiological calcium) and what that does to the scalar-weight abstraction; receptor kinetics and the NMDA receptor's coincidence detection with its 50-fold spread in open probability; dendrites as computational subunits and the honest status of 'a cortical neuron is a 5–8 layer deep network'. Plasticity: Hebb's actual postulate (and that 'cells that fire together wire together' is not his, with the attribution contested), LTP's real 1973 numbers, STDP's dependence on calcium, dendritic location, bursts and neuromodulator sequence — including that the canonical window was measured at ~2.3× physiological calcium and does not survive at 1.3–1.8 mM — plus three-factor rules, behavioural-timescale plasticity, homeostasis as too slow to stabilize Hebbian learning, and the adult-neurogenesis dispute. Circuits: the cortical microcircuit by projection class rather than layer, the three interneuron families and disinhibition, the cortical column as 'a structure without a function', E/I balance as a range not a constant, inhibitory stabilization, the hippocampal circuit with its 2026-updated neuron counts, neural coding, and where CNN–ventral-stream correspondence holds and breaks. And the biological-plausibility-of-backpropagation literature with real benchmark numbers: feedback alignment, target propagation's ImageNet failure, Akrout et al.'s transport-free methods that match backprop, predictive coding's fixed-prediction caveat, equilibrium propagation, dendritic and burst-dependent models, and NGRADs as the organising frame. Use when reasoning about what real neurons do, assessing a biological-plausibility claim about an ML method, checking a brain statistic before repeating it, or explaining neuroscience accurately."
---

# Neural Networks (Biology)

A biological neuron is not a weighted-sum-plus-nonlinearity with noise. It is a
**spatially extended, stiff nonlinear dynamical system** whose inputs arrive as stochastic
few-vesicle events, whose dendrites compute before anything reaches the soma, whose
excitability reconfigures sub-second, whose gain and learning rate are set by diffusing
neuromodulators, and whose firing is metered against a real metabolic budget.

That is the spine of this skill. For the artificial abstraction that borrowed the name, see
[[neural-networks-ml]].

**Two rules govern everything below.** First: **check the number before repeating it.** This
field's most-quoted figures — 100 billion neurons, 10:1 glia, 10⁴ synapses per neuron, 20 W,
"cells that fire together wire together" — are folklore, refuted, undefined, derived, or
misattributed. Second: **state the preparation.** A result from a juvenile rat slice in 3 mM
calcium with the postsynaptic spike injected at the soma is not a fact about brains.

⚠️ throughout marks a claim that is unverified, disputed, or folklore.

## The signal

**The action potential does not start at the axon hillock.** In layer-5 pyramidal neurons it
initiates **~35 µm down the axon**, in the distal axon initial segment; the first node of
Ranvier, ~90 µm out, is not involved. And the AIS sodium-channel density that textbooks
inherited ("same as the soma") was a **patch-extraction artifact** — the true density is
**~50× the proximal dendrite**.

**Hodgkin & Huxley 1952, read off the page, is not what the textbook reports.**

- **The sign convention is inverted** — depolarization *negative*. Published V_Na = **−115**, V_K = **+12**, V_l = **−10.613 mV**. Type the original numbers into a modern-convention simulator and you get a dead axon.
- **The model has no absolute resting potential.** V is displacement from rest. "−70 mV" is a textbook convention; the one real primary measurement in the area is **48 mV** in a squid axon HH themselves said was running down.
- **Two of the seven "parameters" are not measurements.** ḡ_Na = 120 is *chosen* inside a 4-fold experimental spread (means of 80 **and** 160), and the experimental values were back-computed from the fitted α/β — circular, and HH flag it in a footnote. V_l = −10.613 mV is *solved for* to zero the resting current, printed to three decimals against an experimental mean of "−11" with a range of −4 to −22.
- **HH explicitly disclaimed the mechanism:** *"the success of the equations is no evidence in favour of the mechanism of permeability change that we tentatively had in mind."* **m³h and n⁴ are curve shapes.** The four-gating-particles story is an interpretation they offered and then declined to defend.
- **They did not invent the voltage clamp** — *"The experimental method was based on that of Cole (1949) and Marmont (1949)"*, first paragraph of paper I.
- **Threshold is not a voltage.** One paper gives three numbers (6, 8, ~15 mV) differing by temperature and tissue condition, and derives threshold's state-dependence from h and n. **It is a moving boundary in a 4-D state space (V, m, h, n).** There is no activation function in HH 1952.
- **And the canonical model missed its own measured conduction velocity by 11%** on the same fibre, with every parameter measured on that fibre.

**Subthreshold responses exist and are graded.** "All-or-none" is about the spike, not the
membrane. The neuron is an analogue device with one regenerative output mode.

## The famous numbers, audited

| Claim | Status |
|---|---|
| "100 billion neurons" | ⚠️ **Folklore with no primary source.** Herculano-Houzel surveyed senior neuroscientists; *"none of the consulted scientists could cite an original reference."* Measured: **86.1 ± 8.1 billion**, and 100 bn *"lies outside of the margin of variation found so far in human brains."* **Cortex holds 19% of neurons (~16 bn); cerebellum holds 69 bn.** |
| "10× more glia than neurons" | ⚠️ **Refuted — and arithmetically self-refuting from the start.** 130 bn glia at 10:1 caps neurons at 13 bn, but cortex alone had 10–16 bn. Whole-brain ratio is slightly **below 1:1.** |
| "The glia:neuron ratio is 1:1" | ⚠️ Also a bad summary. It spans **0.05 (cerebellum) to ~160 (globus pallidus).** Glial density is near-constant; **the ratio is a neuronal-density readout.** |
| "~10⁴ synapses per neuron" | Defensible order of magnitude for a *mouse cortical* neuron (**measured 6,500–9,500**, a remarkably tight range). **Off by >10× for a Purkinje cell (~175,000).** ⚠️ **And the total human cortical synapse count (10¹⁴–10¹⁵) is unverified — the paper usually cited for it returned zero hits on a title search.** |
| "The brain runs on 20 W" | ⚠️ **No primary source in watts.** The primary measurement is **3.3 ± 0.4 mL O₂/100 g/min**, which derives to **~15.5 W**. The 20 W comes from the glucose route. **State the measurement, not the watts.** |
| Spikes are the expensive thing | ⚠️ **Superseded by Attwell's own senior-author revision.** The 2012 budget: **postsynaptic glutamate receptors 50%, action potentials 21%, resting potentials 20%.** **The expensive thing is receiving, not sending** — which undercuts the usual energy argument for sparse *spiking*. |
| Firing rates | **Lognormal over 3–4 orders of magnitude** (0.001–10 Hz in CA1). **70.4% of CA1 pyramids fire below 1 Hz during running while 13.3% contribute half of all spikes.** Fewer than **5% of auditory-cortex neurons** exceed 20 spikes/s at any instant. ⚠️ **And every mean firing rate from extracellular recording is upward-biased by construction** — spike sorting finds units *by* their spikes. |
| "The neuron" as a type | ⚠️ **A fiction, and the dossier demonstrates it rather than asserting it.** One mouse cortical area, one paper: **116 / 95 / 71 / 56 clusters** by modality. The whole-mouse-brain atlas moved **5,200 → 5,322 clusters** between preprint and print of the same study. Available levels: **34 / 338 / 1,201 / 5,322.** |

## Transmission is stochastic, and that is the point

At a hippocampal CA3→CA1 bouton at physiological calcium: **median 3 docked vesicles**,
**p_syn ≈ 0.26 — about 74% failures** — and **strength is 85% explained by release probability
alone**, with vesicle number uncorrelated and quantal size barely mattering.

> **A scalar weight is a statement about the *mean* of a stochastic, history-dependent,
> few-vesicle process — and the quantity it stands in for is mostly a *presynaptic release
> probability*, not a postsynaptic gain.**

And the receptor is not one device. **NMDA receptor open probability ranges 0.01 (GluN2C/2D) to
~0.5 (GluN2A) — 50-fold — and deactivation 35 ms to ~4,400 ms.** The coincidence window is set
by which GluN2 subunit is present and is **tens to hundreds of milliseconds, not
microseconds** — which is why NMDARs can detect coincidence over a behaviourally meaningful
window at all. Metabotropic effects decay over **200–600 ms, ~500× slower than an AMPA
current.**

**Three corrections worth carrying:**

- ⚠️ **"Shunting inhibition is divisive" is wrong as stated.** The paper is titled *"Shunting inhibition does not have a divisive effect on firing rates."* The divisive formula is at best a *subthreshold-voltage* statement; **the subthreshold-vs-rate distinction is the crux and is usually elided.**
- ⚠️ **"Residual calcium explains facilitation" fails quantitatively** — residual-Ca²⁺-only models cap the paired-pulse ratio at ~1.02.
- ⚠️ **"Electrical coupling synchronizes networks" is not a general answer.** In cerebellar Golgi cells it **desynchronizes**, because the slow afterhyperpolarization survives low-pass filtering better than the spike does. Two papers on the same brain region reach opposite conclusions.

**Dendrites compute.** Inputs on the same thin branch sum **sigmoidally**, inputs on different
branches **linearly** — *"supporting a two-layer model of dendritic integration."* ⚠️ But handle
the depth claim carefully: Beniaguev et al.'s **preprint says seven layers, the published
abstract says five to eight**; it was fit to a **simulated** compartmental model, not a recorded
cell; **removing NMDA receptors makes one hidden layer sufficient**, so it is a claim about NMDA
nonlinearity rather than morphology; and **the same group's 2026 paper uses a three-layer
network as standard.** **Depth is a property of the fitting tolerance.**

## Plasticity

**Hebb's postulate, and what it is not.** ⚠️ **The 1949 book was never opened by anyone in this
chain** — two secondary sources give one wording with a page number, a third (the LTP field's own
founders) gives a different one. The difference is not cosmetic: *"A's efficiency, **as one of
the cells firing B**"* frames A as one of several cells already providing convergent input; the
short form erases that. **There is no depression clause, no timing window, no scalar weight, no
normalisation, no competition, and no ceiling.** And ⚠️ **"cells that fire together wire
together" is not Hebb — a 2022 paper credits Löwel & Singer 1992, a 2025 paper credits Shatz
1992, and neither 1992 text was readable.**

**LTP's founding paper reports no single effect size.** Bliss & Lømo 1973 report the *fraction of
experiments* in which each of three measures changed — and **the commonest sign was a latency
reduction (57%)**, with the authors explicitly invoking **an increase in granule-cell
excitability**. "LTP = synaptic weight increase" is a later simplification. **Longest duration in
either 1973 paper: 3 days awake, 10 hours anaesthetized** — and **LTP was inducible awake on only
26% of occasions, with 8% showing depression.**

**STDP is the single most over-generalized result in the field.**

| | |
|---|---|
| ⚠️ **Calcium** | **The canonical ±20 ms window was measured in 3 mM extracellular calcium, ~2.3× physiological.** At 1.3–1.5 mM, single-spike pairing produces **no plasticity**; at 1.8 mM, **LTD for *both* timings**. It is restored only by raising the pairing frequency to 5–10 Hz or using 3–4 postsynaptic spikes. **And this retrospectively explains a long-standing contradiction in which "the only obvious difference was the concentration of extracellular calcium used (2 vs. 3 mM)."** |
| ⚠️ **Dendritic location** | **At distal dendrites the window is inverted.** |
| ⚠️ **Superposition** | *"The efficacy of each spike in synaptic modification was suppressed by the preceding spike in the same neuron"* — **which invalidates the linear-superposition-of-pairs assumption underlying essentially every pairwise STDP simulation.** |
| ⚠️ **Neuromodulators** | In striatum, **blocking D1/D5 receptors prevents both LTD and LTP.** In hippocampus, **dopamine applied *after* the induction protocol still changes the outcome**, and acetylcholine-then-dopamine converts depression into potentiation. **The sign is not determined at the time of the spikes.** |
| ⚠️ **The postsynaptic spike** | *"Backpropagating action potentials may be neither necessary nor sufficient."* Under synaptic rather than injected drive, *"the results do not generally support STDP."* **The experiment's own manipulation creates the phenomenon it measures.** |
| ⚠️ **Cell type** | **Absent when the postsynaptic cell is GABAergic.** The canonical window is an exc→exc rule only. |
| ⚠️ **Models** | *"the measured single-spike learning rule between hippocampal CA3 and CA1 pyramidal neurons **does not predict the existence of long-term potentiation**."* |

**And the rule that matches behaviour is not STDP.** Behavioural timescale synaptic plasticity
operates over **seconds** (depression gone beyond ~4–5 s), in **one trial in vivo**, on input
that was *"not initially coincident"* with spiking, triggered by a **dendritic calcium plateau**,
with the **sign set by the current synaptic weight — weak inputs potentiate, strong inputs
depress.** **BTSP is not "slow STDP"; its authors call it non-Hebbian.** ⚠️ Established at one
synapse class by one group plus collaborators.

Three further corrections: ⚠️ **synaptic scaling is not multiplicative** (the scaling factor is
~1 for small mEPSCs and rises with amplitude, across three datasets including previously
published ones — **so the information-preservation argument for scaling does not go through as
usually stated**); ⚠️ **homeostasis is 10³–10⁵ times slower than the instability it must
suppress, so it cannot be the stabilizer** and the fast stabilizer is unidentified; and ⚠️
**adult human hippocampal neurogenesis is a genuine unresolved dispute** — present both sides.

## Circuits

**Classify excitatory cells by projection, not by layer.** IT (the only class projecting to
contralateral cortex), PT (subcerebral), CT (corticothalamic) — ⚠️ **and their laminar
distributions overlap, so "layer 5 cell" is not a cell type.** The strongest published warning
against the textbook L4→L2/3→L5 cartoon is from the authors of the modern synthesis: there are
*"**multiple entry points** … and … **multiple exit points** — a key principle of cortical
circuit organization often lost in simplified schematics."*

**Interneurons partition into three groups accounting for nearly 100%:** **PV ~40%** (basket and
chandelier; **times individual sodium spikes**), **SST ~30%** (Martinotti; **gates dendritic
integration, calcium spikes and bursts**), **5HT3aR ~30%** (VIP ≈ 12% of all interneurons;
neurogliaform cells). ⚠️ **These fractions are established for mouse S1 — the canonical
interneuron taxonomy is a mouse taxonomy, and the double-bouquet cell has no rodent homologue.**
The canonical disinhibitory motif is **VIP→SST**, driven by cortico-cortical feedback and
cholinergic input — but ⚠️ *"the mere presence of an interneuron-to-interneuron connection does
not imply disinhibition."*

**The cortical column is "a structure without a function"** — the authors' own registered keyword
is **spandrel**. *"A 'column' now refers to cells in any vertical cluster that share the same
tuning for any given receptive field attribute"*; ocular dominance columns are **present in some
species and absent in others with no identified behavioural correlate**, and vary **between
conspecifics and within one individual's V1.** Hubel & Wiesel's own data showed the term is a
misnomer — *"the columns were not Greek pillars, but swirling slabs"* — and Mountcastle's
minicolumn dimensions were **guesses**, because he could not find his electrode tracks. ⚠️ **But
do not write "columns don't exist." Write "no demonstrated function, and no single referent."**

**E/I balance is a range, not a constant:** ~**15%** GABAergic in rodent cortex, ~**20–25%** in
monkey, **<20% in monkey V1**, varying by area and layer and **between individual animals in the
same paper.** The structural asymmetry matters more than the ratio: **inhibition is dense and
blanket** (pyramid↔PV probability 0.5–0.75, nearly distance-independent) while **excitation is
sparse and local** (0.09 → 0.01 over 25–200 µm).

**Surround suppression is a withdrawal of recurrent excitation, not added inhibition** — a
preferred-orientation surround reduced **both** excitatory and inhibitory conductances, by ~51%
and ~38%. ⚠️ **But a paradoxical response is not a unique signature of an inhibition-stabilized
network** (a two-population inhibitory circuit mimics it), and ⚠️ **the effect appears only with
transgenic, not viral, opsin expression — so any single optogenetic negative result may be an
expression artefact.**

**The hippocampal numbers in every model are legacy.** A January 2026 systematic review of 264
stereological estimates gives male rat **CA3 210,000, CA1 350,000, EC layer II 108,000** — the
last being **about half** the traditional figure. ⚠️ **And the Hopfield 0.138N capacity is Amit,
Gutfreund & Sompolinsky's, not Hopfield's**, and holds only for full connectivity, symmetric
weights, random unbiased patterns, zero temperature and a catastrophic-breakdown definition.
**It is not a fact about CA3.**

**On the CNN correspondence.** What Yamins et al. actually established is that **task performance
predicts neural predictivity**, in a model *"not explicitly constrained to match neural data"* —
a real and non-obvious result. ⚠️ **But the metric is explained variance of single-site responses
to static isolated objects after linear regression, normalised by a noise ceiling, and each
qualifier does load-bearing work.** The permissiveness is the critics' point: *"the predictions
may be mediated by DNNs that share little overlap with biological vision."* ⚠️ **Texture bias is
now contested in print** (NeurIPS 2025), and ⚠️ **Quiroga's concept cells are explicitly *not*
grandmother cells, per Quiroga.**

**And a connectome does not give you the function.** *C. elegans* has had its wiring diagram
since **1986** and there is still no complete account of its behaviour. ⚠️ **Nor are the
connectome numbers what people quote:** FlyWire's paper gives **three irreconcilable synapse
figures**; MICrONS is **0.93 mm³ and 84,035 segmented neurons from one mouse**, with **85
neurons fully proofread**; and about **a third of hemibrain cell types could not be reliably
reidentified in FlyWire.** The sharpest argument here is Jonas & Kording's: their 6502 — **which
has no oscillatory mechanism whatsoever** — produced power-law LFP spectra and region-specific
"rhythms," and forcing transistors on produced **"Donkey Kong transistors."**

## Is backprop biologically plausible?

The honest shape of this literature, with the numbers:

| Question | Answer |
|---|---|
| Is **exact** backprop implemented in cortex? | **No**, and nobody in this literature argues otherwise — including Hinton, co-author of both the key negative result and the main framework paper. ⚠️ **But do not quote Crick 1989 for why: its entire published abstract is two sentences and the weight-transport argument is in the paywalled body.** |
| Is weight **symmetry** necessary? | **No.** Fixed random feedback gives a usable descent direction: MNIST **FA 2.1% vs BP 2.4%**, holding at **50% synapse-level sparsification**, and **1.8% in a stochastic spiking net.** This retires the strongest form of the objection. |
| Does feedback alignment **scale**? | **No** — ImageNet top-1 error **93.08%** in a locally-connected net (vs BP 71.43%), independently corroborated at **97.4% / 98.9%** in ResNets. |
| Does **target propagation** scale? | **No.** ImageNet top-1 **98.34–99.36%** — essentially chance. *"Our results are largely negative."* **The failure mode is informational:** a one-hot label carries ~10 bits that must be inverted into a target for a high-dimensional penultimate layer. |
| Can weight **transport** be removed at scale? | **Yes — if the feedback path *learns*.** ResNet-50 ImageNet top-1: **weight mirrors 23.4%, Kolen–Pollack 23.9%, backprop 22.9%**; on ResNet-18 **Kolen–Pollack's 29.2% slightly beat backprop's 30.1%.** ⚠️ **But Kolen–Pollack transports *updates* (demanding identical increments and decay at each forward/feedback pair), weight mirrors need a separate noisy "mirror mode," and these are ConvNets — so weight *sharing* is retained.** |
| Does **DFA** match backprop without transport? | ⚠️ **Not on the configuration that works.** WikiText-103 Transformer validation perplexity: BP **29.8**; DFA-Macro **52.0** — and *"Macro … impl[ies] weight transport at the layer-scale"*; the genuinely transport-free Micro lands at **93.3**. Same paper: *"DFA fails to train more classic 2D image convolutional layers."* |
| Does **predictive coding** solve it? | ⚠️ **The equivalence holds only under the "fixed prediction assumption," under which the algorithm is *"algorithmically equivalent to a direct implementation of backpropagation"* — so the plausibility gain is illusory.** And *"a strict interpretation … does not accurately compute gradients."* |
| **Equilibrium propagation?** | CIFAR-10 **11.7%** with symmetric nudging (vs **86%**, near chance, for standard same-sign nudging). ⚠️ **Real progress, two benchmark generations behind the ImageNet question — and EP ties its update to "a standard form of spike-timing dependent plasticity," an assumption the plasticity section shows is not safe.** |
| **Forward-forward?** | ⚠️ **Never claimed to scale** — *"a few small problems,"* *"Some Preliminary Investigations."* **Greedy-layerwise: it avoids deep credit assignment rather than solving it.** |

**The organising idea is NGRADs** — *"feedback connections may instead induce neural activities
whose **differences** can be used to locally approximate these signals."* Target prop,
equilibrium prop, contrastive Hebbian learning, recirculation, dendritic microcircuits and
predictive coding are all NGRADs. **It recasts "how does the brain do backprop?" as "how does the
brain compute and use activity differences?"** — and cortical biology supplies candidate
substrate: **segregated apical vs basal compartments**, **interneuron-computed apical prediction
errors**, **burst-multiplexed dual channels on one axon** (with signed error as a deviation of
burst fraction from baseline, so no negative rates are needed), and **eligibility traces with a
hard 0.3–2 s window** imposed by phosphodiesterase activity.

> **So the defensible claim is narrower than "no biologically-plausible rule has matched backprop
> at scale." It is: no rule that is *simultaneously* local, phase-free, spike-compatible,
> weight-sharing-free AND transport-free has matched backprop at ImageNet scale. Each individual
> implausibility has been removed by some method; none has removed them all at once.** ⚠️ And no
> 2024–2026 primary on this question was found, so this is the state of the art **as of ~2023**.

## Always-apply

1. **Check the number before repeating it.** 100 billion, 10:1 glia, 10⁴ synapses, 20 W, 0.138N, "CA3 = 250,000" and the Aα-to-C conduction-velocity table are all folklore, refuted, superseded, or unverifiable. Give the measured value in its own units.
2. **State the preparation and the species.** Juvenile vs adult, slice vs culture vs in vivo, rodent vs primate vs human, and **the extracellular calcium concentration** if the claim is about plasticity.
3. **Never present pairwise STDP as the brain's learning rule.** If you invoke it, say which calcium, which dendritic location, which cell type, and whether the postsynaptic spike was injected.
4. **Do not quote a verbatim sentence from a paper nobody in the chain opened.** This applies above all to Hebb 1949 and Crick 1989 — both are routinely quoted and neither was readable here.
5. **Record disputes as disputes.** Gliotransmission, metabotropic NMDAR signalling, adult human neurogenesis, the cortical column, GABA polarity in development, inhibition stabilization, texture bias, and whether electrical coupling synchronizes are all live. Give both sides; do not harmonize.
6. **Keep "excitatory/inhibitory identity is a cell-type property" and "Dale's law says one neuron, one transmitter" apart.** The first survives; the second was stated by neither Dale nor Eccles.
7. **When comparing brains to artificial networks, state both measurements in their own units and refuse the ratio.** Published "brain compute" spans 10¹³–10²⁸ op/s depending on the unit chosen, and per-spike energy is unsettled by four orders of magnitude *within* neuroscience.
8. **Distinguish "the anatomy permits X" from "X is demonstrated."** CA3-as-attractor, columns-as-computational-units, and astrocytes-as-computational-elements are all interpretations fitted to permissive anatomy.
9. **Say which version of a connectome you mean, with its date.** Cell-type and synapse counts have moved substantially between preprint and publication of the same study.
10. **Separate prediction scores from hypothesis tests.** A leaderboard that rewards linear-readout predictivity can be topped by a model whose features are unlike cortical ones, because the regression does the work.

## How to use the references

- **`references/neurons-and-signalling.md`** — anatomy and glia (including the gliotransmission Dual Perspectives pair in both camps' own words); the resting potential with Nernst and GHK as Hodgkin & Katz printed them, orientation and caveats intact; Hodgkin–Huxley 1952 in full — the five *J Physiol* papers properly distinguished, the equation set and rate functions transcribed from the page images, Table 3 with the two non-measurements exposed, HH's own disclaimers, threshold, refractoriness and the 11% velocity miss; the complete folklore audit with the arithmetic that should have caught the 10:1 ratio in the 1970s; neuron diversity and the method-dependence of cell-type counts; and **the 18-item itemized list of where McCulloch–Pitts and the perceptron depart from biology**, with MP's five assumptions and four equivalence theorems quoted, and Rosenblatt's own 1958 critique of the lineage.
- **`references/synapses-and-transmission.md`** — release machinery and vesicle pools (with the labs' disagreements and the ~2-orders-of-magnitude dispute about retrieval time); the calcium cooperativity exponent and why it is not 4; the full quantal analysis at a central synapse at physiological calcium and the argument it makes against the scalar weight; the Tsodyks–Markram parameters with the juvenile-rat preparation that is always dropped; receptor kinetics tables for AMPA, kainate and NMDA with the 50-fold open-probability spread; the NMDA coincidence detector's four requirements and three complications; the unresolved metabotropic-NMDAR dispute; the verified unitary-EPSP table and why "human synapses are stronger" is confounded; shunting inhibition's correction; dendritic spikes, NMDA plateaus, and the four problems with "a neuron is a 5–8 layer network"; gap junctions including the desynchronization inversion; neuromodulation anatomy and the honest limits on the functional vocabulary; and the cleft-width and energy corrections.
- **`references/plasticity-and-learning.md`** — Hebb's two renderings side by side and what he did not claim; the instability of Hebbian learning with Oja, BCM and the normalisation choices, and why hard bounds are necessary but not sufficient; LTP and LTD with the 1973 numbers, synaptic tagging and capture, the protein-synthesis challenge, and what engram optogenetics does and does not establish; STDP's founding experiments with the protocols restored, the four model-side results that retire it as a "first law," and the physiological-calcium headline in full; three-factor rules, the phosphodiesterase-gated eligibility window, and BTSP; homeostasis with both corrections; neurogenesis, critical periods and consolidation; and **the backprop-plausibility literature in depth** — all nine objections, every method's actual benchmark numbers, and the two refereed statements that are in tension.
- **`references/circuits-and-coding.md`** — the microcircuit by projection class with the scale numbers; the three interneuron families, their targets and the disinhibition caveats; the column dispute with Mountcastle's guesses, Hubel & Wiesel's misnomer, Horton & Adams's five-step argument and da Costa & Martin's "whose column would that be?"; E/I counts with the between-animal variation; inhibitory stabilization with the expression-artefact finding; the hippocampal circuit with the 2026 counts, the Hopfield attribution correction and an honest audit of the attractor story; neural coding; the CNN correspondence with what is and is not verifiable about the variance-explained figures, Brain-Score's citability problem, and Bowers et al.'s critique; oscillations and why gamma is not a clock; connectomics with exact versioned counts and Jonas & Kording; Dale's principle and the small-worldness critique; energy with the seven reasons the brain-vs-GPU ratio is refused; and neuromorphic hardware with vendor claims separated from peer review.

## Sources

Research compiled **2026-11-13** from primary literature. Routes that worked: NCBI E-utilities
`efetch`, Europe PMC REST, ar5iv/arXiv. **416 unique DOIs, 218 unique PMCIDs** across the four
reference files, each claim carrying either a named artifact or an explicit unverified flag.

⚠️ **Access failures that shape this skill, stated plainly.** NCBI Bookshelf is behind reCAPTCHA,
so **Purves *Neuroscience* was never consulted and no Purves citation appears anywhere**; Kandel,
Koch, Dayan & Abbott and Bear were likewise unobtainable. PMC gates article HTML behind a SHA-256
proof-of-work; nature.com, science.org, royalsocietypublishing.org, sciencedirect.com, pnas.org
and jneurosci.org all return 403. **This is a primary-literature-based account, not a
textbook-based one** — which is why some ordinary textbook numbers (reversal potentials, the
fibre-class velocity table, NMJ quantal content, the Mg²⁺ block IC50, spines per cortical
pyramidal neuron) appear here as **unverified** rather than as facts.

**The spine.** Hodgkin & Huxley, *J Physiol* 117(4):500–544, 1952 (PMC1392413, incl. pp. 519–520
page images); Hodgkin, Huxley & Katz, *J Physiol* 116(4):424–448 (PMC1392219); Hodgkin & Katz,
*J Physiol* 108(1):37–77, 1949 (PMC1392331, incl. p. 66 image); Goldman, *J Gen Physiol*
27(1):37–60, 1943 (PMC2142582); Kety & Schmidt, *J Clin Invest* 27(4):476–483, 1948 (PMC439518);
Azevedo et al., *J Comp Neurol* 513(5):532–541, 2009, doi:10.1002/cne.21974 (⚠️ **abstract only —
so n, sex and age of the sample are unverified**); Herculano-Houzel, *Front Hum Neurosci* 3:31,
2009 (PMC2776484); von Bartheld, Bahney & Herculano-Houzel, *J Comp Neurol* 524(18), 2016
(PMC5063692); Howarth, Gleeson & Attwell, 2012 (PMC3390818); Mizuseki & Buzsáki, *Cell Rep*
4(5):1010–21, 2013 (PMC3804159); Südhof, *Neuron* 80(3):675–690, 2013 (PMC3866025); Durst et al.,
*Nat Commun* 2022 (PMC9576736); Hansen et al., *Pharmacol Rev* 73(4):298–487, 2021 (PMC8626789);
Inglebert, Aljadeff, Brunel & Debanne, *PNAS* 117(52):33639–48, 2020 (PMC7777146); Inglebert &
Debanne, *Front Cell Neurosci* 15:727336, 2021 (PMC8488271); Milstein et al., *eLife* 10:e73046,
2021 (PMC8776257); Lillicrap, Cownden, Tweed & Akerman, *Nat Commun* 7:13276, 2016 (PMC5105169);
Bartunov et al., arXiv:1807.04587 (NeurIPS 2018); Akrout, Wilson, Humphreys, Lillicrap & Tweed,
arXiv:1904.05391 (NeurIPS 2019); Rosenbaum, *PLoS One* 17(3):e0266102, 2022 (PMC8970408);
Lillicrap, Santoro, Marris, Akerman & Hinton, *Nat Rev Neurosci* 21(6):335–346, 2020; Harris &
Shepherd, *Nat Neurosci* 18(2):170–181, 2015 (PMC4889215); Tremblay, Lee & Rudy, *Neuron*
91(2):260–292, 2016 (PMC4980915); Horton & Adams, *Phil Trans R Soc B* 360(1456):837–862, 2005
(PMC1569491); da Costa & Martin, *Front Neuroanat* 4:16, 2010 (PMC2904586); Ozeki et al.,
*Neuron* 62(4):578–592, 2009 (PMC2691725); Sanzeni et al., *eLife* 9:e54875, 2020 (PMC7324160);
Arellano & Rakic, *Hippocampus* 36(1):e70070, 2026 (PMC12812505); Yamins et al., *PNAS*
111(23):8619–24, 2014 (⚠️ **abstract and Significance only — the Results body was unavailable, so
the variance-explained figures are not verified**); Bowers et al., *Behav Brain Sci* 46:e385.
Full citation lists with DOIs, PMCIDs and per-claim flags are in the four reference files.

**The folklore list, for quick reference.** Do not repeat any of these without the correction:
100 billion neurons; 10:1 glia:neuron; a single glia:neuron ratio; 10¹⁴–10¹⁵ total synapses;
"pyramidal cells are 70–80% of cortical neurons"; 20 W as a measurement; the Aα–C
conduction-velocity table; "the action potential starts at the axon hillock"; HH's values in
modern-convention form presented as theirs; "cells that fire together wire together" as Hebb;
the pairwise STDP window as the brain's learning rule; "Markram et al. paired at 10 Hz" (the OA
source says 20 Hz, in bursts); τ₊/τ₋ as Bi & Poo's own fit (they are plausibly Pfister &
Gerstner's); "synaptic scaling is multiplicative"; "shunting inhibition is divisive"; "the
calcium cooperativity of release is 4"; "the cleft is ~20 nm" (a dehydrated-tissue number);
0.138N as Hopfield's and as a fact about CA3; "CA3 = 250,000 rat neurons"; "Dale's law says one
neuron, one transmitter"; "small-world" as informative; Quiroga's concept cells as grandmother
cells; MICrONS as 1 mm³ and 200,000 neurons; FlyWire's synapse count without a version; Nansen
on glia as the seat of intelligence; and the GPT-3/car-lifetimes energy figures without their
corrections.

## Related

- [[neural-networks-ml]] — the artificial abstraction, whose 18 departures from this substrate are itemized in `references/neurons-and-signalling.md`.
- [[integrated-information-theory]] — a theory that takes the *causal* structure of this substrate, rather than its function, to be what matters for consciousness.
- [[panpsychism]] — the metaphysical position IIT is repeatedly accused of occupying.
- [[evolutionary-algorithms]] — the other biologically-inspired paradigm, with its folklore checked the same way.
- [[self-organizing-maps]] / [[learning-vector-quantization]] — Kohonen's competitive-learning branch, motivated by cortical topographic maps.
- [[information-theory]] — the entropy and mutual-information machinery behind the efficient- and sparse-coding arguments.
- [[dsm-neurocognitive]] — where this substrate's failures become clinical.
