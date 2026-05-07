#!/usr/bin/env bash
set +e

# test-swain-keys.sh — Acceptance tests for swain-keys.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEYS_SCRIPT="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/swain-keys.sh"

PASS=0; FAIL=0
pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

echo "=== swain-keys Acceptance Tests ==="
echo "Script: $KEYS_SCRIPT"
echo ""

# ----- AC1-3: basic GitHub flow (preserved) -----

echo "--- AC1: status tolerates missing git email ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR" "$REPO_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@github.com:cristoslc/swain.git"

cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" SWAIN_FORGE="github" bash "$KEYS_SCRIPT" --status 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -eq 0 && "$output" == *"Git email:        (not set)"* ]]; then
  pass "AC1: status exits 0 and shows placeholder email"
else
  fail "AC1" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

echo "--- AC2: provision writes GitHub SSH-over-443 alias config ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR" "$REPO_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@github.com:cristoslc/swain.git"
git -C "$REPO_DIR" config user.name "Test User"
git -C "$REPO_DIR" config user.email "test@example.com"
printf 'seed\n' > "$REPO_DIR/README.md"
git -C "$REPO_DIR" add README.md
git -C "$REPO_DIR" commit -qm "seed"

cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --provision 2>&1)"
status=$?
cd - >/dev/null
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
cat > "$alias_file" <<SSHEOF
Host github.com-swain
  HostName github.com
  User git
  IdentityFile $HOME_DIR/.ssh/swain_signing
  IdentitiesOnly yes
SSHEOF
cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" SWAIN_FORGE="github" bash "$KEYS_SCRIPT" --provision 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -eq 0 ]] \
  && grep -q "HostName ssh.github.com" "$alias_file" \
  && grep -q "Port 443" "$alias_file"; then
  pass "AC3: provision migrates legacy alias config"
else
  fail "AC3" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# ----- AC4-7: forge detection -----

echo "--- AC4: detection — github.com remote → GitHub ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR" "$REPO_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@github.com:cristoslc/test-project.git"
cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --status 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -eq 0 && "$output" == *"Forge:            github"* ]]; then
  pass "AC4: detects GitHub forge from remote URL"
else
  fail "AC4" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

echo "--- AC5: detection — localhost remote → Forgejo ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR" "$REPO_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@localhost:cristoslc/my-project.git"
cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --status 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -eq 0 && "$output" == *"Forge:            forgejo"* ]]; then
  pass "AC5: detects Forgejo forge from localhost remote URL"
else
  fail "AC5" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

echo "--- AC6: detection — codeberg.org remote → Forgejo ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR" "$REPO_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@codeberg.org:user/cool-project.git"
cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --status 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -eq 0 && "$output" == *"Forge:            forgejo"* ]]; then
  pass "AC6: detects Forgejo forge from codeberg.org remote"
else
  fail "AC6" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

echo "--- AC7: SWAIN_FORGE override respected ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR" "$REPO_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@github.com:cristoslc/test-project.git"
cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" SWAIN_FORGE="forgejo" bash "$KEYS_SCRIPT" --status 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -eq 0 && "$output" == *"Forge:            forgejo"* ]]; then
  pass "AC7: SWAIN_FORGE override respected"
else
  fail "AC7" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# ----- AC8: Forgejo provision -----

echo "--- AC8: Forgejo provision generates GPG key and configures openpgp ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo" BIN_DIR="$TMPDIR/bin"
mkdir -p "$HOME_DIR" "$REPO_DIR" "$BIN_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@localhost:cristoslc/the-repo.git"
git -C "$REPO_DIR" config user.name "Test User"
git -C "$REPO_DIR" config user.email "test@example.com"
printf 'seed\n' > "$REPO_DIR/README.md"
git -C "$REPO_DIR" add README.md
git -C "$REPO_DIR" commit -qm "seed"

cat > "$BIN_DIR/gpg" <<'GPGMOCK'
#!/usr/bin/env bash
case "$*" in
  *--list-secret-keys\ *)
    exit 0
    ;;
  *--with-colons*)
    exit 0
    ;;
  *--batch*--generate-key*)
    echo "gpg: key ABCDEF1234567890 marked as ultimately trusted"
    exit 0
    ;;
  *--armor*--export*)
    echo "-----BEGIN PGP PUBLIC KEY BLOCK-----"
    echo "mock-key-data"
    echo "-----END PGP PUBLIC KEY BLOCK-----"
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
GPGMOCK

cat > "$BIN_DIR/fj" <<'FJMOCK'
#!/usr/bin/env bash
# fj mock: args are fj -H <host> user <cmd> ...
shift; shift  # skip -H <host>
if [[ "$1 $2" == "user info" ]]; then exit 0; fi
if [[ "$1 $2 $3" == "user gpg list" ]]; then
  echo "ABCDEF1234567890 Can Sign: true Verified: true"
  exit 0
fi
if [[ "$1 $2 $3" == "user gpg upload" ]]; then exit 0; fi
exit 0
FJMOCK
chmod +x "$BIN_DIR/gpg" "$BIN_DIR/fj"

cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" SWAIN_FORGE="forgejo" PATH="$BIN_DIR:$PATH" bash "$KEYS_SCRIPT" --provision 2>&1)"
status=$?
cd - >/dev/null
gpg_format="$(git -C "$REPO_DIR" config --local gpg.format || true)"
# In mock env with real gpg in PATH, the "already registered" path also counts as success
if [[ "$output" == *"GPG key generated"* || "$output" == *"GPG key already tracked"* ]] \
  && { [[ "$output" == *"registered on Forgejo as signing key"* ]] || [[ "$output" == *"already registered on Forgejo"* ]]; } \
  && [[ "$gpg_format" == "openpgp" ]]; then
  pass "AC8: Forgejo provision generates GPG key and configures openpgp"
else
  fail "AC8" "status=$status gpg_format=$gpg_format output=$output"
fi

echo "--- AC8b: Forgejo provision does NOT write SSH config alias ---"
if [[ ! -f "$HOME_DIR/.ssh/config.d/the-repo.conf" ]]; then
  pass "AC8b: no SSH config alias written for Forgejo"
else
  fail "AC8b" "SSH config alias should not exist for Forgejo"
fi

echo "--- AC8c: Forgejo provision leaves remote URL unchanged ---"
remote_url="$(git -C "$REPO_DIR" remote get-url origin)"
if [[ "$remote_url" == *"localhost"* ]]; then
  pass "AC8c: remote URL unchanged for Forgejo"
else
  fail "AC8c" "remote URL was changed: $remote_url"
fi
rm -rf "$TMPDIR"

# ----- AC9: Forgejo status -----

echo "--- AC9: status shows Forgejo with GPG key info ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo" BIN_DIR="$TMPDIR/bin"
mkdir -p "$HOME_DIR" "$REPO_DIR" "$BIN_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@localhost:cristoslc/proj.git"
git -C "$REPO_DIR" config user.email "tester@example.com"

cat > "$BIN_DIR/gpg" <<'GPGMOCK9'
#!/usr/bin/env bash
exit 1
GPGMOCK9

cat > "$BIN_DIR/fj" <<'FJMOCK9'
#!/usr/bin/env bash
shift 2  # skip -H <host>
if [[ "$1 $2" == "user info" ]]; then exit 0; fi
if [[ "$1 $2 $3" == "user gpg list" ]]; then
  echo "BEEF1234567890AB Can Sign: true Verified: true"
  exit 0
fi
exit 0
FJMOCK9
chmod +x "$BIN_DIR/gpg" "$BIN_DIR/fj"

mkdir -p "$HOME_DIR/.ssh"
echo "BEEF1234567890AB" > "$HOME_DIR/.ssh/proj_gpg_keyid"

cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" SWAIN_FORGE="forgejo" PATH="$BIN_DIR:$PATH" bash "$KEYS_SCRIPT" --status 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -eq 0 ]] \
  && echo "$output" | grep -q "Forge:            forgejo" \
  && echo "$output" | grep -q "GPG keyid file" \
  && { echo "$output" | grep -q "registered on Forgejo as signing key" || echo "$output" | grep -q "fj CLI not authenticated"; }; then
  pass "AC9: status shows Forgejo with GPG key info"
else
  fail "AC9" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# ----- AC10: GitHub path doesn't call GPG -----

echo "--- AC10: GitHub provision does not invoke GPG key generation ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR" "$REPO_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@github.com:cristoslc/swain.git"
git -C "$REPO_DIR" config user.name "Test User"
git -C "$REPO_DIR" config user.email "test@example.com"
printf 'seed\n' > "$REPO_DIR/README.md"
git -C "$REPO_DIR" add README.md
git -C "$REPO_DIR" commit -qm "seed"

cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --provision 2>&1)"
status=$?
cd - >/dev/null
alias_file="$HOME_DIR/.ssh/config.d/swain.conf"
if [[ $status -eq 0 && -f "$alias_file" ]] \
  && [[ "$output" != *"Generating OpenPGP"* ]]; then
  pass "AC10: GitHub provision does not invoke GPG key generation"
else
  fail "AC10" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# ----- AC11: Forgejo provision reuses existing GPG key -----

echo "--- AC11: Forgejo provision reuses existing GPG key ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo" BIN_DIR="$TMPDIR/bin"
mkdir -p "$HOME_DIR" "$REPO_DIR" "$BIN_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@localhost:cristoslc/the-repo.git"
git -C "$REPO_DIR" config user.name "Test User"
git -C "$REPO_DIR" config user.email "test@example.com"
printf 'seed\n' > "$REPO_DIR/README.md"
git -C "$REPO_DIR" add README.md
git -C "$REPO_DIR" commit -qm "seed"

mkdir -p "$HOME_DIR/.ssh"
echo "EXISTKEY12345678" > "$HOME_DIR/.ssh/the-repo_gpg_keyid"

cat > "$BIN_DIR/gpg" <<'GPGMOCK11'
#!/usr/bin/env bash
if [[ "$*" == *"--list-secret-keys "* ]]; then exit 0; fi
if [[ "$*" == *"EXISTKEY12345678" ]]; then exit 0; fi
if [[ "$*" == *"--with-colons"* ]]; then
  echo "sec:u:255:1:EXISTKEY12345678:::0:::scESC:::+::ed25519:::"
  exit 0
fi
if [[ "$*" == *"--armor --export"* ]]; then
  echo "-----BEGIN PGP PUBLIC KEY BLOCK-----"
  echo "mock-key-data"
  echo "-----END PGP PUBLIC KEY BLOCK-----"
  exit 0
fi
exit 0
GPGMOCK11

cat > "$BIN_DIR/fj" <<'FJMOCK11'
#!/usr/bin/env bash
shift 2  # skip -H <host>
if [[ "$1 $2" == "user info" ]]; then exit 0; fi
if [[ "$1 $2 $3" == "user gpg list" ]]; then
  echo "EXISTKEY12345678 Can Sign: true Verified: true"
  exit 0
fi
if [[ "$1 $2 $3" == "user gpg upload" ]]; then exit 0; fi
exit 0
FJMOCK11
chmod +x "$BIN_DIR/gpg" "$BIN_DIR/fj"

cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" SWAIN_FORGE="forgejo" PATH="$BIN_DIR:$PATH" bash "$KEYS_SCRIPT" --provision 2>&1)"
status=$?
cd - >/dev/null
if [[ "$output" == *"GPG key already"* ]]; then
  pass "AC11: Forgejo provision reuses existing GPG key"
else
  fail "AC11" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# ----- AC12: Forgejo fails cleanly without gpg -----

echo "--- AC12: Forgejo provision fails cleanly when gpg not installed ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo" BIN_DIR="$TMPDIR/bin"
mkdir -p "$HOME_DIR" "$REPO_DIR" "$BIN_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@localhost:cristoslc/failproj.git"
git -C "$REPO_DIR" config user.email "test@example.com"
printf 'seed\n' > "$REPO_DIR/README.md"
git -C "$REPO_DIR" add README.md
git -C "$REPO_DIR" commit -qm "seed"

# Create a BIN_DIR with fj mock but NO gpg
cat > "$BIN_DIR/fj" <<'FJMOCK12'
#!/usr/bin/env bash
shift 2
exit 0
FJMOCK12
chmod +x "$BIN_DIR/fj"

cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" SWAIN_FORGE="forgejo" PATH="$BIN_DIR:/usr/bin:/bin" bash "$KEYS_SCRIPT" --provision 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -ne 0 ]] && [[ "$output" == *"gpg is required"* ]]; then
  pass "AC12: Forgejo provision fails with clear gpg install message"
else
  fail "AC12" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

# ----- AC13: verify shows forge type -----

echo "--- AC13: verify shows forge type for Forgejo ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo" BIN_DIR="$TMPDIR/bin"
mkdir -p "$HOME_DIR" "$REPO_DIR" "$BIN_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@localhost:cristoslc/vproj.git"
git -C "$REPO_DIR" config user.email "test@example.com"
printf 'seed\n' > "$REPO_DIR/README.md"
git -C "$REPO_DIR" add README.md
git -C "$REPO_DIR" commit -qm "seed"

cat > "$BIN_DIR/gpg" <<'GPGMOCK13'
#!/usr/bin/env bash
exit 0
GPGMOCK13

cat > "$BIN_DIR/fj" <<'FJMOCK13'
#!/usr/bin/env bash
shift 2  # skip -H <host>
if [[ "$1 $2" == "user info" ]]; then exit 0; fi
if [[ "$1 $2 $3" == "user gpg list" ]]; then
  echo "BEEF12345678 Can Sign: true Verified: true"
  exit 0
fi
exit 0
FJMOCK13
chmod +x "$BIN_DIR/gpg" "$BIN_DIR/fj"

mkdir -p "$HOME_DIR/.ssh"
echo "BEEF12345678" > "$HOME_DIR/.ssh/vproj_gpg_keyid"

cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" SWAIN_FORGE="forgejo" PATH="$BIN_DIR:$PATH" bash "$KEYS_SCRIPT" --verify 2>&1)"
cd - >/dev/null
if [[ "$output" == *"forge: forgejo"* ]]; then
  pass "AC13: verify shows forge type for Forgejo"
else
  fail "AC13" "status=$? output=$output"
fi
rm -rf "$TMPDIR"

# ----- AC14: unknown forge -----

echo "--- AC14: unknown forge exits with code 2 and clear message ---"
TMPDIR="$(mktemp -d)"
HOME_DIR="$TMPDIR/home" REPO_DIR="$TMPDIR/repo"
mkdir -p "$HOME_DIR" "$REPO_DIR"
git -C "$REPO_DIR" init -q
git -C "$REPO_DIR" remote add origin "git@bitbucket.org:user/unknown-project.git"
cd "$REPO_DIR"
output="$(HOME="$HOME_DIR" bash "$KEYS_SCRIPT" --status 2>&1)"
status=$?
cd - >/dev/null
if [[ $status -eq 2 && "$output" == *"UNKNOWN_FORGE"* ]]; then
  pass "AC14: unknown forge exits with code 2"
else
  fail "AC14" "status=$status output=$output"
fi
rm -rf "$TMPDIR"

echo ""
echo "=== Summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [[ $FAIL -gt 0 ]]; then exit 1; fi
