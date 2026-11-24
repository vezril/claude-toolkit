#!/usr/bin/env bash
# Usage: [REPEAT=3] [TAG=s2] ./run.sh v1 [haiku|sonnet|all]
#
# The agent WRITES INTO the fixtures, so they are restored from git before every run. Without
# that, a second run grades the previous run's work and the scores are meaningless.
set -euo pipefail
cd "$(dirname "$0")"

# Restore the fixtures from git. **Refuses if they are not tracked**, because on an
# uncommitted tree `git clean` does not restore anything — it deletes the fixtures outright.
# That is not hypothetical: it wiped three of them here before this guard existed.
restore_fixtures() {
  if ! git ls-files --error-unmatch fixture >/dev/null 2>&1; then
    echo "fixture/ is not tracked by git, so it cannot be restored — and cleaning it would" >&2
    echo "DELETE it. Commit the fixtures first." >&2
    exit 2
  fi
  git checkout -- fixture/
  git clean -fdq fixture/
}
restore_fixtures

# Calibrate AFTER restoring, so the grader is checked against pristine fixtures. Running it
# first meant a tree left dirty by a previous run failed calibration and aborted before the
# restore could clean it — a real refusal, in an order that could not recover.
python3 -I calibrate.py >/dev/null || {
  echo "the grader failed calibration against pristine fixtures; fix grade.py" >&2; exit 1; }

# REPEAT must stay 1. promptfoo's --repeat reruns a case against the SAME working_dir, and
# this agent writes into it — repeat 2 would be graded against repeat 1's files, and the
# grader's comparison against the pristine fixture would be meaningless. The three consecutive
# runs certification wants come from invoking this script three times, which restores the
# fixtures between them.
if [ "${REPEAT:-1}" != "1" ]; then
  echo "REPEAT must be 1: --repeat reuses the working dir and this agent writes into it." >&2
  echo "Run ./run.sh three times instead (TAG=s2, TAG=s3); fixtures are restored each time." >&2
  exit 2
fi

v="$1"; p="${2:-all}"
cp "prompts/prompt_${v}.md" prompts/current.md
filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")
npx promptfoo eval --no-cache --repeat 1 ${filter[@]+"${filter[@]}"} \
  -o "results/run_${v}_${p}${TAG:+.$TAG}.json" >/dev/null 2>&1 || true

echo "wrote results/run_${v}_${p}${TAG:+.$TAG}.json"
restore_fixtures
echo "fixtures restored"
