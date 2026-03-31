# swain shell launcher — thin wrapper
# Version: 5.0.0
#
# Delegates to the project-root swain script (SPEC-180) when available.
# Falls back to direct runtime invocation for projects without it.
# See: SPEC-181 (Shell Function Refactor)

swain() {
  if [ -x "bin/swain" ]; then
    exec bin/swain "$@"
  elif command -v claude >/dev/null 2>&1; then
    local _prompt='/swain-init'
    [ $# -gt 0 ] && _prompt="/swain-session Session purpose: $*"
    if [ -z "$TMUX" ]; then
      tmux new-session -s swain "claude --dangerously-skip-permissions '${_prompt}'"
    else
      claude --dangerously-skip-permissions "$_prompt"
    fi
  else
    echo "swain: no bin/swain script and no supported runtime found" >&2
    return 1
  fi
}
