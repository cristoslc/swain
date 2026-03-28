# swain shell launcher — copilot / bash
# Runtime: GitHub Copilot CLI | Shell: bash
# Version: 4.1.0
#
# Launches GitHub Copilot CLI interactively with swain's recommended flags.
# --yolo: allow all permissions (tools, paths, URLs)
# -i: interactive mode with initial prompt
# When arguments are provided, they become the session purpose.

swain() {
  local _prompt='/swain-init'
  if [ $# -gt 0 ]; then
    _prompt="/swain-session Session purpose: $*"
  fi
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "copilot --yolo -i '${_prompt}'"
  else
    copilot --yolo -i "$_prompt"
  fi
}
