# Design: new-python-project

## Shape (mirror of new-scala-pekko-service)

```
new-python-project (workflow)
│  args: { name, visibility: 'public'|'private', dockerhub: boolean, auto?: false, pkg?: derived }
│
├─ Phase 1  BOOTSTRAP   workflow('new-github-project', {docs:false, ship:false})
│                         → repo + (plan-permitting) protected main + openspec init
├─ Phase 2  SCAFFOLD    on feat/scaffold, sequential:
│                         python-uv-build → python-package → python-tests →
│                         repo-starter-docs → README enrichment (python-uv-build) →
│                         github-actions-python-ci
├─ Phase 3  DOCKERHUB   only if dockerhub:true → dockerhub-setup (reused as-is)
├─ Phase 4  VERIFY      uv sync && uv run ruff check . && uv run ruff format --check .
│                         && uv run mypy src && uv run pytest
│                         red → status:failed, nothing pushed (repoCreated reported)
└─ Phase 5  SHIP        git-ship: one PR (includes uv.lock + openspec config);
                          gated → awaiting-merge-approval; auto → merge + development
```

## Decisions

**Toolchain: uv** (human, 2026-07-11). `pyproject.toml` is the single config surface
(project metadata, dependencies, `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`,
`[dependency-groups]` dev = ruff + mypy + pytest). `.python-version` pins the interpreter
(3.12). ruff replaces black (format) + flake8/isort (lint). CI uses `uv sync --locked` +
`uv run`.

**Name derivation, consistent with scala.** `SERVICE` = name minus `-service`/`-svc`
(image name); python package = `SERVICE` with hyphens → underscores (e.g.
`athena-service` → package `athena`, `data-tools` → `data_tools`). Overridable via the
workflow's `pkg` arg / the scripts' second parameter.

**The lockfile is generated, not scaffolded.** `python-uv-build` writes no `uv.lock`;
the verify phase's `uv sync` creates it (network-dependent by nature), and the ship
includes it so CI can run `uv sync --locked`. The scaffold scripts stay byte-deterministic;
the lockfile is the one deliberately non-deterministic artifact.

**`development` branch: yes, matching scala** (human, 2026-07-11). Same post-merge step:
created from merged `main`; dev.yml publishes `:dev` + `:dev-<sha>` images from it.

**Docker: optional, like scala** (human, 2026-07-11). `dockerhub` stays a required
boolean arg. The `Dockerfile` is a packaging concern → owned by `python-uv-build` and
always scaffolded (multi-stage: uv sync → slim runtime running `python -m <pkg>`); the
publish jobs live in dev.yml/release.yml with the same secrets-absent skip pattern.
No HTTP server in the scaffold — the entry point is a hello-world CLI (`python -m <pkg>`);
web frameworks are a per-project choice, unlike Pekko in the scala flavor. Consequence:
no HEALTHCHECK in the Dockerfile (nothing to probe) — a service-ification later adds both.

**Versioning: tag-driven, no dynver equivalent.** `version = "0.1.0"` static in
pyproject.toml; image tags come from the git tag in release.yml (`${REF_NAME#v}`), same
gates as scala (tag-on-main ancestry, semver image immutability). Python-side dynamic
versioning (hatch-vcs) is deliberately out — add per-project if it ever publishes to PyPI.

**Territory rules carry over.** `python-package` never touches `tests/`; `python-tests`
never touches `src/` and reads the real package name from `src/` (fails if the package
scaffold hasn't run). Overwrite refusal on each script's key output (pyproject.toml,
`src/<pkg>/`, `tests/`).

**CI jobs.** ci.yml on PRs to `development`/`main`: lint (`ruff check`), format
(`ruff format --check`, own job — same can't-be-masked rationale as scala), types
(`mypy src`), tests (`pytest`), gitleaks. All jobs `uv sync --locked` via a shared
setup-uv composite action (pinned `astral-sh/setup-uv`, uv-managed Python, cache keyed
on uv.lock).

## Risks

- uv's CLI surface moves fast; the composite action pins the setup-uv SHA and the scaffold
  pins `.python-version` — the green gate catches breakage at scaffold time, not in CI.
- `uv sync` needs network at verify time (lockfile creation) — acceptable; the same is true
  of sbt's first resolve in the scala flavor.
- Dockerfile-always + dockerhub:false leaves an unpublished Dockerfile in the repo — that's
  intentional (parity with scala, where the Docker plugin config also ships regardless), and
  documented in the scaffold README enrichment.
