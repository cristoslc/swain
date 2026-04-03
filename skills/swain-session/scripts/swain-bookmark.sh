#!/usr/bin/env bash
set -euo pipefail

# swain-bookmark.sh — Unified bookmark management for swain
#
# Manages two kinds of bookmarks in session.json:
#   - Context bookmarks: free-text notes about what the operator is working on
#   - Worktree bookmarks: structured records of worktrees created during sessions
#
# Usage (context):
#   swain-bookmark.sh "note text"
#   swain-bookmark.sh "note text" --files file1.md file2.md
#   swain-bookmark.sh --clear
#
# Usage (worktree):
#   swain-bookmark.sh worktree add <path> <branch>
#   swain-bookmark.sh worktree remove <path>
#   swain-bookmark.sh worktree list
#   swain-bookmark.sh worktree prune
#
# Requires: jq (for worktree subcommands)

REPO_ROOT="${SWAIN_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
SESSION_FILE="${SWAIN_SESSION_FILE:-$REPO_ROOT/.agents/session.json}"

# --- Locate / migrate session.json ---
if [[ ! -f "$SESSION_FILE" ]]; then
  _OLD_SLUG=$(echo "$REPO_ROOT" | tr '/' '-')
  _OLD_FILE="$HOME/.claude/projects/${_OLD_SLUG}/memory/session.json"
  if [[ -f "$_OLD_FILE" ]]; then
    mkdir -p "$(dirname "$SESSION_FILE")"
    cp "$_OLD_FILE" "$SESSION_FILE"
  fi
fi

if [[ ! -f "$SESSION_FILE" ]]; then
  mkdir -p "$(dirname "$SESSION_FILE")"
  echo '{}' > "$SESSION_FILE"
fi

# ============================================================
# Worktree subcommands
# ============================================================

worktree_cmd() {
  local subcmd="${1:-}"
  case "$subcmd" in
    add)    worktree_add "$2" "$3" ;;
    remove) worktree_remove "$2" ;;
    list)   worktree_list ;;
    prune)  worktree_prune ;;
    *)      echo "Usage: swain-bookmark.sh worktree <add|remove|list|prune>" >&2; exit 1 ;;
  esac
}

worktree_add() {
  local wt_path="${1:-}"
  local wt_branch="${2:-}"

  if [[ -z "$wt_path" ]] || [[ -z "$wt_branch" ]]; then
    echo "Error: worktree add requires <path> and <branch>" >&2
    exit 1
  fi

  if ! command -v jq &>/dev/null; then
    echo "Error: jq is required for worktree operations" >&2
    exit 1
  fi

  # Skip trunk
  if [[ "$wt_path" == "$REPO_ROOT" ]]; then
    echo "Skipping trunk — trunk is never bookmarked."
    return 0
  fi

  # Get session_id
  local session_id
  session_id=$(jq -r '.session_id // empty' "$REPO_ROOT/.agents/session-state.json" 2>/dev/null || echo "")
  if [[ -z "$session_id" ]]; then
    session_id="no-session"
  fi

  local timestamp
  timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  # Build new worktree entry as JSON
  local new_entry
  new_entry=$(jq -n \
    --arg path "$wt_path" \
    --arg branch "$wt_branch" \
    --arg session_id "$session_id" \
    --arg last_active "$timestamp" \
    '{
      path: $path,
      branch: $branch,
      session_id: $session_id,
      last_active: $last_active
    }')

  # Remove any existing entry for this path, then append new one
  # Worktrees is an array; we filter out the matching path and append
  local tmp
  tmp="$(mktemp)"

  jq --argjson new_entry "$new_entry" \
    '.worktrees = (
       [ (.worktrees // [])[] | select(.path != $new_entry.path) ] +
       [$new_entry]
     )' \
    "$SESSION_FILE" > "$tmp" && mv "$tmp" "$SESSION_FILE"

  echo "Worktree bookmark added: $wt_path ($wt_branch)"
}

worktree_remove() {
  local wt_path="${1:-}"

  if [[ -z "$wt_path" ]]; then
    echo "Error: worktree remove requires <path>" >&2
    exit 1
  fi

  if ! command -v jq &>/dev/null; then
    echo "Error: jq is required for worktree operations" >&2
    exit 1
  fi

  local tmp
  tmp="$(mktemp)"

  jq --arg path "$wt_path" \
    '.worktrees = [ (.worktrees // [])[] | select(.path != $path) ]' \
    "$SESSION_FILE" > "$tmp" && mv "$tmp" "$SESSION_FILE"

  echo "Worktree bookmark removed: $wt_path"
}

worktree_list() {
  if ! command -v jq &>/dev/null; then
    echo "Error: jq is required for worktree operations" >&2
    exit 1
  fi

  local worktrees
  worktrees=$(jq -r '.worktrees | if type == "array" then . else [] end | .[] | "\(.path)|\(.branch)|\(.session_id)|\(.last_active)"' "$SESSION_FILE" 2>/dev/null || echo "")

  if [[ -z "$worktrees" ]]; then
    echo "No worktree bookmarks found."
  else
    while IFS='|' read -r path branch session_id last_active; do
      echo "$path|$branch|$session_id|$last_active"
    done <<< "$worktrees"
  fi
}

worktree_prune() {
  if ! command -v jq &>/dev/null; then
    echo "Error: jq is required for worktree operations" >&2
    exit 1
  fi

  local tmp
  tmp="$(mktemp)"
  local removed=0

  # Read all paths and check which directories still exist
  local paths
  IFS=$'\n' read -r -d '' -a paths < <(jq -r '.worktrees | if type == "array" then .[].path else [] end | select(. != "")' "$SESSION_FILE" 2>/dev/null | sort -u) || true

  if [[ ${#paths[@]} -eq 0 ]]; then
    echo "No worktree bookmarks to prune."
    return 0
  fi

  for wt_path in "${paths[@]}"; do
    if [[ ! -d "$wt_path" ]]; then
      jq --arg path "$wt_path" \
        '.worktrees = [ (.worktrees // [])[] | select(.path != $path) ]' \
        "$SESSION_FILE" > "$tmp" && mv "$tmp" "$SESSION_FILE"
      echo "Pruned stale worktree bookmark: $wt_path"
      ((removed++)) || true
    fi
  done

  echo "Pruned $removed stale worktree bookmark(s)."
}

# ============================================================
# Context bookmark (existing behavior)
# ============================================================

if [[ "${1:-}" == "worktree" ]]; then
  shift
  worktree_cmd "${1:-}" "${2:-}" "${3:-}"
  exit $?
fi

# --- Context bookmark: requires jq for note operations ---
if ! command -v jq &>/dev/null; then
  exit 0
fi

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
  echo "       swain-bookmark.sh worktree <add|remove|list|prune> [args]" >&2
  exit 1
fi
