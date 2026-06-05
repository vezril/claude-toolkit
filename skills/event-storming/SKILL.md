---
name: event-storming
description: EventStorming — Alberto Brandolini's collaborative workshop technique for exploring complex business domains with colored sticky notes on an unlimited modeling surface, from *Introducing EventStorming* (Brandolini). Covers the notation/grammar (Domain Events, Commands, Actors, Aggregates, Policies, Read Models, External Systems, Hot Spots), the three formats (Big Picture, Design-Level/Software Design, Value Stream), running and facilitating the workshop (phases, patterns and anti-patterns, group dynamics, remote), and turning the output into Domain-Driven Design models and code (aggregates, bounded contexts, event sourcing/CQRS). Use whenever the user wants to explore or map a business process or domain, run a discovery/modeling workshop, align stakeholders and developers, find bounded contexts or aggregates, model with domain events, kick off a project or product, untangle a legacy process, or asks about EventStorming, event modeling, domain events, the orange-sticky notation, or workshop facilitation — even if they don't say "EventStorming." Pairs tightly with the domain-driven-design skill and maps onto Scala/FP event modeling.
---

# EventStorming

Alberto Brandolini's workshop technique for **collaboratively exploring a complex business domain** by putting the people who know different parts of it in one room and modeling the flow of **domain events** on a long wall of sticky notes. It's fast, low-tech, high-bandwidth group learning — the fastest way to build a shared understanding of how a business actually works, and a front door into Domain-Driven Design.

This skill is the working guide: the notation and grammar, how to run each format, how to facilitate well, and how to turn the wall into DDD models and code. It maps onto the audience's Scala/FP stack and pairs tightly with [[domain-driven-design]].

If the user's explicit instructions conflict with this skill, the user wins.

## Why it works (the point before the mechanics)

Software complexity lives in the **business domain**, and the knowledge about that domain is **scattered** across many people who never share a complete picture — and across organizational silos that distort it. EventStorming attacks this directly:

- **Domain Events as the lingua franca.** A *domain event* — something meaningful that happened, phrased in the past tense ("Order Shipped", "Payment Received") — is understood by business and tech people alike, so it's a unit everyone can contribute. Modeling the timeline of events surfaces the real process.
- **Unlimited modeling space + everyone at once.** A long paper roll (not a cramped whiteboard) and many markers let the whole group externalize knowledge in parallel, instead of one scribe bottlenecking a meeting. Conflicts, gaps, and fuzzy areas become *visible* (Hot Spots) instead of staying hidden.
- **Learning is the deliverable.** The sticky-note artifact matters less than the shared understanding and the questions it exposes. EventStorming makes a group's collective ignorance visible and shrinks it fast.

It's an investment that pays when the domain is genuinely complex and cross-functional. For a trivial domain, it's overkill — match it to the complexity, the same restraint as in [[domain-driven-design]] and [[design-patterns]].

## The notation in one breath

Brandolini uses a deliberate, consistent color scheme (he's strict about it so any photo of a workshop is legible; the exact colors matter less than keeping a **visible legend** and being consistent):

- **Orange — Domain Event**: something that happened, past tense. The backbone of everything.
- **Blue — Command**: an action/decision that *causes* an event (often a user's intent).
- **Yellow (small) — Actor**: the person/role issuing a command.
- **Large pale-yellow — Aggregate / "System"**: the business entity (later a DDD aggregate) that receives commands and emits events.
- **Lilac/purple — Policy**: reactive business logic — "**whenever** \<event\> **then** \<command\>" — the glue that connects an event to its consequence.
- **Green — Read Model**: the information an actor looks at to make a decision.
- **Pink — External System**: a system outside our control that emits or receives events.
- **Red/magenta — Hot Spot**: a problem, conflict, question, or risk. Mark them loudly; they're often the most valuable output.

**The grammar that ties them together** (the design-level "picture that explains everything"): an **Actor** consults a **Read Model** and issues a **Command** to an **Aggregate**, which emits a **Domain Event**; a **Policy** reacts to that event ("whenever X, then…") and triggers the next Command; **External Systems** also emit and receive events. Full detail and the Scala/FP/event-sourcing mapping: **`references/notation-and-grammar.md`**.

## The three formats

EventStorming is one technique at several **scales** — detail in **`references/formats-and-to-code.md`**:

- **Big Picture** — broad, whole-business exploration with many stakeholders; goal is shared understanding, surfacing hot spots, and discovering boundaries. Mostly orange events + hot spots, loosely on a timeline.
- **Design-Level (Software Design)** — zoomed into one subdomain with the full grammar (commands, aggregates, policies, read models). Goal is a model precise enough to drive code — this is the bridge to DDD aggregates and bounded contexts.
- **Value Stream / Process Modeling** — adds value created/destroyed and flow analysis to study and improve a process.

## How to run it

Facilitation makes or breaks a session — phases, preparation, and the catalog of patterns/anti-patterns are in **`references/facilitation.md`**. The Big Picture arc: **Kick-off → Chaotic Exploration** (everyone throws orange events on the wall at once) **→ Enforcing the Timeline** (order them, resolve duplicates/conflicts) **→ People & Systems** (add actors, external systems, read models) **→ Problems & Opportunities** (hot spots) **→ Pick your problem** (decide where to go deeper). Core stance: provide an **unlimited modeling surface**, invite the **right (diverse) people**, *do first / explain later*, **keep your mouth shut** as facilitator, and make it safe to be wrong.

## From wall to code (the DDD/modern bridge)

This is why it matters for building software — full treatment in `references/formats-and-to-code.md`:

- **Design-Level output maps almost directly onto [[domain-driven-design]] tactical patterns.** The pale-yellow "systems" become **Aggregates** (a command lands on an aggregate, which enforces invariants and emits events); clusters of cohesive events/aggregates reveal **Bounded Contexts**; the **Ubiquitous Language** is literally the words on the stickies.
- **Event sourcing & CQRS fall out naturally.** Domain Events are first-class, so persisting them *is* event sourcing; the Command→Aggregate→Event→Read Model flow *is* CQRS (write model vs read model). EventStorming is the design technique these architectures were waiting for.
- **Scala/FP.** Model the discovered events and commands as **ADTs** (`sealed trait OrderEvent`); an aggregate's behavior is a pure `decide: (State, Command) => Either[Error, List[Event]]` plus `evolve: (State, Event) => State`; policies are functions `Event => List[Command]`; read models are projections (folds) over the event stream. The wall translates to immutable data + pure functions — see [[functional-programming]] and [[scala]].
- Events also convert to **user stories / acceptance criteria** for delivery (Given the events leading up, When this command, Then these events).

## Related

- [[domain-driven-design]] — EventStorming is the discovery front-end to DDD; events→aggregates, clusters→bounded contexts, stickies→Ubiquitous Language. Brandolini built it from DDD practice.
- [[functional-programming]] — events/commands as ADTs, aggregates as pure decide/evolve functions, read models as folds; immutability throughout.
- [[scala]] — `sealed trait` event/command ADTs, smart-constructor invariants for aggregates.
- [[design-patterns]] — shares the "apply to real complexity only" restraint.
- [[cqrs-event-sourcing]] — the domain events, commands, and policies on the wall become event-sourced aggregates, CQRS read models, and saga reactions.
- Source: *Introducing EventStorming* by Alberto Brandolini (Leanpub, work-in-progress). Notation and workshop structure are faithful to the book; the Scala/FP and event-sourcing/CQRS mappings and DDD bridge are added for this repo.
