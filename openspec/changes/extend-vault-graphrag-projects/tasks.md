## 0. Inputs

- [x] 0.1 Read Olympus's answer to question 8.2 (`iris-service`): phase 1 is read-only with no project notes; folded into `design.md` D7 (filesystem default, Iris backend deferred)
- [ ] 0.2 Inventory the current graph root (`Atlas/RAG`) to confirm no existing `decisions/` or `deliveries/` folders or conflicting basenames

## 1. Schema reference

- [ ] 1.1 Update `skills/vault-graphrag/references/schema.md`: `project` entity type; optional `project` field on incident, lesson and service/component entities; optional `domains` on lessons; layout block with `decisions/` and `deliveries/`
- [ ] 1.2 Add the `decision` type section: frontmatter contract, supersede workflow, refs rule, minting rules, worked example
- [ ] 1.3 Add the `delivery` type section: frontmatter contract, status vocabulary, collision rule (`<KEY> (delivery)` plus aliases), worked example
- [ ] 1.4 Extend the link vocabulary table with the new link fields (`project`, `decisions`, `superseded_by`, delivery `services`/`patterns`)

## 2. Recall and update operations

- [ ] 2.1 Write `skills/vault-graphrag/references/delivery-recall.md`: inputs, both call points, candidate sets, scoring, threshold and caps, accepted-only rule, output format, coverage and empty-result rules, "facts not advice"
- [ ] 2.2 Add the delivery update operation to `skills/vault-graphrag/SKILL.md` (upsert by key, entity stubs, decision linking, mint-only-from-accepted-design rule, receipt)
- [ ] 2.3 Update `SKILL.md`'s model paragraph, operations list, argument hint (`delivery-recall`, `delivery-update`) and description triggers; keep incident sections unchanged

## 3. Eval suite

- [ ] 3.1 Build the synthetic mini-vault fixture under `evals/vault-delivery-recall/cases/`: one project, two services, accepted and superseded decisions, three deliveries, lessons with domains, one cross-project decoy
- [ ] 3.2 Write `evals/vault-delivery-recall/promptfooconfig.yaml` (keyless Agent SDK provider) with deterministic asserts: sections present, expected matches present, decoy absent, superseded decision only in coverage, ≤80 lines, no body text
- [ ] 3.3 Add an implementation-mode case asserting domain-weighted lessons outrank keyword-only ones
- [ ] 3.4 Certify delivery recall to the Stage 3 bar via `prompt-edd`: naive baseline, ≥2 iterations in `evals/vault-delivery-recall/iteration-log.md`, ≥3 distinct deterministic criteria, a load-bearing appendix in `delivery-recall.md`; run Haiku first, then Sonnet, and record the cheapest tier scoring ≥95% (feeds `add-delivery-flow`'s `steps.yaml` entry and `prompt_sha256`)

## 4. Backward compatibility

- [ ] 4.1 Re-run the private repo's `evals/vault-recall` and `evals/vault-update` suites against the updated skill with no config or fixture edits; record pass results in the PR
- [ ] 4.2 Confirm `recall.md` (incident recall) has no diff

## 5. Verification

- [ ] 5.1 `openspec validate extend-vault-graphrag-projects` green
- [ ] 5.1a Add `vault.backend` (`filesystem` default; `iris` specified, returns a clear "not implemented" error) and `scan: by-type` to the binding reference
- [ ] 5.2 Hand-create one real `project` entity (`olympus`), seeding decision notes from `codex/docs/*.md` design notes or an archived OpenSpec `design.md` (linked, not copied) and one real decision note in the vault from an existing Olympus ADR or OpenSpec design; run delivery recall for a real backlog item and check the output file by eye
