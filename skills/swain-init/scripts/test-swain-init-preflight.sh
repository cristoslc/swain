#!/usr/bin/env bash
# test-swain-init-preflight.sh — test suite for the preflight scanner
#
# Creates temp directories with various project states and verifies
# the preflight script emits correct JSON for each scenario.
#
# Usage: bash test-swain-init-preflight.sh
# Exit: 0 if all tests pass, 1 if any fail

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PREFLIGHT="$SCRIPT_DIR/swain-init-preflight.sh"
PASS=0
FAIL=0
ERRORS=""

# --- Helpers ---

setup_temp() {
  local dir
  dir=$(mktemp -d)
  # Initialize a git repo so git rev-parse works
  git init -q "$dir"
  echo "$dir"
}

cleanup_temp() {
  rm -rf "$1"
}

assert_json_key() {
  local json="$1" key="$2" expected="$3" label="$4"
  local actual
  actual=$(echo "$json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
keys = '$key'.split('.')
v = d
for k in keys:
    if isinstance(v, dict):
        v = v.get(k)
    else:
        v = None
        break
if isinstance(v, bool):
    print(str(v).lower())
elif v is None:
    print('null')
else:
    print(v)
" 2>/dev/null || echo "PARSE_ERROR")

  if [ "$actual" = "$expected" ]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    ERRORS="${ERRORS}FAIL: $label — expected '$expected', got '$actual'\n"
  fi
}

assert_json_valid() {
  local json="$1" label="$2"
  if echo "$json" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    ERRORS="${ERRORS}FAIL: $label — invalid JSON output\n"
  fi
}

# --- Test 1: Fresh project (no marker, no CLAUDE.md, no AGENTS.md) ---

test_fresh_project() {
  local dir
  dir=$(setup_temp)

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "fresh: valid JSON"
  assert_json_key "$output" "marker.exists" "false" "fresh: marker.exists"
  assert_json_key "$output" "marker.action" "onboard" "fresh: marker.action"
  assert_json_key "$output" "migration.state" "fresh" "fresh: migration.state"
  assert_json_key "$output" "migration.claude_md" "missing" "fresh: migration.claude_md"
  assert_json_key "$output" "migration.agents_md" "missing" "fresh: migration.agents_md"
  assert_json_key "$output" "beads.exists" "false" "fresh: beads.exists"
  assert_json_key "$output" "governance.installed" "false" "fresh: governance.installed"
  assert_json_key "$output" "readme.exists" "false" "fresh: readme.exists"
  assert_json_key "$output" "agents_dir.exists" "false" "fresh: agents_dir.exists"

  cleanup_temp "$dir"
}

# --- Test 2: Already-initialized project (same major version) ---

test_initialized_same_version() {
  local dir
  dir=$(setup_temp)

  # Create .swain-init marker
  cat > "$dir/.swain-init" << 'MARKER'
{
  "history": [
    {
      "version": "4.0.0",
      "timestamp": "2026-04-01T00:00:00Z",
      "action": "init"
    }
  ]
}
MARKER

  # Create a fake SKILL.md so version detection works
  mkdir -p "$dir/.claude/skills/swain-init"
  cat > "$dir/.claude/skills/swain-init/SKILL.md" << 'SKILL'
---
name: swain-init
metadata:
  version: 4.1.0
---
SKILL

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "init-same: valid JSON"
  assert_json_key "$output" "marker.exists" "true" "init-same: marker.exists"
  assert_json_key "$output" "marker.last_version" "4.0.0" "init-same: marker.last_version"
  assert_json_key "$output" "marker.current_version" "4.1.0" "init-same: marker.current_version"
  assert_json_key "$output" "marker.action" "delegate" "init-same: marker.action"

  cleanup_temp "$dir"
}

# --- Test 3: Initialized with older major version ---

test_initialized_older_version() {
  local dir
  dir=$(setup_temp)

  cat > "$dir/.swain-init" << 'MARKER'
{
  "history": [
    {
      "version": "3.2.0",
      "timestamp": "2026-01-01T00:00:00Z",
      "action": "init"
    }
  ]
}
MARKER

  mkdir -p "$dir/.claude/skills/swain-init"
  cat > "$dir/.claude/skills/swain-init/SKILL.md" << 'SKILL'
---
name: swain-init
metadata:
  version: 4.0.0
---
SKILL

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "init-upgrade: valid JSON"
  assert_json_key "$output" "marker.exists" "true" "init-upgrade: marker.exists"
  assert_json_key "$output" "marker.action" "upgrade" "init-upgrade: marker.action"

  cleanup_temp "$dir"
}

# --- Test 4: Standard migration (CLAUDE.md has content, no AGENTS.md) ---

test_standard_migration() {
  local dir
  dir=$(setup_temp)

  echo "# My Project Instructions" > "$dir/CLAUDE.md"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "standard: valid JSON"
  assert_json_key "$output" "migration.state" "standard" "standard: migration.state"
  assert_json_key "$output" "migration.claude_md" "has_content" "standard: migration.claude_md"
  assert_json_key "$output" "migration.agents_md" "missing" "standard: migration.agents_md"

  cleanup_temp "$dir"
}

# --- Test 5: Split state (both have content) ---

test_split_state() {
  local dir
  dir=$(setup_temp)

  echo "# CLAUDE instructions" > "$dir/CLAUDE.md"
  echo "# AGENTS instructions" > "$dir/AGENTS.md"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "split: valid JSON"
  assert_json_key "$output" "migration.state" "split" "split: migration.state"
  assert_json_key "$output" "migration.claude_md" "has_content" "split: migration.claude_md"
  assert_json_key "$output" "migration.agents_md" "has_content" "split: migration.agents_md"

  cleanup_temp "$dir"
}

# --- Test 6: Already migrated (CLAUDE.md is just @AGENTS.md) ---

test_already_migrated() {
  local dir
  dir=$(setup_temp)

  echo "@AGENTS.md" > "$dir/CLAUDE.md"
  echo "# AGENTS instructions" > "$dir/AGENTS.md"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "migrated: valid JSON"
  assert_json_key "$output" "migration.state" "migrated" "migrated: migration.state"
  assert_json_key "$output" "migration.claude_md" "include_only" "migrated: migration.claude_md"

  cleanup_temp "$dir"
}

# --- Test 7: Beads directory present ---

test_beads_present() {
  local dir
  dir=$(setup_temp)

  mkdir -p "$dir/.beads/backup"
  echo '{}' > "$dir/.beads/backup/issues.jsonl"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "beads: valid JSON"
  assert_json_key "$output" "beads.exists" "true" "beads: beads.exists"
  assert_json_key "$output" "beads.has_backup" "true" "beads: beads.has_backup"

  cleanup_temp "$dir"
}

# --- Test 8: README and artifacts ---

test_readme_with_artifacts() {
  local dir
  dir=$(setup_temp)

  echo "# My Project" > "$dir/README.md"
  mkdir -p "$dir/docs/vision/Active"
  echo "---" > "$dir/docs/vision/Active/VISION-001-test.md"
  mkdir -p "$dir/docs/design/Active"
  echo "---" > "$dir/docs/design/Active/DESIGN-001-test.md"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "readme: valid JSON"
  assert_json_key "$output" "readme.exists" "true" "readme: readme.exists"
  assert_json_key "$output" "readme.has_artifacts" "true" "readme: readme.has_artifacts"
  assert_json_key "$output" "readme.active_count" "2" "readme: readme.active_count"

  cleanup_temp "$dir"
}

# --- Test 9: Governance present ---

test_governance_present() {
  local dir
  dir=$(setup_temp)

  echo "<!-- swain governance -->" > "$dir/AGENTS.md"

  local output
  output=$(bash "$PREFLIGHT" --repo-root "$dir" 2>/dev/null)

  assert_json_valid "$output" "governance: valid JSON"
  assert_json_key "$output" "governance.installed" "true" "governance: governance.installed"

  cleanup_temp "$dir"
}

# --- Run all tests ---

echo "Running swain-init-preflight tests..."
echo ""

test_fresh_project
test_initialized_same_version
test_initialized_older_version
test_standard_migration
test_split_state
test_already_migrated
test_beads_present
test_readme_with_artifacts
test_governance_present

echo ""
echo "Results: $PASS passed, $FAIL failed"

if [ $FAIL -gt 0 ]; then
  echo ""
  printf "%b" "$ERRORS"
  exit 1
fi

exit 0
