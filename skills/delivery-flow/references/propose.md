---
name: propose
description: "Turn a challenged breakdown into a proposed change — an OpenSpec change directory plus the structured contract the rest of the flow reads. Emits proposal.json."
---

# Propose the change

**This prompt is not yet certified.** `propose` is listed in `allow_uncertified`, every run is
traced `certified: false`, and those runs are excluded from the certified-only end-to-end rate.
Do not cite a `full`-profile success rate as a Stage 4 number until this node carries a
`prompt-edd` package. Editing this file does not un-certify anything, because there is nothing
to un-certify yet.

## Inputs

You are given, and may read nothing else:

- `item.json` — the ticket as the tracker holds it
- `triage.json` — its classification and policy flags
- `breakdown.json` — the epics, stories and acceptance criteria
- `challenge-breakdown.json` — the adversarial verdict and findings
- `carry_forward` — findings from a `WEAKENED` verdict that you are required to address

You do not get the conversation that produced any of them. That is deliberate: a proposal
written from the reasoning behind a breakdown tends to inherit its blind spots.

## What to produce

**1. An OpenSpec change directory** at `openspec/changes/<change-id>/`, where `<change-id>` is
kebab-case and starts with a verb (`add-`, `extend-`, `fix-`, `retire-`):

- `proposal.md` — `## Why`, `## What Changes`, `## Capabilities`, `## Impact`. Distill the
  ticket and the breakdown; reference them, never refork their content.
- `design.md` — `## Context`, `## Goals / Non-Goals`, `## Decisions` (numbered `D1`, `D2`, …,
  each stating the alternative it rejected and why), `## Risks / Trade-offs`,
  `## Migration Plan`, `## Open Questions`.
- `specs/<capability>/spec.md` — at least one delta spec in `## ADDED Requirements` /
  `## MODIFIED Requirements` form, each requirement followed by `#### Scenario:` blocks in
  **GIVEN / WHEN / THEN** form.
- `tasks.md` — a checklist whose every item begins `- [ ] T<n> ` with a stable, unique id.
  The ids are the contract: `proposal.json` must list exactly the same set.

**2. `proposal.json`** in the item's delivery directory, conforming to
`schemas/proposal.schema.json`:

```json
{
  "item": "<ITEM-KEY>",
  "change_id": "add-bounded-backoff",
  "change_path": "openspec/changes/add-bounded-backoff",
  "specs_touched": ["openspec/changes/add-bounded-backoff/specs/retry-policy/spec.md"],
  "tasks": [
    {"id": "T1", "description": "Add the backoff schedule", "files": ["src/main/scala/Consumer.scala"]}
  ],
  "dependencies_added": [],
  "scope": false,
  "architecture": false,
  "breaking": false
}
```

Then write its sentinel: `write-sentinel.py <path>/proposal.json --step propose`.

## The rules the edge enforces

Its checks are deterministic, so these are not advice:

- **Task ids match in both directions.** Every `T<n>` in `proposal.json` appears in `tasks.md`,
  and every `T<n>` in `tasks.md` appears in `proposal.json`. A JSON that omits planned work
  understates the change as badly as one that invents work the markdown never agreed to.
- **Every path in `specs_touched` exists on disk.** Name the delta specs you actually wrote.
- **Every task names at least one file, and every file path stays inside the repository.** No
  absolute paths outside the repo, no `..` escapes.
- **No empty task descriptions.**
- `openspec validate --strict` also runs where the CLI is installed.

## The flags, and why lying about them is pointless

`scope`, `architecture` and `breaking` are your own assessment, and they *raise* a decision for
a human — they never lower one. The punch-out triggers also derive from the files your tasks
name: a planned path under a shared contract or a protected path fires regardless of what you
set. Setting a flag false that the paths contradict does not avoid the gate; it records a
disagreement against your proposal in the audit trail.

Set them true when you believe them. A false negative costs the project a decision nobody made;
a false positive costs a human one question.

## Judgement

- **Address the carry-forward findings.** A `WEAKENED` verdict means the breakdown was right but
  incomplete. Each finding must be visibly answered in the proposal — in a requirement, a task,
  or an explicit `## Open Questions` entry saying why not.
- **Propose the smallest change that satisfies the acceptance criteria.** The size ceilings are
  policy, not a target; a proposal that trips them should be because the work genuinely is large,
  not because it absorbed adjacent cleanups.
- **Name decisions, not preferences.** A `D<n>` that does not say what it rejected is a
  description, not a decision.
- **Do not plan to touch protected paths casually.** If the work truly needs one, say so in
  `design.md` so the human reading the brief has your reasoning alongside the question.
