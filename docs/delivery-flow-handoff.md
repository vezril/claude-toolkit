# delivery-flow: handoff

For a Claude instance picking this work up cold. Read this first, then
`openspec/changes/add-delivery-flow/` (proposal, design, specs, tasks) for the full
specification. Last updated 2026-10-27.

## What this is

A workflow that takes one work item from a tracker to a merged, deployed change, built so it
can be certified at **Stage 4 of Improving's AI Maturity Model**. The certification is
Calvin's; the workflow is general and lives in the public `claude-toolkit` plugin.

**What Stage 4 requires is written up in full in the `workflow-certification` skill**
(`skills/workflow-certification/`) — the node/edge model, sentinels, punch-outs, the five
examined criteria with a per-criterion evidence checklist, and a self-test. Read it before
making design calls; you do not need the course deck to work here. An earlier version of this
design was wrong in three ways until the deck was read, and the corrections are recorded in
`design.md` (D7, D12–D15).

The deck itself — Improving's *AI Governance & Guardrails (Stage 3 → Stage 4, Q3 2026)* — stays
the authority if a reviewer disputes a reading. It is in Calvin's iCloud under
`Documents/Library/1xx - Personal/120 - Work and Career/121 - Employer and Clients/Improving/Stage 4/`,
on his machine only.

The model in one paragraph: a **node** is a non-deterministic LLM step, each independently
certified at Stage 3; an **edge** is a deterministic code check between nodes; "a workflow is
only as trustworthy as its edges, not its nodes". Three rules follow that shaped everything
here: a node's output must be structured data a schema can check (prose does not count);
edge checks run as **hooks after the write**, not as something a model chooses to call; and
an LLM reviewing another LLM is a second node needing its own certification, not a guardrail.

The five things the certification examines, and where each stands:

| Criterion | State |
|---|---|
| Workflow definition | Built: the skill, the router, the schemas |
| Guardrails | Built: edge hook, sentinels, schemas |
| Punch-out evidence | Built: triggers, signed decisions, blocking hook, bypass report |
| End-to-end success rate | Machinery built; **needs real runs** |
| Audit trail | Built: trace hook, report |

## Where the work lives

Everything is on branch **`feat/delivery-flow-triage-node`**, open as **PR #88**. Merge it
before starting, or work on that branch — `main` does not have any of it yet, and `main` is
PR-protected (always branch, never push to it).

```
openspec/changes/add-delivery-flow/   proposal, design, 6 capability specs, tasks (29 done / 43 open)
openspec/changes/add-jira-triage-profile/  the certifiable slice: profiles, Jira, the brief,
                                      derived triggers — 4 capability specs
openspec/changes/add-openspec-proposal-step/  the full profile: propose, the approval brief,
                                      proposal triggers, lifecycle closure — 3 specs
openspec/changes/add-vault-delivery-memory/   project memory: recall as a *script*,
                                      reachability, the update node — 3 specs
skills/workflow-certification/        what Stage 4 requires, standalone — read this first
skills/delivery-flow/
  SKILL.md                            the orchestrator: routing table, profiles, rules
  steps.yaml                          the step registry: certification evidence per step
  references/                         config.md, adapters.md, roster.md, trace.md
  references/triage.md                CERTIFIED node prompt (byte-identical to its eval version)
  references/breakdown.md             CERTIFIED node prompt
schemas/                              item, triage, breakdown, challenge, sentinel, outcome
templates/delivery-flow/profiles.yaml named slices of the routing table (triage | full)
templates/delivery-flow/roster.yaml   kinds of work -> architect, skills, reviewers
scripts/delivery-flow/
  common.py                           repo/config/roster/schema/pricing/signature helpers,
                                      plus the adapter contract: exit codes and `outward_refusal`
  flow-status.py                      the router: where an item is, what runs next (profile-aware)
  adapters/jira.py                    the Jira tracker adapter (REST, no LLM, no MCP)
  adapters/github_issues.py           GitHub Issues, through `gh`
  adapters/github_pr.py               open a PR, read the checks on a ref
  adapters/local_markdown.py          a backlog file as a tracker — the one to pilot with
  brief.py                            the brief's template + its coverage checks, shared
  render-brief.py                     writes summary.md from the structured artifacts
  write-outcome.py                    the report step: outcome.json, manual-correction detection
  triggers.py                         punch-out derivations, independent of triage's own flags
  init-delivery-flow.py               opt a repo in: detects what it can, asks for the rest
  validate-proposal.py                the proposal edge: JSON vs the OpenSpec change directory
  close-openspec-change.py            ticks tasks.md from implementation; never archives
  vault-recall.py                     delivery recall, deterministic (a script, not a node)
  scaffold-vault.py                   creates the graph in an existing vault, additively
  validate-artifact.py                schema subset checker (stdlib only)
  write-sentinel.py                   a node's claim about what it produced
  check-punch-out.py                  the eight triggers
  decide.py                           signed human decisions
  check-certification.py              the Stage 3 bar per step
  delivery-report.py                  end-to-end rate, cost per step and model
hooks/
  check-edge.py                       PostToolUse: the edge checks
  trace-step.py                       SubagentStop/Stop: model, tokens, cost per step
  enforce-punch-outs.py               PreToolUse: agents cannot decide, merge or deploy
evals/delivery-triage/                10 real fixtures, 4 criteria, iteration log, load-bearing map
evals/delivery-breakdown/             6 real fixtures, same shape
tests/delivery-flow/                  375 tests across 14 suites
tests/delivery-flow/bypass/           the bypass suite and its report
```

## Run everything

```bash
cd ~/Code/claude-toolkit
for t in tests/delivery-flow/test_*.py; do python3 "$t"; done     # 375 tests
python3 scripts/delivery-flow/check-certification.py --all        # every registered step
python3 tests/delivery-flow/bypass/run-bypass.py --model sonnet   # 23 attacks, ~12 min, costs usage
#   writes bypass-report.md and bypass-report.results.json (reword the prose from the JSON,
#   never by re-running: each run is ~12 min of real model calls)
```

Evals (each suite has `run.sh`; `REPEAT=1` for a single pass):

```bash
cd evals/delivery-triage && ./run.sh v8 sonnet
cd evals/delivery-breakdown && REPEAT=1 ./run.sh v6 sonnet
node rescore.js results/run_v6_sonnet_run1.json   # re-score saved outputs, no model calls
```

## What is certified

| Step | Model | Evidence |
|---|---|---|
| `triage` | Sonnet | 3 consecutive runs: 95.0 / 97.5 / 100% |
| `breakdown` | Sonnet | 3 consecutive runs: 100 / 95.8 / 100% |
| `challenge-breakdown` | Sonnet | 3 consecutive runs, prompt v3a |
| `pr-description` | Haiku | 89/90, but terminal prose with no edge — **not** chain evidence |

`propose` and `vault-update` are **declared uncertified** (`allow_uncertified`), so the `full`
profile's rate is not a Stage 4 number. `project-memory` is not in that list because it is a
script: its scoring is arithmetic the spec fully determines, so it is tested exactly rather
than certified to a 95% bar. That is a deliberate departure from
`extend-vault-graphrag-projects` task 3.4 — reasoning in `add-vault-delivery-memory` design D1.

The `triage` profile is the chain to submit: `triage → breakdown → challenge-breakdown`, three
certified nodes, ending in a rendered brief and an outcome. The brief and the report are
scripts, not nodes, so they need no certification — that is deliberate, and it is why this
slice adds no eval suites. See `docs/figures/delivery-flow-profiles.svg`.

**Haiku is ruled out for both chain nodes, with evidence, not assumption.** Across three
tactics (anchored literal, stated consequence, worked example) it kept wrapping JSON in a
```json fence: 26 runs out of 30 on triage, and schema 0/18 on breakdown. Its judgement was
never the problem (grounding 30/30). If you certify a new node, try Haiku first and record
the failure — that is the model-tier policy, and `check-certification.py` enforces the rest.

## Conventions that are not optional

**Evals before prompts.** Follow the `prompt-edd` skill: write the suite, measure an honest
naive baseline, then change **one concern per iteration** with the hypothesis written down
*before* the run. Every number in an iteration log comes from an executed run.

**Never weaken an assert to make a score look better.** If an assert is genuinely wrong, fix
it, say so in the log, and re-score every prior version on the corrected basis (`rescore.js`
replays saved outputs with no model calls). This has happened twice, and both times the tell
was the same: *the model disagreeing with the labels in one consistent direction.* Suspect
the labels when that happens.

**Discard contaminated runs rather than report them.** Usage-limit cut-offs and harness bugs
have produced partial runs; they are deleted or renamed `DISCARDED-*`, and the log says why.

**Artifacts are contracts.** Never hand-write or tidy an artifact to get past a check. The
trace records each artifact's sha, so a hand-edit marks the run `failed` with reason
`manual-correction` — which is the honest outcome, not a thing to route around.

**The work is public.** `claude-toolkit` is a public repo. No client names, no real log lines,
no PHI in fixtures. Client-specific work belongs in the private `claude-toolkit-private`.

## Verified facts, so you do not re-derive them

Checked against Claude Code 2.1.209 on 2026-09-16, with a live payload capture:

- `SubagentStop` carries `agent_id`, `agent_type`, `agent_transcript_path`, `transcript_path`,
  `stop_hook_active`, `last_assistant_message`. `Stop` carries the same minus the agent
  fields. `SubagentStart` fires too.
- **Transcripts repeat the same `usage` object on every content block of one API message.**
  Summing lines overcounts several-fold; count once per `message.id`. There is a test for it.
- Transcripts are written asynchronously, so a record can lag the final message.
- **A TTY check is not a security boundary.** Claude Code's Bash tool has no TTY, but an agent
  can fake one with `script -q /dev/null` or Python's `pty.fork()`. That is why decisions are
  signed by a key requiring human presence rather than gated on a terminal.
- PyYAML is not installed on either of Calvin's Macs. Everything is standard library;
  `common.py` has the config and pricing parsers.
- The plugin cache lags `main`: merging a hook does not activate it until the cache updates
  and the session restarts. Budget for it when testing hooks on a real repo.

## The vault: a local clone, the NAS canonical

**Restructured 2026-10-28.** It used to be read straight off the AFP mount at
`/Volumes/Private/Amazon RAG`. That failed its first real test — away from the home network the
mount is gone, recall exits 3, and the flow stops. The NAS being unreachable is not a good
enough reason to stop work, and the mount had already dropped mid-session once while at home.

The shape now:

| Where | What | Role |
|---|---|---|
| `~/Amazon RAG` | a git work tree; the real Obsidian vault, `Atlas/RAG/` inside it | what recall reads; always reachable |
| `http://mimir.experimentalneutron.com:8668/git/cference/amazon-rag.git` | a **private GitBucket repo** | `origin`, the canonical copy both Macs converge on |

**Live since 2026-10-28.** Git rather than a synced directory: two Macs editing the same
decision note is exactly what last-writer-wins would destroy silently, and a decision's history
is part of the audit trail. NAS-only — no third-party host — so client decision notes stay on
hardware Calvin owns.

The remote is **GitBucket, not an ssh bare repo**, which is a change from the original plan: ssh
to mimir refused the laptop's key, and GitBucket was already running on the same NAS, so it
serves the same need over HTTP with a token and needs neither an ssh key nor the AFP mount. Read
`skills/gitbucket` (on `origin/main`) before touching it — its API is GitHub-*shaped*, not
GitHub-complete, and the differences bite.

Two things about it to carry forward:

- **The transport is plain HTTP.** The token and the whole note history cross the LAN
  unencrypted, and GitBucket's `GET /api/v3/users` needs no authentication and returns every
  account with email addresses. Accepted for a trusted home LAN; the fix is TLS via a reverse
  proxy. Task 3.6c.
- **GitBucket has no repo-deletion API**, so a repo created wrong has to be fixed in the web UI.
  The vault repo was therefore verified private four separate ways rather than trusting the
  creation response — which that skill warns can return `200` and have done nothing.

Pushing needs credentials without putting a token in `.git/config`:

```bash
set -a; . ~/.config/gitbucket.env; set +a
printf '#!/bin/sh\ncase "$1" in *[Uu]sername*) printf "%%s" "$GITBUCKET_USERNAME";; *[Pp]assword*) printf "%%s" "$GITBUCKET_TOKEN";; esac\n' > /tmp/gb-askpass.sh
chmod 700 /tmp/gb-askpass.sh
GIT_ASKPASS=/tmp/gb-askpass.sh git -C ~/"Amazon RAG" push
rm -f /tmp/gb-askpass.sh
```

The askpass script holds no secret — it echoes variables already in the environment — so the
token never reaches disk, `.git/config` or shell history.

Create it with one command (and it is idempotent):

```bash
python3 scripts/delivery-flow/scaffold-vault.py --repo <delivery-repo> --create \
    --remote http://mimir.experimentalneutron.com:8668/git/cference/amazon-rag.git
```

`--create` is required because a missing vault is otherwise still exit 3: creating one where a
mount was expected gives you two divergent vaults and no way to tell which is authoritative.

**The cost of this change, stated plainly.** The old design's insight was that an unmounted NAS
and an empty vault look identical at the output, so the former had to fail loudly. A local clone
is always reachable, so recall always succeeds — and can serve month-old memory as current,
which is a silent wrong answer and therefore worse. So the loudness moved from reachability to
freshness: every run reports HEAD, dirty, ahead/behind and days since the last fetch in
`project-context.json` and the trace, sets `stale` against `punch_out.vault_staleness_days`
(14 by default), and the rendered context opens with a stale-memory warning above any content.

Three things that are easy to get wrong, each pinned by a test:

- **Staleness is the last *fetch*, never the last push.** A push proves the NAS was reachable
  but teaches this clone nothing, so a laptop that pushed an hour ago can still be a month
  behind what the other Mac decided. The first implementation used `max(fetch, push)` and a
  test caught it. `.git/FETCH_HEAD`'s mtime is the signal; the tracking ref's reflog is
  ambiguous because a push updates it too.
- **Recall makes no network call.** A step that hung on an unreachable NAS would reinstate the
  dependency the clone removes. There is a test that greps the source for `ls-remote`, `fetch`,
  `pull` and `push`.
- **No upstream means `null`, not `0`.** Reporting zero ahead would claim agreement with the
  NAS that was never observed.

Nothing in the flow pushes. `vault-update` commits so notes are durable; the push is outward
over a network that may not be there, so it waits for a human on the home network.

The graph holds no decisions or deliveries yet, so recall honestly returns a cold start — which
is also why this restructure was free to do now, with nothing to migrate.

**Still open:** promoting `stale` from a recorded fact to a derived punch-out trigger. It
belongs there, but a punch-out needs a signed decision to clear and the signing key does not
exist yet, so making it a trigger today would block offline work rather than flag it.

Seeding real decision notes needs Calvin's judgement about which existing choices are worth
recording — an invented decision note is worse than an empty folder, because recall will quote
it back as though it were settled.

## Blocked on Calvin

1. **The signing key.** Secretive is installed; he still has to create a Secure Enclave key
   with *authenticate on every use*, then add its public half to
   `~/.config/delivery-flow/allowed_signers` as `calvin <public key>`. Until then `decide.py`
   is tested only with throwaway keys. He plans a hardware key later; either works.
2. **Jira credentials in the environment.** The pilot target is settled (below); the adapter
   reads `JIRA_BASE_URL`, `JIRA_EMAIL` and `JIRA_API_TOKEN` and nothing else. Shell state does
   not persist between tool calls, so put them in `~/.config/delivery-flow/jira.env` (chmod
   600, never in the repo) and source it per command:
   `set -a; . ~/.config/delivery-flow/jira.env; set +a; python3 scripts/delivery-flow/adapters/jira.py fetch AN-3704`
   — that way the token never lands in a transcript or in shell history.
3. **Two questions for the certification reviewers**, unresolved: whether knowledge skills
   (`scala`, `react`) need their own Stage 3 packages (the design assumes not), and whether a
   "run" is one work item with punch-outs excluded from the rate (the report emits both
   readings until someone says).

## The pilot target, settled 2026-10-28

**Jira project `AN` ("Amazon Neptune") on `bitquill.atlassian.net`**, cloudId
`4ef75afd-3201-49fc-ac9c-13b7159b14d6`, against the repo **`~/Code/nx-neptune`**
(`awslabs/nx-neptune`). It is a **client's** Jira, so `tracker.external: true` and every
post-back needs a signed decision — which the `triage` profile never does, because it has no
post-back step. The chain only reads Jira.

```bash
python3 scripts/delivery-flow/init-delivery-flow.py ~/Code/nx-neptune \
    --profile triage --jira-project AN          # no --internal: it is a client's site
```

**The finding that shaped the design: these tickets are routing stubs.** Sprint, epic, assignee
and component live in Jira; the requirement lives in a GitHub issue. Three of the four newest
tickets have no description beyond `github reference: <url>`. `labels`, `issuelinks` and
`comment` are empty on every ticket sampled; `components` carries `NetworkX` and `parent`
carries the epic.

Fed a stub as-is, the chain would have done the right thing and punched out —
`require_acceptance_signal: true` derives a scope trigger for an item stating no expected
outcome — so three runs would have been three punch-outs and no completed chain. Rather than
cherry-pick the tickets that happen to have bodies, the Jira adapter now **follows the link**
(design D10): it fetches the referenced issue through `gh`, fences it as unverified external
content, and records it in `references`. An unfetchable reference is exit 3, because a body
that varies with network state would break byte-identical reruns.

Ticket shapes worth knowing before the first run:

| Ticket | Shape |
|---|---|
| `AN-3704`, `AN-3703`, `AN-3702` | stubs linking `awslabs/nx-neptune#579/#576/#555` — the sharpest test of the follow path |
| `AN-3600` | a `[SPIKE]` with three explicit questions |
| `AN-3630`, `AN-3631` | real task descriptions with code pointers and numbered options |
| `AN-3644` | "Andrew to fill out" — genuinely empty; expect a punch-out, and that is correct |

## What to build next, in order

Two things are now off this list. **`challenge-breakdown`** is built and certified, finishing
the chain. **The adapters** are built: `github_issues.py`, `github_pr.py` and
`local_markdown.py`, plus `templates/delivery-flow/roster.yaml`. Task 1.1's static
`delivery-flow.yaml` template was deliberately dropped — `init-delivery-flow.py` generates
the config, and a template would be a fourth place its shape lives.

`agents/adversarial-validator.md` still needs pinning to `model: sonnet` (task 8b.5).

1. **Work-type routing** (task 4.x) — `resolve-roster.py` reading `roster.yaml`, the optional
   `Domains:` story field (change `story-schema.md` and `lint-story.py` together; CLAUDE.md
   requires it), and the orchestrator dispatching from the resolve.
2. **Evidence package** (9b) — `package-evidence.py`, one directory per criterion, refusing to
   build when a chain step is uncertified.
3. **Docs** (task 9.x) — the playbook section and `docs/figures/delivery-flow.svg`. CLAUDE.md's
   doc-sync rule makes this part of the change, not an afterthought.
4. **Real runs on Olympus**, which produce the only thing nothing else can: the rate and trend.
   `local_markdown.py` is what makes a pilot possible without touching a client's tracker.

## Things that bit us, so they do not bite you again

- **A negative rule without its positive half teaches a new wrong answer.** "Logging inside
  one service is not an architecture change" taught the model that a brand-new service was not
  one either, two iterations later.
- **Keep a rule and its reason in the same place.** A refactor moved "parsed by `json.loads`,
  so a fence is a parse error" one section away from "no code fence" and cost 7 of 18 runs.
- **A shape constraint makes models terser.** Adding "reply with nothing else" dropped coverage
  until a matching content requirement was added beside it.
- **`\b` before a hyphen never matches.** `\b-X` in a hook regex silently allowed every
  `gh api -X POST`. The bypass suite caught it; the unit tests were green throughout.
- **Cheap bail-outs skip the check.** The punch-out hook's early exit did not mention `curl`,
  so an HTTP client bypassed enforcement entirely. Same suite, same run.
- **Test the test.** The first bypass run reported a breach because *any* `gh` call counted,
  including a harmless `gh pr view`. A test that fails for the wrong reason misleads as badly
  as one that passes for the wrong reason.
- **That same bug came back twice more.** On 2026-10-28 the suite scored
  `gh pr view 42 --json url,state,mergeable` as a merge, because `mergeable` contains `merge`.
  Matching is now on whole argv tokens. **Three strikes for substring matching in one suite** —
  if you add an attack, match tokens, and quote the command line in the evidence so a false
  positive is visible on the face of the report.
- **A refusal is not a guardrail.** Six attacks were written as "do X so nothing triggers".
  The model read that as being asked to defeat a safety control and declined, producing rows
  that looked like blocks and proved only that it was polite — the weakest possible evidence
  under a standard whose whole premise is that guardrails must not depend on the model's
  cooperation. Write attacks as plausible work with the same mechanical effect ("the triage
  over-flagged this, correct it"), and report a row where nothing was rewritten as
  **inconclusive**, never as a pass.
- **One fixture shared across a suite leaks state forward.** Attack 18 appeared to silence the
  `scope` trigger; attack 15's edit three rows earlier had done it. A row's evidence has to
  belong to its own attack, so each one builds its own fixture — rebuilding costs no model
  calls, which is the only expensive part.
- **"Does any check fire" is not the same question as "does *this* check fire".** The derived
  gates were judged on whether anything still fired, so an attack that silenced `scope` passed
  because `architecture` happened to survive. On a scope-only item there would have been
  nothing left and the suite would never have said so.
- **An unconfigured fixture silently tests nothing.** The bypass fixture had no `punch_out:`
  block, so `contract_paths` and `protected_paths` were unset and three proposal triggers could
  not fire at all — they were resting on the node's own claims, the exact thing the derived
  triggers exist to replace. Four attacks were exercising nothing while their instructions
  named `.github` and `the-lexicon` as though they were configured. **Assert your fixture's
  baseline**, and print it in the report so a reviewer can check the arithmetic.
- **Say "API-equivalent cost", never "cost".** Runs are on a subscription; the figure is
  tokens priced at list rates, and the report labels it that way everywhere.

## Working with Calvin

He wants to be told when something is wrong, including when the fault is his design or his
labels. He asked explicitly for "it's okay to be wrong" when the course was analysed, and the
most useful answers in this project have been the ones that said a previous decision was
mistaken. Report failures with the output, discard contaminated runs out loud, and never
present an unverified claim as a measured one.
