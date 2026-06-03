# Symmetric algorithms, cipher modes, and hashes — with C

C examples are adapted from *Applied Cryptography* 2nd ed., Part V (Source Code), lightly cleaned from OCR (notably restoring `<` and loop bounds the scan dropped, and `0x` hex prefixes). They illustrate structure; they are **not** production code (no constant-time guarantees, no authentication, host-endianness assumed). Pair any real use with a vetted library (see the main SKILL.md). Recommendations here follow *Cryptography Engineering* (2010); the C illustrates how the older ciphers are built.

## Contents

1. Shared C conventions
2. Block ciphers: the Feistel idea
3. DES — structure, context, and API
4. AES — the modern default (structure)
5. Blowfish — a clean Feistel round in C
6. RC5 — a complete small cipher in C
7. Cipher modes: ECB, CBC, CTR (and which to use)
8. Stream ciphers: RC4, SEAL
9. One-way hash functions, and the length-extension fix
10. MACs: HMAC, CMAC, GMAC
11. Choosing a symmetric algorithm (then vs. now)

---

## 1. Shared C conventions

The book's listings use fixed-width typedefs, a context struct for the expanded key, and an init/key/encrypt/decrypt/destroy API:

```c
typedef unsigned char  u1;   /* 8-bit  */
typedef unsigned short u2;   /* 16-bit */
typedef unsigned long  u4;   /* 32-bit on the book's platforms; use uint32_t today */

/* rotations — replace with hardware rotate instructions where available */
#define ROTL32(X,C) (((X)<<(C))|((X)>>(32-(C))))
#define ROTR32(X,C) (((X)>>(C))|((X)<<(32-(C))))
```

On a modern compiler prefer `<stdint.h>` (`uint8_t`, `uint16_t`, `uint32_t`) so widths are exact regardless of platform — the book's `unsigned long` is 64-bit on LP64 systems, which would break the code.

## 2. Block ciphers: the Feistel idea

Most block ciphers in the book (DES, Blowfish, ...) are **Feistel networks**. Split the block into halves *L* and *R*; each round computes `L_{i} = R_{i-1}`, `R_{i} = L_{i-1} XOR F(R_{i-1}, K_i)`. The round function *F* need not be invertible — decryption runs the same structure with subkeys in reverse order. This is why the same code path, with a reversed key schedule, both encrypts and decrypts.

## 3. DES — structure, context, and API

DES is a 16-round Feistel cipher on 64-bit blocks with a 56-bit key (8 bytes, one parity bit each). It is **broken by brute force** — present it for historical/structural understanding and steer real use to AES. The book's interface:

```c
#define EN0 0   /* MODE == encrypt */
#define DE1 1   /* MODE == decrypt */

typedef struct {
    unsigned long ek[32];   /* encryption key schedule */
    unsigned long dk[32];   /* decryption key schedule */
} des_ctx;

extern void deskey(unsigned char *, short);  /* hexkey[8], MODE: build key register   */
extern void usekey(unsigned long *);          /* cookedkey[32]: load expanded key       */
extern void cpkey(unsigned long *);            /* copy expanded key out                  */
extern void des(unsigned char *, unsigned char *); /* from[8] -> to[8], one block        */
```

The internal round (`desfunc`) applies the initial permutation, 16 rounds of expansion / key-mixing / S-box substitution / P-permutation, then the final permutation, driven by eight precomputed S-box tables (`SP1`..`SP8`, each `unsigned long[64]`). The S-box tables are the bulk of the listing and are what make a software DES fast (they fold permutation + substitution into table lookups).

**Triple-DES** (encrypt–decrypt–encrypt with two or three keys) was the book-era fix for DES's short key, but its 64-bit block makes it vulnerable to birthday-bound (Sweet32) attacks on long data streams; prefer AES.

## 4. AES — the modern default (structure)

AES (Rijndael) is **the** block cipher to use today; it postdates *Applied Cryptography* so there's no Part V C for it, but its structure is worth knowing. It's a **substitution-permutation network** (not Feistel): 128-bit blocks, 128/192/256-bit keys, 10/12/14 rounds. Each round on the 4×4 byte state applies four steps — **SubBytes** (a fixed nonlinear S-box per byte), **ShiftRows** (cyclically shift rows), **MixColumns** (mix each column via GF(2⁸) arithmetic), and **AddRoundKey** (XOR the round subkey); the last round omits MixColumns. Decryption runs the inverse steps.

*Cryptography Engineering* recommends AES as the default and **256-bit keys** (per the "2n bits for n-bit security" rule). Known attacks on AES are academic only. Don't hand-implement it — table-based implementations leak via cache-timing side channels, so use a library with AES-NI hardware support or a constant-time/bitsliced implementation. If you want extra margin, double-encrypt AES then Serpent or Twofish with **independent** keys. For a stream/AEAD alternative, **ChaCha20-Poly1305** is excellent and easy to implement in constant time.

## 5. Blowfish — a clean Feistel round in C

Blowfish (Schneier's own cipher) is a 16-round Feistel on 64-bit blocks with key-derived S-boxes and a P-array of 18 subkeys. The round function and encipher loop OCR'd cleanly and show the Feistel structure plainly:

```c
unsigned long F(blf_ctx *bc, unsigned long x)
{
    unsigned short a, b, c, d;
    unsigned long y;

    d = x & 0x00FF;  x >>= 8;
    c = x & 0x00FF;  x >>= 8;
    b = x & 0x00FF;  x >>= 8;
    a = x & 0x00FF;
    /* (S0[a] + S1[b]) XOR S2[c], + S3[d]  — mod 2^32 */
    y = bc->S[0][a] + bc->S[1][b];
    y = y ^ bc->S[2][c];
    y = y + bc->S[3][d];
    return y;
}

void Blowfish_encipher(blf_ctx *c, unsigned long *xl, unsigned long *xr)
{
    unsigned long Xl = *xl, Xr = *xr, temp;
    short i;
    for (i = 0; i < N; ++i) {          /* N == 16 rounds */
        Xl = Xl ^ c->P[i];
        Xr = F(c, Xl) ^ Xr;
        temp = Xl; Xl = Xr; Xr = temp; /* swap halves */
    }
    temp = Xl; Xl = Xr; Xr = temp;     /* undo last swap */
    Xr = Xr ^ c->P[N];
    Xl = Xl ^ c->P[N + 1];
    *xl = Xl; *xr = Xr;
}
```

Decryption is identical but walks `c->P` from `N+1` down to `0`. The key schedule expands the key into `P[0..17]` and the four S-boxes by repeatedly enciphering an all-zero block — which is why setup is comparatively slow and Blowfish resists key-search via that cost. Blowfish is sound but its 64-bit block is dated; its successor in spirit is AES (or use ChaCha20 as a stream cipher).

## 6. RC5 — a complete small cipher in C

RC5 (Rivest) is the book's most compact full cipher: a data-dependent-rotation design parameterized by word size, round count, and key length. The whole thing fits on a page, so it's the best worked example. The listing below is faithful to Part V, with the loop headers the OCR dropped restored to the canonical algorithm (the round bodies are verbatim).

```c
#include <stdio.h>
#include <stdlib.h>

typedef unsigned char  u1;
typedef unsigned long  u4;

/* An RC5 context knows its round count and its subkeys. */
typedef struct {
    u4 *xk;   /* expanded key table, length 2*nr + 2 */
    int nr;   /* number of rounds */
} rc5_ctx;

#define ROTL32(X,C) (((X)<<(C))|((X)>>(32-(C))))
#define ROTR32(X,C) (((X)>>(C))|((X)<<(32-(C))))

void rc5_init(rc5_ctx *c, int rounds) {
    c->nr = rounds;
    c->xk = (u4 *) malloc(4 * (rounds * 2 + 2));
}

/* Scrub sensitive values before freeing — good hygiene the book models. */
void rc5_destroy(rc5_ctx *c) {
    int i;
    for (i = 0; i < (c->nr) * 2 + 2; i++) c->xk[i] = 0;
    free(c->xk);
}

void rc5_encrypt(rc5_ctx *c, u4 *data, int blocks) {
    u4 *d = data, *sk = (c->xk) + 2;
    int h, i, rc;
    for (h = 0; h < blocks; h++) {
        d[0] += c->xk[0];
        d[1] += c->xk[1];
        for (i = 0; i < c->nr * 2; i += 2) {
            d[0] ^= d[1];
            rc = d[1] & 31;            /* data-dependent rotation amount */
            d[0] = ROTL32(d[0], rc);
            d[0] += sk[i];
            d[1] ^= d[0];
            rc = d[0] & 31;
            d[1] = ROTL32(d[1], rc);
            d[1] += sk[i + 1];
        }
        d += 2;
    }
}

void rc5_decrypt(rc5_ctx *c, u4 *data, int blocks) {
    u4 *d = data, *sk = (c->xk) + 2;
    int h, i, rc;
    for (h = 0; h < blocks; h++) {
        for (i = c->nr * 2 - 2; i >= 0; i -= 2) {
            d[1] -= sk[i + 1];
            rc = d[0] & 31;
            d[1] = ROTR32(d[1], rc);
            d[1] ^= d[0];
            d[0] -= sk[i];
            rc = d[1] & 31;
            d[0] = ROTR32(d[0], rc);
            d[0] ^= d[1];
        }
        d[0] -= c->xk[0];
        d[1] -= c->xk[1];
        d += 2;
    }
}
```

The key schedule (`rc5_key`) seeds the table with the magic constants `P32 = 0xb7e15163` and `Q32 = 0x9e3779b9` (derived from *e* and the golden ratio), mixes in the user key, and stirs three passes:

```c
c->xk[0] = 0xb7e15163;                 /* P32 */
for (i = 1; i < xk_len; i++)
    c->xk[i] = c->xk[i - 1] + 0x9e3779b9;  /* Q32 */
/* then 3*max(pk_len, xk_len) mixing steps over A,B and the padded key pk[] */
```

Data-dependent rotations are RC5's novelty; they're what gives it strength with so little code. Note that even RC5 should use a vetted implementation and an authenticated mode for real use.

## 7. Cipher modes (AC Chapter 9; recommendations per Cryptography Engineering Chapter 4)

A block cipher only enciphers one fixed block. A **mode** turns it into something that handles arbitrary-length messages. Let `E` be one-block encryption and `XOR` be `^`:

- **ECB (Electronic Codebook)** — encrypt each block independently: `C_i = E(P_i)`. **Never use it**: equal plaintext blocks → equal ciphertext blocks, leaking structure. Schneier's example is the only mode he warns against unconditionally.
- **CBC (Cipher Block Chaining)** — XOR each plaintext block with the previous ciphertext block before encrypting; seed with a random **IV**:
  ```c
  /* CBC encrypt, conceptual: prev starts as a random IV */
  for (i = 0; i < nblocks; i++) {
      xor_block(P[i], prev);      /* P[i] ^= prev      */
      E(P[i]);                    /* C[i] = E(P[i])    */
      prev = P[i];                /* chain             */
  }
  ```
  Decryption inverts: `P_i = D(C_i) XOR C_{i-1}`. Needs a unique unpredictable IV per message and (separately) a MAC.
- **CFB (Cipher Feedback)** — turns the block cipher into a self-synchronizing stream cipher: `C_i = P_i XOR E(C_{i-1})`. Good for streams; an error propagates for a few blocks then heals.
- **OFB (Output Feedback)** — a synchronous stream cipher: keystream `O_i = E(O_{i-1})` (seeded by IV), `C_i = P_i XOR O_i`. No error propagation, but you must **never reuse the IV/keystream**.
- **CTR (Counter)** — `C_i = P_i XOR E(nonce || i)`. Parallelizable, random-access, simple; the basis of modern AEAD (GCM = CTR + a GHASH authenticator). Nonce must never repeat under a key.

**Which mode (Cryptography Engineering Ch. 4 & 7):** of these, only **CBC and CTR** are worth considering — ECB is never secure, and OFB is strictly dominated by CTR. CE's *current* recommendation is **CBC with a random IV**: it reversed its earlier CTR advice because too many real systems generate nonces incorrectly, and a repeated nonce in CTR (or GCM/ChaCha20-Poly1305) is catastrophic. CTR is excellent *only when* nonce uniqueness is guaranteed. Either way, **encryption alone is not enough** — combine with a MAC (encrypt-then-MAC, authenticating the IV too) or use a standardized authenticated mode (**CCM** or **GCM**, NIST). Prefer AEAD (GCM, ChaCha20-Poly1305) when you can meet its nonce discipline.

## 8. Stream ciphers: RC4, SEAL

A stream cipher generates a keystream that is XORed with the plaintext. The cardinal rule: **never reuse a keystream** — two messages under the same keystream XOR to reveal `P1 XOR P2`.

- **RC4** — tiny and once ubiquitous (SSL, WEP): a 256-byte permutation state `S[]` plus two indices, swapped to emit keystream bytes. **Broken** — its early keystream is biased and key-related-key attacks devastated WEP. Replace with **ChaCha20**.
- **SEAL** — a fast software stream cipher in the book (Part V), more of a historical reference now.
- **LFSRs** (Chapter 16) — linear-feedback shift registers are building blocks for hardware stream ciphers (e.g. A5 in GSM, also in Part V); linear on their own, so they're combined nonlinearly. A5 has since been broken.

## 9. One-way hash functions, and the length-extension fix

A one-way hash maps arbitrary input to a fixed digest such that it's infeasible to find a preimage or a collision. AC covers MD4, **MD5** (128-bit), MD2, **SHA** (160-bit), RIPE-MD, HAVAL; all are **Merkle–Damgård** — pad, split into blocks, run a compression function over a chaining state.

**Status:** MD4, MD5, and SHA-0/SHA-1 are **broken** (practical collisions). Use **SHA-256/SHA-512 (SHA-2)**, **SHA-3**, or **BLAKE2/BLAKE3**.

**The length-extension weakness (CE Ch. 5).** Merkle–Damgård hashes (MD5, SHA-1, SHA-2) leak structure: knowing `H(m)` lets an attacker compute `H(m ‖ padding ‖ suffix)` without knowing `m`. This is why `hash(key ‖ message)` is **not** a safe MAC. *Cryptography Engineering*'s fixes: **double hashing** `SHAd(m) = SHA(SHA(m))`, or **truncation** — e.g. for 128-bit security, hash with SHA-512 and keep 256 bits (which is what SHA-384/SHA-224 do). Birthday attacks mean an *n*-bit hash gives only *n/2*-bit collision resistance, so target a 256-bit digest for 128-bit security. SHA-3 (Keccak, sponge construction) is immune to length extension by design.

## 10. MACs: HMAC, CMAC, GMAC (CE Ch. 6)

A MAC gives keyed integrity/authenticity. Options: **CBC-MAC/CMAC** (block-cipher based), **HMAC** (hash based: `HMAC(k,m) = H((k⊕opad) ‖ H((k⊕ipad) ‖ m))`, which sidesteps length extension), and **GMAC** (the authenticator inside GCM). CE's pick: **HMAC-SHA-256, using the full 256-bit output.** Warnings it gives: GMAC degrades badly if you truncate tags (a 32-bit GMAC tag forges in ~2¹⁶ tries, not 2³²), and nonce-exposing modes are risky because applications reuse nonces — so avoid handing nonce generation to app developers. Never compare MAC tags with a non-constant-time `memcmp`.

## 11. Choosing a symmetric algorithm (then vs. now)

AC's selection advice (prefer publicly scrutinized algorithms with no known shortcuts over the secret or novel) still holds; *Cryptography Engineering* makes it concrete: **AES** (256-bit keys) for block encryption, **ChaCha20-Poly1305** for stream/AEAD, **HMAC-SHA-256** for MACs, **CBC-with-random-IV + MAC** or **GCM** for a secure channel. When a user reaches for DES/3DES/IDEA/Blowfish/RC4, explain the structure if they want to learn, but recommend the modern equivalent for anything real.
