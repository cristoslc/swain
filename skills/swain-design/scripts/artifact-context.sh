#!/usr/bin/env bash
# artifact-context.sh — context-rich display for artifact IDs (SPEC-201)
# Usage: artifact-context.sh [--format line|json] [-h|--help] <ID> [<ID>...]

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

FORMAT="line"
IDS=()

# --- Arg parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      cat <<'USAGE'
Usage: artifact-context.sh [--format line|json] [-h|--help] <ID> [<ID>...]

Resolve artifact IDs to context-rich display lines.

Options:
  --format line   Markdown-formatted context line (default)
  --format json   JSON array output
  -h, --help      Show this help

Exit codes:
  0  All artifacts resolved
  1  One or more artifacts not found (partial results still printed)
  3  Usage error (no arguments)
USAGE
      exit 0
      ;;
    --format)
      shift
      FORMAT="${1:-line}"
      shift
      ;;
    *)
      IDS+=("$1")
      shift
      ;;
  esac
done

if [[ ${#IDS[@]} -eq 0 ]]; then
  echo "artifact-context: no artifact IDs provided" >&2
  exit 3
fi

# --- Type mapping from ID prefix ---
prefix_to_dir() {
  local id="$1"
  local prefix="${id%%-*}"
  case "$prefix" in
    SPEC)       echo "spec" ;;
    EPIC)       echo "epic" ;;
    INITIATIVE) echo "initiative" ;;
    VISION)     echo "vision" ;;
    SPIKE)      echo "spike" ;;
    ADR)        echo "adr" ;;
    PERSONA)    echo "persona" ;;
    RUNBOOK)    echo "runbook" ;;
    DESIGN)     echo "design" ;;
    JOURNEY)    echo "journey" ;;
    TRAIN)      echo "train" ;;
    *)          echo "" ;;
  esac
}

# --- Resolve artifact file path ---
resolve_artifact() {
  local id="$1"
  local type_dir
  type_dir="$(prefix_to_dir "$id")"
  if [[ -z "$type_dir" ]]; then
    return 1
  fi
  local search_dir="$REPO_ROOT/docs/$type_dir"
  if [[ ! -d "$search_dir" ]]; then
    return 1
  fi
  local found
  found=$(find "$search_dir" -name "(${id})*" -type f -name "*.md" 2>/dev/null | head -1)
  if [[ -z "$found" ]]; then
    return 1
  fi
  echo "$found"
}

# --- Extract data from artifact using Python ---
extract_artifact_data() {
  local filepath="$1"
  local id="$2"
  local prefix="${id%%-*}"
  local child_prefix=""

  # Determine child type for parent counting
  case "$prefix" in
    EPIC)       child_prefix="parent-epic" ;;
    INITIATIVE) child_prefix="parent-initiative" ;;
  esac

  python3 - "$filepath" "$id" "$child_prefix" "$REPO_ROOT" <<'PYEOF'
import sys, re, os, subprocess, json

filepath = sys.argv[1]
artifact_id = sys.argv[2]
child_fm_key = sys.argv[3]  # e.g. "parent-epic" or ""
repo_root = sys.argv[4]

with open(filepath, 'r') as f:
    content = f.read()

# Parse frontmatter
fm = {}
fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
if fm_match:
    for line in fm_match.group(1).splitlines():
        m = re.match(r'^(\S[^:]*?):\s*(.*)', line)
        if m:
            key, val = m.group(1).strip(), m.group(2).strip().strip('"').strip("'")
            fm[key] = val

title = fm.get('title', 'Unknown')
status = fm.get('status', 'Unknown')

# Scope sentence: first sentence after ## Problem Statement, ## Goal, or ## Goal / Objective
scope = ""
scope_pattern = re.compile(
    r'^##\s+(Problem Statement|Goal|Goal\s*/\s*Objective)\s*\n+(.+?)(?:\n\n|\n##|\Z)',
    re.MULTILINE | re.DOTALL
)
scope_m = scope_pattern.search(content)
if scope_m:
    paragraph = scope_m.group(2).strip()
    # First sentence (up to first period followed by space or end)
    sent_m = re.match(r'(.+?\.)\s', paragraph + ' ')
    if sent_m:
        scope = sent_m.group(1)
    else:
        scope = paragraph.split('\n')[0]

# Progress clause
progress = ""

# Priority a: ## Progress section
prog_pattern = re.compile(r'^##\s+Progress\s*\n+(.+?)(?:\n##|\Z)', re.MULTILINE | re.DOTALL)
prog_m = prog_pattern.search(content)
if prog_m:
    paragraph = prog_m.group(1).strip()
    sent_m = re.match(r'(.+?\.)\s', paragraph + ' ')
    if sent_m:
        progress = sent_m.group(1)
    else:
        progress = paragraph.split('\n')[0]

# Priority b: child artifact counts
if not progress and child_fm_key:
    docs_dir = os.path.join(repo_root, 'docs')
    # Try specgraph first
    try:
        result = subprocess.run(
            ['python3', os.path.join(repo_root, '.agents/bin/chart_cli.py'), 'children', artifact_id],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
            total = len(lines)
            # Count complete children by checking their status
            complete = 0
            for child_line in lines:
                # child_line might be an ID or a path
                child_id_m = re.match(r'((?:SPEC|EPIC|INITIATIVE|SPIKE|ADR)-\d+)', child_line)
                if child_id_m:
                    child_id = child_id_m.group(1)
                    child_prefix_dir = child_id.split('-')[0].lower()
                    child_dir = os.path.join(docs_dir, child_prefix_dir)
                    if os.path.isdir(child_dir):
                        import glob
                        matches = glob.glob(os.path.join(child_dir, '**', f'({child_id})*'), recursive=True)
                        for cm in matches:
                            if cm.endswith('.md'):
                                with open(cm) as cf:
                                    cc = cf.read()
                                cfm = re.match(r'^---\n(.*?)\n---', cc, re.DOTALL)
                                if cfm:
                                    for cl in cfm.group(1).splitlines():
                                        sm = re.match(r'^status:\s*(.*)', cl)
                                        if sm and sm.group(1).strip().strip('"') == 'Complete':
                                            complete += 1
                                break
            if total > 0:
                child_type = 'child specs' if child_fm_key == 'parent-epic' else 'child epics'
                progress = f"{complete} of {total} {child_type} complete"
    except Exception:
        pass

    # Fallback: grep for parent reference
    if not progress:
        try:
            result = subprocess.run(
                ['grep', '-rl', f'{child_fm_key}: {artifact_id}', docs_dir],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                children = [l for l in result.stdout.strip().splitlines() if l.endswith('.md')]
                total = len(children)
                complete = 0
                for child_path in children:
                    with open(child_path) as cf:
                        cc = cf.read()
                    cfm = re.match(r'^---\n(.*?)\n---', cc, re.DOTALL)
                    if cfm:
                        for cl in cfm.group(1).splitlines():
                            sm = re.match(r'^status:\s*(.*)', cl)
                            if sm and sm.group(1).strip().strip('"') == 'Complete':
                                complete += 1
                if total > 0:
                    child_type = 'child specs' if child_fm_key == 'parent-epic' else 'child epics'
                    progress = f"{complete} of {total} {child_type} complete"
        except Exception:
            pass

# Priority c: fallback to status
if not progress:
    progress = status

# Output as JSON for the bash wrapper to consume
print(json.dumps({
    "id": artifact_id,
    "title": title,
    "scope": scope,
    "progress": progress,
    "status": status
}))
PYEOF
}

# --- Main loop ---
had_error=0
results=()

for id in "${IDS[@]}"; do
  filepath=$(resolve_artifact "$id" 2>/dev/null) || true
  if [[ -z "$filepath" ]]; then
    echo "artifact-context: $id not found" >&2
    had_error=1
    continue
  fi
  json_line=$(extract_artifact_data "$filepath" "$id")
  results+=("$json_line")
done

# --- Output ---
if [[ "$FORMAT" == "json" ]]; then
  # Combine individual JSON objects into an array
  if [[ ${#results[@]} -eq 0 ]]; then
    echo "[]"
  else
    printf '%s\n' "${results[@]}" | python3 -c "
import sys, json
items = [json.loads(line) for line in sys.stdin if line.strip()]
print(json.dumps(items, indent=2))
"
  fi
else
  # Line format: **Title** \`ID\` — scope. progress.
  for json_line in "${results[@]}"; do
    echo "$json_line" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
parts = []
parts.append('**' + d['title'] + '**')
parts.append('\`' + d['id'] + '\`')
detail = ''
if d.get('scope'):
    detail += d['scope']
if d.get('progress'):
    if detail and not detail.endswith('.'):
        detail += '.'
    if detail:
        detail += ' '
    detail += d['progress']
    if not detail.endswith('.'):
        detail += '.'
if detail:
    print(parts[0] + ' ' + parts[1] + ' — ' + detail)
else:
    print(parts[0] + ' ' + parts[1])
"
  done
fi

exit "$had_error"
