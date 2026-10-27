# The five criteria, and what to hand a reviewer

One section per examined criterion: what satisfies it, what does not, and the concrete
artifact this repo submits. The package builder
(`scripts/delivery-flow/package-evidence.py` — one directory per criterion, plus a README
mapping each to its criterion) is specified but **not yet written**; see tasks 9b.

Paths below are `claude-toolkit`'s. If you are certifying a different workflow, the shapes
transfer; the filenames will not.

---

## 1. Workflow definition

**Satisfies.** An executable definition of the sequence: the routing table, the artifact each
step produces, the schema each artifact must match, and a router that *computes* position from
what is on disk rather than remembering it.

**Does not.** A diagram, a README paragraph, or an orchestrator prompt that describes the
order in prose. If the only thing that knows the sequence is a model's context, there is no
definition — there is a habit.

**This repo.** `skills/delivery-flow/SKILL.md` (routing table), `schemas/*.schema.json` (each
naming `produced_by` / `consumed_by`), `scripts/delivery-flow/flow-status.py` (the router:
prints what exists, what each edge said, and either `Next: <step>` or `BLOCKED — <reason>`),
`docs/figures/delivery-flow.svg`.

**Tell.** Delete the conversation and run the router. If it can still say where the item is
and what runs next, the definition is real.

---

## 2. Guardrails

**Satisfies.** Deterministic checks that fire automatically at every handoff, in code, after
the write. For each artifact, in order: it parses → its sha matches its sentinel → it conforms
to its schema → the sentinel's claimed counts match the real counts → it satisfies the input
contract of the step that consumes it.

**Does not.** A validator script the orchestrator is told to call. An LLM "reviewing" the
output. A prompt instruction to self-check. Each of these depends on the model's cooperation,
which is exactly what a guardrail is for.

**This repo.** `hooks/check-edge.py` (PostToolUse; exit 2 feeds the failure back to the model
and appends the verdict to `trace.jsonl`), `scripts/delivery-flow/validate-artifact.py`
(stdlib JSON Schema subset, `--consumer` for input contracts),
`scripts/delivery-flow/write-sentinel.py`, `tests/delivery-flow/test_edges.py`.

**Submit also:** traces from real runs showing the hook firing — including at least one
*failed* edge and the rerun that followed. An edge that has never caught anything is
indistinguishable from an edge that cannot.

---

## 3. Punch-out evidence

**Satisfies.** Triggers defined as properties of artifacts; enforcement in a `PreToolUse` hook
that denies the action; decisions a human alone can produce; and an adversarial suite that
tried to get past all of it.

**Does not.** Fixed human review between steps (that is Stage 2). An instruction in the
orchestrator prompt saying "ask the human before merging". A TTY check — fakeable with
`script -q /dev/null` or `pty.fork()`.

**This repo.** `scripts/delivery-flow/check-punch-out.py` (eight triggers),
`scripts/delivery-flow/decide.py` (`ssh-keygen -Y sign`, namespace `delivery-flow-decision`,
human-presence key), `hooks/enforce-punch-outs.py` (denies decision writes, continuation while
a punch-out is open, every merge, and deploys without a valid signed decision unless the
auto-roll rule covers them — and an auto-roll pass is written to the trace, so it is a recorded
policy decision rather than a silent one), `tests/delivery-flow/bypass/bypass-report.md`.

**Submit the holes too.** The bypass report is stronger for naming the three real gaps the
first run found (a regex that could never match, a bail-out missing `curl`, a check that was
not checking) than it would be for reporting a clean sweep. Reviewers have seen clean sweeps.

---

## 4. End-to-end success rate

**Satisfies.** A rate over **real runs on real work items**, with the denominator stated, a
weekly trend, and manual corrections counted as failures.

**Does not.** Eval-suite pass rates. Evals guard against regression; they are not the pipeline
running. This is the one criterion no amount of building can produce — it needs weeks of use.

**This repo.** `scripts/delivery-flow/delivery-report.py` emits per-item outcomes, a weekly
rate, and a **certified-only** column (runs made entirely of certified steps — that is the
Stage 4 number; runs including uncertified steps are reported separately, never merged in).
Outcomes are `completed` / `punched-out` / `failed` / `abandoned`; `failed` includes reason
`manual-correction`, detected by comparing an artifact's sha to the trace record.

**Open with your reviewer.** Whether a "run" is one work item, and whether punch-outs sit in
the denominator. The report emits both readings until that is settled — say so rather than
picking the flattering one.

---

## 5. Audit trail

**Satisfies.** One machine-readable record per step: timestamp, item, step, agent, session,
**model actually used**, tokens by class (input, output, cache creation, cache read),
API-equivalent cost, the artifact produced, and the checker's verdict. Plus whether the step
was certified and whether the model matched its declared tier.

**Does not.** Chat logs. A list of commits. A record that says a step ran but not what ran it.

**This repo.** `hooks/trace-step.py` (SubagentStop/Stop → `trace.jsonl`),
`scripts/delivery-flow/delivery-report.py` (per-step and per-model tables).

**Two traps worth inheriting.**

- Claude Code repeats the same `usage` object on **every content block** of one API message.
  Summing transcript lines overcounts several-fold; de-duplicate by `message.id`.
  `tests/delivery-flow/test_trace.py` pins this.
- Transcripts are written asynchronously, so a record can lag the final message. Write the
  record immediately and reconcile at report time rather than blocking.

---

## Order to build in

Criteria 1–3 and 5 are construction; criterion 4 is calendar time. Build the trace and the
enforcement first, start running real items as early as the pipeline tolerates, and finish the
remaining nodes while the rate accumulates. Nothing else in the package can substitute for
runs that happened.
