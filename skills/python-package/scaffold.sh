#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# python-package scaffold — PRODUCTION sources only: src/<pkg>/ with the pure
# greeting module and the __main__ CLI entry point. Never tests.
#
#   usage: scaffold.sh <project-name> [package-name]
# ---------------------------------------------------------------------------
set -euo pipefail

NAME="${1:?usage: scaffold.sh <project-name> [package-name]}"

SERVICE="${NAME%-service}"
SERVICE="${SERVICE%-svc}"
PKG_DEFAULT="${SERVICE//-/_}"
PKG="${2:-$PKG_DEFAULT}"
DEST="$PWD"

if ! printf '%s' "$PKG" | grep -Eq '^[a-z_][a-z0-9_]*$'; then
  echo "ERROR: package name '$PKG' must be a valid python identifier." >&2
  exit 2
fi
if [ -e "$DEST/src/$PKG" ]; then
  echo "ERROR: $DEST/src/$PKG already exists — refusing to overwrite." >&2
  exit 3
fi

mkdir -p "$DEST/src/$PKG"

cat > "$DEST/src/$PKG/__init__.py" <<'FILE'
"""__SERVICE__ — pure domain logic lives here; keep I/O at the edges."""
FILE

cat > "$DEST/src/$PKG/greeting.py" <<'FILE'
"""Pure domain logic — no I/O, exhaustively unit-testable."""


def message(name: str = "World") -> str:
    """Build a greeting for the given name (defaults to "World")."""
    return f"Hello, {name}!"
FILE

cat > "$DEST/src/$PKG/__main__.py" <<'FILE'
"""CLI entry point: `python -m __PKG__` (also the Docker image's CMD)."""

from __PKG__.greeting import message


def main() -> None:
    print(message())


if __name__ == "__main__":
    main()
FILE

find "$DEST/src/$PKG" -type f -print0 \
  | xargs -0 perl -pi -e "
      s#__SERVICE__#${SERVICE}#g;
      s#__PKG__#${PKG}#g;
      s#__NAME__#${NAME}#g;
    "

echo "python-package scaffold complete: $DEST/src/$PKG"
