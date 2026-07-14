# OpenClaw — configuring agents: runtime, prompt, tools, thinking, delegation

Source: docs.openclaw.ai `/concepts/agent`, `/concepts/system-prompt`, `/tools`, `/tools/thinking`, `/tools/exec-approvals`, `/tools/subagents` — fetched 2026-07. This is how you *shape* an agent: its identity, workspace, prompt, model, reasoning, tool access, and how it delegates.

## The agent runtime & multi-agent config

OpenClaw ships **one embedded agent runtime** — a built-in agent loop, tool wiring, and prompt assembly (distinct from external processes). Each configured agent has its **own workspace, bootstrap files, and session store** (a SQLite DB at `~/.openclaw/agents/<agentId>/agent/openclaw-agent.sqlite`).

Configure agents two ways:
- **`agents.defaults`** — shared settings for every agent.
- **`agents.list[]`** — per-agent overrides: identity, model, binding, routing.

**Model refs** use `provider/model`, split on the **first** `/`. Omit the provider and OpenClaw tries an **alias** first, then a unique configured-provider match.

### Workspace & bootstrap files

Every agent has a single **workspace directory** as its exclusive working dir. User-editable bootstrap files are resolved from the active workspace and injected into the prompt (blank files skipped; large files trimmed + truncation marker so prompts stay lean):

| File | Role |
|---|---|
| `AGENTS.md` | Operating instructions + memory |
| `SOUL.md` | Persona, boundaries, tone |
| `TOOLS.md` | User-maintained tool notes |
| `IDENTITY.md` | Agent name / vibe / emoji |
| `USER.md` | User profile |
| `HEARTBEAT.md` | Heartbeat-specific instructions |
| `BOOTSTRAP.md` | One-time first-run ritual (brand-new workspaces only) |
| `MEMORY.md` | Long-term memory (when present) |

Size limits: `agents.defaults.bootstrapMaxChars` (per file, **20 000**), `agents.defaults.bootstrapTotalMaxChars` (total, **60 000**), `agents.defaults.bootstrapPromptTruncationWarning` (`always`). **Sub-agent sessions inject only `AGENTS.md` + `TOOLS.md`.** The `agent:bootstrap` internal hook can mutate injected files. (On Codex harnesses, stable files aren't repeated every turn — `AGENTS.md` loads via project-doc discovery, `TOOLS.md` as inherited developer instructions, etc.)

## System-prompt assembly

A **unique system prompt is built per run** (not a runtime default), across three layers: **pure rendering** (`buildAgentSystemPrompt`, from explicit inputs), **config resolution** (`resolveAgentSystemPromptConfig` — owner display, TTS hints, model aliases, memory-citation mode, sub-agent delegation mode), and **runtime adaptation** (live tools, sandbox state, channel caps, context files, provider contributions).

**Fixed sections** (compact prompt): Tooling · Execution Bias · **Safety** (power-seeking/oversight guardrails — *advisory, not enforced*) · Skills · OpenClaw Control · Self-Update · Workspace · Documentation · Workspace Files · Sandbox · Date & Time · Output Directives · Heartbeats · Runtime (host/OS/node/model/thinking level) · Reasoning.

**Cache-boundary strategy:** large stable content (incl. **Project Context**) stays *above* the internal prompt-cache boundary; volatile sections (Control-UI embed, Messaging, Voice, Group-Chat Context, Reactions, Heartbeats, Runtime) go *below* it — so prefix-cache backends reuse the stable workspace prefix across turns.

**Provider contributions:** provider plugins can replace one of three named core sections (`interaction_style`, `tool_call_style`, `execution_bias`), inject a stable prefix above the cache boundary, or a dynamic suffix below it (e.g. the bundled GPT-5 overlay via `agents.defaults.promptOverlays.gpt5.personality`).

**Prompt modes:** `full` (default; all sections) · `minimal` (sub-agents — omits memory recall, self-update, model aliases, user identity, output directives, messaging, silent replies, heartbeats; injected prompts labeled **Subagent Context**) · `none` (base identity line only).

**Long-running-work guidance baked into the tooling section:** use `cron` for future follow-ups (not sleep loops/polling); use `exec`/`process` only for commands that start immediately in the background; prefer `sessions_spawn` for larger tasks with push completion; **don't loop `subagents list`/`sessions_list` to detect completion**.

### Skills injection

When eligible skills exist, OpenClaw injects a compact `<available_skills>` list with file paths and content-derived `<version>sha256:…</version>` markers, instructing the model to `read` the SKILL.md and re-read when versions differ. Budget: `skills.limits.maxSkillsPromptChars` (global) / `agents.list[].skillsLimits.maxSkillsPromptChars` (per-agent). Eligibility = skill metadata gates + runtime-environment checks + per-agent skill allowlists.

## Thinking / reasoning

Inline directives — `/t <level>`, `/think:<level>`, `/thinking <level>` — set per-message thinking with no session change. Levels: `minimal, low, medium, high, xhigh, adaptive, max` plus `ultra` (roughly "think" → "ultrathink"). A **directive-only message** (e.g. `/think:medium`) sets a session override; clear with `/think default` (aliases `inherit`/`clear`/`reset`/`unpin`); bare `/think` shows the current level.

**Resolution order:** inline directive → session override → per-agent `agents.list[].thinkingDefault` → global `agents.defaults.thinkingDefault` → provider default (reasoning-capable fallback `medium`).

**Provider mapping** (per OpenClaw's docs — provider plugins declare exact level sets and reject unsupported ones): Anthropic Claude 4.6 defaults to `adaptive`; Claude Opus 4.7+ keeps thinking off by default and maps `xhigh` → adaptive + `output_config.effort:"xhigh"`; DeepSeek V4 maps `xhigh|max` → `reasoning_effort:"max"`; OpenAI maps through Responses-API effort; Gemini `adaptive` uses provider dynamic thinking; Ollama exposes `low|medium|high|max`.

**Adjacent directives:** `/fast auto|on|off|default` (OpenAI priority processing; Anthropic `service_tier`), `/verbose on|full|off` (structured tool results echoed as metadata-only messages; `toolProgressDetail` shapes the summary), `/trace` (plugin-owned debug lines only), `/reasoning on|off|stream` (reasoning as a separate `Thinking`-prefixed message; `stream` previews it live).

## Tools — what an agent can do

Three capability surfaces: **Tools** (callable functions the agent invokes), **Skills** (instruction packs loaded into the prompt), **Plugins** (runtime tools/providers/channels/skills).

| Category | Examples |
|---|---|
| Runtime | `exec`, `process`, `code_execution` |
| Files | `read`, `write`, `edit`, `apply_patch` |
| Web | `web_search`, `x_search`, `web_fetch` |
| Browser | `browser` |
| Messaging | `message` |
| Sessions/Agents | `sessions_*`, `subagents`, `session_status` |
| Automation | `cron`, `heartbeat_respond` |
| Gateway/Nodes | `gateway`, `nodes` |
| Media | `image_generate`, `tts`, `video_generate` |
| Large catalogs | `tool_search`, `tool_search_code` |

**Tool policy is enforced *before* the model call.** A tool becomes unavailable via global config, per-agent restriction, channel policy, provider limitation, sandbox rule, or plugin status. Plugin-provided tools include `diffs`, `show_widget`, `llm_task`, `canvas`, `tool_search`, etc.

### Exec approvals (the execution gate)

Exec approvals are a **security companion to sandboxing** — they control when commands run on real hosts. Three layers must agree: **policy + allowlist + (optional) user approval**, and the **stricter setting always wins** (approvals can only tighten, never loosen). Enforced locally on the execution host (gateway `openclaw` process, or the node's macOS/headless runner). *Not* a per-user auth boundary or a read-only filesystem policy — once approved, a command can modify files per host/sandbox permissions.

| Setting | Options | Purpose |
|---|---|---|
| `tools.exec.mode` | `deny, allowlist, ask, auto, full` | Primary normalized policy |
| `exec.security` | `deny, allowlist, full` | Block / restrict / permit |
| `exec.ask` | `off, on-miss, always` | When to prompt |
| `askFallback` | `deny, allowlist, full` | Behavior when UI unavailable |
| `strictInlineEval` | bool | Require approval for `python -c`, `node -e`, … |

**Allowlists are per-agent**, glob-based (bare names match PATH lookups; path globs match locations; optional `argPattern` is an ECMAScript regex on args). **Approval flow:** gateway broadcasts `exec.approval.requested` → Control UI / macOS app resolves via `exec.approval.resolve` → gateway forwards approved request to the node → a canonical `systemRunPlan` prevents post-approval tampering; denials are terminal. State in `$OPENCLAW_STATE_DIR/exec-approvals.json` (or `~/.openclaw/exec-approvals.json`). **YOLO mode** (`openclaw exec-policy preset yolo`) = `security: full` + `ask: off` + host `askFallback: full`. Inspect with `openclaw approvals get` / `openclaw exec-policy show|set`. `autoAllowSkills` implicitly allowlists skill-referenced executables on nodes (disable for strict manual allowlists).

## Sub-agents — delegating work

Sub-agents spawn **isolated background agent runs** that report back to the requesting chat, appearing as tracked background tasks. Purpose: "parallelize research, long tasks, and slow tool work without blocking the main run." Sub-agents are isolated by default — **no session/message tools** unless configured for orchestrator patterns.

- **`sessions_spawn`** — start a delegated task; **non-blocking**, returns a run id immediately. Params include `task`, `taskName`, `model`, `thinking`, `context` mode. Needs tool-policy inclusion (built into the `coding` profile).
- **`sessions_yield`** — end the current turn to receive completion events; child results arrive as the next message. **Do not** replace with polling loops over `subagents`/`sessions_list`.
- **`subagents`** — inspect: `/subagents list`, `/subagents log <id>`, `/subagents info <id>`.

**Context modes:** `isolated` (clean child transcript, lower tokens — default) vs `fork` (branches the parent transcript into the child).

**Config** under `agents.defaults.subagents`: `model`, `thinking`, `maxSpawnDepth` (1–5, default **1**), `maxConcurrent` (lane cap, default **8**), `delegationMode` (`suggest` default / `prefer`). `delegationMode` is **prompt-only** — with `prefer`, a **Sub-Agent Delegation** section tells the agent to act as a coordinator and push complex work through `sessions_spawn`; actual availability is still governed by tool policy.

**Nesting** (`maxSpawnDepth: 2`): depth 0 = main agent · depth 1 = orchestrator (gets `sessions_spawn`, `sessions_list`) · depth 2 = leaf workers (cannot spawn further). Results flow back up the chain, including status + token stats + guidance (never replacing user instructions). Supported channels (Discord, iMessage, Matrix, Telegram) allow persistent **thread-bound** sessions via `sessions_spawn` with `thread: true` (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`).
