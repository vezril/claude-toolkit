#!/usr/bin/env bash
# Keyless exec provider: the Claude Code CLI, which authenticates from the keychain.
#
# **Only $1.** promptfoo passes three arguments — the rendered prompt, an options JSON, and a
# context JSON — and the context contains the test's ground truth. Reading anything but $1
# feeds the expected answer to the model and invalidates every score while looking like it
# worked. The prompt-edd skill calls this out by name; it is the single easiest way to produce
# a suite that measures nothing.
set -uo pipefail

PROMPT="$1"
# MODEL_OVERRIDE is set by the per-model wrapper. There is no default: a silent fallback is
# exactly what made both providers run as sonnet while the results claimed otherwise.
MODEL="${MODEL_OVERRIDE:?MODEL_OVERRIDE must be set — invoke provider/claude-<model>.sh}"

# The case comes from the FIRST LINE of the rendered prompt ("CASE: <id>"), not from provider
# env: promptfoo's exec provider did not pass `config.env` through, and the failure was a bare
# "Command failed" that said nothing. The prompt is the one thing it definitely renders.
CASE="$(printf '%s' "$PROMPT" | sed -n '1s/^CASE:[[:space:]]*//p')"
if [ -z "$CASE" ]; then
  echo "the prompt does not start with 'CASE: <id>'; cannot pick a fixture" >&2
  exit 1
fi
# The agent works on a COPY. Editing fixture/<case> in place made the grader compare that
# directory against itself, so `territory` read "0 files touched" no matter what the agent did
# and could never fail. Calibration could not catch it: calibration copies to a temp tree, so
# the harness and the real run disagreed about where work happens. They agree now.
# Keyed by case AND model: promptfoo runs providers in parallel, and both models sharing
# one directory produced `.work/case-01/case-01` — one provider's `cp` landing inside the
# other's tree. Every criterion then read nonsense, reporting files nobody had touched.
WORKDIR="${CLI_WORKDIR:-.work/$CASE-$MODEL}"

# Resolve against this script's suite root, so a relative CLI_WORKDIR does not depend on
# whatever directory promptfoo happens to invoke from.
SUITE="$(cd "$(dirname "$0")/.." && pwd)"
case "$WORKDIR" in /*) ABS="$WORKDIR" ;; *) ABS="$SUITE/${WORKDIR#./}" ;; esac

# Fresh copy per invocation, so a rerun never grades the previous run's work.
rm -rf "$ABS"
mkdir -p "$(dirname "$ABS")"
mkdir -p "$ABS"
# Copy the CONTENTS, so a directory that already exists cannot make the copy nest inside it.
cp -R "$SUITE/fixture/$CASE/." "$ABS/" || { echo "no fixture for $CASE" >&2; exit 1; }
cd "$ABS" || { echo "could not enter $ABS" >&2; exit 1; }

# Tools, scoped to this directory. The agent has to write test files to do the job at all;
# the grader then diffs the tree, so a write outside test territory is caught rather than
# prevented — which is the behaviour being measured.
# stdout is the model's answer and promptfoo grades it, so stderr cannot go there. It goes to
# a file rather than /dev/null: discarding it is what turned a missing model into a bare
# "Command failed" with nothing to read, and three runs were discarded before that was found.
claude -p "$PROMPT" \
  --model "$MODEL" \
  --allowedTools "Read,Grep,Glob,Bash,Edit,Write" \
  --permission-mode acceptEdits \
  2>"$ABS.stderr"
