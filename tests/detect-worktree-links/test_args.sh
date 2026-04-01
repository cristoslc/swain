#!/usr/bin/env bash
# Tests for detect-worktree-links.sh argument parsing
# RED phase — script does not exist yet, all tests must fail

set -euo pipefail

SCRIPT="$(git rev-parse --show-toplevel)/.agents/bin/detect-worktree-links.sh"
PASS=0
FAIL=0

assert_exit() {
    local desc="$1" expected="$2"
    shift 2
    local actual
    actual=$("$@" 2>/dev/null; echo $?) || actual=$?
    # Capture exit code properly
    set +e
    "$@" > /dev/null 2>&1
    actual=$?
    set -e
    if [ "$actual" -eq "$expected" ]; then
        echo "PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "FAIL: $desc (expected exit $expected, got $actual)"
        FAIL=$((FAIL + 1))
    fi
}

assert_output_contains() {
    local desc="$1" pattern="$2"
    shift 2
    local out
    set +e
    out=$("$@" 2>&1)
    set -e
    if echo "$out" | grep -q "$pattern"; then
        echo "PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "FAIL: $desc (expected output matching '$pattern', got: $out)"
        FAIL=$((FAIL + 1))
    fi
}

# T1a: no args → exit 2
assert_exit "no args exits 2" 2 "$SCRIPT"

# T1b: no args → prints usage to stderr
assert_output_contains "no args prints usage" "Usage" "$SCRIPT"

# T1c: --repo-root flag accepted (with a real dir, no files to scan → exit 0)
TMPDIR_TEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TEST"' EXIT
assert_exit "--repo-root flag accepted, empty dir exits 0" 0 \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST"

# T1d: --worktree-root flag accepted
assert_exit "--worktree-root flag accepted, empty dir exits 0" 0 \
    "$SCRIPT" --worktree-root "$TMPDIR_TEST" "$TMPDIR_TEST"

# T1e: both flags together
assert_exit "both flags accepted, empty dir exits 0" 0 \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" --worktree-root "$TMPDIR_TEST" "$TMPDIR_TEST"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
