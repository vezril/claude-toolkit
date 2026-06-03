---
name: akka-utilities
description: Akka core utilities (Akka Core 2.10.x, Typed API) in Scala and Java — the EventStream (system pub/sub + dead letters), logging (SLF4J/Logback, context.log, MDC, async logging), the Circuit Breaker (fail-fast for failing dependencies), Futures patterns (Patterns.after/retry, pipeToSelf, ask interop), and extending Akka with custom Extensions. Use whenever subscribing to system events or dead letters, setting up or debugging Akka logging/MDC/log levels, protecting calls to a flaky dependency with a circuit breaker, adding timeouts/retries to Futures, bridging async results into actors, or building a per-ActorSystem extension — even if "utilities" isn't named but EventStream, dead letters, logging config, circuit breakers, or Akka extensions are involved. Builds on akka-actors.
---

# Akka Utilities

Cross-cutting helpers in `akka-actor`/`akka-actor-typed`: the **EventStream**, **logging**, the **Circuit Breaker**, **Futures patterns**, and **Extensions**. Builds on [[akka-actors]]. Cross-links: [[akka]] (meta), [[akka-actors]], [[modern-java]].

## EventStream — system pub/sub & dead letters

Each `ActorSystem` has an `eventStream` carrying log events and **dead letters**, open for user pub/sub with **subchannel classification** (subscribing to a supertype receives all subtypes). It is a **local** facility (not cluster-distributed — use the [[akka-cluster]] Receptionist, group routers, or Distributed Pub-Sub for cluster-wide events).

```scala
import akka.actor.typed.eventstream.EventStream.{Subscribe, Publish}
val adapter = context.messageAdapter[DeadLetter](d => d.message.toString)
context.system.eventStream ! Subscribe(adapter)
context.system.eventStream ! Publish(Jazz("Sonny Rollins"))
```
```java
ActorRef<DeadLetter> adapter = context.messageAdapter(DeadLetter.class, d -> d.message().toString());
context.getSystem().eventStream().tell(new Subscribe<>(DeadLetter.class, adapter));
```
**Dead letters:** messages to a stopped actor are wrapped in `akka.actor.DeadLetter` and published. Subscribe to `DeadLetter`, `SuppressedDeadLetter`, or `AllDeadLetters` to debug. The stream doesn't preserve the sender — put any reply ref in the message. Custom buses: `LookupEventBus`, `SubchannelEventBus`, `ScanningEventBus`, `ManagedActorEventBus`.

## Logging

Backend is **SLF4J 2.0** (recommended: Logback). Each actor gets a logger via `context.log` / `context.getLog()`:

```scala
context.log.info("Received message: {}", message)    // {} placeholders avoid string concat when disabled
```
```java
getContext().getLog().info("Received message: {}", message);
```
- Logger name defaults to the behavior's class; override with `context.setLoggerName(...)`. **Don't cache the logger** (`getLog` sets the `akkaSource` MDC each call) and **never call it from a `Future` callback** (not thread-safe — use `LoggerFactory` there).
- **MDC:** built-in keys `akkaSource`, `akkaAddress`, `akkaTags`, `sourceActorSystem`; add custom via `Behaviors.withMdc(staticMap, perMessageFn)(behavior)`; tag actors with `ActorTags("processing")`. Render in Logback with `%X{akkaSource}` / `%mdc`.
- **Async logging is critical in production** — configure a Logback `AsyncAppender` (`<queueSize>8192</queueSize><neverBlock>true</neverBlock>`) so log IO doesn't starve dispatchers.
- `akka.loglevel` (default INFO) is a pre-filter applied *before* SLF4J — set it to DEBUG to let DEBUG reach the backend, then control the real level cheaply in Logback (incl. per-module: `<logger name="akka.cluster.sharding" level="DEBUG"/>`). `akka.stdout-loglevel` is for startup only. Tune `akka.log-dead-letters`. Markers include `SECURITY`, `ClusterLogMarker`, etc.

## Circuit Breaker

`akka.pattern.CircuitBreaker` fails fast once a dependency is unhealthy instead of piling up hanging calls. States: **Closed** (normal; counts failures/timeouts, trips at `maxFailures`) → **Open** (fail-fast with `CircuitBreakerOpenException` for `resetTimeout`) → **Half-Open** (first call probes; success → Closed, failure → Open). Pair with sensible `callTimeout`s.

```hocon
akka.circuit-breaker.data-access { max-failures = 5, call-timeout = 10s, reset-timeout = 1m }
```
```scala
val breaker = CircuitBreaker("data-access")(context.system)     // named lookup; same name => same instance
val result: Future[Done] = breaker.withCircuitBreaker(service.call(id))
context.pipeToSelf(result) { case Success(_) => Ok; case Failure(e) => Failed(e) }
```
```java
CircuitBreaker breaker = CircuitBreaker.lookup("data-access", context.getSystem());
CompletionStage<Done> result = breaker.callWithCircuitBreakerCS(() -> service.call(id));
```
Variants: `withSyncCircuitBreaker` (synchronous), a `defineFailureFn` to count specific successes as failures, listeners (`onOpen`/`onClose`/`onHalfOpen`, `onCallFailure`…), and a low-level `succeed()`/`fail()` + `isClosed`/`isOpen`/`isHalfOpen` API for "tell protection" (guarding fire-and-forget message sends).

## Futures patterns

In `akka.pattern` (Scala) / `akka.pattern.Patterns` (Java):
- **`after(duration)(fallback)`** — complete a Future/CS after a delay; combine with `firstCompletedOf` for a timeout.
- **`retry(() => future, attempts, delay)`** — retry a Future/CS N times with a delay.
- **`pipeToSelf`** — bring an async result back into a typed actor as a message (the safe way to use Futures in actors; never touch actor state in the callback). Ask interop: `context.ask`/`askWithStatus` inside an actor, `AskPattern.ask` from outside.

```scala
val delayed = akka.pattern.after(200.millis)(Future.failed(new TimeoutException))
val result  = Future.firstCompletedOf(Seq(realFuture, delayed))
```

## Extending Akka

An **Extension** is created **once per `ActorSystem`** and reachable everywhere (the mechanism behind Cluster, Serialization, Sharding). Implement an `Extension` (holds the state/API, must be **thread-safe**) + an `ExtensionId[T]` (identity/factory; `createExtension` runs once).

```scala
class DatabasePool(system: ActorSystem[_]) extends Extension { val connection = new Conn() }
object DatabasePool extends ExtensionId[DatabasePool] {
  def createExtension(system: ActorSystem[_]) = new DatabasePool(system)
  def get(system: ActorSystem[_]) = apply(system)   // Java API
}
DatabasePool(system).connection
```
```java
public class DatabasePool implements Extension {
  public final Conn connection = new Conn();
  public static class Id extends ExtensionId<DatabasePool> {
    private static final Id instance = new Id();
    @Override public DatabasePool createExtension(ActorSystem<?> s) { return new DatabasePool(s); }
    public static DatabasePool get(ActorSystem<?> s) { return instance.apply(s); }
  }
}
```
Eager-load at startup via `akka.actor.typed.extensions = ["com.example.DatabasePool"]` (typed; classic uses `akka.extensions`).

## Related

- [[akka-actors]] — utilities operate on actors (`context.log`, `pipeToSelf`, `messageAdapter`).
- [[akka-cluster]] — for cluster-wide events use the Receptionist / Distributed Pub-Sub, not the local EventStream.
- [[modern-java]] — circuit breaker, timeouts, and structured logging are general robustness practices.
- Source: Akka Core docs, https://doc.akka.io/libraries/akka-core/current/index-utilities.html (v2.10.x).
