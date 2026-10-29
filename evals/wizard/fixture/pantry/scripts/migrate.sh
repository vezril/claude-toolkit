#!/usr/bin/env bash
# Copies recipes_v1 into recipes, then drops recipes_v1. Irreversible.
# (Eval fixture: it only records that it ran.)
echo "MIGRATE $*" >> "${WIZARD_LOG:-/dev/null}"
echo "migrated"
