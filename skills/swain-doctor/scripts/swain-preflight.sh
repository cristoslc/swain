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

# 2b. Governance freshness — compare installed block against canonical
CANONICAL="skills/swain-doctor/references/AGENTS.content.md"
if [[ -f "$CANONICAL" ]] && grep -q "swain governance" AGENTS.md CLAUDE.md 2>/dev/null; then
  GOV_FILE=$(grep -l "swain governance" AGENTS.md CLAUDE.md 2>/dev/null | head -1)
  if [[ -n "$GOV_FILE" ]]; then
    # Extract content between markers (exclusive) and hash
    extract_gov() { awk '/<!-- swain governance/{f=1;next}/<!-- end swain governance/{f=0}f' "$1"; }
    INSTALLED_HASH=$(extract_gov "$GOV_FILE" | shasum -a 256 | cut -d' ' -f1)
    CANONICAL_HASH=$(extract_gov "$CANONICAL" | shasum -a 256 | cut -d' ' -f1)
    if [[ "$INSTALLED_HASH" != "$CANONICAL_HASH" ]]; then
      issues+=("governance block is stale (differs from canonical AGENTS.content.md)")
    fi
  fi
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

# Evidence pool migration check
if [[ -d "$REPO_ROOT/docs/evidence-pools" ]]; then
  echo "preflight: docs/evidence-pools/ detected — trove migration needed"
  issues+=("docs/evidence-pools/ detected — trove migration needed")
fi

# 6. No stale tk lock files (older than 1 hour)
if [[ -d .tickets/.locks ]]; then
  stale_locks=$(find .tickets/.locks -type f -mmin +60 2>/dev/null | head -1)
  if [[ -n "$stale_locks" ]]; then
    issues+=("stale tk lock files in .tickets/.locks/")
  fi
fi

# 7. Old lifecycle phase directories (ADR-003 migration)
OLD_PHASES="Draft Planned Review Approved Testing Implemented Adopted Deprecated Archived Sunset Validated"
for dir in docs/*/; do
  [[ -d "$dir" ]] || continue
  for phase in $OLD_PHASES; do
    phase_dir="${dir}${phase}"
    if [[ -d "$phase_dir" ]]; then
      # Only flag non-empty directories (ignore .DS_Store and hidden files)
      if find "$phase_dir" -maxdepth 1 -not -name '.*' -not -name "$phase" -print -quit 2>/dev/null | grep -q .; then
        issues+=("old lifecycle directory: $phase_dir (run migrate-lifecycle-dirs.py)")
        break 2
      fi
    fi
  done
done

# 8. Commit signing configured
if [[ "$(git config --local commit.gpgsign 2>/dev/null)" != "true" ]]; then
  issues+=("commit signing not configured (run swain-keys --provision)")
fi

# 9. Script permissions (spot check)
if find .claude/skills/*/scripts/ -type f \( -name '*.sh' -o -name '*.py' \) ! -perm -u+x 2>/dev/null | grep -q .; then
  issues+=("scripts missing executable permission")
fi

# 10. Superpowers detection (advisory — warn but don't fail)
SUPERPOWERS_SKILLS="brainstorming writing-plans test-driven-development verification-before-completion subagent-driven-development executing-plans"
sp_missing=0
for skill in $SUPERPOWERS_SKILLS; do
  if ! ls .agents/skills/$skill/SKILL.md .claude/skills/$skill/SKILL.md 2>/dev/null | head -1 | grep -q .; then
    sp_missing=$((sp_missing + 1))
  fi
done
if [[ $sp_missing -gt 0 ]]; then
  echo "swain-preflight: superpowers: $sp_missing/6 skills missing (advisory)"
fi

# Check for epics without parent-initiative (initiative migration advisory)
EPICS_WITHOUT_INITIATIVE=0
while IFS= read -r -d '' f; do
  if grep -q '^parent-vision:' "$f" 2>/dev/null && ! grep -q '^parent-initiative:' "$f" 2>/dev/null; then
    EPICS_WITHOUT_INITIATIVE=$((EPICS_WITHOUT_INITIATIVE + 1))
  fi
done < <(find docs/epic -name '*.md' -not -name 'README.md' -not -name 'list-*.md' -print0 2>/dev/null)
if [[ "$EPICS_WITHOUT_INITIATIVE" -gt 0 ]]; then
  echo "advisory: $EPICS_WITHOUT_INITIATIVE epic(s) without parent-initiative — run initiative migration"
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
