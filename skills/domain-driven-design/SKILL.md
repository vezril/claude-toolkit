---
name: domain-driven-design
description: Domain-Driven Design — modeling complex business domains in software, from Eric Evans' *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003, the "Blue Book"). Covers the core ideas (a shared domain model, Ubiquitous Language, model-driven design, layered architecture), the tactical building blocks (Entity, Value Object, Domain Service, Module, Aggregate, Factory, Repository), supple design (intention-revealing interfaces, side-effect-free functions, assertions, conceptual contours, closure of operations, the Specification pattern), and strategic design (Bounded Context, Context Map and integration patterns like Anticorruption Layer / Shared Kernel / Open Host Service, Distillation and the Core Domain, Large-Scale Structure). Use whenever the user is modeling a business domain, deciding how to structure domain logic, asks about entities/value objects/aggregates/repositories/factories/domain services, wants to define bounded contexts or integrate multiple models/teams/services, is fighting an anemic domain model or tangled domain logic, is aligning code with business language, or is drawing service boundaries for microservices — even if they don't say "DDD." Maps the patterns onto Scala/FP idioms and notes modern connections (microservices, event sourcing/CQRS, functional DDD).
---

# Domain-Driven Design

Eric Evans' approach (2003) to taming complexity in software whose hardest part is the **business domain itself**. The premise: for complex domains, the design's center of gravity should be a **domain model** — a rigorously chosen, shared abstraction of the business — and the whole team's job is to keep that model, the language, and the code reinforcing each other.

This skill maps the patterns onto Scala/FP idioms (the audience's stack) and adds modern connections. The book is OO/Java; the *modeling judgment* is what generalizes.

If the user's explicit instructions conflict with this skill, the user wins.

## When DDD is (and isn't) worth it

DDD pays off when **domain complexity** is the dominant difficulty — rich, evolving business rules that are hard to get right. It is *not* free: it demands sustained collaboration with domain experts and continuous refactoring. For a CRUD app or a domain with thin logic, the book's own advice is to use a **Smart UI** ("anti-pattern" by DDD's standards, but the right call when logic is simple) rather than pay for elaborate modeling. Match the investment to the complexity; don't impose aggregates and bounded contexts on a problem that doesn't have the complexity to justify them. This is the same restraint as in [[design-patterns]].

## The core ideas (Part I)

These motivate everything else:

- **The domain model is the backbone.** A model is a *selectively simplified, deliberately structured* view of the domain — not a diagram of reality, but the set of concepts the software actually runs on. Its value is leverage over complexity.
- **Ubiquitous Language.** One rigorous language, based on the model, used by developers *and* domain experts, in conversation, code, and documents alike. If experts say "policy" and "claim" but the code says `DataManager` and `flag2`, the model has failed. Class names, methods, and modules should be words from this language; changing the language changes the model and the code together. **This is the single most load-bearing practice in the book.**
- **Model-Driven Design.** Don't keep an "analysis model" separate from the code's "design model" — bind them. The code *is* an expression of the model; a concept with no faithful code representation isn't really in your design. "Hands-on modelers": the people shaping the model must also touch the code.
- **Layered Architecture.** Isolate the domain model in its own layer (UI → Application → **Domain** → Infrastructure), so domain logic isn't smeared through UI and persistence. The domain layer holds the model and knows nothing about the others. (See tactical reference.)

## The pattern map

Detail lives in three references — read the one matching the question:

- **`references/tactical-patterns.md`** — expressing a model in running software: **Entity, Value Object, Domain Service, Module**, and the object lifecycle — **Aggregate, Factory, Repository** — plus Layered Architecture. Read this for "how do I represent / structure / persist this domain concept."
- **`references/supple-design.md`** — making a model that's a pleasure to work with and refactoring toward deeper insight: **Intention-Revealing Interfaces, Side-Effect-Free Functions, Assertions, Conceptual Contours, Standalone Classes, Closure of Operations, Declarative Design**, the **Specification** pattern, and making implicit concepts explicit. Read this for "how do I make this model cleaner / express a hidden rule."
- **`references/strategic-design.md`** — keeping models coherent at scale across teams and systems: **Bounded Context, Context Map**, the integration patterns (**Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Separate Ways, Open Host Service, Published Language**), **Distillation** (Core Domain, Generic Subdomains, Domain Vision Statement), and **Large-Scale Structure** (Responsibility Layers, Knowledge Level, Evolving Order). Read this for "we have multiple models/teams/services — how do they relate," service boundaries, or "where should we focus effort."

## At a glance

| Building block | What it is | Scala/FP note |
|---|---|---|
| **Entity** | Object defined by *identity* and continuity, not attributes | Class/case class with a stable id; identity ≠ structural equality |
| **Value Object** | Defined wholly by its attributes; no identity; immutable | The natural fit: immutable `case class` / ADT — see [[functional-programming]] |
| **Domain Service** | A domain operation that isn't naturally an Entity/VO | A stateless function or module of pure functions |
| **Aggregate** | A cluster of objects with one **root** + a consistency boundary | Root case class owning its parts; enforce invariants in smart constructors |
| **Factory** | Encapsulates complex creation, producing valid objects | Smart constructor / companion `apply` returning `Either[Error, T]` |
| **Repository** | Collection-like access to aggregate roots; hides persistence | A trait (port); pure core, effectful impl at the edge |
| **Specification** | A predicate object capturing a business rule | A `A => Boolean` predicate, composable with and/or/not |
| **Bounded Context** | The boundary within which a model is unified and consistent | A module/service with its own model; often a microservice boundary |
| **Anticorruption Layer** | Translation layer protecting your model from a foreign one | An adapter translating an external model into yours at the boundary |

## Scala/FP framing (the audience codes in Scala)

DDD and FP align unusually well:

- **Value Objects are immutable data** — exactly the [[functional-programming]] default (`case class`, ADTs, structural equality). Most of a rich model is value objects.
- **Make illegal states unrepresentable.** DDD's aggregate invariants and "valid by construction" objects are the same goal as smart constructors and ADTs in the [[scala]] skill — push rules into types so a malformed `Order` can't exist.
- **Supple design is functional design.** Evans' *Side-Effect-Free Functions* and *Assertions* explicitly push computation into pure functions returning value objects, isolating state change — a pure-core/effectful-shell architecture before the name was common. *Closure of Operations* is just an operation `A => A` (a monoid/endo), and *Specifications* are composable predicates.
- **Repositories are ports.** Keep the domain pure; let the repository be a trait whose effectful implementation lives in the shell (Cats Effect `IO` in this repo's stack).

## Modern lens (the audience asked for this)

- **Bounded Context ≈ microservice boundary.** The most durable strategic idea: each service should own one model with clear edges, integrated via Context Map relationships. A service split that ignores context boundaries (two services sharing one database/model) recreates the coupling DDD warns against. The Anticorruption Layer is how a service defends its model from upstream ones.
- **Event sourcing & CQRS** grew up alongside DDD: model state changes as a stream of **domain events** (named in the Ubiquitous Language), and separate the write model (aggregates enforcing invariants) from read models. Domain events are now considered a first-class DDD building block (added after the book).
- **"Anemic domain model"** — the trap (named by Fowler) of entities that are bare data bags with all logic in "service" classes; DDD argues behavior belongs with the data it governs. In FP the resolution is nuanced: pure functions over rich value types keep behavior *near* the data without OO mutation — fine, as long as the model (not a procedural service layer) owns the rules.
- **Strategic DDD has outlasted tactical dogma.** Bounded contexts, context mapping, and distillation (focus on the Core Domain) are the parts practitioners most consistently keep; treat the tactical building blocks as useful defaults, not rules.

## Related

- [[functional-programming]] — immutability, ADTs, making illegal states unrepresentable, pure-core/effectful-shell; the substrate for Value Objects, Aggregates, supple design.
- [[scala]] — smart constructors, `sealed abstract case class`, traits-as-ports, Cats Effect for repositories.
- [[design-patterns]] — Evans uses Strategy, Composite, and others as *domain* patterns; shares the "apply only to real complexity" restraint.
- [[tdd]] — refactoring toward deeper insight relies on a fast test suite over a pure domain.
- [[cqrs-event-sourcing]] — the event-driven data patterns (CQRS, Event Sourcing, Sagas, Domain Events) that are tactical DDD's natural persistence and cross-context consistency mechanisms.
- Source: *Domain-Driven Design: Tackling Complexity in the Heart of Software*, Eric Evans (Addison-Wesley, 2003). Pattern definitions are faithful to the book; Scala/FP mappings and the modern lens are added for this repo.
