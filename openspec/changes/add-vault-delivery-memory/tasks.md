## 0. Verify assumptions

- [x] 0.1 Confirm the target vault's current contents and that it has no graph root, so the scaffold is additive rather than a migration
- [x] 0.2 Confirm `Atlas/RAG` belongs to a different vault and nothing in this one collides
- [x] 0.3 Re-read `extend-vault-graphrag-projects`'s recall spec and confirm the scoring is fully determined by it (it is: that is the basis for D1)

## 1. The contract

- [x] 1.1 `schemas/project-context.schema.json`: `item`, `project`, `mode`, `matched`, `decisions[]`, `deliveries[]`, `lessons[]`, `patterns[]`, `coverage{entities, keywords, domains, scanned{}, dropped, superseded_skipped}`; `produced_by: project-memory`, `consumed_by: [breakdown, propose]`
- [x] 1.2 Counts in the schema for each result list, so the sentinel's claim is testable

## 2. Recall as a script

- [x] 2.1 `scripts/delivery-flow/vault-recall.py`: stdlib frontmatter parsing, folder scan, the specified scoring, threshold, date tie-break and caps
- [x] 2.2 Keyword extraction per D6, with the stop list in the module and reported in coverage
- [x] 2.3 Accepted-only rule, with superseded decisions redirected into coverage naming their replacement
- [x] 2.4 Both call points: `--mode solutioning` and `--mode implementation --story <id>`, the latter writing a suffixed artifact
- [x] 2.5 Emit `project-context.json` plus its sentinel, and `project-context.md` within the 80-line cap
- [x] 2.6 Reachability check before scanning: exit 3 and no artifact when unreachable, exit 0 with `matched: false` when merely empty, exit 2 for an unimplemented backend
- [x] 2.9 **Revised (D3a):** the vault is a local git clone with the NAS hosting the canonical bare repo, because reading an AFP mount stopped the flow dead whenever the laptop left the home network. Recall reports the clone's sync state (`head`, `dirty`, `upstream`, `ahead`/`behind`, `last_sync`, `days_since_sync`) and sets `stale` against `punch_out.vault_staleness_days`; the markdown opens with a stale warning. Staleness is the last **fetch**, not the last push — a test caught the first implementation taking `max(fetch, push)`. No network call in recall, with a test asserting it. 13 new tests
- [x] 2.7 `tests/delivery-flow/test_vault_recall.py` with the synthetic mini-vault from the parent change's 3.1 (one project, two services, accepted and superseded decisions, three deliveries, lessons with domains, a cross-project decoy), asserting **exact scores** and membership rather than a pass rate
- [x] 2.8 Tests for the unmounted path, the file-where-a-directory-should-be case, and byte-identical reruns

## 3. The scaffold

- [x] 3.1 `scripts/delivery-flow/scaffold-vault.py`: graph root, the five folders, one `project` entity for the binding, the note templates
- [x] 3.2 Additive and idempotent: never overwrite, report skips, refuse paths that do not resolve inside `vault.path`
- [x] 3.3 Tests including the path-escape refusal and the second-run no-op
- [x] 3.4 Scaffolded `/Volumes/Private/Amazon RAG` with `graph_root: Atlas/RAG`, `binding: amazon` — 13 additions, the three existing notes verified byte-identical by checksum, and Obsidian indexed the new structure live one second later. **Superseded by 3.5:** that NAS directory is no longer what recall reads
- [x] 3.5 `--create`, `--git` and `--remote` on the scaffold: create the local clone when absent (a missing vault is otherwise still exit 3, because creating one where a mount was expected yields two divergent vaults), `git init` with a `.gitignore` for Obsidian's volatile state so `dirty` reports notes rather than pane movements, an initial commit, and `origin` set without ever pushing. An existing `origin` that disagrees is reported, not replaced
- [x] 3.6 Created the real clone at `~/Obsidian/Amazon RAG` (git work tree on `main`, scaffold committed) and pushed it. **The remote is GitBucket on mimir, not an ssh bare repo** — `http://mimir.experimentalneutron.com:8668/git/cference/amazon-rag.git`, created `private: true` via `POST /api/v3/user/repos`. ssh to mimir refused the laptop's key, and GitBucket was already running on the same box, so it answered the same need over HTTP with a token. Still NAS-only: it is Calvin's hardware, which is what the earlier decision required
- [x] 3.6a Verified the repo is genuinely private four ways, not just by the creation response (which the GitBucket skill warns can echo success and do nothing): authenticated `private: true`, unauthenticated API `401`, unauthenticated clone refused, and absent from `GET /api/v3/repositories`
- [x] 3.6b Recall against the real vault reports `upstream origin/main`, `ahead 0`, `behind 0`, `days_since_sync 0`, `stale false` and **no warning notes**. The push-then-fetch sequence also demonstrated the fetch/push distinction in practice: after the push alone, `last_sync` was still null with "no record of ever fetching", because a push sends without learning
- [ ] 3.6c **Residual: the transport is plain HTTP.** The token and the full note history cross the LAN unencrypted, and GitBucket's `GET /api/v3/users` needs no auth and returns every account with email addresses. Accepted deliberately for a trusted home LAN; the fix is a reverse proxy with TLS (see the `gitbucket` and `nginx` skills). Revisit before the vault holds anything a LAN observer should not see
- [x] 3.6d **Resolved differently and better:** Calvin moved the real vault to `~/Amazon RAG`, so rather than copying three files off the NAS share, the git metadata moved *into* the real vault. The scaffolded `Atlas/RAG/` files were byte-identical to the ones already committed, so commit `d403bff` adds the real notes (`AWS Git Standards.md`, `Isengard.md`, `Welcome.md`, the daily-notes template) and the Obsidian settings alongside them, preserving history and the GitBucket tracking. 18 files tracked; `.trash/`, `workspace.json` and `.DS_Store` stay ignored so a dirty tree means uncommitted notes
- [ ] 3.6e Delete the now-stray scaffold copy at `~/Obsidian/Amazon RAG` once Calvin confirms. Its `.git` and `.gitignore` were moved out, so what remains is a duplicate of the scaffold with no history — harmless but confusing. **Not deleted unasked**

## 4. The schema deltas from the parent change

- [x] 4.1 `skills/vault-graphrag/references/schema.md`: `project` entity type, optional `project` field, layout gaining `decisions/` and `deliveries/`
- [x] 4.2 The `decision` note type: frontmatter contract, supersede workflow, refs rule, minting rules, worked example
- [x] 4.3 The `delivery` note type: frontmatter contract, status vocabulary, collision rule, worked example
- [x] 4.4 Extend the link vocabulary table with `project`, `decisions`, `superseded_by`, delivery `services`/`patterns`
- [x] 4.5 `skills/vault-graphrag/references/delivery-recall.md` documenting the algorithm as implemented, naming the script as normative
- [x] 4.6 `skills/vault-graphrag/SKILL.md`: operations list, argument hint, description triggers; incident sections unchanged
- [x] 4.7 Confirm `references/recall.md` (incident recall) has no diff

## 5. The update node

- [x] 5.1 `skills/delivery-flow/references/vault-update.md`: what it upserts, the one-line field rule, the stubs it may mint, and the no-invented-decisions rule
- [x] 5.2 Add `vault-update` to `allow_uncertified` alongside `propose`, and document why
- [x] 5.3 Confirmed, after fixing the `certified: None` bug in `trace-step.py` — see `add-openspec-proposal-step` task 6.3

## 6. Wiring and docs

- [x] 6.1 Binding keys `vault.path`, `vault.graph_root`, `vault.backend` in the config template and `references/config.md`
- [x] 6.2 `skills/delivery-flow/SKILL.md`: the vault steps, recall as a script, the unreachable-versus-empty rule
- [x] 6.3 `references/trace.md`: what a failed recall and a cold-start recall each look like
- [x] 6.4 `docs/delivery-flow-handoff.md`: new files, test count, and the D1 disagreement stated plainly
- [x] 6.5 Ran recall against the real vault for a sample item: exit 0, honest cold-start artifact, coverage showing 0 notes scanned — and exit 3 with no artifact when the graph root was pointed at an unmounted path

## 7. Follow-up, not in this change

- [ ] 7.1 Certify `vault-update` (`prompt-edd`) — needs model runs
- [ ] 7.2 Seed real decision notes from existing Olympus ADRs or archived OpenSpec designs (parent change 5.2) — needs Calvin's judgement about which matter
- [ ] 7.3 Retune the scoring weights against real recalls, and decide whether they are policy like the punch-out ceilings
- [ ] 7.4 The `iris` backend, if Olympus's phase 2 ever needs it
