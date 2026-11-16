---
name: stochastic-parrot
description: "The 'stochastic parrot' critique of large language models — what Bender, Gebru, McMillan-Major & Shmitchell actually argued in the 2021 FAccT paper, and the state of the debate it started. Covers the verbatim definition and the fact that the phrase appears only twice in the body text; the paper's real argument set, which is far broader than the slogan (environmental and financial cost and its unequal distribution, undocumentable training data and 'documentation debt', why filtering corpora can make bias worse, 'value-lock', coherence-in-the-eye-of-the-beholder and the accountability thesis, and the Paths Forward recommendations); the form-versus-meaning argument that actually carries the weight, which lives in Bender & Koller's ACL 2020 octopus paper and Merrill et al.'s formal version, not in the FAccT paper; the Google departures of Gebru and Mitchell with the documented facts separated from the disputed ones; the term's drift from a predicate about a mechanism into a generic noun and a null hypothesis, documented through the ADS 2023 vote, Altman's tweet and the arXiv title record; and the counterarguments at full strength — emergent abilities and the metric-artefact rebuttal, the probing evidence for internal world models and the 'bag of heuristics' counter-counter, the compression argument, and the Searle/Block/Chalmers/Shanahan philosophy. Scores the paper's risk claims (which largely aged well) separately from its capability claims (which aged worst), and states what evidence would actually resolve it. Use when evaluating claims about whether LLMs understand or merely pattern-match, citing or rebutting the parrots paper, reasoning about emergence or world models or anthropomorphism, or needing an honest, sourced account of a debate that is usually conducted with strawmen on both sides."
---

# Stochastic Parrot

A phrase from one paper that escaped into the language and changed meaning on the way out.

**The verbatim definition**, from §6.1 "Coherence in the Eye of the Beholder" of Bender, Gebru, McMillan-Major & Shmitchell (FAccT 2021):

> "Contrary to how it may seem when we observe its output, an LM is a system for haphazardly stitching together sequences of linguistic forms it has observed in its vast training data, according to probabilistic information about how they combine, but without any reference to meaning: a stochastic parrot."

Three facts that most citations get wrong:

1. **The phrase appears in the body text exactly twice** — this definition, and one line in §7 about dual use. It is a **predicate describing a mechanism**, used once in passing. It is not the paper's thesis and the paper never uses it as a plural noun for a class of system.
2. **The paper is eight sections and only one of them is about meaning.** The others are cost, training data, research-effort misallocation, deployment harms, and recommendations.
3. **The capability argument is deferred, not made.** §5 cites Bender & Koller (2020) for "form alone cannot yield meaning." Bender confirmed this in a 2026 retrospective: the top misconception is *"Bender says AI is a stochastic parrot,"* the phrase *"specifically refers to large language models,"* and the title was chosen because *"we liked it!"* **So capability claims should be scored against Bender & Koller (2020) and Merrill et al. (TACL 2021), not against the FAccT paper.**

## What the paper actually argues

| § | Argument | Status in 2026 |
|---|---|---|
| 3 | **Cost, unequally distributed.** Strubell et al.'s 284 t CO₂ for Transformer-big + architecture search; BERT-base ≈ a trans-American flight; +0.1 BLEU ≈ $150,000. Is it just to ask residents of the Maldives or flood-hit Sudan to pay for English LMs when none is built for Dhivehi or Sudanese Arabic? | **Directionally vindicated**, absolute numbers now far larger. ⚠️ Cite the 2021 figures as *historical* — Strubell's headline was a *neural architecture search*, not one run, and Patterson et al. corrected it by **88×** (3,223 kg vs 284,019 kg). Both framings are interested; Patterson is at the company supplying the efficiency factor |
| 4 | **Undocumentable data.** Internet-scale corpora encode the hegemonic view: Reddit was 67% men and 64% aged 18–29; 8.8–15% of Wikipedians are women or girls. **Filtering makes it worse** — C4 discarded any page containing one of ~400 "Dirty, Naughty, Obscene or Otherwise Bad Words," which *"will also undoubtedly attenuate, by suppressing such words as twink, the influence of online spaces built by and for LGBTQ people."* Plus **'value-lock'** and **documentation debt**: *"putting ourselves in a situation where the datasets are both undocumented and too large to document post hoc"* | **Uncontroversial now.** The direct ancestor of datasheets, model cards and provenance work |
| 5 | **Misdirected research effort.** LMs "cheat their way through tests meant to require language understanding"; the opportunity cost is time not spent on meaning-sensitive approaches or on the >90% of languages with little language technology | **The capability claim that aged worst** — but see the deferral above |
| 6 | **Coherence is in the eye of the beholder**, and the **accountability thesis**: risks of synthetic text are *"deeply connected to the fact that such synthetic text can enter into conversations without any person or entity being accountable for it."* Harms: hegemonic amplification, abusive output, invisible allocational harm in classification, disinformation and extremist recruitment, MT fluency masking error (the Palestinian man arrested after "good morning" was translated "attack them"), PII extraction | **Vindicated and institutionalised.** Note §6 also predicted **model collapse** in 2021: more text "to future LMs trained on training sets that ingested the previous generation LM's output" |
| 7 | **Paths forward:** budget documentation as a cost of dataset creation and collect only what you can document; data statements, datasheets, model cards; value-sensitive design with indirect stakeholders; **pre-mortems**; energy reporting as an evaluation metric; watermarking | Largely adopted as governance practice |

The citation chain in §6.1 is **Herbert H. Clark** on common ground, **Nass, Steuer & Tauber (1994) "Computers are social actors"**, and **Weizenbaum (1976)** for the ELIZA effect. **Grice is not cited** — he appears in Bender & Koller, and for the utterer's-meaning/sentence-meaning distinction, not the maxims.

## The argument that actually carries the weight

**Bender & Koller, "Climbing towards NLU," ACL 2020** (Best Theme Paper). Form is any observable realization of language; meaning is the relation `M ⊆ E × I` between expressions and the communicative intents they evoke; *understanding* is retrieving `i` from `e`. A system trained on form alone has no access to `I`.

**The octopus.** A and B, fluent English speakers, are stranded on two uninhabited islands and communicate by telegraph over an underwater cable. **O, a hyper-intelligent deep-sea octopus**, taps the cable. O knows no English but is excellent at statistical patterns, and learns to predict B's replies.

- **Small talk works.** Such conversations "have a primarily social function… It is sufficient to produce text that is internally coherent."
- **The coconut catapult fails invisibly.** A sends build instructions; O does not know what *rope* and *coconut* refer to, so it says "Cool idea, great job!" — and *"It is absolutely conceivable that A accepts this reply as meaningful — but only because A does all the work in attributing meaning to O's response."*
- **The bear kills her.** A is chased by a bear and asks how to make a weapon from sticks. *"It is at this point that O would fail the Turing test, if A hadn't been eaten by the bear before noticing the deception."*

The conclusion is about the listener, not the speaker: *"It is not that O's utterances make sense, but rather, that A can make sense of them."*

The formal version, which is the one to cite when steelmanning: **Merrill, Goldberg, Schwartz & Smith, "Provable Limitations of Acquiring Meaning from Ungrounded Form," TACL 9:1047–1060 (2021).**

## The drift

The paper used "stochastic parrot" as a predicate about a mechanism. It is now a noun you can be, and a null hypothesis to be refuted.

- **American Dialect Society, 2023.** "Stochastic parrot" **won** the AI-Related Word of the Year — 106 in the first round, 147 in the runoff, against ChatGPT's 111/130. (English Wikipedia says only "nominated"; the primary press release shows it won.) The ADS gloss is itself the best single evidence of drift: *"large language model that can generate plausible synthetic text without having any understanding"* — the artifact, not the mechanism.
- **Altman, 4 Dec 2022**, four days after ChatGPT: *"i am a stochastic parrot, and so r u."* Bender's response: *"People want to believe so badly that these language models are actually intelligent that they're willing to take themselves as a point of reference and devalue that to match what the language model can do."*
- **The arXiv title record** traces the lexicalization: pluralized into a class of thing ("Flocks of Stochastic Parrots," "Do Stochastic Parrots have Feelings Too?"), then made a binary ("Stochastic Parrots or ICU Experts?", "LLMs are not stochastic parrots"), then verbed ("Stochastic Parroting," 2025–26). The first hostile response arrived **10 weeks after the paper and before it was presented** (Lissack, arXiv:2101.10098, 11 Jan 2021).

## The counterarguments, at full strength

**Emergent abilities, and the metric rebuttal.** Wei et al. (TMLR 2022) defined an ability as emergent if "not present in smaller models but present in larger models," and documented jumps at specific FLOP counts. Schaeffer, Miranda & Koyejo (**NeurIPS 2023 Outstanding Main Track Paper**, not a runner-up) argued the jumps are artefacts of **discontinuous metrics**: under a power-law per-token loss, whole-sequence accuracy decays as `p^L` (looks like a threshold) while token edit distance is `L(1−p)` (looks smooth). **Multiple Choice Grade and Exact String Match account for >92% of claimed emergent abilities**, and they *induce* emergence at will in vision models nobody calls emergent.

Two corrections to how this is usually told: **Wei et al. pre-empted the metric objection in their own §5.1**, and **Schaeffer et al. explicitly do not claim LLMs lack emergent abilities** — their thesis is about evidence and measurement. Using it as "LLMs don't really gain new abilities" is a misreading. The strongest metric-independent counterexample is **induction heads** (Olsson et al. 2022), where the phase change is visible in the **training loss itself** — though that is a transition over training time, not over scale.

**Internal world models.** Text-only training does produce decodable, sometimes causally efficacious representations of non-linguistic structure: Othello board state (Li et al. ICLR 2023; **Nanda's correction** that it is linear after all, in a *my-colour/their-colour* frame — the original nonlinear probe was likely learning an XOR with "which side am I"), perceptual colour topology in CIELAB (Abdou et al., CoNLL 2021), latitude/longitude and historical time (Gurnee & Tegmark, R² ≈ 0.91 for world places), program execution state (Jin & Rinard, ICML 2024), truth value (Marks & Tegmark, COLM 2024), and millions of steerable features at production scale (Anthropic, May 2024).

**The counter-counter that matters.** Lin, JackS, Karvonen & Rager (2024) found Othello-GPT computes board state through **many board-position-specific rules that do not generalise across translations** — e.g. L1N421 gated by L0N377. *"Our best guess is that Othello-GPT's learned algorithm is just a bag of independent heuristics."* This is the honest residue: **decoding and causal intervention can both succeed while the underlying computation is a pile of local heuristics** — on a toy model where ground truth is fully known.

**Compression.** Sutskever's version: "to 'just learn' the statistical correlations in text, to compress them really well, what the neural network learns is some representation of the process that produced the text. This text is actually a projection of the world." The quantitative support: Chinchilla 70B, trained predominantly on text, compresses **ImageNet patches to 43.4% (PNG: 58.5%)** and **LibriSpeech to 16.4% (FLAC: 30.3%)**.

Against it: **Block's "Blockhead" (1981)** — a vast lookup table passes any finite behavioural test with no understanding, so the argument is about *capacity*, not possibility, and the disagreement is quantitative. And Krakauer et al.'s sharper point, which cuts both ways: **the more world-structure is already encoded in language, the weaker emergence claims become** — the model may be fitting redundant data rather than reconstructing a generative process.

**Is "it's just statistics" a category error?** If mental states are individuated by functional role, then "it's just statistics" describes the *implementation* ("it's just chemistry" is equally true of brains). Block's reply is that behavioural equivalence is not functional equivalence, so the functionalist owes an account of internal organisation — which is what the probing programme tries to supply and what the bag-of-heuristics result complicates. Note the real disanalogy with **Searle's Chinese Room**: it stipulates a hand-written rulebook with no learning and no internal representation. "It's just syntax" is a claim about the *form* of the implementation; the probing results are claims about the *content* of learned states. The strongest reply on Searle's side is that **decodability is not aboutness** — the probe supplies the interpretation.

## The honest scoreboard

**Use Mahowald et al. (*TiCS* 28(6):517–540, 2024) as the organising frame**, because it is the rare vocabulary both camps adopted:

- **Formal linguistic competence** (rules and patterns) — LLMs are *"surprisingly good."*
- **Functional linguistic competence** (using language to understand and act) — *"spotty."*

**"Stochastic parrot" is close to false about the first and close to true about the second, and most benchmark fights are a category confusion between them.**

So: the paper's **risk** claims largely aged well — anthropomorphism, documentation debt, data bias, disinformation at scale, cost asymmetry, the underserved-languages point, even model collapse. Its **capability** claim aged worst, and the a-priori form of "form alone cannot yield meaning" is in trouble. But nothing in the probing literature establishes a *unified compositional* world model, and the best recent sceptical result is strong: **PhysiCo** (Yu et al., NAACL 2025) finds frontier models trail humans by **~40%** on abstract grid renderings of physical concepts they describe fluently in words — and the difficulty is intrinsic to the task, not the format.

**The hard case nobody has solved:** distinguishing "a unified compositional world model" from "a very large bag of locally-valid heuristics that is behaviourally and causally indistinguishable at the tested resolution." Until there is a measure that separates them, the evidence underdetermines what both camps want from it. That, rather than any single paper, is where the debate stands.

## Always-apply

1. **Quote the definition, not the slogan.** If you are citing the FAccT paper for a capability ceiling, you are citing the wrong paper — use Bender & Koller (2020) or Merrill et al. (2021).
2. **Separate risk claims from capability claims** before scoring anything. They have opposite track records.
3. **Say "formal" or "functional"** competence. Most disputes dissolve on contact with the distinction.
4. **Demand three things of any probing result:** the probe decodes the property, a causal intervention on that direction changes behaviour as predicted, and a control shows the probe is not doing the work itself. Jin & Rinard's interventional baseline is the template.
5. **Do not cite the 2021 carbon figures as current**, and give both the Strubell and Patterson framings with their interests noted.
6. **Do not use Schaeffer et al. as "emergence isn't real"** — they disclaim that reading — and do not say Wei et al. ignored metrics; they addressed it in §5.1.
7. **Attribute positions only to primary sources.** Hinton's widely-repeated "LLMs genuinely understand" has no reachable primary source; LeCun's "dead end" carries the qualifier *when it comes to superintelligence*, which summaries drop; Hassabis's position is not verifiable from secondary coverage.
8. **Note Sutskever's 2025 reversal** when the compression argument comes up: *"These models somehow just generalize dramatically worse than people,"* a *"very fundamental thing"*; the data "is very clearly finite"; on 100× compute, *"I don't think that's true."* The strongest advocate of prediction-implies-world-modelling now concedes the generalisation gap — a concession about *functional* competence, not about internal representations.

## How to use the references

- **`references/the-paper-and-the-argument.md`** — the paper section by section with verbatim passages, Table 1's scale figures, the full Paths Forward list with its citation anchors, Bender & Koller and the octopus in full including the pre-empted counterarguments, and the Google departures with documented facts and disputed characterisations kept apart.
- **`references/the-debate.md`** — emergence and the mirage argument with Schaeffer's mathematical model and BIG-Bench meta-analysis, the world-model probing literature paper by paper with each author's own stated limits, compression, the philosophy (Searle and the SEP replies, Block, Chalmers' explicit credences, Shanahan, Piantadosi), the 2026 positions, and Krakauer/Krakauer/Mitchell's published criterion list for what would resolve it.

## Sources

Bender, Gebru, McMillan-Major & Shmitchell, "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? 🦜," FAccT '21, pp. 610–623, doi:10.1145/3442188.3445922, CC-BY 4.0 — read in full from the author PDF mirror, cross-checked against Crossref (`dl.acm.org` returns 403). Bender & Koller, "Climbing towards NLU," ACL 2020, pp. 5185–5198, doi:10.18653/v1/2020.acl-main.463 — read in full. Merrill, Goldberg, Schwartz & Smith, *TACL* 9:1047–1060, 2021. Rak, "Emily Bender Sets the Record Straight on 'Stochastic Parrots'," *IEEE Spectrum*, 30 June 2026. Wei et al., TMLR 08/2022, arXiv:2206.07682. Schaeffer, Miranda & Koyejo, NeurIPS 36, pp. 55565–55581, arXiv:2304.15004; award confirmed on the official NeurIPS blog, 11 Dec 2023. Li, Hopkins, Bau, Viégas, Pfister & Wattenberg, ICLR 2023, arXiv:2210.13382. Nanda, Lee & Wattenberg, BlackboxNLP 2023, pp. 16–30, doi:10.18653/v1/2023.blackboxnlp-1.2. Lin, JackS, Karvonen & Rager, "OthelloGPT learned a bag of heuristics," LessWrong, 2 July 2024. Olsson et al., "In-context Learning and Induction Heads," *Transformer Circuits Thread*, 8 Mar 2022 / arXiv:2209.11895, 24 Sep 2022 (cite both dates). Gurnee & Tegmark, arXiv:2310.02207. Abdou et al., CoNLL 2021, doi:10.18653/v1/2021.conll-1.9. Jin & Rinard, ICML 2024, PMLR 235:22160–22184. Marks & Tegmark, COLM 2024, arXiv:2310.06824. Delétang et al., "Language Modeling Is Compression," arXiv:2309.10668. Mahowald, Ivanova, Blank, Kanwisher, Tenenbaum & Fedorenko, *TiCS* 28(6):517–540, 2024, doi:10.1016/j.tics.2024.01.011 — note it never uses the phrase "stochastic parrot." Mitchell & Krakauer, *PNAS* 120(13), doi:10.1073/pnas.2215907120. Shanahan, *CACM* 67(2):68–79, doi:10.1145/3624724. Chalmers, "Could a Large Language Model be Conscious?", arXiv:2303.07103. Searle, *BBS* 3(3):417–424, 1980. Block, *Philosophical Review* 90(1):5–43, 1981. Krakauer, Krakauer & Mitchell, *Phil. Trans. R. Soc. A* 384(2320):20250014, 14 May 2026, doi:10.1098/rsta.2025.0014. Yu et al., "The Stochastic Parrot on LLM's Shoulder," NAACL 2025, arXiv:2502.08946. American Dialect Society press release, 5 Jan 2024. Weil, "You Are Not a Parrot," *New York Magazine*, 1 Mar 2023. Newton, *Platformer*, 3 Dec 2020 (full text of both Gebru's and Dean's emails). Hao, *MIT Technology Review*, 4 Dec 2020. Simonite, *WIRED*, 8 June 2021. BBC News, 20 Feb 2021. *The Verge*, 19 Feb 2021. All fetches 2026-11-11.

**Verification notes.** Quotations are from locally downloaded PDFs read with `pdftotext`, not from search summaries. **Not verified, and not asserted here:** Hinton's position that LLMs genuinely understand (no reachable primary source; his verified claims are narrower); Hassabis's position on understanding; LeCun's "dead end" quote (reaches only via Wikipedia quoting the paywalled *FT*); the full text of LeCun's "A Path Towards Autonomous Machine Intelligence" (OpenReview blocked); Patel & Pavlick's ICLR 2022 method; Templeton et al.'s "Scaling Monosemanticity" author list. **All tweets** — Gebru's, Dean's, Altman's, Mitchell's "I'm fired" — are reported via the journalism cited, not read at source. **Sutskever's GTC quote rests on a Whisper-generated, LifeArchitect.ai-edited transcript** and the date is disputed (15 vs 22 March 2023); it is the one famous quote here with non-authoritative provenance.

## Related

- [[neural-networks-ml]] — what the system under dispute actually is, and the interpretability work the world-model argument rests on.
- [[integrated-information-theory]] / [[panpsychism]] — the adjacent question of whether such a system could be conscious, where Chalmers' credences live.
- [[detect-ai]] — the synthetic-text detection problem the paper's watermarking question anticipated.
- [[grounded-answers]] — the house discipline of sourcing claims, which this debate badly needs.
- [[information-theory]] — cross-entropy, perplexity and the compression argument's formal basis.
- [[agentic-workflows]] / [[claude-api]] — building on these systems while holding an accurate model of what they do.
