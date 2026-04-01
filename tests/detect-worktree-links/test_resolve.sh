#!/usr/bin/env bash
# Tests for resolve-worktree-links.sh
set -euo pipefail

DETECT="$(git rev-parse --show-toplevel)/.agents/bin/detect-worktree-links.sh"
RESOLVE="$(git rev-parse --show-toplevel)/.agents/bin/resolve-worktree-links.sh"
PASS=0; FAIL=0
TMPDIR_TEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TEST"' EXIT

ae() { local d="$1" ex="$2"; shift 2; local a; set +e; "$@" >/dev/null 2>&1; a=$?; set -e
  [ "$a" -eq "$ex" ] && { echo "PASS: $d"; PASS=$((PASS+1)); } || { echo "FAIL: $d (got $a want $ex)"; FAIL=$((FAIL+1)); }; }
aoc() { local d="$1" p="$2"; shift 2; local o; set +e; o=$("$@" 2>&1); set -e
  echo "$o"|grep -q "$p" && { echo "PASS: $d"; PASS=$((PASS+1)); } || { echo "FAIL: $d (pattern '$p' not in: $o)"; FAIL=$((FAIL+1)); }; }

# ── Setup: nested dir so ../ hops make sense ──────────────────────────────────
NESTED="$TMPDIR_TEST/a/b/c"
mkdir -p "$NESTED"
# A sibling file at the repo root level so links can validly target it
touch "$TMPDIR_TEST/target.md"

# T1a: standalone mode — file with escaping link gets resolved
# Link: ../../../../../../../../target.md from a/b/c/ → should resolve to ../../../target.md
cat > "$NESTED/doc.md" <<EOF
See [thing](../../../../../../../../target.md) for details.
EOF

ae "standalone: escaping link detected before resolve" 1 \
  "$DETECT" --repo-root "$TMPDIR_TEST" "$NESTED/doc.md"

ae "standalone: resolve exits 0 after fix" 0 \
  "$RESOLVE" --repo-root "$TMPDIR_TEST" "$NESTED/doc.md"

ae "standalone: detector exits 0 after resolve" 0 \
  "$DETECT" --repo-root "$TMPDIR_TEST" "$NESTED/doc.md"

# T1b: piped mode — pipe detector output to resolver
cat > "$NESTED/doc2.md" <<EOF
See [thing](../../../../../../../../target.md) for details.
EOF

# Pipe: detect finds it, resolve fixes it
# Disable pipefail: DETECT exits 1 (found issues) but we care only about RESOLVE's exit
set +eo pipefail
"$DETECT" --repo-root "$TMPDIR_TEST" "$NESTED/doc2.md" | \
  "$RESOLVE" --repo-root "$TMPDIR_TEST" --from-stdin
PIPE_EXIT="${PIPESTATUS[1]}"
set -eo pipefail
[ "$PIPE_EXIT" -eq 0 ] && { echo "PASS: piped mode exits 0 after fix"; PASS=$((PASS+1)); } \
  || { echo "FAIL: piped mode exits $PIPE_EXIT"; FAIL=$((FAIL+1)); }

ae "piped: detector clean after pipe resolve" 0 \
  "$DETECT" --repo-root "$TMPDIR_TEST" "$NESTED/doc2.md"

# T1c: idempotent — second resolve on already-fixed file is no-op
ae "idempotent: second resolve exits 0" 0 \
  "$RESOLVE" --repo-root "$TMPDIR_TEST" "$NESTED/doc.md"
ae "idempotent: detector still clean" 0 \
  "$DETECT" --repo-root "$TMPDIR_TEST" "$NESTED/doc.md"

# T1d: UNRESOLVABLE — escaping link where target filename doesn't exist in repo at all
cat > "$NESTED/unresolvable.md" <<'EOF'
See [bad](../../../../../../../../totally-nonexistent-xyzzy-42.md) for details.
EOF
ae "unresolvable: exits 1" 1 \
  "$RESOLVE" --repo-root "$TMPDIR_TEST" "$NESTED/unresolvable.md"
aoc "unresolvable: UNRESOLVABLE in output" "UNRESOLVABLE" \
  "$RESOLVE" --repo-root "$TMPDIR_TEST" "$NESTED/unresolvable.md"

echo ""; echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
