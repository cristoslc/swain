#!/usr/bin/env bash
set -e

# swain-motd.sh — Dynamic status pane for swain-stage
#
# Runs in a loop, displaying project context and agent status.
# Shows an animated spinner when the agent is working.
#
# Reads project data from swain-status cache (status-cache.json) when
# available, falling back to direct git/ticket queries when the cache is
# absent or stale. Agent state (spinner/context) remains MOTD-owned
# via stage-status.json for real-time responsiveness.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJECT_NAME="$(basename "$REPO_ROOT")"
SETTINGS_PROJECT="$REPO_ROOT/swain.settings.json"
SETTINGS_USER="${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json"

# Memory directory for stage status
MEMORY_DIR="${SWAIN_MEMORY_DIR:-$HOME/.claude/projects/-Users-${USER}-Documents-code-$(basename "$REPO_ROOT")/memory}"
AGENT_STATUS_FILE="$MEMORY_DIR/stage-status.json"
STATUS_CACHE="$MEMORY_DIR/status-cache.json"

# Cache staleness threshold (seconds) — beyond this, fall back to direct queries
CACHE_STALE_THRESHOLD=300

# Spinner frames
BRAILLE_FRAMES=("⣾" "⣽" "⣻" "⢿" "⡿" "⣟" "⣯" "⣷")
DOTS_FRAMES=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
BAR_FRAMES=("[    ]" "[=   ]" "[==  ]" "[=== ]" "[ ===]" "[  ==]" "[   =]" "[    ]")

read_setting() {
  local key="$1"
  local default="$2"
  local val=""
  if [[ -f "$SETTINGS_USER" ]]; then
    val=$(jq -r "$key // empty" "$SETTINGS_USER" 2>/dev/null)
  fi
  if [[ -z "$val" && -f "$SETTINGS_PROJECT" ]]; then
    val=$(jq -r "$key // empty" "$SETTINGS_PROJECT" 2>/dev/null)
  fi
  echo "${val:-$default}"
}

REFRESH_INTERVAL=$(read_setting '.stage.motd.refreshInterval' '5')
SPINNER_STYLE=$(read_setting '.stage.motd.spinnerStyle' 'braille')

# Select spinner frames based on style
case "$SPINNER_STYLE" in
  dots)    FRAMES=("${DOTS_FRAMES[@]}") ;;
  bar)     FRAMES=("${BAR_FRAMES[@]}") ;;
  *)       FRAMES=("${BRAILLE_FRAMES[@]}") ;;  # braille is default
esac

FRAME_COUNT=${#FRAMES[@]}
frame_idx=0

# --- Status cache reader ---
# Returns true if status-cache.json exists and is fresh enough
cache_is_usable() {
  [[ -f "$STATUS_CACHE" ]] || return 1
  local cache_age
  if [[ "$(uname)" == "Darwin" ]]; then
    cache_age=$(( $(date +%s) - $(stat -f %m "$STATUS_CACHE") ))
  else
    cache_age=$(( $(date +%s) - $(stat -c %Y "$STATUS_CACHE") ))
  fi
  [[ "$cache_age" -lt "$CACHE_STALE_THRESHOLD" ]]
}

# Read a value from the status cache
cache_get() {
  local query="$1" default="$2"
  if cache_is_usable; then
    local val
    val=$(jq -r "$query // empty" "$STATUS_CACHE" 2>/dev/null) || true
    echo "${val:-$default}"
  else
    echo "$default"
  fi
}

# --- Data getters (cache-first with direct fallback) ---

get_branch() {
  if cache_is_usable; then
    cache_get '.git.branch' 'detached'
  else
    git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached"
  fi
}

get_dirty_state() {
  local staged=0 modified=0 untracked=0 parts=()

  if cache_is_usable; then
    local dirty
    dirty=$(cache_get '.git.dirty' 'false')
    if [[ "$dirty" != "true" ]]; then
      echo "clean"
      return
    fi
    # Use cached per-category counts (populated by swain-status collect_git)
    staged=$(cache_get '.git.staged' '0')
    modified=$(cache_get '.git.modified' '0')
    untracked=$(cache_get '.git.untracked' '0')
    [[ $staged -gt 0 ]] && parts+=("${staged} staged")
    [[ $modified -gt 0 ]] && parts+=("${modified} modified")
    [[ $untracked -gt 0 ]] && parts+=("${untracked} new")
    if [[ ${#parts[@]} -eq 0 ]]; then
      echo "clean"
    else
      local IFS=", "
      echo "${parts[*]}"
    fi
    return
  fi

  # No usable cache — fall back to direct git query
  local porcelain
  porcelain=$(git status --porcelain 2>/dev/null) || { echo "?"; return; }

  if [[ -z "$porcelain" ]]; then
    echo "clean"
    return
  fi

  while IFS= read -r line; do
    local x="${line:0:1}" y="${line:1:1}"
    if [[ "$x" == "?" ]]; then
      (( untracked++ ))
    else
      [[ "$x" != " " ]] && (( staged++ ))
      [[ "$y" != " " ]] && (( modified++ ))
    fi
  done <<< "$porcelain"

  [[ $staged -gt 0 ]] && parts+=("${staged} staged")
  [[ $modified -gt 0 ]] && parts+=("${modified} modified")
  [[ $untracked -gt 0 ]] && parts+=("${untracked} new")

  if [[ ${#parts[@]} -eq 0 ]]; then
    echo "clean"
  else
    local IFS=", "
    echo "${parts[*]}"
  fi
}

get_last_commit() {
  local msg age result
  if cache_is_usable; then
    age=$(cache_get '.git.lastCommit.age' 'unknown')
    msg=$(cache_get '.git.lastCommit.message' 'no commits')
  else
    msg=$(git log -1 --pretty=format:'%s' 2>/dev/null || echo "no commits")
    age=$(git log -1 --pretty=format:'%cr' 2>/dev/null || echo "unknown")
  fi
  # Truncate combined output to fit box (width - "last: " prefix = 34 chars)
  result="${age}: ${msg}"
  echo "${result:0:34}"
}

get_epic_line() {
  if cache_is_usable; then
    cache_get '
      .artifacts.epics | to_entries |
      if length > 0 then
        (.[0].value) as $e |
        "\($e.id) \($e.progress.done)/\($e.progress.total)"
      else "no active epics" end
    ' "no active epics"
  else
    echo "no cache"
  fi
}

get_task() {
  if cache_is_usable; then
    local task
    task=$(cache_get '
      if .tasks.inProgress | length > 0 then
        .tasks.inProgress[0] | "\(.id) \(.title)" | .[0:40]
      else "no active task" end
    ' "no active task")
    echo "$task"
  else
    # Fall back to ticket-query directly
    local tq_bin="" tickets_dir=""
    local skill_bin="$REPO_ROOT/skills/swain-do/bin/ticket-query"
    if [[ -x "$skill_bin" ]]; then
      tq_bin="$skill_bin"
    elif command -v ticket-query &>/dev/null; then
      tq_bin="ticket-query"
    fi
    if [[ -d "$REPO_ROOT/.tickets" ]]; then
      tickets_dir="$REPO_ROOT/.tickets"
    fi

    if [[ -n "$tq_bin" ]] && [[ -n "$tickets_dir" ]]; then
      local task
      task=$(TICKETS_DIR="$tickets_dir" "$tq_bin" '.status == "in_progress"' 2>/dev/null | jq -r '"\(.id) \(.title)"' 2>/dev/null | head -1)
      echo "${task:-no active task}"
    else
      echo "no task tracking"
    fi
  fi
}

get_ready_count() {
  if cache_is_usable; then
    cache_get '.artifacts.counts.ready' '0'
  else
    echo "?"
  fi
}

get_issue_count() {
  if cache_is_usable; then
    cache_get '.issues.assigned | length' '0'
  else
    echo "0"
  fi
}

# --- Agent status (always from stage-status.json, real-time) ---

get_agent_status() {
  if [[ -f "$AGENT_STATUS_FILE" ]]; then
    local state context
    state=$(jq -r '.state // "unknown"' "$AGENT_STATUS_FILE" 2>/dev/null)
    context=$(jq -r '.context // ""' "$AGENT_STATUS_FILE" 2>/dev/null)

    if [[ "$state" == "working" ]]; then
      echo "working|$context"
    else
      echo "idle|$context"
    fi
  else
    echo "idle|no status"
  fi
}

get_touched_files() {
  if [[ -f "$AGENT_STATUS_FILE" ]]; then
    local count
    count=$(jq -r '.touchedFiles | length // 0' "$AGENT_STATUS_FILE" 2>/dev/null)
    echo "$count"
  else
    echo "0"
  fi
}

# Box drawing
BOX_TL="┌" BOX_TR="┐" BOX_BL="└" BOX_BR="┘" BOX_H="─" BOX_V="│"

draw_line() {
  local content="$1"
  local width="$2"
  local padded
  padded=$(printf "%-${width}s" "$content")
  echo " ${BOX_V} ${padded} ${BOX_V}"
}

draw_separator() {
  local width="$1"
  local line=""
  for ((i = 0; i < width; i++)); do
    line+="$BOX_H"
  done
  echo " ${BOX_V}${line}${BOX_V}"  # use thin separator
}

draw_top() {
  local width="$1"
  local line=""
  for ((i = 0; i < width + 2; i++)); do
    line+="$BOX_H"
  done
  echo " ${BOX_TL}${line}${BOX_TR}"
}

draw_bottom() {
  local width="$1"
  local line=""
  for ((i = 0; i < width + 2; i++)); do
    line+="$BOX_H"
  done
  echo " ${BOX_BL}${line}${BOX_BR}"
}

render() {
  local width=40
  local branch dirty last_commit current_task agent_raw agent_state agent_ctx touched
  local epic_line ready_count issue_count

  branch=$(get_branch)
  dirty=$(get_dirty_state)
  last_commit=$(get_last_commit)
  current_task=$(get_task)
  epic_line=$(get_epic_line)
  ready_count=$(get_ready_count)
  issue_count=$(get_issue_count)
  agent_raw=$(get_agent_status)
  agent_state="${agent_raw%%|*}"
  agent_ctx="${agent_raw#*|}"
  touched=$(get_touched_files)

  # Truncate context to fit box
  if [[ ${#agent_ctx} -gt $((width - 6)) ]]; then
    agent_ctx="${agent_ctx:0:$((width - 9))}..."
  fi

  # Build agent status line with spinner
  local agent_line
  if [[ "$agent_state" == "working" ]]; then
    local spinner="${FRAMES[$frame_idx]}"
    agent_line="${spinner} agent working..."
    frame_idx=$(( (frame_idx + 1) % FRAME_COUNT ))
  else
    agent_line="● idle"
  fi

  # Clear screen and draw
  clear

  draw_top $width
  draw_line "$PROJECT_NAME @ $branch ($dirty)" $width
  draw_line "$agent_line" $width

  if [[ -n "$agent_ctx" && "$agent_ctx" != "no status" ]]; then
    draw_line "  $agent_ctx" $width
  fi

  draw_separator $width
  draw_line "epic: $epic_line" $width
  draw_line "task: $current_task" $width
  draw_line "ready: $ready_count actionable" $width
  draw_line "last: $last_commit" $width

  if [[ "$issue_count" -gt 0 ]]; then
    draw_line "issues: $issue_count assigned" $width
  fi

  if [[ "$touched" -gt 0 ]]; then
    draw_line "touched: $touched file(s)" $width
  fi

  draw_bottom $width
}

# --- Main loop ---

# Handle SIGTERM/SIGINT gracefully
trap 'echo ""; exit 0' TERM INT

# Refresh status cache on startup if stale (#12)
if ! cache_is_usable; then
  STATUS_SCRIPT="$(find "$REPO_ROOT" -path '*/swain-status/scripts/swain-status.sh' -print -quit 2>/dev/null)"
  if [[ -n "$STATUS_SCRIPT" ]]; then
    bash "$STATUS_SCRIPT" --refresh >/dev/null 2>&1 &
  fi
fi

# Fast refresh (0.2s) when agent is working, slow refresh otherwise
while true; do
  render

  agent_raw=$(get_agent_status)
  agent_state="${agent_raw%%|*}"

  if [[ "$agent_state" == "working" ]]; then
    sleep 0.2  # fast refresh for smooth animation
  else
    sleep "$REFRESH_INTERVAL"
  fi
done
