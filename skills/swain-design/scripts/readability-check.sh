#!/usr/bin/env bash
# readability-check.sh — Flesch-Kincaid readability enforcement (SPEC-194)
# Scores markdown files after stripping non-prose content.
# Exit 0 = all PASS/SKIP, exit 1 = any FAIL, exit 3 = usage error.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: readability-check.sh [OPTIONS] FILE [FILE...]

Score markdown files using Flesch-Kincaid grade level.
Non-prose content (frontmatter, code blocks, tables, etc.) is stripped first.
Files with fewer than 50 prose words are skipped.

Options:
  --threshold N   Maximum FK grade level (default: 9)
  --json          Output results as JSON array
  -h, --help      Show this help message

Exit codes:
  0   All files PASS or SKIP
  1   One or more files FAIL
  3   Usage error (no files, bad arguments)
USAGE
}

THRESHOLD=9
JSON_MODE=false
FILES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --threshold)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --threshold requires a value" >&2
        exit 3
      fi
      THRESHOLD="$2"
      shift 2
      ;;
    --json)
      JSON_MODE=true
      shift
      ;;
    -*)
      echo "Error: unknown option $1" >&2
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
  echo "Error: no files specified" >&2
  usage >&2
  exit 3
fi

# Build newline-separated file list
FILE_LIST=""
for f in "${FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "Error: file not found: $f" >&2
    exit 3
  fi
  FILE_LIST="${FILE_LIST}${f}"$'\n'
done

# Pass file list to Python via environment variable (stdin is used by heredoc)
export READABILITY_FILES="$FILE_LIST"

PYTHON_EXIT=0
RESULTS=$(uv run --with textstat python3 - "$THRESHOLD" "$JSON_MODE" << 'PYTHON_EOF'
import sys, re, json, os
import textstat

threshold = int(sys.argv[1])
json_mode = sys.argv[2] == "true"

file_list = [line.strip() for line in os.environ["READABILITY_FILES"].splitlines() if line.strip()]

results = []

for filepath in file_list:
    with open(filepath, "r") as f:
        content = f.read()

    # Strip YAML frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, count=1, flags=re.DOTALL)

    # Strip fenced code blocks (``` and ~~~)
    content = re.sub(r'```[^\n]*\n.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'~~~[^\n]*\n.*?~~~', '', content, flags=re.DOTALL)

    # Strip markdown tables (lines matching |...|)
    content = re.sub(r'^\|.*\|$', '', content, flags=re.MULTILINE)

    # Strip images ![...](...)
    content = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', content)

    # Strip markdown links but keep link text [text](url) -> text
    content = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', content)

    # Strip standalone URLs
    content = re.sub(r'https?://\S+', '', content)

    # Strip inline code
    content = re.sub(r'`[^`]+`', '', content)

    # Strip HTML tags
    content = re.sub(r'<[^>]+>', '', content)

    # Strip heading markers (keep text)
    content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)

    # Strip bold/italic markers (keep text)
    content = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', content)
    content = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', content)

    # Strip list markers (keep text)
    content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^[\s]*\d+\.\s+', '', content, flags=re.MULTILINE)

    # Count words
    words = content.split()
    word_count = len(words)

    basename = os.path.basename(filepath)

    if word_count < 50:
        results.append({
            "file": filepath,
            "result": "SKIP",
            "grade": None,
            "words": word_count,
            "basename": basename,
        })
    else:
        grade = round(textstat.flesch_kincaid_grade(content), 1)
        if grade <= threshold:
            result = "PASS"
        else:
            result = "FAIL"
        results.append({
            "file": filepath,
            "result": result,
            "grade": grade,
            "words": word_count,
            "basename": basename,
        })

if json_mode:
    output = [
        {"file": r["file"], "result": r["result"], "grade": r["grade"], "words": r["words"]}
        for r in results
    ]
    print(json.dumps(output))
else:
    for r in results:
        if r["result"] == "SKIP":
            print(f"SKIP  {r['file']}  words={r['words']}")
        else:
            print(f"{r['result']}  {r['file']}  grade={r['grade']}")

# Exit code
has_fail = any(r["result"] == "FAIL" for r in results)
sys.exit(1 if has_fail else 0)
PYTHON_EOF
) || PYTHON_EXIT=$?

# Print the results
if [[ -n "$RESULTS" ]]; then
  echo "$RESULTS"
fi

exit "$PYTHON_EXIT"
