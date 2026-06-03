# Cryptography engineering & operations

From *Cryptography Engineering* (Ferguson, Schneier & Kohno, 2010) — the system-level layer that turns sound primitives into a secure system. This is where real deployments succeed or fail (the weakest-link property). Recommendations here are current best practice.

## Contents

1. The secure channel
2. Generating randomness (Fortuna)
3. Key management and the clock
4. PKI: the dream vs. reality
5. Storing secrets (passwords, salting & stretching, sharing, wiping)
6. Implementation issues & side channels

---

## 1. The secure channel (Ch. 7)

A secure channel gives Alice and Bob **confidentiality**, **authenticity/integrity**, and correct **ordering** over a hostile network. The properties to design for: Bob receives a subsequence of Alice's messages, in order, with no duplicates, modifications, or forgeries, and he learns which messages he missed. The channel itself never resends — reliability is the caller's job (keeping the channel simple keeps it secure).

Design essentials:

- **Message numbers.** Give every message a unique, increasing number. It doubles as the **nonce** for encryption and defeats replay/reordering. Never let a number repeat under a key.
- **Order: encrypt-then-authenticate.** Encrypt the (numbered) plaintext, then MAC the **ciphertext including the nonce/IV and any header**. The receiver checks the MAC first and discards forgeries *before* decrypting — cheaper and avoids handing an attacker a decryption oracle. (The 1st-edition argued authenticate-then-encrypt; the modern consensus and CE's discussion favor protecting the ciphertext.)
- **Separate keys per direction and per purpose.** Derive distinct keys for A→B vs B→A and for encryption vs MAC from the negotiated key, so no key is used two ways.
- **Frame format** that unambiguously delimits message number, ciphertext, and MAC, so parsing can't be confused by attacker-chosen content.

In practice, use a vetted construction (TLS, the Noise framework, libsodium's `secretstream`) rather than assembling this by hand — but these are the properties to verify it provides.

## 2. Generating randomness — Fortuna (Ch. 9)

Bad randomness silently breaks everything above it (keys, IVs, nonces, DSA `k`). You need a **cryptographically secure PRNG** seeded by real entropy. CE specifies **Fortuna**, its own design:

- **Generator** — a block cipher (AES) in counter mode produces output; after each request it rekeys itself from its own output (so a later compromise can't reveal past output — forward secrecy), and it limits bytes per request.
- **Accumulator** — collects entropy from many sources into **32 pools**. Incoming events are distributed round-robin across pools; reseeds draw from pool *i* only every 2^i reseeds. This **defeats an attacker who controls some entropy sources**: even if they flood the fast pools, the slow pools eventually collect enough unpredictable entropy to recover.
- **Seed file** — persist entropy across reboots; read-and-update it atomically at startup, and be careful with **VM snapshots/clones** (two clones with the same seed produce the same "random" stream — a real-world catastrophe).

In application code, the pragmatic advice is to use the **OS CSPRNG** (`getrandom()`, `/dev/urandom`, `BCryptGenRandom`), which implements these ideas. Never use `rand()`, an LCG, or the clock. To choose a random value in a range, generate enough random bits and reduce carefully to avoid modulo bias.

## 3. Key management and the clock (Ch. 16–17)

Key management is the usual Achilles' heel. Themes:

- **The clock** (Ch. 16) — many protocols need time (expiry, uniqueness, monotonicity). Attackers can set it back, forward, or stop it; build a reliable monotonic clock and don't trust the bare RTC for security decisions.
- **Key servers / Kerberos** (Ch. 17) — a central trusted server shares a key with each party and issues session keys. Simple and effective inside one administrative domain, but a single point of trust and failure.
- **Keys wear out** (Ch. 20) — limit each key's lifetime and the volume of data under it; rotate. Long-lived keys accumulate exposure (more ciphertext for cryptanalysis, more chances to leak).

## 4. PKI: the dream vs. reality (Ch. 18–20)

**Public-Key Infrastructure** binds public keys to identities via certificates signed by a Certificate Authority, so parties who never met can authenticate. That's the *dream* (Ch. 18). The *reality* (Ch. 19) is harder:

- **Names** are ambiguous; a certificate binds a key to a name, but not the name to the real-world entity you care about. Authorization (what a key may *do*) is often what you actually want, not identity.
- **Trust** is transitive and rooted in CA root keys you must protect absolutely; a compromised or careless CA undermines everyone.
- **Revocation is required and hard.** A key can be compromised before its expiry, so you need **CRLs** (certificate revocation lists), **short expiry / fast re-issue**, or **online checking (OCSP)** — each with availability and freshness trade-offs. A PKI without working revocation is not trustworthy.

Use a PKI where it genuinely fits (a closed system with a clear authority — VPN access, internal services); be skeptical of a "universal" PKI. Prefer narrow, direct authorization and short-lived credentials.

## 5. Storing secrets (Ch. 21)

- **Passwords: salt and stretch.** Human passwords have little entropy, so a fast hash is brute-forceable. Add a per-password random **salt** (CE: 256-bit) stored alongside, and **stretch** by iterating a strong hash many times: `x₀ = 0; xᵢ = h(xᵢ₋₁ ‖ password ‖ salt); K = x_r`, with *r* as large as tolerable. The salt defeats precomputation/rainbow tables; stretching multiplies the attacker's per-guess cost. This is exactly what modern KDFs (**Argon2, scrypt, bcrypt, PBKDF2**) formalize — use one of those.
- **Secret sharing** — split a key so any *m* of *n* shares reconstruct it (Shamir threshold scheme) for robust backup / multi-party control. (See `protocols.md`.)
- **Where keys live** — disk (encrypted), human memory (passwords), portable/secure tokens, biometrics (recognize their limits — not secret, not revocable). Single sign-on concentrates risk.
- **Wiping secrets** — overwrite keys when done. Beware copies the platform makes: swap files, RAM caches, **solid-state wear-leveling** (which can leave old copies physically present), and cold-boot residual memory.

## 6. Implementation issues & side channels (Ch. 8, 15)

Correct algorithm, broken implementation = broken system.

- **Keeping secrets in memory** — wipe key material after use (`memset`, but beware the compiler optimizing it away — use a secure-zero routine); prevent keys from hitting the **swap file** (lock pages, `mlock`); mind caches and data remanence.
- **Side-channel attacks** — secrets leak through **timing**, power, cache behavior, and error messages, not just the output. Compare MACs and other secrets in **constant time**; make modular exponentiation and table lookups data-independent (the classic AES cache-timing leak); don't branch on secret data. Padding-oracle attacks turn a decryption error signal into full plaintext recovery — return uniform errors.
- **Quality of code** — simplicity, modularization, assertions, and avoiding buffer overflows matter more for crypto than almost anywhere; complexity is the enemy of security.
- **Big-integer arithmetic** (Ch. 15) — public-key code needs correct, side-channel-resistant bignum math. CE describes **"wooping"** — a redundant checksum modulo a small random prime carried alongside each computation — to catch computation errors (and fault attacks) in DH/RSA. Don't write your own bignum library for production; use a vetted constant-time one.

Bottom line: spend security attention on the system around the cipher — randomness, key handling, side channels, protocol glue, and human factors. That's where the weakest link almost always is.
