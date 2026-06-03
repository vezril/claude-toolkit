# Public-key algorithms and their number theory

From *Applied Cryptography* 2nd ed., Chapters 11 (math), 19 (public-key), 20 (signatures), 22 (key exchange). Public-key crypto rests on problems that are easy one way and hard the other: factoring large integers (RSA) and the discrete logarithm (Diffie-Hellman, ElGamal, DSA). Modern caveats noted throughout.

## Contents

1. Why public-key, and the hybrid pattern
2. Number-theory background you actually need
3. RSA
4. Diffie-Hellman key exchange
5. ElGamal
6. DSA and discrete-log signatures
7. Elliptic curves (post-book, but essential today)
8. Key length and modern recommendations

---

## 1. Why public-key, and the hybrid pattern

Symmetric crypto needs the two parties to already share a secret key — the distribution problem. Public-key crypto gives each party a **key pair**: a public key (published) and a private key (secret). Anyone can encrypt to you with your public key; only your private key decrypts. Sign with your private key; anyone verifies with your public key.

Public-key operations are ~100–1000× slower than symmetric, so real systems are **hybrid**: use public-key to agree on or transport a random **symmetric session key**, then encrypt the bulk data with AES/ChaCha20. This is exactly what TLS, PGP, and SSH do.

## 2. Number-theory background (Chapter 11)

- **Modular arithmetic.** Work in integers mod *n*. `a ≡ b (mod n)` means *n* divides *a−b*. Addition, multiplication, and exponentiation all reduce mod *n*.
- **Modular inverse.** `a^{-1} mod n` is the *x* with `a·x ≡ 1 (mod n)`; it exists iff `gcd(a,n)=1`, and the **extended Euclidean algorithm** finds it. Inverses are how RSA's private exponent is derived.
- **Euler's totient** `φ(n)` counts integers below *n* coprime to it; for a prime *p*, `φ(p)=p−1`, and for `n=pq` (distinct primes), `φ(n)=(p−1)(q−1)`. Euler's theorem: `a^{φ(n)} ≡ 1 (mod n)` when `gcd(a,n)=1` — the engine behind RSA.
- **Primes & generation** (11.5). Generate large primes by picking random odd numbers and applying a probabilistic primality test (**Miller–Rabin**) until one passes; the density of primes makes this efficient.
- **Hard problems.** **Factoring** `n=pq` and the **discrete logarithm** (given `g`, `p`, and `g^x mod p`, find *x*) are believed infeasible for large enough parameters on classical computers. (Both fall to a large quantum computer via Shor's algorithm — hence the push toward post-quantum crypto, well beyond this book.)
- **Fast modular exponentiation** (square-and-multiply) makes `m^e mod n` practical even for thousand-bit numbers; doing it in **constant time** matters to avoid leaking the exponent via timing.

## 3. RSA (19.3)

The most widely used public-key algorithm. Key generation:

1. Pick two large random primes *p*, *q*; let `n = p·q` (the modulus).
2. Compute `φ(n) = (p−1)(q−1)`.
3. Choose public exponent *e* with `1 < e < φ(n)` and `gcd(e, φ(n)) = 1` (commonly `e = 65537`).
4. Compute private exponent `d = e^{-1} mod φ(n)` (extended Euclidean).
5. **Public key** `(e, n)`; **private key** `d` (keep *p*, *q*, *d* secret).

Encryption / decryption of a message block `m < n`:

```
c = m^e mod n          (encrypt with public key)
m = c^d mod n          (decrypt with private key)
```

It works because `(m^e)^d = m^{ed} = m^{1 + kφ(n)} ≡ m (mod n)` by Euler's theorem. **Signing** is the mirror image: `s = m^d mod n` (private), verify `m = s^e mod n` (public) — in practice you sign a hash of the message, not the message.

**Security & caveats (sharpened by *Cryptography Engineering* Ch. 12).** RSA's security rests on the hardness of factoring *n*. Rules the bare math hides:

- **Never use textbook RSA.** Pad with **OAEP** for encryption and **PSS** for signatures — raw/deterministic RSA is malleable and leaks structure. CE stresses that the basic RSA operation is like a raw block-cipher round: you must wrap it in an encoding scheme.
- **Don't reuse one key for both encryption and signing.** Signing a value is the same math as decrypting it, so an attacker could get a ciphertext "signed" to decrypt it. CE's trick: two different public exponents on the same *n* (e.g. `e=3` for signatures, `e=5` for encryption) to decouple the operations; simpler still, use separate key pairs.
- **Short public exponent is fine and fast** (`e=3` or `65537`), as long as padding is used and `gcd(e, lcm(p−1,q−1))=1`.
- **Size of *n* ≥ 2048 bits** (1024 deprecated); design the system to handle up to **8192 bits** so you can grow in the field if cryptanalysis improves. Use the **Chinese Remainder Theorem** (Garner's formula) for ~4× faster private-key operations.
- Generate *p*, *q* from a strong CSPRNG with no shared factors across keys; sign `H(m)`, never raw *m*.

## 4. Diffie-Hellman key exchange (22.1)

Lets two parties derive a shared secret over a public channel without a prior shared key. Public parameters: a large prime *p* and a generator *g*.

```
Alice: picks secret a, sends  A = g^a mod p
Bob:   picks secret b, sends  B = g^b mod p
Alice computes  K = B^a mod p
Bob   computes  K = A^b mod p
       both get  K = g^{ab} mod p
```

An eavesdropper sees *g*, *p*, `g^a`, `g^b` but recovering `g^{ab}` requires solving the discrete log — infeasible for large *p*. **DH gives no authentication**, so plain DH is fully exposed to a **man-in-the-middle** who swaps in their own values; bind the exchange to identities (signatures, certificates) — that's what the **Station-to-Station** protocol does, and what TLS does. Prefer **ephemeral** DH (new secret per session) for forward secrecy.

**CE's practical rules (Ch. 11)** for a finite-field DH group, to avoid subtle subgroup/small-subgroup attacks:

- Work in a prime-order subgroup: pick **q a 256-bit prime** (DH exponents should be 256 bits so a collision attack on the exponent still costs ~2¹²⁸), and **p a large prime of the form `p = Nq + 1`** (a "safe prime" is the case `N=2`). Pick a generator *g* with `g ≠ 1` and `g^q = 1`.
- Make **p large enough** for the secrecy lifetime (≥ 2048 bits; support up to 8192).
- **Validate received parameters**: check that *p* and *q* are prime, *q* divides `p−1`, *q* is the right size, and any received public value *X* satisfies `X ≠ 1` and `X^q = 1 mod p` — otherwise you're open to small-subgroup attacks. Don't trust keys that are too small.

Or sidestep all of this with **X25519** (Curve25519 ECDH), which bakes in safe parameters.

## 5. ElGamal (19.6)

A public-key encryption and signature scheme based on discrete logs. Private key *x*; public key `y = g^x mod p`. To encrypt *m*, pick a random ephemeral *k* and send `(g^k mod p, m·y^k mod p)`; decrypt by recovering `y^k = (g^k)^x` and dividing it out. The random *k* must be **fresh and secret per message** — reuse leaks the key. ElGamal underlies DSA.

## 6. DSA and discrete-log signatures (20.1)

The **Digital Signature Algorithm** (NIST) signs with a discrete-log construction. It produces a pair `(r, s)` from the message hash, the private key, and a **per-message secret *k***. The non-negotiable rule: *k* must be **unique, secret, and unpredictable** for every signature. A repeated or predictable *k* (the bug that broke the Sony PS3 and some Bitcoin wallets) lets an attacker **recover the private key** from two signatures. Modern practice uses deterministic *k* (RFC 6979) or **Ed25519**, which sidesteps the whole class of nonce bugs.

## 7. Elliptic curves (post-book, essential today)

The 2nd edition mentions elliptic-curve cryptosystems (19.8) as promising but new. They've since become the default: EC discrete-log is harder per bit, so a **~256-bit EC key ≈ 128-bit symmetric security** (vs. ~3072-bit RSA). In modern systems prefer **X25519** for key exchange and **Ed25519** for signatures — fast, small keys, and designed to avoid the nonce/padding pitfalls above. Flag to users that anything elliptic-curve is largely outside this 1996 book.

## 8. Key length and modern recommendations

Book Table 7.9 (brute-force-equivalent): symmetric ↔ public-key — 56↔384, 64↔512, 80↔768, 112↔1792, 128↔2304 bits. The durable lesson is the large multiplier between symmetric and RSA/DH key sizes. Updated floors:

- Symmetric: **≥ 128 bits** (256 for long-term / post-quantum margin).
- RSA / finite-field DH: **≥ 2048 bits** (3072+ for long-term).
- Elliptic curve: **256-bit** curves (Curve25519/P-256) ≈ 128-bit security.
- Hashes: **≥ 256-bit** output (SHA-256, SHA-3, BLAKE2).

Always pull *p*, *q*, *k*, nonces, and session keys from the OS CSPRNG, and prefer audited libraries (libsodium et al.) over hand-rolled bignum code — timing side channels in modular exponentiation are a classic break.
