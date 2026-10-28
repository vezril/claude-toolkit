#!/usr/bin/env bash
#
# promptfoo `exec:` provider for the finch suite.
#
# WHY NOT anthropic:claude-agent-sdk (what every other suite in evals/ uses):
# that provider spawns the claude-code binary directly, so on a Bedrock-backed
# install it inherits no AWS credentials and every case errors with
# "Could not load AWS credentials". Going through the `claude` CLI on PATH uses
# whatever auth that CLI is already configured with — API key, Bedrock, or a
# corporate wrapper — so the suite is runnable without an ANTHROPIC_API_KEY.
#
# !! promptfoo passes THREE arguments to an exec provider: $1 is the rendered
# !! prompt, $2 is the options JSON, and $3 is the context JSON — and the context
# !! CONTAINS THE TEST'S ASSERTS. Forwarding "$@" or "$3" leaks the expected
# !! answers into the prompt and every score becomes meaningless while still
# !! looking green. Only ever pass $1.
#
# Tools are disabled: these cases are pure knowledge questions, and a model that
# can shell out could read skills/finch/SKILL.md off disk during the BASELINE arm
# and contaminate the comparison.
set -euo pipefail

exec claude -p "$1" \
  --model "${EVAL_MODEL:-sonnet}" \
  --allowedTools "" \
  --disallowedTools "Bash Read Write Edit Glob Grep WebFetch WebSearch Task"
