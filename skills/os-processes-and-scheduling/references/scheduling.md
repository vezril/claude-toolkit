# CPU scheduling algorithms

OSTEP (Scheduling; MLFQ; Lottery) · Silberschatz Ch. 5 · Tanenbaum Ch. 2. The scheduler chooses which ready thread runs next; policies trade off competing metrics.

## Metrics

- **Turnaround time** = completion − arrival (throughput/batch goal).
- **Response time** = first-scheduled − arrival (interactivity goal).
- **Fairness**, **predictability**, **starvation-freedom**, **overhead** (context-switch cost).
These conflict: optimizing turnaround (run short jobs to completion) hurts response time; optimizing response time (frequent switching) adds overhead. A real scheduler balances them.

## Batch / foundational policies

- **FIFO / FCFS** — run in arrival order to completion. Simple; suffers the **convoy effect** (a long job delays all short jobs behind it → bad average turnaround).
- **SJF (Shortest Job First)** — run the shortest job first; **optimal average turnaround** for jobs arriving together. Non-preemptive; needs to know/estimate job length; can starve long jobs.
- **STCF / SRTF (Shortest Time-to-Completion First)** — preemptive SJF: always run the job with the least remaining time; optimal turnaround when jobs arrive over time. Still needs length knowledge.

## Interactive policies

- **Round-Robin (RR)** — each ready job runs for a fixed **time slice (quantum)**, then goes to the back of the queue. Excellent **response time** and fairness; worse turnaround. Quantum choice: too small → switch overhead dominates; too large → degrades to FIFO. Amortize the slice against context-switch cost.
- **Priority scheduling** — run the highest-priority ready job. Risk: **starvation** of low-priority jobs → fix with **aging** (raise priority over wait time). Priority inversion (a high-priority job blocked on a lock held by a low one) is solved with **priority inheritance** (see [[os-concurrency]]).
- **Multi-Level Feedback Queue (MLFQ)** — multiple priority queues; **learn** a job's nature from behavior instead of knowing its length: new jobs start high; a job that uses its whole slice (CPU-bound) is **demoted**; a job that yields early for I/O (interactive) **stays high**. Periodically **boost** all jobs to avoid starvation and adapt to phase changes; account total CPU used per level to prevent gaming. MLFQ approximates SJF (good turnaround) *and* gives good response time without an oracle — the basis of classic Unix/Windows interactive schedulers.

## Proportional-share / fair

- **Lottery scheduling** — give each job tickets proportional to its share; hold a lottery each slice. Probabilistically fair, simple, supports ticket transfer/currencies. **Stride scheduling** is the deterministic version (smallest "pass" value runs next).
- **Linux CFS (Completely Fair Scheduler)** — tracks each task's weighted **virtual runtime (vruntime)**; always run the task with the smallest vruntime (kept in a red-black tree). Weights come from **nice** values; targets fair CPU shares with a tunable scheduling latency rather than fixed quanta. (Newer kernels: **EEVDF**.)

## Multiprocessor scheduling

- **Cache affinity** — keep a task on the CPU where its cache is warm; migration is costly.
- **Single-queue (SQMS)** vs **multi-queue (MQMS)** — one global ready queue (simple, poor scalability/affinity, lock contention) vs per-CPU queues (scalable, affinity-friendly) needing **load balancing** (work stealing/migration) to avoid imbalance.
- Beware **synchronization** of shared scheduler data on many cores; per-CPU run queues + periodic balancing is the norm.
- **Real-time** scheduling (rate-monotonic, EDF) for deadline guarantees is a separate discipline when timing is hard-constrained.

## Choosing / implementing

- Interactive general-purpose OS → MLFQ-style or CFS-style fair scheduling with preemption off the timer.
- Know your workload: batch/throughput → SJF/STCF-like; latency-sensitive → RR/priority with aging.
- In a hobby kernel, start with **round-robin over a ready list driven by the timer interrupt**, then evolve to priorities/MLFQ. Keep the policy isolated behind a `pick_next()` so you can swap it.
