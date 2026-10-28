---
name: finch
description: Finch — the open-source, Docker-free container development tool (runfinch.com, AWS). A thin CLI over nerdctl + containerd + BuildKit running inside a Lima-managed Linux VM on macOS/Windows, or natively as root on Linux. Covers the architecture and why it is not a Docker drop-in (no Docker socket, no Docker-in-Docker), the VM lifecycle (finch vm init/start/stop/remove/settings/disk resize, auto_vm_start), the finch.yaml configuration reference and its real schema, building with finch build (BuildKit flags, Containerfile fallback, multi-platform and Rosetta/QEMU emulation), running containers and port publishing, host-directory mounts and the security consequences, registry authentication (osxkeychain, ecr-login, finch login with ECR tokens), SOCI lazy loading, cosign signing and verification, finch compose, DevContainers via dockercompat, and diagnostics with support-bundle generate. Use when migrating off Docker Desktop, setting up or debugging Finch, writing build/run/compose commands for Finch, tuning finch.yaml, fixing finch VM/mount/registry/TLS problems, or deciding between Finch and Docker. Complements docker (the image and Dockerfile model, which Finch reuses unchanged), os-virtualization, devops, github-actions and secure-coding.
---

# Finch

**Finch is a client, not an engine.** It is a distribution of open-source parts: a Go CLI on the host that forwards most commands to **nerdctl** inside a Linux VM, where **containerd** runs the containers and **BuildKit** builds the images. **Lima** creates the VM, shares files, and forwards ports. On macOS the hypervisor is **Apple Virtualization.framework** (`vmType: vz`) or **QEMU**; on Windows it is **WSL 2**; on Linux there is no VM — Finch drives containerd on the host directly, as root.

The image format, Dockerfile language, and registry protocol are unchanged, so everything in [[docker]] about layers, caching, multi-stage builds, volumes, and networks still applies. What changes is the *plumbing*, and that is where every Finch-specific problem lives.

Cross-links: [[docker]] (the model Finch reuses), [[os-virtualization]] (VM vs container — Finch is both at once), [[devops]] / [[github-actions]] (CI), [[secure-coding]] (the VM is not a security boundary), [[dockerhub-setup]] (registry side).

## What it is not

- **No Docker daemon and no Docker socket.** Nothing binds `/var/run/docker.sock`. Any tool that talks to the Docker API, mounts the socket, or does **Docker-in-Docker** will not work. This is the single most common migration failure — check for it first.
- **Not a security boundary.** `finch vm init` says so out loud since v1.19. A container escape reaches the VM, and the VM has your home directory mounted writable (see Mounts). Treat the host as the boundary, exactly as you would with Docker Desktop.
- **Not 100% CLI-compatible.** It is nerdctl's surface, which is Docker-*like*. `finch compose` lacks some `docker compose` features (notably advanced network creation). `dockercompat: true` translates a limited set of Docker-shaped arguments and responses to nerdctl.

## The VM lifecycle

```bash
finch vm init                      # create the VM (first run; reads ~/.finch/finch.yaml)
finch vm status                    # Running / Stopped / Nonexistent
finch vm start / finch vm stop     # the restart cycle every config change needs
finch vm remove                    # destroy it (required to change Lima-level mounts)
finch vm settings --cpus 6 --memory 12GiB    # restart to take effect
finch vm disk resize --size 100GiB           # stop the VM first; grow only
```

**`auto_vm_start` defaults to true**, so any nerdctl-proxied command silently boots the VM — including `finch build --help`, because the help text itself comes from inside the VM. Commands implemented natively on the host (`finch vm *`, `finch version`, `finch --help`) never start it. If a "harmless" `--help` hangs for a minute, that is why; set `auto_vm_start: false` to make it explicit.

## Configuration — `~/.finch/finch.yaml`

(`%LocalAppData%\.finch\finch.yaml` on Windows.) **Every change needs `finch vm stop && finch vm start`.**

```yaml
cpus: 7                      # macOS only; default 0.25 × cores, min 2
memory: 24GiB                # macOS only; default 0.25 × RAM, min 2GiB
bootdisk: 100GiB             # guest OS disk; must exceed 10GiB
datadisk: 50GiB              # images/containers/volumes; must exceed 10GiB
vmType: vz                   # macOS: vz (needs macOS 13+) or qemu. Windows: wsl2 only
rosetta: false               # macOS/Apple Silicon amd64 emulation; needs vz + macOS 26+
vmnet: false                 # routable host IP; qemu needs socket_vmnet + one sudo prompt
additional_directories:
  - path: /Volumes           # NOTE the `path:` key — a bare string does not parse
snapshotters: ["soci"]       # soci | overlayfs (default overlayfs)
creds_helpers: ["ecr-login"]
dockercompat: true           # required for DevContainers
auto_vm_start: true
experimental:
  mountInotify: false        # inotify across host mounts
```

The `additional_directories` entry is a **map with a `path:` key** (`AdditionalDirectory{Path}` in the source), not the bare string some docs show. `cpus`, `memory`, disks, mounts, `rosetta` and `vmnet` are macOS-only; `snapshotters`, `creds_helpers`, `dockercompat` and `auto_vm_start` are shared.

**`vz` + virtiofs is markedly faster than `qemu` + sshfs** for mounted source trees — reach for it before blaming your build.

## Building

```bash
finch build -t app:1.0 .
finch build --platform linux/amd64,linux/arm64 -t app:1.0 .   # one tag, one row per arch
finch build -f Containerfile --target runtime --progress plain .
finch build --secret id=npmrc,src=$HOME/.npmrc --ssh default .
finch build --cache-from type=local,src=.cache --cache-to type=local,dest=.cache .
finch build --no-cache --iidfile id.txt -o type=local,dest=./out .
```

- **BuildKit must be running** in the VM; `finch build` fails without buildkitd.
- With no `Dockerfile` and no `-f`, Finch looks for **`Containerfile`**.
- `--platform` accepts bare arches (`amd64`) or full ones (`linux/amd64`); with no flag you build for the host arch only.
- `--network` for builds is `network=default|none|host`.
- `--progress plain` to see container output; `--buildkit-host` / `$BUILDKIT_HOST` to point elsewhere.
- Cross-arch runs need emulation: **Rosetta** (`vmType: vz`, Apple Silicon, macOS 26+) or QEMU otherwise. Rosetta is much faster; it is not available on macOS 15, so leave it unset or `false` there.

## Running

```bash
finch run --rm -it public.ecr.aws/docker/library/amazonlinux:latest /bin/bash
finch run -d -p 8080:80 --name web public.ecr.aws/nginx/nginx
finch exec -it web sh ; finch logs -f web ; finch ps -a ; finch stop web && finch rm web
```

Flags worth knowing beyond the Docker set: `--verify none|cosign|notation` with the `--cosign-*` options, `--pull always|missing|never`, `--runtime` (`crun`, `io.containerd.runsc.v1`), `--gpus all`, `--init` / `--init-binary` (tini), `--cgroup-conf` for cgroup v2, `--rdt-class`, `--log-driver` (`json-file` default, or `binary://<path>`). `--net`/`--network` accept a CNI network name as well as `bridge|host|none|container:<name>`.

Published host ports are forwarded by Lima and must be unique across containers.

## Mounts — and the security cost

Your home directory is mounted into the VM **writable by default**. A compromised container can therefore read and rewrite your SSH keys and registry credentials. Hardening:

- Add other paths via `additional_directories` in `finch.yaml`, then `finch vm stop && finch vm start`.
- To make the home mount read-only or remove it, edit `mounts:` in `/Applications/Finch/os/finch.yaml` (needs admin). That file is read **only at VM creation**, so apply it with `finch vm stop && finch vm remove && finch vm init`.
- On Windows the VM is the WSL distro `lima-finch` (`wsl -d lima-finch`); `.wslconfig` caps memory/processors but applies to **every** WSL 2 distro, not just Finch.

## Disk space

Disks are sparse and **grow only — they never shrink**. Inside the VM, `finch image prune [--all]` and `finch system prune` reclaim container-level space but **do not shrink the host file**. To give space back to macOS:

```bash
export LIMA_HOME=/Applications/Finch/lima/data
/Applications/Finch/lima/bin/limactl shell finch
sudo fstrim -v /mnt/lima-finch
```

## Registry authentication

Credentials live in `~/.finch/config.json` (macOS/Windows) or `/root/.docker/config.json` (Linux). `osxkeychain` is the macOS default `credsStore`; its `docker-credential-osxkeychain` binary must be on `PATH` (`/usr/local/bin`, or `brew install docker-credential-helper`). **`wincred` and `secretservice` are unsupported** and configuring them breaks auth outright.

```bash
# ECR private — tokens last 12 hours
aws ecr get-login-password --region "$AWS_REGION" \
  | finch login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
# ECR public — always us-east-1
aws ecr-public get-login-password --region us-east-1 \
  | finch login --username AWS --password-stdin public.ecr.aws
```

For hands-off ECR, set **both** halves: `creds_helpers: ["ecr-login"]` in `finch.yaml` *and* `{"credsStore": "ecr-login"}` in `config.json`, then restart the VM. It reads `~/.aws/credentials`; prefix a login with `AWS_PROFILE=…` to pick an account, after which later commands use the stored credential. ([[docker]]'s registry model otherwise applies unchanged.)

## SOCI lazy loading

SOCI starts a container before the image is fully downloaded, fetching data on demand.

```yaml
snapshotters: ["soci"]      # then finch vm stop && finch vm start
```

```bash
finch tag app:1.0 <registry>/app:1.0
finch push --snapshotter soci <registry>/app:1.0   # the INDEX is built at push time
finch run  --snapshotter soci <registry>/app:1.0
```

Layers under the `min-layer-size` (10 MiB) are skipped, so small images gain nothing. If the index is missing or unreadable Finch **silently falls back** to a full pull — measure, don't assume it worked.

## Signing

**cosign only, self-managed keys only — no keyless signing.** Signing happens at push, so tag for the destination registry first; verification needs the public key locally.

```bash
cosign generate-key-pair                                        # cosign.key + cosign.pub
finch push --sign=cosign --cosign-key cosign.key <registry>/app:1.0
finch pull --verify=cosign --cosign-key cosign.pub <registry>/app:1.0
finch run --rm --verify=cosign --cosign-key cosign.pub <registry>/app:1.0
cosign verify --key cosign.pub <registry>/app:1.0
```

In Compose, put it on the service: `x-nerdctl-sign: cosign` + `x-nerdctl-cosign-private-key: cosign.key` (applies on `compose build`/`push`), and `x-nerdctl-verify` + `x-nerdctl-cosign-public-key` (applies on `compose pull`/`run`).

## Compose

```yaml
services:
  web:
    image: app
    build: .
    ports: ["8080:3000"]
```

`finch compose up|down|build|ps|logs|exec|run|pull|push|config|cp|create|kill|pause|unpause|port|restart|rm|start|stop|top|images|version`, with `-f/--file`, `-p/--project-name`, `--project-directory`, `--env-file` and `--profile`. `up` builds a missing image first. Advanced network creation is the usual gap versus `docker compose`.

## DevContainers

Needs `dockercompat: true` in `finch.yaml`, then in the VS Code Dev Containers extension set **Docker Path** to the `finch` binary, **Docker Compose Path** to `finch compose`, and **disable Docker Credential Helper**. Export `DOCKER_COMPOSE_VERSION` above `2.9.0` — Finch only supports the `-` project-name separator, and older versions default to `_`, which mismatches names and fails startup. Also: VS Code's default names can exceed nerdctl's 76-character limit, so pin `"runArgs": ["--name", "${localWorkspaceFolderBasename}"]`. Docker-in-Docker and cached-build optimization are unsupported.

## Linux

There is no VM: Finch runs containerd on the host **as root**, so every command needs `sudo` (`sudo finch build …`, `sudo finch image list`). Use `sudo -E` when the command must see your AWS environment. Credentials go to `/root/.docker/config.json`, and the ECR helper, SOCI, and other extras come from the "optional components" install rather than `finch.yaml`.

## Troubleshooting

- **`finch support-bundle generate`** zips environment info and component logs. Produce it before filing anything.
- **Corporate TLS-inspecting proxy:** install the CA **inside the VM**, not on the host — `limactl shell finch`, drop the certs in `/etc/pki/ca-trust/source/anchors/`, run `update-ca-trust`. Host keychain trust does nothing for containerd.
- **`unrecognized system status` / "another hostagent may already be running"** means a stale Lima host agent. Stop it and `finch vm start`; `finch vm remove` + `finch vm init` is the last resort (it destroys images and volumes).
- **A config change did nothing** — you almost certainly skipped `finch vm stop && finch vm start`, or the change was a Lima-level mount needing `vm remove` + `vm init`.

## Anti-patterns

- Assuming a **Docker socket** exists: mounting `/var/run/docker.sock`, Docker-in-Docker, Testcontainers-style socket use, or any Docker-API client.
- Editing `finch.yaml` and expecting it to apply live; or writing `additional_directories: ["/Volumes/x"]` instead of `- path: /Volumes/x`.
- Treating the Finch VM as isolation, while the home directory is mounted writable.
- Running on `qemu` with large mounted source trees and blaming the build for sshfs latency.
- Setting `rosetta: true` on macOS 15 or Intel, or expecting cross-arch builds to be fast without any emulation configured.
- Expecting `datadisk` to shrink, or `finch system prune` to return space to the host.
- Enabling `soci` and assuming lazy loading happened — it falls back to a full pull without complaint.
- Reaching for cosign **keyless** signing, or `wincred`/`secretservice` credential stores.
- Pasting a `docker compose` file that relies on advanced networking and expecting parity.

## Always-apply

1. **Finch is nerdctl + containerd + BuildKit in a Lima VM.** [[docker]]'s image/Dockerfile knowledge transfers; the plumbing does not. **No Docker socket, no Docker-in-Docker.**
2. **`finch vm stop && finch vm start` after every `finch.yaml` change**; `vm remove` + `vm init` for Lima-level mounts.
3. **Prefer `vmType: vz`** on macOS 13+ (virtiofs over sshfs); Rosetta only with `vz` + Apple Silicon + macOS 26+.
4. **The VM is not a security boundary** and your home directory is mounted writable — make it read-only if you handle untrusted images ([[secure-coding]]).
5. **`sudo` everything on Linux**; credentials land in `/root/.docker/config.json`.
6. **Disks only grow.** Size `datadisk` up front; `fstrim` inside the VM to give space back to the host.
7. **Verify SOCI and signature behaviour by observation** — both fail soft.

## Related

- [[docker]] — the image model, Dockerfiles, volumes, networks and Compose semantics Finch inherits.
- [[os-virtualization]] — the VM-plus-container stack Finch actually is.
- [[secure-coding]] — the writable home mount, the non-boundary VM, image signing and verification.
- [[devops]] / [[github-actions]] — building and publishing images in CI.
- [[dockerhub-setup]] — registry repos and access tokens on the publishing side.
- Source: [runfinch.com/docs](https://runfinch.com/docs/) and the `runfinch/finch` source (config schema), verified against Finch v1.19.0.
