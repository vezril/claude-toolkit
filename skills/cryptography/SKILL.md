---
name: cryptography
description: Applied and engineering cryptography — concepts, algorithms, protocols, and real-world design practice, distilled from Bruce Schneier's *Applied Cryptography* (2nd ed., 1996) and Ferguson, Schneier & Kohno's *Cryptography Engineering* (2010), with C examples drawn from Applied Cryptography's Part V source code. Covers design philosophy and threat modeling (weakest-link, professional paranoia, attack models, security levels), practical use and pitfalls (choosing algorithms, cipher modes ECB/CBC/CTR, key length, key management), block/stream cipher internals (AES, DES, Blowfish, RC5, RC4), one-way hash functions (SHA-2/3, MD5) and MACs (HMAC/CMAC/GMAC), public-key algorithms and their number theory (RSA, Diffie-Hellman, DSA, ElGamal), cryptographic protocols (key exchange, digital signatures, authentication, secret sharing, zero-knowledge proofs), and the engineering layer (secure-channel design, randomness/Fortuna, PKI, key management, storing secrets, side channels). Use whenever the user asks about encryption, decryption, ciphers, hashing, digital signatures, key exchange, key management, PKI, certificates, cipher modes, secure channels, password storage, random number generation for crypto, side-channel/timing attacks, a specific algorithm (AES/DES/RSA/Diffie-Hellman/Blowfish/RC4/SHA/HMAC), how a cryptographic primitive works, how to implement or use one in C, or whether some crypto design is secure — even if they don't say the word "cryptography." Flags what is broken or deprecated and gives current best-practice recommendations.
---

# Cryptography

Concepts, algorithms, protocols, and engineering practice drawn from two books:

- **Ferguson, Schneier & Kohno, *Cryptography Engineering* (2010)** — the **modern authority** for what to actually do: recommendations, threat modeling, secure-channel and key-management design, implementation pitfalls. When the two books disagree (key sizes, mode choices, what's secure), this one wins.
- **Schneier, *Applied Cryptography* 2nd ed. (1996)** — the **historical and structural reference**, and the source of the **C examples** (its Part V source listings). Great for how a primitive is built; out of date on what's safe to ship.

This skill is the working map plus the parts that come up most. Recommendations reflect current best practice, not 1996.

If the user's explicit instructions conflict with this skill, the user wins.

## Design philosophy (the engineering mindset)

*Cryptography Engineering*'s core lesson is that crypto fails at the system level, not the math level. Carry these into every review:

- **Weakest-link property.** A system is only as secure as its weakest part — and unlike a chain, strengthening a strong link buys nothing. Find and fix the weakest link rather than over-engineering an already-strong primitive. Most real breaks are in key management, randomness, implementation, and protocol glue, not the cipher.
- **Cryptography is the easy part.** The algorithms are the most thoroughly studied piece; the surrounding system (key storage, RNG, error handling, side channels, humans) is where things go wrong. Spend attention there.
- **Professional paranoia.** Think like an attacker. For every design, ask what an adversary who controls the network, can submit chosen inputs, and observes timing/error behavior could do. Define an explicit **threat model** (who the attacker is, what they can do, what they're trying to achieve) before reasoning about security.
- **Attack models** to evaluate a cipher/scheme against: *ciphertext-only*, *known-plaintext*, *chosen-plaintext*, *chosen-ciphertext*, and the *distinguishing* goal (can the attacker tell the output from random?). A modern primitive must resist chosen-ciphertext attacks.
- **Security level, not "secure."** Quantify strength in bits (e.g. 128-bit security = ~2¹²⁸ work to break) and design every component to meet the same level — the weakest-link rule again. Beware **generic attacks** that apply regardless of the algorithm: **birthday attacks** (collisions in ~2^(n/2)) and **meet-in-the-middle** attacks, which is why effective strengths are often half the naive size.

## The single most important rule: don't roll your own crypto

The book teaches how primitives work so you can reason about them. It does **not** license you to ship hand-written crypto. Real systems are broken far more often by implementation flaws — timing side channels, weak randomness, nonce reuse, padding oracles, key-management mistakes — than by broken math. Default guidance for any production task:

- **Use a vetted, high-level library**: libsodium / NaCl, or your platform's audited primitives. Reach for an "AEAD" construction (authenticated encryption — e.g. AES-GCM, ChaCha20-Poly1305) rather than a bare cipher.
- **Encrypt-then-MAC, or use AEAD.** Encryption without authentication is almost always a bug; an attacker who can flip ciphertext bits can often break you (padding-oracle, bit-flipping attacks).
- **Get randomness from the OS CSPRNG** (`/dev/urandom`, `getrandom()`, `CryptGenRandom`), never from `rand()`/`random()`/an LCG. The book's Chapter 17 on real random-sequence generators underlines how hard this is.
- Treat the C in this skill as **explanatory** — to understand a cipher's structure — not as code to paste into production.

Say this plainly when a user asks to implement crypto for real use, then help them with the primitive if they still want to learn or have a genuine reason.

## Foundational vocabulary

Plaintext *M*, ciphertext *C*, encryption *E(M)=C*, decryption *D(C)=M*, with *D(E(M))=M*. A **cryptographic key** *K* parameterizes these: *E_K(M)=C*, *D_K(C)=M*. Two families:

- **Symmetric (secret-key)** — same key encrypts and decrypts (or keys are trivially derivable). Fast; the problem is sharing the key securely. Split into **block ciphers** (fixed-size blocks, e.g. 64/128 bits) and **stream ciphers** (keystream XORed with data).
- **Asymmetric (public-key)** — a public key encrypts / verifies, a private key decrypts / signs. Solves key distribution and enables signatures; orders of magnitude slower, so in practice it's used to exchange a symmetric session key (hybrid encryption).

Other core primitives: **one-way hash functions** (fixed-size digest, preimage- and collision-resistant), **MACs / HMAC** (keyed integrity), **digital signatures** (sign with private key, verify with public), and **CSPRNGs** (cryptographically secure randomness). **Kerckhoffs's principle**: security must rest in the key, never in keeping the algorithm secret.

## How to use this skill

The detail lives in three reference files — read the one that matches the question rather than loading everything:

- **`references/algorithms-and-c-code.md`** — symmetric ciphers and how they're built, with the book's C: DES (structure + API), the **Blowfish** Feistel round, a complete small cipher (**RC5**), stream ciphers (RC4, SEAL), one-way hashes (MD4/MD5/SHA), and **cipher modes** (ECB/CBC/CFB/OFB/CTR) with C-style mode loops. Read this for "how does cipher X work", "show me X in C", "which mode should I use".
- **`references/public-key-and-math.md`** — RSA, Diffie-Hellman, ElGamal, DSA, and the number theory behind them (modular arithmetic, primes, discrete logs, factoring). Read this for any public-key, signature-algorithm, or key-exchange-math question.
- **`references/protocols.md`** — protocol-level constructions: key exchange and authentication (incl. man-in-the-middle and replay), digital-signature protocols, secret splitting/sharing, timestamping, bit commitment, zero-knowledge proofs, blind signatures, digital cash. Read this for "how would two parties do X securely".
- **`references/engineering-practice.md`** — the *Cryptography Engineering* operational layer: secure-channel design (message order, encrypt-then-authenticate), the **Fortuna** RNG and entropy management, MAC selection, key management, **PKI** (the dream vs. reality, revocation/CRL/OCSP), **storing secrets** (password salting & stretching, secret sharing, wiping), and implementation / side-channel issues. Read this for "how do I build/operate this safely", randomness, certificates, password storage, or side channels.

Each reference begins with a short table of contents.

## Choosing primitives: the book's logic, updated for today

The book devotes Chapters 7–10 to picking and using algorithms. Carry the *reasoning* forward, but use modern choices:

**Block cipher: AES.** *Cryptography Engineering* recommends **AES** as the default — fast, ubiquitous, the standard; its academic-only attacks don't threaten real systems. Keep **3DES** only for legacy/64-bit-block compatibility (and mind its weak 64-bit block, Sweet32). For belt-and-suspenders against future cryptanalysis, you can double-encrypt with **independent** keys (AES then Serpent or Twofish). (For historical/structural comparison, the 1996 book's Table 7.9 mapped brute-force-equivalent strengths: symmetric↔public-key 56↔384, 80↔768, 128↔2304 — the durable point being that public keys must be far longer than symmetric ones.)

**Key size: use 256-bit symmetric keys.** CE's rule of thumb: *for a security level of n bits, every cryptographic value should be at least 2n bits long* — because birthday and meet-in-the-middle (generic) attacks erode effective strength to half. So for 128-bit security use **256-bit keys**. Public-key: RSA/DH ≥ **2048 bits** (3072+ long-term; build in support up to 8192 so you can grow in the field); or elliptic curve (~256-bit ≈ 128-bit security — X25519/Ed25519), now mainstream though exotic in 1996.

**Cipher mode: CBC with a random IV** (CE's current recommendation), plus a separate MAC, or a combined authenticated mode (CCM/GCM). Notably, CE *changed* its advice from CTR to **CBC-with-random-IV** because so many real systems mishandle nonce generation — and a repeated nonce in CTR/GCM/ChaCha20-Poly1305 is catastrophic. CTR is excellent *only if* nonce uniqueness is guaranteed; OFB is strictly worse than CTR; **ECB is never acceptable** (identical plaintext blocks leak as identical ciphertext blocks — the "ECB penguin"). Prefer authenticated encryption (AEAD) so confidentiality and integrity come together, but respect the nonce discipline it demands. See the modes section in `references/algorithms-and-c-code.md`.

**What's broken or dated vs. what to use now** (state the deprecation whenever these come up):

| Old choice | Status today | Use instead |
|---|---|---|
| DES (56-bit) | Broken (brute force) | AES-256 |
| Triple-DES | Legacy only; 64-bit block (Sweet32) | AES-256 |
| IDEA, Blowfish | Dated; 64-bit block | AES-256, or ChaCha20 (stream) |
| RC4 | Broken (biased keystream) | ChaCha20 |
| MD4, MD5 | Broken (collisions) | SHA-256, SHA-3, BLAKE2 |
| SHA-0 / SHA-1 | Broken (collisions) | SHA-256 / SHA-512 / SHA-3 |
| RSA/DH 512–1024-bit | Too short | RSA/DH ≥ 2048, or X25519/Ed25519 |
| `hash(key‖msg)` as a MAC | Length-extension-vulnerable | HMAC-SHA-256 |
| Plain/fast hash for passwords | Brute-forceable | salt + stretch: Argon2/scrypt/bcrypt/PBKDF2 |
| `rand()`, LCGs for keys | Insecure | OS CSPRNG / Fortuna |

AES, SHA-2/3, HMAC, GCM, and the SHA-3 (Keccak) result all postdate the 1996 book; *Cryptography Engineering* covers them (SHA-3 was still an open competition at its 2010 writing — Keccak was selected in 2012).

## Recurring pitfalls (worth flagging proactively)

- **ECB mode** anywhere; reusing an IV or a stream-cipher keystream; reusing a nonce with GCM/ChaCha20-Poly1305 (catastrophic — reveals the auth key / plaintext XOR).
- **Encryption without authentication** — leads to bit-flipping and padding-oracle attacks.
- **Weak/duplicated randomness** for keys, IVs, nonces, or DSA per-message secrets (a repeated DSA `k` leaks the private key).
- **Rolling your own** cipher, mode, padding, or constant-time comparison; **non-constant-time** key/MAC comparisons leak via timing.
- **Treating a hash as a MAC** (`hash(key || message)` is length-extension-vulnerable for MD5/SHA-1/SHA-256 — use HMAC).
- **Storing passwords with a plain or fast hash** — salt (256-bit) and stretch (iterate), i.e. a slow KDF (Argon2, scrypt, bcrypt, PBKDF2); CE describes salting-and-stretching directly.
- **No man-in-the-middle protection** on key exchange — unauthenticated Diffie-Hellman is wide open; bind keys to identities (certificates, signatures).
- **Authenticating in the wrong order / partially** — prefer **encrypt-then-authenticate**, and the MAC must cover the IV/nonce and any headers, not just the plaintext.
- **Exposing nonces to application code** — CE's reason for favoring CBC-random-IV: every value an app must make unique is a value it eventually gets wrong. Hide nonce generation or make it impossible to misuse.
- **Key management neglected** — generation, storage, rotation, and destruction are the usual Achilles' heel; see `references/engineering-practice.md`.
- **Ignoring the weakest link / side channels** — a perfect cipher behind a timing leak, a swapped-to-disk key, or a sloppy PKI is not secure. Audit the whole system.

## Style for C examples

When illustrating a primitive in C, match the book's Part V conventions so examples are consistent and recognizable:

- Width typedefs `u1`/`u2`/`u4` for unsigned 8/16/32-bit, a `*_ctx` struct holding the expanded key/subkeys, and an init / key-schedule / encrypt / decrypt / destroy API.
- Rotations via macros, e.g. `#define ROTL32(X,C) (((X)<<(C))|((X)>>(32-(C))))`.
- Scrub sensitive material before freeing (`memset` the key schedule), as the book's `rc5_destroy` does.
- Add a one-line caveat that the snippet is for understanding, not production (no constant-time guarantees, no authentication, host-endianness assumptions).

## Related

- [[functional-programming]], [[scala]], [[tdd]] — sibling skills in this repo (general engineering practice).
- Primary source for recommendations: *Cryptography Engineering* — Ferguson, Schneier & Kohno (Wiley, 2010). The modern best-practice authority; basis of the design philosophy, recommendations, and `references/engineering-practice.md`.
- Source for structure and the C examples: *Applied Cryptography*, 2nd ed., Bruce Schneier (Wiley, 1996) — Parts I–V. C is adapted from the Part V source listings (lightly cleaned from OCR; loop bounds restored where the scan dropped characters). Historical/structural; defer to *Cryptography Engineering* on what's secure today.
