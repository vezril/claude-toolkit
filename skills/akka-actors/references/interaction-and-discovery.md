# Interaction patterns, discovery & routers

Akka Typed (2.10.x). Source: doc.akka.io/libraries/akka-core/current/typed/{interaction-patterns,actor-discovery,routers}.html

## Interaction patterns

**Fire-and-forget** — `ref ! msg` / `ref.tell(msg)`. No delivery/processing guarantee; risk of unbounded inflow → OOM. Default for one-way notifications.

**Request-Response** — put the reply address in the message: `final case class Req(data: X, replyTo: ActorRef[Resp])`; the receiver does `replyTo ! Resp(...)`. Good for streams of replies/subscriptions. Correlate with a request id if needed.

**Adapted response** — when an actor talks to another whose response type shouldn't pollute its own protocol, register a **message adapter** in `setup` and wrap the foreign response into a private `Command` subtype:
```scala
val adapter: ActorRef[Backend.Response] = context.messageAdapter(WrappedBackendResponse(_))
backend ! Backend.Job(id, adapter)
// handle: case WrappedBackendResponse(resp) => …
```
```java
ActorRef<Backend.Response> adapter = context.messageAdapter(Backend.Response.class, WrappedBackendResponse::new);
```

**ActorContext.ask** — request-response **between two actors** (1:1), turning success/failure into a `Command`. The adapting function runs *in the asking actor* (safe to read its state; if it throws, the actor stops). Needs a `Timeout`. Prefer this over `?` inside an actor.
```scala
context.ask(hal, Hal.Open.apply) {
  case Success(Hal.Response(m)) => AdaptedResponse(m)
  case Failure(_)               => AdaptedResponse("request failed")
}
```
```java
context.ask(Hal.Response.class, hal, Duration.ofSeconds(3),
  ref -> new Hal.Open(ref),
  (resp, thr) -> resp != null ? new AdaptedResponse(resp.message) : new AdaptedResponse("failed"));
```

**AskPattern** — request-response **from outside** an actor; returns a `Future`/`CompletionStage` that fails with `TimeoutException`.
```scala
import akka.actor.typed.scaladsl.AskPattern._
implicit val timeout: Timeout = 3.seconds
val f: Future[Reply] = target.ask(ref => GiveMeCookies(3, ref))
```
```java
CompletionStage<Reply> f = AskPattern.ask(target, ref -> new GiveMeCookies(3, ref),
    Duration.ofSeconds(3), system.scheduler());
```

**pipeToSelf** — bridge a `Future`/`CompletionStage` back into the actor as a message; **the only safe way to use async results** (never touch actor state in the Future callback):
```scala
context.pipeToSelf(db.update(v)) {
  case Success(_) => Updated(v.id); case Failure(e) => UpdateFailed(v.id, e)
}
```
```java
context.pipeToSelf(db.update(v), (ok, err) -> err == null ? new Updated(v.id()) : new UpdateFailed(v.id(), err));
```

**StatusReply** — a reply that is success or error: `StatusReply.Success(v)` / `StatusReply.Error("msg")` / `StatusReply.Ack` (= `StatusReply[Done]`). `context.askWithStatus` / `AskPattern.askWithStatus` unwrap the error side into a failed Future. Use it instead of bespoke `Ok | Error` reply hierarchies (heavily used by [[akka-persistence]]).

**Ignore replies** — pass `context.system.ignoreRef` as `replyTo` to make a request-response one-way (won't ever terminate; don't use with an outside `ask`).

**Per-session child / aggregator** — spawn a short-lived child to collect replies from several actors (using a message adapter), reply once, then stop. The reusable form is a general aggregator actor that gathers N replies under a timeout.

## Actor discovery — the Receptionist

To find actors without passing refs around, register against a `ServiceKey[T]` and look them up (local **and** cluster-wide).
```scala
val Key = ServiceKey[Ping]("pingService")
context.system.receptionist ! Receptionist.Register(Key, context.self)
context.system.receptionist ! Receptionist.Subscribe(Key, subscriberRef)   // ongoing Listings
context.system.receptionist ! Receptionist.Find(Key, adapterRef)            // one-shot
// handle: case Key.Listing(instances) => instances.foreach(…)
```
```java
ServiceKey<Ping> key = ServiceKey.create(Ping.class, "pingService");
ctx.getSystem().receptionist().tell(Receptionist.register(key, ctx.getSelf()));
ctx.getSystem().receptionist().tell(Receptionist.subscribe(key, subscriber));
// msg.getServiceInstances(key).forEach(...)
```
Cluster Receptionist state propagates via Distributed Data (eventually consistent), tracks reachability, and lists only **reachable** actors (use `allServiceInstances` for the full set). Messages must be serializable. Use it for **initial contact** (scales to thousands of services, not high turnover), not as a registry of millions.

## Routers

Distribute same-typed messages over routees. The router is itself one actor with one mailbox (sequential routing can bottleneck very high throughput — for stable routing + rebalancing use [[akka-cluster]] sharding).

**PoolRouter** — creates N local children from a routee behavior (never spread across the cluster). Default round-robin. Supervise the routee so a crash doesn't shrink the pool to zero.
```scala
val pool = Routers.pool(4)(Behaviors.supervise(Worker()).onFailure[Exception](SupervisorStrategy.restart))
val router = ctx.spawn(pool.withRouteeProps(DispatcherSelector.blocking()), "pool")
```
```java
PoolRouter<Worker.Command> pool = Routers.pool(4,
    Behaviors.supervise(Worker.create()).onFailure(SupervisorStrategy.restart()));
ActorRef<Worker.Command> router = ctx.spawn(pool, "pool");
```

**GroupRouter** — created from a `ServiceKey`; discovers routees via the Receptionist → **cluster-aware**. Default random. Stashes until the first listing arrives; drops (to `Dropped`) if the listing is empty.
```scala
val router = ctx.spawn(Routers.group(serviceKey), "group")
```

Strategies: round-robin (pool default), random (group default), consistent-hashing (`withConsistentHashingRouting(virtualNodesFactor, hashKey)` — same hash → same routee while membership is stable). `withBroadcastPredicate` sends matching messages to all routees.
