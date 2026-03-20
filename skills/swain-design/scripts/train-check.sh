#!/usr/bin/env bash
# train-check.sh — Staleness detection for TRAIN artifacts.
#
# Reads artifact-refs entries with rel: [documents] and commit pins.
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

find_train_md() {
    local train_dir="$1"
    find "$train_dir" -maxdepth 1 -name '*TRAIN-*.md' | head -1
}

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
    find "$DOCS_DIR/$type_dir" -name "*${artifact_id}*" -name "*.md" 2>/dev/null | head -1
}

check_train() {
    local train_dir="$1"
    local train_md
    train_md=$(find_train_md "$train_dir")
    if [[ -z "$train_md" ]]; then
        return 0
    fi

    local train_id
    train_id=$(grep -m1 '^artifact:' "$train_md" | sed 's/artifact:\s*//' | tr -d '[:space:]')

    local stale_deps
    stale_deps=$(uv run python3 -c "
import sys, re

content = open('$train_md').read()
fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
if not fm_match:
    sys.exit(0)

fm = fm_match.group(1)
lines = fm.splitlines()
in_artifact_refs = False
current_entry = None
entries = []

for line in lines:
    if re.match(r'^artifact-refs:', line):
        in_artifact_refs = True
        continue
    if in_artifact_refs:
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
            in_artifact_refs = False
            if current_entry and 'artifact' in current_entry:
                entries.append(current_entry)
            current_entry = None

if current_entry and 'artifact' in current_entry:
    entries.append(current_entry)

for e in entries:
    rel = e.get('rel', [])
    if isinstance(rel, str):
        rel = [rel]
    if 'documents' not in rel:
        continue
    commit = e.get('commit')
    if not commit:
        continue
    artifact_id = e['artifact']
    print(f'{artifact_id}\t{commit}')
" 2>/dev/null) || return 0

    if [[ -z "$stale_deps" ]]; then
        return 0
    fi

    local found_stale=0
    while IFS=$'\t' read -r dep_id pinned_commit; do
        local dep_path
        dep_path=$(resolve_artifact_path "$dep_id")
        if [[ -z "$dep_path" ]]; then
            echo "WARN: $train_id → $dep_id (artifact not found)" | tee -a "$LOG_FILE"
            continue
        fi

        local current_commit
        current_commit=$(git -C "$REPO_ROOT" log -1 --format=%H -- "$dep_path" 2>/dev/null) || continue

        checked_count=$((checked_count + 1))

        if [[ "$pinned_commit" != "$current_commit" ]]; then
            local behind
            behind=$(git -C "$REPO_ROOT" rev-list --count "${pinned_commit}..${current_commit}" 2>/dev/null) || behind="?"
            echo "STALE: $train_id → $dep_id (pinned: $pinned_commit, current: $current_commit, $behind commits behind)" | tee -a "$LOG_FILE"
            found_stale=1
            stale_count=$((stale_count + 1))
        fi
    done <<< "$stale_deps"

    return $found_stale
}

mkdir -p "$(dirname "$LOG_FILE")"
> "$LOG_FILE"

if [[ $# -ge 1 ]]; then
    check_train "$1" || true
else
    if [[ ! -d "$TRAIN_DIR" ]]; then
        echo "train-check: no docs/train/ directory found" >&2
        exit 0
    fi
    while read -r dir; do
        check_train "$dir" || true
    done < <(find "$TRAIN_DIR" -mindepth 2 -maxdepth 3 -type d -name '*TRAIN-*' 2>/dev/null)
fi

if [[ $stale_count -gt 0 ]]; then
    echo "train-check: found $stale_count stale dependency(ies) across $checked_count checked." | tee -a "$LOG_FILE"
    exit 1
elif [[ $checked_count -gt 0 ]]; then
    echo "train-check: $checked_count dependency(ies) checked, all current."
    exit 0
else
    echo "train-check: no pinned dependencies found."
    exit 0
fi
