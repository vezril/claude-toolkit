# Objects, errors, boundaries, classes, systems, emergence, concurrency

*Clean Code* (Martin, 2008), Chapters 6–8, 10–13. Faithful, with Scala/FP notes and critique.

## Objects and data structures (Ch. 6)

- **Data/object anti-symmetry.** *Objects* hide data behind behavior (expose operations); *data structures* expose data and have no meaningful behavior. They're opposites: objects make it easy to add new *types* without changing existing functions; data structures (+ procedures) make it easy to add new *functions* without changing existing types. Don't make hybrids ("train wreck" half-object half-DTO).
- **The Law of Demeter** — a method should only talk to its immediate friends: its own fields, its parameters, objects it creates. Avoid "train wrecks": `ctxt.getOptions().getScratchDir().getAbsolutePath()`. If you're navigating a chain you're reaching across structure; tell, don't ask.
- **DTOs / Active Record** — plain data carriers at boundaries (serialization, DB rows) are fine *as* data structures; don't bolt business rules onto them.

**Scala/FP:** this anti-symmetry **is the expression problem** ([[design-patterns]]): a `sealed trait` ADT + pattern match = easy new operations, harder new cases (the "data structure" side); a polymorphic trait = easy new cases, harder new operations. Choose by which axis changes. Immutable case classes are clean DTOs.

## Error handling (Ch. 7)

- **Use exceptions, not return codes** — error codes clutter the caller with inline checks and nesting.
- **Write the `try/catch/finally` first** — it defines the scope/transaction boundary; build the body within the guarantee it provides.
- **Prefer unchecked exceptions** (checked exceptions break encapsulation by forcing signature changes up the call chain). *(Scala/FP: for **expected** failures prefer **errors-as-values** — `Either`/`Try`/an error ADT — and reserve exceptions for the truly exceptional; this is cleaner than Martin's exceptions-everywhere on this stack. See [[functional-programming]], [[modern-java]].)*
- **Provide context** with exceptions (what operation failed, why); **define exception classes in terms of the caller's needs** (wrap third-party exception zoos in one or few of your own).
- **Define the normal flow** — don't use exceptions for control flow; the Special Case / Null Object pattern can remove a special-case branch entirely.
- **Don't return `null`** (returns empty collection / Null Object / `Optional`) and **don't pass `null`** — both breed `NullPointerException`s and defensive checks everywhere.

## Boundaries (Ch. 8)

- **Wrap third-party code** behind an interface you control (e.g. don't pass a raw `Map`/library type around) — you depend on your boundary, not their API, and can swap or adapt later (an Adapter, [[design-patterns]]).
- **Learning tests** — write small tests that exercise a third-party library the way you'll use it; they verify your understanding *and* catch breaking changes when you upgrade (better than free).
- **Code that doesn't exist yet** — define the interface you *wish* you had at the boundary, code against it, and adapt to reality later.

**Scala/FP:** boundaries map onto **ports & adapters** — a trait (port) in the pure core, the effectful/third-party adapter at the edge (pure-core/effectful-shell from [[functional-programming]]).

## Classes (Ch. 10)

- **Classes should be small** — measured by **responsibilities**, not lines.
- **Single Responsibility Principle (SRP):** a class should have **one reason to change** (one actor/axis of change). A class doing many things is a maintenance hazard. *(Critique: SRP is widely misread as "one method/verb per class" — it means one axis of change; don't shatter a cohesive class into anemic fragments.)*
- **Cohesion:** methods should use many of the class's fields; when cohesion drops, that's a signal the class wants to split into smaller, more cohesive classes.
- **Organize for change / isolate from change:** depend on abstractions (interfaces) so new requirements add classes rather than editing existing ones (Open/Closed); this also makes the code testable.

## Systems (Ch. 11)

- **Separate constructing a system from using it.** Don't let business logic `new` its own collaborators — move wiring to a startup boundary (`main`/composition root), factories, or **dependency injection**. This is the single biggest enabler of testability and change.
- **Scaling up:** systems grow; keep cross-cutting concerns (persistence, security, transactions) out of business logic (the book uses AOP/proxies — modern equivalents: middleware, decorators, effect systems). **Test-drive the architecture**; defer decisions until you have information; use standards only when they add demonstrable value; consider a DSL for the domain.

**Scala/FP:** "separate construction from use" = wiring effects at the edge and passing dependencies as values/functions (constructor injection, the Reader pattern, or a simple composition root) — see [[functional-programming]] and the [[akka-sdk]] DI model.

## Emergent design (Ch. 12) — Kent Beck's four rules of simple design

A design is "simple" if, in priority order, it:
1. **Runs all the tests** (it's verifiably correct; being testable forces good design — small, decoupled, SRP).
2. **Contains no duplication** (DRY — the primary enemy of clean design).
3. **Expresses the intent** of the programmer (clear names, small functions, well-known patterns).
4. **Minimizes the number of classes and methods** (lowest priority — don't over-fragment in the name of the other rules).

Good design **emerges** from continuously applying these during refactoring, not from big up-front design.

## Concurrency (Ch. 13)

Concurrency decouples *what* from *when* but is hard and bug-prone. Defense principles: keep concurrency code **separate** (SRP for threads); **limit the scope of shared mutable data** (and use copies); make threads **as independent as possible** (no shared state); know your library (thread-safe collections, executors) and your execution models (producer-consumer, readers-writers, dining philosophers); keep synchronized sections small; get non-threaded code working first; make threaded code pluggable and tunable; treat spurious failures as real threading bugs.

**Scala/FP:** this stack largely *avoids* the problem — prefer **immutability + message passing/streams** (the [[akka]] actor model, Akka Streams) or pure effect systems over shared-memory locking; Martin's "limit shared mutable data" becomes "don't share mutable data at all."
