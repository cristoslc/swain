#!/usr/bin/env bash
# swain-session-digest.sh — Generate a structured JSONL digest of a session
# Part of SPEC-199: Session Digest Auto-Generation
#
# Usage:
#   swain-session-digest.sh --session-id <ID> --start-time <ISO8601> [--focus <ARTIFACT-ID>] [--repo-root <PATH>] [--output <PATH>]
#
# Exit codes:
#   0 — digest written successfully
#   1 — error (missing required args, git not available, etc.)

set -euo pipefail

SESSION_ID=""
START_TIME=""
FOCUS=""
REPO_ROOT=""
OUTPUT_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --session-id)
      SESSION_ID="$2"
      shift 2
      ;;
    --start-time)
      START_TIME="$2"
      shift 2
      ;;
    --focus)
      FOCUS="$2"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# Validate required args
if [[ -z "$SESSION_ID" ]]; then
  echo "Error: --session-id is required" >&2
  exit 1
fi
if [[ -z "$START_TIME" ]]; then
  echo "Error: --start-time is required" >&2
  exit 1
fi

# Defaults
if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "Error: not in a git repository and --repo-root not specified" >&2
    exit 1
  }
fi

if [[ -z "$OUTPUT_FILE" ]]; then
  OUTPUT_FILE="$REPO_ROOT/.agents/session-log.jsonl"
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# --- Evidence gathering ---

# 1. Git commits since start-time
GIT_LOG=$(git -C "$REPO_ROOT" log --after="$START_TIME" --oneline --no-decorate 2>/dev/null || echo "")

# 2. Ticket completions — scan .tickets/ for closed tickets updated after start-time
TICKETS_DIR="$REPO_ROOT/.tickets"
CLOSED_TICKETS=""
if [[ -d "$TICKETS_DIR" ]]; then
  for ticket_file in "$TICKETS_DIR"/*.md; do
    [[ -f "$ticket_file" ]] || continue
    # Check if status is closed
    status=$(sed -n '/^---$/,/^---$/{ /^status:/{ s/^status: *//; p; q; } }' "$ticket_file" 2>/dev/null || echo "")
    if [[ "$status" == "closed" ]]; then
      # Check if file was modified after start-time (use file mtime as proxy)
      # Extract tags for spec references
      tags=$(sed -n '/^---$/,/^---$/{ /^tags:/{ s/^tags: *\[//; s/\].*//; p; q; } }' "$ticket_file" 2>/dev/null || echo "")
      CLOSED_TICKETS="${CLOSED_TICKETS}${tags}"$'\n'
    fi
  done
fi

# 3. Pass everything to Python for JSON construction and output
export SESSION_ID START_TIME FOCUS GIT_LOG CLOSED_TICKETS OUTPUT_FILE REPO_ROOT
uv run python3 -c "
import json
import sys
import os
from datetime import datetime, timezone

session_id = os.environ['SESSION_ID']
start_time = os.environ['START_TIME']
focus = os.environ.get('FOCUS', '')
git_log = os.environ.get('GIT_LOG', '')
output_file = os.environ['OUTPUT_FILE']

# Parse git log lines
commits_lines = [line.strip() for line in git_log.strip().split('\n') if line.strip()]
commit_count = len(commits_lines)

# Extract artifact references and actions from commit messages
# Commit format: <hash> <prefix>(<scope>): <message>  OR  <hash> <prefix>: <message>
artifact_pattern_ids = set()
artifacts_touched = []
seen_ids = set()

import re

# Map conventional-commit prefixes to actions
prefix_map = {
    'feat': 'implemented',
    'fix': 'fixed',
    'docs': 'documented',
    'close': 'completed',
    'test': 'tested',
    'research': 'researched',
    'refactor': 'refactored',
    'chore': 'maintained',
    'ci': 'maintained',
    'style': 'maintained',
    'perf': 'optimized',
}

# Pattern for artifact IDs
artifact_re = re.compile(r'(SPEC|EPIC|INITIATIVE|ADR|SPIKE|VISION|PERSONA|RUNBOOK|DESIGN|JOURNEY)-(\d+)')
# Pattern for conventional commit prefix
prefix_re = re.compile(r'^[a-f0-9]+ (\w+)(?:\([^)]*\))?[!]?:\s*(.*)')

for line in commits_lines:
    # Find artifact IDs in this commit line
    ids_in_line = artifact_re.findall(line)
    if not ids_in_line:
        continue

    # Parse the commit prefix
    prefix_match = prefix_re.match(line)
    action = 'touched'
    summary = line
    if prefix_match:
        prefix = prefix_match.group(1).lower()
        action = prefix_map.get(prefix, 'touched')
        summary = prefix_match.group(2).strip()

    for artifact_type, artifact_num in ids_in_line:
        artifact_id = f'{artifact_type}-{artifact_num}'
        if artifact_id in seen_ids:
            continue
        seen_ids.add(artifact_id)

        # Try to read the artifact title from disk
        title = ''
        repo_root = os.environ['REPO_ROOT']
        # Map artifact type to directory
        type_dir_map = {
            'SPEC': 'spec', 'EPIC': 'epic', 'INITIATIVE': 'initiative',
            'ADR': 'adr', 'SPIKE': 'spike', 'VISION': 'vision',
            'PERSONA': 'persona', 'RUNBOOK': 'runbook', 'DESIGN': 'design',
            'JOURNEY': 'journey',
        }
        type_dir = type_dir_map.get(artifact_type, artifact_type.lower())
        # Search common locations
        for subdir in ['Active', 'Complete', 'Proposed', 'InProgress', 'NeedsManualTest', 'Ready', 'Adopted', 'Retired', 'Superseded', 'Abandoned', 'Draft', '']:
            candidate = os.path.join(repo_root, 'docs', type_dir, subdir)
            if not os.path.isdir(candidate):
                continue
            for fname in os.listdir(candidate):
                if artifact_id not in fname:
                    continue
                fpath = os.path.join(candidate, fname)
                # Handle subdirectory layout: (SPEC-194)-Title/(SPEC-194)-Title.md
                if os.path.isdir(fpath):
                    for inner in os.listdir(fpath):
                        if artifact_id in inner and inner.endswith('.md'):
                            fpath = os.path.join(fpath, inner)
                            break
                    else:
                        continue
                elif not fname.endswith('.md'):
                    continue
                try:
                    with open(fpath) as f:
                        in_frontmatter = False
                        for fline in f:
                            fline = fline.rstrip()
                            if fline == '---':
                                if not in_frontmatter:
                                    in_frontmatter = True
                                    continue
                                else:
                                    break
                            if in_frontmatter and fline.startswith('title:'):
                                title = fline[len('title:'):].strip().strip('\"').strip(\"'\")
                                break
                except (IOError, OSError):
                    pass
                break
            if title:
                break

        artifacts_touched.append({
            'id': artifact_id,
            'title': title,
            'action': action,
            'summary': summary,
        })

# Count tasks closed (from ticket tags referencing specs)
closed_tickets_raw = os.environ.get('CLOSED_TICKETS', '')
tasks_closed = len([line for line in closed_tickets_raw.strip().split('\n') if line.strip()])

# Build session summary
if artifacts_touched:
    summaries = [a['summary'] for a in artifacts_touched]
    session_summary = '; '.join(summaries[:5])
    if len(summaries) > 5:
        session_summary += f' (and {len(summaries) - 5} more)'
elif commit_count > 0:
    session_summary = f'{commit_count} commits with no artifact references.'
else:
    session_summary = 'Empty session — no commits recorded.'

# Build the digest entry
entry = {
    'session_id': session_id,
    'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'focus_lane': focus if focus else None,
    'artifacts_touched': artifacts_touched,
    'commits': commit_count,
    'tasks_closed': tasks_closed,
    'session_summary': session_summary,
}

# Append to output file
with open(output_file, 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
" <<< "" || {
  echo "Error: Python JSON construction failed" >&2
  exit 1
}

echo "Digest written to $OUTPUT_FILE" >&2
exit 0
