---
name: docker
description: Containerizing software with Docker — packaging, isolating, distributing, and running applications in containers. Distilled from Jeff Nickoloff's *Docker in Action*. Covers what a container is and how it differs from a VM (OS-level isolation via Linux namespaces and cgroups, not a hypervisor), the image model (layers, union filesystem, tags, the registry/Docker Hub), writing Dockerfiles and image best practices (small base images, layer caching, multi-stage builds, non-root, .dockerignore), the container lifecycle (run/exec/logs/stop/rm), resource limits and isolation, persistent state with volumes (bind mounts vs managed volumes), container networking (bridge/host/none, port publishing, user-defined networks), multi-container apps with Docker Compose, and an intro to multi-host orchestration. Use when writing or reviewing a Dockerfile or compose file, containerizing an app, debugging container build/run/networking/volume issues, optimizing image size or build caching, or reasoning about container isolation and security. Complements os-virtualization (containers vs VMs), devops/terraform/ansible (what runs on provisioned infra), github-actions (CI images), and secure-coding.
---

# Docker

Package an application and its dependencies into a **container** — an isolated, portable, reproducible unit that runs the same on any host with a container runtime. Distilled from **Jeff Nickoloff's *Docker in Action***. The core promise: *"build once, run anywhere"* and *"keep a tidy computer"* — software ships with its environment, isolated from the host and from other software.

Cross-links: [[os-virtualization]] (containers vs VMs — the OS-level mechanism), [[os-security]] (namespaces/cgroups), [[devops]] / [[terraform]] / [[ansible]] (containers run on the infra those provision), [[github-actions]] (building/publishing images in CI), [[secure-coding]] (image and runtime hardening).

## What a container is (and isn't)

A container is **OS-level virtualization**: the Linux kernel isolates a process with **namespaces** (its own view of the filesystem, PIDs, network, users, mounts, hostname) and limits it with **cgroups** (CPU, memory, I/O). Crucially:

- **Not a VM.** A VM virtualizes hardware and runs a full guest OS on a hypervisor; a container **shares the host kernel** and isolates at the process level. Containers are far lighter (MBs, start in ms) but offer weaker isolation than a VM (shared kernel) — see [[os-virtualization]].
- **A container = a running (or stopped) instance of an image** + a thin writable layer. The image is the read-only template; the container is the live process with its own isolated environment.
- Docker is the tooling (CLI, daemon, image format, registry protocol) around these kernel features.

## The image model

- **Images are layered.** Each instruction in a Dockerfile produces a **layer**; layers stack via a **union filesystem** into the container's root filesystem. Layers are **content-addressed and shared** across images (dedup) and **cached** on build.
- **Tags** name image versions (`app:1.2.0`, `app:latest` — avoid relying on `latest`). An image is identified by repository + tag (or digest).
- **Registries** distribute images: **Docker Hub** (default), plus private/alternative registries (ECR, GCR, GHCR). `pull` to fetch, `push` to publish, `login` to authenticate.
- The thin **writable container layer** sits atop the read-only image layers; changes there are lost when the container is removed (use **volumes** for persistence).

## Dockerfiles & image best practices

A `Dockerfile` declares how to build an image:

```dockerfile
FROM node:20-slim                  # small, pinned base
WORKDIR /app
COPY package*.json ./              # copy deps manifest first — cache-friendly
RUN npm ci --omit=dev              # cached unless manifest changes
COPY . .                           # source changes don't bust the deps layer
USER node                          # don't run as root
EXPOSE 3000
CMD ["node", "server.js"]
```

- **Order for cache** — put rarely-changing steps (deps install) before frequently-changing ones (source copy); Docker caches layers up to the first change.
- **Small bases** — `-slim`/`alpine`/distroless; fewer layers; combine related `RUN`s; use a **`.dockerignore`** to keep build context lean.
- **Multi-stage builds** — build in a heavy stage, copy only artifacts into a tiny runtime stage → small, attack-surface-minimal final images.
- **Run as non-root** (`USER`), pin versions, prefer `COPY` over `ADD`, set one concern per container, use `CMD`/`ENTRYPOINT` deliberately, add a `HEALTHCHECK`.

## Container lifecycle

```bash
docker run -d --name web -p 8080:80 nginx   # create+start (detached), publish port
docker ps [-a]                              # list running [/all]
docker logs -f web                          # stream logs
docker exec -it web sh                      # shell into a running container
docker stop web && docker rm web            # stop, then remove
docker build -t app:1.0 .                   # build an image from a Dockerfile
docker image ls / docker rmi app:1.0        # list / remove images
```

Containers are meant to be **ephemeral and cattle, not pets** — recreate rather than mutate. Set **resource limits** (`--memory`, `--cpus`) so one container can't starve the host (cgroups in action).

## Persistent state — volumes

The writable layer dies with the container, so persist data in **volumes**:

- **Bind mounts** (`-v /host/path:/container/path`) — map a host directory in; great for dev (live code), couples you to host layout.
- **Docker-managed volumes** (`-v name:/path` or `--mount`) — Docker owns the storage; portable, the right default for databases/state.
- Volumes have a **lifecycle independent of containers** (create/inspect/prune); mind **ownership/permissions** (the non-root `USER` must own mounted paths). Patterns: shared volumes between containers, data-only volume containers.

## Networking

- Docker gives containers a virtual network. Default **bridge** network with **NAT + port forwarding**: `-p host:container` publishes a container port to the host.
- Network modes: **bridge** (default, isolated virtual net), **host** (share the host's network stack — no isolation), **none** (no networking). 
- **User-defined bridge networks** are the modern default for multi-container apps: containers on the same user network reach each other **by name** (built-in DNS) — this is how Compose services talk.
- Isolation is a security boundary *and* a risk surface — don't publish ports you don't need; segment networks ([[secure-coding]]).

## Multi-container apps — Docker Compose

Define a multi-container app declaratively in `compose.yaml` and run it as a unit:

```yaml
services:
  web:
    build: .
    ports: ["8080:3000"]
    depends_on: [db]
    environment: { DATABASE_URL: postgres://db/app }
  db:
    image: postgres:16
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment: { POSTGRES_DB: app }
volumes: { pgdata: {} }
```

`docker compose up -d` / `down` / `logs` / `ps`. Compose wires a shared user network (services resolve each other by name), manages volumes, and captures the whole stack as version-controlled config — ideal for local dev and simple deployments.

## Beyond one host — orchestration

For multiple hosts, scaling, self-healing, and rolling updates you need an **orchestrator**: **Kubernetes** (the standard) or Docker Swarm. The container *image* is the portable unit across all of them. Orchestration concerns (scheduling, service discovery, scaling, health) tie into [[site-reliability-engineering]] and [[devops]]; provisioning the cluster ties to [[terraform]].

## Anti-patterns

- Running as **root**; baking **secrets** into image layers (they persist in history — use build secrets / runtime env / a secrets manager). ([[secure-coding]])
- Fat images (full OS base, build toolchain in the runtime image) — use slim bases + **multi-stage**.
- Cache-busting layer order (copying all source before installing deps).
- Relying on `:latest`; unpinned bases → non-reproducible builds.
- Storing state in the container's writable layer instead of a **volume** (data loss on `rm`).
- One container running many concerns (app + db + cron); treating containers as pets you SSH in and mutate.
- Publishing all ports / using `--network host` for convenience; no resource limits (one container OOMs the host).
- Confusing a Docker **container** with a C4/architecture "container" (different meaning — see [[software-architecture]]).

## Always-apply

1. **One concern per container**, ephemeral and reproducible; recreate, don't mutate.
2. **Small, pinned, multi-stage images**; cache-friendly layer order; `.dockerignore`; **non-root**.
3. **Volumes** for state (managed volumes by default); never persist in the writable layer.
4. **User-defined networks** + name-based discovery; publish only needed ports; set resource limits.
5. **Compose** for multi-container apps; an orchestrator (k8s) for multi-host; **no secrets in images** ([[secure-coding]]).

## Related

- [[os-virtualization]] — containers vs VMs; the virtualization spectrum.
- [[os-security]] — namespaces & cgroups, the kernel isolation mechanism.
- [[devops]] / [[terraform]] / [[ansible]] — provisioning and operating the infra containers run on.
- [[github-actions]] — building, scanning, and publishing images in CI.
- [[secure-coding]] — image hardening, secrets, least privilege, network exposure.
- [[software-architecture]] — note the terminology clash with C4 "containers."
- Source: *Docker in Action* (Jeff Nickoloff, Manning).
