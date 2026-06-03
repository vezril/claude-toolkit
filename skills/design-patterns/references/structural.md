# Structural patterns

How classes and objects are composed into larger structures while keeping them flexible. Intent statements quoted from GoF (1994); Scala/FP mapping and critique added.

## Contents

1. Adapter
2. Bridge
3. Composite
4. Decorator
5. Facade
6. Flyweight
7. Proxy

---

## 1. Adapter

**Intent (GoF):** "Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces." (a.k.a. *Wrapper*)

**Problem.** You have a useful class but its interface doesn't match what a client needs (often integrating a third-party or legacy library).

**Structure.** *Object adapter*: the adapter holds an instance of the adaptee and translates calls. *Class adapter*: multiple-inheritance (less relevant outside C++).

**Scala/FP.** A small wrapper class, **extension methods** (`implicit class` / Scala 3 `extension`) to add the expected interface, or just a **converting function** `Foreign => Expected`. Prefer object adaptation/composition.

**When to use / critique.** A genuinely useful, common pattern — interface mismatch at boundaries is real. Keep the adapter thin; don't let it accrete logic.

## 2. Bridge

**Intent (GoF):** "Decouple an abstraction from its implementation so that the two can vary independently." (a.k.a. *Handle/Body*)

**Problem.** Both an abstraction and its implementation have several variants, and binding them by inheritance gives a combinatorial class explosion (e.g. `Window` × platform). You want the two dimensions to vary independently.

**Structure.** The abstraction holds a reference to an `Implementor` interface and forwards work to it; abstraction and implementor hierarchies evolve separately.

**Scala/FP.** **Compose** rather than inherit: the abstraction takes a trait-typed (or function-typed) implementation value. This is the "favor composition" principle applied to two axes of variation.

**When to use / critique.** Use when you truly have two independent dimensions; otherwise it's premature. Easy to confuse with Adapter — Bridge is designed in up front to separate axes; Adapter retrofits a mismatch.

## 3. Composite

**Intent (GoF):** "Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions of objects uniformly."

**Problem.** You have part-whole trees (graphics groups, file systems, UI containers) and want clients to treat a leaf and a composite the same way.

**Structure.** A `Component` interface is implemented by both `Leaf` and `Composite`; the composite holds children of the component type and forwards operations to them.

**Scala/FP.** A **recursive ADT**: `sealed trait Node; case class Leaf(...); case class Branch(children: List[Node])`, processed with recursion/`fold`. Pattern matching makes "treat uniformly, distinguish when needed" natural and exhaustiveness-checked. See [[scala]].

**When to use / critique.** Strong, frequently-justified pattern wherever data is genuinely tree-shaped. The ADT form is the idiomatic FP expression.

## 4. Decorator

**Intent (GoF):** "Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality." (a.k.a. *Wrapper*)

**Problem.** You want to add behavior (a border, scrolling, buffering, compression) to individual objects without subclassing every combination.

**Structure.** A decorator implements the same interface as the component it wraps, holds a component, and adds behavior before/after delegating. Decorators nest.

**Scala/FP.** **Function composition** is decoration: `f andThen g`, wrapping a handler in middleware (`Handler => Handler`), or layering streams/transformers. A wrapper trait works too. This is composition over inheritance in its purest form.

**When to use / critique.** Excellent for stackable, optional responsibilities (the I/O-stream model). Watch for too many tiny decorators making flow hard to trace.

## 5. Facade

**Intent (GoF):** "Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use."

**Problem.** A subsystem is complex; most clients need only a simple, common slice of it and shouldn't couple to its internals.

**Structure.** One facade object exposes a small high-level API and delegates to the subsystem; advanced clients can still reach past it.

**Scala/FP.** A **module/`object`** (or a single entry-point function) exposing a minimal public API over internal pieces. Just good API design.

**When to use / critique.** Cheap, low-risk, broadly useful for taming complexity and decoupling. One of the patterns you can apply liberally.

## 6. Flyweight

**Intent (GoF):** "Use sharing to support large numbers of fine-grained objects efficiently."

**Problem.** A naive design would create huge numbers of nearly-identical small objects (e.g. one object per character glyph), exhausting memory. Split each object's **intrinsic** (shareable) state from **extrinsic** (context-dependent) state, and share the intrinsic part.

**Structure.** A factory hands out shared flyweight instances keyed by intrinsic state; extrinsic state is passed in by the client at use time.

**Scala/FP.** **Interning/caching** of immutable values (immutability is what makes sharing safe), or **memoization** of constructors. The intrinsic/extrinsic split is "pass the context as an argument instead of storing it."

**When to use / critique.** A performance optimization — apply only when profiling shows the object count is the problem. Don't pre-optimize.

## 7. Proxy

**Intent (GoF):** "Provide a surrogate or placeholder for another object to control access to it." (a.k.a. *Surrogate*)

**Problem.** You need to interpose on access to an object: defer expensive creation (virtual proxy), represent a remote object (remote proxy), check permissions (protection proxy), or add caching/logging.

**Structure.** The proxy implements the subject's interface, holds or creates the real subject, and forwards requests, doing its extra work around them.

**Scala/FP.** **Lazy `val`** is a virtual proxy (defer construction until first use); a wrapper or higher-order function gives logging/caching/auth interception. Caching proxies overlap with memoization.

**When to use / critique.** Justified when access genuinely needs control (laziness, remoteness, protection). Structurally like Decorator (same interface, wraps a subject) but the intent differs: Proxy controls *access*, Decorator adds *responsibilities*.
