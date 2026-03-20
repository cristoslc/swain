#!/usr/bin/env bash
# test-ssh-readiness.sh — Acceptance tests for swain-doctor SSH readiness helper
#
# Usage: bash skills/swain-doctor/tests/test-ssh-readiness.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSH_HELPER="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/ssh-readiness.sh"

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

echo "=== swain-doctor SSH Readiness Tests ==="
echo "Helper: $SSH_HELPER"
echo ""

echo "--- AC1: check reports missing alias config for alias remotes ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home"
REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR"
make_repo "$REPO_DIR"

output="$(cd "$REPO_DIR" && HOME="$HOME_DIR" bash "$SSH_HELPER" --check 2>&1)"
status=$?
if [[ $status -ne 0 && "$output" == *"github.com-swain"* && "$output" == *"swain-keys --provision"* ]]; then
  pass "AC1: missing alias config reported"
else
  fail "AC1" "status=$status output=$output"
fi

echo "--- AC2: repair creates include + alias config when key exists ---"
mkdir -p "$HOME_DIR/.ssh"
touch "$HOME_DIR/.ssh/swain_signing"
chmod 600 "$HOME_DIR/.ssh/swain_signing"

output="$(cd "$REPO_DIR" && HOME="$HOME_DIR" bash "$SSH_HELPER" --repair 2>&1)"
status=$?
config_file="$HOME_DIR/.ssh/config"
alias_file="$HOME_DIR/.ssh/config.d/swain.conf"
if [[ $status -eq 0 && -f "$config_file" && -f "$alias_file" ]] \
  && grep -q "Include config.d/\\*" "$config_file" \
  && grep -q "Host github.com-swain" "$alias_file" \
  && grep -q "HostName ssh.github.com" "$alias_file" \
  && grep -q "Port 443" "$alias_file" \
  && grep -q "IdentityFile $HOME_DIR/.ssh/swain_signing" "$alias_file"; then
  pass "AC2: repair writes SSH include and alias config"
else
  fail "AC2" "status=$status output=$output"
fi

echo "--- AC3: repair migrates legacy github.com:22 alias config ---"
cat > "$alias_file" <<EOF
Host github.com-swain
  HostName github.com
  User git
  IdentityFile $HOME_DIR/.ssh/swain_signing
  IdentitiesOnly yes
EOF

output="$(cd "$REPO_DIR" && HOME="$HOME_DIR" bash "$SSH_HELPER" --repair 2>&1)"
status=$?
if [[ $status -eq 0 ]] \
  && grep -q "HostName ssh.github.com" "$alias_file" \
  && grep -q "Port 443" "$alias_file"; then
  pass "AC3: repair migrates legacy alias config"
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
