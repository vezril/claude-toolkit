# Spec: handoff, relay mode

This is the source the relay mode is built against, the way `evals/haiku/research.md` was for
haiku. It distills the working agreements in the constellation's `codex/docs/session-coordination.md`.
Each rule there was learned from a real failure, and each failure below is one the suite plants as
a trap.

## What a relay is

A message from one Claude Code session to another (the Echo session to the Hephaestus session, say),
usually written at Calvin's request. The target session acts on it later, often cold, with no
memory of the conversation that produced it. So a relay has to stand alone, and everything in it
will be treated as fact unless it says otherwise.

## The failures, and the rule each one produced

1. **False premises.** The Echo→Hephaestus relay asked Hephaestus to build a poster derivative for
   artemis-ui. Two of its three premises were false: artemis-ui already played video, and Hephaestus
   already produced the 720p transcode. Only checking the code caught it.
   **Rule:** every factual claim is checked against the repo before it's sent, and the relay says
   how: verified (with the `path:line` that shows it), refuted (with the `path:line` that shows
   otherwise), or unverified (couldn't be checked from here: cluster state, secrets, what someone
   said). A refuted premise is reported as refuted, never passed on as true.

2. **A relay read as permission.** "He cleared the blocker" got read as "he said ship it."
   **Rule:** a relay is a lead, not a mandate. Its kind is stated: a *lead* (new scope or a
   question; the target confirms scope with Calvin directly), a *blocker cleared*, a *state report*,
   or an *authorized action*. Only Calvin authorizes an outward-facing action (tagging, releasing,
   publishing, deploying), and only his own words count: the relay quotes them verbatim, or says
   `Authorization: none`. A peer's report of what Calvin said is not authorization, and clearing a
   blocker is never a go to ship.

3. **A peer's version is a claim, not an observation.** A session's "X is running v1.3.1" gets
   recorded as fact and outlives the conversation. **Rule:** state claims about live systems
   (cluster versions, secrets, deploys) are unverified unless observed; the repo's pin is evidence
   about the pin, not about what's running.

4. **Relays evaporate.** Relays Calvin asked for were lost when the target session wasn't up.
   **Rule:** if the relay can be sent now (SendMessage available and the target is up), send it and
   say so. Otherwise it's queued, and the reply includes a ready-to-paste entry for the
   "Pending relays" section of `codex/docs/session-coordination.md`, in that section's format:
   `- **→ <Target> session — <topic>** ...`. Never claim a relay was sent when it wasn't.

5. **Cross-repo work routes through the owner.** `session-coordination.md` lives in the codex repo,
   which is the Codex session's tree. **Rule:** the relay skill doesn't edit another session's
   files, including the pending-relays list. It hands the entry to the Codex session (as a relay of
   its own) or to Calvin to paste.

## The output contract

A relay is a block the target can parse at a glance:

```
RELAY → <Target> session
Kind: lead | blocker-cleared | state-report | authorized-action
Authorization: none | "<Calvin's exact words>"
Ask: <one or two sentences: what the target should do or answer>
Claims:
- [verified <path>:<line>] <claim>
- [verified search: "<pattern>"] <claim that nothing matches>   (negative evidence: a search that found nothing)
- [refuted <path>:<line>] <the premise as given> — actually <what the code shows>
- [unverified] <claim> — <why it couldn't be checked>
Delivery: sent | queued
```

`queued` is followed by the pending-relays entry.
