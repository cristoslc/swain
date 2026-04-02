# swain shell launcher — claude / fish
# Runtime: Claude Code | Shell: fish
# Version: 5.0.0
#
# Launches Claude Code interactively with swain's recommended flags.
# Handles tmux wrapping: outside tmux, starts a new tmux session;
# inside tmux, launches directly in the current pane.
# When arguments are provided, they become the session purpose.
# SPEC-196: Checks .swain-init marker to skip the init skill on established projects.

# Check .swain-init marker and return the appropriate initial prompt.
# Returns /swain-session if marker is current, /swain-init otherwise.
function _swain_check_marker
    set -l marker ".swain-init"

    # No marker → need init
    if not test -f "$marker"
        echo "/swain-init"
        return
    end

    # Extract marker major version (last history entry)
    set -l marker_version ""
    if command -q jq
        set marker_version (jq -r '.history[-1].version // empty' "$marker" 2>/dev/null)
    else
        # Fallback: grep for version field in JSON
        set marker_version (grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$marker" 2>/dev/null | tail -1 | grep -o '"[0-9][^"]*"' | tr -d '"')
    end

    if test -z "$marker_version"
        echo "/swain-init"
        return
    end

    # Extract installed major version from skill file
    set -l installed_version ""
    set -l skill_file (find . .claude .agents skills -path '*/swain-init/SKILL.md' -print -quit 2>/dev/null)
    if test -n "$skill_file"
        set installed_version (head -20 "$skill_file" 2>/dev/null | grep '^version:' | awk '{print $2}')
    end

    if test -z "$installed_version"
        echo "/swain-init"
        return
    end

    # Compare major versions
    set -l marker_major (string split '.' "$marker_version")[1]
    set -l installed_major (string split '.' "$installed_version")[1]

    if test "$marker_major" = "$installed_major"
        echo "/swain-session"
    else
        echo "/swain-init"
    end
end

function swain
    if test -x bin/swain
        exec bin/swain $argv
    end
    set -l _prompt
    if test (count $argv) -gt 0
        set _prompt "/swain-session Session purpose: $argv"
    else
        set _prompt (_swain_check_marker)
    end
    if not set -q TMUX
        tmux new-session -s swain "claude --dangerously-skip-permissions '$_prompt'"
    else
        claude --dangerously-skip-permissions "$_prompt"
    end
end
