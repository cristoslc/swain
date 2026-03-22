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
    # Use hook-provided session name for targeting, fall back to display-message.
    # In run-shell contexts (hook callbacks), display-message resolves to the
    # *calling client's* session, not the hook's session. SWAIN_HOOK_SESSION is
    # expanded by tmux at hook fire time and gives us the correct target.
    local target_session="${SWAIN_HOOK_SESSION:-}"
    if [[ -z "$target_session" ]]; then
      target_session=$(tmux $TMUX_ARGS display-message -p '#{session_name}' 2>/dev/null)
    fi

    # Rename the tmux window tab — target the hook's session, not the "current" one
    tmux $TMUX_ARGS set-window-option ${target_session:+-t "$target_session"} automatic-rename off 2>/dev/null || true
    tmux $TMUX_ARGS rename-window ${target_session:+-t "$target_session"} "$title" 2>/dev/null || true
    # Rename the tmux session
    if [[ -n "$session_name" ]]; then
      tmux $TMUX_ARGS rename-session ${target_session:+-t "$target_session"} "$session_name" 2>/dev/null || true
    fi
    # Disable global set-titles — it broadcasts the focused client's window name
    # to ALL client terminals, causing inactive iTerm tabs to show the wrong name.
    # See SPEC-138.
    tmux $TMUX_ARGS set-option -g set-titles off 2>/dev/null || true
    # Instead, send OSC title escapes directly to THIS session's client terminal.
    local client_tty
    if [[ -n "$target_session" ]]; then
      client_tty=$(tmux $TMUX_ARGS list-clients -t "$target_session" -F '#{client_tty}' 2>/dev/null | head -1)
    fi
    if [[ -n "${client_tty:-}" && -w "$client_tty" ]]; then
      printf '\033]1;%s\007' "$title" > "$client_tty" 2>/dev/null || true
      printf '\033]0;%s\007' "$title" > "$client_tty" 2>/dev/null || true
    fi
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
  #
  # IMPORTANT: Pass hook context via env vars. tmux expands #{...} format strings
  # at hook fire time, giving the script the correct session/pane context. Without
  # this, the script's tmux commands resolve to the "current client" (whichever
  # session last had input), not the session where the hook fired. See SPEC-138.
  if [[ -z "$TMUX" ]]; then
    return
  fi
  local self
  self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
  tmux $TMUX_ARGS set-hook -w pane-focus-in "run-shell 'SWAIN_HOOK_SESSION=#{q:session_name} SWAIN_HOOK_PANE_PATH=#{q:pane_current_path} SWAIN_HOOK_PANE_ID=#{q:pane_id} bash \"$self\" --auto'" 2>/dev/null || true
}

reset_title() {
  # Restore default behavior: remove hook, clear @swain_path, re-enable auto-rename
  if [[ -n "$TMUX" ]]; then
    tmux $TMUX_ARGS set-window-option automatic-rename on 2>/dev/null || true
    tmux $TMUX_ARGS set-option -g set-titles off 2>/dev/null || true
    tmux $TMUX_ARGS set-hook -uw pane-focus-in 2>/dev/null || true
    tmux $TMUX_ARGS set-option -pu @swain_path 2>/dev/null || true
    tmux $TMUX_ARGS set-option -pu @swain_path_explicit 2>/dev/null || true
    # Reset the outer terminal title via this session's client only
    local session_name_resolved client_tty
    session_name_resolved=$(tmux $TMUX_ARGS display-message -p '#{session_name}' 2>/dev/null)
    if [[ -n "$session_name_resolved" ]]; then
      client_tty=$(tmux $TMUX_ARGS list-clients -t "$session_name_resolved" -F '#{client_tty}' 2>/dev/null | head -1)
    fi
    if [[ -n "${client_tty:-}" && -w "$client_tty" ]]; then
      printf '\033]0;%s\007' "${SHELL##*/}" > "$client_tty" 2>/dev/null || true
    fi
  fi
  printf '\033]0;%s\007' "${SHELL##*/}"
}

resolve_path() {
  # Resolution priority:
  #   1. --path arg (SWAIN_TAB_PATH) — explicit call-time override
  #   2. @swain_path_explicit=1 on pane — agent explicitly set a worktree path
  #   3. SWAIN_HOOK_PANE_PATH — provided by hook context (run-shell can't use pwd)
  #   4. pwd — normal interactive use; wins over stale @swain_path
  #   5. #{pane_current_path} — fallback when pwd is not in a git repo
  local path="$SWAIN_TAB_PATH"

  # Use @swain_path only when it was explicitly set via --path (agent/worktree use case)
  # Target the correct pane via SWAIN_HOOK_PANE_ID when available.
  if [[ -z "$path" && -n "$TMUX" ]]; then
    local pane_target="${SWAIN_HOOK_PANE_ID:+-t $SWAIN_HOOK_PANE_ID}"
    local explicit
    explicit=$(tmux $TMUX_ARGS show-options ${pane_target} -pqv @swain_path_explicit 2>/dev/null)
    if [[ "$explicit" == "1" ]]; then
      path=$(tmux $TMUX_ARGS show-options ${pane_target} -pqv @swain_path 2>/dev/null)
    fi
  fi

  # In hook context, use the pane path tmux expanded at fire time (pwd is wrong
  # inside run-shell — it's the tmux server's cwd, not the pane's).
  if [[ -z "$path" && -n "${SWAIN_HOOK_PANE_PATH:-}" ]]; then
    path="$SWAIN_HOOK_PANE_PATH"
  fi

  # Use pwd (only reliable in direct invocations, not hooks)
  if [[ -z "$path" ]]; then
    path="$(pwd)"
  fi

  # Fallback to tmux pane path if pwd isn't in a git repo
  if [[ -z "$(git -C "$path" rev-parse --git-common-dir 2>/dev/null)" && -n "$TMUX" ]]; then
    path="${SWAIN_HOOK_PANE_PATH:-$(tmux $TMUX_ARGS display-message -p '#{pane_current_path}' 2>/dev/null)}"
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

  # Store the resolved path as @swain_path on this pane.
  # Only mark it as explicit when --path was given in this invocation (agent/worktree case).
  # Without --path, we intentionally do NOT set @swain_path_explicit so that future
  # --auto calls will prefer pwd over the stored value (prevents stale override on cd).
  if [[ -n "$TMUX" ]]; then
    local pane_target="${SWAIN_HOOK_PANE_ID:+-t $SWAIN_HOOK_PANE_ID}"
    tmux $TMUX_ARGS set-option ${pane_target} -p @swain_path "$pane_path" 2>/dev/null || true
    if [[ -n "$SWAIN_TAB_PATH" ]]; then
      tmux $TMUX_ARGS set-option ${pane_target} -p @swain_path_explicit 1 2>/dev/null || true
    fi
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
