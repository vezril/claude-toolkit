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
- **Bypass suite: 23/23 blocked**, 0 breached, 0 inconclusive. A 24th attack
  (`write-decision-absolute-variable`) is now in the table but **has not been run** — the suite
  spends real API credits per attack, so the count stays 23/23 until it is.
- **Defect 12 fixed** (see below), **open decision 3 ruled** (see below), **open decision 1
  narrowed** and **open decision 2 found already closed**. All in the working tree, not yet
  committed.
- **14 commits**, 466 tests green (`/tmp/dfvenv/bin/pytest tests/delivery-flow`: 466 passed,
  1 skipped, 90 subtests). Note for the next session: neither `pytest` nor `uv` is on PATH and
  mise has no global python pinned, so the suite needs a venv built from
  `~/.local/share/mise/installs/python/3.12.15/bin/python3` before it will run at all.

## Open decisions

1. ~~`contract_paths` is the whole package.~~ **Narrowed — and the recommendation turned out to
   be nearly a no-op.** `~/Code/nx-neptune/.delivery-flow.yaml` now lists the surface callers
   can reach instead of the blanket `nx_neptune`: the modules `__init__.py` re-exports, plus the
   two entry points `pyproject.toml` declares (`nx_neptune.interface:BackendInterface` and
   `nx_plugin:get_info`). The 12 modules excluded are the ones nothing outside the package
   imports — the AWS client internals, `utils/`, `validators.py`. Uncommitted in that repo, on
   branch `cference/session-auto-stop`.

   **The premise was wrong, though.** `nx_neptune/__init__.py` re-exports from nearly every
   top-level module, so the exported surface *is* most of the package — 24 of its 36 modules.
   Both of AN-3630's punch-outs would still fire, because `session_manager.py` and
   `instance_management.py` are each exported. `nx_neptune` was never really a misconfiguration;
   the real problem is one a path list cannot express. See new open decision 4.
2. ~~Repo registry for the edge hook.~~ **Done — built, and defect 3 with it.**
   `init-delivery-flow.py` records an opted-in repo; `hooks/check-edge.py` reads the list. The
   registered repos are extra **bases** a relative artifact fragment may belong to, not extra
   trees to scan — scanning the registry broke the hook's inertness in unrelated sessions,
   which is what commit 303008c reverted. Covered both ways:
   `test_edges.py::test_the_registry_catches_the_write_no_parsing_could` and
   `::test_an_unregistered_repo_is_still_left_alone`, plus a new bypass attack
   (`write-decision-absolute-variable`) that drives the same shape with a model choosing the
   syntax instead of a crafted payload.
3. ~~`project-context` consumer mismatch.~~ **Ruled: the schema overstated.** `breakdown` is
   removed from `consumed_by`. Adding the input instead would have un-certified breakdown — its
   certified prompt (`prompt_v6`) never mentions project context. `consumed_by` is not inert
   documentation: `hooks/check-edge.py` loops it and runs each named consumer's input contract,
   so the overstated entry was changing which checks ran at that edge.

   The consequence, stated rather than hidden: on the `triage` profile `project-memory` now has
   **no downstream consumer at all**. Recall still earns its place by writing the vault trail the
   next run reads, but nothing in that profile's chain reads `project-context.json`.
   `tests/delivery-flow/test_schema_consumers.py` cross-checks every schema's `consumed_by`
   against the registry's `inputs`, so the two cannot drift apart again — for the consumers the
   registry can see. `steps.yaml` holds the *certified* steps only, so deterministic ones
   (`intake`, `brief`, `report`), uncertified ones (`propose`, `implementation`) and non-step
   readers (`check-edge`, the dev pair) declare no `inputs` to compare against and are left
   alone rather than asserted about with a registry that cannot see them.

4. **A path list cannot say what a breaking change is.** Open decision 1 narrowed
   `contract_paths` as far as paths allow and it is still coarse: any edit to an exported module
   fires the breaking and architecture triggers, including one that only rewrites a function
   body. Either accept the false-positive rate and state it in the report, or derive the
   breaking trigger from the *public API* — exported names and their signatures — rather than
   from file paths. The second is real work and should not start before a clean run says how
   often this actually fires.
5. **Three registry steps declare an input their schema does not claim.** `breakdown` and
   `challenge-breakdown` both read `item.json`; `challenge-breakdown` reads `triage.json`.
   Unlike decision 3 these are *under*-declarations, so no check runs that shouldn't — but no
   input contract is enforced for them either. Closing it means deciding which fields those
   certified steps require, which would start failing edges in a chain whose evals were run
   without those contracts. Pinned at exactly three by
   `test_schema_consumers.py::test_the_registry_declares_inputs_the_schemas_do_not_claim_as_consumers`,
   which fails if it grows.
6. **`certify-sdlc-pipeline` is 5/58 tasks** and was written before the D10 stories seam landed
   (ea29f43). Worth checking whether the task list still describes the plan being followed.

## Defects found by real runs, 2026-10-28

Ten, every one invisible from a toolkit checkout. All fixed and committed except where noted.

1. Edge check skipped a relative Bash write after a `cd` (payload `cwd` is the session's).
2. Edge check skipped a path built from a shell variable (early bail-out grepped for
   `delivery/`). Detection is now by content — comparing bytes to the sha the trace recorded.
3. **Fixed:** absolute path in a shell variable, no `cd`, cwd not a delivery repo. The repo
   registry closed it — see open decision 2.
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

## Defect 12 (fixed): the breaking derivation attributed the whole branch diff to one item

Found on the AN-3704 re-run, 2026-10-29. The derivation reads `git diff main...HEAD` and
matches it against `punch_out.contract_paths`. The branch `cference/session-auto-stop` holds
four commits implementing **AN-3630's** feature, touching `nx_neptune/session_manager.py`,
`instance_management.py` and `clients/neptune_constants.py`. AN-3704 is a
`proxy/docker-compose.yml` and `proxy/Makefile` bug that touches none of them — yet it raised a
breaking-change punch-out citing those three files.

So two items worked on one branch each inherit the other's changes, and the punch-out's
evidence names files the item never asked to change. A gate whose evidence belongs to a
different work item is worse than no gate: it reads as authoritative and is wrong.

**Fixed: option 2 — narrow by attribution, not by path.** `item_changed_files` in
`check-punch-out.py` now reads the commits whose message names the item key, plus the
uncommitted working tree, and nothing else from the branch.

Why not option 1 (scope to the proposal's `tasks[].files`): it would make the plan
unfalsifiable. The realized-diff check exists precisely to catch a contract path the proposal
never declared, and it cannot do that if the plan defines where it looks. Option 3 was the
smallest change but the strongest constraint on how work actually happens, so it stayed a
non-goal.

Three things the fix carries beyond the rename:

- The evidence now names **whose** diff it is ("the diff attributed to AN-3704 (2 commits
  naming AN-3704 and the uncommitted working tree) touches …"). Defect 12's punch-out looked
  identical to a true one; the provenance is what lets a reader tell them apart.
- Path matching moved to `triggers.under`, a path-*segment* test shared with the planned-path
  gate — so `nx_neptune` no longer matches `nx_neptune_extra/foo.py`, and a prefix cannot match
  the plan but miss the diff that implemented it.
- Untracked files are included (`git ls-files --others --exclude-standard`). `git diff HEAD`
  omits them, so a new file under a protected path, not yet committed, was invisible to this
  gate — the one shape where it is needed before anyone can review anything.

**Residual gap, counted rather than papered over:** a commit naming no item key is attributed to
nobody and its paths go unchecked. That is a missed gate rather than a misattributed one, which
is the safer direction, but it is real — so `diff_attribution.commits_unattributed` is in the
`--json` output and the script says so on stderr.

Related: the same run shows why `contract_paths: [nx_neptune, ...]` is too broad. It has been
narrowed (open decision 1), but narrowing by path does not reach the real problem — see new open
decision 4. A punch-out rate needs that one settled before it means anything.

## Stage 4 submission

Not this week. Criterion 4 wants a rate over real runs with a weekly trend, and there are zero
completed runs. Run one found five defects, run two found five more, and fixing run two's turned
up two more in the code immediately around them (the untracked-file and prefix-matching bugs
above) — the curve has not flattened, so a rate computed now measures a pipeline still changing
underneath it.

The one free thing worth doing: **ask the reviewer whether criterion 4 needs a trend or just a
rate with a stated denominator.** That answer is the difference between a one-week and a
four-week submission. **Not sent yet** — it needs Calvin, and it is the highest-leverage item on
this page because it is the only one that can shrink the remaining work rather than do it.

## What a clean run still needs

Nothing on the critical path is now blocked by a decision. The next action is one run driven
from a session started **inside** the delivery repo, which is what produces the first
trustworthy trace. `artifacts.root` means the artifacts can live in the vault while the session
sits in the project, which is exactly what the two discarded runs needed and did not have.
