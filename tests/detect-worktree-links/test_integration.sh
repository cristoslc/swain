#!/usr/bin/env bash
# Integration tests for the link-safety block logic (SPEC-218)
# Tests the detect+resolve+amend flow in isolation (not inside skill invocation)
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
anoc() { local d="$1" p="$2"; shift 2; local o; set +e; o=$("$@" 2>&1); set -e
  echo "$o"|grep -q "$p" && { echo "FAIL: $d (unexpected '$p' in: $o)"; FAIL=$((FAIL+1)); } || { echo "PASS: $d"; PASS=$((PASS+1)); }; }

# ── link_safety_run: simulates the completion hook logic ─────────────────────
# Usage: link_safety_run <repo_root> <file...>
# Returns: 0 (clean/resolved), 1 (unresolvable), prints [link-safety] messages
link_safety_run() {
    local repo_root="$1"; shift
    local files=("$@")
    local output=""

    set +eo pipefail
    FINDINGS=$("$DETECT" --repo-root "$repo_root" "${files[@]}" 2>/dev/null)
    DETECT_EXIT=$?
    set -eo pipefail

    if [ "$DETECT_EXIT" -eq 0 ]; then
        return 0  # clean — no output
    fi

    echo "[link-safety] Found suspicious links. Resolving automatically..."
    local resolve_out resolve_exit
    set +e
    resolve_out=$("$RESOLVE" --repo-root "$repo_root" "${files[@]}" 2>&1)
    resolve_exit=$?
    set -e

    echo "$resolve_out"

    if [ "$resolve_exit" -ne 0 ]; then
        echo "[link-safety] UNRESOLVABLE links remain — merge aborted. Fix before pushing."
        return 1
    fi
    return 0
}

# ── T1: clean files — no link-safety output ──────────────────────────────────
mkdir -p "$TMPDIR_TEST/docs"
cat > "$TMPDIR_TEST/docs/clean.md" <<'EOF'
# Clean doc
See [sibling](./other.md) for details.
EOF
touch "$TMPDIR_TEST/docs/other.md"

OUT=$(link_safety_run "$TMPDIR_TEST" "$TMPDIR_TEST/docs/clean.md" 2>&1 || true)
[ -z "$OUT" ] && { echo "PASS: clean files — no output"; PASS=$((PASS+1)); } \
  || { echo "FAIL: clean files — unexpected output: $OUT"; FAIL=$((FAIL+1)); }

# ── T2: auto-resolvable link — resolved, FIXED in output ─────────────────────
NESTED="$TMPDIR_TEST/a/b/c"
mkdir -p "$NESTED"
touch "$TMPDIR_TEST/target.md"
cat > "$NESTED/doc.md" <<'EOF'
See [thing](../../../../../../../../target.md) for details.
EOF

OUT=$(link_safety_run "$TMPDIR_TEST" "$NESTED/doc.md" 2>&1 || true)
echo "$OUT" | grep -q "\[link-safety\]" && { echo "PASS: auto-resolvable — link-safety output present"; PASS=$((PASS+1)); } \
  || { echo "FAIL: auto-resolvable — no link-safety output"; FAIL=$((FAIL+1)); }
echo "$OUT" | grep -q "FIXED" && { echo "PASS: auto-resolvable — FIXED in output"; PASS=$((PASS+1)); } \
  || { echo "FAIL: auto-resolvable — no FIXED in output (got: $OUT)"; FAIL=$((FAIL+1)); }

# File now passes detector
ae "auto-resolvable: file clean after resolve" 0 \
  "$DETECT" --repo-root "$TMPDIR_TEST" "$NESTED/doc.md"

# ── T3: UNRESOLVABLE — hook exits 1, message shown ───────────────────────────
cat > "$NESTED/bad.md" <<'EOF'
See [missing](../../../../../../../../totally-nonexistent-file-xyzzy.md) for details.
EOF

set +e
OUT=$(link_safety_run "$TMPDIR_TEST" "$NESTED/bad.md" 2>&1)
HOOK_EXIT=$?
set -e

[ "$HOOK_EXIT" -eq 1 ] && { echo "PASS: UNRESOLVABLE — hook exits 1"; PASS=$((PASS+1)); } \
  || { echo "FAIL: UNRESOLVABLE — expected exit 1, got $HOOK_EXIT"; FAIL=$((FAIL+1)); }
echo "$OUT" | grep -q "UNRESOLVABLE\|merge aborted" && { echo "PASS: UNRESOLVABLE — abort message shown"; PASS=$((PASS+1)); } \
  || { echo "FAIL: UNRESOLVABLE — no abort message (got: $OUT)"; FAIL=$((FAIL+1)); }

# ── T4: only scans changed files (integration contract) ──────────────────────
# This tests that if we pass a specific file list, only those are scanned
ae "scoped scan: unrelated clean file exits 0" 0 \
  "$DETECT" --repo-root "$TMPDIR_TEST" "$TMPDIR_TEST/docs/clean.md"

echo ""; echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
