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
anoc() { local d="$1" p="$2"; shift 2; local o; set +e; o=$("$@" 2>&1); set -e
  echo "$o"|grep -q "$p" && { echo "FAIL: $d (unexpected '$p' in: $o)"; FAIL=$((FAIL+1)); } || { echo "PASS: $d"; PASS=$((PASS+1)); }; }

# Script with /tmp/worktree- path — flagged
cat > "$TMPDIR_TEST/bad1.sh" <<'EOF'
#!/bin/bash
source /tmp/worktree-abc/scripts/helper.sh
EOF
ae "tmp/worktree- path exits 1" 1 "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/bad1.sh"
aoc "tmp/worktree- has HARDCODED_WORKTREE_PATH" "HARDCODED_WORKTREE_PATH" "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/bad1.sh"

# Script with .claude/worktrees/ path — flagged
cat > "$TMPDIR_TEST/bad2.sh" <<'EOF'
#!/bin/bash
BASE=/Users/dev/.claude/worktrees/my-branch/scripts
EOF
ae ".claude/worktrees/ exits 1" 1 "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/bad2.sh"
aoc ".claude/worktrees/ has HARDCODED_WORKTREE_PATH" "HARDCODED_WORKTREE_PATH" "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/bad2.sh"

# Clean script — not flagged
cat > "$TMPDIR_TEST/clean.sh" <<'EOF'
#!/bin/bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
source "$REPO_ROOT/scripts/helper.sh"
EOF
ae "clean script exits 0" 0 "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/clean.sh"
anoc "clean script not flagged" "HARDCODED_WORKTREE_PATH" "$SCRIPT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/clean.sh"

echo ""; echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
