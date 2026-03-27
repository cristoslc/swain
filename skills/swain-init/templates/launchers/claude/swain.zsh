# swain shell launcher — claude / zsh
# Runtime: Claude Code | Shell: zsh
# Version: 4.0.0
#
# Launches Claude Code interactively with swain's recommended flags.
# Handles tmux wrapping: outside tmux, starts a new tmux session;
# inside tmux, launches directly in the current pane.

swain() {
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "claude --dangerously-skip-permissions '/swain-init'"
  else
    claude --dangerously-skip-permissions '/swain-init'
  fi
}
