# swain shell launcher — codex / fish
# Runtime: Codex CLI (OpenAI) | Shell: fish
# Version: 4.1.0
#
# Launches Codex CLI interactively with swain's recommended flags.
# --yolo: bypass all approvals and sandboxing
# When arguments are provided, they become the session purpose.

function swain
    set -l _prompt '/swain-init'
    if test (count $argv) -gt 0
        set _prompt "/swain-session Session purpose: $argv"
    end
    if not set -q TMUX
        tmux new-session -s swain "codex --yolo '$_prompt'"
    else
        codex --yolo "$_prompt"
    end
end
