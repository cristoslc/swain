---
title: "Generalize Trunk Change Detection"
artifact: SPEC-149
track: implementable
status: Proposed
author: swain-design
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: low
type: enhancement
parent-epic: EPIC-041
parent-initiative: ""
linked-artifacts:
  - SPEC-148
  - ADR-011
depends-on-artifacts:
  - SPEC-148
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Generalize Trunk Change Detection

## Problem Statement

[SPEC-148](../../spec/NeedsManualTest/(SPEC-148)-Worktree-Discipline-For-Skill-Changes/(SPEC-148)-Worktree-Discipline-For-Skill-Changes.md) introduced `check-skill-changes.sh` to detect non-trivial skill file changes on trunk. However, the detection only covers `skills/`, `.claude/skills/`, and `.agents/skills/` directories. Non-trivial changes to other code-like files — project scripts (`scripts/*.sh`), standalone Python tooling, and test files outside skill directories — can still bypass worktree isolation without any advisory signal.

## Desired Outcomes

The advisory detection at session start covers all code-like files, not just skill directories. The operator sees a consistent warning whenever non-trivial code changes land on trunk without worktree isolation, regardless of file type. The same triviality threshold from SPEC-148 applies uniformly.

## External Behavior

### Expanded file coverage

`check-skill-changes.sh` (or a renamed successor) scans trunk commits for non-trivial diffs to any file matching:

- `skills/**` (already covered by SPEC-148)
- `.claude/skills/**` (already covered)
- `.agents/skills/**` (already covered)
- `scripts/**` (project-level automation)
- `**/*.sh` (shell scripts anywhere)
- `**/*.py` (Python scripts anywhere)
- `**/tests/**` (test files)

### Excluded paths

These paths are **not** code and should be exempt from detection even if diffs are large:

- `docs/**` (artifacts, retros, specs — these are documentation, not code)
- `.tickets/**` (task tracking state)
- `*.md` files outside skill directories (README, CHANGELOG, etc.)
- `AGENTS.md`, `CLAUDE.md` (managed by governance reconciliation)
- `**/*.json` (configuration, not logic — unless in `scripts/`)

### Triviality threshold

Same as SPEC-148: single file, ≤5 lines total diff, no structural changes. Applied uniformly to all covered file types.

### Warning format

```
⚠ Trunk commit <hash> <subject> touches code files with non-trivial changes.
  Non-trivial code changes should use worktree branches.
```

## Acceptance Criteria

**AC1 — Script detection:**
Given a trunk commit that adds a 20-line script to `scripts/new-tool.sh`,
When the check runs,
Then it emits the advisory warning.

**AC2 — Test file detection:**
Given a trunk commit that modifies a test file at `skills/swain-doctor/tests/test-foo.sh` with a 15-line diff,
When the check runs,
Then it emits the advisory warning.

**AC3 — Doc exemption:**
Given a trunk commit that adds a 200-line spec to `docs/spec/`,
When the check runs,
Then no warning is emitted.

**AC4 — Ticket exemption:**
Given a trunk commit that modifies `.tickets/*.md`,
When the check runs,
Then no warning is emitted.

**AC5 — Trivial code change passes:**
Given a trunk commit that fixes a typo in `scripts/swain-trunk.sh` (2-line diff),
When the check runs,
Then no warning is emitted.

**AC6 — Backward compatibility:**
Given the updated check script,
When SPEC-148's existing tests run,
Then all 5 tests still pass (no regressions).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- **In scope:** Extend check-skill-changes.sh (or replace with a broader check-trunk-changes.sh) to cover all code-like files. Update preflight integration if the script is renamed. Update governance principle if wording needs broadening.
- **Out of scope:** Hard gates, pre-commit hooks, changing the triviality threshold, modifying vendored skills.
- **Design decision:** Reuse the existing detection infrastructure from SPEC-148 rather than creating a parallel system. The script should be a clean extension, not a separate tool.

## Implementation Approach

1. **TDD cycle 1 (expanded tests):** Write tests for script detection, test file detection, doc exemption, ticket exemption, and trivial code pass-through. Run existing SPEC-148 tests as regression suite.

2. **TDD cycle 2 (script update):** Extend `check-skill-changes.sh` to scan for code-like file patterns beyond skill directories. Add exclusion logic for docs, tickets, and non-code markdown.

3. **TDD cycle 3 (governance update):** If the governance principle needs broadening from "Skill files" to "code-like files", update `AGENTS.content.md` and run reconciliation.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | — | Agent-suggested: generalizes SPEC-148 detection to all code-like files |
