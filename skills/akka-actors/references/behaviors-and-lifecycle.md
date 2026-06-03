# Behaviors, ActorContext & lifecycle

Akka Typed (2.10.x). Code Scala then Java. Source: doc.akka.io/libraries/akka-core/current/typed/{actors,actor-lifecycle,dispatchers,mailboxes}.html

## Behaviors factories & signals

`Behaviors` factory methods build a `Behavior[T]`:

- `receive((ctx, msg) => …)` / `receiveMessage(msg => …)` (no context) — handle a message, return the next behavior.
- `setup(ctx => …)` — runs on start **and on restart**; the place to create children, acquire resources, read `ActorContext`. Wrap mutable state here so restart gets a fresh copy.
- `receivePartial` / `receiveMessagePartial` — `PartialFunction` variants (composable across states with `orElse`).
- `same` (stay), `stopped` (stop self), `unhandled` (reuse + log), `empty` (expect no messages), `ignore` (drop silently).
- `withTimers(timers => …)` (scheduled/periodic self-messages), `withStash(capacity)(buffer => …)`, `supervise(b).onFailure[E](strategy)`, `monitor(probe, b)`, `withMdc(...)`.

Signals (lifecycle/system notifications) handled via `.receiveSignal { case (ctx, sig) => … }` (Scala) / `.onSignal(Sig.class, …)` (Java): `PostStop` (clean up on stop), `PreRestart` (clean up before restart — `PostStop` is **not** emitted on restart, so handle both), `Terminated`/`ChildFailed` (a watched actor stopped).

```scala
Behaviors.setup[Command] { context =>
  context.log.info("starting")
  Behaviors.receiveMessage[Command] { … }
    .receiveSignal { case (_, PostStop) => cleanup(); Behaviors.same }
}
```
```java
Behaviors.setup(context -> {
  context.getLog().info("starting");
  return Behaviors.receive(Command.class)
    .onMessage(...)
    .onSignal(PostStop.class, sig -> { cleanup(); return Behaviors.same(); })
    .build();
});
```

## ActorContext

Obtain from `setup`/`receive`. **Not thread-safe** — only touch on the actor's own message thread (never from `Future`/`CompletionStage` callbacks, never share). Provides: `spawn`/`spawnAnonymous`, `stop(child)`, `watch`/`watchWith`/`unwatch`, `self`/`getSelf`, `log`/`getLog`, `messageAdapter`, `ask`, `pipeToSelf`, `setReceiveTimeout`, `system`, `executionContext`/`getExecutionContext`.

## ActorSystem & the guardian

One `ActorSystem` per JVM (heavyweight; allocates dispatchers/threads). It's created from a root/guardian `Behavior`; messages to the system go to the guardian. Stopping the guardian stops the system.

```scala
val system: ActorSystem[Main.Command] = ActorSystem(Main(), "my-system")
system ! Main.Start("World")
```
```java
ActorSystem<Main.Command> system = ActorSystem.create(Main.create(), "my-system");
system.tell(new Main.Start("World"));
```

## Spawning, stopping, watching

- **Spawn children** from `ActorContext`: `context.spawn(behavior, "name")`, `context.spawnAnonymous(behavior)`, with optional `Props` (dispatcher/mailbox/tags): `context.spawn(b, "name", DispatcherSelector.blocking())`.
- **Stop**: return `Behaviors.stopped` (self) or `context.stop(childRef)` (a direct child only). A child can never outlive its parent; stopping a parent recursively stops children; `ActorSystem` shutdown stops all. On stop the actor gets `PostStop`.
- **Watch**: `context.watch(ref)` → receive a `Terminated(ref)` signal when `ref` stops; `context.watchWith(ref, MyMsg)` → receive your own message instead (**preferred** — can carry context). Works across cluster nodes. `Terminated` is delivered even if the watched actor was already dead.

## SpawnProtocol — spawning from outside the guardian

When code outside the actor hierarchy (e.g. an HTTP route) needs to spawn actors, make the guardian a `SpawnProtocol`:

```scala
def apply(): Behavior[SpawnProtocol.Command] = Behaviors.setup(_ => SpawnProtocol())
// val ref: Future[ActorRef[Greet]] = system.ask(SpawnProtocol.Spawn(Greeter(), "greeter", Props.empty, _))
```
```java
Behaviors.setup(ctx -> SpawnProtocol.create());
```

## Dispatchers

A `MessageDispatcher` runs actors and is also an `ExecutionContext`. Default = `akka.actor.default-dispatcher` (fork-join). Select per actor at spawn via `DispatcherSelector`: `default()`, `blocking()`, `sameAsParent()`, `fromConfig("path")`.

**Never block on the default dispatcher** — it starves *all* actors. Wrapping in a `Future` on the actor's EC, `Await`, or `CompletableFuture.get()` does **not** help (ManagedBlocker can exhaust the pool). The fix is a dedicated **`thread-pool-executor` with `fixed-pool-size`** (bulkheading), or on Java 21+ a `virtual-thread-executor`:

```hocon
my-blocking-dispatcher {
  type = Dispatcher
  executor = "thread-pool-executor"
  thread-pool-executor { fixed-pool-size = 16 }
  throughput = 1
}
```
`throughput` = messages an actor processes before the thread is yielded (1 = most fair). `PinnedDispatcher` gives an actor its own single thread.

## Mailboxes

Each actor has a mailbox. **Default = `SingleConsumerOnlyUnboundedMailbox`** (fast MPSC, unbounded → OOM risk under overload). Select per actor via `MailboxSelector.bounded(capacity)` or `.fromConfig("path")` in `Props`. Bounded mailboxes route overflow to `deadLetters`. Other types: `NonBlockingBoundedMailbox`, `UnboundedControlAwareMailbox` (prioritizes `ControlMessage`), `Unbounded/BoundedPriorityMailbox`, stable-priority variants. Custom mailboxes implement `MessageQueue` + a `MailboxType` with a `(Settings, Config)` constructor.
