#!/usr/bin/env bash
# swain-session-archive.sh — Archive session.json for retro reconstruction
# SPEC-248 | EPIC-056
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ARCHIVE_DIR="${SWAIN_ARCHIVE_DIR:-$REPO_ROOT/.agents/session-archive}"

_ensure_dir() {
  mkdir -p "$ARCHIVE_DIR"
}

cmd_save() {
  local worktree_path="$1"
  local session_file="$worktree_path/.agents/session.json"

  if [ ! -f "$session_file" ]; then
    echo "No session.json in $worktree_path" >&2
    return 0  # graceful, not an error
  fi

  _ensure_dir

  # Generate session ID from branch name + timestamp
  local branch
  branch="$(git -C "$worktree_path" branch --show-current 2>/dev/null || echo "unknown")"
  local timestamp
  timestamp="$(date +%Y%m%dT%H%M%S)"
  local session_id="${branch//\//-}-${timestamp}"

  cp "$session_file" "$ARCHIVE_DIR/${session_id}.json"
  echo "Archived: $session_id"
}

cmd_get() {
  local session_id="$1"
  local archive_file="$ARCHIVE_DIR/${session_id}.json"
  local archive_gz="$ARCHIVE_DIR/${session_id}.json.gz"

  if [ -f "$archive_file" ]; then
    cat "$archive_file"
    return 0
  elif [ -f "$archive_gz" ]; then
    gzip -dc "$archive_gz"
    return 0
  fi

  echo "Not found: $session_id" >&2
  return 1
}

cmd_find() {
  local artifact_id="$1"
  _ensure_dir

  local found=false
  for f in "$ARCHIVE_DIR"/*.json "$ARCHIVE_DIR"/*.json.gz; do
    [ -f "$f" ] || continue

    local content
    if [[ "$f" == *.gz ]]; then
      content="$(gzip -dc "$f")"
    else
      content="$(cat "$f")"
    fi

    if echo "$content" | grep -q "$artifact_id"; then
      local name
      name="$(basename "$f")"
      echo "$name: $(echo "$content" | grep -o "\"note\":[^,}]*" | head -1)"
      found=true
    fi
  done

  if [ "$found" = false ]; then
    return 0  # empty output, no matches
  fi
}

cmd_compress() {
  _ensure_dir

  local now_epoch
  now_epoch="$(date +%s)"
  local seven_days=$((7 * 86400))

  for f in "$ARCHIVE_DIR"/*.json; do
    [ -f "$f" ] || continue
    # Skip if already has a .gz companion
    [ -f "${f}.gz" ] && continue

    local file_epoch
    file_epoch="$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo "$now_epoch")"
    local age=$((now_epoch - file_epoch))

    if [ "$age" -gt "$seven_days" ]; then
      gzip "$f"
      echo "Compressed: $(basename "$f")"
    fi
  done
}

# --- Main dispatch ---

cmd="${1:-help}"
shift || true

case "$cmd" in
  save)     cmd_save "$@" ;;
  get)      cmd_get "$@" ;;
  find)     cmd_find "$@" ;;
  compress) cmd_compress ;;
  help)
    echo "Usage: swain-session-archive.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  save <worktree-path>     Archive session.json from worktree"
    echo "  get <session-id>         Retrieve archived session"
    echo "  find <artifact-id>       Find sessions touching an artifact"
    echo "  compress                 Gzip archives older than 7 days"
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    exit 1
    ;;
esac
