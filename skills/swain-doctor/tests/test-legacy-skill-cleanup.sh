#!/usr/bin/env bash
# test-legacy-skill-cleanup.sh — verifies stale swain skill cleanup

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DOCTOR_SCRIPT="$REPO_ROOT/.agents/bin/swain-doctor.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

make_test_repo() {
  local repo_dir="$1"
  mkdir -p "$repo_dir/.agents/bin" "$repo_dir/.agents/skills" "$repo_dir/.claude/skills" "$repo_dir/skills/swain/scripts"
  cd "$repo_dir" || exit 1
  git init -q
  git checkout -q -b trunk
  git config user.email "test@test.com"
  git config user.name "Test"
  git config commit.gpgsign true

  cat > AGENTS.md <<'EOF_AGENTS'
<!-- swain governance -->
Swain governance
<!-- end swain governance -->
EOF_AGENTS

  cat > .agents/bin/swain-trunk.sh <<'EOF_TRUNK'
#!/usr/bin/env bash
echo trunk
EOF_TRUNK
  chmod +x .agents/bin/swain-trunk.sh

  cat > skills/swain/scripts/swain <<'EOF_SWAIN'
#!/usr/bin/env bash
exit 0
EOF_SWAIN
  chmod +x skills/swain/scripts/swain

  git add -A
  git commit -q -m "initial: create test repo"
}

echo "=== Legacy Skill Cleanup Tests ==="
echo ""

echo "--- Removes fingerprinted swain-status from .agents/skills ---"
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

output="$(cd "$REPO_DIR" && bash "$DOCTOR_SCRIPT" 2>/dev/null)"
status=$?
legacy_status="$(echo "$output" | jq -r '.checks[] | select(.name == "legacy_skills") | .status' 2>/dev/null)"

if [[ $status -eq 0 && "$legacy_status" == "advisory" && ! -d "$REPO_DIR/.agents/skills/swain-status" ]]; then
  pass "doctor removes fingerprinted stale skill"
else
  fail "doctor removes fingerprinted stale skill" "status=$status legacy_status=$legacy_status"
fi
rm -rf "$TMPDIR"

echo "--- Leaves non-swain skill with same directory name in place ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/repo"
make_test_repo "$REPO_DIR"
mkdir -p "$REPO_DIR/.claude/skills/swain-status"
cat > "$REPO_DIR/.claude/skills/swain-status/SKILL.md" <<'EOF_SKILL'
---
name: swain-status
description: third-party status helper
---

# Custom status helper
EOF_SKILL

output="$(cd "$REPO_DIR" && bash "$DOCTOR_SCRIPT" 2>/dev/null)"
status=$?
legacy_status="$(echo "$output" | jq -r '.checks[] | select(.name == "legacy_skills") | .status' 2>/dev/null)"

if [[ $status -eq 0 && "$legacy_status" == "warning" && -d "$REPO_DIR/.claude/skills/swain-status" ]]; then
  pass "doctor preserves non-swain directory name collision"
else
  fail "doctor preserves non-swain directory name collision" "status=$status legacy_status=$legacy_status"
fi
rm -rf "$TMPDIR"

echo ""
echo "=== Summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
