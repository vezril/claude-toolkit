# Incremental kernel roadmap

A milestone-by-milestone order for building a kernel, each step small, testable in QEMU, and bootable. Each maps to the concept skill that explains the *why*. Don't skip ahead; keep it running at every step.

## Milestone 0 — It boots and prints
- Toolchain + linker script + boot handoff (GRUB/bootimage on x86-64, `-kernel` on ARM); set up stack, zero BSS.
- UART `putc`/`printf` (and VGA text on x86). **Test:** "Hello, kernel" in `-serial stdio`.
- Skill: [[osdev-kernel]] (`references/bringup.md`).

## Milestone 1 — Interrupts, exceptions, timer
- GDT+TSS (x86) / exception vectors+`VBAR_EL1` (ARM); IDT (x86) / handlers.
- Handle CPU exceptions (page fault, GP/sync) with a panic that prints registers.
- Interrupt controller (APIC / GIC) + a periodic **timer** tick; acknowledge correctly (EOI/EOIR).
- **Test:** timer ticks counted; a deliberate fault prints a useful dump.
- Skill: [[os-io-and-devices]].

## Milestone 2 — Physical memory
- Parse the memory map (Multiboot2 / bootloader / device tree).
- **Physical frame allocator** (bitmap first; buddy later). `alloc_frame`/`free_frame`.
- **Test:** allocate/free frames; no overlap with the kernel image.
- Skill: [[os-memory-and-virtual-memory]].

## Milestone 3 — Virtual memory + kernel heap
- Build your own **page tables**; map the kernel (higher-half), enable paging/MMU.
- A **kernel heap** allocator (bump → free-list/slab) so you can `kmalloc`.
- Handle page faults for legitimate cases.
- **Test:** map/unmap pages; heap allocations survive; bad access faults cleanly.
- Skill: [[os-memory-and-virtual-memory]] (+ `references/paging-and-replacement.md`).

## Milestone 4 — Tasks, context switch, scheduler
- A task/PCB struct + per-task kernel stack; a **context switch** (save/restore callee-saved regs, swap stacks; craft a fake initial frame for new tasks).
- A **round-robin scheduler** driven by the timer interrupt.
- **Test:** two kernel threads alternate; preemption works.
- Skill: [[os-processes-and-scheduling]] (+ `references/scheduling.md`).

## Milestone 5 — Synchronization
- Interrupt-safe **spinlocks**; later sleeping locks/condition variables.
- Protect scheduler/allocator/driver shared state.
- **Test:** concurrent kernel threads mutate shared state without corruption.
- Skill: [[os-concurrency]] (+ `references/synchronization-and-deadlock.md`).

## Milestone 6 — User mode + system calls
- Switch to **user mode** (ring 3 / EL0); set up a syscall entry (`syscall`/`int 0x80` on x86, `svc` on ARM).
- A minimal syscall ABI (write, exit, getpid…); **validate user pointers/args** at the boundary.
- **Test:** a tiny user program traps into the kernel and back.
- Skills: [[os-processes-and-scheduling]], [[os-security]], [[secure-coding]].

## Milestone 7 — Block device + file system
- Drive **virtio-blk** (QEMU) over your interrupt infra; a **buffer cache**.
- A simple **inode-based FS** (or ext2/FAT for tooling): superblock, bitmaps, inodes, dirs; read then write; a small redo **journal** for metadata consistency.
- **Test:** create/read/write/list files; survive a simulated crash (replay).
- Skills: [[os-io-and-devices]], [[os-file-systems-and-persistence]] (+ `references/file-system-implementation.md`).

## Milestone 8 — Loader & user space
- An **ELF loader**; run real user programs; a tiny libc/shell.
- More drivers (keyboard, console, virtio-net), `fork`/`exec`/`wait`, pipes.

## Beyond — hardening & scale
- **SMP** (bring up other cores, per-CPU run queues, finer locking).
- Demand paging / COW / swap; signals; a VFS for multiple file systems.
- Security hardening (W^X, ASLR, seccomp-like syscall filtering — [[os-security]]).
- Decide and enforce **monolithic vs microkernel** structure ([[operating-systems]]).

## Models worth reading
- **xv6** (MIT) — a tiny, complete teaching Unix in C (RISC-V or x86) — the best end-to-end model to read.
- **"Writing an OS in Rust"** (os.phil-opp.com) — x86-64 + Rust, milestone-by-milestone, mirrors this roadmap.
- **OSTEP projects** — focused exercises per subsystem.
- **osdev.org wiki** — the practical reference for every bring-up detail.
