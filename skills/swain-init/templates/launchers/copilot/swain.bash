# swain shell launcher — copilot / bash
# Runtime: GitHub Copilot CLI | Shell: bash
# Version: 4.0.0
#
# Launches GitHub Copilot CLI interactively with swain's recommended flags.
# --yolo: allow all permissions (tools, paths, URLs)
# -i: interactive mode with initial prompt

swain() {
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "copilot --yolo -i '/swain-init'"
  else
    copilot --yolo -i '/swain-init'
  fi
}
