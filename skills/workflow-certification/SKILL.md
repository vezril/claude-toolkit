---
name: workflow-certification
description: "Certify a multi-step agentic workflow — AI Maturity Stage 4 (\"Workflow\"), the level above a single certified prompt. Covers the node/edge model, what counts as a deterministic guardrail, sentinel files, punch-out points and how to prove they hold, the end-to-end success rate, and the audit trail. Use when someone is designing, auditing or submitting an agentic pipeline for Stage 4, asks what Stage 4 requires, asks whether a chain of agents is certifiable, or wants to know if a check they have written is a real guardrail. The Stage 3 counterpart is prompt-edd."
user-invocable: true
argument-hint: "[workflow to certify, or a criterion to check]"
---

# Certifying a workflow (AI Maturity Stage 4)

Stage 3 certifies **one prompt**: measurable criteria, a real eval suite, an iteration log
(`prompt-edd`). Stage 4 certifies **one workflow**: several certified prompts wired together,
with deterministic code between them and a human holding the decisions that matter.

This file is a restatement of Improving's course *AI Governance & Guardrails (Stage 3 → Stage 4)*,
written so you can work without the deck. Where a reviewer disputes a reading, the deck wins —
Calvin has it under `Improving/Stage 4/` in iCloud. The interpretation calls this project made
are recorded in `openspec/changes/add-delivery-flow/design.md` (D7, D11–D15).

## The one sentence that decides most arguments

> A workflow is only as trustworthy as its **edges**, not its nodes.

- A **node** is a non-deterministic LLM step. Each one is independently certified at Stage 3.
- An **edge** is a deterministic check between two nodes. Code. No model in it anywhere.

Nodes are where the capability is; edges are where the trust is. Stage 4 examines the edges,
because a chain of individually-excellent prompts with nothing between them is still Stage 3
repeated N times.

Scale: a submission is a chain of roughly **2–3 nodes**, each clearing its Stage 3 bar over
**3 consecutive runs**. It is not "certify all forty of my agents".

## Three rules that fall out of it

**1. If a node's output is read by another node, it must be structured data with a schema.**
Deterministic code can check "does this match the schema". It cannot check "is this a good
paragraph". Markdown with agreed section headings is not a contract — the course names that
exact substitution as the thing that does not count. Prose survives only at the ends of the
chain, where a person is the reader and no node consumes it.

**2. Edge checks run as hooks after the write, never as a call the model chooses to make.**
A validator the orchestrator is instructed to invoke is not a guardrail: if the model skips it,
nothing happens, and the guardrail now depends on the thing it guards. The check needs the
artifact to exist, so it belongs on `PostToolUse`. A `PostToolUse` hook cannot un-write the
file — that is why it records a verdict in the trace and the orchestrator refuses to advance
past a failed edge, rather than pretending it prevented anything.

**3. An LLM reviewing another LLM is a node, not a guardrail.** The *reviewer trap*: in shared
context, the reviewer rationalizes rather than reviews, and you have added a second
non-deterministic step while believing you added a check. It becomes legitimate only when it
runs in a **fresh context**, carries its **own Stage 3 certification**, emits a **structured
verdict**, and a **harness applies fixed rules** to that verdict (e.g. REFUTED reruns the
producing step, WEAKENED requires each finding addressed, SURVIVED proceeds). The reviewer is
the node; the rules are the edge.

## Sentinels: make the node state a claim you can falsify

Each node writes `<artifact>.sentinel.json` beside its output: `{artifact, sha256, counts, status, step, ts}`,
where `counts` is what the node *believes* it produced (epics, stories, acceptance criteria,
findings, failing tests).

The sentinel is a **claim, not a fact**. Its whole value is the gap it exposes: a node reporting
`status: complete, stories: 8` over a file holding 5 passes schema validation and fails the edge.
A node that writes no sentinel fails its edge too. Without sentinels a node's self-report is
never tested against its own output.

## Punch-outs: the decisions an AI does not get to make

A **punch-out** is a decision handed to a human because of what the work turned out to be, not
because of where the flow got to.

**Human review between every step is Stage 2, not Stage 4.** Fixed checkpoints mean the
workflow cannot run; Stage 4 wants a pipeline that runs end to end and *stops on policy*.
Triggers are properties of the artifacts — scope change, architecture change, breaking change,
protected paths, a challenge refuted twice, retry limit, budget breach, an outward-facing post.

Three things separate a real punch-out from a documented intention:

- **Enforcement the agent cannot talk its way past.** A `PreToolUse` hook that denies the
  action, not a sentence in a prompt. Instructions are not controls.
- **A decision only a human can produce.** This project signs decisions with an SSH key that
  requires human presence (Secure Enclave/Touch ID or a FIDO key). Note what does *not* work:
  **a TTY check is not a security boundary** — an agent fakes one with `script -q /dev/null` or
  `pty.fork()`.
- **Evidence it was tested.** Someone tried to get past it and was blocked. Write an adversarial
  bypass suite, run it, and submit the report including the holes it found. See
  `tests/delivery-flow/bypass/`: 15 attacks, and the first run exposed three genuine gaps that
  64 green unit tests had not.

## What gets examined, and what counts as evidence

Five criteria. `references/evidence-checklist.md` has the per-criterion checklist and how this
repo satisfies each.

| Criterion | The question behind it |
|---|---|
| Workflow definition | Is the sequence written down as something executable, not described in prose? |
| Guardrails | Are the checks between steps deterministic, automatic, and unskippable? |
| Punch-out evidence | Are the human decision points enforced, and was that tested adversarially? |
| End-to-end success rate | Over real runs, how often does the whole thing finish without a human fixing output by hand? |
| Audit trail | For each step: which model, how many tokens, what cost, which artifact, what the checker said? |

Two definitions that catch people out:

- **"No agents that still require regular manual correction."** Hand-editing a validated
  artifact to get a step to pass is not a repair, it is a failed run. Detect it: compare the
  artifact's sha to the one in the trace, and mark the run `failed` with reason
  `manual-correction`. A pipeline whose number depends on quiet hand-fixes has no number.
- **Punched-out ≠ failed.** Distinguish `completed` / `punched-out` / `failed` / `abandoned` in
  the outcome record. Handing a decision to a human is the system working. (Whether punch-outs
  belong inside or outside the success-rate denominator is worth asking your reviewer; emit
  both readings until someone rules.)

## Every node is Stage 3 certified, on the cheapest model that passes

An uncertified node makes the end-to-end number meaningless, so the chain's nodes each need a
`prompt-edd` package: ≥3 distinct criteria, ≥95% of asserts, a load-bearing map covering ≥90%
of the prompt's instructions, an iteration log with real measured hypotheses, and the certified
prompt's sha recorded so any edit forces recertification. Enforce it in code before delegating
a step — see `scripts/delivery-flow/check-certification.py`.

Model policy, and it runs the other way from instinct:

- Try **Haiku first**, then Sonnet. The tier is the cheapest one whose suite actually passes.
- Frontier models need **escalation evidence**: a committed results file showing the cheaper
  model below the bar on the same suite. Defaulting to Opus inverts the burden of proof and
  inflates the audit trail's cost column for nothing.
- The course's "separate model for validation" means the checker differs from the generator —
  a different model, or the same model in a fresh context with a refute-framed prompt. It does
  not mean "use the big model".
- Record the model each step **actually ran on** and flag drift. Declared tiers lie; traces do not.
- Knowledge skills loaded as context (`scala`, `react`) are reference material, not prompts with
  an output contract. This project's working assumption is that they are covered by the eval of
  the agent consuming them. Unconfirmed by reviewers — flag it rather than assume it.

## Self-test before submitting

Answer these honestly; each one has sunk a design here at least once.

1. Point at an edge. Is there a model anywhere inside it? If yes, it is a node.
2. Could the orchestrator complete a step *without* the check running? If yes, it is not a guardrail.
3. Is any artifact a node consumes prose? Rewrite it as schema-backed data.
4. Has anyone actually attacked the punch-outs, or is the evidence "we wrote a rule"?
5. Does the success rate come from real runs, or from eval suites? Evals guard regressions; only
   real runs produce the rate.
6. Does the audit trail name the model per step, or just that the step happened?
7. Can you state the number of manually-corrected runs? If you cannot detect them, you cannot.

## The cost word

If runs execute under a subscription rather than per-token billing, the figure in the report is
tokens priced at published list rates. Call it **API-equivalent cost** everywhere, never "cost".
Claiming billed spend you did not incur is the kind of thing a reviewer checks.
