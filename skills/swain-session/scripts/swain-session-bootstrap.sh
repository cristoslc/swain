#!/usr/bin/env bash
set +e  # Never fail hard — session bootstrap is a convenience, not a gate

# swain-session-bootstrap.sh — Consolidated session startup
#
# Replaces multi-step agent orchestration (tab naming + worktree detection +
# session.json loading) with a single script call that emits structured JSON.
#
# Usage:
#   swain-session-bootstrap.sh --auto                    # full bootstrap
#   swain-session-bootstrap.sh --path DIR --auto         # resolve from DIR
#   swain-session-bootstrap.sh --skip-worktree --auto    # omit worktree check
#
# Output: JSON to stdout with keys: tab, worktree, session, warnings
# See SPEC-172 for the full contract.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAB_NAME_SCRIPT="$SCRIPT_DIR/swain-tab-name.sh"
BOOKMARK_SCRIPT="$SCRIPT_DIR/swain-bookmark.sh"

# ─── Argument parsing ───
SWAIN_BOOTSTRAP_PATH=""
SKIP_WORKTREE=0
AUTO=0
WARNINGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      SWAIN_BOOTSTRAP_PATH="$2"
      shift 2
      ;;
    --skip-worktree)
      SKIP_WORKTREE=1
      shift
      ;;
    --auto)
      AUTO=1
      shift
      ;;
    --help|-h)
      echo "Usage: swain-session-bootstrap.sh [--path DIR] [--skip-worktree] --auto"
      echo ""
      echo "  --path DIR         Resolve git context from DIR (default: auto-detect)"
      echo "  --skip-worktree    Omit worktree isolation detection"
      echo "  --auto             Run in non-interactive mode"
      exit 0
      ;;
    *)
      shift
      ;;
  esac
done

# ─── Resolve repo root ───
if [[ -n "$SWAIN_BOOTSTRAP_PATH" ]]; then
  REPO_ROOT="$(git -C "$SWAIN_BOOTSTRAP_PATH" rev-parse --show-toplevel 2>/dev/null || echo "$SWAIN_BOOTSTRAP_PATH")"
else
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

# ─── Step 1: Tab naming (tmux only) ───
TAB_RESULT=""
if [[ -n "${TMUX:-}" ]]; then
  if [[ -f "$TAB_NAME_SCRIPT" ]]; then
    TAB_ARGS=()
    [[ -n "$SWAIN_BOOTSTRAP_PATH" ]] && TAB_ARGS+=(--path "$SWAIN_BOOTSTRAP_PATH")
    TAB_ARGS+=(--auto)
    TAB_RESULT=$(bash "$TAB_NAME_SCRIPT" "${TAB_ARGS[@]}" 2>/dev/null)
  else
    WARNINGS+=("tab-name script not found at $TAB_NAME_SCRIPT")
  fi
fi

# ─── Step 2: Worktree detection ───
WT_ISOLATED="false"
WT_PATH=""
WT_BRANCH=""

DETECT_PATH="${SWAIN_BOOTSTRAP_PATH:-$REPO_ROOT}"

if [[ "$SKIP_WORKTREE" -eq 0 ]]; then
  GIT_COMMON=$(git -C "$DETECT_PATH" rev-parse --git-common-dir 2>/dev/null)
  GIT_DIR=$(git -C "$DETECT_PATH" rev-parse --git-dir 2>/dev/null)

  if [[ -n "$GIT_COMMON" && -n "$GIT_DIR" && "$GIT_COMMON" != "$GIT_DIR" ]]; then
    WT_ISOLATED="true"
    WT_PATH="$DETECT_PATH"
    WT_BRANCH=$(git -C "$DETECT_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  else
    WT_ISOLATED="false"
    WT_BRANCH=$(git -C "$DETECT_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  fi
fi

# ─── Step 3: Session.json loading ───
SESSION_FILE="$REPO_ROOT/.agents/session.json"
SESSION_FOCUS=""
SESSION_BOOKMARK=""
SESSION_LAST_BRANCH=""

if [[ -f "$SESSION_FILE" ]] && command -v jq &>/dev/null; then
  SESSION_FOCUS=$(jq -r '.focus_lane // empty' "$SESSION_FILE" 2>/dev/null)
  SESSION_BOOKMARK=$(jq -r '.bookmark.note // empty' "$SESSION_FILE" 2>/dev/null)
  SESSION_LAST_BRANCH=$(jq -r '.lastBranch // empty' "$SESSION_FILE" 2>/dev/null)

  # Update lastBranch to current
  CURRENT_BRANCH=$(git -C "$DETECT_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  if [[ -n "$CURRENT_BRANCH" ]]; then
    jq --arg branch "$CURRENT_BRANCH" '.lastBranch = $branch' \
      "$SESSION_FILE" > "${SESSION_FILE}.tmp" 2>/dev/null \
      && mv "${SESSION_FILE}.tmp" "$SESSION_FILE" 2>/dev/null
  fi
elif [[ ! -f "$SESSION_FILE" ]]; then
  # Check for old global location and migrate
  _OLD_SLUG=$(echo "$REPO_ROOT" | tr '/' '-')
  _OLD_FILE="$HOME/.claude/projects/${_OLD_SLUG}/memory/session.json"
  if [[ -f "$_OLD_FILE" ]]; then
    mkdir -p "$(dirname "$SESSION_FILE")" 2>/dev/null
    cp "$_OLD_FILE" "$SESSION_FILE" 2>/dev/null
    WARNINGS+=("migrated session.json from old global location")
    # Re-read after migration
    if command -v jq &>/dev/null; then
      SESSION_FOCUS=$(jq -r '.focus_lane // empty' "$SESSION_FILE" 2>/dev/null)
      SESSION_BOOKMARK=$(jq -r '.bookmark.note // empty' "$SESSION_FILE" 2>/dev/null)
      SESSION_LAST_BRANCH=$(jq -r '.lastBranch // empty' "$SESSION_FILE" 2>/dev/null)
    fi
  fi
fi

# ─── Build JSON output ───
build_fallback_json() {
  # Minimal JSON construction without jq
  local out='{"worktree":{"isolated":'
  out+="$WT_ISOLATED"
  out+='},"session":{},"warnings":['
  local first=1
  for w in "${WARNINGS[@]}"; do
    [[ $first -eq 0 ]] && out+=","
    # Escape quotes in warning text
    out+="\"${w//\"/\\\"}\""
    first=0
  done
  out+=']}'
  echo "$out"
}

# Use jq if available and functional, fall back to manual construction
OUTPUT=""
if command -v jq &>/dev/null && jq -n '{}' &>/dev/null; then
  # Build warnings array
  WARNINGS_JSON="[]"
  for w in "${WARNINGS[@]}"; do
    WARNINGS_JSON=$(echo "$WARNINGS_JSON" | jq --arg w "$w" '. + [$w]')
  done

  OUTPUT=$(jq -n \
    --arg tab "$TAB_RESULT" \
    --arg wt_isolated "$WT_ISOLATED" \
    --arg wt_path "$WT_PATH" \
    --arg wt_branch "$WT_BRANCH" \
    --arg s_focus "$SESSION_FOCUS" \
    --arg s_bookmark "$SESSION_BOOKMARK" \
    --arg s_last_branch "$SESSION_LAST_BRANCH" \
    --argjson warnings "$WARNINGS_JSON" \
    '{
      worktree: {
        isolated: ($wt_isolated == "true"),
        path: (if $wt_path == "" then null else $wt_path end),
        branch: (if $wt_branch == "" then null else $wt_branch end)
      },
      session: {
        focus: (if $s_focus == "" then null else $s_focus end),
        bookmark: (if $s_bookmark == "" then null else $s_bookmark end),
        lastBranch: (if $s_last_branch == "" then null else $s_last_branch end)
      },
      warnings: $warnings
    }
    | if $tab != "" then .tab = $tab else . end' 2>/dev/null)
fi

# If jq failed or wasn't available, use the fallback
if [[ -z "$OUTPUT" ]]; then
  WARNINGS+=("jq not available — session fields may be incomplete")
  OUTPUT=$(build_fallback_json)
fi

echo "$OUTPUT"
