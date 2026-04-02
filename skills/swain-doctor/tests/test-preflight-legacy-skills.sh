#!/usr/bin/env bash
# test-preflight-legacy-skills.sh — verifies preflight surfaces stale skills

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PREFLIGHT="$REPO_ROOT/.agents/bin/swain-preflight.sh"
CANONICAL_AGENTS="$REPO_ROOT/skills/swain-doctor/references/AGENTS.content.md"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

make_test_repo() {
  local repo_dir="$1"
  mkdir -p "$repo_dir/.agents/bin" "$repo_dir/.agents/skills"
  cd "$repo_dir" || exit 1
  git init -q
  git checkout -q -b trunk
  git config user.email "test@test.com"
  git config user.name "Test"
  git config commit.gpgsign true

  cp "$CANONICAL_AGENTS" "$repo_dir/AGENTS.md"

  cat > .agents/bin/swain-trunk.sh <<'EOF_TRUNK'
#!/usr/bin/env bash
echo trunk
EOF_TRUNK
  chmod +x .agents/bin/swain-trunk.sh

  git add -A
  git commit -q -m "initial: create test repo"
}

echo "=== Preflight Legacy Skill Tests ==="
echo ""

echo "--- Clean repo does not report legacy skill directories ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/repo"
make_test_repo "$REPO_DIR"

output="$(cd "$REPO_DIR" && bash "$PREFLIGHT" 2>&1)"
status=$?
if [[ "$output" != *"legacy skill directories detected"* ]]; then
  pass "clean repo stays clear of legacy-skill warnings"
else
  fail "clean repo stays clear of legacy-skill warnings" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

echo "--- Fingerprinted stale skill triggers doctor via preflight ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/repo"
make_test_repo "$REPO_DIR"
mkdir -p "$REPO_DIR/.agents/skills/swain-status"
cat > "$REPO_DIR/.agents/skills/swain-status/SKILL.md" <<'EOF_SKILL'
---
name: swain-status
author: cristos
source: swain
---

# swain-status
EOF_SKILL

output="$(cd "$REPO_DIR" && bash "$PREFLIGHT" 2>&1)"
status=$?
if [[ $status -eq 1 && "$output" == *"legacy skill directories detected"* ]]; then
  pass "stale skill triggers doctor invocation"
else
  fail "stale skill triggers doctor invocation" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

echo ""
echo "=== Summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
