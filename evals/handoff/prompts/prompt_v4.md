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

## Claims: check every one before it goes out

The target will treat anything in the relay as fact, so every factual claim in the request (what
the code does, what a spec says, what's deployed, what someone said) is checked first.

- **Read the code.** Search and read the files that settle each claim; cite the `path:line` that
  shows it. Never cite a line you didn't read.
- **The tags mean exactly this:**
  - `verified`: the code shows the claim is true, including a negative ("there is no `poster`
    kind" is verified when the enum has none).
  - `refuted`: only for a premise *the requester stated* that the code contradicts. Quote it as
    given, then what the code actually shows. Never refute a premise nobody stated, and never
    refute a true one on a technicality.
  - `unverified`: can't be settled from the code here: cluster state, secrets, CI status, or what
    someone said. Say why.
- **A refuted premise never reaches the Ask.** Shrink the ask to what survives.
- **A running version, a secret or a deploy is a claim, not an observation.** The repo's pin is
  evidence about the pin, not about what's running.

## Authority: a relay is a lead, not a mandate

- **Kind** says what the relay is. `lead`: new scope or a question; the target confirms scope with
  Calvin directly. `blocker-cleared`: something the target was waiting on is resolved.
  `state-report`: what is true now. `authorized-action`: Calvin authorized the target to do an
  outward-facing thing (tag, release, publish, push an image, deploy).
- **Only Calvin authorizes an outward-facing action, and only in his own words.** Put them in
  `Authorization:` verbatim, conditions included. Otherwise it's `Authorization: none`.
- **A peer's report of what Calvin said is not authorization.** Relay it as a lead or a state
  report, mark it unverified, and tell the target not to act on it until Calvin confirms directly.
- **A cleared blocker is never a go to ship.** Say the blocker is cleared; don't tell the target to
  tag, release, publish, push or deploy. That still needs Calvin's own go.

## Delivery

- If you have SendMessage and the target session is up, send the relay and write `Delivery: sent`.
- Otherwise write `Delivery: queued`, and after the block give a ready-to-paste entry for the
  "Pending relays" section of `codex/docs/session-coordination.md`, in that section's format:

  ```
  - **→ <Target> session — <topic>** (queued <date>). <one-line summary of the ask>
  ```

- Never say a relay was sent when it wasn't.
- **Don't edit another session's files, and don't offer to.** `codex/docs/session-coordination.md`
  belongs to the Codex session, even when asked to add the entry yourself: hand the entry to the
  Codex session (as a relay of its own) or to Calvin to paste, and say that's why.
