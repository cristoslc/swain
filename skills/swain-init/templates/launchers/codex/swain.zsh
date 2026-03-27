# swain shell launcher — codex / zsh
# Runtime: Codex CLI (OpenAI) | Shell: zsh
# Version: 4.0.0
#
# Launches Codex CLI interactively with swain's recommended flags.
# --yolo: bypass all approvals and sandboxing

swain() {
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "codex --yolo '/swain-init'"
  else
    codex --yolo '/swain-init'
  fi
}
