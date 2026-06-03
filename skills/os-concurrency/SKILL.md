---
name: os-concurrency
description: Operating-system concurrency and synchronization — running threads correctly over shared memory. Covers the concurrency problem (race conditions, critical sections, atomicity), building locks from hardware atomics (test-and-set, compare-and-swap, load-linked/store-conditional; spinlocks vs blocking mutexes), condition variables, semaphores, monitors, and classic problems (producer/consumer with bounded buffer, readers-writers, dining philosophers), plus deadlock (the four conditions; prevention, avoidance/banker's, detection, recovery), livelock, starvation, priority inversion, and common concurrency bugs (atomicity- and order-violations). Use when reasoning about thread synchronization, designing locks/semaphores/monitors in a kernel or app, diagnosing races/deadlocks, or protecting shared kernel data structures. Part of the operating-systems skill set; contrast with message-passing concurrency in functional-programming/akka.
---

# Concurrency & Synchronization

Doing many things at once over **shared memory**, correctly. Threads share an address space ([[os-processes-and-scheduling]]), so unsynchronized access to shared data races. Part of the [[operating-systems]] set. The alternative philosophy — **don't share mutable state, pass messages** — is [[akka]] / [[functional-programming]]; this skill is the shared-memory, lock-based world OSes (and most languages) actually run on.

## The problem

A **race condition** is when the result depends on the nondeterministic interleaving of threads. The classic example: `counter++` is really load–increment–store; two threads interleaving lose an update. The code touching shared data is a **critical section**; correctness needs **mutual exclusion** (at most one thread in it at a time) plus progress and bounded waiting. The root issue is that operations we think of as atomic aren't, and the scheduler can preempt anywhere.

## Locks

A **lock** (mutex) makes a critical section atomic: `lock(); /* critical section */; unlock();`. You can't build a correct lock from ordinary loads/stores alone (Peterson's algorithm works but doesn't scale); you need **hardware atomic instructions**:
- **Test-And-Set (TAS)** / `xchg` — atomically read-and-set; the basis of a **spinlock** (`while (TAS(&flag)) ;`).
- **Compare-And-Swap (CAS)** — atomically "if `*p == expected`, set `*p = new`"; the workhorse for locks **and lock-free** data structures.
- **Load-Linked / Store-Conditional (LL/SC)** — RISC equivalent (ARM `ldxr/stxr`); store succeeds only if no one wrote since the load.
- **Fetch-And-Add** — for ticket locks (fair FIFO ordering).

**Spinlock vs blocking lock**: a spinlock busy-waits (fine for very short critical sections on a multiprocessor, *terrible* on a uniprocessor or long holds — wastes the slice); a **blocking mutex** parks the waiter (yields/sleeps until woken) — better for contention/long holds, but with wake-up cost. Real mutexes are often hybrid (spin briefly, then block). **Memory barriers/ordering** matter on weakly-ordered hardware (ARM): atomics must carry the right acquire/release semantics.

## Higher-level primitives

- **Condition variables** — wait for a condition while holding a mutex: `wait(cond, mutex)` atomically releases the lock and sleeps; `signal`/`broadcast` wake waiters. **Always re-check the condition in a `while` loop** (spurious wakeups, and the woken thread re-acquires the lock after others may have changed state — Mesa semantics). The mutex+CV pair is the foundation of most coordination.
- **Semaphores** — an integer with atomic `wait/P` (decrement, block if <0) and `post/V` (increment, wake). A semaphore initialized to 1 is a lock; initialized to N it bounds concurrency; used as a **condition** it signals events. Elegant but error-prone (no association between the semaphore and the data it guards).
- **Monitors** — a language construct bundling shared data + the mutex + condition variables (Java `synchronized`/`wait`/`notify`, etc.); safer because the locking is structural.

## Classic problems (patterns to know)

- **Producer/Consumer (bounded buffer)** — two condition variables (`empty`, `full`) + a mutex; producers wait when full, consumers when empty. The template for queues/pipelines (cf. [[akka-streams]] backpressure as the message-passing solution).
- **Readers-Writers** — many concurrent readers OR one writer; watch writer starvation; modern answer is often a **read-write lock** or RCU.
- **Dining Philosophers** — the canonical deadlock illustration; the fix (break the cycle, e.g. asymmetric acquire order) generalizes to lock-ordering discipline.

## Deadlock & friends

Detail in **`references/synchronization-and-deadlock.md`**. The **four necessary conditions** (mutual exclusion, hold-and-wait, no preemption, circular wait) must *all* hold; remove any one to prevent deadlock. Practically: enforce a **global lock-ordering** to kill circular wait. Also beware **livelock** (threads keep retrying without progress), **starvation** (a thread never gets the resource), and **priority inversion** (fixed by priority inheritance — the Mars Pathfinder bug).

## Always-apply notes

- **Hold locks for the shortest time**; never call out to unknown code (or do blocking I/O) while holding a lock; acquire multiple locks in a **consistent global order**.
- Protect *every* access to shared mutable data, including reads; on weak-memory hardware use proper atomics/barriers.
- In a kernel: disable interrupts (or use interrupt-safe spinlocks) for data shared with interrupt handlers; never sleep while holding a spinlock; keep critical sections tiny.
- Prefer **higher-level constructs** (monitors, message queues) over raw semaphores; prefer **immutability and message-passing** ([[functional-programming]], [[akka]]) where you can — it removes whole classes of these bugs.

## Related

- [[operating-systems]] (map) · [[os-processes-and-scheduling]] (threads) · [[osdev-kernel]] (kernel locking, interrupts).
- [[akka]], [[functional-programming]], [[scala]] — message-passing/immutability as the alternative to shared-memory locking; [[akka-streams]] for backpressured producer/consumer.
- `references/synchronization-and-deadlock.md` — deadlock handling and concurrency-bug taxonomy.
- Sources: OSTEP (Concurrency: locks, condition variables, semaphores, common bugs, deadlock); Silberschatz Ch. 6–8; Tanenbaum Ch. 2 & 6.
