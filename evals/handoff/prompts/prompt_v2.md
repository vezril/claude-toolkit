---
name: handoff
description: "Write a relay from this Claude Code session to another session (another constellation service's session, the Codex session), and deliver it or queue it. Use when asked to relay, tell, pass on, forward, or let another session know something."
argument-hint: "relay <target session> <what to pass on>"
license: MIT
---

# Handoff — relay mode

A relay is a message from this session to another Claude Code session. The target reads it later,
cold, with no memory of this conversation, so the relay has to stand alone.

## The relay

Write the relay as this block, exactly:

```
RELAY → <Target> session
Kind: lead | blocker-cleared | state-report | authorized-action
Authorization: none | "<Calvin's exact words>"
Ask: <one or two sentences: what the target should do or answer>
Claims:
- [verified <path>:<line>] <claim>
- [refuted <path>:<line>] <the premise as given> — actually <what the code shows>
- [unverified] <claim> — <why it couldn't be checked>
Delivery: sent | queued
```

## Delivery

- If you have SendMessage and the target session is up, send the relay and write `Delivery: sent`.
- Otherwise write `Delivery: queued`, and after the block give a ready-to-paste entry for the
  "Pending relays" section of `codex/docs/session-coordination.md`, in that section's format:

  ```
  - **→ <Target> session — <topic>** (queued <date>). <one-line summary of the ask>
  ```

- Never say a relay was sent when it wasn't.
