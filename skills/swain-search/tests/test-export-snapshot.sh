#!/usr/bin/env bash
# test-export-snapshot.sh — Acceptance tests for snapshot export evidence pipeline (SPEC-220)
#
# Usage: bash skills/swain-search/tests/test-export-snapshot.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EXPORT_SCRIPT="$ROOT_DIR/scripts/export-snapshot.sh"
LOG_SCRIPT="$ROOT_DIR/scripts/log-snapshot-metadata.sh"
VERIFY_SCRIPT="$ROOT_DIR/scripts/verify-snapshot-evidence.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1 — $2"; FAIL=$((FAIL + 1)); }

echo "=== snapshot export pipeline Tests (SPEC-220) ==="
echo "Export script: $EXPORT_SCRIPT"
echo "Log script: $LOG_SCRIPT"
echo "Verify script: $VERIFY_SCRIPT"
echo ""

TMPDIR_TEST="$(mktemp -d)"
cleanup() { rm -rf "$TMPDIR_TEST"; }
trap cleanup EXIT

RAW_INPUT="$TMPDIR_TEST/raw-input.txt"
cat > "$RAW_INPUT" <<'TXT'
This is a simulated Google Doc export body.
TXT

SNAPSHOT_DIR="$TMPDIR_TEST/snapshots"
METADATA_FILE="$TMPDIR_TEST/metadata.jsonl"
NORMALIZED_PATH="$TMPDIR_TEST/normalized.md"
cat > "$NORMALIZED_PATH" <<'MD'
---
title: Simulated normalized source
---

# Simulated normalized source

This is normalized content.
MD

SOURCE_URL="https://docs.google.com/document/d/abc123/edit"

echo "--- AC1: Google Doc URL exports a raw snapshot ---"
export_output="$(bash "$EXPORT_SCRIPT" \
  --url "$SOURCE_URL" \
  --out-dir "$SNAPSHOT_DIR" \
  --mock-export-url "file://$RAW_INPUT" 2>&1)"
status=$?
if [[ $status -eq 0 ]]; then
  pass "AC1: export script exits 0"
else
  fail "AC1: export script exit code" "expected 0, got $status output=$export_output"
fi

raw_path="$(echo "$export_output" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["raw_path"])' 2>/dev/null)"
if [[ -n "$raw_path" && -f "$raw_path" ]]; then
  pass "AC1: raw snapshot file created"
else
  fail "AC1: raw snapshot path" "missing file path in output=$export_output"
fi

echo ""
echo "--- AC2: Metadata log writes required fields ---"
log_output="$(bash "$LOG_SCRIPT" \
  --source-url "$SOURCE_URL" \
  --export-mode "google-doc-export" \
  --raw-path "$raw_path" \
  --normalized-path "$NORMALIZED_PATH" \
  --normalization-skill "writing-skills" \
  --metadata-file "$METADATA_FILE" 2>&1)"
status=$?
if [[ $status -eq 0 ]]; then
  pass "AC2: metadata logger exits 0"
else
  fail "AC2: metadata logger exit code" "expected 0, got $status output=$log_output"
fi

metadata_check="$(python3 - "$METADATA_FILE" "$SOURCE_URL" "$NORMALIZED_PATH" <<'PY'
import json,sys
path,source,normalized = sys.argv[1], sys.argv[2], sys.argv[3]
ok = False
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        item = json.loads(line)
        if item.get("source_url") == source and item.get("normalized_path") == normalized:
            required = [
                "source_url",
                "export_mode",
                "export_timestamp",
                "normalization_skill",
                "normalized_path",
                "digest",
            ]
            ok = all(item.get(k) for k in required)
            break
print("ok" if ok else "bad")
PY
)"
if [[ "$metadata_check" == "ok" ]]; then
  pass "AC2: metadata contains required fields"
else
  fail "AC2: metadata fields" "required fields missing in $METADATA_FILE"
fi

echo ""
echo "--- AC3: Verification gate passes when metadata exists ---"
verify_output="$(bash "$VERIFY_SCRIPT" \
  --source-url "$SOURCE_URL" \
  --metadata-file "$METADATA_FILE" 2>&1)"
status=$?
if [[ $status -eq 0 ]]; then
  pass "AC3: verification exits 0 for verified source"
else
  fail "AC3: verification exit code" "expected 0, got $status output=$verify_output"
fi

echo ""
echo "--- AC4: Verification gate warns for unverified sources ---"
unverified_output="$(bash "$VERIFY_SCRIPT" \
  --source-url "https://docs.google.com/document/d/missing/edit" \
  --metadata-file "$METADATA_FILE" 2>&1)"
status=$?
if [[ $status -eq 2 ]]; then
  pass "AC4: verification exits 2 for unverified source"
else
  fail "AC4: unverified exit code" "expected 2, got $status output=$unverified_output"
fi

if echo "$unverified_output" | grep -q "^WARN: unverified source"; then
  pass "AC4: warning emitted for unverified source"
else
  fail "AC4: warning output" "expected WARN line, got output=$unverified_output"
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
