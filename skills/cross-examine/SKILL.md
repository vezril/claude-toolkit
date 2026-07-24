---
name: cross-examine
description: "Spin up an independent adversarial validator to try to REFUTE a finding, analysis, or proposed fix before a human accepts it — the challenge protocol for uncertain conclusions at decision gates. Use when the user is unsure about an analysis or root cause, wants a second opinion with teeth, says 'challenge this', 'red-team this', 'are we sure?', or before approving a gate on shaky evidence. Invokes the adversarial-validator agent in a fresh context with full code/log access and the artifact under challenge (never the reasoning that produced it), and turns the verdict into a challenge artifact the gate decision can use."
user-invocable: true
argument-hint: "[artifact or claim to challenge, e.g. 'the analysis for AICAA-123']"
---

# cross-examine — the challenge protocol

When a conclusion matters and you are not sure of it, don't re-read it harder. Hand it to an opponent. This skill is the protocol around the `adversarial-validator` agent: what to send, what to withhold, and what the verdict means.

## Why a separate agent, every time

The refutation must run in a fresh context. A challenger who has watched the analysis being built inherits its anchoring and will find what the analyst found. Independence rules:

- **Send the artifact under challenge and raw-material pointers** (repo paths, log excerpts or store access, the ticket). The challenger re-derives from evidence.
- **Withhold the reasoning chain.** Not the chat history, not "we think X because Y", not prior drafts. The artifact must stand on what it states and cites.
- **Prefer the strongest model available.** The agent inherits your session model; if you are running a small model, override upward when spawning (this work is judgment-heavy). The mandate matters more than the model, but give it both.

## Run it

1. Identify the exact artifact under challenge (a file, or a stated claim quoted verbatim).
2. Spawn the `adversarial-validator` agent with: the artifact content, pointers to the raw material it needs (code paths, log data, tickets), and nothing else about how the conclusion was reached.
3. Wait for the verdict. Do not run your own parallel defense; the point is to see whether the artifact survives on its own.

## The challenge artifact

Persist the result next to the thing it challenged (in a pipeline: `defects/<KEY>/challenge-<artifact>.md`; standalone: alongside the file). Content: the agent's verdict block verbatim, plus a one-line header naming what was challenged and when.

## Acting on the verdict

- **REFUTED** — the challenged artifact is invalid. Rerun the step that produced it with the refutation's findings as input. Do not patch the artifact by hand; the producing step owns it.
- **WEAKENED** — the core stands but holes are real. Address each finding explicitly (in the artifact or the gate decision) before proceeding. A weakness acknowledged at the gate is fine; one discovered after shipping is not.
- **SURVIVED** — proceed with earned confidence. Read the attack log anyway: the attacks that were tried and failed are exactly what to cite when a stakeholder asks "are we sure?"

A verdict is input to the human gate, not a replacement for it. The human still decides; the challenge changes what they know when they do.

## When to reach for a panel instead

One adversary is the default and usually enough. If the stakes justify it (an irreversible change, a contested root cause), escalate to a panel: three validators with distinct lenses (evidence-chain, alternative-hypothesis, reproduction) and treat two successful refutations as decisive. That is a Workflow-scale job; build it only when a single challenger has actually proven insufficient.
