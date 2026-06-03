# Behavioral patterns

How objects distribute responsibility and communicate. This is where first-class functions and ADTs collapse the most GoF machinery, so the Scala/FP notes matter most here. Intent statements quoted from GoF (1994).

## Contents

1. Chain of Responsibility
2. Command
3. Interpreter
4. Iterator
5. Mediator
6. Memento
7. Observer
8. State
9. Strategy
10. Template Method
11. Visitor

---

## 1. Chain of Responsibility

**Intent (GoF):** "Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it."

**Problem.** Multiple objects might handle a request and you don't want the sender to know which; the handler set should be configurable (e.g. context-sensitive help, event bubbling, middleware).

**Scala/FP.** A **list of handler functions** tried in order, or `PartialFunction` composed with `orElse` (each handler is defined only where it applies; `orElse` falls through). `foldRight` over middleware also models a chain.

**When to use / critique.** Good for pipelines/fallback handling. Risk: a request silently falling off the end unhandled — make the terminal case explicit.

## 2. Command

**Intent (GoF):** "Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations." (a.k.a. *Action, Transaction*)

**Problem.** You want to treat an action as a value — to queue it, log it, parameterize a widget with it, or support undo/redo.

**Scala/FP.** A **function/closure** (`() => Unit`, or `State => State`) is the lightweight Command. For logging/undo/serialization, model commands as an **ADT** (`sealed trait Command` with cases) and interpret them — data you can inspect, persist, and reverse. Undo = keep the inverse, or keep prior state (see Memento).

**When to use / critique.** Very useful (undo stacks, job queues, event sourcing). The OO command-object-with-`execute()` is usually just a function or a data value in FP.

## 3. Interpreter

**Intent (GoF):** "Given a language, define a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language."

**Problem.** A simple, recurring language/grammar (regex, boolean expressions, a DSL) is worth representing explicitly and evaluating.

**Scala/FP.** An **ADT for the abstract syntax tree** + a recursive `eval` (a fold over the tree) — exactly how FP builds interpreters. Pair with **parser combinators** for the front end. This is one of FP's home turfs.

**When to use / critique.** Fine for small, stable grammars; for anything sizable use a real parser/AST toolchain rather than hand-rolled interpreter classes. Overkill for one-off parsing.

## 4. Iterator

**Intent (GoF):** "Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation." (a.k.a. *Cursor*)

**Scala/FP.** **Built into the language and library**: `Iterator`, `Iterable`, `LazyList`, and for-comprehensions. You essentially never implement this by hand; you implement the standard collection traits and get iteration for free.

**When to use / critique.** Historically important, now a solved problem in every modern language. Implement a custom iterator only for a bespoke lazy/streaming source.

## 5. Mediator

**Intent (GoF):** "Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly, and it lets you vary their interaction independently."

**Problem.** A set of objects (e.g. widgets in a dialog) reference each other directly, creating a tangle of many-to-many coupling. Route their interaction through one mediator so each only knows the mediator.

**Scala/FP.** A **coordinator object/function** that owns the interaction logic; or an **event bus / message hub** the components publish to. Components depend on the channel, not each other.

**When to use / critique.** Helps when n-to-n coupling among peers is real. Risk: the mediator becomes a god object — keep its responsibility to *coordination*, not everything.

## 6. Memento

**Intent (GoF):** "Without violating encapsulation, capture and externalize an object's internal state so that the object can be restored to this state later." (a.k.a. *Token*)

**Problem.** You need checkpoints/undo: save an object's state and restore it later, without exposing its internals.

**Scala/FP.** With **immutable data** this is trivial — the value *is* its own memento; "save" is keeping a reference, "restore" is rebinding it. No special encapsulation dance needed. See [[functional-programming]].

**When to use / critique.** Core to undo and transactional rollback. The GoF machinery (opaque memento objects guarding mutable state) mostly evaporates under immutability.

## 7. Observer

**Intent (GoF):** "Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically." (a.k.a. *Dependents, Publish-Subscribe*)

**Problem.** Several objects must stay in sync with one subject's state (the classic MVC: multiple views on one model) without the subject being coupled to concrete observers.

**Scala/FP.** **Functional reactive programming / streams** — signals, `Observable`/`Stream`, or event streams — express "derived values that update automatically" declaratively. Lightweight version: a list of callback functions the subject invokes.

**When to use / critique.** Ubiquitous and useful, but classic mutable Observer is a notorious source of bugs: update ordering, re-entrancy, memory leaks from un-removed listeners, and cascade storms. Prefer a principled streams/FRP library that manages subscription lifecycle.

## 8. State

**Intent (GoF):** "Allow an object to alter its behavior when its internal state changes. The object will appear to change its class."

**Problem.** An object's behavior depends on a mode that changes at runtime (e.g. `TCPConnection`: Established / Listening / Closed), and you want to avoid sprawling conditionals on a state field.

**Scala/FP.** Model state as a **`sealed trait` ADT** and transitions as a pure function `(State, Event) => State`; behavior is a `match` on the current state. Exhaustiveness checking ensures every state handles every event. See [[scala]].

**When to use / critique.** Good when there's a real state machine. The ADT + transition-function form is clearer and safer than swapping behavior objects, and makes illegal transitions representable-or-not by design.

## 9. Strategy

**Intent (GoF):** "Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it." (a.k.a. *Policy*)

**Scala/FP.** The **canonical collapse to a higher-order function**: pass the algorithm as a function parameter (`sort(xs)(comparator)`, `process(data)(strategy)`). The whole pattern is "take a function." A typeclass is the right tool when the strategy should be chosen by type.

**When to use / critique.** The need (interchangeable algorithms) is real and constant; in FP you almost never build Strategy *objects* — you pass functions. If you find yourself writing a `Strategy` interface with one method, make it a function.

## 10. Template Method

**Intent (GoF):** "Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure."

**Problem.** Several algorithms share a fixed overall structure but differ in specific steps; you want to write the skeleton once.

**Scala/FP.** A **higher-order function** that implements the skeleton and takes the varying steps as function arguments — composition instead of the inheritance/override the GoF version uses. (It's "inverted Strategy": Strategy passes the whole algorithm; Template Method fixes the outline and passes the holes.)

**When to use / critique.** Useful for genuine shared skeletons (resource setup/teardown, parsing frames). Prefer passing functions over an abstract-base-class-with-hooks, which couples subclasses to the base.

## 11. Visitor

**Intent (GoF):** "Represent an operation to be performed on the elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates."

**Problem.** You have a fixed object structure (e.g. an AST) and want to add many *operations* over it without editing every element class each time. Visitor uses double dispatch to externalize operations.

**Scala/FP.** **`sealed trait` ADT + exhaustive pattern match** gives this directly: define a new operation as a new function that matches over the cases — no visitor interface, no `accept`/`visit` double-dispatch boilerplate, and the compiler checks you handled every case. This is the idiomatic replacement.

**When to use / critique.** This is the **expression problem** in sharp form. Visitor/OO makes adding new *element types* hard (touch every visitor) but new *operations* easy; ADTs + match make adding *operations* easy but new *types* hard (touch every match). Pick by which axis changes more often: stable type set + growing operations → ADT/match (the FP default); growing type set + stable operations → an OO/Visitor-ish or typeclass approach.
