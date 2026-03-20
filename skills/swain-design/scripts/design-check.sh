#!/usr/bin/env bash
# design-check.sh — Blob SHA drift detection for DESIGN artifacts.
#
# Reads sourcecode-refs entries from DESIGN frontmatter.
# Compares pinned blob SHA against the file's current blob SHA at HEAD.
#
# Usage:
#   design-check.sh [path-to-design.md]   Check a single DESIGN
#   design-check.sh                        Check all DESIGNs under docs/design/Active/
#   design-check.sh --repin <design.md>    Update all pins to current HEAD
#   design-check.sh --help                 Show this help
#
# Exit codes:
#   0 — all refs CURRENT or MOVED (content intact)
#   1 — at least one ref is STALE, MOVED+STALE, or BROKEN
#   2 — git unavailable or not in a git repo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "design-check: git not available or not in a git repo" >&2
    exit 2
}

DESIGN_DIR="$REPO_ROOT/docs/design/Active"
LOG_FILE="${REPO_ROOT}/.agents/design-check.log"

MODE="check"
stale_count=0
checked_count=0
moved_count=0
broken_count=0

usage() {
    cat <<'USAGE'
design-check.sh — Blob SHA drift detection for DESIGN artifacts.

Usage:
  design-check.sh [path-to-design.md]   Check a single DESIGN
  design-check.sh                        Check all DESIGNs under docs/design/Active/
  design-check.sh --repin <design.md>    Update all pins to current HEAD
  design-check.sh --help                 Show this help

Exit codes:
  0 — all refs CURRENT or MOVED (content intact)
  1 — at least one ref is STALE, MOVED+STALE, or BROKEN
  2 — git unavailable or not in a git repo

Output format:
  CURRENT <path>
  STALE <path> (<N> commits behind)
  MOVED <old-path> → <new-path>
  MOVED+STALE <old-path> → <new-path> (<N> commits behind)
  BROKEN <path>
USAGE
}

# Parse sourcecode-refs from DESIGN frontmatter using inline Python.
# Outputs tab-separated lines: path\tblob\tcommit\tverified
parse_sourcecode_refs() {
    local design_md="$1"
    uv run python3 -c "
import sys, re

content = open('$design_md').read()
fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
if not fm_match:
    sys.exit(0)

fm = fm_match.group(1)
lines = fm.splitlines()
in_sourcecode_refs = False
current_entry = None
entries = []

for line in lines:
    if re.match(r'^sourcecode-refs:', line):
        in_sourcecode_refs = True
        # Handle empty list on same line: sourcecode-refs: []
        rest = line.split(':', 1)[1].strip()
        if rest == '[]':
            sys.exit(0)
        continue
    if in_sourcecode_refs:
        list_match = re.match(r'^\s+-\s+(.+)$', line)
        if list_match:
            if current_entry and 'path' in current_entry:
                entries.append(current_entry)
            val = list_match.group(1).strip()
            kv = re.match(r'^([a-z][a-z0-9-]*):\s+(.+)$', val)
            if kv:
                current_entry = {kv.group(1): kv.group(2).strip()}
            else:
                current_entry = None
            continue
        indent_kv = re.match(r'^\s+([a-z][a-z0-9-]*):\s+(.+)$', line)
        if indent_kv and current_entry is not None:
            current_entry[indent_kv.group(1)] = indent_kv.group(2).strip()
            continue
        if re.match(r'^[a-z]', line):
            in_sourcecode_refs = False
            if current_entry and 'path' in current_entry:
                entries.append(current_entry)
            current_entry = None

if current_entry and 'path' in current_entry:
    entries.append(current_entry)

for e in entries:
    path = e.get('path', '')
    blob = e.get('blob', '')
    commit = e.get('commit', '')
    verified = e.get('verified', '')
    if path and blob and commit:
        print(f'{path}\t{blob}\t{commit}\t{verified}')
" 2>/dev/null
}

# Check a single sourcecode-ref entry.
# Arguments: path, pinned_blob, pinned_commit, design_id
check_ref() {
    local ref_path="$1"
    local pinned_blob="$2"
    local pinned_commit="$3"
    local design_id="$4"

    # Make path relative to repo root for git operations
    local rel_path="$ref_path"

    checked_count=$((checked_count + 1))

    # Step 1: Does path exist at HEAD?
    local current_blob
    current_blob=$(git -C "$REPO_ROOT" ls-tree HEAD -- "$rel_path" 2>/dev/null | awk '{print $3}')

    if [[ -n "$current_blob" ]]; then
        # Path exists at HEAD
        if [[ "$current_blob" == "$pinned_blob" ]]; then
            echo "CURRENT $rel_path"
            return 0
        else
            # Blob differs — STALE
            local behind
            behind=$(git -C "$REPO_ROOT" rev-list --count "${pinned_commit}..HEAD" -- "$rel_path" 2>/dev/null) || behind="?"
            echo "STALE $rel_path ($behind commits behind)"
            stale_count=$((stale_count + 1))
            return 1
        fi
    fi

    # Step 2: Path missing — search for pinned blob in HEAD tree
    local new_path
    new_path=$(git -C "$REPO_ROOT" ls-tree -r HEAD 2>/dev/null | awk -v blob="$pinned_blob" '$3 == blob {print $4; exit}')

    if [[ -n "$new_path" ]]; then
        echo "MOVED $rel_path → $new_path"
        moved_count=$((moved_count + 1))
        return 0
    fi

    # Step 3: Blob not found anywhere — check for rename via git diff
    local rename_target
    rename_target=$(git -C "$REPO_ROOT" diff --find-renames --diff-filter=R --name-status "${pinned_commit}" HEAD -- "$rel_path" 2>/dev/null | awk '{print $3}')

    if [[ -n "$rename_target" ]]; then
        local behind
        behind=$(git -C "$REPO_ROOT" rev-list --count "${pinned_commit}..HEAD" -- "$rename_target" 2>/dev/null) || behind="?"
        echo "MOVED+STALE $rel_path → $rename_target ($behind commits behind)"
        stale_count=$((stale_count + 1))
        return 1
    fi

    # Step 4: No rename found — BROKEN
    echo "BROKEN $rel_path"
    broken_count=$((broken_count + 1))
    return 1
}

# Check all sourcecode-refs in a single DESIGN artifact.
check_design() {
    local design_md="$1"

    if [[ ! -f "$design_md" ]]; then
        echo "design-check: file not found: $design_md" >&2
        return 0
    fi

    local design_id
    design_id=$(grep -m1 '^artifact:' "$design_md" | sed 's/artifact:\s*//' | tr -d '[:space:]')

    local refs
    refs=$(parse_sourcecode_refs "$design_md") || return 0

    if [[ -z "$refs" ]]; then
        return 0
    fi

    local found_drift=0
    while IFS=$'\t' read -r ref_path pinned_blob pinned_commit verified; do
        if ! check_ref "$ref_path" "$pinned_blob" "$pinned_commit" "$design_id"; then
            found_drift=1
        fi
    done <<< "$refs"

    return $found_drift
}

# Repin all sourcecode-refs in a DESIGN artifact to current HEAD values.
repin_design() {
    local design_md="$1"

    if [[ ! -f "$design_md" ]]; then
        echo "design-check: file not found: $design_md" >&2
        return 1
    fi

    local design_id
    design_id=$(grep -m1 '^artifact:' "$design_md" | sed 's/artifact:\s*//' | tr -d '[:space:]')

    local refs
    refs=$(parse_sourcecode_refs "$design_md") || {
        echo "design-check: no sourcecode-refs found in $design_id"
        return 0
    }

    if [[ -z "$refs" ]]; then
        echo "design-check: no sourcecode-refs found in $design_id"
        return 0
    fi

    local current_commit
    current_commit=$(git -C "$REPO_ROOT" rev-parse HEAD)
    local today
    today=$(date +%Y-%m-%d)

    local updated=0
    while IFS=$'\t' read -r ref_path pinned_blob pinned_commit verified; do
        # Resolve current path (may have moved)
        local actual_path="$ref_path"
        local current_blob
        current_blob=$(git -C "$REPO_ROOT" ls-tree HEAD -- "$ref_path" 2>/dev/null | awk '{print $3}')

        if [[ -z "$current_blob" ]]; then
            # Path missing — try to find blob at new location
            local new_path
            new_path=$(git -C "$REPO_ROOT" ls-tree -r HEAD 2>/dev/null | awk -v blob="$pinned_blob" '$3 == blob {print $4; exit}')
            if [[ -n "$new_path" ]]; then
                actual_path="$new_path"
                current_blob="$pinned_blob"
            else
                # Try rename detection
                local rename_target
                rename_target=$(git -C "$REPO_ROOT" diff --find-renames --diff-filter=R --name-status "${pinned_commit}" HEAD -- "$ref_path" 2>/dev/null | awk '{print $3}')
                if [[ -n "$rename_target" ]]; then
                    actual_path="$rename_target"
                    current_blob=$(git -C "$REPO_ROOT" ls-tree HEAD -- "$rename_target" 2>/dev/null | awk '{print $3}')
                else
                    echo "SKIP $ref_path (file not found, cannot repin)"
                    continue
                fi
            fi
        fi

        if [[ -z "$current_blob" ]]; then
            echo "SKIP $ref_path (cannot determine current blob)"
            continue
        fi

        # Update the frontmatter in-place using Python
        uv run python3 -c "
import sys, re

path = '$design_md'
old_path = '$ref_path'
new_path = '$actual_path'
new_blob = '$current_blob'
new_commit = '$current_commit'
today = '$today'

content = open(path).read()
fm_match = re.match(r'^(---\s*\n)(.*?)(\n---)', content, re.DOTALL)
if not fm_match:
    sys.exit(1)

pre, fm, post = fm_match.group(1), fm_match.group(2), fm_match.group(3)
rest = content[fm_match.end():]

# Replace the specific entry's fields
lines = fm.splitlines()
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Look for '  - path: <old_path>'
    m = re.match(r'^(\s+-\s+path:\s+)(.+)$', line)
    if m and m.group(2).strip() == old_path:
        # Found the entry — update path, blob, commit, verified
        new_lines.append(m.group(1) + new_path)
        i += 1
        while i < len(lines):
            sub = lines[i]
            blob_m = re.match(r'^(\s+blob:\s+)(.+)$', sub)
            commit_m = re.match(r'^(\s+commit:\s+)(.+)$', sub)
            verified_m = re.match(r'^(\s+verified:\s+)(.+)$', sub)
            if blob_m:
                new_lines.append(blob_m.group(1) + new_blob)
                i += 1
            elif commit_m:
                new_lines.append(commit_m.group(1) + new_commit)
                i += 1
            elif verified_m:
                new_lines.append(verified_m.group(1) + today)
                i += 1
            else:
                break
        continue
    new_lines.append(line)
    i += 1

new_fm = '\n'.join(new_lines)
new_content = pre + new_fm + post + rest
open(path, 'w').write(new_content)
" 2>/dev/null || {
            echo "FAIL $ref_path (could not update frontmatter)"
            continue
        }

        if [[ "$actual_path" != "$ref_path" ]]; then
            echo "REPINNED $ref_path → $actual_path (blob: ${current_blob:0:8}..., commit: ${current_commit:0:8}...)"
        else
            echo "REPINNED $ref_path (blob: ${current_blob:0:8}..., commit: ${current_commit:0:8}...)"
        fi
        updated=$((updated + 1))
    done <<< "$refs"

    echo "design-check: repinned $updated ref(s) in $design_id"
}

# --- Argument parsing ---

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
fi

if [[ "${1:-}" == "--repin" ]]; then
    MODE="repin"
    shift
    if [[ $# -lt 1 ]]; then
        echo "design-check: --repin requires a DESIGN path argument" >&2
        usage >&2
        exit 2
    fi
fi

mkdir -p "$(dirname "$LOG_FILE")"
> "$LOG_FILE"

# --- Main ---

if [[ "$MODE" == "repin" ]]; then
    repin_design "$1"
    exit $?
fi

# Check mode
any_drift=0

if [[ $# -ge 1 ]]; then
    check_design "$1" || any_drift=1
else
    if [[ ! -d "$DESIGN_DIR" ]]; then
        echo "design-check: no docs/design/Active/ directory found" >&2
        exit 0
    fi
    while IFS= read -r md_file; do
        check_design "$md_file" || any_drift=1
    done < <(find "$DESIGN_DIR" -name '*.md' -type f 2>/dev/null)
fi

# Summary
total_issues=$((stale_count + broken_count))
if [[ $total_issues -gt 0 ]]; then
    echo "design-check: $checked_count ref(s) checked — $stale_count stale, $broken_count broken, $moved_count moved." | tee -a "$LOG_FILE"
    exit 1
elif [[ $checked_count -gt 0 ]]; then
    msg="design-check: $checked_count ref(s) checked, all current"
    if [[ $moved_count -gt 0 ]]; then
        msg="$msg ($moved_count moved, content intact)"
    fi
    echo "$msg."
    exit 0
else
    echo "design-check: no sourcecode-refs found."
    exit 0
fi
