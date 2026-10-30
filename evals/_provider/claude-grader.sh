#!/usr/bin/env bash
#
# Shared promptfoo `exec:` provider for GRADING llm-rubric asserts.
#
# Separate from claude.sh because a grader must return ONLY a JSON object
# ({"reason","pass","score"}). `claude -p` tends to wrap it in prose or a fenced
# block, which promptfoo cannot parse -- it then reports the assert as failed and
# you get a suite that looks broken rather than a grade. So this extracts the
# first balanced JSON object from the reply and emits that alone.
#
# Same three-argument hazard as claude.sh: only $1 is forwarded.
set -euo pipefail

# Prompt on STDIN, not as an argument -- see the note in claude.sh: a rubric prompt
# quoting an output that starts with "-" would be parsed as a CLI option.
raw=$(printf '%s' "$1" | claude -p \
  --model "${GRADER_MODEL:-sonnet}" \
  --allowedTools "" \
  --disallowedTools "Bash Read Write Edit Glob Grep WebFetch WebSearch Task")

printf '%s' "$raw" | python3 -c '
import sys, json
s = sys.stdin.read()
# Strip fences, then scan for the first balanced {...} that parses as JSON.
start = s.find("{")
while start != -1:
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{": depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    print(json.dumps(json.loads(s[start:i+1]))); sys.exit(0)
                except json.JSONDecodeError:
                    break
    start = s.find("{", start + 1)
# No parseable object: fail loudly rather than silently scoring 0.
print(json.dumps({"pass": False, "score": 0,
                  "reason": "grader returned no parseable JSON: " + s[:300]}))
'
