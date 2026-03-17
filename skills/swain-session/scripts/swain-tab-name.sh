#!/usr/bin/env bash
set +e  # Never fail hard — session naming is a convenience, not a gate

# swain-tab-name.sh — Set terminal tab/window/session title
#
# Usage:
#   swain-tab-name.sh --auto                        # project @ branch (from settings)
#   swain-tab-name.sh --path DIR --auto             # resolve git context from DIR
#   swain-tab-name.sh --reset                       # restore defaults, remove hooks
#   swain-tab-name.sh "Custom Title"                # set a custom title
#
# See SPEC-056 and DESIGN-001 for the full interaction model.

# Allow socket override for testing or targeting a specific tmux server
TMUX_ARGS=""
if [[ -n "${SWAIN_TMUX_SOCKET:-}" ]]; then
  TMUX_ARGS="-S $SWAIN_TMUX_SOCKET"
  # Ensure TMUX-presence checks pass
  TMUX="${TMUX:-$SWAIN_TMUX_SOCKET,0,0}"
fi

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
    # Rename the tmux window tab
    tmux $TMUX_ARGS set-window-option automatic-rename off 2>/dev/null || true
    tmux $TMUX_ARGS rename-window "$title" 2>/dev/null || true
    # Rename the tmux session
    if [[ -n "$session_name" ]]; then
      tmux $TMUX_ARGS rename-session "$session_name" 2>/dev/null || true
    fi
    # Propagate window name to the outer terminal (iTerm tab title).
    tmux $TMUX_ARGS set-option -g set-titles on 2>/dev/null || true
    tmux $TMUX_ARGS set-option -g set-titles-string "#W" 2>/dev/null || true
  elif [[ -t 1 ]]; then
    if [[ "$TERM_PROGRAM" == "iTerm.app" ]]; then
      printf '\033]1;%s\007' "$title"
    fi
    printf '\033]0;%s\007' "$title"
  fi
}

install_hook() {
  # Install a per-window pane-focus-in hook so titles update on pane switch.
  # Per-window (set-hook -w) avoids interfering with other tmux sessions.
  # Idempotent — re-running replaces the previous hook.
  if [[ -z "$TMUX" ]]; then
    return
  fi
  local self
  self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
  tmux $TMUX_ARGS set-hook -w pane-focus-in "run-shell 'bash \"$self\" --auto'" 2>/dev/null || true
}

reset_title() {
  # Restore default behavior: remove hook, clear @swain_path, re-enable auto-rename
  if [[ -n "$TMUX" ]]; then
    tmux $TMUX_ARGS set-window-option automatic-rename on 2>/dev/null || true
    tmux $TMUX_ARGS set-option -g set-titles-string "#W" 2>/dev/null || true
    tmux $TMUX_ARGS set-hook -uw pane-focus-in 2>/dev/null || true
    tmux $TMUX_ARGS set-option -pu @swain_path 2>/dev/null || true
  fi
  printf '\033]0;%s\007' "${SHELL##*/}"
}

resolve_path() {
  # Resolution priority: --path arg > @swain_path (per-pane) > pwd > #{pane_current_path}
  local path="$SWAIN_TAB_PATH"

  # Try @swain_path from the current pane
  if [[ -z "$path" && -n "$TMUX" ]]; then
    path=$(tmux $TMUX_ARGS show-options -pqv @swain_path 2>/dev/null)
  fi

  # Try pwd
  if [[ -z "$path" ]]; then
    path="$(pwd)"
  fi

  # Fallback to tmux pane path if pwd isn't in a git repo
  if [[ -z "$(git -C "$path" rev-parse --git-common-dir 2>/dev/null)" && -n "$TMUX" ]]; then
    path=$(tmux $TMUX_ARGS display-message -p '#{pane_current_path}' 2>/dev/null)
    path="${path:-$(pwd)}"
  fi

  echo "$path"
}

auto_title() {
  local project branch fmt title pane_path

  pane_path=$(resolve_path)

  # Use --git-common-dir to resolve the main repo root (not the worktree root)
  local common_dir repo_root
  common_dir=$(git -C "$pane_path" rev-parse --git-common-dir 2>/dev/null) || true
  if [[ -n "$common_dir" ]]; then
    repo_root=$(cd "$pane_path" && cd "$common_dir/.." && pwd 2>/dev/null) || true
  fi
  project=$(basename "${repo_root:-unknown}")
  branch=$(git -C "$pane_path" rev-parse --abbrev-ref HEAD 2>/dev/null) || true
  branch="${branch:-no-branch}"
  fmt=$(read_setting '.terminal.tabNameFormat' '{project} @ {branch}')

  title="${fmt//\{project\}/$project}"
  title="${title//\{branch\}/$branch}"

  set_title "$title" "$title"

  # Store the resolved path as @swain_path on this pane
  if [[ -n "$TMUX" ]]; then
    tmux $TMUX_ARGS set-option -p @swain_path "$pane_path" 2>/dev/null || true
  fi

  echo "$title"
}

# ─── Argument parsing ───
SWAIN_TAB_PATH=""
args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      SWAIN_TAB_PATH="$2"
      shift 2
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

case "${args[0]:-}" in
  --auto)
    auto_title
    install_hook
    ;;
  --reset)
    reset_title
    echo "(reset)"
    ;;
  --help|-h)
    echo "Usage: swain-tab-name.sh [--path DIR] [TITLE | --auto | --reset]"
    echo ""
    echo "  --path DIR  Resolve git context from DIR (for agents in worktrees)"
    echo "  TITLE       Set a custom tab/window title"
    echo "  --auto      Generate title from git project + branch (uses settings)"
    echo "  --reset     Restore default terminal title"
    exit 0
    ;;
  "")
    auto_title
    ;;
  *)
    set_title "${args[0]}" "${args[0]}"
    echo "${args[0]}"
    ;;
esac
