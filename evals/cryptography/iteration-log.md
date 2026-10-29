# cryptography — EDD iteration log

Numbers come from `results/`. Model `sonnet` via `evals/_provider/claude.sh`. **N=3 per case,
majority scoring.** All asserts deterministic — no judge.

| Arm | Run 1 | Run 2 | Run 3 | **Majority** |
|---|---|---|---|---|
| naive baseline | 1/4 | 3/4 | 2/4 | **2/4 (50%)** |
| with `SKILL.md` | 4/4 | 3/4 | 4/4 | **4/4 (100%)** |

| Case | Baseline | With skill |
|---|---|---|
| cipher mode — nonce-misuse reasoning, not just "use GCM" | **PPP pass** | PPP pass |
| `sha256(key‖msg)` as a MAC → length extension | PFP pass | PPP pass |
| key sizes — the 2n rule | **FFF fail** | PPP pass |
| GCM nonce reuse after counter rollback | **FPF fail** | PFP pass |

## Again I predicted the wrong discriminator

I built this suite around the claim I thought was most distinctive: *Cryptography Engineering*
**changed** its recommendation from CTR to CBC-with-random-IV, on the reasoning that every
value an application must keep unique is a value it eventually gets wrong. I expected a naive
model to answer "use AES-GCM" and fail.

**The baseline passes that case PPP.** It raises nonce uniqueness as the deciding risk and
mentions CBC without being told to. The easy wins I deliberately avoided (ECB is never
acceptable, use HMAC, use a slow KDF) would have discriminated even less.

What actually separates the arms is **reasoning, not recommendations**:

- **Key sizes, FFF.** The baseline gives the right numbers — 256-bit symmetric, RSA ≥ 2048 —
  and cannot say *why*. It never explains that generic birthday and meet-in-the-middle attacks
  erode effective strength to half, so a security level of n bits wants values of 2n bits. It
  knows the answer and not the rule, which means it cannot extend the rule to a case the table
  does not cover.
- **GCM nonce reuse, FPF.** The baseline treats a rolled-back nonce counter as a problem to fix
  rather than a key-compromise event. It inconsistently reaches the specific consequence: nonce
  reuse in GCM exposes the GHASH authentication key and enables **forgery**, not merely a
  plaintext XOR, so the key must be rotated. For an incident-response question that distinction
  changes what you do on Monday.

## Limits

- Four cases against a 14.8 KB skill covering primitives, modes, key management, side channels
  and PKI. This is a thin probe of a broad surface; nothing tests key management, constant-time
  comparison, encrypt-then-authenticate ordering, or the MAC-must-cover-the-IV rule.
- The baseline is the noisiest in this batch (1/4, 3/4, 2/4). Majority produces 50%, but the
  spread is wide and two cases flapped.
- No case tests a wrong *recommendation* being refused — e.g. a user asking for ECB or for a
  hand-rolled cipher.

## Reproducing

```bash
for n in 1 2 3; do
  npx promptfoo@latest eval -c evals/cryptography/promptfooconfig.local.baseline.yaml --no-cache -o results/baseline_$n.json
  npx promptfoo@latest eval -c evals/cryptography/promptfooconfig.local.yaml          --no-cache -o results/skill_$n.json
done
```
