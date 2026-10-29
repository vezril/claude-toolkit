#!/usr/bin/env bash
# Usage: [REPEAT=3] [FILTER=regex] [TAG=s2] ./run.sh <version> [model...]
#   models: sonnet (default, the pinned claude-sonnet-5-5), haiku (claude-haiku-5-5), haiku45, all
# Snapshots the three SKILL.md files to prompts/<skill>/<version>.md (the evidence of what
# was under test), runs the suite without cache on the chosen models, writes
# results/run_<version>_<models>[.<TAG>].json, and prints per-criterion scores.
# The committed config holds only the pinned model; others are added in a temp config.
set -euo pipefail
cd "$(dirname "$0")"
v="$1"; shift
models=("${@:-sonnet}"); [ "${models[0]}" = all ] && models=(haiku sonnet)
id_of() { case "$1" in haiku) echo claude-haiku-5-5;; sonnet) echo claude-sonnet-5-5;; haiku45) echo claude-haiku-4-5;; *) echo "unknown model: $1" >&2; exit 2;; esac; }
for s in intentional-daily intentional-weekly aversion-breaker; do
  mkdir -p "prompts/$s"; cp "../../skills/$s/SKILL.md" "prompts/$s/$v.md"
done
cfg=".run-$$.yaml"; trap 'rm -f "$cfg"' EXIT
{ sed -n '1,/^# Only the pinned model/p' promptfooconfig.yaml | sed '$d'
  echo "providers:"
  for m in "${models[@]}"; do printf '  - id: file://provider.js\n    label: %s\n    config: { model: %s }\n' "$m" "$(id_of "$m")"; done
  sed -n '/^evaluateOptions:/,$p' promptfooconfig.yaml; } > "$cfg"
args=(-c "$cfg" --no-cache --repeat "${REPEAT:-3}")
[ -n "${FILTER:-}" ] && args+=(--filter-pattern "$FILTER")
mkdir -p results
name=$(IFS=-; echo "${models[*]}")
out="results/run_${v}_${name}${TAG:+.$TAG}.json"
npx promptfoo eval "${args[@]}" -o "$out" >"results/.last.log" 2>&1 || true
node score.js "$out"
