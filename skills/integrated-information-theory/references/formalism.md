# IIT: the formalism, version by version

Research date **2026-11-11**. Method note: the PLOS papers were pulled as raw **JATS manuscript XML** (`journals.plos.org/ploscompbiol/article/file?id=<DOI>&type=manuscript`) and the supplementary PDFs directly, **so all axiom/postulate wording below is verbatim from the authoritative markup, not from a summarizer.** ⚠️ marks what could not be verified or where sources genuinely disagree.

---

## Version history

### IIT 1.0 — Tononi 2004

**Tononi G., "An information integration theory of consciousness," *BMC Neuroscience* 2004;5:42**, doi:10.1186/1471-2202-5-42. Received 10 Aug 2004, published 2 Nov 2004. (Companion/predecessor: **Tononi & Sporns, "Measuring information integration," *BMC Neuroscience* 2003;4:31** — IIT 4.0's own supplement cites *both* as "IIT 1.0".)

**Φ in 1.0 is effective information across bipartitions, with no cause-effect structure.** The chain, verbatim:

- **Effective information**: *"we define the effective information between A and B as **EI(A→B) = MI(A^Hmax; B)**."* Maximum entropy `Hmax` is **injected** into A's outgoing connections (independent noise) — a **perturbational, not observational** measure: *"EI(A→B) measures all possible effects of A on B, not just those that are observed if the system were left to itself."* Asymmetric; summed bidirectionally: **`EI(A↔B) = EI(A→B) + EI(B→A)`**.
- **MIB**: *"The minimum information bipartition **MIB_A↔B** of subset S – its 'weakest link' – is its bipartition for which the normalized effective information reaches a minimum, corresponding to `min{EI(A↔B)/H_max(A↔B)}`"*, where `H_max(A↔B) = min{H_max(A); H_max(B)}`.
- **Φ**: *"The information integration for subset S, or Φ(S), is simply the **(non-normalized)** value of EI(A↔B) for the minimum information bipartition: Φ(S) = EI(MIB_A↔B)."* ⚠️ **Note: the minimum is taken over the *normalized* quantity, and Φ is reported *un-normalized*.**
- **Symbol etymology**, verbatim: *"The symbol Φ is meant to indicate that the information (the vertical bar 'I') is integrated within a single entity (the circle 'O')."*
- **Complex**: *"a complex is a subset S having Φ>0 that is **not included within a larger subset having higher Φ**."* Main complex: *"the one with the maximum value of Φ(S) is called the **main complex**."* ⚠️ **1.0-specific properties, verbatim:** *"the same element can belong to more than one complex, and **complexes can overlap**."* **Exclusion in the later sense does not yet hold.** I/O elements are *"ports-in"* and *"ports-out."*
- **Grain is already present in 1.0**, verbatim: *"The Φ value of a complex is dependent on both spatial and temporal scales… there will be a 'grain size', in both space and time, at which Φ reaches a maximum."* Predicts cortical **minicolumns** over single neurons, and *"Φ values in the brain are likely to show a maximum between tens and hundreds of milliseconds."*
- **No axioms/postulates, no concepts, no cause-effect structure.** The argument rests on two "phenomenological properties": **differentiation and integration.**
- ⚠️ **"Qualia space" *does* appear in 1.0, but means something different from 2009.** Verbatim: *"the elements of a complex constitute the dimensions of an abstract relational space, the **qualia space**… The **effective information matrix** defines the relational structure of the space."* **So in 1.0 the axes are *elements*; from 2.0 on, the axes are *system states*. This is a common conflation.**
- **Stationary, not state-dependent.** Models *"implemented as a stationary multidimensional Gaussian process."* IIT 3.0's supplement confirms 1.0 *"dealt only with stationary systems"* / *"only for a stationary system at equilibrium."*
- Headline claim: *"consciousness corresponds to the **capacity** of a system to integrate information"* — **note *capacity*, a dispositional reading that 2.0 replaced.**

### IIT 2.0 — Balduzzi & Tononi 2008, 2009; Tononi 2008

**Balduzzi & Tononi, "Integrated information in discrete dynamical systems: motivation and theoretical framework," *PLoS Comput Biol* 2008;4(6):e1000091.** **Balduzzi & Tononi, "Qualia: the geometry of integrated information," *PLoS Comput Biol* 2009;5(8):e1000462.** **Tononi, "Consciousness as integrated information: a provisional manifesto," *Biological Bulletin* 2008;215(3):216–242.** (Also in the lineage: Tononi, "Integrated Information Theory of Consciousness: An Updated Account," *Archives Italiennes de Biologie* 2012;150:56–90.)

What 2.0 added:

1. **State-dependence.** BT2008 abstract: *"This paper introduces a **time- and state-dependent** measure of integrated information, φ."* *"φ varies depending on the state entered by a network, being higher if active and inactive elements are balanced and lower if the network is inactive or hyperactive."*
2. **Actual vs potential repertoires** (BT2009's terms; BT2008 calls them *a posteriori* / *a priori*). *"This **potential repertoire** (or '**a priori repertoire**') is the maximum entropy (maxent or uniform) distribution, which entails maximum ignorance"*; *"mechanism and current state specify an **actual repertoire** (or '**a posteriori repertoire**')."* **Effective information = "the entropy of the actual repertoire *relative to* the potential repertoire … also known as Kullback-Leibler divergence."** → **the measure in 2.0 is KL divergence.**
3. ⚠️ **2.0 evaluates CAUSES ONLY.** The a posteriori repertoire is *"the repertoire of states that could have led to x₁"*, computed by perturbing and applying Bayes' rule. IIT 4.0's supplement confirms 2.0 identified complexes by φ_s *"although in that case **only causes (and not effects) were evaluated**."*
4. **φ definition** (Eq 2A): *"Integrated information φ (I for information and O for integration) is defined as the entropy of the a posteriori repertoire of the system **relative to the combined a posteriori repertoires of the parts**"*, evaluated at `P_MIP`. **Bounded: "For a discrete system composed of n binary elements φ(x₁) ≤ n bits."** Distinguished from Ay's **stochastic interaction**: *"our approach is distinguished by comparing the whole to the parts, rather than the parts to one another."*
5. **MIP with normalization**: *"The normalization is the size of the smallest a priori repertoire of a part multiplied by the number of other parts"*; the MIP is *"the partition for which **normalized** effective information is a minimum."* Tie-break: lowest *un-normalized* EI.
6. **Main complex redefined**: *"A subset S of X forms a complex when it enters state s₁ if φ(s₁)>0 and S is **not contained in some larger set with strictly higher φ**. A complex whose subsets have **strictly lower** φ is called a **main complex**."* **Still permits nesting**: *"a smaller complex of high φ (main complex) may be contained within a larger complex of low φ."*
7. **Qualia space (the real thing) — BT2009**, verbatim: *"**Qualia space (Q) is a space having an axis for each possible state (activity pattern) of a complex.** Within Q, each submechanism specifies a point corresponding to a repertoire of system states. **Arrows between repertoires in Q define informational relationships.** Together, these arrows specify a **quale—a shape** that completely and univocally characterizes the quality of a conscious experience. **Φ — the height of this shape** — is the quantity of consciousness associated with the experience. **Entanglement** measures how irreducible informational relationships are to their component relationships, specifying **concepts and modes**."* Q is **2ⁿ-dimensional.** Terminology: **q-arrows, q-edges, q-folds.**
   - BT2009 corollaries worth keeping: *"Both active and inactive elements specify a quale, but elements that are **inactivated** do not"* (**this survives into 4.0 as a prediction**); *"two different systems having identical activity patterns may generate different qualia."*
8. **Tononi 2008 (Biol Bull) is the verbal manifesto**: *"(i) the quantity of consciousness corresponds to the amount of integrated information generated by a complex of elements; (ii) the quality of experience is specified by the set of informational relationships generated within that complex."*

⚠️ **Notational inconsistency to flag:** Tononi 2008 and BT2009 use **capital Φ** for the complex-level integrated information; BT2008 uses **lowercase φ** for the same thing. **The small-φ/big-Φ split as a *mechanism vs system* distinction only arrives in 3.0.**

### IIT 3.0 — Oizumi, Albantakis & Tononi 2014

**Oizumi M., Albantakis L. & Tononi G., "From the Phenomenology to the Mechanisms of Consciousness: Integrated Information Theory 3.0," *PLoS Computational Biology* 2014;10(5):e1003588**, doi:10.1371/journal.pcbi.1003588. Received 18 Nov 2013, accepted 11 Mar 2014, **published 8 May 2014.**

**The ten changes are enumerated by the authors themselves** in **Text S1, "Main differences between IIT 3.0 and earlier versions"** (supplementary file `pcbi.1003588.s002`):

1. **Axioms and postulates presented explicitly for the first time** — *"This clarifies many issues and highlights the link between the starting point of IIT, which is phenomenology itself… and the postulates that must be satisfied by physical systems."* Applied *"explicitly both at the level of individual mechanisms and at that of systems of mechanisms."*
2. **Mechanisms specify both causes AND effects** — *"Unlike IIT 2.0, IIT 3.0 considers how mechanisms in a state constrain both the past and the future… In a way this is a **return to the state-independent framework of IIT 1.0**, which considered both causes and effects, but only for a stationary system at equilibrium. It is also a return to IIT 1.0 in capturing the idea that information is 'a difference that makes a difference', and not simply 'a difference'."* Also: *"the relationship between information and causation… **in IIT 3.0 are one and the same thing**."*
3. **Elements are mechanisms in a state**, not connections (as in 2.0).
4. **Complexes identified via the whole conceptual structure.** *"For computational expediency, in IIT 1.0 and 2.0, complexes were identified by assessing the irreducibility of a set of elements through partitions of its **highest-order concept only**… In IIT 3.0, the irreducibility of a set of elements is assessed by considering how a partition affects its **entire conceptual structure** — all the concepts specified by its elements in all combinations (power set)."*
5. ⚠️ **MIP evaluated WITHOUT normalization** — *"In IIT 1.0 and 2.0, normalization was used… In IIT 3.0 this is no longer necessary."* **(Normalization returns in 4.0 — a real oscillation across versions.)**
6. **Concepts must be irreducible** — *"This important requirement had been **overlooked in IIT 2.0**."*
7. **EMD replaces KLD.** *"In IIT 2.0, the effect of partitions was measured by the Kullback-Leibler divergence (KLD), which **only takes into account differences in selectivity**. IIT 3.0 recognizes the need for a **true metric (the earth mover's distance, EMD)** that also takes into account the similarity or dissimilarity of states between whole and partitioned distributions. Moreover, an **extended version of EMD** is applied to measure the distance between whole and partitioned constellations of concepts in concept space."*
8. **Exclusion applied to individual mechanisms' causes and effects**, not just to systems.
9. **Background conditions fixed at actual values**, rather than noised.
10. A public program was released (`github.com/Albantakis/iit`, branch `IIT-3.0-Program`) — **the ancestor of PyPhi.**

**The intrinsic/causal reframing** is in 3.0's **Text S2**, verbatim: *"Shannon information … is always assessed from the **extrinsic perspective of an observer**… Therefore, Shannon information could be called **extrinsic information**. In IIT, by contrast, information is **intrinsic**: it is assessed from the intrinsic perspective of a system in terms of the differences that make a difference to it. Intrinsic information is **causal**, and it must be evaluated by **perturbing** a set of elements in all possible ways, not just by observing them. It is also **compositional**… Crucially, in IIT information must also be **integrated**… **IIT only considers information that is maximally integrated or exclusive** because, from the intrinsic perspective, there can only be one set of causes."* And the strong line: *"classical information theory does not deal with meaning… **In IIT, instead, information IS meaning**: more precisely, intrinsic integrated information is a maximally irreducible information structure (MICS)… It is thus a **shape in concept space, not a message transmitted across a channel**."* **The corollary they draw: "dreams have as much meaning as awake experiences."**

**3.0's central identity, verbatim:** *"**The maximally irreducible conceptual structure (MICS) generated by a complex of elements is identical to its experience.** The constellation of concepts of the MICS completely specifies the quality of the experience (its quale 'sensu lato'). Its irreducibility **Φ^Max** specifies its quantity. The maximally irreducible cause-effect repertoire (MICE) of each concept within a MICS specifies what the concept is about… while its value of irreducibility **φ^Max** specifies how much the concept is present in the experience."*

### IIT 4.0 — Albantakis et al. 2023

**Albantakis L., Barbosa L., Findlay G., Grasso M., Haun A.M., Marshall W., Mayner W.G.P., Zaeemzadeh A., Boly M., Juel B.E., Sasai S., Fujii K., David I., Hendren J., Lang J.P. & Tononi G., "Integrated information theory (IIT) 4.0: Formulating the properties of phenomenal existence in physical terms," *PLOS Computational Biology* 2023;19(10):e1011465**, doi:10.1371/journal.pcbi.1011465. Received 11 Jan 2023; accepted 26 Aug 2023; **published 17 October 2023.** The first eight authors are marked "contributed equally"; Tononi is corresponding.

**The authoritative change list is supplementary file `pcbi.1011465.s002` = "S2 Text – Comparison to IIT 1.0–3.0 and subsequent publications"** (dated 12 Sep 2023):

1. **Axioms/postulates restructured.** *"The updated 4.0 exposition of IIT's axioms **explicitly separates phenomenal existence, which is not a property, from intrinsicality, which is one of the essential properties**… the existence of experience is introduced as IIT's foundational, **zeroth axiom**."* On the reordering: *"Because only an experience that exists intrinsically, in a way that is specific, irreducible, and definite can also be structured, **composition takes the final position** in the ordering of the axioms and postulates."* ⚠️ **The refinement was partly defensive:** *"the formulation of the axioms has been refined **to avoid misunderstandings [Bayne 2018; Merker, Williford & Rudrauf 2021]**."*
2. **ID replaces KLD and EMD — the explicit abandonment statement**, verbatim: *"**Supplanting prior measures such as the Kullback-Leibler divergence (KLD, IIT 2.0), or the (extended) Earth Mover's Distance (EMD, IIT 3.0), the IIT 4.0 formalism features a newly developed Intrinsic Difference (ID) measure, which uniquely complies with the postulates of IIT.**"* The reason: *"**ID is related to the KLD, which can be viewed as an average of the point-wise mutual information across states and is an additive measure. By contrast, the ID is defined based on the state that maximizes the difference between distributions (specificity property).**"* **Theorem 1** states the unique form `D(p,q) = max_u {k·p(u)·log(p(u)/q(u))}`, `k ∈ ℝ⁺` — proof in Barbosa et al. 2020.
3. **Intrinsic information = selectivity × informativeness.** *"the intrinsic information specified by a system (or mechanism) over a cause or effect state is evaluated as a **product of informativeness and selectivity**, which makes it **subadditive if p < 1**."*
4. **"Concepts" renamed "distinctions".** *"In IIT 3.0, distinctions were called '**concepts**' (which composed to a '**conceptual**' structure), a term that **could generate unnecessary misunderstandings**."* Also: *"**Unlike IIT 3.0, in IIT 4.0 distinctions select a specific state** as a cause and an effect."* The "virtual elements" device of 3.0 is gone: now *"presented more formally in terms of product probabilities."*
5. **Relations become explicit.** *"Developing an explicit account of phenomenal relations in terms of causal relations was a main goal of IIT since IIT 1.0. **IIT 3.0 employed a distance metric—the Earth Mover's Distance—that was sensitive to whether different distinctions ('concepts') had similar cause–effect repertoires, but relations did not figure explicitly in the formalism despite their central role in characterizing experience.**"*
6. **Complex selection and the new Φ.** *"Maximal substrates, or complexes, are identified based on their **system integrated information φ_s (as in IIT 2.0 but unlike IIT 3.0, which evaluated integration after composition)**."* Normalization returns: *"In IIT 4.0, the minimum partition (MIP) is identified as the partition with minimal integrated information (φ_s), **normalized** by the maximal possible value of φ_s across this partition for an arbitrary TPM of the same dimensions… In this way, the MIP is sensitive to the **fault lines** of a candidate system, rather than defaulting to partitions of individual system units."*

   **The Φ redefinition, verbatim — the single most important correction in the subject:** *"In IIT 3.0… **the Φ value corresponding to the quantity of consciousness only captured the distinctions affected by the minimum partition**, as opposed to all the distinctions (and relations) unfolded from a maximally irreducible substrate. **Because Φ is not evaluated with respect to a MIP, there is no normalization involved in determining Φ (in contrast to φ_s).** Instead, Φ captures the complete structure integrated information of a complex in the form of a **sum** over the integrated information φ of all components… where **the sum was chosen as the simplest option** that captures all that exists within the complex. As such, **Φ in IIT 4.0 is more aligned with the common-sense notion that the quantity of consciousness relates to the 'richness' or 'vividness' of an experience** considering all its contents. However, whether a system exists as one integrated entity is evaluated by its system integrated information φ_s, **which is not compositional**."*
7. **Background conditions, a third treatment in three versions.** 3.0 fixed them in the current state (effects) and the actual past state (causes); interim publications fixed them in the current state for both; *"**In IIT 4.0, the treatment of background conditions is updated to causally marginalize the background units, conditional on the current state of the universe.** This formulation avoids the problem of unreachable states."*

### Is there a 4.5 or anything newer? (as of 2026-11-11)

**No. There is no IIT 4.5 or 5.0.** The evidence:

- The **official IIT wiki, `www.iit.wiki`**, labels its formalism page *"Mathematical Formalism: IIT 4.0"* and is itself at *"Version 1.0 (version 30.06.2024)."* No later version number appears.
- A sweep of **PubMed for all Tononi papers 2024–2026 (42 records) and all Albantakis papers 2023–2026 (19 records)** found **no paper announcing a new version number.** The 4.0 framework is instead being **extended in modular follow-ups**:
  - **Zaeemzadeh & Tononi, "Upper bounds for integrated information," *PLoS Comput Biol* 2024;20(8):e1012323** (cited in IIT 4.0 as ref [50] "in preparation").
  - **Comolatti, Grasso & Tononi, "Why does time feel the way it does? Toward a principled account of temporal experience," *iScience* 2025;28(10):113434** (was 4.0 footnote 16).
  - **Marshall, Findlay, Albantakis & Tononi, "Intrinsic units: identifying a system's causal grain," *Neuroscience of Consciousness* 2026;2026(1):niag013** — abstract, verbatim: *"we **extend the mathematical framework of IIT 4.0** to assess cause-effect power across grains."*
  - **Mayner, Marshall & Tononi, "Intrinsic Cause-Effect Power: The Tradeoff Between Differentiation and Specification," *Entropy* 2026;28(4):410**, published 4 Apr 2026.
- ⚠️ **The theory's book-length statement is still forthcoming.** IIT 4.0's S1 Notes footnote 3 reads simply *"Tononi, G. On Being (forthcoming book)"*; iit.wiki still describes it as forthcoming. **Publication could not be confirmed.**
- **PyPhi 2.0 implements IIT 4.0** and is the closest thing to a "4.x" artifact.

---

## Axioms and postulates, verbatim

### IIT 3.0 (2014), in the paper's order

**Framing**, verbatim: *"**axioms are self-evident truths about consciousness** – the only truths that, with Descartes, cannot be doubted and do not need proof… **Postulates** instead are assumptions about the physical world and specifically about the physical substrates of consciousness."*

**Five axioms — note *existence*, not intrinsicality, and *composition second*:**

- **Existence:** *"Consciousness exists – it is an undeniable aspect of reality. Paraphrasing Descartes, 'I experience therefore I am'."*
- **Composition:** *"Consciousness is compositional (structured): each experience consists of multiple aspects in various combinations."*
- **Information:** *"Consciousness is informative: each experience differs in its particular way from other possible experiences."*
- **Integration:** *"Consciousness is integrated: each experience is (strongly) irreducible to non-interdependent components."*
- **Exclusion:** *"Consciousness is exclusive: each experience excludes all others – at any given time there is only one experience having its full content, rather than a superposition of multiple partial experiences; each experience has definite borders – certain things can be experienced and others cannot; **each experience has a particular spatial and temporal grain** – it flows at a particular speed, and it has a certain resolution such that some distinctions are possible and finer or coarser distinctions are not."*

**Postulates — 3.0 splits these across two levels, a structure 4.0 abandons.**

- **Existence:** *"Mechanisms in a state exist. A system is a set of mechanisms."*
- **Composition:** *"Elementary mechanisms can be combined into higher order ones."*
- Then: *"The next three postulates, information, integration, and exclusion, apply **both to individual mechanisms and to systems of mechanisms**."*

*At the level of mechanisms:*

- **Information:** *"A mechanism can contribute to consciousness only if it specifies 'differences that make a difference' within a system. That is, a mechanism in a state generates information only if it constrains the states of a system that can be its possible causes and effects – its **cause-effect repertoire**. The more selective the possible causes and effects, the higher the cause-effect information *cei* specified by the mechanism."*
- **Integration:** *"A mechanism can contribute to consciousness only if it specifies a cause-effect repertoire (information) that is irreducible to independent components. Integration/irreducibility φ is assessed by partitioning the mechanism and measuring what difference this makes to its cause-effect repertoire."*
- **Exclusion:** *"A mechanism can contribute to consciousness at most one cause-effect repertoire, the one having the maximum value of integration/irreducibility φ^Max. This is its **maximally irreducible cause-effect repertoire (MICE**, or quale sensu stricto). If the MICE exists, the mechanism constitutes a **concept**."*

*At the level of systems of mechanisms:*

- **Information:** *"A set of elements can be conscious only if its mechanisms specify a set of 'differences that make a difference' to the set – i.e. a **conceptual structure**. A conceptual structure is a constellation of points in **concept space**, where each axis is a possible past/future state of the set of elements… The higher the number of different concepts and their φ^Max value, the higher the conceptual information CI."*
- **Integration:** *"A set of elements can be conscious only if its mechanisms specify a conceptual structure that is irreducible to non-interdependent components (strong integration). Strong integration/irreducibility Φ is assessed by partitioning the set of elements into subsets with **unidirectional cuts**."*
- **Exclusion:** *"Of all overlapping sets of elements, only one set can be conscious – the one whose mechanisms specify a conceptual structure that is maximally irreducible (**MICS**) to independent components. A local maximum of integrated information Φ^Max (over elements, space, and time) is called a **complex**."*

### IIT 4.0 (2023), in the paper's order

**Framing**, verbatim: *"**That experience exists—that 'there is something it is like to be'—is immediate and irrefutable**, as everybody can confirm, say, upon awakening from dreamless sleep. Phenomenal existence is immediate in the sense that my experience is simply there, directly rather than indirectly: I do not need to infer its existence from something else. **It is irrefutable because the very doubting that my experience exists is itself an experience that exists—the experience of doubting.** Thus, to claim that my experience does not exist is self-contradictory or absurd."*

**Zeroth axiom — Existence:** *"Experience exists: there is something."*

**The five axioms of phenomenal existence**, verbatim and complete:

> **Intrinsicality** — *"Experience is intrinsic: it exists for itself."*
> **Information** — *"Experience is specific: it is this one."*
> **Integration** — *"Experience is unitary: it is a whole, irreducible to separate experiences."*
> **Exclusion** — *"Experience is definite: it is this whole."*
> **Composition** — *"Experience is structured: it is composed of distinctions and the relations that bind them together, yielding a phenomenal structure that feels the way it feels."*

**Their own worked illustration**, verbatim: *"if I awaken from dreamless sleep and experience the white wall of my room, my bed, and my body, the experience not only exists, immediately and irrefutably, but 1) it exists **for me**, not for something else, 2) it is **specific** (this one experience, not a generic one), 3) it is **unitary** (the left side is not experienced separately from the right side), 4) it is **definite** (it includes the visual scene in front of me—neither less, say, its left side only, nor more, say, the wall behind my head), 5) it is **structured** by distinctions (the wall, the bed, the body) and relations (the body is on the bed, the bed in the room)."*

**The completeness claim**, verbatim: *"IIT takes the above set of axioms to be **complete**: there are no further properties of experience that are essential."* Candidates explicitly **rejected** as non-essential: **space, time, change, subject–object distinction, intentionality, sense of self, figure–ground segregation, situatedness, will, affect** — *"experiences lacking each of these candidate properties are **conceivable**… **They are also achievable**, as revealed by altered states of consciousness reached through dreaming, meditative practices, or drugs."*

**Zeroth postulate — Existence:** *"The substrate of consciousness can be characterized operationally by cause–effect power: its units must take and make a difference."*

**The five postulates of physical existence**, verbatim and complete, with their attached gloss sentences:

> **Intrinsicality** — *"Its cause–effect power must be intrinsic: it must take and make a difference within itself."*
> **Information** — *"Its cause–effect power must be specific: it must be in this state and select this cause–effect state."* *Gloss:* *"This state is the one with maximal intrinsic information (ii), a measure of the difference a system takes or makes over itself for a given cause state and effect state."*
> **Integration** — *"Its cause–effect power must be unitary: it must specify its cause–effect state as a whole set of units, irreducible to separate subsets of units."* *Gloss:* *"Irreducibility is measured by integrated information (φ) over the substrate's minimum partition."*
> **Exclusion** — *"Its cause–effect power must be definite: it must specify its cause–effect state as this whole set of units."* *Gloss:* *"This is the set of units that is maximally irreducible, as measured by **maximum φ (φ\*)**. This set is called a **maximal substrate**, also known as a **complex**."*
> **Composition** — *"Its cause–effect power must be structured: subsets of its units must specify cause–effect states over subsets of units (**distinctions**) that can overlap with one another (**relations**), yielding a cause–effect structure or **Φ-structure** ('Phi-structure') that is the way it is."*

Then, verbatim: *"Distinctions and relations, in turn, must **also** satisfy the postulates of physical existence: they must have cause–effect power, within the substrate of consciousness, in a specific, unitary, and definite way (**they do not have components, being components themselves**). They thus have an associated φ value. **The Φ-structure unfolded from a complex corresponds to the quality of consciousness. The sum total of the φ values of the distinctions and relations that compose the Φ-structure measures its structure integrated information Φ ('big Phi,' 'structure Phi') and corresponds to the quantity of consciousness.**"*

**Necessity and sufficiency**, verbatim: *"the physical properties characterized by the postulates are **necessary and sufficient** for an entity to be conscious. They are necessary because they are needed to account for the properties of experience that are essential, in the sense that it is **inconceivable** for an experience to lack any one of them. They are also sufficient because no additional property of experience is essential."*

### The method, and the identity claim

**Why start from phenomenology**, verbatim: *"IIT's starting point is **experience itself rather than its behavioral, functional, or neural correlates**. Furthermore, in IIT '**physical**' is meant in a **strictly operational sense**—in terms of what can be observed and manipulated."* And: *"Unlike phenomenal existence, which is immediate and irrefutable (an **axiom**), physical existence is an **explanatory construct** (a **postulate**), and it is assessed operationally (**from within consciousness**): in physical terms, **to be is to have cause–effect power**. In other words, something can be said to exist physically if it can 'take and make a difference'—bear a cause and produce an effect—**as judged by a conscious observer/manipulator**."*

**The inference step**, verbatim: *"The next step of IIT is to formulate the essential phenomenal properties (the axioms) in terms of corresponding physical properties (the postulates). This formulation is an '**inference to a good explanation**' and rests on basic assumptions such as **realism, physicalism, and atomism**."*

**The identity claim**, verbatim: *"IIT proposes a fundamental **explanatory identity**: **an experience is identical to the cause–effect structure unfolded from a maximal substrate.** Accordingly, all the specific phenomenal properties of any experience must have a good explanation in terms of the specific physical properties of the corresponding cause–effect structure, **with no additional ingredients**."* Expanded: *"every property of an experience is accounted for in full by the physical properties of the Φ-structure unfolded from a maximal substrate (a complex) in its current state, with no further or '**ad hoc**' ingredients. That is, there must be a **one-to-one correspondence** between the way the experience feels and the way distinctions and relations are structured. **Importantly, the identity is not meant as a correspondence between the properties of two separate things.** Instead, the identity should be understood in an **explanatory** sense: the intrinsic (subjective) feeling of the experience can be explained extrinsically (objectively, i.e., operationally or physically) in terms of cause–effect power."*

**Box 1, "Methodological guidelines of IIT" — the criteria for a "good explanation,"** verbatim: *"an explanation is good if it can account for a broad set of facts (**scope**), does so in a unified manner (**synthesis**), can explain facts precisely (**specificity**), is internally coherent (**self-consistency**), is coherent with our overall understanding of things (**system consistency**), is simpler than alternatives (**simplicity**), and can make testable predictions (**scientific validation**)."* Box 1 also states **operational reductionism/atomism** (*"cause–effect power 'all the way down'… Eventually, this would leave neither room nor need to assume intrinsic properties or laws"*) and the **intrinsic perspective** (*"information in IIT must be relative to the specific state the entity is in, rather than an average of states as assessed by an external observer… evaluated based on the **uniform distribution** of possible states, as captured by the entity's TPM, rather than on an **observed** probability distribution"*).

**Box 2, "Ontological principles of IIT" — three principles, all load-bearing in the formalism:**

- **Principle of being:** *"to be is to have cause–effect power."* Explicitly compared to Plato's Eleatic principle (*Sophist*) and Dharmakīrti — **with the difference flagged**: *"the Eleatic principle is enunciated as a **disjunction** (either to do something… or to be affected…), whereas IIT's principle of being is presented as a **conjunction** (take **and** make a difference)."*
- **Principle of maximal existence:** *"**when it comes to a requirement for existence, what exists is what exists the most.**"* **This is what licenses every `argmax`** — the cause–effect state, the complex's borders, the distinctions' purviews, and the unit grain.
- **Principle of minimal existence:** *"**when it comes to a requirement for existence, nothing exists more than the least it exists.**"* **This is what licenses every `min`** — the MIP, and the min over cause/effect sides.
- ⚠️ S1 Notes footnote 9 mentions a fourth, unpublished: *"**Principle of becoming**, which states that powers become what powers do."*

---

## Φ precisely

### What it measures, and what it is NOT

**It is not Shannon information about external messages.** In 3.0/4.0 Φ is defined over **interventional (`do`-operator)** conditional probabilities of the system over *itself*. 4.0's formal setup, verbatim: *"we assume a complete description of the substrate, which means that we can determine the conditional probabilities… for every system state, with `p(ū|u) = p(ū|do(u))`, where the 'do-operator' do(u) indicates that u is imposed by **intervention**."* Background units are **causally marginalized**, *"so that causes and effects are evaluated from the **intrinsic perspective** of the system."*

**4.0 even coins a unit to mark the break with Shannon**, verbatim: *"The intrinsic information ii is quantified in units of **intrinsic bits, or ibits**, to distinguish it from **standard information-theoretic measures (which are typically additive)**. Formally, the ibit corresponds to a point-wise information value (measured in bits) **weighted by a probability**."*

⚠️ **Terminology change to flag: "qualia space" (2.0) and "concept space" (3.0) do not appear in IIT 4.0 at all** (grep-verified). The 4.0 object is the **Φ-structure** of distinctions and relations.

### The IIT 4.0 formalism, step by step

**Intrinsic information** (Eq 5, effect side): `ii_e(s, s̄) = p_e(s̄|s) · log( p_e(s̄|s) / p_e(s̄) )`, where the unconstrained `p_e(s̄)` is the marginal *"averaged across all possible current states of S **with equal probability**."* Cause side (Eq 7): `ii_c(s, s̄) = p_c←(s̄|s) · log( p_c(s|s̄) / p_c(s) )` — ⚠️ **note the asymmetry: the *selectivity* term uses the backward (Bayes) probability but the *informativeness* term uses forward probabilities on both sides.**

- **Informativeness** = the log term. Verbatim: *"a system S in state s has cause–effect power (it takes and makes a difference) if it **raises the probability of a possible effect state compared to chance**."* Property: *"Informativeness is **additive** over the number of units… (**expansion**)."*
- **Selectivity** = the probability prefactor. Verbatim: *"cause–effect power over a specific cause or effect state depends not only on the deviation from chance it produces, but also on **how its probability is concentrated on that state, rather than being diluted over other states**… if p < 1, the system's causal power becomes **subadditive (dilution)**."*
- **The central tension**, verbatim: *"taking the product of informativeness and selectivity leads to a tension between **expansion and dilution**: a larger system will tend to have higher informativeness… but it will also tend to have lower selectivity because it will have a larger repertoire of states to select from."* Consequence: *"intrinsic information is **reduced by indeterminism and degeneracy**."*
- **Maximal cause–effect state** (Eq 12): `s'_e = argmax_{s̄ ∈ Ω_S} ii_e(s, s̄)` — **by the principle of maximal existence.**

**Intrinsic Difference (ID) — the three uniqueness properties**, verbatim: *"a measure of the difference between two probability distributions which **uniquely satisfies three properties** (causality, intrinsicality, and specificity) that align with the postulates of IIT (but also have independent justification):*

- ***causality (Existence):** the measure is zero if and only if the system does not make a difference*
- ***intrinsicality (Intrinsicality):** the measure increases if the system is expanded without noise (expansion) and decreases if the system is expanded without signal (dilution)*
- ***specificity (Information):** the measure reflects the cause–effect power of a specific state over a specific cause and effect state."*

⚠️ **Honest caveat they themselves state:** *"on the effect side, ii_e is formally equivalent to the ID… On the cause side, the application of Bayes rule… means that **ii_c is not strictly equivalent to the ID** between two probability distributions."* Primary source for ID: **Barbosa, Marshall, Streipert, Albantakis & Tononi, "A measure for intrinsic information," *Scientific Reports* 2020;10(1):18803**, doi:10.1038/s41598-020-75943-4.

**Directional system partitions** (Eq 15): `θ = {S^(1)_δ1, …, S^(k)_δk}` with `δ_i ∈ {←, →, ↔}` cutting inputs, outputs, or both, replacing severed connections with independent noise. **Why directional**, verbatim: *"Directional partitions are necessary because, from the intrinsic perspective of a system, **a subset of units that cannot affect the rest of the system, or cannot be affected by it, cannot truly be a part of the system.**"* **Partitions allow k ≥ 2 parts, not just bipartitions.**

**System integrated information φ_s:**

- Eq 19: `φ_e(T_e, s, θ) = p_e(s'_e|s) · |log( p_e(s'_e|s) / p_e^θ(s'_e|s) )|⁺` — same form as `ii_e` *"**with the partitioned effect probability taking the place of the unconstrained (marginal) probability**."* `|·|⁺` is the positive part operator.
- Eq 21, **min over cause/effect sides**: `φ_s(θ) = min{ φ_c(θ), φ_e(θ) }` — *"By the zeroth postulate, existence requires cause **and** effect power… By the **principle of minimal existence**, then, system integrated information for a given partition is the minimum of its irreducibility on the cause and effect sides."*
- Eq 22–23, **min over partitions (the MIP)**: `θ' = argmin_{θ∈Θ(S)} [ φ_s(T_e,T_c,s,θ) / max_{T'_e,T'_c} φ_s(T'_e,T'_c,s,θ) ]`.

### The MIP and why the minimum is taken

**The rationale is identical in spirit across all four versions: a system is only as integrated as its weakest fault line.**

- **1.0:** *"a subset can integrate little information if there is a way to partition it in two parts A and B such that EI(A↔B) is low: the effective information across that bipartition is the **limiting factor**… Therefore… we should search for the bipartition(s) of S for which EI(A↔B) reaches a minimum (the informational '**weakest link**')."*
- **2.0:** *"for any system, we need to find the informational 'weakest link', i.e. the decomposition into those parts that are most independent (least integrated)."*
- **3.0:** *"integrated information is evaluated across the minimum information partition (MIP), the partition that makes the **least difference** to the cause and effect repertoires (in other words, the minimum 'difference' partition)."*
- **4.0** (principle of minimal existence): *"given that a system can only exist as one system if it is irreducible, **its degree of irreducibility should be assessed over the partition across which it is least irreducible**."*

### ⚠️ The normalization oscillation — sources genuinely differ by version

| Version | MIP normalization |
|---|---|
| **1.0** | minimize the **normalized** quantity, **report un-normalized** |
| **2.0** | **normalized** — *"the size of the smallest a priori repertoire of a part multiplied by the number of other parts"* |
| **3.0** | **explicitly DROPPED** — *"In IIT 3.0 this is no longer necessary"* |
| **4.0** | **RESTORED**, with a new normalizer and a different justification |

**4.0's justification**, verbatim: *"**The normalization term… ensures that φ_s is evaluated fairly over a system's fault lines by assessing integration relative to its maximum possible value over a given partition. Using the relative integrated information quantifies the strength of the interactions between parts in a way that does not depend on the number of parts and their size.**"* The normalizer is proved to be `Σ_i |S^(i)|·|X^(i)|`, *"the maximal possible number of 'connections' (pairwise interactions) affected by θ."*

**The worked consequence**, verbatim: *"the MIP will correctly identify the fault line dividing a system into two large subsets of units linked through a few interconnected units (**a 'bridge'**), rather than defaulting to partitions between individual units and the rest of the system."* Tie-break: **largest un-normalized φ_s** (maximal existence). Also: *"Defining θ' as in (23)… ensures that **φ_s = 0 if the system is not strongly connected** in graph-theoretic terms."*

### small φ vs big Φ — the critical correction

**The terms shift meaning between 3.0 and 4.0.**

**IIT 3.0** (from its glossary, verbatim):

- **φ, "small phi"** = mechanism-level: *"How irreducible the cause-effect repertoire specified by a mechanism is compared to its minimum information partition (MIP)."*
- **Φ, "big phi"** = system-level **integrated conceptual information**: *"How irreducible the conceptual structure specified by a set of mechanism is compared to its minimum information partition (MIP)."* Computed as the **extended EMD** between the whole's constellation and the partitioned constellation.
- **Complex = Φ^Max**: *"A set of elements within a system that generates a **local maximum of integrated conceptual information Φ^Max**."* **So in 3.0, big Φ selects the complex.**

**IIT 4.0 — the roles split apart:**

- ⚠️ **`φ_s` ("system phi") is ALSO called "small phi"**, verbatim: *"the system integrated information (φ_s), **also called 'small phi'**, quantifies the extent to which system S in state s has cause–effect power over itself as one system (i.e., irreducibly). φ_s is thus a **quantifier of irreducible existence**."* **It is *not* compositional.**
- **`φ_d`** = distinction (mechanism) integrated information, Eq 47: `φ_d(m) = min( φ_c(m), φ_e(m) )`, each side being `max_{Z⊆S} φ(m, Z)` over purviews.
- **`φ_r`** = relation integrated information, Eq 55 — *"guarantees that the integrated information of a relation **cannot exceed the integrated information of its weakest distinction**."*
- **Φ ("big Phi", "structure Phi")**, Eq 59: `Φ(T_e, T_c, s*) = Σ_{C(T_e,T_c,s*)} φ` — **a plain sum** over all distinctions and relations. Verbatim: *"**Note that Φ is not computed based on a partition (as system phi), but rather a sum of the integrated information within the structure** (where each term of the sum was computed by partitioning)."*
- **⇒ In 4.0 the complex is selected by maximum φ_s, NOT by maximum Φ.** Eq 24–25: `φ_s*(T_e,T_c,u_k) = max_{S⊆U_k} φ_s(…)`, `S_k* = argmax_{S⊆U_k} φ_s(…)`. **Φ is then computed *from* the already-identified complex.** This is exactly what the S2 Text flags: complexes are identified by φ_s *"as in IIT 2.0 but **unlike IIT 3.0**, which evaluated integration after composition."*

### Exclusion, the complex, and the Φ-structure

**4.0 exclusion, verbatim:** *"In general, multiple candidate systems with overlapping units may have positive values of φ_s. By the exclusion postulate, the substrate of consciousness must be definite… But which one? Once again, we employ the **principle of maximal existence**: among candidate systems competing over the same substrate with respect to an essential requirement for existence, in this case irreducibility, **the one that exists is the one that exists the most**. Accordingly, the **maximal substrate, or complex**, is the candidate substrate with the maximum value of system integrated information (φ_s*), and **overlapping substrates with lower φ_s are thus excluded from existence**."*

**Sufficient condition** (Eq 26), verbatim: *"specifying a maximum of integrated information φ_s* compared to all overlapping systems — `S ∩ S̃ ≠ ∅ ⇒ φ_s(s) > φ_s(s̃), ∀ S ≠ S̃ ⊆ U` — is a **sufficient** requirement for a system S ⊆ U to be a complex."*

**Recursive condensation (new in 4.0)**, verbatim: *"the substrate with maximum φ_s* is identified as a complex, the corresponding units are **excluded from further consideration**, the remaining units are searched for the next maximal substrate"*; `U_{k+1} = U_k \ S_k*` until exhausted. *"this recursive search for maximal substrates '**condenses**' the universe U₀ in state u₀ into a **disjoint (non-overlapping) and exhaustive set of complexes—the first complex, second complex, and so on**."* **Compare 1.0 and 2.0, where complexes could overlap and nest; and 3.0's "major complex" plus non-overlapping "minor complexes."** Tie-handling: *"If the maximal substrate S_k* is not unique, and all tied systems overlap, the next best system that is unique is chosen instead."*

**Φ-structure** (Eq 57–58): `C(D) = D ∪ R(D)`; *"The cause–effect structure specified by a maximal substrate—a complex—is also called a **Φ-structure**."* Sub-structures are **Φ-folds**:

- **distinction Φ-fold** — a distinction plus the relations binding it, *"which form its **context**"*;
- **compound Φ-fold** — *"a relevant part of a Φ-structure because it can be **accessed or manipulated** by changing the state, connections, or functioning of a part of the substrate"*;
- **content Φ-fold** — *"a subset of distinctions that are **highly interrelated**, regardless of the mechanisms and units that specify them."*

**The ontological punchline**, verbatim: *"**By IIT, a complex S\* does not exist as such, but exists 'unfolded' into its Φ-structure**, with all the causal distinctions and relations that compose it. In other words, a substrate is what can be observed and manipulated 'operationally' from the extrinsic perspective. From the intrinsic perspective, what truly exists is a complex with all its causal powers unfolded—**an intrinsic entity that exists for itself, absolutely, rather than relative to an external observer**."*

**Relations** (Eq 51–52): `r(d) = (d, f(d), φ_r)`. *"A relation that binds together h = |d| distinctions is an **h-degree relation**."* *"a relation r(d) with |d| > 1 may comprise up to **3^|d| faces**."* **The important point**, verbatim: *"the fact that the two distinctions overlap irreducibly **can only be captured by a relation and not by a high-order distinction**."* Relations require **congruent** overlap. Distinctions themselves only count if *"congruent with the system's overall cause–effect state (z_c* ⊆ s_c*, z_e* ⊆ s_e*)."*

### Evaluation over all subsets, all partitions, and all grains

Verbatim (4.0 composition step): *"As required by composition, unfolding the full cause–effect structure of the system S in state s requires assessing the irreducible cause–effect power of **every subset of units** within S."* Purview exclusion (Eq 45): `z_e*(m) = argmax_{Z⊆S} φ_e(m, z'_e(m,Z))` — **a max over all purviews `Z ⊆ S`.** Distinction MIP (Eq 43) requires *"a search over **all possible partitions** θ ∈ Θ(M,Z)"* — and ⚠️ these **"disintegrating partitions" differ formally from system partitions.**

**Grain dependence**, verbatim: *"Above, we presented how to determine the borders of a complex within a larger system U, **assuming a particular grain** for the units. **In principle, however, all possible grains should be considered.** In the brain, for example, the grain of units could be **brain regions, groups of neurons, individual neurons, sub-cellular structures, molecules, atoms, quarks, or anything finer**, down to hypothetical atomic units of cause–effect power. For any unit grain—neurons, for example—**the grain of updates could be minutes, seconds, milliseconds, micro-seconds**, and so on. However, by the exclusion postulate, the units that constitute a system S must also be definite, in the sense of having a **definite grain**… the 'winning' grain is the one that ensures maximally irreducible existence (φ_s*)."*

**Units must themselves satisfy the postulates**, verbatim: *"**units themselves must also be maximally irreducible**… Otherwise it would be possible to '**make something out of nothing**.'"* But with a twist: *"in contrast to systems, units only need to be maximally irreducible **within**, because they do not exist as complexes in their own right."* And the selection criterion differs from the units' own interest: *"the set of (macro) units that define a complex is the one that **maximizes the existence of the complex to which the units belong, rather than their own existence**."*

**S1 Notes footnote 2 draws the AI-relevant consequence**, verbatim: *"a substrate unit must be maximally irreducible within, which is **likely the case for 'real' neurons in the brain, but is not the case for 'virtual,' simulated neurons** in a computer program."*

**State dependence, with their own numbers (4.0 Fig 7):** a system in state `ABcdE` is *"a maximal substrate with **φ_s = 1.1 ibits** and a Φ-structure composed of **23 distinctions and their 13740 relations**."* Change one unit's state and the structure changes; **inactivate** unit E (fix it OFF) and *"the inactivated unit cannot contribute to the complex or Φ-structure anymore. The complex is now constituted of four units (ABcd), with only **14 distinctions and markedly reduced structure integrated information (Φ = 3.35)**."* Contrast with a "large" but chain-like substrate: *"despite the 'large' substrate, the Φ-structure it specifies has **low structure integrated information (Φ = 7.65)**… because the system's Φ-structure is composed **exclusively of first-order distinctions**."* And a 6-unit specialized lattice: *"Out of **63 possible distinctions**, the Φ-structure comprises **27 distinctions** with causes and effects congruent with the system's maximal cause–effect state."*

---

## Computational intractability — the full record

### The scaling claims, as published

- **Candidate systems:** `2ⁿ − 1` non-empty subsets. IIT 1.0 already spelled out the loop: *"we consider every possible subset S of m elements out of the n elements of a system, starting with subsets of two elements (m = 2) and ending with a subset corresponding to the entire system (m = n)."*
- **IIT 4.0**, verbatim (MathML-verified): *"The number of distinctions specified by an optimally connected, specialized system is **bounded above by 2ⁿ−1**, and that of the relations among as many distinctions is **bounded by 2^(2ⁿ−1) − 1**."* **Doubly exponential.**
- **Zaeemzadeh & Tononi 2024**, verbatim: *"a system consisting of N units can potentially contain as many as **2^(2^N−1) − 1** causal relations. Any nonempty subset of units can define a distinction and any nonempty subset of distinctions can potentially define a relation."* They use *"**hyper-exponentially**"*, *"**super exponential growth**"*, and predict *"**hyper-astronomical values of Φ**."*
- **Partitions:** 4.0 allows `k ≥ 2`-part **directional** set partitions, so the count is a direction-weighted Bell polynomial, `Σ_{q≥2} S(n,q)·3^q ≈ B_n(3)` ⚠️ (this exact expression is from PyPhi's 2.0 **documentation**, not a paper).
- **Toker & Sommer 2019**, verbatim: *"the measurement of integrated information involves a combinatorial search for the informational 'weakest link' of a network, a process whose computation time **explodes super-exponentially** with network size."* With concrete Bell numbers: *"a network of **8 nodes can be partitioned 4,140 ways**, a network of **10 nodes can be partitioned 115,975 ways**, and a network of **12 nodes can be partitioned 4,213,597 ways**"*; restricting to bipartitions still leaves *"a **20-node network can be bipartitioned 524,287 ways** and a **30-node network can be bipartitioned 536,870,911 ways**."* Citation: **Toker & Sommer, "Information integration in large brain networks," *PLOS Computational Biology* 2019;15(2):e1006807.**

  ⚠️ **Important caveat: Toker & Sommer compute Φ^G (geometric integrated information) on Gaussian time series, NOT IIT's Φ.** They also could not run Queyranne's algorithm above 50 nodes: *"the computation time… increased exponentially, making its application to networks with **more than 50 nodes prohibitively expensive**."*
- **IIT 4.0's own summary**, verbatim: *"The number of possible systems, of system partitions, of candidate distinctions—**each with their partitions and relations**—is the result of **multiple, nested combinatorial explosions**. Moreover, these observations, manipulations, and calculations would need to be **repeated at many different grains, with many rounds of maximizations**."*

### Is there a published hardness result? — NO. Verified absence; do not assert one

| Claim | Source | Status |
|---|---|---|
| Computing Φ exactly is **#P-hard** | Aaronson blog 2014 | *"Presumably"* — **conjecture, blog, non-peer-reviewed** |
| Approximating Φ is **NP-hard** | Aaronson blog 2014 | *"I conjecture"* — **conjecture, blog** |
| Approximating Φ ∈ **AM** | Aaronson, blog comment #180 | sketched derivation, **blog** |
| Exact Φ scales as **O(13^m)** | Hanson & Walker 2023, *Neurosci Conscious* | **peer-reviewed counting argument, not a hardness proof**; disputed |
| Exact Φ scales as **O(n·53ⁿ)** | Mayner et al. 2018, *PLOS Comput Biol* | **peer-reviewed**, derivation not shown |
| MIP search is **super-exponential** | Toker & Sommer 2019 | **peer-reviewed** (for Φ^G) |
| Φ_MI is **submodular ⇒ MIP in polynomial time** | Kitazono et al. 2018 | **peer-reviewed** (for the **superseded 2004** Φ) |

**Aaronson, verbatim** ("Why I Am Not An Integrated Information Theorist (or, The Unconscious Expander)," *Shtetl-Optimized*, 21 May 2014 — **a blog, not peer-reviewed**): *"I leave it as a challenge for interested readers to pin down the computational complexity of approximating Φ… **(Presumably Φ will be #P-hard to calculate exactly, but only because calculating entropy exactly is a #P-hard problem—that's not interesting.) I conjecture that approximating Φ is an NP-hard problem**, even for restricted families of f's like NC⁰ circuits—which invites the amusing thought that God, or Nature, would need to solve an NP-hard problem just to decide whether or not to imbue a given physical system with consciousness!"* Upper bound, verbatim: *"**I don't know that this problem is in NP—the best I can observe is that it's in AM.**"* In comment #180 he adds that entropy estimation is SZK-complete and *"using that, one can derive that the problem of approximating Φ is in the complexity class **AM** (Arthur-Merlin). **I leave it as a challenge for others to show that approximating Φ is NP-hard.**"*

⚠️ **Two caveats on citing Aaronson:** (a) it is a blog; (b) **his Φ is the 1.0/2.0 EI-based definition**, `Φ(A,B) = EI(A→B)+EI(B→A)` minimized over bipartitions — **not 3.0 or 4.0.**

What he *did* compute: for a modified Vandermonde system, *"this system's Φ equals **half of its entire information content**"*, and *"if n were **10¹⁴** or so… this system's Φ would exceed any plausible upper bound on the integrated information content of the human brain"*; of expanders, *"I feel 100% confident in saying that the so-constructed expander graphs are **not conscious**."* In the follow-up post ("Giulio Tononi and Me: A Phi-nal Exchange," 30 May 2014) he gives *"a √n×√n square grid… **Φ-value of about √n**… logic gates arranged in a 1-dimensional line would produce a tiny Φ-value (**Φ=O(1)**)"* — **and Koch concurs in a comment (#72): *"we agree on a 1-D array having a small but non-zero Phi value while Phi for a 2-D array increases as √(# of nodes)."***

⚠️ **Hanson & Walker — all three papers checked; NONE states a complexity class.** Zero occurrences of "NP-hard" or "#P."

- Hanson & Walker, "Integrated Information Theory and Isomorphic Feed-Forward Philosophical Zombies," *Entropy* 2019;21(11):1073 — no complexity statements.
- Hanson & Walker, "Formalizing falsification for theories of consciousness across computational hierarchies," *Neuroscience of Consciousness* 2021;2021(2):niab014 — computational **hierarchies** (FSA vs CSA), not complexity classes.
- **Hanson & Walker, "On the non-uniqueness problem in integrated information theory," *Neuroscience of Consciousness* 2023;2023(1):niad014** — **this one has a section literally titled "On the computational complexity of Φ," the only published derivation found.** Their chain: `2S(n,2)+1` directional bipartitions (Stirling numbers of the second kind) × `2ⁿ−1` mechanisms × `2Σ_k C(n,k)S(k,2) = 2(3ⁿ)` elementary distance calculations `≈ 12ⁿ` per subsystem; then `Σ_n C(m,n)12ⁿ = 13^m` for the global system. Verbatim conclusion: *"**For all but the smallest m values, the computational resources required to actually calculate Φ^max are impossible to realize.**"* And: *"considering the system as a whole is both **computationally intractable**… and philosophically challenging in all but the simplest cases."* **Their own corpus: "small systems (2–4 nodes)." They also tabulate every published Φ value they could find — all 2–5 nodes.**

### PyPhi

**Mayner, Marshall, Albantakis, Findlay, Marchman & Tononi, "PyPhi: A toolbox for integrated information theory," *PLOS Computational Biology* 2018;14(7):e1006343**, doi:10.1371/journal.pcbi.1006343; arXiv:1712.09644.

**The stated limit, verbatim:**

> *"PyPhi's main limitation is that the algorithm is exponential time in the number of nodes, **O(n 53ⁿ)**. This is because the number of states, subsystems, mechanisms, purviews, and partitions that must be considered each **grows exponentially** in the size of the system. **This limits the size of systems that can be practically analyzed to ~10–12 nodes.**"*

⚠️ **Sources disagree on the exponent, and this is an easy error to make.** Tag-stripped text reads as `O(n⁵3ⁿ)`; **the raw PLOS JATS markup is `<italic>O</italic>(<italic>n</italic>53<sup><italic>n</italic></sup>)` — only the final n is superscripted, so the published expression is `O(n·53ⁿ)`, base 53.** The authors' own arXiv LaTeX confirms: `\(O(n 53^n)\)`. Hanson & Walker 2023 also read it as base-53 and contrast it with their own result: their timings are *"within an order of magnitude of the calculated O(13^m) scaling but **off by 40 orders of magnitude from [O(53^m)] scaling**."* **However**, PyPhi's *current* (2026) documentation renders the same result as `O(n⁵3ⁿ)` and derives the base-3 justification (*"the base is 3 because each unit is in the mechanism, the purview, or neither"*). **Recommended wording: "published as O(n·53ⁿ); the project's current documentation renders the same result as O(n⁵·3ⁿ)." Do not present either as uncontested.**

**Timings, verbatim:** *"calculating the major complex of systems of three, five, and seven stochastic majority gates, connected in a circular chain of bidirectional edges, takes **~1 s, ~16 s, and ~2.75 h** respectively (parallel evaluation of system cuts, **32 × 3.1GHz CPU cores**). Using the 'cut one' approximation, these calculations take **~1 s, ~12 s, and ~0.63 h**."*

**TPM representation:** state-by-node form has *"**2ⁿ × n** entries instead of **2ⁿ × 2ⁿ**."* **EMD cost:** *"**O(n 2^{3n})** where n is the number of nodes in the purview"*; an analytical shortcut for *effect* repertoires (valid under conditional independence) drops this to **O(n)** and *"can be used for **half of all repertoire calculations**."*

**Approximations (disabled by default), verbatim:**

- `CUT_ONE_APPROXIMATION` — *"Instead of evaluating the partitioned CES for each of the **2ⁿ** unidirectional bipartitions of the system, only those **2n** bipartitions are evaluated that sever the edges from a single node to the rest of the network or vice versa… provides an **upper bound** on the exact Φ value."*
- `ASSUME_CUTS_CANNOT_CREATE_NEW_CONCEPTS` — *"only those mechanisms are taken into account that already specify concepts in the unpartitioned CES… **Note, however, that this approximation provides neither a theoretical upper nor lower bound** on the exact Φ value."*
- **Exact (non-approximate) optimizations:** strong-connectivity pruning (*"if the subsystem is not strongly connected then **Φ is necessarily zero**"*), block-factorability of repertoires from the connectivity matrix, the analytical EMD, and memoization/caching.
- ⚠️ `PARALLEL` and `WELCOME_OFF` are **not found** in the paper; treat those config names as unverified.
- ⚠️ **The published PyPhi 1.x did not search over grains at all**, verbatim: *"a module for calculating Φ over multiple spatial and temporal scales, **as theoretically required by the exclusion postulate** (in the current version, the Network **is assumed** to represent the system at the spatiotemporal timescale at which Φ is maximized)."*

**PyPhi 2.0 exists and implements IIT 4.0 — verified.** Repo `github.com/wmayner/pyphi` (default branch `main`, last push 2026-11-02). PyPI releases **2.0.0rc1 (2026-09-15) through 2.0.0rc4 (2026-10-13)**; ⚠️ **last stable non-rc is 1.2.0 (2019-06-22), so `pip install pyphi` still yields 1.x.** README, verbatim: *"It implements **IIT 4.0** (Albantakis et al., 2023; Mayner, Marshall & Tononi, 2026)… The current release on PyPI is the **2.0** line, which implements IIT 4.0… The **1.x** line (IIT 3.0) remains available: install `pyphi<2`."* It also ships *"**Analytical bounds** — bound Φ and its components from above without the full combinatorial computation (Zaeemzadeh & Tononi, 2024)."*

**PyPhi 2.0's "Computational complexity" documentation page** ⚠️ (documentation, not peer-reviewed) is the densest scaling source available, and **it reports a lower ceiling for 4.0 than for 3.0**:

| Formalism | Stage | Dominant cost | Practical ceiling |
|---|---|---|---|
| IIT 4.0 | distinctions (CES) | ≳2ⁿ mechanisms | **~6–8 units** |
| IIT 4.0 | relations | up to 2^(2ⁿ−1)−1 | **~6–8 units** |
| IIT 4.0 | system φ_s | B_n(3) directed set partitions | **~10–12 units** |
| IIT 3.0 | CES / subsystem Φ / major complex | O(n⁵3ⁿ) / 6ⁿ / 7ⁿ | **~10–12 units** |

Verbatim: *"The single most expensive term anywhere in IIT is the 4.0 relation count, 2^(2ⁿ−1)−1 (**doubly exponential**)."* **Measured realized counts for the ring family:** n=2 → 3 distinctions / 5 relations; n=3 → 7/127; n=4 → 15/6,879; **n=5 → 31/1,413,375.** *"Without a per-evaluation time budget, IIT 4.0 CES at n=6 takes about **30 minutes** with analytical relations."*

**And the key caution**, verbatim: *"**Neither stack changes the exponential base** — they lower the constant and the polynomial factor, buying a unit or two, **not a new complexity class**. The base is fixed by the formalism."* Plus a conceptual point worth quoting anywhere: cheaper partition schemes are *"**formalism choices** — change *which* quantity is computed… **a different scheme is a different definition, not a faster route to the same number**."*

⚠️ The same page disputes Hanson & Walker's `O(13^m)` as *"erroneous because it treats each distance evaluation as a constant-time operation"* — **documentation, not a peer-reviewed rebuttal. Flag the three-way disagreement: `O(n·53ⁿ)` vs `O(13^m)` vs `O(n⁵7ⁿ)`.**

### Tractable MIP search — the submodularity line

**Kitazono, Kanai & Oizumi, "Efficient Algorithms for Searching the Minimum Information Partition in Integrated Information Theory," *Entropy* 2018;20(3):173**, doi:10.3390/e20030173; arXiv:1712.06745. ⚠️ MDPI returned HTTP 403; content taken from the authors' arXiv source — **verify page-level detail against the published version before quoting.**

Abstract, verbatim: *"**The computational cost for exhaustively searching for the MIP grows exponentially with system size**, making it difficult to apply IIT to real neural data. It has been previously shown that, if a measure of Φ satisfies a mathematical property, **submodularity**, the MIP can be found in a **polynomial order**… However, although **the first version of Φ is submodular, the later versions are not**."*

- *"**Hidaka and Oizumi** showed that the computational cost for finding the MIP is reduced to **O(N³)** by utilizing **Queyranne's algorithm**."* ⚠️ The full Hidaka & Oizumi citation could not be resolved.
- **Measured:** *"the computational time of Queyranne's algorithm increases in polynomial order (**T ∝ N^3.066**), while that of the exhaustive search exponentially increases (**T ∝ 1.929^N**). For example, when **N = 100, Queyranne's algorithm takes ~197 sec while the exhaustive search takes 1.16 × 10²⁵ sec**."* For Φ_G: **O(N^4.776)**.
- **Their own stated limits:** *"If the system size is much larger (**N ≳ 100**), Queyranne's algorithm will be computationally very demanding"*; and crucially, *"the computational complexity of the algorithm for **K-partitions is O(N^{3(K−1)})**. **This is the main reason why we focused on bi-partitions.**"*
- ⚠️ **Sources disagree on Queyranne's accuracy:** Kitazono et al. report near-perfect MIP recovery (Φ_SI 100/100; Φ_G 100% normal, 97% block models), whereas **Toker & Sommer 2019 report perfect matches in only 1/50 (14-node) and 2/50 (16-node) networks**, mean Rand Index ~0.58. **Toker & Sommer attribute the discrepancy to normalized vs non-normalized Φ^G and say so explicitly.**

### Explicit proponent acknowledgments that Φ has never been computed for a brain

**IIT 3.0 (2014), "Limitations and future directions" — the clearest admission, verbatim:**

> *"**Directly applying this approach to physical systems of interest, such as brains, is unfeasible for several reasons:** i) One would need either to discretize the variables of interest or to extend the theoretical treatment to continuous variables. ii) For biological systems, one is usually limited to observable system states, and **the exhaustive perturbation of a system as the brain across all its possible states is unfeasible**. iii) Variables recorded in most neurophysiological experiments **may not correspond to the spatial and temporal grain at which integrated information reaches a maximum**, which is the appropriate level of analysis. **iv) The present analysis is unfeasible for systems of more than a dozen elements or so. This is because, to calculate Φ^Max exhaustively, all possible partitions of every mechanism and of every system of mechanisms should be evaluated, which leads to a combinatorial explosion, not to mention that the analysis should be performed at every spatio-temporal grain.** For these reasons, **the primary aim of IIT 3.0 is simply to begin characterizing, in a self-consistent and explicit manner, the fundamental properties of consciousness**… Hopefully, **heuristic measures** and experimental approaches inspired by this theoretical framework will make it possible to test some of the predictions of the theory."*

**IIT 4.0 (2023), verbatim:**

> *"Even though the entire framework of IIT is based on just a few axioms and postulates, **it is not possible in practice to exhaustively apply the postulates to unfold the cause–effect power of realistic systems**. **It is not feasible to perform all possible observations and manipulations to fully characterize a universal TPM, or to perform all calculations on the TPM that would be necessary to condense it exhaustively into complexes and unfold their cause–effect power in full.** … For these reasons, **a full analysis of complexes and their cause–effect structure can only be performed on idealized systems of a few units.**"*
> *"**Despite the infeasibility of an exhaustive calculation** of the relevant quantities and structures for a realistic system, IIT already provides considerable explanatory and predictive power…"*
> *"Developing tight approximations, as well as bounded estimates of a system's integrated information (φ_s and Φ), **is one of the main areas of ongoing research related to IIT**."*
> *"the IIT formalism will be applied to **extremely simple, simulated networks, rather than causal models of actual substrates**."*
> *"**IIT must still be considered as work in progress**"*; *"some of the **algorithmic choices remain open to further evaluation**"*, naming *"the proper treatment of background conditions and the resolution of ties."*

⚠️ **Noteworthy: IIT 4.0's two citations for its own infeasibility claim are to critics** — Barrett & Mediano 2019 (*JCS* 26(1–2):11–20, "The phi measure of integrated information is not well-defined for general physical systems") and Moyal, Fekete & Edelman 2020 (*Minds and Machines* 30(1):1–21).

**Zaeemzadeh & Tononi 2024 — the most direct and most recent statement, verbatim:**

> *"IIT is unique in providing an exact calculus for the quantity and quality of consciousness—from first principles and based on phenomenology. **However, unfolding cause-effect structures and determining the associated value of Φ exactly is not feasible for realistic systems, for several reasons. Among them is the difficulty of obtaining a system TPM at the right grain, the nested combinatorial explosions in assessing candidate unit grains and candidate complexes, as well as the composing distinctions and relations.** For these reasons, and **not unlike well-known precedents in statistical physics and quantum mechanics, it is essential to develop approximations and heuristics.** … By obtaining such bounds… **we should ultimately be able to make well-grounded estimates** about the presence and quantity of consciousness in different regions of the human brain."*

⚠️ **Flagged as NOT verified:** **Tononi, Boly, Massimini & Koch, *Nature Reviews Neuroscience* 2016;17(7):450–461** and **Koch, Massimini, Boly & Tononi, *Nature Reviews Neuroscience* 2016;17(5):307–321** — citations confirmed via Crossref/PubMed, but **both are paywalled and not in PMC; full text not obtained. Do not attribute quotes to either.** ⚠️ Also: **Tononi & Koch, *Phil Trans R Soc B* 2015;370(1668):20140167** — full text *was* read, and **it contains no explicit statement that Φ cannot be computed for a brain.** Its brain-vs-computer claims are hedged: *"**we suspect that** the computer would likely not form a large complex of high Φ^max, but break down into many mini-complexes of low Φ^max."* **Do not cite it for a computability admission.**

### Proxies, and the published statements that they are not Φ

| Measure | Symbol | Citation |
|---|---|---|
| Practical measures for time-series | Φ_E | Barrett & Seth, *PLoS Comput Biol* 2011;7(1):e1001052 |
| Causal density + integrated information | cd, Φ | Seth, Barrett & Barnett, *Phil Trans R Soc A* 2011;369(1952):3748–3767 |
| Stochastic interaction | Φ_SI | Ay, *Entropy* 2015;17(4):2432–2458 |
| Mismatched-decoding Φ-star | **Φ\*** | Oizumi, Amari, Yanagawa, Fujii & Tsuchiya, *PLOS Comput Biol* 2016;12(1):e1004654 |
| Geometric integrated information | **Φ_G** | Oizumi, Tsuchiya & Amari, *PNAS* 2016;113(51):14817–14822 |
| "Improved" Φ family | — | Tegmark, *PLOS Comput Biol* 2016;12(11):e1005123 |
| Comparison/critique of candidates | — | Mediano, Seth & Barrett, *Entropy* 2019;21(1):17 |
| Upper bounds (a certified ceiling, not a proxy) | — | Zaeemzadeh & Tononi 2024 |

⚠️ **"Φ_AR" is NOT verified as a named published measure.** Barrett & Seth 2011 and Tegmark 2016 both use autoregressive Gaussian models, which is probably the referent, but neither uses that symbol as if it were a citation. ⚠️ Also not located: a Barbosa/Marshall/Albantakis "Mean field dynamics" paper.

**Published statements that the proxies are not IIT's Φ:**

1. **Kitazono et al. 2018:** *"although **the first version of Φ is submodular, the later versions are not**"* — **i.e. the measure they make tractable (Φ_MI) is the superseded 2004 one.**
2. **Toker & Sommer 2019** compute Φ^G, normalized — and note *"**normalization was not discussed in the paper in which geometric integrated information was originally derived**,"* **so even their Φ^G differs from Oizumi et al.'s.**
3. **IIT 4.0:** *"human studies that have applied **measures of complexity inspired by IIT**"* — "inspired by," not Φ.
4. **IIT 3.0:** *"Hopefully, **heuristic measures**… will make it possible to test some of the predictions."*
5. **PyPhi 2.0 docs:** *"a different scheme is **a different definition**, not a faster route to the same number."*

---

## The empirical / clinical program

### Massimini et al. 2005 — the TMS-EEG foundation

**Massimini, Ferrarelli, Huber, Esser, Singh & Tononi, "Breakdown of cortical effective connectivity during sleep," *Science* 2005;309(5744):2228–2232**, doi:10.1126/science.1117256. Abstract, verbatim: *"we used **transcranial magnetic stimulation together with high-density electroencephalography** and asked how the activation of one cortical area (the **premotor area**) is transmitted to the rest of the brain. **During quiet wakefulness, an initial response (approximately 15 milliseconds) at the stimulation site was followed by a sequence of waves that moved to connected cortical areas several centimeters away. During non-rapid eye movement sleep, the initial response was stronger but was rapidly extinguished and did not propagate beyond the stimulation site.** Thus, the fading of consciousness during certain stages of sleep may be related to a **breakdown in cortical effective connectivity**."*

### Casali et al. 2013 — PCI

**Casali, Gosseries, Rosanova, Boly, Sarasso, Casali, Casarotto, Bruno, Laureys, Tononi & Massimini, "A theoretically based index of consciousness independent of sensory processing and behavior," *Science Translational Medicine* 2013;5(198):198ra105**, doi:10.1126/scitranslmed.3006294. Published 14 August 2013.

Framing, verbatim from the abstract: *"**Theoretical considerations suggest that consciousness depends on the brain's ability to support complex activity patterns that are, at once, distributed among interacting cortical areas (integrated) and differentiated in space and time (information-rich). We introduce and test a theory-driven index of the level of consciousness called the perturbational complexity index (PCI). PCI is calculated by (i) perturbing the cortex with transcranial magnetic stimulation (TMS) to engage distributed interactions in the brain (integration) and (ii) compressing the spatiotemporal pattern of these electrocortical responses to measure their algorithmic complexity (information).**"*

**Pipeline:** TMS → high-density EEG → source modelling → **statistical thresholding to identify significant cortical sources** → **binarization** into a spatiotemporal matrix → **Lempel-Ziv compression** → normalization. ⚠️ Note the later characterization in Colombo et al. 2024: *"the **Lempel-Ziv compressibility used in PCI only approximates algorithmic complexity**."*

Conditions tested, verbatim: *"a large data set of TMS-evoked potentials recorded in healthy subjects during **wakefulness, dreaming, nonrapid eye movement sleep, and different levels of sedation induced by anesthetic agents (midazolam, xenon, and propofol)**, as well as in patients who had emerged from coma (**vegetative state, minimally conscious state, and locked-in syndrome**)."* Result: *"**PCI reliably discriminated the level of consciousness in single individuals during wakefulness, sleep, and anesthesia, as well as in patients who had emerged from coma and recovered a minimal level of consciousness.**"*

⚠️ **GAP: the per-condition PCI numeric ranges from the 2013 paper itself are behind the *Science Translational Medicine* paywall** (science.org 403; not in PMC). **The method, the condition list and the qualitative result were obtained; the primary paper's own numeric ranges were not. The operative cutoff comes from the 2016 follow-up, which is the value actually used clinically.**

### Casarotto et al. 2016 — the validated PCI* cutoff

**Casarotto, Comanducci, Rosanova, Sarasso, Fecchio, Napolitani, Pigorini, Casali, Trimarchi, Boly, Gosseries, Bodart, Curto, Landi, Mariotti, Devalle, Laureys, Tononi & Massimini, "Stratification of unresponsive patients by an independently validated index of brain complexity," *Annals of Neurology* 2016;80(5):718–729**, doi:10.1002/ana.24779.

Headline numbers, verbatim from the abstract:

> *"we address this problem by **first validating** a promising metric of consciousness—the Perturbational Complexity Index (PCI)—**in a benchmark population who could confirm the presence or absence of consciousness through subjective reports**, and then applying the same index to patients with disorders of consciousness (DOCs). The benchmark population encompassed **150 healthy controls and communicative brain-injured subjects** in various states of **conscious wakefulness, disconnected consciousness, and unconsciousness**. **Receiver operating characteristic curve analysis** was performed to define an optimal cutoff… This cutoff was then applied to a cohort of noncommunicative DOC patients (**38 in a minimally conscious state [MCS] and 43 in a vegetative state [VS]**). **We found an empirical cutoff that discriminated with 100% sensitivity and specificity between the conscious and the unconscious conditions in the benchmark population. This cutoff resulted in a sensitivity of 94.7% in detecting MCS and allowed the identification of a number of unresponsive VS patients (9 of 43) with high values of PCI**, overlapping with the distribution of the benchmark conscious condition… In particular, **the high-PCI subgroup of VS patients may retain a capacity for consciousness that is not expressed in behavior**."*

⚠️ **PCI\* = 0.31 — confirmed, but the 2016 paper is paywalled at Wiley**, so the value was corroborated from a peer-reviewed source reusing the same cohort: **Colombo, Comanducci et al., "Beyond alpha power: EEG spatial and spectral gradients robustly stratify disorders of consciousness," *Cerebral Cortex* 2023**, doi:10.1093/cercor/bhad031. Verbatim from that paper (patients *"largely overlap with those previously reported in Casarotto et al. (2016) (n = 104 across datasets)"*): *"the highest individual PCI value across stimulation sites (**PCI-max**) was retained and identified three categories… **0 PCI**: no significant response could be evoked (PCI-max = 0)… **Lo PCI**: low complexity (**PCI-max ≤ 0.31**), indexing unconsciousness; **Hi PCI**: high complexity (**PCI-max > 0.31**), indexing preserved capacity for consciousness."* And on the UWS/MCS split: *"**while most UWS patients had 0 PCI or Lo PCI values, a minority had Hi PCI values; conversely nearly all MCS and all conscious brain-injured patients had Hi PCI values.**"*

### Sarasso et al. 2015 — anesthetics, and why ketamine mattered

**Sarasso, Boly, Napolitani, Gosseries, Charland-Verville, Casarotto, Rosanova, Casali, Brichant, Boveroux, Rex, Tononi, Laureys & Massimini, "Consciousness and complexity during unresponsiveness induced by propofol, xenon, and ketamine," *Current Biology* 2015;25(23):3099–3105.** n = 18 healthy volunteers.

**Why ketamine is the pivotal case**, verbatim: *"subjects can become **disconnected from the environment while still having conscious experiences**, as demonstrated by sleep states associated with dreaming. Among anesthetics, **ketamine is remarkable in that it induces profound unresponsiveness, but subjects often report 'ketamine dreams'** upon emergence."*

Results, verbatim: *"Both frontal and parietal TMS elicited **a low-amplitude EEG slow wave corresponding to a local pattern of cortical activation with low complexity during propofol anesthesia**, **a high-amplitude EEG slow wave corresponding to a global, stereotypical pattern of cortical activation with low complexity during xenon anesthesia**, and **a wakefulness-like, complex spatiotemporal activation pattern during ketamine anesthesia**. Crucially, **participants reported no conscious experience after emergence from propofol and xenon anesthesia, whereas after ketamine they reported long, vivid dreams unrelated to the external environment.** These results are relevant because they suggest that **brain complexity may be sensitive to the presence of disconnected consciousness in subjects who are considered unconscious based on behavioral responses.**"*

**This dissociates complexity from behavioral responsiveness: all three agents abolish responsiveness; only propofol and xenon abolish complexity, and only propofol and xenon abolish reported experience.** Corroborated in PCI* terms by Colombo et al. (2023), verbatim: *"**all individuals under Propofol or Xenon anesthesia had Lo PCI values and reported no conscious experience upon awakening; conversely, all individuals under Ketamine anesthesia had Hi PCI values and retrospectively reported vivid dreams** upon awakening, thus constituting **a model of unresponsive consciousness**."*

**Note the mechanism difference, which is the best evidence PCI tracks the integration/differentiation *conjunction***: under propofol PCI drops *"because the matrix of activation engaged by TMS was spatially restricted… consistent with a **loss of integration**"*; under xenon it drops *"because the pattern… was a widespread but stereotypical slow wave… consistent with a **loss of differentiation**."*

### PCI follow-ups

**Comolatti, Pigorini, Casarotto, Fecchio, Faria, Sarasso, Rosanova, Gosseries, Boly, Bodart, Ledoux, Brichant, Nobili, Laureys, Tononi, Massimini & Casali, "A fast and general method to empirically estimate the complexity of brain responses to transcranial and intracranial stimulations," *Brain Stimulation* 2019;12(5):1280–1289.** Verbatim: *"**PCI depends on elaborate experimental setups and offline processing, and has restricted applicability** to other types of brain signals beyond TMS and high-density EEG… We aim to address these limitations by introducing **PCI_ST**, a fast method… based on **dimensionality reduction and state transitions (ST) quantification** of evoked potentials. The index was validated on a large dataset of TMS/hd-EEG recordings obtained from **108 healthy subjects and 108 brain-injured patients**, and tested on sparse intracranial recordings (**SEEG**) of **9 patients**… **PCI_ST performed with the same accuracy as the original PCI, while improving on the previous method by being computed in less than a second** and requiring a simpler set-up."*

Also: **Sarasso, D'Ambrosio, Fecchio, Casarotto, Viganò, Landi et al., "Local sleep-like cortical reactivity in the awake brain after focal injury," *Brain* 2020;143(12):3672–3684** — cited by IIT 4.0 (ref 59) as supporting evidence.

⚠️ **"Zap and zip" — provenance NOT verified.** The phrase circulates as an informal label for the TMS-EEG/PCI method — e.g. **Kosik et al., "Why brain organoids are not conscious yet," *Patterns* 2024;5(9):101011**, verbatim: *"a **PCI readout called zap and zip**"* (citing Massimini, Boly, Casali, Rosanova & Tononi, *Progress in Brain Research* 2009;177:201–214 — **but that paper predates PCI by four years and the attribution looks loose**); and a 2024 *Brain Sciences* review. **No primary coinage could be confirmed** (search engines were bot-blocked). It is commonly attributed to Koch's *The Feeling of Life Itself* (MIT Press 2019) and/or Massimini & Tononi's *Sizing Up Consciousness* (OUP 2018) — **treat that attribution as unverified.** ⚠️ **Caution: a PMC full-text search for the exact phrase mostly returns Bliss, Collingridge & Laroche, "ZAP and ZIP, a story to forget," *Science* 2006;313(5790):1058–1059 — an unrelated LTP/PKMζ paper. Do not let those collide.**

### ⚠️ PCI is NOT Φ — what proponents actually claim

**This is the most important thing to get right, and the proponents' own language is unusually clear.**

**What PCI is called by its own authors:** *"a **theoretically based** index"* (2013 title), *"a **theory-driven** index"* (2013 abstract), *"**a promising metric of consciousness**"* (2016), *"**an independently validated index of brain complexity**"* (2016 title). **Never "a measure of Φ."**

**The decisive proponent statements:**

1. **Zaeemzadeh & Tononi 2024 — the cleanest disclaimer in print:** IIT *"has led to clinical applications, using **crude proxies of the system integrated information φ_s** that nevertheless offer what is currently the most sensitive and specific test for the presence of consciousness in non-responsive patients."* **Note it is φ_s (system phi), not Φ.**
2. **IIT 4.0:** *"This prediction has already found substantial support in human studies that have applied **measures of complexity inspired by IIT** to successfully classify subjects as conscious vs. unconscious."* **"Inspired by," and the object classified is a binary conscious/unconscious label, not a Φ value.**
3. **IIT 3.0:** *"Hopefully, **heuristic measures** and experimental approaches **inspired by** this theoretical framework will make it possible to test **some of the predictions** of the theory."*

**Stated precisely: PCI is a Lempel-Ziv compressibility statistic computed on thresholded TMS-evoked cortical source activity. It is not computed from a TPM, involves no partition search, no purviews, no distinctions or relations, and yields a number in roughly [0,1] rather than a Φ value in ibits.** Its connection to IIT is **conceptual** — it operationalizes the *joint* presence of integration (a single TMS pulse engages distributed interactions) and differentiation (the response resists compression), which is the pre-formal intuition IIT started from in 2004.

- **What PCI genuinely tests:** the directional, coarse-grained prediction that brain complexity tracks the presence of consciousness **and dissociates from behavioral responsiveness.** The ketamine result is the strongest form of this. IIT 4.0's own framing, verbatim: *"**A fundamental prediction is that Φ should be high in conscious states, such as wakefulness and dreaming, and low in unconscious states, such as dreamless sleep and anesthesia.**"*
- **What PCI does NOT test:** any quantitative claim of IIT — the φ_s formula, the ID measure, the MIP, the exclusion postulate, the recursive condensation into complexes, the distinction/relation decomposition, the Φ-structure, or the identity claim. **A high PCI is consistent with IIT but equally consistent with any theory on which consciousness requires differentiated, integrated cortical dynamics. PCI cannot discriminate IIT from its rivals, and no published work claims it does.**
- **For what IIT's proponents treat as the *genuinely* stringent and quantitative predictions**, IIT 4.0 lists them explicitly, verbatim: *"A **stringent prediction** is that **the location of the main complex, as determined by the overall maximum of φ_s within the brain, should correspond to its location as determined through clinical and experimental evidence**"*; *"constituents of the main complex can support conscious contents **even if they are mostly inactive, but not if they are inactivated**"*; *"**the complete inactivation of constituents of the main complex should lead to absolute agnosia** (unawareness that anything is missing)"*; and *"**changes in the strength of connections within the neural substrate of consciousness should be associated with changes in experience, even if neural activity does not change**."* **The paper concedes: "While the listed predictions may appear largely qualitative in nature, many of them rest on specific features of the accompanying quantitative analysis."**

### The cerebellum puzzle

**Neuron counts.** **Azevedo, Carvalho, Grinberg, Farfel, Ferretti, Leite, Jacob Filho, Lent & Herculano-Houzel, "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain," *Journal of Comparative Neurology* 2009;513(5):532–541**, doi:10.1002/cne.21974. Verbatim: *"the adult male human brain contains on average **86.1 ± 8.1 billion** NeuN-positive cells ('neurons')… **With only 19% of all neurons located in the cerebral cortex**, greater cortical size (representing 82% of total brain mass) in humans compared with other primates does not reflect an increased relative number of cortical neurons."*

The widely quoted split is **~69 billion cerebellar vs ~16 billion cerebral-cortical neurons (≈4.3×)** — consistent with 19% of 86.1 billion ≈ 16.4 billion in cortex. ⚠️ **The 69B figure was confirmed from a peer-reviewed *secondary* source** (Vandervert, *Cerebellum & Ataxias* 2016;3:10), **not from Azevedo et al.'s own tables.**

**IIT's explanation is architectural: modularity creates fault lines, and fault lines destroy φ_s.** Built from a worked 6-unit example (4.0 Fig 6B), verbatim: *"a network comprising **three weakly interconnected modules**, each having two strongly connected units… **the weak inter-module connections are clear fault lines**. Properly normalized, partitions along these fault lines separating modules yield values of φ_s that are **much smaller** than those yielded by partitions that cut across modules. As a consequence, the 6-unit system **condenses into three complexes** (Ab, cd, and ef)… because the modules are small, their Φ values are low."*

Then, verbatim: *"**Intriguingly, a brain region such as the cerebellum, whose anatomical organization is highly modular, does not contribute to consciousness, even though it contains several times more neurons than the cerebral cortex (and is indirectly connected to it).**"* ⚠️ **Note IIT 4.0 says "several times more neurons," not "4×" — the 4× figure comes from the Azevedo/Herculano-Houzel literature, not from IIT's own text.**

IIT 4.0's clinical citations for the cerebellum's dispensability: **Lemon & Edgley, "Life without a cerebellum," *Brain* 2010;133(3):652–654**; and **Yu, Jiang, Sun & Zhang, "A new case of complete primary cerebellar agenesis," *Brain* 2015;138(6):e353.**

**The same mechanism is reused for sleep**, verbatim: *"fault lines can be due **not just to neuroanatomy but also to neurophysiological factors**. For example, **during early slow-wave sleep, the dense interconnections among neuronal groups in cerebral cortical areas may break down, becoming causally ineffective due to the bistability of neuronal excitability.**"*

And Zaeemzadeh & Tononi 2024 give the contrastive version, verbatim: *"**large systems with fault lines, or high levels of indeterminism and/or degeneracy, break down into many small complexes, which will necessarily have very low values of Φ. This should be the case for many other regions of the brain, such as the cerebellum and much of prefrontal cortex, for other parts of the body, and certainly for artificial systems such as computers.**"* **They call the predicted gap "hyper-astronomical."**

### The posterior hot zone claim

**IIT 4.0's own statements**, verbatim: *"In the brain, **a large part of the cerebral cortex, especially its posterior regions, is organized as a dense, divergent-convergent hierarchical 3D lattice of specialized units, which makes it a plausible candidate for the substrate of human consciousness**."* And: *"its anatomical organization may be such that **a subset of brain regions, arranged in a dense 3D lattice primarily located in posterior cortex, may achieve a much higher value of integrated information than any other subset**."* The supporting formal result: *"Preliminary work indicates that **lattices of specialized units, implementing different input–output functions, but partially overlapping in their inputs (receptive field) and outputs (projective fields), are particularly well suited to constituting large substrates that unfold into extraordinarily rich Φ-structures.**"*

Primary citations:

- **Boly, Massimini, Tsuchiya, Postle, Koch & Tononi, "Are the Neural Correlates of Consciousness in the Front or in the Back of the Cerebral Cortex? Clinical and Neuroimaging Evidence," *Journal of Neuroscience* 2017;37(40):9603–9613.** Abstract, verbatim: *"**The role of the frontal cortex in consciousness remains a matter of debate.** In this **Perspective**, we will critically review the clinical and neuroimaging evidence…"* ⚠️ **Note it is a *Perspective*, published as one half of a "Dual Perspectives" pair — the opposing piece is Odegaard, Knight & Lau, "Should a Few Null Findings Falsify Prefrontal Theories of Conscious Perception?", *J Neurosci* 2017;37(40):9593–9602. Cite the pairing.**
- **Siclari, Baird, Perogamvros, Bernardi, LaRocque, Riedner, Boly, Postle & Tononi, "The neural correlates of dreaming," *Nature Neuroscience* 2017;20(6):872–878** — **the phrase "hot zone" appears here**, verbatim: *"In both NREM and REM sleep, reports of dream experience were associated with local decreases in low-frequency activity in posterior cortical regions. High-frequency activity in these regions correlated with specific dream contents. **Monitoring this posterior 'hot zone' in real time predicted whether an individual reported dreaming or the absence of dream experiences during NREM sleep**, suggesting that it may constitute **a core correlate of conscious experiences in sleep**."*
- ⚠️ **Koch, Massimini, Boly & Tononi, "Neural correlates of consciousness: progress and problems," *Nature Reviews Neuroscience* 2016;17(5):307–321** — **citation verified; full text NOT obtained (paywalled, not in PMC). Flag any quote attributed to it.**

---

## Summary of flags and disagreements

**Corrections to common framings:**

1. **In IIT 4.0 the complex is selected by maximum φ_s (system "small phi"), NOT by maximum Φ.** Big Φ is a *sum* computed from the already-identified complex and plays no role in selecting it. The "only the maximum-Φ candidate set is conscious" framing is correct for **IIT 3.0** and **incorrect for 4.0.**
2. **"Qualia space" in IIT 1.0 ≠ qualia space in IIT 2.0.** In 1.0 the axes are *elements* and the structure is the effective information matrix; from 2.0 the axes are *system states*. **1.0 does use the term**, so "no qualia space yet in 1.0" is not quite right — the *formal* qualia space arrives in 2009.
3. **Qualia space / concept space is GONE from IIT 4.0** entirely, replaced by the Φ-structure.
4. **PyPhi's published complexity is `O(n·53ⁿ)`, not `O(n⁵3ⁿ)`** — verified in the JATS superscript markup and the authors' arXiv LaTeX. The `O(n⁵3ⁿ)` form is PyPhi's *current documentation*'s re-rendering. **Report both.**
5. **MIP normalization oscillates across versions:** used in 1.0 and 2.0, explicitly dropped in 3.0, explicitly restored in 4.0 with a new normalizer. **Don't describe it as a constant.**
6. **IIT 4.0 says the cerebellum has "several times more neurons" than cortex** — the ~4× / 69B-vs-16B figures come from Azevedo/Herculano-Houzel, not from IIT's text.

**Could not verify:**

- **No published NP-hard / #P-hard theorem for Φ exists.** The only such claims are **Aaronson's 2014 blog conjectures, about the pre-3.0 Φ definition. Do not assert a complexity class.**
- Casali et al. 2013's **own per-condition PCI numeric ranges** (paywalled).
- **"Zap and zip" primary coinage.**
- **Full text of both 2016 *Nature Reviews Neuroscience* reviews** — citations confirmed, text not.
- Publication status of **Tononi's book *On Being*** (still "forthcoming").
- Hidaka & Oizumi, the original submodularity/Queyranne result; a Barbosa/Marshall/Albantakis "Mean field dynamics" paper; "Φ_AR" as a named published measure; PyPhi's `WELCOME_OFF` config option.
- ⚠️ **There is no dedicated SEP entry on IIT.** It is covered in **"The Neuroscience of Consciousness," *SEP*, first published 9 Oct 2018, substantive revision 3 Apr 2024, §3.4 "Information Integration Theory"** (with IIT also in §3's intro and §3.5 "Frontal or Posterior?"). **SEP characterizes IIT as "probably best understood as a metaphysical theory about the essential features of consciousness" rather than a neuroscientific theory as such — a framing IIT's authors would contest, given their "operational" self-description.**

**Where sources genuinely disagree — surface these:**

1. **Exact-Φ growth rate:** `O(n·53ⁿ)` (Mayner et al. 2018) vs `O(13^m)` (Hanson & Walker 2023, with full derivation) vs `O(n⁵7ⁿ)` for the major complex (PyPhi 2026 docs, which calls H&W's derivation "erroneous").
2. **Practical ceiling:** *"~10–12 nodes"* (PyPhi 2018 / IIT 3.0's "more than a dozen elements or so") vs *"~6–8 units"* for the full IIT 4.0 Φ-structure (PyPhi 2026 docs). **The 4.0 ceiling is LOWER than the 3.0 ceiling — the theory got less computable as it got more precise. State this explicitly.**
3. **Queyranne's practical accuracy on Φ_G:** near-perfect (Kitazono et al. 2018, non-normalized) vs 1/50 and 2/50 exact matches (Toker & Sommer 2019, normalized). **The two papers disagree about normalized vs non-normalized Φ^G and say so.**
