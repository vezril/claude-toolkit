# The debate: emergence, world models, compression, philosophy

Everything here is sourced; each author's own stated limits are kept with their claim, because in this literature the limits are usually the interesting part.

## 1. Emergent abilities

### Wei et al. — the original claim

Wei, Tay, Bommasani, Raffel, Zoph, Borgeaud, Yogatama, Bosma, Zhou, Metzler, Chi, Hashimoto, Vinyals, Liang, Dean & Fedus, "Emergent Abilities of Large Language Models," *TMLR* 08/2022, arXiv:2206.07682.

**Definitions, verbatim:**

> "Emergence is when quantitative changes in a system result in qualitative changes in behavior." (adapted from Steinhardt 2022, rooted in Philip Anderson's 1972 "More Is Different")

> "An ability is emergent if it is not present in smaller models but is present in larger models."

> "Emergent abilities would not have been directly predicted by extrapolating a scaling law from small-scale models."

They call the shape "a phase transition," measure scale in training FLOPs, and caution that emergence "should probably be viewed as a function of many correlated variables."

**The documented jumps:** BIG-Bench 3-digit arithmetic at **2·10²² FLOPs (13B) for GPT-3**, 10²³ (68B) for LaMDA; **TruthfulQA** — GPT-3 never above random at any size, Gopher only at **5·10²³ (280B)**; **MMLU** — at chance around 10²² (~10B), substantially above random at **3–5·10²³ (70B–280B)**. Augmented prompting counts as emergent if **neutral-or-harmful** below a scale: **chain-of-thought** only beats standard prompting at 10²³ FLOPs (~100B); **instruction tuning *hurts*** at ≤7·10²¹ (8B) and helps only at ~10²³.

**⚠️ Wei et al. pre-empted the metric objection in their own §5.1** — the single most-missed fact in this debate:

> "using exact string match as the evaluation metric for long-sequence targets may disguise compounding incremental improvements as emergence."

They argue it is insufficient because "the jump in final answer accuracy does not explain why the quality of intermediate steps suddenly emerges to above random," and because emergence appears on classification tasks that do give partial credit. In Appendix A they report cross-entropy improving for six emergent tasks where exact-match is flat — then concede this "does not explain why downstream metrics are emergent."

§5.2 shows scale is not the only lever (PaLM 62B beats LaMDA 137B and GPT-3 175B on 14 BIG-Bench tasks). §5.4 notes **risks may emerge too**.

### Schaeffer, Miranda & Koyejo — the mirage argument

"Are Emergent Abilities of Large Language Models a Mirage?", *NeurIPS 36*, pp. 55565–55581, arXiv:2304.15004. **NeurIPS 2023 Outstanding Main Track Paper** (one of two) — confirmed on the official NeurIPS blog, 11 Dec 2023. **Not a runner-up.**

**The mathematical model.** With per-token cross-entropy falling as a power law `L_CE(N) = (N/c)^α`, per-token correctness is `p = exp(−L_CE(N))`. Then:

```
Accuracy (all L tokens correct)  ≈ p^L      → decays geometrically  → looks like a threshold
Token Edit Distance              ≈ L(1 − p) → quasi-linear          → looks smooth
```

**Three predictions, all confirmed** on InstructGPT/GPT-3 arithmetic (350M, 1.3B, 6.7B, 175B): swapping Accuracy for Token Edit Distance on the *same outputs of the same models* reveals smooth improvement; increasing test-set resolution puts **every** model above chance; and performance falls predictably with target length in the metric-specific way.

**The BIG-Bench meta-analysis.** Only **4–5 of 39** preferred metrics ever show emergence. **Multiple Choice Grade (discontinuous) and Exact String Match (nonlinear) account for >92%** of claimed emergent abilities. LaMDA's emergence under Multiple Choice Grade disappears under the continuous Brier Score. And the multiple-comparisons point: ≥220 tasks × ~40 metrics × ~10 model families ≈ **10⁶ triplets**, so spurious emergence is near-certain without correction.

**They induce emergence at will** in architectures nobody calls emergent — shallow autoencoders on CIFAR-100 under a thresholded reconstruction metric, LeNet on MNIST under subset accuracy, Transformers on Omniglot.

**⚠️ Their explicit disclaimer:** they do **not** claim LLMs cannot have emergent abilities. Previously claimed abilities "might likely be a mirage induced by researcher analyses" and "may be creations of the researcher's choices." The thesis is about **evidence and measurement**. Using it as "LLMs don't really gain new abilities" is a misreading.

### The rebuttals of the rebuttal

**Lu, Bigoulaeva, Sachdeva, Tayyar Madabushi & Gurevych, "Are Emergent Abilities in Large Language Models just In-Context Learning?", ACL 2024, pp. 5098–5139**, doi:10.18653/v1/2024.acl-long.279. Over 1,000 experiments. Purported emergent abilities "are not truly emergent, but result from a combination of **in-context learning, model memory, and linguistic knowledge**." A *different* deflation from Schaeffer's — about confounded causes, not metrics. They adopt Mahowald et al.'s formal/functional split.

**Berti, Giorgi & Kasneci, "Emergent Abilities in Large Language Models: A Survey," arXiv:2503.05788** — skeptical of the mirage argument. Their specific critiques: Token Edit Distance scores a *wrong* arithmetic answer as nearly correct (4237+5487 → 2724 is a one-token edit), so the "continuous" metric isn't measuring the ability; the claimed qualitative match lacks statistical rigour; log-scale plots can conceal residual jumps; the emergence-score threshold of 100 is stringent. They cite counter-evidence that emergence survives continuous metrics, including **Du et al. (2024)** on Brier Score jumps on MMLU and C-Eval and a **pre-training-loss threshold** after which downstream performance jumps largely independent of parameter count. ⚠️ Those 2025/2026 citations are as the survey reports them and were **not** independently verified.

**Ganguli, Hernandez, Lovitt, Askell, Bai, Chen, Conerly, DasSarma et al., "Predictability and Surprise in Large Generative Models," FAccT 2022, pp. 1747–1764**, doi:10.1145/3531146.3533229. Aggregate loss is *predictable* from scale while *specific* capabilities are *unpredictable* — compatible with both Wei and Schaeffer, and it shifts the live question to "can we forecast which capability appears when?"

**Induction heads — the strongest metric-independent counterexample.** Olsson, Elhage, Nanda, Joseph, DasSarma, Henighan, Mann, Askell, Bai, Chen, Conerly, Drain, Ganguli, Hatfield-Dodds, Hernandez, Johnston, Jones, Kernion, Lovitt, Ndousse, Amodei, Brown, Clark, Kaplan, McCandlish & Olah, "In-context Learning and Induction Heads," *Transformer Circuits Thread*, **8 March 2022**; arXiv:2209.11895, **24 September 2022** (⚠️ cite both dates).

An induction head is a two-head circuit: a previous-token head copies the prior token forward; the induction head attends to the token that *followed* an earlier occurrence of the current token — `[A][B] … [A] → [B]`. Defined behaviourally by **prefix matching** and **copying**.

**The phase change.** In-context learning appears abruptly in a narrow window **~2.5 to 5 billion training tokens**, coincident with induction-head formation, and shows as a visible **bump in the training loss curve**. ICL score (loss at token 50 minus loss at token 500) is **<0.15 nats before** and **≈0.4 nats after**, then flat. The plateau holds across sizes; the exception is the **one-layer** model, where almost no ICL forms — consistent with the two-layer circuit story.

Because the signal is in the loss itself and in a continuous nats-based score, this is **largely immune to Schaeffer's argument**. Note the difference in kind: it is a phase change **over training time**, not over scale.

**Their own honesty about strength** — worth quoting: for small attention-only models the evidence is **strong and causal**; for larger models with MLPs it is **correlational**. They call the whole a "circumstantial case" and "only the beginnings of evidence," and concede "a large number of subtle confounds or alternative hypotheses are possible."

### The 2026 reframing

**Krakauer, Krakauer & Mitchell, "Large language models and emergence: a complex systems perspective," *Phil. Trans. R. Soc. A* 384(2320):20250014, 14 May 2026**, doi:10.1098/rsta.2025.0014; preprint arXiv:2506.11135.

- Emergence = "the reorganization of a system that can support a new, often smaller description"; the minimal signature is "a coarse-graining of observables coupled to a compression of the system description" that remains predictive. **Abruptness is not required** — which reframes the whole Wei/Schaeffer dispute as arguing about the wrong diagnostic.
- Five non-exclusive conditions: **scaling, criticality, compression, novel bases, generalization**.
- **Knowledge-Out (KO)** emergence (complex behaviour from simple interactions among simple elements — physics, chemistry) vs **Knowledge-In (KI)** emergence (complex behaviour from complex inputs — evolved and learned systems). **LLMs are KI**, so an emergence claim must establish *both* the global property *and* the local mechanism.
- "More is different" (capability) vs "**less is more**" (intelligence as compact, efficient, analogy-driven problem solving). A calculator is capable but not intelligent in that sense.
- On the mirage paper: they describe it but **do not adopt it**; their own objection goes further — "it is not clear that LLM abilities have clear 'phases'."
- Verdict: LLMs at best "demonstrate emergent capability"; evidence across all three claim families is "provocative" but "in all cases that evidence is incomplete." Emergent *intelligence* is "an unproven feature of LLMs."
- **The point that cuts both ways:** the more world-structure is already encoded in language, the **weaker** emergence claims become — the model may be fitting the data rather than building a coarse-grained internal model.

## 2. World models — the probing literature

### Othello-GPT

**Li, Hopkins, Bau, Viégas, Pfister & Wattenberg, "Emergent World Representations," ICLR 2023** (oral, notable-top-5%), arXiv:2210.13382.

An 8-layer, 8-head, 512-dim GPT variant trained from scratch on next-move prediction. Vocabulary = **60 tokens**, one per placeable tile. **No board structure, no rules, no board state in the input** — only move indices. Not trained to win.

- **Legal-move top-1 error: 0.01% (synthetic), 5.17% (championship), 93.29% (untrained).** A "skewed" set with one opening removed still gives 0.02% — their argument against pure memorisation, with the caveat they state that different move orders reach the same board state.
- **Linear probes: poor** (~20%+ error). *"it does not have a simple linear form."*
- **Nonlinear MLP probes: good** — ~**1.7% error at layer 6** (synthetic); randomised-network baseline ~25–26%.
- **Causal intervention:** change one tile's probe-predicted state by gradient descent on activations from layer 4 onward, then read the next-move prediction. Average errors **0.12 / 0.06** on natural/unnatural positions vs baselines **2.68 / 2.59**. Representations are "causal to model predictions."
- **Latent saliency maps:** the synthetic model "shows high saliency for precisely those tiles that are required to make a move legal."

**Limits the paper states:** one synthetic game, one small model. The probe is nonlinear, so accuracy shows information is *recoverable*, not that the model uses it simply. Saliency fails when a move flips discs along several lines. Intervening on shallow layers is "hazardous." Championship accuracy is much lower. (Internal inconsistency noted on inspection: the randomised-probe baseline is 52.95% in text but ~47% in a footnote, and the main results use L_s = 4 while Appendix G's sweep uses L_s = 5.)

### Nanda's correction — it is linear after all

**Nanda, "Actually, Othello-GPT Has A Linear Emergent World Representation," LessWrong, 29 March 2023.** Paper version: **Nanda, Lee & Wattenberg, BlackboxNLP 2023, pp. 16–30**, doi:10.18653/v1/2023.blackboxnlp-1.2.

**The correction:** the board state *is* linearly represented — but in **"my colour / their colour"** terms, not black/white. Because the model alternates sides, the player-relative frame fits its computation, and **Li et al.'s nonlinear probe plausibly learned an XOR** of "I am playing white" and "this square has my colour" — which is exactly why a linear probe in the black/white frame failed.

How he found it: activation patching → interpretable neurons → neurons firing on alternating moves with parity flipping → **neuron L5N1393** tracking a square-pair condition conditioned on move parity. Probes trained separately on odd and even moves **transfer across sides when the sign is flipped**.

**His own assessment of the weakest part:** interventions work but edits don't fully restore originally-legal logits, which he attributes to untuned hyperparameters, computation spread across layers and dropout-induced redundancy — *"I consider this the weakest part of my investigation."* And: *"this is preliminary work on a toy model, and generalising to language models is speculative."*

### The counter-counter — a bag of heuristics

**Lin, JackS, Karvonen & Rager, "OthelloGPT learned a bag of heuristics," LessWrong, 2 July 2024** — interim report from Neel Nanda's MATS 6.0.

The board state is computed by **many independent, board-position-specific decision rules**, not a unified world model. *"Our best guess is that Othello-GPT's learned algorithm is just a bag of independent heuristics."*

- Linear probes show the board representation repeatedly up- and down-weighted across layers 0–4 — consistent with many useful but imperfect rules.
- Concrete rule: **L1N421** ≈ "if A4 was just played and B4 and C4 are occupied, update B4+C4+D4 toward 'theirs'," gated by **L0N377** checking whether B4 is occupied. **This rule does not generalise across board translations.**
- **610 "board pattern neurons"** whose union-of-patterns classification reaches **F1 > 0.99 over 60k board states**; some are "clock neurons" tracking move number rather than moves played.
- Individual heuristics are sometimes wrong and get corrected by other neurons or later layers.

Their caveats: interim; a succinct algorithm is not ruled out; circuit analysis used 50 games; probes trained only on layer 6; ablation effects small for layers 3–6.

**Krakauer et al.'s fair summary:** OthelloGPT is "a different form of emergence" from Wei et al.'s — **no scaling was involved**. And: "the internal model may not have been as parsimonious or 'compressed' as implied in the original papers… Moreover, there was only weak evidence that the emergent representation was causally responsible for the network's ability to predict legal moves."

### Space and time

**Gurnee & Tegmark, "Language Models Represent Space and Time," arXiv:2310.02207** (ICLR 2024 attribution is conventional, unverified).

Six datasets (world/USA/NYC places; historical figures by death year 1000 BC–2000 AD; art release dates; NYT headlines). Base Llama-2 7B/13B/70B. Ridge-regression probes on the residual stream at the last entity token.

At 60% depth, **Llama-2-70B linear probes reach R² ≈ 0.91 (world places), 0.86 (USA), 0.36 (NYC)**. A nonlinear MLP probe adds little — evidence the representation is **linear**. PCA shows Spearman correlation rising faster than R², suggesting the model uses **its own** coordinate system. Individual "space neurons" and "time neurons" exist, with ablation and intervention effects — but these are explicitly **small-scale case studies**.

**Their own limits, which are the load-bearing part:** high probe accuracy "does not imply that the model actually uses these representations"; probes may be learning the mapping to human coordinates; the data is "skewed towards the Anglosphere"; single neurons are a **lower bound** because of superposition; block holdout is only **"weak evidence"** that probes extract learned features rather than memorising; and they **"conjecture, but do not show, these basic primitives underlie a more comprehensive causal world model."** The abstract claims only "basic ingredients of a world model."

### Other strong evidence

- **Abdou, Kulmizev, Hershcovich, Frank, Pavlick & Søgaard, "Can Language Models Encode Perceptual Structure Without Grounding? A Case Study in Color," CoNLL 2021**, pp. 109–132, doi:10.18653/v1/2021.conll-1.9. (**CoNLL**, not EMNLP.) Monolexemic English colour terms against colour chips in **CIELAB**. Significant structural alignment ⇒ "some approximation of perceptual color space topology can indeed be learned from text alone"; **warmer colours align better than cooler ones**. Framed explicitly as a reply to Bender & Koller, Bisk et al. and Merrill et al.
- **Jin & Rinard, "Emergent Representations of Program Semantics in Language Models Trained on Programs," ICML 2024**, PMLR 235:22160–22184, arXiv:2305.11169. A probe recovers **unobserved intermediate grid states** from hidden states with increasing accuracy over training. **They introduce an interventional baseline to separate what the model represents from what the probe learns** — methodologically the right move, and the template for good practice here.
- **Marks & Tegmark, "The Geometry of Truth," COLM 2024**, arXiv:2310.06824. Visualisation, **transfer** across datasets, and **causal interventions** that make false statements be treated as true. "at sufficient scale, LLMs linearly represent the truth or falsehood of factual statements"; simple **difference-in-mean** probes generalise about as well as fancier ones. They are upfront that probing for falsehood is "controversial, since probes can fail to generalize in basic ways."
- **Anthropic, "Mapping the mind of a large language model," 21 May 2024.** Millions of features from the middle layer of Claude 3 Sonnet via sparse autoencoders; **feature steering** changes behaviour (Golden Gate Bridge self-identification; a scam-email feature overriding harmlessness training). Their own caveats: this doesn't show *how* the model uses the representations, and circuits remain open. ⚠️ The underlying paper is Templeton et al., "Scaling Monosemanticity," *Transformer Circuits Thread*, 2024 — **author list and exact date unverified here.**
- **Patel & Pavlick, "Mapping Language Models to Grounded Conceptual Spaces," ICLR 2022** — venue verified, but ⚠️ **the method and results were not retrievable** (OpenReview CAPTCHA, no arXiv version, no DOI). Do not describe its rotated/isomorphic mapping conditions.

### The methodological bottom line

Every result here is a **probing** result, and the field's own best practice now demands three things together:

1. the probe decodes the property,
2. a **causal intervention** on the probed direction changes behaviour as predicted,
3. a **control** showing the probe isn't doing the work itself.

Li et al. have (1)+(2). Nanda tightens (1) and admits (2) is weak. Jin & Rinard supply (3). Gurnee & Tegmark are explicit that they lack (2) at scale. **Lin et al. show that (1)+(2) can both hold while the underlying computation is still a pile of position-specific heuristics.**

**The honest claim the counterargument can sustain is "not surface statistics over tokens" — not "a unified, compositional world model."**

## 3. Compression

**Sutskever's version**, from the GTC 2023 fireside chat with Jensen Huang:

> "When we train a large neural network to accurately predict the next word in lots of different texts from the Internet, what we are doing is that we are learning a world model. It may look—on the surface—that we are just learning statistical correlations in text. But it turns out that to 'just learn' the statistical correlations in text, to compress them really well, what the neural network learns is some representation of the process that produced the text. This text is actually a projection of the world."

Also: "the better a neural network can predict the next word in text, the more it understands it"; "If you compress the data really well you must extract all the hidden secrets which exist in it." See also his talk "An Observation on Generalization," Simons Institute, 14 August 2023.

⚠️ **Two provenance problems.** The date is disputed — the transcript source dates it **15 March 2023** ("the day after GPT-4 release"), NVIDIA's blog **22 March 2023** (GTC ran 20–23 March); most likely recorded ~15 March, aired 22 March. And **the only reachable transcript was generated with Whisper and edited by LifeArchitect.ai — not official.** This is the one famous quote in this material with non-authoritative provenance.

**The formal result.** Delétang, Ruoss, Duquenne, Catt, Genewein, Mattern, Grau-Moya, Wenliang, Aitchison, Orseau, Hutter & Veness, "Language Modeling Is Compression," arXiv:2309.10668.

| Data | Chinchilla 70B | Domain-specific baseline |
|---|---|---|
| ImageNet patches | **43.4%** | PNG 58.5% |
| LibriSpeech samples | **16.4%** | FLAC 30.3% |

Chinchilla 70B was trained **predominantly on text** yet beats purpose-built image and audio codecs. The equivalence runs both ways: any compressor (gzip) can be turned into a conditional generative model.

### Counter-counters

1. **Block's "Blockhead."** Block, "Psychologism and Behaviorism," *The Philosophical Review* 90(1):5–43, 1981, doi:10.2307/2184371. A machine passes any finite behavioural test via a vast pre-computed string tree with no intelligence. Applied here: in the limit of finite context and finite task length, a sufficiently large table achieves arbitrarily good next-token prediction with no world model. **The reply is about capacity and compression, not possibility** — the needed table is astronomically larger than the model, so the model must be doing something that generalises. **The disagreement is therefore quantitative, not conceptual** — how much compression licenses what inference.
2. **Single-pass expressivity is provably bounded.** Fixed-depth transformers are limited in serial computation per forward pass; chain-of-thought buys back serial depth. ⚠️ Merrill & Sabharwal's chain-of-thought expressivity paper (arXiv:2310.07923 / ICLR 2024) is cited from memory and **unverified**; verified neighbours by the same authors: "Exact Expressive Power of Transformers with Padding," *NeurIPS 38* (2025), pp. 124733–124760, and "A Little Depth Goes a Long Way."
3. **Good prediction is often reducible to n-gram-ish rules.** Nguyen, "Understanding Transformers via N-Gram Statistics," *NeurIPS 37* (2024), pp. 98049–98082, doi:10.52202/079017-3112. ⚠️ Citation verified only; do not attribute specific percentages.
4. **"A projection of the world" is not "the world."** Krakauer et al.'s point bites hardest here: the compression argument assumes the model must *reconstruct the generative process*; it could instead be exploiting that the text already contains the answer in redundant form.
5. **Bender does not engage it on its own ground.** Her move is to deny the question is about the model at all — *"when LLM output makes sense, it's because we are making sense of it"* — so evaluation must factor out human sense-making. That is a claim about the *evidential status of fluent output*, and it is **not refuted by compression results**; it has to be met with the probing evidence instead. **Worth saying plainly: the compression and anthropomorphism arguments talk past each other. Only the probing arguments engage.**

## 4. Philosophy

### Searle and the Chinese Room

Searle, "Minds, brains, and programs," *Behavioral and Brain Sciences* 3(3):417–424, September 1980, doi:10.1017/S0140525X00005756. The same issue carries the open peer commentary — the right place to cite the original replies.

From the **Stanford Encyclopedia of Philosophy**, "The Chinese Room Argument" (first published 19 March 2004; substantive revision **23 October 2024**):

- **The narrow reductio:** if Strong AI is true there is a program such that any system running it understands Chinese; Searle could run it without understanding; therefore Strong AI is false.
- **The broader version:** programs are purely syntactic, minds have semantic contents, **"Syntax is not by itself sufficient for, nor constitutive of, semantics."**
- **Systems Reply** — the whole system understands. **Searle:** he could internalise it all and still not understand.
- **Virtual Mind Reply** — the running system constitutes a distinct *virtual* mind. **This is the reply most directly applicable to LLMs**: the persona is not the substrate.
- **Robot Reply** — embed it in sensors. **Searle:** sensor input is just more syntax.
- **Brain Simulator Reply** — **Churchlands'** "luminous room" analogy: intuitions about complex systems are unreliable.
- **Criticisms:** **Block** — the argument "depends for its force on intuitions that certain entities do not think." **Dennett** — an "intuition pump," later "clearly a fallacious and misleading argument." **Chalmers** — the recipe parody: syntax alone doesn't make a cake crumbly either.
- **The entry's own LLM material** contains a genuinely useful dialectical point: ChatGPT, asked about Searle, says its processing lacks genuine comprehension — which the entry calls **self-contradictory**, since its other outputs claim understanding. It observes that a system *denying* understanding would fail the Turing Test, and that a future system avoiding such "locutionary suicide" would make "really" understanding undetectable and hence **epiphenomenal**. **If no behavioural or mechanistic test could distinguish real from simulated understanding, the distinction does no explanatory work.**

**Is the parallel apt?** The strongest disanalogy: the Chinese Room stipulates a **hand-written rulebook with no learning and no internal representation**. An LLM's weights are *learned* and demonstrably contain decodable, sometimes causally-efficacious representations of non-linguistic structure. **"It's just syntax" is a claim about the *form* of the implementation; the probing results are claims about the *content* of learned states.** Conflating them is the category error the counterargument alleges. The strongest reply on Searle's side: **decodability is not aboutness** — the probe supplies the interpretation.

⚠️ The SEP fetch was truncated partway through §5.1; the Many Mansions Reply and the bibliography are uncovered, and the entry author (David Cole) was not visible in the fetched portion.

### Chalmers

Chalmers, "Could a Large Language Model be Conscious?", arXiv:2303.07103; *Boston Review*, 9 August 2023. Comments field says **invited lecture** at NeurIPS, 28 November 2022 — not keynote.

Evidence *for*: self-report, seems-conscious, conversational ability, general intelligence. Evidence *against* (his six X's): **biology, senses and embodiment, world models and self models, recurrent processing, global workspace, unified agency.**

His assessment: these "arguably include the most important current obstacles," though "it's entirely possible that there are unknown X's." **"Perhaps the strongest objections are those from recurrent processing, global workspace, and unified agency."** And: "for all of these objections except perhaps biology, it looks like the objection is temporary rather than permanent."

**His explicit credences:**

- "at least a one-in-three chance" that biology is required; the same for each of the other five.
- If independent, "less than a one-in-ten chance that a system lacking all six, like a current paradigmatic LLM, would be conscious."
- Net: **"confidence somewhere under 10 percent in current LLM consciousness"** — with the caveat "You shouldn't take the numbers too seriously (that would be specious precision)."
- Future: **over 50%** that we'll have sophisticated LLM+ systems with all these properties within a decade, and **at least 50%** that such systems would be conscious ⇒ **"a credence of 25 percent or more"** for conscious LLM+s within a decade.
- Footnote 29: his own views "lean somewhat more to consciousness being widespread" than mainstream.

**Relevant to the probing literature:** in *X = World Models and Self Models* he explicitly discusses **Othello-GPT** and reframes the question as "not whether it's possible for language models to have world-models and self-models, but instead whether these models are" deep and robust. A philosopher treating the empirical probing work as directly load-bearing.

### Shanahan — the careful middle

Shanahan, "Talking about Large Language Models," *CACM* 67(2):68–79, doi:10.1145/3624724 (online 25 January 2024); preprint arXiv:2212.03551.

⚠️ **Correction to a common paraphrase:** "LLMs do not have beliefs" does **not** appear. His wording is qualified — a simple LLM-based question-answering system *"does not properly speaking have beliefs."*

- **The reframing:** asking an LLM a question is really asking about likely continuations in a text corpus.
- **The category mistake:** "knowing that the word 'Burundi' is likely to succeed" the relevant words "is not the same as knowing that Burundi is to the south of Rwanda." Conflating them is "a profound category mistake."
- **Why not truth-apt:** "The model itself has no notion of truth or falsehood, properly speaking, because it lacks the means to exercise these concepts," and "has no access to any external reality against which its words might be measured." Belief requires updating in light of evidence.
- **Wittgenstein:** an LLM "cannot participate fully in the human language game of truth, because it does not inhabit the world we human language-users share."
- **Model vs system:** at the *system* level belief talk is at least coherent; the case strengthens with tool use, retrieval and model editing — but "the language model itself is still just a sequence predictor."
- **Vision-language models:** "the former relationship is mere correlation, while the latter is causal." A VLM might say "dog" because of a kennel. One that generates hypotheses, verifies them against the image and is fine-tuned on the results would make belief talk "perhaps less problematic."
- **Reasoning:** chain-of-thought works "by mimicking well-formed arguments in its training set and / or in the prompt." "We can trust a deductive theorem prover because" its causal structure mirrors the inference; an LLM gives no such faithfulness guarantee.
- **RLHF changes nothing categorical:** "the result is still a model of the distribution of tokens in human language, albeit one that has been slightly skewed."

**Shanahan, McDonell & Reynolds, "Role play with large language models," *Nature* 623(7987):493–498, 8 November 2023**, doi:10.1038/s41586-023-06647-8. The dilemma: folk-psychological vocabulary is readable but "taken too literally, such language promotes anthropomorphism." The proposal: **foreground role-play**, which "allows us to draw on familiar folk psychological terms, without ascribing human characteristics to language models they in fact lack." Applied to apparent deception and apparent self-awareness. ⚠️ The second metaphor (a simulator maintaining a superposition of simulacra) is in the *Nature* body, which was not read directly.

### Piantadosi — meaning without reference

**Piantadosi & Hill, "Meaning without reference in large language models," arXiv:2208.02957.** Reject "claims that LLMs possess no meaning whatsoever"; LLMs "likely capture important aspects of meaning," via **conceptual role** — constituted by relationships *among internal representational states*, not by a direct word-world link.

**The decisive methodological consequence:** meaning **"cannot be read off a model's architecture, training data, or objective function."** It can only be assessed by examining how internal states relate to one another. *This is why the probing literature is the right evidential battleground, and why an a-priori argument from the training objective is, on this view, the wrong kind of argument.*

⚠️ The arXiv abstract names no specific opponent; the "reply to Bender & Koller" framing is a standard reading, not something the abstract states.

**Piantadosi, "Modern language models refute Chomsky's approach to language,"** lingbuzz/007180, published in *From Fieldwork to Linguistic Theory: A Tribute to Dan Everett*, Language Science Press, pp. 353–414. LLMs "implement genuine theories of language" and "discovered grammar" without the methods some linguists held necessary.

### Mitchell & Krakauer — the even-handed survey

**Mitchell & Krakauer, "The debate over understanding in AI's large language models," *PNAS* 120(13):e2215907120, 21 March 2023**, doi:10.1073/pnas.2215907120. (Content read from arXiv:2210.13966 v3; minor risk the final text differs.)

**The survey number:** a 2022 metasurvey of active NLP researchers asked whether "Some generative model trained only on text, given enough data and computational resources, could understand natural language in some non-trivial sense." **Of 480 respondents, 51% agreed and 49% disagreed.**

**Their strongest contribution, and the best steelman of the sceptical side.** Benchmarks named "general language understanding" embed an assumption that they *require* human-like understanding. They don't necessarily. The worked example: the **Argument Reasoning Comprehension Task** — BERT reached near-human performance; one group found the mere presence of words like "not" predicts the answer; **after de-correlating, BERT dropped to chance.** This is **shortcut learning**, and "many other, as yet undetected, subtle shortcuts likely exist." Conclusion: "It is possible that, at the scale of these LLMs… any such assessment will contain complex statistical correlations that enable near-perfect performance without humanlike understanding." Hence psychological tests designed for humans may not be valid proxies for machines.

**Their three framing questions:** is understanding-talk here a category error? Do these systems create something like concept-based mental models? Or — if not — can "unimaginably large systems of statistical correlations produce abilities that are functionally equivalent to human understanding," and at that point "will it still make sense to call such correlations 'spurious' or the resulting solutions 'shortcuts'"? Would it be "not 'competence without comprehension' but a new, nonhuman form of understanding"?

They lean to the third as a live possibility, invoking AlphaZero and AlphaFold as bringing "an 'alien' form of intuition," and quote Sejnowski: "A threshold was reached, as if a space alien suddenly appeared that could communicate with us in an eerily human way."

### Mahowald et al. — formal vs functional competence

**Mahowald, Ivanova, Blank, Kanwisher, Tenenbaum & Fedorenko, "Dissociating language and thought in large language models," *Trends in Cognitive Sciences* 28(6):517–540, 2024**, doi:10.1016/j.tics.2024.01.011; arXiv:2301.06627.

- **Formal linguistic competence** — knowledge of linguistic rules and patterns. LLMs are **"surprisingly good."**
- **Functional linguistic competence** — using language to understand and act in the world. **"Spotty,"** often dependent on "specialized fine-tuning and/or coupling with external modules."

Grounded in human neuroscience: the two rely on **different neural mechanisms** (Fedorenko's language-network work).

**Why it is the most useful frame available:** it dissolves much of the fight. "Stochastic parrot" is close to *false* about formal competence and close to *true-ish* about functional competence, and most benchmark disputes are about which bucket a task falls in. Lu et al. (ACL 2024) build on it and Mitchell & Krakauer adopt it — **it is the shared vocabulary of both camps**, which is rare.

⚠️ **The paper never uses the phrase "stochastic parrot,"** and "Bender" appears once, as a cite to Bender & Koller. Do not claim it engages the metaphor by name.

### The functionalist reply, briefly

If mental states are individuated by causal/functional role, then "it's just statistics" describes the **implementation**, not the **functional organisation** — and implementation-level descriptions never settle functional-level questions ("it's just chemistry" is equally true of brains). **The strongest rebuttal is Block's:** behavioural equivalence is not functional equivalence, so the functionalist owes an account of the *internal* organisation — which is exactly what the probing programme tries to supply, and exactly what the bag-of-heuristics result complicates.

## 5. Positions as of late 2026

**LeCun — autoregressive LLMs as a dead end for superintelligence.** The fetchable primary for the argument is **Browning & LeCun, "AI And The Limits Of Language," *Noema*, 23 August 2022**: language is "a highly specific, and deeply limited, kind of knowledge representation"; "Language is a very low-bandwidth method for transmitting information"; three limits — explaining ≠ doing, "they have the attention span and memory of roughly a paragraph," and mimicry; much knowledge is non-linguistic (iconic forms, know-how, mental simulation, affordances, apprenticeship). Conclusion: "A system trained on language alone will never approximate human intelligence." The mirror analogy: "it is only a centimeter thick."

Verified career facts: joined Facebook 2013 as chief AI scientist; **confirmed on 19 November 2025 he would leave Meta** after ten years; **co-founded Advanced Machine Intelligence Labs (AMI Labs) in December 2025** as Executive Chair (CEO Alex LeBrun), focused on "world models"; **March 2026, AMI announced $1.03 billion at a $3.5 billion pre-money valuation.**

⚠️ **His sharpest formulation — "LLMs basically are a dead end when it comes to superintelligence"** — reaches only via Wikipedia quoting the paywalled *FT*. **Note the qualifier *when it comes to superintelligence*; most summaries drop it.** His position paper "A Path Towards Autonomous Machine Intelligence" could **not** be fetched (OpenReview blocks); do not quote it.

**Hinton.** Verified: left Google May 2023 to speak freely about risks; AI may surpass the human brain's information capacity; **chatbots can share learned knowledge, so one copy's new information reaches all copies** — his core argument for digital over biological intelligence; **2024 Nobel Prize in Physics** with Hopfield, 8 October 2024; **December 2024, 10–20% chance AI causes human extinction within three decades.**

⚠️ **His widely-repeated position that LLMs genuinely understand has no reachable primary source.** Do not attribute an "LLMs do understand" quote to him. The one citable third-party characterisation: Krakauer et al. quote his claim that digital computation "may soon be much more intelligent than us" and present it as influential but unsupported.

**Bengio — the risk-governance pole, not the capability-scepticism pole.** Led the **International AI Safety Report** (first edition 29 January 2025; 2026 edition 3 February 2026), written by **over 100 independent experts**, backed by **over 30 countries**. Key concept: the **"evidence dilemma"** — acting before clear evidence risks wasted mitigation, waiting for proof risks unpreparedness. His own research direction: **Bengio et al., "Superintelligent Agents Pose Catastrophic Risks: Can Scientist AI Offer a Safer Path?", arXiv:2502.15657**, proposing non-agentic "Scientist AI." Launched **LawZero** (~3 June 2025, incubated at Mila). ⚠️ No crisp primary statement from him on whether LLMs *understand* — **he is often slotted into the parrots camp and does not belong there.**

**Sutskever — the most interesting 2025 datapoint.** Dwarkesh Patel interview, **25 November 2025**. The same person who in March 2023 said next-word prediction means "learning a world model" now identifies **generalisation** as the central failure: *"These models somehow just generalize dramatically worse than people,"* a *"very fundamental thing."* His analogy: models "are much more like the first student," who memorised everything. On scaling: *"The data is very clearly finite"*; asked whether 100× compute changes everything, *"I don't think that's true."* Conclusion: *"So it's back to the age of research again, just with big computers."*

**Note the asymmetry:** his concession is about *functional* competence, not about whether internal representations exist.

**Hassabis** — ⚠️ **not verifiable from fetchable sources.** DeepMind's public framing centres on "world models" (Genie 3), but the reachable blog page contains no quotable Hassabis statement on understanding, limitations or timelines. One aggregator also mis-dated his Nobel (Chemistry 2024, not 2023) — a good reason to distrust that tier of source.

**Two recent empirical datapoints worth knowing:**

- **Pro-sceptic, and the best recent one: Yu, Liu, Wu, Chung, Zhang, Li, Yeung & Zhou, "The Stochastic Parrot on LLM's Shoulder," NAACL 2025**, arXiv:2502.08946. PhysiCo presents physical phenomena as abstract **grid-format** inputs to defeat memorised text. GPT-4o, o1 and Gemini 2.0 flash thinking **trail humans by ~40%**; models fail the grid task while fluently describing the same concepts in words; and **the difficulty is intrinsic to the task, not the unfamiliar format** — in-context learning and same-format fine-tuning barely help.
- **Pro-capability: Zimmerman et al., "LLMs are not stochastic parrots: Evidence for meaning-mediated abstraction from conlang-like tasks," arXiv:2609.34187.** Models get only natural-language descriptions of fictional conlangs combining statistically uncommon features that cut *against* training-data patterns — **no example outputs**. They generally behaved as the stated meanings predict. Good design (the "surface statistics point the wrong way" manipulation is the right control), but **preprint, not peer-reviewed**.

Also: **Webb, Holyoak & Lu, "Emergent analogical reasoning in large language models," *Nature Human Behaviour* 7(9):1526–1541, 2023**, with a published counterfactual-tasks follow-up — the existence of a rebuttal-and-counter-rebuttal exchange is itself the pattern of this field. And **Kambhampati, "Can large language models reason and plan?", *Ann. NYAS* 1534(1):15–18, 2024** — the standard planning-specific sceptical cite.

## 6. What would actually resolve it

Krakauer, Krakauer & Mitchell give the most explicit published criterion list:

1. **Breaking of scaling** via internal reorganisation, not smooth extrapolation.
2. **Phase-like transitions in internal structure**, not merely jumps in external benchmarks. (Olsson et al.'s induction-head bump is the existing proof-of-concept that this is measurable.)
3. **Compression the model actually uses** for prediction, with **causal** evidence.
4. **Novel bases and manifolds** supporting interpolation *and* extrapolation.
5. **Generalisation to qualitatively different tasks**, with robustness checks against memorisation and shortcuts.
6. **Demonstrable efficiency** — the "less is more" criterion.
7. **For *intelligence* specifically:** compact, transferable abstractions that can be communicated and modified, plus **instruction-mediated learning** — acquiring new structure from verbal instruction in minutes, as humans do. They state flatly that **"instruction-mediated emergence has yet to be demonstrated in an LLM."**

They concede: "We do not yet have a theory" for predicting which capabilities arise from scale alone.

Converging requirements from the other sources:

- **Mitchell & Krakauer:** new benchmarks built for "exotic, mind-like entities" rather than borrowed from human psychometrics, **shortcut-resistant by construction**. PhysiCo's abstract grids and the conlang paper's anti-surface-statistics design are two concrete attempts.
- **Piantadosi & Hill:** the decisive evidence is about *relations among internal states* — so probing is the right programme, but it must measure conceptual role, not mere decodability.
- **Mahowald et al.:** always report formal and functional competence separately.
- **The three-part probing standard:** decode + causally intervene + control for the probe doing the work.
- **Shanahan:** for *belief* talk, the test is whether the system updates in light of evidence against an external reality it has access to — so tool use, retrieval and verification-against-perception are the architecturally relevant changes, not more scale.
- **Chalmers:** for *consciousness*, the operationalisable question is recurrence, a global workspace and unified agency — engineering targets, not metaphysical ones.

**The hard case nobody has solved:** distinguishing "a unified compositional world model" from "a very large bag of locally-valid heuristics that is behaviourally and causally indistinguishable at the tested resolution." **Lin et al. show the two can look identical under probes *and* interventions on a toy model where the ground truth is fully known.** Until there is a measure that separates them, the probing evidence underdetermines the conclusion both camps want from it — and that, rather than any single paper, is the honest answer to "where does the debate stand."

## Sources and verification

Verbatim quotations here come from locally downloaded PDFs read with `pdftotext`, or from full-text HTML; bibliographic records were checked against the Crossref and arXiv APIs. All fetches 2026-11-11.

**Read in full or near-full:** Wei et al. (TMLR 2022); Schaeffer et al. (plus the NeurIPS award confirmed on the official blog); Li et al. (ICLR 2023); Nanda's LessWrong post and the BlackboxNLP paper record; Lin et al.; Gurnee & Tegmark; Olsson et al. (including the phase-change numbers); Chalmers (all credences); Shanahan's CACM preprint; Mitchell & Krakauer (arXiv v3, including the 51%/49% survey of 480 respondents); Krakauer/Krakauer/Mitchell; Abdou et al.; Lu et al.; Browning & LeCun; Delétang et al. (abstract and numbers); Anthropic's 21 May 2024 post.

**Not verified — do not assert:** LeCun's "A Path Towards Autonomous Machine Intelligence" full text (OpenReview 403); the LeCun "dead end" quote at source (paywalled *FT*); Hinton's position that LLMs understand; Hassabis's position; Patel & Pavlick's method; Templeton et al.'s author list and date; Merrill & Sabharwal's chain-of-thought paper ID and venue; Elhage et al.'s "A Mathematical Framework for Transformer Circuits" (cited throughout the induction-head literature but not fetched); the 2025/2026 citations inside Berti et al.'s survey; Piantadosi & Hill as a reply to Bender & Koller specifically; Shanahan et al.'s superposition-of-simulacra passage; Sutskever's GTC date and transcript provenance. Venue attributions for Delétang et al. and Gurnee & Tegmark (both "ICLR 2024") are conventional and unverified — neither arXiv page lists a venue.

PNAS, OpenReview, ACM DL, *Nature* and the Royal Society are hard-blocked to automated fetching; where that mattered, the preprint was read instead and the substitution is noted.
