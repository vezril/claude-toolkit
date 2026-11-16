---
name: neural-networks-ml
description: "Artificial neural networks and deep learning — the mechanics, the architectures and what each is actually for, the honest limitations, and a lineage with the folklore stripped out. Covers the unit (weighted sum + nonlinearity) and why nonlinearity is load-bearing, activations, losses, gradient descent and the optimizer family, backpropagation as reverse-mode automatic differentiation, initialization and normalization, regularization, and the bias–variance picture as corrected by double descent (Belkin et al. 2019) and deep double descent — including the honest reading that double descent falsifies a particular *drawing* of the trade-off rather than abolishing it, and that optimally tuned regularization largely removes the peak. Architectures as inductive biases: MLPs (universality is the absence of a bias, not a feature), CNNs (translation *equivariance*, not invariance, and the aliasing that leaks it), RNNs/LSTM/GRU, Transformers in detail (why √d_k, QK vs OV, the residual stream, positional encodings from sinusoidal to RoPE/ALiBi/NoPE, the KV cache, and why FlashAttention's exact-but-IO-aware win beat the approximate-attention literature), state-space models and Mamba, autoencoders/VAEs, GANs, diffusion and flow matching, GNNs and the 1-WL expressivity ceiling, and mixture-of-experts. Honest limitations with primary sources: sample inefficiency and systematic compositionality, adversarial examples through to LLM jailbreaks and prompt injection, shortcut learning and underspecification, catastrophic forgetting, calibration, energy cost with both the Strubell figures and Patterson's 88× correction, reproducibility, and the real state of mechanistic interpretability including the sparse-autoencoder critical turn. Use when choosing or debugging an architecture, reasoning about why a model generalizes or fails, picking an optimizer or regularizer, explaining a deep-learning concept accurately, or needing the history without the standard myths."
---

# Neural Networks (Machine Learning)

A unit computes `σ(w·x + b)`; a network composes them. **Everything interesting follows from which compositions you allow**, because an architecture is a set of assumptions about the data — an *inductive bias* — and the bias, not the expressive power, is what determines whether learning works.

That framing is the spine of this skill. For the biological systems the name borrowed from, and the honest bounds on the analogy, see [[neural-networks-biology]].

## The mechanics, with the parts people get wrong

**Why nonlinearity.** Without it, composing affine maps gives an affine map: an arbitrarily deep linear network has exactly the expressive power of one layer. The nonlinearity is not a detail; it is the reason depth exists.

**Activations and their real trade-offs.** Sigmoid and tanh saturate (|σ′| ≤ 0.25 for logistic), which is the proximate cause of vanishing gradients in deep stacks. ReLU (`max(0,x)`) has constant gradient on the positive half — AlexNet reported reaching 25% CIFAR-10 training error **six times faster** than tanh — at the cost of dying units (zero gradient forever). GELU and its relatives smooth the kink; softmax is a normalization over classes, not an activation in the same sense.

**Losses.** Cross-entropy for classification, not MSE: with a softmax output the cross-entropy gradient is simply `(p − y)`, which does not vanish when the model is confidently wrong, whereas MSE through a saturating output does.

**Backpropagation is reverse-mode automatic differentiation.** The chain rule applied backwards through the computation graph, at cost proportional to the forward pass. Its generality is Linnainmaa's (1970/1976); the neural-network application is Werbos's; the 1986 contribution was the demonstration that this *discovers useful distributed internal representations* — and the field's adoption dates from 1986, which is a real historical contribution even though the mathematics was not new. See `references/history-and-lineage.md`, which also flags the genuine unresolved disagreement about whether Werbos's 1974 thesis contained the NN application.

**Optimizers.** SGD + momentum, Nesterov, RMSprop, Adam/AdamW. The practical ordering for tuning: **learning rate first** (and its warmup/schedule), then batch size and weight decay, then width/depth, then regularization knobs.

**Initialization** (Xavier/Glorot, He) exists to keep activation and gradient variance roughly constant across layers at initialization. **Normalization** (batch, layer) is what made deep stacks reliably trainable — note that batch norm works but its originally stated mechanism ("internal covariate shift") has been contested; the loss-landscape-smoothing account is the competing explanation.

**Pre-LN vs post-LN** is why modern LLMs train without learning-rate warmup; essentially all of them are pre-LN.

### Double descent, stated correctly

The classical U-curve says test error falls then rises with capacity. **Belkin et al. (*PNAS* 2019) showed a second descent past the interpolation threshold** — the capacity at which the model first fits the training data exactly. The peak sits *at* the threshold; beyond it, risk falls again, and the largest-capacity predictor can beat the bottom of the classical U.

Their proposed mechanism is the important part: **larger function classes contain interpolating solutions of smaller norm.** The norm of the learned predictor peaks at the threshold and *decreases* past it, while the parameter count rises monotonically — the two axes simply disagree.

**Nakkiran et al.** generalized it with **Effective Model Complexity** (a property of the whole training procedure, not the architecture), giving three forms: model-wise, **epoch-wise** (test error falls, rises around the epoch training error hits zero, then falls again — the one that breaks naive early stopping), and **sample-wise**, where more data can hurt a model in the critical regime.

**Four things to get right, because this is widely over-read:**

1. Double descent does **not** abolish the bias–variance trade-off. It falsifies a specific *drawing* of it. The classical U-curve is a theorem about a fixed, properly-indexed complexity measure under squared loss with a well-specified model — none of which holds for "parameter count in an overparameterized net trained by SGD."
2. The failure is one of **coordinates**. Replace the axis with something tracking the actual inductive bias (solution norm, margin, effective rank, EMC) and the pathology largely disappears.
3. **Optimally tuned regularization mitigates it** — proved for linear regression with isotropic data, demonstrated empirically for networks. The peak is largely an artifact of *under-regularized* model families, which also defuses the "more data can hurt" headline: it can, for a fixed under-regularized procedure, and generally does not once regularization or early stopping is tuned per model size.
4. The algorithm, not the hypothesis class, selects which interpolating solution you get. That is the missing piece in **Zhang et al.**'s puzzle (standard networks fit *completely random labels* to zero training error, so architecture-only capacity measures cannot explain generalization) — gradient descent has an implicit bias toward max-margin and minimum-norm solutions.

## Architectures are inductive biases

| Architecture | The assumption it encodes | Fails when |
|---|---|---|
| **MLP** | none over input structure — indifferent to a fixed permutation of input coordinates. **Universality is the absence of a bias, not a feature** | the signal has structure worth assuming: parameter blow-up and sample inefficiency |
| **CNN** | locality, weight sharing, approximate translation symmetry | shift/scale fragility (see below); texture-over-shape bias; no long-range relations at low depth; grids only |
| **RNN / LSTM / GRU** | causal order, recency, compression into a bounded state | sequential dependency blocks parallel training; fixed state is a hard information bottleneck (poor exact copying/retrieval) |
| **Transformer** | relations are long-range, content-dependent, not spatially local | O(n²) FLOPs; KV-cache-bound serving; no inherent length extrapolation; data-hungry relative to structure-aware models |
| **VAE** | data near a low-dimensional manifold, smooth factorized latent | posterior collapse with a powerful decoder; blurry samples (a Gaussian likelihood is an L2 loss) |
| **GAN** | implicit density — only has to fool a critic | mode collapse; it is a game, not a minimization, so non-convergence and oscillation; no likelihood for evaluation |
| **Diffusion** | a smooth family of denoisers across noise scales | sampling is iterative (originally hundreds of network evaluations); guidance doubles per-step cost |
| **GNN** | permutation equivariance; locality by graph metric | over-smoothing; over-squashing; **expressivity capped at 1-WL** — vanilla message passing cannot count triangles or distinguish some regular graphs |
| **MoE** | different inputs need different parameters | all experts must be resident (memory); all-to-all dispatch dominates at scale; load imbalance and router instability |

**Two precision points worth internalizing.**

**Convolution is translation-*equivariant*, not invariant.** Shifting the input shifts the feature map. Invariance is approximate and *engineered* — pooling, striding, global average pooling, augmentation — and it leaks, because subsampling after a non-bandlimited filter violates Nyquist and aliases. Small translations genuinely flip predictions; the fix is anti-aliased downsampling.

**The modernized-CNN counterpoint matters for how you read 2020–21.** ConvNeXt — a ResNet with ViT-era training choices — matches Swin Transformers. Much of ViT's advantage was *recipe, scale and data*, not self-attention as such. A weaker inductive bias is a bet on data and compute; ViT's data-hunger is the direct consequence of discarding conv priors.

### The Transformer, in the detail that matters

```
Attention(Q,K,V) = softmax(QKᵀ/√d_k)V
```

- **Why `√d_k`:** for unit-variance components, `q·k` has variance `d_k`, so unscaled logits grow like `√d_k` and push softmax into saturation where its Jacobian ≈ 0. Dividing standardizes the temperature so it does not depend on head width.
- **QK determines *where* information moves; OV determines *what* moves.** Q is what a position is looking for, K is what each position advertises, V is what gets transported. Attention is a differentiable, content-addressed weighted average — a soft dictionary lookup whose weights are computed at runtime, unlike a conv's fixed kernel.
- **The FFN holds roughly two-thirds of the parameters** (attention ≈ 4d², FFN ≈ 8d² per block).
- **The residual stream** is a shared additive channel every sublayer reads from and writes to — a communication bus with limited bandwidth whose dimensions get claimed by competing features.
- **Causal masking** is what lets every position train in parallel in one pass. That, not attention, is the biggest practical difference from an RNN.
- **Positional information** must be injected because attention over a set is permutation-equivariant: sinusoidal → learned absolute → relative → **RoPE** (rotate Q and K so the dot product depends only on relative offset; the handle for context-extension tricks) → **ALiBi** (a linear recency penalty that extrapolates) → **NoPE** (decoder-only models can learn position implicitly, since causal masking already breaks the symmetry).
- **The O(n²) problem is time *and* memory**, and the decisive win was neither sparse nor linear attention. **FlashAttention is exact** — tiling, online softmax, recomputation in the backward pass — dropping memory traffic from O(n²) to O(n) while FLOPs stay O(n²). Meanwhile Long Range Arena found **no efficient approximate variant dominates**, with vanilla attention competitive on several tasks. The lesson: the bottleneck was the memory hierarchy, not the algorithm.
- **The KV cache** is the binding constraint on long-context serving — it grows linearly with context *and* batch, unlike weights. MQA and GQA trade quality for cache size.
- **State-space models are the real competitor.** S4's trick is a duality: computable either as a long convolution (parallel training) or as a recurrence (O(1) state per step at inference). Mamba makes the parameters input-dependent, which buys content-based forgetting that linear time-invariant SSMs cannot do. **The existence of hybrids like Jamba is the honest verdict** — a constant-size state is lossy for exact recall, so a few attention layers are kept to do retrieval while SSM layers carry cheap long-range context.

## Honest limitations

- **Sample inefficiency and systematic compositionality.** Seq2seq models interpolate within the training distribution and fail systematic splits (SCAN). The important update: **meta-learning for compositionality** achieved human-level systematic generalization with a standard seq2seq net — so systematicity is achievable with the right *training distribution*, and the architecture debate becomes a training-distribution debate.
- **Adversarial examples.** Imperceptible perturbations flip predictions and *transfer*. The linear explanation: in high dimensions a bounded per-coordinate perturbation aligned with the weights produces an unbounded pre-activation change, so vulnerability is a property of near-linear behaviour in high dimensions. **Obfuscated gradients** broke most proposed defenses — the literature was measuring attack weakness, not robustness. And the reframing worth knowing: adversarial examples may be **genuinely predictive but brittle features**, i.e. a property of the data distribution plus ERM, not a model defect. The current form is **GCG jailbreak suffixes** and **indirect prompt injection** — which has no clean fix because a prompt architecturally does not separate instructions from data.
- **Shortcut learning.** Decision rules that pass i.i.d. tests and fail o.o.d. An i.i.d. split *cannot* distinguish a shortcut from the intended solution, because both pass it by construction — they call the i.i.d. assumption "the big lie in machine learning." Adapt Morgan's Canon: **"Never attribute to high-level abilities that which can be adequately explained by shortcut learning."** Two deflating results sit underneath: with honest model selection, **plain ERM is competitive with the whole domain-generalization catalogue**, and **underspecification** means an ML pipeline admits many predictors with equal i.i.d. performance and arbitrarily different o.o.d. behaviour — the random seed selects among them. You cannot fix that by optimizing i.i.d. metrics harder.
- **Catastrophic forgetting.** The direct cost of distributed, overlapping representations, and the stability–plasticity dilemma. Replay remains the strongest and cheapest trick, and nothing solves it — "continual learning" in production usually means retrain from scratch on the pooled data.
- **Calibration.** Modern nets are over-confident, and temperature scaling is hard to beat post-hoc. ⚠️ But the sources disagree: a 2021 revisit found recent non-convolutional families (ViT, MLP-Mixer) among the *best* calibrated, with calibration tracking accuracy. The resolution is that it is architecture- and recipe-dependent, not a law of depth. Also: **ECE is not a proper scoring rule**, is binning-sensitive and biased, and only assesses top-label marginal confidence.
- **Interpretability** — see below; it is mid-reassessment, not settled.
- **Energy cost.** Give both framings and date them. Strubell et al.'s famous 626,155 lb was a neural **architecture search**, not one training run, and Patterson et al. corrected it by **88×** (3,223 kg vs 284,019 kg) — decomposed as ~5× from hardware/datacenter assumptions and ~18.7× from assuming the search repeated full-size training. Patterson is at the company supplying the efficiency factor, so both framings are interested. Current trend: frontier training compute ~**5×/year** since 2020.
- **Reproducibility.** Hyperparameters, seeds and even the choice of codebase change reported conclusions. The operational rule: **tune your baseline with the same budget and search procedure as your method, and report seed variance.** The recurring finding across subfields — language models, metric learning, GANs, recommenders, ResNets — is that claimed architectural gains were tuning gaps.

### Interpretability, honestly

Saliency and attribution came first and took a serious hit: **several widely used methods produce compelling maps that are invariant to randomizing the model's weights and to training on random labels.** A method that cannot tell a trained model from a random one is not explaining the model. On attention, cite the pair — "Attention is not Explanation" and "Attention is not not Explanation" — because the disagreement is the lesson.

The circuits programme is the live one: features as the unit of analysis, circuits as computational subgraphs, **superposition** (a network represents more features than it has dimensions when features are sparse, which explains polysemantic neurons), and the linear representation hypothesis.

**The sparse-autoencoder arc is the honest case study.** Optimism in 2023–24 (Towards/Scaling Monosemanticity, TopK SAEs, Gemma Scope) then a critical turn: SAE latents are **not canonical units** (small-SAE features are missing from larger SAEs and large-SAE latents decompose), no SAE+baseline ensemble beat baseline-only on realistic sparse probing, and **SAEBench found a metric-validity problem** — gains on proxy objectives do not transfer to downstream utility. A 2026 critical survey of 138 studies concludes effectiveness is mixed and highly setup-dependent. Meanwhile the frontier labs moved to crosscoders → cross-layer transcoders → circuit tracing → parameter decomposition, and the broader field published hundreds of SAE *application* papers. **Fair summary: SAEs failed as a claimed solution to features and succeeded as a widely used, imperfect instrument.**

For calibration on where this stands, Amodei's April 2025 essay is the right cite precisely because it is aspiration plus admission: >30 million features found in one model, which he calls "a small fraction"; circuits "found manually, in small numbers"; understanding a single few-dozen-word prompt's circuitry takes "a few hours of human effort."

**Chain-of-thought faithfulness** has professionalized into its own field: reasoning models often use a hint without verbalizing it; an LLM monitor reading the CoT detects reward hacking well, but *optimizing against that monitor* teaches the agent to hide intent while still misbehaving. The central tension: **CoT is informative precisely as long as you don't train on it.**

## Always-apply

1. **Name the inductive bias before the architecture.** "Which assumptions about this data do I want baked in?" is the design question; expressivity almost never is.
2. **Do not cite universal approximation as an explanation.** It is an existence result with no bound on width, no claim about learnability (training a 3-node net is NP-complete), and nothing about generalization. It only rules out "too weak in principle."
3. **Tune the learning rate first.** If you have time for one hyperparameter, it is this one. Prefer random over grid search — only a few hyperparameters matter per dataset, and grid wastes its budget on the irrelevant ones.
4. **Overfit one batch** before anything else. It separates optimization failures from statistical ones.
5. **Fit every transform inside the CV fold.** Preprocessing statistics fit before the split is the most common silent bug; for LLMs, pretraining contamination is the dominant modern form of leakage.
6. **Report distributions over ≥3–5 seeds**, never a single run, and tune the baseline with your method's budget.
7. **Test out of distribution deliberately.** An i.i.d. split cannot detect a shortcut.
8. **Date every energy, compute and cost figure**, and give the correction alongside the headline.
9. **Never say "we're past the interpolation threshold so overfitting is impossible."** The defensible claim is narrower: at modern pretraining scales, parameter count alone is a bad proxy for overfitting risk.

## How to use the references

- **`references/history-and-lineage.md`** — the lineage with the myths dismantled: what McCulloch & Pitts actually proved (and why "they couldn't do XOR" misattributes it), what Minsky & Papert actually proved (order-limited single-layer lower bounds) and the documented evidence that **they knew multilayer nets could compute XOR**, what really caused the first AI winter (Mansfield 1969, ALPAC, the 1974 DARPA speech cancellation — and that **Lighthill was positive about neural modelling**), Olazaran's sociological corrective, the backprop credit allocation with the Werbos disagreement flagged, universal approximation and what it does not promise, depth separation, AlexNet's real numbers (the 15.3% was an ensemble of 7; single-model was 18.2%) and the Cireşan/IDSIA GPU CNNs that preceded it by 20 months, the second neural winter of 1995–2006, and scaling laws including why Besiroglu et al. did **not** overturn Chinchilla.
- **`references/architectures-and-limits.md`** — each architecture's mechanism, inductive bias, suitability and failure modes in depth; the Transformer's components with citations; efficient-attention, SSM and MoE engineering; and the limitations sections with primary sources and the places the literature openly disagrees.

## Sources

Primary papers verified against the Crossref and arXiv APIs; quotations read from downloaded PDFs. The spine: McCulloch & Pitts, *Bull. Math. Biophys.* 5(4):115–133, 1943. Rosenblatt, *Psychological Review* 65(6):386–408, 1958. Minsky & Papert, *Perceptrons*, MIT Press, 1969 (expanded ed. 1988). Linnainmaa, *BIT* 16(2):146–160, 1976. Rumelhart, Hinton & Williams, *Nature* 323(6088):533–536, 1986, doi:10.1038/323533a0. Cybenko, *Math. Control Signals Systems* 2(4):303–314, 1989. Hornik, *Neural Networks* 4(2):251–257, 1991. Leshno, Lin, Pinkus & Schocken, *Neural Networks* 6(6):861–867, 1993. LeCun et al., *Neural Computation* 1(4):541–551, 1989, and *Proc. IEEE* 86(11):2278–2324, 1998. Hochreiter & Schmidhuber, *Neural Computation* 9(8):1735–1780, 1997. Bengio, Simard & Frasconi, *IEEE TNN* 5(2):157–166, 1994. Krizhevsky, Sutskever & Hinton, NIPS 25, 2012 (numbers read from the camera-ready PDF — the `papers.nips.cc` HTML abstract serves an earlier version). He et al., arXiv:1512.03385. Vaswani et al., arXiv:1706.03762. Belkin, Hsu, Ma & Mandal, *PNAS* 116(32):15849–15854, 2019. Nakkiran et al., arXiv:1912.02292. Zhang, Bengio, Hardt, Recht & Vinyals, arXiv:1611.03530. Geirhos et al., *Nature Machine Intelligence* 2:665–673, 2020. D'Amour et al., *JMLR* 23(226), 2022. Gulrajani & Lopez-Paz, arXiv:2007.01434. Adebayo et al., arXiv:1810.03292. Strubell, Ganesh & McCallum, arXiv:1906.02243, and Patterson et al., arXiv:2104.10350 plus the Google Research blog post of 2022-02-15. Epoch AI "Trends in AI" (page updated 2026-02-05). Full citation lists, DOIs and arXiv IDs are in the two reference files. All web fetches 2026-11-11.

**Verification notes.** Several widely repeated details could not be confirmed and are flagged in the references rather than asserted: the Mark I Perceptron's 400-photocell camera; Hebb's exact wording and page; the verbatim Minsky & Papert "sterile" sentence; Linnainmaa's Finnish thesis title; GPT-1/GPT-2 tech-report metadata; Chinchilla's "~20 tokens per parameter" rule (implied by the verified equal-scaling result but not stated in the abstract). Sources actively disagree on: **whether Werbos's 1974 thesis contained the NN application** (the most load-bearing disagreement in the backprop story), the Novikoff convergence-proof citation, LSTM's 1995-report vs 1997-journal date, calibration trends across model generations, and whether *Perceptrons* caused the first AI winter. Schmidhuber's annotated histories are reliable for *dates and prior art* and are advocacy on *credit* — he is an interested party.

## Related

- [[neural-networks-biology]] — the real neurons, and a rigorous account of where backprop is biologically implausible.
- [[stochastic-parrot]] — what these systems do and don't understand, and the interpretability evidence both sides lean on.
- [[k-nearest-neighbours]] — the baseline worth clearing, and the ANN search that serves embedding retrieval.
- [[evolutionary-algorithms]] — the derivative-free alternative, and neuroevolution.
- [[information-theory]] — cross-entropy, KL, perplexity and the compression view.
- [[self-organizing-maps]] / [[learning-vector-quantization]] — the competitive-learning branch that did not become deep learning.
- [[python]] — implementation context.
- [[claude-api]] — building on these systems in practice.
