# Items 1–25: Objects, common methods, classes & interfaces

Effective Java 3rd ed., Items 1–25, faithful to Bloch and updated for Java 21. Modern notes flag where records, sealed types, and pattern matching change the default.

## Contents

- Creating and Destroying Objects (1–9)
- Methods Common to All Objects (10–14)
- Classes and Interfaces (15–25)

---

## Creating and destroying objects

**1. Consider static factory methods instead of constructors.** Factories have names (clarify intent), can cache/return preexisting instances (instance control), can return any subtype, and can vary the returned class by input. Conventions: `of`, `valueOf`, `from`, `getInstance`, `newInstance`. Downside: classes without public/protected constructors can't be subclassed (often fine).

**2. Consider a builder when faced with many constructor parameters.** Telescoping constructors don't scale and JavaBeans (setters) leave objects in inconsistent, mutable states. A builder gives readable, safe construction. **Modern:** for a plain immutable data holder prefer a **`record`** with a compact constructor; reserve the Builder for many *optional* params or staged/validated construction.

**3. Enforce the singleton property with a private constructor or an enum.** A single-element **enum** is the best singleton (concise, serializable, reflection-proof). But remember a stateful singleton is hard to test (Item 5 / DI is usually better).

**4. Enforce noninstantiability with a private constructor.** For utility classes of static methods, a private constructor (that throws) prevents instantiation. **Modern:** put static helpers on an interface where it reads better; still, prefer instances + DI over piles of statics.

**5. Prefer dependency injection to hardwiring resources.** Don't `new` or hardcode a class's dependencies; pass them in (constructor injection). Improves flexibility, testability, reuse. The antidote to Item 3's singleton/global-state trap.

**6. Avoid creating unnecessary objects.** Reuse immutable objects and expensive-to-create objects (e.g. compiled `Pattern`); beware autoboxing creating garbage. Don't take this as a license for object pooling of cheap objects — the JVM is good at that.

**7. Eliminate obsolete object references.** Null out references you no longer need only where you manage your own memory (e.g. a stack's popped slots), watch caches and listener registrations — common memory-leak sources.

**8. Avoid finalizers and cleaners.** Unpredictable, slow, dangerous. For cleanup, implement **`AutoCloseable`** and use **try-with-resources** (Item 9); cleaners only as a safety net at best.

**9. Prefer try-with-resources to try-finally.** Cleaner, correct (no suppressed-exception bugs), works with multiple resources. Always use it for anything `AutoCloseable`.

## Methods common to all objects

**10. Obey the general contract when overriding `equals`.** Reflexive, symmetric, transitive, consistent, non-null. Don't violate symmetry/transitivity by comparing across types. Often you shouldn't override it at all. **Modern: a `record` generates a correct value-based `equals` for you — prefer it.**

**11. Always override `hashCode` when you override `equals`.** Equal objects must have equal hash codes. Use `Objects.hash(...)` or a good manual combination. **Modern:** records do this correctly automatically.

**12. Always override `toString`.** Provide a useful, informative representation; document the format (or that it may change). Records auto-generate a reasonable `toString`.

**13. Override `clone` judiciously.** The `Cloneable`/`clone` mechanism is broken. **Prefer a copy constructor or copy/static factory** instead. With immutable objects you rarely need copies at all.

**14. Consider implementing `Comparable`.** For value classes with a natural ordering, implement `compareTo` consistent with `equals`. Build comparators with the **`Comparator`** combinators (`comparing`, `thenComparing`) rather than error-prone hand-written subtraction.

## Classes and interfaces

**15. Minimize the accessibility of classes and members.** The most important rule of API design: make everything as private as possible; expose the minimal interface. Aids decoupling, testing, and safe evolution. **Modules** (Item 15, Java 9) add another encapsulation layer.

**16. In public classes, use accessor methods, not public fields.** Public mutable fields break encapsulation and prevent invariants. **Modern:** a `record`'s accessors satisfy this for immutable data.

**17. Minimize mutability.** Make classes immutable unless there's a reason not to: no setters, `final` class (or sealed), `final` private fields, defensive copies of mutable components, ensure exclusive access to any mutable internals. Immutable objects are simple, thread-safe, freely shareable. **Modern: `record` is the default immutable carrier**; for richer immutables keep the five rules.

**18. Favor composition over inheritance.** Inheritance across package boundaries is fragile (it breaks encapsulation; subclass depends on superclass implementation details). Prefer a wrapper (decorator) holding the component and forwarding. See [[design-patterns]].

**19. Design and document for inheritance, or else prohibit it.** If a class isn't designed and documented for subclassing, make it `final` (or use sealed permits). Document self-use of overridable methods; never call overridable methods from constructors.

**20. Prefer interfaces to abstract classes.** Interfaces allow mixins, multiple inheritance of type, and non-hierarchical types; default methods let you provide implementations. A skeletal implementation (`AbstractXxx`) can combine the benefits.

**21. Design interfaces for posterity.** Default methods (Java 8) let you add methods to interfaces, but they can break existing implementors — design carefully; don't rely on defaults to fix a bad interface.

**22. Use interfaces only to define types.** Don't use an interface just to export constants (the "constant interface" anti-pattern); use a utility class, enum, or static imports.

**23. Prefer class hierarchies to tagged classes.** A class with a "type" field and a `switch` on it is a verbose, error-prone substitute for a subtype hierarchy. **Modern: model it as a `sealed interface` + `record` cases and use pattern-matching `switch` — an algebraic data type with compiler-checked exhaustiveness.** This is the idiomatic modern replacement.

**24. Favor static member classes over nonstatic.** A nonstatic inner class holds a hidden reference to its enclosing instance (memory leaks, cost). If a member class doesn't need the enclosing instance, make it `static`.

**25. Limit source files to a single top-level class.** Multiple top-level classes in one file causes order-dependent compilation bugs. One public type per file.
