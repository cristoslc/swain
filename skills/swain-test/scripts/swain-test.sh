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
  local start_time end_time

  start_time=$(date +%s)

  # Run with timeout — capture exit code before || true swallows it
  _RUN_EXIT=0
  if command -v gtimeout &>/dev/null; then
    _RUN_OUTPUT=$(cd "$REPO_ROOT" && gtimeout "$timeout" bash -c "$cmd" 2>&1) || _RUN_EXIT=$?
  elif command -v timeout &>/dev/null; then
    _RUN_OUTPUT=$(cd "$REPO_ROOT" && timeout "$timeout" bash -c "$cmd" 2>&1) || _RUN_EXIT=$?
  else
    _RUN_OUTPUT=$(cd "$REPO_ROOT" && bash -c "$cmd" 2>&1) || _RUN_EXIT=$?
  fi

  end_time=$(date +%s)
  _RUN_DURATION="$((end_time - start_time))s"
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
  [[ ${#ARTIFACT_IDS[@]} -eq 0 ]] && return 0
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
    # Search for the artifact
    local found
    found=$(find "$REPO_ROOT/docs/$type_lower" -type f -name "*.md" -path "*${id}*" 2>/dev/null | head -1)
    if [[ -z "$found" ]]; then
      # Try searching all docs
      found=$(find "$REPO_ROOT/docs" -type f -name "*.md" -path "*${id}*" 2>/dev/null | head -1)
    fi
    if [[ -n "$found" ]]; then
      paths="${paths}  - ${found#"$REPO_ROOT/"}\n"
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
  _RUN_EXIT=0
  _RUN_DURATION=""
  _RUN_OUTPUT=""
  run_integration "$TEST_CMD" "$TEST_TIMEOUT"
  INTEGRATION_DURATION="$_RUN_DURATION"
  INTEGRATION_OUTPUT="$_RUN_OUTPUT"

  if [[ "$_RUN_EXIT" -eq 0 ]]; then
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
