# Akka SDK: project setup, running, deploying, testing

Java. Source: doc.akka.io/sdk/running-locally.html, getting-started/*, operations/services/deploy-service.html

## Project & build

- **Maven** (3.9+), Java 21. The SDK artifact is **`akka-javasdk`** with a parent POM / build plugin in the **`akka-javasdk-maven`** family (supplies the `exec:java` run goal and the Docker image build); test dependency **`akka-javasdk-testkit`**. Artifacts come from Akka's repository, so add your **Akka token to `pom.xml`**.
- **Bootstrap**: clone a sample template rather than an archetype, e.g. `git clone https://github.com/akka-samples/helloworld-agent.git --depth 1`, then add your token. Prereqs: Java 21, Maven 3.9+, Git; for agents a model-provider key (e.g. `OPENAI_API_KEY`).

## Running locally

```bash
mvn compile exec:java        # from project root; service listens on localhost:9000
```
- **Local console** (optional): install the Akka CLI, run `akka local console` in another terminal, open `http://localhost:9889/` for tracing/inspection (survives restarts).
- **Persistence is off by default** (in-memory). Enable durable local persistence with `akka.javasdk.dev-mode.persistence.enabled=true` (state file `db.mv.db`; delete to reset).
- **Brokers off by default**: `akka.javasdk.dev-mode.eventing.support=kafka` (Kafka on localhost:9092) or `google-pubsub-emulator`.
- **Multiple services locally**: give each a distinct `akka.javasdk.dev-mode.http-port` (e.g. 9001); they discover each other by logical name.

## Deploying (Akka Automated Operations)

```bash
mvn clean install -DskipTests                       # builds the container image (needs Docker)
akka service deploy my-service my-image:tag --push  # push to Akka Container Registry (all regions) + deploy
akka service list                                   # Ready / UpdateInProgress / Unavailable / PartiallyReady
```
Updates = build a new image and `akka service deploy ... newtag --push` → **rolling update, no downtime**. Prereqs: Akka account, a created Akka **project**, the Akka CLI. Self-managed deployment runs the same image on your own Kubernetes/infra.

## Testing

- **Integration tests** extend **`TestKitSupport`** (from `akka-javasdk-testkit`), which starts the runtime + components in-process; drive components via the injected `componentClient`. Run with `mvn verify`.
- Configure the testkit by overriding `testKitSettings()`:
  ```java
  @Override protected TestKit.Settings testKitSettings() {
    return TestKit.Settings.DEFAULT
      .withModelProvider(MyAgent.class, testModel)             // mock an agent's LLM (see akka-sdk-agents)
      .withKeyValueEntityIncomingMessages(CustomerEntity.class)// feed a view/consumer source
      .withTopicIncomingMessages("topic").withTopicOutgoingMessages("topic")
      .withAdditionalConfig("akka.javasdk.agent.openai.api-key = n/a");
  }
  ```
- `TestKitSupport` loads `src/test/resources/application-test.conf` if present (commonly `include "application.conf"` then overrides), else `application.conf`.
- **Component unit testkits** (no full runtime): `EventSourcedTestKit`, `KeyValueEntityTestKit` (see the entity skills). **Domain-layer** logic (plain records in `domain/`) is unit-testable without Akka at all.
- Views/consumers are eventually consistent — poll with Awaitility in integration tests.
