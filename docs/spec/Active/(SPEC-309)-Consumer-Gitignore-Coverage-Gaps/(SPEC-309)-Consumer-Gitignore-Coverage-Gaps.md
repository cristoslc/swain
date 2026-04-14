---
title: "Consumer Gitignore Coverage Gaps"
artifact: SPEC-309
track: implementable
status: Active
author: operator
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: ""
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-168
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Consumer Gitignore Coverage Gaps

## Problem Statement

When swain is installed into a consumer project, several generated paths should be gitignored but coverage is incomplete. The init skill adds `.agents/bin/` and `.agents/session.json` to `.gitignore`, and [SPEC-168](../../Active/(SPEC-168)-Gitignore-Skill-Folders-Check/(SPEC-168)-Gitignore-Skill-Folders-Check.md) covers skill folders in doctor checks. However, the full set of swain-generated paths is not checked in a single place: doctor doesn't verify `.agents/bin/` or `.agents/session.json`, and init doesn't cover skill folders. A consumer project that runs doctor but skips init (or vice versa) can end up with swain internals committed to their repo.

## Desired Outcomes

- One consolidated gitignore check covers all swain-generated paths in consumer projects.
- Both doctor and init use the same path list so coverage can't drift.
- Consumer projects that install swain get clean repos without manual gitignore editing.

## External Behavior

### Paths to gitignore in consumer projects

All of these should be gitignored in consumer projects (not in swain's own repo):

| Path | Purpose | Currently checked by |
|------|---------|---------------------|
| `.claude/skills/swain/` | Vendored swain skills | SPEC-168 (doctor) |
| `.claude/skills/swain-*/` | Vendored swain skills | SPEC-168 (doctor) |
| `.agents/skills/swain/` | Vendored swain skills | SPEC-168 (doctor) |
| `.agents/skills/swain-*/` | Vendored swain skills | SPEC-168 (doctor) |
| `.agents/bin/` | Symlinked scripts | init only |
| `.agents/session.json` | Session state | init only |
| `.swain-init` | Init marker | init only |

### Consolidated check

Doctor and init should share a single canonical list of swain-generated paths. When doctor runs its gitignore check, it should verify all paths in the list (not just skill folders). When init sets up gitignore entries, it should use the same list.

### Self-detection

Same as SPEC-168: skip the check if the current project is swain itself (remote URL contains `cristoslc/swain`).

## Acceptance Criteria

1. **Given** a consumer project missing `.agents/bin/` from `.gitignore`, **when** swain-doctor runs, **then** it reports a warning and offers remediation.

2. **Given** a consumer project missing `.agents/session.json` from `.gitignore`, **when** swain-doctor runs, **then** it reports a warning and offers remediation.

3. **Given** a consumer project missing `.swain-init` from `.gitignore`, **when** swain-doctor runs, **then** it reports a warning and offers remediation.

4. **Given** a consumer project with all swain paths already gitignored, **when** swain-doctor runs, **then** the check reports `ok`.

5. **Given** swain-init runs on a consumer project, **when** it sets up `.gitignore`, **then** it adds all paths from the canonical list (not just `.agents/bin/` and `.agents/session.json`).

6. **Given** the swain source repo, **when** doctor or init runs, **then** the consumer gitignore check is skipped.

## Reproduction Steps

1. Install swain into a consumer project via `swain-init`.
2. Run `swain-doctor`.
3. Observe that `.agents/bin/` is in `.gitignore` (added by init) but doctor doesn't check for it.
4. Remove `.agents/bin/` from `.gitignore`.
5. Run `swain-doctor` again.
6. Doctor does not warn about the missing entry.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** Doctor checks all swain-generated paths in consumer projects. Init adds all swain-generated paths to gitignore. Both use the same list.

**Actual:** Doctor only checks skill folders (per SPEC-168). Init only adds `.agents/bin/`, `.agents/session.json`, and `.swain-init`. The lists are maintained independently and can drift.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- This spec subsumes SPEC-168's gitignore scope. SPEC-168 should be closed or merged into this spec when this is implemented.
- The canonical path list should live in a shared location (e.g., a config file or script) that both doctor and init read.
- Consumer project's own files in `.claude/skills/` or `.agents/skills/` must not be affected.
- Self-detection uses the same mechanism as SPEC-168 (`origin` remote URL).

## Implementation Approach

1. Create a shared gitignore path list (shell array or config file) in `.agents/bin/` or a doctor reference file.
2. Update the doctor gitignore check to use the full list instead of just skill folders.
3. Update init to use the same list instead of hardcoded paths.
4. Update existing tests and add tests for the new paths.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
