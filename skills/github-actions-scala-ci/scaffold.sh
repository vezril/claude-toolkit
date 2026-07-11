#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# github-actions-scala-ci scaffold — the CI/CD surface: ci.yml (format,
# compile+test+coverage, dynver sanity, secret scan), dev.yml (:dev images),
# release.yml (semver images + GitHub Release), and the setup-scala action.
#
#   usage: scaffold.sh <project-name> [pkg-root]      (pkg-root default: me.cference)
#
# Runs in the CURRENT directory (the project's working tree). Writes only the
# files listed above; README/LICENSE/docs belong to repo-starter-docs, and the
# other scala-* / github-actions-scala-ci skills own their own territories.
# Split from the retired new-scala-service monolith; heredoc bodies unchanged.
# ---------------------------------------------------------------------------
set -euo pipefail

NAME="${1:?usage: scaffold.sh <project-name> [pkg-root]}"
PKG_ROOT="${2:-me.cference}"

# NAME    repo / folder name (hyphens allowed): athena-service
# SERVICE short name (image name + health "service" field): strip a -service/-svc suffix
# PKGSEG  Scala package segment (no hyphens — must be a valid identifier)
# PKG     dotted package: <pkg-root>.<pkgseg>
SERVICE="${NAME%-service}"
SERVICE="${SERVICE%-svc}"
PKGSEG="${SERVICE//-/}"
OWNER="vezril"
DOCKERHUB_USER="calvinference"
PKG="${PKG_ROOT}.${PKGSEG}"
PKGPATH="$(printf '%s' "$PKG" | tr '.' '/')"
YEAR="$(date +%Y)"
DEST="$PWD"

if ! printf '%s' "$NAME" | grep -Eq '^[a-z][a-z0-9-]*[a-z0-9]$'; then
  echo "ERROR: project name '$NAME' must be lowercase, start with a letter, and use only [a-z0-9-]." >&2
  exit 2
fi
if ! printf '%s' "$PKG_ROOT" | grep -Eq '^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*$'; then
  echo "ERROR: pkg-root '$PKG_ROOT' must be dotted lowercase identifiers (e.g. me.cference)." >&2
  exit 2
fi
if [ -e "$DEST/.github/workflows/ci.yml" ]; then
  echo "ERROR: $DEST/.github/workflows/ci.yml already exists — refusing to overwrite." >&2
  exit 3
fi

mkdir -p \
  "$DEST/.github/workflows" \
  "$DEST/.github/actions/setup-scala"

# --- .github: composite setup action ----------------------------------------
cat > "$DEST/.github/actions/setup-scala/action.yml" <<'FILE'
name: "Setup Scala build"
description: "JDK (Temurin 21), sbt, and Coursier/sbt caching — shared by all workflows."
runs:
  using: "composite"
  steps:
    - name: Set up JDK 21
      uses: actions/setup-java@c1e323688fd81a25caa38c78aa6df2d33d3e20d9 # v4
      with:
        distribution: temurin
        java-version: "21"

    - name: Set up sbt
      uses: sbt/setup-sbt@66fb4376e81982c7d92a4074170846fff88e2e30 # v1

    - name: Cache Coursier and sbt
      uses: actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830 # v4
      with:
        path: |
          ~/.cache/coursier
          ~/.sbt
          ~/.ivy2/cache
        key: ${{ runner.os }}-sbt-${{ hashFiles('**/build.sbt', 'project/**') }}
        restore-keys: |
          ${{ runner.os }}-sbt-
FILE

# --- .github: CI ------------------------------------------------------------
cat > "$DEST/.github/workflows/ci.yml" <<'FILE'
name: CI

# Verifies every pull request targeting development or main: formatting,
# compilation, and the full test suite. Merging is blocked unless all required
# checks pass (branch protection).
on:
  pull_request:
    branches: [development, main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

# Least privilege: CI only reads the repo (no package/image publish here).
permissions:
  contents: read

jobs:
  # Formatting is a separate job so a scalafmt violation fails independently of
  # the tests (a green test suite must not mask a format failure).
  format:
    name: Format (scalafmt)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: ./.github/actions/setup-scala
      - name: Check formatting
        run: sbt -batch scalafmtCheckAll scalafmtSbtCheck

  build-test:
    name: Compile & test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0 # sbt-dynver needs full history + tags
      - uses: ./.github/actions/setup-scala
      - name: Compile
        run: sbt -batch compile Test/compile
      - name: Test (with coverage)
        # Coverage is reported, not gated — add `coverageMinimumStmtTotal := N` in build.sbt to enforce.
        run: sbt -batch clean coverage test coverageReport

  # sbt-dynver sanity: an untagged commit must yield a snapshot (non-releasable)
  # version so releases can only come from an explicit tag.
  version-check:
    name: Version derivation (dynver)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0
      - uses: ./.github/actions/setup-scala
      - name: Assert untagged build is a snapshot
        run: |
          VERSION=$(sbt -Dsbt.log.noformat=true -batch -error 'print version' | tail -n1 | perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g' | tr -d '[:space:]')
          echo "Derived version: $VERSION"
          case "$VERSION" in
            *SNAPSHOT*|*-*-*) echo "OK: snapshot version" ;;
            *) echo "ERROR: untagged build produced a clean release version '$VERSION'"; exit 1 ;;
          esac

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

# --- .github: Dev publish ---------------------------------------------------
cat > "$DEST/.github/workflows/dev.yml" <<'FILE'
name: Dev publish

# Every push to development publishes an explicitly-unstable image (:dev and
# :dev-<short-sha>) after the tests pass. Runs only on pushes to this repo's
# development branch — fork pull requests cannot push here, so secrets are never
# exposed to forks.
on:
  push:
    branches: [development]

# Never cancel a half-finished dev push (leaving the registry partially updated);
# serialize per ref instead.
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
        with:
          fetch-depth: 0

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

      - uses: ./.github/actions/setup-scala

      - name: Log in to Docker Hub
        if: steps.creds.outputs.present == 'true'
        uses: docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9 # v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Run tests
        run: sbt -batch test

      # build.sbt reads DOCKERHUB_USERNAME to name the image namespace, so the
      # locally-built image matches the push targets below (single source of truth).
      - name: Build image
        if: steps.creds.outputs.present == 'true'
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
        run: sbt -batch server/Docker/publishLocal

      - name: Tag and push dev + dev-<short-sha>
        if: steps.creds.outputs.present == 'true'
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          COMMIT_SHA: ${{ github.sha }}
        run: |
          VERSION=$(sbt -Dsbt.log.noformat=true -batch -error 'print server/version' | tail -n1 | perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g' | tr -d '[:space:]')
          SHORT_SHA="$(echo "$COMMIT_SHA" | cut -c1-7)"
          LOCAL="$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION"
          for TARGET in "$DOCKERHUB_USERNAME/$IMAGE_NAME:dev" "$DOCKERHUB_USERNAME/$IMAGE_NAME:dev-$SHORT_SHA"; do
            docker tag "$LOCAL" "$TARGET"
            docker push "$TARGET"
          done
FILE

# --- .github: Release -------------------------------------------------------
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
          fetch-depth: 0 # full history for dynver + ancestry check

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

      # Fail before any build/push if credentials are absent (no partial publish).
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

      - uses: ./.github/actions/setup-scala

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

      # Nothing is pushed unless the whole suite passes first.
      - name: Run tests
        run: sbt -batch test

      - name: Build image
        if: steps.creds.outputs.present == 'true'
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
        run: sbt -batch server/Docker/publishLocal

      - name: Tag and push X.Y.Z + latest
        if: steps.creds.outputs.present == 'true'
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          REF_NAME: ${{ github.ref_name }}
        run: |
          VERSION="${REF_NAME#v}"
          LOCAL="$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION" # dynver on a clean tag == X.Y.Z
          for TARGET in "$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION" "$DOCKERHUB_USERNAME/$IMAGE_NAME:latest"; do
            docker tag "$LOCAL" "$TARGET"
            docker push "$TARGET"
          done

      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REF_NAME: ${{ github.ref_name }}
        run: gh release create "$REF_NAME" --generate-notes --title "$REF_NAME"
FILE

# Substitute placeholders in the files THIS script generated (longer tokens first).
find "$DEST/.github" -type f -not -path '*/.git/*' -print0 \
  | xargs -0 perl -pi -e "
      s#__PKGPATH__#${PKGPATH}#g;
      s#__PKGSEG__#${PKGSEG}#g;
      s#__DOCKERHUB_USER__#${DOCKERHUB_USER}#g;
      s#__SERVICE__#${SERVICE}#g;
      s#__PKG__#${PKG}#g;
      s#__NAME__#${NAME}#g;
      s#__OWNER__#${OWNER}#g;
      s#__YEAR__#${YEAR}#g;
    "

echo "github-actions-scala-ci scaffold complete: $DEST"
