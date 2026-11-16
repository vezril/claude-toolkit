# Lineage, with the folklore removed

Every citation below was checked against Crossref or the arXiv API unless flagged. Things that could not be confirmed are marked ⚠️ and are not asserted.

## 1943 — McCulloch & Pitts

Warren S. McCulloch & Walter H. Pitts, "A logical calculus of the ideas immanent in nervous activity," *Bulletin of Mathematical Biophysics* 5(4):115–133, Dec 1943, doi:10.1007/BF02478259.

A binary **threshold logic unit**: binary in, binary out, fixed weights, a Heaviside threshold, excitatory and inhibitory connections, a synaptic delay per step. **No learning whatsoever** — the designer sets the weights. This is the most common misattribution: it is a *computability* result, not a learning model. Learning arrives with Hebb (1949) as hypothesis and Rosenblatt (1958) as algorithm.

What they established: nets without cycles compute exactly the propositional functions; nets *with* cycles realize temporal and recursive predicates; and such a net furnished with an infinite tape is Turing-equivalent.

**⚠️ Myth to kill: "McCulloch–Pitts neurons can't do XOR."** A *single* threshold unit computes only linearly separable functions. A *network* of them trivially does XOR — and the 1943 paper is about networks. The XOR limitation belongs to the single-layer perceptron story.

## 1949 — Hebb

Donald O. Hebb, *The Organization of Behavior*, Wiley, 1949. A **neuropsychological hypothesis**, not an algorithm and not a convergence result. ⚠️ The exact wording and page (commonly cited as p. 62) could not be confirmed. "Cells that fire together wire together" is a later popularization, **not Hebb's words**. Jerzy Konorski made similar observations in 1948.

## 1957–1962 — Rosenblatt

- 1958 journal paper: F. Rosenblatt, "The perceptron: A probabilistic model for information storage and organization in the brain," *Psychological Review* 65(6):386–408, 1958, doi:10.1037/h0042519.
- 1962 book: *Principles of Neurodynamics*, Spartan Books. **Crucially for the backprop story**, it already discusses multi-layer and "back-coupled" perceptrons and introduces the term **"back-propagating error correction"** (pp. 287–298) for a hypothetical multilayer generalization — which Rosenblatt did not know how to implement, since his discrete-output units have zero derivative.
- ⚠️ The 1957 Cornell report (85-460-1) is dated 1957 by some sources and January 1958 by others; the report number is consistent.
- Hardware: simulations ran on an **IBM 704** in 1957; Mark I construction culminated in **1960**; the machine is now at the Smithsonian. ⚠️ The universally repeated 20×20 = 400-photocell camera and motor-driven-potentiometer weights could not be confirmed from a primary source.

**The convergence theorem.** For a dataset with max‖x‖₂ = R linearly separable with margin γ, the perceptron rule makes **at most (R/γ)² mistakes**, for any learning rate and any sampling order. What it does **not** say: nothing if the data is not separable (the rule cycles forever); no guarantee on margin quality or generalization; no wall-clock bound if γ is tiny; nothing about multilayer nets. ⚠️ The Novikoff citation is inconsistent across sources — "On convergence proofs **on** perceptrons," Brooklyn symposium vol. 12, 1962, 615–622, vs "proofs **for** perceptrons," ONR, 1963.

**The 1958 overclaiming, attributed honestly.** The US Office of Naval Research unveiled the perceptron at a press event in **July 1958**; *The New York Times*, 8 July 1958: **"NEW NAVY DEVICE LEARNS BY DOING; Psychologist Shows Embryo of Computer Designed to Read and Grow Wiser."** The claims came from the Navy-organized press conference and were "based on Rosenblatt's statements." Rosenblatt himself called it "the first machine which is capable of having an original idea" and wrote that "we are about to witness the birth of such a machine." **So the hype was jointly Rosenblatt's and the Navy's** — the "journalists got carried away" exculpation is itself a misconception.

## 1960 — Widrow & Hoff, ADALINE / LMS

A single unit whose output is a **continuous** weighted sum, trained by the LMS/delta rule: update ∝ (target − *linear* output) × input. Because the error is computed on the linear output rather than the thresholded one, it works on non-separable data (unlike the perceptron rule) and converges to a least-squares solution. This is exactly SGD on squared error for linear regression. LMS went on to become the most widely deployed adaptive algorithm in engineering (adaptive filtering, noise and echo cancellation). ⚠️ The standard WESCON citation (Part 4, 1960, 96–104) could not be confirmed.

## 1969 — Minsky & Papert, and the historically accurate AI-winter story

*Perceptrons: An Introduction to Computational Geometry*, MIT Press, 1969; expanded edition 1988 which adds a prologue and epilogue and, per Wikipedia's account, **no new scientific results**; 2017 reissue with a Léon Bottou foreword.

### What they actually proved

The formal object is **not** "a one-layer net on raw pixels." It is a linear threshold function over local predicates φᵢ, parameterized by **order** (max retinal points any φᵢ depends on) and **diameter-limited** (each φᵢ sees a bounded region).

- **Parity (Thm 3.1.1):** parity on |R| points has **order |R|** — no bounded-order perceptron computes it. **XOR is the |R| = 2 special case.**
- **Connectedness (§5.5, due to Huffman):** not computable by a diameter-limited perceptron; order grows at least Ω(|Rₙ|^½).
- Plus positive normal form, the group invariance theorem (the key tool for the lower bounds), and topological-invariant results.

**These are order-limited / diameter-limited *single-layer* lower bounds.** They are **not** theorems that multilayer networks cannot compute parity, and **not** theorems that multilayer networks cannot be trained. "They proved neural nets can't do XOR" loses the actual content (an order lower bound) and overstates the scope.

### They knew about multilayer nets

- **Both Minsky and Papert already knew multi-layer perceptrons could produce an XOR function.**
- They named two-layer machines with learned first layers **"Gamba perceptrons,"** conjectured these would need "an enormous number" of masks, and called the multilayer extension **"sterile"** — the word is theirs. ⚠️ The widely reproduced full sentence from §13.2 ("…we consider it to be an important research problem to elucidate (or reject) our intuitive judgment that the extension is sterile") could not be confirmed verbatim. **Note that even the common quote is a research problem posed, not a theorem claimed.**
- **The 1971 Project MAC report is the strongest documented evidence of their actual pessimism**, and it is explicitly a belief about an unknown: on Gamba networks, *"Virtually nothing is known about the computational capabilities of this latter kind of machine"* and *"We believe that it can do little more than can a low order perceptron."*
- The 1988 epilogue asserts "little of significance [has] changed since 1969" and advances the "society of mind" position.
- Rumelhart's rebuttal: their "pessimism about learning in multilayer machines was misplaced."
- Minsky and Papert themselves argued perceptron research waned because of inherent problems, not because of their book.

### What actually did the funding damage

| Date | Event | What it hit |
|---|---|---|
| 1966 | **ALPAC report** — MT "more expensive, less accurate and slower" than humans; ~$20M spent, funding ended | MT, symbolic NLP |
| **1969** | **Mansfield Amendment** — DARPA must fund "mission-oriented direct research, rather than basic undirected research" | *all* open-ended AI |
| 1969 | *Perceptrons* published | perceptron research |
| 1973 | **Lighthill report** | UK symbolic AI, robotics, NLP |
| **1974** | DARPA cancels CMU **Speech Understanding Research**, $3M/year; DARPA felt misled | speech |
| 1973–74 | Broad DARPA cutbacks; by 1974 AI funding "hard to find" | US academic AI |

**Lighthill, precisely.** Sir James Lighthill, "Artificial Intelligence: A General Survey," Science Research Council (UK), 1973 (written 1972). His **ABC** taxonomy: **A** = Advanced Automation (successful only in narrow hand-fed domains); **B** = Bridge/Building robots (**a failure**); **C** = Computer-based CNS research (**viewed favourably**). Central critique: **combinatorial explosion**.

**→ The single most important corrective: Lighthill was *positive* about category C, explicitly noting that artificial neural networks modelled neurobiological data successfully. It was category B he destroyed. The report did not condemn perceptrons.** ⚠️ The commonly stated "BBC televised debate" framing is unconfirmed — the documented venue is the Royal Institution, 9 May 1973.

### Olazaran — the scholarly corrective

Mikel Olazaran, "A Sociological Study of the Official History of the Perceptrons Controversy," *Social Studies of Science* 26(3):611–659, Aug 1996, doi:10.1177/030631296026003005. Companion: *Advances in Computers* 37:335–425, 1993.

His argument: the reading of Minsky & Papert as showing neural-net research had to be abandoned became the **"official history" because symbolic AI was being institutionalized and legitimated** — the interpretation was a product of the field's institutional politics, not a logical consequence of the theorems. He documents **interpretive flexibility** among working researchers and shows the late-1980s connectionist revival produced a rewriting of that official history by both sides. ⚠️ The body is paywalled; these findings are from the abstract. **This is the citation to lean on for "the popular story is a retrospective construction."**

### Connectionist work demonstrably continued through the 1970s

- **Shun-ichi Amari**, "A Theory of Adaptive Pattern Classifiers," *IEEE Trans. Electronic Computers* EC-16(3):**299–307**, 1967, doi:10.1109/PGEC.1967.264666 — the first deep MLP trained by stochastic gradient descent. ⚠️ **Wikipedia's Backpropagation page miscites the pages as 279–307.**
- von der Malsburg, *Kybernetik* 14(2):85–100, 1973.
- **Fukushima**, "Cognitron," *Biological Cybernetics* 20(3–4):121–136, 1975; **"Neocognitron,"** *Biological Cybernetics* 36(4):193–202, 1980, doi:10.1007/BF00344251; Fukushima & Miyake, *Pattern Recognition* 15(6):455–469, 1982 — **where max pooling appears.**
- **Hopfield**, *PNAS* 79(8):2554–2558, 1982.
- Grossberg (ART), Kohonen (associative memory 1972, SOM 1982 — see [[self-organizing-maps]]).

**Structural point:** the Japanese and European lines (Amari, Fukushima, Kohonen) were largely insulated from US/UK funding politics — strong evidence the "winter" was a funding-regime phenomenon in two countries, not a global scientific verdict.

### The disputed Rosenblatt claims

- **"Perceptrons cost Rosenblatt his funding"** — ⚠️ **likely folklore.** No primary evidence of a funding decision traceable to the book was found. Note the timing problem: the book is 1969, the DARPA collapse is 1974, and Rosenblatt died in 1971.
- **His death:** 11 July 1971, on his 43rd birthday, in a boating accident in Chesapeake Bay (drowned while sailing a sloop called *Shearwater*). **Not** suicide, and no source connects it to the book.
- **"Minsky and Rosenblatt had public shouting matches"** — softened by the sources. Documented: Rosenblatt called Minsky "the loyal opposition"; they "publicly debated the perceptron's viability at conferences."

## Backpropagation — the credit allocation

### Chronology

**Optimal-control antecedents** (gradient by backward recursion; the adjoint method). **None concern neural networks.** Kelley, *ARS Journal* 30(10):947–954, 1960. Bryson, Harvard symposium, 1961 (proceedings 1962). Dreyfus, *J. Math. Anal. Appl.* 5(1):30–45, 1962, and *IEEE Trans. Automatic Control* 18(4):383–385, 1973 (the first instance of *using* backprop to minimize a cost by adjusting weights). **Technical caveat:** these used standard stage-to-stage Jacobian calculations and did not address direct cross-stage links or exploit sparsity — they are not the general reverse-mode AD algorithm.

**Linnainmaa — the algorithm.** 1970 Master's thesis, University of Helsinki, in Finnish (⚠️ exact Finnish title unconfirmed); published as "Taylor expansion of the accumulated rounding error," *BIT* 16(2):146–160, 1976, doi:10.1007/BF01931367. Establishes the general **reverse mode of automatic differentiation** for arbitrary discrete, possibly sparse compositional functions — efficient exact gradients at cost proportional to the forward computation. **It does not mention neural networks.**

**Werbos — the NN application.** PhD thesis, Harvard, 1974, *Beyond Regression*. Then "Applications of advances in nonlinear sensitivity analysis," IFIP 1981 proceedings, Springer 1982, 762–770. *The Roots of Backpropagation*, Wiley, 1994.

⚠️ **SOURCES DIRECTLY CONTRADICT EACH OTHER AND THIS SHOULD BE FLAGGED, NOT RESOLVED.** Wikipedia's *Paul Werbos* page says the 1974 thesis "first described the process of training artificial neural networks through backpropagation of errors." Schmidhuber says the opposite: the NN application "was not yet in this thesis, **as is sometimes claimed**," crediting Werbos 1982. Wikipedia's *History of ANNs* splits it: developed 1971–72, published 1974, first applied to NNs 1982. **This is the single most load-bearing disagreement in the backprop story.**

**The 1985–86 rediscoveries.** Parker, TR-47, MIT, 1985. **LeCun**, "Une procédure d'apprentissage pour réseau à seuil asymétrique," *Cognitiva 85*, Paris, 599–604 (pages verified from a primary source — it is reference 3 of the 1986 *Nature* paper). Rumelhart, Hinton & Williams, ICS-8506 tech report, UCSD, 1985; then *Nature* 323(6088):533–536, Oct 1986, doi:10.1038/323533a0; and the PDP chapter 8, 318–362.

### The key primary finding

**Verified from Crossref's reference list for doi:10.1038/323533a0: the 1986 *Nature* paper cites exactly FOUR references** — Rosenblatt's *Principles of Neurodynamics* (1961), Minsky & Papert's *Perceptrons* (1969), LeCun's *Cognitiva 85* paper, and their own PDP chapter.

So Schmidhuber's factual complaint is **correct**: RHW 1986 does not cite Linnainmaa, Werbos, Kelley, Bryson, Dreyfus, Amari or Ivakhnenko & Lapa. But the same list shows RHW **did** cite LeCun (1985), the contemporaneous independent derivation — which undercuts the stronger "they credited nobody" reading. (Fairness caveat: a four-reference list is a *Nature* Letter format constraint.)

### An honest allocation

- **The algorithm as a general procedure (reverse-mode AD):** Linnainmaa 1970/1976, with Kelley/Bryson/Dreyfus as the optimal-control precursors.
- **First application to training neural networks:** Werbos — 1974 or 1982 depending on which source you believe.
- **Independent contemporaneous derivations:** Parker (1985), LeCun (1985), Rumelhart (c. 1982, published 1985/86).
- **What RHW 1986 established that none of the predecessors did:** the empirical demonstration that gradient descent in multilayer nets **discovers useful distributed internal representations**. Schmidhuber's own page concedes exactly this. Plus the naming, the packaging, and — via the PDP volumes — the creation of connectionism as a research community. **The field's adoption dates from 1986, and that is a real historical contribution even if the mathematics was not new.**
- **The laureates' own published framing** (LeCun, Bengio & Hinton, *Nature* 521:436–444, 2015, p. 438): backpropagation is "nothing more than a practical application of the chain rule for derivatives" and **"The idea that this could be done, and that it worked, was discovered independently by several different groups during the 1970s and 1980s."** So "independently rediscovered many times" is the Turing laureates' own position, not a defensive retrofit.
- **Hinton, from Martin Ford's *Architects of Intelligence* (2018):** "David Rumelhart came up with the basic idea of backpropagation, so it's his invention." ⚠️ The frequently cited Hinton remarks acknowledging Linnainmaa/Werbos/Parker specifically could not be retrieved — do not print a Hinton quote you cannot source.

**Handling Schmidhuber:** his *bibliography* is unusually careful and checkable (several of his citations were independently verified and held up). His *attributions and normative claims* are advocacy in a dispute in which he is an interested party — he co-authored LSTM and was Hochreiter's advisor. **Cite him for the existence and dates of prior art; do not cite him for conclusions about who deserves credit.**

## Universal approximation — and what it does not promise

- **Cybenko**, *Math. Control Signals Systems* 2(4):303–314, 1989: finite sums `Σⱼ aⱼσ(wⱼ·x + bⱼ)` with σ continuous sigmoidal are **dense in C(Iₙ)** in the sup norm. Proof via discriminatory functions, Hahn–Banach and Riesz representation — **non-constructive by nature.**
- **Hornik, Stinchcombe & White**, *Neural Networks* 2(5):359–366, 1989: independent, via Stone–Weierstrass.
- **Hornik**, *Neural Networks* 4(2):251–257, 1991 — **the point: universality comes from the multilayer architecture, not the specific activation.** Any continuous, bounded, non-constant activation suffices.
- **Leshno, Lin, Pinkus & Schocken**, *Neural Networks* 6(6):861–867, 1993 — **the sharp "iff":** a single-hidden-layer net with locally bounded, piecewise continuous activation is dense **iff the activation is not a polynomial.** This covers ReLU.
- **Width-bounded versions:** Lu, Pu, Wang, Hu & Wang, NeurIPS 2017, arXiv:1709.02540 — width-(n+4) ReLU nets are universal approximators, with a phase transition at width n. Hanin & Sellke, arXiv:1710.11278 — the minimal width for arbitrary-depth ReLU nets is **exactly d_in + 1**.
- ⚠️ **Kolmogorov's 1957 superposition theorem is often presented as the ancestor and should not be.** Girosi & Poggio (1989), "Representation properties of networks: Kolmogorov's theorem is irrelevant," argued the inner functions are highly non-smooth and depend on the target, so it does not license the MLP architecture.

### What the theorem does NOT promise

1. **Existence, not construction.** No algorithm, no weights.
2. **No useful bound on the number of units.** Density statements are unquantified; required width can be astronomically large. The standard counterweight — Barron, *IEEE Trans. IT* 39(3):930–945, 1993, giving O(1/n)-type rates — is **for a restricted function class** (bounded Barron norm), which is precisely the point: good rates require assumptions the theorem itself does not make.
3. **Nothing about learnability.** Blum & Rivest, "Training a 3-node neural network is NP-complete," *Neural Networks* 5(1):117–127, 1992.
4. **Nothing about generalization.** It is a statement about hypothesis-class expressivity — and expressivity is the one thing that is never the binding constraint in practice.
5. **Hypothesis caveats:** compact domain, continuous (or Lᵖ) target, approximation in a *specified* norm. The approximating network may be arbitrarily ill-conditioned.

**Net effect: UAT does not explain why deep learning works.** It only rules out "the architecture is too weak in principle," and is routinely over-cited as if it were an explanation.

### Depth separation — why depth matters anyway

- **Telgarsky**, COLT 2016, arXiv:1602.04485: for every k there exist networks with Θ(k³) layers, Θ(1) nodes per layer and Θ(1) parameters that cannot be approximated by O(k)-layer networks unless those have **Ω(2^k)** nodes. Holds for semi-algebraic gates, hence standard ReLU nets.
- **Eldan & Shamir**, COLT 2016, arXiv:1512.03965: a simple radial function expressible by a small **3-layer** network cannot be approximated beyond a constant accuracy by any **2-layer** network unless its width is **exponential in d**.
- **Honest limitation:** depth separation is essentially solved only for 2-vs-3 layers and for specific sawtooth constructions. General k vs k+1 remains largely open, and the known constructions are fragile. **So depth provably helps, but not in a way that explains practice either.**

## Neocognitron → LeNet

Fukushima's Neocognitron (1980) alternates **S-cells** (feature extraction, shared local weights) and **C-cells** (spatial tolerance/pooling), giving shift invariance, **trained without backpropagation**. It is the direct architectural ancestor of CNNs, and the 2015 *Nature* review says so in the laureates' own words (p. 439): "ConvNets have their roots in the neocognitron, the architecture of which was somewhat similar, but did not have an end-to-end supervised-learning algorithm such as backpropagation."

- **LeCun, Boser, Denker, Henderson, Howard, Hubbard & Jackel**, "Backpropagation Applied to Handwritten Zip Code Recognition," *Neural Computation* 1(4):541–551, 1989, doi:10.1162/neco.1989.1.4.541. **This, not AlexNet, is the origin of the modern CNN** — the Neocognitron architecture trained end-to-end by backprop on real data.
- **LeCun, Bottou, Bengio & Haffner**, *Proc. IEEE* 86(11):2278–2324, 1998 — LeNet-5, and the paper that popularized MNIST.
- **Real deployment, from the primary text** (*Nature* 521, p. 439): "**By the late 1990s this system was reading over 10% of all the cheques in the United States.**" Use "over 10%" with this citation; the commonly repeated "10–20%" is unconfirmed.

**The second neural winter, 1995–2006** — which the standard narrative usually collapses into the first. From the same review, p. 438: "**In the late 1990s, neural nets and backpropagation were largely forsaken by the machine-learning community and ignored by the computer-vision and speech-recognition communities. It was widely thought that learning useful, multistage, feature extractors with little prior knowledge was infeasible.**" And p. 440: "**Despite these successes, ConvNets were largely forsaken by the mainstream computer-vision and machine-learning communities until the ImageNet competition in 2012.**" Driven by SVMs/kernel methods and the local-minima folk belief.

## Vanishing gradients

- **Hochreiter**, Diploma thesis, TU München, 1991 — the first systematic analysis. The error signal flowing back through t steps is a product of t Jacobian factors, so it shrinks geometrically or blows up. With saturating squashing functions the vanishing case is generic, making gradient-based learning of dependencies more than ~10 steps apart practically impossible.
- **Bengio, Simard & Frasconi**, *IEEE TNN* 5(2):157–166, 1994, doi:10.1109/72.279181 — independent and complementary: a **structural trade-off**, since a recurrent system that robustly *stores* information necessarily has vanishing gradients. Robust memory and gradient-trainability are in tension.

The credit pattern mirrors backprop: Hochreiter's is earlier, in German, unpublished; Bengio et al.'s is the peer-reviewed English statement everyone reads.

## LSTM

- **Hochreiter & Schmidhuber**, *Neural Computation* 9(8):1735–1780, 1997, doi:10.1162/neco.1997.9.8.1735. The **constant error carousel**: a linear self-connected memory cell (weight 1.0) so the gradient neither vanishes nor explodes through it, guarded by multiplicative input and output gates. ⚠️ Wikipedia dates "the LSTM publication" to 1995 — that is the earlier tech report (FKI-207-95).
- **Gers, Schmidhuber & Cummins**, *Neural Computation* 12(10):2451–2471, 2000 — adds the **forget gate**, without which the cell state grows without bound on continual streams. **The 1997 LSTM had no forget gate, so "the LSTM" everyone uses is really the 2000 variant.**
- **GRU naming caveat:** the gated unit appears in Cho et al., arXiv:1406.1078 (EMNLP 2014), whose headline contribution is the **RNN Encoder–Decoder**. ⚠️ **That paper never says "GRU" or "gated recurrent unit"** — the name is standardly attributed to the follow-up comparison (Chung et al., arXiv:1412.3555). Cite 1406.1078 for the architecture and note the acronym is retrospective.

## 2006 — the revival, and why it was superseded

Hinton, Osindero & Teh, *Neural Computation* 18(7):1527–1554, 2006; Hinton & Salakhutdinov, *Science* 313(5786):504–507, 2006.

From the primary text (*Nature* 521, p. 439): interest was revived "by a group of researchers brought together by the **Canadian Institute for Advanced Research (CIFAR)**" using unsupervised pre-training to initialize deep networks, which "worked remarkably well… **especially when the amount of labelled data was very limited**." Then: "The first major application of this pre-training approach was in **speech recognition**, and it was made possible by the advent of fast **graphics processing units**… **By 2012, versions of the deep net from 2009 were being developed by many of the major speech groups and were already being deployed in Android phones.**" And decisively: "**Once deep learning had been rehabilitated, it turned out that the pre-training stage was only needed for small data sets.**"

**Honest framing: DBN pretraining's historical function was sociological and practical** — it broke the "deep nets can't be trained" consensus and produced the first wins — **not mathematical.** It was superseded within ~6 years by better initialization, ReLUs, large labelled datasets and GPUs. And the local-minima rationale it was built on has itself been retired: same review, p. 438, "**poor local minima are rarely a problem with large networks**… the landscape is packed with a combinatorially large number of saddle points."

## 2012 — AlexNet, with the real numbers

Krizhevsky, Sutskever & Hinton, "ImageNet Classification with Deep Convolutional Neural Networks," NIPS 25, 1097–1105.

⚠️ **Source discrepancy:** the `papers.nips.cc` HTML abstract serves an **earlier submitted version** (39.7%/18.9%, "500,000 neurons"). The camera-ready PDF differs. All numbers below are from the PDF.

- **Verbatim:** top-1/top-5 of **37.5%/17.0%** on ILSVRC-2010; **60 million parameters and 650,000 neurons**; five convolutional layers, three fully-connected; "**a winning top-5 test error rate of 15.3%, compared to 26.2% achieved by the second-best entry**" on ILSVRC-2012.
- **The 15.3% was an ensemble of 7 CNNs.** Table 2: SIFT+FVs 26.2% test; **1 CNN 18.2% val**; 5 CNNs 16.4%; 7 CNNs → 15.4% val / **15.3% test**. Single-model top-5 was 18.2% — still far ahead of 26.2%, but state it precisely.
- **Hardware:** "between **five and six days** to train on **two GTX 580 3GB GPUs**." The two-GPU split was a *memory* workaround (3 GB per card), which also cut top-1/top-5 error by 1.7%/1.2%.
- **ReLU:** a four-layer convnet reaches 25% CIFAR-10 training error "**six times faster**" than tanh. Their own framing: "we would not have been able to experiment with such large neural networks for this work if we had used traditional saturating neuron models."
- **Dropout** p=0.5 on the first two FC layers; "roughly doubles the number of iterations required to converge." **Augmentation:** random 224×224 crops + horizontal reflections ("a factor of **2048**") and PCA colour jitter ("reduces the top-1 error rate by over 1%").

### The "AlexNet came from nowhere" correction

- **ImageNet is half the story.** Deng, Dong, Socher, Li, Li & Fei-Fei, CVPR 2009, 248–255, doi:10.1109/CVPR.2009.5206848. Without this dataset the 2012 result is not possible.
- **GPU precursors:** Raina, Madhavan & Ng, ICML 2009, 873–880 — a 100M-parameter DBN on 30 GTX 280s, up to **70× faster**.
- **🔑 Cireşan / IDSIA — the result that most complicates the standard story.** Cireşan, Meier, Gambardella & Schmidhuber, *Neural Computation* 22(12):3207–3220, 2010. Then Cireşan, Meier, Masci, Gambardella & Schmidhuber, arXiv:**1102.0183**, **1 Feb 2011** — a GPU CNN implementation reporting best published results: **NORB 2.53%, CIFAR-10 19.51%, MNIST 0.35%**. **A GPU CNN beating the state of the art 20 months before AlexNet.** Plus "Multi-column Deep Neural Networks," CVPR 2012 — first near-human MNIST, and on a traffic-sign benchmark it "**outperforms humans by a factor of two**." "DanNet" won the IJCNN 2011 traffic-sign and ICDAR 2011 Chinese-handwriting contests.
- **The correct framing:** AlexNet was the inflection point because it won **ImageNet** — the benchmark the computer-vision establishment cared about, at a scale nobody could dismiss as a toy — and because `cuda-convnet` was released and immediately reproducible. It was **not** the first GPU CNN, nor the first superhuman CNN, nor the first CNN to beat hand-engineered features. **Its own paper acknowledges the lineage:** the two-column architecture is "somewhat similar to that of the 'columnar' CNN employed by Cireşan et al., except that our columns are not independent."

## 2014–2015 — depth, normalization, residuals

- **VGG** (Simonyan & Zisserman, arXiv:1409.1556): homogeneous stacks of **3×3** convolutions, depth 16–19. ILSVRC-2014: 1st in localisation, 2nd in classification.
- **GoogLeNet/Inception** (Szegedy et al., arXiv:1409.4842): **22 layers**, parallel multi-scale branches with 1×1 bottlenecks.
- **Batch normalization** (Ioffe & Szegedy, arXiv:1502.03167): same accuracy with **14× fewer training steps**; an ensemble reaches 4.9% top-5 val, "exceed[ing] the accuracy of human raters." ⚠️ **The stated mechanism — internal covariate shift — has since been contested**; the competing account is loss-landscape smoothing. BN works; the explanation is disputed.
- **ResNet** (He, Zhang, Ren & Sun, arXiv:1512.03385). **The problem it solved was not overfitting:** adding layers made *training* error worse, so it was an optimization failure — solvers could not even find the identity mapping. Residual blocks learn `F(x) = H(x) − x` with an identity skip, so "do nothing" is the default. Depth to **152 layers**, "8× deeper than VGG" with lower complexity; ensemble **3.57%** ImageNet test error; 1st in ILSVRC 2015 classification, detection, localization and COCO detection/segmentation.

**The thread:** 1989 LeNet (~5 layers) → 2012 AlexNet (8) → 2014 VGG/GoogLeNet (19/22) → 2015 ResNet (152, 1000+ demonstrated). **Residual/skip connections are the single structural idea that made arbitrary depth trainable, and they are in every Transformer block.**

## The Transformer and its precursors

- **seq2seq** (Sutskever, Vinyals & Le, arXiv:1409.3215): LSTM encoder → fixed vector → LSTM decoder. WMT'14 En→Fr BLEU 34.8 vs a phrase-based baseline at 33.3. Reversing the source word order markedly helped.
- **Attention enters NLP** (Bahdanau, Cho & Bengio, arXiv:1409.0473, ICLR 2015 oral): the diagnosis is that "the use of a fixed-length vector is a bottleneck"; the fix lets the model "automatically (soft-)search for parts of a source sentence that are relevant."
- **Luong, Pham & Manning**, arXiv:1508.04025 (EMNLP 2015): global vs local attention, and the simpler multiplicative/dot-product scoring the Transformer later uses.
- **Intra-sequence attention:** Cheng, Dong & Lapata, arXiv:1601.06733 (⚠️ the abstract never says "self-attention" — the terminology is retrospective); then Lin et al., arXiv:1703.03130, which is explicitly a self-attention mechanism.
- **The Transformer** (Vaswani et al., arXiv:1706.03762, 12 June 2017): "based solely on attention mechanisms, **dispensing with recurrence and convolutions entirely**." WMT 2014 En→De BLEU 28.4, En→Fr 41.8, after **3.5 days on eight GPUs**.

**What it actually changed, precisely.** Attention was already there (2014); self-attention was already there (2016–17). The contribution is **removing the recurrence**, which removes the sequential dependency in the computation graph: every position is computed from every other in **O(1) sequential steps** instead of O(n), so the whole sequence processes in parallel. **That is a systems property, and it is what made scaling to internet-sized corpora economically possible.** Secondary: scaled dot-product, multi-head, positional encodings, and the residual + layer-norm block. The cost: self-attention is **O(n²)**, trading a sequential bottleneck for a quadratic one — which is the whole subsequent long-context literature.

## BERT and GPT

- **BERT** (Devlin, Chang, Lee & Toutanova, arXiv:1810.04805, NAACL 2019): masked language modelling (mask 15%; of those 80% `[MASK]`, 10% random, 10% unchanged) plus next-sentence prediction (later shown unnecessary by RoBERTa). GLUE 80.5% (+7.7), MultiNLI 86.7%, SQuAD v1.1 F1 93.2. Established pretrain-then-finetune and the encoder-only branch.
- ⚠️ **GPT-1 and GPT-2 are OpenAI tech reports, not peer-reviewed**, and their metadata could not be fetched. Cite as tech reports.
- **GPT-3** (Brown, Mann, Ryder et al., 31 authors, arXiv:2005.14165, NeurIPS 2020): 175B parameters, tasks specified purely in text "**without any gradient updates or fine-tuning**." ⚠️ The abstract reports no specific benchmark scores. Significance: in-context learning as a capability of scale, which converted "pretrain + finetune" into "prompt."

## Scaling laws, and the correction

- **The routinely omitted precursor:** Hestness, Narang, Ardalani, Diamos, Jun et al., "Deep Learning Scaling is Predictable, Empirically," arXiv:1712.00409, **Dec 2017**. Power-law generalization-error scaling with training-set size across four domains; architecture improvements **shift the error curve but do not change the power-law exponent**; model size grows **sublinearly** with data. Two years before Kaplan.
- **Kaplan et al.**, arXiv:2001.08361, Jan 2020: loss scales as a power law with model size, dataset size and compute, with trends spanning "more than seven orders of magnitude." **The conclusion later shown wrong, in their own words:** "**Larger models are significantly more sample-efficient**," so compute-optimal training means "training very large models on a relatively modest amount of data and stopping significantly before convergence."
- **Chinchilla** (Hoffmann, Borgeaud, Mensch et al., 24 authors, arXiv:2203.15556, March 2022): over **400 models from 70M to 16B+ parameters on 5B to 500B tokens**. For compute-optimal training, **model size and training tokens should be scaled equally** — "for every doubling of model size the number of training tokens should also be doubled." Therefore "**current large language models are significantly undertrained**." Chinchilla at 70B beats Gopher (280B), GPT-3 (175B), Jurassic-1 and Megatron-Turing NLG (530B) at the same compute, reaching **67.5% MMLU**. ⚠️ The widely quoted "~20 tokens per parameter" and the 1.4T token count are **not in the abstract** — they come from the tables, and the equal-scaling statement implies the constant ratio.
- **⚠️ Besiroglu, Erdil, Barnett & You, arXiv:2404.10102, does NOT overturn Chinchilla.** They replicate Hoffmann et al.'s **third** estimation procedure and find it inconsistent with the authors' own first two methods, failing to fit the extracted data, and reporting implausibly narrow confidence intervals — "intervals this narrow would require over **600,000 experiments**, while they likely only ran fewer than **500**." **But their own rederivation agrees with the other two methods**, i.e. with the equal-scaling result. This is a critique of one fitting procedure and of reported uncertainty, not a refutation of the conclusion.

## Prizes

- **ACM A.M. Turing Award, 2018** (announced 27 March 2019): Bengio, Hinton, LeCun. Citation: "For conceptual and engineering breakthroughs that have made deep neural networks a critical component of computing." Note the common confusion — the award **year is 2018**, the announcement 2019. ⚠️ `acm.org` returned 403; the wording is verified only via two agreeing Wikipedia pages.
- **Nobel Prize in Physics, 2024** (announced 8 October 2024): Hopfield and Hinton, "for foundational discoveries and inventions that enable machine learning with artificial neural networks." ⚠️ `nobelprize.org` returned 403; **re-verify this wording before publishing it.** The award was controversial among physicists.

## Consolidated unverified list

Could not confirm from a primary source: the Widrow & Hoff WESCON part/pages; Linnainmaa's Finnish thesis title; the verbatim Minsky & Papert "sterile" sentence and its page; the Mark I's 400-photocell camera and potentiometer weights; the full 1958 NYT sentence (the headline *is* verified from two sources); Hebb's wording and page; GPT-1/GPT-2 tech-report metadata; Chinchilla's 20-tokens/parameter and 1.4T tokens; ResNet's 1202-layer CIFAR net; GoogLeNet's 6.67% and VGG's top-5 numbers; Novikoff's citation; Olazaran's body text; whether the 1973 Lighthill debate was BBC-broadcast.

Sources actively disagree on: **Werbos 1974 vs 1982**; Rosenblatt's 1957 report date; Bryson 1961 vs 1962; Amari's pages (299–307 per Crossref, which is authoritative, vs 279–307 on Wikipedia's Backpropagation page — **wrong**); LSTM 1995 report vs 1997 journal, and the forget gate 1999 vs 2000; LeCun's 1985 Cognitiva paper vs 1987 thesis; AlexNet's HTML vs PDF abstract numbers; and **whether *Perceptrons* caused the first AI winter** — where the honest treatment is to state the popular claim, then the four independent lines of counter-evidence (the documented funding events all targeted symbolic AI/robotics/speech; Lighthill was positive about neural modelling; connectionist work continued in Japan and Europe; Olazaran's retrospective-construction argument) and attribute the causal claim to no one as established fact.
