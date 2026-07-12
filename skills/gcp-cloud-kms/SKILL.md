---
name: gcp-cloud-kms
description: "Google Cloud KMS (Key Management Service) — central store and control plane for cryptographic KEYS (not secret payloads): you ask KMS to encrypt/decrypt/sign/verify/MAC or to WRAP a data key, and the key material never leaves. Hierarchy project→location→keyRing→cryptoKey→cryptoKeyVersion, location-bound; protection level per key (SOFTWARE cheap → Cloud HSM FIPS 140-2 L3 → EXTERNAL/EKM); purposes symmetric ENCRYPT_DECRYPT vs ASYMMETRIC_SIGN/DECRYPT vs MAC; envelope encryption (local DEK wrapped by KEK in KMS); CMEK points GCS/BigQuery/Compute at your key; automatic (symmetric-only) + manual rotation, old versions still decrypt; per-key IAM with separation of duties (admin vs crypto user); import/BYOK; 64 KiB direct encrypt limit. Use when creating/managing keys, choosing protection level, envelope-encrypting data, wiring CMEK, setting rotation, splitting key IAM, or deciding KMS-vs-Secret-Manager."
license: MIT
---

# GCP Cloud KMS

Centralized service to create, import, and manage cryptographic keys and to run
cryptographic operations (encrypt/decrypt, sign/verify, MAC, wrap/unwrap) in the cloud.
KMS holds and controls the *keys* — it does not hand back arbitrary stored payloads
(that is Secret Manager). You keep custody and an audit trail; Google runs the crypto.

## The mental model

- KMS stores and controls **keys**, not secret strings. You never "read a key back."
  You send data (or a data key) to KMS and get back ciphertext / plaintext / a signature.
  Key material for SOFTWARE/HSM keys **never leaves KMS**.
- Hierarchy: **project → location → key ring → key (`cryptoKey`) → key version**. Names:
  `projects/P/locations/L/keyRings/R/cryptoKeys/K/cryptoKeyVersions/V`.
- **Location-bound.** A key ring lives in one Cloud KMS location (region, dual/multi-region);
  keys inherit it. Key rings **cannot be deleted** and cost nothing; deleted key *names*
  can never be reused (the resource id must always point to the original material).
- **Protection level is per key and immutable after creation:** `SOFTWARE` (BoringCrypto,
  FIPS 140-3 validated, cheapest) → `HSM` (Cloud HSM, multi-tenant, FIPS 140-2 **Level 3**)
  → `HSM_SINGLE_TENANT` → `EXTERNAL` / `EXTERNAL_VPC` (Cloud EKM — key lives in a
  third-party manager outside Google, reached over internet or VPC). Same KMS API regardless.
- **Purpose is per key and fixed:** symmetric `ENCRYPT_DECRYPT`, `RAW_ENCRYPT_DECRYPT`,
  `ASYMMETRIC_SIGN`, `ASYMMETRIC_DECRYPT`, `MAC`. Symmetric keys have a **primary version**
  used by default for new encryption; asymmetric keys have **no primary** — you must name the
  version and distribute the **public key** to verifiers/encryptors.
- **Rotation adds a new version and makes it primary; old versions stay `ENABLED` and keep
  decrypting the data they encrypted.** Rotation does not re-encrypt existing data.

## Envelope encryption (why, and how it scales)

Direct `Encrypt`/`Decrypt` cap at **64 KiB** of input, and calling KMS per byte does not scale.
So wrap a key with a key:

1. Generate a **DEK** (data encryption key) locally, e.g. 256-bit AES-GCM.
2. Encrypt your data with the DEK, locally, at full speed.
3. Ask KMS (a **KEK** — key encryption key) to **wrap** (encrypt) the DEK — one small call.
4. Store the **wrapped DEK alongside the ciphertext**; discard the plaintext DEK.
5. To read: send the wrapped DEK to KMS to **unwrap**, then decrypt data locally.

One KEK in KMS protects millions of DEKs — every object can have its own DEK without
storing millions of keys centrally. The KEK never leaves KMS; only the tiny DEK crosses the wire.

## CMEK — customer-managed encryption keys

Point a GCP service's at-rest encryption at *your* KMS key instead of Google-managed keys —
Cloud Storage buckets, BigQuery datasets/tables, Compute/PD, and many more. Under the hood
each CMEK integration is server-side symmetric envelope encryption using your key.

- The service's **service agent** (a per-service Google-managed account) does the crypto; grant
  it `roles/cloudkms.cryptoKeyEncrypterDecrypter` **on the key**. End users need no key access.
- **Region colocation is required:** the KMS key location must match the protected resource's
  location (a regional bucket needs a key in the same region; multi-region resources need a
  compatible multi-region key). `EXTERNAL_VPC` is not available in multi-region locations.
- **Disable or destroy the CMEK and the data becomes inaccessible**; if it stays
  inaccessible too long some services incur permanent data loss.
- Enforce org-wide with org policy: `constraints/gcp.restrictNonCmekServices` (require CMEK),
  `constraints/gcp.restrictCmekCryptoKeyProjects` (limit which key projects are allowed).
- **Autokey** automates CMEK: it provisions key rings and keys on demand, per service and per
  best practice, when a resource is created — removing the manual keyring/key/IAM setup.

## Verified shapes (from docs)

```bash
# Key ring (location-bound, one-time), then a rotating symmetric key
gcloud kms keyrings create RING --location LOCATION
gcloud kms keys create KEY --location LOCATION --keyring RING \
    --purpose encryption --protection-level software \
    --rotation-period 30d --next-rotation-time 2026-08-01T00:00:00Z   # auto-rotate

# Encrypt / decrypt (<=64 KiB plaintext)
gcloud kms encrypt --location LOCATION --keyring RING --key KEY \
    --plaintext-file in.txt --ciphertext-file out.enc
gcloud kms decrypt --location LOCATION --keyring RING --key KEY \
    --ciphertext-file out.enc --plaintext-file back.txt

# Manual rotation = new version (becomes primary for symmetric keys)
gcloud kms keys versions create --location LOCATION --keyring RING --key KEY

# Grant a crypto user on ONE key (least privilege, per-key IAM)
gcloud kms keys add-iam-policy-binding KEY --location LOCATION --keyring RING \
    --member=serviceAccount:SA@PROJECT.iam.gserviceaccount.com \
    --role=roles/cloudkms.cryptoKeyEncrypterDecrypter
```

Rotation period must be **>= 1 day and <= 100 years**. Automatic rotation is **symmetric-only**
(not asymmetric sign/decrypt); rotate those manually. REST `:encrypt`/`:decrypt` take/return
base64. **Import/BYOK:** create an import job (RSA-OAEP 3072/4096 wrapping key), wrap your
material locally, import it as a version; supported for symmetric + asymmetric purposes on
SOFTWARE/HSM (not EXTERNAL). Version `origin` is `IMPORTED` vs `GENERATED`.

## Gotchas

- **Region colocation for CMEK is mandatory** — mismatched key/resource locations fail. Plan
  the key location before creating the protected resource.
- **Version states:** `PENDING_GENERATION` → `ENABLED` → `DISABLED` (reversible, blocks use) →
  `DESTROY_SCHEDULED` → `DESTROYED`. Destroy is not instant: there is a scheduled-destruction
  waiting period (default 24h, configurable) during which you can **restore** — irreversible only
  after it elapses. A version is usable only when `ENABLED`.
- **Separation of duties:** `roles/cloudkms.admin` manages keys but **cannot** encrypt/decrypt;
  crypto users get `cryptoKeyEncrypterDecrypter` / `cryptoKeyEncrypter` / `cryptoKeyDecrypter`
  or `signerVerifier`. Don't give one identity both, and avoid `owner`. Roles bind at project,
  key-ring, or (best) individual-key level.
- **Cost shape:** billed per **active key version per month** (SOFTWARE cheapest → HSM more →
  EKM most) **plus per cryptographic operation** (per 10,000 ops). Key rings are free. Disabled
  and destroy-scheduled versions can keep billing until fully destroyed. Cut cost with envelope
  encryption (few KMS calls), destroying stale versions, and SOFTWARE where custody rules allow.
  Confirm current numbers on the pricing page.

## KMS vs Secret Manager (get this right)

- **Cloud KMS = keys that DO crypto.** It wraps/unwraps data keys, signs/verifies, MACs. It
  never returns arbitrary stored bytes; the key stays inside. Use it for encryption-at-rest
  control (CMEK), envelope encryption, code/artifact signing, and BYOK/HSM/EKM custody.
- **[[gcp-secret-manager]] = secret STRINGS you store and read back.** API keys, DB passwords,
  certs, connection strings — versioned payloads fetched via `versions.access`. Secret Manager
  can itself use a KMS key for CMEK. If you need the value back, it's a secret; if you need
  something wrapped or signed, it's a key.

## Related

[[gcp-secret-manager]] · [[gcp-iam]] (roles/service agents) · [[gcp-cloud-storage]] (CMEK buckets) · [[gcp-bigquery]] (CMEK datasets) · [[gcp-compute-engine]] (CMEK disks) · [[gcp-cloud-sql]] · [[gcp-cloud-logging]] (key audit logs) · [[gcp-vpc-service-controls]] (EKM/exfiltration perimeter) · [[cryptography]] · [[secure-coding]]

Sources: https://docs.cloud.google.com/kms/docs , /kms/docs/resource-hierarchy , /kms/docs/envelope-encryption , /kms/docs/rotating-keys , /kms/docs/encrypt-decrypt , /kms/docs/cmek , /kms/docs/protection-levels , /kms/docs/reference/permissions-and-roles , /kms/docs/importing-a-key , https://cloud.google.com/kms/pricing (fetched 2026-07).
