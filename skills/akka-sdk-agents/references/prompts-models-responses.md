# Agents: prompts, models, responses, streaming, failures

Akka SDK (Java). Source: doc.akka.io/sdk/agents/{prompt,calling,structured,streaming,failures}.html, sdk/model-provider-details.html

## Prompts

- `systemMessage(...)` (role/constraints, processed first) + `userMessage(...)` (the input). Either can be computed per request.
- **Dynamic templates:** `effects().systemMessageFromTemplate("activity-agent-prompt", args...)` reads from a built-in `PromptTemplate` Event Sourced Entity (auto-registered when any Agent exists) — change prompts at runtime without redeploy, with history. Manage via `componentClient.forEventSourcedEntity(key).method(PromptTemplate::update/get)`; init it in `ServiceSetup.onStartup`.
- **Multimodal** (model-dependent): `userMessage(UserMessage.from(TextMessageContent.from("..."), ImageMessageContent.fromUri("https://...")))`; object-storage refs via `ImageUrlMessageContent.create(bucket, key)` / `PdfUrlMessageContent.create(...)`. For private/auth'd sources implement a `ContentLoader` and register with `.contentLoader(...)`.

## Model / provider config

Default in `application.conf` under `akka.javasdk.agent.model-provider` + a `<provider>` block (api-key via env). Per-agent override:
```java
.model(ModelProvider.openAi().withApiKey(System.getenv("OPENAI_API_KEY"))
   .withModelName("gpt-4o").withTemperature(0.6).withMaxTokens(10000))
```
Providers: `openAi()`, `anthropic()`, Bedrock, `googleAiGemini()`, Hugging Face (hosted); LocalAI, Ollama (local); `ModelProvider.custom(...)` (wrap a LangChain4J `ChatModel`/`StreamingChatModel`); `ModelProvider.fromConfig("path")` (named config block).

## Calling & sessions

```java
var sessionId = UUID.randomUUID().toString();
String suggestion = componentClient.forAgent().inSession(sessionId).method(ActivityAgent::query).invoke("...");
```
- Session id = memory scope + tracing + eval grouping. Fresh UUID when standalone; shared id (often the workflow id) for collaboration/multi-step.
- `.withDetailedReply()` → `AgentReply<T>` with `value()` and `tokenUsage()`.
- **Dynamic dispatch** when the agent class is only known at runtime: `componentClient.forAgent().inSession(id).<Req,Resp>dynamicCall(agentId).invoke(req)` (no compile-time safety). Discover agents via injected **`AgentRegistry`** (`agentsWithRole("worker")`, lookup by id/role — fed by `@Component(name=,description=)` + `@AgentRole`).
- Prefer driving agents from a [[akka-sdk-workflows]] Workflow (durable, retried, timed); model calls take seconds.

## Structured responses

- `.responseAs(Activity.class)` — map JSON to a record; pair with prompt instructions describing the shape; handle bad JSON via `.onFailure(t -> ... )`.
- `.responseConformsTo(Activity.class)` — on models with native structured output (OpenAI, Gemini), auto-generates and sends a JSON schema from the type (field-level `@Description` included); no need to describe the format in the prompt. Combine both if a model still misbehaves.

## Streaming

```java
public StreamEffect query(String message) {
  return streamEffects().systemMessage(SYSTEM).userMessage(message).thenReply();
}
```
Consume from an endpoint: `componentClient.forAgent().inSession(id).tokenStream(Agent::query).source(question)` → `Source<String, NotUsed>` → `HttpResponses.serverSentEvents(...)`. Group to cut SSE overhead: `.groupedWithin(20, Duration.ofMillis(100)).map(g -> String.join("", g))`. From a Workflow, inject `NotificationPublisher` + `Materializer` and `publishTokenStream(...)`.

## Failure handling

`.onFailure(exception -> ...)` with a `switch` and a **default** branch (unexpected errors may be wrapped `RuntimeException`). Exception taxonomy: model — `ModelException`, `RateLimitException`, `ModelTimeoutException`, `UnsupportedFeatureException`, `InternalServerException`; tools — `ToolCallExecutionException` (has `getToolName()`), `McpToolCallExecutionException`, `ToolCallLimitReachedException`; response — `JsonParsingException`.
