# swain shell launcher — gemini / bash
# Runtime: Gemini CLI | Shell: bash
# Version: 4.0.0
#
# Launches Gemini CLI interactively with swain's recommended flags.
# -y: auto-approve all tool actions (yolo mode)
# -i: interactive mode with initial prompt

swain() {
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "gemini -y -i '/swain-init'"
  else
    gemini -y -i '/swain-init'
  fi
}
