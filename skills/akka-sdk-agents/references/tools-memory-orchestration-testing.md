# Agents: tools, memory, orchestration, guardrails, evaluation, testing

Akka SDK (Java). Source: doc.akka.io/sdk/agents/{extending,memory,orchestrating,guardrails,llm_eval,testing}.html

## Function tools (function calling)

The agent advertises tools; the LLM chooses which to call; the agent executes and loops until the LLM stops. Four ways to register:

1. **Agent-defined** — annotate a method (even `private`) with `@FunctionTool(description="...")`; auto-registered.
2. **External object/class** — `effects().tools(weatherService)` or `.tools(MyService.class)` (lazy via `DependencyProvider`); the class needs ≥1 `@FunctionTool` public method.
3. **Akka components as tools** — annotate command handlers on ESE/KVE/Workflow/View with `@FunctionTool`, pass the class to `.tools(...)` (lets the agent read/mutate domain state or trigger a workflow).
4. **Remote MCP servers** — `effects().mcpTools(RemoteMcpTools.fromService("svc"), RemoteMcpTools.fromServer("https://host/mcp").withAllowedToolNames(Set.of(...)))`.

```java
@FunctionTool(description = "Returns the weather forecast for a given city.")
String getWeather(@Description("city name") String location,
                  @Description("date yyyy-MM-dd") Optional<String> date) { ... }
```
`@Description` on params helps the model. **An Agent cannot be a tool for another agent** — orchestrate with Workflows. `akka.javasdk.agent.max-tool-call-steps` (default 100) bounds the loop.

## Session memory

User and AI messages are auto-stored and auto-included on subsequent requests; memory is keyed by **session id**, shared across agents in that session, and **persisted as an Event Sourced Entity** (`SessionMemoryEntity`).

```hocon
akka.javasdk.agent.memory { enabled = true; limited-window { max-size = 156KiB } }
```
Per-call `.memory(MemoryProvider...)`: `none()` (disable), `limitedWindow()` (`readLast(n)`, read-only/write-only, `filtered(...)`), `fromConfig()`, `custom(...)`. **Filtering** for multi-agent: `MemoryFilter.includeFromAgentId/excludeFromAgentId/includeFromAgentRole/excludeFromAgentRole` (same-type filters OR-merge). **`SessionMemoryInterceptor`** (`.withInterceptor(...)`) rewrites messages before persistence (redact secrets) — must be stateless/thread-safe. Memory is a normal ESE: read/modify via `ComponentClient`, or subscribe to its events with a [[akka-sdk-consumers]] Consumer. **Compaction**: a `CompactionAgent` (with `MemoryProvider.none()`) summarizes history when `historySizeInBytes()` exceeds a threshold, written back via `SessionMemoryEntity::compactHistory`.

## Multi-agent orchestration

Orchestrate with [[akka-sdk-workflows]] Workflows (durable, retried, resumable); agents collaborate by **sharing a session id**. Patterns:

- **Sequential** — a `Workflow` whose steps each call an agent via `componentClient.forAgent().inSession(sessionId()).method(WeatherAgent::query).invoke(...)`, storing results in durable state, with `WorkflowSettings` step timeouts/recovery.
- **Planner/router (dynamic)** — a `SelectorAgent` (injects `AgentRegistry`, `agentsWithRole("worker")`) picks relevant agent ids (`responseConformsTo(AgentSelection.class)`); a `PlannerAgent` orders them and emits a per-agent query; the workflow executes each via `dynamicCall(agentId)`. Agent descriptions (`@Component(name=,description=)` + `@AgentRole`) drive planning quality.

## Guardrails

Implement `TextGuardrail` (`Result evaluate(String)`); **enable by config** (not code) so deployment enforces them:
```hocon
akka.javasdk.agent.guardrails."pii guard" {
  class = "com.example.PiiGuard"
  agents = ["planner-agent"]            # or agent-roles = ["worker"], "*"
  use-for = ["model-request", "mcp-tool-request"]   # also model-response / mcp-tool-response / "*"
  category = PII
  report-only = false                   # false = abort on fail; true = log/track only
}
```
Built-in `SimilarityGuard` flags text similar to a corpus of bad examples (ships with jailbreak prompts).

## LLM evaluation

LLM output is non-deterministic → use **LLM-as-judge** evaluators implemented as `Agent`s whose result implements `EvaluationResult` (`boolean passed()` + `String explanation()`), results captured in metrics/traces; use `MemoryProvider.none()`. Built-ins: `ToxicityEvaluator`, `SummarizationEvaluator`, `HallucinationEvaluator`. Common pattern: a [[akka-sdk-consumers]] Consumer on the runtime's `TaskEntity` reacts to completion and invokes the evaluator. Evaluators cost tokens — enable mainly in test/CI.

## Testing (deterministic)

Extend `TestKitSupport`; register a **`TestModelProvider`** per agent:
```java
return TestKit.Settings.DEFAULT
  .withAdditionalConfig("akka.javasdk.agent.openai.api-key = n/a")
  .withModelProvider(WeatherAgent.class, weatherModel);
```
- `weatherModel.fixedResponse("...")` — always the same.
- `weatherModel.whenMessage(pred).reply(resp)` — conditional on the user message.
- **Tool-driving**: `whenMessage(...).reply(new ToolInvocationRequest(toolName, jsonArgs))` makes the runtime invoke the real tool and feed the result back; then `whenToolResult(tr -> ...).thenReply(tr -> new AiResponse("..." + tr.content()))`. Tool name = `<ToolClassSimpleName>_<methodName>` (agent-local `@FunctionTool` → agent simple class name prefix).

Invoke via `componentClient.forAgent().inSession(UUID...).method(...).invoke(...)` and assert. For a deployed mock model (load tests) point `openai.base-url` at a stub service implementing the `/chat/completions` shape.
