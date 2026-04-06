#!/usr/bin/env bash
# renumber-artifact.sh — Rename an artifact from OLD-ID to NEW-ID
#
# Usage: renumber-artifact.sh <OLD-ID> <NEW-ID> [--dry-run] [--source-dir <path>]
#   OLD-ID: e.g., SPEC-119
#   NEW-ID: e.g., SPEC-163
#   --source-dir: explicit directory to rename (required when OLD-ID has duplicates)
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

REPO_ROOT="$(cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && pwd -P)"
DRY_RUN=false
SOURCE_DIR=""

# --- Parse args ---
if [ $# -lt 2 ]; then
  echo "Usage: renumber-artifact.sh <OLD-ID> <NEW-ID> [--dry-run] [--source-dir <path>]" >&2
  exit 1
fi

OLD_ID="$1"
NEW_ID="$2"
shift 2
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --source-dir) shift; SOURCE_DIR="$1" ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
  shift
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
if [ -n "$SOURCE_DIR" ]; then
  OLD_DIR="$(cd "$SOURCE_DIR" && pwd -P)"
  if [ ! -d "$OLD_DIR" ]; then
    echo "Error: --source-dir '$SOURCE_DIR' does not exist" >&2
    exit 1
  fi
else
  OLD_DIR=$(find "$REPO_ROOT/docs" -maxdepth 5 -type d -name "(${OLD_ID})-*" 2>/dev/null | head -1)
  if [ -z "$OLD_DIR" ]; then
    echo "Error: artifact directory for '$OLD_ID' not found" >&2
    exit 1
  fi
  # Warn if there are duplicates and no --source-dir was given
  dup_count=$(find "$REPO_ROOT/docs" -maxdepth 5 -type d -name "(${OLD_ID})-*" 2>/dev/null | wc -l)
  if [ "$dup_count" -gt 1 ]; then
    echo "Warning: $dup_count directories match '$OLD_ID' — use --source-dir to specify which one." >&2
    echo "  Picking: $OLD_DIR" >&2
  fi
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
# In collision context (--source-dir), use git history to distinguish keeper
# references from collision references. Only rewrite references that were
# introduced after the collision artifact was created. (SPEC-204)

KEEPER_DIRS=()
COLLISION_CREATION_COMMIT=""
if [ -n "$SOURCE_DIR" ]; then
  # Find keeper directories
  while IFS= read -r dup_dir; do
    [ "$dup_dir" = "$OLD_DIR" ] && continue
    KEEPER_DIRS+=("$dup_dir")
  done < <(find "$REPO_ROOT/docs" -maxdepth 5 -type d -name "(${OLD_ID})-*" 2>/dev/null)

  # Find the commit that created the collision artifact
  COLLISION_CREATION_COMMIT=$(git log --all --diff-filter=A --format=%H -- "$OLD_DIR" 2>/dev/null | tail -1)
fi

# Helper: check if a file's reference to OLD_ID predates the collision
ref_belongs_to_collision() {
  local file="$1"
  # No collision context — rewrite everything (non-collision renumber)
  [ -z "$COLLISION_CREATION_COMMIT" ] && return 0

  # File is inside the collision artifact's directory — always rewrite
  # (Use string prefix check instead of case/glob to avoid parentheses in paths
  # being interpreted as case pattern delimiters)
  [[ "$file" == "$OLD_DIR"/* ]] && return 0
  [[ "$file" == "$NEW_DIR"/* ]] && return 0

  # File is inside a keeper directory — never rewrite
  for kd in "${KEEPER_DIRS[@]-}"; do
    [[ "$file" == "$kd"/* ]] && return 1
  done

  # Check git: when was OLD_ID first introduced to this file?
  # If the reference was introduced in or after the collision creation commit,
  # it belongs to the collision and should be rewritten.
  local intro_commit
  intro_commit=$(git log --all --format=%H -S "$OLD_ID" -- "$file" 2>/dev/null | tail -1)

  # No git history for this reference — conservative: skip (assume keeper)
  [ -z "$intro_commit" ] && return 1

  # If the intro commit is an ancestor of the collision creation commit
  # (i.e., it came before or at the same time), it's a keeper reference.
  if git merge-base --is-ancestor "$intro_commit" "$COLLISION_CREATION_COMMIT" 2>/dev/null; then
    # intro_commit is ancestor of collision — reference predates collision
    # But if they're the same commit, the reference was introduced alongside
    if [ "$intro_commit" = "$COLLISION_CREATION_COMMIT" ]; then
      return 0  # same commit as collision — rewrite
    fi
    return 1  # predates collision — skip
  fi

  # intro_commit is NOT an ancestor — it came after the collision
  return 0
}

REF_COUNT=0
SKIP_COUNT=0
while IFS= read -r md_file; do
  [ -f "$md_file" ] || continue
  if grep -q "$OLD_ID" "$md_file" 2>/dev/null; then
    rel="${md_file#"$REPO_ROOT/"}"
    if ref_belongs_to_collision "$md_file"; then
      if [ "$DRY_RUN" = true ]; then
        echo "  [dry-run] rewrite refs in: $rel"
        REF_COUNT=$((REF_COUNT + 1))
      else
        sed -i '' "s/${OLD_ID}/${NEW_ID}/g" "$md_file"
        git add "$md_file"
        REF_COUNT=$((REF_COUNT + 1))
      fi
    else
      SKIP_COUNT=$((SKIP_COUNT + 1))
      if [ "$DRY_RUN" = true ]; then
        echo "  [dry-run] skip (keeper ref): $rel"
      fi
    fi
  fi
done < <(find "$REPO_ROOT/docs" -name '*.md' -not -path '*/troves/*' 2>/dev/null)

echo "  Cross-references updated: $REF_COUNT file(s)${SKIP_COUNT:+, $SKIP_COUNT skipped (keeper refs)}"

if [ "$DRY_RUN" = true ]; then
  echo "[dry-run] No changes made."
else
  echo "Done. Changes staged — commit when ready."
fi
