#!/usr/bin/env bash
# Usage: [REPEAT=3] [TAG=s2] ./run.sh v1 [haiku|sonnet|all]
# Copies prompts/prompt_<v>.md to prompts/current.md, runs the suite without cache,
# and writes the evidence to results/run_<v>_<provider>.json.
#
# Asserts are mutation-tested before any model call; run `node asserts/selftest.js` first.
set -euo pipefail
cd "$(dirname "$0")"

# promptfoo needs Node >= 22 and the repo's default is 18, where it exits with a version
# message that `run.sh` used to swallow via `>/dev/null 2>&1 || true` — the suite looked like
# it ran and wrote nothing. Prefer a mise-installed 22+ if the current node is too old.
node_major() { node --version 2>/dev/null | sed 's/^v//' | cut -d. -f1; }
if [ "$(node_major)" -lt 22 ] 2>/dev/null; then
  for candidate in "$HOME"/.local/share/mise/installs/node/2[2-9]*/bin; do
    [ -x "$candidate/node" ] && PATH="$candidate:$PATH" && export PATH && break
  done
fi
if [ "$(node_major)" -lt 22 ] 2>/dev/null; then
  echo "promptfoo needs Node >= 22; found $(node --version 2>/dev/null || echo none)" >&2
  exit 2
fi
node asserts/selftest.js >/dev/null || { echo "asserts failed their self-test; fix them first" >&2; exit 1; }
v="$1"; p="${2:-all}"
cp "prompts/prompt_${v}.md" prompts/current.md
filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")
npx promptfoo eval --no-cache --repeat "${REPEAT:-3}" ${filter[@]+"${filter[@]}"} -o "results/run_${v}_${p}${TAG:+.$TAG}.json" >/dev/null 2>&1 || true
node ../pr-description/score.js "results/run_${v}_${p}${TAG:+.$TAG}.json" 2>/dev/null \
  || echo "wrote results/run_${v}_${p}${TAG:+.$TAG}.json (score.js unavailable; read the JSON)"
