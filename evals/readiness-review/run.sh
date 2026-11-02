#!/usr/bin/env bash
# Usage: [REPEAT=1] ./run.sh v1 [haiku|sonnet|all]
#
# Copies prompts/prompt_<v>.md to prompts/current.md, runs the suite without cache, and
# writes the evidence to results/run_<v>_<provider>.json.
#
# Node 22 is put on PATH explicitly: promptfoo needs >=22.22.0 and this machine's global pin
# is 18.20.2. Repinning globally for one suite would be a machine-wide change.
set -euo pipefail
cd "$(dirname "$0")"

NODE22="$HOME/.local/share/mise/installs/node/22.23.4/bin"
[ -x "$NODE22/node" ] && export PATH="$NODE22:$PATH"

v="$1"; p="${2:-all}"
cp "prompts/prompt_${v}.md" prompts/current.md

filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")
npx promptfoo@latest "eval" --no-cache --repeat "${REPEAT:-1}" \
  ${filter[@]+"${filter[@]}"} -o "results/run_${v}_${p}.json" || true

node score.js "results/run_${v}_${p}.json"
