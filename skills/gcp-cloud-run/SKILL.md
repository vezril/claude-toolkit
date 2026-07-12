---
name: gcp-cloud-run
description: "Google Cloud Run — GCP's fully managed serverless container platform and the modern default for deploying web apps, APIs, and batch work on GCP. Covers the three resource types (services for request-driven autoscaling workloads, jobs for run-to-completion tasks, worker pools for always-on pull-based consumers), the container contract (listen on 0.0.0.0:$PORT, stateless, in-memory filesystem, SIGTERM + 10s grace), the service → revision → instance model with traffic splitting/tags/gradual rollouts, autoscaling and concurrency tuning (default 80/vCPU concurrent requests, scale to zero, min/max instances, cold starts), request-based vs instance-based billing (CPU throttled between requests vs always allocated), Direct VPC egress vs Serverless VPC Access connectors, volume mounts (Cloud Storage FUSE, NFS, in-memory, secrets), GPU support (NVIDIA L4, RTX PRO 6000 — GA), Cloud Run functions as source-deployed services, deploy-from-source via buildpacks, quotas (8 vCPU/32 GiB, 60 min request timeout, 1000 concurrency) and pricing shape. Use when deploying or configuring a Cloud Run service/job/worker pool, writing gcloud run commands, tuning concurrency/scaling/billing mode, debugging cold starts or CPU throttling, wiring VPC egress or volumes, splitting traffic between revisions, or choosing between Cloud Run, Cloud Run functions, App Engine, and GKE."
license: MIT
---

# GCP Cloud Run

Google Cloud's fully managed serverless container platform: give it a Linux x86_64 container image (or just source code), it runs it, scales it with traffic — down to zero — and bills you only for what you use. No cluster, no VMs, no capacity planning. It is Google's recommended default for new applications on GCP.

## The mental model

**Three resource types, one platform.** A **service** handles HTTP/gRPC/WebSocket requests behind a stable `*.run.app` URL and autoscales with traffic (to zero, or to 1000+ instances). A **job** runs containers to completion — no port, no URL; think migrations, batch processing, array jobs fanned out over up to 10,000 parallel tasks. A **worker pool** (GA) is a set of always-on instances with no endpoint and no request-based autoscaling — you set the instance count manually (or drive it from external metrics like Kafka lag) — for pull-based consumers: Kafka, Pub/Sub pull, RabbitMQ.

**Service → revisions → instances.** Every deploy of a service creates an immutable **revision** (image + config snapshot). Traffic is split across revisions by percentage; each serving revision autoscales its own **instances**. Rollback = point traffic at the old revision. Nothing is ever edited in place — "artifacts drive state" applies here too.

**Jobs decompose into tasks.** A job execution runs `--tasks` N containers; each learns its shard from `CLOUD_RUN_TASK_INDEX` and processes its slice. `--parallelism` caps how many run at once; failed tasks retry up to `--max-retries`, and the exit code is the contract (0 = success).

**The container contract.** Your container must listen on `0.0.0.0` (not `127.0.0.1`) on the port in the `PORT` env var (default 8080), and be ready within 4 minutes of start. Treat instances as stateless and disposable: the filesystem is in-memory (writes consume the instance's RAM and vanish on shutdown). On scale-down you get `SIGTERM`, then `SIGKILL` 10 seconds later — flush and exit fast. Services see `K_SERVICE`/`K_REVISION`/`K_CONFIGURATION`; job tasks see `CLOUD_RUN_TASK_INDEX`/`CLOUD_RUN_TASK_COUNT`/`CLOUD_RUN_TASK_ATTEMPT` (that's how an array job shards work). A metadata server at `http://metadata.google.internal/` (header `Metadata-Flavor: Google`) hands out the project ID, region, and service-account tokens — never bake credentials into images.

**Concurrency is the scaling lever.** One instance serves many requests simultaneously — default max 80 per instance via console, 80 × vCPU via CLI/Terraform, cap 1,000. The autoscaler targets ~60% of the concurrency and CPU limits; when there's no free capacity it queues briefly (up to 3.5× average cold-start time or 10 s) and launches instances. Scale-to-zero means the first request after idle pays a **cold start**; mitigate with `--min-instances` (billed as idle instances), startup CPU boost, and lazy-loading less at boot.

## Deploy and traffic shapes

```bash
# Deploy a prebuilt image (creates the service or a new revision)
gcloud run deploy myapp --image us-docker.pkg.dev/PROJECT/repo/app:tag --region us-central1

# Deploy straight from source — Cloud Build + buildpacks (or your Dockerfile),
# image lands in the auto-created 'cloud-run-source-deploy' Artifact Registry repo
gcloud run deploy myapp --source . --region us-central1

# Canary: ship a revision with no traffic, test it via a tag URL, then shift
gcloud run deploy myapp --image IMAGE --no-traffic --tag green
#   → https://green---myapp-HASH.a.run.app for testing
gcloud run services update-traffic myapp --to-tags green=10      # 10% canary
gcloud run services update-traffic myapp --to-revisions myapp-00042-abc=100  # rollback
gcloud run services update-traffic myapp --to-latest             # back to normal

# Inspect state (revisions are the source of truth, not your memory of deploys)
gcloud run services describe myapp --region us-central1
gcloud run revisions list --service myapp --region us-central1

# Jobs: create, fan out, execute (or schedule via Cloud Scheduler)
gcloud run jobs deploy migrate --image IMAGE --region us-central1 \
  --tasks 100 --parallelism 10 --max-retries 3 --task-timeout 30m
gcloud run jobs execute migrate            # or --execute-now on deploy

# Worker pool: always-on consumers, manually scaled
gcloud run worker-pools deploy consumer --image IMAGE --region us-central1

# Billing mode: instance-based (CPU always on) vs request-based (default)
gcloud run deploy myapp --image IMAGE --no-cpu-throttling   # instance-based
gcloud run deploy myapp --image IMAGE --cpu-throttling      # request-based

# Scaling and concurrency knobs
gcloud run services update myapp --region us-central1 \
  --min-instances 1 --max-instances 50 --concurrency 40 \
  --cpu 2 --memory 1Gi --timeout 300

# Volumes: mount a GCS bucket via Cloud Storage FUSE (GA, gen2 exec env)
gcloud run deploy myapp --image IMAGE \
  --add-volume name=data,type=cloud-storage,bucket=MY_BUCKET \
  --add-volume-mount volume=data,mount-path=/mnt/data
```

Once you've split traffic, the split **persists across future deploys** until you `--to-latest` — a classic surprise when a "deploy" appears to do nothing.

## Configuration surface worth knowing

- **Auth & ingress.** By default a service requires IAM (`roles/run.invoker`); `--allow-unauthenticated` makes it public. Service-to-service calls send an ID token for the caller's service account (fetch it from the metadata server). `--ingress internal` / `internal-and-cloud-load-balancing` restricts who can even reach the URL; pair with [[gcp-iap]] or a load balancer for user-facing auth.
- **Service identity.** Each revision runs as a service account (`--service-account`); default is the Compute Engine default SA — give production services a dedicated least-privilege SA instead. Tokens come from the metadata server, so client libraries just work.
- **Env vars & secrets.** `--set-env-vars KEY=VAL` (limit 1,000 per container); Secret Manager secrets mount as env vars (`--set-secrets KEY=secret:version`) or as volume files — prefer volumes for rotation without redeploy. See [[gcp-secret-manager]].
- **Health probes.** Optional startup and liveness probes (HTTP/TCP/gRPC). Liveness probes require instance-based billing (the probe itself needs CPU between requests).
- **Sidecars (multi-container).** A service instance can run additional containers next to the serving one — Envoy, monitoring agents, proxies — sharing the network namespace and optional shared volumes. Only one container receives requests.
- **Manual scaling (services).** An alternative to autoscaling: pin a fixed instance count for a service when you need fully predictable capacity — the worker-pool model applied to a service.
- **Execution environments.** Gen2 is the modern default (full Linux syscall surface, required for GCS/NFS volume mounts); gen1 starts slightly faster for tiny workloads.
- **In-memory and NFS volumes.** Besides Cloud Storage FUSE, you can mount `type=in-memory` tmpfs volumes (sized against the memory limit, shareable between sidecars) and NFS/Filestore shares for POSIX file semantics.
- **Regions.** Services are regional; multi-region = deploy per region behind a global external Application Load Balancer with serverless NEGs ([[gcp-load-balancing]]).

## Gotchas

- **CPU throttling between requests (request-based billing, the default).** Outside of request processing the CPU is throttled to near-zero — background threads, async work kicked off after the response, and metrics flushes silently stall. Anything that must run outside a request needs instance-based billing (`--no-cpu-throttling`), a job, or a worker pool.
- **Request-based vs instance-based billing** is a per-service switch, not a different product. Request-based: pay per request + CPU/memory only while serving (cheap for spiky traffic). Instance-based: pay for the whole instance lifetime at a lower unit rate (cheaper for steady load; required for health-check probes and GPU services; needs ≥512 MiB memory). The GCP Recommender will suggest switching when the math favors it.
- **`--min-instances` costs real money.** A min instance is billed continuously as an idle instance. It's the cold-start cure, but 1 always-on instance can dwarf the bill of a low-traffic service that would otherwise sit at zero. Idle instances above min are reclaimed after ~15 minutes (~10 for GPU).
- **Timeout maxima.** Service request timeout: default 5 min, max **60 minutes** — the response must complete within it, including cold-start time. Job task timeout: default 10 min, max **168 hours** (1 h with GPU). Longer than that → jobs with checkpointing, or a worker pool.
- **Concurrency tuning.** Single-threaded runtimes (one-request-at-a-time frameworks) on multi-vCPU instances create hot-spot cores and confuse CPU-based autoscaling — lower concurrency (even to 1) so scaling follows throughput. High concurrency saves money only if your code genuinely handles parallel requests (async I/O or threads). Adaptive Concurrency Tuning nudges the effective limit to keep CPU under 90%.
- **Direct VPC egress over connectors.** Both are GA, but Direct VPC egress is the recommendation: no connector VMs to pay for or manage, lower latency, higher throughput (1 Gbps/instance), per-service network tags for firewalling. Serverless VPC Access connectors remain for legacy setups — they bill compute 24/7 and bottleneck under spikes.
- **Filesystem is RAM.** Writing a 2 GiB temp file eats 2 GiB of the instance's memory limit; runaway writes OOM the instance. Use GCS volume mounts (no file locking, not fully POSIX; FUSE caches also consume memory) or NFS/Filestore volumes for real file needs.
- **GPUs (GA):** NVIDIA L4 (24 GB) and RTX PRO 6000 Blackwell (96 GB), one GPU per instance, instance-based billing required but still scales to zero; L4 needs ≥4 vCPU/16 GiB (8/32 recommended); limited regions; zonal redundancy on by default (reserved capacity, higher price) — `--no-gpu-zonal-redundancy` for best-effort at lower cost. `--gpu 1 --gpu-type nvidia-l4`.
- **Images must be Linux x86_64** (multi-arch images need a `linux/amd64` manifest entry) and should live in [[gcp-artifact-registry]] — a Mac-built `arm64` image fails at startup with an opaque error. Docker Manifest V2 and OCI formats are accepted.
- **Event-driven invocation is just HTTP.** Pub/Sub push subscriptions and [[gcp-eventarc]] deliver events as POSTs to your service URL; mind the mismatch between the Pub/Sub ack deadline (max 600 s) and your handler's processing time — long work belongs in a job or worker pool, with the handler only enqueueing.
- **`--max-instances` is a soft ceiling.** During spikes and deploys Cloud Run may briefly exceed it; when it saturates, excess requests queue ~10 s then get **429**s. Size it against downstream capacity (database connection pools especially — 100 instances × pool of 10 = 1,000 connections at your Cloud SQL box).
- **Session affinity is best-effort.** Instances are disposable; sticky sessions can break at any scale-down. Keep session state in [[gcp-memorystore-redis]] or a database, not instance memory.
- **WebSockets and streaming work, but live inside the request timeout** (max 60 min) — clients must implement reconnect logic, and each open socket occupies a concurrency slot for its lifetime.
- **Cold-start mitigation, in order of preference:** trim the image and lazy-load heavy deps (start listening on `$PORT` first, initialize after); enable startup CPU boost; raise concurrency so fewer instances are needed; set `--min-instances 1+` for latency-critical paths; keep instances warm with real traffic rather than synthetic pingers (min-instances is cheaper and honest). Deploys themselves cause a wave of cold starts as new-revision instances spin up — use gradual traffic migration for latency-sensitive services.

## Quotas and pricing shape

**Key limits (2026-07):** 8 vCPU / 32 GiB per instance; 1,000 concurrent requests per instance; 60 min max request timeout; 32 MiB HTTP/1 request cap (use streaming/gRPC/HTTP2 beyond that); 1,000 services and 1,000 jobs per project-region; 1,000 revisions per service (oldest pruned); jobs: 10,000 tasks, 10 retries, 168 h task timeout; 700 outbound connections/s per instance; 600 Mbps egress (1 Gbps with Direct VPC); container must start listening within 4 min. Most are per-region and increasable except the per-instance shape.

**Pricing shape** — two modes per service:

- **Request-based (default):** vCPU-seconds + GiB-seconds *only while serving requests* (100 ms granularity), plus ~$0.40 per million requests, plus egress. Idle costs nothing (scale to zero). Order of magnitude (2026-07): ~$0.000024/vCPU-s, ~$0.0000025/GiB-s.
- **Instance-based:** pay for the entire instance lifetime at lower unit rates, no per-request fee dominance; required for GPUs and liveness probes; the win-over point is steady traffic keeping instances busy most of the time.
- **Free tier ballpark:** 2 M requests, 360 K vCPU-s, 180 K GiB-s per month. Jobs and worker pools bill instance time only (no request fee). GPU time is a separate per-GPU-second rate. Rates vary by region and change — check cloud.google.com/run/pricing before doing cost math.

## Cloud Run vs siblings

- **vs Cloud Run functions**: a function *is* a Cloud Run service deployed from source — Google folded Cloud Functions (2nd gen) into Cloud Run; the function tooling adds event-trigger wiring (Eventarc, 90+ sources) and per-language function signatures. Use functions for small event handlers; use plain services when you want the container, sidecars, or full config surface. (1st-gen Cloud Functions is the legacy island.) See [[gcp-cloud-functions]].
- **vs App Engine**: App Engine (standard/flex) predates it and still runs, but Cloud Run is the strategic successor — same serverless economics with an open container contract instead of runtime lock-in. New projects should not start on App Engine. See [[gcp-app-engine]].
- **vs Compute Engine**: raw VMs ([[gcp-compute-engine]]) are for workloads that break the container contract — privileged access, custom kernels, GPUs beyond the Cloud Run catalog, licensing tied to machines, or anything needing local persistent disks.
- **vs GKE**: choose GKE when you need Kubernetes itself — operators/CRDs, DaemonSets, stateful workloads, multi-container orchestration beyond sidecars, node-level control. Cloud Run runs on Google's infrastructure with a Knative-shaped API, so the mental model transfers, but it deliberately hides the cluster. Default to Cloud Run; graduate to GKE when the platform's constraints (no privileged containers, request-shaped scaling) actually bite. See [[gcp-gke]].
- **Companions:** images from [[gcp-cloud-build]] + [[gcp-artifact-registry]] (source deploys use [[gcp-buildpacks]]); schedule jobs with [[gcp-cloud-scheduler]]; async triggers via [[gcp-pubsub]], [[gcp-eventarc]], and [[gcp-cloud-tasks]]; front with [[gcp-load-balancing]] + [[gcp-cloud-cdn]] or [[gcp-api-gateway]]; state in [[gcp-cloud-sql]], [[gcp-alloydb]], [[gcp-memorystore-redis]], or [[gcp-cloud-storage]].

## Related

[[gcp-cloud-functions]], [[gcp-app-engine]], [[gcp-gke]], [[gcp-cloud-build]], [[gcp-artifact-registry]], [[gcp-buildpacks]], [[gcp-cloud-sdk]], [[gcp-cloud-scheduler]], [[gcp-cloud-tasks]], [[gcp-eventarc]], [[gcp-workflows]], [[gcp-pubsub]], [[gcp-api-gateway]], [[gcp-load-balancing]], [[gcp-cloud-cdn]], [[gcp-vpc]], [[gcp-cloud-nat]], [[gcp-iam]], [[gcp-iap]], [[gcp-secret-manager]], [[gcp-cloud-sql]], [[gcp-alloydb]], [[gcp-memorystore-redis]], [[gcp-cloud-storage]], [[gcp-compute-engine]], [[gcp-cloud-logging]], [[gcp-cloud-monitoring]], [[gcp-cloud-trace]], [[docker]], [[devops]]

Sources: https://docs.cloud.google.com/run/docs, https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run, https://docs.cloud.google.com/run/docs/container-contract, https://docs.cloud.google.com/run/docs/configuring/billing-settings, https://docs.cloud.google.com/run/docs/about-instance-autoscaling, https://docs.cloud.google.com/run/docs/about-concurrency, https://docs.cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration, https://docs.cloud.google.com/run/docs/configuring/connecting-vpc, https://docs.cloud.google.com/run/docs/configuring/services/cloud-storage-volume-mounts, https://docs.cloud.google.com/run/docs/functions/comparison, https://docs.cloud.google.com/run/docs/configuring/services/gpu, https://docs.cloud.google.com/run/docs/deploying-source-code, https://docs.cloud.google.com/run/docs/create-jobs, https://docs.cloud.google.com/run/docs/deploy-worker-pools, https://docs.cloud.google.com/run/quotas, https://cloud.google.com/run/pricing (fetched 2026-07).
