# `.delivery-flow.yaml`

One file at the repo root. Its presence is what makes a repo a delivery-flow repo: every
hook and script in this plugin is inert without it, so an unrelated repo is untouched.

```yaml
tracker:
  kind: github-issues        # github-issues | local-markdown
  backlog: docs/backlog.md   # local-markdown only
  external: false            # true for a client's tracker: every post needs a decision

forge:
  kind: github-pr            # github-pr
  base: main

vault:
  binding: null              # a project name enables the recall and update steps

test_command: "sbt test"     # what `verify` runs

artifacts:
  commit: true               # commit delivery/<KEY>/ to the work branch, so the audit
                             # trail travels with the PR and both machines aggregate

punch_out:
  cost_budget_usd: 5.00      # API-equivalent, per item
  retry_limit: 3
  contract_paths: [the-lexicon]     # a diff here is a breaking-change trigger
  protected_paths: [.github, charts, hooks]

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

allow_uncertified: []        # steps that may run without certification; each run is
                             # marked certified: false and excluded from the Stage 4 rate
```

## Rules

- **Missing file: stop and ask.** Never guess a tracker or a forge.
- **`external: true`** on a tracker means a post to it is a punch-out: a client's ticket is
  not somewhere to write unattended.
- **`artifacts.commit: true`** is the default for a reason — traces committed to the work
  branch are how two machines' runs end up in one report.
- **Roster overrides replace**, so an override is the whole entry for that kind of work.
