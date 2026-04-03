#!/usr/bin/env bash
# export-snapshot.sh — Export raw source snapshots for swain-search (SPEC-220)

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash skills/swain-search/scripts/export-snapshot.sh \
    --url <source-url> \
    --out-dir <snapshot-dir> \
    [--format txt|pdf] \
    [--browser-export-helper <helper-script>] \
    [--mock-export-url <url>]

Outputs one JSON object to stdout:
  {"source_url":"...","export_mode":"...","export_timestamp":"...","raw_path":"..."}
USAGE
}

SOURCE_URL=""
OUT_DIR=""
EXPORT_FORMAT="txt"
BROWSER_EXPORT_HELPER=""
MOCK_EXPORT_URL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      SOURCE_URL="${2:-}"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="${2:-}"
      shift 2
      ;;
    --format)
      EXPORT_FORMAT="${2:-}"
      shift 2
      ;;
    --browser-export-helper)
      BROWSER_EXPORT_HELPER="${2:-}"
      shift 2
      ;;
    --mock-export-url)
      MOCK_EXPORT_URL="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$SOURCE_URL" || -z "$OUT_DIR" ]]; then
  echo "ERROR: --url and --out-dir are required" >&2
  usage >&2
  exit 1
fi

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
mkdir -p "$OUT_DIR"

slug="$(echo "$SOURCE_URL" | tr '[:upper:]' '[:lower:]' | sed -E 's#https?://##' | sed -E 's#[^a-z0-9]+#-#g' | sed -E 's#(^-|-$)##g' | cut -c1-80)"
[[ -z "$slug" ]] && slug="snapshot"
raw_path="$OUT_DIR/${timestamp//[:]/-}-$slug.$EXPORT_FORMAT"

detected_mode="direct-export"
export_url=""

if [[ -n "$MOCK_EXPORT_URL" ]]; then
  export_url="$MOCK_EXPORT_URL"
  detected_mode="mock-export"
elif [[ "$SOURCE_URL" =~ ^https://docs\.google\.com/document/d/([^/]+)/ ]]; then
  doc_id="${BASH_REMATCH[1]}"
  export_url="https://docs.google.com/document/d/${doc_id}/export?format=${EXPORT_FORMAT}"
  detected_mode="google-doc-export"
elif [[ "$SOURCE_URL" =~ ^https://docs\.google\.com/presentation/d/([^/]+)/ ]]; then
  presentation_id="${BASH_REMATCH[1]}"
  export_url="https://docs.google.com/presentation/d/${presentation_id}/export/${EXPORT_FORMAT}"
  detected_mode="google-slides-export"
elif [[ "$SOURCE_URL" =~ ^https://drive\.google\.com/file/d/([^/]+)/ ]]; then
  file_id="${BASH_REMATCH[1]}"
  export_url="https://drive.google.com/uc?export=download&id=${file_id}"
  detected_mode="google-drive-download"
else
  export_url="$SOURCE_URL"
  detected_mode="direct-export"
fi

download_ok=0
if curl -fLsS --retry 3 --retry-all-errors --connect-timeout 10 \
  --max-time 120 "$export_url" -o "$raw_path"; then
  download_ok=1
fi

if [[ $download_ok -ne 1 ]]; then
  if [[ -n "$BROWSER_EXPORT_HELPER" && -x "$BROWSER_EXPORT_HELPER" ]]; then
    "$BROWSER_EXPORT_HELPER" "$SOURCE_URL" "$raw_path"
    detected_mode="browser-helper-export"
  else
    echo "ERROR: export failed for $SOURCE_URL (mode=$detected_mode) and no helper succeeded" >&2
    exit 1
  fi
fi

if [[ ! -s "$raw_path" ]]; then
  echo "ERROR: exported file is empty: $raw_path" >&2
  exit 1
fi

python3 - "$SOURCE_URL" "$detected_mode" "$timestamp" "$raw_path" <<'PY'
import json
import sys

print(json.dumps({
    "source_url": sys.argv[1],
    "export_mode": sys.argv[2],
    "export_timestamp": sys.argv[3],
    "raw_path": sys.argv[4],
}))
PY

