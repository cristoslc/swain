#!/usr/bin/env bash
# Generates a unique worktree name: <context>-YYYYMMDD-HHmmss-XXXX
# Usage: swain-worktree-name.sh [context]
#   context — optional prefix (default: "session")

CONTEXT="${1:-session}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
SUFFIX="$(head -c 2 /dev/urandom | od -An -tx1 | tr -d ' \n')"

printf '%s-%s-%s\n' "$CONTEXT" "$TIMESTAMP" "$SUFFIX"
