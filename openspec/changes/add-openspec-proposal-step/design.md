## Context

After `add-jira-triage-profile` the `triage` profile runs end to end on three certified nodes.
The `full` profile does not: its `solutioning` step has no producer, and `spec-ready.json` has
no schema and no edge. This change fills that slot with an OpenSpec proposal and makes the brief
the thing a human approves.

What already exists and constrains the design:

- The live spec `openspec/specs/sdlc-solutioning-openspec/spec.md` says solutioning *is* the
  OpenSpec propose flow, names the four artifacts, puts `openspec validate` in the readiness
  gate, and makes `openspec archive` human-triggered. This change must agree with it rather
  than invent a parallel notion of "proposal".
- `brief.py` is shared by `render-brief.py` and `hooks/check-edge.py`, so the template and its
  coverage check cannot drift. Extending the brief means extending both at once, by construction.
- `triggers.py` is shared by `check-punch-out.py` and the edge hook, with the established rule:
  fire on derivation **or** claim, record disagreement as evidence, never fail an edge on it.
- Hooks are global to every session with the plugin installed, so everything stays inert outside
  a repo holding `.delivery-flow.yaml`.
- `openspec` is not installed on this machine (node 18 via mise; only `corepack` and `npm`
  global).

## Goals / Non-Goals

**Goals:**
- Turn a challenged breakdown into a proposed change whose contract downstream steps can read.
- Give a human one artifact to approve, in the brief's fixed shape, with the decision stated.
- Derive the decision gate from planned file paths rather than from text or from a node's flag.
- Close the OpenSpec lifecycle far enough that `tasks.md` does not drift and archiving is an
  explicit human act rather than a thing nobody does.
- Leave the certified `triage` profile byte-for-byte unaffected.

**Non-Goals:**
- Certifying the `propose` node. It ships declared-uncertified; its eval suite is another change.
- A `challenge-proposal` node.
- Auto-archive, auto-merge, or deploy. All stay human.
- Making delivery-flow depend on the `openspec` CLI.

## Decisions

**D1 — `propose` replaces `solutioning`; `proposal.json` replaces `spec-ready.json`.**
`spec-ready.json` was a placeholder with no schema, no producer and no consumer contract, so
there is nothing to migrate. Replacing rather than chaining matters for cost: OpenSpec's
`tasks.md` *is* the sequenced backlog `story-planner` would otherwise produce, so running both
means two nodes to certify and two decompositions to keep in step. The SDLC dev pair still does
the implementing — it reads `proposal.json.tasks` instead of story files.

**D2 — The change directory is the human artifact; `proposal.json` is the contract.**
OpenSpec's four files are prose and markdown, and Stage 4's first rule is that anything a
downstream node reads must be schema-backed. So the node writes both, and the edge checks that
they agree: every task id in the JSON appears in `tasks.md` and the reverse. Writing one without
the other is the failure mode this catches — a beautiful change directory with a JSON that omits
half of it, or a JSON describing tasks the markdown never lists.

**D3 — The brief is where the human approves, and it moves to sit after `propose`.**
This is the point of the whole pipeline for its intended reader: one artifact, fixed shape,
stating what will change and what is being asked. The brief gains a "What will change" section
(change id, task count, files touched, dependencies added, flags raised) and its coverage edge
extends to proposal task ids — so a brief that silently drops half the change fails rather than
reading as reassuringly short. The section order is unchanged for the `triage` profile, where it
states that nothing has been proposed.

**D4 — `validate-proposal.py` is the edge; `openspec validate` is an optional extra layer.**
The CLI is not installed, and an edge that cannot run is not a guardrail. So the deterministic
checks are ours: directory structure, the four artifacts, task-id closure in both directions,
spec files existing, task file paths inside the repo, no empty task. When `openspec` *is* on
PATH, `--strict` runs as well and its result is recorded; when it is not, the trace records
`openspec_validate: "skipped: not installed"` so its absence is visible rather than silently
assumed-fine.

This deliberately does **not** satisfy the live spec's requirement that a missing CLI block the
*SDLC readiness gate*. That is a different gate in a different pipeline, it is still unmet, and
`add-jira-triage-profile` task 7.2 already records it. Quietly reinterpreting that requirement
to mean "delivery-flow is fine without the CLI" would be the kind of thing a reviewer catches.

**D5 — Proposal triggers derive from planned file paths, which makes them the strong ones.**
The `triage` profile's derivations are text heuristics over a ticket, with the laundering
residual recorded in `add-jira-triage-profile`'s design. The proposal names the files each task
will touch, so these derivations are path matches:

| Trigger | Derivation |
|---|---|
| `proposal-scope` | task count over `proposal_task_ceiling`, or distinct file count over `proposal_file_ceiling` |
| `proposal-breaking` | a planned file path is under a `punch_out.contract_paths` entry |
| `protected-path` | a planned file path is under a `punch_out.protected_paths` entry |
| `new-dependency` | `proposal.json.dependencies_added` is non-empty |

A path match is not defeated by rewording. It is still defeated by a node that plans one set of
files and implements another — which is why `protected_paths` is *also* checked against the
realized diff at `verify`, as it already is. Two checks on the same property at two points,
because the proposal is a claim about the future and the diff is a fact about the past.

**D6 — The triggers fire on leaving the brief, not on writing the proposal.**
A punch-out raised while `proposal.json` is being written would block the brief that explains
it, and the human would be asked to decide with nothing to read. Writing the proposal, rendering
the brief, then evaluating policy puts the explanation in front of the decision.

**D7 — Closure marks `tasks.md`; only a human archives.**
`close-openspec-change.py` ticks the change's `tasks.md` from `implementation.json` and prints
the `openspec archive <id>` command. It does not run it: the live spec says archiving is
human-triggered, `enforce-punch-outs.py` already blocks an agent from it, and promoting deltas
into the living specs is exactly the kind of irreversible act that should cost a deliberate
keystroke. What this does buy is that `tasks.md` stops lying about what shipped.

**D8 — `propose` is declared uncertified rather than quietly run.**
It goes in `allow_uncertified`, each run traces `certified: false`, and
`delivery-report.py` already excludes such runs from the certified-only rate. The alternative —
running it and reporting the `full` profile's rate as a Stage 4 number — would be the exact
error `workflow-certification` warns about: an uncertified node makes the end-to-end number
meaningless.

## Risks / Trade-offs

- **The `full` profile's rate will not be submittable** until `propose` is certified. Accepted:
  the `triage` profile carries the submission, and the two profiles' rates are reported
  separately precisely so one cannot borrow the other's credibility.
- **`proposal.json`'s file lists are predictions.** A node may plan `a.scala` and touch `b.scala`.
  Mitigated by the realized-diff checks at `verify`, not by trusting the proposal.
- **Retiring `spec-ready.json` touches the parent change's deltas.** Handled the same way as
  before: the amendment is in prose here, and the changes archive together.
- **The brief grows.** Its whole value for its reader is brevity, and a proposal section adds
  length. Mitigated by rendering counts and paths rather than prose, and by the word and
  sentence ceilings staying measured in the trace so the trend is visible.

## Migration Plan

1. Schema, validator and tests first — the edge before the producer, so a bad proposal cannot
   pass while the node is being written.
2. `profiles.yaml` and `flow-status.py` together; the `triage` profile's rows must not move.
3. `brief.py` and its coverage, with the `triage` profile's output asserted byte-identical.
4. Triggers, then the closure script.
5. `propose.md` and `allow_uncertified`, then docs and figures in the same PR.

## Open Questions

1. **Should `propose` run on Sonnet or be tried on Haiku first?** Model policy says Haiku first
   with recorded failure. Deferred to the certification change, where the evidence gets produced.
2. **Does the brief need the delta-spec text, or only the task shape?** Starting with the shape;
   revisit after real briefs show what a reader was missing.
3. **Is `openspec` worth installing on this machine?** It would add `validate --strict` here and
   unblock the SDLC readiness gate requirement. Needs a decision about adding a global npm
   dependency to the toolchain.
