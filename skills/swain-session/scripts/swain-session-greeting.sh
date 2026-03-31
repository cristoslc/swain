#!/usr/bin/env bash
# swain-session-greeting.sh — SPEC-194: Fast-path session greeting
#
# Produces immediate session context without expensive operations.
# Runs bootstrap (tab naming + worktree detect + session.json) and
# adds lightweight preflight warnings. Does NOT invoke specgraph,
# GitHub API, or the full status dashboard.
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
BOOTSTRAP_SCRIPT="$SCRIPT_DIR/swain-session-bootstrap.sh"

JSON_MODE=0
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON_MODE=1; shift ;;
    --path) EXTRA_ARGS+=(--path "$2"); shift 2 ;;
    *) shift ;;
  esac
done

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# ─── Step 1: Run bootstrap (fast — ~400ms) ───
BOOTSTRAP_JSON=""
if [[ -f "$BOOTSTRAP_SCRIPT" ]]; then
  BOOTSTRAP_JSON=$(bash "$BOOTSTRAP_SCRIPT" "${EXTRA_ARGS[@]}" --auto 2>/dev/null)
fi

# Parse bootstrap output
if command -v jq &>/dev/null && [[ -n "$BOOTSTRAP_JSON" ]]; then
  BRANCH=$(echo "$BOOTSTRAP_JSON" | jq -r '.worktree.branch // empty' 2>/dev/null)
  ISOLATED=$(echo "$BOOTSTRAP_JSON" | jq -r '.worktree.isolated // false' 2>/dev/null)
  BOOKMARK=$(echo "$BOOTSTRAP_JSON" | jq -r '.session.bookmark // empty' 2>/dev/null)
  FOCUS=$(echo "$BOOTSTRAP_JSON" | jq -r '.session.focus // empty' 2>/dev/null)
  TAB=$(echo "$BOOTSTRAP_JSON" | jq -r '.tab // empty' 2>/dev/null)
  BOOT_WARNINGS=$(echo "$BOOTSTRAP_JSON" | jq -r '.warnings[]? // empty' 2>/dev/null)
else
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  ISOLATED="false"
  BOOKMARK=""
  FOCUS=""
  TAB=""
  BOOT_WARNINGS=""
fi

# ─── Step 2: Quick dirty state check ───
DIRTY="false"
PORCELAIN=$(git status --porcelain 2>/dev/null | head -1)
[[ -n "$PORCELAIN" ]] && DIRTY="true"

# ─── Step 3: Lightweight preflight warnings (critical only, no network) ───
WARNINGS=()

# Add bootstrap warnings
if [[ -n "$BOOT_WARNINGS" ]]; then
  while IFS= read -r w; do
    [[ -n "$w" ]] && WARNINGS+=("$w")
  done <<< "$BOOT_WARNINGS"
fi

# Check for stale tk locks (auto-heal, fast)
if [[ -d "$REPO_ROOT/.tickets/.locks" ]]; then
  stale_count=$(find "$REPO_ROOT/.tickets/.locks" -type d -mmin +60 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$stale_count" -gt 0 ]]; then
    find "$REPO_ROOT/.tickets/.locks" -type d -mmin +60 -exec rm -rf {} + 2>/dev/null
    WARNINGS+=("cleaned $stale_count stale tk lock(s)")
  fi
fi

# Check for crash debris (git lock files)
if [[ -f "$REPO_ROOT/.git/index.lock" ]]; then
  WARNINGS+=("stale git index.lock detected — may need manual removal")
fi

# Check .agents directory
if [[ ! -d "$REPO_ROOT/.agents" ]]; then
  mkdir -p "$REPO_ROOT/.agents"
  WARNINGS+=("created missing .agents/ directory")
fi

# ─── Step 4: Output ───
if [[ "$JSON_MODE" -eq 1 ]]; then
  # Build JSON output
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
    # Fallback minimal JSON
    echo "{\"greeting\":true,\"branch\":\"$BRANCH\",\"dirty\":$DIRTY}"
  fi
else
  # Human-readable output
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
