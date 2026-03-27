# swain shell launcher — codex / fish
# Runtime: Codex CLI (OpenAI) | Shell: fish
# Version: 4.0.0
#
# Launches Codex CLI interactively with swain's recommended flags.
# --yolo: bypass all approvals and sandboxing

function swain
    if not set -q TMUX
        tmux new-session -s swain "codex --yolo '/swain-init'"
    else
        codex --yolo '/swain-init'
    end
end
