# OpenClaw — the agent loop, concurrency, streaming, lifecycle

Source: docs.openclaw.ai `/concepts/agent-loop`, `/concepts/queue`, `/concepts/streaming`, `/concepts/compaction`, `/automation/hooks` + `/plugins/hooks` — fetched 2026-07. The embedded agent runtime is a **serialized, per-session process**: message → context → inference → tools → stream → persist.

## The run sequence (five stages)

1. **RPC entry** — the `agent` / `agent.wait` gateway methods (or CLI `openclaw agent`) validate params, resolve the **session key/ID**, persist metadata, and **immediately return `{ runId, acceptedAt }`**. The call is accepted asynchronously; the run itself proceeds in the background.
2. **Command execution** — `agentCommand` resolves model defaults (thinking / verbose / trace), loads the **skills snapshot**, invokes `runEmbeddedAgent`, and emits fallback lifecycle events if needed.
3. **Embedded agent run** — `runEmbeddedAgent` serializes execution via **per-session and global queues**, resolves auth, builds the OpenClaw session context, subscribes to runtime events, streams deltas, **enforces timeouts**, and returns payloads with usage metadata.
4. **Event bridging** — `subscribeEmbeddedAgentSession` routes runtime events to **three streams**: `tool` (tool start/update/end), `assistant` (model deltas), `lifecycle` (phase: start / end / error).
5. **Completion wait** — `agent.wait` (`waitForAgentRun`) polls for **lifecycle end/error** on a `runId` and returns `{ status: ok | error | timeout, startedAt, endedAt, error? }`. Waiting is *observation only* — an `agent.wait` timeout never stops the underlying run.

## Queueing & concurrency (the lane system)

Inbound auto-reply runs (all channels) pass through a tiny in-process, **lane-aware FIFO queue**; each lane drains with a configurable concurrency cap. This "prevents multiple agent runs from colliding."

- **One active run per session key.** Messages enqueue by session key → a dedicated **session lane** serializes them, preventing tool/session races. Global parallelism is capped by `agents.defaults.maxConcurrent`.
- **Lane caps:** `main` defaults to **4**, `subagent` to **8**, unconfigured lanes to **1**. Background lanes (`cron`, `nested`, `subagent`) keep background work from blocking inbound.
- **Typing indicators fire immediately** despite queue waits (UX preserved). Queued waits do **not** project as active runs in `sessions.list`.

### Queue modes — how messages that arrive mid-run are handled

| Mode | Behavior |
|---|---|
| `steer` (default) | Inject the new message into the active runtime, applied **after the current assistant turn finishes its tool calls** |
| `followup` | Queue sequentially; run after the current run completes |
| `collect` | Coalesce queued messages into a single followup after a quiet window |
| `interrupt` | **Abort** the active run and execute the newest message |

**Resolution order:** per-session `/queue` override → channel `messages.queue.byChannel` → global `messages.queue.mode` → built-in default (`steer`). Options: `debounceMs` (quiet window, default 500 ms), `cap` (max queued per session, default 20), `drop` (`summarize` | `old` | `new`; default `summarize`). Set per session with `/queue <mode> debounce:500ms cap:25 drop:summarize`; clear with `/queue default` / `/queue reset`.

### Session write lock

Transcript writes are protected by a **file-based, process-aware lock** on the session file. Writers wait up to `session.writeLock.acquireTimeoutMs` (default **60 000 ms**) before the session is reported busy. Non-reentrant unless `allowReentrant: true`.

## Streaming behavior

OpenClaw has **two independent streaming layers** and *no true token-delta streaming*:

- **Block streaming (channels)** — assistant output ships in **coarse completed blocks** as normal channel messages: `model output → text_delta events → chunker → channel send`. `EmbeddedBlockChunker` enforces min/max bounds and break preferences.
  - `blockStreamingDefault` (`on`/`off`, default `off`); `blockStreamingBreak` = `text_end` (flush each event) or `message_end` (buffer until the assistant message completes, then flush).
  - Chunk bounds `blockStreamingChunk { minChars, maxChars, breakPreference }`; break chain **paragraph → newline → sentence → whitespace → hard**; **never splits inside code fences** (closes/reopens if forced). Coalescing (`blockStreamingCoalesce { minChars, maxChars, idleMs }`) merges consecutive chunks.
- **Preview streaming (multi-platform)** — temporary preview messages updated on Telegram/Discord/Slack/Matrix/Mattermost/MS Teams. Modes `off | partial | block | progress`. Tool-progress lines ("reading file", "calling tool") show during execution; hide with `streaming.preview.toolProgress: false`.

At the run level: **assistant deltas** stream as `assistant` events; block streaming emits partial replies on `text_end`/`message_end`; **reasoning** can stream separately or fold into block replies; chat channels buffer deltas into `delta` messages and emit a single **`final`** on lifecycle end/error.

**Reply shaping:** tool results are sanitized for size/images before logging; messaging tool sends are de-duplicated; the silent token **`NO_REPLY` is filtered** from outgoing payloads. The final reply combines assistant text (+ optional reasoning), inline tool summaries (when verbose/allowed), and error text.

## Compaction & retries (long runs)

- **Auto-compaction** triggers when a session nears the context limit or the model returns an overflow error (OpenClaw recognizes dozens of provider overflow strings — "context length exceeded", "input is too long", etc.). Older turns are summarized into the transcript; recent turns kept; **tool-call/`toolResult` pairs are kept together** at the split point. Emits `compaction` stream events; **on retry, in-memory buffers and tool summaries reset** to avoid duplicate output.
- Before summarizing, the agent is reminded to **save important data to memory files** first.
- Manual: `/compact [guidance]`. Config lives under `agents.defaults.compaction`: `model` (dedicated summarizer, local ok), `mode` (defaults to `safeguard` — stricter guardrails + summary audits), `identifierPolicy` (`strict` default / `off` / `custom`), `maxActiveTranscriptBytes` (byte-guard trigger independent of context state), `notifyUser`, `memoryFlush.model`, `truncateAfterCompaction` (successor transcripts + checkpoints), `provider` (pluggable). **Compaction ≠ pruning**: compaction summarizes history to the transcript; pruning trims *tool results only*, in-memory per request.

## Timeouts

| Timeout | Default | Notes |
|---|---|---|
| `agent.wait` | 30 s | Wait-only; `timeoutMs` overrides. **Does not stop the run.** |
| Agent runtime `agents.defaults.timeoutSeconds` | 172 800 s (48 h) | Enforced by `runEmbeddedAgent` abort timer. `0` = unlimited. |
| Cron isolated agent turn | owned by cron | Scheduler times the turn, aborts at deadline, runs bounded cleanup. |
| Model idle | cloud 120 s / self-hosted 300 s | Aborts when no response chunks arrive. Extend via `models.providers.<id>.timeoutSeconds`. |
| Provider HTTP request | `models.providers.<id>.timeoutSeconds` | Covers connect, headers, body, and stream idle watchdog. |

**Early-termination points:** agent timeout (abort) · AbortSignal (cancel) · gateway disconnect / RPC timeout · `agent.wait` timeout (wait-only).

## Stuck-session diagnostics

With `diagnostics.stuckSessionWarnMs` (default 120 000 ms), a long `processing` session with no reply/tool/status/block progress is classified:

- `session.long_running` — active embedded run / model / tool calls; silent model calls stay here until `stuckSessionAbortMs`.
- `session.stalled` — active work, no recent progress; model calls switch here at/after the abort threshold.
- `session.stuck` — recoverable stale bookkeeping with idle queued sessions.

`diagnostics.stuckSessionAbortMs` defaults to ≥5 min and 3× the warn threshold. `stalled`/`stuck` trigger recovery on heartbeat ticks.

## Hooks around the agent lifecycle

**Internal (gateway) hooks** — event-driven scripts for commands and lifecycle, e.g. `agent:bootstrap` (runs *before* system-prompt finalization to add/remove bootstrap context files), plus command hooks for `/new`, `/reset`, `/stop`.

**Plugin hooks** — extension points across the agent/tool/gateway pipeline:

| Hook | Purpose |
|---|---|
| `before_model_resolve` | Override provider/model before resolution (pre-session) |
| `before_prompt_build` | Inject context / system-prompt overrides after session load |
| `before_agent_start` | Legacy compat (prefer the explicit hooks above) |
| `before_agent_reply` | Claim the turn / return a synthetic reply after inline actions |
| `agent_end` | Post-completion with final message list + metadata |
| `before_compaction` / `after_compaction` | Observe/annotate compaction cycles |
| `before_tool_call` / `after_tool_call` | Intercept tool params/results |
| `tool_result_persist` | Transform tool results before transcript write |
| `before_install` | Modify staged skill/plugin install material |
| `message_received` / `message_sending` / `message_sent` | Inbound/outbound message hooks |
| `session_start` / `session_end`, `gateway_start` / `gateway_stop` | Lifecycle boundaries |

**Decision rules:** `before_tool_call` / `before_install` use `{ block: true }` (terminal) vs `{ block: false }` (no-op); `message_sending` uses `{ cancel: true/false }`.
