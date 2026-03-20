---
title: "Worktree Landing Via Merge With Retry"
artifact: ADR-011
track: standing
status: Proposed
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
supersedes: ADR-005
linked-artifacts:
  - ADR-005
  - SPIKE-022
  - SPEC-113
depends-on-artifacts:
  - ADR-012
evidence-pool: "multi-agent-collision-vectors"
---

# Worktree Landing Via Merge With Retry

## Context

[ADR-005](../Active/(ADR-005)-swain-sync-worktree-completion-workflow/(ADR-005)-swain-sync-worktree-completion-workflow.md) established a worktree completion workflow: rebase onto `origin/main`, then `git push origin HEAD:main`. On non-fast-forward rejection, the agent stops and reports.

During EPIC-038, two parallel worktree agents (SPEC-107, SPEC-108) both modified `roadmap.py`. SPEC-107 (sort-order) landed first. SPEC-108 (data model refactor) landed second. After both landed, SPEC-108's enrichment fields were missing from main — SPEC-107's changes were intact.

The SPEC-108 agent reported success with 12 passing tests in its worktree before landing. The retro does not record the exact git operations during landing. The most plausible mechanism: when SPEC-108 rebased onto post-107 main (ADR-005 step 2), git auto-resolved a region of `roadmap.py` by keeping the base (post-107) version, silently dropping 108's additions to that region. This is consistent with known rebase behavior — rebase can auto-resolve textual conflicts by favoring one side when the diff is clean enough. The agent's tests passed pre-rebase, not post-rebase, so the data loss was not detected.

We cannot prove this was the exact mechanism without the git reflog from that session. But the following properties of ADR-005's workflow are confirmed:

- The rebase step can produce a result different from what the agent tested, with no verification after rebase
- The recovery path on push rejection is to stop — there is no retry or merge fallback
- The agent reported success despite the data loss, meaning either rebase produced a fast-forwardable result (no rejection), or the agent continued past a rejection

Independently of the EPIC-038 root cause, swain is moving toward a swarming model where agents self-merge, making concurrent worktree completion the normal case rather than an edge case. This motivates revisiting the landing workflow. See [SPIKE-022](../../research/Active/(SPIKE-022)-Multi-Agent-Collision-Vectors/(SPIKE-022)-Multi-Agent-Collision-Vectors.md) for the full investigation.

Two questions follow:

1. **Merge or rebase?** Rebase can silently drop changes when replaying commits onto a new base. Merge combines both sides, surfacing textual conflicts explicitly. This is the primary decision.
2. **Retry or stop?** ADR-005 stops on push rejection. In a swarming model, stopping requires operator intervention on every concurrent completion. This is a secondary improvement.

## Decision

**Replace rebase with merge. Add retry on push rejection.**

### The workflow

When a worktree agent completes its work:

```
1. git fetch origin
2. git merge origin/main          # combine, don't rebase
3. run tests                      # verify integrated result
4. git push origin HEAD:main
5. if rejected (non-fast-forward):
     goto 1                       # re-fetch, re-merge, re-test, retry
6. on success: prune worktree
```

This is `git pull --no-rebase && git push` with a retry loop — the standard workflow when multiple people push to the same branch.

### Primary change: merge instead of rebase

This is what fixes the EPIC-038 failure class.

- **Merge preserves both sides.** Git's three-way merge combines the agent's changes with whatever landed on main since the agent branched. If both sides modified different regions of the same file, both are preserved. If they overlap textually, git raises a conflict — which is correct behavior. The agent should not silently resolve ambiguous cases.
- **Rebase can silently drop changes.** Rebase replays the agent's commits onto a new base. When the base has changed (another agent landed), the replay can auto-resolve textual conflicts by favoring one side, silently dropping the other's additions. This is the most plausible explanation for the EPIC-038 data loss.
- **Merge conflicts are explicit.** When merge cannot auto-resolve, it stops and reports a conflict. Rebase can auto-resolve in ways that produce a subtly different result. Explicit failure is better than silent data loss.
- **Rebase rewrites history.** In a swarming model, rewritten commit hashes break lifecycle stamps and cross-references between artifacts (see [ADR-012](../Active/(ADR-012)-Lifecycle-Hashes-Must-Be-Reachable-From-Main.md) — lifecycle hashes must be reachable from main).

### Secondary change: retry instead of stop

This enables swarming without operator intervention.

ADR-005 stops on push rejection. In a swarming model, this means every concurrent completion requires the operator to manually re-run the landing. The retry loop is the standard optimistic concurrency pattern: try, fail, update local state, retry. Git's ref lock ensures only one push succeeds at a time — contention resolves naturally.

**Retry bounds:** Maximum 3 attempts (configurable). No backoff needed — the merge+test cycle provides natural spacing. If contention persists beyond 3 retries, stop and report.

### What stays from ADR-005

- Step 1 (detect worktree context) — unchanged
- Step 4 (prune worktree after success) — unchanged
- Branch protection detection (fall back to PR creation) — unchanged
- swain-do owns worktree creation — unchanged

## Alternatives Considered

### A. Keep rebase, add flock-based serialization

Wrap ADR-005's rebase-push sequence in a file lock so only one agent lands at a time.

```bash
flock /tmp/swain-main.lock bash -c '
  git fetch origin && git rebase origin/main && git push origin HEAD:main
'
```

**Pros:**
- Minimal change to ADR-005
- Serialization eliminates the contention window

**Cons:**
- Does not fix the primary problem. Rebase can still silently drop changes even when serialized — if the base changed between the agent's last test and the rebase, the replayed result is untested and potentially incorrect.
- flock is POSIX-local: doesn't work across machines (remote dispatch)
- Serializes the entire rebase+push cycle — agents queue up waiting
- Keeps rebase's history rewriting

### B. Keep rebase, add an independent integration agent

A dedicated coordinator agent watches for completed worktree branches and serially rebases+pushes them.

**Pros:**
- Centralizes integration logic
- Serialization is implicit (single agent)

**Cons:**
- Does not fix the primary problem for the same reason as A — rebase can still silently drop changes
- Introduces a new agent role and single point of failure
- Moves toward hub-and-spoke, away from swarming
- More code to write and maintain

### C. Merge-then-push with retry (this decision)

Replace rebase with merge; add retry on rejection.

**Pros:**
- Fixes the primary problem: merge preserves both sides, conflicts surface explicitly
- Tests run on the merged result before push
- Uses git's own concurrency model — no external primitives
- Retry handles contention automatically
- Works identically for local and remote agents
- ~15 lines of shell

**Cons:**
- Merge commits add noise to git history (vs. rebase's linear history)
- If tests are slow, the retry loop wastes time re-running tests on each attempt
- Textually clean merges can still be semantically broken (tests are the only safety net for cross-file conflicts)
- Flaky tests cause false rejections in the retry loop

### D. Agents push branches, use git-hosting merge queue

Agents push their worktree branches and open PRs. The hosting platform's merge queue serializes integration.

**Pros:**
- Battle-tested infrastructure, uses merge (not rebase)
- Full CI pipeline on each merge
- Works for remote/distributed agents

**Cons:**
- Requires a specific git hosting platform — violates swain's runtime-agnostic principle
- Not available for local-only or air-gapped setups
- Adds network round-trip latency for every agent completion

## Consequences

**Positive:**
- Merge preserves both agents' changes — eliminates the class of silent data loss observed in EPIC-038
- Merge conflicts surface explicitly instead of being silently auto-resolved by rebase
- Tests on the merged result verify the integrated state before push
- Retry enables concurrent agent completion without operator intervention
- Standard git workflow — no new concepts, infrastructure, or external dependencies

**Accepted downsides:**
- Non-linear git history (merge commits). Acceptable — correctness is more important than linear history in a swarming model.
- Test suite must be reliable. Flaky tests cause retry loops and false rejections. This is a prerequisite, not a new risk — ADR-005 also assumed tests pass.
- Textually clean merges can still be semantically broken across files (e.g., Agent A changes `models.py`, Agent B changes `views.py` that imports from it). This is inherent to any merge-based approach — only the test suite can catch cross-file semantic conflicts.
- The retry loop adds latency under contention. For 2-4 concurrent agents with <60s test suites, worst case is bounded at ~3 minutes.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-20 | -- | Drafted from SPIKE-022 findings; supersedes ADR-005 |
