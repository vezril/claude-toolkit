#!/usr/bin/env bash
# Usage: [TAG=s2] ./run.sh v1 [sonnet|haiku|all]
# One sample: each case once per provider, in a fresh temp copy of fixture/ per provider.
# The agent edits code here, so worlds can't be shared: not between providers (they run
# in parallel) and not between repeats (a fix from one repeat would greet the next).
# Hence no --repeat; take more samples with TAG. Results go to
# results/run_<v>_<provider>[.<TAG>].json, and each case's project as the agent left it
# to results/worlds/<v>_<provider>[.<TAG>]/<case>/, which is what the asserts grade and
# what rescore.js regrades. Tools: Read/Grep/Glob/Bash plus Edit/Write limited to the
# world by absolute path (a relative rule broke when an agent cd'd away: v2 sonnet's
# first sample had an edit denied), Bash sandboxed to it.
set -euo pipefail
cd "$(dirname "$0")"
v="$1"; which="${2:-all}"
test -f "prompts/prompt_${v}.md"
providers=(sonnet haiku); [ "$which" != all ] && providers=("$which")
one() {
  local p="$1" WORLD SNAP cfg out
  WORLD="$(mktemp -d)/world"; cp -R fixture "$WORLD"; mkdir -p "$WORLD/.skill"
  # Real path (/var is a symlink on macOS): the Edit/Write rules below are absolute, so a
  # `cd` into the agent's scratchpad can't turn "./**" into the wrong directory.
  WORLD="$(cd "$WORLD" && pwd -P)"
  python3 make_sample_log.py "$WORLD/logs/sample.log"
  [ -d "prompts/prompt_${v}.files" ] && cp -R "prompts/prompt_${v}.files/." "$WORLD/.skill/"
  SNAP="$PWD/results/worlds/${v}_${p}${TAG:+.$TAG}"; rm -rf "$SNAP"; mkdir -p "$SNAP"
  cfg=".run.$$.$p.yaml"
  sed -e "s#(\./\*\*)#(/${WORLD}/**)#g" -e "s#\./fixture#${WORLD}#g" -e "s#file://prompts/current.md#file://prompts/prompt_${v}.md#" -e "s#__SKILL_DIR__#${WORLD}/.skill#" promptfooconfig.yaml > "$cfg"
  out="results/run_${v}_${p}${TAG:+.$TAG}.json"
  WORLD="$WORLD" SNAP="$SNAP" npx promptfoo eval -c "$cfg" --no-cache --filter-providers "^${p}$" -o "$out" >/dev/null 2>&1 || true
  node scan.js "$out" "$WORLD"
  rm -f "$cfg"; rm -rf "$(dirname "$WORLD")"
}
for p in "${providers[@]}"; do one "$p" & done
wait
for p in "${providers[@]}"; do node score.js "results/run_${v}_${p}${TAG:+.$TAG}.json"; done
