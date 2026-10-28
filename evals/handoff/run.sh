#!/usr/bin/env bash
# Usage: [REPEAT=3] [TAG=s2] ./run.sh v1 [sonnet|haiku|all]
# Runs prompts/prompt_<v>.md through the suite without cache, and writes the evidence to results/run_<v>_<provider>[.<TAG>].json. TAG names an
# extra sample of the same version so it doesn't overwrite the first.
#
# Isolation: the agent's working directory is a fresh copy of fixture/ under a temp
# dir, not fixture/ itself. Run in place, the agent could walk up out of the fixture:
# into this eval's own expected/ answers and prompts (Sonnet read one in an early v1
# run) and into the real constellation repos in ~/Code (Haiku did). Those runs were
# deleted and re-run. The generated config sits next to the real one so file:// paths
# still resolve, and names the prompt file directly, so runs of different versions
# can go in parallel.
set -euo pipefail
cd "$(dirname "$0")"
v="$1"; p="${2:-all}"
test -f "prompts/prompt_${v}.md"
world="$(mktemp -d)/constellation"
cp -R fixture "$world"
cfg=".run.$$.yaml"
sed -e "s#working_dir: ./fixture#working_dir: ${world}#" -e "s#file://prompts/current.md#file://prompts/prompt_${v}.md#" promptfooconfig.yaml > "$cfg"
trap 'rm -f "$cfg"; rm -rf "$(dirname "$world")"' EXIT
filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")
out="results/run_${v}_${p}${TAG:+.$TAG}.json"
npx promptfoo eval -c "$cfg" --no-cache --repeat "${REPEAT:-3}" ${filter[@]+"${filter[@]}"} -o "$out" >/dev/null 2>&1 || true
node score.js "$out"
