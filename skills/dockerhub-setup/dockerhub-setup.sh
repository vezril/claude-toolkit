#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# dockerhub-setup.sh — wire a project into Docker Hub end to end:
#   1) create the Docker Hub repository (idempotent),
#   2) mint a dedicated CI access token (label <repo>-ci, write scope),
#   3) print the resulting CI credentials AS SHELL ASSIGNMENTS on fd 3 so the
#      caller can pipe them into `gh secret set` without them ever touching
#      the terminal, history, or logs.
#
#   usage: DOCKERHUB_USERNAME=… DOCKERHUB_TOKEN=… \
#            dockerhub-setup.sh <namespace> <repo> [description] 3>creds.env
#
# DOCKERHUB_TOKEN must be an ADMIN personal access token (token minting needs
# it). If minting fails (2FA, plan limits, API drift), falls back to emitting
# the admin PAT itself as the CI credential and says so LOUDLY on stderr.
# Requires: curl, jq. Credentials come from the environment, never args.
# Inherits the repo-creation logic of the retired new-scala-service/dockerhub-repo.sh.
# ---------------------------------------------------------------------------
set -euo pipefail

NS="${1:?usage: dockerhub-setup.sh <namespace> <repo> [description]}"
REPO="${2:?usage: dockerhub-setup.sh <namespace> <repo> [description]}"
DESC="${3:-}"
: "${DOCKERHUB_USERNAME:?set DOCKERHUB_USERNAME in the environment}"
: "${DOCKERHUB_TOKEN:?set DOCKERHUB_TOKEN in the environment}"

# fd 3 must be wired up by the caller — refuse to print secrets to stdout.
if ! { true >&3; } 2>/dev/null; then
  echo "ERROR: open fd 3 for the credential output (e.g. '3>creds.env') — secrets are never printed to stdout." >&2
  exit 2
fi

# 1) Exchange username + admin PAT for a short-lived JWT.
JWT="$(curl -fsS -H 'Content-Type: application/json' \
  -d "{\"username\":\"${DOCKERHUB_USERNAME}\",\"password\":\"${DOCKERHUB_TOKEN}\"}" \
  https://hub.docker.com/v2/users/login/ | jq -r '.token // empty')"
if [ -z "$JWT" ]; then
  echo "ERROR: Docker Hub login failed (check DOCKERHUB_USERNAME / DOCKERHUB_TOKEN; 2FA accounts may need an OTP flow — create the token manually instead)." >&2
  exit 1
fi

# 2) Create the repo (idempotent).
CODE="$(curl -fsS -o /dev/null -w '%{http_code}' \
  -H "Authorization: JWT ${JWT}" \
  "https://hub.docker.com/v2/repositories/${NS}/${REPO}/" || true)"
if [ "$CODE" = "200" ]; then
  echo "Docker Hub repo ${NS}/${REPO} already exists — skipping creation."
else
  RESP="$(curl -fsS -X POST \
    -H "Authorization: JWT ${JWT}" \
    -H 'Content-Type: application/json' \
    -d "{\"namespace\":\"${NS}\",\"name\":\"${REPO}\",\"is_private\":false,\"description\":\"${DESC}\"}" \
    https://hub.docker.com/v2/repositories/ || true)"
  if printf '%s' "$RESP" | jq -e '.name' >/dev/null 2>&1; then
    echo "Created Docker Hub repo ${NS}/${REPO} (public)."
  else
    echo "ERROR: could not create ${NS}/${REPO}:" >&2
    printf '%s\n' "$RESP" | jq -r '.detail // .message // .' >&2 2>/dev/null || printf '%s\n' "$RESP" >&2
    exit 1
  fi
fi

# 3) Mint a dedicated CI token. NOTE: Hub personal access tokens are
# account-wide (scoped by permission, not by repo) — documented limitation.
TOKEN_RESP="$(curl -fsS -X POST \
  -H "Authorization: JWT ${JWT}" \
  -H 'Content-Type: application/json' \
  -d "{\"token_label\":\"${REPO}-ci\",\"scopes\":[\"repo:write\"]}" \
  https://hub.docker.com/v2/access-tokens/ || true)"
CI_TOKEN="$(printf '%s' "$TOKEN_RESP" | jq -r '.token // empty' 2>/dev/null || true)"

if [ -n "$CI_TOKEN" ]; then
  echo "Minted CI access token '${REPO}-ci' (scope repo:write, account-wide by Hub design)."
  printf 'CI_DOCKERHUB_USERNAME=%s\nCI_DOCKERHUB_TOKEN=%s\n' "$DOCKERHUB_USERNAME" "$CI_TOKEN" >&3
else
  echo "WARNING: could not mint a CI access token (2FA/plan limits/API change?)." >&2
  echo "WARNING: FALLING BACK to the ADMIN PAT as the CI credential — this is an" >&2
  echo "WARNING: account-wide admin token in CI. Recommended: mint a token manually" >&2
  echo "WARNING: at hub.docker.com > Account Settings > Personal access tokens," >&2
  echo "WARNING: then update the repo secret." >&2
  printf 'CI_DOCKERHUB_USERNAME=%s\nCI_DOCKERHUB_TOKEN=%s\nFALLBACK=admin-pat\n' "$DOCKERHUB_USERNAME" "$DOCKERHUB_TOKEN" >&3
fi

echo "dockerhub-setup complete for ${NS}/${REPO}."
