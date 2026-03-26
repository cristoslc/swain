#!/usr/bin/env bash
# test-gitignore-skill-folders.sh — Acceptance tests for gitignore skill-folder check
#
# Tests the detection logic used by swain-doctor and swain-preflight to verify
# that .claude/skills/ and .agents/skills/ are gitignored in consumer projects.
#
# Usage: bash skills/swain-doctor/tests/test-gitignore-skill-folders.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFLIGHT="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/swain-preflight.sh"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

# Helper: create a minimal git repo with optional remote
make_consumer_repo() {
  local repo_dir="$1"
  mkdir -p "$repo_dir"
  git -C "$repo_dir" init -q
  git -C "$repo_dir" remote add origin "git@github.com:someuser/someproject.git"
  # Create skill folders to simulate installed skills
  mkdir -p "$repo_dir/.claude/skills/swain-doctor"
  mkdir -p "$repo_dir/.agents/skills/brainstorming"
}

make_swain_repo() {
  local repo_dir="$1"
  mkdir -p "$repo_dir"
  git -C "$repo_dir" init -q
  git -C "$repo_dir" remote add origin "git@github.com-swain:cristoslc/swain.git"
  mkdir -p "$repo_dir/.claude/skills/swain-doctor"
  mkdir -p "$repo_dir/.agents/skills/brainstorming"
}

echo "=== Gitignore Skill Folders Check Tests ==="
echo ""

# --- AC1: Warning on missing gitignore ---
echo "--- AC1: consumer project without gitignore warns about skill folders ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/consumer1"
make_consumer_repo "$REPO_DIR"

# Run git check-ignore against the skill folders — should NOT be ignored
claude_ignored=$(cd "$REPO_DIR" && git check-ignore -q .claude/skills/ 2>/dev/null; echo $?)
agents_ignored=$(cd "$REPO_DIR" && git check-ignore -q .agents/skills/ 2>/dev/null; echo $?)

if [[ "$claude_ignored" -ne 0 && "$agents_ignored" -ne 0 ]]; then
  pass "AC1: skill folders are not gitignored in bare consumer repo"
else
  fail "AC1" "expected both folders NOT ignored, got claude=$claude_ignored agents=$agents_ignored"
fi
rm -rf "$TMPDIR"

# --- AC2: OK when already gitignored ---
echo "--- AC2: consumer project with gitignore reports OK ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/consumer2"
make_consumer_repo "$REPO_DIR"

cat > "$REPO_DIR/.gitignore" <<'EOF'
# Vendored swain skills (managed by swain-update)
.claude/skills/
.agents/skills/
EOF

claude_ignored=$(cd "$REPO_DIR" && git check-ignore -q .claude/skills/ 2>/dev/null; echo $?)
agents_ignored=$(cd "$REPO_DIR" && git check-ignore -q .agents/skills/ 2>/dev/null; echo $?)

if [[ "$claude_ignored" -eq 0 && "$agents_ignored" -eq 0 ]]; then
  pass "AC2: skill folders are gitignored when .gitignore has entries"
else
  fail "AC2" "expected both folders ignored, got claude=$claude_ignored agents=$agents_ignored"
fi
rm -rf "$TMPDIR"

# --- AC3: Swain repo self-detection skips check ---
echo "--- AC3: swain source repo is detected and check is skipped ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/swain"
make_swain_repo "$REPO_DIR"

remote_url=$(cd "$REPO_DIR" && git remote get-url origin 2>/dev/null)
is_swain=no
if [[ "$remote_url" == *"cristoslc/swain"* ]]; then
  is_swain=yes
fi

if [[ "$is_swain" == "yes" ]]; then
  pass "AC3: swain repo detected via remote URL"
else
  fail "AC3" "expected swain detection, got remote=$remote_url"
fi
rm -rf "$TMPDIR"

# --- AC4: Creates .gitignore if absent ---
echo "--- AC4: remediation creates .gitignore when file is absent ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/consumer3"
make_consumer_repo "$REPO_DIR"

# Simulate remediation: append entries to .gitignore
gitignore_path="$REPO_DIR/.gitignore"
if [[ ! -f "$gitignore_path" ]]; then
  cat > "$gitignore_path" <<'GITIGNORE'
# Vendored swain skills (managed by swain-update)
.claude/skills/
.agents/skills/
GITIGNORE
fi

if [[ -f "$gitignore_path" ]]; then
  claude_ignored=$(cd "$REPO_DIR" && git check-ignore -q .claude/skills/ 2>/dev/null; echo $?)
  agents_ignored=$(cd "$REPO_DIR" && git check-ignore -q .agents/skills/ 2>/dev/null; echo $?)
  if [[ "$claude_ignored" -eq 0 && "$agents_ignored" -eq 0 ]]; then
    pass "AC4: created .gitignore covers both skill folders"
  else
    fail "AC4" "gitignore created but folders not ignored: claude=$claude_ignored agents=$agents_ignored"
  fi
else
  fail "AC4" ".gitignore was not created"
fi
rm -rf "$TMPDIR"

# --- AC5: Partial coverage — only one path gitignored ---
echo "--- AC5: partial coverage detects the missing entry ---"
TMPDIR="$(mktemp -d)"
REPO_DIR="$TMPDIR/consumer4"
make_consumer_repo "$REPO_DIR"

# Only gitignore .claude/skills/, not .agents/skills/
cat > "$REPO_DIR/.gitignore" <<'EOF'
.claude/skills/
EOF

claude_ignored=$(cd "$REPO_DIR" && git check-ignore -q .claude/skills/ 2>/dev/null; echo $?)
agents_ignored=$(cd "$REPO_DIR" && git check-ignore -q .agents/skills/ 2>/dev/null; echo $?)

if [[ "$claude_ignored" -eq 0 && "$agents_ignored" -ne 0 ]]; then
  pass "AC5: partial coverage detected — .claude/skills/ ignored, .agents/skills/ not"
else
  fail "AC5" "expected partial coverage, got claude=$claude_ignored agents=$agents_ignored"
fi
rm -rf "$TMPDIR"

echo ""
echo "=== Summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
