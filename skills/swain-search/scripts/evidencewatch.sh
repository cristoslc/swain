#!/usr/bin/env bash
set -euo pipefail

# evidencewatch — monitor evidence pools for size, freshness, and consistency
#
# Usage:
#   evidencewatch.sh scan     Check all pools for issues
#   evidencewatch.sh status   Summary of all pools

# --- Configuration ---

POOLS_DIR="docs/evidence-pools"
LOG_FILE=".agents/evidencewatch.log"
CONFIG_FILE=".agents/evidencewatch.vars.json"

# Defaults (overridable via config file)
MAX_SOURCES_PER_POOL=20
MAX_POOL_SIZE_MB=5
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
  echo "evidencewatch: error: $1" >&2
  exit 2
}

# Load config overrides if present
load_config() {
  if [ -f "$CONFIG_FILE" ]; then
    local val
    val=$(python3 -c "
import json, sys
try:
    c = json.load(open('$CONFIG_FILE'))
    print(c.get('max_sources_per_pool', ''))
    print(c.get('max_pool_size_mb', ''))
    print(c.get('freshness_multiplier', ''))
except Exception:
    print(''); print(''); print('')
" 2>/dev/null)
    local line1 line2 line3
    line1=$(echo "$val" | sed -n '1p')
    line2=$(echo "$val" | sed -n '2p')
    line3=$(echo "$val" | sed -n '3p')
    [ -n "$line1" ] && MAX_SOURCES_PER_POOL="$line1"
    [ -n "$line2" ] && MAX_POOL_SIZE_MB="$line2"
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

# --- Pool scanning ---

scan_pool() {
  local pool_dir="$1"
  local pool_id
  pool_id=$(basename "$pool_dir")
  local manifest="$pool_dir/manifest.yaml"
  local sources_dir="$pool_dir/sources"
  local issues=0

  echo "Pool: $pool_id"
  log "SCAN $pool_id"

  # Check manifest exists
  if [ ! -f "$manifest" ]; then
    warn "$pool_id: missing manifest.yaml"
    issues=$((issues + 1))
    echo ""
    return $issues
  fi

  # Check source count
  local source_count=0
  if [ -d "$sources_dir" ]; then
    source_count=$(find "$sources_dir" -name '*.md' -type f | wc -l | tr -d ' ')
  fi

  if [ "$source_count" -gt "$MAX_SOURCES_PER_POOL" ]; then
    warn "$pool_id: $source_count sources (max: $MAX_SOURCES_PER_POOL) — consider splitting or pruning"
    log "SIZE_WARN $pool_id sources=$source_count max=$MAX_SOURCES_PER_POOL"
    issues=$((issues + 1))
  fi

  # Check pool size
  local size_mb
  size_mb=$(dir_size_mb "$pool_dir")
  if [ "$size_mb" -gt "$MAX_POOL_SIZE_MB" ]; then
    warn "$pool_id: ${size_mb}MB (max: ${MAX_POOL_SIZE_MB}MB) — consider removing large sources"
    log "SIZE_WARN $pool_id size=${size_mb}MB max=${MAX_POOL_SIZE_MB}MB"
    issues=$((issues + 1))
  fi

  # Parse manifest for source entries and check freshness + consistency
  if command -v python3 >/dev/null 2>&1; then
    local py_result
    py_result=$(python3 << PYEOF
import yaml, os, sys, hashlib
from datetime import datetime, timezone

manifest_path = "$manifest"
sources_dir = "$sources_dir"
pool_id = "$pool_id"
freshness_mult = float("$FRESHNESS_MULTIPLIER")

try:
    with open(manifest_path) as f:
        m = yaml.safe_load(f)
except Exception as e:
    print(f"MANIFEST_ERROR {pool_id}: {e}")
    sys.exit(0)

if not m or not isinstance(m, dict):
    print(f"MANIFEST_ERROR {pool_id}: empty or invalid")
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

manifest_ids = set()
for src in sources:
    sid = src.get("id", "?")
    slug = src.get("slug", "unknown")
    stype = src.get("type", "web")
    fetched_str = src.get("fetched", "")
    manifest_ids.add(f"{sid}-{slug}.md")

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
                print(f"STALE {pool_id}/{sid}-{slug}: {age_days}d old (ttl: {ttl_str})")
        except Exception:
            pass

    # Check source file exists
    expected = os.path.join(sources_dir, f"{sid}-{slug}.md")
    if not os.path.isfile(expected):
        print(f"MISSING_FILE {pool_id}: manifest has {sid}-{slug} but file not found")

# Check for orphaned files
if os.path.isdir(sources_dir):
    for fname in os.listdir(sources_dir):
        if fname.endswith(".md") and fname not in manifest_ids:
            print(f"ORPHAN {pool_id}: {fname} exists but not in manifest")

# Check synthesis exists
if not os.path.isfile(os.path.join(os.path.dirname(sources_dir), "synthesis.md")):
    print(f"MISSING_SYNTHESIS {pool_id}: no synthesis.md")
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

status_pool() {
  local pool_dir="$1"
  local pool_id
  pool_id=$(basename "$pool_dir")
  local manifest="$pool_dir/manifest.yaml"
  local sources_dir="$pool_dir/sources"

  local source_count=0
  if [ -d "$sources_dir" ]; then
    source_count=$(find "$sources_dir" -name '*.md' -type f | wc -l | tr -d ' ')
  fi

  local size_mb
  size_mb=$(dir_size_mb "$pool_dir")

  local refreshed="unknown"
  local tags=""
  if [ -f "$manifest" ] && command -v python3 >/dev/null 2>&1; then
    local py_out
    py_out=$(python3 -c "
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
    "$pool_id" "$source_count" "$size_mb" "$refreshed" "$tags"
}

# --- Main ---

main() {
  local cmd="${1:-help}"

  load_config
  mkdir -p "$(dirname "$LOG_FILE")"

  case "$cmd" in
    scan)
      echo "" > "$LOG_FILE"
      log "=== evidencewatch scan $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

      if [ ! -d "$POOLS_DIR" ]; then
        echo "evidencewatch: no evidence pools found (${POOLS_DIR}/ does not exist)."
        exit 0
      fi

      local total_issues=0
      local pool_count=0

      echo "evidencewatch: scanning evidence pools..."
      echo ""

      for pool_dir in "$POOLS_DIR"/*/; do
        [ -d "$pool_dir" ] || continue
        pool_count=$((pool_count + 1))
        scan_pool "$pool_dir" || total_issues=$((total_issues + $?))
      done

      if [ "$pool_count" -eq 0 ]; then
        echo "evidencewatch: no pools found in ${POOLS_DIR}/."
        exit 0
      fi

      if [ "$total_issues" -gt 0 ]; then
        echo "evidencewatch: found ${total_issues} issue(s) across ${pool_count} pool(s). See ${LOG_FILE}"
        exit 1
      else
        echo "evidencewatch: all ${pool_count} pool(s) healthy."
        exit 0
      fi
      ;;

    status)
      if [ ! -d "$POOLS_DIR" ]; then
        echo "evidencewatch: no evidence pools found."
        exit 0
      fi

      local pool_count=0
      echo "Evidence pools:"
      echo ""

      for pool_dir in "$POOLS_DIR"/*/; do
        [ -d "$pool_dir" ] || continue
        pool_count=$((pool_count + 1))
        status_pool "$pool_dir"
      done

      if [ "$pool_count" -eq 0 ]; then
        echo "  (none)"
      fi
      echo ""
      echo "${pool_count} pool(s) total."
      ;;

    help|--help|-h)
      echo "Usage: evidencewatch.sh <command>"
      echo ""
      echo "Commands:"
      echo "  scan     Check all pools for size, freshness, and consistency issues"
      echo "  status   Summary of all pools"
      echo ""
      echo "Configuration: .agents/evidencewatch.vars.json"
      echo "  max_sources_per_pool  (default: 20)"
      echo "  max_pool_size_mb      (default: 5)"
      echo "  freshness_multiplier  (default: 1.5)"
      ;;

    *)
      die "unknown command: $cmd (try: scan, status, help)"
      ;;
  esac
}

main "$@"
