---
name: os-file-systems-and-persistence
description: Operating-system file systems and persistent storage — storing data durably across crashes. Covers the file & directory abstraction and the POSIX file API, the storage stack and disk scheduling, file-system implementation (the superblock/inode/data-block layout, free-space bitmaps, directory structures, FAT vs inode-based FFS/ext, extents), hard vs symbolic links, the buffer/page cache, crash consistency (fsck, journaling/write-ahead logging, copy-on-write file systems, log-structured file systems), and RAID levels. Use when reasoning about how files and storage work, designing or implementing a file system in a kernel, choosing journaling vs COW, ensuring crash consistency, or understanding inodes/directories/links and RAID. Part of the operating-systems skill set (persistence); see operating-systems for the map, os-io-and-devices for the device layer, and osdev-kernel for implementation.
---

# File Systems & Persistence

How an OS stores data **durably** — surviving process exit, reboot, and crashes — on top of block devices. Part of the [[operating-systems]] set (the *persistence* pillar of OSTEP). The device mechanics (interrupts, DMA, drivers, HDD/SSD) are [[os-io-and-devices]]; implementation is [[osdev-kernel]].

## The abstractions

- **File** — a linear array of bytes with a name and metadata; identified internally by an **inode number**. **Directory** — a file that maps names → inode numbers, forming the namespace tree (with `.`/`..`).
- **POSIX API** — `open` (returns a **file descriptor**), `read`/`write` (advance an offset), `lseek`, `close`, `fsync` (force to stable storage), `stat`, `mkdir`, `link`/`unlink`, `rename`. FDs are per-process indices into open-file tables; `dup`/redirection build on them.
- **Hard links** (multiple names → same inode; inode freed when link count hits 0) vs **symbolic links** (a file whose contents are a path; can dangle, cross file systems). **Mounting** grafts one file system into the tree; a **VFS** layer lets many file systems share one API.

## On-disk structures (inode-based, the common design)

A typical layout in blocks: **superblock** (FS metadata: sizes, locations) · **inode bitmap** + **data bitmap** (free-space tracking) · **inode table** · **data region**. An **inode** holds metadata (type, size, permissions/owner, timestamps, link count) and **pointers to data blocks**: a set of **direct** pointers plus **single/double/triple indirect** pointers (a multi-level index — small files are cheap, huge files still addressable). Modern file systems (ext4, XFS, APFS, btrfs/ZFS) use **extents** (offset+length runs) instead of block lists for efficiency. **FAT** is the alternative classic design (a file-allocation table = a linked list of clusters; simple, no inodes, poor for large/fragmented files).

**Directories** are stored as files containing name→inode entries (linear lists in simple FSes; B-trees/hashed in fast ones). **Path resolution** walks the tree inode by inode from the root (or cwd).

## Performance: caching & scheduling

- **Buffer/page cache** — RAM caches recently-used blocks/pages; reads hit cache, writes are **buffered** and flushed later (write-back). Trades durability for speed → `fsync` forces a flush; the cache is unified with the VM page cache in modern kernels.
- **Disk scheduling** (HDDs) — reorder requests to cut seek time: FCFS, SSTF (shortest-seek-time-first), **SCAN/C-SCAN** (elevator). Less relevant for **SSDs** (no seeks; instead worry about write amplification, the FTL, TRIM, wear leveling — see [[os-io-and-devices]]).
- **Locality** — place an inode near its data and a directory's files together (FFS **cylinder/block groups**) to exploit spatial locality.

## Crash consistency — the hard problem

A crash mid-update can leave the FS inconsistent (e.g. data block written but bitmap not, or inode updated but directory entry not). Approaches (detail in `references/file-system-implementation.md`):
- **fsck** — scan and repair after the fact (slow, and can't recover lost data); legacy.
- **Journaling (write-ahead logging)** — write intended changes to a **log** first, mark committed, then apply (checkpoint); after a crash, replay the log. **Metadata journaling** (ext3/4 default) logs only metadata (data written first) for speed; full data journaling is safer/slower. The dominant approach.
- **Copy-on-write** (ZFS, btrfs, APFS) — never overwrite in place; write new blocks and atomically switch a root pointer → always-consistent on disk, enables snapshots/checksums.
- **Log-structured (LFS)** — treat the whole disk as an append-only log (great write throughput; needs garbage collection); influential on SSD/flash FS design.

## RAID (redundancy across disks)

Combine disks for capacity/performance/reliability: **RAID-0** (striping, no redundancy — speed/capacity, no safety), **RAID-1** (mirroring — full redundancy), **RAID-5/6** (striping + distributed parity — tolerate 1/2 disk failures with less overhead than mirroring), **RAID-10** (mirrored stripes). Trade-offs in space, read/write performance, and failure tolerance; this is applied **coding theory** ([[information-theory]] — erasure codes).

## Always-apply notes (for implementation)

- For a hobby kernel, start with a **simple inode-based FS** (superblock + bitmaps + inode table + data blocks, direct+indirect pointers) or even adopt an existing layout (ext2, FAT) for tooling compatibility; build it over the block-device driver from [[os-io-and-devices]].
- Get the **write ordering** right for consistency (or add a small journal) before worrying about performance; `fsync` semantics matter.
- A **buffer cache** is the single biggest performance win; unify it with the page cache if you have VM.
- Persisting *application* state durably and consistently is the same problem one level up — see [[akka-persistence]] (event sourcing/journaling) and [[akka-persistence-plugins]].

## Related

- [[operating-systems]] (map) · [[os-io-and-devices]] (block devices, drivers, SSD/HDD) · [[osdev-kernel]] (implementing a FS) · [[information-theory]] (RAID/erasure coding).
- [[akka-persistence]] — journaling/event-sourcing as the application-level analog of crash-consistent storage.
- `references/file-system-implementation.md` — layout, inodes, and crash-consistency mechanisms in depth.
- Sources: OSTEP (Persistence: I/O devices, HDDs, RAID, files & directories, FS implementation, FFS, journaling, LFS); Silberschatz Ch. 11–14; Tanenbaum Ch. 4.
