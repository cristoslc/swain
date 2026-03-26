---
title: "Gitignore Skill Folders Check"
artifact: SPEC-168
track: implementable
status: Active
author: operator
created: 2026-03-25
last-updated: 2026-03-25
type: enhancement
linked-artifacts:
  - ADR-015
swain-do: required
---

# Gitignore Skill Folders Check

## Problem Statement

When swain is installed into a consumer project, vendored skill folders (`.claude/skills/`, `.agents/skills/`) should not be committed to the consumer's repository. Today, swain-doctor has no check for this. If a consumer project lacks the appropriate `.gitignore` entries, skill dependencies silently end up in version control — bloating the repo and creating merge noise on skill updates.

The swain project itself is the exception: it tracks its own skill source code and must **not** gitignore these folders.

## Desired Outcomes

- Consumer projects are warned (and offered remediation) when skill folders are not gitignored.
- The swain project itself is detected and the check is skipped.
- The check follows the existing swain-doctor pattern: detection, status, remediation, reporting.

## External Behavior

### Detection

swain-doctor runs a new check: **Skill folder gitignore hygiene**.

1. **Self-detection**: determine whether the current project is swain itself. Signal: the `origin` remote URL contains `cristoslc/swain` (or the repo root contains `PURPOSE.md` with swain's identity marker). If self-detected, skip the check with status `skipped` and message: "Swain source repo — skill folders are tracked."

2. **Gitignore scan**: for each of these paths, check whether it is covered by `.gitignore`:
   - `.claude/skills/`
   - `.agents/skills/`

   Use `git check-ignore -q <path>` to test coverage. This respects nested `.gitignore` files and global gitignore config.

3. **Status**:
   - All paths ignored → `ok`
   - Some/all paths not ignored → `warning` with remediation offer

### Remediation

When paths are not ignored, offer to append the missing entries to the project's root `.gitignore`:

```gitignore
# Vendored swain skills (managed by swain-update)
.claude/skills/
.agents/skills/
```

If `.gitignore` doesn't exist, create it with those entries.

### Preflight integration

Add a lightweight check to `swain-preflight.sh`: if not the swain repo and `.claude/skills/` or `.agents/skills/` exists on disk but `git check-ignore -q` fails, emit an advisory (non-blocking).

## Acceptance Criteria

1. **Given** a consumer project with `.claude/skills/` not in `.gitignore`, **when** swain-doctor runs, **then** it reports a `warning` and offers to add the gitignore entry.

2. **Given** a consumer project with both `.claude/skills/` and `.agents/skills/` already gitignored, **when** swain-doctor runs, **then** the check reports `ok`.

3. **Given** the swain source repo (`origin` contains `cristoslc/swain`), **when** swain-doctor runs, **then** the check is `skipped` with an explanatory message.

4. **Given** a consumer project with no `.gitignore` file, **when** the operator accepts remediation, **then** a new `.gitignore` is created with the skill folder entries.

5. **Given** a consumer project where only one of the two paths is gitignored, **when** swain-doctor runs, **then** only the missing entry is offered for addition.

## Verification

| # | Criterion | Evidence | Result |
|---|-----------|----------|--------|
| 1 | Warning on missing gitignore | | |
| 2 | OK when already gitignored | | |
| 3 | Skipped in swain repo | | |
| 4 | Creates .gitignore if absent | | |
| 5 | Partial coverage detection | | |

## Scope & Constraints

- Detection must use `git check-ignore` (not string matching on `.gitignore` content) to respect nested and global gitignore rules.
- Self-detection should be robust: check remote URL first, fall back to `PURPOSE.md` marker.
- The check is advisory in preflight (non-blocking) and a `warning` in full doctor (not `error`).
- No changes to the swain repo's own `.gitignore`.

## Implementation Approach

1. Add a reference file `skills/swain-doctor/references/gitignore-skill-folders.md` documenting the check.
2. Add detection logic to swain-doctor's check sequence (after tool availability, before tk health).
3. Add a lightweight advisory to `swain-preflight.sh`.
4. Tests: shell script tests in `skills/swain-doctor/tests/` using temp git repos.

## Lifecycle

| Phase | Date | Hash |
|-------|------|------|
| Active | 2026-03-25 | |
