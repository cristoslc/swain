# swain shell launcher — claude / fish
# Runtime: Claude Code | Shell: fish
# Version: 4.1.0
#
# Launches Claude Code interactively with swain's recommended flags.
# Handles tmux wrapping: outside tmux, starts a new tmux session;
# inside tmux, launches directly in the current pane.
# When arguments are provided, they become the session purpose.

function swain
    set -l _prompt '/swain-init'
    if test (count $argv) -gt 0
        set _prompt "/swain-session Session purpose: $argv"
    end
    if not set -q TMUX
        tmux new-session -s swain "claude --dangerously-skip-permissions '$_prompt'"
    else
        claude --dangerously-skip-permissions "$_prompt"
    end
end
