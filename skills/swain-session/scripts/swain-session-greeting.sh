#!/usr/bin/env bash
# swain-session-greeting.sh — SPEC-194: Fast-path session greeting
#
# Produces immediate session context without expensive operations.
# Calls the preflight script for all read-only state, then applies
# lightweight mutations (tab naming, lock cleanup, .agents dir).
# Does NOT invoke specgraph, GitHub API, or the full status dashboard.
#
# Usage:
#   swain-session-greeting.sh              # human-readable output
#   swain-session-greeting.sh --json       # structured JSON
#   swain-session-greeting.sh --path DIR   # resolve from DIR
#
# Output (human-readable):
#   Branch, dirty state, bookmark, focus lane, warnings
#
# Output (JSON):
#   { greeting: true, branch, dirty, bookmark, focus, warnings[] }

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFLIGHT_SCRIPT="$SCRIPT_DIR/swain-session-preflight.sh"
TAB_NAME_SCRIPT="$SCRIPT_DIR/swain-tab-name.sh"

JSON_MODE=0
EXTRA_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON_MODE=1; shift ;;
    --path) EXTRA_PATH="$2"; shift 2 ;;
    *) shift ;;
  esac
done

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# ─── Step 1: Run preflight (single script, no subprocess chain) ───
PREFLIGHT_ARGS=(--repo-root "$REPO_ROOT")
[[ -n "$EXTRA_PATH" ]] && PREFLIGHT_ARGS+=(--path "$EXTRA_PATH")

PREFLIGHT_JSON=""
if [[ -f "$PREFLIGHT_SCRIPT" ]]; then
  PREFLIGHT_JSON=$(bash "$PREFLIGHT_SCRIPT" "${PREFLIGHT_ARGS[@]}" 2>/dev/null)
fi

# Parse preflight output
if command -v jq &>/dev/null && [[ -n "$PREFLIGHT_JSON" ]]; then
  BRANCH=$(echo "$PREFLIGHT_JSON" | jq -r '.git.branch // "unknown"' 2>/dev/null)
  DIRTY=$(echo "$PREFLIGHT_JSON" | jq -r 'if .git.dirty then "true" else "false" end' 2>/dev/null)
  ISOLATED=$(echo "$PREFLIGHT_JSON" | jq -r 'if .git.worktree.isolated then "true" else "false" end' 2>/dev/null)
  BOOKMARK=$(echo "$PREFLIGHT_JSON" | jq -r '.session.bookmark // empty' 2>/dev/null)
  FOCUS=$(echo "$PREFLIGHT_JSON" | jq -r '.session.focus // empty' 2>/dev/null)
  TAB_NAME=$(echo "$PREFLIGHT_JSON" | jq -r '.tmux.tab_name // empty' 2>/dev/null)
  # Collect preflight warnings (structured keys like "stale_tk_locks:3")
  PREFLIGHT_WARNINGS=$(echo "$PREFLIGHT_JSON" | jq -r '.warnings[]? // empty' 2>/dev/null)
else
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  DIRTY="false"
  [[ -n "$(git status --porcelain 2>/dev/null | head -1)" ]] && DIRTY="true"
  ISOLATED="false"
  BOOKMARK=""
  FOCUS=""
  TAB_NAME=""
  PREFLIGHT_WARNINGS=""
fi

# ─── Step 2: Apply mutations ───
WARNINGS=()

# Tab naming (tmux only) — uses the precomputed name, avoids full tab-name.sh resolution
if [[ -n "${TMUX:-}" && -n "$TAB_NAME" && -f "$TAB_NAME_SCRIPT" ]]; then
  TAB_ARGS=("$TAB_NAME")
  [[ -n "$EXTRA_PATH" ]] && TAB_ARGS=(--path "$EXTRA_PATH" --auto)
  TAB=$(bash "$TAB_NAME_SCRIPT" "${TAB_ARGS[@]}" 2>/dev/null)
else
  TAB="$TAB_NAME"
fi

# Clean stale tk locks
for w in $PREFLIGHT_WARNINGS; do
  case "$w" in
    stale_tk_locks:*)
      count="${w#stale_tk_locks:}"
      find "$REPO_ROOT/.tickets/.locks" -type d -mmin +60 -exec rm -rf {} + 2>/dev/null
      WARNINGS+=("cleaned $count stale tk lock(s)")
      ;;
    stale_git_index_lock)
      WARNINGS+=("stale git index.lock detected — may need manual removal")
      ;;
    missing_agents_dir)
      mkdir -p "$REPO_ROOT/.agents"
      WARNINGS+=("created missing .agents/ directory")
      ;;
    *)
      WARNINGS+=("$w")
      ;;
  esac
done

# Update lastBranch in session.json
SESSION_FILE="$REPO_ROOT/.agents/session.json"
if [[ -f "$SESSION_FILE" ]] && command -v jq &>/dev/null; then
  jq --arg branch "$BRANCH" '.lastBranch = $branch' \
    "$SESSION_FILE" > "${SESSION_FILE}.tmp" 2>/dev/null \
    && mv "${SESSION_FILE}.tmp" "$SESSION_FILE" 2>/dev/null
fi

# ─── Step 3: Output ───
if [[ "$JSON_MODE" -eq 1 ]]; then
  WARNINGS_JSON="[]"
  if command -v jq &>/dev/null; then
    for w in "${WARNINGS[@]}"; do
      WARNINGS_JSON=$(echo "$WARNINGS_JSON" | jq --arg w "$w" '. + [$w]')
    done
  fi

  if command -v jq &>/dev/null; then
    jq -n \
      --arg branch "$BRANCH" \
      --arg dirty "$DIRTY" \
      --arg bookmark "$BOOKMARK" \
      --arg focus "$FOCUS" \
      --arg isolated "$ISOLATED" \
      --arg tab "$TAB" \
      --argjson warnings "$WARNINGS_JSON" \
      '{
        greeting: true,
        branch: $branch,
        dirty: ($dirty == "true"),
        isolated: ($isolated == "true"),
        bookmark: (if $bookmark == "" then null else $bookmark end),
        focus: (if $focus == "" then null else $focus end),
        tab: (if $tab == "" then null else $tab end),
        warnings: $warnings
      }'
  else
    echo "{\"greeting\":true,\"branch\":\"$BRANCH\",\"dirty\":$DIRTY}"
  fi
else
  state="clean"
  [[ "$DIRTY" == "true" ]] && state="dirty"
  isolation=""
  [[ "$ISOLATED" == "true" ]] && isolation=" (worktree)"

  echo "Branch: $BRANCH${isolation} [$state]"

  if [[ -n "$BOOKMARK" ]]; then
    echo "Bookmark: $BOOKMARK"
  fi

  if [[ -n "$FOCUS" ]]; then
    echo "Focus: $FOCUS"
  fi

  for w in "${WARNINGS[@]}"; do
    echo "Warning: $w"
  done
fi
