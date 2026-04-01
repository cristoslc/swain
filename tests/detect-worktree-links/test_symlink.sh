#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(git rev-parse --show-toplevel)/.agents/bin/detect-worktree-links.sh"
PASS=0; FAIL=0
TMPDIR_TEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TEST"' EXIT

ae() { local d="$1" ex="$2"; shift 2; local a; set +e; "$@" >/dev/null 2>&1; a=$?; set -e
  [ "$a" -eq "$ex" ] && { echo "PASS: $d"; PASS=$((PASS+1)); } || { echo "FAIL: $d (got $a want $ex)"; FAIL=$((FAIL+1)); }; }
aoc() { local d="$1" p="$2"; shift 2; local o; set +e; o=$("$@" 2>&1); set -e
  echo "$o"|grep -q "$p" && { echo "PASS: $d"; PASS=$((PASS+1)); } || { echo "FAIL: $d (pattern '$p' not in: $o)"; FAIL=$((FAIL+1)); }; }

# Symlink within repo root — clean
ln -s "$TMPDIR_TEST/real.sh" "$TMPDIR_TEST/ok-link"
touch "$TMPDIR_TEST/real.sh"
ae "in-repo symlink exits 0" 0 "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/ok-link"

# Symlink to outside repo root — SYMLINK_ESCAPE
ln -s /tmp/outside.sh "$TMPDIR_TEST/bad-link"
ae "escaping symlink exits 1" 1 "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/bad-link"
aoc "escaping symlink has SYMLINK_ESCAPE" "SYMLINK_ESCAPE" "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/bad-link"

echo ""; echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
