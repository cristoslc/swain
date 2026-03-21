---
title: "Commit Atomization in swain-sync"
artifact: SPEC-099
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: feature
parent-epic: EPIC-036
parent-initiative: ""
linked-artifacts:
  - SPEC-094
depends-on-artifacts:
  - SPEC-098
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Commit Atomization in swain-sync

## Problem Statement

swain-sync's commit step reads the entire staged diff, picks a single conventional-commit prefix based on "dominant change type," and creates one commit. A session where the agent transitioned SPEC-094 to Complete, fixed a bug in design-check.sh, and rebuilt the spec index produces:

```
docs: update specs, fix script, rebuild index
```

This obscures the logical structure. Worse, if a second session was also working on the same branch, its uncommitted changes get silently absorbed into the first session's commit with no attribution.

With SPEC-098's session-scoped action log available, swain-sync can produce:

```
docs(SPEC-094): transition to Complete
fix(design-check): correct path resolution for worktree detection
chore: rebuild spec index
```

Each commit is attributable to the session that produced it, reviewable, and revertable independently. Concurrent sessions' uncommitted work is left unstaged — they commit their own changes when they sync.

## External Behavior

### Commit grouping algorithm

When the current session's action log (`session.json .action_log.<SWAIN_SESSION_ID>.actions[]`) is non-empty, swain-sync replaces its single-commit step with:

1. **Read own actions** via `swain-bookmark.sh --read-actions` (returns only the current session's actions).
2. **Scope staged files to own session:** intersect each action's `files[]` with the set of currently staged files. Files claimed by the current session's actions are committed. **Files not claimed by any of the current session's actions are left unstaged** — they belong to another session or are uncommitted manual edits.
3. **Orphan collection:** Staged files that appear in `git diff --cached` but are NOT claimed by any action in any active session's log form an "orphan" group. Files claimed by another session's actions are NOT orphans — they are skipped entirely.
4. **Commit generation:** For each action group (chronological order, then orphans last):
   - Stage only that group's files (`git reset HEAD` then `git add <files>`).
   - Generate a commit message:
     - **Subject:** `<commit_prefix>(<scope>): <summary>` — prefix from action, scope from artifact ID or directory, summary from action summary (truncated to 72 chars).
     - **Body:** 1-2 lines if the summary was truncated, otherwise omit.
     - **Trailer:** `Co-Authored-By` as today.
   - Commit.
5. **Orphan commit:** prefix determined by file-path heuristics (existing swain-sync logic), summary: "sync uncommitted session changes."
6. **Clear own action log** via `swain-bookmark.sh --clear-actions` (clears only the current session's entry).
7. **Push** all commits at once (single push, multiple commits).

### File ownership rules

- A file claimed by the current session's actions → committed by this session.
- A file claimed by another session's actions (checked via `--list-sessions` + cross-session read) → **skipped**. That session is responsible for committing it.
- A file not claimed by any session → orphan, committed by this session (backward compatibility for non-action-emitting workflows).

### Fallback behavior

When the current session has no action log entry or `SWAIN_SESSION_ID` is unset, swain-sync falls back to its current single-commit behavior — stages and commits everything. No behavioral change for sessions that don't emit actions.

### Constraints

- **Atomic push:** all commits push together. If push fails, all commits are local and can be retried.
- **Pre-commit hooks run per commit.** If a hook rejects one commit, stop and report (consistent with current behavior).
- **File overlap:** if the same file appears in multiple actions, it is claimed by the **latest** action (last-writer-wins). This handles files that are touched multiple times during a session.
- **Empty groups:** if an action's files are all claimed by later actions, the action produces no commit (skip silently).
- **Gitignore hygiene and ADR compliance checks** run once before the commit loop, not per commit.
- **Index rebuilds** that swain-sync triggers itself should emit their own action (type: `index-rebuild`) before the commit loop begins, so the rebuild gets its own commit.

### Interaction with existing swain-sync steps

| Step | Change |
|------|--------|
| 1. Fetch/rebase | No change |
| 2. Survey | No change |
| 3. Stage | Stage everything initially (same as today) |
| 3.5 Gitignore | No change (runs once) |
| 3.7 ADR check | No change (runs once) |
| 3.8 Design check | No change (runs once) |
| **4. Commit** | **Replaced:** single commit → action-grouped multi-commit loop |
| 4.5 Pre-commit | Runs per commit in the loop |
| 5. Commit exec | Absorbed into step 4 |
| 6. Push | No change (pushes all commits) |
| 7. Verify | No change |
| Bookmark | Calls `--clear-actions` in addition to bookmark update |

## Acceptance Criteria

- **Given** a session with 3 actions logged (artifact transition, script fix, index rebuild) and matching staged files, **when** swain-sync runs, **then** 3 separate commits are created with correct prefixes and scopes.
- **Given** a session with actions but some action files are unstaged (reverted before sync), **when** swain-sync runs, **then** those actions produce no commit (empty group skip).
- **Given** a session with no action log, **when** swain-sync runs, **then** a single commit is produced (current behavior, no regression).
- **Given** `SWAIN_SESSION_ID` is unset, **when** swain-sync runs, **then** it falls back to single-commit behavior (no regression).
- **Given** a file appears in two of the current session's actions, **when** swain-sync groups commits, **then** the file is attributed to the latest action only.
- **Given** staged files not claimed by any session's actions, **when** swain-sync runs, **then** an orphan commit is created after all action commits.
- **Given** session A and session B both have actions, and session B modified `script.sh`, **when** session A runs swain-sync, **then** `script.sh` is NOT committed by session A (it is skipped, not orphaned).
- **Given** session A runs swain-sync and clears its actions, **when** session B later runs swain-sync, **then** session B's actions are intact and its files are committed correctly.
- **Given** a pre-commit hook rejects one commit in the loop, **when** the rejection occurs, **then** swain-sync stops, reports the failure, and does not clear the action log.
- **Given** the action log has a `commit_prefix` of `docs` for an artifact transition, **when** the commit is generated, **then** the commit subject starts with `docs(<artifact-id>):`.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Does NOT change swain-sync's fetch, rebase, staging, or push behavior.
- Does NOT implement action emission from skills — that is integration work done after both SPEC-098 and SPEC-099 are complete (or as part of SPEC-098 implementation).
- Does NOT resolve cross-session file conflicts — if two sessions both claim the same file via their action logs, git's normal merge/push conflict resolution applies. The second session to push will need to rebase.
- The commit grouping algorithm lives in the swain-sync SKILL.md instructions, not in a script — the agent performs the git operations. A helper script for reading/grouping actions may be added if the jq logic is complex enough to warrant it.
- Ordering guarantee: commits appear in git log in the same chronological order as actions were logged.
- Session isolation guarantee: a session never commits files claimed by another session's action log.

## Implementation Approach

1. **Modify swain-sync SKILL.md Step 4** — replace the single-commit instruction block with the multi-commit loop described above.
2. **Add a grouping helper** (`action-group.sh` or inline jq) that reads actions, intersects with staged files, and outputs ordered groups as JSON.
3. **Handle the git staging dance** — the tricky part is selectively staging per group. Approach: `git stash --keep-index`, then for each group: `git add <files>`, commit, repeat. Or: commit from a clean stage by resetting and re-adding per group.
4. **Test manually** by injecting actions into session.json and running swain-sync. Verify commit count, prefixes, and file attribution.
5. **Wire orphan handling** — reuse existing swain-sync commit message generation for the orphan group.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Initial creation |
