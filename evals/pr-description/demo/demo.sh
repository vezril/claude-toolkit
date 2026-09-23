#!/usr/bin/env bash
# Town hall demo driver for the pr-description suite, Haiku only.
# Usage: [REPEAT=3] [DEMO_DELAY_MS=0] ./demo.sh record|replay v2|v3
#   record  real Haiku calls; writes recordings/<v>.json (the replay source)
#   replay  no model calls; serves recordings/<v>.json, writes recordings/<v>.replay.json
# Scores print via ../score.js; `npx promptfoo view` shows the latest run in the browser.
set -euo pipefail
cd "$(dirname "$0")"
mode="$1"; v="$2"
cp "../prompts/prompt_${v}.md" skill.md
case "$mode" in
  record)
    npx promptfoo eval -c promptfooconfig.yaml --no-cache --no-table --repeat "${REPEAT:-3}" \
      -o "recordings/${v}.json" || true
    node ../score.js "recordings/${v}.json" ;;
  replay)
    DEMO_RECORDING="recordings/${v}.json" npx promptfoo eval -c promptfooconfig.yaml \
      -r file://replay.js --no-cache --no-table --repeat "${REPEAT:-3}" \
      -o "recordings/${v}.replay.json" || true
    node ../score.js "recordings/${v}.replay.json" ;;
  *) echo "usage: $0 record|replay v2|v3" >&2; exit 2 ;;
esac
