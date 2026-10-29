#!/usr/bin/env bash
# Usage: [REPEAT=3] [TAG=s2] ./run.sh v1 [sonnet|haiku|all]
# Runs prompts/prompt_<v>.md through the suite without cache and writes the evidence
# to results/run_<v>_<provider>[.<TAG>].json. TAG names an extra sample.
#
# Isolation (learned on the handoff suite): the agent works in a fresh temp copy of
# fixture/, never fixture/ itself, so it can't walk up into expected/ or prompts/.
# If prompts/prompt_<v>.files/ exists it is the skill's own folder (the files its
# relative links point at) and lands at $WORLD/.skill, named in the prompt the way
# Claude Code names a skill's base directory. The generated config names the prompt
# file directly, so versions can run in parallel.
set -euo pipefail
cd "$(dirname "$0")"
v="$1"; p="${2:-all}"
test -f "prompts/prompt_${v}.md"
WORLD="$(mktemp -d)/world"; export WORLD
cp -R fixture "$WORLD"
mkdir -p "$WORLD/.skill"
[ -d "prompts/prompt_${v}.files" ] && cp -R "prompts/prompt_${v}.files/." "$WORLD/.skill/"
cfg=".run.$$.yaml"
sed -e "s#\./fixture#${WORLD}#g" -e "s#file://prompts/current.md#file://prompts/prompt_${v}.md#" -e "s#__SKILL_DIR__#${WORLD}/.skill#" promptfooconfig.yaml > "$cfg"
trap 'rm -f "$cfg"; rm -rf "$(dirname "$WORLD")"' EXIT
filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")
out="results/run_${v}_${p}${TAG:+.$TAG}.json"
npx promptfoo eval -c "$cfg" --no-cache --repeat "${REPEAT:-3}" ${filter[@]+"${filter[@]}"} -o "$out" >/dev/null 2>&1 || true
node scan.js "$out" "$WORLD"
node score.js "$out"
