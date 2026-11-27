#!/usr/bin/env bash
# The haiku wrapper. There is no default model in claude-cli.sh on purpose: a silent fallback
# once ran both providers as sonnet while the results claimed a two-model comparison.
set -uo pipefail
MODEL_OVERRIDE=haiku exec "$(dirname "$0")/claude-cli.sh" "$1"
