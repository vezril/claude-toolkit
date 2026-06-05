# MCP — Model Context Protocol (detail)

Revision **2025-11-25** (current "latest"; prior was 2025-06-18). Normative against the TypeScript `schema.ts`; RFC-2119 keywords. Dated 2026-06 — re-verify at modelcontextprotocol.io.

## What & why
*"An open protocol that enables seamless integration between LLM applications and external data sources and tools... a standardized way to connect LLMs with the context they need."* Explicitly inspired by the **Language Server Protocol**: instead of N×M bespoke integrations, any MCP client can talk to any MCP server. Standardizes: sharing context with models, exposing tools, building composable integrations.

## Foundation
- **JSON-RPC 2.0** messages, UTF-8.
- **Stateful** sessions.
- **Capability negotiation** at initialization — client and server each declare which features they support, and both must respect what was declared.

## Architecture: host / client / server
*"A client-host-server architecture where each host can run multiple client instances."*

- **Host** — the LLM application/container. Manages clients, enforces **security/consent and authorization**, coordinates the LLM (and sampling), aggregates context.
- **Client** — instantiated by the host, **1:1 with one server**, one stateful session, routes messages bidirectionally, **maintains isolation** between servers.
- **Server** — exposes resources/tools/prompts; focused and composable; local subprocess or remote service.

Isolation principle (security-critical): *"Servers should not be able to read the whole conversation, nor 'see into' other servers."* The host is the trust boundary.

## Server-exposed primitives
- **Resources** — *"context and data, for the user or the AI model to use."* Can support subscriptions/update notifications when the server declares it.
- **Tools** — *"functions for the AI model to execute."* Arbitrary code execution → **explicit user consent required**; tool annotations are untrusted unless the server is trusted.
- **Prompts** — *"templated messages and workflows for users."*

## Client-exposed primitives
- **Sampling** — *"server-initiated agentic behaviors and recursive LLM interactions"*: the server asks the client's LLM to generate; the user approves the prompt and the result. **2025-11-25 adds tool-calling to sampling** (`tools`/`toolChoice`).
- **Roots** — *"server-initiated inquiries into URI or filesystem boundaries to operate in."*
- **Elicitation** — *"server-initiated requests for additional information from users"* (structured input). 2025-11-25 reworks enum schemas and adds **URL-mode elicitation**.
- Utilities: configuration, progress, cancellation, error reporting, logging.

## Transports
- **stdio** — client launches the server as a subprocess; newline-delimited JSON-RPC over stdin/stdout; stderr is free for logging. Clients SHOULD support stdio whenever possible. Ideal for local tools.
- **Streamable HTTP** — a single MCP endpoint supporting **POST + GET**, with **optional SSE** for streaming/server→client messages. Session via `MCP-Session-Id` header; `MCP-Protocol-Version` header required. **Replaces the deprecated HTTP+SSE transport (2024-11-05).** Resume via GET + `Last-Event-ID`.
- Custom transports allowed.
- **Security:** servers MUST validate the `Origin` header (403 on invalid) to prevent DNS-rebinding; bind to localhost for local servers.

## Notable in 2025-11-25
- **Experimental Tasks** — track durable requests with polling + deferred result retrieval (SEP-1686). (MCP "Task" is distinct from A2A "Task.")
- **Tool calling in Sampling.**
- **Icons** metadata for tools/resources/templates/prompts.
- **Elicitation** overhaul: standards-based `ElicitResult`/`EnumSchema`, single/multi-select enums, defaults; **URL-mode elicitation**.
- **Auth:** OpenID Connect Discovery; incremental scope consent via `WWW-Authenticate`; OAuth Client ID Metadata Documents; RFC-9728 alignment.
- **JSON Schema 2020-12** now the default dialect.
- Tool input-validation errors returned as **Tool Execution Errors** (not protocol errors) so the model can self-correct.
- Governance formalized (working/interest groups; SDK tiering).

## Practical
Build servers/clients with the official SDKs; expose the *minimum* tools needed; document tools well (the model reads the schema/description — see tool design in [[agentic-workflows]]); require consent for anything consequential; sandbox tool execution ([[secure-coding]]).
