#!/usr/bin/env bash
# test-swain-doctor-sh.sh — tests for the consolidated swain-doctor.sh script
# Verifies SPEC-192: parallel check cascade failure fix

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DOCTOR_SCRIPT="$REPO_ROOT/.agents/bin/swain-doctor.sh"

PASS=0
FAIL=0
TOTAL=0

assert() {
  local desc="$1"
  local result="$2"
  TOTAL=$((TOTAL + 1))
  if [[ "$result" == "0" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $desc"
  fi
}

# --- Test 1: Script exists and is executable ---
echo "Test 1: swain-doctor.sh exists and is executable"
assert "script exists" "$([ -f "$DOCTOR_SCRIPT" ] && echo 0 || echo 1)"
assert "script is executable" "$([ -x "$DOCTOR_SCRIPT" ] && echo 0 || echo 1)"

# --- Test 2: Script outputs valid JSON ---
echo "Test 2: outputs valid JSON"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  echo "$output" | jq empty 2>/dev/null
  assert "output is valid JSON" "$?"
else
  assert "output is valid JSON" "1"
fi

# --- Test 3: JSON has expected structure ---
echo "Test 3: JSON has expected top-level fields"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  assert "has 'checks' array" "$(echo "$output" | jq -e '.checks | type == "array"' >/dev/null 2>&1 && echo 0 || echo 1)"
  assert "has 'summary' object" "$(echo "$output" | jq -e '.summary | type == "object"' >/dev/null 2>&1 && echo 0 || echo 1)"
  assert "summary has total count" "$(echo "$output" | jq -e '.summary.total | type == "number"' >/dev/null 2>&1 && echo 0 || echo 1)"
else
  assert "has 'checks' array" "1"
  assert "has 'summary' object" "1"
  assert "summary has total count" "1"
fi

# --- Test 4: Each check has name, status, and message ---
echo "Test 4: each check entry has required fields"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  # Every check must have name and status
  bad_checks=$(echo "$output" | jq '[.checks[] | select(.name == null or .status == null)] | length' 2>/dev/null || echo "999")
  assert "all checks have name and status" "$([ "$bad_checks" = "0" ] && echo 0 || echo 1)"
else
  assert "all checks have name and status" "1"
fi

# --- Test 5: Script does NOT exit non-zero when checks find issues ---
echo "Test 5: script always exits 0 (findings reported in JSON, not exit code)"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  bash "$DOCTOR_SCRIPT" >/dev/null 2>&1
  assert "exits 0 regardless of findings" "$?"
else
  assert "exits 0 regardless of findings" "1"
fi

# --- Test 6: Known check names are present ---
echo "Test 6: known check categories are present"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  check_names=$(echo "$output" | jq -r '.checks[].name' 2>/dev/null || true)
  assert "governance check present" "$(echo "$check_names" | grep -q "governance" && echo 0 || echo 1)"
  assert "tools check present" "$(echo "$check_names" | grep -q "tools" && echo 0 || echo 1)"
  assert "agents_directory check present" "$(echo "$check_names" | grep -q "agents_directory" && echo 0 || echo 1)"
else
  assert "governance check present" "1"
  assert "tools check present" "1"
  assert "agents_directory check present" "1"
fi

# --- Test 7: agents_bin_symlinks check is present and passes (SPEC-206) ---
echo "Test 7: agents_bin_symlinks check"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  check_names=$(echo "$output" | jq -r '.checks[].name' 2>/dev/null || true)
  assert "agents_bin_symlinks check present" "$(echo "$check_names" | grep -q "agents_bin_symlinks" && echo 0 || echo 1)"
  symlink_status=$(echo "$output" | jq -r '.checks[] | select(.name == "agents_bin_symlinks") | .status' 2>/dev/null || echo "missing")
  assert "agents_bin_symlinks not warning" "$([ "$symlink_status" != "warning" ] && echo 0 || echo 1)"
else
  assert "agents_bin_symlinks check present" "1"
  assert "agents_bin_symlinks not warning" "1"
fi

# --- Test 8: agents_bin_symlinks detects broken symlinks (SPEC-206) ---
echo "Test 8: agents_bin_symlinks detects broken symlinks"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  # Create a broken symlink, run doctor (which auto-repairs), verify it was caught
  FAKE_LINK="$REPO_ROOT/.agents/bin/_test_broken_link.sh"
  ln -sf "../../skills/nonexistent/scripts/fake.sh" "$FAKE_LINK"
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  detail=$(echo "$output" | jq -r '.checks[] | select(.name == "agents_bin_symlinks") | .detail // ""' 2>/dev/null || echo "")
  assert "detects broken symlink" "$(echo "$detail" | grep -q "_test_broken_link" && echo 0 || echo 1)"
  # Verify auto-repair removed it
  assert "auto-repairs broken symlink" "$([ ! -L "$FAKE_LINK" ] && echo 0 || echo 1)"
  rm -f "$FAKE_LINK" 2>/dev/null || true
else
  assert "detects broken symlink" "1"
  assert "auto-repairs broken symlink" "1"
fi

# --- Test 9: agents_bin_symlinks detects missing symlinks (SPEC-206) ---
echo "Test 9: agents_bin_symlinks detects and repairs missing symlinks"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  # Remove a known symlink, run doctor, verify it was repaired
  TARGET="$REPO_ROOT/.agents/bin/swain-session-greeting.sh"
  if [[ -L "$TARGET" ]]; then
    SAVED_LINK=$(readlink "$TARGET")
    rm -f "$TARGET"
    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    assert "repairs missing symlink" "$([ -L "$TARGET" ] && [ -e "$TARGET" ] && echo 0 || echo 1)"
    # Clean up — restore original if repair used a different path
    if [[ ! -e "$TARGET" ]]; then
      ln -sf "$SAVED_LINK" "$TARGET"
    fi
  else
    # Symlink wasn't there to begin with — skip
    TOTAL=$((TOTAL + 1))
    PASS=$((PASS + 1))
    echo "  PASS: (skipped — symlink not present to test removal)"
  fi
else
  assert "repairs missing symlink" "1"
fi
# ============================================================
# SPEC-222: Auto-repair promotion tests
# ============================================================

# --- Test 10: memory_directory auto-repair (SPEC-222 AC1) ---
echo "Test 10: memory_directory auto-repair creates missing dir"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  project_slug=$(echo "$REPO_ROOT" | tr '/' '-')
  memory_dir="$HOME/.claude/projects/${project_slug}/memory"
  memory_existed=false
  if [[ -d "$memory_dir" ]]; then
    memory_existed=true
  else
    # Remove it so we can test repair
    true
  fi

  if [[ "$memory_existed" == "false" ]]; then
    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    mem_status=$(echo "$output" | jq -r '.checks[] | select(.name == "memory_directory") | .status' 2>/dev/null || echo "missing")
    assert "memory_directory auto-creates dir and reports advisory" "$([ "$mem_status" = "advisory" ] && echo 0 || echo 1)"
    assert "memory_directory dir now exists after repair" "$([ -d "$memory_dir" ] && echo 0 || echo 1)"
    # Idempotency: run again, should report ok
    output2=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    mem_status2=$(echo "$output2" | jq -r '.checks[] | select(.name == "memory_directory") | .status' 2>/dev/null || echo "missing")
    assert "memory_directory idempotent (ok on second run)" "$([ "$mem_status2" = "ok" ] && echo 0 || echo 1)"
  else
    # Dir already exists — just verify ok
    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    mem_status=$(echo "$output" | jq -r '.checks[] | select(.name == "memory_directory") | .status' 2>/dev/null || echo "missing")
    assert "memory_directory reports ok when dir exists" "$([ "$mem_status" = "ok" ] && echo 0 || echo 1)"
    # Force test: remove dir, run, verify advisory + creation
    rmdir "$memory_dir" 2>/dev/null || true
    if [[ ! -d "$memory_dir" ]]; then
      output2=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
      mem_status2=$(echo "$output2" | jq -r '.checks[] | select(.name == "memory_directory") | .status' 2>/dev/null || echo "missing")
      assert "memory_directory auto-creates and reports advisory" "$([ "$mem_status2" = "advisory" ] && echo 0 || echo 1)"
      assert "memory_directory dir exists after repair" "$([ -d "$memory_dir" ] && echo 0 || echo 1)"
      # Restore
      mkdir -p "$memory_dir"
    else
      TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
      echo "  PASS: (skipped — could not remove non-empty memory dir)"
      TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
      echo "  PASS: (skipped — could not remove non-empty memory dir)"
    fi
  fi
else
  assert "memory_directory auto-creates dir and reports advisory" "1"
  assert "memory_directory dir now exists after repair" "1"
  assert "memory_directory idempotent (ok on second run)" "1"
fi

# --- Test 11: script_permissions auto-repair (SPEC-222 AC2) ---
echo "Test 11: script_permissions auto-repair chmod +x"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  # Find a swain-owned script to chmod -x temporarily
  test_script=$(find "$REPO_ROOT/skills" -path '*/scripts/*.sh' -perm -u+x -not -name 'test-*' | head -1 || true)
  if [[ -n "$test_script" ]]; then
    chmod -x "$test_script"
    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    perm_status=$(echo "$output" | jq -r '.checks[] | select(.name == "script_permissions") | .status' 2>/dev/null || echo "missing")
    assert "script_permissions reports advisory after repair" "$([ "$perm_status" = "advisory" ] && echo 0 || echo 1)"
    assert "script_permissions restores execute bit" "$([ -x "$test_script" ] && echo 0 || echo 1)"
    # Idempotency
    output2=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    perm_status2=$(echo "$output2" | jq -r '.checks[] | select(.name == "script_permissions") | .status' 2>/dev/null || echo "missing")
    assert "script_permissions idempotent (ok on second run)" "$([ "$perm_status2" = "ok" ] && echo 0 || echo 1)"
  else
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — no suitable test script found)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — no suitable test script found)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — no suitable test script found)"
  fi
else
  assert "script_permissions reports advisory after repair" "1"
  assert "script_permissions restores execute bit" "1"
  assert "script_permissions idempotent (ok on second run)" "1"
fi

# --- Test 12: crash_debris git lock auto-repair (SPEC-222 AC5) ---
echo "Test 12: crash_debris removes stale .git/index.lock"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  # Resolve git dir (handles worktrees where .git is a file)
  if [[ -f "$REPO_ROOT/.git" ]]; then
    _git_dir=$(sed 's/^gitdir: //' "$REPO_ROOT/.git")
    [[ "$_git_dir" != /* ]] && _git_dir="$REPO_ROOT/$_git_dir"
  else
    _git_dir="$REPO_ROOT/.git"
  fi
  lock_file="$_git_dir/index.lock"

  if [[ ! -f "$lock_file" ]]; then
    # Create a fake stale lock (PID 99999999 is not running)
    echo "99999999" > "$lock_file"
    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    debris_status=$(echo "$output" | jq -r '.checks[] | select(.name == "crash_debris") | .status' 2>/dev/null || echo "missing")
    # Lock should be removed regardless of other debris in the environment
    assert "crash_debris removes git index.lock" "$([ ! -f "$lock_file" ] && echo 0 || echo 1)"
    # Status is advisory if lock was sole issue, warning if other debris also found
    assert "crash_debris reports advisory or warning (not ok/missing) after lock repair" \
      "$([ "$debris_status" = "advisory" ] || [ "$debris_status" = "warning" ] && echo 0 || echo 1)"
    # Idempotency: run again, lock should still be gone (not re-created)
    output2=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    lock_in_output2=$(echo "$output2" | jq -r '.checks[] | select(.name == "crash_debris") | .message // ""' 2>/dev/null || echo "")
    assert "crash_debris does not re-report removed lock on second run" \
      "$(echo "$lock_in_output2" | grep -qv 'index.lock' && echo 0 || echo 1)"
    rm -f "$lock_file" 2>/dev/null || true
  else
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — real index.lock exists, not safe to test)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — real index.lock exists, not safe to test)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — real index.lock exists, not safe to test)"
  fi
else
  assert "crash_debris removes git index.lock" "1"
  assert "crash_debris reports advisory or warning (not ok/missing) after lock repair" "1"
  assert "crash_debris does not re-report removed lock on second run" "1"
fi

# --- Test 13: governance stale block auto-repair (SPEC-222 AC4) ---
echo "Test 13: governance stale block auto-repair"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  # Find a context file with governance markers
  gov_file=$(grep -l "<!-- swain governance" "$REPO_ROOT/AGENTS.md" "$REPO_ROOT/CLAUDE.md" 2>/dev/null | head -1 || true)
  canonical=$(find "$REPO_ROOT/skills/swain-doctor/references" -name "AGENTS.content.md" 2>/dev/null | head -1 || true)
  if [[ -n "$gov_file" && -f "$canonical" ]]; then
    # Corrupt the governance block by inserting a sentinel line
    backup=$(mktemp)
    cp -f "$gov_file" "$backup"
    awk '
      /<!-- swain governance/{p=1; print; next}
      /<!-- end swain governance/{p=0}
      p==1 && !done{print "# SPEC-222-TEST-SENTINEL"; done=1; next}
      {print}
    ' "$gov_file" > "${gov_file}.tmp" && mv -f "${gov_file}.tmp" "$gov_file"

    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    gov_status=$(echo "$output" | jq -r '.checks[] | select(.name == "governance") | .status' 2>/dev/null || echo "missing")
    assert "governance stale block auto-repair reports advisory" "$([ "$gov_status" = "advisory" ] && echo 0 || echo 1)"
    # Sentinel should be gone after repair
    assert "governance block sentinel removed after repair" "$(! grep -q 'SPEC-222-TEST-SENTINEL' "$gov_file" && echo 0 || echo 1)"
    # Idempotency
    output2=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    gov_status2=$(echo "$output2" | jq -r '.checks[] | select(.name == "governance") | .status' 2>/dev/null || echo "missing")
    assert "governance idempotent (ok on second run)" "$([ "$gov_status2" = "ok" ] && echo 0 || echo 1)"
    # Restore
    cp -f "$backup" "$gov_file"
    rm -f "$backup"
  else
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — no governance file or canonical source found)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — no governance file or canonical source found)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — no governance file or canonical source found)"
  fi
else
  assert "governance stale block auto-repair reports advisory" "1"
  assert "governance block sentinel removed after repair" "1"
  assert "governance idempotent (ok on second run)" "1"
fi

# --- Test 14: commit_signing auto-repair (SPEC-222 AC3) ---
echo "Test 14: commit_signing auto-repair"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  current_gpgsign=$(git -C "$REPO_ROOT" config --local commit.gpgsign 2>/dev/null || echo "")
  signing_key_path="$HOME/.ssh/swain_signing"
  allowed_signers=$(git -C "$REPO_ROOT" config --global gpg.ssh.allowedSignersFile 2>/dev/null || echo "")
  key_available=false
  [[ -f "$signing_key_path" ]] && key_available=true
  [[ -n "$allowed_signers" && -f "$allowed_signers" ]] && key_available=true

  if [[ "$key_available" == "true" ]]; then
    # Disable signing, run doctor, expect advisory
    git -C "$REPO_ROOT" config --local commit.gpgsign false
    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    sign_status=$(echo "$output" | jq -r '.checks[] | select(.name == "commit_signing") | .status' 2>/dev/null || echo "missing")
    assert "commit_signing auto-configures when key present (advisory)" "$([ "$sign_status" = "advisory" ] && echo 0 || echo 1)"
    configured=$(git -C "$REPO_ROOT" config --local commit.gpgsign 2>/dev/null || echo "")
    assert "commit_signing sets gpgsign=true" "$([ "$configured" = "true" ] && echo 0 || echo 1)"
    # Restore
    if [[ -n "$current_gpgsign" ]]; then
      git -C "$REPO_ROOT" config --local commit.gpgsign "$current_gpgsign"
    else
      git -C "$REPO_ROOT" config --local --unset commit.gpgsign 2>/dev/null || true
    fi
  else
    # No key: doctor should warn, not configure
    git -C "$REPO_ROOT" config --local commit.gpgsign false 2>/dev/null || true
    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    sign_status=$(echo "$output" | jq -r '.checks[] | select(.name == "commit_signing") | .status' 2>/dev/null || echo "missing")
    assert "commit_signing warns when no key available" "$([ "$sign_status" = "warning" ] && echo 0 || echo 1)"
    # Restore
    if [[ -n "$current_gpgsign" ]]; then
      git -C "$REPO_ROOT" config --local commit.gpgsign "$current_gpgsign"
    else
      git -C "$REPO_ROOT" config --local --unset commit.gpgsign 2>/dev/null || true
    fi
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — no signing key to test auto-configure path)"
  fi
else
  assert "commit_signing auto-configures when key present (advisory)" "1"
  assert "commit_signing sets gpgsign=true" "1"
fi

# --- Test 15: artifact_indexes check is present ---
echo "Test 15: artifact_indexes check"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
  check_names=$(echo "$output" | jq -r '.checks[].name' 2>/dev/null || true)
  assert "artifact_indexes check present" "$(echo "$check_names" | grep -q "artifact_indexes" && echo 0 || echo 1)"
else
  assert "artifact_indexes check present" "1"
fi

# --- Test 16: artifact_indexes repairs stale index and is idempotent ---
echo "Test 16: artifact_indexes repairs stale index"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  index_file="$REPO_ROOT/docs/spec/list-spec.md"
  if [[ -f "$index_file" ]]; then
    backup=$(mktemp)
    cp -f "$index_file" "$backup"
    printf '\n<!-- SPEC-227-TEST-SENTINEL -->\n' >> "$index_file"

    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    idx_status=$(echo "$output" | jq -r '.checks[] | select(.name == "artifact_indexes") | .status' 2>/dev/null || echo "missing")
    assert "artifact_indexes reports advisory after repairing stale index" "$([ "$idx_status" = "advisory" ] && echo 0 || echo 1)"
    assert "artifact_indexes removes stale sentinel from list-spec.md" "$(! grep -q 'SPEC-227-TEST-SENTINEL' "$index_file" && echo 0 || echo 1)"

    output2=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    idx_status2=$(echo "$output2" | jq -r '.checks[] | select(.name == "artifact_indexes") | .status' 2>/dev/null || echo "missing")
    assert "artifact_indexes is idempotent after stale repair" "$([ "$idx_status2" = "ok" ] && echo 0 || echo 1)"

    cp -f "$backup" "$index_file"
    rm -f "$backup"
  else
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — docs/spec/list-spec.md not present)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — docs/spec/list-spec.md not present)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — docs/spec/list-spec.md not present)"
  fi
else
  assert "artifact_indexes reports advisory after repairing stale index" "1"
  assert "artifact_indexes removes stale sentinel from list-spec.md" "1"
  assert "artifact_indexes is idempotent after stale repair" "1"
fi

# --- Test 17: artifact_indexes recreates missing index ---
echo "Test 17: artifact_indexes recreates missing index"
if [[ -x "$DOCTOR_SCRIPT" ]]; then
  index_file="$REPO_ROOT/docs/spec/list-spec.md"
  if [[ -f "$index_file" ]]; then
    backup=$(mktemp)
    cp -f "$index_file" "$backup"
    rm -f "$index_file"

    output=$(bash "$DOCTOR_SCRIPT" 2>/dev/null || true)
    idx_status=$(echo "$output" | jq -r '.checks[] | select(.name == "artifact_indexes") | .status' 2>/dev/null || echo "missing")
    assert "artifact_indexes reports advisory after recreating missing index" "$([ "$idx_status" = "advisory" ] && echo 0 || echo 1)"
    assert "artifact_indexes recreates docs/spec/list-spec.md" "$([ -f "$index_file" ] && echo 0 || echo 1)"

    cp -f "$backup" "$index_file"
    rm -f "$backup"
  else
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — docs/spec/list-spec.md not present)"
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo "  PASS: (skipped — docs/spec/list-spec.md not present)"
  fi
else
  assert "artifact_indexes reports advisory after recreating missing index" "1"
  assert "artifact_indexes recreates docs/spec/list-spec.md" "1"
fi

# --- Summary ---
echo ""
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
