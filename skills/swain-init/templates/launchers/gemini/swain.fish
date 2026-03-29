# swain shell launcher — gemini / fish
# Runtime: Gemini CLI | Shell: fish
# Version: 4.1.0
#
# Launches Gemini CLI interactively with swain's recommended flags.
# -y: auto-approve all tool actions (yolo mode)
# -i: interactive mode with initial prompt
# When arguments are provided, they become the session purpose.

function swain
    set -l _prompt '/swain-init'
    if test (count $argv) -gt 0
        set _prompt "/swain-session Session purpose: $argv"
    end
    if not set -q TMUX
        tmux new-session -s swain "gemini -y -i '$_prompt'"
    else
        gemini -y -i "$_prompt"
    end
end
