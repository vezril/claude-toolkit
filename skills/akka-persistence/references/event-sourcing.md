# EventSourcedBehavior, the Effect API & CQRS

Akka Persistence (2.10.x). Source: doc.akka.io/libraries/akka-core/current/typed/{persistence,cqrs}.html

## The four components

`EventSourcedBehavior[Command, Event, State]` needs: `persistenceId` (stable, unique), `emptyState`, `commandHandler: (State, Command) => Effect[Event, State]`, `eventHandler: (State, Event) => State`. Wrap construction in `Behaviors.setup { ctx => EventSourcedBehavior(...) }` when you need `ActorContext`.

**PersistenceId:** `PersistenceId.ofUniqueId("raw")` or `PersistenceId(entityTypeHint, entityId)` (default `|` separator). With Cluster Sharding, derive the id from the `EntityContext`.

**Command handler** validates and returns one Effect. **Event handler** is called once per persisted event, in order, during both normal operation and recovery — so it must **only update state, never perform side effects**.

## The Effect API

Exactly one primary effect per command:

- `Effect.persist(event)` / `Effect.persist(e1, e2, …)` — persist one or several events **atomically** (all-or-nothing; recovery never sees a partial batch).
- `Effect.none` — read-only command, persist nothing.
- `Effect.unhandled` — command not valid in the current state.
- `Effect.stop` — stop the entity.
- `Effect.stash` / `Effect.unstashAll` (via chaining) — defer/replay commands.
- `Effect.reply(replyTo)(msg)` / `Effect.noReply` — reply effects (see below).

Chain side effects (run **after** successful persist, sequentially; at-most-once; **not** re-run on recovery): `.thenRun(state => …)`, `.thenReply(replyTo)(state => msg)`, `.thenStop()`, `.thenUnstashAll()`.

```scala
Effect.persist(Added(data)).thenRun(state => subscriber ! state).thenReply(replyTo)(_ => StatusReply.Ack)
```
```java
Effect().persist(new Added(c.data)).thenRun(state -> subscriber.tell(state))
        .thenReply(c.replyTo, s -> StatusReply.ack());
```

Side-effect guarantees: not run if persist fails, not replayed on restart. To re-issue unacknowledged effects after a crash, inspect state on `RecoveryCompleted` (may then run more than once). A side effect *before* persisting may run even if persist fails — avoid.

## Replies, StatusReply, enforced replies

Request-response: include `replyTo: ActorRef[Reply]` in the command. Use `StatusReply[T]` to model success-or-validation-error uniformly: `StatusReply.Success(v)` / `StatusReply.Error("msg")` / `StatusReply.Ack` (`StatusReply[Done]`).

`EventSourcedBehavior.withEnforcedReplies(...)` (Scala) / extend `EventSourcedBehaviorWithEnforcedReplies` (Java) forces every command to return a `ReplyEffect` — **compile-time proof that you never forget to reply**. Build with `Effect.reply` / `Effect.noReply` / `.thenReply` / `.thenNoReply`; Java uses `newCommandHandlerWithReplyBuilder`.

```scala
def withdraw(acc: OpenedAccount, c: Withdraw): ReplyEffect[Event, Account] =
  if (acc.canWithdraw(c.amount)) Effect.persist(Withdrawn(c.amount)).thenReply(c.replyTo)(_ => StatusReply.Ack)
  else Effect.reply(c.replyTo)(StatusReply.Error(s"Insufficient balance ${acc.balance}"))
```
```java
private ReplyEffect<Event, Account> withdraw(OpenedAccount acc, Withdraw c) {
  if (!acc.canWithdraw(c.amount)) return Effect().reply(c.replyTo, StatusReply.error("not enough funds"));
  return Effect().persist(new Withdrawn(c.amount)).thenReply(c.replyTo, a -> StatusReply.ack());
}
```

## Recovery

On start/restart, events (after the latest snapshot) are replayed; commands arriving during recovery are stashed. The **`RecoveryCompleted`** signal always fires (even for an empty journal), carrying the current state — the place for end-of-recovery side effects. `RecoveryFailed` logs and stops the actor. Concurrency capped by `akka.persistence.max-concurrent-recoveries = 50`. A **replay filter** (`replay-filter.mode = repair-by-discard-old`) protects against corrupt streams from accidental multiple writers.

## State-dependent (FSM-style) handlers

There is no returning a new `Behavior` (state *is* the behavior). Branch on the `State` first, then the command — Scala via nested `match`, Java via `newCommandHandlerBuilder().forStateType(Open.class).onCommand(...)` / `.forAnyState()`. A common style pushes handler methods onto the `State` class.

## Tagging & CQRS

Tag events to drive read-side queries: `.withTagger(event => Set("orders"))` (Scala) / override `tagsFor(event)` (Java). Tags are consumed by Persistence Query (`EventsByTag`) and by [[akka-projections]].

**CQRS:** the write side is your event-sourced entities; the read side is one or more **projections** built from the event stream (via tagging / `EventsByTag` / `EventsBySlice`). Don't query entities directly for reporting — project into read-optimized models. To parallelize the read-side, run N tagged projection workers as a [[akka-cluster]] Sharded Daemon Process.
