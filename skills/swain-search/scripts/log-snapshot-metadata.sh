#!/usr/bin/env bash
# log-snapshot-metadata.sh — Append swain-search snapshot metadata records (SPEC-220)

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash skills/swain-search/scripts/log-snapshot-metadata.sh \
    --source-url <source-url> \
    --export-mode <mode> \
    --raw-path <raw-file> \
    --normalized-path <normalized-file> \
    --normalization-skill <writing-skills|skill-creator|...> \
    [--metadata-file <path>]
USAGE
}

SOURCE_URL=""
EXPORT_MODE=""
RAW_PATH=""
NORMALIZED_PATH=""
NORMALIZATION_SKILL=""
METADATA_FILE=".agents/search-snapshots/metadata.jsonl"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-url)
      SOURCE_URL="${2:-}"
      shift 2
      ;;
    --export-mode)
      EXPORT_MODE="${2:-}"
      shift 2
      ;;
    --raw-path)
      RAW_PATH="${2:-}"
      shift 2
      ;;
    --normalized-path)
      NORMALIZED_PATH="${2:-}"
      shift 2
      ;;
    --normalization-skill)
      NORMALIZATION_SKILL="${2:-}"
      shift 2
      ;;
    --metadata-file)
      METADATA_FILE="${2:-}"
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

if [[ -z "$SOURCE_URL" || -z "$EXPORT_MODE" || -z "$RAW_PATH" || -z "$NORMALIZED_PATH" || -z "$NORMALIZATION_SKILL" ]]; then
  echo "ERROR: missing required arguments" >&2
  usage >&2
  exit 1
fi

if [[ ! -f "$RAW_PATH" ]]; then
  echo "ERROR: raw file not found: $RAW_PATH" >&2
  exit 1
fi
if [[ ! -f "$NORMALIZED_PATH" ]]; then
  echo "ERROR: normalized file not found: $NORMALIZED_PATH" >&2
  exit 1
fi

digest="$(shasum -a 256 "$NORMALIZED_PATH" | awk '{print $1}')"
timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$(dirname "$METADATA_FILE")"

python3 - "$SOURCE_URL" "$EXPORT_MODE" "$timestamp" "$RAW_PATH" "$NORMALIZATION_SKILL" "$NORMALIZED_PATH" "$digest" >> "$METADATA_FILE" <<'PY'
import json
import sys

entry = {
    "source_url": sys.argv[1],
    "export_mode": sys.argv[2],
    "export_timestamp": sys.argv[3],
    "raw_path": sys.argv[4],
    "normalization_skill": sys.argv[5],
    "normalized_path": sys.argv[6],
    "digest": sys.argv[7],
}
print(json.dumps(entry, separators=(",", ":")))
PY

echo "logged:$METADATA_FILE"

