# Toolchain, boot & bring-up (x86-64 and AArch64)

Practical detail for getting a kernel running. References: osdev.org wiki, "Writing an OS in Rust" (os.phil-opp.com), xv6, the Multiboot2/UEFI specs.

## Toolchain

You're building **freestanding** code (no host OS/libc at runtime).

- **C**: use a **cross-compiler** for a bare ELF target (`x86_64-elf-gcc`, `aarch64-elf-gcc`; build via crosstool-ng or your distro). Compile with `-ffreestanding -nostdlib -fno-stack-protector -mno-red-zone` (x86-64) / appropriate ARM flags; you provide `_start`, `memcpy/memset`, etc. Link with a **custom linker script** (`-T kernel.ld`) that places sections (`.text/.rodata/.data/.bss`) and sets the entry point and load address.
- **Rust**: `#![no_std]` + `#![no_main]`, a **custom target spec** (or `aarch64-unknown-none` / `x86_64-unknown-none`), `panic = "abort"`, build with `build-std` (cargo, nightly) or `bootimage`/`cargo-binutils`. You define `_start`/`#[no_mangle]` entry and a `#[panic_handler]`. The `bootloader`/`bootimage` crates handle x86-64 boot; for ARM you use QEMU `-kernel`.
- **Linker script** essentials: entry symbol, base/load address (e.g. higher-half `0xffffffff80000000` once paging is on; a physical load address before), section layout, and symbols for the kernel start/end and the BSS to zero.

## Boot — x86-64

x86 boots in 16-bit **real mode**; getting to 64-bit **long mode** is the legacy obstacle course. Two sane options:

1. **Use a bootloader (recommended).**
   - **GRUB + Multiboot2**: mark your kernel with a Multiboot2 header; GRUB loads your ELF, switches to 32-bit protected mode, and jumps to your entry with a known machine state and a pointer to boot info (memory map, modules, framebuffer). You then set up a GDT, initial page tables, and switch to long mode.
   - **Limine** / Rust **`bootloader`/bootimage**: modern loaders that can hand you a 64-bit long-mode environment, a memory map, and a framebuffer directly — less assembly.
2. **Write your own** MBR/stage1+stage2 (educational, fiddly): 512-byte boot sector → load more → enable A20 → GDT → protected mode → paging → long mode.

After handoff: build a real **GDT** (flat code/data + TSS for stack switching), an **IDT** for interrupts/exceptions, remap or disable the legacy **PIC** (prefer the **APIC**/x2APIC), and set up paging (4-level; CR3).

## Boot — AArch64 (cleaner)

QEMU's `virt` board (or a Raspberry Pi) starts your image at a defined entry, typically in **EL2** or **EL1**, MMU **off**, caches cold. Bring-up:
- Set up the **stack pointer**, zero **.bss**, (optionally drop EL2→EL1).
- Install the **exception vector table** and point `VBAR_EL1` at it (16 entries: sync/IRQ/FIQ/SError × from-EL levels).
- Configure the **MMU**: build translation tables, set `MAIR_EL1` (memory attributes), `TCR_EL1` (granule/size), `TTBR0_EL1`/`TTBR1_EL1` (user/kernel split), then enable via `SCTLR_EL1`.
- Interrupt controller is the **GIC**; the timer is the architected **generic timer** (`CNTP_*`). Devices are discovered via the **device tree** QEMU passes in.

ARM64 has far less legacy ceremony — a good first target.

## Running & debugging in QEMU

- x86-64: `qemu-system-x86_64 -cdrom os.iso` (GRUB image) or `-kernel kernel.elf`; `-serial stdio` (UART output), `-d int,guest_errors`, `-no-reboot -no-shutdown`.
- AArch64: `qemu-system-aarch64 -M virt -cpu cortex-a72 -kernel kernel.elf -serial stdio -nographic`.
- **GDB**: add `-s -S` (listen on :1234, halt at start), then `gdb kernel.elf` → `target remote :1234` → set breakpoints, step source. Indispensable.
- **virtio** devices in QEMU (`virtio-blk`, `virtio-net`, `virtio-gpu`, `virtio-console`) are simple ring-buffer interfaces — vastly easier to drive than emulated real hardware. Start with virtio.

## Early output (your first `printf`)

- **Serial/UART**: x86-64 the legacy **16550 UART** at I/O port `0x3F8` (init line control, poll the THR-empty bit, write bytes) → shows up in `-serial stdio`. ARM: the PL011 UART (`virt` board) at a known MMIO address.
- x86-64 also: the **VGA text buffer** at physical `0xB8000` (80×25, 2 bytes/char) for on-screen output.
Wire `printf`/formatting to the UART first — it's your lifeline before a real console exists.

## Common pitfalls

- Forgetting to zero **.bss** or set up a stack before running C/Rust.
- Wrong **linker addresses** (load vs virtual) when going higher-half; map the kernel before jumping to virtual addresses.
- Treating MMIO as cacheable, or missing **memory barriers** on ARM.
- Not acknowledging interrupts (PIC EOI / GIC EOIR) → interrupt storms.
- Red zone enabled on x86-64 kernel code (`-mno-red-zone`) corrupting state in interrupt handlers.
