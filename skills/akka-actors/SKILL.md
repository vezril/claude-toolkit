---
name: akka-actors
description: Akka Typed actors (Akka Core 2.10.x, akka-actor-typed) in Scala and Java — the foundation of all Akka modules. Covers Behaviors (functional & object-oriented styles), the typed message protocol, ActorContext, actor lifecycle (spawn/stop/watch/SpawnProtocol), interaction patterns (tell, request-response, adapted response, ActorContext.ask vs AskPattern, pipeToSelf, StatusReply), supervision and fault tolerance ("let it crash"), actor discovery via the Receptionist, routers (pool & group), stash, behaviors-as-FSM, dispatchers, mailboxes, and testing (ActorTestKit, BehaviorTestKit, TestProbe, LoggingTestKit). Use whenever writing or reviewing Akka actor code, designing an actor message protocol, choosing an interaction pattern, setting up supervision, discovering or routing actors, tuning dispatchers/mailboxes, or testing actors — even if "Akka" isn't named but actors/Behaviors/ActorRef/typed messaging are involved. The base skill the akka (meta), akka-cluster, akka-persistence, and akka-streams skills build on.
---

# Akka Typed Actors

The actor model in Akka 2.10 (`akka.actor.typed`), Scala and Java. An actor is a unit of state + behavior that communicates **only by asynchronous messages**, processes one message at a time (so no locks/`synchronized` needed), and evolves by returning its next `Behavior`. This is the foundation every other Akka module (cluster, persistence, streams interop) builds on.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Otherwise this is the default style. Cross-links: [[akka]] (meta), [[akka-cluster]], [[akka-persistence]], [[akka-streams]], [[functional-programming]], [[scala]].

Dependency: `"com.typesafe.akka" %% "akka-actor-typed" % AkkaVersion` (+ `akka-actor-testkit-typed % Test`). Akka 2.10 runs on Scala 2.13/3.3, JDK 11/17/21, and is licensed under BSL 1.1.

## The core model

- An `ActorRef[T]` accepts **only** messages of type `T` — the compiler enforces the actor's *protocol*. `ref ! msg` (Scala) / `ref.tell(msg)` (Java) is fire-and-forget and asynchronous.
- A `Behavior[T]` describes how the actor handles the next message and returns the next behavior (`Behaviors.same` to stay). State changes = behavior changes; **never** mutable static/shared state.
- Bundle the protocol (a `sealed trait Command` + reply types) with the behavior in one object/class. Reply addresses travel **inside** messages as `replyTo: ActorRef[Reply]` — there is no ambient `sender()`.

## Two styles (both first-class)

**Functional** (idiomatic Scala): immutable state passed as parameters, switch behavior to change state, context from `Behaviors.setup`/the `receive` lambda.

```scala
object Counter {
  sealed trait Command
  final case class Increment(by: Int) extends Command
  final case class GetValue(replyTo: ActorRef[Int]) extends Command

  def apply(): Behavior[Command] = counter(0)
  private def counter(n: Int): Behavior[Command] = Behaviors.receiveMessage {
    case Increment(by)     => counter(n + by)
    case GetValue(replyTo) => replyTo ! n; Behaviors.same
  }
}
```

**Object-oriented** (idiomatic Java): `AbstractBehavior` with mutable fields, return `this` to stay, context via constructor; **always create it from `Behaviors.setup`** so a fresh instance is made on restart (state never shared).

```java
public class Counter extends AbstractBehavior<Counter.Command> {
  public interface Command {}
  public static final class Increment implements Command { public final int by; public Increment(int by){this.by=by;} }
  public static final class GetValue implements Command { public final ActorRef<Integer> replyTo; public GetValue(ActorRef<Integer> r){replyTo=r;} }

  public static Behavior<Command> create() { return Behaviors.setup(Counter::new); }
  private int n = 0;
  private Counter(ActorContext<Command> ctx) { super(ctx); }
  @Override public Receive<Command> createReceive() {
    return newReceiveBuilder()
      .onMessage(Increment.class, m -> { n += m.by; return this; })
      .onMessage(GetValue.class, m -> { m.replyTo.tell(n); return this; })
      .build();
  }
}
```

Prefer functional in Scala, OO in Java. Mix freely. See [[functional-programming]] — typed actors reward the same immutability/ADT discipline.

## Always-apply defaults

1. **Model the protocol as a `sealed trait`/`interface Command`** so matches are exhaustive (an unhandled message → `MatchError`/logged). Events (for [[akka-persistence]]) are named in the **past tense**.
2. **Expose the initial behavior from a factory** — `apply()` (Scala) / static `create()` (Java) — with a private constructor; put `setup`/`withTimers`/`withStash` there.
3. **Replies travel as `replyTo: ActorRef[Reply]`** in the message; prefer `StatusReply[T]` when a request can succeed or return a validation error.
4. **Never close over or share mutable state across the actor boundary** — never touch `ActorContext` or mutable fields from a `Future`/`CompletionStage` callback; use `context.pipeToSelf` to bring async results back as messages.
5. **Default supervision is stop** — wrap with `Behaviors.supervise(...).onFailure[E](SupervisorStrategy.restart)` where restart-on-failure is wanted; model expected/validation failures as messages, not exceptions ("let it crash" is for the unexpected).
6. **Don't block on the actor's dispatcher.** Offload blocking calls to a dedicated `DispatcherSelector.blocking()` / bulkhead dispatcher.
7. **Prefer `context.ask` inside an actor; `AskPattern.ask` only from outside.** Every `ask` needs a timeout.

## Anti-patterns (flag in review)

- Mutable shared/static state, or reading/mutating actor state from `Future` callbacks instead of `pipeToSelf`.
- A `sender()`-style assumption (there is none in typed) — pass `replyTo` explicitly.
- Unbounded fire-and-forget into a slow actor (mailbox growth → OOM) — apply backpressure (Reliable Delivery, [[akka-streams]], or request-response).
- Blocking on the default dispatcher; giant actors that should be split; using an actor where a pure function would do.
- Catch-and-swallow inside `receive`; using exceptions for expected validation outcomes.
- Stashing without a bounded `StashBuffer`; huge stashes (OOM, and `unstashAll` starves other actors).

## How to use this skill

The detail lives in four references — read the one matching the task:

- **`references/behaviors-and-lifecycle.md`** — `Behaviors` factories & signals, `ActorContext`, spawning/stopping/`watch`/`watchWith`, `SpawnProtocol`, guardian/`ActorSystem`, dispatchers, and mailboxes.
- **`references/interaction-and-discovery.md`** — tell, request-response, adapted response (message adapters), `ActorContext.ask` vs `AskPattern`, `pipeToSelf`, `StatusReply`, per-session child & aggregator patterns, the **Receptionist**, and **routers** (pool & group).
- **`references/fault-tolerance-fsm-stash.md`** — supervision strategies & restart semantics, `PreRestart`/`PostStop`, `watch`/`Terminated`/`ChildFailed`/`DeathPactException`, behaviors-as-FSM (with `withTimers`), and `StashBuffer`.
- **`references/testing.md`** — async `ActorTestKit` + `TestProbe`, sync `BehaviorTestKit` + `TestInbox` + effects, `LoggingTestKit`, `ManualTime`, and config/log-capturing.

## Related

- [[akka]] — the meta skill mapping all Akka modules and when to reach for each.
- [[akka-cluster]] — distributing actors across nodes (sharding, singleton, group routers are cluster-aware).
- [[akka-persistence]] — `EventSourcedBehavior`/`DurableStateBehavior` are actors with persisted state.
- [[akka-streams]] — actor↔stream interop (`ask` in a stream, `ActorSource`/`ActorSink`).
- [[functional-programming]], [[scala]], [[tdd]] — immutability/ADTs, Scala mechanics, and testing discipline that make actors clean.
- Source: Akka Core docs, https://doc.akka.io/libraries/akka-core/current/typed/ (v2.10.x).
