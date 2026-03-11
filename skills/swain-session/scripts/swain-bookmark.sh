#!/usr/bin/env bash
set -euo pipefail

# swain-bookmark.sh — Update the session bookmark in session.json
#
# Usage:
#   swain-bookmark.sh "note text"
#   swain-bookmark.sh "note text" --files file1.md file2.md
#   swain-bookmark.sh --clear
#
# Locates session.json in the Claude Code memory directory and updates
# the bookmark field atomically. Fails silently if jq is unavailable
# or session.json cannot be found — bookmarking is a convenience, not a gate.

# --- Locate session.json ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || REPO_ROOT="$PWD"
PROJECT_SLUG=$(echo "$REPO_ROOT" | tr '/' '-')
SESSION_FILE="${SWAIN_SESSION_FILE:-$HOME/.claude/projects/${PROJECT_SLUG}/memory/session.json}"

if [[ ! -f "$SESSION_FILE" ]]; then
  # Try find as fallback
  SESSION_FILE="$(find ~/.claude/projects/ -path '*/memory/session.json' -print -quit 2>/dev/null)" || true
fi

if [[ -z "$SESSION_FILE" || ! -f "$SESSION_FILE" ]]; then
  exit 0  # No session file — nothing to update
fi

if ! command -v jq &>/dev/null; then
  exit 0  # No jq — skip silently
fi

# --- Parse arguments ---
CLEAR=0
NOTE=""
FILES=()
PARSING_FILES=0

for arg in "$@"; do
  if [[ "$arg" == "--clear" ]]; then
    CLEAR=1
  elif [[ "$arg" == "--files" ]]; then
    PARSING_FILES=1
  elif [[ "$PARSING_FILES" -eq 1 ]]; then
    FILES+=("$arg")
  elif [[ -z "$NOTE" ]]; then
    NOTE="$arg"
  fi
done

# --- Update session.json ---
if [[ "$CLEAR" -eq 1 ]]; then
  jq 'del(.bookmark)' "$SESSION_FILE" > "$SESSION_FILE.tmp" \
    && mv "$SESSION_FILE.tmp" "$SESSION_FILE"
elif [[ -n "$NOTE" ]]; then
  TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if [[ "${#FILES[@]}" -gt 0 ]]; then
    FILES_JSON=$(printf '%s\n' "${FILES[@]}" | jq -R . | jq -s . 2>/dev/null || echo '[]')
    jq --arg note "$NOTE" --arg ts "$TIMESTAMP" --argjson files "$FILES_JSON" \
      '.bookmark = {note: $note, files: $files, timestamp: $ts}' \
      "$SESSION_FILE" > "$SESSION_FILE.tmp" \
      && mv "$SESSION_FILE.tmp" "$SESSION_FILE"
  else
    jq --arg note "$NOTE" --arg ts "$TIMESTAMP" \
      '.bookmark = {note: $note, timestamp: $ts}' \
      "$SESSION_FILE" > "$SESSION_FILE.tmp" \
      && mv "$SESSION_FILE.tmp" "$SESSION_FILE"
  fi
else
  echo "Usage: swain-bookmark.sh \"note text\" [--files file1 file2 ...]" >&2
  echo "       swain-bookmark.sh --clear" >&2
  exit 1
fi
