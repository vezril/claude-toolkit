# Proposal: new-python-project

## Why

The bootstrap primitives and the scala flavor exist, but starting a Python project is still manual. A `new-python-project` workflow — same shape as `new-scala-pekko-service`, reusing the bootstrap, docs, Docker Hub, and ship primitives — closes the loop: any blank Python project gets repo + protection + OpenSpec + a working uv/ruff/mypy/pytest scaffold + CI/CD in one gated PR.

## What Changes

- Three new Python scaffold skills, each with a deterministic bundled script, mirroring the scala decomposition's territory rules:
  - `python-uv-build` — pyproject.toml (uv-managed, ruff/mypy/pytest configured), `.python-version`, `.gitignore`, the optional `Dockerfile` (packaging concern), and the README enrichment step.
  - `python-package` — production sources only: `src/<pkg>/` with a pure `greeting` module and a `__main__` CLI entry point.
  - `python-tests` — test sources only: `tests/test_greeting.py`; reads the package name from `src/` rather than re-deriving.
- New `github-actions-python-ci` skill: ci.yml (ruff check + format check, mypy, pytest on PRs to `development`/`main`, gitleaks), dev.yml (`:dev` images from `development`) and release.yml (`:X.Y.Z` + `:latest` from a `vX.Y.Z` tag) with the same secrets-absent publish-skip pattern as the scala CI.
- New `new-python-project` workflow: bare bootstrap (which brings `openspec init --tools claude`) → scaffold on `feat/scaffold` (build → package → tests → `repo-starter-docs` → README enrichment → CI) → optional `dockerhub-setup` → uv green gate (`uv sync`, ruff check + format check, mypy, pytest; red ships nothing) → one gated PR via `git-ship`; `development` created from merged `main` post-approval. Args `{ name, visibility, dockerhub, auto?, pkg? }` — `visibility` and `dockerhub` required decisions.
- Reused unchanged: `new-github-project` (bare mode), `repo-starter-docs`, `dockerhub-setup`, `git-ship`, `github-branch-protection` (incl. plan-403 degrade).

## Capabilities

### New Capabilities
- `python-uv-build`: the uv build definition — pyproject.toml with dev tooling, `.python-version`, `.gitignore`, optional Dockerfile, README enrichment.
- `python-package`: production source scaffold under `src/<pkg>/`.
- `python-tests`: test scaffold under `tests/`.
- `github-actions-python-ci`: the Python CI/CD surface with graceful Docker Hub degradation.
- `new-python-project-workflow`: the orchestration — args contract, phases, gates.

### Modified Capabilities
<!-- none — the reused capabilities (new-github-project-bare-mode, dockerhub-setup, …) are consumed as specced -->

## Impact

- New: 4 skill folders under `skills/`, `workflows/new-python-project.js` (+ installed copy).
- `README.md`: new *Python project scaffolding* group + Workflows entry.
- No changes to existing skills/workflows; `openspec/specs/` gains the five capabilities on archive.
