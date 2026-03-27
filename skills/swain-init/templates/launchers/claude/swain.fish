# swain shell launcher — claude / fish
# Runtime: Claude Code | Shell: fish
# Version: 4.0.0
#
# Launches Claude Code interactively with swain's recommended flags.
# Handles tmux wrapping: outside tmux, starts a new tmux session;
# inside tmux, launches directly in the current pane.

function swain
    if not set -q TMUX
        tmux new-session -s swain "claude --dangerously-skip-permissions '/swain-init'"
    else
        claude --dangerously-skip-permissions '/swain-init'
    end
end
