#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# python-tests scaffold — TEST sources only: tests/test_greeting.py. Never
# production sources. Reads the package name from src/ (the production
# sources are the source of truth) — run python-package first.
#
#   usage: scaffold.sh <project-name>
# ---------------------------------------------------------------------------
set -euo pipefail

NAME="${1:?usage: scaffold.sh <project-name>}"

SERVICE="${NAME%-service}"
SERVICE="${SERVICE%-svc}"
DEST="$PWD"

# The production sources are the source of truth for the package name.
PKG=""
for d in "$DEST"/src/*/; do
  [ -f "$d/__init__.py" ] && PKG="$(basename "$d")" && break
done
if [ -z "$PKG" ]; then
  echo "ERROR: no package found under $DEST/src — run python-package's scaffold first." >&2
  exit 4
fi
if [ -e "$DEST/tests" ]; then
  echo "ERROR: $DEST/tests already exists — refusing to overwrite." >&2
  exit 3
fi

mkdir -p "$DEST/tests"

cat > "$DEST/tests/test_greeting.py" <<'FILE'
from __PKG__.greeting import message


def test_message_greets_the_world_by_default() -> None:
    assert message() == "Hello, World!"


def test_message_greets_a_given_name() -> None:
    assert message("__SERVICE__") == "Hello, __SERVICE__!"
FILE

find "$DEST/tests" -type f -print0 \
  | xargs -0 perl -pi -e "
      s#__SERVICE__#${SERVICE}#g;
      s#__PKG__#${PKG}#g;
    "

echo "python-tests scaffold complete: $DEST/tests (package read from src: $PKG)"
