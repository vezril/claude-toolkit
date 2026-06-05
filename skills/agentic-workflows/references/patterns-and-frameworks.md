# Agentic patterns & frameworks

Detail on the patterns from Anthropic's "Building Effective Agents," the agent loop from the Claude Agent SDK, and a framework comparison.

## The augmented LLM (the building block)
`LLM + tools + retrieval + memory`. Every pattern below composes this unit. Invest in: a clear tool interface, good tool docs/examples, and letting the model decide when to call what. Get one augmented LLM working well before composing many.

## The five workflow patterns

**1. Prompt chaining** — fixed sequence of LLM calls, each consuming the prior output; optional programmatic **gates** between steps to validate/branch.
- *Use when:* the task splits cleanly into ordered subtasks (e.g. outline → draft → polish; or SRS → HLD → code).
- *Trade:* lower latency tolerance, higher accuracy per step.

**2. Routing** — a classifier LLM categorizes the input, then routes to a specialized prompt/tool/agent.
- *Use when:* inputs fall into distinct classes better served by focused handlers (support triage; "is this a bug fix or a feature?").
- *Benefit:* separation of concerns keeps each prompt sharp.

**3. Parallelization** — two flavors:
- **Sectioning** — split into independent subtasks, run concurrently, combine (faster).
- **Voting** — run the *same* task several times, aggregate by consensus/majority (higher confidence, diverse views).
- *Use when:* subtasks are independent, or you want speed / multiple perspectives (e.g. several reviewers).

**4. Orchestrator-workers** — a central **orchestrator** LLM dynamically decomposes a task, spins up **worker** LLMs for subtasks, and synthesizes their outputs.
- *Use when:* the subtasks **aren't known in advance** and depend on the input. Differs from parallelization in that decomposition is dynamic.
- *This is the SDLC Coordinator* in [[sdlc-orchestration]].

**5. Evaluator-optimizer** — a **generator** LLM produces output; an **evaluator** LLM critiques it against criteria; loop until the evaluator is satisfied (bounded).
- *Use when:* clear evaluation criteria exist and iteration measurably helps (code that must pass review; a doc that must meet a checklist).
- *This is the maker-checker / generator-critic pattern* behind every SDLC phase gate. Make the evaluator a **different/stronger model** and **ground it in execution** where possible.

## The autonomous agent loop (Claude Agent SDK)
When steps can't be pre-defined, use a true agent:
```
start from a human command
loop:
  gather context   (read files, retrieve, recall memory)
  take action      (call tools: edit files, run commands, query APIs)
  verify the work  (run tests/linters/build; read REAL output)
  until: task complete OR stop condition OR max iterations
check in with the human (checkpoints + on completion)
```
Essentials: a clear **stopping condition**, a **max-iteration cap**, **execution-grounded verification**, **context management** (compaction/retrieval), and **human checkpoints** before consequential actions. Subagents can own sub-loops; MCP exposes tools.

## Choosing: call → workflow → agent
- **Single augmented call** — most tasks. Cheapest, most predictable. Try this first.
- **Workflow** — known decomposition; pick the pattern above. Predictable, debuggable.
- **Agent** — unpredictable steps needing adaptation. Most capable, least predictable, most expensive.

Escalate only when the simpler tier demonstrably falls short.

## Framework comparison

| Framework | Model | Best for | Notes |
|---|---|---|---|
| **Claude Agent SDK** | gather→act→verify loop; tools, subagents, MCP, context mgmt | Building agents/coding agents on Claude | The SDK this system runs on; harness + tool ecosystem |
| **LangGraph** | Graph: nodes (agents) + edges (control), shared **state**, conditional routing, **checkpointing**, HITL interrupts | Explicit, durable, stateful workflows you want to see and resume | Most control; more boilerplate |
| **CrewAI** | Role-based "crews" with tasks, delegation, parallelism | Quick role-based multi-agent setups | Higher-level, opinionated |
| **AutoGen** | Multi-agent **conversation** framework | Conversational agent collaboration, research | Microsoft; evolved across versions |

**Anthropic's caveat:** frameworks add abstraction that can **obscure the underlying prompts and control flow**, making debugging harder. Start by calling the API directly; adopt a framework only once it clearly earns its complexity. Whatever you choose, **understand what's happening underneath.**

## Interop note
Agent↔tool standardization is **MCP**; agent↔agent is **A2A**. See **[[agent-interoperability]]** for both (MCP primitives/transports, A2A Agent Cards/Tasks, and when to use which). For coordination within [[sdlc-orchestration]], prefer shared artifacts + MCP tools, moving to A2A once role agents become independently deployed services.
