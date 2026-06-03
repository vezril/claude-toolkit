---
name: akka-sdk-workflows
description: Akka SDK Workflows (Java) — durable, long-running, multi-step orchestration (the saga primitive) with reliable execution, retries, timeouts, compensation, and pause/resume. Covers defining a Workflow (extend Workflow<State>, @Component(id), WorkflowSettings), command handlers returning Effect (updateState/transitionTo/pause/end/reply) and internal step methods returning StepEffect (stepEffects().updateState/thenTransitionTo/thenPause/thenEnd), step timeouts and RecoverStrategy (maxRetries/failoverTo), durable execution & resume-from-where-it-left-off, saga compensation, human-in-the-loop pause/resume, calling components via ComponentClient, lifecycle control (terminate/suspend/resume/delete), notifications, and orchestrating agents. Use to coordinate multi-step business processes reliably, build sagas, or orchestrate Agents in an Akka SDK service. Part of the Akka SDK (Java); see akka-sdk for the model and akka-sdk-agents for agent orchestration.
---

# Akka SDK — Workflows

A **durable, long-running, multi-step orchestration** — the SDK's saga primitive. It models a business transaction in one place and the runtime keeps it running reliably (retries, timeouts) or rolls it back (compensation). Workflows are stateful, sharded, single-writer-per-id components that **resume from where they left off** after a crash/passivation/rolling update. The recommended way to orchestrate [[akka-sdk-agents]]. Part of the [[akka-sdk]] (Java).

Cross-links: [[akka-sdk]] (meta), [[akka-sdk-agents]] (orchestrate agents), [[akka-sdk-event-sourced-entities]] / [[akka-sdk-key-value-entities]] (steps call these), [[domain-driven-design]].

## Two Effect APIs

A Workflow is the only component with both:
- **`Effect`** — returned by **public command handlers** (called externally via `ComponentClient`): `effects().updateState(s).transitionTo(step).withInput(x).thenReply(...)`, `.pause()`, `.end()`, `.delete()`, `.error(...)`, `.reply(...)`; `ReadOnlyEffect<T>` for reads.
- **`StepEffect`** — returned by **internal step methods** (usually `private`): `stepEffects().updateState(s).thenTransitionTo(nextStep).withInput(x)`, `.thenPause(...)`, `.thenEnd()`.

```java
@Component(id = "transfer")
public class TransferWorkflow extends Workflow<TransferState> {
  private final ComponentClient componentClient;
  public TransferWorkflow(ComponentClient cc) { this.componentClient = cc; }

  @Override public WorkflowSettings settings() {
    return WorkflowSettings.builder()
      .defaultStepTimeout(Duration.ofSeconds(5))
      .defaultStepRecovery(RecoverStrategy.maxRetries(2).failoverTo(TransferWorkflow::compensateStep))
      .build();
  }

  public Effect<Done> start(Transfer t) {                      // command handler: starts the workflow
    if (currentState() != null) return effects().error("already started");
    return effects().updateState(new TransferState(t))
                    .transitionTo(TransferWorkflow::withdrawStep).withInput(new Withdraw(t.from(), t.amount()))
                    .thenReply(Done.getInstance());
  }

  private StepEffect withdrawStep(Withdraw w) {                // internal step
    componentClient.forEventSourcedEntity(w.from()).method(WalletEntity::withdraw).invoke(w.amount());
    return stepEffects().updateState(currentState().withStatus(WITHDRAWN))
                        .thenTransitionTo(TransferWorkflow::depositStep).withInput(new Deposit(/*...*/));
  }
  private StepEffect depositStep(Deposit d) {
    componentClient.forEventSourcedEntity(d.to()).method(WalletEntity::deposit).invoke(d.amount());
    return stepEffects().updateState(currentState().withStatus(COMPLETED)).thenEnd();
  }
}
```

Steps are methods referenced by **method reference** in `transitionTo`/`thenTransitionTo`; `@StepName` overrides the name. `.withInput(x)` passes typed input. `currentState()` reads state (override `emptyState()` to avoid null); `commandContext().workflowId()` gives the id.

## Always-apply defaults

1. **`@Component(id)` must be stable**; have at least one public command handler that starts the workflow and transitions to the first step.
2. **Make step side effects idempotent** — steps are retried, so non-idempotent calls (deposit/withdraw) will repeat; dedup by a command id.
3. **Workflows should only fail on *unknown* errors** — model expected failures as domain result types and **compensate** (transition to a compensation step) rather than throwing.
4. **Set step timeouts and a `RecoverStrategy`** (`maxRetries(n).failoverTo(step)`); the global workflow `timeout(...)` must be greater than any step timeout. AI/agent steps are slow — give them generous timeouts.
5. **Keep state a plain record with a status enum**; transitions update state durably so progress survives restarts.
6. **Use `thenPause` + a command handler to resume** for human-in-the-loop; guard resume handlers on the expected status.

## Durable execution, recovery, compensation, pause/resume

Detail in **`references/steps-recovery-saga.md`** — the steps/transitions model, `WorkflowSettings` (timeouts, `defaultStepRecovery`/`stepRecovery`, timeout handlers), durable resume-from-current-step, saga **compensation** (inspect a step's result and transition to a reversing step), **pause/resume** (`thenPause(pauseSetting(...).timeoutHandler(...))` + a guarded command handler), external **lifecycle control** (`componentClient.forWorkflow(id).terminate/suspend/resume`, `effects().delete()`), and **notifications** (push progress via `NotificationPublisher` → SSE).

## Orchestrating agents

The recommended pattern for [[akka-sdk-agents]]: a Workflow whose steps each call an agent via `componentClient.forAgent().inSession(sessionId()).method(SomeAgent::query).invoke(...)`, storing intermediate results in durable state, with generous step timeouts and bounded recovery. Agents in the same session share memory. For runtime-selected agents, use `AgentRegistry` + `dynamicCall` (see [[akka-sdk-agents]]).

## Anti-patterns (flag in review)

- Non-idempotent step side effects without dedup; throwing on expected failures instead of compensating.
- Workflow timeout ≤ step timeout (runtime rejects); no recovery strategy on steps that call flaky services.
- Driving agents/LLM calls with default (short) timeouts; chaining agents directly instead of orchestrating here.
- Resuming a paused workflow without checking the status; reusing a workflow id after delete.

## Related

- [[akka-sdk]] · [[akka-sdk-agents]] · [[akka-sdk-event-sourced-entities]] · [[akka-sdk-key-value-entities]] · [[akka-sdk-timed-actions]]
- Source: https://doc.akka.io/sdk/workflows.html
