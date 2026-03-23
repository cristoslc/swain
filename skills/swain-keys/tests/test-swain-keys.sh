#!/usr/bin/env bash
# test-swain-keys.sh — Acceptance tests for swain-keys.sh
#
# Usage: bash skills/swain-keys/tests/test-swain-keys.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEYS_SCRIPT="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/swain-keys.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

make_repo() {
  local repo_dir="$1"
  mkdir -p "$repo_dir"
  git -C "$repo_dir" init -q
  git -C "$repo_dir" remote add origin "git@github.com-swain:cristoslc/swain.git"
}

echo "=== swain-keys Acceptance Tests ==="
echo "Script: $KEYS_SCRIPT"
echo ""

echo "--- AC1: status tolerates missing git email ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home"
REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR"
make_repo "$REPO_DIR"

output="$(cd "$REPO_DIR" && HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --status 2>&1)"
status=$?
if [[ $status -eq 0 && "$output" == *"Git email:        (not set)"* ]]; then
  pass "AC1: status exits 0 and shows placeholder email"
else
  fail "AC1" "status=$status output=$output"
fi

rm -rf "$TMPDIR"

echo "--- AC2: provision writes GitHub SSH-over-443 alias config ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home"
REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR"
make_repo "$REPO_DIR"
git -C "$REPO_DIR" config user.name "Test User"
git -C "$REPO_DIR" config user.email "test@example.com"
printf 'seed\n' > "$REPO_DIR/README.md"
git -C "$REPO_DIR" add README.md
git -C "$REPO_DIR" commit -qm "seed"

output="$(cd "$REPO_DIR" && HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --provision 2>&1)"
status=$?
alias_file="$HOME_DIR/.ssh/config.d/swain.conf"
if [[ $status -eq 0 && -f "$alias_file" ]] \
  && grep -q "Host github.com-swain" "$alias_file" \
  && grep -q "HostName ssh.github.com" "$alias_file" \
  && grep -q "Port 443" "$alias_file"; then
  pass "AC2: provision writes SSH-over-443 alias config"
else
  fail "AC2" "status=$status output=$output"
fi

echo "--- AC3: provision migrates legacy github.com:22 alias config ---"
cat > "$alias_file" <<EOF
Host github.com-swain
  HostName github.com
  User git
  IdentityFile $HOME_DIR/.ssh/swain_signing
  IdentitiesOnly yes
EOF

output="$(cd "$REPO_DIR" && HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --provision 2>&1)"
status=$?
if [[ $status -eq 0 ]] \
  && grep -q "HostName ssh.github.com" "$alias_file" \
  && grep -q "Port 443" "$alias_file"; then
  pass "AC3: provision migrates legacy alias config"
else
  fail "AC3" "status=$status output=$output"
fi

rm -rf "$TMPDIR"

echo ""
echo "=== Summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
