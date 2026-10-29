# delivery-flow: running status

Short, current, and overwritten each session. The full picture is in
`docs/delivery-flow-handoff.md`; this is just where things stand right now.

Last updated 2026-10-29.

## Runs: both completed ones are discarded, for the same cause

`trace-step` was briefly resolved from a repo registry instead of the session's
working directory, so every Stop event in any session was attributed to whichever
item held a `.current-step`. Both AN-3630 and AN-3704 absorbed the orchestrating
session's usage: their artifacts and edge records are sound, their token and cost
records are not. Each is renamed `DISCARDED-*` with the reason beside it.

**So the end-to-end rate and the audit trail have no clean data yet.** A run must be
driven from a session started inside the delivery repo to produce any.

## AN-3630 — artifacts sound, trace discarded

| Step | State |
|---|---|
| intake | edge ok |
| triage | edge ok — `feature` / `standard` / `backend` |
| project-memory | edge ok — cold start, 0 notes |
| breakdown | edge ok — 1 epic, 3 stories, 6 criteria |
| punch-out-1 architecture | signed `proceed` |
| punch-out-2 breaking | signed `proceed` |
| challenge-breakdown | edge ok — **SURVIVED**, 5 attacks, 0 findings |
| brief | `summary.md` rendered |
| report | `outcome.json` — completed |

Both punch-outs rested on the same evidence: `the text names a shared contract: nx_neptune`,
which is open decision 1 below. They were signed `proceed` with that reasoning recorded in the
decision notes rather than waved through silently.

## Open question: does the signing key really require presence?

Three consecutive `ssh-keygen -Y sign` calls succeeded with no prompt, after one that did
prompt. Either Secretive caches authorization for a window, or the key was created without
*Authenticate before use*. No cache setting appears in its preferences, so this is not
determinable from the shell. **Criterion 3's claim rests on this**, so it needs settling by
looking at the key in Secretive's UI before the key is cited as evidence.

## Done today

- **Signing key is real.** Secure Enclave via Secretive, prompts on every use, registered in
  `~/.config/delivery-flow/allowed_signers`. Verified strict: right identity passes, wrong
  identity fails, wrong namespace fails. Task 0.5 closed; criterion 3 no longer rests on a
  throwaway key. Env in `~/.config/delivery-flow/signing.env`.
- **Vault is live** at `~/Amazon RAG`, pushed to a private GitBucket repo on mimir
  (`cference/amazon-rag`). Recall reports `ahead 0`, `behind 0`, `stale false`.
- **Jira ingestion works** end to end against project `AN` on bitquill.
- **Bypass suite: 23/23 blocked**, 0 breached, 0 inconclusive.
- **14 commits**, 406 tests green.

## Open decisions

1. **`contract_paths`** in `~/Code/nx-neptune/.delivery-flow.yaml` is
   `[nx_neptune, nx_plugin, cloudformation-templates]`. `nx_neptune/` is the library's own
   package (36 of 158 py files), so the breaking-change and architecture triggers fire on any
   change to it — which is why both of AN-3630's punch-outs exist. Recommendation: narrow it to
   the exported surface (`nx_neptune/__init__.py` plus the public algorithms module).
2. **Repo registry for the edge hook.** A `PostToolUse` hook cannot tell which repo a shell
   command wrote to, so one write shape still escapes the edge check
   (`R=/abs; cat x > "$R/delivery/K/f.json"`). Recommendation: have `init-delivery-flow.py`
   record opted-in repos in `~/.config/delivery-flow/repos` and let the hook scan those. A
   `PreToolUse` deny rule does **not** fix it — it reads the same command text.
3. **`project-context` consumer mismatch.** `schemas/project-context.schema.json` says
   `consumed_by: [breakdown, propose]`, but `steps.yaml` lists breakdown's inputs as
   `[item.json, triage.json]`. So recall's output is currently used by nobody on the `triage`
   profile. Likely the schema overstates — breakdown's certified prompt never mentions project
   context — but it needs a ruling.

## Defects found by real runs, 2026-10-28

Ten, every one invisible from a toolkit checkout. All fixed and committed except where noted.

1. Edge check skipped a relative Bash write after a `cd` (payload `cwd` is the session's).
2. Edge check skipped a path built from a shell variable (early bail-out grepped for
   `delivery/`). Detection is now by content — comparing bytes to the sha the trace recorded.
3. **Still open:** absolute path in a shell variable, no `cd`, cwd not a delivery repo. See
   open decision 2.
4. `check-certification.py` resolved `steps.yaml` against cwd, so the certification gate could
   not run from a delivery repo — the only place it is used.
5. Recall never wrote its sentinel, so the edge rejected `project-context.json` and the flow
   stuck one step after it.
6. An empty vault blocked `propose`: its contract required `decisions` non-empty, against
   design D3's rule that a cold start is not a failure. Added `requires_present`.
7. Jira ADF smart links (`inlineCard.attrs.url`) dropped their URLs silently, defeating the
   GitHub-follow step with no error.
8. **The worst one:** the architecture derivation scanned triage's own `rationale`, so a node
   writing "a single library change with no new service" triggered the architecture gate with
   its own explanation. The guard was reading the guarded node's reasoning. Now derives from
   item + breakdown only, per the spec.
9. Brief test fixtures modelled impossible pipeline states (artifacts without sentinels, a
   proposal without its OpenSpec change directory).
10. The typed confirmation in `decide.py` is not a control: `--yes` skips it and an agent can
    pass `--yes`. The signature is the control. Worth an `invoke-decide --yes` bypass attack so
    the report says so explicitly.

## Defect 12: the breaking derivation attributes the whole branch diff to one item

Found on the AN-3704 re-run, 2026-10-29. The derivation reads `git diff main...HEAD` and
matches it against `punch_out.contract_paths`. The branch `cference/session-auto-stop` holds
four commits implementing **AN-3630's** feature, touching `nx_neptune/session_manager.py`,
`instance_management.py` and `clients/neptune_constants.py`. AN-3704 is a
`proxy/docker-compose.yml` and `proxy/Makefile` bug that touches none of them — yet it raised a
breaking-change punch-out citing those three files.

So two items worked on one branch each inherit the other's changes, and the punch-out's
evidence names files the item never asked to change. A gate whose evidence belongs to a
different work item is worse than no gate: it reads as authoritative and is wrong.

Options, none chosen yet:

1. Scope the diff to the files the item's own artifacts name (the proposal's `tasks[].files`
   where there is one, nothing before that) and derive nothing from the branch otherwise.
2. Scope the diff to commits whose message or trailer names the item key.
3. Declare one branch per item a precondition of the flow and check it, which is the smallest
   change but the strongest constraint on how work actually happens.

Related: the same run shows why `contract_paths: [nx_neptune, ...]` is too broad — see open
decision 1. Both must be settled before a punch-out rate means anything.

## Stage 4 submission

Not this week. Criterion 4 wants a rate over real runs with a weekly trend, and there are zero
completed runs. Run one found five defects, run two found five more — the curve has not
flattened, so a rate computed now measures a pipeline still changing underneath it.

The one free thing worth doing: **ask the reviewer whether criterion 4 needs a trend or just a
rate with a stated denominator.** That answer is the difference between a one-week and a
four-week submission.
