#!/usr/bin/env bash
# Tests for detect-worktree-links.sh markdown link scanner
set -euo pipefail

SCRIPT="$(git rev-parse --show-toplevel)/.agents/bin/detect-worktree-links.sh"
REPO_ROOT="$(git rev-parse --show-toplevel)"
PASS=0
FAIL=0
TMPDIR_TEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TEST"' EXIT

assert_exit() {
    local desc="$1" expected="$2"
    shift 2
    local actual
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
        echo "FAIL: $desc (expected '$pattern' in output, got: $out)"
        FAIL=$((FAIL + 1))
    fi
}

assert_output_not_contains() {
    local desc="$1" pattern="$2"
    shift 2
    local out
    set +e
    out=$("$@" 2>&1)
    set -e
    if echo "$out" | grep -q "$pattern"; then
        echo "FAIL: $desc (expected no '$pattern' in output, got: $out)"
        FAIL=$((FAIL + 1))
    else
        echo "PASS: $desc"
        PASS=$((PASS + 1))
    fi
}

# ── Set up test files ─────────────────────────────────────────────────────────

# A markdown file deep in a nested dir so ../../../.. escapes repo root
NESTED="$TMPDIR_TEST/a/b/c"
mkdir -p "$NESTED"

# T3a: link with too many ../ hops → ESCAPES_REPO
cat > "$NESTED/escaping.md" <<'EOF'
# Doc

See [outside](../../../../../../../../outside.md) for details.
EOF

# T3b: valid relative link within same dir → not flagged
cat > "$NESTED/clean.md" <<'EOF'
# Clean

See [sibling](./sibling.md) for details.
EOF
touch "$NESTED/sibling.md"

# T3c: valid link to parent dir within repo — use a real path inside TMPDIR_TEST
cat > "$NESTED/valid_parent.md" <<EOF
# Valid

See [parent](../README.md) for details.
EOF
touch "$TMPDIR_TEST/a/b/README.md"

# T3d: https link → not flagged
cat > "$NESTED/url.md" <<'EOF'
# URL

See [external](https://example.com/doc) for details.
EOF

# T3e: anchor link → not flagged
cat > "$NESTED/anchor.md" <<'EOF'
# Anchor

See [section](#heading) for details.
EOF

# ── Tests ─────────────────────────────────────────────────────────────────────

# T3a: escaping link flagged as ESCAPES_REPO
assert_exit "escaping link exits 1" 1 \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" "$NESTED/escaping.md"

assert_output_contains "escaping link has ESCAPES_REPO reason" "ESCAPES_REPO" \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" "$NESTED/escaping.md"

# T3b: same-dir relative link → clean
assert_exit "same-dir relative link exits 0" 0 \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" "$NESTED/clean.md"

# T3c: parent-dir link still in TMPDIR_TEST → clean
assert_exit "parent-dir link within root exits 0" 0 \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" "$NESTED/valid_parent.md"

# T3d: https link not flagged
assert_exit "https link exits 0" 0 \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" "$NESTED/url.md"

assert_output_not_contains "https link not in output" "ESCAPES_REPO" \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" "$NESTED/url.md"

# T3e: anchor link not flagged
assert_exit "anchor link exits 0" 0 \
    "$SCRIPT" --repo-root "$TMPDIR_TEST" "$NESTED/anchor.md"

# T3f: output format check — file:line: target [REASON]
OUT=$("$SCRIPT" --repo-root "$TMPDIR_TEST" "$NESTED/escaping.md" 2>/dev/null || true)
if echo "$OUT" | grep -qE "^[^:]+:[0-9]+: .+ \[ESCAPES_REPO\]$"; then
    echo "PASS: output format is file:line: target [REASON]"
    PASS=$((PASS + 1))
else
    echo "FAIL: output format wrong (got: $OUT)"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
