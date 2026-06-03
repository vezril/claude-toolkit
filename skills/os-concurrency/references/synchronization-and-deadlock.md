# Deadlock & concurrency-bug taxonomy

OSTEP (Common Concurrency Problems; Deadlock) · Silberschatz Ch. 8 · Tanenbaum Ch. 6.

## Deadlock — the four necessary conditions

A deadlock is a set of threads each waiting for a resource another holds, forever. It can occur **only if all four** hold simultaneously (Coffman conditions):
1. **Mutual exclusion** — resources held in a non-shareable way.
2. **Hold-and-wait** — a thread holds resources while waiting for more.
3. **No preemption** — resources can't be forcibly taken.
4. **Circular wait** — a cycle of threads each waiting on the next.

Break any one and deadlock is impossible.

## Strategies

**Prevention** (negate a condition, statically):
- Negate **circular wait** — impose a **total ordering on locks** and always acquire in that order. The most practical, widely-used technique.
- Negate **hold-and-wait** — acquire all needed locks atomically up front (needs a meta-lock; reduces concurrency).
- Negate **no preemption** — use `trylock` and back off (release held locks and retry) — risks **livelock** (add randomized backoff).
- Negate **mutual exclusion** — use lock-free/wait-free structures (CAS-based) where possible.

**Avoidance** (decide dynamically whether granting a request stays "safe"): the **Banker's Algorithm** grants a resource only if a safe sequence still exists (every thread can eventually finish). Requires knowing maximum claims in advance; rarely used in general-purpose OSes (too restrictive/impractical) but important conceptually.

**Detection & recovery**: allow deadlocks, detect cycles in the resource-allocation/wait-for graph periodically, then recover by **killing** a thread or **preempting/rolling back** a resource (common in databases via transaction abort + retry; cf. [[akka-persistence]]/transactions). The "**ostrich algorithm**" — ignore it — is what most general OSes actually do for rare cases, leaving lock-ordering discipline to developers.

## Related hazards

- **Livelock** — threads keep changing state in response to each other but make no progress (e.g. two people stepping aside in a hallway). Fix with randomized/exponential backoff.
- **Starvation** — a thread is perpetually denied a resource (e.g. writer starvation in readers-writers, low-priority starvation). Fix with fairness/aging.
- **Priority inversion** — a high-priority thread blocks on a lock held by a low-priority thread that's been preempted by a medium-priority one. Fix with **priority inheritance** (the holder temporarily inherits the waiter's priority) or priority ceilings. (Famously caused the Mars Pathfinder resets.)

## Non-deadlock concurrency bugs (the majority, per OSTEP's study)

- **Atomicity violation** — a sequence assumed atomic is interleaved (e.g. check-then-use of a shared field across two statements). Fix: hold a lock across the whole sequence.
- **Order violation** — code assumes A happens before B but ordering isn't enforced (e.g. using a pointer a thread hasn't initialized yet). Fix: a condition variable / join / happens-before.
These are subtler than deadlocks and far more common; most real bugs are atomicity/order violations, not deadlocks.

## Practical discipline

- Establish and document a **global lock order**; encode it where possible (lock hierarchies, lockdep-style checkers).
- Keep critical sections small; never block/IO/call-out under a lock.
- Prefer coarse correctness first, then refine; prefer higher-level constructs and, where feasible, **message passing / immutability** ([[akka]], [[functional-programming]]) which avoids shared-lock deadlocks entirely (you can still get logical deadlocks via request cycles — design protocols to avoid them).
- For databases/persistent actors, lean on transactions + retry rather than fine-grained locks.
