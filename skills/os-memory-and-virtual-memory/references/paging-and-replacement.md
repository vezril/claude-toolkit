# Demand paging & page replacement

OSTEP (Swapping: mechanisms & policies) · Silberschatz Ch. 10 · Tanenbaum Ch. 3.

## Demand paging mechanism

Not all of a process's pages are in RAM. A PTE marked **not present** triggers a **page fault** on access; the fault handler:
1. Checks the access is legal (in the address space, right permissions) — else deliver a fault/segfault.
2. Finds a free frame (or evicts one — see replacement).
3. Reads the page from its **backing store** (swap, or the file for memory-mapped/file pages), updates the PTE to present, and restarts the faulting instruction.

This enables programs larger than RAM, fast startup (load on demand), **copy-on-write** (fork shares pages read-only; copy on first write), and memory-mapped files. The OS keeps a **high/low watermark** and a background **swap daemon** to keep some frames free rather than evicting synchronously on every fault.

## Replacement policies (pick the victim)

Goal: minimize page faults (each costs a slow disk access). Evaluated by fault rate on a reference string.

- **Optimal (Belady / MIN)** — evict the page used **farthest in the future**. Unbeatable, but unimplementable (needs the future); the baseline to compare against.
- **FIFO** — evict the oldest-loaded page. Simple but ignores usage; suffers **Belady's anomaly** (more frames can *increase* faults).
- **LRU (Least Recently Used)** — evict the page unused for the longest; a good approximation of optimal under locality. **Exact LRU is too expensive** (update on every access), so it's approximated:
  - **Clock / second-chance** — frames in a circular list; the **accessed (reference) bit** is checked by a sweeping hand: if set, clear it and skip (second chance); if clear, evict. Cheap, widely used. Augment with the **dirty bit** (prefer evicting clean pages — no write-back) → the "enhanced second-chance" 4-class scheme.
  - Aging/counter approximations track reference history in a few bits.
- **Random** — surprisingly decent and dead simple; sometimes a useful fallback.
- **LFU/MFU** and **working-set/WSClock** variants exist for specific workloads.

Page-cache eviction in real kernels blends recency and frequency (e.g. Linux's active/inactive LRU lists, or ARC-style).

## Working set & thrashing

The **working set** `W(t, Δ)` is the set of pages a process referenced in the last `Δ` time — its current memory demand. If the sum of working sets exceeds physical memory, the system **thrashes**: it spends nearly all its time paging, and CPU utilization collapses. Defenses:
- **Working-set / page-fault-frequency** based **admission control**: don't run (or suspend/swap out) a process whose working set won't fit; give each enough frames to hold its working set.
- Local vs global replacement: **local** confines a process to its own frames (isolates fault behavior); **global** lets any frame be taken (better utilization, but one greedy process can hurt others).

## Practical notes

- A page fault that's a normal event (demand load, COW, stack growth) vs an illegal access must be distinguished in the handler.
- Track **accessed** and **dirty** bits (hardware-set) to drive clock and write-back decisions.
- Keep a free-frame reserve so fault handling isn't synchronously blocked on eviction + write-back.
- For a hobby kernel, start without swapping at all (fault = allocate-or-fault), add COW for `fork`, and only later add a backing store and a clock-based replacer.
