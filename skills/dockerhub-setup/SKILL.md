---
name: dockerhub-setup
description: "Wire a project into Docker Hub end to end: create the Docker Hub repository (idempotent), mint a dedicated CI access token via the Hub API (label <repo>-ci), and set DOCKERHUB_USERNAME / DOCKERHUB_TOKEN as GitHub Actions secrets on the matching GitHub repo so dev/release workflows can publish images. Requires an admin PAT in the environment (DOCKERHUB_USERNAME + DOCKERHUB_TOKEN); absent credentials stop the skill with setup instructions — it never asks for a password in chat. Used by the new-scala-pekko-service workflow when dockerhub: true."
argument-hint: "<repo-name> [github-owner/repo]   (Docker Hub namespace fixed: calvinference)"
license: MIT
---

# Docker Hub setup (repo + CI token + GitHub secrets)

Fixed conventions (don't ask): Docker Hub namespace `calvinference`, GitHub owner `vezril`,
image name = `SERVICE` (project name minus a `-service`/`-svc` suffix).

Bundled script: `dockerhub-setup.sh` in this skill's folder — it does the Hub API work
(login → repo create → token mint) and emits the CI credentials **only on fd 3**, never
stdout.

## Step 0 — credentials gate

`DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (an **admin** personal access token) must be in
the environment. If either is missing, STOP and report:

> Docker Hub setup skipped — set `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (create an
> admin PAT at hub.docker.com → Account Settings → Personal access tokens) and re-run.
> CI stays green meanwhile: the workflows skip image publishing while the secrets are absent.

Never ask for, echo, or paste a password or token value in chat. This is not a failure of
the surrounding workflow — report it as a skipped, resumable step.

## Step 1 — run the script

```
DOCKERHUB_USERNAME="$DOCKERHUB_USERNAME" DOCKERHUB_TOKEN="$DOCKERHUB_TOKEN" \
  bash <skill-dir>/dockerhub-setup.sh calvinference <SERVICE> "<description>" 3>"$TMPDIR/dockerhub-ci.env"
```

- Repo creation is idempotent (no-op if it exists).
- Token minting: label `<SERVICE>-ci`, scope `repo:write`. Hub personal tokens are
  **account-wide** (scoped by permission, not per-repo) — include this in the report.
- If minting fails (2FA, plan limits, API drift) the script falls back to the admin PAT as
  the CI credential and warns loudly on stderr — surface that warning verbatim in the
  report, with the manual remediation (mint a token in the Hub UI, update the secret).

## Step 2 — set the GitHub secrets

Source the fd-3 output and pipe values straight into gh — never echo them:

```
. "$TMPDIR/dockerhub-ci.env"
printf '%s' "$CI_DOCKERHUB_USERNAME" | gh secret set DOCKERHUB_USERNAME --repo vezril/<NAME>
printf '%s' "$CI_DOCKERHUB_TOKEN"    | gh secret set DOCKERHUB_TOKEN    --repo vezril/<NAME>
rm -f "$TMPDIR/dockerhub-ci.env"
```

Verify with `gh secret list --repo vezril/<NAME>` (names only — values are never readable).

## Step 3 — report

Hub repo URL, token label minted (or the FALLBACK warning verbatim), both secret names
confirmed present on the GitHub repo, and the account-wide-token caveat. Delete the
temporary credentials file and say so.

## Guardrails

- Credentials come from the environment only; values are piped, never echoed, never logged.
- The fallback (admin PAT in CI) is acceptable but must be flagged loudly — never silently.
- Do not create the GitHub repo or touch CI files here — this skill only wires credentials.
