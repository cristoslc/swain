# swain shell launcher — copilot / fish
# Runtime: GitHub Copilot CLI | Shell: fish
# Version: 4.0.0
#
# Launches GitHub Copilot CLI interactively with swain's recommended flags.
# --yolo: allow all permissions (tools, paths, URLs)
# -i: interactive mode with initial prompt

function swain
    if not set -q TMUX
        tmux new-session -s swain "copilot --yolo -i '/swain-init'"
    else
        copilot --yolo -i '/swain-init'
    end
end
