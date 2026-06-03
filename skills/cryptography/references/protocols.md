# Cryptographic protocols

From *Applied Cryptography* 2nd ed., Parts I (Chapters 2–6) and III (Chapter 23). A **protocol** is an ordered series of steps, involving two or more parties, designed to accomplish a task. Cryptographic protocols use crypto to achieve goals — secrecy, authentication, fairness — even among parties who don't fully trust each other. The recurring threat models are **eavesdroppers** (passive), **active attackers** (modify/inject/replay), and **dishonest participants** (cheat within the protocol). Conventionally: Alice and Bob are the parties, Eve eavesdrops, Mallory is an active man-in-the-middle, Trent is a trusted arbitrator.

## Contents

1. Building blocks
2. Confidential communication (symmetric, public-key, hybrid)
3. One-way hashes and digital signatures
4. Key exchange and authentication (and their attacks)
5. Secret splitting and secret sharing
6. Intermediate protocols (timestamping, bit commitment, fair coin flips)
7. Advanced protocols (zero-knowledge, blind signatures, digital cash)
8. Protocol design pitfalls

---

## 1. Building blocks (Chapter 2)

- **One-way function** — easy to compute, infeasible to invert. The basis of much of what follows.
- **One-way hash function** — fixed-size, collision- and preimage-resistant digest; used for integrity, commitments, and to compress a message before signing.
- **Symmetric and public-key encryption** — see the algorithms references.
- **Digital signature** — sign with a private key, verify with the public key; provides authentication, integrity, and **non-repudiation** (the signer can't later deny it).
- **Nonce / random challenge** — a fresh, unpredictable value used once to defeat replay.

## 2. Confidential communication

- **Symmetric** (2.2): Alice and Bob share key *K*; Alice sends `E_K(M)`, Bob decrypts. Problem: they must establish *K* securely first.
- **Public-key** (2.5): Alice encrypts with Bob's public key; only Bob's private key decrypts. Solves distribution but is slow.
- **Hybrid** (the practical norm): Alice picks a random session key *k*, sends `E_{Bob_pub}(k)` plus `E_k(M)`. Fast bulk encryption with public-key distribution — TLS/PGP/SSH all do this.

## 3. One-way hashes and digital signatures (2.4, 2.6, 2.7)

- **Signing a hash**: signing the full message with a slow public-key op is wasteful and can be insecure, so sign `H(M)`. Verification re-hashes and checks. Always.
- **Signature + encryption** (2.7): to get confidentiality *and* authentication, combine carefully — sign then encrypt, or use authenticated constructions. Naively reusing one key pair for both signing and encryption, or signing ciphertext vs. plaintext ambiguously, opens attacks; modern guidance is to use distinct keys per purpose and a vetted scheme.
- **MAC vs. signature**: a MAC (HMAC) gives integrity between parties sharing a key but **not** non-repudiation (either party could have produced it); a digital signature gives non-repudiation because only the private-key holder could sign.

## 4. Key exchange and authentication (Chapter 3)

- **Key exchange with symmetric crypto + KDC**: a trusted **Key Distribution Center** (Trent) shares a key with everyone and hands out session keys — the model behind **Kerberos** (Part IV). Single point of trust/failure.
- **Key exchange with public-key**: Diffie-Hellman (see public-key reference) or public-key transport of a session key.
- **Authentication**: prove identity via something derived from a secret without revealing it — a challenge–response on a shared key or a signature over a nonce.
- **Interlock / Station-to-Station**: authenticated key agreement that resists man-in-the-middle by binding the exchange to signed identities.

**The attacks to always consider:**

- **Man-in-the-middle (Mallory)** — relays and substitutes during an *unauthenticated* exchange so each party shares a key with Mallory, not each other. Defeated only by authenticating the key material (certificates, signatures, pre-shared identity).
- **Replay** — Eve records a valid message and re-sends it later. Defeated with nonces, timestamps, or sequence numbers.
- **Reflection / oracle** — tricking a party into answering its own challenge or acting as a decryption/signing oracle. Defeated by directional, well-typed messages.

## 5. Secret splitting and secret sharing (3.6, 3.7)

- **Secret splitting**: split a secret so all pieces are needed to reconstruct it. Simplest scheme: XOR the secret with random pads so the shares XOR back to the secret — lose one share and you have nothing.
- **Threshold secret sharing** (Shamir, 23.2): a `(m, n)` scheme distributes *n* shares such that **any *m*** reconstruct the secret but `m−1` reveal nothing. Built on polynomial interpolation: encode the secret as a degree-`(m−1)` polynomial's constant term; shares are points; any *m* points determine the polynomial. Used for key escrow, robust key backup, multi-party control.

## 6. Intermediate protocols (Chapter 4)

- **Timestamping** (4.1): prove a document existed at a time — hash it and have a trusted service (or a hash chain / linking scheme) sign the hash + time, so the content can't be backdated or altered.
- **Bit commitment** (4.9): commit to a value now, reveal later, unable to change it meanwhile (like a sealed envelope). Implement by sending `H(value || nonce)`; reveal `value` and `nonce` to open. Foundation for coin flips and ZK proofs.
- **Fair coin flip over a channel** (4.10): use bit commitment so neither party can bias the result — commit, then the other calls it, then open.
- **Subliminal channel, undeniable / fail-stop signatures** (4.x): signature variants with extra properties (hidden messages, signer-controlled verification, forgery detection).

## 7. Advanced protocols (Chapter 5)

- **Zero-knowledge proofs** (5.1): prove you know a secret (e.g. a discrete log, or a graph 3-coloring) **without revealing it**, by a challenge–response repeated until a cheater's success probability is negligible. Basis of identification schemes (Feige–Fiat–Shamir, Schnorr — Chapter 21).
- **Blind signatures** (5.3): get a message signed without the signer seeing its content (the signer signs a blinded value; you unblind to a valid signature). The engine of anonymous **digital cash** (6.4) and anonymous credentials.
- **Oblivious transfer, contract signing, certified mail** (5.5–5.8): fairness primitives ensuring neither party gains an advantage by quitting early.

## 8. Protocol design pitfalls

- **No authentication on key agreement** → man-in-the-middle. Authenticate key material.
- **No freshness** (nonce/timestamp/sequence) → replay.
- **Reusing keys across purposes** (same key for signing and decryption, same key in two protocols) → cross-protocol attacks.
- **Acting as an oracle** — answering arbitrary decrypt/sign queries lets an attacker extract secrets; constrain and type your messages.
- **Assuming participants are honest** — design so a cheating party gains nothing (commitments, threshold schemes, ZK).
- **Wrong authentication order** — prefer **encrypt-then-authenticate**, with the MAC covering the IV/nonce and headers (see `engineering-practice.md` on secure-channel design).
- **Rolling your own protocol** — like rolling your own cipher, this is where subtle breaks live. Prefer analyzed, standard protocols (TLS, Signal, Noise framework) and authenticated AEAD over bespoke message flows.

For building and operating a secure channel end to end — message numbering, ordering, key management, PKI, and storing the resulting keys — see `references/engineering-practice.md`.
