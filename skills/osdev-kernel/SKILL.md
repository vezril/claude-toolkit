---
name: osdev-kernel
description: Hands-on OS / kernel development — actually writing an operating system from scratch. Covers the toolchain (cross-compiler, freestanding C / Rust no_std, linker scripts, building a bootable image), the boot process (BIOS/MBR vs UEFI, bootloaders, multiboot/GRUB, getting into 64-bit/long mode or ARM EL1), running and debugging in QEMU with GDB, and the kernel bring-up sequence (early output, the interrupt/exception table, a timer, physical & virtual memory, processes/context switch/scheduler, system calls, device drivers via virtio, then a file system), with an incremental roadmap. Arch-agnostic with x86-64 and AArch64/ARM notes, in C or Rust. Use when building a hobby/teaching OS or kernel, bootstrapping bare-metal code, setting up an osdev toolchain/QEMU, or implementing kernel subsystems. The practical companion to the operating-systems concept skills.
---

# Writing a Kernel (osdev)

The **practical** path to building an operating system — the part the textbooks ([[operating-systems]] and its subsystem skills) don't walk you through: the toolchain, the boot process, getting bare-metal code running in an emulator, and the order to build a kernel up. **Arch-agnostic** with **x86-64** and **AArch64 (ARM64)** notes; in **C** or **Rust** (both are first-class kernel languages — Rust adds memory safety, see [[functional-programming]]/[[secure-coding]]). Lean on the [[operating-systems]] subsystem skills for the algorithms behind each step.

Reference detail: **`references/bringup.md`** (toolchain, boot, the bring-up sequence per arch) and **`references/roadmap.md`** (the incremental milestone order, with what to build and which skill backs it).

## The mindset

- **Start absurdly small and always-runnable.** First goal: a kernel that boots in **QEMU** and prints one character. Grow one capability at a time, keeping it bootable. Never "big-bang" a kernel.
- **You're writing freestanding code** — no OS, no libc, no `main` runtime. The compiler must target a **bare-metal** environment (`-ffreestanding`, no stdlib; Rust **`#![no_std]` + `#![no_main]`**). You bring your own startup, memory, and (eventually) everything.
- **Emulate first.** Develop against **QEMU** (+ **GDB** for source-level debugging, and serial/UART for `printf`) before ever touching real hardware. QEMU's **virtio** devices are far simpler to drive than real ones.
- **Pick one architecture to start.** x86-64 has the most tutorials but messy legacy boot (real mode → protected → long mode); **AArch64** is cleaner (boots into a defined exception level, simple to bring up on QEMU's `virt` board, fits an Apple/ARM leaning). Don't try to be portable on day one.

## Toolchain & boot (summary)

- **Cross-compiler**: build/use a toolchain targeting your bare-metal triple (`x86_64-elf-gcc` or `aarch64-elf-gcc`; or Rust with a custom target JSON / `aarch64-unknown-none`). You need a **linker script** to lay out sections and set the load/entry addresses, and to produce an ELF/flat binary the loader understands.
- **Boot (x86-64)**: either use a bootloader that does the heavy lifting — **GRUB + the Multiboot2 spec** (GRUB loads your ELF and hands off in protected mode with a known state) or a modern crate like **Limine/bootimage** — or write your own MBR/stage loader. Then you switch real→protected→**long mode**, set up a GDT and initial paging.
- **Boot (AArch64)**: firmware/QEMU drops you at the kernel entry in a known **exception level (EL1/EL2)** with an MMU off; set up the stack, exception vector table (`VBAR_EL1`), and page tables (`TTBR0/1`). Much less ceremony than x86.
- **Run**: `qemu-system-x86_64`/`qemu-system-aarch64` with `-kernel`/`-drive`, `-serial stdio`, `-s -S` to wait for GDB. Iterate in seconds.

## The kernel bring-up sequence (and the skill behind each)

Build in roughly this order — each step is small and testable (full roadmap in `references/roadmap.md`):

1. **Boot + early console** — get to your kernel's entry, set up a stack, and print via **UART/serial** (and VGA text on x86). *Hello from the kernel.*
2. **Interrupts & exceptions** — install the **IDT** (x86) / exception vectors (ARM), handle faults, set up the interrupt controller (PIC/APIC, or GIC on ARM), and a **timer** tick. *Now you can preempt and react.* ([[os-io-and-devices]])
3. **Physical memory** — parse the memory map (from the bootloader/firmware), build a **physical frame allocator** (bitmap or buddy). ([[os-memory-and-virtual-memory]])
4. **Virtual memory** — set up your own **page tables**, map the kernel (often higher-half), enable paging/MMU, and a **kernel heap allocator**. ([[os-memory-and-virtual-memory]])
5. **Processes & scheduling** — a task/PCB, a **context switch** routine (save/restore registers, swap stacks), and a simple **round-robin scheduler** driven by the timer. ([[os-processes-and-scheduling]])
6. **Synchronization** — kernel locks (interrupt-safe spinlocks), since interrupts and (later) multiple cores race on kernel data. ([[os-concurrency]])
7. **System calls & user mode** — a syscall entry, switching to **user mode**, and the user/kernel trust boundary (validate args!). ([[os-security]], [[secure-coding]])
8. **Device drivers** — a **virtio-blk** block device and **virtio-net** / keyboard, on top of your interrupt infrastructure. ([[os-io-and-devices]])
9. **File system** — a simple inode-based FS (or adopt ext2/FAT) over the block device, with a buffer cache. ([[os-file-systems-and-persistence]])
10. Then: an ELF **loader** + a tiny user-space, more drivers, SMP, and hardening.

## Always-apply notes

- Keep it bootable at every commit; add capabilities incrementally; test each in QEMU before moving on.
- Use **GDB + QEMU** and serial logging relentlessly — bare-metal debugging without them is brutal.
- Decide **monolithic vs microkernel** early ([[operating-systems]]) — it shapes whether drivers/FS live in-kernel or as user servers.
- In **Rust**, `#![no_std]` + a custom target gets you safety and a real type system in the kernel; isolate the genuinely-unsafe bits (MMIO, asm, page tables) behind small `unsafe` blocks ([[secure-coding]]).
- Lean on real references: **osdev.org wiki**, **Philipp Oppermann's "Writing an OS in Rust"** (x86-64/Rust), **OSTEP's projects** and **xv6** (a tiny teaching Unix, C, RISC-V/x86) as a model to read, and the three textbooks for the *why* behind each subsystem.
- Don't reinvent the bootloader first — use GRUB/Limine (x86) or QEMU's `-kernel` (ARM) and focus your effort on the kernel itself.

## Related

- [[operating-systems]] — the concept map; each bring-up step maps to a subsystem skill.
- [[os-io-and-devices]], [[os-memory-and-virtual-memory]], [[os-processes-and-scheduling]], [[os-concurrency]], [[os-file-systems-and-persistence]], [[os-security]] — the algorithms behind each kernel subsystem.
- [[os-virtualization]] — running your kernel under QEMU/KVM and virtio.
- [[secure-coding]], [[functional-programming]] — safe systems programming, especially in Rust.
- References: `references/bringup.md` (toolchain/boot/bring-up per arch), `references/roadmap.md` (milestone order). External: osdev.org, "Writing an OS in Rust" (os.phil-opp.com), xv6, OSTEP projects.
