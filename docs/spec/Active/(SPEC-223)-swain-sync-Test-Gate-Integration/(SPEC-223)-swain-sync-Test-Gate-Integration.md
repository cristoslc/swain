---
title: "swain-sync test gate integration"
artifact: SPEC-223
track: implementable
status: Active
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: enhancement
parent-epic: EPIC-052
parent-initiative: ""
linked-artifacts:
  - EPIC-052
  - SPEC-221
  - SPEC-226
depends-on-artifacts:
  - SPEC-221
  - SPEC-226
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-sync test gate integration

## Problem Statement

swain-sync's Step 6 retry loop already has a placeholder comment: `# Run tests on the merged result before retrying push`. ADR-011 mandates tests before push. Neither has been implemented. The gate from SPEC-221 must be wired into swain-sync at the right step.

## Desired Outcomes

swain-sync invokes swain-test after every commit and before every push. On the worktree retry loop, it re-runs after each re-merge. Failures block the push.

## External Behavior

**Insertion point:** after commit (Step 5), before push (Step 6).

**New Step 5.5 in swain-sync:**
```
Step 5.5 — Test gate

Invoke swain-test. Pass --artifacts with any artifact IDs relevant to this sync session
(from the focus lane, recent tk tasks, or explicit operator context).

  .agents/bin/swain-test.sh [--artifacts SPEC-NNN,...]

If the gate exits 0: proceed to Step 6 (push).
If the gate exits 1 or Phase 2 fails: fix the issue and re-run from Step 5.5.
After 2 gate failures: escalate to operator before proceeding.

On success: include the Verified: annotation in the push commit message.
```

**Worktree retry loop (Step 6 retries):**
On each retry (fetch → re-merge → attempt push), re-run Step 5.5 before the push attempt. The re-merged state is new and must be re-verified.

**On trunk (no worktree):**
The gate runs identically. swain-test.sh detects the trunk context and uses `HEAD~1..HEAD` for diff.

## Acceptance Criteria

**Given** swain-sync is about to push from a worktree,
**When** Step 5.5 runs,
**Then** `swain-test.sh` is invoked before `git push`, and push does not proceed if the gate exits non-zero.

**Given** swain-sync enters the worktree retry loop after a rejected push,
**When** the next push attempt is made after re-merging,
**Then** Step 5.5 re-runs on the merged result before the push retry.

**Given** swain-sync runs directly on trunk (no worktree),
**When** Step 5.5 runs,
**Then** the gate still runs and the script uses `HEAD~1..HEAD` for diff.

**Given** the test gate passes,
**When** the commit message is assembled for push,
**Then** a `Verified:` annotation is included.

**Given** the SKILL.md for swain-sync is updated,
**When** read by an agent,
**Then** Step 5.5 appears clearly between Step 5 (commit) and Step 6 (push), with instructions matching this spec.

## Scope & Constraints

- This spec modifies only `skills/swain-sync/SKILL.md`.
- The existing Step 4.5 (pre-commit hook verification) is not changed.
- The push retry counter and error handling in Step 6 are not changed — the gate has its own failure/retry logic.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation; implements ADR-011 Step 3 placeholder |
