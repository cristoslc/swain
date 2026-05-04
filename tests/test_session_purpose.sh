#!/usr/bin/env bash
# RED tests for SPEC-297: greeting must extract SWAIN_PURPOSE → bookmark + JSON.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GREETING="$REPO_ROOT/skills/swain-session/scripts/swain-session-greeting.sh"
BOOKMARK="$REPO_ROOT/skills/swain-session/scripts/swain-bookmark.sh"
PREFLIGHT="$REPO_ROOT/skills/swain-session/scripts/swain-session-preflight.sh"

PASS=0
FAIL=0

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

echo "=== SPEC-297: Session Purpose Text Drop Tests ==="

# Guard: required scripts exist
assert "greeting script exists" "$([ -f "$GREETING" ] && echo true || echo false)"
assert "bookmark script exists" "$([ -f "$BOOKMARK" ] && echo true || echo false)"
assert "preflight script exists" "$([ -f "$PREFLIGHT" ] && echo true || echo false)"

# --- Fixture: isolated tmpdir repo with no existing bookmark ---
make_repo() {
  local dir
  dir=$(mktemp -d)
  (
    cd "$dir"
    git init -q
    git config user.email test@test
    git config user.name test
    git commit --allow-empty -q -m init
    mkdir -p .agents
    echo '{}' > .agents/session.json
  )
  echo "$dir"
}

PURPOSE_TEXT="fix the login bug"

# T1: SWAIN_PURPOSE is captured into session.json bookmark by greeting
TMP1=$(make_repo)
(
  cd "$TMP1"
  SWAIN_PURPOSE="$PURPOSE_TEXT" bash "$GREETING" --json >/dev/null 2>&1
)
BOOKMARK_NOTE=$(jq -r '.bookmark.note // empty' "$TMP1/.agents/session.json" 2>/dev/null)
assert "SWAIN_PURPOSE writes session.json bookmark.note" \
  "$([ "$BOOKMARK_NOTE" = "$PURPOSE_TEXT" ] && echo true || echo false)"
rm -rf "$TMP1"

# T2: Greeting JSON output exposes purpose field
TMP2=$(make_repo)
GREETING_JSON=$(cd "$TMP2" && SWAIN_PURPOSE="$PURPOSE_TEXT" bash "$GREETING" --json 2>/dev/null)
GREETING_PURPOSE=$(echo "$GREETING_JSON" | jq -r '.purpose // empty' 2>/dev/null)
assert "greeting JSON includes purpose field" \
  "$([ "$GREETING_PURPOSE" = "$PURPOSE_TEXT" ] && echo true || echo false)"
rm -rf "$TMP2"

# T3: Existing bookmark is NOT clobbered by SWAIN_PURPOSE
TMP3=$(make_repo)
(
  cd "$TMP3"
  jq -n '{bookmark: {note: "existing note", timestamp: "2026-01-01T00:00:00Z"}}' > .agents/session.json
  SWAIN_PURPOSE="$PURPOSE_TEXT" bash "$GREETING" --json >/dev/null 2>&1
)
EXISTING_NOTE=$(jq -r '.bookmark.note // empty' "$TMP3/.agents/session.json" 2>/dev/null)
assert "existing bookmark is preserved (SWAIN_PURPOSE does not clobber)" \
  "$([ "$EXISTING_NOTE" = "existing note" ] && echo true || echo false)"
rm -rf "$TMP3"

# T4: Human-readable output includes purpose line when set
TMP4=$(make_repo)
HUMAN_OUT=$(cd "$TMP4" && SWAIN_PURPOSE="$PURPOSE_TEXT" bash "$GREETING" 2>/dev/null)
assert "human-readable output includes Purpose line" \
  "$(echo "$HUMAN_OUT" | grep -q "Purpose: $PURPOSE_TEXT" && echo true || echo false)"
rm -rf "$TMP4"

# T5: No SWAIN_PURPOSE → no purpose field, no bookmark mutation
TMP5=$(make_repo)
NO_PURPOSE_JSON=$(cd "$TMP5" && bash "$GREETING" --json 2>/dev/null)
NO_PURPOSE_FIELD=$(echo "$NO_PURPOSE_JSON" | jq -r '.purpose // "null"' 2>/dev/null)
NO_PURPOSE_NOTE=$(jq -r '.bookmark.note // empty' "$TMP5/.agents/session.json" 2>/dev/null)
assert "purpose field null when SWAIN_PURPOSE unset" \
  "$([ "$NO_PURPOSE_FIELD" = "null" ] && echo true || echo false)"
assert "bookmark unset when SWAIN_PURPOSE unset" \
  "$([ -z "$NO_PURPOSE_NOTE" ] && echo true || echo false)"
rm -rf "$TMP5"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
