# swain shell launcher — crush / fish
# Runtime: Crush (formerly opencode) | Shell: fish
# Version: 4.0.0
#
# Launches Crush interactively with swain's recommended flags.
# --yolo: auto-approve all permission requests
#
# NOTE: Crush does not support an initial prompt in interactive mode
# (Partial support per ADR-017). Session initialization relies on
# AGENTS.md auto-invoke directives instead.

function swain
    if not set -q TMUX
        tmux new-session -s swain "crush --yolo"
    else
        crush --yolo
    end
end
