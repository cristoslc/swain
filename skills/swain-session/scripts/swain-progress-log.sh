#!/usr/bin/env bash
# swain-progress-log.sh — Append progress entries and synthesize progress sections
#
# Modes:
#   --artifact-id <ID> --entry <text>       Append a dated entry to progress.md
#   --artifact-id <ID> --synthesize         Regenerate ## Progress section from progress.md
#   --digest <path-to-jsonl-entry>          Process a session digest line
#
# SPEC-200: Progress Log and Synthesis

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

# ─── Argument parsing ───

ARTIFACT_ID=""
ENTRY=""
SYNTHESIZE=false
DIGEST_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --artifact-id) ARTIFACT_ID="$2"; shift 2 ;;
    --entry) ENTRY="$2"; shift 2 ;;
    --synthesize) SYNTHESIZE=true; shift ;;
    --digest) DIGEST_PATH="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# ─── Helpers ───

resolve_artifact_dir() {
  local id="$1"
  # Find the directory containing this artifact under docs/
  local dir
  dir=$(find "$REPO_ROOT/docs" -type d -name "*${id}*" 2>/dev/null | head -1)
  if [[ -z "$dir" ]]; then
    echo "ERROR: Could not find artifact directory for $id" >&2
    return 1
  fi
  echo "$dir"
}

resolve_artifact_file() {
  local dir="$1"
  local id="$2"
  # Find the .md file matching the artifact ID in the directory
  local file
  file=$(find "$dir" -maxdepth 1 -name "*${id}*.md" ! -name "progress.md" 2>/dev/null | head -1)
  if [[ -z "$file" ]]; then
    echo "ERROR: Could not find artifact file for $id in $dir" >&2
    return 1
  fi
  echo "$file"
}

append_entry() {
  local artifact_dir="$1"
  local entry_text="$2"
  local progress_file="$artifact_dir/progress.md"
  local today
  today=$(date +%Y-%m-%d)

  if [[ ! -f "$progress_file" ]]; then
    echo "# Progress Log" > "$progress_file"
    echo "" >> "$progress_file"
  fi

  {
    echo "## $today"
    echo ""
    echo "$entry_text"
    echo ""
  } >> "$progress_file"

  echo "Appended entry to $progress_file"
}

synthesize_progress() {
  local artifact_dir="$1"
  local artifact_id="$2"
  local progress_file="$artifact_dir/progress.md"
  local artifact_file

  artifact_file=$(resolve_artifact_file "$artifact_dir" "$artifact_id")

  if [[ ! -f "$progress_file" ]]; then
    echo "No progress.md found in $artifact_dir — nothing to synthesize" >&2
    return 0
  fi

  # Use Python for reliable text manipulation
  uv run python3 -c "
import sys, re

progress_path = sys.argv[1]
artifact_path = sys.argv[2]

# Read progress.md and extract recent entries (last 2-3)
with open(progress_path) as f:
    content = f.read()

# Split into dated sections
sections = re.split(r'^## (\d{4}-\d{2}-\d{2})', content, flags=re.MULTILINE)
# sections[0] is header, then pairs of (date, body)
entries = []
for i in range(1, len(sections) - 1, 2):
    date = sections[i]
    body = sections[i + 1].strip()
    entries.append((date, body))

# Take last 2-3 entries for synthesis
recent = entries[-3:] if len(entries) > 3 else entries
synthesis_lines = []
for date, body in recent:
    # Take first line of each entry as the synthesis line
    first_line = body.split('\n')[0].strip()
    if first_line:
        synthesis_lines.append(f'**{date}:** {first_line}')

synthesis = '\n\n'.join(synthesis_lines) if synthesis_lines else '_No progress entries yet._'

# Read artifact file
with open(artifact_path) as f:
    artifact_content = f.read()

# Find ## Progress section and replace its content
# Section runs from '## Progress' to the next '## ' heading or end of file
progress_pattern = re.compile(
    r'(## Progress\n).*?(?=\n## [^\n]|\Z)',
    re.DOTALL
)

progress_section = f'## Progress\n\n{synthesis}\n'

if progress_pattern.search(artifact_content):
    new_content = progress_pattern.sub(progress_section, artifact_content)
else:
    # Insert after ## Desired Outcomes or ## Goal / Objective
    insert_patterns = [
        r'(## Desired Outcomes\n.*?)(?=\n## )',
        r'(## Goal / Objective\n.*?)(?=\n## )',
    ]
    inserted = False
    for pat in insert_patterns:
        match = re.search(pat, artifact_content, re.DOTALL)
        if match:
            insert_pos = match.end()
            new_content = artifact_content[:insert_pos] + '\n\n' + progress_section + '\n' + artifact_content[insert_pos:]
            inserted = True
            break
    if not inserted:
        # Fallback: append before ## Lifecycle or at end
        lifecycle_match = re.search(r'\n## Lifecycle', artifact_content)
        if lifecycle_match:
            pos = lifecycle_match.start()
            new_content = artifact_content[:pos] + '\n' + progress_section + '\n' + artifact_content[pos:]
        else:
            new_content = artifact_content + '\n\n' + progress_section

with open(artifact_path, 'w') as f:
    f.write(new_content)

print(f'Synthesized progress into {artifact_path}')
" "$progress_file" "$artifact_file"
}

# ─── Digest mode ───

process_digest() {
  local digest_path="$1"

  if [[ ! -f "$digest_path" ]]; then
    echo "ERROR: Digest file not found: $digest_path" >&2
    exit 1
  fi

  uv run python3 -c "
import json, sys, subprocess, os

digest_path = sys.argv[1]
script = sys.argv[2]

with open(digest_path) as f:
    entry = json.loads(f.read().strip())

artifacts = entry.get('artifacts_touched', [])
session_summary = entry.get('session_summary', 'Session work recorded.')

for artifact in artifacts:
    artifact_id = artifact.get('id', '') if isinstance(artifact, dict) else str(artifact)
    summary = artifact.get('summary', session_summary) if isinstance(artifact, dict) else session_summary
    if not artifact_id:
        continue

    # Only update EPICs and Initiatives (container artifacts that track progress)
    if not any(artifact_id.startswith(p) for p in ['EPIC-', 'INITIATIVE-']):
        continue

    result = subprocess.run(
        ['bash', script, '--artifact-id', artifact_id, '--entry', summary],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f'Warning: failed to append entry for {artifact_id}: {result.stderr}', file=sys.stderr)
    else:
        print(result.stdout, end='')

    # Synthesize
    result = subprocess.run(
        ['bash', script, '--artifact-id', artifact_id, '--synthesize'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f'Warning: failed to synthesize for {artifact_id}: {result.stderr}', file=sys.stderr)
    else:
        print(result.stdout, end='')
" "$digest_path" "${BASH_SOURCE[0]}"
}

# ─── Main dispatch ───

if [[ -n "$DIGEST_PATH" ]]; then
  process_digest "$DIGEST_PATH"
elif [[ -n "$ARTIFACT_ID" ]]; then
  ARTIFACT_DIR=$(resolve_artifact_dir "$ARTIFACT_ID")

  if [[ -n "$ENTRY" ]]; then
    append_entry "$ARTIFACT_DIR" "$ENTRY"
  fi

  if [[ "$SYNTHESIZE" == true ]]; then
    synthesize_progress "$ARTIFACT_DIR" "$ARTIFACT_ID"
  fi

  if [[ -z "$ENTRY" && "$SYNTHESIZE" == false ]]; then
    echo "ERROR: --artifact-id requires --entry and/or --synthesize" >&2
    exit 1
  fi
else
  echo "ERROR: Must provide --artifact-id or --digest" >&2
  exit 1
fi
