# Deep modules & information hiding

*A Philosophy of Software Design* (Ousterhout), Chapters 4–9. Faithful; Scala/FP notes inline.

## Modules should be deep (Ch. 4)

A module's **interface** = everything a developer must know to use it (formal: signatures, types; informal: side effects, ordering, "gotchas"). The **implementation** = the code behind it. Each provides an **abstraction**: a simplified mental model that omits unimportant detail. A bad abstraction either omits something important (false simplicity) or exposes something unimportant.

**Depth = functionality ÷ interface complexity.** A **deep module** has a *simple interface over a powerful implementation* — it hides a lot of complexity behind a little. Best example: Unix file I/O (`open/read/write/close/lseek` — 5 calls hide device drivers, scheduling, buffering, permissions). A **shallow module** exposes nearly as much in its interface as it implements; it adds interface cost without hiding much, so it's a net complexity *loss*.

**Classitis** — the dogma that classes/methods must be small — produces lots of shallow modules. Each adds an interface to learn and a boundary to cross; the accumulation makes the *system* more complex even as each piece looks "clean." Module count is not the metric; **depth** is. (This is APoSD's direct counter to Clean Code's small-class/small-function emphasis — extract to deepen or de-duplicate, not to shrink.)

**Scala/FP:** a small total function or typeclass with a rich, hidden implementation is a deep module; resist splitting a cohesive type into many anemic ones.

## Information hiding & leakage (Ch. 5)

- **Information hiding:** each module encapsulates a *design decision* (a data structure, a file format, an algorithm, a dependency) so knowledge of it lives in one place and doesn't appear in the interface. This is the primary way to make modules deep and reduce dependencies.
- **Information leakage** (the opposite, a red flag): the same knowledge is needed by, or embedded in, multiple modules — change one and you must change the others. Often subtle (two classes that both know a file format). Fix by merging the leak into one module or hiding it better.
- **Temporal decomposition** (a common cause of leakage): structuring modules around *order of execution* (read → process → write) instead of around *knowledge*. Code that runs at different times may share knowledge and belongs together; design around knowledge, not the time sequence.
- Hide within a class too (private methods/fields); but **don't take it too far** — information needed by the caller (genuine interface) must be exposed; over-hiding that forces awkward workarounds is also bad.

## General-purpose modules are deeper (Ch. 6)

Make modules **"somewhat general-purpose"**: implement the general mechanism the problem fundamentally needs, not a narrowly special-cased API for today's first caller. A general-purpose interface is usually **simpler, smaller, and deeper**, and pushes special-case logic up to the (fewer) places that truly need it — improving information hiding. Questions to ask: *What is the simplest interface that covers all my current needs? In how many situations will this method be used? Is this API easy to use for my current need?* (Balance: don't speculatively over-generalize for needs you don't have — "general-purpose" means the natural mechanism, not maximum configurability.)

## Different layer, different abstraction (Ch. 7)

Adjacent layers should provide **different** abstractions; if they don't, you have needless complexity:
- **Pass-through methods** — a method that does nothing but call another method with (nearly) the same signature. It adds interface without adding abstraction; remove it (let the caller call directly, or redistribute responsibility).
- **Decorators** are a related risk: they add a thin layer; use them only when they genuinely add a useful abstraction, not reflexively.
- **Pass-through variables** — a variable threaded through many method signatures just to reach a deep caller. Each intermediate layer must know about it for no reason. Eliminate via a shared context object, or storing it where it's needed.
- Keep interface and implementation at different abstraction levels — if a method's interface is as complex as its body, it isn't hiding anything.

## Pull complexity downward (Ch. 8)

Given a choice, it's usually better for a **module to handle complexity internally** than to expose it and make every caller deal with it. The module developer pays the cost once; all users benefit. Examples: provide good **defaults** so callers needn't configure; handle edge cases inside rather than documenting them as caller obligations. **Don't take it too far** — pulling down complexity that callers genuinely need to control, or that makes the module's interface worse, is wrong; the test is whether it *simplifies the overall system*.

## Better together or better apart? (Ch. 9)

Bring two pieces of functionality **together** when they: share information; are always used together; overlap conceptually; or doing so removes duplication or simplifies the interface. Keep them **apart** when: they're only weakly related, or one is general-purpose and the other special-purpose (separate those — a classic split). Subdivision adds interfaces, indirection, and the risk of conjoined components that are hard to understand separately. **Splitting/joining methods:** split a method only if it produces cleaner, independently-meaningful pieces (or removes duplication) — *not* merely to make methods shorter; a long method that does one thing cohesively can be clearer than two coupled fragments.
