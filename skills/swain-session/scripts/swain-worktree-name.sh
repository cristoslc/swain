#!/usr/bin/env bash
# Generates artifact-aware worktree names (SPEC-251, ADR-025)
#
# Naming rules by track:
#   Implementable (SPEC, SPIKE):   <id>-<title-slug>
#   Container (EPIC, INITIATIVE):  <purpose-slug>-<YYYYMMDD>-<id>-<title-slug>
#   Standing (VISION, ADR, etc.):  <id>-<title-slug>
#   No artifact:                   session-<YYYYMMDD>-<HHMMSS>-<random>
#
# Usage: swain-worktree-name.sh [purpose-text]
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PURPOSE="${1:-}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
SUFFIX="$(head -c 2 /dev/urandom | od -An -tx1 | tr -d ' \n')"

# --- Helpers ---

slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50
}

# Track classification (ADR-025)
artifact_track() {
  local type="$1"
  case "$(echo "$type" | tr '[:upper:]' '[:lower:]')" in
    spec|spike)                                    echo "implementable" ;;
    epic|initiative)                               echo "container" ;;
    vision|journey|persona|adr|runbook|design|train) echo "standing" ;;
    *)                                             echo "unknown" ;;
  esac
}

# Find artifact file and extract title from frontmatter
artifact_title() {
  local id="$1"
  local type num
  type="$(echo "$id" | sed 's/-[0-9]*//' | tr '[:upper:]' '[:lower:]')"
  num="$(echo "$id" | grep -oE '[0-9]+')"
  local padded
  padded="$(printf '%03d' "$num" 2>/dev/null || echo "$num")"

  # Search for the artifact file
  local artifact_file
  artifact_file="$(find "$REPO_ROOT/docs" -name "*${id^^}*" -name "*.md" 2>/dev/null | head -1)"
  # Try case-insensitive if not found
  if [ -z "$artifact_file" ]; then
    artifact_file="$(find "$REPO_ROOT/docs" -iname "*$(echo "$id" | tr '[:lower:]' '[:upper:]')*" -name "*.md" 2>/dev/null | head -1)"
  fi

  if [ -z "$artifact_file" ]; then
    return 1
  fi

  # Extract title from frontmatter
  local title
  title="$(grep -m1 '^title:' "$artifact_file" | sed 's/^title:[[:space:]]*//' | sed 's/^"//;s/"$//')"
  if [ -n "$title" ]; then
    echo "$title"
    return 0
  fi
  return 1
}

# --- Extract artifact ID ---

# Regex: TYPE-NNN (case insensitive)
ARTIFACT_ID=""
if [ -n "$PURPOSE" ]; then
  # Extract all artifact IDs
  ALL_IDS="$(echo "$PURPOSE" | grep -ioE '(SPEC|EPIC|SPIKE|VISION|INITIATIVE|ADR|DESIGN|JOURNEY|PERSONA|RUNBOOK|TRAIN)-[0-9]+' || true)"

  if [ -n "$ALL_IDS" ]; then
    # Prefer container type if present (EPIC, INITIATIVE), else take first
    CONTAINER_ID="$(echo "$ALL_IDS" | grep -iE '^(EPIC|INITIATIVE)-' | head -1)"
    if [ -n "$CONTAINER_ID" ]; then
      ARTIFACT_ID="$CONTAINER_ID"
    else
      ARTIFACT_ID="$(echo "$ALL_IDS" | head -1)"
    fi
    # Normalize to uppercase type, lowercase for slug
    ARTIFACT_ID="$(echo "$ARTIFACT_ID" | tr '[:lower:]' '[:upper:]')"
  fi
fi

# --- Generate name ---

if [ -z "$ARTIFACT_ID" ]; then
  # Fallback: session-YYYYMMDD-HHMMSS-XXXX
  if [ -n "$PURPOSE" ]; then
    PURPOSE_SLUG="$(slugify "$PURPOSE")"
    # Use purpose slug if meaningful, else session
    if [ -n "$PURPOSE_SLUG" ] && [ "${#PURPOSE_SLUG}" -gt 3 ]; then
      printf 'session-%s-%s\n' "$TIMESTAMP" "$SUFFIX"
    else
      printf 'session-%s-%s\n' "$TIMESTAMP" "$SUFFIX"
    fi
  else
    printf 'session-%s-%s\n' "$TIMESTAMP" "$SUFFIX"
  fi
  exit 0
fi

# Extract type and number
ART_TYPE="$(echo "$ARTIFACT_ID" | sed 's/-[0-9]*//')"
ART_NUM="$(echo "$ARTIFACT_ID" | grep -oE '[0-9]+')"
ART_ID_LOWER="$(echo "$ARTIFACT_ID" | tr '[:upper:]' '[:lower:]')"
TRACK="$(artifact_track "$ART_TYPE")"

# Try to get title from frontmatter
TITLE=""
if TITLE_RAW="$(artifact_title "$ARTIFACT_ID")"; then
  TITLE="$(slugify "$TITLE_RAW")"
fi

case "$TRACK" in
  implementable)
    # Pattern: <id>-<title-slug>
    if [ -n "$TITLE" ]; then
      printf '%s-%s\n' "$ART_ID_LOWER" "$TITLE"
    else
      printf '%s\n' "$ART_ID_LOWER"
    fi
    ;;
  container)
    # Pattern: <purpose-slug>-<YYYYMMDD>-<id>-<title-slug>
    # Extract purpose words (remove the artifact ID from purpose text)
    PURPOSE_CLEAN="$(echo "$PURPOSE" | sed -E "s/$ARTIFACT_ID//i" | xargs)"
    PURPOSE_SLUG="$(slugify "$PURPOSE_CLEAN")"
    DATE_ONLY="$(date +%Y%m%d)"
    if [ -n "$PURPOSE_SLUG" ] && [ "${#PURPOSE_SLUG}" -gt 2 ]; then
      if [ -n "$TITLE" ]; then
        printf '%s-%s-%s-%s\n' "$PURPOSE_SLUG" "$DATE_ONLY" "$ART_ID_LOWER" "$TITLE"
      else
        printf '%s-%s-%s\n' "$PURPOSE_SLUG" "$DATE_ONLY" "$ART_ID_LOWER"
      fi
    else
      if [ -n "$TITLE" ]; then
        printf '%s-%s-%s\n' "$DATE_ONLY" "$ART_ID_LOWER" "$TITLE"
      else
        printf '%s-%s\n' "$DATE_ONLY" "$ART_ID_LOWER"
      fi
    fi
    ;;
  standing)
    # Pattern: <id>-<title-slug>
    if [ -n "$TITLE" ]; then
      printf '%s-%s\n' "$ART_ID_LOWER" "$TITLE"
    else
      printf '%s\n' "$ART_ID_LOWER"
    fi
    ;;
  *)
    # Unknown type — use ID + fallback
    printf '%s-%s-%s\n' "$ART_ID_LOWER" "$TIMESTAMP" "$SUFFIX"
    ;;
esac
