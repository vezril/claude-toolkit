#!/usr/bin/env bash
# Keyless exec provider: the Claude Code CLI, which authenticates from the keychain.
#
# `anthropic:claude-agent-sdk` is what this suite's config named first and it reports
# `Not logged in` here, which is why the review step has a mutation-tested suite and no
# scores. This suite has NO prior model runs, so choosing the provider now breaks no
# comparability with anything.
#
# **Only $1.** promptfoo passes three arguments and the third is a context JSON containing the
# test's ground truth. Reading anything else feeds the expected answer to the model and
# invalidates every score while looking like it worked.
set -uo pipefail
PROMPT="$1"
MODEL="${MODEL_OVERRIDE:?MODEL_OVERRIDE must be set — invoke provider/claude-<model>.sh}"

# No tools, and that is the production condition rather than a shortcut: the reviewer judges
# the material it was handed and cannot go and read the repository either.
claude -p "$PROMPT" --model "$MODEL" 2>"${TMPDIR:-/tmp}/delivery-review-$MODEL.stderr"
