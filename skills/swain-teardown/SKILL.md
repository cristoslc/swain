---
name: swain-teardown
description: "Full session shutdown — digest, retro, merge worktree branches, worktree cleanup, close session state, and commit handoff. This is the single entry point for ending a session. Triggers on: 'teardown', 'clean up', 'wrap up', 'session end', 'end session', 'close session', 'done', 'log off', 'sign off', or automatically when the decision budget is reached."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, EnterWorktree, ExitWorktree
metadata:
  short-description: Full session shutdown sequence
  version: 3.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: medium -->

# Session Teardown

Single entry point for ending a session. Runs the full shutdown sequence: digest, retro, merge, cleanup, close, commit. Replaces the former swain-session close handler (ADR-023).

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

## Step 0 — Release current lockfile claim (SPEC-247)

If the current session is running in a worktree with an active lockfile, release the claim. This runs first so that subsequent orphan detection does not flag the current worktree as active.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LOCKFILE_SCRIPT="$REPO_ROOT/.agents/bin/swain-lockfile.sh"
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null)

if [ "$GIT_COMMON" != "$GIT_DIR" ] && [ -f "$LOCKFILE_SCRIPT" ]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  bash "$LOCKFILE_SCRIPT" release "$BRANCH" 2>/dev/null || true
fi
```

## Step 1 — Orphan worktree check (SPEC-233, SPEC-247)

This step reads worktree bookmarks from the `worktrees` array in session.json and cross-references lockfile state (SPEC-247). Orphan worktrees are offered for operator-confirmed removal with safety checks. **This step always runs** regardless of `--session-chain`.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SESSION_FILE="$REPO_ROOT/.agents/session.json"
LOCKFILE_SCRIPT="$REPO_ROOT/.agents/bin/swain-lockfile.sh"

# Build a list of bookmarked worktree paths from session.json
bookmarked_wts=$(jq -r '(.worktrees // [])[] | .path' "$SESSION_FILE" 2>/dev/null)

orphan_candidates=()
orphan_results=()
ready_candidates=()

# Get all physical worktrees
git worktree list --porcelain 2>/dev/null | grep "^worktree " | while read -r line; do
  wt_path="${line#worktree }"
  wt_branch="$(git -C "$wt_path" rev-parse --abbrev-ref HEAD 2>/dev/null)"

  # Skip trunk (protected)
  if [ "$wt_path" = "$REPO_ROOT" ]; then
    echo "protected: $wt_path (trunk)"
    continue
  fi

  # Check lockfile state (SPEC-247)
  if [ -f "$LOCKFILE_SCRIPT" ]; then
    lock_branch="${wt_branch##*/}"  # strip refs/heads/ prefix
    lockfile="$REPO_ROOT/.agents/worktrees/${lock_branch}.lock"
    if [ -f "$lockfile" ]; then
      # Check if ready_for_cleanup — safe to remove without confirmation
      if grep -q 'ready_for_cleanup=true' "$lockfile" 2>/dev/null; then
        echo "ready: $wt_path ($wt_branch) — marked ready_for_cleanup"
        ready_candidates+=("$wt_path|$wt_branch|$lockfile")
        continue
      fi
      # Check if actively claimed by another session
      if ! bash "$LOCKFILE_SCRIPT" is-stale "$lock_branch" >/dev/null 2>&1; then
        echo "claimed: $wt_path ($wt_branch) — active lockfile, skip"
        continue
      fi
    fi
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

### Auto-remove ready_for_cleanup worktrees (SPEC-247)

Worktrees marked `ready_for_cleanup` have been merged and pushed — safe to remove without operator confirmation. Archive session.json first (SPEC-248):

```bash
ARCHIVE_SCRIPT="$REPO_ROOT/.agents/bin/swain-session-archive.sh"
for candidate in "${ready_candidates[@]}"; do
  IFS='|' read -r wt_path wt_branch lockfile <<< "$candidate"

  # Archive session.json before deletion
  if [ -f "$ARCHIVE_SCRIPT" ]; then
    bash "$ARCHIVE_SCRIPT" save "$wt_path" 2>/dev/null || true
  fi

  if git worktree remove "$wt_path" 2>/dev/null; then
    rm -f "$lockfile"  # Clean up lockfile (SPEC-247 AC3)
    bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" worktree remove "$wt_path" 2>/dev/null || true
    echo "Auto-removed (ready_for_cleanup): $wt_path"
  fi
done
```

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
    # Archive session.json before deletion (SPEC-248)
    if [ -f "$ARCHIVE_SCRIPT" ]; then
      bash "$ARCHIVE_SCRIPT" save "$wt_path" 2>/dev/null || true
    fi
    if git worktree remove "$wt_path" 2>/dev/null; then
      removed_worktrees+=("$wt_path|$wt_branch")
      # Clean up lockfile if present (SPEC-247 AC3)
      lock_branch="${wt_branch##*/}"
      rm -f "$REPO_ROOT/.agents/worktrees/${lock_branch}.lock" 2>/dev/null || true
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
```

If `session_status` is not `"active"`:
- If `--session-chain` was passed, proceed anyway (caller already confirmed).
- Otherwise, inform the operator: "No active session. Run `/swain-init` to start one, or proceed with cleanup only?" If they proceed, skip Steps 1-2 (digest/retro need session state) and jump to Step 3 (merge).

---

## Step 1 — Session digest

Generate the session digest while the session is still active.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SESSION_ID="$(jq -r '.session_id // empty' "$REPO_ROOT/.agents/session-state.json" 2>/dev/null)"

if [ -n "$SESSION_ID" ]; then
  bash "$REPO_ROOT/.agents/bin/swain-session-digest.sh" \
    --session-id "$SESSION_ID" \
    --output "$REPO_ROOT/.agents/session-log.jsonl" 2>/dev/null
fi
```

If the digest script is missing or fails, log a warning and continue. The digest is useful but not blocking.

---

## Step 2 — Retro (session still active)

**Critical:** The session must still be active when retro runs so it can read session state. Do not close the session before this step.

Invoke **swain-retro**:

```
Skill("swain-retro", "Session is closing. Run retro to capture learnings before session state is cleared.")
```

If swain-retro is not available, log "Retro skill not found — skipping" and continue. The shutdown sequence must not fail because a skill is missing.

---

## Step 3 — Merge worktree branches

For each active worktree (excluding trunk), offer to merge its branch into trunk. This is the step that was missing from the old teardown — without it, worktrees could never be "safe to remove" because their branches were never merged.

### 3.1 — Enumerate worktrees

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TRUNK=$(bash "$REPO_ROOT/.agents/bin/swain-trunk.sh" 2>/dev/null || echo "trunk")

git worktree list --porcelain 2>/dev/null | grep "^worktree " | while read -r line; do
  wt_path="${line#worktree }"
  # Skip trunk
  [ "$wt_path" = "$REPO_ROOT" ] && continue
  wt_branch="$(git -C "$wt_path" rev-parse --abbrev-ref HEAD 2>/dev/null)"
  echo "$wt_path|$wt_branch"
done
```

### 3.2 — Triage each worktree

For each worktree, classify its state:

| State | Condition | Action |
|-------|-----------|--------|
| **Already merged** | `git merge-base --is-ancestor "$wt_branch" "$TRUNK"` | Skip merge, mark safe for cleanup |
| **Clean, unmerged** | No uncommitted changes, branch not merged | Offer merge |
| **Dirty** | `git -C "$wt_path" status --porcelain` has output | Warn operator, offer to commit first |
| **Current directory** | `"$wt_path" = "$(pwd)"` | Must exit first via ExitWorktree |

### 3.3 — Merge unmerged branches

For each "clean, unmerged" worktree, ask the operator:

> Worktree `{path}` (branch `{branch}`) has unmerged changes. Options:
> 1. **Merge** — merge branch into {trunk} now
> 2. **PR** — push branch and create a pull request
> 3. **Skip** — leave branch as-is (worktree will be preserved)

**If merge:**

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TRUNK=$(bash "$REPO_ROOT/.agents/bin/swain-trunk.sh" 2>/dev/null || echo "trunk")

# Link safety — scan for worktree-specific path links before merging
DETECT_SCRIPT="$REPO_ROOT/.agents/bin/detect-worktree-links.sh"
RESOLVE_SCRIPT="$REPO_ROOT/.agents/bin/resolve-worktree-links.sh"
if [ -x "$DETECT_SCRIPT" ]; then
  MERGE_BASE=$(git -C "$wt_path" merge-base HEAD "origin/$TRUNK" 2>/dev/null || true)
  CHANGED_FILES=$([ -n "$MERGE_BASE" ] && git -C "$wt_path" diff --name-only "$MERGE_BASE" HEAD 2>/dev/null || true)
  if [ -n "$CHANGED_FILES" ]; then
    if ! echo "$CHANGED_FILES" | xargs "$DETECT_SCRIPT" --repo-root "$REPO_ROOT" > /dev/null 2>&1; then
      echo "[link-safety] Found suspicious links in $wt_branch. Resolving..."
      echo "$CHANGED_FILES" | xargs "$RESOLVE_SCRIPT" --repo-root "$REPO_ROOT" 2>/dev/null || true
    fi
  fi
fi

# Merge into trunk from the main worktree
cd "$REPO_ROOT"
git fetch origin 2>/dev/null
git merge "$wt_branch" --no-edit
```

If the merge has conflicts, report them to the operator and skip this worktree. Do not force-resolve.

**If PR:**

```bash
cd "$wt_path"
git push -u origin "$wt_branch" 2>/dev/null
SUBJECT=$(git log -1 --pretty=format:'%s')
gh pr create --base "$TRUNK" --head "$wt_branch" --title "$SUBJECT" --body "Teardown PR — branch from session teardown."
```

Report the PR URL.

**If skip:** Mark the worktree as preserved. It will not be removed in Step 4.

### 3.4 — Handle "current directory" worktree

If the operator is currently inside a worktree, handle it last. After all other worktrees are processed:

1. Ask if they want to merge this branch too (same options as 3.3).
2. If merge or PR: commit any uncommitted changes first, then call `ExitWorktree` to return to trunk.
3. If skip: call `ExitWorktree` with `action: "keep"` to preserve the branch.

---

## Step 4 — Worktree cleanup

After merges, clean up worktrees whose branches are now merged.

### 4.1 — Re-enumerate and check merge status

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TRUNK=$(bash "$REPO_ROOT/.agents/bin/swain-trunk.sh" 2>/dev/null || echo "trunk")

git worktree list --porcelain 2>/dev/null | grep "^worktree " | while read -r line; do
  wt_path="${line#worktree }"
  [ "$wt_path" = "$REPO_ROOT" ] && continue
  wt_branch="$(git -C "$wt_path" rev-parse --abbrev-ref HEAD 2>/dev/null)"

  # Safety checks
  if [ "$wt_path" = "$(pwd)" ]; then
    echo "SKIP: $wt_path — current directory"
    continue
  fi
  if [ -n "$(git -C "$wt_path" status --porcelain 2>/dev/null)" ]; then
    echo "SKIP: $wt_path — uncommitted changes"
    continue
  fi
  if ! git merge-base --is-ancestor "$wt_branch" "$TRUNK" 2>/dev/null; then
    echo "SKIP: $wt_path — branch not merged"
    continue
  fi

  echo "SAFE: $wt_path|$wt_branch"
done
```

### 4.2 — Remove safe worktrees

For each SAFE worktree, remove it without asking. The branch is merged, there are no uncommitted changes, and it is not the current directory. The operator already approved the merge in Step 3.

```bash
git worktree remove "$wt_path" 2>/dev/null && echo "Removed: $wt_path ($wt_branch)"
# Clear bookmark
bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" worktree remove "$wt_path" 2>/dev/null
```

If removal fails, report and continue.

### 4.3 — Prune stale worktree references

```bash
git worktree prune 2>/dev/null
bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" worktree prune 2>/dev/null
```

---

## Step 5 — Close session state

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
WALKAWAY_NOTE="${WALKAWAY:-Session closed via teardown}"

bash "$REPO_ROOT/.agents/bin/swain-session-state.sh" close \
  --walkaway "$WALKAWAY_NOTE" \
  --session-roadmap "$(pwd)/SESSION-ROADMAP.md" 2>/dev/null
```

The walkaway note should summarize what was accomplished. Infer from the session's work (merged branches, closed tasks, retro output) or ask the operator for a one-liner.

---

## Step 6 — Commit handoff

Stage and commit any session artifacts that changed during teardown.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Stage session artifacts
git add SESSION-ROADMAP.md 2>/dev/null
git add docs/swain-retro/ 2>/dev/null
git add .agents/session-state.json 2>/dev/null
git add .agents/session-log.jsonl 2>/dev/null

# Check if there's anything to commit
if [ -n "$(git diff --cached --name-only 2>/dev/null)" ]; then
  git commit -m "chore: session teardown handoff

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
fi
```

---

## Summary report

After all steps, display a summary:

```
=== Session Teardown Complete ===

Retro:          {fired / skipped / not available}
Branches:       {N merged, M PRs created, K preserved}
Worktrees:      {N removed, M preserved}
Session state:  closed
Handoff commit: {hash or "nothing to commit"}
```

Exit with code 0 unless a critical error occurred.

---

## Error handling

| Situation | Response |
|-----------|----------|
| No active session (without --session-chain) | Offer cleanup-only mode (Steps 3-4), skip digest/retro |
| Digest script missing | Warn and continue |
| Retro skill missing | Warn and continue |
| Merge conflict | Report conflicting files, skip that worktree |
| Worktree removal fails | Report and continue |
| Session state script missing | Warn, skip close |
| Nothing to commit in Step 6 | Report "clean" and exit |
| Git unavailable | Fatal — cannot proceed |

---

## Integration

### Called from swain-init (decision budget)

When the decision budget is reached during a session, swain-init can invoke teardown:

```
Skill("swain-teardown", "Decision budget reached. Run teardown sequence.")
```

### Called from meta-router

The swain meta-router routes "done", "wrap up", "close session", "teardown" to this skill.

### Standalone invocation

The operator can run `/swain-teardown` at any time. If no session is active, it offers cleanup-only mode.
