# swain shell launcher — copilot / fish
# Runtime: GitHub Copilot CLI | Shell: fish
# Version: 4.1.0
#
# Launches GitHub Copilot CLI interactively with swain's recommended flags.
# --yolo: allow all permissions (tools, paths, URLs)
# -i: interactive mode with initial prompt
# When arguments are provided, they become the session purpose.

function swain
    set -l _prompt '/swain-init'
    if test (count $argv) -gt 0
        set _prompt "/swain-session Session purpose: $argv"
    end
    if not set -q TMUX
        tmux new-session -s swain "copilot --yolo -i '$_prompt'"
    else
        copilot --yolo -i "$_prompt"
    end
end
