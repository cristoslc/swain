#!/usr/bin/env bash
# Bootstrap script for swain-search media ingestion scripts.
# Verifies uv is available. yt-dlp, opencv, easyocr run transiently via uv.
# Safe to re-run — a marker file short-circuits after the first successful run.

set -euo pipefail

MARKER="${XDG_DATA_HOME:-$HOME/.local/share}/swain-search/.bootstrapped"

# If already bootstrapped, verify uv still exists and exit early
if [[ -f "$MARKER" ]]; then
  if command -v uv >/dev/null 2>&1; then
    exit 0
  fi
  # uv was removed — fall through to re-check
fi

echo "swain-search: checking dependencies…"

# uv is a hard requirement — it manages Python and Python packages
if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is required but not found. Install it first:" >&2
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

# Stamp the marker so subsequent runs exit early
mkdir -p "$(dirname "$MARKER")"
touch "$MARKER"

# --- One-time permissions audit ---
# Scan settings files for overly broad patterns. Scripts in this skill feed
# external content (transcripts, X threads) into the model's context — broad
# patterns widen the blast radius if that content contains prompt injection.

BROAD_PATTERNS=(
  'Bash(osascript:*)|Bash(osascript *)|Full arbitrary code execution via AppleScript — keychain access, app control, shell commands.'
  'Bash(open:*)|Bash(open *)|Opens any file or URL via default handler — phishing, payload launch.'
)

audit_permissions() {
  local dominated=()
  local settings_files=(
    "$HOME/.claude/settings.json"
    "$HOME/.claude/settings.local.json"
  )
  local project_root
  project_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$project_root" ]]; then
    settings_files+=("$project_root/.claude/settings.json")
    settings_files+=("$project_root/.claude/settings.local.json")
  fi

  for f in "${settings_files[@]}"; do
    [[ -f "$f" ]] || continue
    for entry in "${BROAD_PATTERNS[@]}"; do
      IFS='|' read -r colon_pat space_pat explanation <<< "$entry"
      if grep -qF "$colon_pat" "$f" 2>/dev/null || \
         grep -qF "$space_pat" "$f" 2>/dev/null; then
        dominated+=("$colon_pat  in $f|$explanation")
      fi
    done
  done

  if [[ ${#dominated[@]} -eq 0 ]]; then
    return
  fi

  echo ""
  echo "┌─────────────────────────────────────────────────────────────┐"
  echo "│              ⚠  BROAD PERMISSIONS DETECTED                 │"
  echo "└─────────────────────────────────────────────────────────────┘"
  echo ""
  echo "  Found overly broad patterns in your settings:"
  echo ""
  for item in "${dominated[@]}"; do
    local pattern="${item%%|*}"
    local risk="${item#*|}"
    echo "    • $pattern"
    echo "      → $risk"
    echo ""
  done
  echo "  Why this matters: swain-search feeds external content (X threads,"
  echo "  video captions) into Claude's context. Broad patterns widen the"
  echo "  attack surface if any source contains prompt injection. Swap them"
  echo "  for narrow entries (see skills/swain-search/README.md)."
  echo ""
}
audit_permissions

echo "swain-search: dependencies ready."
