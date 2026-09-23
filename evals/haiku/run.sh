#!/usr/bin/env bash
# Usage: [REPEAT=3] [TAG=s2] ./run.sh v1 [sonnet|haiku|all]
# Copies prompts/prompt_<v>.md to prompts/current.md, runs the suite without cache,
# and writes the evidence to results/run_<v>_<provider>[.<TAG>].json. TAG names an
# extra sample of the same version so it doesn't overwrite the first.
set -euo pipefail
cd "$(dirname "$0")"
v="$1"; p="${2:-all}"
cp "prompts/prompt_${v}.md" prompts/current.md
filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")
out="results/run_${v}_${p}${TAG:+.$TAG}.json"
npx promptfoo eval --no-cache --repeat "${REPEAT:-3}" ${filter[@]+"${filter[@]}"} -o "$out" >/dev/null 2>&1 || true
node score.js "$out"
