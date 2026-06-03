---
name: modern-java
description: Best practices for writing modern Java (Java 21 LTS), distilled from Joshua Bloch's *Effective Java* (3rd ed., all 90 items) and updated with current language features (records, sealed types, pattern matching for switch and record patterns, virtual threads, text blocks, sequenced collections, enhanced instanceof, var). Covers object creation and destruction, methods common to all objects (equals/hashCode/toString/Comparable), classes and interfaces, generics, enums and annotations, lambdas and streams, method design, exceptions, concurrency, and serialization. Use this whenever writing, reviewing, refactoring, or designing ANY Java code — defining a class, API, or method; choosing between a class and a record; handling errors; writing generics; using streams or Optionals; doing concurrency; or deciding an idiom — even if the user doesn't say "Effective Java" or "best practices." Apply these defaults proactively on any .java work: prefer immutability, program to interfaces, fail fast, and use modern Java features over their legacy equivalents.
---

# Modern Java

How to write clear, correct, robust Java, targeting **Java 21 LTS**. The foundation is Joshua Bloch's *Effective Java* (3rd ed., 90 items); this skill keeps his reasoning but **defaults to modern language features** (records, sealed types, pattern matching, virtual threads, etc.) where they supersede the 2018 advice, and flags what's now dated. Apply these as defaults on any Java code, not only when asked.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Otherwise this is the default style.

## Guiding principles (from the book's introduction)

Most items derive from a few ideas — when in doubt, fall back to these:

- **Clarity and simplicity first.** A component's user should never be surprised by its behavior. Make components as small as possible but no smaller. This skill is *not* primarily about performance — write clear, correct code, then optimize only where measurement demands it (Item 67).
- **Fail fast.** Detect errors as soon as possible, ideally at compile time, otherwise as early as possible at runtime (validate parameters, Item 49). Push correctness into the type system.
- **Minimize mutability and accessibility.** Immutable objects and the smallest possible API surface are the two most reliable ways to reduce bugs.
- **Program to interfaces; favor composition over inheritance.** Depend on abstractions; reach for composition before subclassing.
- **Rules are defaults, not laws.** Violate them occasionally with good reason — but know the rule first.

## Modern Java baseline (Java 21) — default to these

Bloch's 2018 text predates much of this. On Java 21, prefer:

- **`record`** for immutable data carriers — replaces most hand-written value classes, the telescoping-constructor problem, much of the Builder boilerplate, and auto-generates `equals`/`hashCode`/`toString` (Items 10–12, 17). Add compact constructors for validation/normalization and defensive copies.
- **`sealed` interfaces/classes + pattern matching** — a sealed hierarchy of records is an **algebraic data type**; `switch` with pattern matching (and record patterns) handles it exhaustively, with the compiler checking all cases. This is the modern replacement for tagged classes (Item 23) and for the Visitor pattern. Prefer it for closed type hierarchies.
- **`switch` expressions** (arrow form, exhaustive, yields a value) over fall-through statement switches.
- **Pattern matching for `instanceof`** — `if (o instanceof String s) {…}` — over cast-after-check.
- **Virtual threads** (Item 80 updated) — for high-concurrency blocking I/O, `Executors.newVirtualThreadPerTaskExecutor()`; cheap to create, so "thread per task" is again viable. Still prefer the `java.util.concurrent` executors/tasks model over raw threads.
- **Text blocks** (`"""…"""`) for multi-line strings.
- **`var`** for local variables when the initializer makes the type obvious (Item 57 spirit: keep scope tight, names clear) — not for fields or APIs.
- **Sequenced collections** (`SequencedCollection`/`getFirst`/`getLast`) and the modern collection factories (`List.of`, `Map.of`, `Stream.toList()`).
- **`Optional`** as a return type for "maybe absent" (Item 55) — never for fields or parameters, and never `Optional.get()` without checking.

## How to use this skill

The 90 items, faithfully covered and modernized, live in four thematic references — read the one matching the task:

- **`references/objects-and-classes.md`** — Items 1–25: creating/destroying objects (static factories, builders, DI, avoiding finalizers, try-with-resources), methods common to all objects (`equals`, `hashCode`, `toString`, `clone`, `Comparable`), and class/interface design (accessibility, **immutability**, composition over inheritance, interfaces, **records & sealed types**). Read for "how do I define this class/type/API."
- **`references/generics-enums-functional.md`** — Items 26–48: generics (no raw types, wildcards, generic methods), enums & annotations (enums over int constants, `EnumSet`/`EnumMap`), and lambdas & streams (lambdas/method refs, standard functional interfaces, side-effect-free streams, `Collection` vs `Stream` returns). Read for generics, enums, or functional-style code.
- **`references/methods-exceptions-general.md`** — Items 49–77: method design (validate params, defensive copies, signatures, overloading/varargs, return empties not null, `Optional`, Javadoc), general programming (scope, for-each, know the libraries, avoid float/double for money, boxing, strings), and exceptions (checked vs unchecked, standard exceptions, failure atomicity, don't ignore). Read for method/API signatures or error handling.
- **`references/concurrency-and-serialization.md`** — Items 78–90: concurrency (synchronize shared mutable state, prefer executors/tasks + **virtual threads**, `java.util.concurrent` over `wait`/`notify`, document thread safety) and serialization (avoid Java serialization; if forced, defensive `readObject`, serialization proxies). Read for threading or serialization.

## Always-apply defaults (the short list)

When writing Java without a specific question, these change the most code and should be automatic:

1. **Make classes immutable** unless there's a reason not to; if mutable, minimize mutability. Use `record` for data; `final` fields; no setters.
2. **Minimize accessibility** — everything as private as possible; no public fields (use accessors, or a record's accessors).
3. **Favor composition over inheritance;** design for inheritance or forbid it (`final`/sealed). Prefer interfaces to abstract classes.
4. **Static factory methods** over public constructors when naming, caching, or returning a subtype helps (Item 1).
5. **No raw types; fix all unchecked warnings** (Items 26–27). Prefer generic, type-safe APIs.
6. **Validate parameters and fail fast;** make defensive copies of mutable inputs/outputs (Items 49–50).
7. **Return empty collections/arrays, never null;** use `Optional` for scalar "maybe" returns (Items 54–55).
8. **Exceptions for exceptional conditions only;** unchecked for programming errors, checked only for recoverable conditions you expect callers to handle; never swallow an exception (Items 69–77).
9. **`equals`/`hashCode` together or not at all;** prefer records so the compiler writes them correctly (Items 10–11).
10. **Prefer the standard libraries** (`java.util`, `java.util.concurrent`, `java.util.function`) over rolling your own (Item 59).

## Notable anti-patterns (flag these in review)

- Mutable public fields; setters everywhere; God objects.
- Raw types (`List` instead of `List<String>`); suppressing unchecked warnings without justification.
- Returning `null` for collections/absent values; `Optional` fields or parameters; `optional.get()` without `isPresent`.
- Tagged classes / `int` "type" constants / `switch` on a type code — use sealed types + pattern matching or enums.
- `equals` without `hashCode`; hand-written `equals`/`hashCode`/`toString` where a record fits.
- Inheritance for code reuse across package boundaries; subclassing a class not designed for it.
- Checked exceptions for unrecoverable errors; empty `catch` blocks; exceptions for control flow.
- Raw `Thread`/`wait`/`notify`; sharing mutable state without synchronization; `synchronized` over-broadly.
- Implementing `Serializable` casually; using Java serialization for new designs (use JSON/protobuf etc.).
- `float`/`double` for money (use `BigDecimal` or integer cents); String concatenation in loops (use `StringBuilder`).

## Related

- [[design-patterns]] — Bloch references GoF throughout; static factories, builders, and the sealed-type/pattern-matching replacement for Visitor connect directly.
- [[functional-programming]], [[scala]] — many EJ principles (immutability, ADTs via sealed types + records, programming to interfaces, errors as values via `Optional`) are FP ideas; useful context since this repo's primary language is Scala, though this skill is pure Java.
- [[tdd]] — fail-fast validation and small, interface-based components are what make Java code testable.
- Source: *Effective Java*, 3rd ed., Joshua Bloch (Addison-Wesley, 2018), all 90 items. Item rules are faithful; the Java 21 modernizations (records, sealed types, pattern matching, virtual threads, etc.) and "default to modern" stance are added per request.
