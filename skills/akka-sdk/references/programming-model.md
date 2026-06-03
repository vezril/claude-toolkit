# Akka SDK programming model

Java, package `akka.javasdk.*`. Source: doc.akka.io/sdk/{setup-and-dependency-injection,component-and-service-calls}.html, concepts/architecture-model.html

## Layering (api / application / domain)

```
src/main/java/acme/app/
  api/          # HTTP/gRPC/MCP endpoints — call components via ComponentClient, enforce @Acl/validation
  application/  # Akka components: Agents, Entities, Views, Workflows, Consumers, Timed Actions
  domain/       # plain Java (records) business logic — no Akka dependency, unit-testable in isolation
src/main/resources/application.conf
```
Inner layers must not depend on outer ones; the api layer must not call domain directly (go through a component); never expose domain types externally — map to API records.

## Declarative Effects

Handlers return an `Effect<T>` describing intent, not performing side effects. The exact API varies per component (see each skill) but the shape is consistent: `effects().<primary>()...<chaining>().thenReply(...)`. Examples: `effects().reply(v)`, `effects().error("msg")`, entity `effects().persist(event).thenReply(...)` / `effects().updateState(s).thenReply(...)`, workflow `effects().updateState(s).transitionTo(step)`, view `effects().updateRow(row)`. `ReadOnlyEffect<T>` is compile-time-enforced read-only (servable from any region in multi-region).

## ComponentClient

Injected into Setup, Endpoints, Agents, Consumers, Timed Actions, and Workflows. Type-safe, location-transparent calls (over the network, JSON-serialized):

```java
// synchronous (preferred — runtime optimizes)
var cart = componentClient.forEventSourcedEntity(cartId).method(ShoppingCartEntity::getCart).invoke();
componentClient.forEventSourcedEntity(cartId).method(ShoppingCartEntity::addItem).invoke(item);
// async (parallel / long-running)
CompletionStage<Counter> c = componentClient.forKeyValueEntity(id).method(CounterEntity::get).invokeAsync();
// targets:
componentClient.forEventSourcedEntity(id) / .forKeyValueEntity(id) / .forWorkflow(id)
              / .forView() / .forTimedAction() / .forAgent().inSession(sessionId)
```
Use `invoke()` (sync) by default; `invokeAsync()` for parallelism; `.deferred(arg)` to build a deferred call for a timer. Never access another component's storage directly.

## Calling other services & external HTTP

- Other Akka services in the project: inject `HttpClientProvider` → `httpClientFor("service-name")` (routing/auth/TLS handled by the runtime), or `GrpcClientProvider`. External: pass a full `https://…` URL.
- Service-to-service **eventing** (brokerless) is done with Consumers + `@Produce.ServiceStream` / `@Consume.FromServiceStream` (see [[akka-sdk-consumers]]).

## Dependency injection & ServiceSetup

Constructor injection. Always injectable: `Config`, `AgentRegistry`, OpenTelemetry `Meter`. In Setup/Endpoints/Agents/Consumers/Timed-Actions/Workflows: `ComponentClient`, `HttpClientProvider`, `GrpcClientProvider`, `TimerScheduler`, `Materializer`, `Retries`, a virtual-thread `Executor`. Component-specific contexts: `EventSourcedEntityContext`, `KeyValueEntityContext`, `WorkflowContext`, `AgentContext` (session id), `RequestContext` (endpoints).

```java
@Setup
public class MyAppSetup implements ServiceSetup {
  @Override public void onStartup() { /* init, e.g. PromptTemplate */ }
  @Override public DependencyProvider createDependencyProvider() {
    return new MyDependencyProvider();   // resolve custom constructor types; must be thread-safe/immutable
  }
}
```
At most one `@Setup` class per service. `onStartup`/`onShutdown` run per instance (mind rolling upgrades). A `DependencyProvider` (a SAM `Class<T> → T`) resolves any constructor type the runtime doesn't know (can bridge to Spring). Returned instances are shared across parallel component instances → must be thread-safe/immutable.

## Configuration

HOCON in `src/main/resources/application.conf`; access via the injected `Config` (never `ConfigFactory.load()`). Env overrides via `${?VAR}`. SDK settings live under `akka.javasdk.*` (e.g. `akka.javasdk.agent.model-provider`, `akka.javasdk.event-sourced-entity.snapshot-every`, `akka.javasdk.dev-mode.*`).
