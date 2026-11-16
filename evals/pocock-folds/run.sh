#!/usr/bin/env bash
# Usage: [REPEAT=3] [TAG=s2] ./run.sh v1|v2 [sonnet|haiku|all]
# v1 = the four target skills as they were on main; v2 = with the Pocock folds. The temp world
# holds that version's skill folders under .skill/ so a skill can read its references.
set -euo pipefail
cd "$(dirname "$0")"
v="$1"; p="${2:-all}"
test -d "prompts/$v"
WORLD="$(mktemp -d)/world"; cp -R fixture "$WORLD"; mkdir -p "$WORLD/.skill"; cp -R "prompts/$v/." "$WORLD/.skill/"
cfg=".run.$$.yaml"
sed -e "s#__WORLD__#${WORLD}#g" -e "s#__V__#${v}#g" promptfooconfig.yaml > "$cfg"
trap 'rm -f "$cfg"; rm -rf "$(dirname "$WORLD")"' EXIT
filter=(); [ "$p" != all ] && filter=(--filter-providers "^${p}$")
out="results/run_${v}_${p}${TAG:+.$TAG}.json"
npx promptfoo eval -c "$cfg" --no-cache --repeat "${REPEAT:-3}" ${filter[@]+"${filter[@]}"} -o "$out" >/dev/null 2>&1 || true
node scan.js "$out" "$WORLD"
node score.js "$out"
