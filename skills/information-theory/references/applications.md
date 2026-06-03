# Applications of information theory

How the core results show up in the toolkit's domains. *Elements of Information Theory* Ch. 11 (statistics), 12 (max entropy), 14 (Kolmogorov complexity), plus standard application links.

## Cryptography ([[cryptography]])

Shannon's *Communication Theory of Secrecy Systems* applied these exact tools:
- **Entropy = strength of randomness/keys.** Key/password strength is measured in bits of entropy; a CSPRNG/Fortuna's job is to produce output indistinguishable from `H = full` (uniform). Low-entropy keys/nonces are the weak link.
- **Perfect secrecy** — a cipher is perfectly secret iff the ciphertext is independent of the plaintext, `I(M;C) = 0`. Shannon proved this requires `H(K) ≥ H(M)` — the theoretical justification for the **one-time pad** (key at least as long as the message, used once).
- **Unicity distance** — `≈ H(K)/D` (where `D` is the per-character redundancy of the language) estimates how much ciphertext is needed before the key is, in principle, uniquely determined. High redundancy → short unicity distance; compression before encryption increases it.
- **Confusion & diffusion** (Shannon's design principles) are about destroying statistical structure (driving the ciphertext toward maximal entropy).

## Compression & serialization ([[akka-serialization]])

The **source-coding theorem** is the *why* behind gzip/lz4: entropy is the floor, and you can't beat it losslessly. Practical takeaways: already-encrypted/random data won't compress (it's near-max entropy); choosing what to compress and the `compress-larger-than` threshold is an entropy/overhead trade-off; modeling (finding redundancy) + entropy coding (Huffman/arithmetic) is the universal recipe.

## Reliable systems & coding theory ([[akka-projections]], reliable delivery)

**Channel capacity** and **error-correcting/erasure codes** are the theory under checksums (CRC), replication, erasure-coded storage (Reed–Solomon), and reliable delivery over lossy links — you can drive error rates to ~0 below capacity by adding redundancy. Useful intuition when reasoning about replication factor, redundancy vs throughput, and why retransmission/coding schemes work.

## Machine learning & AI ([[akka-sdk-agents]], LLM evaluation)

The most forward-looking application — modern ML is information theory in disguise:
- **Cross-entropy loss** = `H(p, q)`: training a classifier/LM to minimize cross-entropy minimizes `D(p‖q)` to the true distribution. The default loss for classification and language modeling.
- **KL divergence** — the regularizer/objective in variational inference, VAEs, and RLHF/policy-optimization (KL-to-reference penalties keep a fine-tuned model near the base model).
- **Perplexity** = `2^{cross-entropy}` (or `e^{…}`) — the standard language-model quality metric (lower = better predictions); directly an entropy measure. Relevant to evaluating LLM outputs (cf. the `akka-sdk-agents` evaluators).
- **Mutual information** — feature selection, representation learning, and the **information-bottleneck** view of deep nets (compress input while keeping info about the label).
- **Maximum-entropy models** — logistic regression / softmax *are* the max-entropy distributions under moment constraints; MaxEnt is the principled "least-biased" modeling choice.

## Statistics & model selection (Ch. 11–12, 14)

- **Hypothesis testing** — the error exponents of optimal tests are KL divergences (Stein's lemma, Chernoff information); `D(p‖q)` quantifies how distinguishable two distributions are.
- **Maximum-entropy principle** — given constraints (known mean/variance/etc.), pick the highest-entropy distribution; it's the most honest about what you *don't* know (yields Gaussian, exponential, uniform, etc.).
- **Kolmogorov complexity & MDL** — the information in an *object* is the length of its shortest program (uncomputable, but foundational). The practical shadow is **Minimum Description Length**: pick the model that most compresses the data (`description of model + data given model`), a rigorous Occam's-razor criterion for model selection — and a clean way to think about overfitting.

## Hashing & data structures

Entropy and the **birthday bound** (see [[cryptography]]) govern hash-collision probability, deduplication effectiveness, and sizing of probabilistic structures (Bloom filters, HyperLogLog — itself an entropy/cardinality-estimation trick).

## Practical lens for this stack

You'll rarely write information-theory code in application logic, but the concepts sharpen decisions: estimating key/randomness quality, predicting whether data compresses, choosing redundancy for reliability, picking/reading ML losses and perplexity, and applying MDL when comparing models. When one of those comes up, this is the skill to consult for the *why*.
