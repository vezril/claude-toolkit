# Creational patterns

How objects get created, abstracting the instantiation so clients don't depend on concrete classes. Intent statements are quoted from GoF (1994); the Scala/FP mapping and critique are added.

## Contents

1. Abstract Factory
2. Builder
3. Factory Method
4. Prototype
5. Singleton

---

## 1. Abstract Factory

**Intent (GoF):** "Provide an interface for creating families of related or dependent objects without specifying their concrete classes." (a.k.a. *Kit*)

**Problem.** You need to create whole *families* of objects that must be used together and stay consistent (e.g. a UI toolkit's buttons, scrollbars, menus for a given look-and-feel), and you want to swap the entire family without touching client code.

**Structure.** An `AbstractFactory` interface declares a creation method per product. Each concrete factory produces one consistent family. Clients hold the abstract factory and abstract products only.

**Scala/FP.** Often just a record (case class) of constructor functions, or a typeclass instance selected implicitly: `trait WidgetFactory { def button(): Button; def scrollbar(): Scrollbar }`, with the chosen family passed in. The "family" guarantee is the real value.

**When to use / critique.** Worth it when there are genuinely multiple product families and a real need to switch among them; otherwise it's heavy indirection. Don't introduce it for a single family "in case."

## 2. Builder

**Intent (GoF):** "Separate the construction of a complex object from its representation so that the same construction process can create different representations."

**Problem.** Constructing an object involves many steps/options, or the same build sequence should yield different representations (e.g. an RTF reader driving either an ASCII converter or a widget tree).

**Structure.** A `Director` runs the construction steps against a `Builder` interface; concrete builders accumulate and return the product.

**Scala/FP.** For the common "too many constructor params" case, **default + named arguments** and immutable `case class` + `copy` usually suffice — no builder object needed. A fluent/immutable builder is worth it when construction is genuinely staged or validated incrementally. Prefer returning a new builder value over mutating one.

**When to use / critique.** Real builders shine for stepwise/validated construction or multiple output representations. The telescoping-constructor problem it classically fixes is already solved by named/default args in Scala.

## 3. Factory Method

**Intent (GoF):** "Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses." (a.k.a. *Virtual Constructor*)

**Problem.** A class needs to create collaborator objects but shouldn't hard-code their concrete type — subclasses (or callers) decide.

**Structure.** A creator declares an abstract `factoryMethod()` returning a product; subclasses override it to pick the concrete product.

**Scala/FP.** A plain **function returning the product**, or a companion-object `apply`, or simply passing a constructor function (`make: () => Product`). Subclassing-to-choose-a-type is rarely the right tool; pass the function.

**When to use / critique.** Reasonable when a framework must create objects whose type only the application knows. In FP it almost always collapses to "take a function."

## 4. Prototype

**Intent (GoF):** "Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype."

**Problem.** You want to create objects configured like an existing instance, or avoid a parallel factory hierarchy, by cloning a registered prototype.

**Structure.** A `Prototype` interface declares `clone()`; clients copy a prototype instead of calling a constructor.

**Scala/FP.** Largely dissolved by **immutability**: an immutable value can be shared freely, and "a variant of this" is `prototype.copy(field = ...)`. No deep-clone machinery, no shared-mutable-state hazard. See [[functional-programming]].

**When to use / critique.** Mostly relevant where objects are expensive to build from scratch but cheap to copy, or built dynamically at runtime. With immutable data it's a non-issue.

## 5. Singleton

**Intent (GoF):** "Ensure a class only has one instance, and provide a global point of access to it."

**Problem.** Exactly one instance must exist (one window manager, one config registry) and be globally reachable.

**Structure.** Private constructor + a static accessor returning the lone instance.

**Scala/FP.** Scala's `object Foo { ... }` *is* a lazily-initialized singleton, thread-safe by construction — no boilerplate.

**When to use / critique.** **Widely regarded as an anti-pattern.** It's global state in disguise: it hides dependencies (callers reach out to it instead of receiving it), couples code to a concrete instance, and wrecks testability (you can't substitute a fake). A stateless `object` (pure utilities) is fine; a *stateful* singleton is a red flag. Prefer **explicit dependency injection** — pass the dependency in — which is also what makes code testable (see [[tdd]]).
