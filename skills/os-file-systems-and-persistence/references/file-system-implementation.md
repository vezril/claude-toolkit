# File-system implementation & crash consistency

OSTEP (Persistence: FS implementation, FFS, FSCK & journaling, LFS) · Silberschatz Ch. 14 · Tanenbaum Ch. 4.

## A very simple file system (vsfs) layout

Disk as an array of blocks (e.g. 4 KiB). A minimal inode-based FS:

```
[ superblock | inode bitmap | data bitmap | inode table .... | data blocks ......... ]
```
- **Superblock** — counts/locations of the regions, block size, magic, FS state.
- **Bitmaps** — one bit per inode / per data block marking free vs used (allocate = find a 0, set it; free = clear).
- **Inode table** — array of inodes; **inode number** = index. An inode = metadata + block pointers.
- **Data region** — file contents and directory blocks.

**Inode block pointers**: N **direct** pointers (cover small files) + a **single indirect** (a block full of pointers) + **double** + **triple** indirect → a lopsided multi-level index that keeps small files fast while still addressing large ones. Modern FSes replace this with **extents** (a few `(start_block, length)` runs) — far less metadata for large contiguous files.

**Directories**: a directory's data blocks hold `(name, inode#)` records (plus `.` and `..`). Lookups are linear in simple FSes; production FSes use **hashed (htree)** or **B-tree** directories for O(log n)/O(1) lookup with many entries.

**Reading `/foo/bar`**: read root inode (well-known number) → read its data to find `foo`'s inode# → read `foo` inode → find `bar` → read `bar`'s inode → read data blocks. Each level is a couple of I/Os — hence caching matters.

## Allocation & locality

- **Free-space**: bitmaps (compact, easy to scan) or free lists. Try to allocate a file's blocks **contiguously** (fewer seeks; enables extents).
- **FFS (Fast File System)** insight: split the disk into **cylinder/block groups**, each with its own inodes+bitmaps+data, and place an inode near its data and a directory's inodes/files in the same group → exploit spatial locality, cut seeks. Keep some free space per group so allocation has room to stay contiguous.

## Caching

A **buffer/page cache** holds hot blocks/pages in RAM. Reads serve from cache; writes are **write-back** (buffered, flushed by a daemon or on `fsync`) — a durability/performance trade-off. Unified with the VM page cache in modern kernels (one pool for file data and memory-mapped pages).

## Crash consistency in depth

Problem: a single logical operation (e.g. append a block) updates several on-disk structures (data block, data bitmap, inode); a crash between writes leaves inconsistency (lost block, dangling pointer, double-allocated block).

- **fsck** — after a crash, scan the whole FS and fix inconsistencies by reasoning about redundancy (e.g. rebuild bitmaps from inodes, fix link counts). Correct but **O(disk size)** slow and can't recover *data*, only consistency. Legacy.
- **Journaling / write-ahead logging** — first write the intended updates to a **journal (log)**: `TxBegin → [blocks] → TxEnd(commit)`; only after the commit record is durable do you **checkpoint** (write the blocks to their real locations). After a crash, **replay** committed transactions and discard incomplete ones. Variants:
  - **Data journaling** — log data + metadata (safe, double-writes everything).
  - **Ordered/metadata journaling** (ext3/4 default) — write data blocks first, then journal only **metadata** → much less write traffic, avoids pointing metadata at garbage. Issue a barrier/flush between log write and commit so ordering holds on real hardware.
- **Copy-on-write (COW)** (ZFS, btrfs, APFS) — never overwrite live data; write changed blocks to new locations and **atomically flip the root/superblock pointer**. The on-disk image is always consistent; enables cheap **snapshots** and block **checksums** (end-to-end integrity). Cost: fragmentation, GC-like behavior.
- **Log-structured FS (LFS)** — buffer all writes and stream them sequentially as one big **append-only log** (huge write throughput, ideal for flash); a **cleaner/garbage collector** reclaims space from obsolete blocks. Influential on modern flash file systems (F2FS) and SSD FTLs.

## Practical guidance

- Correctness before speed: pick a consistency scheme up front (a small **metadata journal** is the sweet spot; COW if you want snapshots/checksums).
- Respect device **write ordering / flush (FUA/barrier)** — journaling is only safe if the commit record truly lands after the logged blocks.
- For a hobby kernel: implement vsfs (or ext2/FAT for tooling), add a buffer cache, then add a simple redo journal for metadata. The application-level mirror of all this is event-sourced journaling in [[akka-persistence]].
