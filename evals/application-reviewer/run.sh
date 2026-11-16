#!/usr/bin/env bash
# Usage: [REPEAT=3] ./run.sh v1 [haiku|sonnet|all]
#        [REPEAT=1] ./run.sh baseline [haiku|sonnet|all]
#
# Copies prompts/prompt_<v>.md to prompts/current.md, runs the suite with the
# cache off, and writes the evidence to results/run_<v>_<provider>.json.
#
# Run the suites SEQUENTIALLY. Two at once hits the five-hour usage limit, and
# a partial run is worse than no run: keep it as
# results/run_<v>_<p>.DISCARDED-usage-limit-partial.json and say so in the log.
set -euo pipefail
cd "$(dirname "$0")"

v="${1:?usage: ./run.sh <version> [provider]}"
p="${2:-all}"

# The fixtures and the gold are generated. A stale tree would score the model
# against yesterday's cases, so this refuses to run rather than quietly lie.
echo "--- checking fixtures are current"
python3 fixtures/build.py --check

# The graders are calibrated before every run, because a miscalibrated grader
# produces numbers that look like evidence and are not.
echo "--- calibrating the graders"
python3 calibration/run.py >/dev/null

# promptfoo needs Node >= 22 and this machine's default is pinned to 18, so the
# run finds a new enough one rather than changing the global pin. NODE_BIN
# overrides it if neither of these is where yours lives.
if [ -z "${NODE_BIN:-}" ]; then
  current="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
  if [ "$current" -lt 22 ] 2>/dev/null; then
    for candidate in \
      "$(mise where node@22 2>/dev/null || true)/bin" \
      "$(ls -d "$HOME"/.local/share/mise/installs/node/2[2-9].* 2>/dev/null | sort -V | tail -1)/bin" \
      "$(ls -d "$HOME"/.nvm/versions/node/v2[2-9].* 2>/dev/null | sort -V | tail -1)/bin"
    do
      if [ -x "${candidate}/node" ]; then
        NODE_BIN="$candidate"
        break
      fi
    done
  fi
fi
if [ -n "${NODE_BIN:-}" ]; then
  PATH="${NODE_BIN}:${PATH}"
  export PATH
fi
echo "--- node $(node -v)"
case "$(node -p 'process.versions.node.split(".")[0]')" in
  1[0-9]|2[01]) echo "promptfoo needs Node >= 22; set NODE_BIN to a newer install" >&2; exit 1 ;;
esac

config=promptfooconfig.yaml
if [ "$v" = baseline ]; then
  config=promptfooconfig.baseline.yaml
else
  cp "prompts/prompt_${v}.md" prompts/current.md
fi

filter=()
[ "$p" != all ] && filter=(--filter-providers "^${p}$")
# PATTERN=case-01 ./run.sh v1 haiku  runs one case, for smoke-testing the
# harness cheaply before committing to a full run.
[ -n "${PATTERN:-}" ] && filter+=(--filter-pattern "$PATTERN")

mkdir -p results
out="results/run_${v}_${p}.json"
[ -n "${PATTERN:-}" ] && out="results/SMOKE_run_${v}_${p}.json"
echo "--- running ${config} (REPEAT=${REPEAT:-3}) -> ${out}"
# promptfoo's own progress output is noisy and its exit status is non-zero
# whenever any assert fails, which is normal here. VERBOSE=1 shows it when the
# harness itself is what's broken.
if [ -n "${VERBOSE:-}" ]; then
  npx promptfoo eval -c "$config" --no-cache --repeat "${REPEAT:-3}" \
    ${filter[@]+"${filter[@]}"} -o "$out" || true
else
  npx promptfoo eval -c "$config" --no-cache --repeat "${REPEAT:-3}" \
    ${filter[@]+"${filter[@]}"} -o "$out" >/tmp/promptfoo-appreview.log 2>&1 || true
fi

if [ ! -f "$out" ]; then
  echo "promptfoo wrote no results file. Last 30 lines of its output:" >&2
  tail -n 30 /tmp/promptfoo-appreview.log >&2 || true
  exit 1
fi

node score.js "$out"
