#!/usr/bin/env bash
# One wrapper per model, because promptfoo's exec provider does NOT pass `config.env`.
# Relying on it meant both providers defaulted to sonnet and wrote to the same work tree, so
# the "haiku" rows were sonnet's output graded against a directory that never existed — a
# two-model comparison that was only ever one model. Explicit beats a silent default here.
MODEL_OVERRIDE=sonnet exec "$(dirname "$0")/claude-cli.sh" "$@"
