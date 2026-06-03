---
name: akka-diagnostics
description: Akka Diagnostics (Scala+Java) — two startup-time diagnostic tools for Akka apps. The Config Checker scans configuration for typos, misplaced settings, conflicting/sub-optimal values, and risky "power-user" changes; the Thread Starvation Detector watches dispatchers and warns (with aggregated stack traces) when one becomes unresponsive, usually from blocking work on the default dispatcher. Covers enabling them, what each catches (dispatcher sizing, failure-detector settings, remoting frame size, typos), how to silence intentional settings (disabled-checks, confirmed-power-user-settings, confirmed-typos), failing tests on warnings, and how to fix starvation (dedicated dispatchers). Use when diagnosing latency/timeouts/thread-starvation in an Akka app, validating Akka configuration, or hardening an Akka deployment. Complements akka-actors (dispatchers) and akka-cluster.
---

# Akka Diagnostics

Two tools that **run automatically when the ActorSystem starts** (single dependency `com.lightbend.akka:akka-diagnostics`): the **Config Checker** and the **Thread Starvation Detector**. They catch the configuration and operational mistakes the Akka team sees most often. Complements [[akka-actors]] (dispatchers/blocking) and [[akka-cluster]].

Cross-links: [[akka]] (meta), [[akka-actors]], [[akka-cluster]]. Pin all `akka-*` to one version.

## Thread Starvation Detector

A monitor thread schedules a trivial task on a dispatcher and measures how long it takes to run; if it exceeds a threshold it logs a **warning with aggregated stack traces** of the busy threads. The usual cause is **blocking work on the default dispatcher**, which starves mailbox processing and `Future` callbacks → high latency despite low CPU, timeouts, failing remoting.

Auto-runs on the main dispatcher when the dependency is present. For others: `StarvationDetector.checkDispatcher(system, "my-dispatcher")` / `checkExecutionContext(...)`.
```hocon
akka.diagnostics.starvation-detector {
  check-interval = 1s
  initial-delay = 10s                 # skip startup noise (class loading / JIT)
  max-delay-warning-threshold = 100ms # lower to catch smaller stalls
  warning-interval = 10s              # min gap between warnings
  thread-traces-limit = 5
}
```
**Java 17+** needs the JVM flag `--add-opens=java.base/java.util.concurrent=ALL-UNNAMED`. **The fix** is almost always: move blocking calls off the default dispatcher onto a dedicated `thread-pool-executor` (bulkhead) dispatcher (see [[akka-actors]] dispatchers). Trust the stack traces over thread-state counts (native blocking IO shows as `RUNNABLE`); a trace is one sample = an indication.

## Config Checker

Scans config at startup for suspicious/typo'd/conflicting/sub-optimal settings, logging WARNs via logger `akka.diagnostics.ConfigChecker` (messages start `Configuration recommendation:`). General rule it enforces: **use defaults until you have a measured problem.**

```hocon
akka.diagnostics.checker {
  fail-on-warning = on              # throw IllegalArgumentException on ActorSystem start if any issue (great in a config test)
  disabled-checks = []              # disable a check by its key, e.g. ["dispatcher-throughput"]
  confirmed-power-user-settings = []# low-level settings you knowingly changed
  confirmed-typos = []              # config paths under akka.* that are intentional (e.g. your app's settings)
}
```
Run standalone: main class `akka.diagnostics.ConfigChecker` (exits -1 with issues, 0 when clean).

**What it catches** (check keys): `[typo]` (props under `akka.*` with no `reference.conf` match — put app settings *outside* the `akka` tree, or add to `confirmed-typos`); `[power-user-settings]` (changing low-level constants like gossip/failure-detector internals — confirm via `confirmed-power-user-settings`); dispatcher sizing (`[default-dispatcher-size]`, `[dispatcher-throughput]`, `[dispatcher-count]`, `[fork-join-pool-size]` — don't size up the default dispatcher for blocking; use a dedicated one); failure detectors (`[cluster-failure-detector]`, `[remote-watch-failure-detector]` — too-short `acceptable-heartbeat-pause` causes false unreachable/**quarantine**); remoting (`[maximum-frame-size]` large messages delay heartbeats; `[remote-artery-disabled]` classic remoting is deprecated); `[cluster-dispatcher]` (needing `akka.cluster.use-dispatcher` usually means you're running blocking/CPU-heavy work on the default dispatcher).

## Always-apply defaults

1. **Keep both tools enabled** (they're on by default with the dependency); add the Java 17+ `--add-opens` flag for the starvation detector.
2. **Add a test that boots with production-like config and `akka.diagnostics.checker.fail-on-warning = on`** so config regressions fail CI.
3. **Treat a starvation warning as a blocking-on-the-wrong-dispatcher bug** — move blocking work to a dedicated bulkhead dispatcher ([[akka-actors]]); don't just raise the threshold.
4. **Put application config outside the `akka.*` namespace** to avoid false `[typo]` warnings; only silence checks you've deliberately decided on (`disabled-checks`/`confirmed-*`).
5. **Don't shorten failure-detector `acceptable-heartbeat-pause` to silence warnings** — false positives quarantine remote nodes (fatal) or wrongly mark cluster members unreachable.

## Anti-patterns (flag in review)

- Silencing a starvation warning by raising the threshold instead of fixing the blocking call; sizing up the default dispatcher for blocking work.
- Disabling the config checker wholesale; adding app settings under `akka.*` then suppressing the typo check; changing power-user/failure-detector settings without a measured reason.

## Related

- [[akka-actors]] (dispatchers / "blocking needs careful management") · [[akka-cluster]] (failure detectors, remoting) · [[akka]] (meta).
- Source: https://doc.akka.io/libraries/akka-diagnostics/current/
