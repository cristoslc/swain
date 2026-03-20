#!/bin/bash
# resolve-artifact-link.sh — Resolve an artifact ID to its filesystem path
#
# Usage:
#   resolve-artifact-link.sh <ARTIFACT-ID>                    # absolute path
#   resolve-artifact-link.sh <ARTIFACT-ID> <SOURCE-FILE>      # relative path from source
#
# Examples:
#   resolve-artifact-link.sh SPEC-045
#   resolve-artifact-link.sh SPEC-045 docs/epic/Active/(EPIC-031)-Foo/EPIC-031.md
#
# Exit codes:
#   0 — resolved successfully (path on stdout)
#   1 — not found or invalid input

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 1
}
DOCS_DIR="$REPO_ROOT/docs"

# --- Validate input ---
ARTIFACT_ID="${1:-}"
SOURCE_FILE="${2:-}"

if [ -z "$ARTIFACT_ID" ]; then
  echo "Usage: resolve-artifact-link.sh <ARTIFACT-ID> [SOURCE-FILE]" >&2
  exit 1
fi

# Validate artifact ID format: TYPE-NNN
VALID_PREFIXES="SPEC|EPIC|INITIATIVE|VISION|SPIKE|ADR|PERSONA|RUNBOOK|DESIGN|JOURNEY|TRAIN"
if ! echo "$ARTIFACT_ID" | grep -qE "^($VALID_PREFIXES)-[0-9]+$"; then
  echo "Error: invalid artifact ID format: $ARTIFACT_ID" >&2
  exit 1
fi

# --- Find the artifact on disk ---
# Search by ID in filename — handles:
#   (SPEC-045)-Title/SPEC-045.md          (spec convention)
#   (EPIC-031)-Title/(EPIC-031)-Title.md  (epic/vision/initiative convention)
FOUND=""
while IFS= read -r candidate; do
  FOUND="$candidate"
  break
done < <(find "$DOCS_DIR" \( -name "${ARTIFACT_ID}*" -o -name "(${ARTIFACT_ID})*" \) -name "*.md" -not -name "list-*" 2>/dev/null | head -1)

if [ -z "$FOUND" ]; then
  exit 1
fi

# --- Output ---
if [ -n "$SOURCE_FILE" ]; then
  # Compute relative path from source file's directory to found file
  local_source="$SOURCE_FILE"
  # If source is relative, make it absolute
  if [[ "$local_source" != /* ]]; then
    local_source="$REPO_ROOT/$local_source"
  fi
  SOURCE_DIR="$(dirname "$local_source")"
  # Use python for reliable relpath (handles ../ traversal correctly)
  python3 -c "import os; print(os.path.relpath('$FOUND', '$SOURCE_DIR'))" 2>/dev/null
else
  echo "$FOUND"
fi
