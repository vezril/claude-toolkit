---
name: agent-interoperability
description: Standards for connecting AI agents to their tools and to each other — the Model Context Protocol (MCP) for agent↔tool/context, and the Agent2Agent (A2A) protocol for agent↔agent collaboration. Covers the clean split "MCP = vertical (model↔tools/data), A2A = horizontal (agent↔agent)"; MCP's JSON-RPC client–host–server architecture and primitives (Resources, Tools, Prompts exposed by servers; Sampling, Roots, Elicitation exposed by clients), transports (stdio, Streamable HTTP), and the 2025-11-25 revision; and A2A's Agent Card discovery (/.well-known/agent-card), Client/Server roles, the Task lifecycle, Message/Part/Artifact, contextId grouping, JSON-RPC/gRPC transports with SSE streaming and push notifications, and auth. Use when designing how agents expose or consume tools, integrating an MCP server/client, enabling cross-framework/multi-vendor agent collaboration, choosing MCP vs A2A, or reasoning about agent discovery, transports, and security. Specs evolve — figures are dated; re-verify. Pairs with agentic-workflows and sdlc-orchestration; security via secure-coding.
---

# Agent Interoperability (MCP & A2A)

The two open standards that let agentic systems stop being islands: **MCP** connects an agent to **tools and context**, and **A2A** connects an agent to **other agents**. The one-line mental model:

> **MCP = vertical** (model ↔ tools/data) · **A2A = horizontal** (agent ↔ agent).

They're complementary — an agent typically *uses MCP* to reach its tools and *speaks A2A* to collaborate with peer agents. Distilled from the **MCP spec (revision 2025-11-25)** and the **A2A protocol (v1.0, Linux Foundation)**.

> **These specs move fast.** Versions, method names, and well-known paths have already changed once (A2A's early-2025 draft → v1.0). Treat every concrete detail here as **dated (2026-06)** and re-verify against modelcontextprotocol.io and a2a-protocol.org before building.

Cross-links: [[agentic-workflows]] (how to design the agents that use these), [[sdlc-orchestration]] (a multi-agent system that coordinates via shared artifacts + tools), [[secure-coding]] (the security model for both is critical).

## MCP — Model Context Protocol (agent ↔ tool/context)

*"An open protocol that enables seamless integration between LLM applications and external data sources and tools."* Inspired by the Language Server Protocol — one standard so any client can talk to any tool server. **JSON-RPC 2.0**, stateful sessions, capability negotiation at init.

**Architecture: host / client / server.**
- **Host** — the LLM app; manages clients, enforces consent/security/authorization, coordinates the model.
- **Client** — created by the host, **1:1 with a server**, one stateful session, keeps servers isolated.
- **Server** — exposes capabilities; local process or remote service; focused and composable. Key isolation rule: *a server can't read the whole conversation or see into other servers.*

**Server-exposed primitives:** **Resources** (context/data for user or model), **Tools** (functions the model can execute — arbitrary code, so explicit user consent required), **Prompts** (templated messages/workflows).

**Client-exposed primitives:** **Sampling** (server asks the client's LLM to generate — 2025-11-25 adds tool-calling here), **Roots** (filesystem/URI boundaries the server may operate in), **Elicitation** (server requests structured input from the user — 2025-11-25 adds URL-mode).

**Transports:** **stdio** (client launches the server as a subprocess; newline-delimited JSON-RPC over stdin/stdout — prefer when possible) and **Streamable HTTP** (one endpoint, POST+GET, optional SSE; session via `MCP-Session-Id`, `MCP-Protocol-Version` header) — which **replaces the deprecated HTTP+SSE transport**. Security: servers MUST validate `Origin` (anti DNS-rebinding) and bind to localhost when local.

**Notable in 2025-11-25:** experimental **Tasks** (durable requests + deferred retrieval — note: MCP's "Task" ≠ A2A's), tool-calling in sampling, icons metadata, elicitation overhaul + URL mode, OAuth/OIDC discovery & incremental consent, JSON Schema 2020-12 default. → `references/mcp.md`

## A2A — Agent2Agent (agent ↔ agent)

*"An open standard that enables seamless communication and collaboration between AI agents... a common language for agents built using diverse frameworks and by different vendors."* It lets an agent be exposed **as an agent** (autonomous, **opaque** — no exposure of internal logic/memory/tools), not crippled into a mere tool. Donated to the **Linux Foundation**; **v1.0** shipped.

**Actors:** **User** (defines the goal); **A2A Client / Client Agent** (initiates on the user's behalf); **A2A Server / Remote Agent** (an HTTP endpoint implementing A2A; an opaque black box).

**Agent Card** — *"a JSON metadata document describing an agent's identity, capabilities, endpoint, skills, and authentication requirements"* — the agent's digital business card. Published at the well-known path **`/.well-known/agent-card`** (⚠️ early drafts used `/.well-known/agent.json`). Declares identity, service `url`, capabilities, `securitySchemes`, and skills.

**Communication elements:**
- **Task** — a stateful unit of work with a `taskId` and lifecycle (`input-required`/`auth-required` → terminal `completed`/`canceled`/`rejected`/`failed`). Terminal tasks are immutable; refinements start a **new task within the same `contextId`**.
- **Message** — one turn (role `user`/`agent`), for immediate exchanges or capability negotiation.
- **Part** — the content container: exactly one of `text` / `raw` bytes / `url` / structured `data` (modality-independent).
- **Artifact** — a tangible task output (id, name, Parts; can stream incrementally).
- **`contextId`** groups related tasks + messages into a session; `referenceTaskIds` links a refinement to a prior task; parallel tasks per context are allowed.

**Transport:** HTTP(S) with **JSON-RPC 2.0** as the core payload (v1.0 also has gRPC and REST/JSON bindings). Methods (v1.0): **`SendMessage`** (sync) and **`SendMessageStream`** (SSE) — ⚠️ early drafts used `tasks/send`/`tasks/sendSubscribe`. Three interaction modes: request/response polling, **SSE streaming** (incremental status/artifact events), and **push notifications** (server POSTs to a client webhook for long-running/disconnected work).

**Auth:** standard web security; requirements declared in the Agent Card `securitySchemes` (OIDC/OAuth/API keys); credentials in **HTTP headers, separate from A2A messages**; HTTPS throughout. → `references/a2a.md`

## Choosing / combining

- **Reaching a tool, data source, or capability** (a database, a code runner, a SaaS API, your file system) → **MCP**. The agent is the client; the tool is an MCP server.
- **Delegating to or collaborating with another autonomous agent** (different team, framework, or vendor; long-running, multi-turn, negotiated work) → **A2A**. Discover via Agent Card, exchange Tasks/Messages.
- **Both at once** is normal: an A2A remote agent internally uses MCP servers for its tools. Don't wrap a full agent as an MCP tool when it should be an A2A peer (you'd lose its autonomy and statefulness).
- Within this toolkit's [[sdlc-orchestration]], coordination is currently via **shared artifacts + MCP tools**; A2A is the path when role agents become independently deployed services.

## Security (both)

- **Tools execute code / agents take actions** — require explicit **user consent** for consequential operations; keep a human in the loop ([[agentic-workflows]]).
- **Isolation** — MCP servers can't see the whole conversation or each other; A2A agents stay opaque. Preserve these boundaries.
- **Transport hardening** — validate `Origin` (MCP), HTTPS + header-based auth (A2A), OAuth/OIDC for delegated access; never put credentials in message bodies.
- **Treat tool descriptions / agent cards as untrusted input** — validate; don't let a malicious server/card drive dangerous actions ([[secure-coding]]).

## Anti-patterns

- Wrapping an autonomous agent as a plain MCP **tool** when it should be an A2A **peer** (loses autonomy, statefulness, negotiation).
- Hard-coding the **old** well-known path (`agent.json`) or method names (`tasks/send`) — use current (`/.well-known/agent-card`, `SendMessage`) and re-verify.
- Using the deprecated MCP HTTP+SSE transport instead of **Streamable HTTP**.
- Ignoring the consent/isolation model — auto-executing tools or letting a server see everything.
- Putting credentials in A2A message bodies instead of headers; skipping `Origin` validation in MCP.
- Building bespoke point-to-point agent integrations where A2A's discovery + standard messaging would do.

## Always-apply

1. **MCP for tools/context, A2A for agent-to-agent** — and combine them (A2A agents use MCP internally).
2. Both are **JSON-RPC 2.0**; MCP = host/client/server with Resources/Tools/Prompts (+ client Sampling/Roots/Elicitation); A2A = Agent Card discovery + Task/Message/Part/Artifact.
3. **Consent + isolation + transport hardening** are not optional ([[secure-coding]]).
4. Prefer **stdio** for local MCP, **Streamable HTTP** for remote; A2A over HTTPS with header auth.
5. **Re-verify versions/methods/paths** — these specs change; everything here is dated 2026-06.

## How to use the references

- **`references/mcp.md`** — MCP architecture, the six primitives, transports, lifecycle, and the 2025-11-25 changes, in detail.
- **`references/a2a.md`** — A2A actors, the Agent Card, the Task lifecycle and contextId model, transports/streaming/push, and auth, in detail.

## Related

- [[agentic-workflows]] — designing the agents and tools that speak these protocols; the patterns layer.
- [[sdlc-orchestration]] — a coordinated multi-agent system; artifacts + MCP now, A2A when agents become services.
- [[secure-coding]] — consent, isolation, untrusted-input, and transport security.
- Sources: Model Context Protocol spec, revision 2025-11-25 (modelcontextprotocol.io); A2A protocol v1.0 (a2a-protocol.org, Linux Foundation). Dated 2026-06 — re-verify.
