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
  commit: true               # commit delivery/<KEY>/ to the work branch, so the audit
                             # trail travels with the PR and both machines aggregate

punch_out:
  cost_budget_usd: 5.00      # API-equivalent, per item
  retry_limit: 3
  contract_paths: [the-lexicon]     # a diff here is a breaking-change trigger
  protected_paths: [.github, charts, hooks]
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

models:                      # per step; the registry's certified tier is the default
  triage: sonnet
  breakdown: sonnet

roster_overrides:            # replaces a kind of work wholesale, never merges into it
  backend:
    architect: solution-architect
    skills: [scala, akka]
    reviewers: [scala-fp-reviewer]

allow_uncertified: [propose, vault-update]   # steps that may run without certification; each
                             # run is marked certified: false and excluded from the Stage 4
                             # rate. Both are here until they carry a prompt-edd package.
                             # `project-memory` is NOT here: it is a script, not a node.
```

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
- **`artifacts.commit: true`** is the default for a reason — traces committed to the work
  branch are how two machines' runs end up in one report.
- **Roster overrides replace**, so an override is the whole entry for that kind of work.
