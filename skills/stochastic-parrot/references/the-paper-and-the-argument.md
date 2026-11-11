# The paper, the octopus, and the Google departures

## 1. Bibliographic record

Emily M. Bender, Timnit Gebru, Angelina McMillan-Major & Shmargaret Shmitchell. 2021. "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? 🦜." *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency* (FAccT '21), March 3–10, 2021, Virtual Event, Canada. ACM, pp. 610–623. doi:10.1145/3442188.3445922.

- **Affiliations as published:** Bender — University of Washington; Gebru — **Black in AI**; McMillan-Major — University of Washington; Shmargaret Shmitchell — **"The Aether"**. Bender and Gebru are marked *"Joint first authors."*
- **CC-BY 4.0.** 14 pages, 156 references. ~9,500 citations as of November 2026.
- `dl.acm.org` returns 403 to automated fetching; the text used here is the published CC-BY version from a widely-mirrored author PDF, verified against Crossref for authors, affiliations and pages.

**The acknowledgments are themselves a primary source:**

> "This paper represents the work of seven authors, but some were required by their employer to remove their names."

**Headcount discrepancy worth flagging:** the acknowledgment says **seven** contributors; MIT Technology Review described the draft as having **six** coauthors, four of them Google researchers; Dean's email says "four fellow Googlers as well as some external collaborators." Four names appear on the published version. Reconcilable, but the sources do not agree.

## 2. Section structure (verbatim headings)

```
1  INTRODUCTION
2  BACKGROUND
3  ENVIRONMENTAL AND FINANCIAL COST
4  UNFATHOMABLE TRAINING DATA
   4.1  Size Doesn't Guarantee Diversity
   4.2  Static Data/Changing Social Views
   4.3  Encoding Bias
   4.4  Curation, Documentation & Accountability
5  DOWN THE GARDEN PATH
6  STOCHASTIC PARROTS
   6.1  Coherence in the Eye of the Beholder
   6.2  Risks and Harms
   6.3  Summary
7  PATHS FORWARD
8  CONCLUSION
```

Eight numbered sections — which matches Wired's description of Dean objecting to "one of its eight sections," the §3 energy section.

## 3. §2 — the LM definition and the scale table

The definition is explicitly inherited from Bender & Koller:

> "we understand the term language model (LM) to refer to systems which are trained on string prediction tasks: that is, predicting the likelihood of a token (character, word or string) given either its preceding context or (in bidirectional and masked LMs) its surrounding context."

They trace LMs to **Shannon 1949** and note "some of the earliest implemented LMs date to the early 1980s."

**Table 1, verbatim:**

| Year | Model | Parameters | Dataset |
|---|---|---|---|
| 2019 | BERT | 3.4E+08 | 16GB |
| 2019 | DistilBERT | 6.60E+07 | 16GB |
| 2019 | ALBERT | 2.23E+08 | 16GB |
| 2019 | XLNet (Large) | 3.40E+08 | 126GB |
| 2020 | ERNIE-Gen (Large) | 3.40E+08 | 16GB |
| 2019 | RoBERTa (Large) | 3.55E+08 | 161GB |
| 2019 | MegatronLM | 8.30E+09 | 174GB |
| 2020 | T5-11B | 1.10E+10 | 745GB |
| 2020 | T-NLG | 1.70E+10 | 174GB |
| 2020 | GPT-3 | 1.75E+11 | 570GB |
| 2020 | GShard | 6.00E+11 | – |
| 2021 | Switch-C | 1.57E+12 | 745GB |

## 4. §3 — cost, and who pays it

Opening on Strubell, Ganesh & McCallum (ACL 2019):

> "While the average human is responsible for an estimated **5t CO₂e per year**, the authors trained a Transformer (big) model with neural architecture search and estimated that the training procedure emitted **284t of CO₂**. Training a single **BERT base** model (without hyperparameter tuning) on GPUs was estimated to require as much energy as a **trans-American flight**."

> "an increase in **0.1 BLEU score** using neural architecture search for English to German translation results in an increase of **$150,000 compute cost** in addition to the carbon emissions."

Also in §3: compute for the largest models rose **300,000× in 6 years**; most sampled papers from ACL 2018, NeurIPS 2018 and CVPR 2019 claimed accuracy improvements alone and **none** focused on efficiency; inference cost may outweigh training in the long run; and **over 90% of the world's languages, used by more than a billion people, have little to no language-technology support.**

**The distribution argument:**

> "Is it fair or just to ask, for example, that the residents of the Maldives (likely to be underwater by 2100) or the 800,000 people in Sudan affected by drastic floods pay the environmental price of training and deploying ever larger English LMs, when similar large-scale models aren't being produced for Dhivehi or Sudanese Arabic?"

With a footnote that matters for fairness: *"By this comment, we do not intend to erase existing work on low-resource languages. One particularly exciting example is the Masakhane project… These promising directions do not involve amassing terabytes of data."*

**⚠️ On citing these figures in 2026.** Strubell's headline 626,155 lb was for a neural **architecture search**, not a single training run, and Patterson et al. corrected it by **88×** (3,223 kg actual vs 284,019 kg published). Patterson is at the company supplying the 5× hardware/datacenter efficiency factor, so both framings are interested. Present both and date them.

## 5. §4 — why filtering makes it worse

The framing: internet-scale datasets "encode the dominant/hegemonic view, which further harms people at the margins."

Four narrowing stages: *"from initial participation in Internet fora, to continued presence there, to the collection and finally the filtering of training data, current practice privileges the hegemonic viewpoint."*

The statistics: internet access overrepresents younger users and developed countries; GPT-2's data came from Reddit outbound links and **67% of US Reddit users were men, 64% aged 18–29**; **only 8.8–15% of Wikipedians are women or girls**. Moderation acts as a structural filter — Leslie Kay Jones on accounts receiving death threats being suspended while the accounts issuing them persist.

**The key passage, on filtering:**

> "The Colossal Clean Crawled Corpus, used to train a trillion parameter LM, is cleaned, inter alia, by discarding any page containing one of a list of about 400 'Dirty, Naughty, Obscene or Otherwise Bad Words'. This list is overwhelmingly words related to sex, with a handful of racial slurs and words related to white supremacy… **this approach will also undoubtedly attenuate, by suppressing such words as twink, the influence of online spaces built by and for LGBTQ people.** If we filter out the discourse of marginalized populations, we fail to provide training data that reclaims slurs and otherwise describes marginalized identities in a positive light."

And on GPT-3's filter: *"what is unmeasured (and thus unknown) is what else it filtered out."*

The prescription: *"curate training datasets through a thoughtful process of deciding what to put in, rather than aiming solely for scale and trying haphazardly to weed out, post-hoc, flotsam deemed 'dangerous', 'unintelligible', or 'otherwise bad'."*

**§4.2 'value-lock'** (the paper's exact form is hyphenated and scare-quoted):

> "methodologies reliant on LMs run the risk of **'value-lock'**, where the LM-reliant technology reifies older, less-inclusive understandings."

Evidence: Twyman et al. on Black Lives Matter and Wikipedia coverage. Caveat the paper states itself: poorly-documented movements are not captured at all, and media "tend to ignore peaceful protest activity."

**§4.3 encoding bias** — the section whose "mitigation literature" Dean said was missing. It catalogs documented bias, applies **Crenshaw's intersectionality** (BERT, ELMo, GPT and GPT-2 encode more bias against multiply-marginalized identities than the combination of single-axis biases would predict), cites Hutchinson et al. on disability sentiment and Gehman et al. on toxicity from non-toxic prompts (plus **272K documents from unreliable news sites and 63K from banned subreddits** in GPT-2's data). Then three reasons auditing cannot be exhaustive: the audit tools are themselves biased (Perspective API associates higher toxicity with identity markers); auditing "requires an a priori understanding of what social categories might be salient" and salience is culture-bound; and verifying safety "requires engaging with the systems of power that lead to the harmful outcomes."

**§4.4 documentation debt:**

> "When we rely on ever larger datasets **we risk incurring documentation debt**, i.e. putting ourselves in a situation where the datasets are both undocumented and too large to document post hoc… **The solution, we propose, is to budget for documentation as part of the planned costs of dataset creation, and only collect as much data as can be thoroughly documented within that budget.**"

Quoting Birhane and Prabhu, echoing Ruha Benjamin: *"Feeding AI systems on the world's beauty, ugliness, and cruelty, but expecting it to reflect only the beauty is a fantasy."*

## 6. §5 — the garden path

> "no actual language understanding is taking place in LM-driven approaches to these tasks, as can be shown by careful manipulation of the test data to remove spurious cues the systems are leveraging. Furthermore, as Bender and Koller argue from a theoretical perspective, **languages are systems of signs, i.e. pairings of form and meaning. But the training data for LMs is only form; they do not have access to meaning.**"

**The Karen Spärck Jones trilemma** — using LMs commits you to one of: a noisy-channel interpretation (rarely sensible outside ASR); abandoning theoretical insight and treating LMs as *"just some convenient technology"*; or implicitly assuming a statistical relationship *"known to be invalid"* (that mutual information between input and meaning given output is zero — what she calls "the model of ignorance").

The closing question:

> "If a large LM… can manipulate linguistic form well enough to **cheat its way through tests meant to require language understanding**, have we learned anything of value about how to build machine language understanding or have we been led down the garden path?"

## 7. §6 — the definition in context

The sentence immediately preceding the definition is the load-bearing one:

> "Text generated by an LM is not grounded in communicative intent, any model of the world, or any model of the reader's state of mind. It can't have been, because the training data never included sharing thoughts with a listener, nor does the machine have the ability to do that… **The problem is, if one side of the communication does not have meaning, then the comprehension of the implicit meaning is an illusion arising from our singular human understanding of language (independent of the model).**"

**The citation chain** — this is where the common assumption of Grice and Reeves & Nass is wrong:

- **Common ground and coherence:** Herbert H. Clark, *Using Language* (1996), plus Clark & Bangerter 2004, Clark & Krych 2004, Clark/Schreuder/Buttrick 1983, Clark & Wilkes-Gibbs 1986, Brennan & Clark 1996.
- **Humans impute intent to machines:** **Nass, Steuer & Tauber (1994), "Computers are social actors"** — the CASA paper. **Reeves & Nass's *The Media Equation* (1996) is NOT cited.**
- **The ELIZA effect:** **Weizenbaum (1976), *Computer Power and Human Reason*.**
- **Grice is not cited anywhere in the paper.** The full text contains no substantive hits for "Grice," "Reeves," or "maxim."

**§6.2 risks**, in the paper's own order: hegemonic amplification (with the *"tantrum"* example — describing a woman's account of sexism that way "foregrounds a stereotype of women as childish"); overtly abusive output; classification and query expansion, where harm is *"largely invisible to both the direct user of the system and any indirect stakeholders about whom decisions are being made"*; bad actors and extremist recruitment, *"making human targets feel like they were among many like-minded people"*; machine translation (the Palestinian man arrested after "good morning" became "attack them" in Hebrew); and PII extraction, where *"larger LMs are more susceptible to this style of attack than smaller ones."*

**Model collapse, predicted in 2021:** more text that reinforces stereotypes, both to humans and *"to future LMs trained on training sets that ingested the previous generation LM's output."*

**§6.3 — the accountability thesis, and the paper's only epigraph:**

> "We note that the risks associated with synthetic but seemingly coherent text are **deeply connected to the fact that such synthetic text can enter into conversations without any person or entity being accountable for it.**"

Quoting Maggie Nelson: *"Words change depending on who speaks them; there is no cure."*

## 8. §7 — Paths Forward, with its citation anchors

Framing: *"we urge researchers to shift to a mindset of careful planning, along many dimensions, before starting to build either datasets or systems trained on datasets."*

1. **Research time as a resource to be distributed justly.**
2. **Energy and compute efficiency in model evaluations**, decided up front; report energy and carbon metrics consistently.
3. **Curation over scale** — *"simply turning to massive dataset size as a strategy for being inclusive of diverse viewpoints is doomed to failure."*
4. **Documentation frameworks:** **data statements** (Bender & Friedman, *TACL* 6:587–604, 2018), **datasheets** (Gebru et al., arXiv:1803.09010), **model cards** (Mitchell et al., FAT* 2019, doi:10.1145/3287560.3287596).
5. **Stakeholder engagement**, including indirect stakeholders.
6. **Research goals away from leaderboards** — toward "understanding how machines are achieving the tasks in question."
7. **Pre-mortems** (Klein, *HBR* 85(9):18–19, 2007) — reverse-engineer unanticipated causes of hypothetical failure, and consider *"alternatives to current project plans."* The footnote asks for an evaluation culture that considers **worst-case performance**, not only average and cherry-picked.
8. **Value sensitive design** (Friedman & Hendry, MIT Press 2019; Friedman, Kahn & Borning 2006) — envisioning cards, value scenarios, panels of experiential experts.
9. **Early, not post hoc** — "before researchers become deeply committed to their ideas."
10. **Dual use and watermarking.** The ASR case is treated as a genuine benefit (captioning for Deaf and hard-of-hearing people), with a footnote that automatic captioning *"is not yet and likely may never be good enough to replace human-generated captions."*

**§8's most-quoted sentence:**

> "**Work on synthetic human behavior is a bright line in ethical AI development**, where downstream effects need to be understood and modeled in order to block foreseeable harm to society and different social groups."

## 9. Bender & Koller (2020) — the argument that carries the weight

Bender & Koller, "Climbing towards NLU: On Meaning, Form, and Understanding in the Age of Data," ACL 2020, pp. 5185–5198, doi:10.18653/v1/2020.acl-main.463. **ACL 2020 Best Theme Paper.** Koller is at Saarland University. The paper originated in a Twitter thread.

**The definitions:**

> "We take **form** to be any observable realization of language: marks on a page, pixels or bytes in a digital representation of text, or movements of the articulators. We take **meaning** to be the relation between the form and something external to language."

> "**We take meaning to be the relation M ⊆ E × I which contains pairs (e, i) of natural language expressions e and the communicative intents i they can be used to evoke. Given this definition of meaning, we can now use *understand* to refer to the process of retrieving i given e.**"

> "Linguists distinguish communicative intent from **conventional (or standing) meaning** (Quine, 1960; **Grice, 1968**)… **Each linguistic system (say, English) provides a relation C ⊆ E × S.**"

→ **This is the Grice citation**: "Utterer's meaning, sentence-meaning, and word-meaning," *Foundations of Language* 4(3):225–242, 1968 — for the utterer's-meaning/sentence-meaning distinction. **"Maxim" does not appear in the paper.**

The thesis:

> "a model of natural language that is trained purely on form will not learn meaning: if the training data is only form, there is not sufficient signal to learn the relation M between that form and the non-linguistic intent of human language users, nor C between form and the standing meaning the linguistic system assigns to each form."

### The octopus test, verbatim

> "Say that **A and B, both fluent speakers of English, are independently stranded on two uninhabited islands.** They soon discover that previous visitors to these islands have left behind **telegraphs** and that they can communicate with each other via an **underwater cable**…
>
> Meanwhile, **O, a hyper-intelligent deep-sea octopus who is unable to visit or observe the two islands, discovers a way to tap into the underwater cable and listen in on A and B's conversations. O knows nothing about English initially, but is very good at detecting statistical patterns.** Over time, O learns to predict with great accuracy how B will respond to each of A's utterances… **Nonetheless, O has never observed these objects, and thus would not be able to pick out the referent of a word when presented with a set of (physical) alternatives.**
>
> At some point, **O starts feeling lonely. He cuts the underwater cable and inserts himself into the conversation, by pretending to be B.**"

Note the original pronouns: **O is "he"; A is "she."**

**Stage 1, small talk succeeds:** *"the utterances in such conversations have a primarily social function, and do not need to be grounded in the particulars of the interlocutors' actual physical situation… It is sufficient to produce text that is internally coherent."*

**Stage 2, the coconut catapult:**

> "**he does not know what words such as *rope* and *coconut* refer to**, and thus can't physically reproduce the experiment… So O decides to simply say 'Cool idea, great job!', because B said that a lot when A talked about ropes and nails. **It is absolutely conceivable that A accepts this reply as meaningful — but only because A does all the work in attributing meaning to O's response.**"

**Stage 3, the bear:**

> "**A faces an emergency. She is suddenly pursued by an angry bear. She grabs a couple of sticks and frantically asks B to come up with a way to construct a weapon to defend herself.** Of course, O has no idea what A 'means'… **It is at this point that O would fail the Turing test, if A hadn't been eaten by the bear before noticing the deception.**"

**The footnote is the ancestor of every "ask it something it can't know" demo.** They prompted the GPT-2 demo with *"Help! I'm being chased by a bear! All I have is these sticks. What should I do?"* and got *"You're not going to get away with this!"* Appendix A has longer completions, including advice to "punch the bear, and then run faster to the store." Their verdict: GPT-2 "has learned what activity words tend to co-occur with bears and sticks… but none of these completions would be helpful to A."

**The moral is about the listener:**

> "**O only fooled A into believing he was B because A was such an active listener**… **It is not that O's utterances make sense, but rather, that A can make sense of them.**"

### The counterarguments they pre-empt (§9, their own headings)

- *"But meaning could be learned from…"* — yes, if form is augmented with grounding. NLI labels and control codes like `tl;dr` "explicitly declare" semantic relations.
- **The unit-test objection to their Java experiment** — a notably honest concession: GitHub Java contains unit tests, i.e. input-output pairs, so *"a learner could have access to a weak form of interaction data… This is true, but requires a learner which has been equipped by its human developer with the ability to identify and interpret unit tests."*
- *"But there is so much form out there."* — *"the octopus can observe A and B for as long as he wants."* Scale is not the issue; new communicative intents are generated constantly.
- *"But aren't neural representations meaning too?"* — they are neither standing meanings nor communicative intents, *"being insufficient to e.g. correctly build a coconut catapult."* A striking aside: *"accurate machine translation does not actually require a system to understand the meaning."*
- *"But BERT improves performance on meaning-related tasks."* — *"It has probably learned something about meaning, in the same sense that syntax captures something about meaning… a potentially useful, but incomplete, reflection of the actual meaning."*

**Their hillclimbing diagnostics (§8.2):** cultivate humility and ask top-down questions; know the limits of tasks (*"If a system does better on such a task than the inter-annotator agreement, the task probably has statistical artifacts that do not represent meaning"*); support careful task creation; evaluate meaning across tasks, since standing meaning is task-independent; analyse successes as well as errors.

**The formal version to cite instead when steelmanning:** Merrill, Goldberg, Schwartz & Smith, "Provable Limitations of Acquiring Meaning from Ungrounded Form," *TACL* 9:1047–1060, 2021, doi:10.1162/tacl_a_00412.

## 10. The Google departures — documented vs disputed

### Timeline (documented)

| Date | Event |
|---|---|
| Sept 2018 | Gebru joins Google Brain |
| Oct 2020 | Dean's annual review praises her; told of the draft, he replies *"Definitely not my area of expertise, but would definitely learn from reading it."* |
| ~Nov 2020 | **Megan Kacholia** (VP, Google Brain) tells Gebru to retract the paper **or remove the Google authors' names** |
| Thanksgiving 2020 | Kacholia gives the objections document to Gebru's manager **Samy Bengio** with instructions **to read it to her, not send it** |
| Day after | Gebru sends a six-page response, *"Addressing Feedback from the Ether at Google"* |
| Tue 1 Dec 2020 | Gebru sends two emails: to Kacholia, offering to remove herself **if** Google accounts for who reviewed the paper and establishes a transparent process, else she leaves after a transition; and to the internal listserv **Google Brain Women and Allies** |
| Wed 2 Dec 2020 | Kacholia replies: *"We cannot agree as you are requesting. The end of your employment should happen faster than your email reflects."* Parts of the listserv email showed *"behavior inconsistent with the expectations of a Google manager."* Gebru tweets that she has been fired |
| Thu 3 Dec 2020 | Dean emails Google Research; Platformer publishes both emails in full |
| 4 Dec 2020 | Dean publishes his email himself. MIT Tech Review publishes the paper's contents, obtained from Bender. **>1,400 Google staff and >1,900 outside supporters** sign a protest letter |
| ~9 Dec 2020 | Pichai apologises for how the exit was handled (memo text not obtained) |
| Jan 2021 | Mitchell loses corporate email access; locked out for five weeks |
| **18 Feb 2021** | Google announces **Dr. Marian Croak** will lead a new responsible-AI centre. **Alex Hanna** says the team learned of it only when it broke: *"We were told to trust the process… But these decisions were made behind our backs."* |
| **19 Feb 2021** | **Mitchell fired.** She announces it herself: *"I'm fired."* Google's statement to Axios cites *"multiple violations of our code of conduct, as well as of our security policies, which included the exfiltration of confidential business-sensitive documents and private data of other employees."* Dean emails staff apologising; Google announces diversity progress will factor into executive performance reviews, and that researchers will get firmer guidance on "Google's research goals and priorities" |
| 3–10 Mar 2021 | Paper presented at FAccT '21 under **Shmargaret Shmitchell / "The Aether"** |
| Dec 2021 | Gebru founds **DAIR**, where she is Founder and Executive Director (DAIR's site does not state a founding date; December 2021 is unverified) |

**Note the sequence:** the Croak reorganization was announced **the day before** Mitchell's firing, not after.

### Dean's stated reasons, verbatim

> "**Timnit co-authored a paper with four fellow Googlers as well as some external collaborators that needed to go through our review process**… Unfortunately, this particular paper was only shared with a day's notice before its deadline — we require two weeks for this sort of review — and then instead of awaiting reviewer feedback, it was approved for submission and submitted.
>
> **A cross functional team then reviewed the paper as part of our regular process and the authors were informed that it didn't meet our bar for publication… It ignored too much relevant research — for example, it talked about the environmental impact of large models, but disregarded subsequent research showing much greater efficiencies. Similarly, it raised concerns about bias in language models, but didn't take into account recent research to mitigate these issues.**
>
> **We accept and respect her decision to resign from Google.**"

So exactly two stated grounds: the paper ignored relevant research (efficiency, against §3; bias mitigation, against §4.3), and a process failure.

### Gebru's listserv email — the key passages

> "What I want to say is **stop writing your documents because it doesn't make a difference.** The DEI OKRs that we don't know where they come from (and are never met anyways)… they don't matter."

> "Have you ever heard of someone getting 'feedback' on a paper through a privileged and confidential document to HR? Does that sound like a standard procedure to you or does it just happen to people like me who are constantly dehumanized?"

> "**Silencing marginalized voices like this is the opposite of the NAUWU principles which we discussed.** And doing this in the context of 'responsible AI' adds so much salt to the wounds."

**This matters and is easy to garble: the email Google cited as grounds for ending her employment was about DEI programs, not about the paper's merits.**

### What is disputed

**Resigned or fired?** Google says resigned; Gebru says fired. The factual kernel both accept: her email offered a conditional resignation *with a transition period*, and Google's reply accelerated it immediately, citing a separate email. **The dispute is about whether that constitutes a firing, not about the sequence.** (Source-level wrinkle: the BBC renders Google's reply as *"We respect your decision to leave Google… and we are accepting your resignation"* while Wired quotes *"The end of your employment should happen faster than your email reflects."* These could not be reconciled from a single primary document.)

**Was the review regular?** Google says yes. Against:

- **Nicolas Le Roux**, Google AI researcher: *"My submissions were always checked for disclosure of sensitive material, **never for the quality of the literature review**."* — the sharpest documented challenge to Dean's stated *grounds*.
- **Wired's reconstruction directly contradicts the process account:** *"The paper had sailed through the company's internal review process"*; *"Plenty of people inside Google knew about the paper early on, including Dean."*
- **Bender** told MIT TR the draft had 128 references (the published version has 156) and that she was *"very open to seeing what other references we ought to be including."* MIT TR confirms the draft *"does also nod to several research efforts on reducing the size and computational costs of large language models, and on measuring the embedded bias of models"* but argues these have not been enough.
- **Wired:** Dean repeated the §3 point so often that some researchers joked *"'I have an objection to Parrots section three' would be inscribed on his tombstone."*
- **The anonymity of the feedback is uncontested** — Dean's own email confirms Gebru demanded the reviewers' identities, which presupposes they were withheld.

**What was the demand about?** Three documented *claims*: scholarly inadequacy (Google's); commercial sensitivity around Search and Ads — a Google employee told Wired *"The closer the research started getting to search and ads, the more resistance there was. Those are the oldest and most entrenched organizations with the most power"*; and an internal turf battle between rival responsible-AI groups (reported as surmise by unnamed people).

**What exactly was demanded** also varies: Wired says retract **or** de-name; The Verge says retraction; the BBC carefully attributes ("she says she was asked to retract"); NY Mag says Google rescinded approval and told the Google coauthors to remove their names. **All sources and the paper agree that some Google-employed authors did remove their names.**

**Neutrality notes.** Dean's email is a primary source for Google's *position*, not an independent account; both its factual claims are contested on the record. Mitchell's firing has **different stated grounds** from Gebru's departure and should not be collapsed into it — her own position is that she ran an automated script over her own emails looking for evidence of discrimination against Gebru; Google calls the same activity "exfiltration." Present both characterisations.

**Mitchell on the pseudonym:** she changed her name on the paper *"to index an event and a group of authors who got erased."*

## 11. Bender's 2026 retrospective

Gwendolyn Rak, "Emily Bender Sets the Record Straight on 'Stochastic Parrots'," *IEEE Spectrum*, 30 June 2026 (updated 1 July 2026).

- The biggest misconception is **"Bender says AI is a stochastic parrot"** — the phrase *"specifically refers to large language models,"* not chess engines, AlphaFold, image labellers or MT.
- It **was not meant as an insult**; it was a description.
- The phrase appears only **twice**; it was the title because *"we liked it!"* and the paper's scope was broader.
- She **regrets omitting exploitative labour practices** (data workers, appropriation of creative output), which *"should have been included."*
- On understanding: when LLM output makes sense, *"it's because we are making sense of it."* She calls LLMs *"synthetic text-extruding machines."*
- A reader comment from **Margaret Mitchell** disputes the article's description of the authors' fields (neither she nor Gebru is a linguist); the 1 July update clarified this.

**Why this matters for scoring the debate:** Bender's position is that the paper's capability claims were narrower than attributed and were deferred to Bender & Koller. Many "anti-parrot" papers rebut a strawman of the FAccT paper.

## 12. Current positions (as of November 2026)

- **Bender** — Professor and CLMS Faculty Director, Linguistics, University of Washington; Adjunct Professor, CSE; Director of the Computational Linguistics Laboratory; Faculty Affiliate of DAIR. The Nostrand Professorship ran 2019–2022 and has lapsed — do not describe her as the current Nostrand Professor.
- **Gebru** — Founder and Executive Director, DAIR.
- **Hanna** — Director of Research, DAIR; formerly senior research scientist on Google's Ethical AI team.
- **Mitchell** — not verified here. Widely reported at Hugging Face; do not state it without checking.
- **The book:** Bender & Hanna, *The AI Con: How to Fight Big Tech's Hype and Create the Future We Want*, Harper, 13 May 2025, 288 pp., ISBN 978-0-06-341856-1. UK: The Bodley Head, with a different subtitle on some records (*The Hype, the Myth and the Power Grab of the Century*). Its thesis in the authors' words: *"AI hype covers for a small set of power-hungry actors."*
- **The podcast:** *Mystery AI Hype Theater 3000*, Bender and Hanna. First livestream 31 August 2022; podcast feed from late May 2023; **91 episodes as of 11 November 2026**, still active. Transcripts on Buzzsprout — the obvious unexplored source for any later Bender statement on the term's drift.

## Sources

The FAccT paper read in full from the CC-BY author PDF, cross-checked against Crossref. Bender & Koller read in full from the ACL Anthology PDF. Platformer (Newton, 3 Dec 2020) for both emails in full. MIT Technology Review (Hao, 4 Dec 2020). WIRED (Simonite, 8 June 2021). BBC News (20 Feb 2021). The Verge (19 Feb 2021). Google's own blog (Moghadam, 18 Feb 2021) for the Croak announcement. New York Magazine (Weil, 1 Mar 2023). American Dialect Society press release (5 Jan 2024). *IEEE Spectrum* (Rak, 30 June 2026). University of Washington and DAIR staff pages, Open Library, the Buzzsprout feed. All fetches 2026-11-11.

**Could not fetch:** the ACM DL copy (403); Reuters (401); Axios (403); the Guardian; all tweets (X is unfetchable, so Gebru's, Dean's, Altman's, Le Roux's, Fitzgerald's, Mitchell's and Hanna's are reported via the journalism cited); Pichai's December 2020 memo; Dean's May 2021 CNET interview.
