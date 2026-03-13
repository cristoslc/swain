#!/usr/bin/env bash
set -e

# swain-stage.sh — Tmux workspace manager for swain
#
# Subcommands:
#   layout <name>                  Apply a layout preset (review, browse, focus)
#   pane <type> [args...]          Open a pane (editor, browser, motd, shell)
#   motd start|stop|update <ctx>   Manage the MOTD status pane
#   close <position>               Close a pane by position (right, bottom, top)
#   status                         Show current tmux layout info
#   reset                          Kill all panes except the current one

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LAYOUTS_DIR="$SKILL_DIR/references/layouts"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SETTINGS_PROJECT="$REPO_ROOT/swain.settings.json"
SETTINGS_USER="${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json"

# Memory directory for stage status (Claude Code project memory — slug derived from repo path)
_PROJECT_SLUG=$(echo "$REPO_ROOT" | tr '/' '-')
MEMORY_DIR="${SWAIN_MEMORY_DIR:-$HOME/.claude/projects/${_PROJECT_SLUG}/memory}"

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

require_tmux() {
  if [[ -z "$TMUX" ]]; then
    echo "error: swain-stage requires tmux (not in a tmux session)" >&2
    exit 1
  fi
}

## Tool preference lists — first entry is recommended, rest are fallbacks
EDITOR_PREFS=(micro helix nano vim vi)
BROWSER_PREFS=(yazi nnn ranger mc)

detect_pkg_manager() {
  if command -v brew &>/dev/null; then echo "brew"
  elif command -v apt &>/dev/null; then echo "apt"
  elif command -v snap &>/dev/null; then echo "snap"
  elif command -v cargo &>/dev/null; then echo "cargo"
  elif command -v pip &>/dev/null; then echo "pip"
  else echo "curl"
  fi
}

# Select the first pane (respects pane-base-index setting)
select_first_pane() {
  tmux select-pane -t "$(tmux list-panes -F '#{pane_index}' | head -1)"
}

# Returns install command for a tool on the detected package manager.
# Uses a function instead of associative arrays for bash 3 compatibility (macOS).
install_hint() {
  local tool="$1"
  local pm="$2"
  case "${tool}:${pm}" in
    micro:brew)  echo "brew install micro" ;;
    micro:apt)   echo "apt install micro" ;;
    micro:snap)  echo "snap install micro" ;;
    micro:curl)  echo "curl https://getmic.ro | bash" ;;
    helix:brew)  echo "brew install helix" ;;
    helix:apt)   echo "add-apt-repository ppa:maveonair/helix-editor && apt install helix" ;;
    yazi:brew)   echo "brew install yazi" ;;
    yazi:cargo)  echo "cargo install --locked yazi-fm" ;;
    nnn:brew)    echo "brew install nnn" ;;
    nnn:apt)     echo "apt install nnn" ;;
    ranger:brew) echo "brew install ranger" ;;
    ranger:pip)  echo "pip install ranger-fm" ;;
    mc:brew)     echo "brew install mc" ;;
    mc:apt)      echo "apt install mc" ;;
    *)           echo "" ;;
  esac
}

# Resolve a tool from a preference list.
# If the configured value is missing, offer to install it.
# If "auto", walk the list and suggest the recommended (first) entry.
# Returns the resolved command on stdout.
# Prints install suggestions to stderr so they're visible but don't pollute stdout.
resolve_tool() {
  local setting="$1"
  local setting_key="$2"
  shift 2
  local prefs=("$@")
  local recommended="${prefs[0]}"
  local pkg_mgr

  # Explicit setting (not "auto")
  if [[ "$setting" != "auto" ]]; then
    if command -v "$setting" &>/dev/null; then
      echo "$setting"
      return
    fi
    # Configured tool is missing — suggest install
    pkg_mgr=$(detect_pkg_manager)
    local hint
    hint=$(install_hint "$setting" "$pkg_mgr")
    echo >&2 ""
    echo >&2 "  swain-stage: '$setting' is configured but not installed."
    if [[ -n "$hint" ]]; then
      echo >&2 "  Install it with:  $hint"
    else
      echo >&2 "  Install '$setting' using your package manager."
    fi
    echo >&2 "  Falling back to auto-detection..."
    echo >&2 ""
  fi

  # Auto-detection: walk the preference list
  for cmd in "${prefs[@]}"; do
    if command -v "$cmd" &>/dev/null; then
      # If we found something but it's not the recommended tool, suggest upgrading
      if [[ "$cmd" != "$recommended" ]]; then
        pkg_mgr=$(detect_pkg_manager)
        local hint
        hint=$(install_hint "$recommended" "$pkg_mgr")
        echo >&2 ""
        echo >&2 "  swain-stage: using '$cmd' (recommended: '$recommended')."
        if [[ -n "$hint" ]]; then
          echo >&2 "  Install the recommended tool:  $hint"
        fi
        echo >&2 "  Or set your preference in swain.settings.json:  \"$setting_key\": \"$cmd\""
        echo >&2 ""
      fi
      echo "$cmd"
      return
    fi
  done

  # Nothing found at all — suggest installing the recommended tool
  pkg_mgr=$(detect_pkg_manager)
  local hint
  hint=$(install_hint "$recommended" "$pkg_mgr")
  echo >&2 ""
  echo >&2 "  swain-stage: no supported tool found (tried: ${prefs[*]})."
  if [[ -n "$hint" ]]; then
    echo >&2 "  Install the recommended tool:  $hint"
  else
    echo >&2 "  Install '$recommended' using your package manager."
  fi
  echo >&2 ""

  # Return empty — callers should handle gracefully
  return 1
}

get_editor() {
  local setting
  setting=$(read_setting '.editor' 'auto')
  resolve_tool "$setting" "editor" "${EDITOR_PREFS[@]}" || echo "${EDITOR:-vi}"
}

get_file_browser() {
  local setting
  setting=$(read_setting '.fileBrowser' 'auto')
  resolve_tool "$setting" "fileBrowser" "${BROWSER_PREFS[@]}" || echo "ls"
}

get_file_browser_command() {
  local browser
  browser=$(get_file_browser)

  if [[ "$browser" == "yazi" ]]; then
    printf 'env XDG_CONFIG_HOME=%q %q' "$SKILL_DIR/references" "$browser"
  else
    printf '%q' "$browser"
  fi
}

# --- Subcommands ---

cmd_layout() {
  require_tmux
  local name="${1:-$(read_setting '.stage.defaultLayout' 'focus')}"
  local layout_file="$LAYOUTS_DIR/${name}.json"

  # Check for user override in settings
  local override
  override=$(jq -r ".stage.layouts.\"$name\" // empty" "$SETTINGS_PROJECT" 2>/dev/null || true)
  if [[ -n "$override" ]]; then
    layout_file=$(mktemp)
    echo "$override" > "$layout_file"
    trap "rm -f '$layout_file'" EXIT
  fi

  if [[ ! -f "$layout_file" ]]; then
    echo "error: unknown layout '$name'. Available: $(ls "$LAYOUTS_DIR" | sed 's/\.json$//' | tr '\n' ' ')" >&2
    exit 1
  fi

  # Reset to single pane first
  cmd_reset 2>/dev/null || true

  # Read layout and create panes
  local pane_count
  pane_count=$(jq '.panes | length' "$layout_file")

  for ((i = 1; i < pane_count; i++)); do
    local position size command pane_type
    position=$(jq -r ".panes[$i].position" "$layout_file")
    size=$(jq -r ".panes[$i].size // \"30%\"" "$layout_file")
    pane_type=$(jq -r ".panes[$i].type // \"shell\"" "$layout_file")
    command=$(jq -r ".panes[$i].command // \"\"" "$layout_file")

    # Resolve placeholders in command
    command="${command//\{editor\}/$(get_editor)}"
    command="${command//\{fileBrowser\}/$(get_file_browser_command)}"
    command="${command//\{scriptDir\}/$SCRIPT_DIR}"
    command="${command//\{repoRoot\}/$REPO_ROOT}"

    local split_flag="-h"  # horizontal split (side by side)
    case "$position" in
      right)        split_flag="-h" ;;
      bottom|below) split_flag="-v" ;;
      left)         split_flag="-hb" ;;
      top|above)    split_flag="-vb" ;;
    esac

    if [[ -n "$command" ]]; then
      tmux split-window $split_flag -l "$size" "$command"
    else
      tmux split-window $split_flag -l "$size"
    fi
  done

  # Return focus to the first (main) pane
  select_first_pane

  echo "layout: $name applied"
}

cmd_pane() {
  require_tmux
  local pane_type="${1:-shell}"
  shift || true

  case "$pane_type" in
    editor)
      local files=("$@")
      local editor
      editor=$(get_editor)
      if [[ ${#files[@]} -eq 0 ]]; then
        tmux split-window -h -l 40% "$editor"
      else
        tmux split-window -h -l 40% "$editor ${files[*]}"
      fi
      select_first_pane
      echo "pane: editor opened"
      ;;
    browser)
      local dir="${1:-$REPO_ROOT}"
      local browser
      browser=$(get_file_browser_command)
      tmux split-window -h -l 40% "$browser $dir"
      select_first_pane
      echo "pane: file browser opened"
      ;;
    motd)
      tmux split-window -v -l 12 "uv run $SCRIPT_DIR/swain-motd.py"
      select_first_pane
      echo "pane: motd started"
      ;;
    shell)
      tmux split-window -h -l 40%
      select_first_pane
      echo "pane: shell opened"
      ;;
    *)
      echo "error: unknown pane type '$pane_type'. Available: editor, browser, motd, shell" >&2
      exit 1
      ;;
  esac
}

cmd_motd() {
  local action="${1:-start}"
  shift || true

  case "$action" in
    start)
      require_tmux
      cmd_pane motd
      ;;
    stop)
      require_tmux
      # Find and kill any pane running swain-motd.sh
      local panes
      panes=$(tmux list-panes -F '#{pane_id} #{pane_current_command}' 2>/dev/null || true)
      echo "$panes" | while read -r pane_id cmd; do
        if [[ "$cmd" == *"swain-motd"* ]]; then
          tmux kill-pane -t "$pane_id" 2>/dev/null || true
        fi
      done
      echo "motd: stopped"
      ;;
    update)
      local context="$*"
      mkdir -p "$MEMORY_DIR"
      local status_file="$MEMORY_DIR/stage-status.json"
      local state="working"
      if [[ "$context" == "idle" || "$context" == "done" ]]; then
        state="idle"
        context="${context#idle }"
        context="${context#done }"
      fi
      jq -n \
        --arg state "$state" \
        --arg context "$context" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{state: $state, context: $context, touchedFiles: [], timestamp: $timestamp}' \
        > "$status_file"
      echo "motd: updated ($state: $context)"
      ;;
    *)
      echo "error: unknown motd action '$action'. Available: start, stop, update <context>" >&2
      exit 1
      ;;
  esac
}

cmd_close() {
  require_tmux
  local position="${1:-right}"

  # Get list of panes sorted by position
  local pane_count
  pane_count=$(tmux list-panes | wc -l | tr -d ' ')

  if [[ "$pane_count" -le 1 ]]; then
    echo "warning: only one pane remaining, nothing to close" >&2
    return 0
  fi

  case "$position" in
    right)
      # Kill the last horizontal pane
      tmux select-pane -t "{right}" 2>/dev/null && tmux kill-pane
      ;;
    bottom)
      tmux select-pane -t "{bottom}" 2>/dev/null && tmux kill-pane
      ;;
    left)
      tmux select-pane -t "{left}" 2>/dev/null && tmux kill-pane
      ;;
    top)
      tmux select-pane -t "{top}" 2>/dev/null && tmux kill-pane
      ;;
    all)
      cmd_reset
      return
      ;;
    *)
      echo "error: unknown position '$position'. Available: right, bottom, left, top, all" >&2
      exit 1
      ;;
  esac

  select_first_pane
  echo "closed: $position pane"
}

cmd_reset() {
  require_tmux
  # Kill all panes except the current one
  local current
  current=$(tmux display-message -p '#{pane_id}')
  tmux list-panes -F '#{pane_id}' | while read -r pane_id; do
    if [[ "$pane_id" != "$current" ]]; then
      tmux kill-pane -t "$pane_id" 2>/dev/null || true
    fi
  done
  echo "reset: all extra panes closed"
}

cmd_status() {
  if [[ -z "$TMUX" ]]; then
    echo "tmux: not in session"
    return 0
  fi

  echo "=== swain-stage status ==="
  echo ""
  echo "session: $(tmux display-message -p '#{session_name}')"
  echo "window:  $(tmux display-message -p '#{window_name}')"
  echo "panes:   $(tmux list-panes | wc -l | tr -d ' ')"
  echo ""
  tmux list-panes -F '  #{pane_index}: #{pane_width}x#{pane_height} #{pane_current_command}'
  echo ""
  echo "editor:       $(get_editor)"
  echo "file browser: $(get_file_browser)"
  echo "default layout: $(read_setting '.stage.defaultLayout' 'focus')"
}

# --- Main dispatch ---

case "${1:-}" in
  layout)  shift; cmd_layout "$@" ;;
  pane)    shift; cmd_pane "$@" ;;
  motd)    shift; cmd_motd "$@" ;;
  close)   shift; cmd_close "$@" ;;
  reset)   cmd_reset ;;
  status)  cmd_status ;;
  --help|-h)
    echo "Usage: swain-stage.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  layout <name>              Apply a layout preset (review, browse, focus)"
    echo "  pane <type> [args...]      Open a pane (editor, browser, motd, shell)"
    echo "  motd start|stop|update     Manage the MOTD status pane"
    echo "  close <position>           Close a pane (right, bottom, left, top, all)"
    echo "  reset                      Kill all panes except current"
    echo "  status                     Show current layout info"
    exit 0
    ;;
  *)
    echo "error: unknown command '${1:-}'. Run with --help for usage." >&2
    exit 1
    ;;
esac
