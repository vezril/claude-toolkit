# Fault tolerance, FSM & stash

Akka Typed (2.10.x). Source: doc.akka.io/libraries/akka-core/current/typed/{fault-tolerance,fsm,stash}.html

## Supervision & "let it crash"

Distinguish **validation errors** (bad command data — model as part of the protocol, reply with an error, don't throw) from **failures** (unexpected, e.g. a broken DB connection — let it crash and recover). In Typed the **default on a thrown exception is STOP**; opt into restart/resume by wrapping the behavior:

```scala
Behaviors.supervise(behavior).onFailure[IllegalStateException](SupervisorStrategy.restart)
Behaviors.supervise(behavior).onFailure[DbException](
  SupervisorStrategy.restartWithBackoff(minBackoff = 1.second, maxBackoff = 30.seconds, randomFactor = 0.2))
// nest for different exception types:
Behaviors.supervise(
  Behaviors.supervise(behavior).onFailure[IllegalStateException](SupervisorStrategy.restart)
).onFailure[IllegalArgumentException](SupervisorStrategy.stop)
```
```java
Behaviors.supervise(behavior).onFailure(IllegalStateException.class, SupervisorStrategy.restart());
Behaviors.supervise(behavior).onFailure(DbException.class,
    SupervisorStrategy.restartWithBackoff(Duration.ofSeconds(1), Duration.ofSeconds(30), 0.2));
```

Strategies: `stop`, `restart`, `resume` (keep state, ignore the failure — rarely right), `restart.withLimit(maxNrOfRetries, withinTimeRange)`, `restartWithBackoff(...)`, `.withStopChildren(false)`.

**Restart semantics:** restart re-installs the *original* `Behavior` passed to `supervise`, so mutable state must be created inside `Behaviors.setup` (factory) to get a fresh copy. By default children are stopped on restart (setup re-runs). To keep children, put `supervise` *inside* `setup` and use `SupervisorStrategy.restart.withStopChildren(false)`.

**Cleanup signals:** handle **both** `PreRestart` (before restart) and `PostStop` (on stop) to release resources — `PostStop` is not emitted on restart.

## Watching & bubbling failures up

A parent that `watch`es a child receives `Terminated(ref)` when it stops, or **`ChildFailed`** (a `Terminated` subtype carrying the cause) when it fails. If a watcher doesn't handle `Terminated`/`ChildFailed`, it fails with **`DeathPactException`** — which you can in turn supervise higher up to escalate (the Akka equivalent of classic supervision hierarchies). The failure cause is exposed only to the immediate parent (no leaking internals); rethrow from a `Terminated` handler to propagate.

## Behaviors as a finite state machine

Model each state as a behavior (a method returning `Behavior`), carry data as parameters, and use `Behaviors.withTimers` for state timeouts. Events are the actor's message type.

```scala
def idle(data: Data): Behavior[Event] = Behaviors.receiveMessage {
  case SetTarget(ref)             => idle(Todo(ref, Vector.empty))
  case Queue(o): @unchecked       => active(/* … */)
  case _                          => Behaviors.unhandled
}
def active(todo: Todo): Behavior[Event] = Behaviors.withTimers { timers =>
  timers.startSingleTimer(Timeout, 1.second)
  Behaviors.receiveMessagePartial {
    case Flush | Timeout => todo.target ! Batch(todo.queue); idle(todo.copy(queue = Vector.empty))
    case Queue(o)        => active(todo.copy(queue = todo.queue :+ o))
  }
}
```
```java
private static Behavior<Event> active(Todo todo) {
  return Behaviors.withTimers(timers -> {
    timers.startSingleTimer(Timeout.INSTANCE, Duration.ofSeconds(1));
    return Behaviors.receive(Event.class)
      .onMessage(Queue.class, q -> active(todo.add(q)))
      .onMessage(Flush.class, f -> flush(todo))
      .onMessage(Timeout.class, t -> flush(todo)).build();
  });
}
```

## Stash — buffering messages

`Behaviors.withStash(capacity)` gives a **bounded** `StashBuffer` to defer messages the current behavior can't handle yet (e.g. while loading initial state). Common with `pipeToSelf`:

```scala
def apply(id: String, db: DB): Behavior[Command] = Behaviors.withStash(100) { buffer =>
  Behaviors.setup { ctx => new DataAccess(ctx, buffer, id, db).start() }
}
// in start(): case Initial(v) => buffer.unstashAll(active(v))
//             case other      => buffer.stash(other); Behaviors.same
```
```java
public static Behavior<Command> create(String id, DB db) {
  return Behaviors.withStash(100, stash ->
    Behaviors.setup(ctx -> new DataAccess(ctx, stash, id, db).start()));
}
```

Rules: capacity is mandatory (overflow → `StashOverflowException`; check `buffer.isFull`); stashed messages live in memory until `unstashAll` — keep counts low (a large `unstashAll` processes all sequentially and starves other actors). Stash inside `withStash` placed *inside* `supervise` is recreated (lost) on each restart.
