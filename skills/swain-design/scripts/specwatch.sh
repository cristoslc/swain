#!/bin/bash
# specwatch.sh — Background filesystem watcher for stale path references in docs/
# Detects file moves/renames/deletes and flags stale markdown links with suggested fixes.
# Uses fswatch (macOS FSEvents) with a sentinel-based inactivity timeout.

set -euo pipefail

# --- Resolve repo root ---
# Use the caller's working directory to find the repo root via git,
# not the script's install location (which may be in a different repo).
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 1
}
_src="${BASH_SOURCE[0]}"
while [[ -L "$_src" ]]; do
  _dir="$(cd "$(dirname "$_src")" && pwd)"
  _src="$(readlink "$_src")"
  [[ "$_src" != /* ]] && _src="$_dir/$_src"
done
SPECWATCH_SCRIPT_DIR="$(cd "$(dirname "$_src")" && pwd)"
SPECWATCH_SKILLS_ROOT="$(dirname "$(dirname "$SPECWATCH_SCRIPT_DIR")")"
DOCS_DIR="$REPO_ROOT/docs"
LOG_FILE="$REPO_ROOT/.agents/specwatch.log"
IGNORE_FILE="$REPO_ROOT/.agents/specwatch-ignore"

# --- Sentinel and PID paths (repo-specific) ---
REPO_HASH=$(printf '%s' "$REPO_ROOT" | shasum -a 256 | cut -c1-12)
SENTINEL="/tmp/.specwatch-sentinel-${REPO_HASH}"
PID_FILE="/tmp/.specwatch-pid-${REPO_HASH}"

# --- Defaults ---
TIMEOUT_SECS="${SPECWATCH_TIMEOUT:-3600}"   # 1 hour
CHECK_INTERVAL=60                            # seconds between sentinel age checks
DEBOUNCE_SECS=1                              # batch window for fswatch events

# --- Helpers ---

usage() {
  cat <<'USAGE'
Usage: specwatch.sh <command> [args]

Commands:
  watch              Start background filesystem watcher (default)
  scan               Run a full stale-reference scan (no watcher)
  tk-sync            Check artifact/tk sync state (open tk items for implemented specs, etc.)
  phase-fix          Move artifacts whose phase directory doesn't match frontmatter status
  stop               Stop a running watcher
  status             Show watcher status (running/stopped, log summary)
  touch              Refresh the sentinel keepalive timer

Options:
  --timeout <secs>   Inactivity timeout in seconds (default: 3600)
  --foreground       Run watcher in foreground (for debugging)

Environment:
  SPECWATCH_TIMEOUT  Override default timeout (seconds)
USAGE
}

check_fswatch() {
  if ! command -v fswatch >/dev/null 2>&1; then
    echo "specwatch: fswatch is not installed." >&2
    echo "" >&2
    echo "Install with:" >&2
    echo "  brew install fswatch     # macOS (recommended)" >&2
    echo "  apt install fswatch      # Debian/Ubuntu" >&2
    echo "  cargo install fswatch    # via Rust" >&2
    echo "" >&2
    echo "fswatch uses macOS FSEvents for efficient, kernel-level file monitoring." >&2
    return 1
  fi
}

log_header() {
  {
    echo "# Specwatch log — repo: $(basename "$REPO_ROOT")"
    echo "# Scanned: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""
  } > "$LOG_FILE"
}

# --- Ignore list ---
# Reads .agents/specwatch-ignore for glob patterns to suppress from stale-reference reports.
# Supports blank lines, # comments, and .gitignore-style glob patterns.
# Patterns are matched against: source file path (repo-relative), broken link target, and artifact ID.

IGNORE_PATTERNS=()

load_ignore_patterns() {
  IGNORE_PATTERNS=()
  [ -f "$IGNORE_FILE" ] || return 0
  while IFS= read -r line; do
    # Strip leading/trailing whitespace
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    # Skip blank lines and comments
    [ -z "$line" ] && continue
    [[ "$line" == \#* ]] && continue
    IGNORE_PATTERNS+=("$line")
  done < "$IGNORE_FILE"
}

# is_ignored <source_rel_path> <link_target> <artifact_id>
# Returns 0 (true) if any ignore pattern matches any of the three fields.
is_ignored() {
  local source_path="$1"
  local link_target="$2"
  local artifact_id="$3"
  [ "${#IGNORE_PATTERNS[@]}" -eq 0 ] && return 1
  for pattern in "${IGNORE_PATTERNS[@]}"; do
    # Match against source file path (repo-relative)
    # shellcheck disable=SC2254
    if [[ "$source_path" == $pattern ]]; then return 0; fi
    # Match against the broken link target
    # shellcheck disable=SC2254
    if [[ "$link_target" == $pattern ]]; then return 0; fi
    # Match against the artifact ID (if present)
    if [ -n "$artifact_id" ]; then
      # shellcheck disable=SC2254
      if [[ "$artifact_id" == $pattern ]]; then return 0; fi
    fi
  done
  return 1
}

# --- Stale reference scanner ---
# Extracts markdown links [text](path) pointing to local files, checks existence,
# and suggests corrections using artifact ID extraction.

scan_stale_refs() {
  local mode="${1:-full}"   # "full" or "event" with artifact ID
  local event_id="${2:-}"   # artifact ID for event-driven mode (e.g., ADR-001)
  local found_stale=0
  local found_broken_link=0

  load_ignore_patterns

  log_header

  # Collect all markdown files in docs/
  local -a md_files=()
  while IFS= read -r -d '' f; do
    md_files+=("$f")
  done < <(find "$DOCS_DIR" -name '*.md' -print0 2>/dev/null)

  # Use Python to extract markdown links (handles balanced parens in filenames)
  # Output format: file\tline_num\tlink_target (one per line)
  local links_tmp
  links_tmp=$(mktemp /tmp/specwatch-links-XXXXXX)

  uv run python3 - "${md_files[@]}" > "$links_tmp" <<'PYEOF'
import re, sys

# Regex handles balanced parens: [text](path with (parens) inside)
link_re = re.compile(r'\[([^\]]*)\]\(((?:[^()\s]|\([^()]*\))+)\)')

for filepath in sys.argv[1:]:
    try:
        with open(filepath) as f:
            for line_num, line in enumerate(f, 1):
                for m in link_re.finditer(line):
                    target = m.group(2)
                    # Skip external URLs, anchors, mailto
                    if target.startswith(('http://', 'https://', 'mailto:', '#')):
                        continue
                    # Skip targets that can't be file paths (no / or . means no path separator or extension)
                    if '/' not in target and '.' not in target:
                        continue
                    print(f"{filepath}\t{line_num}\t{target}")
    except (OSError, UnicodeDecodeError):
        pass
PYEOF

  # Process extracted links
  while IFS=$'\t' read -r md_file line_num link_target; do
    local dir
    dir="$(dirname "$md_file")"

    # Strip any anchor from the path
    local clean_path="${link_target%%#*}"
    [ -z "$clean_path" ] && continue

    # Resolve relative to the file's directory
    local resolved_path
    resolved_path="$(cd "$dir" && realpath -q "$clean_path" 2>/dev/null || echo "")"

    # If realpath fails or file doesn't exist, it's stale
    if [ -z "$resolved_path" ] || [ ! -e "$resolved_path" ]; then
      # In event mode, only report if the link mentions the affected artifact
      if [ "$mode" = "event" ] && [ -n "$event_id" ]; then
        case "$link_target" in
          *"$event_id"*) ;;  # matches — continue to report
          *) continue ;;      # doesn't match — skip
        esac
      fi

      # Try to find the new location
      local suggested=""
      local artifact_id=""

      # Extract artifact ID from the path: (TYPE-NNN) or TYPE-NNN
      local paren_id_re='\(([A-Z]+-[0-9]+)\)'
      local bare_id_re='([A-Z]+-[0-9]+)'
      if [[ "$clean_path" =~ $paren_id_re ]]; then
        artifact_id="${BASH_REMATCH[1]}"
      elif [[ "$clean_path" =~ $bare_id_re ]]; then
        artifact_id="${BASH_REMATCH[1]}"
      fi

      # Check ignore list — skip if source path, link target, or artifact ID matches
      local rel_source_check="${md_file#"$REPO_ROOT"/}"
      if is_ignored "$rel_source_check" "$link_target" "$artifact_id"; then
        continue
      fi

      if [ -n "$artifact_id" ]; then
        # Search for the file by artifact ID
        local found_file
        found_file="$(find "$DOCS_DIR" -name "*${artifact_id}*" -name "*.md" -not -name "list-*" 2>/dev/null | head -1)"
        if [ -n "$found_file" ]; then
          # Compute relative path from the source file's directory
          suggested="$(uv run python3 -c "import os; print(os.path.relpath('$found_file', '$dir'))" 2>/dev/null || echo "$found_file")"
        fi
      fi

      # Write structured log entry
      local rel_source
      rel_source="${md_file#"$REPO_ROOT"/}"
      {
        echo "STALE ${rel_source}:${line_num}"
        echo "  broken: ${link_target}"
        if [ -n "$suggested" ]; then
          echo "  found: ${suggested}"
        else
          echo "  found: NONE"
        fi
        echo "  artifact: ${artifact_id:-UNKNOWN}"
        echo ""
      } >> "$LOG_FILE"
      found_stale=1
      # Also emit a BROKEN_LINK entry — specifically for body-text markdown hyperlinks
      echo "BROKEN_LINK ${rel_source}:${line_num} -> ${link_target} (file not found)" >> "$LOG_FILE"
      found_broken_link=1
    fi
  done < "$links_tmp"

  rm -f "$links_tmp"

  # --- Frontmatter reference scan ---
  # Check all frontmatter artifact ID references (depends-on, parent-*, linked-*, etc.)
  # for resolution and semantic coherence.
  local fm_tmp
  fm_tmp=$(mktemp /tmp/specwatch-fm-XXXXXX)

  uv run python3 - "$DOCS_DIR" > "$fm_tmp" <<'PYEOF'
import os, re, sys, glob

docs_dir = sys.argv[1]

# Fields that contain artifact ID references (single-value or list)
SINGLE_REF_FIELDS = ['parent-vision', 'parent-epic', 'superseded-by', 'fix-ref']
LIST_REF_FIELDS = [
    'depends-on-artifacts', 'linked-artifacts', 'artifact-refs', 'addresses',
    'validates', 'affected-artifacts'
]
ALL_REF_FIELDS = SINGLE_REF_FIELDS + LIST_REF_FIELDS

# Terminal/suspicious statuses (for targets)
TERMINAL_STATUSES = {'Abandoned', 'Rejected', 'Superseded'}

# Terminal/closed phases for source artifacts — these are historical records
# and should not warn when referencing Superseded/Retired targets
SOURCE_TERMINAL_PHASES = {
    'Complete', 'Implemented', 'Done',
    'Abandoned', 'Rejected',
    'Retired', 'Archived',
    'Superseded', 'Deprecated',
}

# Phase ordering for mismatch detection (higher = more advanced)
PHASE_ORDER = {
    'Proposed': 0, 'Draft': 0,  # Draft is legacy alias
    'Ready': 1, 'Approved': 1,  # Approved is legacy alias
    'Active': 2, 'Adopted': 2, 'Validated': 2,  # Adopted/Validated are legacy
    'In Progress': 3, 'Implementing': 3,  # Implementing is legacy
    'Needs Manual Test': 4, 'Testing': 4,  # Testing is legacy
    'Complete': 5, 'Implemented': 5, 'Done': 5,  # Implemented/Done are legacy
    'Retired': 6, 'Archived': 6,  # Archived is legacy
    'Superseded': 6,
    'Abandoned': -1, 'Rejected': -1
}

def extract_frontmatter(filepath):
    """Return (dict of fields, artifact_id, status, line_map)."""
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return {}, None, None, {}

    if not lines or lines[0].strip() != '---':
        return {}, None, None, {}

    artifact_id = None
    status = None
    refs = {}        # field_name -> [artifact_id, ...]
    line_map = {}    # field_name -> first line number
    current_list_field = None

    for i, line in enumerate(lines[1:], 2):
        if line.strip() == '---':
            break

        matched = False

        # Single-value field
        for field in SINGLE_REF_FIELDS:
            m = re.match(rf'^{re.escape(field)}:\s*(.+)', line)
            if m:
                val = m.group(1).strip().strip('"').strip("'")
                if val and val.upper() != 'NONE' and re.match(r'^[A-Z]+-\d+', val):
                    refs[field] = [val]
                    line_map[field] = i
                current_list_field = None
                matched = True
                break

        if not matched:
            # List field header or inline value
            for field in LIST_REF_FIELDS:
                m = re.match(rf'^{re.escape(field)}:\s*$', line)
                if m:
                    current_list_field = field
                    line_map.setdefault(field, i)
                    refs.setdefault(field, [])
                    matched = True
                    break
                # Inline single-item list: "field: VALUE" or "field: - VALUE"
                m = re.match(rf'^{re.escape(field)}:\s*-?\s*(.+)', line)
                if m:
                    val = m.group(1).strip().strip('"').strip("'")
                    if val and re.match(r'^[A-Z]+-\d+', val):
                        refs.setdefault(field, []).append(val)
                        line_map.setdefault(field, i)
                    current_list_field = None
                    matched = True
                    break

        # List item continuation
        if not matched and current_list_field:
            m = re.match(r'^\s+-\s+(.+)', line)
            if m:
                val = m.group(1).strip().strip('"').strip("'")
                if val and re.match(r'^[A-Z]+-\d+', val):
                    refs.setdefault(current_list_field, []).append(val)
                # Handle dict-style entries like "artifact: SPEC-067" in artifact-refs
                elif val:
                    kv = re.match(r'^artifact:\s*(.+)', val)
                    if kv:
                        art_val = kv.group(1).strip().strip('"').strip("'")
                        if art_val and re.match(r'^[A-Z]+-\d+', art_val):
                            refs.setdefault(current_list_field, []).append(art_val)
                matched = True
            elif re.match(r'^\s+[a-z]', line):
                # Indented continuation of a dict entry (e.g., "    rel: [documents]")
                # Stay in the current list field but don't extract
                matched = True
            elif not re.match(r'^\s', line):
                current_list_field = None

        # Extract artifact and status (these can coexist with matched)
        if not matched:
            m = re.match(r'^artifact:\s*(.+)', line)
            if m:
                artifact_id = m.group(1).strip().strip('"').strip("'")
            m = re.match(r'^status:\s*(.+)', line)
            if m:
                status = m.group(1).strip().strip('"').strip("'")

    return refs, artifact_id, status, line_map

def resolve_artifact_id(artifact_id, docs_dir):
    """Find the file for an artifact ID. Returns (path, status) or (None, None)."""
    # Search for files/dirs matching the artifact ID
    pattern = os.path.join(docs_dir, '**', f'*{artifact_id}*')
    matches = []
    for p in glob.glob(pattern, recursive=True):
        if p.endswith('.md') and not os.path.basename(p).startswith(('list-', 'README')):
            matches.append(p)

    if not matches:
        return None, None

    # Prefer the primary .md (one whose name contains the artifact ID)
    best = matches[0]
    for m in matches:
        basename = os.path.basename(m)
        if artifact_id in basename:
            best = m
            break

    # Extract status from the target
    _, _, target_status, _ = extract_frontmatter(best)
    return best, target_status

# Build index of all artifacts first (for efficient lookups)
artifact_index = {}  # artifact_id -> (filepath, status)
for root, dirs, files in os.walk(docs_dir):
    for fname in files:
        if not fname.endswith('.md') or fname.startswith(('list-', 'README')):
            continue
        fp = os.path.join(root, fname)
        _, aid, astatus, _ = extract_frontmatter(fp)
        if aid:
            artifact_index[aid] = (fp, astatus)

# Scan all artifacts for frontmatter references
for root, dirs, files in os.walk(docs_dir):
    for fname in files:
        if not fname.endswith('.md') or fname.startswith(('list-', 'README')):
            continue
        filepath = os.path.join(root, fname)
        refs, source_id, source_status, line_map = extract_frontmatter(filepath)
        if not refs or not source_id:
            continue

        rel_source = os.path.relpath(filepath, os.path.dirname(docs_dir))

        for field, targets in refs.items():
            line_num = line_map.get(field, 0)
            for target_id in targets:
                # Strip any "PP-NN" suffix for pain point refs (JOURNEY-001.PP-02)
                base_id = target_id.split('.')[0] if '.' in target_id else target_id

                if base_id in artifact_index:
                    target_path, target_status = artifact_index[base_id]
                    rel_target = os.path.relpath(target_path, os.path.dirname(docs_dir))

                    # Check for terminal status — but only warn if
                    # the SOURCE artifact is still active (not terminal/closed).
                    # Closed artifacts referencing Superseded/Retired targets
                    # are historical records and don't need updating.
                    if target_status in TERMINAL_STATUSES and source_status not in SOURCE_TERMINAL_PHASES:
                        print(f"WARN\t{rel_source}\t{line_num}\t{field}\t{target_id}\t{rel_target}\ttarget is {target_status}")

                    # Check for phase mismatch
                    elif source_status and target_status:
                        src_order = PHASE_ORDER.get(source_status, -99)
                        tgt_order = PHASE_ORDER.get(target_status, -99)
                        # Flag if source is significantly more advanced than target
                        # (e.g., source is Complete but target is still Proposed)
                        if src_order >= 3 and tgt_order <= 0 and tgt_order != -1:
                            print(f"WARN\t{rel_source}\t{line_num}\t{field}\t{target_id}\t{rel_target}\tsource is {source_status} but target is still {target_status}")
                else:
                    # Unresolvable — try a filesystem search as fallback
                    found, _ = resolve_artifact_id(base_id, docs_dir)
                    if found:
                        # Index was stale? Shouldn't happen, but handle gracefully
                        rel_found = os.path.relpath(found, os.path.dirname(docs_dir))
                        print(f"WARN\t{rel_source}\t{line_num}\t{field}\t{target_id}\t{rel_found}\tresolved by search but missing from index")
                    else:
                        print(f"STALE_REF\t{rel_source}\t{line_num}\t{field}\t{target_id}\tNONE\tunresolvable artifact ID")
PYEOF

  # Process frontmatter reference results
  while IFS=$'\t' read -r severity rel_source line_num field target_id resolved issue; do
    [ -z "$severity" ] && continue

    # Check ignore list
    local artifact_id_from_target=""
    artifact_id_from_target="$target_id"
    if is_ignored "$rel_source" "$target_id" "$artifact_id_from_target"; then
      continue
    fi

    {
      echo "${severity} ${rel_source}:${line_num} (frontmatter)"
      echo "  field: ${field}"
      echo "  target: ${target_id}"
      echo "  resolved: ${resolved}"
      echo "  issue: ${issue}"
      echo ""
    } >> "$LOG_FILE"
    found_stale=1
  done < "$fm_tmp"

  rm -f "$fm_tmp"

  if [ "$found_stale" -eq 0 ] && [ "$found_broken_link" -eq 0 ]; then
    echo "specwatch: no stale references found."
  else
    local stale_count warn_count broken_link_count
    stale_count=$(grep -c '^STALE' "$LOG_FILE" 2>/dev/null)
    stale_count=${stale_count:-0}
    warn_count=$(grep -c '^WARN' "$LOG_FILE" 2>/dev/null)
    warn_count=${warn_count:-0}
    broken_link_count=$(grep -c '^BROKEN_LINK' "$LOG_FILE" 2>/dev/null)
    broken_link_count=${broken_link_count:-0}
    echo "specwatch: found ${stale_count} stale reference(s), ${warn_count} warning(s), ${broken_link_count} broken link(s). See ${LOG_FILE}"
  fi
  return $(( found_stale > 0 || found_broken_link > 0 ? 1 : 0 ))
}

# --- TK sync checker ---
# Cross-references artifact phase/status with tk item state.
# Detects: open tk items for Complete/Abandoned artifacts,
#          all-closed tk items for still-active artifacts.
# Requires: vendored ticket-query plugin and .tickets/ initialized.

scan_tk_sync() {
  # Locate vendored ticket-query plugin
  local TICKET_QUERY="$SPECWATCH_SKILLS_ROOT/swain-do/bin/ticket-query"
  if [ ! -x "$TICKET_QUERY" ]; then
    echo "specwatch tk-sync: ticket-query not found at $TICKET_QUERY, skipping."
    return 0
  fi
  if [ ! -d "$REPO_ROOT/.tickets" ]; then
    echo "specwatch tk-sync: no .tickets/ directory, skipping."
    return 0
  fi

  local found_mismatch=0

  # Ensure log file exists with header if this is a standalone run
  if [ ! -f "$LOG_FILE" ] || ! grep -q '^# Specwatch log' "$LOG_FILE" 2>/dev/null; then
    log_header
  fi

  # Get all tk items as JSON (via vendored ticket-query plugin)
  local tk_items_tmp
  tk_items_tmp=$(mktemp /tmp/specwatch-tk-XXXXXX)
  "$TICKET_QUERY" > "$tk_items_tmp" 2>/dev/null || {
    echo "specwatch tk-sync: ticket-query failed, skipping."
    rm -f "$tk_items_tmp"
    return 0
  }

  # Build artifact index and cross-reference with tk items
  uv run python3 - "$DOCS_DIR" "$tk_items_tmp" >> "$LOG_FILE" <<'PYEOF'
import json, os, re, sys

docs_dir = sys.argv[1]
tk_items_file = sys.argv[2]

# Terminal artifact statuses (implementation is done or artifact is dead)
IMPLEMENTED_STATUSES = {'Implemented', 'Complete', 'Done'}
ABANDONED_STATUSES = {'Abandoned', 'Rejected'}
TERMINAL_STATUSES = IMPLEMENTED_STATUSES | ABANDONED_STATUSES
# Active statuses where open tk items are expected
ACTIVE_STATUSES = {'Proposed', 'Draft', 'Active', 'Ready', 'Approved',
                   'Validated', 'Adopted', 'In Progress', 'Implementing',
                   'Needs Manual Test', 'Testing', 'Review'}

def extract_frontmatter(filepath):
    """Return (artifact_id, status) from YAML frontmatter."""
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return None, None
    if not lines or lines[0].strip() != '---':
        return None, None
    artifact_id = None
    status = None
    for line in lines[1:]:
        if line.strip() == '---':
            break
        m = re.match(r'^artifact:\s*(.+)', line)
        if m:
            artifact_id = m.group(1).strip().strip('"').strip("'")
        m = re.match(r'^status:\s*(.+)', line)
        if m:
            status = m.group(1).strip().strip('"').strip("'")
    return artifact_id, status

# Build artifact index: artifact_id -> (rel_path, status)
artifact_index = {}
for root, dirs, files in os.walk(docs_dir):
    for fname in files:
        if not fname.endswith('.md') or fname.startswith(('list-', 'README')):
            continue
        fp = os.path.join(root, fname)
        aid, astatus = extract_frontmatter(fp)
        if aid:
            rel = os.path.relpath(fp, os.path.dirname(docs_dir))
            artifact_index[aid] = (rel, astatus)

# Load tk items
try:
    with open(tk_items_file) as f:
        tk_items = json.load(f)
except (json.JSONDecodeError, OSError):
    tk_items = []

if not isinstance(tk_items, list):
    tk_items = []

# Group tk items by artifact ID (via external-ref and spec: tags)
# artifact_id -> {'open': [...], 'closed': [...]}
artifact_tk_map = {}

for item in tk_items:
    item_id = item.get('id', '?')
    item_status = item.get('status', '')
    item_title = item.get('title', '')
    is_open = item_status in ('open', 'in_progress', 'blocked')

    # Check external-ref (tk uses hyphenated field name)
    ext_ref = item.get('external-ref', '') or item.get('external_ref', '') or ''
    if ext_ref:
        artifact_tk_map.setdefault(ext_ref, {'open': [], 'closed': []})
        bucket = 'open' if is_open else 'closed'
        artifact_tk_map[ext_ref][bucket].append({
            'id': item_id, 'status': item_status, 'title': item_title
        })

    # Check spec: tags (tk uses 'tags' instead of 'labels')
    tags = item.get('tags', []) or item.get('labels', []) or []
    for tag in tags:
        if isinstance(tag, str) and tag.startswith('spec:'):
            spec_id = tag[5:]  # strip "spec:" prefix
            artifact_tk_map.setdefault(spec_id, {'open': [], 'closed': []})
            bucket = 'open' if is_open else 'closed'
            artifact_tk_map[spec_id][bucket].append({
                'id': item_id, 'status': item_status, 'title': item_title
            })

# Detect mismatches
mismatches = []

for artifact_id, tk_state in artifact_tk_map.items():
    if artifact_id not in artifact_index:
        # tk references an artifact that doesn't exist in docs/
        if tk_state['open']:
            open_ids = ', '.join(i['id'] for i in tk_state['open'])
            mismatches.append({
                'type': 'TK_ORPHAN',
                'artifact': artifact_id,
                'issue': f"tk has open items ({open_ids}) referencing non-existent artifact",
                'tk_items': tk_state['open']
            })
        continue

    rel_path, art_status = artifact_index[artifact_id]

    # Case 1: Artifact is Complete but tk still has open items
    if art_status in IMPLEMENTED_STATUSES and tk_state['open']:
        open_ids = ', '.join(i['id'] for i in tk_state['open'])
        mismatches.append({
            'type': 'TK_SYNC',
            'artifact': artifact_id,
            'artifact_path': rel_path,
            'artifact_status': art_status,
            'issue': f"artifact is {art_status} but tk has open items: {open_ids}",
            'tk_items': tk_state['open']
        })

    # Case 2: Artifact is Abandoned/Rejected but tk still has open items
    elif art_status in ABANDONED_STATUSES and tk_state['open']:
        open_ids = ', '.join(i['id'] for i in tk_state['open'])
        mismatches.append({
            'type': 'TK_SYNC',
            'artifact': artifact_id,
            'artifact_path': rel_path,
            'artifact_status': art_status,
            'issue': f"artifact is {art_status} but tk has open items: {open_ids}",
            'tk_items': tk_state['open']
        })

    # Case 3: All tk items closed but artifact is still active (not terminal)
    elif (art_status in ACTIVE_STATUSES
          and tk_state['closed'] and not tk_state['open']
          and len(tk_state['closed']) > 0):
        closed_count = len(tk_state['closed'])
        mismatches.append({
            'type': 'TK_SYNC',
            'artifact': artifact_id,
            'artifact_path': rel_path,
            'artifact_status': art_status,
            'issue': f"all {closed_count} tk item(s) are closed but artifact is still {art_status}",
            'tk_items': tk_state['closed']
        })

# Output structured log entries
for m in mismatches:
    mtype = m['type']
    artifact = m['artifact']
    issue = m['issue']
    art_path = m.get('artifact_path', 'N/A')
    art_status = m.get('artifact_status', 'N/A')
    items = m.get('tk_items', [])

    print(f"{mtype} {art_path} ({artifact})")
    print(f"  artifact-status: {art_status}")
    print(f"  issue: {issue}")
    for item in items[:5]:  # cap at 5 items per entry
        print(f"  tk-item: {item['id']} [{item['status']}] {item['title']}")
    print()
PYEOF

  rm -f "$tk_items_tmp"

  # Count mismatches in log
  local sync_count
  sync_count=$(grep -c '^TK_SYNC\|^TK_ORPHAN' "$LOG_FILE" 2>/dev/null)
  sync_count=${sync_count:-0}

  if [ "$sync_count" -gt 0 ]; then
    echo "specwatch tk-sync: found ${sync_count} artifact/tk mismatch(es). See ${LOG_FILE}"
    echo "  Invoke swain-do to reconcile (close stale items or transition artifacts)."
    return 1
  else
    echo "specwatch tk-sync: artifacts and tk items are in sync."
    return 0
  fi
}

# --- Architecture diagram checker ---
# Warns (ARCH_NO_DIAGRAM) for architecture-overview.md files that have no diagram.
# A diagram is: a mermaid code block, an image reference, or a ## Diagram heading.

scan_arch_diagrams() {
  local warn_count=0
  while IFS= read -r arch_file; do
    [ -f "$arch_file" ] || continue
    # Check for mermaid block, image reference, or diagram section heading
    if grep -qE '```mermaid|!\[.*\]\(.*\)|^## .*[Dd]iagram' "$arch_file" 2>/dev/null; then
      continue
    fi
    echo "ARCH_NO_DIAGRAM: $arch_file (no mermaid block, image reference, or ## Diagram heading found)"
    warn_count=$(( warn_count + 1 ))
  done < <(find "$REPO_ROOT/docs" -name "architecture-overview.md" 2>/dev/null)

  if [ "$warn_count" -gt 0 ]; then
    echo "specwatch arch-diagrams: found ${warn_count} architecture overview(s) without a diagram."
    return 1
  else
    echo "specwatch arch-diagrams: all architecture overviews have diagrams."
    return 0
  fi
}

# --- Sentinel management ---

touch_sentinel() {
  touch "$SENTINEL"
}

sentinel_age() {
  if [ ! -f "$SENTINEL" ]; then
    echo "999999"
    return
  fi
  local now
  now=$(date +%s)
  local mod
  mod=$(stat -f %m "$SENTINEL" 2>/dev/null || stat -c %Y "$SENTINEL" 2>/dev/null || echo "0")
  echo $(( now - mod ))
}

# --- Watcher lifecycle ---

is_running() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
    # Stale PID file
    rm -f "$PID_FILE"
  fi
  return 1
}

stop_watcher() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null
      echo "specwatch: stopped watcher (PID $pid)."
    else
      echo "specwatch: watcher not running (stale PID file removed)."
    fi
    rm -f "$PID_FILE"
  else
    echo "specwatch: no watcher running."
  fi
}

show_status() {
  if is_running; then
    local pid
    pid=$(cat "$PID_FILE")
    local age
    age=$(sentinel_age)
    local remaining=$(( TIMEOUT_SECS - age ))
    [ "$remaining" -lt 0 ] && remaining=0
    echo "specwatch: running (PID $pid)"
    echo "  sentinel age: ${age}s"
    echo "  timeout in: ${remaining}s"
  else
    echo "specwatch: not running"
  fi

  if [ -f "$LOG_FILE" ]; then
    local count
    count=$(grep -c '^STALE ' "$LOG_FILE" 2>/dev/null)
    count=${count:-0}
    echo "  stale refs in log: $count"
  else
    echo "  log: clean"
  fi
}

run_watcher() {
  local foreground="${1:-false}"

  check_fswatch || return 1

  if is_running; then
    local pid
    pid=$(cat "$PID_FILE")
    echo "specwatch: already running (PID $pid). Use 'specwatch.sh stop' first."
    return 1
  fi

  touch_sentinel

  if [ "$foreground" = "true" ]; then
    echo "specwatch: watching $DOCS_DIR (foreground, timeout=${TIMEOUT_SECS}s)"
    _watcher_loop
  else
    _watcher_loop &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    echo "specwatch: started (PID $pid, timeout=${TIMEOUT_SECS}s)"
    echo "  log: $LOG_FILE"
    echo "  sentinel: $SENTINEL"
  fi
}

_watcher_loop() {
  # Write our PID if running in foreground (background case writes it in run_watcher)
  trap '_cleanup' EXIT INT TERM

  # Start fswatch in the background, collecting events
  local batch_file
  batch_file=$(mktemp /tmp/specwatch-batch-XXXXXX)

  fswatch -r "$DOCS_DIR" \
    --include '\.md$' \
    --exclude '.*' \
    --batch-marker=EOF \
    -0 2>/dev/null | while IFS= read -r -d '' event; do
    if [ "$event" = "EOF" ]; then
      # Process the batch: extract any artifact IDs from changed paths
      if [ -s "$batch_file" ]; then
        # Debounce: wait a moment for additional events
        sleep "$DEBOUNCE_SECS"

        # Extract artifact IDs from the changed file paths
        local ids=""
        local paren_id_re='\(([A-Z]+-[0-9]+)\)'
        local bare_id_re='([A-Z]+-[0-9]+)'
        while IFS= read -r changed_path; do
          if [[ "$changed_path" =~ $paren_id_re ]]; then
            ids="${ids:+$ids }${BASH_REMATCH[1]}"
          elif [[ "$changed_path" =~ $bare_id_re ]]; then
            ids="${ids:+$ids }${BASH_REMATCH[1]}"
          fi
        done < "$batch_file"

        # Run scan (event-driven if we found IDs, full otherwise)
        if [ -n "$ids" ]; then
          for id in $ids; do
            scan_stale_refs "event" "$id" >/dev/null 2>&1 || true
          done
        else
          scan_stale_refs "full" >/dev/null 2>&1 || true
        fi
      fi
      : > "$batch_file"  # clear for next batch
    else
      echo "$event" >> "$batch_file"
    fi

    # Check sentinel age
    local age
    age=$(sentinel_age)
    if [ "$age" -ge "$TIMEOUT_SECS" ]; then
      echo "specwatch: inactivity timeout (${age}s >= ${TIMEOUT_SECS}s). Shutting down." >&2
      break
    fi
  done

  rm -f "$batch_file"
}

_cleanup() {
  rm -f "$PID_FILE"
  # Kill any fswatch children
  jobs -p 2>/dev/null | xargs -r kill 2>/dev/null || true
}

# --- Phase/folder mismatch checker ---
# Every artifact lives in docs/<type>/<Phase>/<artifact>.
# This command checks that the frontmatter status: matches the phase subdirectory
# and moves mismatched artifacts with git mv.

phase_fix() {
  if [ ! -d "$DOCS_DIR" ]; then
    echo "specwatch phase-fix: no docs/ directory found."
    return 0
  fi

  local mismatches=0
  local fixed=0

  # Use Python to scan all markdown files, extract frontmatter status and artifact ID,
  # and compare against the directory structure.
  # Output format: action\tartifact_path\texpected_phase\tactual_phase\tstatus
  local results
  results=$(uv run python3 - "$DOCS_DIR" <<'PYEOF'
import os, re, sys

docs_dir = sys.argv[1]

# Known type directories and whether artifacts are folders or files
# (folder-based have a primary .md inside; file-based are the .md directly)
TYPE_DIRS = {
    'vision', 'journey', 'epic', 'story', 'spec',
    'research', 'adr', 'persona', 'runbook', 'design', 'train'
}

def extract_frontmatter(filepath):
    """Extract status and artifact fields from YAML frontmatter."""
    status = None
    artifact = None
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return None, None

    if not lines or lines[0].strip() != '---':
        return None, None

    for line in lines[1:]:
        if line.strip() == '---':
            break
        m = re.match(r'^status:\s*(.+)', line)
        if m:
            status = m.group(1).strip().strip('"').strip("'")
        m = re.match(r'^artifact:\s*(.+)', line)
        if m:
            artifact = m.group(1).strip().strip('"').strip("'")

    return status, artifact

for root, dirs, files in os.walk(docs_dir):
    for fname in files:
        if not fname.endswith('.md'):
            continue
        # Skip index files and READMEs
        if fname.startswith('list-') or fname == 'README.md':
            continue

        filepath = os.path.join(root, fname)
        status, artifact_id = extract_frontmatter(filepath)

        if not status or not artifact_id:
            continue

        # Determine the path components relative to docs/
        rel = os.path.relpath(filepath, docs_dir)
        parts = rel.split(os.sep)

        # Expected structure: <type_dir>/<phase_dir>/<artifact...>
        # Need at least: type_dir/phase_dir/something
        if len(parts) < 3:
            # File is directly in type_dir (no phase subdir) — that's a mismatch
            if len(parts) == 2 and parts[0] in TYPE_DIRS:
                type_dir = parts[0]
                actual_phase = "(none)"
                # The artifact is at docs/<type>/<file>.md — needs to be in docs/<type>/<status>/
                artifact_path = filepath
                # For folder-based: check if this .md is inside an artifact folder
                # that's directly in the type dir (no phase subdir)
                print(f"MISMATCH\t{os.path.relpath(filepath, docs_dir)}\t{status}\t{actual_phase}")
            continue

        type_dir = parts[0]
        if type_dir not in TYPE_DIRS:
            continue

        phase_dir = parts[1]

        # Check if the phase directory matches the status
        if phase_dir == status:
            continue  # match — all good

        # It's a mismatch
        print(f"MISMATCH\t{os.path.relpath(filepath, docs_dir)}\t{status}\t{phase_dir}")
PYEOF
  ) || true

  if [ -z "$results" ]; then
    echo "specwatch phase-fix: all artifacts in correct phase directories."
    return 0
  fi

  echo "$results" | while IFS=$'\t' read -r action rel_path expected_phase actual_phase; do
    [ "$action" = "MISMATCH" ] || continue
    mismatches=$(( mismatches + 1 ))

    local full_path="$DOCS_DIR/$rel_path"
    local type_dir
    type_dir=$(echo "$rel_path" | cut -d/ -f1)

    # Determine what to move: the artifact folder or the file itself.
    # For folder-based artifacts, the .md is inside (TYPE-NNN)-Title/,
    # so we move the parent directory. For file-based (story, bug, adr),
    # the .md IS the artifact.
    local artifact_item=""
    local item_name=""
    local parts
    IFS='/' read -ra parts <<< "$rel_path"

    if [ "${#parts[@]}" -ge 4 ]; then
      # e.g., epic/Proposed/(EPIC-001)-Foo/(EPIC-001)-Foo.md — move the folder
      artifact_item="$DOCS_DIR/${parts[0]}/${parts[1]}/${parts[2]}"
      item_name="${parts[2]}"
    elif [ "${#parts[@]}" -eq 3 ]; then
      # e.g., adr/Proposed/(ADR-001)-Foo.md — move the file
      #    or adr/Proposed/(ADR-001)-Foo.md
      if [ -d "$DOCS_DIR/${parts[0]}/${parts[1]}/${parts[2]%%.*}" ] 2>/dev/null; then
        # Actually a folder artifact where the .md name matches the folder
        artifact_item="$DOCS_DIR/${parts[0]}/${parts[1]}/${parts[2]%%.*}"
        item_name="${parts[2]%%.*}"
      else
        artifact_item="$full_path"
        item_name="${parts[2]}"
      fi
    else
      # Unexpected structure — skip
      echo "  SKIP: $rel_path (unexpected path depth)"
      continue
    fi

    local target_dir="$DOCS_DIR/$type_dir/$expected_phase"
    local target_path="$target_dir/$item_name"

    # Create target phase directory if needed
    mkdir -p "$target_dir"
    if [ -e "$artifact_item" ]; then
      git -C "$REPO_ROOT" mv "$artifact_item" "$target_path" 2>/dev/null
      if [ $? -eq 0 ]; then
        echo "  MOVED: $type_dir/${actual_phase}/$item_name -> $type_dir/${expected_phase}/$item_name"
        fixed=$(( fixed + 1 ))
      else
        echo "  FAILED: $type_dir/${actual_phase}/$item_name (git mv error)"
      fi
    else
      echo "  SKIP: $artifact_item does not exist"
    fi
  done

  local total
  total=$(echo "$results" | grep -c '^MISMATCH')
  total=${total:-0}
  echo "specwatch phase-fix: $total mismatch(es) found, moved artifacts to correct phase directories."
  echo "  Run 'git status' to review staged moves, then commit."
  echo ""
  echo "Scanning for stale references caused by moves..."
  scan_stale_refs "full" || true
}

# --- Main dispatch ---

cmd="${1:-watch}"
shift 2>/dev/null || true

case "$cmd" in
  watch)
    foreground=false
    while [ $# -gt 0 ]; do
      case "$1" in
        --timeout) TIMEOUT_SECS="$2"; shift 2 ;;
        --foreground) foreground=true; shift ;;
        *) echo "specwatch: unknown option: $1" >&2; exit 1 ;;
      esac
    done
    run_watcher "$foreground"
    ;;
  scan)
    scan_stale_refs "full" || scan_result=$?
    scan_result="${scan_result:-0}"
    scan_tk_sync || tk_result=$?
    tk_result="${tk_result:-0}"
    scan_arch_diagrams || arch_result=$?
    arch_result="${arch_result:-0}"
    # TRAIN staleness check
    train_result=0
    train_check_script="$(dirname "${BASH_SOURCE[0]}")/train-check.sh"
    if [[ -x "$train_check_script" ]]; then
        bash "$train_check_script" || train_result=$?
        if [[ $train_result -eq 2 ]]; then
            train_result=0  # git unavailable is not a scan failure
        fi
    fi
    # DESIGN drift check
    design_result=0
    design_check_script="$(dirname "${BASH_SOURCE[0]}")/design-check.sh"
    if [[ -x "$design_check_script" ]]; then
        bash "$design_check_script" || design_result=$?
        if [[ $design_result -eq 2 ]]; then
            design_result=0  # git unavailable is not a scan failure
        fi
    fi
    # Duplicate artifact number check (SPEC-158)
    dup_result=0
    dup_check_script="$(dirname "${BASH_SOURCE[0]}")/detect-duplicate-numbers.sh"
    if [[ -x "$dup_check_script" ]]; then
        dup_output=$(bash "$dup_check_script" 2>/dev/null) || dup_result=$?
        if [[ $dup_result -ne 0 ]] && [[ -n "$dup_output" ]]; then
            echo "specwatch duplicate-numbers: found collision(s):"
            echo "$dup_output"
        fi
    fi
    exit $(( scan_result > 0 || tk_result > 0 || arch_result > 0 || train_result > 0 || design_result > 0 || dup_result > 0 ? 1 : 0 ))
    ;;
  tk-sync)
    log_header
    scan_tk_sync
    ;;
  phase-fix)
    phase_fix
    ;;
  stop)
    stop_watcher
    ;;
  status)
    show_status
    ;;
  touch)
    touch_sentinel
    echo "specwatch: sentinel refreshed."
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "specwatch: unknown command: $cmd" >&2
    usage >&2
    exit 1
    ;;
esac
