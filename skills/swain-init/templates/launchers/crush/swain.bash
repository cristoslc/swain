# swain shell launcher — crush / bash
# Runtime: Crush (formerly opencode) | Shell: bash
# Version: 4.1.0
#
# Launches Crush interactively with swain's recommended flags.
# --yolo: auto-approve all permission requests
#
# NOTE: Crush does not support an initial prompt in interactive mode
# (Partial support per ADR-017). Session initialization relies on
# AGENTS.md auto-invoke directives instead. Free-text session purpose
# is passed via the SWAIN_PURPOSE environment variable.

swain() {
  if [ -x "bin/swain" ]; then
    exec bin/swain "$@"
  fi
  if [ $# -gt 0 ]; then
    export SWAIN_PURPOSE="$*"
  fi
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "crush --yolo"
  else
    crush --yolo
  fi
}
