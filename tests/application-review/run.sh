#!/usr/bin/env bash
# Run every application-review test suite. Standard library only, no pytest.
#   ./tests/application-review/run.sh
# Regenerate the render golden files after an intentional wording change:
#   UPDATE_GOLDEN=1 ./tests/application-review/run.sh
set -uo pipefail
cd "$(dirname "$0")"

status=0
for suite in test_contracts test_years test_extract test_edges test_verdict test_render; do
  [ -f "$suite.py" ] || continue
  printf '\n=== %s\n' "$suite"
  # The output is captured rather than piped so the suite's own exit status is
  # what decides the result, not tail's.
  if output=$(python3 "$suite.py" 2>&1); then
    printf '%s\n' "$output" | tail -n 2
  else
    status=1
    printf '%s\n' "$output" | grep -E 'FAIL:|ERROR:|Traceback|^Ran|^FAILED' || printf '%s\n' "$output" | tail -n 20
  fi
done

printf '\n'
if [ "$status" -eq 0 ]; then
  echo "all application-review suites passed"
else
  echo "FAILURES above"
fi
exit "$status"
