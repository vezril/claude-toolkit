# Items 78–90: Concurrency and serialization

Effective Java 3rd ed., Items 78–90, faithful to Bloch and updated for Java 21 (notably virtual threads and structured concurrency).

## Contents

- Concurrency (78–84)
- Serialization (85–90)

---

## Concurrency

**78. Synchronize access to shared mutable data.** Synchronization is for both *mutual exclusion* and *visibility* — without it, threads may see stale values (the `volatile`/happens-before issue), not just torn writes. Either don't share mutable data (confine it, or make it immutable) or synchronize all access (reads too). For single-variable visibility without atomicity needs, `volatile` suffices; for atomic updates use `java.util.concurrent.atomic`.

**79. Avoid excessive synchronization.** Holding a lock while calling an "alien" method (an overridable method or a client-supplied callback) risks deadlock and data corruption. Do as little as possible inside `synchronized` blocks; never call out to unknown code while holding a lock. Over-synchronizing also kills performance/scalability.

**80. Prefer executors, tasks, and streams to threads.** Use the `java.util.concurrent` **`Executor`/`ExecutorService`** framework and `Runnable`/`Callable` tasks rather than working with `Thread` directly. **Modern (Java 21): virtual threads** make "thread-per-task" cheap again — use `Executors.newVirtualThreadPerTaskExecutor()` for large numbers of blocking-I/O tasks; and **structured concurrency** (`StructuredTaskScope`) for forking subtasks with reliable cancellation/joining. Keep the task-based mindset; let the executor manage threads.

**81. Prefer concurrency utilities to `wait` and `notify`.** Hand-written `wait`/`notify` is error-prone (always loop on the condition; prefer `notifyAll`). Use higher-level utilities instead: `ConcurrentHashMap` and other concurrent collections, `BlockingQueue`, and synchronizers (`CountDownLatch`, `Semaphore`, `CyclicBarrier`, `Phaser`). For timing use `System.nanoTime`.

**82. Document thread safety.** State each class's thread-safety level in its docs: immutable, unconditionally thread-safe, conditionally thread-safe (which sequences need external locking), not thread-safe, or thread-hostile. Don't rely on `synchronized` in the signature as documentation. Use a private lock object for unconditionally thread-safe classes to prevent clients/subclasses interfering with the lock.

**83. Use lazy initialization judiciously.** Usually initialize eagerly. If you must lazy-init: for instance fields, the double-check idiom with a `volatile` field; for static fields, the **lazy-initialization holder class** idiom. Don't lazy-init without a demonstrated need.

**84. Don't depend on the thread scheduler.** Programs whose correctness or performance depends on thread priorities or scheduler behavior are non-portable. Don't busy-wait; keep the number of runnable threads reasonable; `Thread.yield`/priorities are not fixes — restructure instead.

## Serialization

**Overarching modern guidance:** Java's built-in serialization is a persistent source of security holes (deserialization of untrusted data enables remote code execution) and maintenance pain. For new designs use a **cross-platform structured data format** — JSON, protobuf, CBOR, etc. — not Java serialization. Items 85–90 apply when you're stuck with it.

**85. Prefer alternatives to Java serialization.** The best defense against deserialization attacks is to **never deserialize untrusted bytes**. Avoid `Serializable` entirely where you can; use JSON/protobuf. If you must accept serialized data, consider serialization filtering (`ObjectInputFilter`) to whitelist classes.

**86. Implement `Serializable` with great caution.** It's a lasting commitment: it constrains future evolution, expands the attack surface, increases testing burden, and makes every serializable class's byte-stream part of its public API. Don't implement it casually, especially not on classes designed for inheritance.

**87. Consider using a custom serialized form.** Don't accept the default serialized form unless it matches the object's logical content. Define `serialVersionUID` explicitly. Use `transient` for fields that shouldn't be serialized, and `writeObject`/`readObject` for a custom form.

**88. Write `readObject` methods defensively.** `readObject` is effectively a public constructor taking a byte stream: validate all invariants and make defensive copies of mutable components, exactly as a real constructor would — otherwise crafted bytes can produce an invalid or aliased object.

**89. For instance control, prefer enum types to `readResolve`.** If you need a singleton/instance-controlled class to survive serialization, a single-element **enum** guarantees it; `readResolve` is fragile (every field must be `transient`).

**90. Consider serialization proxies instead of serialized instances.** The serialization proxy pattern (a private static nested `SerializationProxy` with `writeReplace`/`readResolve`) is the most robust way to serialize an immutable class safely — it sidesteps most `readObject` attacks. Use it when you must serialize and can.

---

**Bottom line for new code:** make domain objects immutable and *not* `Serializable`; persist/transmit via an explicit DTO + JSON/protobuf layer at the boundary; reserve Items 86–90 for legacy interop you can't avoid.
