---
name: akka-sdk-timed-actions
description: Akka SDK Timed Actions (Java) — schedule a durable deferred call to run at or after a future time (timeouts, reminders, "do X later"), guaranteed to run at least once by the Akka runtime. Covers the TimedAction component (extend TimedAction, @Component(id), effects().done()/error()), scheduling via the injected TimerScheduler (createSingleTimer(name, delay, deferredCall), delete), deduplication by unique timer name, building deferred ComponentClient calls (.deferred(arg)), retry/backoff behavior, limits, and designing the target to be idempotent. Use to implement order/payment expiration, confirmation timeouts, reminders, or scheduled work in an Akka SDK service. Part of the Akka SDK (Java); see akka-sdk for the model and akka-sdk-workflows for multi-step orchestration.
---

# Akka SDK — Timed Actions

Schedule a call to run **at/after a future time** — order/payment expiration, confirmation timeouts, reminders, "check later". Timers are **stored by the Akka runtime and guaranteed to run at least once**: on success the timer auto-removes; on failure it reschedules (exponential backoff) until it succeeds. Part of the [[akka-sdk]] (Java).

Cross-links: [[akka-sdk]] (meta), [[akka-sdk-workflows]] (durable multi-step orchestration — often a better fit than many timers), [[akka-sdk-event-sourced-entities]] / [[akka-sdk-key-value-entities]] (timer targets).

## Scheduling & the component

Inject `TimerScheduler` (available in Setup, Endpoints, Consumers, Timed Actions, Workflows) and schedule a **deferred** `ComponentClient` call:

```java
// scheduling (e.g. from an endpoint), BEFORE the business op
private String timerName(String orderId) { return "order-expiration-" + orderId; }
timerScheduler.createSingleTimer(
  timerName(orderId),                       // unique name across the cluster — rescheduling the same name REPLACES it
  Duration.ofSeconds(10),
  componentClient.forTimedAction().method(OrderTimedAction::expireOrder).deferred(orderId));

// the Timed Action component
@Component(id = "order-timed-action")
public class OrderTimedAction extends TimedAction {
  private final ComponentClient componentClient;
  public OrderTimedAction(ComponentClient cc) { this.componentClient = cc; }

  public Effect expireOrder(String orderId) {
    var result = componentClient.forKeyValueEntity(orderId).method(OrderEntity::cancel).invoke();
    return switch (result) {                 // NotFound/Invalid/Ok all => done() (obsolete => no reschedule)
      case OrderEntity.Result.Ok o, OrderEntity.Result.NotFound n, OrderEntity.Result.Invalid i -> effects().done();
    };
  }
}
```

A Timed Action `extends TimedAction`, has `@Component(id)`, and its handlers return `effects().done()` (success → timer removed) or `effects().error(...)` (failure → reschedule). A timer can target **any** `ComponentClient`-reachable method, not only Timed Actions. Cancel with `timerScheduler.delete(timerName(orderId))`.

## Always-apply defaults

1. **Use a deterministic timer name keyed on the business id** — timers are unique by name across the cluster, so scheduling the same name **replaces** the existing one (this is the dedup mechanism).
2. **Register the timer *before* the business operation** so a failed registration leaves no untracked work; the target handles the reverse (timer fires, op never completed) gracefully.
3. **The timer target must not fail unless retry is intended** — an unhandled error reschedules forever. Design it to return success for terminal/obsolete cases (entity not found / already cancelled).
4. **Make the target idempotent** — it may run more than once (at-least-once); deleting the timer on completion is just housekeeping (the target still handles an obsolete trigger).
5. **Reach for [[akka-sdk-workflows]] instead** when you need multi-step orchestration with retries/compensation — Timed Actions are for single deferred calls.

## Limits & evolution

- Payload ≤ **1024 bytes**; ≤ **50,000 active timers** per service.
- Backoff starts ~3s, capped ~30s, indefinite by default (cap via the `maxRetries` parameter).
- The serialized timer stores **component id + method name + parameter**, so those must stay stable across deploys — a changed id/method/payload makes the timer fail and reschedule until a compatible deploy. When refactoring a timer-target method, keep the old method (delegate or make it a no-op `return effects().done();`) while scheduled calls may still reference it.
- CLI: `akka services components list-timers <service> -o json`.

## Anti-patterns (flag in review)

- Random/non-deterministic timer names (lose the dedup/replace semantics); registering the timer after the business op.
- A target that throws/`error()`s on obsolete triggers (reschedules forever); non-idempotent target side effects.
- Renaming/moving a timer-target method without keeping a compatible shim; using many timers where a Workflow's steps/timeouts fit better.

## Related

- [[akka-sdk]] · [[akka-sdk-workflows]] · [[akka-sdk-event-sourced-entities]] · [[akka-sdk-key-value-entities]]
- Source: https://doc.akka.io/sdk/timed-actions.html
