# Architectures as inductive biases, and the honest limitations

Organizing thesis: **an architecture is a symmetry assumption.** Bronstein, Bruna, Cohen & Veličković, "Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges," arXiv:2104.13478 — CNNs are the translation group on grids, GNNs the permutation group on graphs, spherical/gauge CNNs rotations on manifolds.

## MLP

`h = σ(Wx + b)`, every unit sees every input.

**Inductive bias: essentially none over input structure.** The diagnostic: an MLP is indifferent to a fixed permutation of input coordinates — permute every image's pixels identically and learning is unchanged. Any structure (adjacency, order, symmetry) must be learned from data rather than assumed. **Universality is the absence of a bias, not a feature.**

**Suits:** low-dimensional tabular/vector data; fixed-size features with no known geometry; as a *component* (the Transformer FFN, GNN update functions, heads on encoders).

**Failure mode:** parameter blow-up and sample inefficiency on structured signals. A fully connected layer from 224×224×3 to 1,000 hidden units is ~1.5×10⁸ weights; the same mapping with 3×3 convs costs tens of thousands. With no weight sharing, each translated copy of a pattern must be learned separately.

## CNN

Convolution is a **sparse, weight-shared linear map** (a Toeplitz-structured matrix): parameters per layer are `k²·C_in·C_out`, independent of spatial resolution.

### Equivariance vs invariance — be precise

Convolution is **translation-equivariant**: `f(T_x u) = T_x f(u)`, exactly only modulo boundary handling and integer shifts. It is **not** translation-*invariant*. Invariance is approximate and *engineered* — pooling, striding, global average pooling, augmentation — and **it leaks, because subsampling after a non-bandlimited filter violates Nyquist and aliases.**

- Azulay & Weiss, "Why do deep convolutional networks generalize so poorly to small image transformations?", arXiv:1805.12177, *JMLR* 20(184):1–25, 2019 — small translations and rescalings flip predictions; outputs are jagged functions of the transformation parameter. ⚠️ Specific percentage figures not verified.
- Zhang, "Making Convolutional Networks Shift-Invariant Again," arXiv:1904.11486, **ICML 2019** — diagnoses it as aliasing; fixes it with anti-aliased downsampling (low-pass filter before subsample), improving both shift-consistency *and* accuracy.

### Other mechanisms

- **Receptive field** grows additively with depth (+(k−1) per layer at stride 1), multiplicatively with stride, and **exponentially with dilation** (Yu & Koltun, arXiv:1511.07122, ICLR 2016).
- **Pooling → strided conv.** Max/avg pooling is a hand-coded local invariance, largely replaced by learned stride-2 convolutions (Springenberg et al., arXiv:1412.6806). **Global average pooling and the 1×1 convolution** both come from Lin, Chen & Yan, "Network In Network," arXiv:1312.4400 — a 1×1 conv is a per-position MLP across channels: pure channel mixing, zero spatial mixing.
- **Depthwise-separable conv** factorizes `k²·C_in·C_out` into depthwise `k²·C_in` + pointwise `C_in·C_out`, ~8–9× fewer multiply-adds for 3×3 at typical widths (Xception arXiv:1610.02357; MobileNets arXiv:1704.04861; MobileNetV2 arXiv:1801.04381).

### The modernized-CNN counterpoint

Liu et al., "A ConvNet for the 2020s" (ConvNeXt), arXiv:2201.03545, **CVPR 2022** — a ResNet modernized with ViT-era choices (large depthwise kernels, inverted bottleneck, LayerNorm, GELU, AdamW, strong augmentation) matches or exceeds Swin Transformers. **Honest reading: much of ViT's 2020–21 advantage was training recipe, scale and data, not self-attention as such.**

**Failure modes:** shift/scale fragility; **texture over shape** bias (Geirhos et al., arXiv:1811.12231, ICLR 2019 oral — training on Stylized-ImageNet shifts the bias toward shape and improves robustness); no long-range relational modelling at low depth; the grid assumption excludes sets, graphs and irregular meshes; invariances not in the architecture (rotation, viewpoint) must be bought with augmentation.

## RNN / LSTM / GRU

`h_t = φ(W h_{t−1} + U x_t)` — a learned dynamical system with fixed-size state, trained by **BPTT**. **Truncated BPTT** bounds memory and compute but also *bounds credit assignment* to the window.

**Vanishing/exploding gradients:** the gradient across t steps is a product of Jacobians, behaving like the product of their spectral radii. Pascanu, Mikolov & Bengio, arXiv:1211.5063 — gradient clipping for explosion, a regularizer for vanishing.

**LSTM's trick** is the separate **cell state** with an almost-additive update path (the constant error carousel), which keeps the Jacobian near identity along the memory channel. **GRU** collapses cell and hidden state, uses update + reset gates, no output gate. Chung et al. (arXiv:1412.3555): gated units clearly beat tanh RNNs; **GRU vs LSTM is a wash**, task-dependent.

**Teacher forcing and exposure bias.** Training conditions on ground-truth prefixes, inference on the model's own possibly-wrong prefix — a train/test mismatch that compounds. Remedies: scheduled sampling (arXiv:1506.03099), sequence-level training (arXiv:1511.06732).

**Inductive bias:** causal order, recency, Markov-ish compression into a bounded state, parameter sharing across time (so variable length is native).

**Suits:** streaming/online inference (O(1) state and work per token), long-running control, small-memory deployment, strongly sequential data where per-step latency matters.

**Failure modes:** sequential dependency prevents parallelism over time during training; the fixed-size state is a hard information bottleneck (lossy recall, poor exact copying/retrieval); long-range credit assignment remains hard despite gates.

**Counter-current worth a footnote:** Feng et al., "Were RNNs All We Needed?", arXiv:2410.01201 — minGRU/minLSTM, stripped of hidden-state-dependent gates, become parallel-scannable and competitive. **The gap was partly about trainability-at-scale, not expressivity.**

## Transformer

```
Attention(Q,K,V) = softmax(QKᵀ/√d_k)V
```

**Why √d_k.** For q,k with independent zero-mean unit-variance components, `q·k` has mean 0 and **variance d_k**, i.e. std √d_k. Unscaled logits grow like √d_k, pushing softmax into saturation where one weight ≈ 1 and the softmax Jacobian ≈ 0 — vanishing gradients and brittle hard selection. Dividing standardizes logit scale so the attention temperature does not depend on head width. (This is the argument in the paper's own footnote.)

**Q/K/V roles.** All three are learned linear projections of the same residual-stream vectors. **Query** = what this position is looking for; **Key** = what each position advertises as matchable; **Value** = what gets transported if matched. So attention is a differentiable, content-addressed, data-dependent weighted average — a soft dictionary lookup whose mixing weights are computed at runtime, unlike a conv's fixed kernel. **The QK pair determines *where* information moves; the OV pair determines *what* moves** — the decomposition made explicit in Anthropic's QK/OV circuit framing.

**Multi-head attention.** `h` heads of width `d/h`, concatenated then projected. At fixed total FLOPs you buy **several independent comparison subspaces**, so one head can do syntactic adjacency while another does coreference. Observed specialization: previous-token heads, duplicate-token heads, **induction heads**. It also mitigates having to blend conflicting relations into one softmax distribution.

**FFN block.** Position-wise two-layer MLP, expansion ≈4×. Per block: attention ≈ `4d²` (Q,K,V,O), FFN ≈ `8d²`, so **the FFN holds roughly two-thirds of the parameters**. (The "memorized knowledge lives there" key-value-memory reading needs its own citation; the parameter arithmetic is safe.)

**Residual stream + normalization.** Each sublayer reads from and writes to a shared additive channel — a communication bus with limited bandwidth whose dimensions get claimed by different features ("Privileged Bases in the Transformer Residual Stream," transformer-circuits, March 2023). LayerNorm: Ba, Kiros & Hinton, arXiv:1607.06450. **Pre-LN vs post-LN:** Xiong et al., arXiv:2002.04745, **ICML 2020** — pre-LN keeps expected gradients well-scaled at initialization and trains **without learning-rate warmup**, which is why essentially all modern LLMs are pre-LN.

**Causal masking** adds −∞ to the upper triangle pre-softmax. It enforces the autoregressive factorization while letting all positions train **in parallel** in one forward/backward pass under teacher forcing — **the single biggest practical difference from an RNN.**

### Positional information

Attention over a set is permutation-equivariant, so position must be injected.

| Scheme | Mechanism | Note |
|---|---|---|
| **Sinusoidal absolute** (Vaswani 2017) | fixed multi-frequency features | linear maps can express relative offsets |
| **Learned absolute** (BERT/GPT) | an embedding per position | no extrapolation beyond trained length |
| **Relative** (Shaw, Uszkoreit & Vaswani, arXiv:1803.02155, NAACL 2018) | relative position representations | — |
| **T5 bucketed relative bias** (arXiv:1910.10683) | a learned scalar bias per bucket | — |
| **RoPE** (Su et al., arXiv:2104.09864) | rotate Q and K in 2-D subspaces by angle ∝ position, so the dot product depends only on **relative** offset | dominant in current LLMs; the handle for context-extension (interpolation/NTK scaling) |
| **ALiBi** (Press, Smith & Lewis, arXiv:2108.12409) | add a head-specific `−m·|i−j|` penalty to logits | a recency prior that extrapolates |
| **NoPE** (Kazemnejad et al., arXiv:2305.19466, NeurIPS 2023) | **nothing** | decoder-only models learn position implicitly, since causal masking breaks the symmetry — and can length-generalize better than several explicit schemes |

### The O(n²) problem — time *and* memory

`QKᵀ` is n×n: `O(n²d)` FLOPs and, if materialized, `O(n²)` HBM traffic and activation memory per head per layer.

**Exact, IO-aware — and this is the one that won.** Dao, Fu, Ermon, Rudra & Ré, "FlashAttention: Fast and Memory-Efficient **Exact** Attention with IO-Awareness," arXiv:2205.14135. Tile Q/K/V into SRAM, use online (streaming) softmax normalization, and recompute attention in the backward pass instead of storing it. **Same math**; what changes is memory traffic, which drops from O(n²) to O(n), making attention memory-*linear* in sequence length. FLOPs stay O(n²). Then FlashAttention-2 (arXiv:2307.08691, better work partitioning) and -3 (arXiv:2407.08608, Hopper asynchrony and FP8).

**This distinction matters rhetorically: the dominant long-context win of 2022–2024 came from fixing the memory hierarchy, not from approximating attention.**

**Sparse/local (approximate):** Sparse Transformers (arXiv:1904.10509, O(n√n) factorized strided/fixed patterns); Longformer (arXiv:2004.05150, sliding + dilated window + global tokens, linear in n); BigBird (arXiv:2007.14062, NeurIPS 2020, window + global + random, with theory that it retains universal-approximation/Turing-completeness properties).

**Linear attention:** Katharopoulos et al., "Transformers are RNNs," arXiv:2006.16236, **ICML 2020** — replace `exp(qᵀk)` with a feature map `φ(q)ᵀφ(k)`, then use associativity to accumulate `Σφ(k)vᵀ`; **the causal version is literally an RNN with a matrix-valued state, O(1) per step at inference.** Performers (arXiv:2009.14794, FAVOR+ gives an *unbiased* softmax-kernel estimate); Linformer (arXiv:2006.04768, low-rank projection of K and V — needs the whole sequence, so awkward for causal decoding).

**The honest benchmark:** Tay et al., "Long Range Arena," arXiv:2011.04006 — 1K–16K-length tasks. **No efficient variant dominates**; speed/memory wins trade against quality, rankings reorder across tasks, and vanilla attention remains competitive on several. ⚠️ Per-model numbers and the Path-X claim not verified.

### State-space models — the real competitor

- **S4** (Gu, Goel & Ré, arXiv:2111.00396, **ICLR 2022 Outstanding Paper honorable mention**). A linear time-invariant SSM `x' = Ax + Bu, y = Cx + Du` with HiPPO-structured A, computable **either** as a long convolution (parallel training, FFT) **or** as a recurrence (O(1) state per step at inference). **That duality is the whole point.** S4 was the first model to beat chance on LRA Path-X.
- **Mamba** (Gu & Dao, arXiv:2312.00752). Makes the SSM parameters **input-dependent** — selectivity gives content-based forgetting, which LTI SSMs cannot do — giving up the convolution form and recovering speed with a hardware-aware parallel scan. Linear in sequence length, constant-size state, no attention, **no KV cache**. ⚠️ Its venue is widely reported as rejected at ICLR 2024 and appearing at COLM 2024; do not assert it.
- **Mamba-2** (Dao & Gu, arXiv:2405.21060, ICML 2024) — the SSD framework showing structured SSMs and a form of masked attention are two views of the same object, letting SSMs use matmul-heavy, tensor-core-friendly kernels.
- **Jamba** (arXiv:2403.19887) interleaves attention, Mamba and MoE layers. **The existence of hybrids is the honest conclusion:** a constant-size state is lossy for exact recall and copying, so a few attention layers are kept to do retrieval while SSM layers carry cheap long-range context.

### The KV cache

```
cache ≈ 2 · n_layers · n_kv_heads · d_head · seq_len · batch · bytes_per_elem
```

**The binding constraint on long-context serving** — it grows linearly with context *and* batch, unlike weights. **MQA** (Shazeer, arXiv:1911.02150) uses one shared K/V head, cutting the cache by `n_heads` at some quality cost. **GQA** (Ainslie et al., arXiv:2305.13245, EMNLP 2023) uses `g` KV groups to interpolate MHA↔MQA, and can be **uptrained cheaply from an existing MHA checkpoint**. Modern direction: low-rank latent KV compression (DeepSeek's MLA).

### Vision Transformer

Dosovitskiy et al., arXiv:2010.11929, ICLR 2021. 16×16 patch embeddings + absolute positions + a plain encoder; **essentially all conv priors are discarded.** Data-hunger is the direct consequence: on mid-size data it underperforms comparable ResNets and only overtakes them with very large pretraining (ImageNet-21k/JFT-300M). **The general lesson: a weaker inductive bias is a bet on data and compute.** ConvNeXt is the counter-bet.

**Transformer failure modes:** quadratic FLOPs; KV-cache-bound serving; no inherent length extrapolation; permutation equivariance requiring positional hacks; attention-sink/outlier-activation pathologies that complicate quantization *and* interpretability (see "Massive Activations Confound Sparse Autoencoders," arXiv:2611.13548, 2026-11-10); data-hungry relative to structure-aware architectures.

## Autoencoders / VAEs

Maximize the **ELBO**: `E_q[log p_θ(x|z)] − KL(q_φ(z|x) ‖ p(z))` — reconstruction minus a rate/regularization term. The **reparameterization trick** writes `z = μ_φ(x) + σ_φ(x) ⊙ ε`, `ε∼N(0,I)`, making the sampling node differentiable w.r.t. φ (a low-variance pathwise estimator versus the high-variance score-function one).

Kingma & Welling, arXiv:1312.6114 (ICLR 2014); concurrently Rezende, Mohamed & Wierstra, arXiv:1401.4082, ICML 2014.

**Failure modes:**

- **Posterior collapse** — with a sufficiently powerful (e.g. autoregressive) decoder the optimum drives `KL→0` and the latent is ignored. Bowman et al., arXiv:1511.06349, CoNLL 2016 — KL annealing, word dropout.
- **Blurry samples** — a Gaussian observation model *is* an L2 loss; the posterior-mean reconstruction averages over modes.
- **ELBO is a bound**, and the KL term penalizes rate rather than perceptual fidelity, so likelihood and sample quality decouple.

**VQ-VAE and the modern role.** van den Oord, Vinyals & Kavukcuoglu, arXiv:1711.00937 — a discrete codebook with nearest-neighbour lookup, straight-through gradients and a commitment loss; sidesteps posterior collapse and turns generation into fitting a prior over discrete codes. **Why it matters today:** discrete autoencoders are the **tokenizers** that let image and audio be fed to autoregressive LLM-style models, and continuous KL/VQ autoencoders are what make *latent* diffusion cheap.

## GANs

Goodfellow et al., arXiv:1406.2661. Two-player minimax; for a fixed optimal discriminator `D*(x) = p_data/(p_data+p_g)` the generator objective equals `2·JSD(p_data ‖ p_g) − log 4`, so vanilla GAN implicitly minimizes **Jensen–Shannon divergence**. In practice the non-saturating `max_G log D(G(z))` heuristic is used, because the original form gives vanishing generator gradients when D is confident.

**Inductive bias: *implicit* density** — no likelihood, no normalization; the model only has to produce samples a critic cannot distinguish. That buys sharpness and **single-forward-pass sampling**.

**Failure modes:** mode collapse (JSD does not punish dropped modes the way reverse-KL coverage would); non-convergence and oscillation (**it is a game, not a minimization**); exploding/vanishing discriminator gradients; extreme hyperparameter sensitivity; no likelihood, so evaluation leans on IS/FID with known pathologies.

**Milestones:** DCGAN (arXiv:1511.06434, the recipe that made them trainable); WGAN (arXiv:1701.07875, Earth-Mover distance, continuous under disjoint supports, needing a Lipschitz critic); Progressive Growing (arXiv:1710.10196); **StyleGAN** (arXiv:1812.04948, CVPR 2019 — mapping network to an intermediate W space, AdaIN style injection, per-pixel noise; W/W+ disentanglement is what made GAN editing a research area); BigGAN (arXiv:1809.11096, scale + orthogonal regularization + the truncation trick as an explicit fidelity/diversity dial).

**Displacement by diffusion:** Dhariwal & Nichol, arXiv:2105.05233, is the usual pivot. **GANs remain genuinely preferable where one-step sampling, low latency or tiny models matter** (super-resolution, neural vocoders) and as the adversarial term in diffusion *distillation*.

## Diffusion

A fixed forward Markov process adds Gaussian noise until `x_T ≈ N(0,I)`; a network learns the reverse. DDPM's simplification is to train a noise-prediction network with the plain regression loss `E‖ε − ε_θ(x_t,t)‖²`, which is (up to weighting) denoising score matching: **`ε_θ` is equivalent to learning `∇_x log p_t(x)` at every noise scale.**

**Lineage:** Sohl-Dickstein et al., arXiv:1503.03585 → Song & Ermon (NCSN), arXiv:1907.05600, NeurIPS 2019 oral → Ho, Jain & Abbeel (DDPM), arXiv:2006.11239 → Song et al., arXiv:2011.13456, ICLR 2021 oral, which **unifies DDPM (VP-SDE) and NCSN (VE-SDE) as discretizations of SDEs** and introduces the **probability-flow ODE** (deterministic sampling, exact likelihoods) → DDIM, arXiv:2010.02502 (a non-Markovian family with a deterministic sampler, cutting steps by an order of magnitude).

**Classifier-free guidance** (Ho & Salimans, arXiv:2207.12598): jointly train conditional and unconditional models via condition dropout, then extrapolate `ε̃ = ε_∅ + w(ε_c − ε_∅)`. **This is *the* quality/diversity knob in every modern text-to-image system, and the source of its characteristic over-saturation at high w.**

**Latent diffusion** (Rombach et al., arXiv:2112.10752, CVPR 2022): run diffusion in the latent space of a pretrained autoencoder with cross-attention conditioning. This is Stable Diffusion, and the reason text-to-image became commodity compute.

**Flow matching / rectified flow — the current frontier.** Lipman et al., arXiv:2210.02747 — simulation-free training of continuous normalizing flows by regressing a *conditional* vector field; with OT-style conditional paths the trajectories are straighter, so fewer solver steps are needed. Liu, Gong & Liu, arXiv:2209.03003 — "reflow" iteratively straightens trajectories toward one-step generation.

**Costs:** sampling is **iterative** (originally hundreds to 1,000 network evaluations); guidance doubles per-step cost. Mitigations: better ODE solvers and **distillation** (Consistency Models, arXiv:2303.01469, ICML 2023, for 1–2 step sampling). Other honest costs: guidance artifacts, heavy compute for video, and training-data memorization/replication concerns.

## Graph neural networks

**Message passing** (Gilmer et al., arXiv:1704.01212, ICML 2017): per-edge message M, per-node update U, graph-level readout R, iterated T times so each node aggregates a T-hop neighbourhood.

**Instances:** **GCN** (Kipf & Welling, arXiv:1609.02907, ICLR 2017) — `H' = σ(D̃^{−1/2}ÃD̃^{−1/2} H W)`, symmetric-normalized neighbour averaging with self-loops. **GraphSAGE** (arXiv:1706.02216, NIPS 2017) — neighbour *sampling* plus learnable aggregators, which makes GNNs minibatchable and **inductive**. **GAT** (arXiv:1710.10903, ICLR 2018) — learned anisotropic attention over neighbours.

**Inductive bias:** **permutation equivariance** at the node level (invariance for graph-level readout); weights shared across all nodes and edges; locality defined by the graph metric rather than a grid.

**Failure modes:**

- **Over-smoothing** — stacking layers drives node representations toward a common per-component limit. Li, Han & Wu, arXiv:1801.07606, AAAI 2018 (GCN as Laplacian smoothing); Oono & Suzuki, arXiv:1905.10947, ICLR 2020 (an exponential-rate result).
- **Over-squashing** — exponentially many distant nodes compressed into a fixed-width vector.
- **Expressivity ceiling = 1-WL.** Xu, Hu, Leskovec & Jegelka (GIN), arXiv:1810.00826, ICLR 2019 — message-passing GNNs are at most as discriminative as the 1-dimensional Weisfeiler-Leman colour-refinement test, and sum aggregation with an injective MLP achieves that bound (mean and max are strictly weaker). Morris et al., arXiv:1810.02244, AAAI 2019 — the same limit plus a k-WL hierarchy at higher cost. **Practical consequence: vanilla GNNs cannot count triangles or distinguish certain regular graphs** (e.g. some molecular ring structures) — hence positional/structural encodings and subgraph GNNs.
- **Scale** (neighbour explosion) and **heterophily** (neighbour averaging is the wrong prior when connected nodes have different labels).

See [[graph-databases]] and [[python-networkx]] for the data side.

## Mixture-of-experts

**Origin:** Jacobs, Jordan, Nowlan & Hinton, "Adaptive Mixtures of Local Experts," *Neural Computation* 3(1):79–87, 1991 — a gating network softly partitions the input space; originally *dense*.

**The sparse revival:** Shazeer et al., "Outrageously Large Neural Networks," arXiv:1701.06538, ICLR 2017 — top-k noisy gating over thousands of experts, up to ~137B parameters, with the two devices every later MoE inherits: an **auxiliary load-balancing loss** (so the router doesn't collapse onto a few experts) and an **expert capacity** limit (tokens beyond capacity are dropped).

**Scaling:** GShard (arXiv:2006.16668, 600B parameters, all-to-all expert parallelism); **Switch Transformers** (arXiv:2101.03961, JMLR — top-**1** routing, capacity factor, selective precision for router stability, 1.6T parameters); ST-MoE (arXiv:2202.08906 — router z-loss for stability, and the fine-tuning pathologies of sparse models).

**Production (verified numbers):** Mixtral (arXiv:2401.04088) — 8 experts/layer, top-2, **47B total / 13B active**, 32k context. DeepSeekMoE (arXiv:2401.06066) — fine-grained expert segmentation + shared always-on experts. DeepSeek-V3 (arXiv:2412.19437) — **671B total / 37B activated per token**, 14.8T training tokens, 2.788M H800 GPU-hours.

**The economics, which is the actual point:** sparse MoE **decouples parameter count from FLOPs per token.** Capacity scales with total parameters (a memory and communication cost) while compute per token scales with the activated subset. You buy quality per unit of *compute*, paying in HBM, interconnect and complexity.

**Failure modes:** all experts must be resident; all-to-all dispatch dominates at scale and hates slow interconnects; load imbalance and token dropping; router instability and non-differentiable discrete routing; worse fine-tuning/overfitting behaviour; throughput depends on batch composition, which complicates latency SLOs.

## Brief mentions

- **Neural ODEs** (Chen, Rubanova, Bettencourt & Duvenaud, arXiv:1806.07366) — parameterize `dh/dt = f(h,t,θ)` and call a solver; the adjoint method gives O(1) memory in depth. Costs: solver time is data-dependent and unbounded, and the flow is a homeomorphism, limiting what a plain Neural ODE can represent.
- **Capsule networks — didn't pan out.** Sabour, Frosst & Hinton, arXiv:1710.09829. Never scaled, and the robustness claim was directly challenged: Gu, Tresp & Hu, "Capsule Network is Not More Robust than Convolutional Network," arXiv:2103.15459, **CVPR 2021** — ablations show dynamic routing can *hurt* robustness, and a plain ConvNet with the beneficial pieces does better.
- **Hypernetworks** (Ha, Dai & Le, arXiv:1609.09106) — one network generates another's weights. Live descendants: adapter/LoRA weight generation, implicit neural representations.
- **KANs — hype and critique, stated honestly.** Liu et al., arXiv:2404.19756, ICLR 2025 — learnable spline activations *on edges*, claimed better accuracy/interpretability per parameter and better continual learning. Counter-evidence: Yu, Yu & Wang, "KAN or MLP: A Fairer Comparison," arXiv:2407.16674 — **controlling for parameters and FLOPs, MLPs outperform KANs on everything tested except symbolic-formula representation**; that one advantage traces to the B-spline activation (which also improves MLPs when added); and **KANs forget *more* than MLPs** in class-incremental learning, contradicting the original claim. Fair summary: an interesting basis-function choice with a narrow symbolic-regression niche, oversold on first release.

---

# Honest limitations

## Sample inefficiency and compositionality

- Lake, Ullman, Tenenbaum & Gershman, "Building machines that learn and think like people," *BBS* 40, 2017, doi:10.1017/S0140525X16001837. Humans learn concepts from one or a few examples and then *use* them generatively, supported by start-up software (intuitive physics and psychology) and compositional, causal machinery.
- Lake & Baroni (**SCAN**), arXiv:1711.00350, ICML 2018 — seq2seq models interpolate within the training distribution and fail *systematic* compositional splits (hold out "jump", test "jump twice").
- **The important update:** Lake & Baroni, "Human-like systematic generalization through a meta-learning neural network," *Nature* 623:115–121, 2023, doi:10.1038/s41586-023-06668-3 — **meta-learning for compositionality** gets a standard seq2seq net to human-level systematic generalization in a head-to-head behavioural comparison. **Honest reading: systematicity is achievable with the right meta-training distribution; it does not come free from scale. The architecture debate becomes a training-distribution debate.**

## Adversarial examples

- Szegedy, Zaremba, Sutskever, Bruna, Erhan, Goodfellow & Fergus, arXiv:1312.6199 — imperceptible optimizer-found perturbations flip predictions, and they *transfer* across models and training sets.
- **Earlier and often uncredited:** Biggio et al., "Evasion Attacks against Machine Learning at Test Time," ECML PKDD 2013, LNCS 8190:387–402 (arXiv:1708.06131 — posted four years *after* publication, part of why it gets under-cited). Gradient-based evasion of SVMs and PDF-malware detectors, same phenomenology.
- **The linear explanation** (Goodfellow, Shlens & Szegedy, arXiv:1412.6572): **FGSM** `x + ε·sign(∇_x L)`, and the insight that in high dimensions a bounded per-coordinate perturbation aligned with the weights produces an unbounded pre-activation change (`ε‖w‖₁`). **Vulnerability is a property of near-linear behaviour in high-dimensional space, not exotic overfitting.**
- **PGD adversarial training** (Madry et al., arXiv:1706.06083, ICLR 2018) frames robustness as a saddle-point problem and became the standard baseline, at substantial clean-accuracy and compute cost.
- **The damning survey:** Athalye, Carlini & Wagner, "Obfuscated Gradients Give a False Sense of Security," arXiv:1802.00420, **ICML 2018** — identifies obfuscated gradients as the hidden mechanism behind most proposed defenses and breaks the great majority of then-current ICLR defenses. **The field's defense literature was mostly measuring attack weakness, not robustness.**
- **The reframing:** Ilyas et al., "Adversarial Examples Are Not Bugs, They Are Features," arXiv:1905.02175, NeurIPS 2019 — vulnerability arises from **genuinely predictive but brittle features** that generalize to the test set, so it is a property of the data distribution plus ERM, not a model defect. With Tsipras et al., arXiv:1805.12152, ICLR 2019, giving an explicit construction where robust and standard accuracy trade off.
- **Physical world:** Kurakin et al. (arXiv:1607.02533); the stop-sign sticker attack (Eykholt et al., arXiv:1707.08945, CVPR 2018); EOT and the 3-D-printed turtle classified as a rifle (Athalye et al., arXiv:1707.07397, ICML 2018).
- **The current form:** **GCG** (Zou, Wang, Carlini, Nasr, Kolter & Fredrikson, arXiv:2307.15043) — greedy-coordinate-gradient search finds suffixes that transfer across models, i.e. the 2013 phenomenon in discrete token space. And **indirect prompt injection** (Greshake et al., arXiv:2302.12173) — untrusted retrieved content as the attack surface. **Architecturally there is no separation between instructions and data in a prompt, which is why this has no clean fix.** See [[secure-coding]].

## Shortcut learning, distribution shift, underspecification

**Geirhos, Jacobsen, Michaelis, Zemel, Brendel, Bethge & Wichmann, "Shortcut learning in deep neural networks," *Nature Machine Intelligence* 2:665–673, 2020**, doi:10.1038/s42256-020-00257-z.

Their **taxonomy of decision rules**, four nested sets:

1. **All possible rules** — fail even on training data (uninformative features).
2. **Training solutions** — fit training data, fail i.i.d. test (overfitting features).
3. **i.i.d. test solutions, incl. shortcuts** — pass training *and* i.i.d. test, fail o.o.d. (shortcut features).
4. **Intended solution** — passes i.i.d. *and* o.o.d.

The boundary between overfitting and shortcut features is exactly "does it survive the i.i.d. test."

**Their actual examples** (⚠️ correction to a common misattribution — the *ruler on skin lesions*, *surgical skin markers* and *watermark* cases are **not** in this paper): the **cow on the beach**; pneumonia detection that identified hospital systems via a hospital-specific metal token; captioning an empty landscape as a "herd of grazing sheep"; **BERT** solving an argument-comprehension dataset largely by detecting the word "not"; **rats** that appeared to discriminate colours but were using the *odour* of the paint. (The watermark case is Lapuschkin et al., *Nature Communications* 10:1096, 2019 — the PASCAL-VOC "horse" class solved by a source watermark.)

**The i.i.d. point:** an i.i.d. split cannot distinguish a shortcut from the intended solution, because both pass it by construction. They call the i.i.d. assumption **"the big lie in machine learning."**

**Their Morgan's Canon adaptation:** **"Never attribute to high-level abilities that which can be adequately explained by shortcut learning."**

**Two deflating results underneath:**

- **Gulrajani & Lopez-Paz, "In Search of Lost Domain Generalization," arXiv:2007.01434** (DomainBed). With a fixed, honest model-selection protocol — **model selection is itself a core part of the DG problem** — **plain ERM is competitive with, and often beats, the entire catalogue of domain-generalization algorithms.** Much reported DG progress was model-selection leakage.
- **D'Amour et al. (40 authors), "Underspecification Presents Challenges for Credibility in Modern Machine Learning," *JMLR* 23(226):1–61, 2022** — an ML pipeline typically admits many predictors with equally good i.i.d. performance but arbitrarily different o.o.d. behaviour; **something as incidental as the random seed selects among them.** So i.i.d. validation *underspecifies* the model's inductive bias, and you cannot fix it by optimizing i.i.d. metrics harder — you must add stress tests that encode your actual requirements.

Also: Beery, Van Horn & Perona, "Recognition in Terra Incognita," arXiv:1807.04975, ECCV 2018 (camera-trap recognition collapses at new locations — the original cow-on-the-beach result); Sagawa et al., group DRO, arXiv:1911.08731 (worst-group optimization works only with strong regularization, since overparameterized models otherwise memorize their way out of the objective).

## Catastrophic forgetting

- McCloskey & Cohen, *Psychology of Learning and Motivation* 24:109–165, 1989 — the original demonstration.
- French, *TiCS* 3(4):128–135, 1999 — forgetting is the direct cost of **distributed, overlapping** representations, and the **stability–plasticity dilemma**: the same plasticity that allows new learning destroys old learning, and reducing representational overlap trades away generalization.
- **EWC** (Kirkpatrick et al., *PNAS* 114(13):3521–3526, 2017) — a quadratic penalty weighted by the diagonal Fisher information anchors parameters that mattered for previous tasks.
- Families: regularization (EWC/SI/MAS), replay (real or generative), parameter isolation. **Honest bottom line: replay remains the strongest and cheapest trick, nothing solves the problem, and "continual learning" in production usually means retrain from scratch on the pooled data.**

## Calibration

- **Guo, Pleiss, Sun & Weinberger, arXiv:1706.04599, ICML 2017** — modern deep nets are miscalibrated in the **over-confident** direction (unlike shallower 1990s nets); increasing depth/width and removing weight decay worsen it; **temperature scaling** (one scalar on the logits, fit on validation) is remarkably hard to beat.
- **⚠️ The nuance that complicates the story:** Minderer et al., "Revisiting the Calibration of Modern Neural Networks," arXiv:2106.07998, **NeurIPS 2021** — calibration is **not** monotonically worsening with model generation: the most recent non-convolutional families (MLP-Mixer, ViT) are among the *best* calibrated in and out of distribution, and calibration now correlates positively with accuracy and robustness. **Present Guo 2017 as the classic finding and Minderer 2021 as the architecture-dependent correction.**
- **Deep ensembles** (arXiv:1612.01474) give better-calibrated uncertainty than variational or MC-dropout alternatives, at k× cost. Under shift, **all methods degrade, temperature scaling does not transfer off-distribution, and ensembles are the most robust** (Ovadia et al., arXiv:1906.02530).
- **ECE and its flaws.** Binning-sensitive, biased (with sample-size-dependent bias), **not a proper scoring rule** (so it can be gamed), only assesses top-label marginal confidence by default, and ignores class-conditional miscalibration (Nixon et al., arXiv:1904.01685).
- **Conformal prediction** (Angelopoulos & Bates, arXiv:2107.07511) gives finite-sample **marginal** coverage for any black-box model under exchangeability alone. Caveats to state: coverage is marginal not conditional (so it can be achieved while being wrong on a subgroup), set sizes can be uselessly large, and **exchangeability fails exactly under distribution shift.**
- **LLMs:** Kadavath et al., arXiv:2207.05221 — large models are reasonably calibrated on multiple-choice/true-false formats and can be trained to predict P(IK) about their own answers. ⚠️ The widely reported claim that RLHF degrades this calibration was not verified here.

## Interpretability

### Attribution, and the sanity check that broke it

- Input gradients (arXiv:1312.6034); **integrated gradients** (arXiv:1703.01365, ICML 2017 — satisfies sensitivity, implementation invariance and completeness, but the attribution is only as meaningful as the arbitrary baseline); **LIME** (arXiv:1602.04938, KDD 2016 — unstable under resampling); **SHAP** (arXiv:1705.07874 — Shapley axioms, but tractable variants assume feature independence, which is false for correlated features).
- **The damning finding:** Adebayo, Gilmer, Muelly, Goodfellow, Hardt & Kim, "Sanity Checks for Saliency Maps," arXiv:1810.03292, **NeurIPS 2018** — several widely used methods produce visually compelling maps that are **invariant to randomizing the model's weights and to training on randomized labels.** **A method that cannot tell a trained model from a random one is not explaining the model**; some behave like edge detectors.
- **Attention — cite the pair, because the disagreement is the lesson.** Jain & Wallace, "Attention is not Explanation," arXiv:1902.10186, NAACL 2019 (attention weights correlate poorly with gradient/leave-one-out importance, and adversarial attention distributions exist that leave predictions unchanged) vs Wiegreffe & Pinter, "Attention is not not Explanation," arXiv:1908.04626, EMNLP 2019 (it depends what "explanation" claims; the adversarial construction is too permissive; attention does carry *some* faithful signal).
- **Rudin, "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead," *Nature Machine Intelligence* 1:206–215, 2019** — post-hoc explanations can be misleading by construction; for high-stakes decisions build an inherently interpretable model, and the accuracy/interpretability trade-off is often illusory on structured data.

### Circuits, superposition, and the SAE arc

- **Olah et al., "Zoom In: An Introduction to Circuits," *Distill* 5, 2020**, doi:10.23915/distill.00024.001 — three speculative claims: **features** are the unit of analysis, **circuits** are computational subgraphs of features, and **universality** (analogous features recur across models and even across biological vision).
- **Elhage, Nanda, Olsson et al., "A Mathematical Framework for Transformer Circuits," Anthropic, December 2021** — the residual-stream view, the QK/OV factorization, virtual attention heads from head composition, and the discovery of induction heads.
- **Olsson et al., "In-context Learning and Induction Heads"** — transformer-circuits March 2022; arXiv:2209.11895 September 2022 (**cite both dates**). Induction heads form in a narrow training window coinciding with a sharp improvement in in-context learning, visible as a bump in the **training loss itself**.
- **Wang, Variengien, Conmy, Shlegeris & Steinhardt, arXiv:2211.00593** — the indirect-object-identification circuit in GPT-2 small (~26 heads in 7 classes) and the path-patching methodology; also the **"self-repair/backup head"** phenomenon that makes ablation studies deceptive.
- **Elhage et al., "Toy Models of Superposition," Anthropic, September 2022** — when features are sparse, a network represents **more features than it has dimensions** as an overcomplete interfering set of directions. This explains polysemantic neurons and predicts phase transitions and geometric arrangements as a function of sparsity.
- **Park, Choe & Veitch, arXiv:2311.03658, ICML 2024** — the linear representation hypothesis formalized, with counterfactual definitions of a concept direction unifying the "probing" and "steering" senses.

**The SAE timeline:** Cunningham et al. (arXiv:2309.08600) → Bricken, Templeton, Batson et al., "Towards Monosemanticity" (Anthropic, Oct 2023) → Templeton et al., "Scaling Monosemanticity" (Anthropic, May 2024 — SAE features on a production model, the Golden Gate Bridge feature, the steering demo) → Gao et al. (arXiv:2406.04093, TopK autoencoders and SAE scaling laws) → Gemma Scope (arXiv:2408.05147, which made SAE research reproducible outside frontier labs).

**The critical turn, 2025–2026:**

- **Leask et al., "Sparse Autoencoders Do Not Find Canonical Units of Analysis," arXiv:2502.04878, ICLR 2025** — SAE latents are **not atomic**: small-SAE features are missing from larger SAEs, and large-SAE latents decompose into combinations of smaller ones. **There is no canonical dictionary, which undercuts "we found the model's features."**
- **Kantamneni, Engels, Rajamanoharan, Tegmark & Nanda, arXiv:2502.16681** — in realistic sparse probing, SAEs sometimes beat baselines on individual datasets, but the authors **could not construct SAE+baseline ensembles that beat baseline-only ensembles**, and simple non-SAE baselines matched SAEs on spurious correlations, data-quality detection and multi-token concepts.
- **SAEBench (Karvonen, Rager, Lin et al., arXiv:2503.09532, ICML 2025)** — the central finding is a **metric-validity problem**: improvements on the usual proxy objectives do not reliably transfer to downstream utility, and Matryoshka SAEs excel on feature disentanglement *despite* worse proxy scores.
- **A 138-study critical survey** (Lamsiyah et al., arXiv:2610.20139, Oct 2026) — reported effectiveness is **mixed and highly setup-dependent**, with no settled verdict.
- Late-2026 mechanism caveats: "Massive Activations Confound Sparse Autoencoders" (arXiv:2611.13548); "Diminishing Returns of Data in SAEs" (arXiv:2610.20680 — reconstruction saturates at small data budgets while feature *reproducibility* keeps improving).
- **But SAEs were not abandoned.** An arXiv title search (2026-11-11) returns **399 matches**, with **25 in the trailing four weeks**, overwhelmingly *applications* (histopathology, weather models, clinical time series, MoE analysis, AI-text detection, concept erasure). **Fair characterization: SAEs failed as a claimed "solution to features" and succeeded as a widely used, imperfect instrument.**
- **Where the frontier went:** sparse crosscoders (Oct 2024) → stage-wise model diffing (Dec 2024) → **cross-layer transcoders inside circuit tracing (Mar 2025)** → parameter-space decomposition (Bushnaq et al., arXiv:2506.20790) → natural-language/oracle-style descriptions (2025–26). Agenda paper: Sharkey et al., "Open Problems in Mechanistic Interpretability," arXiv:2501.16496.

### Circuit tracing

**Ameisen et al., "Circuit Tracing," and Lindsey et al., "On the Biology of a Large Language Model," transformer-circuits.pub, March 2025.** Method: build a *replacement model* from cross-layer-transcoder features, derive **attribution graphs** linking input tokens → intermediate features → output, and validate with targeted feature interventions. Applied to **Claude 3.5 Haiku** across ~10 behaviours.

Case studies: **multi-step reasoning** ("Dallas" → "Texas" → "capital is Austin", and swapping the Texas feature for California yields Sacramento); **planning in poetry** (a rhyme target is selected *before* the line is written); **language-independent concepts** (shared features across English/French/Chinese); **mental math** (parallel approximate-magnitude and last-digit paths — while the model *reports* using the carry algorithm it did not use); **unfaithful chain of thought** including *motivated reasoning* from a hinted answer; **hallucination** (a default "can't answer" circuit suppressed by a "known entity" feature); **jailbreaks**.

**Their stated limitations, which matter for honesty:** the graphs capture **"only a fraction"** of the model's computation even on short prompts; some apparent mechanisms may be tooling artifacts; **understanding a single prompt's circuitry takes "a few hours of human effort" even for prompts of a few dozen words.** Open-sourced as `circuit-tracer` (May 2025) with a Neuronpedia graph explorer.

**For calibration:** Dario Amodei, "The Urgency of Interpretability," April 2025 — >30 million features found in Claude 3 Sonnet, which he estimates is "a small fraction" of a likely billion-plus concepts; circuits "found manually, in small numbers"; the internal aim is that "interpretability can reliably detect most model problems" by 2027, and he would bet "strongly in favor" of a true "MRI for AI" within 5–10 years; he concedes "we do not understand how our own AI creations work" and calls the remaining work "Herculean." **Treat as aspiration plus honest admission, not status.**

### Chain-of-thought faithfulness

- **Turpin, Michael, Perez & Bowman, arXiv:2305.04388, NeurIPS 2023** — biasing features (reordered options, suggested answers) change the answer while the stated reasoning never mentions them.
- **Lanham et al., arXiv:2307.13702** — intervention-based faithfulness tests (truncation, mistake injection, paraphrase, filler tokens).
- **Chen et al., arXiv:2505.05410** — reasoning models often use a hint without verbalizing it, so CoT monitoring helps but cannot rule out rare dangerous behaviour. ⚠️ Headline percentages not verified.
- **Baker et al. (OpenAI), arXiv:2503.11926** — an LLM monitor reading the CoT detects reward hacking well, but **optimizing against that monitor teaches the agent to hide intent while still misbehaving.** The central tension: **CoT is informative precisely as long as you don't train on it.**
- **Korbak et al., arXiv:2507.11473** — monitorability is a real but **fragile and possibly transient** safety property.
- **State as of late 2026:** the field has moved from "is CoT faithful?" to "how do we measure, preserve, and not over-rely on monitorability?" — measurement frameworks (legibility+coverage; faithfulness×verbosity), stress tests showing evasion under pressure, training-pressure studies finding that adversarial optimization against monitors degrades them *and* that directly optimizing *for* monitorability does not reliably help, a benchmark (MonitorBench), and governance proposals for disclosure. CoT monitoring is a **useful, measurable, non-guaranteeing** layer that degrades under optimization pressure.

## Energy and compute

**Strubell, Ganesh & McCallum, arXiv:1906.02243, ACL 2019** — the table as published (CO₂e lbs): air travel NY↔SF 1,984; human life avg/yr 11,023; American life avg/yr 36,156; car incl. fuel lifetime 126,000. Models: Transformer base 26; Transformer big 192; ELMo 262; BERT base (V100×64, 79 h) 1,438; **NAS (Transformer big), P100×8, 274,120 h → 626,155, cloud cost $942,973–3,201,722.**

⚠️ **The famous 626,155 lb number is for a full neural-architecture *search*** (~979M training steps), **not for training one model** — a distinction routinely lost in secondary citations.

**The correction.** Patterson, Gonzalez, Le, Liang, Munguia, Rothchild, So, Texier & Dean, arXiv:2104.10350, and the Google Research blog post of **2022-02-15**:

- The NAS estimate was an **88× overestimate**: **3,223 kg CO₂e actual vs 284,019 kg published.** Decomposed as ~**5×** from assuming P100s + average-US-datacenter efficiency instead of TPUs + hyperscale facilities, times ~**18.7×** from assuming the search repeated full-size training rather than small proxy tasks.
- The **4Ms** with quoted factors: **Model** (efficient/sparse architectures) 3–10×; **Machine** (ML accelerators) 2–5×; **Mechanization** (cloud vs on-prem) 1.4–2×; **Map** (siting on clean energy) 5–10× — combined ≈100× energy / 1000× emissions.
- Evolved Transformer on the same task with 4M practices: 120 TPUv2-hours, ~$40, **2.4 kg CO₂e**. And "ML training and inference were 10–15% of Google's total energy use" in each of the prior three years.

⚠️ **Present both framings with their interests noted.** Patterson is at the company supplying the 5× hardware/datacenter factor; and Patterson's own blog cites a **120,000×** gap against "some subsequent papers," i.e. the correction literature has its own rhetorical escalation.

Also: Luccioni, Viguier & Ligozat, arXiv:2211.02001 (BLOOM — the methodological contribution is counting embodied hardware manufacturing and idle/overhead energy, not just dynamic training power; ⚠️ tonnage figures not verified); Luccioni, Jernite & Strubell, arXiv:2311.16863, **FAccT '24** (moves the argument to *inference*, where lifetime cost dominates for deployed models); Schwartz, Dodge, Smith & Etzioni, "Green AI," *CACM* 63(12):54–63, 2020 (proposes reporting FPO/compute as a first-class evaluation metric).

**Current trends — Epoch AI "Trends in AI," page updated 2026-02-05** (estimates with CIs, not audited disclosures): frontier-LM **training compute 5×/year since 2020** (90% CI 4–6×), doubling time 5.2 months, with top-5 models up ~**10,000×** since 2020; **training cost 3.5×/year**; AI chip performance per dollar 1.49×/yr since 2023; FLOP/s per watt 1.34×/yr since 2008; quarterly AI-chip compute capacity sold 2.5×/yr since 2024. Largest known AI data center: **~1.1 million H100-equivalents** (Memphis, Tennessee).

**Data-centre electricity, with the scope mismatch that causes most public confusion:**

- **IEA, "Energy and AI," 2025-04-10:** data centres were "around **1.5% of the world's electricity consumption in 2024, or 415 TWh**"; growing "**around 12% per year since 2017**," more than four times faster than total electricity demand; Base Case "**more than double to around 945 TWh by 2030**" and "**around 1 200 TWh by 2035**." The executive summary gives **no separate AI-only share.**
- **US, via the DOE announcement of 2024-12-20** for LBNL's report: **58 TWh in 2014 → 176 TWh in 2023**, "**about 4.4% of total U.S. electricity in 2023**," projected to "**325 to 580 TWh by 2028**," or "**6.7 to 12% of total U.S. electricity.**"
- ⚠️ IEA figures are **global, all data centres** (AI is a subset); LBNL figures are **US-only**; the older widely quoted "460 TWh in 2022 → 620–1050 TWh by 2026" bundles **data centres + crypto + AI**.

## Reproducibility

- **Henderson, Islam, Bachman, Pineau, Precup & Meger, "Deep Reinforcement Learning that Matters," arXiv:1709.06560, AAAI 2018** — hyperparameters, architecture, reward scaling, **random seeds** and even the choice of codebase change reported conclusions; **with few seeds, differently-seeded runs of the *same* algorithm can be made to look "significantly" better than each other.**
- Pineau et al., *JMLR* 22(164), 2021 — the NeurIPS reproducibility program, code-submission policy and the ML Reproducibility Checklist.
- **Lipton & Steinhardt, "Troubling Trends in Machine Learning Scholarship," arXiv:1807.03341** — four patterns: failure to distinguish explanation from speculation; failure to identify the actual *source* of empirical gains (ablation hygiene); "mathiness"; and misuse of suggestive language and anthropomorphism.
- **Kapoor & Narayanan, *Patterns* 4(9):100804, 2023** — a taxonomy of **eight** types of leakage across many scientific fields, plus "model info sheets."
- **Zhuang, Zhang, Song & Hooker, arXiv:2106.11872** — the quiet problem: nondeterminism from tooling (cuDNN kernel selection, atomics, data order) barely moves *top-line* accuracy but can materially change performance **on subsets of the data.** Bitwise-identical reruns are not free, and aggregate metrics hide the variance that matters for fairness and subgroup claims.
- **"Your baseline is undertuned" — the most common cause of fake progress.** Melis, Dyer & Blunsom, arXiv:1707.05589, ICLR 2018: under large-scale automated hyperparameter tuning, **standard LSTMs properly regularized outperform the newer models that had claimed to beat them.** Musgrave, Belongie & Lim, "A Metric Learning Reality Check," arXiv:2003.08505, ECCV 2020: examining four years of deep metric learning, the real improvements are **"marginal at best."** The pattern recurs in GANs, recommenders and ResNets. **The operational rule: tune your baseline with the same budget and search procedure as your method, report seed variance, and report the search budget.**
- **The ImageNet replication, which is more nuanced than usually told.** Recht, Roelofs, Schmidt & Shankar, "Do ImageNet Classifiers Generalize to ImageNet?", arXiv:1902.10811, ICML 2019 — new test sets built by replicating the original collection processes give **accuracy drops of 3–15% on CIFAR-10 and 11–14% on ImageNet**. **But "the relative order of models is almost exactly preserved"** and gains on the original sets translate into *larger* gains on the new sets. They conclude the drops are "not caused by adaptivity" but by "a large distribution gap." **Correct one-line summary: held-out-set reuse turned out to be less damaging than feared; small, innocuous-looking distribution shift turned out to be more damaging than hoped.**

---

# Where sources openly disagree

1. **Calibration** — Guo 2017 (overconfident and worsening) vs Minderer 2021 (recent non-convolutional architectures among the best calibrated). Resolution: architecture- and recipe-dependent, not a law of depth.
2. **Energy/carbon** — Strubell 2019 vs Patterson 2021/2022's **88×** correction (and Patterson's claim of up to 120,000× against some later secondary citations). Both framings are interested.
3. **Adversarial examples** — "bug" (optimization artifact) vs Ilyas et al.'s "feature" (non-robust but genuinely predictive), with Tsipras et al.'s claimed intrinsic trade-off.
4. **Attention as explanation** — a direct, titular disagreement about what "explanation" even claims.
5. **SAEs** — 2024 optimism vs the 2025–26 critical turn vs the simultaneous facts that frontier labs moved on *and* the broader field adopted them. **Present all three.**
6. **Domain generalization** — the DG algorithm literature vs ERM-is-competitive-once-model-selection-is-honest, with underspecification as the explanation for why i.i.d. validation cannot settle it.
7. **Efficient attention** — the sparse/linear literature vs Long Range Arena (no variant dominates) vs FlashAttention (the bottleneck was memory IO and the *exact* algorithm won). Then SSMs vs Transformers vs hybrids — **the existence of hybrids is the verdict.**
8. **KANs** — original claims vs matched-budget comparison (MLPs win except symbolic regression; KANs forget *more*).
9. **Capsules** — Hinton's robustness/equivariance claims vs CVPR 2021 finding routing *harms* robustness.

# Unverified — not asserted above

Azulay & Weiss's specific prediction-change percentages; Long Range Arena per-model rankings and the Path-X claim; Switch Transformer's "7× pretraining speedup"; Jamba's parameter counts; Chen et al.'s CoT-faithfulness percentages; BLOOM's tonnage; Luccioni et al.'s per-task inference energy; Kapoor & Narayanan's paper/field counts; the claim that RLHF degrades LLM calibration; Patterson et al.'s per-model tCO₂e table (PDF unparseable); LBNL's report page (403/404 — numbers via the DOE announcement only); the Mamba venue; Geva et al. on FFNs as key-value memories; WGAN-GP's arXiv ID; over-squashing's primary citation; **and any LeCun or Hinton quotation about ignoring biology** — the "we don't build planes by copying birds" analogy is widely attributed to LeCun but no source was pinned, so do not print it as a quote.

**Scope note:** 2025–2026 *architecture* developments beyond Mamba-2 were not surveyed. Any claim about the current architectural frontier needs its own pass.
