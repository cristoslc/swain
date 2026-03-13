#!/usr/bin/env bash
# swain-preflight.sh — lightweight session-start check
#
# Exit 0 = everything looks fine, skip swain-doctor
# Exit 1 = something needs attention, invoke swain-doctor
#
# This replaces the unconditional auto-invoke of swain-doctor,
# saving tokens on clean sessions. See ADR-001 / SPEC-008.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

issues=()

# 1. Governance files exist
if [[ ! -f AGENTS.md ]] && [[ ! -f CLAUDE.md ]]; then
  issues+=("no governance file (AGENTS.md or CLAUDE.md)")
fi

# 2. Governance markers present
if ! grep -q "swain governance" AGENTS.md CLAUDE.md 2>/dev/null; then
  issues+=("governance markers missing")
fi

# 3. .agents directory exists
if [[ ! -d .agents ]]; then
  issues+=(".agents directory missing")
fi

# 4. .tickets/ directory is valid (if it exists)
if [[ -d .tickets ]]; then
  for f in .tickets/*.md; do
    [[ -f "$f" ]] || continue
    if ! head -1 "$f" | grep -q '^---$'; then
      issues+=("invalid ticket frontmatter: $f")
      break
    fi
  done
fi

# 5. No stale .beads/ directory (needs auto-migration)
if [[ -d .beads ]]; then
  issues+=("stale .beads/ directory needs migration to .tickets/")
fi

# 6. No stale tk lock files (older than 1 hour)
if [[ -d .tickets/.locks ]]; then
  stale_locks=$(find .tickets/.locks -type f -mmin +60 2>/dev/null | head -1)
  if [[ -n "$stale_locks" ]]; then
    issues+=("stale tk lock files in .tickets/.locks/")
  fi
fi

# 7. Script permissions (spot check)
if find .claude/skills/*/scripts/ -type f \( -name '*.sh' -o -name '*.py' \) ! -perm -u+x 2>/dev/null | grep -q .; then
  issues+=("scripts missing executable permission")
fi

# Report
if [[ ${#issues[@]} -eq 0 ]]; then
  exit 0
else
  echo "swain-preflight: ${#issues[@]} issue(s) found:"
  for issue in "${issues[@]}"; do
    echo "  - $issue"
  done
  exit 1
fi
