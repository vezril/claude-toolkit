#!/usr/bin/env bash
# Usage: [REPEAT=3] ./run.sh v1 [haiku|sonnet|all]
# Copies prompts/prompt_<v>.md to prompts/current.md, runs the suite without cache,
# and writes the evidence to results/run_<v>_<provider>.json.
set -euo pipefail
cd "$(dirname "$0")"
v="$1"; p="${2:-all}"
cp "prompts/prompt_${v}.md" prompts/current.md
filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")
npx promptfoo eval --no-cache --repeat "${REPEAT:-3}" ${filter[@]+"${filter[@]}"} -o "results/run_${v}_${p}.json" >/dev/null 2>&1 || true
node score.js "results/run_${v}_${p}.json"
