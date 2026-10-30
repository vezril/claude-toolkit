#!/usr/bin/env bash
#
# Shared promptfoo `exec:` provider for GENERATION, used by the *.local.yaml configs.
#
# WHY: the suites' default provider is anthropic:claude-agent-sdk, which spawns the
# claude-code binary directly. On a Bedrock-backed install that subprocess inherits
# no AWS credentials and every case errors with "Could not load AWS credentials".
# Going through the `claude` CLI uses whatever auth it is already configured with,
# so the suites are runnable without an ANTHROPIC_API_KEY. CI still uses the
# agent-sdk configs; these locals are not auto-discovered.
#
# !! promptfoo passes THREE args: $1 rendered prompt, $2 options JSON, $3 context
# !! JSON -- and the context CONTAINS THE TEST'S ASSERTS. Forwarding "$@" or "$3"
# !! leaks the expected answers into the prompt and every score goes green while
# !! measuring nothing. Only ever pass $1.
#
# Tools are disabled: a baseline-arm model with Read could pull the SKILL.md off
# disk and contaminate the no-skill comparison.
# The prompt goes in on STDIN, never as a positional argument. A rendered prompt
# that starts with "-" is otherwise parsed as a CLI option: cross-examine's begins
# with the "---" of an agent file's YAML frontmatter and the call died with
# `error: unknown option '---'`. Suites whose template puts prose before the
# injected file happen to escape this, which makes a structural bug look
# suite-specific. Stdin also sidesteps ARG_MAX on large prompts.
set -euo pipefail

printf '%s' "$1" | claude -p \
  --model "${EVAL_MODEL:-sonnet}" \
  --allowedTools "" \
  --disallowedTools "Bash Read Write Edit Glob Grep WebFetch WebSearch Task"
