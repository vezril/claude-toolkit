# Tasks: new-python-project

## 1. Scaffold skills

- [ ] 1.1 `skills/python-uv-build/` — SKILL.md + scaffold.sh (pyproject.toml with ruff/mypy/pytest config + dev group, .python-version 3.12, .gitignore, multi-stage uv Dockerfile running `python -m <pkg>`); pkg parameter with scala-consistent derivation; README-enrichment section; overwrite refusal on pyproject.toml
- [ ] 1.2 `skills/python-package/` — SKILL.md + scaffold.sh (`src/<pkg>/__init__.py`, typed `greeting.py`, `__main__.py`); production-only territory
- [ ] 1.3 `skills/python-tests/` — SKILL.md + scaffold.sh (`tests/test_greeting.py`); test-only territory; package read from `src/`
- [ ] 1.4 `skills/github-actions-python-ci/` — SKILL.md + scaffold.sh (setup-uv composite action SHA-pinned, ci.yml with lint/format/types/tests/gitleaks, dev.yml + release.yml with the secrets-absent publish skip and the scala release gates)

## 2. Orchestration workflow

- [ ] 2.1 `workflows/new-python-project.js` — args contract (name/visibility/dockerhub required, pkg/auto optional, stringified-args tolerant), phases per design, uv green gate (uv.lock ships with the PR), single gated PR, development post-merge
- [ ] 2.2 Install to `~/.claude/workflows/`

## 3. Local verification (before anything outward)

- [ ] 3.1 Scratch run of the four scripts in an empty dir: `uv sync` + full gate green; `python -m <pkg>` prints the greeting; overwrite/territory/missing-prerequisite guards fire
- [ ] 3.2 Red-path: sabotage `greeting.py` in scratch, confirm the gate exits non-zero
- [ ] 3.3 Strict-YAML check across all SKILL.md frontmatters; `node --check` the workflow

## 4. Docs + ship

- [ ] 4.1 README: *Python project scaffolding* group + Workflows entry
- [ ] 4.2 Ship via git-ship (gated)

## 5. End-to-end verification (needs the human)

- [ ] 5.1 Full gated run against a throwaway repo (`dockerhub: false`): bare bootstrap (openspec config rides the PR — first live exercise of the OpenSpec phase), scaffold, green gate, PR + `awaiting-merge-approval`; approve, merge, `development` created; ci.yml + dev.yml green with publish skipped; human deletes the throwaway afterwards
