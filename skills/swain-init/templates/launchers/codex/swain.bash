# swain shell launcher — codex / bash
# Runtime: Codex CLI (OpenAI) | Shell: bash
# Version: 5.0.0
#
# Launches Codex CLI interactively with swain's recommended flags.
# --yolo: bypass all approvals and sandboxing
# When arguments are provided, they become the session purpose.
# SPEC-196: Checks .swain-init marker to skip the init skill on established projects.

# Check .swain-init marker and return the appropriate initial prompt.
# Returns /swain-session if marker is current, /swain-init otherwise.
_swain_check_marker() {
  local marker=".swain-init"
  if [ ! -f "$marker" ]; then
    echo "/swain-init"
    return
  fi
  local marker_version=""
  if command -v jq &>/dev/null; then
    marker_version=$(jq -r '.history[-1].version // empty' "$marker" 2>/dev/null)
  else
    marker_version=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$marker" 2>/dev/null | tail -1 | grep -o '"[0-9][^"]*"' | tr -d '"')
  fi
  if [ -z "$marker_version" ]; then
    echo "/swain-init"
    return
  fi
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
  local marker_major="${marker_version%%.*}"
  local installed_major="${installed_version%%.*}"
  if [ "$marker_major" = "$installed_major" ]; then
    echo "/swain-session"
  else
    echo "/swain-init"
  fi
}

swain() {
  local _prompt
  if [ $# -gt 0 ]; then
    _prompt="/swain-session Session purpose: $*"
  else
    _prompt=$(_swain_check_marker)
  fi
  if [ -z "$TMUX" ]; then
    tmux new-session -s swain "codex --yolo '${_prompt}'"
  else
    codex --yolo "$_prompt"
  fi
}
