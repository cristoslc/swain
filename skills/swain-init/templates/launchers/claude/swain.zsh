# swain shell launcher — claude / zsh
# Runtime: Claude Code | Shell: zsh
# Version: 5.0.0
#
# Launches Claude Code interactively with swain's recommended flags.
# Handles tmux wrapping: outside tmux, starts a new tmux session;
# inside tmux, launches directly in the current pane.
# When arguments are provided, they become the session purpose.
# SPEC-196: Checks .swain-init marker to skip the init skill on established projects.

# Check .swain-init marker and return the appropriate initial prompt.
# Returns /swain-session if marker is current, /swain-init otherwise.
_swain_check_marker() {
  local marker=".swain-init"

  # No marker → need init
  if [ ! -f "$marker" ]; then
    echo "/swain-init"
    return
  fi

  # Extract marker major version (last history entry)
  local marker_version=""
  if command -v jq &>/dev/null; then
    marker_version=$(jq -r '.history[-1].version // empty' "$marker" 2>/dev/null)
  else
    # Fallback: grep for version field in JSON
    marker_version=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$marker" 2>/dev/null | tail -1 | grep -o '"[0-9][^"]*"' | tr -d '"')
  fi

  if [ -z "$marker_version" ]; then
    echo "/swain-init"
    return
  fi

  # Extract installed major version from skill file
  local installed_version=""
  local skill_file
  skill_file=$(find . .claude .agents skills -path '*/swain-init/SKILL.md' -print -quit 2>/dev/null)
  if [ -n "$skill_file" ]; then
    installed_version=$(head -20 "$skill_file" 2>/dev/null | grep '^version:' | awk '{print $2}')
  fi

  if [ -z "$installed_version" ]; then
    echo "/swain-init"
    return
  fi

  # Compare major versions
  local marker_major="${marker_version%%.*}"
  local installed_major="${installed_version%%.*}"

  if [ "$marker_major" = "$installed_major" ]; then
    echo "/swain-session"
  else
    echo "/swain-init"
  fi
}

swain() {
  if [ -x "bin/swain" ]; then
    exec bin/swain "$@"
  fi
  local _prompt
  if [ $# -gt 0 ]; then
    _prompt="/swain-session Session purpose: $*"
  else
    _prompt=$(_swain_check_marker)
  fi
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "claude --dangerously-skip-permissions '${_prompt}'"
  else
    claude --dangerously-skip-permissions "$_prompt"
  fi
}
