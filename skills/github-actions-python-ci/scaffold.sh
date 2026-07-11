#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# github-actions-python-ci scaffold — the CI/CD surface for a uv Python
# project: ci.yml (ruff lint, ruff format check, mypy, pytest, gitleaks),
# dev.yml (:dev images from development), release.yml (semver images +
# GitHub Release), and the setup-uv composite action. Image publishing
# SKIPS (not fails) when the DOCKERHUB_* secrets are absent.
#
#   usage: scaffold.sh <project-name>
# ---------------------------------------------------------------------------
set -euo pipefail

NAME="${1:?usage: scaffold.sh <project-name>}"

SERVICE="${NAME%-service}"
SERVICE="${SERVICE%-svc}"
OWNER="vezril"
DOCKERHUB_USER="calvinference"
DEST="$PWD"

if [ -e "$DEST/.github/workflows/ci.yml" ]; then
  echo "ERROR: $DEST/.github/workflows/ci.yml already exists — refusing to overwrite." >&2
  exit 3
fi

mkdir -p \
  "$DEST/.github/workflows" \
  "$DEST/.github/actions/setup-uv"

# --- composite action ---------------------------------------------------------
cat > "$DEST/.github/actions/setup-uv/action.yml" <<'FILE'
name: "Setup uv"
description: "uv + the pinned Python from .python-version + cache keyed on uv.lock — shared by all workflows."
runs:
  using: "composite"
  steps:
    - name: Install uv (cached)
      uses: astral-sh/setup-uv@11f9893b081a58869d3b5fccaea48c9e9e46f990 # v8.3.2
      with:
        enable-cache: true
        cache-dependency-glob: "uv.lock"

    - name: Install the pinned Python
      shell: bash
      run: uv python install
FILE

# --- CI -----------------------------------------------------------------------
cat > "$DEST/.github/workflows/ci.yml" <<'FILE'
name: CI

# Verifies every pull request targeting development or main: lint, formatting,
# types, and the test suite. Merging is blocked unless all required checks pass
# (branch protection, where the plan allows it).
on:
  pull_request:
    branches: [development, main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  # Formatting is a separate job so a format violation fails independently of
  # the tests (a green suite must not mask a format failure).
  format:
    name: Format (ruff format)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: ./.github/actions/setup-uv
      - name: Check formatting
        run: |
          uv sync --locked
          uv run ruff format --check .

  lint:
    name: Lint (ruff check)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: ./.github/actions/setup-uv
      - name: Lint
        run: |
          uv sync --locked
          uv run ruff check .

  types:
    name: Types (mypy)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: ./.github/actions/setup-uv
      - name: Type-check
        run: |
          uv sync --locked
          uv run mypy src

  test:
    name: Test (pytest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: ./.github/actions/setup-uv
      - name: Run tests
        run: |
          uv sync --locked
          uv run pytest

  # Secret scanning — fail the PR if a credential was committed (language-agnostic).
  secrets-scan:
    name: Secret scan (gitleaks)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0 # scan full history
      - name: gitleaks
        run: |
          V=8.18.4
          curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/v${V}/gitleaks_${V}_linux_x64.tar.gz" \
            | tar xz -C /tmp gitleaks
          /tmp/gitleaks detect --source . --redact --verbose
FILE

# --- Dev publish ----------------------------------------------------------------
cat > "$DEST/.github/workflows/dev.yml" <<'FILE'
name: Dev publish

# Every push to development publishes an explicitly-unstable image (:dev and
# :dev-<short-sha>) after the tests pass. Runs only on pushes to this repo's
# development branch — fork pull requests cannot push here, so secrets are
# never exposed to forks.
on:
  push:
    branches: [development]

concurrency:
  group: dev-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: read

env:
  IMAGE_NAME: __SERVICE__

jobs:
  dev-publish:
    name: Test and publish dev image
    runs-on: ubuntu-latest
    if: github.repository_owner == '__OWNER__'
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4

      # Publishing degrades gracefully: absent Docker Hub secrets SKIP the image
      # steps (steps below gate on this output) instead of failing the workflow —
      # a project without a Docker Hub repo still gets green CI. secrets.* is not
      # readable in `if:`, hence this env indirection.
      - name: Check Docker Hub credentials
        id: creds
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
        run: |
          if [ -n "$DOCKERHUB_USERNAME" ] && [ -n "$DOCKERHUB_TOKEN" ]; then
            echo "present=true" >> "$GITHUB_OUTPUT"
          else
            echo "present=false" >> "$GITHUB_OUTPUT"
            echo "NOTICE: Docker Hub secrets absent — image publish steps will be SKIPPED."
          fi

      - uses: ./.github/actions/setup-uv

      - name: Run tests
        run: |
          uv sync --locked
          uv run pytest

      - name: Log in to Docker Hub
        if: steps.creds.outputs.present == 'true'
        uses: docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9 # v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build image
        if: steps.creds.outputs.present == 'true'
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
        run: docker build -t "$DOCKERHUB_USERNAME/$IMAGE_NAME:build" .

      - name: Tag and push dev + dev-<short-sha>
        if: steps.creds.outputs.present == 'true'
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          COMMIT_SHA: ${{ github.sha }}
        run: |
          SHORT_SHA="$(echo "$COMMIT_SHA" | cut -c1-7)"
          for TARGET in "$DOCKERHUB_USERNAME/$IMAGE_NAME:dev" "$DOCKERHUB_USERNAME/$IMAGE_NAME:dev-$SHORT_SHA"; do
            docker tag "$DOCKERHUB_USERNAME/$IMAGE_NAME:build" "$TARGET"
            docker push "$TARGET"
          done
FILE

# --- Release --------------------------------------------------------------------
cat > "$DEST/.github/workflows/release.yml" <<'FILE'
name: Release

# Publishes a Docker image to Docker Hub when a semver tag vX.Y.Z is pushed on
# main. The tag pattern below is the first gate: malformed tags never trigger.
on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"

concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false

# gh release create needs write; nothing else does.
permissions:
  contents: write

env:
  IMAGE_NAME: __SERVICE__

jobs:
  release:
    name: Test, build, and publish
    runs-on: ubuntu-latest
    if: github.repository_owner == '__OWNER__'
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0 # full history for the ancestry check

      # A tag must sit on main's first-parent history to release: this rejects a
      # tag on a feature commit that merely happens to be reachable from main.
      - name: Verify tag is on main
        env:
          TAG_SHA: ${{ github.sha }}
          REF_NAME: ${{ github.ref_name }}
        run: |
          git fetch --no-tags origin main
          if git rev-list --first-parent origin/main | grep -qx "$TAG_SHA"; then
            echo "OK: $REF_NAME is on main's first-parent history"
          else
            echo "ERROR: tag $REF_NAME is not on main's first-parent history — refusing to release"
            exit 1
          fi

      # Publishing degrades gracefully (see dev.yml) — tests and the GitHub
      # Release still run without Docker Hub secrets.
      - name: Check Docker Hub credentials
        id: creds
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
        run: |
          if [ -n "$DOCKERHUB_USERNAME" ] && [ -n "$DOCKERHUB_TOKEN" ]; then
            echo "present=true" >> "$GITHUB_OUTPUT"
          else
            echo "present=false" >> "$GITHUB_OUTPUT"
            echo "NOTICE: Docker Hub secrets absent — image publish steps will be SKIPPED."
          fi

      - uses: ./.github/actions/setup-uv

      - name: Run tests
        run: |
          uv sync --locked
          uv run pytest

      - name: Log in to Docker Hub
        if: steps.creds.outputs.present == 'true'
        uses: docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9 # v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Semver image tags are immutable — only :latest ever moves.
      - name: Enforce semver tag immutability
        if: steps.creds.outputs.present == 'true'
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          REF_NAME: ${{ github.ref_name }}
        run: |
          VERSION="${REF_NAME#v}"
          if docker manifest inspect "$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION" >/dev/null 2>&1; then
            echo "ERROR: $DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION already exists — semver tags are immutable"
            exit 1
          fi
          echo "OK: $VERSION is not yet published"

      - name: Build and push X.Y.Z + latest
        if: steps.creds.outputs.present == 'true'
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          REF_NAME: ${{ github.ref_name }}
        run: |
          VERSION="${REF_NAME#v}"
          docker build -t "$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION" .
          docker tag "$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION" "$DOCKERHUB_USERNAME/$IMAGE_NAME:latest"
          docker push "$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION"
          docker push "$DOCKERHUB_USERNAME/$IMAGE_NAME:latest"

      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REF_NAME: ${{ github.ref_name }}
        run: gh release create "$REF_NAME" --generate-notes --title "$REF_NAME"
FILE

find "$DEST/.github" -type f -print0 \
  | xargs -0 perl -pi -e "
      s#__DOCKERHUB_USER__#${DOCKERHUB_USER}#g;
      s#__SERVICE__#${SERVICE}#g;
      s#__NAME__#${NAME}#g;
      s#__OWNER__#${OWNER}#g;
    "

echo "github-actions-python-ci scaffold complete: $DEST/.github"
