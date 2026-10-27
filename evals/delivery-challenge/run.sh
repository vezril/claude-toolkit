#!/usr/bin/env bash
# Usage: [REPEAT=3] [RUN=1] ./run.sh v1 [haiku|sonnet|all]
# Copies prompts/prompt_<v>.md to prompts/current.md, runs the suite without cache,
# and writes the evidence to results/run_<v>_<provider>.json.
#
# RUN=<n> writes results/run_<v>_<provider>_run<n>.json instead. The certification bar is
# three consecutive runs each at or above 95%, and check-certification.py reads them as
# three separate files, so the three runs are named here rather than renamed by hand
# afterwards.
set -euo pipefail
cd "$(dirname "$0")"

# promptfoo needs Node >= 22.22; a Mac pinned to 18 fails deep inside npx with no useful
# message, so say it here instead.
major="$(node -p 'process.versions.node.split(".")[0]')"
if [ "$major" -lt 22 ]; then
  echo "node $(node --version) is too old for promptfoo (needs >= 22.22)." >&2
  echo "  mise install node@22 && PATH=\"\$HOME/.local/share/mise/installs/node/22.23.4/bin:\$PATH\" ./run.sh $*" >&2
  exit 1
fi

v="$1"; p="${2:-all}"

# --- Bedrock credentials -------------------------------------------------------------
# On the work Mac, Claude Code reaches models through Bedrock and gets its AWS credentials
# from settings.json's `awsCredentialExport` helper, which keeps them in Claude Code's own
# process memory: there is no ~/.aws/config and no AWS_* secret in the environment.
# promptfoo spawns its own Agent SDK subprocess, which inherits CLAUDE_CODE_USE_BEDROCK and
# AWS_REGION but NOT the credentials, and does not read `awsCredentialExport` itself. So the
# credentials have to be put in the environment here. Being logged in is not enough, and
# `aws sts get-caller-identity` failing proves nothing about whether you are logged in.
CRED_HELPER="$HOME/.toolbox/bin/claude"
if [ -n "${CLAUDE_CODE_USE_BEDROCK:-}" ] && [ -z "${AWS_ACCESS_KEY_ID:-}" ]; then
  if [ ! -x "$CRED_HELPER" ]; then
    echo "CLAUDE_CODE_USE_BEDROCK is set but $CRED_HELPER is missing." >&2
    echo "  Every row would fail with 'Could not load AWS credentials'." >&2
    exit 1
  fi
  if ! cred_json="$("$CRED_HELPER" default-credential-export 2>/dev/null)"; then
    echo "The credential helper failed. Run: mwinit && aws login" >&2
    exit 1
  fi
  # Emits `export K=V` lines and the expiry; never echoed, so nothing lands in a log.
  if ! cred_env="$(printf '%s' "$cred_json" | python3 -I -c '
import sys, json
try:
    c = json.load(sys.stdin)["Credentials"]
except Exception:
    sys.exit(1)
for var, key in (("AWS_ACCESS_KEY_ID", "AccessKeyId"),
                 ("AWS_SECRET_ACCESS_KEY", "SecretAccessKey"),
                 ("AWS_SESSION_TOKEN", "SessionToken")):
    if not c.get(key):
        sys.exit(1)
    print(f"export {var}={c[key]}")
expiry = c.get("Expiration", "")
print(f"CRED_EXPIRY={expiry}")
')"; then
    echo "Could not parse credentials out of the helper. Run: mwinit && aws login" >&2
    exit 1
  fi
  eval "$cred_env"
  unset cred_json cred_env
fi

# A run that starts on credentials about to lapse produces a half-failed results file that
# scores like a bad prompt. Refuse instead: 9 cases x REPEAT x providers, and a call is
# rarely under 20s, so demand margin for the whole thing plus a little.
if [ -n "${CRED_EXPIRY:-}" ]; then
  providers=2; [ "$p" != all ] && providers=1
  need="$(python3 -I -c "print(9 * ${REPEAT:-3} * $providers * 20 + 120)")"
  left="$(python3 -I -c "
import datetime, sys
exp = datetime.datetime.fromisoformat('${CRED_EXPIRY}'.replace('Z', '+00:00'))
print(int((exp - datetime.datetime.now(datetime.timezone.utc)).total_seconds()))
")"
  echo "credentials valid for ${left}s; this run needs about ${need}s"
  if [ "$left" -lt "$need" ]; then
    echo "" >&2
    echo "Not enough credential life left for $p at REPEAT=${REPEAT:-3}." >&2
    echo "  Refresh (mwinit && aws login) or run one provider at a time." >&2
    exit 1
  fi
fi

# --- the run -------------------------------------------------------------------------
stem="run_${v}_${p}${RUN:+_run$RUN}"
out="results/${stem}.json"
log="results/${stem}.promptfoo.log"
cp "prompts/prompt_${v}.md" prompts/current.md
filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")

# promptfoo's own exit code is not a verdict on the prompt (assert failures are expected),
# so it is recorded rather than trusted. What must not happen is scoring a run that broke
# for an infrastructure reason: that reads as the prompt failing and has already cost runs.
set +e
npx promptfoo eval --no-cache --repeat "${REPEAT:-3}" ${filter[@]+"${filter[@]}"} -o "$out" >"$log" 2>&1
pf_exit=$?
set -e

if grep -qiE "could not load aws credentials|expiredtoken|unrecognizedclient|accessdenied(exception)?|unable to locate credentials" "$log"; then
  echo "" >&2
  echo "CONTAMINATED: the run hit a credential/authorization error, so these rows say" >&2
  echo "nothing about the prompt. Not scoring it. Offending lines:" >&2
  grep -iE "could not load aws credentials|expiredtoken|unrecognizedclient|accessdenied(exception)?|unable to locate credentials" "$log" | head -3 >&2
  mv -f "$out" "${out%.json}.DISCARDED.json" 2>/dev/null || true
  echo "  results moved to ${out%.json}.DISCARDED.json; full log in $log" >&2
  exit 1
fi

if [ ! -s "$out" ]; then
  echo "promptfoo exited $pf_exit and wrote no results. Last lines of $log:" >&2
  tail -n 20 "$log" >&2
  exit 1
fi

[ "$pf_exit" -ne 0 ] && echo "(promptfoo exited $pf_exit; assert failures are expected, see $log)"
node score.js "$out"
