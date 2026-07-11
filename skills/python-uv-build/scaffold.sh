#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# python-uv-build scaffold — the uv build definition for a Python 3.12 project:
# pyproject.toml (metadata, dev group: ruff/mypy/pytest, tool config),
# .python-version, .gitignore, and the multi-stage uv Dockerfile.
#
#   usage: scaffold.sh <project-name> [package-name]
#          (package default: name minus -service/-svc, hyphens -> underscores)
#
# Runs in the CURRENT directory. Writes NO uv.lock (the verify gate's
# `uv sync` generates it), no sources, tests, docs, or CI — those belong to
# python-package, python-tests, repo-starter-docs, github-actions-python-ci.
# ---------------------------------------------------------------------------
set -euo pipefail

NAME="${1:?usage: scaffold.sh <project-name> [package-name]}"

SERVICE="${NAME%-service}"
SERVICE="${SERVICE%-svc}"
PKG_DEFAULT="${SERVICE//-/_}"
PKG="${2:-$PKG_DEFAULT}"
OWNER="vezril"
DOCKERHUB_USER="calvinference"
YEAR="$(date +%Y)"
DEST="$PWD"

if ! printf '%s' "$NAME" | grep -Eq '^[a-z][a-z0-9-]*[a-z0-9]$'; then
  echo "ERROR: project name '$NAME' must be lowercase, start with a letter, and use only [a-z0-9-]." >&2
  exit 2
fi
if ! printf '%s' "$PKG" | grep -Eq '^[a-z_][a-z0-9_]*$'; then
  echo "ERROR: package name '$PKG' must be a valid python identifier (lowercase, [a-z0-9_])." >&2
  exit 2
fi
if [ -e "$DEST/pyproject.toml" ]; then
  echo "ERROR: $DEST/pyproject.toml already exists — refusing to overwrite." >&2
  exit 3
fi

cat > "$DEST/pyproject.toml" <<'FILE'
[project]
name = "__NAME__"
version = "0.1.0"
description = "__SERVICE__ — a Python project."
readme = "README.md"
license = "MIT"
authors = [{ name = "Calvin Ference", email = "calvin.ference@proton.me" }]
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "ruff>=0.8",
  "mypy>=1.13",
  "pytest>=8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/__PKG__"]

# ruff owns lint AND format (replaces black/flake8/isort).
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
strict = true
files = ["src"]
mypy_path = "src"

[tool.pytest.ini_options]
testpaths = ["tests"]
FILE

cat > "$DEST/.python-version" <<'FILE'
3.12
FILE

cat > "$DEST/.gitignore" <<'FILE'
# Python
__pycache__/
*.py[cod]
.venv/
dist/
build/
*.egg-info/

# Tooling caches
.pytest_cache/
.mypy_cache/
.ruff_cache/

# IDE
.idea/
.vscode/

# OS
.DS_Store

# Local env / secrets
.env
*.local
FILE

# Multi-stage image: uv resolves into a venv, the slim runtime only carries it.
# No HEALTHCHECK by design: the scaffold entry point is a CLI, not a server —
# service-ification later adds the HTTP surface and the probe together.
cat > "$DEST/Dockerfile" <<'FILE'
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app
RUN useradd --uid 1001 --create-home __PKG__
USER __PKG__
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "__PKG__"]
FILE

find "$DEST/pyproject.toml" "$DEST/Dockerfile" -type f -print0 \
  | xargs -0 perl -pi -e "
      s#__DOCKERHUB_USER__#${DOCKERHUB_USER}#g;
      s#__SERVICE__#${SERVICE}#g;
      s#__PKG__#${PKG}#g;
      s#__NAME__#${NAME}#g;
      s#__OWNER__#${OWNER}#g;
      s#__YEAR__#${YEAR}#g;
    "

echo "python-uv-build scaffold complete: $DEST (package: $PKG)"
