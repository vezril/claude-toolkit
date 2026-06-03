# Formats & the path to DDD and code

The scales of EventStorming and how a Design-Level model becomes Domain-Driven Design artifacts and running software. Faithful to *Introducing EventStorming*; DDD bridge, event sourcing/CQRS, and Scala/FP added (the audience asked for tight integration).

## Contents

1. The three formats
2. Big Picture → discovering boundaries
3. Design-Level → DDD aggregates & bounded contexts
4. Event sourcing & CQRS
5. Scala/FP realization
6. From EventStorming to user stories

---

## 1. The three formats

EventStorming is one technique at different **scales and purposes**:

- **Big Picture EventStorming** — the widest lens: the whole business or a large process, with many stakeholders. Mostly **orange events** loosely on a timeline plus **hot spots**. Purpose: shared understanding, surfacing problems, and *discovering* where the boundaries are. Variations: software-project discovery, organization retrospective, onboarding new hires.
- **Design-Level (Software Design) EventStorming** — zoomed into one promising subdomain, using the **full grammar** (commands, aggregates, policies, read models, external systems). Smaller, more technical group. Scope and people differ from Big Picture; the goal is a model **precise enough to write code from**.
- **Value-Stream / Process-Modeling EventStorming** — overlays **value created and destroyed** (and multiple "currencies" of value) onto a process to analyze and improve flow; good for spotting waste and inconsistencies.

## 2. Big Picture → discovering boundaries

As the timeline takes shape, events naturally **cluster**: groups of related events, with their own language and rhythm, separated by pivotal events or by where the language shifts. Those clusters are candidate **Bounded Contexts** ([[domain-driven-design]]). A change in vocabulary across the wall ("lead" becomes "customer" becomes "account") is a strong signal of a context boundary. Hot spots at the seams between clusters are exactly where you'll later want translation (an **Anticorruption Layer**) or a defined integration relationship from the DDD context-map patterns.

## 3. Design-Level → DDD aggregates & bounded contexts

The Design-Level grammar maps almost one-to-one onto DDD tactical patterns:

- A **Command lands on an Aggregate**, which checks invariants and **emits Domain Events** — that's precisely a DDD aggregate's role (the consistency boundary). The pale-yellow "system" stickies *become* aggregates; **postpone naming them** until their behavior is clear, then name them in the Ubiquitous Language.
- **Policies** ("whenever…then…") become the process managers / sagas that coordinate across aggregates.
- **Read Models** become query-side projections; **External Systems** become ports with adapters at the boundary.
- The **words on the stickies are the Ubiquitous Language** — carry them verbatim into type names, methods, and modules. EventStorming is, in effect, how you *discover* the language and the aggregates that DDD then formalizes.

Work the Design-Level board with the book's tips: make alternatives visible, **choose later**, hide unnecessary complexity, and **rewrite, rewrite, rewrite** until the model reads cleanly.

## 4. Event sourcing & CQRS

Because Domain Events are first-class in the model, two architectures fall out naturally (both post-date the DDD book and are where EventStorming shines):

- **Event sourcing** — persist the **stream of domain events** as the source of truth; current state is a fold over past events. The orange stickies are literally your event log.
- **CQRS (Command Query Responsibility Segregation)** — the Command→Aggregate→Event flow is the **write model**; Read Models are the **read side**, built as projections off the events. The board already separates the two, so the architecture mirrors the model.

Use these where the domain's auditability/temporal complexity justifies them — not by default.

## 5. Scala/FP realization

Translate a Design-Level board into the repo's stack (see [[functional-programming]], [[scala]]):

```scala
sealed trait OrderCommand                       // blue stickies
sealed trait OrderEvent                          // orange stickies
final case class OrderState(...)                 // aggregate state (immutable)

// Aggregate = two pure functions
def decide(s: OrderState, c: OrderCommand): Either[OrderError, List[OrderEvent]] = ...
def evolve(s: OrderState, e: OrderEvent): OrderState = ...

// Policy = pure reaction (purple sticky)
def reactions(e: OrderEvent): List[OrderCommand] = ...

// Read Model = projection (green sticky) — a fold over the event stream
def view(events: List[OrderEvent]): OrderSummary = events.foldLeft(empty)(apply)
```

Aggregate invariants live in smart constructors (`sealed abstract case class` + `from`), so an invalid state can't be built — "make illegal states unrepresentable." External systems are traits implemented in the Cats Effect shell; the core (`decide`/`evolve`/projections) stays pure and trivially testable ([[tdd]]).

## 6. From EventStorming to user stories

For delivery, the board converts into backlog items and acceptance criteria without losing the shared understanding:

- A slice of the timeline (a command and the events around it) becomes a **user story** — and, crucially, a *better conversation* placeholder rather than a frozen spec.
- **Acceptance criteria** read straight off the grammar: *Given* the events that led here, *When* this command is issued, *Then* these events result (and these read models update). This Given/When/Then maps cleanly onto BDD tests and onto the `decide`/`evolve` functions above.
- Combine with **User Story Mapping** for release planning: EventStorming gives the deep domain flow; story mapping arranges the slices into a delivery sequence.
