---
name: os-virtualization
description: Machine virtualization and containers — running whole operating systems or isolated workloads on top of a host. Covers hypervisors (type-1/bare-metal vs type-2/hosted), the classic trap-and-emulate model and the Popek-Goldberg requirements, why x86 was historically hard to virtualize and the fixes (binary translation, paravirtualization, hardware-assisted virtualization via Intel VT-x/AMD-V), CPU/memory virtualization (shadow page tables vs nested paging/EPT, the IOMMU for device passthrough), and OS-level virtualization / containers (Linux namespaces + cgroups, vs VMs). Use when reasoning about VMs/hypervisors/containers, isolation and density trade-offs, how a guest OS is virtualized, or designing/deploying virtualized or containerized systems. Part of the operating-systems skill set; note this is MACHINE virtualization (distinct from OSTEP's use of "virtualization" for an OS virtualizing the CPU/memory, which is covered by os-processes-and-scheduling and os-memory-and-virtual-memory).
---

# Machine Virtualization & Containers

Running **whole operating systems** (VMs) or **isolated workloads** (containers) on top of a host — the layer *above* a single OS. Part of the [[operating-systems]] set.

> **Terminology note:** OSTEP uses "virtualization" for how a single OS virtualizes the **CPU** and **memory** for its processes — that material lives in [[os-processes-and-scheduling]] and [[os-memory-and-virtual-memory]]. *This* skill is about **machine virtualization**: virtualizing the whole computer so multiple OSes/containers share it.

## Hypervisors (the VMM)

A **hypervisor / virtual machine monitor (VMM)** runs guest OSes, each believing it owns the hardware:
- **Type-1 (bare-metal)** — runs directly on hardware (Xen, VMware ESXi, Microsoft Hyper-V, KVM-as-hypervisor). Best performance/isolation; the cloud standard.
- **Type-2 (hosted)** — runs as an app on a host OS (VirtualBox, VMware Workstation, QEMU/KVM on Linux, Parallels). Convenient for desktops/dev.

The VMM must give each guest the **illusion of real hardware** while keeping guests isolated and the host in control — the same "virtualize + protect" job an OS does for processes, one level up.

## How CPU virtualization works

Classic technique: **trap-and-emulate** — run guest code directly on the CPU, but run the guest in a de-privileged mode so its **privileged instructions trap** into the VMM, which emulates them. This requires (per **Popek & Goldberg**) that all *sensitive* instructions be *privileged* (so they trap). **x86 historically violated this** — some sensitive instructions didn't trap when run unprivileged — which made it "not classically virtualizable." Fixes:
- **Binary translation** (VMware's original approach) — rewrite guest kernel instruction streams on the fly to be safe.
- **Paravirtualization** (Xen's original approach) — modify the guest OS to call the hypervisor (**hypercalls**) instead of executing the problematic instructions; faster but needs guest cooperation.
- **Hardware-assisted virtualization** (**Intel VT-x / AMD-V**) — a new CPU mode (root/non-root, VMX) lets guests run privileged code directly and trap to the VMM cleanly via VM-exits. The modern default; binary translation/paravirt are largely obsolete for the CPU.

## Memory & device virtualization

- **Memory**: the guest has its own page tables (guest-virtual → guest-physical), but guest-physical must map to **host-physical**. Two approaches: **shadow page tables** (the VMM maintains combined tables the MMU actually uses — correct but expensive to keep in sync) and **nested/extended page tables** (**EPT/NPT** — hardware does the second-level translation, far faster; the standard today).
- **Devices**: emulate real devices (compatible but slow), use **paravirtualized** devices (**virtio** — a fast guest/host ring-buffer interface; what you'll use in QEMU/KVM), or **pass through** real hardware to a guest using the **IOMMU** (VT-d/SMMU) for safe DMA remapping (near-native I/O, e.g. GPU/NIC passthrough).

## OS-level virtualization (containers)

Instead of running a whole guest kernel, **containers** isolate processes within the **host kernel** — much lighter (no guest OS, near-instant start, higher density), at the cost of weaker isolation (shared kernel = larger attack surface). On Linux they're built from:
- **Namespaces** — per-process isolated views of kernel resources: PID, mount (filesystem), network, UTS (hostname), IPC, user, cgroup. A container "sees" only its own processes/mounts/network.
- **cgroups (control groups)** — limit/account resource usage (CPU, memory, I/O, PIDs) per group.
- Plus a layered/union filesystem (overlayfs) for images. Docker/containerd/Podman/Kubernetes orchestrate these.

**VM vs container**: VMs give strong, kernel-level isolation and run different OSes, at higher overhead; containers give lightweight, dense, fast isolation sharing one kernel. Hybrids (Firecracker microVMs, gVisor, Kata) chase "container speed, VM isolation." This connects directly to deployment of [[akka]]/[[akka-sdk]] services (typically containerized on Kubernetes — see [[akka-management]]).

## Always-apply notes

- For *running* a hobby OS, you'll use a **type-2 hypervisor/emulator (QEMU)**, ideally with **KVM** acceleration, and **virtio** devices — far easier than real hardware ([[osdev-kernel]]).
- Choose VMs for strong isolation / different OSes / untrusted multi-tenant; containers for density, fast startup, and same-kernel microservices.
- Nested paging (EPT/NPT) + virtio + IOMMU passthrough are the performance levers; emulated everything is the slow path.

## Related

- [[operating-systems]] (map) · [[os-memory-and-virtual-memory]] & [[os-processes-and-scheduling]] (the *single-OS* CPU/memory virtualization sense) · [[os-io-and-devices]] (virtio, IOMMU) · [[osdev-kernel]] (running your kernel under QEMU/KVM).
- [[akka-management]], [[akka-sdk]] — containerized/k8s deployment of services on top of this.
- Sources: Tanenbaum Ch. 7 (Virtualization and the Cloud); Silberschatz Ch. 18 (Virtual Machines); OSTEP (the CPU/memory-virtualization sense, in the Virtualization pieces).
