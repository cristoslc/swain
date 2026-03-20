---
id: swa-vuxf
status: open
deps: [swa-vrtp]
links: []
created: 2026-03-20T00:42:36Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 8: Create train-check.sh

**Files:**
- Create: `.claude/skills/swain-design/scripts/train-check.sh`

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
# train-check.sh — Staleness detection for TRAIN artifacts.
#
# Reads enriched linked-artifacts entries with rel: [documents] and commit pins.
# Compares pinned commit hash against the documented artifact's current HEAD commit.
#
# Usage:
#   train-check.sh [path-to-train-dir]   Check a single TRAIN
#   train-check.sh                        Check all TRAINs under docs/train/
#
# Exit codes:
#   0 — all pins current
#   1 — drift found (at least one stale dependency)
#   2 — git unavailable or not in a git repo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "train-check: git not available or not in a git repo" >&2
    exit 2
}

DOCS_DIR="$REPO_ROOT/docs"
TRAIN_DIR="$DOCS_DIR/train"
LOG_FILE="${REPO_ROOT}/.agents/train-check.log"

stale_count=0
checked_count=0

# Find the TRAIN's primary markdown file in a TRAIN directory
find_train_md() {
    local train_dir="$1"
    find "$train_dir" -maxdepth 1 -name '*TRAIN-*.md' | head -1
}

# Resolve an artifact ID to its file path
resolve_artifact_path() {
    local artifact_id="$1"
    local prefix type_dir
    prefix=$(echo "$artifact_id" | sed 's/-[0-9]*//')
    case "$prefix" in
        SPEC)       type_dir="spec" ;;
        EPIC)       type_dir="epic" ;;
        SPIKE)      type_dir="research" ;;
        ADR)        type_dir="adr" ;;
        VISION)     type_dir="vision" ;;
        INITIATIVE) type_dir="initiative" ;;
        JOURNEY)    type_dir="journey" ;;
        PERSONA)    type_dir="persona" ;;
        RUNBOOK)    type_dir="runbook" ;;
        DESIGN)     type_dir="design" ;;
        TRAIN)      type_dir="train" ;;
        *)          return 1 ;;
    esac
    # Search across all phase subdirectories
    find "$DOCS_DIR/$type_dir" -name "*${artifact_id}*" -name "*.md" 2>/dev/null | head -1
}

# Check a single TRAIN directory for stale dependencies
check_train() {
    local train_dir="$1"
    local train_md
    train_md=$(find_train_md "$train_dir")
    if [[ -z "$train_md" ]]; then
        return 0
    fi

    local train_id
    train_id=$(grep -m1 '^artifact:' "$train_md" | sed 's/artifact:\s*//' | tr -d '[:space:]')

    # Extract enriched linked-artifacts entries using Python for reliable YAML-ish parsing
    local stale_deps
    stale_deps=$(uv run python3 -c "
import sys, re

content = open('$train_md').read()
# Extract frontmatter
fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
if not fm_match:
    sys.exit(0)

fm = fm_match.group(1)
lines = fm.splitlines()
in_linked = False
current_entry = None
entries = []

for line in lines:
    if re.match(r'^linked-artifacts:', line):
        in_linked = True
        continue
    if in_linked:
        list_match = re.match(r'^\s+-\s+(.+)$', line)
        if list_match:
            if current_entry and 'artifact' in current_entry:
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
            val = indent_kv.group(2).strip()
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip() for v in val[1:-1].split(',') if v.strip()]
            current_entry[indent_kv.group(1)] = val
            continue
        if re.match(r'^[a-z]', line):
            in_linked = False
            if current_entry and 'artifact' in current_entry:
                entries.append(current_entry)
            current_entry = None

if current_entry and 'artifact' in current_entry...

