## MODIFIED Requirements

### Requirement: Readiness gate gains the openspec validate layer

The implementation-readiness gate SHALL run `openspec validate <feature>` as a deterministic
layer alongside `lint-story.py`. Both SHALL run as an **edge check dispatched by
`hooks/check-edge.py`**, declared under `edge_checks` in
`skills/sdlc-orchestration/workflow.yaml` and keyed on the write of `readiness-verdict.json`.
The orchestrator SHALL NOT invoke either script, and SHALL NOT be able to skip them. A non-zero
exit from either SHALL fail the edge, be recorded in the trace, and return the report to the
story-planner (bounded iterations, then human escalation). A missing openspec CLI SHALL block
the gate with a clear report, not pass it.

Two things change from the archived version of this requirement:

- **Who runs it.** It was an instruction in `skills/sdlc-orchestration/SKILL.md` telling the
  orchestrator to run both scripts. An instruction is not a guardrail: a model that skipped it
  produced no failure. It is now dispatched by a hook on the artifact write.
- **When it runs.** The archived requirement said the gate short-circuits "before any LLM
  alignment review runs". That ordering no longer holds and SHALL NOT be claimed. The
  `readiness` segment is the two nodes `readiness` and `readiness-review`; the reviewer writes
  `readiness-verdict.json`, and *that write* is what fires the deterministic checks. The
  guarantee is therefore not "no LLM review runs on a malformed set" but the narrower and
  truthful one below: a `PostToolUse` hook cannot un-write a file, so what the gate guarantees
  is that the failure is recorded and advancing past it is refused.

#### Scenario: Invalid change artifacts

- **GIVEN** a change whose delta spec fails validation
- **WHEN** `readiness-verdict.json` is written and the edge check runs
- **THEN** `scripts/sdlc/readiness-gate.py` exits non-zero with the validator output, the edge
  records the failure, the orchestrator refuses to advance past the `readiness` terminus, and the
  story-planner receives the rework

#### Scenario: The orchestrator cannot substitute its own judgement

- **GIVEN** a story set that fails `lint-story.py`
- **WHEN** the orchestrator has not run either script itself
- **THEN** the edge check still ran, because it is keyed on the artifact write rather than on an
  instruction, and the recorded verdict is what the gate decision reads

#### Scenario: A missing validator blocks rather than passes

- **GIVEN** a repo with no `openspec` CLI on PATH
- **WHEN** the readiness edge check runs
- **THEN** it reports the missing CLI as a failure, because a gate that reports success when it
  could not look is no gate
