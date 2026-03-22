#!/usr/bin/env bash
# check-skill-changes.sh — Detect non-trivial skill file changes on trunk
#
# Scans the last N commits (default: 10) on the current branch for commits
# that touch skill files with non-trivial diffs.
#
# Triviality threshold (all must hold for a commit to be trivial):
#   - Touches exactly 1 skill file
#   - Total diff is ≤5 lines (insertions + deletions)
#   - No structural changes (new sections, frontmatter field adds/removes, version bumps)
#
# Exit 0 = clean (no non-trivial skill changes found)
# Exit 1 = non-trivial skill changes detected (advisory warning emitted)
#
# Usage: bash check-skill-changes.sh [--commits N]

set -euo pipefail

COMMIT_COUNT=10

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commits) COMMIT_COUNT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Skill file path patterns
SKILL_PATHS="skills/ .claude/skills/ .agents/skills/"

found_issues=()

# Scan recent commits
while IFS= read -r commit_hash; do
  [[ -z "$commit_hash" ]] && continue

  # Get list of skill files changed in this commit
  skill_files=()
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    for prefix in $SKILL_PATHS; do
      if [[ "$file" == ${prefix}* ]]; then
        skill_files+=("$file")
        break
      fi
    done
  done < <(git diff-tree --no-commit-id --name-only -r "$commit_hash" 2>/dev/null)

  # Skip commits that don't touch skill files
  [[ ${#skill_files[@]} -eq 0 ]] && continue

  # Multi-file skill change is always non-trivial
  if [[ ${#skill_files[@]} -gt 1 ]]; then
    found_issues+=("$commit_hash")
    continue
  fi

  # Single skill file — check diff size
  file="${skill_files[0]}"
  diff_stat=$(git diff-tree --no-commit-id --numstat -r "$commit_hash" -- "$file" 2>/dev/null)
  insertions=$(echo "$diff_stat" | awk '{print $1}')
  deletions=$(echo "$diff_stat" | awk '{print $2}')

  # Handle binary files
  if [[ "$insertions" == "-" || "$deletions" == "-" ]]; then
    found_issues+=("$commit_hash")
    continue
  fi

  total_lines=$((insertions + deletions))

  # Over 5 lines = non-trivial
  if [[ $total_lines -gt 5 ]]; then
    found_issues+=("$commit_hash")
    continue
  fi

  # Check for structural changes even in small diffs
  diff_content=$(git diff-tree --no-commit-id -p -r "$commit_hash" -- "$file" 2>/dev/null)

  # Version bump detection (version field change in frontmatter)
  if echo "$diff_content" | grep -qE '^\+.*version:'; then
    found_issues+=("$commit_hash")
    continue
  fi

  # New section detection (added ## heading)
  if echo "$diff_content" | grep -qE '^\+##\s'; then
    found_issues+=("$commit_hash")
    continue
  fi

  # Frontmatter field addition/removal
  if echo "$diff_content" | grep -qE '^\+[a-z_-]+:' | head -1; then
    # Check if we're inside frontmatter (between --- markers)
    in_frontmatter=false
    while IFS= read -r line; do
      if [[ "$line" == "---" || "$line" == "+---" || "$line" == " ---" ]]; then
        if $in_frontmatter; then
          in_frontmatter=false
        else
          in_frontmatter=true
        fi
        continue
      fi
      if $in_frontmatter && echo "$line" | grep -qE '^\+[a-z_-]+:'; then
        found_issues+=("$commit_hash")
        break 2
      fi
    done <<< "$diff_content"
  fi

done < <(git log --format='%H' -n "$COMMIT_COUNT" 2>/dev/null)

# Report
if [[ ${#found_issues[@]} -eq 0 ]]; then
  exit 0
fi

for commit in "${found_issues[@]}"; do
  short=$(git log --format='%h %s' -n 1 "$commit" 2>/dev/null)
  echo "⚠ Trunk commit $short touches skill files with non-trivial changes."
  echo "  Skill changes above the triviality threshold should use worktree branches."
done
exit 1
