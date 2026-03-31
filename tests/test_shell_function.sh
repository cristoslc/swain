#!/usr/bin/env bash
# RED tests for SPEC-181: Swain Shell Function Refactor
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
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

echo "=== SPEC-181: Shell Function Refactor Tests ==="

# T1: Thin wrapper template exists
TEMPLATE="$REPO_ROOT/skills/swain-init/templates/launchers/thin-wrapper/swain.bash"
assert "thin wrapper template exists" "$([ -f "$TEMPLATE" ] && echo true || echo false)"

# T2: Template is under 20 lines of function body
FUNC_LINES=$(sed -n '/^swain()/,/^}/p' "$TEMPLATE" 2>/dev/null | wc -l | tr -d ' ')
assert "function body under 20 lines" "$([ "$FUNC_LINES" -le 20 ] && echo true || echo false)"

# T3: Template contains bin/swain delegation
assert "template delegates to bin/swain" "$(grep -q 'bin/swain' "$TEMPLATE" && echo true || echo false)"

# T4: Template has fallback for missing bin/swain
assert "template has fallback" "$(grep -q 'command -v' "$TEMPLATE" && echo true || echo false)"

# T5: Template forwards arguments ($@)
assert "template forwards args" "$(grep -q '"$@"' "$TEMPLATE" && echo true || echo false)"

# T6: bin/swain delegation works (integration test)
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/bin"
cat > "$TMPDIR/bin/swain" <<'FAKESCRIPT'
#!/usr/bin/env bash
echo "DELEGATED: $*"
FAKESCRIPT
chmod +x "$TMPDIR/bin/swain"

DELEGATE_OUT=$(cd "$TMPDIR" && bash -c "source '$TEMPLATE' && swain test-arg-1 test-arg-2" 2>&1 || true)
assert "bin/swain delegation works" "$(echo "$DELEGATE_OUT" | grep -q 'DELEGATED: test-arg-1 test-arg-2' && echo true || echo false)"
rm -rf "$TMPDIR"

# T7: Fallback works when no bin/swain and no runtime
TMPDIR2=$(mktemp -d)
FALLBACK_OUT=$(cd "$TMPDIR2" && PATH=/usr/bin:/bin bash -c "source '$TEMPLATE' && swain" 2>&1 || true)
assert "fallback without runtime shows error" "$(echo "$FALLBACK_OUT" | grep -q 'no bin/swain\|no supported runtime' && echo true || echo false)"
rm -rf "$TMPDIR2"

# T8: Zsh template also exists
ZSH_TEMPLATE="$REPO_ROOT/skills/swain-init/templates/launchers/thin-wrapper/swain.zsh"
assert "zsh template exists" "$([ -f "$ZSH_TEMPLATE" ] && echo true || echo false)"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
