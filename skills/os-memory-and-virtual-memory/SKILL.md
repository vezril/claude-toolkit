---
name: os-memory-and-virtual-memory
description: Operating-system memory management and virtual memory — virtualizing memory so each process sees a private linear address space. Covers the address-space abstraction, address translation, base-and-bounds and segmentation, paging (page tables, the page-table entry, multi-level and inverted page tables), the TLB and translation caching, free-space management/allocators (free lists, buddy, slab; fragmentation), and demand paging with page-replacement policies (FIFO, LRU/clock/approx-LRU, optimal/Belady), the working-set model and thrashing. Use when reasoning about how memory is virtualized and protected, designing paging/MMU handling or an allocator in a kernel, or understanding TLBs, page faults, swapping, and replacement. Part of the operating-systems skill set (memory virtualization); see operating-systems for the map and osdev-kernel for implementation.
---

# Memory & Virtual Memory

How an OS **virtualizes memory**: each process gets a private, large, contiguous-looking **virtual address space**, while the OS+MMU map it onto (scarce, shared, fragmented) physical RAM and disk — transparently, efficiently, and with protection. Part of the [[operating-systems]] set; implementation in [[osdev-kernel]].

## The address space & translation

A process's **address space** is its view of memory: code, then heap (grows up), with the stack growing down from the top. The OS gives each process its own, so addresses are **virtual** and must be **translated** to physical on every access — done by hardware (the **MMU**) using tables the OS sets up. Goals: **transparency** (programs think they own memory), **efficiency** (hardware translation, TLB), **protection/isolation** (a process can't touch another's memory or the kernel's).

**Early schemes**: **base-and-bounds** (add a base register, check a bound — relocation + protection, but one contiguous chunk) → **segmentation** (a base+bound per logical segment: code/heap/stack — supports sparse spaces and sharing, but causes **external fragmentation**).

## Paging — the dominant scheme

Divide the virtual address space into fixed-size **pages** and physical memory into **frames** (e.g. 4 KiB). A **page table** per process maps virtual page number → physical frame number; the virtual address splits into `[VPN | offset]`, the offset passes through untouched. This eliminates external fragmentation (only internal, within the last page) and makes sparse address spaces cheap.

**Page-table entry (PTE)** holds the frame number plus bits: **valid/present**, **protection** (r/w/x), **user/supervisor**, **accessed (referenced)**, **dirty**, and cache/global bits. Page tables are big, so:
- **Multi-level page tables** (a tree; e.g. x86-64's 4–5 levels) — only allocate page-table pages that are needed; the MMU walks the levels.
- **Inverted page tables** — one entry per physical frame instead of per virtual page (scales with RAM, not address-space size); needs a hash to look up.

**The TLB** (Translation Lookaside Buffer) caches recent VPN→PFN translations so most accesses skip the page-table walk; it relies on locality and is the thing that makes paging fast. A **TLB miss** triggers a walk (hardware- or software-managed); a **context switch** must flush or tag (ASID/PCID) the TLB so stale translations don't leak between processes.

## Free-space management (allocators)

Managing variable-size requests (the heap, `malloc`, kernel object allocation): **free lists** with policies (first-fit/best-fit/worst-fit), **coalescing** adjacent free blocks, **splitting**, headers/footers (boundary tags). **External vs internal fragmentation**. Common kernel allocators: the **buddy allocator** (power-of-two blocks, fast split/merge — typical for the physical page allocator) and the **slab allocator** (caches of fixed-size objects — avoids fragmentation and init cost for frequently-allocated kernel structures). Detail of replacement (the *paging* side) is in `references/paging-and-replacement.md`.

## Demand paging, replacement & thrashing

See **`references/paging-and-replacement.md`**. Briefly: pages are loaded **on demand** (a **page fault** on first/absent access; the handler fetches from disk/backing store and resumes). When memory is full, a **replacement policy** chooses a victim to evict (write back if **dirty**). **LRU** is the ideal-ish target, approximated cheaply by the **clock algorithm** using the accessed bit; **Belady's optimal** (evict the page used farthest in the future) is the unbeatable baseline. Over-committing memory so the working sets don't fit causes **thrashing** (constant paging, throughput collapse) — managed via the **working-set model** and admission control.

## Always-apply notes (for implementation)

- The kernel must run with paging configured early ([[osdev-kernel]]): identity-map or higher-half map itself, set up a **physical frame allocator** (bitmap or buddy) and a **kernel heap**, then per-process page tables.
- On x86-64, CR3 holds the top-level table; on AArch64, TTBR0/TTBR1 split user/kernel — switching address spaces means changing those and managing TLB invalidation (ASIDs avoid full flushes).
- Always set protection bits correctly (NX for non-code, supervisor for kernel pages) — this is half of [[os-security]] and [[secure-coding]] memory safety at the hardware level.
- Page faults are normal (demand paging, copy-on-write, growing the stack) — distinguish them from invalid accesses (segfault) in the fault handler.

## Related

- [[operating-systems]] (map) · [[os-processes-and-scheduling]] (the address space swapped on context switch) · [[os-io-and-devices]] (the backing store / swap) · [[osdev-kernel]] (MMU/paging/allocator implementation).
- [[secure-coding]] — page protection + memory-safety; [[os-security]] — isolation via the MMU.
- `references/paging-and-replacement.md` — demand paging and replacement policies in depth.
- Sources: OSTEP (Virtualization: address spaces, segmentation, paging, TLBs, multi-level tables, swapping/replacement); Silberschatz Ch. 9–10; Tanenbaum Ch. 3.
