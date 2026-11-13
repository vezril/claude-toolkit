---
name: integrated-information-theory
description: "Integrated Information Theory (IIT) — Tononi's axiom-to-postulate theory identifying consciousness with the cause-effect structure unfolded from a maximal substrate, across all four versions (2004, 2008, 3.0/2014, 4.0/2023) and the controversy that got it labelled pseudoscience. Covers the method (five axioms of phenomenal existence inferred into five postulates of physical existence, plus the zeroth existence axiom new in 4.0), what Φ actually is and how it changed — critically, that in IIT 4.0 the complex is selected by system integrated information φ_s and NOT by Φ, which is a plain sum computed afterwards, reversing 3.0 — the exclusion postulate and what it buys (no aggregate consciousness, no superposition, the answer to Searle's 'specify the units' demand), and the measure history from effective information through KL divergence and earth-mover's distance to the Intrinsic Difference measure. Precise about intractability: Φ has never been computed for a brain, proponents say so repeatedly in their own papers, the relation count is doubly exponential at 2^(2^n−1)−1, PyPhi's practical ceiling is ~10–12 nodes, and — contrary to common claims — there is NO published complexity-class hardness result, only Aaronson's blog conjectures about the superseded 2004 definition. Covers the empirical program honestly: the Perturbational Complexity Index is a normalized Lempel-Ziv score on a binarized source matrix, is NOT Φ and not an approximation of it (proponents call it 'inspired by' and 'crude proxies'), with the real validated numbers and the trap that 2013's 0.31 and 2016's PCI* = 0.31 are the same number from unrelated procedures. Gives the criticisms at full strength: Aaronson's expander-graph construction, the unfolding argument and Kleiner & Hoel's proof that it generalizes to nearly all theories, Bayne's axiom-by-axiom dilemma, Blackmon's intrinsicality-versus-exclusion tension, the Cogitate adversarial collaboration's actual outcome (IIT passed prediction 2 and failed prediction 3 on connectivity — the reverse of what is often reported), and the 2023/2025 pseudoscience letters with IIT's replies. Use when evaluating an IIT claim, reasoning about machine or animal consciousness, distinguishing PCI from Φ, or needing a sourced account of the field's sharpest live dispute."
---

# Integrated Information Theory

**IIT's central claim, verbatim from IIT 4.0: "an experience is identical to the cause–effect structure unfolded from a maximal substrate."**

It is the most mathematically developed theory of consciousness, the most publicly promoted, and the one 124 researchers signed a letter calling pseudoscience. All three facts are connected.

The method is unusual and is the thing to understand first: IIT starts from **axioms** — claimed self-evident truths about experience — and *infers* **postulates** about what a physical substrate must satisfy. "IIT's starting point is **experience itself rather than its behavioral, functional, or neural correlates**," and the inference step is explicitly "an **inference to a good explanation**" resting on "realism, physicalism, and atomism."

## The axioms and postulates (IIT 4.0)

**Zeroth axiom — Existence:** "Experience exists: there is something." Its warrant: "**It is irrefutable because the very doubting that my experience exists is itself an experience that exists—the experience of doubting.**"

| Axiom (of phenomenal existence) | Postulate (of physical existence) |
|---|---|
| **Intrinsicality** — "Experience is intrinsic: it exists for itself." | cause–effect power must be intrinsic: "take and make a difference within itself" |
| **Information** — "Experience is specific: it is this one." | must "be in this state and select this cause–effect state" — the one with maximal intrinsic information |
| **Integration** — "Experience is unitary: it is a whole, irreducible to separate experiences." | irreducible as a whole set of units, measured by **integrated information φ over the minimum partition** |
| **Exclusion** — "Experience is definite: it is this whole." | "**this whole set of units**" — the one that is maximally irreducible, by **max φ\***. This set is the **complex** |
| **Composition** — "Experience is structured: it is composed of distinctions and the relations that bind them." | subsets must specify distinctions and relations, yielding the **Φ-structure** |

**Zeroth postulate:** "its units must take and make a difference." The ontology behind all of it: **"to be is to have cause–effect power."**

Three ontological principles do the formal work. The **principle of being** (above); the **principle of maximal existence** — "**when it comes to a requirement for existence, what exists is what exists the most**," which licenses every `argmax`; and the **principle of minimal existence** — "**nothing exists more than the least it exists**," which licenses every `min`.

**The completeness claim** is strong and worth knowing: "IIT takes the above set of axioms to be **complete**: there are no further properties of experience that are essential." Space, time, change, the subject–object distinction, intentionality, sense of self, will and affect are all explicitly rejected as non-essential, on the grounds that experiences lacking them are "conceivable" and "also **achievable**, as revealed by altered states of consciousness reached through dreaming, meditative practices, or drugs."

## Φ, and the correction that matters most

**Φ is not Shannon information about messages.** It is defined over **interventional** (`do`-operator) probabilities of a system over *itself*, with background units causally marginalized. IIT 4.0 even coins a unit to mark the break: intrinsic information is measured in "**intrinsic bits, or ibits**," because standard information measures "are typically additive" and this one is not.

**⚠️ The small-φ / big-Φ roles swap between 3.0 and 4.0, and this is the single most common error.**

- **In IIT 3.0, big Φ selects the complex.** A complex is "a local maximum of integrated conceptual information **Φ^Max**."
- **In IIT 4.0, the complex is selected by system integrated information φ_s — also called "small phi" — and NOT by Φ.** The authors' own change log says complexes are now identified by φ_s "as in IIT 2.0 but **unlike IIT 3.0, which evaluated integration after composition**." Φ is then computed *from* the already-identified complex, as a **plain sum** over the φ of every distinction and relation: "**Note that Φ is not computed based on a partition (as system phi), but rather a sum of the integrated information within the structure.**"

So in 4.0: **φ_s answers "does this exist as one entity, and where are its borders?"; Φ answers "how rich is the experience?"** — and "Φ in IIT 4.0 is more aligned with the common-sense notion that the quantity of consciousness relates to the '**richness**' or '**vividness**' of an experience."

**The measure has been replaced three times**, which matters for the non-uniqueness charge: effective information (1.0) → **KL divergence** (2.0) → **earth-mover's distance** (3.0) → **Intrinsic Difference** (4.0). The 4.0 statement is explicit: "**Supplanting prior measures such as the Kullback-Leibler divergence (KLD, IIT 2.0), or the (extended) Earth Mover's Distance (EMD, IIT 3.0), the IIT 4.0 formalism features a newly developed Intrinsic Difference (ID) measure.**" Normalization of the minimum partition was used in 1.0 and 2.0, **explicitly dropped in 3.0** ("no longer necessary"), and **restored in 4.0** with a new justification.

**Intrinsic information is a product of informativeness and selectivity**, and the tension between them is the theory's engine: "a larger system will tend to have higher informativeness… but it will also tend to have lower selectivity because it will have a larger repertoire of states to select from." Consequence: "intrinsic information is **reduced by indeterminism and degeneracy**."

## Exclusion — what it buys and what it costs

"the **maximal substrate, or complex**, is the candidate substrate with the maximum value of system integrated information (φ_s\*), and **overlapping substrates with lower φ_s are thus excluded from existence**."

**This is the postulate that answers Searle's demand** — "Consciousness comes in units and panpsychism cannot specify the units" — and Tononi & Koch quote his "thin veneer of jam" line themselves. Their answer: "**only maxima of integrated information exist**… there is nothing-it-is-like-to-be two people, let alone the 300 plus million citizens making up the USA." And: "**aggregates have no consciousness**."

**What it commits them to, stated plainly in their own words:**

- **No collective consciousness, at any scale.** "if a set of neurons in posterior–central cortex constitutes the main complex, then **no subset, superset, or paraset of it, at any grain, can be conscious**: not individual cortical areas, not the whole cortex, the whole brain, or the whole body."
- **Fusion destroys the originals.** Their own footnote: if two people's brains were connected by "some, yet to be invented, direct brain-to-brain connectivity booster" until the joint Φ exceeded the individual ones, "**their individual conscious mind would disappear and its place would be taken by a new Über-mind that subsumes both.**"
- **A discrete stream.** Exclusion applied to time means "the seemingly continuous 'stream' of consciousness would actually be constituted by a **discrete succession of 'snapshots'**."
- **Recursive condensation** (new in 4.0): the universe condenses into "a **disjoint (non-overlapping) and exhaustive set of complexes**." In 1.0 and 2.0 complexes could overlap and nest.

**The ad-hoc charge, and why it is sharper than it looks.** Tononi himself forbids postulate-patching: "**one cannot simply augment the postulates with ad hoc prescriptions that are not grounded in phenomenology, but merely accommodate some cherished intuition (ensuring, say, that expander graphs, or the United States of America are not conscious by design).**" So critics must argue exclusion fails *his own* test — which is what Cerullo ("**no justification is given to support this principle**"), Bayne (the axiom imposes no substantive constraint) and **Blackmon** attempt. Blackmon's is the most under-used: **having the maximum of anything is a comparative property, and comparative properties are not intrinsic** — so exclusion is in direct tension with the intrinsicality axiom beside it.

## Intractability, stated correctly

**Φ has never been computed for a brain, and the proponents say so in their own papers, repeatedly.**

IIT 3.0: "**The present analysis is unfeasible for systems of more than a dozen elements or so**… which leads to a combinatorial explosion, not to mention that the analysis should be performed at every spatio-temporal grain."

IIT 4.0: "**it is not possible in practice to exhaustively apply the postulates to unfold the cause–effect power of realistic systems**… a full analysis of complexes and their cause–effect structure **can only be performed on idealized systems of a few units.**"

Zaeemzadeh & Tononi 2024: "**unfolding cause-effect structures and determining the associated value of Φ exactly is not feasible for realistic systems**… it is essential to develop approximations and heuristics."

**The scaling:** `2ⁿ − 1` candidate systems; distinctions bounded by `2ⁿ−1`; **relations bounded by `2^(2ⁿ−1) − 1`, doubly exponential** — "The single most expensive term anywhere in IIT." PyPhi's published limit: "the algorithm is exponential time in the number of nodes… **This limits the size of systems that can be practically analyzed to ~10–12 nodes.**" PyPhi 2.0's own docs put IIT 4.0's distinction/relation ceiling *lower*, at ~6–8 units.

**⚠️ There is NO published complexity-class hardness result for Φ. Do not assert one.** Aaronson's "#P-hard to calculate exactly" and "I conjecture that approximating Φ is an NP-hard problem" are **conjectures on a blog**, and his Φ is the **1.0/2.0 effective-information definition**, not 3.0 or 4.0. The only peer-reviewed derivations are counting arguments (Hanson & Walker's `O(13^m)`, Mayner et al.'s `O(n·53ⁿ)`) and they disagree with each other and with PyPhi's documentation — a genuine three-way dispute.

**The honest framing from the IIT side** is their quantum-chemistry analogy: "**This is not dissimilar to the situation in quantum (bio)chemistry in which textbook examples typically deal with a very small number of degrees of freedom, and solving the complete Schrödinger equation for entire proteins remains computationally infeasible.**" And they do name a defeater: "if estimates of integrated information were higher for a model of molecular interactions within a neuron than for a model of synaptic interactions among neurons in a dense cortical lattice, **IIT would be challenged**."

## The empirical program — and PCI is not Φ

**This is the most important distinction in the whole subject, and it is routinely collapsed.**

The **Perturbational Complexity Index** (Casali et al. 2013) is: perturb cortex with TMS, record high-density EEG, source-model and binarize into a significant-sources matrix, then compute **normalized Lempel-Ziv complexity**. Operationally, "PCI is defined as the normalized Lempel-Ziv complexity of the spatiotemporal pattern of cortical activation triggered by a direct TMS perturbation."

**It is not Φ and not an approximation of Φ.** Proponents say "inspired by," "theoretically based," "based on the notion that," and — most explicitly, Zaeemzadeh & Tononi 2024 — "**crude proxies of the system integrated information φ_s**." Grep-verified: "phi" and "Φ" appear **nowhere** in Casali et al.'s body text, and "PCI"/"proxy" appear **nowhere** in IIT 4.0.

**The validated numbers** (PCI, mean ± SD): healthy wakefulness **0.55 ± 0.05**; NREM sleep 0.24 ± 0.02; propofol 0.23 ± 0.04; xenon 0.23 ± 0.06; VS/UWS 0.24 ± 0.04; MCS 0.39 ± 0.05; locked-in syndrome **0.57 ± 0.05**. Casarotto et al. (2016) derived a cutoff on **PCI_max** (the maximum across stimulation sites) over a 150-subject benchmark: "**100% area under the curve**" and "an empirical cutoff PCI\* of 0.31, which discriminated… with **100% sensitivity and 100% specificity**." MCS sensitivity 94.7%.

**⚠️ The trap: 2013's 0.31 and 2016's PCI\* = 0.31 are the same number from unrelated procedures.** The 2013 figure is the *maximum observed* PCI across 24 unconscious subjects; the 2016 figure is an *ROC optimum* on a different, larger sample. The 2013 paper computed **no ROC cutoff and reported no sensitivity or specificity.**

**The best evidence that PCI tracks the integration/differentiation conjunction** is Sarasso et al. (2015), where PCI dropped for **two opposite reasons**: under propofol "because the matrix of activation engaged by TMS was spatially restricted… consistent with a **loss of integration**"; under xenon "because the pattern… was a widespread but stereotypical slow wave… consistent with a **loss of differentiation**." And the dissociation result: ketamine subjects were behaviourally unresponsive (Ramsay 6) with high-amplitude slow waves, yet PCI stayed at 0.44 — and all six "reported having experienced full-fledged dreams."

**What the clinical program licenses, precisely:** one directional claim is framed by proponents as a test — "A straightforward experimental prediction of IIT is that the loss and recovery of consciousness should be associated with the breakdown and recovery of the brain's capacity for information integration. **This prediction has been confirmed**." Everything else — PCI's construction, values and cutoffs — is "consistent with" or "inspired by." ⚠️ And an independent challenge argues PCI's results are equally compatible with Global Neuronal Workspace Theory, i.e. **PCI does not discriminate between theories.**

## The extrapolations IIT accepts

This is where the panpsychism charge comes from, and the proponents do not hedge:

> "It predicts that consciousness is graded, is common among biological organisms and can occur in some very simple systems. Conversely, it predicts that **feed-forward networks, even complex ones, are not conscious, nor are aggregates such as groups of individuals or heaps of sand. Also, in sharp contrast to widespread functionalist beliefs, IIT implies that digital computers, even if their behaviour were to be functionally equivalent to ours, and even if they were to run faithful simulations of the human brain, would experience next to nothing.**"

- **The photodiode.** "even circuits as simple as a 'photodiode'… can have a modicum of experience," for which "the only phenomenal distinction would be between '**this rather than not this**'." Their defence is a temperature analogy: normal matter one degree above absolute zero still contains heat, so "**there may well be a practical threshold for Φmax below which people do not report feeling much of anything, but this does not mean that consciousness has reached its absolute minimum, zero.**"
- **Inactive but not inactivated.** "**A functional cerebral cortex that happens to be silent – no neuron is sending any signal (spike) to any other neuron – would nevertheless be conscious.**" The distinction is load-bearing and critics routinely drop it: *inactive* elements still specify a cause–effect repertoire; *inactivated* ones do not. 4.0-era term: "**causal readiness**."
- **A perfect simulation is a zombie.** "a purely feed-forward system able to replicate the input–output behaviour of the human brain… would be behaviourally indistinguishable from us, and certainly capable of passing the Turing test, yet it would have zero Φ and would thus be a '**perfect**' zombie." And for simulations: "**just like a computer simulation of a giant star will not bend space–time around the machine, a simulation of our conscious brain will not have consciousness.**" Formalized in 2024 with **full** functional equivalence, not approximation.
- **The AI consequence they draw:** "**IIT implies that AI may do everything we do and behave as if it were conscious, but it will not be — 'doing without being'. Conversely… patients who are unresponsive and cognitively incapacitated may still have a rich phenomenology — 'being without doing'.**"

**On panpsychism, their position has been consistent for a decade and is deliberately qualified.** They accept: consciousness is intrinsic and fundamental, graded, likely widespread, present in small amounts in simple systems — "**IIT does side with the panpsychist intuition.**" They reject: "**Unlike panpsychism, however, IIT clearly implies that not everything is conscious.**" And they claim to *solve* panpsychism's combination problem rather than inherit it, while being blunt about its failures: "**panpsychism's beauty has been singularly barren… it has little constructive to say and offers no positive laws.**" See [[panpsychism]].

⚠️ **Whether Koch self-describes as a panpsychist could not be established from any primary source.** What is on the record: joint Tononi–Koch statements that IIT "is not at odds with panpsychism" "in this general sense"; third parties treating him as one; and Aaronson reporting that "**To his credit, Tononi cheerfully accepts the panpsychist implication: yes, he says, it really does mean that thermostats and photodiodes have small but nonzero levels of consciousness.**"

## The criticisms, at full strength

**Aaronson's constructions (blog, 2014).** He builds systems with enormous Φ that are obviously not conscious — a modified Vandermonde system whose "Φ equals **half of its entire information content**," and expander graphs of XOR gates, of which he says "I feel **100% confident** in saying that the so-constructed expander graphs are **not conscious**." His general argument is the respectable version of the incredulous stare: if a theory's verdicts on the paradigm cases are wrong, it has failed at the only task that could have validated it. Note that **Koch conceded the scaling** in the thread: "we agree on a 1-D array having a small but non-zero Phi value while **Phi for a 2-D array increases as √(# of nodes)**."

**The unfolding argument** (Doerig, Schurger, Hess & Herzog 2019). Because feedforward and recurrent networks are both universal approximators, any recurrent system can be "unfolded" into a behaviourally identical feedforward one with Φ = 0. So either IIT is falsified (if unfolded zombies are conscious) or it is "outside the realm of science" (if they aren't, since nothing could distinguish them). They also show the dissociation runs both ways — you can **raise Φ arbitrarily while holding behaviour fixed** by inserting a Φ-increasing device and cancelling its functional effect.

**⚠️ But the selectivity claim lost.** Kleiner (2020) and **Kleiner & Hoel (2021)** proved the problem generalizes: if inference and prediction data are independent, "**either every single inference operation is wrong or the theory under consideration is already falsified**" — for *all* minimally informative theories. And if they are strictly dependent, the theory "is either already falsified or **empirically unfalsifiable**" — which catches the functionalist theories Doerig et al. recommended. "**Theories of consciousness seem caught between Scylla and Charybdis.**"

**The critics' best remaining card is the self-undermining charge** (Herzog, Schurger & Doerig 2022), which is sharper than unfalsifiability: "**IIT implies that both the level and content of consciousness are epiphenomenal… we cannot even trust reports about first-person experiences. But reports about first-person experiences are taken as ground truth and the foundation for IIT's axioms. Therefore, accepting IIT leads to rejecting its own axioms.**"

**And the best technical objection to the unfolding step** is Usher's (2021): universal approximation does not deliver equivalence under **perturbation** or in **temporal dynamics**. That matters enormously, because IIT's actual empirical program (TMS–EEG, PCI) is *perturbational*, not observational.

**Bayne (2018) runs one dilemma on every axiom:** either it is genuinely self-evident, in which case it is too weak to constrain any theory; or it constrains substantively, in which case it is not self-evident. On exclusion and temporal grain he lands a direct hit: Tononi et al. call the duration of an instant of consciousness "definite" and then give a range of "a few tens of milliseconds to a few hundred milliseconds" — "**the architects of IIT themselves regard the duration of consciousness as variable. But if that is the case, then what kind of constraint could the axiom of exclusion place on a theory of consciousness?**"

**The Cogitate adversarial collaboration** (*Nature*, 2025) — and **⚠️ the result is widely misreported, including in my own initial framing.**

| Prediction | Outcome for IIT |
|---|---|
| 1. Decoding location (non-critical for IIT) | **Mixed, favouring IIT.** Orientation decoded in posterior but **not** prefrontal ROIs; adding PFC did not improve decoding (BF₀₁ up to 1.9×10⁵) |
| 2. Maintenance over duration | **PASSED the preregistered criteria** — sustained category and identity representation in posterior cortex. But with a "**sparse neural substrate**" (just 8 of 53 face-selective electrodes), and orientation information **decayed after 0.5 s**, contrary to IIT |
| 3. Sustained gamma connectivity | **FAILED. This is IIT's headline failure.** "The results of the preregistered PPC metric for prediction 3, critical for both IIT and the GNWT, supported neither theory" |

The consortium: "**For IIT, the lack of sustained synchronization within posterior cortex represents the most direct challenge**… This is **incompatible with IIT's claim that the state of the neural network, including its activity and connectivity, specifies the degree and content of consciousness.**"

**Dehaene's reply is the most-quoted line in the controversy, and it is the real problem:** "**None of the massive mathematical backbone of IIT, such as the φ measure of awareness, was tested in the present experiment. Instead, what are presented as unique predictions of IIT (posterior visual activation throughout stimulus duration) are just what any physiologist familiar with the bottom-up response properties of those regions would predict.**"

**Fleming formalized that as a Bayesian point**, and it is the strongest version: the likelihood of posterior decoding given mainstream neuroscience is ~0.99, so observing it multiplies your prior by ~1 — "**The evidence in question here is not diagnostic of IIT, and therefore cannot be used in support of the theory, formally or informally.**" He concedes the connectivity prediction was the genuinely distinctive one, "and this is one that IIT failed to pass."

**The pseudoscience letters.** The 2023 PsyArXiv letter (**124 named signatories**, drafted by ten including Fleming, Frith, Goodale, Lau, LeDoux, Lee, Michel, Owen, Peters, Slagter) objected to media coverage calling IIT "leading" and empirically tested, and argued: "**Given its panpsychist commitments**, until the theory as a whole… is empirically testable, we feel that the pseudoscience label should indeed apply." Its evidence that IIT is not in fact leading: survey work finding "**non-experts view IIT as the theory of consciousness most likely to be true, while it ranks near the bottom among experts in the field.**"

The published 2025 version (*Nature Neuroscience* 28:689–693) **dropped "pseudoscience" from the title**, sharpened the thesis to **in-principle untestability**, and added a crucial scoping move: "**We distinguish the core claims of IIT, which we argue are unscientific, from work merely inspired by IIT that uses measures of complexity… This latter work is uncontroversially scientific, but neither supports nor tests the core claims of IIT.**" It also went down to 103 signatories — 25 dropped, including GNWT's founder Bernard Baars and Patricia Churchland. (No source explains any individual departure; do not speculate.)

**IIT's reply** (*Nature Neuroscience* 28:694–702) reframes it as a paradigm clash: "**Paradigms tend to die when a stubborn fact refuses to be accommodated; in this case, the stubborn fact is consciousness itself.**" And: "**more than three decades ago, some of us set forth to tackle consciousness scientifically, at a time when merely mentioning the word implied a disqualification from science… It is an ironic twist, then, to see a flock of those who can now safely pursue the study of consciousness issue indictments of pseudoscience.**"

**Two facts worth holding alongside the dispute.** Koch and Tononi have a **financial interest in Intrinsic Powers Inc.**, "a company whose purpose is to develop a device that can be used in the clinic to assess the presence and absence of consciousness in patients" — which a separate open letter argued was an undisclosed conflict at the ASSC media event. And Lau's institutional critique argues the whole adversarial-collaboration model was structurally compromised: the conception meeting was hosted by Koch, the invitee list set by Koch and the funder's program officer, and Tononi's objection to psychophysics is what Lau says led to the design flaw of **no unconscious control condition.**

## Always-apply

1. **Say which version.** The axioms, the measure, the normalization, and the role of Φ have all changed. "IIT says X" without a version number is usually wrong about at least one of them.
2. **In 4.0, the complex is selected by φ_s, not Φ.** Getting this backwards inverts the theory's structure.
3. **Never say PCI measures Φ.** Use the proponents' own words — "inspired by," "crude proxies." And keep the two 0.31s apart.
4. **Do not assert a complexity class for Φ.** Aaronson's are blog conjectures about the 2004 definition. Cite the counting arguments and note they disagree.
5. **Quote the proponents' own infeasibility admissions** rather than a critic's paraphrase — they are more damaging and unimpeachable.
6. **Report Cogitate correctly:** IIT **passed** prediction 2 and **failed** prediction 3 (connectivity). The "duration prediction failed" version is wrong.
7. **Pair the unfolding argument with Kleiner & Hoel.** The dilemma is real but it does not single out IIT, and the functionalist alternatives fall to the other horn.
8. **Distinguish strong from weak IIT.** The complexity-measure work is uncontroversially scientific; the untestability charge targets the core claims. Both sides now accept this scoping.
9. **Note the conflicts of interest on both sides** — Intrinsic Powers for the proponents, and that the unfolding-argument authors, the letter signatories and the 2025 letter authors substantially overlap, so their critique is one programme rather than independent convergence.

## How to use the references

- **`references/formalism.md`** — all four versions with their authoritative change logs, the axioms and postulates verbatim for 3.0 and 4.0, the 4.0 formalism step by step (intrinsic information, the Intrinsic Difference measure and its three uniqueness properties, directional partitions, φ_s, distinctions, relations, Φ-folds), the normalization oscillation, grain dependence, the full intractability record with PyPhi's measured timings and the three-way scaling dispute, and the proxy measures with the published statements that they are not Φ.
- **`references/controversies.md`** — Aaronson's two posts and Tononi's reply in detail; the Cogitate collaboration's design, the three predictions, every result, the deviations from preregistration, both adversaries' post-hoc defences, and the third-party critiques (Lau, Fleming, Seth); the unfolding argument and all five published replies; the exclusion-postulate objections (Cerullo, Bayne, Blackmon, Schwitzgebel's withdrawn argument); and the two letters with the signatory diff and IIT's replies.

## Sources

Tononi, *BMC Neuroscience* 5:42, 2004 (IIT 1.0). Balduzzi & Tononi, *PLoS Comput Biol* 4(6):e1000091, 2008 and 5(8):e1000462, 2009 (2.0). **Oizumi, Albantakis & Tononi, "From the Phenomenology to the Mechanisms of Consciousness: IIT 3.0," *PLOS Computational Biology* 10(5):e1003588, 8 May 2014.** **Albantakis, Barbosa, Findlay, Grasso, Haun, Marshall, Mayner, Zaeemzadeh, Boly, Juel, Sasai, Fujii, David, Hendren, Lang & Tononi, "Integrated information theory (IIT) 4.0," *PLOS Computational Biology* 19(10):e1011465, 17 October 2023** — axiom and postulate wording here is verbatim from the JATS manuscript XML, not a summary. Barbosa, Marshall, Streipert, Albantakis & Tononi, *Scientific Reports* 10:18803, 2020 (the ID measure). Zaeemzadeh & Tononi, *PLoS Comput Biol* 20(8):e1012323, 2024 (upper bounds). Mayner, Marshall, Albantakis, Findlay, Marchman & Tononi, "PyPhi," *PLOS Comput Biol* 14(7):e1006343, 2018. Tononi & Koch, "Consciousness: here, there and everywhere?", *Phil. Trans. R. Soc. B* 370(1668):20140167, 2015. Casali et al., *Science Translational Medicine*, 2013 (PCI). Casarotto et al., 2016 (PCI\*). Sarasso et al., 2015 (ketamine). Comolatti et al., 2019 (PCI^ST). Findlay, Marshall, Albantakis, David, Mayner, Koch & Tononi, "Dissociating Artificial Intelligence from Artificial Consciousness," arXiv:2412.04571, 2024. Cogitate Consortium, "Adversarial testing of global neuronal workspace and integrated information theories of consciousness," *Nature* 642(8066):133–142, 30 April 2025. Aaronson, "Why I Am Not An Integrated Information Theorist," *Shtetl-Optimized*, 21 May 2014, and "Giulio Tononi and Me: A Phi-nal Exchange," 30 May 2014 — **a blog, not peer-reviewed**. Doerig, Schurger, Hess & Herzog, *Consciousness and Cognition* 72:49–59, 2019. Kleiner & Hoel, *Neuroscience of Consciousness* 2021(1):niab001. Usher, *Consciousness and Cognition* 95:103212, 2021. Herzog, Schurger & Doerig, *Consciousness and Cognition* 98:103261, 2022. Bayne, *Neuroscience of Consciousness* 2018(1):niy007. Cerullo, *PLOS Comput Biol* 11(9):e1004286, 2015. Blackmon, *JCS* 28(11), 2021. Mediano, Rosas, Bor, Seth & Barrett, "The strength of weak integrated information theory," *TiCS* 26(8):646–655, 2022. IIT-Concerned et al., "What makes a theory of consciousness unscientific?", *Nature Neuroscience* 28(4):689–693, 10 March 2025, and the 2023 PsyArXiv original, doi:10.31234/osf.io/zsr78. Tononi et al., "Consciousness or pseudo-consciousness? A clash of two paradigms," *Nature Neuroscience* 28(4):694–702, 2025. Lau, PsyArXiv 10.31234/osf.io/93ufe and 10.31234/osf.io/28z3y, 2023. Fleming, *The Elusive Self*, 20 July and September 2023. All fetches 2026-11-11.

**Verification notes.** ⚠️ **No published complexity-class result for Φ exists**; Aaronson's are blog conjectures about the 1.0/2.0 definition, and the peer-reviewed counting arguments (`O(13^m)`, `O(n·53ⁿ)`, PyPhi's docs) disagree three ways. ⚠️ **Sources disagree on PyPhi's exponent**: the published JATS markup gives `O(n·53ⁿ)`, the project's current documentation renders the same result as `O(n⁵·3ⁿ)` — present both. ⚠️ **Not verified and not asserted here:** whether Koch self-describes as a panpsychist; the subtitle of his 2019 book; the contents of his popular articles; the Searle *NYRB* exchange's primary citation; Pautz's *JCS* arguments; Barrett & Mediano's *JCS* text; Mørch's verdict on IIT/Russellian-panpsychism compatibility; the "zap and zip" phrase's provenance (a Europe PMC full-text search returns 8 hits, **none** by the Massimini/Tononi group, and the phrase appears in none of nine primary papers checked). ⚠️ **Schwitzgebel withdrew his own conscious-USA argument against IIT**, noting Tononi's position had substantially changed — it targets pre-exclusion IIT (≤2009), not 3.0/4.0. ⚠️ There is **no IIT 4.5 or 5.0** as of November 2026; the framework is being extended in modular follow-ups, and Tononi's book *On Being* remains forthcoming.

## Related

- [[panpsychism]] — the tradition IIT is accused of belonging to, and whose combination problem IIT claims to solve via exclusion. Searle's "specify the units" demand is the hinge.
- [[neural-networks-biology]] — the cortical facts the posterior-hot-zone and cerebellum arguments turn on.
- [[stochastic-parrot]] — the adjacent machine-consciousness question. IIT's answer is unusually sharp: behaviourally equivalent computers "will not replicate our experiences."
- [[information-theory]] — the measures IIT departs from; note it coins "ibits" precisely to mark the break from additive Shannon information.
- [[grounded-answers]] — the sourcing discipline a dispute this contested requires.
