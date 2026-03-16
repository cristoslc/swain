#!/usr/bin/env bash
set +e  # Never fail hard — session naming is a convenience, not a gate

# swain-tab-name.sh — Set terminal tab/window title
#
# Usage:
#   swain-tab-name.sh "Custom Title"
#   swain-tab-name.sh --auto            # project @ branch (from settings)
#   swain-tab-name.sh --reset           # restore default title

SETTINGS_PROJECT="${SWAIN_SETTINGS:-$(git rev-parse --show-toplevel 2>/dev/null)/swain.settings.json}"
SETTINGS_USER="${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json"

# Read a setting with fallback: user settings override project settings
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

set_title() {
  local title="$1"
  local session_name="${2:-}"

  if [[ -n "$TMUX" ]]; then
    # tmux — rename the tmux window tab
    tmux set-window-option automatic-rename off 2>/dev/null || true
    tmux rename-window "$title" 2>/dev/null || true
    # tmux — rename the tmux session (project-level identity)
    if [[ -n "$session_name" ]]; then
      tmux rename-session "$session_name" 2>/dev/null || true
    fi
    # Propagate window name to the outer terminal (iTerm tab title).
    # set-titles-string uses #W (window name) so each window keeps its
    # own title — we only set the format once, rename-window does the rest.
    tmux set-option -g set-titles on 2>/dev/null || true
    tmux set-option -g set-titles-string "#W" 2>/dev/null || true
  elif [[ -t 1 ]]; then
    # Only emit escape sequences if stdout is a real terminal
    # (not piped through an agent subprocess)
    if [[ "$TERM_PROGRAM" == "iTerm.app" ]]; then
      printf '\033]1;%s\007' "$title"
    fi
    printf '\033]0;%s\007' "$title"
  else
    # Not in tmux and stdout is not a terminal — skip escape sequences
    :
  fi
}

install_hook() {
  # Install a tmux pane-focus-in hook so titles update on pane/window switch.
  # Uses the absolute path to this script so the hook survives across shells.
  # The hook is idempotent — re-running replaces the previous one.
  if [[ -z "$TMUX" ]]; then
    return
  fi
  local self
  self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
  tmux set-hook -g pane-focus-in "run-shell 'bash \"$self\" --auto'" 2>/dev/null || true
}

reset_title() {
  # Restore default title behavior and remove the pane-focus-in hook
  if [[ -n "$TMUX" ]]; then
    tmux set-window-option automatic-rename on 2>/dev/null || true
    tmux set-option -g set-titles-string "#W" 2>/dev/null || true
    tmux set-hook -gu pane-focus-in 2>/dev/null || true
  fi
  printf '\033]0;%s\007' "${SHELL##*/}"
}

auto_title() {
  local project branch fmt title pane_path

  # Resolve git context from the active tmux pane's working directory
  if [[ -n "$TMUX" ]]; then
    pane_path=$(tmux display-message -p '#{pane_current_path}' 2>/dev/null)
  fi
  pane_path="${pane_path:-$(pwd)}"

  local toplevel
  toplevel=$(git -C "$pane_path" rev-parse --show-toplevel 2>/dev/null) || true
  project=$(basename "${toplevel:-unknown}")
  branch=$(git -C "$pane_path" rev-parse --abbrev-ref HEAD 2>/dev/null) || true
  branch="${branch:-no-branch}"
  fmt=$(read_setting '.terminal.tabNameFormat' '{project} @ {branch}')

  title="${fmt//\{project\}/$project}"
  title="${title//\{branch\}/$branch}"

  set_title "$title" "$title"
  echo "$title"
}

case "${1:-}" in
  --auto)
    auto_title
    install_hook
    ;;
  --reset)
    reset_title
    echo "(reset)"
    ;;
  --help|-h)
    echo "Usage: swain-tab-name.sh [TITLE | --auto | --reset]"
    echo ""
    echo "  TITLE     Set a custom tab/window title"
    echo "  --auto    Generate title from git project + branch (uses settings)"
    echo "  --reset   Restore default terminal title"
    exit 0
    ;;
  "")
    auto_title
    ;;
  *)
    set_title "$1" "$1"
    echo "$1"
    ;;
esac
