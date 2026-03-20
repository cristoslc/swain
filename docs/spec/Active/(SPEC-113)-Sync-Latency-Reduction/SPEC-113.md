---
title: "Eliminate swain-sync context disruption"
artifact: SPEC-113
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Eliminate swain-sync context disruption

## Problem Statement

swain-sync blocks the operator's conversation thread for 60-90 seconds, breaking flow. The core problem is **context disruption** — the operator loses their train of thought while waiting for sync to complete. Two solution paths address this: (1) make sync fast enough that it doesn't break flow, or (2) make sync run safely in the background so the operator can continue working. Both paths are viable and complementary. However, safe backgrounding is non-trivial because the branch may be shared with other active sessions, and worktrees may be merging back to main concurrently.

## External Behavior

**Current:** Operator invokes /swain-sync, waits 60-90s for the sub-agent to complete all steps, loses train of thought.

**Desired:** Sync either completes fast enough to be unobtrusive, or runs in the background so the operator can continue working. Ideally both — fast AND backgrounded.

## Acceptance Criteria

- **Given** a sync invocation, **When** the operator triggers /swain-sync, **Then** it runs in the background and the operator can immediately continue working
- **Given** a background sync, **When** it completes, **Then** the operator is notified with a one-line summary (commit hash, files changed, push status)
- **Given** a background sync that encounters a conflict or hook failure, **Then** it surfaces the error clearly without losing the operator's staged changes
- **Given** another session has pushed to the same branch since the sync started, **When** the sync attempts to push, **Then** it re-fetches/rebases and retries (or fails cleanly without data loss)
- **Given** a worktree is merging back to main while sync is running on main, **Then** neither operation clobbers the other — both complete or one fails safely
- The advisory checks (ADR compliance, design drift) should be parallelized or deferred for speed, but their omission must not silently drop compliance signals

## Investigation Areas

1. **Concurrency on shared branches** — two sessions on the same branch can both stage/commit/push. Need a strategy: lock file, optimistic push with retry, or serialize via a queue. Git's own push rejection (non-fast-forward) is a natural guard, but the sync must handle it gracefully rather than failing opaquely
2. **Worktree merge coexistence** — when a worktree merges to main while sync is running on main, both operations modify the same ref. Need to define ordering: does sync yield to merge? Does it detect an in-progress merge and defer?
3. **Background-by-default** — sync always runs in background with a notification on completion. The operator must never be blocked
4. **Operator edits during sync** — if the operator changes files while sync is staging/committing in the background, the sync must not capture those mid-flight changes in its commit
5. **Reduce sub-agent overhead** — the sub-agent re-reads the full skill instructions every time. Could the sync steps be a shell script to cut overhead? (Secondary to the concurrency problems)
6. **Fast path** — /push as a lightweight alternative that skips advisory checks (already exists but may need refinement for background safety)

## Scope & Constraints

- Must not sacrifice safety (gitignore checks, hook execution) for background convenience
- Must preserve the commit message quality (conventional commits, Co-Authored-By)
- Background sync must handle concurrent modifications from the operator, other sessions on the same branch, and worktree merges
- Context disruption is the problem to solve — both latency reduction and safe backgrounding are valid solution paths

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Initial creation |
