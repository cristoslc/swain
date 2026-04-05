# swain-test.sh Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `swain-test.sh` script that detects and runs integration tests, then emits structured smoke instructions for agent consumption.

**Architecture:** Single bash script with four stages: (1) detect test command by convention or config, (2) run integration tests with timeout, (3) detect changed files and resolve artifact/skill paths, (4) emit structured output sections. Each stage is a function for testability.

**Tech Stack:** Bash, jq, bats-core (testing)

---

## File Structure

| File | Responsibility |
|------|---------------|
| `skills/swain-test/scripts/swain-test.sh` | Main script — test detection, execution, structured output |
| `skills/swain-test/scripts/run-specs.sh` | BDD suite runner (relocated from `spec/run`) |
| `skills/swain-test/SKILL.md` | Stub skill file (full implementation is SPEC-221) |
| `spec/run` | Symlink → `../skills/swain-test/scripts/run-specs.sh` |
| `.agents/bin/swain-test.sh` | Symlink → `../../skills/swain-test/scripts/swain-test.sh` |
| `spec/test-gate/swain_test.bats` | BDD specs for swain-test.sh |

---

## Chunk 1: Skeleton and test infrastructure

### Task 1: Create skill directory and relocate spec runner

**Files:**
- Create: `skills/swain-test/SKILL.md`
- Move: `spec/run` → `skills/swain-test/scripts/run-specs.sh`
- Create: `spec/run` (symlink)
- Create: `.agents/bin/swain-test.sh` (symlink, to be filled)
- Create: `spec/test-gate/` (directory)

- [ ] **Step 1: Create skill directory structure**

```bash
mkdir -p skills/swain-test/scripts
```

- [ ] **Step 2: Create stub SKILL.md**

```markdown
---
name: swain-test
description: Test gate for swain-sync and swain-release — runs integration tests and emits smoke instructions
version: 0.1.0
---

# swain-test

Automated test gate. See SPEC-220 (script) and SPEC-221 (skill orchestration).

Implementation in progress.
```

- [ ] **Step 3: Move spec/run to skills/swain-test/scripts/run-specs.sh**

```bash
mv spec/run skills/swain-test/scripts/run-specs.sh
chmod +x skills/swain-test/scripts/run-specs.sh
```

- [ ] **Step 4: Create symlink at spec/run**

```bash
ln -sf ../skills/swain-test/scripts/run-specs.sh spec/run
```

- [ ] **Step 5: Verify spec runner still works via symlink**

```bash
spec/run --tap 2>&1 | tail -3
```

Expected: `84 tests, 0 failures` (or similar — all existing tests pass)

- [ ] **Step 6: Create swain-test.sh symlink in .agents/bin/**

```bash
# Relative path from .agents/bin/ to skills/swain-test/scripts/
ln -sf ../../skills/swain-test/scripts/swain-test.sh .agents/bin/swain-test.sh
```

- [ ] **Step 7: Create test-gate spec directory**

```bash
mkdir -p spec/test-gate
```

- [ ] **Step 8: Commit skeleton**

```bash
git add skills/swain-test/ spec/run spec/test-gate .agents/bin/swain-test.sh
git commit -m "feat(swain-test): create skill directory, relocate spec runner

SPEC-220 skeleton — skill dir, run-specs.sh relocation, symlinks."
```

---

### Task 2: Write failing BDD specs for test command detection

The script's core behavior is detecting which test command to use. Write the specs first (RED).

**Files:**
- Create: `spec/test-gate/swain_test.bats`

- [ ] **Step 1: Write the BDD spec file**

This file tests the test command detection logic from SPEC-220. Each test creates a sandbox project with the relevant marker file and verifies the script detects the right command.

```bash
#!/usr/bin/env bats
# swain-test.sh behavioral specs (SPEC-220)
#
# The test gate script detects project test commands, runs them,
# and emits structured output for agent consumption.

load '../support/setup'

# Each test gets its own sandbox
setup() {
  export TEST_SANDBOX
  TEST_SANDBOX="$(create_test_sandbox)"
  scaffold_swain_project "$TEST_SANDBOX"
  cd "$TEST_SANDBOX" || fail "cannot cd to sandbox"
}

teardown() {
  destroy_test_sandbox "$TEST_SANDBOX"
}

# ─── Test command detection ───

@test "detects npm test from package.json" {
  echo '{"name":"test","scripts":{"test":"echo pass"}}' > package.json
  git add -A && git commit -q -m "add package.json"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "command: npm test"
  assert_output --partial "status: PASS"
}

@test "detects cargo test from Cargo.toml" {
  echo '[package]' > Cargo.toml
  echo 'name = "test"' >> Cargo.toml
  git add -A && git commit -q -m "add Cargo.toml"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  # Will either PASS (if cargo is installed) or SKIP (if not)
  assert_output --partial "## INTEGRATION"
}

@test "detects pytest from pyproject.toml with tool.pytest section" {
  cat > pyproject.toml <<'TOML'
[tool.pytest.ini_options]
testpaths = ["tests"]
TOML
  git add -A && git commit -q -m "add pyproject.toml"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## INTEGRATION"
}

@test "detects go test from go.mod" {
  echo 'module test' > go.mod
  git add -A && git commit -q -m "add go.mod"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## INTEGRATION"
}

@test "detects make test from Makefile with test target" {
  printf 'test:\n\techo pass\n' > Makefile
  git add -A && git commit -q -m "add Makefile"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## INTEGRATION"
}

@test "uses testing.json command when present" {
  mkdir -p .agents
  cat > .agents/testing.json <<'JSON'
{"integration":{"command":"echo custom-test-pass","timeout":300}}
JSON
  git add -A && git commit -q -m "add testing.json"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "command: echo custom-test-pass"
  assert_output --partial "status: PASS"
}

@test "skips integration when no test command detected" {
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "status: SKIP"
}

# ─── Exit codes ───

@test "exits 0 when tests pass" {
  echo '{"name":"test","scripts":{"test":"echo pass"}}' > package.json
  git add -A && git commit -q -m "add"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
}

@test "exits 1 when tests fail" {
  echo '{"name":"test","scripts":{"test":"exit 1"}}' > package.json
  git add -A && git commit -q -m "add"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_failure
  assert_output --partial "status: FAIL"
}

# ─── Structured output sections ───

@test "output contains ## INTEGRATION section" {
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## INTEGRATION"
}

@test "output contains ## FALLBACK when no artifacts or skills detected" {
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## FALLBACK"
}

# ─── Artifact resolution ───

@test "--artifacts flag resolves spec paths" {
  create_artifact "." "spec" "SPEC-215" "Consumer Harness"
  git add -A && git commit -q -m "add spec"
  run bash "$AGENTS_BIN/swain-test.sh" --artifacts SPEC-215
  assert_success
  assert_output --partial "## ARTIFACTS"
  assert_output --partial "SPEC-215"
}

# ─── Skill change detection ───

@test "detects changed skill files" {
  mkdir -p skills/swain-test
  echo "# changed" > skills/swain-test/SKILL.md
  git add -A && git commit -q -m "change skill"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## SKILLS"
  assert_output --partial "detected: true"
}

# ─── Changed file detection ───

@test "uses trunk diff when in worktree branch" {
  git checkout -b worktree-test-branch
  echo "new" > newfile.txt
  git add -A && git commit -q -m "worktree change"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  # Should detect newfile.txt as changed
  assert_output --partial "## INTEGRATION"
}

@test "uses HEAD~1 diff when on trunk/main" {
  echo "change" > another.txt
  git add -A && git commit -q -m "trunk change"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## INTEGRATION"
}

# ─── Smoke section from testing.json ───

@test "emits SMOKE section from testing.json smoke entries" {
  mkdir -p .agents
  cat > .agents/testing.json <<'JSON'
{"smoke":["check health endpoint","verify login flow"]}
JSON
  git add -A && git commit -q -m "add smoke"
  run bash "$AGENTS_BIN/swain-test.sh"
  assert_success
  assert_output --partial "## SMOKE"
  assert_output --partial "check health endpoint"
}
```

- [ ] **Step 2: Run the specs to verify they fail (RED)**

```bash
bats spec/test-gate/swain_test.bats 2>&1 | tail -5
```

Expected: All tests FAIL (swain-test.sh doesn't exist yet)

- [ ] **Step 3: Commit RED specs**

```bash
git add spec/test-gate/swain_test.bats
git commit -m "test(swain-test): RED specs for SPEC-220 test command detection

17 behavioral specs covering detection, exit codes, structured output,
artifact resolution, skill detection, and smoke sections."
```

---

## Chunk 2: Implementation (GREEN)

### Task 3: Implement swain-test.sh — core script

**Files:**
- Create: `skills/swain-test/scripts/swain-test.sh`

- [ ] **Step 1: Write the full script**

The script has four stages implemented as functions:

1. `detect_test_command` — checks testing.json, then convention files
2. `run_integration` — executes the detected command with timeout
3. `detect_context` — finds changed files, resolves artifacts and skills
4. `emit_output` — writes structured sections to stdout

```bash
#!/usr/bin/env bash
# swain-test.sh — SPEC-220: Integration test gate and smoke instruction assembly
#
# Detects project test commands by convention or config, runs them,
# and emits structured output for agent consumption.
#
# Usage:
#   swain-test.sh [--artifacts SPEC-NNN,SPEC-NNN]
#
# Exit codes:
#   0 — integration tests passed (or skipped); smoke instructions on stdout
#   1 — integration tests failed; failure details on stdout

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# ─── Argument parsing ───
ARTIFACT_IDS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --artifacts)
      IFS=',' read -ra ARTIFACT_IDS <<< "$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# ─── Stage 1: Detect test command ───

detect_test_command() {
  local cmd="" timeout=120

  # 1. Check .agents/testing.json
  if [[ -f "$REPO_ROOT/.agents/testing.json" ]] && command -v jq &>/dev/null; then
    local json_cmd json_timeout
    json_cmd=$(jq -r '.integration.command // empty' "$REPO_ROOT/.agents/testing.json" 2>/dev/null)
    json_timeout=$(jq -r '.integration.timeout // empty' "$REPO_ROOT/.agents/testing.json" 2>/dev/null)
    if [[ -n "$json_cmd" ]]; then
      cmd="$json_cmd"
      [[ -n "$json_timeout" ]] && timeout="$json_timeout"
      echo "$cmd|$timeout"
      return 0
    fi
  fi

  # 2. Convention detection (in priority order)
  if [[ -f "$REPO_ROOT/package.json" ]]; then
    cmd="npm test"
  elif [[ -f "$REPO_ROOT/Cargo.toml" ]]; then
    cmd="cargo test"
  elif [[ -f "$REPO_ROOT/pyproject.toml" ]] && grep -q '\[tool.pytest' "$REPO_ROOT/pyproject.toml" 2>/dev/null; then
    cmd="pytest"
  elif [[ -f "$REPO_ROOT/requirements.txt" ]] && grep -q 'pytest' "$REPO_ROOT/requirements.txt" 2>/dev/null; then
    cmd="pytest"
  elif [[ -f "$REPO_ROOT/go.mod" ]]; then
    cmd="go test ./..."
  elif [[ -f "$REPO_ROOT/Makefile" ]] && grep -q '^test:' "$REPO_ROOT/Makefile" 2>/dev/null; then
    cmd="make test"
  fi

  if [[ -n "$cmd" ]]; then
    echo "$cmd|$timeout"
    return 0
  fi

  return 1
}

# ─── Stage 2: Run integration tests ───

run_integration() {
  local cmd="$1" timeout="$2"
  local start_time end_time duration exit_code output

  start_time=$(date +%s)

  # Run with timeout
  if command -v timeout &>/dev/null; then
    output=$(cd "$REPO_ROOT" && timeout "$timeout" bash -c "$cmd" 2>&1) || true
    exit_code=$?
  elif command -v gtimeout &>/dev/null; then
    output=$(cd "$REPO_ROOT" && gtimeout "$timeout" bash -c "$cmd" 2>&1) || true
    exit_code=$?
  else
    output=$(cd "$REPO_ROOT" && bash -c "$cmd" 2>&1) || true
    exit_code=$?
  fi

  end_time=$(date +%s)
  duration=$((end_time - start_time))

  echo "$exit_code|${duration}s|$output"
}

# ─── Stage 3: Detect context ───

detect_changed_files() {
  local branch
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

  local changed=""

  # Determine diff strategy
  if [[ "$branch" != "trunk" && "$branch" != "main" && "$branch" != "master" ]]; then
    # Worktree: diff against trunk (or main/master)
    local base=""
    for candidate in trunk main master; do
      if git rev-parse --verify "$candidate" &>/dev/null; then
        base="$candidate"
        break
      fi
    done
    if [[ -n "$base" ]]; then
      changed=$(git diff --name-only "$base..HEAD" 2>/dev/null || echo "")
    fi
  else
    # On trunk: diff against previous commit
    changed=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || echo "")
  fi

  # Add unstaged changes
  local unstaged
  unstaged=$(git diff --name-only 2>/dev/null || echo "")
  if [[ -n "$unstaged" ]]; then
    changed=$(printf '%s\n%s' "$changed" "$unstaged" | sort -u)
  fi

  echo "$changed"
}

resolve_artifact_paths() {
  local paths=""
  for id in "${ARTIFACT_IDS[@]}"; do
    [[ -z "$id" ]] && continue
    # Extract type prefix and find the folder
    local type_lower
    type_lower=$(echo "$id" | sed 's/-.*//' | tr '[:upper:]' '[:lower:]')
    # Map type to directory
    case "$type_lower" in
      spec)       type_lower="spec" ;;
      epic)       type_lower="epic" ;;
      spike)      type_lower="research" ;;
      *)          ;; # use as-is
    esac
    # Search for the artifact folder
    local found
    found=$(find "$REPO_ROOT/docs/$type_lower" -type d -name "*${id}*" 2>/dev/null | head -1)
    if [[ -n "$found" ]]; then
      # Find the .md file inside
      local md_file
      md_file=$(find "$found" -maxdepth 1 -name "*.md" -type f 2>/dev/null | head -1)
      if [[ -n "$md_file" ]]; then
        paths="${paths}  - ${md_file#"$REPO_ROOT/"}\n"
      fi
    fi
  done
  echo -e "$paths"
}

detect_skill_changes() {
  local changed="$1"
  local skill_files=""
  local detected="false"

  while IFS= read -r file; do
    if [[ "$file" == skills/* ]] || [[ "$file" == .agents/skills/* ]] || [[ "$file" == .claude/skills/* ]]; then
      detected="true"
      skill_files="${skill_files}  - ${file}\n"
    fi
  done <<< "$changed"

  echo "${detected}|$(echo -e "$skill_files")"
}

# ─── Stage 4: Emit output ───

emit_output() {
  local integration_status="$1"
  local integration_cmd="$2"
  local integration_duration="$3"
  local integration_output="$4"
  local artifact_paths="$5"
  local skill_detected="$6"
  local skill_files="$7"
  local smoke_items="$8"

  # INTEGRATION section
  echo "## INTEGRATION"
  echo "status: $integration_status"
  if [[ -n "$integration_cmd" ]]; then
    echo "command: $integration_cmd"
  fi
  if [[ -n "$integration_duration" ]]; then
    echo "duration: $integration_duration"
  fi
  if [[ "$integration_status" == "FAIL" ]]; then
    echo "output: $(echo "$integration_output" | tail -50)"
  fi
  echo ""

  local has_context=false

  # ARTIFACTS section
  if [[ -n "$artifact_paths" ]]; then
    has_context=true
    echo "## ARTIFACTS"
    echo "paths:"
    echo -n "$artifact_paths"
    echo ""
  fi

  # SKILLS section
  if [[ "$skill_detected" == "true" ]]; then
    has_context=true
    echo "## SKILLS"
    echo "detected: true"
    echo "changed_skill_files:"
    echo -n "$skill_files"
    echo ""
  fi

  # SMOKE section (from testing.json)
  if [[ -n "$smoke_items" ]]; then
    has_context=true
    echo "## SMOKE"
    echo "$smoke_items"
    echo ""
  fi

  # FALLBACK section (when nothing else was emitted)
  if [[ "$has_context" == "false" ]]; then
    echo "## FALLBACK"
    echo "Describe what you changed, stand up the affected component, and exercise the happy path. Report what you did and what you observed."
  fi
}

# ─── Main ───

# Stage 1: Detect
DETECTION=""
if DETECTION=$(detect_test_command); then
  IFS='|' read -r TEST_CMD TEST_TIMEOUT <<< "$DETECTION"
else
  TEST_CMD=""
  TEST_TIMEOUT=""
fi

# Stage 2: Run
INTEGRATION_STATUS="SKIP"
INTEGRATION_CMD="$TEST_CMD"
INTEGRATION_DURATION=""
INTEGRATION_OUTPUT=""

if [[ -n "$TEST_CMD" ]]; then
  RESULT=$(run_integration "$TEST_CMD" "$TEST_TIMEOUT")
  IFS='|' read -r EXIT_CODE INTEGRATION_DURATION INTEGRATION_OUTPUT <<< "$RESULT"

  if [[ "$EXIT_CODE" -eq 0 ]]; then
    INTEGRATION_STATUS="PASS"
  else
    INTEGRATION_STATUS="FAIL"
  fi
fi

# Stage 3: Context
CHANGED_FILES=$(detect_changed_files)
ARTIFACT_PATHS=$(resolve_artifact_paths)
SKILL_RESULT=$(detect_skill_changes "$CHANGED_FILES")
IFS='|' read -r SKILL_DETECTED SKILL_FILES <<< "$SKILL_RESULT"

# Smoke items from testing.json
SMOKE_ITEMS=""
if [[ -f "$REPO_ROOT/.agents/testing.json" ]] && command -v jq &>/dev/null; then
  SMOKE_ITEMS=$(jq -r '.smoke[]? // empty' "$REPO_ROOT/.agents/testing.json" 2>/dev/null | sed 's/^/- /')
fi

# Stage 4: Output
emit_output "$INTEGRATION_STATUS" "$INTEGRATION_CMD" "$INTEGRATION_DURATION" \
  "$INTEGRATION_OUTPUT" "$ARTIFACT_PATHS" "$SKILL_DETECTED" "$SKILL_FILES" "$SMOKE_ITEMS"

# Exit code
if [[ "$INTEGRATION_STATUS" == "FAIL" ]]; then
  exit 1
fi
exit 0
```

- [ ] **Step 2: Make executable**

```bash
chmod +x skills/swain-test/scripts/swain-test.sh
```

- [ ] **Step 3: Run the BDD specs to verify they pass (GREEN)**

```bash
bats spec/test-gate/swain_test.bats 2>&1 | tail -5
```

Expected: All 17 tests pass (or most — some may need tweaking based on exact output format)

- [ ] **Step 4: Fix any failing specs**

Adjust either the script output or the spec assertions until all tests pass. The spec's output format is the contract — prefer fixing the script to match the spec.

- [ ] **Step 5: Commit GREEN**

```bash
git add skills/swain-test/scripts/swain-test.sh
git commit -m "feat(swain-test): implement swain-test.sh — SPEC-220

Test command detection (testing.json, package.json, Cargo.toml,
pyproject.toml, go.mod, Makefile), integration test execution with
timeout, changed file detection, artifact/skill resolution, and
structured output (INTEGRATION, ARTIFACTS, SKILLS, SMOKE, FALLBACK)."
```

---

### Task 4: Verify full suite and update spec runner

- [ ] **Step 1: Run full BDD suite including new specs**

```bash
spec/run --tap 2>&1 | tail -5
```

Expected: All specs pass (84 original + 17 new = ~101)

- [ ] **Step 2: Update run-specs.sh if needed**

The runner auto-discovers `spec/test-gate/` as a domain directory — no changes needed unless there are issues.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "chore(swain-test): verify full suite passes with new test-gate specs"
```
