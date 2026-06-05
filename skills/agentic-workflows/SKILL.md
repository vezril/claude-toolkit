---
name: agentic-workflows
description: Designing and building agentic AI systems — when to use a single LLM call, a structured workflow, or an autonomous agent, and the proven composition patterns for each. Distilled from Anthropic's "Building Effective Agents," the Claude Agent SDK, and LangGraph. Covers the workflow-vs-agent distinction (predefined paths vs model-directed control), the building block (augmented LLM = model + tools + retrieval + memory), the five workflow patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer), the autonomous agent loop (gather context → act via tools → verify work → repeat), the maker-checker / generator-critic pattern, and the engineering disciplines that matter (start simple, add complexity only when it pays, ground verification in real tool execution, manage context, design tools and guardrails carefully, human-in-the-loop). Use when architecting a multi-agent or agentic system, choosing an orchestration pattern, deciding workflow vs agent, wiring role agents together, or evaluating a framework (Claude Agent SDK, LangGraph, CrewAI, AutoGen). Provides the runtime mechanics for sdlc-orchestration's role agents.
---

# Agentic Workflows

How to build systems with LLMs that *act* — choosing between a simple call, a fixed **workflow**, and an autonomous **agent**, and composing them with patterns that are proven to work. Distilled from **Anthropic's "Building Effective Agents,"** the **Claude Agent SDK**, and **LangGraph**. This is the runtime-mechanics complement to [[sdlc-orchestration]] (which says *what* the SDLC pipeline is; this says *how* to wire the agents that run it).

Cross-links: [[sdlc-orchestration]] (the SDLC application), [[akka]] (a durable actor runtime for long-running/distributed agents), [[software-architecture]] (these are distributed-system designs — the fallacies apply), [[secure-coding]] (tool/guardrail safety).

## The core distinction: workflows vs agents

Anthropic's framing — both are "agentic systems," but:

- **Workflow** — LLMs and tools orchestrated through **predefined code paths**. Predictable, debuggable, cheaper. Use when the task decomposes into known steps.
- **Agent** — the **LLM dynamically directs its own process and tool use**, maintaining control over how it accomplishes the task. Flexible, but less predictable and more expensive. Use when the steps can't be predicted in advance and the model needs to adapt.

**The cardinal rule: start with the simplest thing that works.** A single well-prompted LLM call (with retrieval/examples) beats a multi-agent system for most tasks. Add workflow structure only when it measurably improves outcomes; reach for a full agent only when flexibility genuinely requires it. *"Find the simplest solution possible, and only increase complexity when needed."* Agentic systems trade latency and cost for better task performance — make that trade deliberately.

## The building block: the augmented LLM

Every agentic system is built from an **augmented LLM** — a model enhanced with **tools**, **retrieval**, and **memory**. Get this unit right first: a clear interface, well-documented tools, and the model able to decide when/how to use them.

## The five workflow patterns

When a fixed structure fits, compose from these (all in `references/patterns-and-frameworks.md` with when-to-use):

1. **Prompt chaining** — decompose into a fixed sequence; each step's output feeds the next, with optional programmatic "gates" between. For tasks that cleanly split into ordered subtasks.
2. **Routing** — classify the input, then dispatch to a specialized follow-up. For distinct categories better handled separately (and to keep each prompt focused).
3. **Parallelization** — run subtasks concurrently (**sectioning**) or run the same task multiple times for vote/consensus (**voting**). For speed or diverse perspectives.
4. **Orchestrator-workers** — a central LLM dynamically breaks a task into subtasks, delegates to worker LLMs, and synthesizes. For complex tasks where subtasks aren't known up front (the SDLC Coordinator is this).
5. **Evaluator-optimizer** — one LLM generates, another **evaluates and gives feedback**, in a loop. For tasks with clear evaluation criteria where iteration helps — this is the **maker-checker / generator-critic** pattern that underpins [[sdlc-orchestration]]'s every phase.

## The autonomous agent loop

When you do use a full agent, it runs a loop (the Claude Agent SDK framing): **gather context → take action (via tools) → verify the work → repeat** until done or stopped. Agents start from a human command, then operate independently, ideally **checking in with the human** at checkpoints and on completion. Keys: a clear stopping condition, a max-iteration cap, and — critically — **verification grounded in reality**.

## Engineering disciplines that decide success

- **Ground verification in execution.** The single biggest quality lever (and the source SDLC frameworks' biggest gap): let the agent **run code, tests, linters, `terraform plan`** and read the real output, not judge its own work by reading it. Feedback from the environment beats model self-assessment.
- **Manage context.** Give each step only what it needs (shard docs — [[spec-driven-development]]); compact long histories; use retrieval/memory deliberately. Context is a budget.
- **Design tools like an API.** Clear names, documented params, examples, error messages the model can act on; few sharp tools over many dull ones. Test tools in isolation.
- **Guardrails & safety.** Constrain what tools can do, validate inputs, never give untrusted input a path to dangerous actions ([[secure-coding]]); sandbox execution.
- **Human-in-the-loop.** Checkpoints for consequential actions; the human approves, the agent proposes.
- **Observability.** Log the agent's steps/decisions so failures are debuggable (ties to [[site-reliability-engineering]]).
- **Multi-agent only when it pays.** Multiple agents add coordination cost; use them for genuine parallelism or separation of concerns (e.g. the SDLC role agents), not by default.

## Frameworks (use the simplest that fits)

- **Claude Agent SDK** — build agents on the gather→act→verify loop with tools, subagents, MCP, and context management. (The SDK this very system runs on.)
- **LangGraph** — graph of nodes (agents) + edges (control flow) over a shared state, with conditional routing, checkpointing/persistence, and human-in-the-loop interrupts. Good for explicit, durable, stateful workflows.
- **CrewAI / AutoGen** — role-based crews / multi-agent conversation frameworks.

Anthropic's caveat: **frameworks add abstraction layers that can hide what's really happening** — start by calling the API directly, adopt a framework only when it earns its complexity. `references/patterns-and-frameworks.md` compares them.

## Anti-patterns

- Reaching for a multi-agent system when a single augmented call would do (cost/latency/complexity for nothing).
- **Self-verifying agents** that grade their own output instead of running it (the cardinal sin — see [[test-strategy]], [[sdlc-orchestration]]).
- Framework-first cargo-culting that obscures the actual prompts/control flow.
- Unbounded agent loops (no stop condition / max iterations).
- Dumping everything into one context window; never compacting or sharding.
- Vague, undocumented tools; tools with unrecoverable error messages.
- No human checkpoint before consequential/irreversible actions; no observability.

## Always-apply

1. **Start simple**; escalate single-call → workflow → agent only when it pays.
2. Build on the **augmented LLM**; pick the matching **workflow pattern** before writing a full agent.
3. Use **evaluator-optimizer (maker-checker)** for iterative quality; **orchestrator-workers** for dynamic decomposition.
4. **Ground verification in real tool execution**; manage context; design tools and guardrails carefully.
5. Keep a **human in the loop** for consequential steps; bound every loop; log decisions.

## How to use the reference

- **`references/patterns-and-frameworks.md`** — each workflow pattern with when-to-use and structure, the agent loop in detail, and a Claude Agent SDK / LangGraph / CrewAI / AutoGen comparison.

## Related

- [[sdlc-orchestration]] — the SDLC pipeline these patterns implement (Coordinator = orchestrator-workers; phase gates = evaluator-optimizer).
- [[akka]] — actor model & durable runtime for long-running, distributed, or stateful agents.
- [[software-architecture]] — agentic systems are distributed systems; the fallacies and trade-offs apply.
- [[test-strategy]] — execution-grounded verification, shared discipline.
- [[secure-coding]] — tool sandboxing, input validation, guardrails.
- Sources: Anthropic, "Building Effective Agents" (anthropic.com/research) & the Claude Agent SDK; LangGraph (langchain-ai/langgraph).
