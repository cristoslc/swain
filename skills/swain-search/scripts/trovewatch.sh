#!/usr/bin/env bash
set -euo pipefail

# trovewatch — monitor troves for size, freshness, and consistency
#
# Usage:
#   trovewatch.sh scan     Check all troves for issues
#   trovewatch.sh status   Summary of all troves

# --- Configuration ---

TROVES_DIR="docs/troves"
LOG_FILE=".agents/trovewatch.log"
CONFIG_FILE=".agents/trovewatch.vars.json"

# Defaults (overridable via config file)
MAX_SOURCES_PER_TROVE=20
MAX_TROVE_SIZE_MB=5
FRESHNESS_MULTIPLIER="1.5"

# --- Helpers ---

log() {
  echo "$1" >> "$LOG_FILE"
}

warn() {
  echo "  WARN: $1"
  log "WARN $1"
}

die() {
  echo "trovewatch: error: $1" >&2
  exit 2
}

# Load config overrides if present
load_config() {
  if [ -f "$CONFIG_FILE" ]; then
    local val
    val=$(uv run python3 -c "
import json, sys
try:
    c = json.load(open('$CONFIG_FILE'))
    print(c.get('max_sources_per_trove', c.get('max_sources_per_pool', '')))
    print(c.get('max_trove_size_mb', c.get('max_pool_size_mb', '')))
    print(c.get('freshness_multiplier', ''))
except Exception:
    print(''); print(''); print('')
" 2>/dev/null)
    local line1 line2 line3
    line1=$(echo "$val" | sed -n '1p')
    line2=$(echo "$val" | sed -n '2p')
    line3=$(echo "$val" | sed -n '3p')
    [ -n "$line1" ] && MAX_SOURCES_PER_TROVE="$line1"
    [ -n "$line2" ] && MAX_TROVE_SIZE_MB="$line2"
    [ -n "$line3" ] && FRESHNESS_MULTIPLIER="$line3"
  fi
}

# Parse TTL string (e.g., "7d", "2w", "1m", "never") to seconds
ttl_to_seconds() {
  local ttl="$1"
  case "$ttl" in
    never) echo "0"; return ;;
    *d) echo $(( ${ttl%d} * 86400 )) ;;
    *w) echo $(( ${ttl%w} * 604800 )) ;;
    *m) echo $(( ${ttl%m} * 2592000 )) ;;
    *) echo "0" ;;
  esac
}

# Parse ISO date to epoch seconds
date_to_epoch() {
  local d="$1"
  # Handle both "2026-03-09" and "2026-03-09T14:30:00Z" formats
  if command -v gdate >/dev/null 2>&1; then
    gdate -d "$d" +%s 2>/dev/null || echo "0"
  else
    date -jf "%Y-%m-%dT%H:%M:%SZ" "$d" +%s 2>/dev/null || \
    date -jf "%Y-%m-%d" "$d" +%s 2>/dev/null || \
    echo "0"
  fi
}

now_epoch() {
  date +%s
}

# Get directory size in MB (integer)
dir_size_mb() {
  du -sm "$1" 2>/dev/null | cut -f1
}

# --- Trove scanning ---

scan_trove() {
  local trove_dir="$1"
  local trove_id
  trove_id=$(basename "$trove_dir")
  local manifest="$trove_dir/manifest.yaml"
  local sources_dir="$trove_dir/sources"
  local issues=0

  echo "Trove: $trove_id"
  log "SCAN $trove_id"

  # Check manifest exists
  if [ ! -f "$manifest" ]; then
    warn "$trove_id: missing manifest.yaml"
    issues=$((issues + 1))
    echo ""
    return $issues
  fi

  # Check source count (count directories in sources/)
  local source_count=0
  if [ -d "$sources_dir" ]; then
    source_count=$(find "$sources_dir" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
  fi

  if [ "$source_count" -gt "$MAX_SOURCES_PER_TROVE" ]; then
    warn "$trove_id: $source_count sources (max: $MAX_SOURCES_PER_TROVE) — consider splitting or pruning"
    log "SIZE_WARN $trove_id sources=$source_count max=$MAX_SOURCES_PER_TROVE"
    issues=$((issues + 1))
  fi

  # Check trove size
  local size_mb
  size_mb=$(dir_size_mb "$trove_dir")
  if [ "$size_mb" -gt "$MAX_TROVE_SIZE_MB" ]; then
    warn "$trove_id: ${size_mb}MB (max: ${MAX_TROVE_SIZE_MB}MB) — consider removing large sources"
    log "SIZE_WARN $trove_id size=${size_mb}MB max=${MAX_TROVE_SIZE_MB}MB"
    issues=$((issues + 1))
  fi

  # Parse manifest for source entries and check freshness + consistency
  if command -v uv >/dev/null 2>&1; then
    local py_result
    py_result=$(uv run --with pyyaml python3 << PYEOF
import yaml, os, sys
from datetime import datetime, timezone

manifest_path = "$manifest"
sources_dir = "$sources_dir"
trove_id = "$trove_id"
freshness_mult = float("$FRESHNESS_MULTIPLIER")

try:
    with open(manifest_path) as f:
        m = yaml.safe_load(f)
except Exception as e:
    print(f"MANIFEST_ERROR {trove_id}: {e}")
    sys.exit(0)

if not m or not isinstance(m, dict):
    print(f"MANIFEST_ERROR {trove_id}: empty or invalid")
    sys.exit(0)

sources = m.get("sources", []) or []
default_ttls = m.get("freshness-ttl", {}) or {}
now = datetime.now(timezone.utc)

# Map of TTL strings to seconds
def ttl_seconds(ttl_str):
    if not ttl_str or ttl_str == "never":
        return 0
    s = ttl_str.strip()
    if s.endswith("d"):
        return int(s[:-1]) * 86400
    elif s.endswith("w"):
        return int(s[:-1]) * 604800
    elif s.endswith("m"):
        return int(s[:-1]) * 2592000
    return 0

manifest_source_ids = set()
for src in sources:
    source_id = src.get("source-id", "unknown")
    stype = src.get("type", "web")
    fetched_str = src.get("fetched", "")
    selective = src.get("selective", False)
    manifest_source_ids.add(source_id)

    # Check freshness
    ttl_str = src.get("freshness-ttl") or default_ttls.get(stype, "7d")
    ttl_secs = ttl_seconds(ttl_str)

    if ttl_secs > 0 and fetched_str:
        try:
            if "T" in str(fetched_str):
                fetched = datetime.fromisoformat(str(fetched_str).replace("Z", "+00:00"))
            else:
                fetched = datetime.fromisoformat(str(fetched_str)).replace(tzinfo=timezone.utc)
            age_secs = (now - fetched).total_seconds()
            threshold = ttl_secs * freshness_mult
            if age_secs > threshold:
                age_days = int(age_secs / 86400)
                print(f"STALE {trove_id}/{source_id}: {age_days}d old (ttl: {ttl_str})")
        except Exception:
            pass

    # Check source directory/file exists (skip if selective)
    if not selective:
        source_path = os.path.join(sources_dir, source_id)
        if os.path.isdir(source_path):
            # Hierarchical source — check directory is non-empty
            if not os.listdir(source_path):
                print(f"MISSING_FILE {trove_id}: source directory {source_id}/ exists but is empty")
        elif os.path.isfile(os.path.join(source_path, source_id + ".md")):
            # Flat source — file exists inside its directory (should not reach here if dir doesn't exist)
            pass
        elif not os.path.isdir(source_path):
            print(f"MISSING_FILE {trove_id}: manifest has {source_id} but directory not found")

# Check for orphaned directories in sources/
if os.path.isdir(sources_dir):
    for entry in os.listdir(sources_dir):
        entry_path = os.path.join(sources_dir, entry)
        if os.path.isdir(entry_path) and entry not in manifest_source_ids:
            print(f"ORPHAN {trove_id}: {entry}/ exists but not in manifest")

# Check synthesis exists
if not os.path.isfile(os.path.join(os.path.dirname(sources_dir), "synthesis.md")):
    print(f"MISSING_SYNTHESIS {trove_id}: no synthesis.md")
PYEOF
    )

    if [ -n "$py_result" ]; then
      while IFS= read -r line; do
        case "$line" in
          STALE*)
            warn "${line#STALE }"
            log "$line"
            issues=$((issues + 1))
            ;;
          MISSING_FILE*|ORPHAN*|MISSING_SYNTHESIS*|MANIFEST_ERROR*)
            warn "${line#* }"
            log "$line"
            issues=$((issues + 1))
            ;;
        esac
      done <<< "$py_result"
    fi
  fi

  if [ "$issues" -eq 0 ]; then
    echo "  healthy ($source_count sources, ${size_mb}MB)"
  fi
  echo ""

  return $issues
}

# --- Status ---

status_trove() {
  local trove_dir="$1"
  local trove_id
  trove_id=$(basename "$trove_dir")
  local manifest="$trove_dir/manifest.yaml"
  local sources_dir="$trove_dir/sources"

  local source_count=0
  if [ -d "$sources_dir" ]; then
    source_count=$(find "$sources_dir" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
  fi

  local size_mb
  size_mb=$(dir_size_mb "$trove_dir")

  local refreshed="unknown"
  local tags=""
  if [ -f "$manifest" ] && command -v uv >/dev/null 2>&1; then
    local py_out
    py_out=$(uv run --with pyyaml python3 -c "
import yaml
with open('$manifest') as f:
    m = yaml.safe_load(f) or {}
print(m.get('refreshed', 'unknown'))
print(','.join(m.get('tags', []) or []))
" 2>/dev/null)
    refreshed=$(echo "$py_out" | sed -n '1p')
    tags=$(echo "$py_out" | sed -n '2p')
  fi

  printf "  %-30s %3s sources  %3sMB  refreshed: %-12s  tags: %s\n" \
    "$trove_id" "$source_count" "$size_mb" "$refreshed" "$tags"
}

# --- Main ---

main() {
  local cmd="${1:-help}"

  load_config
  mkdir -p "$(dirname "$LOG_FILE")"

  case "$cmd" in
    scan)
      echo "" > "$LOG_FILE"
      log "=== trovewatch scan $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

      if [ ! -d "$TROVES_DIR" ]; then
        echo "trovewatch: no troves found (${TROVES_DIR}/ does not exist)."
        exit 0
      fi

      local total_issues=0
      local trove_count=0

      echo "trovewatch: scanning troves..."
      echo ""

      for trove_dir in "$TROVES_DIR"/*/; do
        [ -d "$trove_dir" ] || continue
        trove_count=$((trove_count + 1))
        scan_trove "$trove_dir" || total_issues=$((total_issues + $?))
      done

      if [ "$trove_count" -eq 0 ]; then
        echo "trovewatch: no troves found in ${TROVES_DIR}/."
        exit 0
      fi

      if [ "$total_issues" -gt 0 ]; then
        echo "trovewatch: found ${total_issues} issue(s) across ${trove_count} trove(s). See ${LOG_FILE}"
        exit 1
      else
        echo "trovewatch: all ${trove_count} trove(s) healthy."
        exit 0
      fi
      ;;

    status)
      if [ ! -d "$TROVES_DIR" ]; then
        echo "trovewatch: no troves found."
        exit 0
      fi

      local trove_count=0
      echo "Troves:"
      echo ""

      for trove_dir in "$TROVES_DIR"/*/; do
        [ -d "$trove_dir" ] || continue
        trove_count=$((trove_count + 1))
        status_trove "$trove_dir"
      done

      if [ "$trove_count" -eq 0 ]; then
        echo "  (none)"
      fi
      echo ""
      echo "${trove_count} trove(s) total."
      ;;

    help|--help|-h)
      echo "Usage: trovewatch.sh <command>"
      echo ""
      echo "Commands:"
      echo "  scan     Check all troves for size, freshness, and consistency issues"
      echo "  status   Summary of all troves"
      echo ""
      echo "Configuration: .agents/trovewatch.vars.json"
      echo "  max_sources_per_trove  (default: 20)"
      echo "  max_trove_size_mb      (default: 5)"
      echo "  freshness_multiplier   (default: 1.5)"
      ;;

    *)
      die "unknown command: $cmd (try: scan, status, help)"
      ;;
  esac
}

main "$@"
