# delivery-flow: handoff

For a Claude instance picking this work up cold. Read this first, then
`openspec/changes/add-delivery-flow/` (proposal, design, specs, tasks) for the full
specification. Last updated 2026-10-27.

## What this is

A workflow that takes one work item from a tracker to a merged, deployed change, built so it
can be certified at **Stage 4 of Improving's AI Maturity Model**. The certification is
Calvin's; the workflow is general and lives in the public `claude-toolkit` plugin.

The authority on what Stage 4 requires is Improving's own course deck, *AI Governance &
Guardrails (Stage 3 → Stage 4, Q3 2026)*, in Calvin's iCloud at
`Documents/Library/1xx - Personal/120 - Work and Career/121 - Employer and Clients/Improving/Stage 4/`.
**Read it before making design calls** — an earlier version of this design was wrong in three
ways until it was read, and the corrections are recorded in `design.md` (D7, D12–D15).

Its model in one paragraph: a **node** is a non-deterministic LLM step, each independently
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
skills/delivery-flow/
  SKILL.md                            the orchestrator: routing table, rules, how a step runs
  steps.yaml                          the step registry: certification evidence per step
  references/                         config.md, adapters.md, roster.md, trace.md
  references/triage.md                CERTIFIED node prompt (byte-identical to its eval version)
  references/breakdown.md             CERTIFIED node prompt
schemas/                              item, triage, breakdown, challenge, sentinel
scripts/delivery-flow/
  common.py                           repo/config/schema/pricing/usage/signature helpers
  flow-status.py                      the router: where an item is, what runs next
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
tests/delivery-flow/                  64 tests across 4 suites
tests/delivery-flow/bypass/           the bypass suite and its report
```

## Run everything

```bash
cd ~/Code/claude-toolkit
for t in tests/delivery-flow/test_*.py; do python3 "$t"; done     # 64 tests
python3 scripts/delivery-flow/check-certification.py --all        # every registered step
python3 tests/delivery-flow/bypass/run-bypass.py --model sonnet   # 15 attacks, ~8 min, costs usage
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
| `pr-description` | Haiku | 89/90, but terminal prose with no edge — **not** chain evidence |

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

## Blocked on Calvin

1. **The signing key.** Secretive is installed; he still has to create a Secure Enclave key
   with *authenticate on every use*, then add its public half to
   `~/.config/delivery-flow/allowed_signers` as `calvin <public key>`. Until then `decide.py`
   is tested only with throwaway keys. He plans a hardware key later; either works.
2. **The pilot repo and cadence.** `demeter-service` is the suggested pilot (the only Olympus
   repo with required status checks and mutation testing). He runs Olympus work roughly daily;
   the end-to-end trend needs 4–6 weeks of real items.
3. **Two questions for the certification reviewers**, unresolved: whether knowledge skills
   (`scala`, `react`) need their own Stage 3 packages (the design assumes not), and whether a
   "run" is one work item with punch-outs excluded from the rate (the report emits both
   readings until someone says).

## What to build next, in order

1. **`challenge-breakdown`** — the third chain node, finishing the chain. Adversarial
   validator in a fresh context, structured verdict, harness routing (REFUTED reruns the
   producing step). Certify it like the others. `agents/adversarial-validator.md` still needs
   pinning to `model: sonnet` (task 8b.5).
2. **Adapters and templates** (tasks 1.1, 1.2, 2.x) — `github_issues.py`, `github_pr.py`,
   `local_markdown.py`, plus `.delivery-flow.yaml` and `roster.yaml` templates. Scripts, never
   LLM calls, and they refuse while a punch-out is open. Nothing can run end to end until
   these exist.
3. **Work-type routing** (task 4.x) — `resolve-roster.py`, the optional `Domains:` story field
   (change `story-schema.md` and `lint-story.py` together; CLAUDE.md requires it).
4. **Evidence package** (9b) — `package-evidence.py`, one directory per criterion, refusing to
   build when a chain step is uncertified.
5. **Docs** (task 9.x) — the playbook section and `docs/figures/delivery-flow.svg`. CLAUDE.md's
   doc-sync rule makes this part of the change, not an afterthought.
6. **Real runs on Olympus**, which produce the only thing nothing else can: the rate and trend.

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
- **Say "API-equivalent cost", never "cost".** Runs are on a subscription; the figure is
  tokens priced at list rates, and the report labels it that way everywhere.

## Working with Calvin

He wants to be told when something is wrong, including when the fault is his design or his
labels. He asked explicitly for "it's okay to be wrong" when the course was analysed, and the
most useful answers in this project have been the ones that said a previous decision was
mistaken. Report failures with the output, discard contaminated runs out loud, and never
present an unverified claim as a measured one.
