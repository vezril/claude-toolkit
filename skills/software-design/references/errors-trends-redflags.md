# Complexity, errors, trends, performance, and the summaries

*A Philosophy of Software Design* (Ousterhout), Chapters 2, 10, 19–21, and the book's appendix summaries.

## The nature of complexity (Ch. 2)

**Complexity** = anything related to the structure of a system that makes it hard to understand or modify — measured by its effect on the people working on it, not by intuition. It's the sum over components weighted by how often developers touch them (a complex but rarely-touched corner matters less). **Symptoms:** *change amplification* (one logical change → edits in many places), *cognitive load* (how much a developer must know to do something), *unknown unknowns* (you can't tell what to change or what you need to know — the most dangerous, since you can't avoid a bug you can't see). **Causes:** *dependencies* (code that can't be understood/modified independently — not all are bad, but minimize and make obvious) and *obscurity* (important information not apparent — bad names, missing docs, inconsistency). It is **incremental**: each small complication seems harmless, but they compound — so adopt **zero tolerance** for new complexity rather than planning a future cleanup.

## Define errors out of existence (Ch. 10)

Exception handling is a major source of complexity (each `try/catch`, each exceptional path, multiplies states to reason about). Reduce the *number of places that handle exceptions*:
- **Define errors out of existence** — redesign the API so the exceptional case becomes normal. Examples: Java's `substring` throwing on out-of-range indices vs a definition that just clamps/returns what overlaps; Windows file deletion failing if open vs Unix's marking-for-deletion semantics; an `unset` that's a no-op if absent (idempotent). The best exception is the one that can't happen.
- **Mask exceptions** — handle them low in the stack so higher layers never see them (e.g. TCP masking packet loss).
- **Exception aggregation** — handle many exceptions in one place (one top-level handler) rather than at each throw site.
- **Just crash** — for truly unrecoverable errors (out of memory), crashing with a clear message is simpler and fine; don't write elaborate recovery for cases you can't recover from.
- **Design special cases out of existence** — make the general case handle what would otherwise be a special case (e.g. an empty selection behaves like any selection). **Don't take it too far** — don't throw away genuinely useful error information or define away errors callers *need* to know about.

**Scala/FP:** this is "make illegal states unrepresentable" + errors-as-values — `Option`/`Either`/an error ADT turn the error into ordinary data handled once, and smart constructors prevent the bad state up front (see [[functional-programming]]).

## Software trends (Ch. 19) — apply with judgment

Ousterhout evaluates trends by whether they reduce complexity:
- **OOP & inheritance** — useful, but **implementation inheritance creates dependencies** (fragile base class); prefer **composition / interface inheritance**. (Echoes [[design-patterns]] "favor composition.")
- **Agile** — good for incremental development, but its feature-increment focus can push teams *tactical*; keep increments of *abstraction*, not just features.
- **Unit tests** — endorsed; they enable refactoring and catch regressions (see [[tdd]]).
- **Test-driven development** — Ousterhout is **critical**: writing tests first focuses attention on getting specific features working (tactical) rather than on the best design; he suggests designing in larger chunks and using tests to validate, not to drive every step. (A genuinely debated view — weigh against [[tdd]].)
- **Design patterns** — valuable when they fit, but **overuse** (forcing a pattern where a simpler design works) adds complexity; reach for one because it deepens the design.
- **Getters/setters** — mostly boilerplate that exposes fields; don't add them reflexively (prefer real behavior / deeper interfaces).

## Designing for performance (Ch. 20)

- Don't sacrifice clean design for speculative speed; **simpler code is usually faster** and always easier to optimize.
- **Measure before modifying** — find the real critical path with a profiler; intuition about hotspots is often wrong.
- **Design around the critical path** — once measured, design the fundamental data structures/operations so the common case is naturally fast (the RAMCloud `Buffer` example), rather than scattering micro-optimizations.
- Performance work that *also* simplifies (removing special cases) is the ideal.

## Summary of Design Principles (appendix)

1. Complexity is incremental: isolate it and resist it continuously.
2. Working code isn't enough — invest in design (strategic, not tactical).
3. Make continual small investments to improve system design.
4. Modules should be deep.
5. Interfaces should be designed to make the *common* case as simple as possible.
6. It's more important for a module to have a simple interface than a simple implementation.
7. General-purpose modules are deeper.
8. Separate general-purpose and special-purpose code.
9. Different layers should have different abstractions.
10. Pull complexity downward.
11. Define errors (and special cases) out of existence.
12. Design it twice.
13. Comments should describe things that aren't obvious from the code.
14. Software should be designed for ease of *reading*, not ease of writing.
15. The increments of software development should be abstractions, not features.

## Summary of Red Flags (appendix)

- **Shallow Module** — interface complexity high relative to functionality.
- **Information Leakage** — a design decision reflected in multiple modules.
- **Temporal Decomposition** — structure mirrors execution order, exposing knowledge.
- **Overexposure** — using a common feature forces learning rarely-used ones.
- **Pass-Through Method** — does little but forward to another with a similar signature.
- **Repetition** — a snippet appears again and again (DRY).
- **Special-General Mixture** — special-purpose code tangled with general-purpose.
- **Conjoined Methods** — two pieces only understandable by looking at both.
- **Comment Repeats Code** — adds no information beyond the code.
- **Implementation Documentation Contaminates Interface** — interface comment describes implementation details a caller shouldn't need.
- **Vague Name** — too imprecise to convey useful information.
- **Hard to Pick Name** — difficulty naming suggests an unclear/poor design.
- **Hard to Describe** — the doc for a method/variable is long/complicated → the thing is too complex.
- **Nonobvious Code** — behavior/meaning can't be understood quickly.

Use the red flags as review prompts; each points at complexity worth removing.
