---
name: os-processes-and-scheduling
description: Operating-system processes, threads, and CPU scheduling — virtualizing the CPU. Covers the process abstraction and the process control block (PCB), process states and the state machine, context switching and limited direct execution, the process API (fork/exec/wait/exit), threads (kernel vs user threads, the thread model), and CPU scheduling policies (FIFO, SJF/STCF, round-robin, priority, the multi-level feedback queue, lottery/stride, Linux CFS, and multiprocessor/affinity scheduling) with their metrics (turnaround, response time, fairness). Use when reasoning about how an OS runs and switches between programs, designing a scheduler, implementing processes/threads/context-switch in a kernel, or understanding fork/exec and process lifecycle. Part of the operating-systems skill set (CPU virtualization); see operating-systems for the map and osdev-kernel for implementation.
---

# Processes & CPU Scheduling

How an OS **virtualizes the CPU**: it runs many processes on few cores by rapidly switching between them, giving each the illusion of its own machine. Part of the [[operating-systems]] set; for building it, see [[osdev-kernel]]. Concurrency *correctness* is [[os-concurrency]]; memory is [[os-memory-and-virtual-memory]].

## The process abstraction

A **process** is a running program: its machine state = the **address space** (code, data, heap, stack), the **registers** (incl. PC and stack pointer), and **OS state** (open files, etc.). The OS tracks each in a **Process Control Block (PCB)** — pid, state, saved registers, page-table pointer, open-file table, parent/children, scheduling info.

**Process states**: `running` (on a CPU) ↔ `ready` (runnable, waiting for a CPU) ↔ `blocked/waiting` (waiting on I/O or an event), plus `new` and `terminated/zombie`. Transitions are driven by scheduling decisions and events (I/O completion, timer).

**Limited direct execution + context switch**: run user code directly on the CPU for speed, but keep control via the **timer interrupt**. On a switch the kernel saves the current process's registers to its PCB (kernel stack) and restores the next process's — a *context switch* (µs-scale; it also has indirect cost: cache/TLB pollution). Switching is mechanism; choosing *who* runs next is policy (scheduling).

## The process API (Unix model)

- **`fork()`** — create a near-identical child (copy of the address space, usually **copy-on-write**); returns 0 in the child, the child pid in the parent.
- **`exec()`** — replace the current process image with a new program (keeps the pid).
- **`wait()/waitpid()`** — parent reaps a child's exit status (un-reaped → **zombie**; orphan → reparented to init).
- **`exit()`**, signals, pipes/`dup` (the fork-exec-wait + redirection pattern is how a shell works).

This separation of `fork` and `exec` is deliberate — it lets the shell set up redirection/pipes in the child between them.

## Threads

A **thread** is an independent execution stream within a process: its own PC, registers, and stack, but **sharing the address space** (code/heap/globals) with sibling threads. Cheaper than processes; the basis of parallelism on multicore — and the source of the shared-memory hazards that [[os-concurrency]] addresses. Models: **kernel threads** (the OS schedules them; 1:1), **user threads** (a user library schedules them over fewer kernel threads; M:N), each with trade-offs (blocking syscalls, parallelism). Contrast the **message-passing** alternative ([[akka]] actors, [[functional-programming]]) that sidesteps shared mutable state.

## CPU scheduling — the policy

The scheduler picks which ready thread runs next. Detail and the full algorithm catalog are in **`references/scheduling.md`**. Key ideas:

- **Metrics**: *turnaround time* (completion − arrival) favors throughput; *response time* (first-run − arrival) favors interactivity; plus *fairness* and *predictability*. These conflict — a scheduler trades them off.
- **Preemptive vs non-preemptive**: can the scheduler take the CPU away (timer) or only switch when a job yields/blocks? Modern OSes are preemptive.
- **The workhorses**: **Round-Robin** (time slices → good response time), **SJF/STCF** (shortest job first → optimal turnaround but needs to know job length), and the **Multi-Level Feedback Queue (MLFQ)** which *approximates* SJF without oracular knowledge by learning from observed behavior — the basis of real interactive schedulers. Linux's **CFS** uses weighted fair-sharing (virtual runtime) instead.

## Always-apply notes (for implementation)

- The PCB + a per-process kernel stack + a `switch()` routine that saves/restores callee-saved registers and swaps stacks is the heart of multitasking — see [[osdev-kernel]].
- Drive preemption from the **timer interrupt**; choose a time-slice that balances response time against context-switch overhead.
- Keep mechanism (context switch) and policy (scheduler) separate so you can change the policy freely.
- A new context-switched-to thread "returns" into the middle of a previous switch — getting the first switch into a brand-new thread right (fake initial stack frame) is the classic tricky bit.

## Related

- [[operating-systems]] (map) · [[os-memory-and-virtual-memory]] (the address space switched on a context switch) · [[os-concurrency]] (threads safely) · [[osdev-kernel]] (implementing processes/scheduler).
- [[akka]], [[functional-programming]] — message-passing concurrency as an alternative to threads + shared memory.
- `references/scheduling.md` — the scheduling-algorithm catalog.
- Sources: OSTEP (Virtualization: processes, the API, scheduling, MLFQ); Silberschatz Ch. 3–5; Tanenbaum Ch. 2.
