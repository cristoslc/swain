---
title: "swain-sync Lockfile Integration"
artifact: SPIKE-057
track: implementable
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: high
parent-epic: EPIC-056
type: research
swain-do: required
---

# SPIKE-057: swain-sync Lockfile Integration

## Goal

Design and test swain-sync integration with lockfile claiming:
1. Merge trunk into worktree (from inside worktree)
2. Push to remote trunk (from worktree)
3. Mark lockfile `ready_for_cleanup` with commit hash
4. bin/swain verifies + prunes

## Context

**Current swain-sync:**
- Has full merge-with-retry logic (3 attempts) and PR fallback on branch protection
- Removes worktrees itself after push (except `worktree-*` branches)
- Zero lockfile awareness

**New design:**
- swain-sync does merge + push (all from worktree — git supports this)
- Marks lockfile `ready_for_cleanup=true` with `ready_commit=<hash>`
- Does NOT remove worktree — bin/swain handles removal after runtime exits
- bin/swain prunes after verifying no new commits since ready mark

**Runtime constraint:** Most runtimes (Gemini CLI, Codex, Copilot, Crush) cannot change CWD mid-session. Only Claude Code can via EnterWorktree. All git operations must work from within the worktree because the runtime cannot leave it. bin/swain handles cleanup from outside after the runtime exits.

## Findings

### 1. Git Operations from Worktrees

| Operation | Works? | Notes |
|-----------|--------|-------|
| `git merge trunk` | Yes | swain-sync already does this; merge-base confirmed |
| `git push origin HEAD:refs/heads/trunk` | Yes | Non-fast-forward rejected as expected (not a worktree limitation); succeeds after merge |
| `git rebase` | Yes | Full option set available; less relevant per ADR-011 (merge over rebase) |
| `git stash` | Yes, **shared** | Stash is shared across all worktrees — concurrent push/pop can interleave |
| `git worktree remove` (self) | **No** | Cannot remove itself; must cd out first. bin/swain handles from outside. |
| `git worktree list` | Yes | Returns all worktrees from within a linked worktree |
| `git log trunk` | Yes | All refs (branches, tags, remotes) shared across worktrees |
| `git fetch` | Yes | Confirmed with --dry-run |
| `git tag` | Yes, shared | Tags created in any worktree are visible from all others |
| `git worktree lock` | Yes | Git's built-in prune protection; works from within the worktree |
| Branch checkout | **Restricted** | Git refuses checkout of a branch already checked out in another worktree |

**Key behaviors:**
- **Index is per-worktree** — `git add`/`git commit` in one worktree do not interfere with another
- **Stash is shared** — concurrent stash/pop across worktrees can interleave. swain-sync uses labeled stash but `git stash pop` pops the top, not by label.
- **Ref updates use .lock files** — concurrent pushes to the same ref fail cleanly, not corrupt
- **Object creation is atomic** — temp-file-then-rename pattern internally

### 2. swain-sync Current State

**Merge logic (already implemented):**
- Worktree branch with no upstream: `git merge "origin/$TRUNK" --no-edit`
- Retry loop: up to 3 attempts on non-fast-forward push rejection (re-fetch, re-merge, re-push)
- PR fallback on branch protection rejection

**Push logic (already implemented):**
- From worktree: `git push origin HEAD:$TRUNK`
- From non-worktree: simple `git push`

**Cleanup logic (needs changing):**
- `worktree-*` branches: skip removal, defer to ExitWorktree (SPEC-127)
- Other branches: `cd` to main repo, `git worktree remove --force`, `git worktree prune`
- **This cleanup must be replaced** — swain-sync should mark `ready_for_cleanup`, not remove

**Error handling (already implemented):**
- Merge conflicts: abort merge, report to operator, stop
- Push rejection (non-fast-forward): retry with re-fetch + re-merge
- Push rejection (branch protection): fall back to PR creation via `gh pr create`

**Lockfile awareness: none.** Zero references to lockfiles, `.agents/worktrees/`, or claiming/releasing.

### 3. Existing Lockfile Patterns in Codebase

**tk (ticket) claiming locks — proven pattern:**
- Location: `.tickets/.locks/<task-id>/owner` (contains PID)
- Mechanism: `mkdir` for atomic creation (directory creation is atomic on POSIX)
- Stale detection: `kill -0` on owner PID
- Cleanup: `crash-debris-lib.sh` detects stale locks; `tk close` releases
- Age threshold: >1 hour considered stale

**Git's own locking:**
- `index.lock`: per-worktree, detected by crash-debris-lib.sh
- Ref `.lock` files: internal to git, concurrent updates fail cleanly

**No `flock` usage in the codebase.** Explicitly rejected in ADR-011 (POSIX-local, doesn't fix the core merge problem).

### 4. Proposed Lockfile Format (from DESIGN-021)

```bash
version=1
pid=$$
user=$(whoami)
exe=$RUNTIME
pane_id=$PANE_ID
claimed_at=$(date -Iseconds)
worktree_path=$WORKTREE_PATH
purpose="$PURPOSE"
status=active
```

Shell-sourceable key=value format. `source "$lockfile"` loads all fields.

**ready_for_cleanup extension:**
- `ready_for_cleanup=true` — set by swain-sync after successful merge+push
- `ready_commit=<hash>` — HEAD at time of marking

**Location:** `.agents/worktrees/<branch>.lock`

**Atomic write:** temp file + `mv` (rename is atomic on POSIX). Consider `mkdir` as the claiming primitive (like tk) for creation-time atomicity.

### 5. swain-teardown Current Worktree Cleanup

- Reads bookmarked worktree paths from session.json `worktrees` array
- Lists physical worktrees via `git worktree list --porcelain`
- Classifies: protected (trunk), linked (bookmarked), orphan
- Safety rules for orphan removal: not current dir, no uncommitted changes, branch is merged, not trunk
- Requires operator confirmation
- **No lockfile awareness** — needs updating to check/clean `.agents/worktrees/*.lock`

### 6. Git Worktree Edge Cases

**Trunk diverged while worktree was working:**
Merge handles this correctly. `git merge origin/trunk` combines both sides, surfacing conflicts explicitly. This is the ADR-011 decision. Rebase could silently drop changes (the EPIC-038 failure).

**Two worktrees push to trunk simultaneously:**
Git ref `.lock` files ensure only one succeeds. The loser gets non-fast-forward rejection. swain-sync's retry loop handles this (re-fetch, re-merge, re-push, up to 3 attempts). Standard optimistic concurrency.

**`git worktree remove` from outside:**
Yes — takes a path argument, can be called from any location. This is how bin/swain should prune: `git -C "$MAIN_REPO" worktree remove "$WORKTREE_PATH"` after runtime exits.

**`git worktree lock`:**
Prevents pruning by `git worktree prune` or removal without `--force`. Could be a secondary safety mechanism alongside lockfiles, but serves a different purpose (git-level vs application-level).

**Index lock conflicts between worktrees:**
No — each worktree has its own index in `$GIT_DIR/worktrees/<name>/`. Independent `git add`/`git commit`.

### 7. Risks and Open Questions

**RISK 1 (Critical): bin/swain uses `exec`, never regains control.**
`eval exec "$cmd"` replaces the swain process with the runtime. Post-runtime cleanup (verify `ready_for_cleanup`, prune worktree) cannot happen. Options:
- Remove `exec`, run runtime as child process (needs signal forwarding)
- Use tmux hook or wrapper to run cleanup after pane command exits
- Separate `swain-cleanup` process

**RISK 2 (High): Shared stash is a collision vector.**
If two worktrees use `git stash` concurrently, operations can interleave. swain-sync uses labeled stash but `git stash pop` pops the top, not by label. Mitigation: use `git stash pop stash@{n}` with index lookup by label, or avoid stash entirely (commit dirty state instead).

**RISK 3 (Medium): `ready_for_cleanup` should be terminal.**
Between marking ready and bin/swain checking, the runtime could make additional commits. The `ready_commit` hash catches this, but should swain-sync refuse to run again after marking ready? Recommendation: yes — `ready_for_cleanup` is a terminal state. If the operator wants more work, they should clear the flag or start a new session.

**RISK 4 (Medium): Atomic lockfile creation race.**
Two processes could both check "no lockfile exists" and both create one. `mkdir` (used by tk) is truly atomic for creation. Recommendation: use `mkdir .agents/worktrees/<branch>.lock.d/` as the claiming primitive, write metadata inside the directory.

**RISK 5 (Low): swain-teardown needs lockfile awareness.**
Currently checks session.json bookmarks and git merge-base. Must also check/clean `.agents/worktrees/*.lock` to prevent drift between lockfile and bookmark systems.

### 8. Recommended Integration Design

**swain-sync changes:**
1. After successful merge+push, write `ready_for_cleanup=true` and `ready_commit=$(git rev-parse HEAD)` to the lockfile
2. Remove worktree removal logic entirely — do not `cd` to main repo, do not `git worktree remove`
3. Replace `worktree-*` branch heuristic with lockfile existence check

**bin/swain changes:**
1. After runtime exits (requires removing `exec`), check lockfile for `ready_for_cleanup=true`
2. Verify `ready_commit` matches current worktree HEAD (no new commits since marking)
3. If match: `git worktree remove` + delete lockfile
4. If mismatch: warn operator, offer re-entry or forced cleanup

**swain-teardown changes:**
1. Check `.agents/worktrees/*.lock` alongside session.json bookmarks
2. Apply stale detection (PID dead AND pane dead) to lockfiles
3. Clean stale lockfiles during orphan worktree cleanup

## Acceptance Criteria

- [x] **SPIKE-057-AC1: Git operations verified** — full matrix tested; merge, push, fetch, tag all work; stash is shared (risk); self-removal does not work (bin/swain handles from outside)
- [x] **SPIKE-057-AC2: Lockfile protocol defined** — DESIGN-021 format with ready_for_cleanup + ready_commit extension; atomic via mkdir or temp+mv
- [x] **SPIKE-057-AC3: bin/swain verification logic** — commit hash comparison; mismatch offers re-entry or forced cleanup
- [x] **SPIKE-057-AC4: Error handling tested** — merge conflicts abort without marking; push rejection retries; lockfile write failure warns but continues

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | — | Drafted for EPIC-056 |
| Complete | 2026-04-04 | — | Research complete; findings feed SPEC-244 (lockfile mgmt), SPEC-249 (sync integration), SPEC-252 (merge logic) |
