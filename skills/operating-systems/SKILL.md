---
name: operating-systems
description: Operating systems — the meta/overview skill for OS concepts and for writing one, distilled from OSTEP (Arpaci-Dusseau, primary), Silberschatz's *Operating System Concepts*, and Tanenbaum's *Modern Operating Systems*. Explains what an OS does (the three pillars — virtualizing the CPU & memory, concurrency, and persistence), kernel architectures (monolithic, microkernel, hybrid, exokernel/unikernel), the mechanism-vs-policy split, and the core machinery every OS rests on (dual-mode execution, system calls, traps, interrupts, the boot sequence) — then routes to the per-subsystem skills and the hands-on kernel skill. Use as the entry point for any OS question, when studying or reasoning about OS behavior, deciding which subsystem a problem belongs to, or planning/writing an operating system or kernel. From any OS task, defer to the specific subsystem skill (or osdev-kernel) for detail.
---

# Operating Systems (overview / meta)

An operating system is the software between programs and hardware: it **virtualizes** physical resources into easy-to-use abstractions, manages **concurrency**, and stores data **persistently** — while protecting programs from each other and the hardware from programs. This is the map skill; for real depth, **read the specific subsystem skill** below, and for building one, the hands-on **[[osdev-kernel]]** skill.

Primary source is **OSTEP** (*Operating Systems: Three Easy Pieces*, free at ostep.org) — the most practical of the three — with **Silberschatz** (*Operating System Concepts*) and **Tanenbaum** (*Modern Operating Systems*) for breadth, extra depth, and real-system case studies (Linux/Windows/Android). Cross-links: [[functional-programming]], [[akka]] (the message-passing alternative to shared-memory concurrency), [[secure-coding]], [[cryptography]], [[information-theory]].

## The three pillars (OSTEP's organizing idea)

1. **Virtualization** — the OS gives each program the illusion of having the whole machine: its own **CPU** (time-sharing many processes) and its own large private **memory** (virtual address spaces). See [[os-processes-and-scheduling]] and [[os-memory-and-virtual-memory]].
2. **Concurrency** — running things at once (threads, interrupts) correctly, with locks, condition variables, semaphores, and deadlock avoidance. See [[os-concurrency]].
3. **Persistence** — storing data durably across crashes and power loss, through devices and file systems. See [[os-io-and-devices]] and [[os-file-systems-and-persistence]].

Plus, at the layer above the bare machine: **[[os-virtualization]]** (running whole OSes/containers on a hypervisor) and **[[os-security]]** (protection and isolation).

## Foundational machinery (every OS uses these)

- **Dual-mode execution** — the CPU runs in **kernel (privileged) mode** or **user mode**; privileged instructions (I/O, changing the page table, disabling interrupts) trap if attempted in user mode. This hardware boundary is what makes protection possible.
- **System calls** — user programs request OS services (read, write, fork, mmap) via a controlled **trap** into the kernel that switches to kernel mode at a fixed entry point. The syscall interface is the OS's API.
- **Traps & interrupts** — a **trap** is a synchronous entry to the kernel (syscall, fault, exception); an **interrupt** is asynchronous (timer, device). The **timer interrupt** is what lets the OS regain control to time-share the CPU (the "limited direct execution" trick: run user code directly, but keep a tripwire).
- **Mechanism vs policy** — separate *how* something is done (mechanism: context switch, page table) from *what to do* (policy: which process to run, which page to evict). Good OS design keeps them independent so policy can change without rewriting mechanism.
- **Boot sequence** — firmware (BIOS/UEFI) → bootloader → kernel, which initializes itself and starts the first user process. Detail in [[osdev-kernel]].

## Kernel architectures

- **Monolithic** (Linux, classic Unix) — all OS services in one kernel address space; fast, but large and tightly coupled.
- **Microkernel** (MINIX, seL4, QNX) — minimal kernel (IPC, scheduling, low-level memory); drivers/file systems/etc. run as user-space servers communicating by messages. More robust/isolated, historically slower (IPC cost). This is the **message-passing** philosophy that [[akka]]'s actor model shares at the application level.
- **Hybrid** (Windows NT, macOS/XNU) — a pragmatic blend.
- **Exokernel / unikernel / library OS** — push abstraction out of the kernel, or compile the app+OS into one image.

## The subsystem map — which skill to read

- **[[os-processes-and-scheduling]]** — processes, threads, context switching, and CPU scheduling. *Virtualizing the CPU.*
- **[[os-memory-and-virtual-memory]]** — address spaces, paging, the TLB, page replacement. *Virtualizing memory.*
- **[[os-concurrency]]** — locks, semaphores, monitors, classic problems, deadlock. *Doing many things correctly at once.*
- **[[os-file-systems-and-persistence]]** — files, inodes, file-system implementation, RAID, crash consistency. *Storing data durably.*
- **[[os-io-and-devices]]** — interrupts vs polling, DMA, device drivers, the storage stack. *Talking to hardware.*
- **[[os-virtualization]]** — hypervisors and containers. *Running OSes/isolated workloads on top.*
- **[[os-security]]** — protection, isolation, the OS attack surface. *Keeping it all safe.*
- **[[osdev-kernel]]** — the hands-on path to actually building a kernel (boot, toolchain, bring-up, drivers, then the subsystems above).

## Writing an OS — how to use these skills

A sensible build order (each step maps to a skill): get a kernel **booting** and printing (toolchain + boot, [[osdev-kernel]]) → handle **interrupts/exceptions and a timer** ([[os-io-and-devices]], [[osdev-kernel]]) → set up **virtual memory / paging** and a physical+kernel allocator ([[os-memory-and-virtual-memory]]) → add **processes, context switching, and a scheduler** ([[os-processes-and-scheduling]]) → add **synchronization** for the kernel ([[os-concurrency]]) → add **system calls** and a user/kernel boundary → add **device drivers** and a **file system** ([[os-io-and-devices]], [[os-file-systems-and-persistence]]) → harden ([[os-security]]). Start tiny, run in **QEMU**, and grow incrementally.

## Always-apply notes

- This is a **router** — defer to the subsystem skill for algorithms and detail; don't try to recall everything here.
- Prefer OSTEP's framing and worked intuition; reach to Silberschatz/Tanenbaum for breadth and case studies.
- Concurrency at the OS level is shared-memory and lock-based; contrast with the message-passing model in [[akka]] / [[functional-programming]] (immutability removes whole classes of races).

## Related

- The eight OS skills above.
- [[akka]], [[functional-programming]] — message-passing & immutability as alternatives to shared-memory concurrency.
- [[secure-coding]], [[cryptography]], [[information-theory]] — security, crypto, and the entropy/coding theory that storage and channels rely on.
- Sources: *Operating Systems: Three Easy Pieces* (Arpaci-Dusseau, ostep.org, primary); *Operating System Concepts* (Silberschatz, Galvin, Gagne, 10th ed.); *Modern Operating Systems* (Tanenbaum, 4th ed.).
