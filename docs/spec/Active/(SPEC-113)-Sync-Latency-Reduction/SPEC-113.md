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
linked-artifacts:
  - SPIKE-022
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

## Profiling Results (2026-03-20)

Measured on a typical changeset (3 changed files, main branch):

| Component | Time |
|-----------|------|
| Git operations (fetch, status, diff) | ~1.1s |
| Advisory checks (ADR compliance + design drift) | ~0.4s |
| Index rebuild (1 type) | ~1.8s |
| Gitignore, pre-commit, bookmark, misc | ~0.2s |
| **Measured total (shell work)** | **~3.5s** |
| Sub-agent startup + skill re-reading (estimated) | ~10-15s |
| LLM inference per tool-call round-trip × 12-15 steps | ~40-60s |
| **Estimated total (current architecture)** | **~55-80s** |

**Conclusion:** The bottleneck is agent overhead (12-15 sequential LLM round-trips), not git operations or checks. The actual work takes 3.5 seconds.

## Architecture: Hybrid Shell Script + Agent Escalation

### Determinism analysis

Every step in the current sync workflow is fully deterministic except:

1. **Commit message generation** — requires LLM inference to read the diff and produce a conventional-commit message with context-appropriate subject and body
2. **Push failure classification** — distinguishing branch protection rejection from diverged history requires interpreting git's stderr (locale-dependent, fragile across git versions)
3. **Secret detection** — the pattern list (`.env`, `*.pem`, `*_rsa`, `credentials.*`, `secrets.*`) is explicit, but the current "look like secrets" phrasing invites agent discretion beyond the list

### Design: commit queue + mechanical shell executor + agent escalation

The sync workflow splits into three phases with clear boundaries:

**Phase 1 — Agent prepares commit ticket (blocking, ~5-8s):**

The agent reads the working tree state, generates the commit message, and writes a structured commit ticket. This is the only phase that requires LLM inference. The agent's involvement ends here.

1. Read `git status --porcelain` to snapshot the file list
2. Read `git diff` for the changed files
3. Generate conventional-commit message from the diff
4. Run safety pre-checks that benefit from agent judgment (secret detection beyond the explicit pattern list)
5. Write a commit ticket to the queue directory

**Commit ticket format** (`.swain/sync-queue/<timestamp>-<short-hash>.ticket`):

```yaml
created: 2026-03-20T14:32:01Z
branch: main
worktree: no
files:
  - docs/spec/Active/(SPEC-113)-Sync-Latency-Reduction/SPEC-113.md
  - skills/swain-sync/SKILL.md
message: |
  feat(swain-sync): add commit queue for background sync

  Splits sync into agent-prepared tickets and a mechanical shell executor
  to eliminate context disruption during sync operations.

  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
advisory-checks: true   # run ADR compliance + design drift
skip-fetch: false        # operator can override for speed
```

**Phase 2 — Shell executor processes queue (backgrounded, ~5-10s):**

A mechanical shell script processes tickets FIFO. No LLM involvement. The agent spawns this in the background and returns control to the operator immediately.

For each ticket:
1. Fetch and rebase upstream (with stash if dirty)
2. Stage only the files listed in the ticket (concurrent edit safety — snapshot is authoritative)
3. Run gitignore check (blocking — deterministic pattern matching)
4. Run advisory checks if `advisory-checks: true` (ADR compliance, design drift — parallel)
5. Rebuild stale indexes (parallel by type)
6. Run pre-commit hooks
7. Commit with the message from the ticket
8. Push (with one retry on non-fast-forward: fetch + rebase + push)
9. Update session bookmark
10. Write result file (`.swain/sync-queue/<ticket>.result`) with outcome, commit hash, advisory findings
11. Remove processed ticket

**Phase 3 — Agent escalation on failure:**

If any step exits non-zero, the shell script writes the failure to the result file and stops processing that ticket (subsequent tickets remain queued). The next time an agent is active in the session, it checks for failed results and handles them with full judgment:

- Exit 1: rebase conflict → agent reports conflicting files, asks operator
- Exit 2: gitignore violation → agent reports missing patterns, asks operator to fix
- Exit 3: pre-commit hook failure → agent parses hook output, reports findings
- Exit 4: push rejected after retry → agent distinguishes protection vs. divergence, creates PR if needed
- Exit 5: fetch failed → agent reports network issue

This keeps ~90% of syncs fully backgrounded and mechanical. The ~10% that hit edge cases get agent judgment on the next interaction.

### Queue semantics

- **FIFO processing** — tickets are processed in creation order by timestamp prefix
- **Single-writer safety** — the shell executor holds a lock file (`.swain/sync-queue/.lock`) while processing. A second executor instance (from another session) waits or skips
- **Shared-branch concurrency** — two sessions enqueue tickets independently. The lock serializes execution. Git's non-fast-forward rejection + retry handles the case where another session pushed between enqueue and execution
- **Worktree coexistence** — worktree tickets specify `worktree: yes` and push to `origin HEAD:main`. The lock prevents simultaneous pushes to main from worktree and main-worktree executors
- **Stale ticket cleanup** — tickets older than 1 hour with no result file are considered abandoned and logged as warnings

### Open design questions

1. **Advisory output delivery** — result files capture advisory findings, but how does the operator see them? Options: (a) the agent checks results on next interaction, (b) swain-status surfaces unread results, (c) a hook notifies on result file creation
2. **Queue directory location** — `.swain/sync-queue/` is gitignored project-local state. Alternative: `~/.swain/sync-queue/<repo-hash>/` for cross-project consistency
3. **Ticket file format** — YAML shown above for readability. Could also be a flat key=value format for easier shell parsing without a YAML dependency
4. **Index rebuild parallelization** — currently serial at ~1.8s per type. Running changed types in parallel with `&` + `wait` cuts this to ~1.8s total regardless of type count
5. **Executor invocation** — who starts the shell executor? Options: (a) the agent spawns it via `run_in_background` after writing the ticket, (b) a filesystem watcher triggers it, (c) a cron job polls the queue. Option (a) is simplest

## Scope & Constraints

- Must not sacrifice safety (gitignore checks, hook execution) for speed or background convenience
- Must preserve commit message quality (conventional commits, Co-Authored-By)
- Context disruption is the problem to solve — both latency reduction and safe backgrounding are valid, complementary solution paths
- Agent involvement is limited to ticket preparation (Phase 1) — the executor is purely mechanical
- Error/edge cases are deferred to agent judgment on next interaction, not handled by brittle shell parsing
- Secret detection uses both the explicit pattern list (shell) and agent judgment (Phase 1) — the agent catches unusual secrets before writing the ticket
- The commit ticket is the contract between agent and executor — the file list is authoritative and prevents concurrent edit capture

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Initial creation |
