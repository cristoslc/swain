# swain shell launcher — gemini / fish
# Runtime: Gemini CLI | Shell: fish
# Version: 4.0.0
#
# Launches Gemini CLI interactively with swain's recommended flags.
# -y: auto-approve all tool actions (yolo mode)
# -i: interactive mode with initial prompt

function swain
    if not set -q TMUX
        tmux new-session -s swain "gemini -y -i '/swain-init'"
    else
        gemini -y -i '/swain-init'
    end
end
