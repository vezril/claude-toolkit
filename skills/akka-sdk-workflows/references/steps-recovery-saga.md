# Workflows: steps, recovery, saga, pause/resume, lifecycle

Akka SDK (Java). Source: doc.akka.io/sdk/workflows.html

## Settings: timeouts & recovery

```java
@Override public WorkflowSettings settings() {
  return WorkflowSettings.builder()
    .timeout(Duration.ofSeconds(10))                       // global workflow timeout (> any step timeout)
    .defaultStepTimeout(Duration.ofSeconds(2))             // default per-step (else 5s)
    .stepTimeout(TransferWorkflow::depositStep, Duration.ofSeconds(1))
    .defaultStepRecovery(RecoverStrategy.maxRetries(1).failoverTo(TransferWorkflow::failoverStep))
    .stepRecovery(TransferWorkflow::depositStep, RecoverStrategy.maxRetries(2).failoverTo(TransferWorkflow::compensateStep))
    .build();
}
```
A failing step is retried until it succeeds or hits the retry limit, then transitions to the `failoverTo` step. `RecoverStrategy.maxRetries(n).failoverTo(stepRef)`; `defaultStepRecovery` applies to all, `stepRecovery(stepRef, ...)` overrides one. A global `timeout` finishes the workflow (define a timeout handler step that **must end** the workflow). Workflow timeout must exceed step timeouts (validated at startup).

## Durable execution

The runtime executes steps reliably and durably; on restart/crash the workflow **resumes from the current non-completed step** (which is re-executed) — so step side effects must be idempotent.

## Compensation (saga rollback)

Model expected failures as domain result types and compensate; only let truly unknown errors fail the workflow.
```java
private StepEffect depositStep(Deposit d) {
  WalletResult r = componentClient.forEventSourcedEntity(d.to()).method(WalletEntity::deposit).invoke(d);
  return switch (r) {
    case Success ok -> stepEffects().updateState(currentState().withStatus(COMPLETED)).thenEnd();
    case Failure f  -> stepEffects().updateState(currentState().withStatus(DEPOSIT_FAILED))
                                    .thenTransitionTo(TransferWorkflow::compensateWithdrawStep);
  };
}
private StepEffect compensateWithdrawStep() {   // reverses the earlier withdraw (ordinary step)
  componentClient.forEventSourcedEntity(t.from()).method(WalletEntity::deposit).invoke(/* refund */);
  return stepEffects().updateState(currentState().withStatus(COMPENSATED)).thenEnd();
}
```

## Pause / resume (human-in-the-loop)

```java
private StepEffect waitForAcceptanceStep() {
  return stepEffects().thenPause(pauseSetting(Duration.ofHours(8)).timeoutHandler(TransferWorkflow::acceptanceTimeout));
}
public Effect<String> accept() {                                   // resume via a guarded command handler
  if (currentState().status() != WAITING_FOR_ACCEPTANCE) return effects().error("not awaiting acceptance");
  return effects().transitionTo(TransferWorkflow::withdrawStep).withInput(/*...*/).thenReply("accepted");
}
```
`thenPause` postpones until a command handler resumes; calls during an in-flight step are queued until it completes. Only accept resume when the status is expected.

## Lifecycle control (from outside, via ComponentClient)

- **Terminate:** `componentClient.forWorkflow(id).terminate(TransferWorkflow.class, "reason")` — stops permanently (cannot resume), preserves state, idempotent; in-flight step results ignored. (`terminateAsync()` → `CompletionStage`.)
- **Suspend / Resume:** `.suspend(W.class, "reason")` / `.resume(W.class)` — temporary halt keeping the option to continue; on resume the in-flight step restarts; timeouts stay active while suspended.
- **Delete:** from a command handler, `effects().delete().thenReply(done())` — ends + deletes; removal delayed (~1 week) so consumers see prior updates + the delete; `isDeleted()`; avoid id reuse.

## Notifications

Inject `NotificationPublisher<T>`, `publish(msg)` in steps, expose `NotificationStream<T> updates() { return notificationPublisher.stream(); }`; clients subscribe via `componentClient.forWorkflow(id).notificationStream(W::updates).source()` → SSE (`HttpResponses.serverSentEvents(...)`). Live-only, **not guaranteed delivery** — don't build business logic on it; reconcile by fetching authoritative state.

## Retrieving state

```java
public ReadOnlyEffect<TransferState> getState() {
  return currentState() == null ? effects().error("not started") : effects().reply(currentState());
}
```
Convert internal state to a public model in endpoints.

## Testing

Workflow integration tests extend `TestKitSupport`, drive via `componentClient.forWorkflow(id).method(...).invoke(...)`, and poll state with Awaitility (the docs page didn't include a dedicated testing section; this follows the SDK's standard integration-test pattern).
