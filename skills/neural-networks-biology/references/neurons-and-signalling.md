# The neuron and the signal

Anatomy, the resting potential, Hodgkin–Huxley, the famous numbers checked against
their primary sources, neuron diversity, and an itemized account of where the
McCulloch–Pitts/perceptron abstraction departs from the biology.

⚠️ marks a claim that is unverified, disputed, or folklore. Where two sources
disagree, both are recorded and **not** reconciled.

---

## 1. Anatomy — and the compartment the textbook diagram gets wrong

| Compartment | What it does | Status of the usual numbers |
|---|---|---|
| Soma / perikaryon | Nucleus, most protein synthesis | ⚠️ The quoted 4 µm (cerebellar granule) → ~100 µm (motoneuron, Betz cell) diameter range is **unverified** — no primary morphometric study was read. Do not ship it with a citation. |
| Dendrites + spines | The receptive arbor | One verified per-cell count: **~175,000 parallel-fibre synapses on a single rat Purkinje dendritic tree** (Napper & Harvey 1988). ⚠️ Spines per *cortical pyramidal* neuron: unverified. |
| Axon initial segment (AIS) | **Where the action potential actually starts** | Verified — see below. |
| Axon, nodes, terminals | Propagation and output | Node geometry is a tuned variable, not a constant — see §1.2. |

### 1.1 The action potential does not start at the axon hillock

Direct voltage-sensitive-dye measurement in layer-5 pyramidal neurons:

- initiation site **~35 µm from the hillock**, in the **distal** axon initial segment
- AIS length ~40 µm; *"the initial 40 µm of the axon is essential for action potential generation"*
- the first node of Ranvier is **~90 µm** from the hillock and experiments targeting it *"suggested it was not involved in action potential initiation"*
- conclusion: *"action potentials are generated in the distal region of the axon initial segment"*

Palmer & Stuart, *J Neurosci* 2006;26(6):1854–63, PMC6793621 (abstract read).

**And the channel-density figure that was in textbooks was an artifact.** "AIS Na⁺
density equals the soma's" was the patch-clamp answer for years; it was wrong,
because channels anchored to the actin cytoskeleton resist patch extraction —
disrupting actin *increased* the recordable AIS Na⁺ current. True density is
**~50× the proximal dendrite**, and models need ~2,500 pS/µm². Kole et al.,
*Nat Neurosci* 2008;11(2):178–86 (abstract read).

The initiation site also **moves with activity**: ⚠️ "Neuronal adaptation involves
rapid expansion of the action potential initiation site" (Scott et al., *Nat Commun*
2014, PMC4050282 — citation confirmed, body not read).

### 1.2 Myelin and nodes are a tuning knob, not fixed plumbing

- rat optic nerve: node length varies over a **4.4-fold** range; cortical axons **8.7-fold**
- variation is much smaller *along* an axon than *between* axons
- modelled effect on conduction speed: **~20%**, comparable to changing myelin wrap number or internode length
- for a given speed change, the membrane-area change needed at the node is **>270-fold less** than in the sheath — i.e. energy-cheap, fast tuning

Arancibia-Cárcamo et al., *eLife* 2017;6:e23329, PMC5313058 (abstract read). The
authors propose this as a mechanism *"for tuning the arrival time of information in
the CNS."*

⚠️ Internodes per oligodendrocyte ("40–60") and internode length in µm: unverified,
no primary read.

### 1.3 The scale the canonical model was actually fit to

Hodgkin & Huxley's own axon geometry: **axis-cylinder radius a = 238 µm**
(≈0.5 mm diameter), axoplasm resistivity R₂ = 35.4 Ω·cm, C_m = 1.0 µF/cm², at
**6.3 °C**. Verified, HH 1952, PMC1392413.

> The entire canonical model of the neuron was fit to a half-millimetre
> invertebrate cable, at 6.3 °C, with no dendrites and no synapses.

---

## 2. Glia

### 2.1 How many

**Non-neuronal cells 84.6 ± 9.8 billion vs neurons 86.1 ± 8.1 billion** in the adult
male human brain; glia are *"at most 50% of all brain cells."* (Azevedo et al. 2009
abstract; Herculano-Houzel 2009, PMC2776484, full text.)

### 2.2 Human astrocytes are not scaled-up rodent astrocytes

- 2.6-fold larger in diameter than rodent; **~10-fold more GFAP+ primary processes**
- Ca²⁺ waves propagate at **36 µm/s, ~4× faster** than rodent
- human cortex has subclasses **absent in rodent**: interlaminar astrocytes (superficial layers, long unvaricosed processes reaching layers 3–4) and a varicose-projection type in layers 5–6
- *"whereas a domain of a rodent astrocyte covers ~20,000–120,000 synapses, human astrocytes can cover from ~270,000 to 2 million synapses within a single domain"*

Oberheim et al., *J Neurosci* 2009;29(10):3276–87, PMC2819812.

⚠️ The standard itemized function list (glutamate uptake, K⁺ buffering, metabolic
support, blood-flow coupling, synapse formation) was **not** verified primary-by-primary.

⚠️ The microglial pruning literature (Nimmerjahn 2005; Stevens 2007; Paolicelli 2011;
Schafer 2012) is **citation-confirmed, body unread**. "Microglia implement
activity-dependent structural plasticity" is the standard reading of those four
papers, not a verified claim here.

### 2.3 The tripartite synapse is an open fight, not settled background

**Origin:** Araque, Parpura, Sanzgiri & Haydon, "Tripartite synapses: glia, the
unacknowledged partner," *Trends Neurosci* 1999;22(5):208–215 (abstract only;
paywalled, not in PMC). ⚠️ **Note the founding abstract's premise:** *"According to
the classical view … the numerically superior glial cells have inferior roles."*
"Numerically superior" **was already the refuted 10:1 folklore** (§4.2). The framing
of the founding paper rests on a bad number.

*J Neurosci* 2018;38(1) ran this as a commissioned **Dual Perspectives** pair. Both
read in full:

**Against — Fiacco & McCarthy**, "Multiple Lines of Evidence Indicate That
Gliotransmission Does Not Occur under Physiological Conditions," PMC5761435:

> *"while we and others can apply techniques to cause gliotransmission, there is
> considerable evidence … which suggests that gliotransmission is a pharmacological
> phenomenon rather than a physiological process."*
>
> *"Overall, the data suggest that Ca²⁺-dependent release of neurotransmitters is the
> province of neurons, not astrocytes, in the intact brain under physiological
> conditions."*

Their two key negatives: **MrgA1R transgenics** (an exogenous Gq-GPCR in ~90% of
astrocytes, whose Ca²⁺ response closely resembles mGluR-evoked Ca²⁺ in the same
cells) produced *"no effect on neuronal synaptic transmission or short- or long-term
plasticity"*; and **IP3R2 knockout** showed *"no effect of abolishing IP3R-sensitive
sources of astrocyte Ca²⁺ on neuronal synaptic activity."* They state their own
caveat: Ca²⁺ was not examined in the **fine processes** of IP3R2−/− astrocytes. They
are epistemically careful — they distinguish absence of evidence from evidence of
absence and claim the latter.

**For — Savtchouk & Volterra**, "Gliotransmission: Beyond Black-and-White,"
PMC6705815. They name four assumptions behind the negative data and call them
*"likely wrong and oversimplistic"*: that deleting IP3R2 removes all Ca²⁺-dependent
gliotransmission; that stimulating transgenic MrgA1 mimics physiological astrocyte
Ca²⁺; that age-dependent mGluR5 downregulation argues against adult gliotransmission;
and that failure of transcriptomics to detect vGluts/canonical SNAREs proves
vesicular gliotransmission does not exist. On IP3R2:

> *"the initial conclusion made by the field should be revised to the quite different
> 'astrocytic Ca²⁺ signaling mediated by a particular isoform of IP3 receptor does not
> play a role in a particular form of LTP.'"*

**The technical crux** — Bazargani & Attwell, "Astrocyte calcium signaling: the third
wave," *Nat Neurosci* 2016;19(2):182–9 (abstract only). Wave 1: astrocytes as powerful
regulators. Wave 2: *"These findings were challenged by a second wave of reports that
astrocyte calcium transients did not mediate functions attributed to gliotransmitters
and were too slow."* Wave 3: *"Remarkably, the tide has now turned again: the most
important calcium transients occur in fine astrocyte processes not resolved in earlier
studies."*

**The signal may live in a compartment the early methods could not see.** Neither camp
has conceded. The journal itself told readers to *"form their own perspectives."*

⚠️ The commonly cited "Sloan & Barres skepticism about gliotransmission" could not be
located: the Sloan & Barres 2018 *J Neurosci* piece is a Progression/obituary article
about transcriptome databases, not a skeptical gliotransmission paper. If you need the
transcriptomic argument, go find the actual transcriptome paper.

⚠️ **"Nansen said glia are the seat of intelligence" is a misquotation**, traced to
Galambos 1961 and repeated by Fields 2009 and Verkhratsky & Butt 2013. Nansen (1886)
was describing "Leydig's dotted substance" = **neuropil** (neuronal *and* glial
processes). Verified, von Bartheld et al. 2016, Table 5.

---

## 3. The resting membrane potential

### 3.1 Nernst

E_X = (RT / z_X F) · ln([X]_out / [X]_in)

At 37 °C, z = +1: ≈ **61.5 mV per decade**. At ~20 °C and as used in the squid work:
**58 mV per decade** (verified in Hodgkin & Katz 1949's printed text).

⚠️ Nernst's 1888/1889 *Zeitschrift für physikalische Chemie* originals were **not
opened** (German, not reachable). Do not attach a DOI to "Nernst 1888."

### 3.2 Goldman–Hodgkin–Katz, verbatim from the printed page

Hodgkin & Katz 1949, *J Physiol* 108:66, equation (4), read off the page scan:

```
E = (RT/F) · ln[ ( P_K (K)_i + P_Na (Na)_i + P_Cl (Cl)_o )
                /( P_K (K)_o + P_Na (Na)_o + P_Cl (Cl)_i ) ]
```

Same paragraph, verbatim: *"E is the potential difference across the membrane
**(outside − inside)** in the absence of any net ionic current."*

**Note the orientation:** outside minus inside. Modern texts write inside minus
outside, which flips the sign. And the Cl terms are inverted relative to the cations
because Cl⁻ is an anion.

Their adopted internal concentrations: (K)ᵢ = 345 mM, (Na)ᵢ = 72 mM, (Cl)ᵢ = 61 mM.

Their fitted permeability ratios:

| State | P_K : P_Na : P_Cl |
|---|---|
| Resting | 1 : 0.04 : 0.45 — **and they give a second fit**, 1 : 0.025 : 0.3, saying *"rather different values are needed to cover"* the full range |
| Active | 1 : 20 : 0.45 |

> The **500-fold swing in P_Na/P_K** between rest and peak *is* the action potential,
> stated in 1949 language, three years before the HH model.

**Hodgkin & Katz's own caveat on GHK**, verbatim, same page:

> *"There are many reasons for supposing that this equation is no more than a rough
> approximation, and it clearly cannot give exact results if ions enter into chemical
> combination with carrier molecules in the membrane or if appreciable quantities of
> current are transported by ions other than K, Na or Cl."*

They defend it on two grounds only: *"it is extremely simple"* and that it reduces to
thermodynamically correct forms in the single-permeant limit.

Goldman's own 1943 paper (*J Gen Physiol* 27(1):37–60, PMC2142582) was fetched and
read, but the scanned equation displays are OCR-illegible. What is confirmable from
the prose: it rests on **the constant field assumption**, contrasted explicitly with
*"the Planck equation."* ⚠️ The modern printed **GHK current** equation was not
transcribed from Goldman's page — treat as textbook-standard, source-not-read.

### 3.3 The Na⁺/K⁺-ATPase

Stoichiometry **3 Na⁺ out : 2 K⁺ in : 1 ATP**. ⚠️ The primary citations (Post & Jolly
1957; Sen & Post 1964; Thomas 1972) are bibliographically verified but **bodies
unread** — which paper established which part is not checked here.

The consequence is worth stating because ML models have no analogue: **3:2 makes the
pump electrogenic** (net +1 charge out per cycle), so it contributes a few mV to
V_rest directly, and **the resting potential is not an equilibrium but a steady state
maintained by continuous ATP expenditure.**

### 3.4 V_rest — the one real primary measurement

Squid giant axon, Hodgkin & Katz 1949: **mean resting potential 48 mV** (inside
negative); Curtis & Cole's value **51 mV**. The same paper records a disagreement it
does not resolve: HK found spikes rarely >100 mV at 18–23 °C, while *"Curtis & Cole
describe a spike as large as 168 mV in a fibre which gave a resting potential of
58 mV. The matter … has far-reaching implications."* **Sources disagree; recorded, not
reconciled.**

⚠️ **"V_rest = −70 mV" is a textbook convention, not a squid-axon measurement.** The
HH model has no absolute resting potential at all — V is *displacement* from rest —
and HH themselves said the isolated axon's resting potential is depressed relative to
the living animal.

⚠️ Every specific non-axon V_rest commonly quoted (cerebellar granule ≈ −80 mV,
dopaminergic ≈ −55 mV, rod photoreceptor ≈ −40 mV in darkness, hair cells −55 to
−70 mV) is **recollection only** here; a primary for the photoreceptor dark potential
was searched for and **none** was readable. The Allen Cell Types Database holds
per-cell patch-clamp V_rest for human and mouse, but ⚠️ its landing page gives **no
version string, no release date and no cell counts** — cite a specific dataset
release, not the portal. The matching publication (Gouwens et al., *Nat Neurosci*
2019;22(7):1182–95) reports 1,938 neurons with intrinsic ephys, 461 with morphology,
452 with both, and 17/38/46 ephys/morphological/morpho-electric types — but **does not
publish a V_rest distribution in the abstract.** To get the spread you must pull the
database.

---

## 4. Hodgkin & Huxley 1952 — what the papers actually say

### 4.1 "The five" are five *J Physiol* papers, and there are two more

| # | Paper | Identifiers | Read? |
|---|---|---|---|
| I | Hodgkin, Huxley **& Katz**, "Measurement of current-voltage relations…" *J Physiol* 116(4):424–448 | PMC1392219 | ✅ PDF |
| II | Hodgkin & Huxley, "Currents carried by sodium and potassium ions…" 116(4):449–472 | PMC1392213 | citation only |
| III | "The components of membrane conductance…" 116(4):473–496 | PMC1392209 | citation only |
| IV | "The dual effect of membrane potential on sodium conductance…" 116(4):497–506 | PMC1392212 | citation only |
| V | "A quantitative description of membrane current…" 117(4):500–544 | PMC1392413 | ✅ PDF **+ page images of pp. 519–520** |

Two 1952 HH items usually omitted from "the five": *Proc R Soc Lond B*
140(899):177–183 (propagation), and *Cold Spring Harb Symp Quant Biol* 17:43–52 (ion
movements). **Say "the five *J Physiol* 1952 papers," not "the five 1952 papers."**

### 4.2 HH did not invent the voltage clamp, and say so in their first paragraph

> *"The experimental method was based on that of **Cole (1949) and Marmont (1949)**,
> and consisted in measuring the flow of current through a definite area of the
> membrane of a giant axon from Loligo, when the membrane potential was kept uniform
> over this area and was changed in a stepwise manner by a feed-back amplifier."*

Verified, paper (I), p.424.

### 4.3 The sign convention is inverted

From paper (V), p.505, verbatim:

> *"I is the total membrane current density (**inward current positive**); I_i is the
> ionic current density (inward current positive); V is the displacement of the
> membrane potential from its resting value (**depolarization negative**); C_M is the
> membrane capacity per unit area (assumed constant)."*

**Type the original numbers into a modern-convention simulator and you get a dead
axon.**

### 4.4 The equation set, as printed

```
(1)   I   = C_M dV/dt + I_i
(2)   I_i = I_Na + I_K + I_l
(3)   I_Na = g_Na (V − V_Na);  I_K = g_K (V − V_K);  I_l = g_l (V − V_l)

(26)  I = C_M dV/dt + ḡ_K n⁴ (V − V_K) + ḡ_Na m³h (V − V_Na) + g_l (V − V_l)

(7)   dn/dt = α_n(1 − n) − β_n n
(15)  dm/dt = α_m(1 − m) − β_m m
(16)  dh/dt = α_h(1 − h) − β_h h
```

Rate functions, transcribed from the page-519 image:

```
(12)  α_n = 0.01 (V + 10) / ( exp((V + 10)/10) − 1 )
(13)  β_n = 0.125 exp(V/80)
(20)  α_m = 0.1 (V + 25) / ( exp((V + 25)/10) − 1 )
(21)  β_m = 4 exp(V/18)
(23)  α_h = 0.07 exp(V/20)
(24)  β_h = 1 / ( exp((V + 30)/10) + 1 )
```

Units and temperature, verbatim p.519: *"Potentials are given in mV, current density
in µA/cm², conductances in m.mho/cm², capacity in µF/cm², and time in msec. The
expressions for the α's and β's are appropriate to a temperature of **6.3 °C**; for
other temperatures they must be scaled with a **Q₁₀ of 3**."* And: *"The constants in
eqn. (26) are taken as independent of temperature."*

### 4.5 Table 3 (p.520) read off the page scan — and the two "parameters" that are not measurements

| Constant | Value chosen | Experimental mean | Experimental range |
|---|---|---|---|
| C_M (µF/cm²) | 1.0 | 0.91 | 0.8 – 1.5 |
| V_Na (mV) | **−115** | −109 | −95 to −119 |
| V_K (mV) | **+12** | +11 | +9 to +14 |
| V_l (mV) | **−10.613** * | −11 | **−4 to −22** |
| ḡ_Na (m.mho/cm²) | **120** | **80 / 160** † | 65–90 / 120–260 |
| ḡ_K (m.mho/cm²) | 36 | 34 | 26 – 49 |
| g_l (m.mho/cm²) | 0.3 | 0.26 | 0.13 – 0.50 |

HH's own footnotes, verbatim:
\* *"Exact value chosen to make the total ionic current zero at the resting potential
(V = 0)."*
† *"The experimental values for ḡ_Na were obtained by multiplying the peak sodium
conductances by factors derived from the values chosen for α_m, β_m, α_h, and β_h."*

**Three things get laundered out of that table:**

1. **ḡ_Na = 120 is a *chosen* value.** The experimental means were 80 **and** 160 depending on the subset, with ranges 65–90 and 120–260. The "parameter" is a judgement call inside a 4-fold spread.
2. **V_l = −10.613 mV is not a measurement.** It is *solved for*, to zero the resting current — and printed to three decimals against an experimental mean of "−11" with a range from −4 to −22.
3. **The ḡ_Na experimental values are themselves model-dependent**, back-computed using the fitted α/β functions. Circular — and HH flag it in the footnote.

⚠️ The modern-convention rewrite (E_Na = +50, E_K = −77, E_L = −54.4, V_rest = −65 mV)
is arithmetically consistent with the originals, but **who first published the inverted
form, and whether −54.4 is derived the same way as −10.613, was not traced. Do not
present the modern set as "Hodgkin and Huxley's values."**

### 4.6 What HH claimed — and explicitly refused to claim

Verbatim, p.541:

> *"The agreement must not be taken as evidence that our equations are anything more
> than an empirical description of the time-course of the changes in permeability to
> sodium and potassium. An equally satisfactory description of the voltage clamp data
> could no doubt have been achieved with equations of very different form, which would
> probably have been equally successful in predicting the electrical behaviour of the
> membrane. … **the success of the equations is no evidence in favour of the mechanism
> of permeability change that we tentatively had in mind** when formulating them."*
>
> *"The point that we do consider to be established is that fairly simple permeability
> changes in response to alterations in membrane potential … are a **sufficient
> explanation** of the wide range of phenomena that have been fitted by solutions of
> the equations."*

And on scope: *"they cover only the short-term responses of the membrane, and … they
apply in their present form **only to the isolated squid giant axon**."* *"Our
equations give no account of after-potentials, apart from the positive phase and
subsequent oscillations."*

> **m³h and n⁴ are curve shapes**, chosen because (1−e⁻ᵗ)⁴ gives the observed inflected
> rise and e⁻⁴ᵗ the simple exponential fall. The "four gating particles" / "three gates
> plus an inactivation gate" story is a physical interpretation HH offered and then
> declined to defend, in as many words.

### 4.7 Threshold is not a voltage

HH 1952, p.535. Calculated just-threshold low point *"about 6 mV"*; experimental
*"about 8 mV."* Then immediately: *"the value for the calculated series must depend
critically on such things as the leak conductance, whose value was not very well
determined experimentally."* And: *"the experimental value in the series at 23 °C … is
about **15 mV**. However, this fibre had been stored for 5 hr before use."*

On why threshold moves:

> *"During the positive phase which follows each calculated subthreshold response, the
> potassium conductance is raised and there is a higher degree of 'inactivation' than
> in the resting state. The threshold must therefore be raised in the same way as it is
> during the relative refractory period following a spike."*

> **Three different threshold numbers in one paper** (6, 8, ~15 mV), differing by
> temperature and tissue condition, and the paper derives threshold's state-dependence
> from h and n. Threshold is a **moving boundary in a 4-dimensional state space**
> (V, m, h, n) — not a parameter. **There is no threshold voltage in the HH
> equations.** ⚠️ (The dynamical-systems framing of that boundary as a separatrix is
> standard but no primary was verified for it.)

### 4.8 All-or-none is about the spike, not the membrane

Nothing in eqn (26) is discrete. HH's own summary of what the equations account for
includes *"(f) The existence and form of **subthreshold responses**."*

> **Subthreshold responses exist and are graded.** The neuron is an analogue device with
> one regenerative output mode.

### 4.9 Refractory periods

HH 1952, p.534 and Fig. 20: *"membrane potential falls again with hardly a sign of
activity, and the membrane can be said to be in the 'absolute refractory period'. The
later stimuli produce action potentials of increasing amplitude, but still smaller than
the control; these are in the 'relative refractory period'. … The agreement is good, as
regards both the duration of the absolute refractory period and the changes in shape of
the spike as recovery progresses."*

Mechanism: absolute = h still low (Na inactivation unrecovered); relative = h partly
recovered plus n still elevated. ⚠️ HH give this reasoning verbatim for *subthreshold*
responses; applying it to the refractory period is the standard reading, not a direct
quotation.

⚠️ **Absolute durations in ms are unverified.** The printed figures are at 6–9 °C with
Q₁₀ = 3. Any "1–2 ms absolute refractory period" you have heard is a mammalian-at-37 °C
number from a source not read here.

### 4.10 Propagation — and the canonical model's actual accuracy

HH eqn (34): **θ = √( K a / (2 R₂ C_m) )**

Their worked case (a = 238 µm, R₂ = 35.4 Ω·cm, C_m = 1.0 µF/cm², K = 10470):

- **calculated 18.8 m/s**
- **measured on the same fibre 21.2 m/s**

> An **11% miss**, on the same fibre, with every parameter measured on that fibre. That
> is the accuracy of the canonical model on its own preparation. Note the **√a**
> scaling: in an unmyelinated cable, velocity goes as the square root of radius.

### 4.11 Saltatory conduction is not in HH 1952

The squid axon is unmyelinated. Myelinated conduction scales approximately **linearly**
with diameter rather than as √diameter — which is the point of myelin. ⚠️ The primary
for the linear relation (Hursh, *Am J Physiol* 1939;127(1):131–139) is
Crossref-confirmed but **unread**, so the commonly quoted "velocity ≈ 6 × diameter"
attributed to Hursh is **unverified here**.

---

## 5. The famous numbers, checked

### 5.1 86 billion, and why "100 billion" is folklore

Azevedo et al., "Equal numbers of neuronal and nonneuronal cells make the human brain
an **isometrically** scaled-up primate brain," *J Comp Neurol* 2009;513(5):532–541,
doi:10.1002/cne.21974. ⚠️ **Not in PMC; full text paywalled and not read.** (Note the
title: *isometrically*, not "isotropically" — the isotropic *fractionator* is the
method.)

Verified from the abstract:

> *"the adult male human brain contains on average **86.1 ± 8.1 billion** NeuN-positive
> cells ('neurons') and **84.6 ± 9.8 billion** NeuN-negative ('nonneuronal') cells."*
>
> *"With only **19% of all neurons located in the cerebral cortex**, greater cortical
> size (representing 82% of total brain mass) in humans compared with other primates
> does not reflect an increased relative number of cortical neurons."*

**Note the authors' own scare quotes** around 'neurons' and 'nonneuronal'. The
measurement is NeuN immunoreactivity, not neuronhood.

Regional breakdown (Herculano-Houzel 2009, Table 2, reporting Azevedo et al.):

| | Mass | Neurons |
|---|---|---|
| Whole brain | 1508 g | 86 bn (+ 85 bn non-neuronal) |
| Cerebral cortex | 1233 g (82% of mass) | **16 bn (19% of neurons)** |
| Cerebellum | 154 g (10% of mass) | **69 bn** |

**Where did "100 billion" come from? Nowhere traceable.** Herculano-Houzel 2009,
verbatim:

> *"Many original articles, reviews and textbooks affirm that we have 100 billion
> neurons and 10 times more glial cells …, usually with no references cited."*
>
> *"an informal survey with senior neuroscientists that we ran in 2007 showed that most
> believed that the number of cells in the human brain was indeed already known … but
> **none of the consulted scientists could cite an original reference for these
> numbers**."*
>
> *"the ubiquitous quote of 100 billion neurons (a value that **lies outside of the
> margin of variation found so far in human brains**)."*

The folklore's own history is of a defensible order-of-magnitude estimate losing its
error bars. Hubel (1979): *"The number of nerve cells … is on the order of 10¹¹ (a
hundred billion) **give or take a factor of 10**."* And of 23 authors surveyed by von
Bartheld et al., **two texts say one *trillion* neurons** (Kandel & Schwartz 1981,
1985) *"and the authors did not correct this mistake for neuron numbers until
subsequent editions."*

⚠️ **The sample size of the headline number of modern neuroscience is unstated in
anything readable.** The abstract says "adult male human brain … on average" with no n;
the full text is paywalled. The commonly cited "n = 4, aged 50–71" is **recollection
only — do not state n.**

**The isotropic fractionator's own stated limits** (von Bartheld et al. 2016): NeuN
*"does not identify cell types among the non-neuronal cells"*; *"NeuN antigens are not
expressed by a small number of neuronal populations"* (so **Purkinje cells and other
NeuN-negative neurons are systematically missed**); *"only regions and volumes of
tissues that can be dissected macroscopically can be analyzed"*; and a long-standing
concern about *"loss of nuclei when using a biochemical homogenization approach."*
**Endothelial cells are 10–20% of "non-neuronal" cells in white matter and ~30% in
cortical grey matter** — so the "glia" number in a 1:1 glia:neuron claim is already
~20–30% not-glia.

### 5.2 The 10:1 glia:neuron ratio is refuted — and was always arithmetically incoherent

von Bartheld, Bahney & Herculano-Houzel, "The search for true numbers of neurons and
glial cells in the human brain: A review of 150 years of cell counting," *J Comp
Neurol* 2016;524(18), PMC5063692 (full text read). Abstract, verbatim:

> *"For half a century, the human brain was believed to contain about 100 billion
> neurons and one trillion glial cells, with a glia:neuron ratio of 10:1. … The
> recently validated isotropic fractionator demonstrates a glia:neuron ratio of **less
> than 1:1** and a total number of **less than 100 billion glial cells** … histological
> data **always supported a 1:1 ratio** … and a range of 40–130 billion glial cells."*

**The contradiction that should have been caught**, verbatim:

> *"Maximally 130 billion glia with a 10:1 GNR could not be true, because that would
> **cap the total number of neurons at 13 billion**, but there were 10–16 billion
> neurons in cerebral cortex alone, plus at least 10 billion neurons in cerebellar
> cortex (granule neurons alone) … This should have been a warning signal — that the
> GNR could not exceed 6.5:1."*

**Their diagnosis of why it survived:**

> *"the main reason for the origin and persistence of the notion of one trillion glial
> cells was not the technical disadvantage of the … counting methods … but rather the
> **failure to notice that published numbers for all three components** … contradicted
> each other … Major textbooks consistently presented the notion as a well-established
> fact, thereby **allowing circumvention of the normal mechanisms** of review."*

**And there is no "the" glia:neuron ratio.** It spans ~3 orders of magnitude:

| Structure | Glia:neuron |
|---|---|
| Cerebellum | ≤ 0.23 (possibly ~0.05) |
| Cortex + cerebellum together | 0.8 – 0.9 |
| Cortex grey matter | ~1.5 |
| Striatum | 3.7 |
| Superior colliculus | ~10 |
| Ventral pallidum | 12.2 |
| Dorsomedial thalamic nucleus | 17 |
| Lateral vestibular nucleus | ~30–50 |
| **Globus pallidus** | **~160** |

Why it is not a biological constant, verbatim: *"glial cell densities remain remarkably
constant between species and even brain structures, at 50,000–130,000 cells per mm³,
while **neuronal densities** in different parts of the human brain **vary between 0 and
over 400,000 per mm³** … Accordingly, the GNR largely reflects differences in neuronal
density."* **The ratio is a neuronal-density readout.**

Only five publications ever reported a whole-brain GNR of 0.7:1–1:1 (Haug 1986; Azevedo
2009; Andrade-Moraes 2013; Streit 2013; Verkhratsky & Butt 2013). Everyone else said
10:1 or higher. **The majority were wrong.** Haug had it right in 1986 and *"does not
appear to have made any efforts to refute the prevailing numbers."*

⚠️ **Sources disagree ~5× on cerebellar glia** (3 bn, Andersen stereology, vs 16 bn,
isotropic fractionator) because the IF non-neuronal count includes endothelial cells.
Recorded, not reconciled.

### 5.3 "~10⁴ synapses per neuron" — and the total synapse count that may not have a source

**Mouse cortex, direct count:** synapses per neuron *"concentrated in the **6,500–9,500
range**"* across cortical sites. Verified, Ventura-Antunes & Herculano-Houzel, *Front
Integr Neurosci* 2022;16:760887, PMC9465999 (full text). Remarkably tight — a 1.5-fold
range — even though neuronal densities vary 2.2-fold. Their other findings: synapses
per neuron is **not** higher where there are more synapses, **not** correlated with
local glia per neuron, and *"the higher the local glial cell density, the fewer the
synapses per glial cell."*

**Human cortex, synapse density per volume** (FIB/SEM volume EM, layer III;
Cano-Astorga et al., *Cereb Cortex* 2024;34(8):bhae312, PMC11302151, full text):

| Area | Synapses/µm³ |
|---|---|
| BA17 (primary visual) | 0.45 (0.38–0.57 across cases) |
| BA3b (primary somatosensory) | 0.44 ± 0.11 |
| BA4 (primary motor) | **0.28 ± 0.04 — the lowest** |
| dorsal BA38 | **0.76 — the highest** |

Asymmetric : symmetric (excitatory : inhibitory proxy): **92:8 in BA4, 93:7 in BA3b,
94:6 in BA17**, with no significant difference between regions. Intersynaptic distance
843–946 nm. 9,690 synapses reconstructed.

⚠️ **Method-dependence from the same group:** layer III human temporal neocortex gave
**0.49 vs 0.66 synapses/µm³ for autopsy vs biopsy** samples — **the tissue source
changes the answer by 35%.**

**What it varies with:** cortical area (2.7× across human areas), tissue source (1.35×),
cell type (Purkinje ~1.75×10⁵ vs cortical pyramidal ~10⁴, i.e. **>10×**), species, and
layer. *"10⁴ synapses per neuron" is a defensible order of magnitude for a mouse
cortical neuron and is off by more than 10× for a Purkinje cell. There is no single
number.*

⚠️ **The total human cortical synapse count (the "10¹⁴–10¹⁵" figure) is unverified and
the paper people cite for it may not exist as stated.** A Europe PMC search for the
usual title ("Aggregate number of synapses in the human cerebral cortex") returned
**zero hits**. The one accessible modelling paper (Nowinski, *PLoS One* 2024,
PMC11423976) **assumes** three cases of synapses per neuron (1,000; 10,000; 30,000)
rather than measuring. **Do not cite it as a measurement.**

⚠️ **"Pyramidal cells are 70–80% of cortical neurons" is textbook-asserted with no
primary citation** found here.

**Peters' rule fails in dense EM.** Mishchenko et al., *Neuron* 2010;67(6):1009–20,
PMC3215280 (abstract): *"in contrast with Peters' rule, the density of axons within
reach of dendritic spines did not predict synaptic density along dendrites"*; *"an
axo-dendritic touch did not predict a synapse"*; synapse density was *"a universal
fraction, **0.2**, of the density of touches."* Largest bouton–spine touch indicated a
real synapse with ~80% precision *"but would miss about half of all synapses."*
**Connectomics from proximity alone systematically miscounts.**

### 5.4 Conduction velocities — the most commonly fabricated-citation table in the field

The Erlanger–Gasser classification attribution is verified (via Sonawane et al.,
*Cureus* 2023;15(7):e41771 — used **only** for the attribution). Its primaries
(Erlanger & Gasser, *Am J Physiol* 1930;92(1):43–82; *Electrical Signs of Nervous
Activity*, 1937; Lloyd, *J Neurophysiol* 1943;6(4):293–315 for the Roman-numeral muscle-
afferent scheme) are **Crossref-confirmed and unread**.

⚠️ **The full table (Aα 70–120, Aβ 30–70, Aγ 15–30, Aδ 5–30, B 3–15, C 0.5–2 m/s) is
unverified. Do not ship it with a citation.** No primary, and not even a readable
secondary table, was obtained.

**And two readable sources disagree on the top speed:** the Sonawane review says *"up to
**120 m/s**"* (itself citing a textbook with no primary), while McCulloch & Pitts 1943
state *"from < 1 ms⁻¹ in thin axons … to **> 150 ms⁻¹** in thick axons."* Note also that
MP say velocity varies **directly** with diameter — the *myelinated* relation, applied
without qualification.

Calibration point that *is* verified: **21.2 m/s measured / 18.8 m/s calculated for an
unmyelinated squid axon of ~0.5 mm diameter.** ⚠️ The engineering comparison usually
drawn here ("a 20 µm myelinated mammalian fibre beats a 500 µm unmyelinated squid
axon") needs the unread Hursh relation — only the squid half is verified.

### 5.5 Firing rates are lognormal, sparse, and mostly silent

**Hippocampus/entorhinal cortex, freely moving rat** (Mizuseki & Buzsáki, *Cell Rep*
2013;4(5):1010–21, PMC3804159, full text):

- *"firing rates of principal neurons showed a **lognormal-like distribution** in all brain states"*
- *"a **three orders of magnitude** range of the mean firing rates from 0.001 Hz to 10 Hz"*
- proportion firing >2 Hz: **RUN 12.3%, REM 6.0%, IMM 7.1%, SWS 5.7%**
- *"during RUN, **70.4%** of the recorded CA1 pyramidal cells had a mean rate <1 Hz, whereas a small fraction of strongly active pyramidal cells (**13.3%**) contributed to **50% of all spikes**"*
- rates correlate across brain states, testing situations, and familiar vs novel environments → *"a **preconfigured highly active minority** dominates information transmission"*

**Auditory cortex, awake rat, cell-attached** — and the method matters, because *"single-
unit isolation does not depend on neuronal activity"* (Hromádka, DeWeese & Zador, *PLoS
Biol* 2008;6(1):e16, PMC2214813, abstract):

- *"the population response is sparse, with stimuli typically eliciting high firing rates (>20 spikes/second) in **less than 5% of neurons** at any instant"*
- *"Some neurons had very low spontaneous firing rates (<0.01 spikes/second)"*; others *"in excess of 50 spikes/second"*
- *"well described by a **lognormal** distribution, rather than the exponential distribution that is often reported"*

**Barrel cortex, mice localising objects** (O'Connor et al., *Neuron* 2010;67(6):1048–61,
abstract): *"Spike rates varied across neurons, from **silence to >60 Hz**"*;
*"Approximately **13,000 spikes per activated barrel column** were available to mice for
decision making. Coding of object location in the barrel cortex is therefore **highly
redundant**."*

**The general claim** (Buzsáki & Mizuseki, "The log-dynamic brain," *Nat Rev Neurosci*
2014;15(4):264–78, PMC4051294, full text): rates *"span at least four orders of
magnitude"* with a *"long-tailed, typically lognormal"* distribution, creating *"a rate
spectrum with a wide dynamic range, spanning from vast numbers of very slow-firing
neurons to a small fraction of fast-firing 'champion' cells."* Their practical note:
*"a tenfold change in evoked firing of individual neurons is usually considered to be a
large effect but it is **only a single unit on the log scale**."*

**The methodological point is the point.** Shoham, O'Connor & Segev, "How silent is the
brain: is there a 'dark matter' problem in neuroscience?" *J Comp Physiol A*
2006;192(8):777–84 (⚠️ paywalled, abstract only): neurons that *"fire action potentials
rarely or only to very specific stimuli … would be difficult to detect with the most
common method of monitoring neural activity in vivo — extracellular electrode
recording"*, hence *"dark neurons."*

> Extracellular spike sorting finds units **by** their spikes. A neuron that never
> spikes is invisible. **Every "mean cortical firing rate" from extracellular recording
> is conditioned on being detectable, i.e. upward-biased by construction.** This is why
> cell-attached and imaging methods matter — they sample independent of activity, and
> they find the silence.

### 5.6 "The brain runs on 20 W" has no primary source in watts

| Step | What it actually says |
|---|---|
| **The primary measurement** — Kety & Schmidt, *J Clin Invest* 1948;27(4):476–483, PMC439518 (PDF read) | *"the mean value for cerebral blood flow was **54 (σ = ±12) cc./100 g./min**. The mean value for cerebral oxygen consumption was **3.3 (σ = ±0.4) cc. O₂/100 g./min**."* From >300 determinations, *"the only quantitative study yet reported of blood flow and metabolism in the normal human brain."* Note the **22% CV** on flow, 12% on oxygen. |
| **The percentage claim** — Raichle & Gusnard, *PNAS* 2002;99(16):10237–9, PMC124895 (full text read) | *"the brain represents about 2% of the body weight … [yet] accounts for about **20% of the oxygen** and, hence, calories consumed by the body (1)."* ⚠️ **Their reference (1) is a textbook chapter** (Clark & Sokoloff in *Basic Neurochemistry*, 1999, pp. 637–670) **which was not read.** The 20%-of-body-oxygen figure is textbook-asserted at one remove. |
| **Watts** — derived, not published | 1400 g × 3.3 mL O₂/100 g/min = 46.2 mL O₂/min × 20.1 J/mL O₂ = **≈15.5 W**. |

> **The 20 W is ~30% higher than the oxygen route gives.** The discrepancy is tractable:
> the **glucose** route (⚠️ CMR_glc ~31 µmol/100 g/min, textbook-asserted and unverified)
> gives ~20 W because not all glucose taken up is fully oxidised. **State the
> measurement — mL O₂/100 g/min — not the watts.**

Also verbatim from Raichle & Gusnard, and the more interesting claim: *"Attempts to
measure whole brain changes in blood flow and metabolism during intense mental activity
have **failed to demonstrate any change**."* And during local activation, *"blood flow
and glucose utilization increase more than oxygen consumption"* — the basis of the BOLD
signal.

**Where the energy goes — and the 2001 budget was superseded by its own senior author.**

Attwell & Laughlin, *J Cereb Blood Flow Metab* 2001;21(10):1133–45 (⚠️ abstract only;
paywalled, not in PMC): action potentials 47%, postsynaptic glutamate effects 34%,
resting potential 13%, glutamate recycling 3%; *"an increase in activity of 1 action
potential/cortical neuron/s will raise oxygen consumption by 145 mL/100 g grey
matter/h"*; and they predict *"the use of distributed codes, with ≤15% of neurons
simultaneously active, to reduce energy consumption."*

⚠️ **This is a *budget* — a calculation from anatomical and physiological assumptions,
not a measurement of each term — and it is rodent grey matter.** Because the full text
is paywalled, the assumptions behind it (notably Na⁺ entry per action potential) are
**not checked here**.

**Howarth, Gleeson & Attwell 2012 (PMC3390818) exists because the 2001 spike cost was an
overestimate.** Revised cortical signalling budget: **postsynaptic glutamate receptors
50%, action potentials 21%, resting potentials 20%**, presynaptic release 5%, recycling
4%.

> **The expensive thing is receiving, not sending** — which undercuts the usual energy
> argument for sparse *spiking*.

⚠️ **"ATP per action potential" is unsettled by four to five orders of magnitude**
(~3,000 to 10¹⁰ across two secondary readings of the *same* primary paper), and neither
states whether the denominator is per synapse or per neuron. **Never quote it without
the denominator.**

Energy availability is also **spatially shared**: *"it is not that larger neurons,
neurons with more synapses, or even sites with more synapses demand more energy, but
simply that larger neurons (in low density sites) have more energy available per cell"*
— capillary density, not the neuron's own synapse count, sets the budget
(Ventura-Antunes & Herculano-Houzel 2022, verified full text).

---

## 6. "The neuron" is a fiction — demonstrated, not asserted

**The count problem, stated by the people doing the counting** (BICCN, *Nature*
2021;598:86–102, PMC8494634, full text):

> *"The notion of a 'neuron type', with similar properties among its members, as the
> basic unit of brain circuits has been an important concept for over a century;
> however, **rigorous and quantitative definitions have remained surprisingly
> elusive**."*

**Petilla terminology (2008)** — *Nat Rev Neurosci* 9(7):557–68, PMC2868386. 36 authors
convened *"to agree on a set of terms to describe the anatomical, physiological and
molecular features of GABAergic interneurons"*, producing what they themselves call
*"a stepping stone towards a future classification."* **It is a controlled vocabulary
for features, not a classification and not a count.** The field could not agree on
words, let alone types.

**The transcriptomic censuses — and the method-dependence:**

| Study | Date | Counts |
|---|---|---|
| BICCN mouse primary motor cortex, *Nature* 598:86–102, PMC8494634 | online 6 Oct 2021 | **116** total clusters (90 neuronal) by snRNA-seq — and in one figure legend, the *same* cortical area gives **95** (MERFISH), **71** (LIGER), **56** (SingleCellFusion, neuronal), plus **127** human and **94** marmoset |
| Siletti et al., whole adult human brain, *Science* 382:eadd7046 | online 13 Oct 2023 | **461 clusters and 3,313 subclusters** from >3 million nuclei, ~100 dissections, **three** postmortem donors. ⚠️ The record itself flags that these are clusters, *"not a count of cell types."* |
| Yao et al., whole mouse brain, *Nature* 624:317–332, PMC10719114 | online 13 Dec 2023 | **34 classes / 338 subclasses / 1,201 supertypes / 5,322 clusters** — ⚠️ but the **bioRxiv preprint of the same study gave 7 divisions / 32 / 306 / 1,045 / 5,200.** The "number of cell types in the mouse brain" moved by 2 classes, 32 subclasses, 156 supertypes and 122 clusters **between preprint and publication, in nine months.** |

**The assembled case:**

1. There is no agreed definition of a neuron type (BICCN 2021).
2. The count depends on the **modality**: 116 / 95 / 71 / 56 for one cortical area in one paper.
3. The count depends on the **clustering run**: 5,200 → 5,322 between preprint and print.
4. The count depends on **where you cut the dendrogram**: 34 / 338 / 1,201 / 5,322 are all available in the same dataset.
5. Even the **feature vocabulary** had to be negotiated by a 36-author committee.
6. The **measuring instrument is blind to some neurons** — NeuN-negative populations are missed by the isotropic fractionator.
7. The same nominal cell class differs **between species in ways that are not a scale factor** (human astrocytes: ~10× more primary processes, 4× faster Ca²⁺ waves, subclasses with no rodent counterpart).
8. Within one acknowledged type, **firing rate spans 3–4 orders of magnitude** and is lognormal — i.e. there *is* no typical member.

> "A neuron" in a model is a choice of abstraction level with **no unique biological
> referent**. The honest statement: there are between 34 and 5,322 kinds of cell in a
> mouse brain depending on where you cut the dendrogram, and within any one kind the
> members differ by 1,000× in rate.

---

## 7. Where McCulloch–Pitts / the perceptron departs from biology

### 7.1 The two source papers, properly

- **McCulloch & Pitts**, "A logical calculus of the ideas immanent in nervous activity," *Bull Math Biophys* 1943;5(4):115–133, doi:10.1007/BF02478259. Read via the authorised reprint, *Bull Math Biol* 1990;52(1/2):99–115; all page numbers below are the reprint's.
- **Rosenblatt**, "The perceptron: A probabilistic model for information storage and organization in the brain," *Psychological Review* 1958;65(6):386–408, doi:10.1037/h0042519. Full text read.

### 7.2 The five assumptions, verbatim (p.101)

> *"(1) The activity of the neuron is an 'all-or-none' process.
> (2) A certain fixed number of synapses must be excited within the period of latent
> addition in order to excite a neuron at any time, and this number is independent of
> previous activity and position on the neuron.
> (3) The only significant delay within the nervous system is synaptic delay.
> (4) The activity of any inhibitory synapse absolutely prevents excitation of the
> neuron at that time.
> (5) The structure of the net does not change with time."*

**The McCulloch–Pitts neuron has no weights.** Its rule is a threshold on a *count* of
active inputs, with inhibition as an absolute veto. Real-valued weights and the weighted
algebraic sum arrive with **Rosenblatt 1958**. Calling a weighted-sum-plus-nonlinearity
unit "a McCulloch–Pitts neuron" is historically wrong.

### 7.3 They enumerated the biology and then proved it immaterial

This is why "MP didn't know about X" is almost always wrong. They state as known
physiology (pp. 99–100): the period of latent addition (~0.25 ms); synaptic delay
(>0.5 ms); and the full excitability cycle — *"During the first part of the nervous
impulse the neuron is absolutely refractory to any stimulation. Thereafter its
excitability returns rapidly, in some cases reaching a value above normal from which it
sinks again to a subnormal value … **Frequent activity augments this subnormality**."*
(Absolute + relative refractory period, supernormal and subnormal phases, and
spike-frequency adaptation — all named, then dropped.) And: *"As yet experiment has not
shown whether the refractoriness is relative or absolute. We will assume the latter and
**demonstrate that the difference is immaterial to our argument**."*

On what they could not model (pp. 100–101), verbatim:

> *"Two difficulties appeared. The first concerns facilitation and extinction … The
> second concerns learning … But for nets undergoing both alterations, we can substitute
> equivalent fictitious nets composed of neurons whose connections and thresholds are
> unaltered. **But one point must be made clear: neither of us conceives the formal
> equivalence to be a factual explanation. Per contra!** — we regard facilitation and
> extinction as dependent upon continuous changes in threshold related to electrical and
> chemical variables … and learning as an enduring change which can survive sleep,
> anaesthesia, convulsions and coma."*

Their equivalence theorems (pp. 107–108, verbatim headings):

| | |
|---|---|
| **Theorem 4** | *"Relative and absolute inhibition are equivalent in the extended sense."* |
| **Theorem 5** | *"Extinction is equivalent to absolute inhibition."* |
| **Theorem 6** | *"Facilitation and temporal summation may be replaced by spatial summation."* |
| **Theorem 7** | *"Alterable synapses can be replaced by circles."* |

Their learning mechanism is Hebbian *avant la lettre*: *"We suppose that some axonal
terminations cannot at first excite the succeeding neuron; but if at any time the neuron
fires, and the axonal terminations are simultaneously excited, they become synapses of
the ordinary kind."*

> **The correct critique is not "they ignored biology."** It is that they *enumerated*
> the biology and then argued, by equivalence theorems over propositional logic, that
> all of it was computationally immaterial. **The theorems are correct about
> expressiveness and silent about efficiency, learning dynamics, energy and
> robustness. Everything modern ML cares about lives in the gap their theorems leave
> open.**

**And quote both halves of their claim together.** At its most expansive (pp. 113–114):
*"a psychon can be no less than the activity of a single neuron. Since that activity is
inherently propositional, all psychic events have an intentional, or 'semiotic,'
character … **Thus both the formal and the final aspects of that activity which we are
wont to call mental are rigorously deduceable from present neurophysiology**."* A very
strong claim about mind, resting on an explicitly provisional claim about neurons.

### 7.4 Rosenblatt named the biological failures five years before Minsky & Papert

Verbatim, p.388:

> *"The models which have been produced all fail in some important respects (**absence
> of equipotentiality, lack of neuroeconomy, excessive specificity of connections and
> synchronization requirements, unrealistic specificity of stimuli sufficient for cell
> firing, postulation of variables or functional features with no known neurological
> correlates**, etc.) to correspond to a biological system."*

And on why he changed formalism: *"The need for a suitable language for the mathematical
analysis of events in systems where only the gross organization can be characterized …
has led the author to formulate the current model in terms of **probability theory
rather than symbolic logic**."* *"The theorists referred to above were chiefly concerned
with the question of how such functions as perception and recall **might** be achieved
by a deterministic physical system of any sort, rather than how this is **actually** done
by the brain."*

His unit rule (pp. 389–390): *"If the **algebraic sum** of excitatory and inhibitory
impulse intensities is equal to or greater than the threshold (θ) of the A-unit, then the
A-unit fires, again on an all-or-nothing basis (**or, in some models, which will not be
considered here, with a frequency which depends on the net value of the impulses
received**)."*

So Rosenblatt (i) introduced the weighted algebraic sum MP did not have, (ii) explicitly
set aside the rate-coded variant, (iii) named the lineage's biological failures, and
(iv) assumed **random** projection-to-association connectivity — a biological commitment
MP never made.

### 7.5 The itemized departures

| # | The abstraction | The biology | Status |
|---|---|---|---|
| 1 | **Binary (MP) or real-valued scalar (modern) output** | The spike is roughly all-or-none, but subthreshold responses are graded and functional; information is in spike times and rates over 4 decades; and ⚠️ human layer 2/3 dendrites generate **graded** Ca²⁺-mediated dendritic APs that *"let single dendrites classify linearly nonseparable inputs"* (Gidon et al., *Science* 2020;367:83–87 — **abstract only; verify the full text before leaning on this**) | mixed |
| 2 | **No time / no continuous dynamics** — MP has discrete synchronous ticks; a feedforward net has no time at all | A 4-dimensional continuous ODE system per compartment, with **temperature-dependent rates (Q₁₀ = 3)** — the same neuron computes differently at different temperatures. **No artificial unit has a Q₁₀.** | verified |
| 3 | **No refractoriness** — MP assumption (2) says firing is *"independent of previous activity"*, and they proved it away (Thm 5) | Absolute and relative refractory periods, mechanistically grounded in h and n. A biological neuron has a **hard maximum rate** and a **history-dependent threshold**; an artificial unit has neither. | verified |
| 4 | **Weights as deterministic scalars** (and MP has none at all) | Transmission is **quantal and probabilistic**; release probability is itself a variable under feedback control, differing between synapses on the same cell. A "weight" is a **point estimate standing in for a distribution whose mean and variance are both plastic.** | ⚠️ citations real (del Castillo & Katz 1954; Branco & Staras 2009), specific ranges unread here — see the synapses reference |
| 5 | **One summation node per cell** | Dendrites are compartmentalised subunits: inputs on the **same** thin branch sum **sigmoidally**, inputs on **different** branches sum **linearly** — *"supporting a two-layer model of dendritic integration"* (Polsky, Mel & Schiller, *Nat Neurosci* 2004). NMDA spikes in distal tuft dendrites are the main route by which distal input drives firing (Larkum et al., *Science* 2009). **A pyramidal neuron is better modelled as a two-layer network than as one unit.** | ⚠️ citations verified, findings from record abstracts only |
| 6 | **Inhibition as absolute veto (MP) or negative addend (everything since)** | A **conductance change**. Current is g·(V − E), so an inhibitory conductance's effect **depends on V**, which no additive weight can express. ⚠️ MP themselves considered both mechanisms and argued (Thm 4) the choice was immaterial — **for expressiveness it is; for gain control it is not.** | HH conductance form verified; the shunting literature not read here (see the synapses reference, where the usual divisive claim turns out to be **wrong as stated**) |
| 7 | **Sign-unstable weights** — backprop flips signs constantly | Transmitter identity, hence the sign of a cell's effect, is a property of the **presynaptic cell**, not the connection. E/I identity is a **cell type**, not a parameter: excitatory and inhibitory cells have distinct transcriptomes (BICCN 2021) and distinct synapse morphologies (asymmetric 92–94% : symmetric 6–8%, Cano-Astorga 2024). | ⚠️ **but "Dale's principle" is itself disputed in print** — one paper asks whether it is still valid, another says it is valid but useless, another reports dopamine/glutamate co-release from separate sites. Do **not** write "Dale's law says one neuron, one transmitter" as settled fact; that reading is described in this literature as a misattribution. See the circuits reference. |
| 8 | **No neuromodulation** — parameters are fixed during inference; no global state variable rescales gain, threshold or plasticity | MP assumption (2) says firing is independent of previous activity **and position on the neuron**. Both clauses are false, and neuromodulation falsifies the first on a timescale of seconds to minutes, globally, across millions of synapses at once. **No artificial net has an axis for this.** | ⚠️ the monoamine/ACh primaries not read in this section — see the synapses reference |
| 9 | **No delay structure** — a feedforward net has not even MP's one tick | Conduction velocity spans <1 to >150 m/s **by MP's own account**, and node/internode geometry varies 4.4–8.7-fold between axons with ~20% modelled speed effects, proposed as a mechanism for **tuning arrival times**. Delay is a **tuned, plastic variable** — not a constant and not zero. | verified |
| 10 | **No adaptation** | ⚠️ The AP **initiation site itself moves** during adaptation (Scott et al. 2014, unread). Adaptation is not a learned parameter; it is the cell's anatomy of excitability reconfiguring sub-second. | ⚠️ |
| 11 | **No stochasticity** — MP deterministic; Rosenblatt random in *connectivity* but deterministic in the unit rule | Quantal release is probabilistic; channels gate stochastically (HH's m, h, n are *population fractions* of a binomial ensemble, and HH did **not** model channel noise); firing is lognormal across cells and variable within them. **Rosenblatt made randomness architectural; biology makes it moment-to-moment.** | partly ⚠️ |
| 12 | **No energy constraint** — activating all units costs nothing | Signalling energy is dominated by postsynaptic glutamate receptors (50%) and spikes (21%) (Howarth et al. 2012), and firing rate drives consumption hard. Attwell & Laughlin's predicted *"distributed codes, with ≤15% of neurons simultaneously active"* is **independently borne out**: <5% of neurons above 20 spikes/s at any instant (Hromádka 2008), 70.4% of CA1 pyramids below 1 Hz during running (Mizuseki & Buzsáki 2013). | verified |
| 13 | **No glia** | Non-neuronal cells roughly **equal** neurons in number (84.6 vs 86.1 bn), with regional ratios from <0.1 to ~160, and a single human astrocyte domain spans ~270,000–2 million synapses. ⚠️ **Whether glia compute is open** — both camps are in print in the same 2018 journal issue and neither has conceded. State the gap as *"a cell population of comparable cardinality whose computational role is actively disputed,"* **not** as "networks omit the astrocyte's computational role." | verified cardinality, ⚠️ disputed role |
| 14 | **No structural change** — MP assumption (5) verbatim; modern nets fix topology and change weights | Synapses are formed and **eliminated**, ⚠️ including by a non-neuronal cell class acting on activity and complement cues (unread primaries). Spines appear and disappear. Node/internode geometry is adjustable, so **the delays are structurally plastic too.** MP's answer is Theorem 7 — which preserves expressiveness and says nothing about how a net could **find** the right structure, **which is the entire problem.** | mixed |
| 15 | **Weight symmetry** — backprop needs the transpose; Hopfield energy arguments need w_ij = w_ji | A chemical synapse is **unidirectional**, and MP said so in their first paragraph: *"Excitation across synapses occurs predominantly from axonal terminations to somata. It is still a moot point whether this depends upon irreciprocity of individual synapses or merely upon prevalent anatomical configurations."* Reciprocal connections exist but are **not weight-tied** — there is no mechanism by which a presynaptic terminal reads the strength of the reciprocal synapse. | verified (MP p.99); the weight-transport literature is in the plasticity reference |
| 16 | **Continuous differentiability** — gradient descent needs a differentiable unit, hence sigmoid/ReLU/GELU | There is **no "activation function" in HH 1952.** There is a 4-variable stiff nonlinear ODE whose threshold is a moving boundary and whose output is a limit-cycle-like excursion. **The scalar transfer function is an invention of the abstraction, not a simplification of a biological object.** | verified |
| 17 | **One input type per connection** | AMPA (fast), NMDA (slow, voltage-dependent, coincidence-detecting), GABA_A (fast conductance), GABA_B (slow metabotropic), mGluRs — different kinetics and different voltage dependence **at the same synapse**. | ⚠️ kinetics in the synapses reference |
| 18 | **A network of identical units** | Even a perfect per-unit model would misrepresent a population in which rates are lognormal over 3–4 decades, the **same** cells are reliably fast or slow across states and environments, synapse counts vary >10× by cell type, and up to 5,322 transcriptomic clusters coexist. **Homogeneity of units is a separate and arguably larger error than the unit model itself.** | verified |

### 7.6 The honest summary

> The McCulloch–Pitts neuron is not a bad model of a neuron. **It is not a model of a
> neuron at all.** It is a propositional-logic element that its authors defended by
> proving that four named biological facts — relative inhibition, extinction,
> facilitation/temporal summation, and synaptic plasticity — do not change what nets can
> **express**. Their theorems are correct. **The error was never in the theorems.** It
> was in the subsequent inference — which McCulloch and Pitts did not make, and which
> Rosenblatt explicitly refused — that something which can express the same functions is
> therefore a model of the mechanism.
>
> *"neither of us conceives the formal equivalence to be a factual explanation.
> Per contra!"* — p.101.

---

## Sources

Research compiled **2026-11-13** from primary literature. Routes that worked: NCBI
E-utilities `efetch`, Europe PMC REST, ar5iv/arXiv. **Access failures that shape this
file:** NCBI Bookshelf is behind reCAPTCHA, so **Purves *Neuroscience* was never
consulted and no Purves citation appears here**; Kandel, Koch, Dayan & Abbott and Bear
were likewise unobtainable. PMC gates article HTML behind a SHA-256 proof-of-work, and
nature.com, science.org, royalsocietypublishing.org, sciencedirect.com and pnas.org all
returned 403. **This file is primary-literature-based, not textbook-based.**

**Read in full text or page image:** HH 1952 (*J Physiol* 117:500–544, PMC1392413, incl.
pp. 519–520 page scans); Hodgkin, Huxley & Katz 1952 (PMC1392219); Hodgkin & Katz 1949
(PMC1392331, incl. p. 66 image); Goldman 1943 (PMC2142582); Kety & Schmidt 1948
(PMC439518); Raichle & Gusnard 2002 (PMC124895); Herculano-Houzel 2009 (PMC2776484); von
Bartheld, Bahney & Herculano-Houzel 2016 (PMC5063692); Fiacco & McCarthy 2018
(PMC5761435); Savtchouk & Volterra 2018 (PMC6705815); BICCN 2021 (PMC8494634); Mizuseki
& Buzsáki 2013 (PMC3804159); Buzsáki & Mizuseki 2014 (PMC4051294); Cano-Astorga et al.
2024 (PMC11302151); Ventura-Antunes & Herculano-Houzel 2022 (PMC9465999); McCulloch &
Pitts 1943 (via the 1990 *Bull Math Biol* reprint); Rosenblatt 1958.

**Not read (flagged inline):** Azevedo et al. 2009 (Wiley paywall — so **n, sex and age
of the sample are unverified**); Attwell & Laughlin 2001 (abstract only); Shoham et al.
2006 (abstract only); Gidon et al. 2020, Polsky et al. 2004, Larkum et al. 2009 (record
abstracts only); Hursh 1939, Erlanger & Gasser 1930/1937, Lloyd 1943, Post & Jolly 1957,
Sen & Post 1964, Thomas 1972, Strata & Harvey 1999 (bibliographic records only);
reversal potentials (**zero verified values anywhere** — E_Na, E_K, E_Cl, E_AMPA,
E_GABA_A).

---

## Related

- [[neural-networks-ml]] — the artificial abstraction whose departures §7 itemizes.
- [[integrated-information-theory]] — a theory that takes the *causal* structure of this substrate, not its function, to be what matters.
- [[information-theory]] — the entropy and mutual-information machinery behind the coding claims in the circuits reference.
