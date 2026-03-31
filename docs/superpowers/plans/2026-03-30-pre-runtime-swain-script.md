# Pre-Runtime Swain Script — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `swain` project-root script that handles crash detection (Phase 1), session resume selection (Phase 2), and runtime invocation (Phase 3) — all before the LLM starts.

**Architecture:** A single bash script at `skills/swain/scripts/swain` with three sequential phases. Phase 1 sources `crash-debris-lib.sh` (SPEC-182) for detection and offers interactive cleanup. Phase 2 reads `.agents/session.json` and presents resume options when crashed sessions exist. Phase 3 resolves the runtime via a preference chain (per-project > global > auto-detect) and launches it with correct flags per ADR-017. A `bin/swain` symlink already exists for operator access.

**Tech Stack:** Bash (pure — no Python, no Node), crash-debris-lib.sh (SPEC-182), jq (optional, with fallback), git.

---

## File Structure

| File | Responsibility |
|------|---------------|
| `skills/swain/scripts/swain` | Main script — Phase 1 (crash detection + cleanup), Phase 2 (session selection), Phase 3 (runtime invocation) |
| `tests/test_pre_runtime.sh` | Tests for argument parsing, runtime resolution, crash detection integration, prompt composition |

The `bin/swain` symlink already exists and points to `skills/swain/scripts/swain`.

## Chunk 1: Script Skeleton and Runtime Resolution

### Task 1: Scaffold the script and test file

**Files:**
- Create: `skills/swain/scripts/swain`
- Create: `tests/test_pre_runtime.sh`

- [ ] **Step 1: Write the test scaffold**

```bash
#!/usr/bin/env bash
# RED tests for SPEC-180: Pre-Runtime Swain Script
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/skills/swain/scripts/swain"
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

echo "=== SPEC-180: Pre-Runtime Swain Script Tests ==="

# T1: Script exists and is executable
assert "swain script exists" "$([ -f "$SCRIPT" ] && echo true || echo false)"
assert "swain script is executable" "$([ -x "$SCRIPT" ] && echo true || echo false)"

# T2: bin/swain symlink resolves
assert "bin/swain symlink resolves" "$([ -L "$REPO_ROOT/bin/swain" ] && [ -e "$REPO_ROOT/bin/swain" ] && echo true || echo false)"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
```

- [ ] **Step 2: Write the script skeleton**

```bash
#!/usr/bin/env bash
# swain — pre-runtime crash recovery and session launcher (SPEC-180)
#
# Phases:
#   1. Pre-runtime structural checks (crash debris detection + cleanup)
#   2. Session selection (resume crashed session or start fresh)
#   3. Runtime invocation (resolve + launch preferred agentic CLI)
#
# Usage: swain [--fresh] [--runtime <name>] [session purpose text...]
#
# Per ADR-018: all logic is structural (bash), not prosaic (LLM).
# Per ADR-015: never auto-discard worktree state.
# Per ADR-019: canonical location is skills/swain/scripts/swain;
#              operator access via bin/swain symlink.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Resolve repo root: go up from skills/swain/scripts/ to project root
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# --- Argument parsing ---
FLAG_FRESH=false
FLAG_RUNTIME=""
PURPOSE_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fresh)
      FLAG_FRESH=true
      shift
      ;;
    --runtime)
      FLAG_RUNTIME="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: swain [--fresh] [--runtime <name>] [purpose...]"
      echo ""
      echo "Options:"
      echo "  --fresh         Skip crash recovery, start a clean session"
      echo "  --runtime NAME  Force a specific runtime (claude, gemini, codex, copilot, crush)"
      echo ""
      echo "Arguments after flags become the session purpose text."
      exit 0
      ;;
    *)
      PURPOSE_ARGS+=("$1")
      shift
      ;;
  esac
done

# --- Phase 1: Pre-runtime structural checks ---
phase1_crash_detection() {
  : # placeholder — Task 3
}

# --- Phase 2: Session selection ---
phase2_session_selection() {
  : # placeholder — Task 5
}

# --- Phase 3: Runtime invocation ---
phase3_launch_runtime() {
  : # placeholder — Task 4
}

# --- Main ---
cd "$REPO_ROOT"

if [[ "$FLAG_FRESH" != "true" ]]; then
  phase1_crash_detection
  phase2_session_selection
fi

phase3_launch_runtime
```

- [ ] **Step 3: Make executable**

Run: `chmod +x skills/swain/scripts/swain`

- [ ] **Step 4: Run tests to verify scaffold works**

Run: `bash tests/test_pre_runtime.sh`
Expected: 3 PASS (script exists, executable, symlink resolves)

- [ ] **Step 5: Commit**

```bash
git add skills/swain/scripts/swain tests/test_pre_runtime.sh
git commit -m "feat(SPEC-180): scaffold pre-runtime swain script and tests"
```

---

### Task 2: Argument parsing tests

**Files:**
- Modify: `tests/test_pre_runtime.sh`

- [ ] **Step 1: Write argument parsing tests**

Append BEFORE results section:

```bash
# --- Argument parsing ---
# Source the script in a subshell to test argument parsing without launching runtime
# We use --help to verify the script parses without error

# T3: --help exits cleanly
HELP_OUT=$("$SCRIPT" --help 2>&1 || true)
assert "--help shows usage" "$(echo "$HELP_OUT" | grep -q 'Usage: swain' && echo true || echo false)"

# T4: --fresh flag is accepted (script will exit at phase3 since no runtime is available in test)
# We test this by checking the script doesn't error on the flag itself
# (It will fail at runtime detection, which is fine — we're testing arg parsing)
FRESH_OUT=$("$SCRIPT" --fresh --runtime nonexistent 2>&1 || true)
assert "--fresh flag accepted" "$(echo "$FRESH_OUT" | grep -qv 'unknown option' && echo true || echo false)"
```

- [ ] **Step 2: Run tests**

Run: `bash tests/test_pre_runtime.sh`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_pre_runtime.sh
git commit -m "feat(SPEC-180): add argument parsing tests"
```

---

### Task 3: Runtime resolution (Phase 3 core — AC4)

**Files:**
- Modify: `skills/swain/scripts/swain`
- Modify: `tests/test_pre_runtime.sh`

- [ ] **Step 1: Write failing tests for runtime resolution**

Append BEFORE results section:

```bash
# --- Runtime resolution (AC4) ---
# Test the resolve_runtime function by sourcing it

# Create a temp settings file for testing
TMPDIR_RT=$(mktemp -d)

# T5: --runtime flag overrides everything
source "$SCRIPT" --help >/dev/null 2>&1 || true  # source to get functions
# Can't easily source the script without it running. Instead, test via subprocess.

# T5: --runtime flag overrides all other resolution
RUNTIME_OUT=$("$SCRIPT" --runtime gemini --_dry_run 2>&1 || true)
assert "--runtime flag sets runtime" "$(echo "$RUNTIME_OUT" | grep -q 'runtime: gemini' && echo true || echo false)"

# T6: --_dry_run shows resolved runtime without launching
DRY_OUT=$("$SCRIPT" --_dry_run 2>&1 || true)
assert "--_dry_run shows runtime info" "$(echo "$DRY_OUT" | grep -qE 'runtime:' && echo true || echo false)"

# T7: Per-project swain.settings.json runtime is used when no --runtime flag
TMPDIR_RT2=$(mktemp -d)
mkdir -p "$TMPDIR_RT2/.git"
cat > "$TMPDIR_RT2/swain.settings.json" <<'SETTJSON'
{"runtime": "codex"}
SETTJSON
RT_PROJ=$(REPO_ROOT="$TMPDIR_RT2" bash "$SCRIPT" --_dry_run 2>&1 || true)
assert "per-project setting used" "$(echo "$RT_PROJ" | grep -q 'runtime: codex' && echo true || echo false)"

rm -rf "$TMPDIR_RT" "$TMPDIR_RT2"
```

- [ ] **Step 2: Run tests — expect FAIL on T5-T6**

- [ ] **Step 3: Implement runtime resolution and --_dry_run**

Replace the argument parsing section and phase3 in the script:

Add `--_dry_run` to the argument parser:

```bash
    --_dry_run)
      FLAG_DRY_RUN=true
      shift
      ;;
```

Add at the top with other flag declarations:

```bash
FLAG_DRY_RUN=false
```

Replace `phase3_launch_runtime`:

```bash
# --- Runtime resolution ---
# Priority: --runtime flag > per-project setting > global setting > auto-detect
resolve_runtime() {
  # 1. CLI flag
  if [[ -n "$FLAG_RUNTIME" ]]; then
    echo "$FLAG_RUNTIME"
    return
  fi

  # 2. Per-project setting (swain.settings.json)
  local project_settings="$REPO_ROOT/swain.settings.json"
  if [[ -f "$project_settings" ]]; then
    local rt
    rt=$(grep -o '"runtime"[[:space:]]*:[[:space:]]*"[^"]*"' "$project_settings" 2>/dev/null \
         | head -1 | sed 's/.*"runtime"[[:space:]]*:[[:space:]]*"//;s/"$//')
    if [[ -n "$rt" ]]; then
      echo "$rt"
      return
    fi
  fi

  # 3. Global setting (~/.config/swain/settings.json)
  local global_settings="$HOME/.config/swain/settings.json"
  if [[ -f "$global_settings" ]]; then
    local rt
    rt=$(grep -o '"runtime"[[:space:]]*:[[:space:]]*"[^"]*"' "$global_settings" 2>/dev/null \
         | head -1 | sed 's/.*"runtime"[[:space:]]*:[[:space:]]*"//;s/"$//')
    if [[ -n "$rt" ]]; then
      echo "$rt"
      return
    fi
  fi

  # 4. Auto-detect installed runtimes (first match wins)
  local runtimes=(claude gemini codex copilot crush)
  for rt in "${runtimes[@]}"; do
    if command -v "$rt" &>/dev/null; then
      echo "$rt"
      return
    fi
  done

  echo ""
}

# Build launch command for a given runtime
# Returns: command string to exec
build_launch_cmd() {
  local runtime="$1"
  local prompt="$2"

  case "$runtime" in
    claude)
      echo "claude --dangerously-skip-permissions \"$prompt\""
      ;;
    gemini)
      echo "gemini -y -i \"$prompt\""
      ;;
    codex)
      echo "codex --full-auto \"$prompt\""
      ;;
    copilot)
      echo "copilot --yolo -i \"$prompt\""
      ;;
    crush)
      # Partial tier — no initial prompt support (ADR-017)
      echo "crush --yolo"
      ;;
    *)
      echo ""
      ;;
  esac
}

# --- Phase 3: Runtime invocation ---
phase3_launch_runtime() {
  local runtime
  runtime=$(resolve_runtime)

  if [[ -z "$runtime" ]]; then
    echo "error: no supported runtime found. Install one of: claude, gemini, codex, copilot, crush" >&2
    exit 1
  fi

  # Compose initial prompt
  local prompt="/swain-init"
  if [[ ${#PURPOSE_ARGS[@]} -gt 0 ]]; then
    prompt="/swain-session Session purpose: ${PURPOSE_ARGS[*]}"
  fi

  # For Partial tier (crush): use SWAIN_PURPOSE env var instead of prompt (ADR-017)
  if [[ "$runtime" == "crush" ]]; then
    if [[ -n "$RESUME_PROMPT" ]]; then
      export SWAIN_PURPOSE="resume — ${bookmark:-previous session}"
    elif [[ ${#PURPOSE_ARGS[@]} -gt 0 ]]; then
      export SWAIN_PURPOSE="${PURPOSE_ARGS[*]}"
    fi
  fi

  local cmd
  cmd=$(build_launch_cmd "$runtime" "$prompt")

  if [[ "$FLAG_DRY_RUN" == "true" ]]; then
    echo "runtime: $runtime"
    echo "prompt: $prompt"
    echo "command: $cmd"
    return
  fi

  # Launch the runtime via exec (replaces this process)
  eval exec "$cmd"
}
```

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add skills/swain/scripts/swain tests/test_pre_runtime.sh
git commit -m "feat(SPEC-180): implement runtime resolution with preference chain (AC4)"
```

---

### Task 4: --fresh flag skips Phase 2 (AC7)

**Files:**
- Modify: `tests/test_pre_runtime.sh`

- [ ] **Step 1: Write test for --fresh behavior**

Append BEFORE results section:

```bash
# T8: --fresh skips crash recovery (AC7)
FRESH_DRY=$("$SCRIPT" --fresh --_dry_run 2>&1 || true)
# --fresh should NOT show any crash detection output
assert "--fresh skips crash detection" "$(echo "$FRESH_DRY" | grep -qv 'crash debris\|recovery' && echo true || echo false)"
assert "--fresh still shows runtime" "$(echo "$FRESH_DRY" | grep -q 'runtime:' && echo true || echo false)"
```

- [ ] **Step 2: Run tests — expect PASS (--fresh already implemented in skeleton)**

- [ ] **Step 3: Commit**

```bash
git add tests/test_pre_runtime.sh
git commit -m "test(SPEC-180): verify --fresh flag skips crash recovery (AC7)"
```

---

## Chunk 2: Crash Detection and Session Selection

### Task 5: Phase 1 — crash debris detection and cleanup (AC1, AC3)

**Files:**
- Modify: `skills/swain/scripts/swain`
- Modify: `tests/test_pre_runtime.sh`

- [ ] **Step 1: Write failing tests**

Append BEFORE results section:

```bash
# --- Phase 1: Crash detection (AC1, AC3) ---
TMPDIR_P1=$(mktemp -d)
mkdir -p "$TMPDIR_P1/.git"

# T8: Phase 1 sources crash-debris-lib.sh and detects debris
# Create a fake index.lock from dead PID
echo "99999999" > "$TMPDIR_P1/.git/index.lock"

# Test Phase 1 in isolation by calling with --_phase1_only flag
P1_OUT=$(REPO_ROOT="$TMPDIR_P1" bash "$SCRIPT" --_phase1_only --_non_interactive 2>&1 || true)
assert "phase 1 detects crash debris" "$(echo "$P1_OUT" | grep -qi 'debris\|lock\|found' && echo true || echo false)"

# T9: Clean project → phase 1 is silent (AC2 fast path)
TMPDIR_P1B=$(mktemp -d)
mkdir -p "$TMPDIR_P1B/.git"
P1_CLEAN=$(REPO_ROOT="$TMPDIR_P1B" bash "$SCRIPT" --_phase1_only --_non_interactive 2>&1 || true)
assert "clean project → phase 1 silent" "$([ -z "$P1_CLEAN" ] && echo true || echo false)"

rm -rf "$TMPDIR_P1" "$TMPDIR_P1B"
```

- [ ] **Step 2: Run tests — expect FAIL**

- [ ] **Step 3: Implement Phase 1**

Add `--_phase1_only` and `--_non_interactive` to argument parser:

```bash
    --_phase1_only)
      FLAG_PHASE1_ONLY=true
      shift
      ;;
    --_non_interactive)
      FLAG_NON_INTERACTIVE=true
      shift
      ;;
```

Add flag declarations:

```bash
FLAG_PHASE1_ONLY=false
FLAG_NON_INTERACTIVE=false
```

Replace `phase1_crash_detection`:

```bash
# --- Phase 1: Pre-runtime structural checks ---
phase1_crash_detection() {
  # Source the crash debris detection library (SPEC-182)
  local lib="$REPO_ROOT/skills/swain-doctor/scripts/crash-debris-lib.sh"
  if [[ ! -f "$lib" ]]; then
    echo "warning: crash-debris-lib.sh not found; skipping crash detection" >&2
    return
  fi
  source "$lib"

  # Run all crash debris checks
  local findings
  findings=$(check_all_crash_debris "$REPO_ROOT" 2>/dev/null)

  # AC5 silent fast path: no findings → return immediately
  if [[ -z "$findings" ]]; then
    return
  fi

  # Display findings
  echo "=== Crash debris detected ==="
  echo ""
  local count=0
  while IFS=$'\t' read -r type status detail; do
    [[ "$status" != "found" ]] && continue
    count=$((count + 1))
    case "$type" in
      git_index_lock)
        echo "  [$count] Git index lock: $detail"
        ;;
      interrupted_git_ops)
        echo "  [$count] $detail"
        ;;
      stale_tk_locks)
        echo "  [$count] Stale task lock: $detail"
        ;;
      dangling_worktrees)
        echo "  [$count] Dangling worktree: $detail"
        ;;
      orphaned_mcp)
        echo "  [$count] Orphaned MCP server: $detail"
        ;;
      *)
        echo "  [$count] $type: $detail"
        ;;
    esac
  done <<< "$findings"
  echo ""

  if [[ "$FLAG_NON_INTERACTIVE" == "true" ]]; then
    return
  fi

  # Offer cleanup with confirmation (per ADR-015: never auto-discard)
  echo "Clean up crash debris? (y/n/q — q skips remaining)"
  local item_num=0
  while IFS=$'\t' read -r type status detail; do
    [[ "$status" != "found" ]] && continue
    item_num=$((item_num + 1))

    local action=""
    case "$type" in
      git_index_lock)
        local lock_path
        lock_path=$(echo "$detail" | awk '{print $1}')
        action="rm -f \"$lock_path\""
        ;;
      interrupted_git_ops)
        if echo "$detail" | grep -q "merge"; then
          action="git -C \"$REPO_ROOT\" merge --abort"
        elif echo "$detail" | grep -q "rebase"; then
          action="git -C \"$REPO_ROOT\" rebase --abort"
        elif echo "$detail" | grep -q "cherry-pick"; then
          action="git -C \"$REPO_ROOT\" cherry-pick --abort"
        fi
        ;;
      stale_tk_locks)
        local task_id
        task_id=$(echo "$detail" | awk '{print $2}')
        action="rm -rf \"$REPO_ROOT/.tickets/.locks/$task_id\""
        ;;
      dangling_worktrees)
        # Don't auto-cleanup worktrees — surface for Phase 2
        action=""
        ;;
      orphaned_mcp)
        local mcp_pid
        mcp_pid=$(echo "$detail" | grep -oE 'PID [0-9]+' | awk '{print $2}')
        action="kill $mcp_pid"
        ;;
    esac

    if [[ -z "$action" ]]; then
      continue
    fi

    read -r -p "  [$item_num] Clean up? (y/n/q) " choice </dev/tty
    case "$choice" in
      y|Y)
        eval "$action" 2>/dev/null && echo "    Cleaned." || echo "    Failed."
        ;;
      q|Q)
        echo "  Skipping remaining."
        break
        ;;
      *)
        echo "    Skipped."
        ;;
    esac
  done <<< "$findings"
  echo ""

  # Store findings for Phase 2 (session selection needs to know about dangling worktrees)
  PHASE1_FINDINGS="$findings"
}

PHASE1_FINDINGS=""
```

Update the main block to handle `--_phase1_only`:

At the bottom of the main block, before `phase3_launch_runtime`:

```bash
if [[ "$FLAG_PHASE1_ONLY" == "true" ]]; then
  exit 0
fi
```

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add skills/swain/scripts/swain tests/test_pre_runtime.sh
git commit -m "feat(SPEC-180): implement Phase 1 crash detection and cleanup (AC1, AC3)"
```

---

### Task 6: Phase 2 — session selection (AC1, AC5, AC6)

**Files:**
- Modify: `skills/swain/scripts/swain`
- Modify: `tests/test_pre_runtime.sh`

- [ ] **Step 1: Write failing tests**

Append BEFORE results section:

```bash
# --- Phase 2: Session selection (AC1, AC5, AC6) ---
TMPDIR_P2=$(mktemp -d)
mkdir -p "$TMPDIR_P2/.git" "$TMPDIR_P2/.agents"

# T10: No crashed sessions → phase 2 skipped (AC2 fast path)
P2_CLEAN=$(REPO_ROOT="$TMPDIR_P2" bash "$SCRIPT" --_phase2_only --_non_interactive 2>&1 || true)
assert "no crashed sessions → phase 2 silent" "$([ -z "$P2_CLEAN" ] && echo true || echo false)"

# T11: With session bookmark → resume context shown
cat > "$TMPDIR_P2/.agents/session.json" <<'SESSJSON'
{
  "lastBranch": "trunk",
  "bookmark": {
    "note": "Working on crash detection",
    "files": ["scripts/test.sh"],
    "timestamp": "2026-03-28T22:00:00Z"
  },
  "focus_lane": "INITIATIVE-019"
}
SESSJSON
# Simulate a crashed session by creating crash debris
echo "99999999" > "$TMPDIR_P2/.git/index.lock"
P2_RESUME=$(REPO_ROOT="$TMPDIR_P2" bash "$SCRIPT" --_phase2_only --_non_interactive 2>&1 || true)
assert "crashed session → shows resume context" "$(echo "$P2_RESUME" | grep -q 'Working on crash detection' && echo true || echo false)"

rm -rf "$TMPDIR_P2"
```

- [ ] **Step 2: Run tests — expect FAIL**

- [ ] **Step 3: Implement Phase 2**

Add `--_phase2_only` to argument parser:

```bash
    --_phase2_only)
      FLAG_PHASE2_ONLY=true
      shift
      ;;
```

Add flag declaration: `FLAG_PHASE2_ONLY=false`

Replace `phase2_session_selection`:

```bash
# --- Phase 2: Session selection ---
# Only runs when crash debris or crashed sessions are detected
phase2_session_selection() {
  local has_crash_indicators=false

  # Check for crash debris from Phase 1
  if [[ -n "$PHASE1_FINDINGS" ]]; then
    has_crash_indicators=true
  fi

  # Check for session state with a bookmark (indicates prior session)
  local session_file="$REPO_ROOT/.agents/session.json"
  local bookmark="" focus_lane=""

  if [[ -f "$session_file" ]]; then
    bookmark=$(grep -o '"note"[[:space:]]*:[[:space:]]*"[^"]*"' "$session_file" 2>/dev/null \
               | head -1 | sed 's/.*"note"[[:space:]]*:[[:space:]]*"//;s/"$//')
    focus_lane=$(grep -o '"focus_lane"[[:space:]]*:[[:space:]]*"[^"]*"' "$session_file" 2>/dev/null \
                 | head -1 | sed 's/.*"focus_lane"[[:space:]]*:[[:space:]]*"//;s/"$//')
  fi

  # Fast path: no crash indicators and no bookmark → skip Phase 2
  if [[ "$has_crash_indicators" != "true" ]] && [[ -z "$bookmark" ]]; then
    return
  fi

  # Show resume context
  echo "=== Previous session detected ==="
  if [[ -n "$bookmark" ]]; then
    echo "  Last activity: $bookmark"
  fi
  if [[ -n "$focus_lane" ]]; then
    echo "  Focus: $focus_lane"
  fi

  # Show dangling worktrees with uncommitted changes (AC5)
  if echo "$PHASE1_FINDINGS" | grep -q 'dangling_worktrees.*found' 2>/dev/null; then
    echo ""
    echo "  Worktrees with unmerged work:"
    echo "$PHASE1_FINDINGS" | grep 'dangling_worktrees.*found' | while IFS=$'\t' read -r _ _ detail; do
      echo "    - $detail"
    done
  fi
  echo ""

  if [[ "$FLAG_NON_INTERACTIVE" == "true" ]]; then
    # In non-interactive mode, compose resume prompt automatically
    RESUME_PROMPT="/swain-session Session purpose: resume after crash"
    if [[ -n "$bookmark" ]]; then
      RESUME_PROMPT="/swain-session Session purpose: resume — $bookmark"
    fi
    return
  fi

  # Interactive: offer resume or fresh start
  echo "Options:"
  echo "  [r] Resume previous session"
  echo "  [f] Start fresh"
  echo ""
  read -r -p "Choice (r/f): " choice </dev/tty

  case "$choice" in
    r|R)
      # Compose initial prompt with resume context (AC6)
      RESUME_PROMPT="/swain-session"
      if [[ -n "$bookmark" ]]; then
        RESUME_PROMPT="/swain-session Session purpose: resume — $bookmark"
      fi
      echo "  Resuming with context."
      ;;
    *)
      RESUME_PROMPT=""
      echo "  Starting fresh."
      ;;
  esac
  echo ""
}

RESUME_PROMPT=""
```

Update `phase3_launch_runtime` to use `RESUME_PROMPT` if set. In the prompt composition section, replace:

```bash
  # Compose initial prompt
  local prompt="/swain-init"
  if [[ ${#PURPOSE_ARGS[@]} -gt 0 ]]; then
    prompt="/swain-session Session purpose: ${PURPOSE_ARGS[*]}"
  fi
```

with:

```bash
  # Compose initial prompt
  local prompt="/swain-init"
  if [[ -n "$RESUME_PROMPT" ]]; then
    prompt="$RESUME_PROMPT"
  elif [[ ${#PURPOSE_ARGS[@]} -gt 0 ]]; then
    prompt="/swain-session Session purpose: ${PURPOSE_ARGS[*]}"
  fi
```

Handle `--_phase2_only` in the main block — run only phases 1+2 (Phase 1 populates PHASE1_FINDINGS which Phase 2 needs):

```bash
if [[ "$FLAG_PHASE2_ONLY" == "true" ]]; then
  phase1_crash_detection
  phase2_session_selection
  exit 0
fi
```

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add skills/swain/scripts/swain tests/test_pre_runtime.sh
git commit -m "feat(SPEC-180): implement Phase 2 session selection with resume context (AC1, AC5, AC6)"
```

---

### Task 7: Resume prompt composition (AC6)

**Files:**
- Modify: `tests/test_pre_runtime.sh`

- [ ] **Step 1: Write tests for resume prompt content**

Append BEFORE results section:

```bash
# --- Resume prompt composition (AC6) ---
TMPDIR_P3=$(mktemp -d)
mkdir -p "$TMPDIR_P3/.git" "$TMPDIR_P3/.agents"

# T12: Resume prompt includes bookmark and focus lane
cat > "$TMPDIR_P3/.agents/session.json" <<'SESSJSON'
{
  "lastBranch": "feature-branch",
  "bookmark": {
    "note": "Implementing SPEC-182 tests",
    "files": ["tests/test.sh"],
    "timestamp": "2026-03-28T22:00:00Z"
  },
  "focus_lane": "INITIATIVE-019"
}
SESSJSON
echo "99999999" > "$TMPDIR_P3/.git/index.lock"

# Use --_dry_run to see the composed prompt
RESUME_DRY=$(REPO_ROOT="$TMPDIR_P3" bash "$SCRIPT" --_non_interactive --_dry_run 2>&1 || true)
assert "resume prompt includes bookmark" "$(echo "$RESUME_DRY" | grep -q 'SPEC-182' && echo true || echo false)"

# T13: No purpose args + no crash → prompt is /swain-init
TMPDIR_P3B=$(mktemp -d)
mkdir -p "$TMPDIR_P3B/.git"
FRESH_DRY=$(REPO_ROOT="$TMPDIR_P3B" bash "$SCRIPT" --_dry_run 2>&1 || true)
assert "fresh session → /swain-init prompt" "$(echo "$FRESH_DRY" | grep -q '/swain-init' && echo true || echo false)"

# T14: Purpose args → /swain-session with purpose
PURPOSE_DRY=$(REPO_ROOT="$TMPDIR_P3B" bash "$SCRIPT" --_dry_run fix the login bug 2>&1 || true)
assert "purpose args → session purpose prompt" "$(echo "$PURPOSE_DRY" | grep -q 'fix the login bug' && echo true || echo false)"

rm -rf "$TMPDIR_P3" "$TMPDIR_P3B"
```

- [ ] **Step 2: Run tests — expect PASS (implementation already in place)**

- [ ] **Step 3: Commit**

```bash
git add tests/test_pre_runtime.sh
git commit -m "test(SPEC-180): verify resume prompt composition covers all AC6 scenarios"
```

---

### Task 8: Final verification and cleanup

- [ ] **Step 1: Run all SPEC-180 tests**

Run: `bash tests/test_pre_runtime.sh`
Expected: All PASS, 0 failures

- [ ] **Step 2: Run SPEC-182 tests to verify no regressions**

Run: `bash tests/test_crash_debris.sh`
Expected: 18 passed, 0 failed

- [ ] **Step 3: Verify script runs with --_dry_run from the repo root**

Run: `bash bin/swain --_dry_run`
Expected: Shows resolved runtime, prompt, and command

- [ ] **Step 4: Run existing tests for regressions**

Run: `bash tests/test_session_detection.sh && bash tests/test_session_lifecycle.sh`
Expected: All PASS

- [ ] **Step 5: Final commit if any fixes needed**
