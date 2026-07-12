---
name: gcp-cloud-storage
description: "Google Cloud Storage — durable object storage in globally-unique buckets. Storage classes (Standard/Nearline/Coldline/Archive) + Autoclass, location types (region/dual/multi), Object Lifecycle Management, versioning + soft delete, uniform bucket-level access (UBLA) vs legacy ACLs, signed URLs, retention policies + Bucket Lock (WORM), CMEK/CSEK encryption, resumable/composite uploads, requester pays, the `gcloud storage` CLI (replaced gsutil), and cost control (class + lifecycle + egress/operation charges). Use when storing/serving blobs, backups, data-lake or ML datasets, static assets, or logs on GCP; choosing a storage class or bucket location; wiring lifecycle/retention/versioning; locking down bucket access; or controlling storage/egress cost."
license: MIT
---

# GCP Cloud Storage

Google's managed **object storage**: store and retrieve any amount of unstructured data (blobs) worldwide. The flagship durable store on GCP — backups, data-lake/analytics staging, ML datasets, static web assets, logs, archives. Not a filesystem: no in-place edits, no POSIX semantics.

## The mental model

- **Flat namespace of immutable objects inside buckets.** A bucket holds objects keyed by name.
  - Objects are **immutable** — you replace the whole object, never edit in place.
  - "Directories" are an illusion: they're just `/` characters in the key (prefixes). There are no real folders (unless you opt into a hierarchical-namespace bucket).
  - Every write is **atomic** — the object is either fully there or not; a successful write is readable immediately.
- **Bucket names are a single global namespace.** A name like `my-app-data` is unique across *all* of Google Cloud — DNS-like, and a taken name stays taken even after deletion for a while.
  - A bucket's **location is fixed at create time** and can never change. Moving = create-new + copy.
- **Class × location set cost/durability/latency**, chosen independently. *Storage class* is a per-object cost/access tier; *location type* is the geographic redundancy shape. All classes/locations share the same **11 nines** durability design.
  - Classes, hot → cold: **Standard** (no min duration, no retrieval fee, 99.99% avail in a region) → **Nearline** (30-day min, monthly-ish access) → **Coldline** (90-day min, quarterly-ish) → **Archive** (365-day min, <yearly). Colder = cheaper GB-month but higher retrieval fees + longer minimum-storage duration.
  - Location types: **region** (lowest storage price; synchronous redundancy across zones in one region; zero RTO), **dual-region** (a chosen region pair; async cross-region replication; optional *turbo replication* for a ~15-min RPO), **multi-region** (a broad geographic area; highest availability + auto failover; best for global serving).
  - A zonal deployment + the `Rapid` class exists for the highest-performance HPC/AI workloads in a single zone.
- **Strong consistency everywhere.** Read-after-write, read-after-metadata-update, read-after-delete, and object/bucket *listing* are all strongly, globally consistent — a just-written/overwritten/deleted object is immediately correct in reads *and* in list results. No eventual-consistency 404s like early S3.
  - Caveats: *publicly cached* objects (CDN / `Cache-Control`, default public TTL up to ~60 min) can serve stale until TTL expires; IAM grant/revoke and bucket recreate take ~1 minute to propagate; versioning-config changes need ~30 s to settle.
- **Access = IAM (recommended) vs legacy ACLs.**
  - With **Uniform Bucket-Level Access (UBLA)**, IAM alone governs the bucket and every object in it — and it unlocks IAM Conditions, managed folders, and domain-restricted sharing.
  - **Fine-grained** mode layers per-object ACLs on top of IAM: two overlapping systems, and access from *either* is enough — more surface for accidental exposure. Use only for genuine per-object grants or S3 migration.
  - UBLA is the recommended default. After enabling it you have **90 days** to revert to fine-grained.
  - Common predefined roles: `roles/storage.objectViewer` (read objects), `objectCreator` (write only), `objectAdmin` (full object CRUD), `admin` (bucket + objects). Grant at bucket level with IAM Conditions to scope by object prefix.

## Command shapes (`gcloud storage`, verified against docs)

`gcloud storage` is the current CLI — **it replaced `gsutil`** (2023-24; `gsutil` still ships in the SDK but is legacy — prefer `gcloud storage` for new work).

```bash
# Create a bucket with class + location (location is immutable afterward)
gcloud storage buckets create gs://my-app-data \
  --location=us-central1 --default-storage-class=STANDARD \
  --uniform-bucket-level-access --soft-delete-duration=7d

# Copy / sync (rsync mirrors a tree; -d deletes extras at dest)
gcloud storage cp ./build gs://my-app-data/site --recursive
gcloud storage rsync ./dist gs://my-app-data/site --recursive --delete-unmatched-destination-objects

# Set a per-object or default storage class; enable versioning
gcloud storage objects update gs://my-app-data/old.tar --storage-class=COLDLINE
gcloud storage buckets update gs://my-app-data --versioning

# Time-limited signed URL (V4; max 7 days) — needs a signing key/service account
gcloud storage sign-url gs://my-app-data/report.pdf --duration=1h \
  --private-key-file=key.json --http-verb=GET

# Grant read to a principal via IAM (UBLA path — no ACLs)
gcloud storage buckets add-iam-policy-binding gs://my-app-data \
  --member=user:alice@example.com --role=roles/storage.objectViewer
```

## Cost control

Storage cost is **storage (GB-month by class) + operations + network egress + retrieval fees**. Levers:

- **Pick the right class for access frequency.** Match the four classes to how often data is read. If access is *unknown or unpredictable*, enable **Autoclass**: it auto-moves each object toward Standard on read and toward colder classes on inactivity (Standard→Nearline 30d→Coldline 90d→Archive 365d), with **no retrieval or early-deletion fees** (only a per-object management fee). Objects <128 KiB stay in Standard. Best when you can't predict patterns; skip it if you already know them.
- **Object Lifecycle Management** — declarative rules on the bucket, each one action + one-or-more conditions.
  - Actions: `SetStorageClass` (tier down), `Delete`, and `AbortIncompleteMultipartUpload` (reclaim orphaned upload parts).
  - Conditions: `age`, `createdBefore`, `daysSinceCustomTime`, `matchesStorageClass`, `numNewerVersions` (for versioned objects), and more. A rule fires only when **all** its conditions match.
  - Conflict resolution: `Delete` beats a class change, and among class changes the cheaper class wins.
  - Use it to expire logs, prune old noncurrent versions, abort stale multipart uploads, and roll data down the tiers on a schedule — the primary hands-off cost lever alongside Autoclass.
- **Mind early-deletion minimums.** Deleting/overwriting/moving a Nearline/Coldline/Archive object *before* its 30/90/365-day minimum still bills the remaining days. Don't put churny data in cold classes.
- **Operations are billed by class.** Mutating/listing ops (create, list) are **Class A** (pricier); reads/metadata gets are **Class B** (cheaper). Millions of tiny-object ops can cost more than the bytes.
- **Egress.** Reads out of a region/multi-region cost network egress (cross-region and internet especially); intra-region and same-continent-to-Google-services are cheaper/free. Colocate compute with data. Front public read-heavy content with [[gcp-cloud-cdn]] to cut egress.
- **Requester Pays** — flip billing of operation + egress charges to the *caller's* project (they must pass a billing project or requests 400 with `UserProjectMissing`). The owner still always pays storage. Good for sharing large public datasets without eating egress.

## Data protection

- **Object Versioning** — when enabled, an overwrite or delete keeps the prior copy as a *noncurrent version*: same object name, distinct **generation number**.
  - Noncurrent versions are hidden from normal listings and reachable only by explicitly naming the generation.
  - Deleting a live object without a generation just turns it noncurrent (keeps its generation).
  - Pair with a lifecycle `numNewerVersions` / age rule so old versions don't accumulate forever. Each version bills at its normal rate; early-deletion charges apply when a version is *removed*, not when it becomes noncurrent.
- **Soft delete** — on by default, 7-day retention (configurable 7–90 days).
  - Deleted objects (and buckets) enter a recoverable soft-deleted state, excluded from normal lists; restore copies the object back into the bucket. Protects against accidental/malicious deletion.
  - Distinct from versioning: it retains *deleted* data for a window rather than keeping concurrent named versions. It bills storage during that window — **disable it on throwaway/short-lived buckets** to avoid surprise cost.
- **Retention policy + Bucket Lock (WORM)** — a bucket retention period blocks delete/overwrite of each object until it is older than the period (each object gets a `retentionExpirationTime`). Supports FINRA/SEC/CFTC and healthcare compliance when paired with audit logging.
  - **Locking** the policy is *irreversible* — afterward you can only *raise* the retention period, never remove/reduce it, and the bucket can't be deleted until every object ages out. A project lien is auto-applied.
  - **Holds** (event-based, temporary) pin individual objects against deletion independent of the policy; removing an event-based hold resets that object's retention clock.
- **Encryption at rest is always on**, at no extra cost. Options:
  - **Google-managed keys** (default) — nothing to configure.
  - **CMEK** — you hold the key in Cloud KMS to grant/rotate/revoke on your own schedule (PCI-DSS/HIPAA). See [[gcp-iam]] / KMS.
  - **CSEK** — you supply the raw key on every request; Google never stores it. Lose it and the data is permanently unreadable (you still pay storage until you delete it).
  - **Client-side encryption** — you encrypt before upload for maximum control; Google never sees plaintext.

## Uploads & transfer

- **Single-request upload** — the whole object in one HTTP request. Fine for small objects where re-sending on failure is cheap (rule of thumb: up to ~30 MB on a slow link, ~2 GB in-region).
- **Resumable uploads** — recommended for large files or flaky networks; one extra setup request, then the transfer can resume from where it broke instead of restarting. Works for any size and supports streaming.
- **Parallel composite uploads** — split a file into chunks uploaded concurrently, then `compose` them into one composite object (faster for big files; note the result is a *composite* object, which has some CSEK/validation caveats).
- **XML multipart upload** — S3-compatible part-based upload with parallel parts.
- **Storage Transfer Service** — for bulk/scheduled/one-off ingestion from S3, other clouds, HTTP sources, or on-prem — use this, not a plain `cp` loop.

## Access sharing without accounts

- **Signed URLs** — a time-limited URL granting one operation (GET/PUT/etc.) on one object, no account needed. V4 max validity is **7 days**; once minted it can't be revoked short of rotating the signing key. Generate via `gcloud storage sign-url` or client libraries (needs a service-account signing key). Ideal for browser download/upload links.
- **Signed policy documents** — constrain what a browser upload may contain (size, content type), letting untrusted web visitors upload directly under rules you set.

## Gotchas

- **Bucket name is global + immutable location.** Pick names carefully (they're forever-reserved once taken) and get the location right at creation — you cannot move a bucket; migrating means create-new + copy.
- **UBLA migration is one-way-ish.** After enabling UBLA you have only 90 days to switch back to fine-grained ACLs; audit for ACL-dependent flows before enabling.
- **Signed URLs expire (V4 max 7 days)** and, once minted, can't be revoked short of rotating the signing key — keep durations short and don't leak them.
- **Ramp hot buckets gradually.** A bucket starts around ~5,000 reads/s and ~1,000 writes/s and auto-scales over *minutes*; if you spike faster, expect 429/5xx — grow no faster than **doubling every ~20 minutes** and retry with exponential backoff. Avoid **sequential key prefixes** (timestamps, incrementing IDs) — they hotspot the index; add a short hash prefix to spread load. (Hierarchical-namespace buckets get higher initial QPS.)
- **Public caching breaks the "strong consistency" mental model** — cached public objects can serve stale until TTL; version asset filenames or set short `Cache-Control` if freshness matters.

## vs siblings

- **GCS vs Filestore / Persistent Disk** — GCS is object storage (HTTP API, immutable objects, no POSIX). Need a mounted POSIX filesystem, in-place edits, or low-latency block I/O for a VM/GKE? Use Filestore (NFS) or Persistent Disk, not GCS.
- **GCS vs [[gcp-bigquery]]** — store raw/columnar files (Parquet, Avro, CSV) in GCS; query them in place via BigQuery **external tables**, or load them in. GCS is the lake's storage layer; BigQuery is the query engine. [[gcp-dataflow]] reads/writes GCS for batch/stream ETL.

## Related
[[gcp-bigquery]] · [[gcp-dataflow]] · [[gcp-pubsub]] · [[gcp-cloud-cdn]] · [[gcp-media-cdn]] · [[gcp-load-balancing]] · [[gcp-iam]] · [[gcp-secret-manager]] · [[gcp-vpc-service-controls]] · [[gcp-cloud-sdk]] · [[gcp-compute-engine]] · [[gcp-gke]] · [[gcp-cloud-run]] · [[gcp-lakehouse]]

Sources: https://docs.cloud.google.com/storage/docs, /storage/docs/locations, /storage/docs/storage-classes, /storage/docs/autoclass, /storage/docs/lifecycle, /storage/docs/object-versioning, /storage/docs/consistency, /storage/docs/access-control, /storage/docs/access-control/signed-urls, /storage/docs/encryption, /storage/docs/bucket-lock, /storage/docs/soft-delete, /storage/docs/uploads-downloads, /storage/docs/requester-pays, /storage/docs/request-rate, cloud.google.com/storage/pricing (fetched 2026-07).
