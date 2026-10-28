# Session coordination

## Ownership map

| Repo(s) | Session | Notes |
|---|---|---|
| `codex` | Codex | Deploys, pins, constellation docs. Other sessions do not edit this repo. |
| `artemis-service`, `artemis-ui` | Artemis | Media gallery |
| `hephaestus-service`, `hephaestus-ui` | Hephaestus | Media processing (derivatives) |
| `hermesmq` | Hermes | The broker and its clients |
| `demeter-service`, `demeter-ui` | Demeter | Deals |
| `echo-service`, `echo-ui` | Echo | YouTube follower |

## Pending relays (send when the peer channel + target session are both up)

Relays Calvin asked for that couldn't be sent yet. **Any Codex session:** if the channel is up and
the target is online, send it, then delete the entry.

- **→ Artemis session — watched-state per post** (queued 2026-09-09). Echo wants a per-post
  watched flag; nothing built yet, no direction given.
