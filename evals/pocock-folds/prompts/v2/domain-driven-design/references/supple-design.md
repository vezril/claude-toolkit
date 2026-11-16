# Supple design & refactoring toward deeper insight

DDD Part III: how to make a model that's a pleasure to work with, and how to keep deepening it. Most of this is strikingly aligned with functional design. Definitions faithful to Evans (2003); Scala/FP mapping and notes added.

## Contents

1. The goal: refactoring toward deeper insight
2. Making implicit concepts explicit
3. Intention-Revealing Interfaces
4. Side-Effect-Free Functions
5. Assertions
6. Conceptual Contours
7. Standalone Classes
8. Closure of Operations
9. Specification
10. Declarative Design

---

## 1. The goal: refactoring toward deeper insight

A good model isn't designed up front; it's *discovered*. You implement a naive model, work with it, and each time the team understands the domain better you **refactor the model** — not just the code's structure, but the concepts themselves — to reflect that insight. Occasionally this yields a **breakthrough**: a sudden, much deeper model that triggers a cascade of clarifying changes. Supple design is what makes a model *amenable* to this continual reshaping: pliable, with parts you can recombine without fear.

**FP note.** This loop depends on a fast, reliable test suite over a pure domain (see [[tdd]]) — pure functions and immutable values are cheap to test, which is what makes aggressive refactoring safe.

## 2. Making implicit concepts explicit

Listen to the domain experts' language and to awkwardness in the design; a word they keep using, or a rule that's scattered across many methods, is often a **missing concept**. Pull it out into an explicit model element — frequently a Value Object or a Specification. Examples: an implicit "overbooking policy" buried in `if` statements becomes an explicit `OverbookingPolicy`; a relationship becomes a first-class object; a constraint becomes a Specification.

**FP note.** This is the same instinct as introducing an ADT or a named value type instead of passing raw primitives — give the concept a type.

## 3. Intention-Revealing Interfaces

**Name classes and operations to describe their effect and purpose, without referring to the means of achieving them.** A caller should be able to use a component knowing only *what* it does, by its name and signature, never needing to read the implementation. Names come from the Ubiquitous Language. This is the precondition for everything else — you can't compose parts suppleness if using each one requires studying its internals.

**Scala/FP.** Domain-meaningful method/type names; a function's type signature should tell the story (`transfer(from: Account, to: Account, amount: Money): Either[TransferError, (Account, Account)]`).

## 4. Side-Effect-Free Functions

**Place as much of the program's logic as possible into functions — operations that return results with no observable side effects.** Commands (which change state) should be kept separate, simple, and free of domain logic / return values. Operations that compute and return a **Value Object** without modifying anything are safe to call freely and combine in complex expressions, because they can't break anything.

**Scala/FP.** This is literally **purity** from [[functional-programming]]: compute new immutable value objects instead of mutating; segregate the few state-changing commands at the edge (command–query separation). Evans is describing a pure functional core in 2003.

## 5. Assertions

**State the post-conditions of operations and the invariants of aggregates explicitly**, so the meaning of an operation is defined by *what it guarantees*, not by tracing its implementation. Where the language can't enforce them at runtime/compile time, capture them in tests and document them in the model.

**Scala/FP.** Encode invariants in **types** (smart constructors, refined/value types) so the compiler enforces them — the strongest form of assertion. What types can't capture, lock down with tests ([[tdd]]). See [[scala]] on `sealed abstract case class` and `assertDoesNotCompile`.

## 6. Conceptual Contours

**Decompose design elements along the underlying conceptual contours of the domain** — find the natural "joints" where the domain itself divides, so that frequent changes align with module/object boundaries instead of cutting across them. Repeated painful refactors that always touch the same scattered spots are a sign your boundaries don't match the domain's; reshape until they do.

**FP note.** Cohesive ADTs and modules carved at domain seams; high cohesion / low coupling expressed in domain terms, not technical layers.

## 7. Standalone Classes

**Drive down dependencies until a class (or module) can be understood on its own**, in conjunction with only a couple of fundamental concepts. Low coupling isn't just for compilation — every dependency is something a reader must hold in their head. The most valuable place to achieve self-containment is in a highly used, conceptually central module.

**Scala/FP.** Prefer types that depend only on primitives/other value objects; pass collaborators as function arguments rather than wiring in many fields.

## 8. Closure of Operations

**Where it fits, define an operation whose return type is the same as the type of its argument(s)** — the operation is then "closed" under that type, needs no extra concepts, and composes freely (think integer addition: `Int × Int → Int`). Closed operations on value objects are highly composable.

**Scala/FP.** An endomorphism `A => A` (or `(A, A) => A`) — exactly a **monoid/semigroup** combine. This is why value objects compose so well; Cats' `Monoid`/`Semigroup` formalize it. Closed, side-effect-free operations are the most suppleness-producing things you can build.

## 9. Specification

**A predicate-like Value Object that states a constraint or selects objects matching a business rule** ("a delinquent invoice," "a preferred customer"). Specifications make a rule explicit and reusable for three jobs: **validation** (does this object satisfy it?), **selection/querying** (find objects that satisfy it — often handed to a Repository), and **construction** (build something to satisfy it). They **compose** with `and`, `or`, `not`.

**Scala/FP.** A composable predicate `A => Boolean` (or a small ADT of criteria you can also compile to a query). Combine with boolean combinators; this is a Value Object, so it's immutable and shareable. Directly recalls Strategy/Composite from [[design-patterns]].

## 10. Declarative Design

The aspiration tying the above together: a style where you **describe rules and intentions as composable, executable statements** rather than step-by-step procedures — e.g. a Specification combined from smaller specs reads like the business rule itself. Supple building blocks (intention-revealing, side-effect-free, closed, asserted) make a small **domain-specific language** within the model possible.

**Scala/FP.** Combinator libraries and embedded DSLs (parser combinators, predicate algebras, monoidal composition) are the FP realization. Declarative, value-based composition over imperative orchestration.
