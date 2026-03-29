# swain shell launcher — gemini / bash
# Runtime: Gemini CLI | Shell: bash
# Version: 4.1.0
#
# Launches Gemini CLI interactively with swain's recommended flags.
# -y: auto-approve all tool actions (yolo mode)
# -i: interactive mode with initial prompt
# When arguments are provided, they become the session purpose.

swain() {
  local _prompt='/swain-init'
  if [ $# -gt 0 ]; then
    _prompt="/swain-session Session purpose: $*"
  fi
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "gemini -y -i '${_prompt}'"
  else
    gemini -y -i "$_prompt"
  fi
}
