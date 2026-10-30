# TODO

Running tracker for this repo. Ordered by what blocks what, not by size.

Rules for keeping it honest:

- **Blocked means blocked.** If an item cannot start until another finishes, say which.
- **A question for a human is an item.** "Ask the reviewer X" is work, and it is often the
  cheapest work with the highest leverage.
- **Don't record a score that wasn't measured.** EDD rows go in `README.md` only from a results
  file; see `evals/README.md`.

---

## 1. Critical path — the Stage 4 certification

Everything in §2 is gated on this. Four of five criteria are built
(`docs/delivery-flow-handoff.md`); the fifth needs runs, not code.

- [ ] **Produce the real end-to-end runs for `delivery-flow`.** Criterion 4 (end-to-end success
      rate) is the only outstanding one. The `triage` profile exists so a run can reach a
      terminus through certified steps alone; `add-jira-triage-profile` points it at real Jira
      tickets (project `AN`, bitquill). Evals guard regressions — **only real runs produce the
      rate.**
- [ ] **Certify the two remaining delivery-flow nodes.** Both are registered as needing model
      runs:
  - [ ] `propose` — `add-openspec-proposal-step` task 8.1 (`prompt-edd` suite, ≥3 criteria,
        load-bearing map, iteration log, haiku-first escalation evidence)
  - [ ] `vault-update` — `add-vault-delivery-memory` task 7.1
- [ ] **Submit `delivery-flow`.**
- [ ] **Ask the reviewer the composition question.** *Is a pipeline of certified 2–3 node
      segments, joined by deterministic edges and human gates, certifiable segment by segment?*
      This reading is ours, not the deck's. It is Open Question 1 of `certify-sdlc-pipeline` and
      it invalidates most of §2 if the answer is no. Costs one conversation — ask it alongside
      the submission.
- [ ] **Ask Open Question 2:** do knowledge skills loaded as context need their own
      certification? `workflow-certification` records this as unconfirmed. sdlc loads far more of
      them than delivery-flow, so the answer changes §2's cost materially.

---

## 2. The first large workflow, still unfinished — `sdlc-orchestrator`

The sdlc pipeline was the first large workflow built here and it is **not Stage 4 compliant**: it
fails three of five criteria and partially meets a fourth. Full assessment and plan in
`openspec/changes/certify-sdlc-pipeline/`.

**Blocked on §1** — no substrate extraction lands until the `delivery-flow` submission is
accepted. Refactoring the artifact under review, while it is under review, trades a certification
for a tidier tree.

- [ ] Section 0 gate: submission accepted, composition question answered, baseline test output
      committed
- [ ] Extract the workflow-agnostic substrate into `scripts/workflow/`; `delivery-flow` becomes
      consumer one behind re-export shims, with **zero behavioural diff**
- [ ] Generalise `check-edge.py`, `trace-step.py`, `enforce-punch-outs.py` to resolve a workflow
      descriptor instead of keying on `.delivery-flow.yaml`
- [ ] Make the story a data contract: `story.json` + schema, `story.md` rendered from it,
      `lint-story.py` rewritten as schema + semantic checks
- [ ] Register the pipeline as six segments in `skills/sdlc-orchestration/steps.yaml`, all
      uncertified except `readiness`
- [ ] Move the readiness gate from orchestrator-invoked commands onto the edge hook
- [ ] Certify the `readiness` segment: `story-planner` + readiness reviewer, 3 consecutive runs
      each, shas pinned
- [ ] Generalise the bypass suite and run it against sdlc's gates — the delivery-flow run found
      **3 real holes in 15 attacks**, so expect holes
- [ ] Docs in the same PR per `CLAUDE.md`: `docs/using-the-sdlc-dev-team.md`, the
      `readiness-gate` / `sdlc-pipeline` / `human-gates` figures, `agents/README.md`,
      `skills/sdlc-orchestration/SKILL.md`, `skills/prime/` bindings

**Independent of §1 — can land now:**

- [ ] Fix `skills/sdlc-orchestration/SKILL.md`: it says *"use a separate, **stronger** model for
      validation"*, which `workflow-certification` calls a misreading. The checker must *differ*
      from the generator; it does not mean "use the big model". One line plus the model-policy
      sentence, wrong today regardless of whether §2 ever happens.

---

## 3. In-flight OpenSpec changes

Task counts as of this writing.

| Change | Done / open | State |
|---|---|---|
| `add-delivery-flow` | 42 / 37 | The big one. Remaining work includes the human-presence signing key (0.5) and roster dispatch (4.1–4.2) |
| `add-jira-triage-profile` | 40 / 8 | Near done. Has a **known residual to raise with the reviewer** (4.6b: `proposal-scope` has no structural derivation) |
| `add-vault-delivery-memory` | 38 / 6 | Near done. **Residual: the vault transport is plain HTTP** — token and full note history cross the LAN unencrypted (3.6c) |
| `add-openspec-proposal-step` | 33 / 2 | Both remaining items are certification (8.1, 8.3) |
| `extend-vault-graphrag-projects` | 1 / 17 | **Least progressed — effectively stalled.** Adds `project` scoping and a `decision` note type that `delivery-flow` memory depends on |
| `certify-sdlc-pipeline` | 0 / 52 | New, blocked on §1 |

- [ ] Decide whether `extend-vault-graphrag-projects` is still wanted. It is 1 task in out of 17
      and `add-vault-delivery-memory` has moved ahead of it; either revive it or archive it rather
      than leaving it ambiguous.

---

## 4. EDD backlog — paused, and why

**123 of 282 scored; 159 blank.** Verify with `python3 scripts/check-edd-table.py`.

**Recommendation: stop running batches of the current shape.** Pooled across batches 4, 5 and 6
that is **30 skills for 2 gains**, at roughly 60 model runs per batch. Batch 6 scored 0 for 10,
including the Akka SDK family picked specifically because its scored siblings sit at 50–83%
baseline — my suites put the same family at 100%, which points at the suite rather than the
skill.

Three things to change before resuming (detail in `evals/_batch6/iteration-log.md`):

- [ ] **Calibrate asserts against an observed wrong answer**, not against the skill's own
      Always-apply list. Writing down the claim and checking the model restates it is close to
      unfalsifiable. `gitbucket` is the proof: I had measured the model getting those facts
      wrong on a live instance, then wrote cases it passed 3/3.
- [ ] **8–10 cases per skill, or leave the row blank.** At 1–3 cases a single flip is 33–100%
      and a tie carries almost no information.
- [ ] **Find a way to test recall under load and consistency across a long session** — the
      actual value of a reference skill, which a single-turn suite cannot see.

**159 blank is a reasonable resting state.** For most of those the honest annotation is
"untested, and a cheap test would not distinguish it from the baseline" rather than a number.

### What has actually gained, pooled across six batches

Narrow and worth remembering: unusual rails the model has no reason to hold (DSM
refuse-to-diagnose, 15 of 18 chapters), territory splits in paired scaffolds (`python-package`
+50%), calibration behaviour (`detect-ai` 25% → 100%), credential handling (`dockerhub-setup`
50% → 100%), and one recent-API case (`akka-sdk-agents` 50% → 100%).


**60 of 247 table rows scored, 187 blank — and the table is itself missing 12 skills (§4f).** The backlog is not a to-do list — a pass only pays where
the naive baseline plausibly fails. Recorded tiers reflect that, and the lessons from the first
nine passes are in each suite's `iteration-log.md`.

What the first nine taught, worth applying before picking more:

- Safety and interpretation rails tend to be **native**; procedural mechanics are not
  (`phq-9`, `gad-7`).
- The discriminator is usually **reasoning, not recommendations** (`cryptography`: right numbers,
  no rule).
- Predict badly and you build the wrong suite. Three of six Tier 2/3 predictions were wrong.
- **Check your asserts before blaming the skill** (`design-patterns` scored FFF in both arms on
  a bad assert).

### 4a. Certification-critical (these are not optional)

Nodes in a workflow being certified; an uncertified node makes the end-to-end number meaningless.

- [ ] `propose` node — delivery-flow (§1)
- [ ] `vault-update` node — delivery-flow (§1)
- [ ] `story-planner` node — sdlc readiness segment (§2)
- [ ] readiness reviewer node — sdlc readiness segment (§2)
- [ ] Strengthen `evals/cross-examine/` reasoning asserts before promoting
      `adversarial-validator` to a certified node — the suite is currently weighted toward
      output format

### 4b. Load-bearing — referenced by multiple agents, so a regression propagates

- [ ] `godot` (4 agents) · `event-storming` (4) · `game-development` (3)
- [ ] `software-design` (2) · `agentic-workflows` (2) · `modern-java` (2) · `web-development` (2)
- [ ] `network-security` (2) · `computer-networks` (2) · `network-engineering` (2) · `tcp-ip` (2)
- [ ] `game-programming-patterns` (2) · `game-production` (2) · `game-math` (2) · `ux-design` (2)
- [ ] `swiftui-performance-audit` (2) · `swift-concurrency-expert` (2)

### 4c. High-stakes — confidently wrong output causes real harm

- [ ] `secure-coding` is already 100%; the untested neighbours are the gap:
      `network-security`, `os-security`
- [ ] Legal: `canadian-human-rights-act`, `quebec-municipal-law`, `quebec-housing-rights`,
      `quebec-charter-rights`, `canadian-criminal-code`, `quebec-civil-code`,
      `canadian-registered-accounts` — same restraint shape as `personal-finance`, so
      **expect a thin delta** and test routing/refusal rather than recall
- [ ] `canadian-business-registration`

### 4d. Procedure skills — best grading ROI, deterministic asserts, no judge

Following `dockerhub-setup` (50% → 100%, fully deterministic):

- [ ] `github-new-repo` · `python-uv-build` · `python-package` · `release-macos-spm-packaging`
- [ ] `release-app-store-changelog` · `new-constellation-service` · `repo-starter-docs`
- [ ] `git-ship` is scored; `merge` and `pr-description` are done

### 4e. Deliberately deprioritised — say why, don't silently skip

- The **GCP family** (~35 skills) and **AWS family**: large and untested, but reference material
  where the baseline scores well. The `finch` run showed Sonnet knows mainstream cloud docs
  cold — low expected delta, high token cost.
- `gitbucket`: largest untested skill, but hand-verified against a live 4.48.0 instance, so an
  eval would mostly re-measure what is already proven.
- The **Akka family** is largely scored already.

### 4f. The table is now in sync, and checked

**Fixed.** `skills/` and the EDD table both hold **282** entries, verified by
`python3 scripts/check-edd-table.py`, which exits non-zero on a directory with no row, a row
with no directory, or a duplicate.

What the drift was hiding: 12 directories had no row — including `pr-description`, which already
had a working suite and a full iteration log (recorded now as 93% → 100%, haiku tier) — and one
row, `webui-quickfix-demo`, had no directory. **The backlog figure was wrong in both directions**,
and quoting it from memory rather than counting made it worse across several batches.

- [x] Add the 12 missing rows; drop the phantom one
- [x] Add `scripts/check-edd-table.py` and reference it from the table preamble
- [ ] Run the check in CI, so this cannot drift again unnoticed
- [ ] Consider generating the table outright; 282 hand-maintained rows will drift again

**Current honest figure: 113 scored, 169 blank.** The blank count went *up* after the fix,
because the table had been undercounting.


### 4g. Eval infrastructure

- [ ] **Re-enable the `skill-evals` workflow** — it is `disabled_manually`, so none of the nine
      suites added so far has ever run in CI, and every `anthropic:claude-agent-sdk` arm is
      unexecuted. The September run failed, so the workflow may need its own fix first.
- [ ] Needs an `ANTHROPIC_API_KEY` repo secret for CI
- [ ] Rename `evals/cross-examine/` or give the skill its own suite — it is named for a skill but
      binds `agent: agents/adversarial-validator.md`, which is a bookkeeping trap
- [ ] Widen the 2-case suites before anyone leans on their numbers: `personal-finance`,
      `game-design` (each log has a "what a real suite would test instead" section)
- [ ] `personal-finance` measured 100% → 100% and is recorded as **no result**; either widen the
      suite or accept the skill is untested

---

## 5. Loose ends

- [ ] **GitBucket NAS: unauthenticated `GET /api/v3/users` returns every account with email
      addresses.** No GitBucket setting controls it — needs a VPN or authenticating proxy.
      Confirm whether port 8668 is reachable from outside the LAN.
- [ ] Delete `cference/gitbucket-api-probe` on the NAS (web UI → Settings → Danger Zone).
      30 issues, 2 labels, a comment. GitBucket has no repo-deletion endpoint.
- [ ] `~/.config/gitbucket.env` is mode `644`; `chmod 600`.
- [ ] `add-vault-delivery-memory` 3.6e: delete the stray scaffold at `~/Obsidian/Amazon RAG`
      once confirmed.
