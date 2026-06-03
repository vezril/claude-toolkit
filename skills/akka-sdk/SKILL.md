---
name: akka-sdk
description: The Akka SDK (doc.akka.io/sdk) — the opinionated, component-based Java framework (the evolution of Kalix) for building event-driven, transactional, and agentic services that the Akka runtime persists, shards, replicates, and scales for you. This is the meta/overview skill: it explains the programming model (components, the ComponentClient, declarative Effects, dependency injection, the api/application/domain layering), the deployment model (services, regions, projects, dev vs self-managed vs Akka Automated Operations), running/building/testing, and the full component catalog, routing to the per-component skills (agents, event-sourced-entities, key-value-entities, views, workflows, endpoints, consumers, timed-actions). Use as the entry point for any Akka SDK question, when starting or structuring an Akka SDK service, choosing which component fits, or when unsure which SDK piece solves a problem. The SDK is Java-only and distinct from the Akka Core libraries. From any SDK task, defer to the specific component skill for detail.
---

# Akka SDK (overview / meta)

The Akka SDK (formerly **Kalix**) is an **opinionated, component-based Java framework** for building event-driven, transactional, analytics, edge, and **agentic** services. You write small declarative **components**; the **Akka runtime** transparently handles persistence, consistency, sharding, clustering, replication, request routing, and scaling — **no database to manage, no service mesh to wire**. This is the map skill; for any real work, **read the specific component skill** linked below.

**Java-only** API (everything under `akka.javasdk.*`, Java 21, records used heavily). It is **distinct from the Akka Core libraries** (`akka-actor`, cluster, persistence, streams) — those are the low-level toolkit you assemble yourself ([[akka]]); the SDK sits on top and hides that machinery behind a constrained, productive model.

Cross-links: per-component skills [[akka-sdk-agents]], [[akka-sdk-event-sourced-entities]], [[akka-sdk-key-value-entities]], [[akka-sdk-views]], [[akka-sdk-workflows]], [[akka-sdk-endpoints]], [[akka-sdk-consumers]], [[akka-sdk-timed-actions]]; and [[akka]] (Core), [[domain-driven-design]], [[event-storming]], [[modern-java]].

## Programming model (in one breath)

- **Components** are classes you write that extend an SDK base type (`Agent`, `EventSourcedEntity`, `KeyValueEntity`, `Workflow`, `View`, `Consumer`, `TimedAction`) or carry an endpoint annotation (`@HttpEndpoint`, `@GrpcEndpoint`, `@McpEndpoint`). Each is identified by `@Component(id = "...")` (unique, stable across deploys).
- **Declarative Effects:** handlers don't perform side effects directly — they return an `Effect<T>` (or `ReadOnlyEffect`/`StepEffect`/`QueryEffect`) describing what the runtime should do (reply, persist, update, transition, schedule, fail). Build with `effects()...`.
- **`ComponentClient`** (injected) is the type-safe, location-transparent way components call each other: `componentClient.forEventSourcedEntity(id).method(Entity::handler).invoke(arg)` (sync; `invokeAsync` for `CompletionStage`, `deferred` for timers). Calls go over the network (JSON-serialized), not direct method calls.
- **Dependency injection** via constructor (the runtime injects `ComponentClient`, `Config`, `TimerScheduler`, `HttpClientProvider`, component contexts, etc.); custom deps via a `DependencyProvider`. One optional `@Setup ServiceSetup` class has `onStartup`/`onShutdown` hooks.
- **Layered project structure:** `domain/` (plain Java records + business logic, no Akka dependency, unit-testable), `application/` (the Akka components), `api/` (HTTP/gRPC/MCP endpoints that call components via `ComponentClient` and enforce ACLs). Inner layers must not depend on outer; never expose domain types externally.

## The component catalog — which to reach for

Detail in each component's skill:

- **[[akka-sdk-agents]]** — a stateful, durable component that calls an LLM to do one task (session memory, tools/function-calling, structured output, guardrails). *Use for AI/LLM steps.*
- **[[akka-sdk-event-sourced-entities]]** — durable entity whose state is derived from a persisted event log (CQRS source of truth, audit trail). *Use for stateful domain aggregates that need history.*
- **[[akka-sdk-key-value-entities]]** — durable entity storing the latest state directly (CRUD-style, no event log). *Use when you only need current state.*
- **[[akka-sdk-views]]** — read-optimized projection built from entity/topic/stream events, queried with SQL-like syntax. *Use to query by non-id attributes / across instances (CQRS read side).*
- **[[akka-sdk-workflows]]** — durable, long-running multi-step orchestration (the saga primitive) with retries, timeouts, compensation, pause/resume. *Use to coordinate steps reliably, incl. orchestrating agents.*
- **[[akka-sdk-endpoints]]** — HTTP / gRPC / MCP endpoints exposing your service to the outside world (and to LLM clients). *The only externally reachable components.*
- **[[akka-sdk-consumers]]** — consume events/changes (from entities, workflows, other services, or Kafka/PubSub topics) and optionally produce to topics/streams. *Use for eventing in/out and projections to external systems.*
- **[[akka-sdk-timed-actions]]** — schedule a durable deferred call (timeouts, reminders). *Use for "do X later".*

## Deployment model

Services are **distributed by design**, packaged as a single container image, and **self-cluster** (no service mesh). Three modes with identical behavior and no code changes:

- **Development** — default when you build/run any SDK service locally; full persistence/clustering simulated in-process.
- **Self-managed** — run the Akka clusters on your own infra/Kubernetes; you handle routing/certs/persistence.
- **Akka Automated Operations** — deploy from the Akka CLI to Akka's serverless cloud or your private region; multi-region replication, failover, auto-scaling, rolling upgrades.

**Logical model:** a **Service** is the unit of deployment (one image; scaled independently); a **Project** groups services and lists **regions** (first listed = primary); a service runs in a **cluster** spanning nodes in a **region**.

Detail on programming model and run/deploy/test in the references:

- **`references/programming-model.md`** — `ComponentClient`, the Effect API, dependency injection & `ServiceSetup`, calling other services (`HttpClientProvider`/`GrpcClientProvider`), configuration, and the api/application/domain layering.
- **`references/run-deploy-test.md`** — project setup (Maven, `akka-javasdk`), running locally (`mvn compile exec:java`, the local console, dev-mode persistence/eventing), deploying via the Akka CLI, and integration testing with `TestKitSupport`.

## Always-apply defaults

1. **Keep business logic in `domain/` (plain records/functions), thin components in `application/`, endpoints in `api/`.** Never expose domain types over the wire; map to API records.
2. **Change state only through Effects** — never mutate component fields directly (lost on reload); entities change via `persist`/`updateState`, never in-place.
3. **`@Component(id)` must be unique and stable** across production deploys (changing it makes the runtime treat it as brand new — replays/rebuilds).
4. **Call components via `ComponentClient`** (synchronous `invoke()` by default; the runtime optimizes it); never reach into another component's storage.
5. **Secure endpoints explicitly** — no `@Acl` means no client is allowed; grant access deliberately.
6. **Design for at-least-once and reconnection** — consumers may see duplicates (dedup yourself); streaming connections (SSE/gRPC/WebSocket) rebalance, so clients must reconnect with offsets.

## Anti-patterns (flag in review)

- Mutating component state in place instead of via an Effect; calling another component's database directly.
- Putting domain logic in endpoints/components instead of `domain/`; exposing internal event/state types externally.
- Endpoints with no `@Acl`; relying on a long-lived in-JVM object behind a stream.
- Using an Agent for non-AI logic (use an Entity/Workflow), chaining agents directly (orchestrate with a Workflow).
- Reusing a component/entity id after deletion; changing `@Component(id)` casually.

## Related

- [[akka]] — the Akka **Core** libraries the SDK is built on (use those directly when you need low-level control instead of the SDK's model).
- [[domain-driven-design]], [[event-storming]] — model the domain (aggregates, events, bounded contexts) before mapping it to entities/views/workflows.
- [[modern-java]] — the SDK is idiomatic modern Java (records, sealed types, Java 21).
- Source: Akka SDK docs, https://doc.akka.io/sdk/index.html and https://doc.akka.io/concepts/.
