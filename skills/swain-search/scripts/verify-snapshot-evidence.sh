#!/usr/bin/env bash
# verify-snapshot-evidence.sh — Validation gate for swain-search source evidence (SPEC-220)

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash skills/swain-search/scripts/verify-snapshot-evidence.sh \
    --source-url <source-url> \
    [--metadata-file <path>]

Exit codes:
  0: verified (metadata entry exists)
  2: unverified (no metadata entry)
  1: usage or runtime error
USAGE
}

SOURCE_URL=""
METADATA_FILE=".agents/search-snapshots/metadata.jsonl"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-url)
      SOURCE_URL="${2:-}"
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

if [[ -z "$SOURCE_URL" ]]; then
  echo "ERROR: --source-url is required" >&2
  usage >&2
  exit 1
fi

if [[ ! -f "$METADATA_FILE" ]]; then
  echo "WARN: unverified source (no metadata ledger): $SOURCE_URL"
  exit 2
fi

if python3 - "$METADATA_FILE" "$SOURCE_URL" <<'PY'
import json
import sys

path = sys.argv[1]
source_url = sys.argv[2]

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("source_url") == source_url:
            print("verified")
            raise SystemExit(0)

raise SystemExit(2)
PY
then
  echo "verified: source snapshot evidence exists for $SOURCE_URL"
  exit 0
else
  status=$?
  if [[ $status -eq 2 ]]; then
    echo "WARN: unverified source (missing snapshot metadata): $SOURCE_URL"
    exit 2
  fi
  echo "ERROR: verification failed unexpectedly for $SOURCE_URL" >&2
  exit 1
fi

