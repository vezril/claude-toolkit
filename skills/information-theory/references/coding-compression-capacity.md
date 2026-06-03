# AEP, source coding, channel capacity, rate-distortion

*Elements of Information Theory* (Cover & Thomas), Ch. 3–5, 7, 9, 10. Concepts and the operational meaning of the theorems; proofs in the book.

## AEP & the typical set (Ch. 3)

For i.i.d. `X₁…Xₙ ~ p`, the **Asymptotic Equipartition Property** says `−(1/n) log p(X₁…Xₙ) → H(X)` in probability. Consequence: almost all probability sits on a **typical set** `Aₑ⁽ⁿ⁾` of roughly `2^{nH(X)}` sequences, each with probability ≈ `2^{−nH}`. So out of `|𝒳|ⁿ` possible sequences you only ever really see ~`2^{nH}` of them. **This is the engine of compression**: index the typical set in ≈ `nH` bits and you've described the data near-optimally; atypical sequences are negligibly rare.

## Source coding — the compression limit (Ch. 5)

- **Kraft inequality** — a uniquely-decodable (or prefix) code with codeword lengths `ℓᵢ` exists iff `Σ 2^{−ℓᵢ} ≤ 1`. This ties lengths to a probability distribution (`ℓᵢ ≈ −log qᵢ`).
- **Source-coding theorem** — the expected length `L` of any uniquely-decodable code satisfies `L ≥ H(X)`, and there's a code with `H(X) ≤ L < H(X) + 1` (the +1 from integer lengths). **Entropy is the hard floor on lossless compression.** Coding with the *wrong* distribution `q` costs an extra `D(p‖q)` bits — the operational meaning of KL.
- **Optimal codes:** **Huffman** coding is optimal among symbol codes (build the tree by repeatedly merging the two least-probable symbols). **Arithmetic coding** encodes a whole sequence to within ~2 bits of `nH`, beating Huffman's per-symbol integer-length penalty and handling adaptive models — the basis of modern entropy coders. Shannon–Fano–Elias is the intermediate idea.
- Real compressors (gzip/DEFLATE = LZ77 + Huffman; lz4) combine **modeling** (find redundancy/repeats) with **entropy coding** (encode near `H`). If data is already near-maximal entropy (encrypted/random), it won't compress — entropy says so.

## Entropy rate (Ch. 4)

For a stochastic process (not i.i.d.), the **entropy rate** `H(𝒳) = lim (1/n) H(X₁…Xₙ)` is the per-symbol information; for a stationary Markov chain it's `H(X₂|X₁)`. This is the right "bits per symbol" target for sources with memory (language, time series) — and why models that capture dependencies compress better.

## Channel capacity — the communication limit (Ch. 7, 9)

- A (discrete memoryless) **channel** is `p(y|x)`. Its **capacity** `C = max_{p(x)} I(X;Y)` — the most information per use you can get through.
- **Channel-coding theorem (Shannon):** for any rate `R < C` there exist codes with error probability → 0 as block length grows; for `R > C`, reliable communication is impossible (converse, via Fano). The astonishing part: **you can communicate essentially error-free over a noisy channel**, up to `C`, by coding over long blocks.
- Examples: **Binary Symmetric Channel** (bit-flip prob `p`) has `C = 1 − H(p)`; **Binary Erasure Channel** (erase prob `α`) has `C = 1 − α`; the **Gaussian channel** (power `P`, noise `N`) has `C = ½ log(1 + P/N)` — the famous Shannon–Hartley `½ log(1+SNR)`.
- Real **error-correcting / erasure codes** (Hamming, Reed–Solomon, LDPC, turbo, fountain) are constructions approaching `C`; they're what make checksums, RAID/erasure-coded storage, and reliable links work.

## Rate-distortion — lossy compression (Ch. 10)

When you don't need exact reconstruction, the **rate-distortion function** `R(D) = min I(X;X̂)` over reconstructions within average distortion `≤ D` gives the **minimum bits per symbol** to reconstruct within tolerance `D`. It's the theoretical basis for lossy codecs (audio/image/video), quantization, and any "good enough" compression. As `D → 0`, `R(D) → H(X)` (lossless); larger allowed distortion → fewer bits. The dual, channel-capacity-with-cost and rate-distortion, are mirror images.

## The one-line summary

Entropy = the limit of lossless compression; capacity = the limit of reliable communication; rate-distortion = the limit of lossy compression; KL = the cost of using the wrong model; the AEP and Fano's inequality are the tools that make the achievability and converse halves of each theorem work.
