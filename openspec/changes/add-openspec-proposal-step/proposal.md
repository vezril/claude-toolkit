## Why

`add-jira-triage-profile` made the certified chain runnable and gave it somewhere to stop: a
ticket becomes a challenged breakdown, a rendered brief and an outcome. What it deliberately
left out is everything after the breakdown. The `full` profile still routes to a `solutioning`
step that nothing implements, and `spec-ready.json` has no schema, no producer and no edge.

So the pipeline cannot yet answer the question it exists for — *what change do you propose, and
may I make it?* The brief today summarises a plan for work; it cannot summarise a proposed
change, because no step proposes one.

Two further things are missing that only become visible once a change is proposed:

- **The decision gate has nothing to fire on.** The punch-out triggers derive from the item and
  the breakdown — text, domains and counts. The decisions a human actually wants to hold are
  properties of the *proposal*: how many files it touches, whether it adds a dependency, whether
  it edits a protected path, whether it changes a contract. None of that exists before a proposal
  does, which is why the `triage` profile's gate is the weak one.
- **The OpenSpec lifecycle has no closure.** The live `sdlc-solutioning-openspec` spec defines
  `propose → apply → archive`, with archive human-triggered. If delivery-flow proposes a change
  and then implements from a JSON contract, nothing marks the change's `tasks.md` complete and
  nothing ever archives it. Change directories accumulate, `tasks.md` drifts from reality, and
  the deltas never reach `openspec/specs/`.

## What Changes

- **A `propose` step replacing `solutioning`.** The node runs the OpenSpec propose flow for the
  item, producing `openspec/changes/<change-id>/` with `proposal.md`, `design.md`, at least one
  delta spec and `tasks.md`, and then writes `proposal.json` — the structured contract the rest
  of the flow reads. The prose change directory is for humans and for `openspec archive`; the
  JSON is the edge. `spec-ready.json` is retired before it ever shipped.
- **`proposal.json` as the contract**, against `schemas/proposal.schema.json`: the change id and
  path, the delta specs touched, the tasks with ids and the files each touches, the dependencies
  added, and the node's own `scope`/`architecture`/`breaking` claims. Carries a sentinel like any
  node output.
- **A deterministic proposal edge** (`validate-proposal.py`): the change directory exists and
  holds the four required artifacts, every task id in `proposal.json` appears in `tasks.md` and
  the reverse, every spec the proposal names exists on disk, every task file path is inside the
  repo, and no task is empty. `openspec validate --strict` runs as an **additional** layer when
  the CLI is present and is reported as skipped when it is not — delivery-flow's edge does not
  depend on a tool that is not installed here. (The SDLC readiness gate's separate requirement
  that a missing CLI blocks *that* gate is untouched and still unmet; see design D4.)
- **The brief becomes the approval surface.** In the `full` profile `brief` moves to directly
  after `propose`, and `summary.md` gains a "What will change" section rendered from
  `proposal.json`: the change id, the task count, the files touched, the dependencies added and
  the flags raised. Its coverage edge extends to proposal task ids, so a brief that hides half
  the change fails. The `triage` profile's brief is unchanged and states that no change has been
  proposed.
- **Punch-out triggers derived from the proposal**, firing when the flow would advance from the
  brief into implementation: `proposal-scope` (task or file count over a ceiling),
  `proposal-breaking` (a task touches a `contract_paths` entry), `protected-path` (a task
  touches a `protected_paths` entry — derived from the *planned* files, not only the realized
  diff), and `new-dependency` (the proposal adds one). Same rule as before: a trigger fires on
  the derivation or the node's claim, and disagreement is recorded as evidence rather than
  failing the edge. These derivations read planned file paths, so unlike the triage-profile
  triggers they are **not** text heuristics.
- **Lifecycle closure.** `close-openspec-change.py` marks the change's `tasks.md` items complete
  from `implementation.json` and prints the `openspec archive` command for a human to run. It
  never archives: the live spec says archiving is human-triggered, and the enforcement hook
  already blocks an agent from doing it.
- **`profiles.yaml` updated**: `full` becomes intake → triage → project-memory → breakdown →
  challenge-breakdown → propose → brief → implementation → verify → challenge-implementation →
  pr-description → open-pr → post-summary → post-back → report → vault-update. The `triage`
  profile is unchanged.
- **The `propose` node ships uncertified, declared.** It is listed in `allow_uncertified`, every
  run is traced `certified: false`, and it is excluded from the certified-only rate. Certifying
  it needs an eval suite and three consecutive runs; that is its own change, and claiming the
  chain's number while a chain node is uncertified would make the number meaningless.
- Docs updated per the CLAUDE.md doc-sync rule.

## Capabilities

### New Capabilities
- `openspec-proposal-node`: the `propose` step, the change-directory artifacts it must produce,
  the `proposal.json` contract, the deterministic proposal edge, the optional `openspec validate`
  layer, and the brief's proposal section with its extended coverage check.
- `proposal-punch-out-triggers`: the four proposal-derived triggers, their ceilings, derivation
  from planned file paths, and the point in the flow at which they fire.
- `openspec-lifecycle-closure`: marking `tasks.md` complete from the implementation artifact,
  the human-only archive step, and the rule that a change directory is never abandoned silently.

### Modified Capabilities

<!-- none live: delivery-flow's specs belong to the unarchived changes add-delivery-flow and
     add-jira-triage-profile. This change amends their deltas in prose and archives with them. -->

## Impact

- **New:**
  - `schemas/proposal.schema.json`;
  - `skills/delivery-flow/references/propose.md` (the node prompt, uncertified);
  - `scripts/delivery-flow/validate-proposal.py`, `scripts/delivery-flow/close-openspec-change.py`;
  - `tests/delivery-flow/test_proposal.py`, `tests/delivery-flow/test_lifecycle_closure.py`.
- **Modified:**
  - `templates/delivery-flow/profiles.yaml` (`full` gains `propose`, loses `solutioning`, and
    `brief` moves after `propose`);
  - `scripts/delivery-flow/flow-status.py` (`STEPS`: `proposal.json`/`propose` replaces
    `spec-ready.json`/`solutioning`);
  - `scripts/delivery-flow/brief.py` (the proposal section and its coverage);
  - `scripts/delivery-flow/triggers.py` (the proposal derivations);
  - `scripts/delivery-flow/check-punch-out.py`, `hooks/check-edge.py` (wiring);
  - `skills/delivery-flow/SKILL.md`, `references/config.md`, `references/trace.md`;
  - `docs/figures/delivery-flow-profiles.svg`, `docs/delivery-flow-handoff.md`.
- **Dependencies:** `add-delivery-flow` and `add-jira-triage-profile`. The `openspec` CLI is
  optional here and absent on this machine.
- **Deferred:** a `challenge-proposal` node (the certified challenge prompt is certified against
  breakdowns, and retargeting it un-certifies it); certification of `propose`; auto-merge and
  auto-archive, which stay human.
- **Non-breaking for the certified chain:** the `triage` profile's steps, artifacts, edges and
  brief are untouched, so the Stage 4 submission is unaffected by this change.
