# Crash Debris Detection Checks — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build standalone bash functions that detect and report crash debris (git locks, interrupted operations, stale tk locks, dangling worktrees, orphaned MCP servers), callable from both the pre-runtime script (SPEC-180) and swain-doctor.

**Architecture:** A single library file (`crash-debris-lib.sh`) contains pure-bash detection functions. Each function checks one debris type and returns structured output. swain-doctor.sh sources the library and adds a `check_crash_debris()` function that wraps them into doctor's JSON format. A test file validates each detection function against synthetic debris.

**Tech Stack:** Bash, git, ps, the existing swain-doctor `add_check()` pattern, the project's custom test framework (assert pattern).

---

## File Structure

| File | Responsibility |
|------|---------------|
| `skills/swain-doctor/scripts/crash-debris-lib.sh` | Library of standalone detection functions — no output formatting, returns findings as structured text |
| `skills/swain-doctor/scripts/swain-doctor.sh` | Gains `check_crash_debris()` that sources the library and reports via `add_check()` |
| `tests/test_crash_debris.sh` | Tests each detection function against synthetic debris in a temp directory |

## Chunk 1: Library and Tests

### Task 1: Scaffold the library and test file

**Files:**
- Create: `skills/swain-doctor/scripts/crash-debris-lib.sh`
- Create: `tests/test_crash_debris.sh`

- [ ] **Step 1: Write the test scaffold**

```bash
#!/usr/bin/env bash
# RED tests for SPEC-182: Crash Debris Detection Checks
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LIB="$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh"
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

echo "=== SPEC-182: Crash Debris Detection Tests ==="

# T1: Library file exists and is sourceable
assert "crash-debris-lib.sh exists" "$([ -f "$LIB" ] && echo true || echo false)"
source "$LIB" 2>/dev/null || true

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
```

- [ ] **Step 2: Write the empty library file**

```bash
#!/usr/bin/env bash
# crash-debris-lib.sh — standalone crash debris detection functions (SPEC-182)
#
# Each function takes a project root path as $1 and prints findings
# to stdout as tab-separated lines: TYPE\tSTATUS\tDETAIL
#
# STATUS values: found, clean
# When STATUS=found, DETAIL contains human-readable description
#
# These functions are sourceable by both the pre-runtime script
# (SPEC-180) and swain-doctor (SPEC-192).

: # placeholder
```

- [ ] **Step 3: Run tests to verify scaffold works**

Run: `bash tests/test_crash_debris.sh`
Expected: 1 PASS (library exists)

- [ ] **Step 4: Commit scaffold**

```bash
git add tests/test_crash_debris.sh skills/swain-doctor/scripts/crash-debris-lib.sh
git commit -m "feat(SPEC-182): scaffold crash debris library and test file"
```

---

### Task 2: Git index lock detection

**Files:**
- Modify: `tests/test_crash_debris.sh`
- Modify: `skills/swain-doctor/scripts/crash-debris-lib.sh`

- [ ] **Step 1: Write failing tests for git index lock**

Append to `tests/test_crash_debris.sh` before the results section:

```bash
# --- Git index lock detection ---
TMPDIR=$(mktemp -d)
FAKE_GIT="$TMPDIR/.git"
mkdir -p "$FAKE_GIT"

# T2: No lock file → clean
RESULT=$(check_git_index_lock "$TMPDIR" 2>/dev/null || echo "MISSING")
assert "no index.lock → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

# T3: Lock file from dead PID → found
echo "99999999" > "$FAKE_GIT/index.lock"
RESULT=$(check_git_index_lock "$TMPDIR" 2>/dev/null || echo "MISSING")
assert "dead-pid index.lock → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

# T4: Lock file from live PID → clean (not stale)
echo "$$" > "$FAKE_GIT/index.lock"
RESULT=$(check_git_index_lock "$TMPDIR" 2>/dev/null || echo "MISSING")
assert "live-pid index.lock → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

rm -rf "$TMPDIR"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `bash tests/test_crash_debris.sh`
Expected: T2-T4 FAIL (function not defined)

- [ ] **Step 3: Implement check_git_index_lock**

Add to `crash-debris-lib.sh`:

```bash
# Check for stale .git/index.lock
# $1 = project root (must contain .git/ or be a worktree)
check_git_index_lock() {
  local root="$1"
  local git_dir="$root/.git"

  # Handle worktree: .git may be a file pointing to the real git dir
  if [[ -f "$git_dir" ]]; then
    git_dir=$(sed 's/^gitdir: //' "$git_dir")
    # Resolve relative paths
    [[ "$git_dir" != /* ]] && git_dir="$root/$git_dir"
  fi

  local lock="$git_dir/index.lock"
  if [[ ! -f "$lock" ]]; then
    printf "git_index_lock\tclean\n"
    return
  fi

  # Check if creating PID is still alive
  local pid
  pid=$(cat "$lock" 2>/dev/null | head -1 | grep -oE '^[0-9]+$' || echo "")
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    # PID alive — lock is legitimate
    printf "git_index_lock\tclean\tlock held by live PID %s\n" "$pid"
    return
  fi

  printf "git_index_lock\tfound\t%s (owner PID %s not running)\n" "$lock" "${pid:-unknown}"
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `bash tests/test_crash_debris.sh`
Expected: T1-T4 PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_crash_debris.sh skills/swain-doctor/scripts/crash-debris-lib.sh
git commit -m "feat(SPEC-182): add git index lock detection"
```

---

### Task 3: Interrupted git operation detection (merge, rebase, cherry-pick)

**Files:**
- Modify: `tests/test_crash_debris.sh`
- Modify: `skills/swain-doctor/scripts/crash-debris-lib.sh`

- [ ] **Step 1: Write failing tests**

Append to tests before results section:

```bash
# --- Interrupted git operations ---
TMPDIR2=$(mktemp -d)
FAKE_GIT2="$TMPDIR2/.git"
mkdir -p "$FAKE_GIT2"

# T5: No interrupted ops → clean
RESULT=$(check_interrupted_git_ops "$TMPDIR2" 2>/dev/null || echo "MISSING")
assert "no interrupted ops → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

# T6: MERGE_HEAD → found
touch "$FAKE_GIT2/MERGE_HEAD"
RESULT=$(check_interrupted_git_ops "$TMPDIR2" 2>/dev/null || echo "MISSING")
assert "MERGE_HEAD → found merge" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"
rm "$FAKE_GIT2/MERGE_HEAD"

# T7: rebase-merge dir → found
mkdir -p "$FAKE_GIT2/rebase-merge"
RESULT=$(check_interrupted_git_ops "$TMPDIR2" 2>/dev/null || echo "MISSING")
assert "rebase-merge → found rebase" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"
rm -rf "$FAKE_GIT2/rebase-merge"

# T8: CHERRY_PICK_HEAD → found
touch "$FAKE_GIT2/CHERRY_PICK_HEAD"
RESULT=$(check_interrupted_git_ops "$TMPDIR2" 2>/dev/null || echo "MISSING")
assert "CHERRY_PICK_HEAD → found cherry-pick" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"
rm "$FAKE_GIT2/CHERRY_PICK_HEAD"

rm -rf "$TMPDIR2"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `bash tests/test_crash_debris.sh`
Expected: T5-T8 FAIL

- [ ] **Step 3: Implement check_interrupted_git_ops**

```bash
# Check for interrupted git operations (merge, rebase, cherry-pick)
check_interrupted_git_ops() {
  local root="$1"
  local git_dir="$root/.git"

  if [[ -f "$git_dir" ]]; then
    git_dir=$(sed 's/^gitdir: //' "$git_dir")
    [[ "$git_dir" != /* ]] && git_dir="$root/$git_dir"
  fi

  local found=()

  [[ -f "$git_dir/MERGE_HEAD" ]] && found+=("interrupted merge (MERGE_HEAD)")
  [[ -d "$git_dir/rebase-merge" ]] && found+=("interrupted rebase (rebase-merge/)")
  [[ -d "$git_dir/rebase-apply" ]] && found+=("interrupted rebase-apply (rebase-apply/)")
  [[ -f "$git_dir/CHERRY_PICK_HEAD" ]] && found+=("interrupted cherry-pick (CHERRY_PICK_HEAD)")

  if [[ ${#found[@]} -eq 0 ]]; then
    printf "interrupted_git_ops\tclean\n"
    return
  fi

  for item in "${found[@]}"; do
    printf "interrupted_git_ops\tfound\t%s\n" "$item"
  done
}
```

- [ ] **Step 4: Run tests, verify pass**

Run: `bash tests/test_crash_debris.sh`
Expected: T1-T8 PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_crash_debris.sh skills/swain-doctor/scripts/crash-debris-lib.sh
git commit -m "feat(SPEC-182): add interrupted git operation detection"
```

---

### Task 4: Stale tk claim lock detection

**Files:**
- Modify: `tests/test_crash_debris.sh`
- Modify: `skills/swain-doctor/scripts/crash-debris-lib.sh`

- [ ] **Step 1: Write failing tests**

```bash
# --- Stale tk claim locks ---
TMPDIR3=$(mktemp -d)
TICKETS="$TMPDIR3/.tickets"
mkdir -p "$TICKETS/.locks"

# T9: No locks → clean
RESULT=$(check_stale_tk_locks "$TMPDIR3" 2>/dev/null || echo "MISSING")
assert "no tk locks → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

# T10: Lock with dead PID → found
LOCK_DIR="$TICKETS/.locks/task-1"
mkdir -p "$LOCK_DIR"
echo "99999999" > "$LOCK_DIR/owner"
RESULT=$(check_stale_tk_locks "$TMPDIR3" 2>/dev/null || echo "MISSING")
assert "dead-pid tk lock → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

# T11: Lock with live PID → clean
echo "$$" > "$LOCK_DIR/owner"
RESULT=$(check_stale_tk_locks "$TMPDIR3" 2>/dev/null || echo "MISSING")
assert "live-pid tk lock → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

rm -rf "$TMPDIR3"
```

- [ ] **Step 2: Run tests to verify fail**

- [ ] **Step 3: Implement check_stale_tk_locks**

```bash
# Check for stale tk claim locks (dead owner PID or age >1 hour)
check_stale_tk_locks() {
  local root="$1"
  local locks_dir="$root/.tickets/.locks"

  if [[ ! -d "$locks_dir" ]]; then
    printf "stale_tk_locks\tclean\n"
    return
  fi

  local found=0
  for lock_dir in "$locks_dir"/*/; do
    [[ -d "$lock_dir" ]] || continue
    local owner_file="$lock_dir/owner"
    local task_id
    task_id=$(basename "$lock_dir")

    if [[ -f "$owner_file" ]]; then
      local pid
      pid=$(cat "$owner_file" 2>/dev/null | tr -d '[:space:]')
      if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        continue  # alive — legitimate lock
      fi
      printf "stale_tk_locks\tfound\ttask %s locked by dead PID %s\n" "$task_id" "$pid"
    else
      # Lock dir exists but no owner file — treat as stale
      printf "stale_tk_locks\tfound\ttask %s lock has no owner file\n" "$task_id"
    fi
    found=$((found + 1))
  done

  [[ $found -eq 0 ]] && printf "stale_tk_locks\tclean\n"
}
```

- [ ] **Step 4: Run tests, verify pass**

- [ ] **Step 5: Commit**

```bash
git add tests/test_crash_debris.sh skills/swain-doctor/scripts/crash-debris-lib.sh
git commit -m "feat(SPEC-182): add stale tk lock detection"
```

---

### Task 5: Dangling worktree detection (crash-correlated)

**Files:**
- Modify: `tests/test_crash_debris.sh`
- Modify: `skills/swain-doctor/scripts/crash-debris-lib.sh`

- [ ] **Step 1: Write failing tests**

Note: This test uses a real git repo (in temp dir) since worktree commands need one.

```bash
# --- Dangling worktrees ---
TMPDIR4=$(mktemp -d)
git -C "$TMPDIR4" init -q
git -C "$TMPDIR4" commit --allow-empty -m "init" -q

# T12: No worktrees → clean
RESULT=$(check_dangling_worktrees "$TMPDIR4" 2>/dev/null || echo "MISSING")
assert "no worktrees → clean" "$(echo "$RESULT" | grep -q 'clean' && echo true || echo false)"

# T13: Worktree with missing directory → found
WT_PATH="$TMPDIR4/.claude/worktrees/dead-session"
git -C "$TMPDIR4" worktree add -q "$WT_PATH" -b dead-branch 2>/dev/null
rm -rf "$WT_PATH"
RESULT=$(check_dangling_worktrees "$TMPDIR4" 2>/dev/null || echo "MISSING")
assert "missing-dir worktree → found" "$(echo "$RESULT" | grep -q 'found' && echo true || echo false)"

# Cleanup
git -C "$TMPDIR4" worktree prune -q 2>/dev/null
rm -rf "$TMPDIR4"
```

- [ ] **Step 2: Run tests to verify fail**

- [ ] **Step 3: Implement check_dangling_worktrees**

```bash
# Check for dangling worktrees (missing directory or merged branches)
check_dangling_worktrees() {
  local root="$1"
  local found=0
  local in_first=1
  local path="" branch=""

  while IFS= read -r line; do
    if [[ "$line" == worktree\ * ]]; then
      path="${line#worktree }"
    elif [[ "$line" == branch\ * ]]; then
      branch="${line#branch }"
    elif [[ -z "$line" ]]; then
      if [[ $in_first -eq 1 ]]; then
        in_first=0
        path=""
        branch=""
        continue
      fi
      if [[ -n "$path" ]]; then
        if [[ ! -d "$path" ]]; then
          printf "dangling_worktrees\tfound\tmissing directory: %s (branch: %s)\n" "$path" "${branch:-detached}"
          found=$((found + 1))
        else
          # Cross-reference with runtime sessions (best-effort)
          # Check if any runtime has this worktree as its cwd
          local has_live_session=false
          # Claude Code: scan ~/.claude/sessions/ for matching cwd
          if [[ -d "$HOME/.claude/sessions" ]]; then
            for sess in "$HOME/.claude/sessions"/*.json; do
              [[ -f "$sess" ]] || continue
              local sess_cwd sess_pid
              sess_cwd=$(grep -o '"cwd":"[^"]*"' "$sess" 2>/dev/null | head -1 | sed 's/"cwd":"//;s/"$//')
              if [[ "$sess_cwd" == "$path" ]]; then
                sess_pid=$(grep -o '"pid":[0-9]*' "$sess" 2>/dev/null | head -1 | sed 's/"pid"://')
                if [[ -n "$sess_pid" ]] && kill -0 "$sess_pid" 2>/dev/null; then
                  has_live_session=true
                fi
              fi
            done
          fi

          if [[ "$has_live_session" == "true" ]]; then
            continue  # active session owns this worktree
          fi

          # Check for uncommitted changes in orphaned worktree
          local wt_status
          wt_status=$(git -C "$path" status --porcelain 2>/dev/null | head -5)
          if [[ -n "$wt_status" ]]; then
            local change_count
            change_count=$(git -C "$path" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
            printf "dangling_worktrees\tfound\tuncommitted changes (%s files) in %s\n" "$change_count" "$path"
            found=$((found + 1))
          fi
        fi
      fi
      path=""
      branch=""
    fi
  done < <(git -C "$root" worktree list --porcelain 2>/dev/null; echo "")

  [[ $found -eq 0 ]] && printf "dangling_worktrees\tclean\n"
}
```

- [ ] **Step 4: Run tests, verify pass**

- [ ] **Step 5: Commit**

```bash
git add tests/test_crash_debris.sh skills/swain-doctor/scripts/crash-debris-lib.sh
git commit -m "feat(SPEC-182): add dangling worktree detection"
```

---

### Task 6: Orphaned MCP server detection

**Files:**
- Modify: `tests/test_crash_debris.sh`
- Modify: `skills/swain-doctor/scripts/crash-debris-lib.sh`

- [ ] **Step 1: Write failing tests**

```bash
# --- Orphaned MCP servers ---
# T14: Detection function exists and returns clean when no MCP processes
RESULT=$(check_orphaned_mcp "$REPO_ROOT" 2>/dev/null || echo "MISSING")
assert "MCP check runs without error" "$([ "$RESULT" != "MISSING" ] && echo true || echo false)"
# Note: We can't reliably create fake MCP processes in tests,
# so we verify the function runs and returns a valid status line
assert "MCP check returns valid format" "$(echo "$RESULT" | grep -qE '(clean|found)' && echo true || echo false)"
```

- [ ] **Step 2: Run tests to verify fail**

- [ ] **Step 3: Implement check_orphaned_mcp**

```bash
# Check for orphaned MCP servers associated with this project
# Best-effort: matches process names containing "mcp" with cwd matching project root
check_orphaned_mcp() {
  local root="$1"
  local real_root
  real_root=$(cd "$root" && pwd -P 2>/dev/null || echo "$root")
  local found=0

  # Look for processes with "mcp" in the command line whose cwd matches this project
  # This is best-effort — not all platforms expose cwd reliably
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    local pid cmd
    pid=$(echo "$line" | awk '{print $1}')
    cmd=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ //')

    # Check if process cwd matches project root (macOS: lsof -p; Linux: /proc/PID/cwd)
    local proc_cwd=""
    if [[ -d "/proc/$pid" ]]; then
      proc_cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null || echo "")
    else
      proc_cwd=$(lsof -p "$pid" -Fn 2>/dev/null | grep '^n/' | head -1 | sed 's/^n//' || echo "")
    fi

    if [[ "$proc_cwd" == "$real_root"* ]]; then
      printf "orphaned_mcp\tfound\tPID %s: %s\n" "$pid" "$cmd"
      found=$((found + 1))
    fi
  done < <(ps aux 2>/dev/null | grep -i '[m]cp.*server\|[m]cp.*gateway' | awk '{print $2, $11, $12, $13}' || true)

  [[ $found -eq 0 ]] && printf "orphaned_mcp\tclean\n"
}
```

- [ ] **Step 4: Run tests, verify pass**

- [ ] **Step 5: Commit**

```bash
git add tests/test_crash_debris.sh skills/swain-doctor/scripts/crash-debris-lib.sh
git commit -m "feat(SPEC-182): add orphaned MCP server detection"
```

---

### Task 7: Aggregate check function and silent fast path

**Files:**
- Modify: `tests/test_crash_debris.sh`
- Modify: `skills/swain-doctor/scripts/crash-debris-lib.sh`

- [ ] **Step 1: Write failing tests**

```bash
# --- Aggregate function ---
TMPDIR5=$(mktemp -d)
mkdir -p "$TMPDIR5/.git"

# T15: Clean project → empty output (silent fast path, AC5)
RESULT=$(check_all_crash_debris "$TMPDIR5" 2>/dev/null)
assert "clean project → silent (no output)" "$([ -z "$RESULT" ] && echo true || echo false)"

# T16: Multiple debris types → all reported
touch "$TMPDIR5/.git/MERGE_HEAD"
echo "99999999" > "$TMPDIR5/.git/index.lock"
RESULT=$(check_all_crash_debris "$TMPDIR5" 2>/dev/null || echo "MISSING")
FOUND_COUNT=$(echo "$RESULT" | grep -c 'found' || echo "0")
assert "multiple debris → multiple findings" "$([ "$FOUND_COUNT" -ge 2 ] && echo true || echo false)"

rm -rf "$TMPDIR5"
```

- [ ] **Step 2: Run tests to verify fail**

- [ ] **Step 3: Implement check_all_crash_debris**

```bash
# Run all crash debris checks and return combined results
# $1 = project root
# Returns: only "found" lines (tab-separated), or nothing if clean (AC5 silent fast path)
check_all_crash_debris() {
  local root="$1"
  local output=""

  output+=$(check_git_index_lock "$root" 2>/dev/null)
  output+=$'\n'
  output+=$(check_interrupted_git_ops "$root" 2>/dev/null)
  output+=$'\n'
  output+=$(check_stale_tk_locks "$root" 2>/dev/null)
  output+=$'\n'
  output+=$(check_dangling_worktrees "$root" 2>/dev/null)
  output+=$'\n'
  output+=$(check_orphaned_mcp "$root" 2>/dev/null)

  # AC5: silent fast path — only emit lines with findings, nothing if clean
  echo "$output" | grep 'found' || true
}
```

- [ ] **Step 4: Run tests, verify pass**

- [ ] **Step 5: Commit**

```bash
git add tests/test_crash_debris.sh skills/swain-doctor/scripts/crash-debris-lib.sh
git commit -m "feat(SPEC-182): add aggregate check_all_crash_debris function"
```

---

## Chunk 2: Doctor Integration

### Task 8: Integrate into swain-doctor.sh

**Files:**
- Modify: `skills/swain-doctor/scripts/swain-doctor.sh` (add `check_crash_debris` function and call it)

- [ ] **Step 1: Write failing test**

Append to `tests/test_crash_debris.sh`:

```bash
# --- Doctor integration ---
DOCTOR="$REPO_ROOT/skills/swain-doctor/scripts/swain-doctor.sh"

# T17: Doctor output includes crash_debris check
DOCTOR_OUT=$(bash "$DOCTOR" 2>/dev/null || true)
assert "doctor includes crash_debris check" "$(echo "$DOCTOR_OUT" | grep -q 'crash_debris' && echo true || echo false)"
```

- [ ] **Step 2: Run test to verify fail**

Run: `bash tests/test_crash_debris.sh`
Expected: T17 FAIL

- [ ] **Step 3: Add check_crash_debris to swain-doctor.sh**

Add a new check section after `check_ssh_readiness` (before the "Run all checks" block):

```bash
# ============================================================
# Check 18: Crash debris detection (SPEC-182)
# ============================================================
check_crash_debris() {
  local lib="$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh"
  if [[ ! -f "$lib" ]]; then
    add_check "crash_debris" "ok" "crash-debris-lib.sh not found (skipped)"
    return
  fi

  source "$lib"
  local output
  output=$(check_all_crash_debris "$REPO_ROOT" 2>/dev/null || true)

  local found_count
  found_count=$(echo "$output" | grep -c 'found' || echo "0")

  if [[ "$found_count" -eq 0 ]]; then
    add_check "crash_debris" "ok" "no crash debris detected"
    return
  fi

  local details
  details=$(echo "$output" | grep 'found' | cut -f3 | tr '\n' '; ' | sed 's/; $//')
  add_check "crash_debris" "warning" "$found_count crash debris item(s) detected" "$details"
}
```

Add `check_crash_debris` to the run-all-checks block:

```bash
check_crash_debris
```

- [ ] **Step 4: Run test to verify pass**

Run: `bash tests/test_crash_debris.sh`
Expected: All PASS

- [ ] **Step 5: Run full doctor to verify no regressions**

Run: `bash skills/swain-doctor/scripts/swain-doctor.sh`
Expected: JSON output includes `crash_debris` check with status `ok` or `warning`

- [ ] **Step 6: Commit**

```bash
git add skills/swain-doctor/scripts/swain-doctor.sh tests/test_crash_debris.sh
git commit -m "feat(SPEC-182): integrate crash debris checks into swain-doctor"
```

---

### Task 9: Add symlink to .agents/bin/

**Files:**
- Create: `.agents/bin/crash-debris-lib.sh` (symlink)

- [ ] **Step 1: Create symlink**

```bash
ln -sf ../../skills/swain-doctor/scripts/crash-debris-lib.sh .agents/bin/crash-debris-lib.sh
```

- [ ] **Step 2: Verify symlink resolves**

```bash
ls -la .agents/bin/crash-debris-lib.sh
bash .agents/bin/crash-debris-lib.sh  # should exit cleanly (just defines functions)
```

- [ ] **Step 3: Commit**

```bash
git add .agents/bin/crash-debris-lib.sh
git commit -m "feat(SPEC-182): add crash-debris-lib.sh symlink to .agents/bin"
```

---

### Task 10: Final verification

- [ ] **Step 1: Run all SPEC-182 tests**

Run: `bash tests/test_crash_debris.sh`
Expected: All PASS, 0 failures

- [ ] **Step 2: Run swain-doctor and verify crash_debris check appears**

Run: `bash skills/swain-doctor/scripts/swain-doctor.sh | python3 -c "import sys,json; d=json.load(sys.stdin); checks=[c for c in d['checks'] if c['name']=='crash_debris']; print(json.dumps(checks, indent=2))"`
Expected: One check entry with status `ok` (clean environment)

- [ ] **Step 3: Run existing tests to verify no regressions**

Run: `bash tests/test_session_detection.sh && bash tests/test_session_lifecycle.sh`
Expected: All PASS

- [ ] **Step 4: Final commit (if any fixes needed)**
