---
name: swain-teardown
description: "End-of-session hygiene checks — orphan worktree detection with safety checks, git dirty-state warning, ticket sync prompt, and handoff summary. Triggers on: 'teardown', 'clean up', 'wrap up', 'session end', 'end session', 'close session', 'log off', 'sign off', or automatically via swain-session close handler."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Glob
metadata:
  short-description: Session teardown hygiene checks before closing
  version: 2.0.0
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
3. Ticket sync prompt — prompts the operator to verify tickets match what was done (SPEC-234: notes degraded state if no session)
4. Handoff summary — appends a session summary to SESSION-ROADMAP.md

**Note on retro:** Retro invocation was moved to the swain-session close handler (SPEC-234 AC2) so it runs while the session is still active. Do not invoke retro from here.

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

## Step 3 — Ticket sync prompt (SPEC-234 AC3)

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

## Step 4 — Handoff summary

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

## Step 5 — Report findings

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
