#!/usr/bin/env bash
set -euo pipefail

# Scan epics without parent-initiative, grouped by parent-vision
# Usage: swain-initiative-scan.sh

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 1
}

EPIC_DIR="$REPO_ROOT/docs/epic"

if [[ ! -d "$EPIC_DIR" ]]; then
  echo "No docs/epic directory found — nothing to scan."
  exit 0
fi

echo "=== Epics without parent-initiative ==="
echo ""
echo "VISION | EPIC | TITLE"
echo "-------|------|------"

found=0
while IFS= read -r -d '' f; do
  if grep -q '^parent-vision:' "$f" 2>/dev/null && ! grep -q '^parent-initiative:' "$f" 2>/dev/null; then
    vision=$(grep '^parent-vision:' "$f" | head -1 | sed 's/parent-vision: *//' | tr -d ' ')
    artifact=$(grep '^artifact:' "$f" | head -1 | sed 's/artifact: *//' | tr -d ' ')
    title=$(grep '^title:' "$f" | head -1 | sed 's/title: *//' | tr -d '"')
    echo "$vision | $artifact | $title"
    found=$((found + 1))
  fi
done < <(find "$EPIC_DIR" -name '*.md' -not -name 'README.md' -not -name 'list-*.md' -print0 2>/dev/null | sort -z)

echo ""
if [[ "$found" -eq 0 ]]; then
  echo "All epics have parent-initiative. Migration complete."
else
  echo "$found epic(s) need parent-initiative assignment."
  echo ""

  orphan_count=0
  echo "Orphaned epics (no parent-vision or parent-initiative):"
  while IFS= read -r -d '' f; do
    if ! grep -q '^parent-vision:' "$f" 2>/dev/null && ! grep -q '^parent-initiative:' "$f" 2>/dev/null; then
      artifact=$(grep '^artifact:' "$f" | head -1 | sed 's/artifact: *//' | tr -d ' ')
      title=$(grep '^title:' "$f" | head -1 | sed 's/title: *//' | tr -d '"')
      echo "  $artifact | $title"
      orphan_count=$((orphan_count + 1))
    fi
  done < <(find "$EPIC_DIR" -name '*.md' -not -name 'README.md' -not -name 'list-*.md' -print0 2>/dev/null | sort -z)

  if [[ "$orphan_count" -eq 0 ]]; then
    echo "  (none)"
  fi
fi
