---
title: "swain-release test gate integration"
artifact: SPEC-224
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

# swain-release test gate integration

## Problem Statement

swain-release has a security gate (Step 5.5) and a README gate (Step 5.7) but no test gate. Releases often compile multiple worktrees for the first time — the integrated state is new and untested even if each worktree passed its own gate. A test gate before tagging catches integration-level failures that per-worktree tests cannot.

## Desired Outcomes

swain-release enforces the same two-phase test gate as swain-sync, as the final check before tag creation. All other gates pass first; test gate is last.

## External Behavior

**Insertion point:** after README gate (Step 5.7), before tag creation (Step 6).

**New Step 5.8 in swain-release:**
```
Step 5.8 — Test gate

Invoke swain-test. Pass --artifacts with any artifact IDs included in this release
(from the changelog, recent merged specs, or explicit operator context).

  .agents/bin/swain-test.sh [--artifacts SPEC-NNN,...]

If the gate exits 0: proceed to Step 6 (tag).
If the gate exits 1 or Phase 2 fails: fix the issue and re-run from Step 5.8.
After 2 gate failures: escalate to operator before proceeding.

On success: include the Verified: annotation in the release commit message.
```

**Note on re-running release gates:**
If the test gate fails and the agent fixes and re-runs, the security gate (5.5) and README gate (5.7) do not need to re-run — they are not affected by code changes that fix test failures. Only Step 5.8 repeats.

## Acceptance Criteria

**Given** swain-release is about to create a tag,
**When** Step 5.8 runs,
**Then** `swain-test.sh` is invoked after the README gate and before `git tag`, and tagging does not proceed if the gate fails.

**Given** the test gate passes,
**When** the release commit message is assembled,
**Then** a `Verified:` annotation is included.

**Given** the test gate fails and the agent fixes and re-runs,
**When** re-running,
**Then** only Step 5.8 re-runs — Steps 5.5 and 5.7 are not repeated.

**Given** the SKILL.md for swain-release is updated,
**When** read by an agent,
**Then** Step 5.8 appears clearly between Step 5.7 (README gate) and Step 6 (tag creation).

## Scope & Constraints

- This spec modifies only `skills/swain-release/SKILL.md`.
- Steps 5.5 (security gate) and 5.7 (README gate) are not changed.
- The tag creation and squash-merge steps (6, 6.5) are not changed.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
