---
id: s22c-qd0h
status: closed
deps: [s22c-6oeg]
links: []
created: 2026-03-31T03:21:00Z
type: task
priority: 1
assignee: Cristos L-C
parent: s22c-33it
tags: [spec:SPEC-194]
---
# Task 3: Implement readability-check.sh

**Files:**
- Create: `skills/swain-design/scripts/readability-check.sh`
- Create: `.agents/bin/readability-check.sh` (symlink)

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
# readability-check.sh — Score markdown artifacts for Flesch-Kincaid readability (SPEC-194)
#
# Strips non-prose content (frontmatter, code blocks, tables, URLs, images,
# HTML tags, inline code) then scores remaining prose via textstat.
#
# Usage: readability-check.sh [--threshold N] [--json] <file> [file ...]
# Output: PASS/FAIL/SKIP per file with grade level
# Exit codes:
#   0  All files PASS or SKIP
#   1  One or more files FAIL
#   3  Usage error

set -euo pipefail

THRESHOLD=9
JSON_MODE=false
FILES=()

usage() {
  cat <<'USAGE'
Usage: readability-check.sh [--threshold N] [--json] <file> [file ...]

Scores markdown files for Flesch-Kincaid grade level on prose content only.
Non-prose content (frontmatter, code blocks, tables, etc.) is stripped first.

Options:
  --threshold N   Grade-level ceiling (default: 9)
  --json          Output JSON array instead of text lines

Output (text mode):
  PASS  <file>  grade=<N>
  FAIL  <file>  grade=<N>
  SKIP  <file>  words=<N>

Exit codes:
  0  All files PASS or SKIP
  1  One or more files FAIL
  3  Usage error
USAGE
}

# --- Arg parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --threshold)
      THRESHOLD="$2"
      shift 2
      ;;
    --json)
      JSON_MODE=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Error: unknown flag $1" >&2
      usage >&2
      exit 3
      ;;
    *)
      FILES+=("$1")
      shift
      ;;
  esac
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "Error: no files provided" >&2
  usage >&2
  exit 3
fi

# --- Score files via Python ---
HAS_FAILURE=false

# Build file list as newline-separated for the Python script
FILE_LIST=""
for f in "${FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "Error: file not found: $f" >&2
    exit 3
  fi
  FILE_LIST+="$f"$'\n'
done

RESULTS=$(echo "$FILE_LIST" | uv run --with textstat python3 -c "
import sys, re, json
import textstat

def strip_markdown(text):
    # Strip YAML frontmatter
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    # Strip fenced code blocks (backtick and tilde)
    text = re.sub(r'^\`\`\`.*?\`\`\`', '', text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r'^~~~.*?~~~', '', text, flags=re.DOTALL | re.MULTILINE)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Strip markdown tables (lines starting with |)
    text = re.sub(r'^\|.*\|$', '', text, flags=re.MULTILINE)
    # Strip images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Strip URLs (standalone and in links)
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    # Strip inline code
    text = re.sub(r'\`[^\`]+\`', '', text)
    # Strip markdown headings markers (keep the text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Strip bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Strip list markers
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    return text.strip()

files = [f.strip() for f in sys.stdin.read().strip().split('\n') if f.strip()]
threshold = float(sys.argv[1])
json_mode = sys.argv[2] == 'true'

results = []
for filepath in files:
    with open(filepath, 'r') as f:
        raw = f.read()
    prose = strip_markdown(raw)
    words = len(prose.split())
    if words < 50:
        results.append({'file': filepath, 'result': 'SKIP', 'grade': None, 'words': words})
    else:
        grade = round(textstat.flesch_kincaid_grade(prose), 1)
        result = 'PASS' if grade <= threshold else 'FAIL'
        results.append({'file': filepath, 'result': result, 'grade': grade, 'words': words})

if json_m...

