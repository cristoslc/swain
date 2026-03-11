#!/usr/bin/env bash
set -e

# swain-motd.sh — Dynamic status pane for swain-stage
#
# Runs in a loop, displaying project context and agent status.
# Shows an animated spinner when the agent is working.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJECT_NAME="$(basename "$REPO_ROOT")"
SETTINGS_PROJECT="$REPO_ROOT/swain.settings.json"
SETTINGS_USER="${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json"

# Memory directory for stage status
MEMORY_DIR="${SWAIN_MEMORY_DIR:-$HOME/.claude/projects/-Users-${USER}-Documents-code-$(basename "$REPO_ROOT")/memory}"
STATUS_FILE="$MEMORY_DIR/stage-status.json"

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

get_branch() {
  git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached"
}

get_dirty_state() {
  if git diff --quiet HEAD 2>/dev/null; then
    echo "clean"
  else
    local count
    count=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
    echo "${count} changed"
  fi
}

get_last_commit() {
  local msg age
  msg=$(git log -1 --pretty=format:'%s' 2>/dev/null | cut -c1-40)
  age=$(git log -1 --pretty=format:'%cr' 2>/dev/null)
  echo "${age:-unknown}: ${msg:-no commits}"
}

get_bd_task() {
  if command -v bd &>/dev/null; then
    local task
    task=$(bd list --status in_progress --format '#{id} {title}' 2>/dev/null | head -1)
    echo "${task:-no active task}"
  else
    echo "bd not available"
  fi
}

get_agent_status() {
  if [[ -f "$STATUS_FILE" ]]; then
    local state context ts
    state=$(jq -r '.state // "unknown"' "$STATUS_FILE" 2>/dev/null)
    context=$(jq -r '.context // ""' "$STATUS_FILE" 2>/dev/null)
    ts=$(jq -r '.timestamp // ""' "$STATUS_FILE" 2>/dev/null)

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
  if [[ -f "$STATUS_FILE" ]]; then
    local count
    count=$(jq -r '.touchedFiles | length // 0' "$STATUS_FILE" 2>/dev/null)
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
  local branch dirty last_commit bd_task agent_raw agent_state agent_ctx touched

  branch=$(get_branch)
  dirty=$(get_dirty_state)
  last_commit=$(get_last_commit)
  bd_task=$(get_bd_task)
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
  draw_line "task: $bd_task" $width
  draw_line "last: $last_commit" $width

  if [[ "$touched" -gt 0 ]]; then
    draw_line "touched: $touched file(s)" $width
  fi

  draw_bottom $width
}

# --- Main loop ---

# Handle SIGTERM/SIGINT gracefully
trap 'echo ""; exit 0' TERM INT

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
