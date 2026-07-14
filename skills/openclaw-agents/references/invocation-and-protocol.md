# OpenClaw — invoking agents (CLI + gateway protocol) & the trust model

Source: docs.openclaw.ai `/cli/agent`, `/gateway/protocol`, `/gateway/operator-scopes` — fetched 2026-07. Two ways to run one agent turn: the **`openclaw agent` CLI** (which itself calls the gateway, falling back to embedded) and the **gateway `agent` RPC** over WebSocket.

## `openclaw agent` — one turn via the gateway

Executes a single agent turn through the Gateway, **auto-falling back to embedded execution** if the gateway request fails. Force embedded with `--local`.

**Session selector — at least one required:**
- `--to <dest>` — recipient; derives the session key
- `--session-key <key>` — explicit routing key
- `--session-id <id>` — explicit session id
- `--agent <id>` — agent id; **overrides routing bindings**

**Message — exactly one source required:**
- `-m, --message <text>` — inline text
- `--message-file <path>` — read UTF-8 file (preserves multiline, strips BOM, rejects invalid UTF-8)

**Key options:**
- `--model <id>` — override model (`provider/model` or a model id)
- `--thinking <level>` — `off | minimal | low | medium | high` or provider-specific
- `--verbose <on|off>` — persist verbosity for the session
- `--timeout <seconds>` — override the default **600 s**; `0` disables
- `--local` — force embedded execution
- `--deliver` — send the reply to the selected channel/target
- `--json` — JSON output (stdout = response; diagnostics → stderr)

**Delivery overrides:** `--channel <channel>`, `--reply-to <target>`, `--reply-channel <channel>`, `--reply-account <id>`.

```bash
openclaw agent --to +15555550123 --message "status update" --deliver
openclaw agent --agent ops --message "Summarize logs"
openclaw agent --session-id 1234 --message "Summarize inbox" --thinking medium
openclaw agent --agent ops --message "Generate report" --deliver --reply-channel slack --reply-to "#reports"
```

With `--json --deliver`, the response includes a `deliveryStatus` object whose `status` is `sent | suppressed | partial_failed | failed`.

## The gateway RPC surface (WebSocket)

**Frame formats** (WebSocket text frames carrying JSON):
- Request — `{ type:"req", id, method, params }`
- Response — `{ type:"res", id, ok, payload|error }`
- Event — `{ type:"event", event, payload, seq?, stateVersion? }`

**Agent methods:**
- `agent` / `agent.wait` — start a turn (returns `{ runId, acceptedAt }`) and wait for completion (`{ status: ok|error|timeout, startedAt, endedAt, error? }`). Requires scope **`operator.write`**.
- **Idempotency** — side-effecting methods (`send`, `agent`) require idempotency keys; the server keeps a short-lived dedup cache.
- **Cancellation** — `sessions.abort` (pass `key` + optional `runId`, or `runId` alone) stops a run; `chat.abort` cancels a specific queued turn by `runId` or clears authorized queued turns before aborting active runs.

**Timeouts / limits:** default **30 s** per-RPC request timeout; pre-auth frames capped at **64 KiB**; post-handshake limits governed by `hello-ok.policy`.

## Handshake & authentication

1. The server sends a **pre-connect challenge** (nonce + timestamp).
2. The client replies with `connect`: protocol range, client identity, **role**, **scopes**, and device auth — **signing the nonce** (v2/v3 payload; v3 binds platform + deviceFamily) within the allowed clock skew.
3. The gateway replies `hello-ok`: negotiated protocol version, server info, features, snapshot, auth details, policy limits.

**Auth modes:** shared-secret via `connect.params.auth.token` or password; alternatives are **Tailscale Serve** and **trusted-proxy headers**. First frame **must** be `connect` — a non-JSON or non-`connect` first frame closes the connection.

**Pairing / local trust:** every client provides device identity on connect. **Local loopback can auto-approve**; tailnet and LAN connects require explicit approval. The gateway issues device tokens, pins paired metadata, and requires re-pair for changes.

## Roles & operator scopes

Clients connect as one of two **roles**: `operator` (control-plane: CLI, Control UI, automation, trusted processes) or `node` (capability hosts exposing commands via `node.invoke`).

| Scope | Grants |
|---|---|
| `operator.read` | Non-mutating: status, lists, catalog, logs, **session reads** |
| `operator.write` | Mutating: messaging, **tool/agent invocation**, settings updates, node relay (includes `.read`) |
| `operator.admin` | Full admin; satisfies all `operator.*`; required for config changes, updates, native hooks, reserved namespaces |
| `operator.pairing` | Device/node pairing: approve, reject, remove, rotate, revoke |
| `operator.approvals` | Exec & plugin approval APIs |
| `operator.talk.secrets` | Talk configuration incl. secrets |

Scopes are **control-plane guardrails within a trusted operator domain**, not multi-tenant isolation — for real separation, run separate gateways under different OS users/hosts. Method scope is only the first gate; handlers apply stricter per-resource checks (e.g. `/config set`/`/config unset` need `operator.admin` on top of write; approving a device only grants scopes the approver already holds). Shared-secret auth receives the full default operator scope set on OpenAI-compatible HTTP + session-history endpoints regardless of declared scopes; identity-bearing modes can honor explicit restrictions.

## Remote access

Preferred: **Tailscale / VPN**. Alternative: SSH tunnel — `ssh -N -L 18789:127.0.0.1:18789 user@gateway-host` — same handshake and auth apply over the tunnel; TLS + pinning optional. (The gateway listens on `127.0.0.1:18789` by default and is exclusive per host.)
