---
name: design-patterns
description: "The 23 Gang of Four design patterns and the OO design principles behind them, from Gamma, Helm, Johnson & Vlissides' *Design Patterns: Elements of Reusable Object-Oriented Software* (1994) — what each pattern solves, its structure and trade-offs, when (and when not) to reach for it, and how it maps onto Scala/FP idioms (many GoF patterns collapse to language features). Covers the creational patterns (Abstract Factory, Builder, Factory Method, Prototype, Singleton), structural patterns (Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy), and behavioral patterns (Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor), plus the core principles \"program to an interface, not an implementation\" and \"favor object composition over class inheritance.\" Use whenever the user is designing or refactoring object-oriented code, asks about a named pattern or which pattern fits a problem, wants to reduce coupling or improve extensibility, mentions factories/observers/decorators/visitors/strategies/adapters/singletons etc., is reviewing a design for over-engineering, or wants the Scala/FP-idiomatic alternative to a classic OO pattern — even if they don't say \"design pattern.\""
---

# Design Patterns (Gang of Four)

The 23 patterns from Gamma, Helm, Johnson & Vlissides (1994), as a working advisor: each pattern's intent, the problem it solves, its trade-offs, when to use it — and, because the audience codes in Scala/FP, how it maps onto language features and functional idioms. The book is OO (C++/Smalltalk), but the *design judgment* generalizes.

If the user's explicit instructions conflict with this skill, the user wins.

## The point of patterns (and the warning that comes first)

A design pattern is a *named, reusable solution to a recurring design problem*, plus the trade-offs of applying it. Patterns are a **vocabulary** ("let's make that a Strategy") and a record of designs that survived real redesign for flexibility and reuse. They are not goals in themselves.

**Don't reach for a pattern first.** The single most important judgment is restraint. Patterns add indirection, and indirection is a cost paid in every read of the code. Apply a pattern only when there's a *real, present* variation or coupling problem it relieves — not speculatively. Most over-engineered codebases are patterns applied to problems that didn't exist yet. The book itself frames patterns as the designs you refactor *toward* under pressure, not the ones you start with. So: name the concrete pain first (this thing changes for two reasons; these two modules can't be swapped; adding a case touches ten files), then pick the pattern that relieves *that*.

## Two principles underneath everything

The catalog is mostly applications of two ideas from Chapter 1:

1. **Program to an interface, not an implementation.** Depend on the abstract type (what an object *does*), never a concrete class. Clients then don't know or care which implementation they hold, which decouples subsystems and lets implementations vary freely. (In Scala: depend on a `trait`/abstract type; in FP: depend on a function type.)
2. **Favor object composition over class inheritance.** Inheritance is compile-time, white-box, and rigid — a subclass is bound to its parent's implementation. Composition (an object holding and delegating to another) is run-time, black-box, and flexible; it keeps each class focused and lets behavior be reconfigured by swapping parts. Designers habitually overuse inheritance; most patterns achieve reuse by composition + **delegation** (an object forwards a request to a held delegate, passing itself if the delegate needs context).

A corollary the book stresses: **encapsulate what varies.** Find the aspect of your design that changes and isolate it behind a stable interface — that is, in one form or another, what every pattern does.

## How to select a pattern

Work from the problem, not the catalog: (1) state what *varies* and what must stay stable; (2) identify the kind of change you want cheap — object creation, object structure/composition, or object behavior/communication; that maps to the three families below; (3) read the candidate patterns' Intent and Consequences and pick the lightest one that removes the coupling; (4) consider whether a **language feature** already solves it (see the Scala/FP notes) before adding a pattern. Patterns also combine — a real design layers several.

## The three families

Detail lives in the category references — read the one matching the problem:

- **`references/creational.md`** — *how objects get made*, decoupling clients from concrete classes: **Abstract Factory, Builder, Factory Method, Prototype, Singleton**.
- **`references/structural.md`** — *how objects and classes are composed* into larger structures: **Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy**.
- **`references/behavioral.md`** — *how objects distribute responsibility and communicate*: **Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor**.

Each reference gives, per pattern: faithful Intent, the problem, brief structure, a Scala/FP mapping, and a when-to-use / critique.

## Catalog at a glance (intent + Scala/FP note)

| Pattern | Intent (GoF) | Scala/FP note |
|---|---|---|
| **Abstract Factory** | Interface for creating *families* of related objects without their concrete classes | Often a record of functions, or a typeclass instance |
| **Builder** | Separate construction of a complex object from its representation | Default/named args, `copy`, or a fluent builder; immutable case classes |
| **Factory Method** | Define an interface for creating an object, let subclasses choose the class | A function/companion `apply`; pass a constructor function |
| **Prototype** | Create objects by cloning a prototypical instance | Immutable data + `copy`; cloning is rarely needed |
| **Singleton** | One instance + global access point | `object` in Scala. **Often an anti-pattern** (global mutable state) |
| **Adapter** | Convert one interface into another clients expect | Wrapper class, extension methods, or a converting function |
| **Bridge** | Decouple an abstraction from its implementation so both vary | Compose a trait-typed field; pass behavior as a value |
| **Composite** | Tree structures; treat individual & composite objects uniformly | Recursive ADT (`sealed trait` + cases) + fold |
| **Decorator** | Add responsibilities to an object dynamically | Function composition; wrapper trait; middleware |
| **Facade** | One unified interface to a subsystem | A module/object exposing a small API |
| **Flyweight** | Share fine-grained objects to save memory | Interning/caching of immutable values; memoization |
| **Proxy** | A surrogate controlling access to another object | Lazy `val`, wrapper, or higher-order interception |
| **Chain of Responsibility** | Pass a request along handlers until one handles it | List of functions; `orElse` on `PartialFunction` |
| **Command** | Encapsulate a request as an object (queue, log, undo) | A function/closure, or a value (ADT) describing the action |
| **Interpreter** | Represent a grammar and interpret its sentences | ADT for the AST + recursive eval; parser combinators |
| **Iterator** | Sequential access to elements without exposing structure | Built in: `Iterator`, `LazyList`, for-comprehension |
| **Mediator** | Encapsulate how a set of objects interact (loose coupling) | A coordinator object/function; event bus |
| **Memento** | Capture/restore an object's state without breaking encapsulation | Snapshot an immutable value; persist/restore the data |
| **Observer** | One-to-many dependency: notify dependents on state change | FRP/streams (signals, `Observable`); callbacks |
| **State** | Alter behavior when internal state changes | State as an ADT + transition function `S => S` |
| **Strategy** | Encapsulate interchangeable algorithms | A higher-order function parameter — the canonical FP collapse |
| **Template Method** | Algorithm skeleton with steps deferred to subclasses | A higher-order function taking the varying steps |
| **Visitor** | New operations over an object structure without changing it | `sealed trait` + exhaustive pattern match (no Visitor needed) |

## Modern / critical lens (the audience asked for this)

- **Many GoF patterns are workarounds for what 1994 OO languages lacked.** First-class functions turn **Strategy, Command, Template Method, Factory Method**, and much of **Observer/Chain of Responsibility** into "pass a function." **Iterator** is built into every modern language. **Singleton** is `object` in Scala. So before formalizing a pattern, check whether a function, an ADT + pattern match, or a standard-library type already expresses it more directly.
- **ADTs + exhaustive pattern matching replace the Visitor double-dispatch dance.** GoF's Visitor exists because OO makes "add an operation over a fixed type hierarchy" hard; a `sealed trait` with `match` gives it for free and the compiler checks exhaustiveness. The trade-off (the "expression problem") is just inverted: Visitor/OO makes adding *types* easy and *operations* hard; ADTs make adding *operations* easy and *types* harder. Choose by which axis changes more.
- **Singleton is widely considered an anti-pattern** — it's global mutable state in disguise, hurting testability and hiding dependencies. Prefer passing dependencies explicitly (or a stateless `object`).
- **Immutability dissolves several patterns.** Prototype (clone) and Memento (snapshot) are trivial when values are immutable — just share or copy the data. See [[functional-programming]].
- **Patterns still earn their keep** for genuine structural problems: Adapter (interface mismatch), Facade (taming a subsystem), Composite (recursive structures), Decorator/Proxy (layering behavior), Bridge/Abstract Factory (independent variation across two axes). The judgment is to apply them to real coupling, not as decoration.

## Related

- [[functional-programming]] — ADTs, immutability, and pure functions that subsume Strategy/Command/Visitor/State/Memento/Prototype; "program to an interface" and "favor composition" are FP defaults.
- [[scala]] — concrete mechanics (`sealed trait` ADTs + exhaustive match, `object`, `copy`, higher-order functions, traits) used in the Scala/FP mappings.
- [[tdd]] — programming to interfaces and injecting dependencies (vs. Singletons) is what makes code testable.
- Source: *Design Patterns: Elements of Reusable Object-Oriented Software*, Gamma, Helm, Johnson & Vlissides (Addison-Wesley, 1994). Intent statements are quoted faithfully; Scala/FP mappings and critique are added for this repo's stack.
