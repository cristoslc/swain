---
title: "GitHub Issues Integration"
artifact: SPEC-005
status: Draft
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-epic: EPIC-002
linked-research: []
linked-adrs: []
depends-on:
  - SPEC-004
addresses:
  - JOURNEY-001.PP-01
evidence-pool:
swain-do: required
---

# GitHub Issues Integration

## Problem Statement

Work items that originate as GitHub Issues have no path into swain's artifact workflow. Users must manually recreate issue context as a SPEC or ignore the issue tracker entirely. This creates a split-brain problem: some work is tracked in GitHub, some in swain, with no linkage between them.

## External Behavior

**Inputs:**
- `gh issue list` output (filtered by repo, labels, state)
- User command to promote an issue to a SPEC: operator selects issue, swain-design creates a SPEC with `source-issue` frontmatter
- Artifact lifecycle transitions (Approved, Testing, Implemented, Abandoned)

**Outputs:**
- New `source-issue` frontmatter field on SPECs: `source-issue: github:<owner>/<repo>#<number>`
- Comments posted to GitHub issue on artifact transitions (e.g., "SPEC-004 transitioned to Testing")
- GitHub issue closed when linked SPEC reaches Implemented
- swain-status displays linked issues alongside artifacts

**Backend abstraction:**
- An `issue-backend` interface with operations: `list`, `get`, `comment`, `close`
- GitHub backend implemented via `gh` CLI
- Backend selected by convention: `source-issue: github:...` → GitHub backend
- Future backends (Linear, Jira) follow the same interface

**Preconditions:**
- `gh` CLI authenticated and available
- Repository has GitHub Issues enabled

## Acceptance Criteria

1. **Given** a GitHub Issue exists, **when** the user asks to promote it, **then** swain-design creates a SPEC with `source-issue: github:<owner>/<repo>#<number>` and the issue body populates the Problem Statement
2. **Given** a SPEC with `source-issue`, **when** it transitions to Testing, **then** a comment is posted to the linked GitHub issue
3. **Given** a SPEC with `source-issue`, **when** it transitions to Implemented, **then** the linked GitHub issue is closed
4. **Given** a SPEC with `source-issue`, **when** it transitions to Abandoned, **then** a comment is posted but the issue is NOT closed (abandoning a spec doesn't invalidate the issue)
5. **Given** `swain-status` runs, **when** there are SPECs with `source-issue`, **then** the issue number and title appear in the status output
6. **Given** a repo without `gh` CLI, **when** issue integration is attempted, **then** a clear error message appears (not a crash)
7. **Given** the backend interface, **when** a new backend is needed, **then** it can be added by implementing `list`, `get`, `comment`, `close` without modifying core swain-design logic

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- GitHub is the only backend implemented in this spec — Linear/Jira are future work
- Read-only listing of issues (surfacing in swain-status) does NOT require a SPEC — only promoted issues get the full artifact treatment
- Reverse direction (creating GitHub issues from swain artifacts) is out of scope
- The backend abstraction is a convention (URL-prefix dispatch), not a plugin architecture — keep it simple

## Implementation Approach

1. **TDD cycle 1 — source-issue field:** Add `source-issue` to SPEC template. Test: create SPEC with source-issue, verify frontmatter parses.
2. **TDD cycle 2 — issue promotion:** Implement `gh issue view` parsing → SPEC creation. Test: mock gh output, verify SPEC content.
3. **TDD cycle 3 — transition comments:** Hook into swain-design phase transitions to post comments via `gh issue comment`. Test: verify comment posted on transition.
4. **TDD cycle 4 — auto-close:** Hook Implemented transition to `gh issue close`. Test: verify close on Implemented, no close on Abandoned.
5. **TDD cycle 5 — swain-status integration:** Add issue display to status output. Test: verify linked issues appear.
6. **TDD cycle 6 — backend abstraction:** Extract GitHub-specific calls behind interface. Test: verify interface contract.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-12 | — | Initial creation |
