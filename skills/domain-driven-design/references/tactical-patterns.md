# Tactical patterns: expressing a model in software

The building blocks (DDD Parts II) for turning a domain model into running code, plus the layered architecture that isolates it. Definitions are faithful to Evans (2003); Scala/FP mapping and modern notes added.

## Contents

1. Layered Architecture
2. Entity
3. Value Object
4. Domain Service
5. Module (Package)
6. Aggregate
7. Factory
8. Repository

---

## 1. Layered Architecture

Partition the system so the **domain model lives in its own layer**, free of UI, application-coordination, and infrastructure concerns. A common arrangement: **User Interface → Application → Domain → Infrastructure**, where each layer depends only inward/downward.

- The **Domain layer** holds the model — entities, value objects, domain services, the business rules. It must not know about persistence, UI, or frameworks. This isolation is what lets the model grow rich without drowning in plumbing.
- The **Application layer** is thin: it coordinates tasks, drives the domain, holds no business rules.

**Scala/FP.** This is the **pure-core / effectful-shell** architecture from [[functional-programming]]: the domain layer is pure (data + total/fallible functions), effects (DB, IO) live at the edge. A modern restatement is the hexagonal/ports-and-adapters architecture — the domain defines ports (traits), adapters implement them outside.

## 2. Entity

**An object defined not by its attributes but by a thread of identity and continuity** that runs through time and different states. Two entities with identical attributes are still distinct; the same entity remains itself even as every attribute changes (a `Customer` keeps its identity through a name/address change).

- Give it a stable, unique identity (an id assigned at creation, often domain-meaningful or a generated key). Equality is **by identity, not by structure**.
- Keep entities focused on identity + lifecycle + the behavior that genuinely needs continuity; push descriptive attributes into value objects.

**Scala/FP.** A class or `case class` carrying an explicit `id`; override equality to compare ids only (don't use a bare `case class`'s structural `equals` for an entity). Identity-bearing things are the *minority* of a good model.

## 3. Value Object

**An object that describes a characteristic with no conceptual identity — defined entirely by its attributes.** A money amount, a date range, a color, a coordinate. Two value objects with equal attributes are interchangeable.

- Make value objects **immutable**. Immutability lets them be shared, cached, and passed freely without aliasing bugs, and makes equality structural.
- Prefer modeling as much of the domain as possible as value objects — they're simpler and safer than entities.

**Scala/FP.** The most natural fit in the whole catalog: an **immutable `case class`** (structural equality and `copy` come free) or an **ADT** for closed sets of cases. Invariants go in a smart constructor (see [[scala]]). This is exactly [[functional-programming]]'s home ground.

## 4. Domain Service

**When a significant domain operation doesn't naturally belong to any Entity or Value Object, model it as a Service** — a standalone operation named in the Ubiquitous Language, defined purely in terms of the model. Hallmarks: stateless, the operation relates several domain objects, and forcing it onto one of them would distort that object.

- Keep services thin and domain-meaningful (`FundsTransferService`), *not* a dumping ground. A service swollen with logic that belongs on entities/VOs is the **anemic domain model** smell.
- Distinguish *domain* services (express domain concepts) from *application* services (coordinate tasks) and *infrastructure* services.

**Scala/FP.** A **stateless function** or a module/`object` of pure functions over domain types. Many "services" are just `(A, B) => C`.

## 5. Module (Package)

**Choose modules that tell the story of the system and contain a cohesive set of concepts** (verbatim intent). Modules should reflect domain concepts, have low coupling and high cohesion, and their **names become part of the Ubiquitous Language**. If modules don't decouple cleanly, that's a signal to rework the model, not just to shuffle files.

**Scala/FP.** Package/`object` structure organized by domain concept (not by technical layer like `controllers`/`daos`). Name packages in domain terms.

## 6. Aggregate

**Cluster the Entities and Value Objects into Aggregates and define boundaries around each. Choose one Entity to be the root of each Aggregate, and control all access to the objects inside the boundary through the root.** (Verbatim.) External objects may hold references to the **root only**; transient internal references can be passed out for a single operation. Because the root mediates access, it can enforce **all invariants** for the aggregate as a whole on every state change. The aggregate is also the unit of consistency and transactional boundary — invariants hold within an aggregate; across aggregates, expect eventual consistency.

- Keep aggregates **small**; large aggregates create contention and load whole object graphs. Reference other aggregates by **identity**, not by direct object reference.
- One transaction should modify one aggregate (a widely adopted modern rule of thumb).

**Scala/FP.** The root as a `case class` owning its parts, constructed only through a **smart constructor** (`sealed abstract case class` + `from` returning `Either[Error, Root]`) so an aggregate that violates an invariant can't exist — "make illegal states unrepresentable" (see [[scala]], [[functional-programming]]). Cross-aggregate links are stored ids, not nested objects.

## 7. Factory

**Encapsulate the creation of a complex object or Aggregate, so the client isn't burdened with the construction and the object is produced in a valid state.** When construction is complicated or must enforce invariants, a constructor isn't enough; a factory (a dedicated factory method, factory object, or the aggregate root creating its members) hides the assembly and guarantees a consistent result.

**Scala/FP.** A **smart constructor**: a companion-object `apply`/`from` that validates and returns `Either[Error, T]` (or builds a valid value directly). This *is* the factory; it's also where aggregate invariants are checked. See [[scala]] on the `apply`/`copy` leak and `sealed abstract case class`.

## 8. Repository

**Provide the illusion of an in-memory collection of all objects of an Aggregate's root type; encapsulate the actual storage and query.** Clients ask the repository for aggregates by identity or by criteria and get back fully-formed domain objects, with no knowledge of the database, ORM, or queries behind it. Provide repositories **only for aggregate roots**, not for every object.

- This keeps the domain model free of persistence concerns (reinforcing the layered architecture) and keeps query/storage logic in one place.
- A repository can take a **Specification** (see supple-design reference) to express a query as a domain predicate.

**Scala/FP.** Define the repository as a **trait (a port)** in the domain — e.g. `trait OrderRepo { def find(id: OrderId): IO[Option[Order]]; def save(o: Order): IO[Unit] }` — with the effectful implementation (Cats Effect `IO`, a DB) living in the shell. The pure core depends on the trait, not the implementation; this is also what makes the domain testable (see [[tdd]]).
