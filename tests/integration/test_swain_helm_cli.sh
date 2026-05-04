#!/usr/bin/env bash
# Tests for SPEC-319: bin/swain-helm CLI
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/bin/swain-helm"
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

TEST_CONFIG_DIR=$(mktemp -d)
TEST_PROJECTS_DIR="$TEST_CONFIG_DIR/projects"
TEST_BRIDGES_DIR="$TEST_CONFIG_DIR/run/bridges"
mkdir -p "$TEST_PROJECTS_DIR" "$TEST_BRIDGES_DIR"

cleanup() {
  rm -rf "$TEST_CONFIG_DIR"
}
trap cleanup EXIT

echo "=== SPEC-319: bin/swain-helm CLI Tests ==="

echo ""
echo "--- Structural: script exists and is executable ---"
assert "script file exists" "$([ -f "$SCRIPT" ] && echo true || echo false)"
assert "script is executable" "$([ -x "$SCRIPT" ] && echo true || echo false)"
assert "script has valid bash syntax" "$(bash -n "$SCRIPT" 2>/dev/null && echo true || echo false)"

echo ""
echo "--- AC: --help flag works ---"
HELP_OUTPUT=$(bash "$SCRIPT" --help 2>&1)
assert "--help outputs usage text" "$(echo "$HELP_OUTPUT" | grep -q 'swain-helm' && echo true || echo false)"
assert "--help mentions host up" "$(echo "$HELP_OUTPUT" | grep -q 'host up' && echo true || echo false)"
assert "--help mentions project add" "$(echo "$HELP_OUTPUT" | grep -q 'project add' && echo true || echo false)"

echo ""
echo "--- AC1/AC2: host up (syntax and structure) ---"
assert "script contains host up handler" "$(grep -q 'cmd_host_up' "$SCRIPT" && echo true || echo false)"
assert "script supports --foreground flag" "$(grep -q '\-\-foreground' "$SCRIPT" && echo true || echo false)"
assert "script starts watchdog daemon" "$(grep -q 'swain_helm.watchdog' "$SCRIPT" && echo true || echo false)"
assert "script uses nohup for daemon mode" "$(grep -q 'nohup' "$SCRIPT" && echo true || echo false)"
assert "script writes watchdog PID file" "$(grep -q 'watchdog.pid' "$SCRIPT" && echo true || echo false)"

echo ""
echo "--- AC3/AC4: host down ---"
assert "script contains host down handler" "$(grep -q 'cmd_host_down' "$SCRIPT" && echo true || echo false)"
assert "script supports --project flag in down" "$(grep -q '\-\-project' "$SCRIPT" && echo true || echo false)"
assert "script sends SIGTERM on down" "$(grep -q 'kill.*SIGTERM\|kill ' "$SCRIPT" && echo true || echo false)"
assert "script cleans up PID files" "$(grep -q 'rm -f.*pid' "$SCRIPT" && echo true || echo false)"

echo ""
echo "--- AC5: host status ---"
assert "script contains host status handler" "$(grep -q 'cmd_host_status' "$SCRIPT" && echo true || echo false)"
assert "status checks watchdog PID" "$(grep -q 'watchdog.*PID\|watchdog_pid' "$SCRIPT" && echo true || echo false)"
assert "status checks opencode health" "$(grep -q 'global/health' "$SCRIPT" && echo true || echo false)"

echo ""
echo "--- AC6: host provision ---"
assert "script contains host provision handler" "$(grep -q 'cmd_host_provision' "$SCRIPT" && echo true || echo false)"
assert "provision calls swain_helm.provision" "$(grep -q 'swain_helm.provision' "$SCRIPT" && echo true || echo false)"

echo ""
echo "--- AC7: project add ./ succeeds with .git/ ---"
GIT_DIR=$(mktemp -d)
mkdir -p "$GIT_DIR/.git"
OUTPUT_ADD=$(cd "$GIT_DIR" && bash "$SCRIPT" project add . 2>&1)
assert "project add ./ succeeds when .git/ exists" "$(echo "$OUTPUT_ADD" | grep -q 'added' && echo true || echo false)"
assert "config file created" "$([ -f "$HOME/.config/swain-helm/projects/$(basename "$GIT_DIR").json" ] && echo true || echo false)"
rm -rf "$GIT_DIR"
rm -f "$HOME/.config/swain-helm/projects/"*.json

echo ""
echo "--- AC8: project add rejects without .git/ ---"
NO_GIT_DIR=$(mktemp -d)
OUTPUT_NO_GIT=$(bash "$SCRIPT" project add "$NO_GIT_DIR" 2>&1) && no_git_rc=0 || no_git_rc=$?
assert "project add rejects when no .git/" "$(echo "$OUTPUT_NO_GIT" | grep -qi 'not a git repository\|no .git' && echo true || echo false)"
assert "project add exits non-zero without .git/" "$([ "$no_git_rc" -ne 0 ] && echo true || echo false)"
rm -rf "$NO_GIT_DIR"

echo ""
echo "--- AC9: project add by absolute path ---"
ABS_DIR=$(mktemp -d)
mkdir -p "$ABS_DIR/.git"
ABS_OUTPUT=$(bash "$SCRIPT" project add "$ABS_DIR" 2>&1)
ABS_NAME=$(basename "$ABS_DIR")
assert "project add by absolute path succeeds" "$(echo "$ABS_OUTPUT" | grep -q 'added' && echo true || echo false)"
assert "config JSON has correct path" "$(grep -q "\"path\": \"${ABS_DIR}\"" "$HOME/.config/swain-helm/projects/${ABS_NAME}.json" 2>/dev/null && echo true || echo false)"
assert "config JSON has correct name" "$(grep -q "\"name\": \"${ABS_NAME}\"" "$HOME/.config/swain-helm/projects/${ABS_NAME}.json" 2>/dev/null && echo true || echo false)"
assert "config JSON has runtime opencode" "$(grep -q '"runtime": "opencode"' "$HOME/.config/swain-helm/projects/${ABS_NAME}.json" 2>/dev/null && echo true || echo false)"
rm -rf "$ABS_DIR"

echo ""
echo "--- AC10: project remove ---"
REMOVE_DIR=$(mktemp -d)
mkdir -p "$REMOVE_DIR/.git"
bash "$SCRIPT" project add "$REMOVE_DIR" >/dev/null 2>&1
REMOVE_NAME=$(basename "$REMOVE_DIR")
REMOVE_OUTPUT=$(bash "$SCRIPT" project remove --project "$REMOVE_NAME" 2>&1)
assert "project remove succeeds" "$(echo "$REMOVE_OUTPUT" | grep -q 'removed' && echo true || echo false)"
assert "config file deleted after remove" "$([ ! -f "$HOME/.config/swain-helm/projects/${REMOVE_NAME}.json" ] && echo true || echo false)"
rm -rf "$REMOVE_DIR"

echo ""
echo "--- AC11: project list ---"
LIST_DIR=$(mktemp -d)
mkdir -p "$LIST_DIR/.git"
bash "$SCRIPT" project add "$LIST_DIR" >/dev/null 2>&1
LIST_NAME=$(basename "$LIST_DIR")
LIST_OUTPUT=$(bash "$SCRIPT" project list 2>&1)
assert "project list shows registered project" "$(echo "$LIST_OUTPUT" | grep -q "$LIST_NAME" && echo true || echo false)"
assert "project list shows status" "$(echo "$LIST_OUTPUT" | grep -qi 'stopped\|running' && echo true || echo false)"
rm -rf "$LIST_DIR"
rm -f "$HOME/.config/swain-helm/projects/"*.json

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1