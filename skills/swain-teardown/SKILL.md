---
name: swain-teardown
description: "End-of-session hygiene checks — orphan worktree detection with safety checks, git dirty-state warning, ticket sync prompt, and handoff summary. Triggers on: 'teardown', 'clean up', 'wrap up', 'session end', 'end session', 'close session', 'log off', 'sign off', or automatically via swain-session close handler."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Glob
metadata:
  short-description: Session teardown hygiene checks before closing
  version: 2.1.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# Session Teardown

<!-- session-check: SPEC-121, SPEC-234, SPEC-233 -->
Before running checks, verify an active session exists — unless `--session-chain` is passed (which means swain-session already confirmed session state):

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If `session-chain` is NOT passed and the JSON output has `"status"` other than `"active"`, inform the operator: "No active session to tear down." Exit cleanly with code 0.

---

## What this skill does

Session teardown runs a sequence of hygiene checks before a session closes:

1. Orphan worktree detection — finds worktrees with no corresponding session bookmark (SPEC-233: actionable with safety checks)
2. Git dirty-state check — surfaces uncommitted changes before the operator leaves
3. Completion pipeline check — verifies BDD, smoke, and retro ran; invokes missing steps (SPEC-258)
4. Ticket sync prompt — prompts the operator to verify tickets match what was done (SPEC-234: notes degraded state if no session)
5. Handoff summary — appends a session summary to SESSION-ROADMAP.md

**Note on retro:** The SPEC-level retro now runs as part of the completion pipeline (Step 3 / swain-do Step 2d). The EPIC-level retro is invoked by swain-session's close handler. Teardown invokes retro only as a catch-up if the pipeline's retro step was missed.

---

## Step 1 — Orphan worktree check (SPEC-233)

This step reads worktree bookmarks from the `worktrees` array in session.json (managed by swain-bookmark.sh). Orphan worktrees are offered for operator-confirmed removal with safety checks. **This step always runs** regardless of `--session-chain`.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SESSION_FILE="$REPO_ROOT/.agents/session.json"

# Build a list of bookmarked worktree paths from session.json
bookmarked_wts=$(jq -r '(.worktrees // [])[] | .path' "$SESSION_FILE" 2>/dev/null)

orphan_candidates=()
orphan_results=()

# Get all physical worktrees
git worktree list --porcelain 2>/dev/null | grep "^worktree " | while read -r line; do
  wt_path="${line#worktree }"
  wt_branch="$(git -C "$wt_path" rev-parse --abbrev-ref HEAD 2>/dev/null)"

  # Skip trunk (protected)
  if [ "$wt_path" = "$REPO_ROOT" ]; then
    echo "protected: $wt_path (trunk)"
    continue
  fi

  # Check if bookmarked in session.json
  is_orphan=true
  reason=""
  if echo "$bookmarked_wts" | grep -qF "$wt_path"; then
    is_orphan=false
    echo "linked: $wt_path ($wt_branch)"
  fi

  if [ "$is_orphan" = true ]; then
    # Safety checks per SPEC-233 AC1-AC3
    if [ "$wt_path" = "$(pwd)" ]; then
      reason="current directory"
    elif [ -n "$(git -C "$wt_path" status --porcelain 2>/dev/null)" ]; then
      reason="uncommitted changes"
    elif ! git merge-base --is-ancestor "$wt_branch" trunk 2>/dev/null; then
      reason="branch not fully merged"
    else
      reason="safe to remove"
      orphan_candidates+=("$wt_path|$wt_branch")
    fi
    echo "orphan: $wt_path ($wt_branch) — $reason"
    orphan_results+=("$wt_path|$wt_branch|$reason")
  fi
done
```

If orphan worktrees are found, display the message: "The following worktrees have no active session bookmark — consider removing them."

### Operator confirmation for safe orphans

Only offer orphans with `reason="safe to remove"` for removal. For each safe orphan:

```bash
removed_worktrees=()
for candidate in "${orphan_candidates[@]}"; do
  wt_path="${candidate%%|*}"
  wt_branch="${candidate##*|}"

  echo "> Remove orphan worktree $wt_path ($wt_branch)? [y/N]"
  read -r response
  if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    if git worktree remove "$wt_path" 2>/dev/null; then
      removed_worktrees+=("$wt_path|$wt_branch")
      # Clear the bookmark from session.json
      bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" worktree remove "$wt_path"
      echo "Removed: $wt_path"
    else
      echo "ERROR: Failed to remove $wt_path — skipping bookmark cleanup"
    fi
  fi
done
```

### Safety rules (SPEC-233 AC1-AC3, AC7)

- **Current directory:** Never offer for removal. Flag as `reason="current directory"`.
- **Uncommitted changes:** Never offer for removal. Flag as `reason="uncommitted changes"`.
- **Unmerged branch:** Never offer for removal. Flag as `reason="branch not fully merged"`.
- **Trunk:** Never offer for removal. Always show as `protected: <repo_root> (trunk)`.
- **Confirmation required:** Always prompt operator. Never auto-remove.

---

## Step 2 — Git dirty-state check

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

cd "$REPO_ROOT"
git_status=$(git status --porcelain 2>/dev/null)

if [ -n "$git_status" ]; then
  echo "WARN: Dirty git working tree — uncommitted changes detected."
  echo "Changes:"
  echo "$git_status" | head -20
else
  echo "OK: Working tree is clean."
fi
```

Report findings with an actionable recommendation.

---

## Step 3 — Completion pipeline check (SPEC-258)

Before proceeding to ticket sync, verify that the completion pipeline ran for any finished work in this worktree. If steps were missed, run them now.

### 3a — Detect pipeline state

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATE_FILE="$REPO_ROOT/.agents/completion-state.json"
SWAIN_TEST="$REPO_ROOT/.agents/bin/swain-test.sh"
```

**If `completion-state.json` exists:** read it and find incomplete steps:

```bash
PENDING_STEPS=$(jq -r '.steps | to_entries[] | select(.value.status == "pending" or .value.status == "failed") | .key' "$STATE_FILE" 2>/dev/null)
SPEC_ID=$(jq -r '.spec_id // empty' "$STATE_FILE" 2>/dev/null)
```

- If `PENDING_STEPS` is empty → all steps passed or were skipped. Display "Completion pipeline: all steps done." and proceed.
- If `PENDING_STEPS` is not empty → display which steps need attention and run them (see 3b).

**If `completion-state.json` does not exist:** check whether the worktree has closed tasks:

```bash
export PATH="$REPO_ROOT/.agents/bin:$PATH"
CLOSED_COUNT=$(ticket-query '.status == "closed"' 2>/dev/null | wc -l | tr -d ' ')
```

- If `CLOSED_COUNT > 0` → work was done but the pipeline never started. Create the state file with all steps `pending` and run them:
  ```bash
  # Try to find the SPEC ID from the plan epic
  EPIC_ID=$(ticket-query '.type == "epic"' 2>/dev/null | head -1 | jq -r '.id // empty')
  SPEC_ID=$(tk show "$EPIC_ID" 2>/dev/null | grep -i 'external_ref' | awk '{print $NF}')
  mkdir -p "$REPO_ROOT/.agents"
  jq -n --arg spec "${SPEC_ID:-unknown}" --arg branch "$(git branch --show-current)" \
    '{spec_id: $spec, branch: $branch, pipeline_started: (now | todate), steps: {bdd_tests: {status: "pending", timestamp: null, detail: null}, smoke_test: {status: "pending", timestamp: null, detail: null}, retro: {status: "pending", timestamp: null, detail: null}}}' \
    > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
  ```
- If `CLOSED_COUNT == 0` → no finished work, skip this step silently.

### 3b — Run missing steps

For each step in the pipeline order (`bdd_tests` → `smoke_test` → `retro`), check its status. Skip steps that are `passed` or `skipped`. Run steps that are `pending` or `failed`.

**`bdd_tests`:**

```bash
BDD_STATUS=$(jq -r '.steps.bdd_tests.status' "$STATE_FILE")
```

If `BDD_STATUS` is `pending` or `failed`:

- **If `swain-test.sh` exists:**
  ```bash
  BDD_OUTPUT=$(bash "$SWAIN_TEST" --artifacts "$SPEC_ID" 2>&1)
  BDD_EXIT=$?
  ```
  - Exit 0 → update to `passed` with detail from first 5 lines of output.
  - Non-zero → update to `failed` with detail from last 10 lines. Ask: "BDD failed. **retry**, **skip**, or **abort**?"
    - **retry** → re-run this step
    - **skip** → set to `skipped` with detail "operator skipped during teardown"
    - **abort** → stop teardown entirely, do not proceed to sync

- **If `swain-test.sh` does not exist:** set to `skipped` with detail "swain-test.sh not available". Display warning.

Use the atomic jq update pattern from DESIGN-018 for all state writes:
```bash
jq --arg step "$STEP" --arg status "$STATUS" --arg detail "$DETAIL" \
  '.steps[$step].status = $status | .steps[$step].timestamp = (now | todate) | .steps[$step].detail = $detail' \
  "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
```

**`smoke_test`:**

If `pending` or `failed`:

- **If `swain-test.sh` exists:** extract the `## SMOKE` section from swain-test output and present to the operator. Ask: "Did the smoke test pass? (yes / no / skip)"
  - **yes** → set to `passed` with detail "operator confirmed during teardown"
  - **no** → set to `failed`. Ask: "**retry**, **skip**, or **abort**?"
  - **skip** → set to `skipped` with detail "operator skipped during teardown"

- **If `swain-test.sh` does not exist:** set to `skipped` with detail "swain-test.sh not available".

**`retro`:**

If `pending` or `failed`:

Invoke swain-retro using the Skill tool:

> Use the **Skill** tool: invoke `swain-retro` with args: `"Teardown catch-up — run retro for <SPEC-ID> before sync."`

- On success → set to `passed` with detail "retro captured during teardown"
- On failure → ask: "Retro failed. **retry** or **abort**?" (retro cannot be skipped)

### 3c — Force bypass

If the operator invoked teardown with `--force` (detected via the invocation args containing "force" or "--force"):

```bash
# Mark all pending steps as skipped
for step in bdd_tests smoke_test retro; do
  STEP_STATUS=$(jq -r ".steps.$step.status" "$STATE_FILE")
  if [ "$STEP_STATUS" = "pending" ] || [ "$STEP_STATUS" = "failed" ]; then
    jq --arg step "$step" \
      '.steps[$step].status = "skipped" | .steps[$step].timestamp = (now | todate) | .steps[$step].detail = "operator forced bypass"' \
      "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
  fi
done
```

Display: "Force bypass — all pending pipeline steps marked as skipped." Proceed to Step 4.

### 3d — Pipeline gate

After running or skipping all steps, verify:

```bash
REMAINING=$(jq -r '.steps | to_entries[] | select(.value.status == "pending" or .value.status == "failed") | .key' "$STATE_FILE")
```

- If empty → proceed to Step 4
- If not empty → teardown is blocked. Display which steps remain and stop.

---

## Step 4 — Ticket sync prompt (SPEC-234 AC3, renumbered from Step 3)

Always run this step. Note degraded state if no active session:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
session_check=$(bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null)
session_status=$(echo "$session_check" | jq -r '.status // "none"')

if [ "$session_status" = "active" ]; then
  echo "> Before closing, verify that tickets match what was done. Run \`tk issue list\` and confirm open tickets are accurate. Any tickets to close or update?"
else
  echo "> No active session — ticket sync unavailable. Consider running \`tk issue list\` manually."
fi
```

Wait for a response. Do not modify tickets automatically.

---

## Step 5 — Handoff summary

Append a session summary to SESSION-ROADMAP.md, including any worktrees removed during this teardown:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SROADMAP="$REPO_ROOT/SESSION-ROADMAP.md"
session_id="$(jq -r '.session_id // empty' "$REPO_ROOT/.agents/session-state.json" 2>/dev/null)"
focus_lane="$(jq -r '.focus_lane // empty' "$REPO_ROOT/.agents/session-state.json" 2>/dev/null)"

if [ -n "$session_id" ]; then
  {
    echo ""
    echo "## Session $session_id Handoff"
    echo ""
    echo "**Focus lane:** ${focus_lane:-none}"
    echo "**Closed:** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""
    echo "### Findings"
    echo ""
    echo "_(Populated from teardown checks above)_"
  } >> "$SROADMAP"
fi

# Append worktrees removed during this teardown (populated from Step 1)
if [ ${#removed_worktrees[@]} -gt 0 ]; then
  echo "" >> "$SROADMAP"
  echo "### Worktrees Removed During This Teardown" >> "$SROADMAP"
  echo "" >> "$SROADMAP"
  echo "The following orphan worktrees were removed with operator confirmation." >> "$SROADMAP"
  echo "" >> "$SROADMAP"
  for wt in "${removed_worktrees[@]}"; do
    wt_path="${wt%%|*}"
    wt_branch="${wt##*|}"
    echo "- Removed: $wt_path (branch: $wt_branch)" >> "$SROADMAP"
  done
fi
```

If SESSION-ROADMAP.md does not exist, create it with a header first, then append.

---

## Step 6 — Report findings

After all checks, display a summary that distinguishes clean, degraded, and error states (SPEC-234 AC5):

```bash
orphan_count=0
removed_count=0
for result in "${orphan_results[@]}"; do
  reason="${result##*|}"
  if [ "$reason" = "safe to remove" ]; then
    orphan_count=$((orphan_count + 1))
  fi
done
removed_count=${#removed_worktrees[@]}

if [ $orphan_count -eq 0 ] && [ $removed_count -eq 0 ] && [ -z "$git_status" ]; then
  overall_state="clean"
elif [ $removed_count -gt 0 ]; then
  overall_state="degraded (worktrees removed)"
else
  overall_state="degraded"
fi

echo "=== Session Teardown Summary ==="
echo ""
echo "Overall state:   $overall_state"
echo "Worktree state:  $removed_count removed, $orphan_count safe orphans remaining"
echo "Git state:       ${git_status:+dirty — see uncommitted changes above; }clean"
echo "Ticket sync:     ${session_status:-pending operator check}"
echo "Handoff summary: written to SESSION-ROADMAP.md"
echo ""
echo "Session teardown complete."
```

Exit with code 0 unless a critical error occurred.

---

## Error handling

| Situation | Response |
|-----------|----------|
| No active session (without --session-chain) | Report cleanly, exit 0 |
| Git unavailable | Skip git check, note in report |
| Worktree list fails | Skip worktree check, note in report |
| Session state file missing | Note absence, continue with available checks |
| session.json missing worktrees array | Treat all worktrees as orphans, proceed with safety checks |
| git worktree remove fails | Report error, skip bookmark cleanup for that worktree |
| SESSION-ROADMAP.md missing | Create with header, append summary |

---

## Integration with swain-session

swain-session calls this skill from the close handler after the session is closed and before committing SESSION-ROADMAP.md:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SWAIN_TEARDOWN_SKILL="$REPO_ROOT/.claude/skills/swain-teardown/SKILL.md"

# Run teardown as session chain (swain-session already confirmed session state)
Skill("$SWAIN_TEARDOWN_SKILL", "Session teardown — --session-chain flag passed from swain-session close handler.")
```

The `--session-chain` flag is embedded in the prompt args. The skill checks for this flag and skips the redundant session-active check.
