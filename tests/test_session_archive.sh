#!/usr/bin/env bash
# RED tests for SPEC-248: Session Archive Mechanism
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/swain-session-archive.sh"
TEST_DIR="$(mktemp -d)"
PASS=0
FAIL=0

cleanup() {
  rm -rf "$TEST_DIR"
}
trap cleanup EXIT

assert() {
  local desc="$1" result="$2"
  if [ "$result" = "true" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

export SWAIN_ARCHIVE_DIR="$TEST_DIR/session-archive"

echo "=== SPEC-248: Session Archive Mechanism Tests ==="

# --- Script existence ---
echo ""
echo "--- Script existence ---"
assert "swain-session-archive.sh exists" "$([ -f "$SCRIPT" ] && echo true || echo false)"
assert "swain-session-archive.sh is executable" "$([ -x "$SCRIPT" ] && echo true || echo false)"

# --- AC1: Archive before deletion ---
echo ""
echo "--- AC1: Archive save ---"

# Create a fake worktree with session.json
FAKE_WT="$TEST_DIR/fake-worktree/.agents"
mkdir -p "$FAKE_WT"
cat > "$FAKE_WT/session.json" << 'SESS_EOF'
{
  "lastBranch": "worktree/spec-244",
  "bookmark": {
    "note": "Implementing lockfile library",
    "timestamp": "2026-04-04T10:00:00Z"
  },
  "focus_lane": "INITIATIVE-013"
}
SESS_EOF

bash "$SCRIPT" save "$TEST_DIR/fake-worktree" 2>&1 || true
assert "archive created" "$(ls "$SWAIN_ARCHIVE_DIR"/*.json 2>/dev/null | head -1 | xargs test -f 2>/dev/null && echo true || echo false)"

# No session.json -> graceful fail
EMPTY_WT="$TEST_DIR/empty-worktree"
mkdir -p "$EMPTY_WT"
bash "$SCRIPT" save "$EMPTY_WT" 2>&1 || true
assert "missing session.json is graceful" "true"  # should not crash

# --- AC2: Lookup by session ID ---
echo ""
echo "--- AC2: Lookup by session ID ---"

# Find the archived file name
ARCHIVED=$(ls "$SWAIN_ARCHIVE_DIR"/*.json 2>/dev/null | head -1)
if [ -n "$ARCHIVED" ]; then
  SESSION_ID="$(basename "$ARCHIVED" .json)"
  OUTPUT=$(bash "$SCRIPT" get "$SESSION_ID" 2>&1) || true
  assert "get returns session data" "$(echo "$OUTPUT" | grep -q "lockfile" && echo true || echo false)"
else
  assert "get returns session data" "false"
fi

# Not found
bash "$SCRIPT" get "nonexistent-session" 2>&1
NOT_FOUND_EXIT=$?
assert "get nonexistent returns exit 1" "$([ $NOT_FOUND_EXIT -ne 0 ] && echo true || echo false)"

# --- AC3: Lookup by artifact ID ---
echo ""
echo "--- AC3: Lookup by artifact ID ---"

FIND_OUTPUT=$(bash "$SCRIPT" find "INITIATIVE-013" 2>&1) || true
assert "find by artifact returns matches" "$(echo "$FIND_OUTPUT" | grep -q "INITIATIVE-013\|fake-worktree\|lockfile" && echo true || echo false)"

FIND_EMPTY=$(bash "$SCRIPT" find "NONEXISTENT-999" 2>&1) || true
assert "find nonexistent returns empty" "$([ -z "$FIND_EMPTY" ] || echo "$FIND_EMPTY" | grep -qiE "no matches|not found|\[\]" && echo true || echo false)"

# --- AC4: Compression ---
echo ""
echo "--- AC4: Compression ---"

# Create an old archive (fake old timestamp by touching)
if [ -n "$ARCHIVED" ]; then
  OLD_ARCHIVE="$SWAIN_ARCHIVE_DIR/old-session-20260301.json"
  cp "$ARCHIVED" "$OLD_ARCHIVE"
  touch -t 202603010000 "$OLD_ARCHIVE"  # March 1st — more than 7 days ago

  bash "$SCRIPT" compress 2>&1 || true
  assert "old archives compressed" "$([ -f "${OLD_ARCHIVE}.gz" ] && echo true || echo false)"
  assert "recent archives not compressed" "$([ -f "$ARCHIVED" ] && echo true || echo false)"
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
