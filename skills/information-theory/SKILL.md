---
name: information-theory
description: Information theory — the mathematics of quantifying information, distilled from Cover & Thomas's *Elements of Information Theory*, framed for application. Covers the core quantities (entropy, joint/conditional entropy, relative entropy / KL divergence, mutual information, cross-entropy, differential entropy) and the central results (the AEP and typical sets, Shannon's source-coding theorem and the entropy bound on compression, channel capacity and the channel-coding theorem, rate-distortion for lossy compression, the maximum-entropy principle, Kolmogorov complexity / MDL), with their applications: cryptography (entropy, perfect secrecy, randomness), data compression (Huffman/arithmetic/entropy coding), error-correcting/coding theory in reliable systems, and machine learning (cross-entropy loss, KL divergence, mutual information, perplexity). Use when reasoning about entropy/uncertainty/randomness, compression limits, channel capacity or error correction, KL divergence or mutual information between variables, cross-entropy/perplexity in ML, or the information content of data. Concepts + applications (light on proofs); cross-links cryptography, akka-serialization, akka-projections/reliable delivery, and the akka-sdk-agents/LLM-eval work.
---

# Information Theory

The mathematics of **quantifying information, uncertainty, and the limits of compression and communication**, from Cover & Thomas's *Elements of Information Theory*. This skill keeps the central results faithful but frames them for **application** (light on proofs); reach for it whenever "how much information / uncertainty / redundancy is here?" is the underlying question.

It underpins several other skills: [[cryptography]] (entropy, perfect secrecy, randomness), [[akka-serialization]] (compression limits), [[akka-projections]]/reliable delivery (coding theory), and the [[akka-sdk-agents]] / LLM-evaluation work (cross-entropy, KL, perplexity). Cross-links [[functional-programming]], [[scala]], [[modern-java]].

## The core quantities (the whole field rests on these)

For a random variable `X` with distribution `p`:

- **Entropy** `H(X) = −Σ p(x) log p(x)` — the average uncertainty / information content, in **bits** (log base 2). The minimum average number of bits to describe `X`. Maximized by the uniform distribution, zero for a constant.
- **Joint / conditional entropy** `H(X,Y)`, `H(X|Y)` — uncertainty of a pair, and of `X` once `Y` is known. **Chain rule:** `H(X,Y) = H(X) + H(Y|X)`.
- **Relative entropy / KL divergence** `D(p‖q) = Σ p(x) log(p(x)/q(x))` — the "distance" from a true distribution `p` to a model `q`: the extra bits paid for coding with `q` instead of `p`. Always ≥ 0 (Gibbs' inequality), not symmetric, not a true metric.
- **Mutual information** `I(X;Y) = H(X) − H(X|Y) = D(p(x,y)‖p(x)p(y))` — how much knowing `Y` reduces uncertainty about `X` (shared information). Zero iff independent; symmetric.
- **Cross-entropy** `H(p,q) = H(p) + D(p‖q)` — the bits to code `p` using a model `q`; minimizing it (e.g. ML training) minimizes KL to the truth.
- **Differential entropy** `h(X) = −∫ f(x) log f(x) dx` — the continuous analog (can be negative; behaves differently, e.g. under scaling).

Two inequalities everything leans on: **Jensen's** (convexity, gives `D ≥ 0`) and the **data-processing inequality** (post-processing can't increase information: if `X→Y→Z`, then `I(X;Z) ≤ I(X;Y)`). **Fano's inequality** bounds error probability from below by conditional entropy (you can't guess `X` from `Y` better than `H(X|Y)` allows).

## The central theorems (at a glance)

- **AEP (Asymptotic Equipartition Property)** — for long i.i.d. sequences, almost all probability concentrates on a **typical set** of about `2^{nH(X)}` roughly-equiprobable sequences. This is *why* compression works: you only need ~`nH` bits to name a typical sequence.
- **Source-coding theorem (compression limit)** — the expected codeword length of any uniquely-decodable code is **≥ H(X)**, achievable to within 1 bit. **Huffman** coding is optimal symbol-by-symbol; **arithmetic coding** approaches `H` for streams. *Entropy is the hard floor on lossless compression.*
- **Channel-coding theorem (communication limit)** — every noisy channel has a **capacity** `C = max_{p(x)} I(X;Y)`; you can transmit reliably (error → 0) at any rate below `C`, and not above it. Error-correcting codes approach `C`. The Gaussian channel gives `C = ½ log(1 + SNR)`.
- **Rate-distortion** — for *lossy* compression, `R(D)` is the minimum bits per symbol to reconstruct within an allowed distortion `D` (e.g. perceptual codecs, quantization).
- **Maximum-entropy principle** — given constraints, the least-biased distribution is the one of maximum entropy (yields the Gaussian for fixed variance, the exponential for fixed mean, etc.) — the basis of MaxEnt models.
- **Kolmogorov complexity / MDL** — the information in an *object* is the length of its shortest program (uncomputable, but the intuition grounds Occam's razor and the Minimum Description Length principle for model selection).

## Where it applies (your toolkit)

- **Cryptography** ([[cryptography]]) — Shannon founded crypto with these tools: **entropy** measures key/password strength and randomness quality; **perfect secrecy** (the one-time pad) requires `H(key) ≥ H(message)`; **unicity distance** estimates how much ciphertext uniquely determines a key; entropy estimation is exactly what a CSPRNG/Fortuna must guarantee. This is the strongest tie.
- **Compression & serialization** ([[akka-serialization]]) — the source-coding theorem is *why* gzip/lz4 exist and where their limits lie; entropy tells you whether data is even compressible.
- **Reliable systems / coding theory** ([[akka-projections]], reliable delivery) — channel capacity and error-correcting/erasure codes underpin checksums, replication, and pushing data reliably over lossy links.
- **Machine learning / AI** ([[akka-sdk-agents]], LLM eval) — **cross-entropy loss** and **KL divergence** are the training objectives; **mutual information** drives feature selection and the information-bottleneck view; **perplexity** (`= 2^{cross-entropy}`) measures language-model quality; MaxEnt = softmax/logistic models. The most forward-looking application.
- **Hashing & data structures** — entropy and the birthday bound (see [[cryptography]]) for hash collisions, dedup, Bloom-filter sizing.

## When to reach for this skill

When the underlying question is *how much information/uncertainty/redundancy* there is: estimating randomness or password/key strength, deciding if/how well data compresses, reasoning about channel capacity or error correction, comparing distributions (KL), measuring dependence (mutual information), choosing an ML loss or reading perplexity, or applying MaxEnt/MDL for modeling. It's **foundational background**, not daily application code — invoke it for the *why* behind crypto/compression/coding/ML choices.

## Scala/FP note

The core quantities are pure functions over probability distributions — `entropy`, `klDivergence`, `mutualInformation`, `crossEntropy` are trivially expressed as folds over a `Map[A, Double]` of probabilities (log base 2; guard `p = 0` as `0·log0 = 0`). Handy for instrumentation (e.g. measuring the entropy of a tag/keyspace, or KL between an expected and observed distribution).

## How to use this skill

- **`references/core-quantities.md`** — precise definitions and intuition for entropy, joint/conditional entropy, KL divergence, mutual information, cross-entropy, differential entropy; chain rules; Jensen, log-sum, data-processing, and Fano inequalities; sufficient statistics.
- **`references/coding-compression-capacity.md`** — the AEP & typical sets, source coding (Kraft inequality, Huffman, arithmetic, the `H` bound), entropy rate of a process, channel capacity & the channel-coding theorem (BSC, Gaussian channel), and rate-distortion for lossy compression.
- **`references/applications.md`** — worked connections to cryptography (perfect secrecy, unicity, randomness), compression/serialization, coding theory in reliable systems, ML/AI (cross-entropy, KL, mutual information, perplexity, MaxEnt, info bottleneck), and Kolmogorov complexity / MDL.

## Related

- [[cryptography]] — entropy, perfect secrecy, randomness; Shannon links the two fields.
- [[akka-serialization]] — compression limits (the source-coding theorem in practice).
- [[akka-projections]] — reliable delivery / coding theory at scale.
- [[akka-sdk-agents]] — cross-entropy / KL / perplexity for LLM training and evaluation.
- [[functional-programming]], [[scala]], [[modern-java]] — the quantities as pure functions over distributions.
- Source: *Elements of Information Theory*, 2nd ed., Thomas M. Cover & Joy A. Thomas (Wiley, 2006). Results stated faithfully; framed for application with proofs left to the book. (MacKay's *Information Theory, Inference, and Learning Algorithms* is the complementary ML-leaning treatment.)
