# Notation & grammar

The colored sticky-note vocabulary and the grammar that links them, from *Introducing EventStorming*. Faithful to Brandolini; Scala/FP and event-sourcing mappings added. Keep a **visible legend** on the wall — Brandolini is strict about consistent colors so workshop photos stay legible, but he's explicit that the exact colors are flexible; what's load-bearing is the **roles and the relationships**.

## Contents

1. The building blocks (stickies)
2. The grammar (how they connect)
3. Sorting strategies
4. Scala/FP & event-sourcing mapping

---

## 1. The building blocks

- **Domain Event — orange.** Something meaningful that *happened*, phrased in the **past tense** ("Order Placed", "Payment Received", "Cart Abandoned"). The backbone of every EventStorming. Events are precise, carry no implicit scope limit, and represent **state transitions** and **triggers for consequences**. Why orange? It's the color you reach for first and there's lots of it on a wall — events should dominate.
- **Command — blue.** The *intent/action* that causes an event ("Place Order"). Usually issued by an actor; grammatically the active-voice counterpart of an event.
- **Actor / User — small yellow.** The person or role that issues a command (a persona, "the customer", "the fraud analyst").
- **Aggregate / "System" — large pale-yellow.** The business entity (a later DDD **Aggregate**) that *receives* commands and *emits* events. Often left unnamed early — postpone aggregate naming until the behavior is clear.
- **Policy — lilac/purple.** Reactive business logic: "**whenever** \<some event\>, **then** \<some command\>." Policies are the glue connecting an event to its next consequence; they capture rules like "whenever an order is placed, then reserve inventory." Time-triggered events ("every midnight…") are modeled as policies too.
- **Read Model — green.** The information an actor looks at to *decide* — the screen/report/view that informs a command. "Forget CRUD": a read model exists to support a decision, not to mirror a table.
- **External System — pink.** A system outside our control that emits events or receives commands (a payment gateway, a third-party API).
- **Hot Spot — red/magenta.** A problem, conflict, open question, inconsistency, or risk. **Mark them loudly** (often a rotated/diamond sticky). Hot spots are frequently the highest-value output of a Big Picture session — they point at where the organization is confused or in disagreement.
- **Opportunity / Pivotal Event / Value** — additional markers used in specific formats: opportunities (positive counterpart of hot spots), **pivotal events** (events significant enough to divide the timeline into phases — used as a sorting device), and value annotations in Value-Stream EventStorming.

## 2. The grammar (the "picture that explains everything")

At design level the blocks compose into a repeatable sentence — this is the core mental model:

```
            consults                issues             handled by           emits
 Actor  ───────────────▶ Read Model ──▶ Command ─────────────────▶ Aggregate ──────▶ Domain Event
 (yellow)                 (green)        (blue)                     (pale yellow)       (orange)
                                                                                          │
                                                          reacts to (whenever…then)       ▼
                                              Command ◀────────────────────────────── Policy (purple)
 External System (pink) ── also emits/receives events and commands ──▶
 Hot Spot (red) ── attached anywhere there's a problem/question ──▶
```

Read as: *an **Actor**, looking at a **Read Model**, issues a **Command** to an **Aggregate**, which emits a **Domain Event**; a **Policy** reacts to that event ("whenever X, then Y") and issues the next **Command**; **External Systems** emit and consume events too.* Every arrow is a thing the group can question. Big Picture EventStorming uses mostly the orange-events-on-a-timeline subset; Design-Level uses the whole grammar.

## 3. Sorting strategies

When chaotic exploration leaves a large, messy pile of events, impose order with one of Brandolini's recurring strategies (pick the most promising for your context):

- **Pivotal Events** — identify the few events important enough to split the whole timeline into phases/acts; sort everything relative to them. The strongest structuring device.
- **Swimlanes** — horizontal lanes separating parallel flows, actors, or sub-processes.
- **Temporal Milestones** — anchor the timeline on known time markers.
- **Chapter Sorting** — group events into named "chapters" of the story.
- **The Usual Suspects** — start from the events you know must be there and build outward.

## 4. Scala/FP & event-sourcing mapping

The notation translates almost mechanically into functional event modeling (see [[functional-programming]], [[scala]]):

- **Domain Events → an ADT.** `sealed trait OrderEvent; case class OrderPlaced(...) extends OrderEvent; case class PaymentReceived(...) extends OrderEvent`. Immutable, past-tense, carries the data that changed. Persisting the stream of these *is* **event sourcing**.
- **Commands → an ADT.** `sealed trait OrderCommand; case class PlaceOrder(...) extends OrderCommand`. Present-tense intents.
- **Aggregate → two pure functions.** `decide: (State, Command) => Either[Error, List[Event]]` (validate against invariants, produce events) and `evolve: (State, Event) => State` (fold events into current state). State is an immutable value; invariants live in smart constructors. This is the functional aggregate.
- **Policy → `Event => List[Command]`** — a pure reaction function ("whenever this event, issue these commands"), wired up at the edge.
- **Read Model → a projection**: `events.foldLeft(initial)(applyToView)` — a fold over the event stream producing exactly the view an actor needs. Separating this write/read split *is* **CQRS**.
- **External System → a port** (a trait) implemented in the effectful shell; the pure core stays unaware of the gateway behind it.
- **Hot Spots → questions to resolve before coding**, and often the boundaries where you'll want an **Anticorruption Layer** ([[domain-driven-design]]).

So the wall is a blueprint for immutable data + pure functions: events and commands as ADTs, aggregates as `decide`/`evolve`, policies and projections as folds — pure core, effects at the edge.
