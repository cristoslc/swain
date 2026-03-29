# swain shell launcher — claude / bash
# Runtime: Claude Code | Shell: bash
# Version: 4.1.0
#
# Launches Claude Code interactively with swain's recommended flags.
# Handles tmux wrapping: outside tmux, starts a new tmux session;
# inside tmux, launches directly in the current pane.
# When arguments are provided, they become the session purpose.

swain() {
  local _prompt='/swain-init'
  if [ $# -gt 0 ]; then
    _prompt="/swain-session Session purpose: $*"
  fi
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "claude --dangerously-skip-permissions '${_prompt}'"
  else
    claude --dangerously-skip-permissions "$_prompt"
  fi
}
