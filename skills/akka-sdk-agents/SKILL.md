---
name: akka-sdk-agents
description: The Akka SDK Agents component (Java) — a stateful, durable component that calls an LLM to perform one well-defined task, with built-in session memory, function/tool calling, structured output, streaming, guardrails, and LLM-as-judge evaluation. Covers defining an Agent (extend Agent, @Component, the effects() API — system/user messages, model(), memory(), tools(), responseAs/responseConformsTo, onFailure, thenReply), model/provider configuration (OpenAI, Anthropic, Gemini, Bedrock, local), session memory, function tools and MCP tools, multi-agent orchestration via Workflows and the AgentRegistry/dynamicCall, guardrails, evaluation, and deterministic testing with TestModelProvider. Use when building AI/LLM features in an Akka SDK service — agents, chatbots, RAG, tool-using assistants, multi-agent systems — or any time an Akka component needs to call a model. Part of the Akka SDK (Java); see akka-sdk for the meta model and akka-sdk-workflows for orchestration.
---

# Akka SDK — Agents

An **Agent** is a lightweight, **single-purpose, stateful, durable** component that interacts with an LLM to accomplish one discrete goal. It maintains contextual **session memory**, can call **tools** (function calling), and gets the same durability/scaling/observability as every Akka SDK component — conversation history survives node failures with no custom recovery code. Part of the [[akka-sdk]] (Java).

Cross-links: [[akka-sdk]] (meta), [[akka-sdk-workflows]] (orchestrate agents), [[akka-sdk-endpoints]] (expose them), [[akka-sdk-event-sourced-entities]] (memory is an ESE under the hood).

## When to use an Agent (and when not)

Use an Agent when you need to interpret intent / generate content / decide via an LLM, maintain multi-turn context, or call tools dynamically. **Do not** use one for stateful business logic without AI (→ [[akka-sdk-event-sourced-entities]]/[[akka-sdk-key-value-entities]]), for deterministic multi-step orchestration (→ [[akka-sdk-workflows]]), or for plain request/response with no model (→ [[akka-sdk-endpoints]]). **One agent class per role; each agent does one thing** — compose many small agents via Workflows.

## Defining an Agent

```java
@Component(id = "activity-agent")          // unique id; @Component(name=, description=) feed the AgentRegistry for planning
public class ActivityAgent extends Agent {
  public Effect<String> query(String message) {   // exactly ONE public command handler; one or no parameter (wrap many in a record)
    return effects()
      .systemMessage("You are an activity suggestion assistant...")
      .userMessage(message)
      .thenReply();
  }
}
```

The declarative `effects()` API can: set `systemMessage`/`userMessage` (or `systemMessageFromTemplate(...)`, multimodal `UserMessage.from(...)`); pick the `model(...)`; configure `memory(...)`; register `tools(...)`/`mcpTools(...)`; shape output with `responseAs(T.class)` / `responseConformsTo(T.class)`; handle errors with `onFailure(...)`; and terminate with `.thenReply()` / `.reply(...)`. Use `streamEffects()` returning `StreamEffect` for token streaming. Inject `ComponentClient` to enrich requests from entities/views (RAG).

## Calling an agent

Bind every call to a **session id** (the scope of memory, tracing, and evaluation grouping):

```java
String reply = componentClient.forAgent().inSession(sessionId).method(ActivityAgent::query).invoke("Meeting in London");
```

Use a fresh `UUID` when no multi-step/collaboration is needed; reuse the same session id (commonly the workflow id) so collaborating agents share context. **Drive agents from a [[akka-sdk-workflows]] Workflow** for durable execution, retries, and timeouts — AI calls are slow (set a step timeout, e.g. 60s, and a bounded recovery so it doesn't retry forever).

## Model / provider configuration

```hocon
akka.javasdk.agent {
  model-provider = openai
  openai { model-name = "gpt-4o-mini"; api-key = ${?OPENAI_API_KEY} }
}
```
Override per agent with `.model(ModelProvider.openAi().withModelName("gpt-4o").withTemperature(0.6).withMaxTokens(10000))`. Providers: `openAi()`, `anthropic()`, Bedrock, `googleAiGemini()`, Hugging Face; local LocalAI/Ollama; or `ModelProvider.custom(...)` wrapping a LangChain4J model. `ModelProvider.fromConfig("...")` selects a named config block per agent.

## Always-apply defaults

1. **One goal per agent, one handler per agent;** wrap multi-field input in a record. Bind calls to a session id.
2. **Orchestrate with Workflows, never chain agents directly** (an Agent cannot be a tool for another agent). Use `AgentRegistry` + `dynamicCall` only for runtime-selected agents.
3. **Prefer `responseConformsTo(...)` for structured output** on OpenAI/Gemini (auto JSON schema); use `responseAs(...)` + prompt instructions + `onFailure` elsewhere.
4. **Set workflow step timeouts and bounded recovery** around agent calls; `akka.javasdk.agent.max-tool-call-steps` bounds the tool loop.
5. **Enable guardrails and evaluators by config** (not app code) for inputs/outputs; treat token usage as a cost to watch (`withDetailedReply()` exposes it).
6. **Test deterministically with `TestModelProvider`** in `TestKitSupport`; evaluate quality with LLM-as-judge evaluators separately.

## Anti-patterns (flag in review)

- Chaining agents as tools; multiple goals in one agent; calling an agent without a session id.
- Unbounded retries on slow model calls (no step timeout); ignoring token spend.
- Free-form text where a structured response is needed; no `onFailure` fallback for bad JSON / rate limits.
- Building business logic on session memory without compaction (unbounded growth); stateful guardrail/interceptor objects (must be thread-safe/stateless).

## How to use this skill

- **`references/prompts-models-responses.md`** — system/user messages, prompt templates, multimodal input, model/provider config, structured responses, streaming, calling/sessions, and failure handling.
- **`references/tools-memory-orchestration-testing.md`** — function tools (4 ways) & MCP tools, session memory (providers, filtering, interceptors, compaction), multi-agent orchestration (Workflows, `AgentRegistry`, `dynamicCall`), guardrails, LLM evaluation, and deterministic testing.

## Related

- [[akka-sdk]] — the component model, `ComponentClient`, deployment.
- [[akka-sdk-workflows]] — durable orchestration of one or many agents (the recommended way to run agents).
- [[akka-sdk-endpoints]] — expose an agent over HTTP/SSE or MCP.
- Source: Akka SDK docs, https://doc.akka.io/sdk/agents.html (+ sub-pages) and https://doc.akka.io/concepts/ai-agents.html.
