---
name: openclaw-agents
description: "The agent system of OpenClaw — a self-hosted messaging-gateway platform that runs an LLM agent across WhatsApp/Telegram/Slack/Discord/Signal/iMessage/WebChat through one local Gateway. Covers the embedded agent runtime and its per-session serialized run loop (RPC entry → agentCommand → runEmbeddedAgent → three event streams tool/assistant/lifecycle → agent.wait), how a turn is invoked (the `openclaw agent` CLI and the gateway `agent`/`agent.wait` WebSocket RPC returning {runId,acceptedAt}), the lane-based concurrency queue (session lanes, main/subagent caps, steer/followup/collect/interrupt modes), block vs preview streaming, auto-compaction and timeouts, the per-run system-prompt assembly (bootstrap files AGENTS.md/SOUL.md/TOOLS.md/IDENTITY.md, skills injection, cache boundary, full/minimal/none modes), multi-agent config (agents.defaults vs agents.list[], model refs, per-agent workspace + SQLite store), thinking/reasoning levels and directives, the tool catalog + tool policy, exec approvals (policy+allowlist+approval), sub-agents/sessions_spawn delegation, gateway operator scopes (operator.read/write/admin), and lifecycle hooks. Use when building, invoking, configuring, operating, or debugging OpenClaw agents, sub-agent delegation, agent prompts/tools/thinking, or the agent RPC. Distilled from docs.openclaw.ai (fetched 2026-07); an evolving self-hosted project — verify version-specific keys and provider/model mappings against the live docs."
license: MIT
---

# OpenClaw — the agent system

**OpenClaw** is a self-hosted messaging platform: a single persistent **Gateway** (default `127.0.0.1:18789`, exclusive per host) fronts every messaging surface — WhatsApp, Telegram, Slack, Discord, Signal, iMessage, WebChat — and runs **one embedded agent runtime** (a built-in agent loop + tool wiring + prompt assembly) that turns inbound messages into replies and actions. This skill is scoped to **the agent system**, not the whole platform.

> **Not the game engine.** "OpenClaw" also names an unrelated *Captain Claw* reimplementation. This skill is strictly the **docs.openclaw.ai** agent platform. Treat everything here as distilled from those docs (fetched 2026-07) — it's an evolving self-hosted project, so verify version-specific config keys and provider/model mappings against the live docs before relying on them.

Load a reference for depth:

- **[references/agent-loop.md](references/agent-loop.md)** — the run lifecycle, lane-based concurrency & the session write lock, streaming (block vs preview), compaction/retries, the timeout table, early-termination points, stuck-session diagnostics, and the internal + plugin **hooks** around the lifecycle.
- **[references/invocation-and-protocol.md](references/invocation-and-protocol.md)** — the **`openclaw agent` CLI** (every flag), the gateway **`agent`/`agent.wait` RPC** + frame formats, idempotency, cancellation (`sessions.abort`/`chat.abort`), the handshake/auth model, and **operator scopes**.
- **[references/agents-config.md](references/agents-config.md)** — multi-agent config (`agents.defaults` vs `agents.list[]`), workspace + bootstrap files, **system-prompt assembly**, skills injection, **thinking levels**, the **tool catalog + policy**, **exec approvals**, and **sub-agents / `sessions_spawn`** delegation.

## The mental model

- **An agent is a serialized, per-session process.** Each configured agent has its own **workspace**, **bootstrap files**, and **SQLite session store**. A turn is: message intake → context assembly → model inference → tool execution → streaming → persistence. Runs are **serialized per session key** (one active run per session) so tool/session state never races.
- **Invocation is async with a `runId`.** Both the `openclaw agent` CLI and the `agent` RPC **immediately return `{ runId, acceptedAt }`**; the run proceeds in the background. `agent.wait` *observes* completion (`ok|error|timeout`) but never stops the run — cancellation is `sessions.abort` / `chat.abort`.
- **Concurrency is lane-based.** A lane-aware FIFO queue drains each lane with a concurrency cap: `main`=4, `subagent`=8, unconfigured=1; global cap = `agents.defaults.maxConcurrent`. Messages arriving mid-run are handled by the **queue mode**: `steer` (default — inject after the current tool calls), `followup`, `collect`, or `interrupt` (abort + run newest).
- **The system prompt is built per run**, layered from OpenClaw's base prompt + skills + bootstrap files (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, …) + per-run overrides, with a **prompt-cache boundary** keeping stable content reusable. Modes: `full` (primary), `minimal` (sub-agents), `none`.
- **Tools are policy-gated before the model call**, and shell execution passes an **exec-approval gate** (policy + allowlist + optional approval; stricter always wins). The prompt's Safety guardrails are **advisory, not enforced** — the real controls are tool policy, exec approvals, sandboxing, and operator scopes.
- **Delegation is push-based.** `sessions_spawn` starts an isolated background sub-agent and returns a run id; `sessions_yield` ends the turn to receive results — **never poll** `subagents`/`sessions_list` to detect completion.

## Run a turn

```bash
# via the Gateway (falls back to embedded on failure); --local forces embedded
openclaw agent --agent ops --message "Summarize today's alerts" --thinking medium --deliver
openclaw agent --session-id 1234 --message-file ./brief.md --json
```

Over the gateway WebSocket, `{type:"req", method:"agent", params:{…}}` needs scope **`operator.write`** and an **idempotency key**; it returns `{runId, acceptedAt}`, then `tool` / `assistant` / `lifecycle` events stream, and `agent.wait` resolves on lifecycle end/error. See [references/invocation-and-protocol.md](references/invocation-and-protocol.md).

## Configure an agent (shape at a glance)

```jsonc
{
  "agents": {
    "defaults": {
      "maxConcurrent": 4,
      "thinkingDefault": "medium",
      "timeoutSeconds": 172800,              // 48h; 0 = unlimited
      "compaction": { "mode": "safeguard" },
      "subagents": { "delegationMode": "suggest", "maxSpawnDepth": 1, "maxConcurrent": 8 }
    },
    "list": [
      { "id": "ops", "model": "anthropic/<model-id>", "thinkingDefault": "high" }
    ]
  },
  "tools":  { "exec": { "mode": "allowlist", "ask": "on-miss" } },
  "messages": { "queue": { "mode": "steer" } }
}
```

Model refs are `provider/model` (split on the first `/`; omit the provider → alias, then unique provider match). Per-agent state lives at `~/.openclaw/agents/<agentId>/agent/openclaw-agent.sqlite`. Full key catalog: [references/agents-config.md](references/agents-config.md).

## Gotchas

- **`agent.wait` ≠ cancel.** Its timeout is wait-only. To actually stop a run use `sessions.abort` (`key`+`runId`, or `runId`) or, for a queued turn, `chat.abort`.
- **Exit paths differ from Claude Code.** OpenClaw's own agent, not the Claude Code harness — don't assume Claude Code slash-commands/flags carry over. Directives here are the message-level `/think`, `/verbose`, `/queue`, `/compact`, `/reasoning`, `/fast` set.
- **Safety-section guardrails are advisory.** Real enforcement = tool policy (pre-model), exec approvals, sandboxing, and operator scopes. Configure those, don't rely on the prompt.
- **Provider/model mappings and thinking levels are version-sensitive.** The docs' strings (e.g. "Claude Opus 4.7+", "GPT-5 overlay", DeepSeek/Gemini/Ollama level sets) are OpenClaw's own mappings and evolve — verify against the live docs and your configured providers.
- **No true token streaming.** Two coarse layers only: block streaming (completed blocks) and preview streaming (edited preview messages). Plan UX around blocks, not tokens.
- **Sub-agents are isolated by default** — no session/message tools unless you opt into an orchestrator pattern; and `delegationMode: "prefer"` only changes the *prompt*, not tool availability.

## Related

- [[agentic-workflows]] — workflow-vs-agent patterns & the agent loop in the abstract; OpenClaw is one concrete embedded-agent runtime of that shape.
- [[agent-interoperability]] — MCP/A2A; how an agent platform like this exposes/consumes tools and talks to peer agents.
- [[secure-coding]] · [[cryptography]] — the trust model here (operator scopes, exec approvals, device-signed handshakes, shared-secret auth) is security-sensitive.
- [[home-assistant]] — the other self-hosted, always-on gateway in the toolkit; similar operational shape (daemon + channels + automations).

Sources: docs.openclaw.ai — `/concepts/architecture`, `/concepts/agent`, `/concepts/agent-loop`, `/concepts/queue`, `/concepts/streaming`, `/concepts/compaction`, `/concepts/system-prompt`, `/cli/agent`, `/tools`, `/tools/thinking`, `/tools/exec-approvals`, `/tools/subagents`, `/gateway/protocol`, `/gateway/operator-scopes`, `/automation/hooks`, `/plugins/hooks` — fetched 2026-07. Version-specific keys and provider/model mappings evolve; re-verify against the live docs.
