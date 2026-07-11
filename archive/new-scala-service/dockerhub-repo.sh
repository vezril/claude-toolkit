#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# dockerhub-repo.sh — create a Docker Hub repository via the Hub REST API.
#
# The `docker` CLI cannot CREATE a repo (a repo is only made implicitly on the
# first `docker push`). This creates it explicitly so it exists before CI's
# first publish. Idempotent: a no-op if the repo already exists.
#
#   usage: DOCKERHUB_USERNAME=… DOCKERHUB_TOKEN=… dockerhub-repo.sh <namespace> <repo> [description]
#
# Requires: curl, jq. Credentials come from the environment (never args), so
# nothing sensitive lands in shell history or the process table.
# ---------------------------------------------------------------------------
set -euo pipefail

NS="${1:?usage: dockerhub-repo.sh <namespace> <repo> [description]}"
REPO="${2:?usage: dockerhub-repo.sh <namespace> <repo> [description]}"
DESC="${3:-}"
: "${DOCKERHUB_USERNAME:?set DOCKERHUB_USERNAME in the environment}"
: "${DOCKERHUB_TOKEN:?set DOCKERHUB_TOKEN in the environment}"

# 1) Exchange username + PAT for a short-lived JWT.
JWT="$(curl -fsS -H 'Content-Type: application/json' \
  -d "{\"username\":\"${DOCKERHUB_USERNAME}\",\"password\":\"${DOCKERHUB_TOKEN}\"}" \
  https://hub.docker.com/v2/users/login/ | jq -r '.token // empty')"
if [ -z "$JWT" ]; then
  echo "ERROR: Docker Hub login failed (check DOCKERHUB_USERNAME / DOCKERHUB_TOKEN)." >&2
  exit 1
fi

# 2) Short-circuit if it already exists.
CODE="$(curl -fsS -o /dev/null -w '%{http_code}' \
  -H "Authorization: JWT ${JWT}" \
  "https://hub.docker.com/v2/repositories/${NS}/${REPO}/" || true)"
if [ "$CODE" = "200" ]; then
  echo "Docker Hub repo ${NS}/${REPO} already exists — nothing to do."
  exit 0
fi

# 3) Create it (public, matching the constellation convention).
RESP="$(curl -fsS -X POST \
  -H "Authorization: JWT ${JWT}" \
  -H 'Content-Type: application/json' \
  -d "{\"namespace\":\"${NS}\",\"name\":\"${REPO}\",\"is_private\":false,\"description\":\"${DESC}\"}" \
  https://hub.docker.com/v2/repositories/ || true)"

if printf '%s' "$RESP" | jq -e '.name' >/dev/null 2>&1; then
  echo "Created Docker Hub repo ${NS}/${REPO} (public)."
else
  echo "ERROR: could not create ${NS}/${REPO}:" >&2
  printf '%s\n' "$RESP" | jq -r '.detail // .message // .' 2>/dev/null || printf '%s\n' "$RESP" >&2
  exit 1
fi
