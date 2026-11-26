# `.delivery-flow.yaml`

One file at the repo root. Its presence is what makes a repo a delivery-flow repo: every
hook and script in this plugin is inert without it, so an unrelated repo is untouched.

**Generate it rather than typing it:** `init-delivery-flow.py <repo>` detects the forge, base
branch, test command and existing protected paths, and leaves the un-guessable keys
(`tracker.project`, `tracker.external`, `punch_out.contract_paths`) marked for a human. The
shape below is the full reference.

```yaml
profile: full                # full | triage — a named slice of the routing table
                             # (templates/delivery-flow/profiles.yaml). Absent means full.

tracker:
  kind: github-issues        # github-issues | local-markdown | jira
  backlog: docs/backlog.md   # local-markdown only
  external: false            # true for a client's tracker: every post needs a signed decision

forge:
  kind: github-pr            # github-pr
  base: main

vault:
  binding: null              # a project name enables the recall and update steps
  path: ~/Obsidian/MyVault   # the LOCAL clone; recall fails loudly if it is not there
  graph_root: Atlas/RAG      # the graph inside the vault (may be empty for the vault root)
  backend: filesystem        # filesystem | iris (iris is reserved, not implemented)
  remote: ssh://nas/vault.git  # informational: the canonical bare repo. Git's `origin` is the
                             # authority; recall reports a disagreement between the two.

test_command: "sbt test"     # what `verify` runs

artifacts:
  # Run artifacts belong in the vault, not in the repo. `flow-status.py` refuses to compute a
  # position when they are in the repo without a recorded reason, so this is a gate rather
  # than advice — see "Where artifacts live" below.
  root: ~/Vault/Atlas/RAG/_runs   # absolute: the vault's runs directory. `init` derives it
                                  # from --vault-path and --graph-root rather than taking it
                                  # by hand.
  # ...or, instead of `root`, the recorded exception:
  in_repo_ack: "our own tracker, private repo"   # keeps artifacts in `delivery/` and says why

punch_out:
  cost_budget_usd: 5.00      # API-equivalent, per item
  retry_limit: 3
  contract_paths: [the-lexicon]     # a diff here is a breaking-change trigger
  protected_paths: [.github, charts, hooks]
  # Both path lists match by path *segment*, not string prefix: `lib` covers `lib/core.py`
  # and not `lib_extra/core.py`. Keep them as narrow as the surface other callers actually
  # reach — a prefix naming a whole package fires on every change inside it, including ones
  # that break nobody, and a gate that always fires teaches people to wave it through.
  #
  # The realized diff these match is scoped to *the item being checked*: the commits whose
  # message names its key, plus the uncommitted working tree. Two items worked on one branch
  # therefore do not inherit each other's changes. The cost is that a commit naming no item
  # key is attributed to nobody and its paths go unchecked — `check-punch-out.py --json`
  # reports that count under `diff_attribution.commits_unattributed`, and says so on stderr.
  # Ceilings for the derived triggers. Tune them against real runs rather than editing
  # scripts/delivery-flow/triggers.py.
  epic_ceiling: 4            # more epics than this derives a scope trigger
  story_ceiling: 12          # more stories than this derives a scope trigger
  domain_ceiling: 2          # a breakdown spanning more domains derives an architecture trigger
  require_acceptance_signal: true   # an item stating no expected outcome derives a scope
                             # trigger; false rests scope on the ceilings and the node's flag
  proposal_task_ceiling: 8   # a proposal with more tasks needs a decision
  proposal_file_ceiling: 15  # a proposal touching more distinct files needs a decision
  vault_staleness_days: 14   # days since the vault clone last *fetched* before recall marks
                             # its memory stale. `null` disables the check.

deploy:
  patterns: ["helm upgrade", "helm install", "flux reconcile", "docker push"]
  auto_roll:
    routine_bumps: true      # patch-level image pins may roll without a decision
    never: [api, schema, breaking, first-deploy, exposure]

decisions:
  allowed_signers: ~/.config/delivery-flow/allowed_signers
  # The key itself is NOT configured here — see "Signing" below. It is per-machine, and so is
  # the agent socket, so both live in ~/.config/delivery-flow/signing.env.

models:                      # per step; the registry's certified tier is the default
  triage: sonnet
  breakdown: sonnet

roster_overrides:            # replaces a kind of work wholesale, never merges into it
  backend:
    architect: solution-architect
    skills: [scala, akka]
    reviewers: [scala-fp-reviewer]

allow_uncertified: [propose, review, vault-update]   # steps that may run without
                             # certification; each run is marked certified: false and excluded
                             # from the Stage 4 rate. All three are here until they carry a
                             # prompt-edd package.
                             # `project-memory` is NOT here: it is a script, not a node.

punch_out:
  max_diff_files: 25         # a change touching more files than this raises a punch-out at
  max_diff_lines: 800        # verify: the flow stops and a human decides split or proceed.
                             # Derived from the actual diff, never from a node's claim about
                             # its own size, so rewording an artifact cannot clear it.
                             # Per-repo: what counts as large differs by repository, and a
                             # plugin-level default would be wrong everywhere. An ABSENT
                             # ceiling is reported, never treated as unlimited.
```

## `test_command` and the verify step

`run-verify.py` runs `test_command`, runs the protected-path check, and writes `verify.json`
with the `tests[].covers` mapping the scope edge reads. A script, not a node.

`verify` was `kind: build` with no producer for a long time: four things read `verify.json` and
nothing wrote it, so the test-scope edge could never fire and a `full` run could not pass this
step.

Two distinctions the artifact keeps, because collapsing either flatters a bad run:

- **`suite.status: not-run` is not `red`.** A suite that never started says nothing about the
  code. An unset `test_command` is `not-run`, never a failing build.
- **`protected_paths_checked: false` is not an empty pass.** An unusable `protected_paths:`
  block means nobody looked, which must not read as nothing being touched.

A red suite is a **successful** verify — the step reports, the edge and the reviewer judge.

**`verify.json`'s schema is deliberately open**, and tightening it is a mistake worth naming.
Across the eight artifacts written before the schema existed, only `item` appears in every one,
and `test_command` appears as both a string and an object. The rest — `gates`,
`discrepancies`, `planned_vs_realized`, `coverage_percent` and about eighty other keys — varies
by run, because this is an evidence document the orchestrator shapes for the change in front of
it rather than a fixed record. A first version of the schema was closed and required invented
field names; it rejected all eight real artifacts and blocked their edges. `story` and `tests`
are optional for the same reason: the scope edge reports an honest no-op without them.

## `mutation` — the gate that proves the tests can fail

```yaml
mutation:
  enabled: true                            # off unless set; the cost is per-mutant
  subset_template: "pytest -q {paths}"      # {paths} = the diff's test files
  max_mutants: 20                           # budget; a cap is reported, never hidden
  timeout: 300                              # seconds per mutant run
```

A green suite says the tests pass. It does not say they would fail if the code were wrong, and
the difference is where a whole class of review comments lives — one on a client PR read
*"making it unconditional still passes."* A test had been added for a conditional write and
never reached the branch, so deleting the condition broke nothing the suite could see.

`mutation-gate.py` settles that by measurement: break the production lines **this branch
changed**, run the diff's tests, and record which mutants nobody noticed. `verify.json` carries
the result under `mutation`, and `survived[]` is the finding — each entry a line the branch
added that no test defends.

Four properties worth knowing before turning it on:

- **The diff only.** Mutating untouched code measures the suite's whole history, which is a
  different question and would bury the finding.
- **Production files only**, by the same classifier the dev-pair hook uses
  (`hooks/enforce-dev-pair-boundary.py`). Mutating a test and watching it fail proves nothing.
- **It never writes inside your repo.** It copies the tree once and mutates the copy, because
  it deliberately breaks source and the repo may hold uncommitted work.
- **A red baseline means it does not run**, and says so. A mutant "killed" by an
  already-failing suite was killed by the failure. `ran: false` always carries a `reason` and is
  never an empty pass — the same rule as `protected_paths_checked`.

It is **Python-only** today, and off by default. `--mutation` / `--no-mutation` on
`run-verify.py` override the config either way, and `mutation-gate.py` runs standalone: exit 0
all killed, 1 survivors, 3 could not run.

## Before submitting

`check-submission.py` is the last gate: chain certified, package builds without a DRAFT stamp,
criterion 4 has a rate at all, every terminal run has step records, and the denominator's
composition is disclosed. Blocking failures exit 1; a thin denominator is a warning, because
what sample a reviewer accepts is theirs to decide and not this script's.

A check that cannot run is reported as a failure, never a pass.

## Replayed runs

Re-running the flow over an already-closed ticket, to gather volume for criterion 4:

```bash
write-outcome.py <ITEM-KEY> --replay
```

A replay **is** a real run — real nodes, real edges, real artifacts — and for the
analysis-only `triage` profile it exercises exactly what the end-to-end rate measures, so it is
counted in the rates rather than excluded.

It is **not a delivery**. `delivery-report.py` states the split in a "What the runs were"
section placed before any rate computed over it, and names each replayed item so the count can
be audited against the run directories. A rate quoted without that split would imply live work
that did not happen.

The flag is set by the caller, because **nothing on disk distinguishes a replay from a first
run** — the artifacts are identical. That makes it the one claim in `outcome.json` taken on
trust, which is why it is recorded rather than inferred: an inferred flag nobody set would be
worse than an honest one somebody did. Absent rather than `false` when not passed, so outcomes
written before the field existed do not read as asserted first runs.

Two things that make a replay worth counting at all:

- **A fresh item key.** The flow is artifact-driven, so re-running an existing item directory
  skips to `report` without the nodes executing. Deleting artifacts to force a rerun is what
  `manual-correction` detection exists to catch.
- **A ticket with a followable body.** The Jira adapter resolves GitHub issue references, not
  other trackers' links. A triage over a 50-character stub is not a run worth evidencing.

## `review` and the chain gate

`review` is outside the certified chain (`chain: false` in `steps.yaml`). That matters for the
evidence package: `package-evidence.py` gates on `check-certification.py --all --chain-only`,
so an uncertified non-chain step does not block a build whose claim is about the chain. Before
`--chain-only` existed the packager gated on every registered step, and registering `review`
was enough to take the Stage 4 package back to DRAFT while the certified chain was untouched.

`--all` without `--chain-only` still reports every step, including the uncertified ones. The
narrowing is to the *gate*, not to the report.

## Rules

- **Missing file: stop and ask.** Never guess a tracker or a forge.
- **`external: true`** on a tracker means a post to it is a punch-out: a client's ticket is
  not somewhere to write unattended. The adapter refuses the post unless a decision for the
  item carries a signature that verifies against `decisions.allowed_signers` — a decision
  file on its own is not enough, because an agent can write a file.
- **`profile:`** selects which steps run. An unknown name is refused rather than defaulted,
  so a typo cannot silently shorten the pipeline. The format is paired with `load_profiles`
  in `scripts/delivery-flow/common.py`: change one and change the other.
- **Derived-trigger ceilings are policy, not implementation.** They live here so they can be
  tuned from real runs; a trigger still fires on the node's own flag whatever they are set to.
- **An unreachable vault is a failure, not an empty result.** Recall checks the graph root
  before scanning and exits 3 with no artifact if it is missing. A reachable vault with nothing
  relevant exits 0 and writes an artifact saying so. The trace distinguishes "no memory was
  applied" from "memory was consulted and had nothing", which are different facts about a run.
- **The vault is a local clone and the remote is canonical.** `vault.path` points at a git work
  tree on this machine, so recall keeps working away from the network that hosts the remote.
  That trades a loud failure for a quiet one — a clone weeks behind looks identical to a current
  one — so every run reports its sync state (HEAD, dirty, ahead/behind, days since the last
  fetch) in `project-context.json` and the trace, and sets `stale` against
  `punch_out.vault_staleness_days`. **Recall makes no network call**: a step that hung waiting
  on an unreachable remote would reinstate the dependency the local clone removes.
- **Staleness is measured by the last fetch, not the last push.** A push proves the remote was
  reachable but teaches this clone nothing, so a laptop that pushed an hour ago can still be a
  month behind what another machine decided.
- **Nothing in the flow pushes.** `vault-update` commits; a push is an outward action over a
  network that may not be there, so it waits for a human on the right network.
- **The proposal ceilings gate the `full` profile.** They are the decision gate for real work:
  under them, a change goes from ticket to PR without stopping. Lower them to be asked more.
### Signing

The key path and the agent socket are per-machine, so they are not in `.delivery-flow.yaml`.
`decide.py` reads them from `~/.config/delivery-flow/signing.env`:

```
SSH_AUTH_SOCK=~/Library/Containers/com.maxgoedjen.Secretive.SecretAgent/Data/socket.ssh
DELIVERY_FLOW_SIGNING_KEY=~/.ssh/delivery-flow.pub
DELIVERY_FLOW_SIGNER=calvin
```

The file is **parsed, not sourced** — a config file that silently executes shell is the wrong
shape for the thing the punch-out guarantee rests on.

**`SSH_AUTH_SOCK` from the file wins over the environment; the `DELIVERY_FLOW_*` vars yield to
it.** The asymmetry matters: macOS always has `SSH_AUTH_SOCK` pointing at its own launchd
agent, so treating "already set" as authoritative means the file's value never applies and
signing quietly reaches an agent that does not hold the key. Naming the socket in this file is
the deliberate choice; the ambient value is just the default. Nothing but a person sets the
`DELIVERY_FLOW_*` vars, so an explicit one on the command line is an override and is honoured.

**There is no default key path.** `decide.py` used to fall back to `~/.ssh/id_ed25519_sk`, so
a machine that had never had that file refused with "No such file or directory" naming a key
its owner does not own — which points at the wrong problem. It now says "no signing key
configured" and names what to set.

### Where artifacts live

**A run's artifacts go in the vault.** `delivery/<KEY>/` holds the ticket body, the triage
rationale, the breakdown and the brief — someone else's words, most of the time. Inside the
code repo that is one `git add` from a branch and one push from publishing a client's text.
`nx-neptune` is the case in point: a public AWS checkout whose tracker is a client's Jira.

So `flow-status.py` runs a preflight before it computes anything, and exits 2 when:

- the resolved root is inside the code repo's working tree, or
- a vault is bound and the root is not under it.

Since every invocation starts with `flow-status.py`, a misplaced root stops the flow rather
than warning into a log. The vault being its own git repo is fine and is the point — that is
what versions the trail and syncs it between machines. What must not happen is the artifacts
sitting in the repository being worked on.

`artifacts.in_repo_ack` is the only exception, and it is a sentence, not a boolean: say why
in-repo is acceptable here. It covers the default layout, test fixtures, and a private repo
whose tracker is its own. It has to be written down rather than implied, because this is the
one place where "it was fine on my machine" publishes someone else's data.

`init-delivery-flow.py` refuses to guess, the way it already refuses to guess the Jira key and
`contract_paths`: pass `--vault-path ~/Vault [--graph-root Atlas/RAG]` and it derives
`artifacts.root`, or pass `--artifacts-in-repo "<reason>"` and it records the exception.

Two things to get right in the vault: give the runs their own subdirectory rather than mixing
them into `deliveries/`, where recall scans for notes and would start reading `trace.jsonl` as
a decision; and prefix it with an underscore (`_runs`) so Obsidian keeps a few hundred JSON
files out of search and the graph view, the same convention `_templates` uses.

**`artifacts.commit` is gone.** It was written into every generated config and read by no
code — the mechanism it described, traces committed to the work branch so two machines
aggregate, did not exist. The question it was answering does not arise once the trail is not
in the repo.
- **A configured root means that directory and no other.** Path matching is anchored to it, so
  an unrelated directory that happens to be called `delivery` is not mistaken for the root.
- **Roster overrides replace**, so an override is the whole entry for that kind of work.
