#!/usr/bin/env bash
# renumber-artifact.sh — Rename an artifact from OLD-ID to NEW-ID
#
# Usage: renumber-artifact.sh <OLD-ID> <NEW-ID> [--dry-run]
#   OLD-ID: e.g., SPEC-119
#   NEW-ID: e.g., SPEC-163
#
# Renames directory, updates frontmatter artifact field, rewrites
# cross-references in all docs/ artifacts. Uses git mv for history.
#
# SPEC-158 / EPIC-043

set -euo pipefail

git rev-parse --git-dir >/dev/null 2>&1 || {
  echo "Error: not inside a git repository" >&2
  exit 1
}

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DRY_RUN=false

# --- Parse args ---
if [ $# -lt 2 ]; then
  echo "Usage: renumber-artifact.sh <OLD-ID> <NEW-ID> [--dry-run]" >&2
  exit 1
fi

OLD_ID="$1"
NEW_ID="$2"
shift 2
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown flag: $arg" >&2; exit 1 ;;
  esac
done

# --- Validate IDs ---
if ! [[ "$OLD_ID" =~ ^[A-Z]+-[0-9]+$ ]]; then
  echo "Error: OLD-ID '$OLD_ID' doesn't match TYPE-NNN format" >&2
  exit 1
fi
if ! [[ "$NEW_ID" =~ ^[A-Z]+-[0-9]+$ ]]; then
  echo "Error: NEW-ID '$NEW_ID' doesn't match TYPE-NNN format" >&2
  exit 1
fi

OLD_TYPE="${OLD_ID%%-*}"
NEW_TYPE="${NEW_ID%%-*}"
if [ "$OLD_TYPE" != "$NEW_TYPE" ]; then
  echo "Error: type mismatch — OLD-ID is $OLD_TYPE but NEW-ID is $NEW_TYPE" >&2
  exit 1
fi

# --- Find the old artifact directory ---
OLD_DIR=$(find "$REPO_ROOT/docs" -maxdepth 5 -type d -name "(${OLD_ID})-*" 2>/dev/null | head -1)
if [ -z "$OLD_DIR" ]; then
  echo "Error: artifact directory for '$OLD_ID' not found" >&2
  exit 1
fi

# --- Check NEW-ID doesn't already exist ---
EXISTING=$(find "$REPO_ROOT/docs" -maxdepth 5 -type d -name "(${NEW_ID})-*" 2>/dev/null | head -1)
if [ -n "$EXISTING" ]; then
  echo "Error: NEW-ID '$NEW_ID' already exists at $EXISTING" >&2
  exit 1
fi

# --- Compute new directory name ---
OLD_DIRNAME="$(basename "$OLD_DIR")"
# Replace (OLD_ID) with (NEW_ID) in the directory name
NEW_DIRNAME="${OLD_DIRNAME/$OLD_ID/$NEW_ID}"
NEW_DIR="$(dirname "$OLD_DIR")/$NEW_DIRNAME"

echo "Renumber: $OLD_ID → $NEW_ID"
echo "  Dir: $(basename "$(dirname "$OLD_DIR")")/$OLD_DIRNAME → $(basename "$(dirname "$NEW_DIR")")/$NEW_DIRNAME"

# --- Step 1: Rename directory ---
if [ "$DRY_RUN" = true ]; then
  echo "  [dry-run] git mv $OLD_DIR → $NEW_DIR"
else
  git mv "$OLD_DIR" "$NEW_DIR"
fi

# --- Step 2: Rename primary .md file inside ---
OLD_MD="$NEW_DIR/$OLD_DIRNAME.md"
NEW_MD="$NEW_DIR/$NEW_DIRNAME.md"
if [ -f "$OLD_MD" ]; then
  if [ "$DRY_RUN" = true ]; then
    echo "  [dry-run] git mv primary md: $OLD_DIRNAME.md → $NEW_DIRNAME.md"
  else
    git mv "$OLD_MD" "$NEW_MD"
  fi
fi

# --- Step 3: Update frontmatter in the artifact's own file ---
TARGET_MD="$NEW_DIR/$NEW_DIRNAME.md"
if [ -f "$TARGET_MD" ] && [ "$DRY_RUN" = false ]; then
  sed -i '' "s/^artifact: ${OLD_ID}$/artifact: ${NEW_ID}/" "$TARGET_MD"
  git add "$TARGET_MD"
fi
if [ "$DRY_RUN" = true ]; then
  echo "  [dry-run] update frontmatter: artifact: $OLD_ID → $NEW_ID"
fi

# --- Step 4: Rewrite cross-references in all docs/ .md files ---
REF_COUNT=0
while IFS= read -r md_file; do
  [ -f "$md_file" ] || continue
  if grep -q "$OLD_ID" "$md_file" 2>/dev/null; then
    if [ "$DRY_RUN" = true ]; then
      rel="${md_file#"$REPO_ROOT/"}"
      echo "  [dry-run] rewrite refs in: $rel"
      REF_COUNT=$((REF_COUNT + 1))
    else
      # Replace in frontmatter fields and body text
      sed -i '' "s/${OLD_ID}/${NEW_ID}/g" "$md_file"
      git add "$md_file"
      REF_COUNT=$((REF_COUNT + 1))
    fi
  fi
done < <(find "$REPO_ROOT/docs" -name '*.md' -not -path '*/troves/*' 2>/dev/null)

echo "  Cross-references updated: $REF_COUNT file(s)"

if [ "$DRY_RUN" = true ]; then
  echo "[dry-run] No changes made."
else
  echo "Done. Changes staged — commit when ready."
fi
