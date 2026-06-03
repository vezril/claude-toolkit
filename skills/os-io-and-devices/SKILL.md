---
name: os-io-and-devices
description: Operating-system I/O and device management — how the OS talks to hardware. Covers the device model (registers, status/command/data; memory-mapped I/O vs port I/O), the three ways to interact with devices (polling, interrupts, DMA) and their trade-offs, the interrupt mechanism (IRQs, interrupt vectors/handlers, top vs bottom halves), device drivers and the layered I/O software stack, the block vs character device distinction, and storage-device characteristics (HDD geometry/seek/rotation, SSD/flash, the FTL, wear leveling, TRIM). Use when reasoning about how an OS communicates with hardware, writing a device driver or interrupt handler in a kernel, choosing polling vs interrupts vs DMA, or understanding HDD/SSD performance. Part of the operating-systems skill set; see operating-systems for the map, os-file-systems-and-persistence for the storage layer above, and osdev-kernel for implementation.
---

# I/O & Devices

How the OS communicates with hardware and abstracts wildly different devices behind uniform interfaces. Part of the [[operating-systems]] set; the storage/file-system layer above is [[os-file-systems-and-persistence]]; implementation is [[osdev-kernel]].

## The device model

A device exposes **registers** the OS reads/writes: a **status** register (is it busy/ready/error?), a **command** register (tell it what to do), and **data** registers (transfer data). Two ways the CPU reaches them:
- **Port-mapped I/O (PIO)** — a separate I/O address space accessed with special instructions (x86 `in`/`out`).
- **Memory-mapped I/O (MMIO)** — device registers appear at physical memory addresses; ordinary loads/stores (uncached) access them. The norm on modern systems and on ARM. (Mark those pages uncacheable.)

The generic protocol: spin until **not busy** → write parameters to data/command registers → start the command → wait for **completion** → read result. The "wait" is what the three interaction styles differ on.

## Polling vs interrupts vs DMA

- **Polling (programmed I/O)** — the CPU repeatedly reads the status register until ready. Simple and lowest-latency for very fast devices, but **burns CPU** waiting; bad for slow devices.
- **Interrupts** — the device raises an **IRQ** when done; the CPU runs other work meanwhile and is notified asynchronously. Far better CPU utilization for slow/variable-latency devices. Cost: an interrupt has overhead (context save, handler) — for very high-rate devices, interrupts can **livelock** the CPU, so drivers use **interrupt coalescing** or switch to polling under load (e.g. NAPI in networking). A hybrid (poll briefly, then enable interrupts) is common.
- **DMA (Direct Memory Access)** — a DMA engine transfers data between device and memory **without the CPU** copying each byte; the CPU sets up the transfer (address, length) and gets one interrupt at completion. Essential for bulk transfer (disk, network) — frees the CPU and the memory bus does the work.

Rule of thumb: **PIO for tiny/fast transfers, interrupts to avoid busy-waiting, DMA for bulk data.**

## Interrupts in the kernel

The CPU has an **interrupt vector table** (x86 IDT / ARM exception vectors) mapping interrupt/exception numbers to handlers. On an interrupt: the CPU saves minimal state, switches to kernel mode, and jumps to the handler. Handlers must be fast and careful:
- **Top half / bottom half** split (a.k.a. ISR + deferred work / softirq / tasklet / workqueue): do the bare minimum in the interrupt handler (acknowledge the device, grab data), and defer heavy processing to a schedulable context with interrupts enabled.
- **Concurrency**: data shared with an interrupt handler needs interrupt-disabling or interrupt-safe spinlocks; **never sleep in an interrupt handler** (see [[os-concurrency]]).
- Distinguish **interrupts** (asynchronous, from devices), **exceptions/faults** (synchronous CPU-detected: page fault, divide-by-zero), and **traps/syscalls** (deliberate). The **timer interrupt** is what enables preemptive scheduling ([[os-processes-and-scheduling]]).

## Drivers & the I/O software stack

A **device driver** encapsulates device-specific code behind a generic interface, so the rest of the OS doesn't care about the model of disk/NIC. Layers (top to bottom): **user-level I/O (libraries)** → **device-independent OS layer** (naming, buffering, the block/char abstraction, the buffer cache) → **device drivers** → **interrupt handlers** → **hardware**. Devices split into **block devices** (addressable fixed-size blocks, random access, buffered — disks) and **character devices** (byte streams — keyboards, serial, mice). Most kernel code (the majority of Linux) is drivers, and they're the most bug-prone part — keep them simple and well-isolated (a microkernel runs them in user space; see [[operating-systems]]).

## Storage device characteristics (matters for performance)

- **Hard disk (HDD)** — spinning platters + moving head; access time = **seek time** (move the head) + **rotational latency** (wait for the sector) + transfer. Sequential ≫ random; this drives **disk scheduling** (SCAN/elevator) and on-disk locality (FFS block groups) — see [[os-file-systems-and-persistence]].
- **SSD / flash** — no moving parts; fast random reads. But flash can't overwrite in place (erase whole **blocks**, write **pages**), so an **FTL (Flash Translation Layer)** maps logical→physical, does **wear leveling** (spread writes to extend lifespan) and **garbage collection**, causing **write amplification**. **TRIM** lets the FS tell the SSD which blocks are free. Log-structured designs (LFS) suit flash well.

## Always-apply notes (for implementation)

- Bring-up order in a kernel ([[osdev-kernel]]): set up the **interrupt/exception table** and a **timer** first (you need the timer for scheduling and interrupts for everything non-trivial), a **UART/serial** driver for debugging output, then a **keyboard** and a **block device** (e.g. virtio-blk on QEMU) to back a file system.
- On QEMU, **virtio** devices (virtio-blk, virtio-net, virtio-console) are far simpler to drive than emulating real hardware — start there.
- Keep ISRs minimal; defer work; protect shared data from handler races; use MMIO with uncached mappings and the right memory barriers (especially on ARM).

## Related

- [[operating-systems]] (map) · [[os-file-systems-and-persistence]] (the storage stack above block devices) · [[os-processes-and-scheduling]] (timer interrupt → preemption) · [[os-concurrency]] (interrupt-safe synchronization) · [[osdev-kernel]] (writing drivers & interrupt handlers).
- Sources: OSTEP (Persistence: I/O devices, HDDs, flash/SSDs); Silberschatz Ch. 12; Tanenbaum Ch. 5.
