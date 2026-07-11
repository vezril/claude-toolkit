---
name: python-uv-build
description: "Scaffold the uv build definition for a Python 3.12 project into the current working tree: pyproject.toml (hatchling src-layout build, empty runtime deps, dev group with ruff/mypy/pytest, ruff+mypy+pytest tool config), .python-version, .gitignore, and a multi-stage uv Dockerfile running python -m <pkg>. Writes no uv.lock (the verify gate's uv sync generates it), no sources, tests, docs, or CI — those belong to python-package, python-tests, repo-starter-docs, and github-actions-python-ci. First scaffold step of the new-python-project workflow."
argument-hint: "<project-name> [package-name]   (e.g. athena-service → package athena)"
license: MIT
---

# Python uv build scaffold

Generate the build definition — deterministically, via the bundled script. Run from the
project's working tree.

Bundled script: `scaffold.sh` in this skill's folder (invoke by absolute path).

## Run

```
bash <skill-dir>/scaffold.sh <project-name> [package-name]
```

- `project-name` — lowercase `[a-z0-9-]`. The package derives scala-consistently: name
  minus `-service`/`-svc`, hyphens → underscores (`athena-service` → `athena`,
  `data-tools` → `data_tools`); override with the second argument.
- Refuses to run if `pyproject.toml` exists; writes only its own territory.
- **`uv.lock` is deliberately not scaffolded** — it's generated (network-dependent) by the
  workflow's verify gate (`uv sync`) and ships with the scaffold PR so CI can
  `uv sync --locked`.
- The Dockerfile has **no HEALTHCHECK** by design: the entry point is a CLI, not a server;
  when a project grows an HTTP surface, add the probe with it.

## README enrichment (after repo-starter-docs)

If `README.md` exists (repo-starter-docs wrote it), **replace the Getting-started TODO
section** — never the description or license sections — with:

- Layout: `src/<pkg>/` (sources), `tests/` (pytest suite).
- Develop: `uv sync` (env + lockfile), `uv run pytest`, `uv run python -m <pkg>`,
  `uv run ruff check .` / `uv run ruff format .`, `uv run mypy src`.
- Docker: `docker build -t <user>/<service> .`, `docker run <user>/<service>` — noting the
  Dockerfile ships regardless of Docker Hub wiring (publish is CI's job, gated on secrets).
- CI/CD: ci.yml on PRs (lint/format/types/tests); dev.yml publishes `:dev` images from
  `development`; release.yml publishes `:X.Y.Z` + `:latest` from a `vX.Y.Z` tag; image
  publishing skips gracefully while the `DOCKERHUB_*` secrets are absent.

## Report

Files written, the derived package name, and what was appended to the README.

## Guardrails

- Territory: never write sources, tests, README/LICENSE creation, CI files, or `uv.lock`.
- Never overwrite an existing `pyproject.toml` (the script enforces this).
- Version pins (Python, ruff/mypy/pytest floors) live in the script — one place.
- pyproject.toml declares `readme = "README.md"`, so `uv sync` fails until a README exists —
  in the workflow, repo-starter-docs writes it before the gate runs; standalone, create the
  README (or run repo-starter-docs) before syncing.
