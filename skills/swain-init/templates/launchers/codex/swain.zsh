# swain shell launcher — codex / zsh
# Runtime: Codex CLI (OpenAI) | Shell: zsh
# Version: 4.1.0
#
# Launches Codex CLI interactively with swain's recommended flags.
# --yolo: bypass all approvals and sandboxing
# When arguments are provided, they become the session purpose.

swain() {
  local _prompt='/swain-init'
  if [ $# -gt 0 ]; then
    _prompt="/swain-session Session purpose: $*"
  fi
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "codex --yolo '${_prompt}'"
  else
    codex --yolo "$_prompt"
  fi
}
