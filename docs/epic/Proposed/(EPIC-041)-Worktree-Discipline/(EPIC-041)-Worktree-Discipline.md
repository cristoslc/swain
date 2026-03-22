---
title: "Worktree Discipline"
artifact: EPIC-041
track: container
status: Proposed
author: swain-design
created: 2026-03-22
last-updated: 2026-03-22
parent-vision: ""
parent-initiative: ""
priority-weight: medium
success-criteria:
  - Non-trivial skill file changes on trunk trigger an advisory warning at session start
  - Non-trivial code changes (scripts, tooling) on trunk trigger an advisory warning at session start
  - Governance principle in AGENTS.md instructs agents to use worktree isolation for non-trivial changes
  - Trivial fixes (typos, ≤5-line single-file diffs) remain trunk-eligible with no ceremony
  - No vendored superpowers skills are modified
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Worktree Discipline

## Goal / Objective

Establish consistent worktree isolation discipline for all code-like changes — not just `.sh` and `.py` files, but also skill files (markdown-as-code), scripts, and tests. Non-trivial changes should go through worktree branches and land via the merge-with-retry workflow ([ADR-011](../../adr/Active/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md)), while trivial fixes remain fast-path on trunk.

## Desired Outcomes

Agents and the operator get consistent isolation guarantees across all code-like file types. The advisory detection at session start surfaces drift when non-trivial changes bypass worktrees, creating a feedback loop that reinforces the discipline without hard-blocking trunk commits. The governance principle in AGENTS.md makes the rule explicit so agents self-enforce before swain-doctor needs to catch drift.

## Scope Boundaries

**In scope:**
- Governance principle establishing "skill changes are code changes" (and by extension, all code-like changes)
- Advisory detection in swain-doctor for non-trivial trunk commits touching skill files
- Generalized detection for non-trivial trunk commits touching any code files (scripts, tooling, tests)
- Preflight integration to surface findings at session start
- Triviality threshold definition (single file, ≤5 lines, no structural changes)

**Out of scope:**
- Hard gates or pre-commit hooks blocking trunk commits
- Modifying vendored superpowers skills (using-git-worktrees)
- Retroactive enforcement on existing trunk history
- Changes to the merge workflow (swain-sync, ADR-011)
- doc-only changes (specs, retros, ADRs) — these are artifacts, not code

## Child Specs

- [SPEC-148](../../spec/NeedsManualTest/(SPEC-148)-Worktree-Discipline-For-Skill-Changes/(SPEC-148)-Worktree-Discipline-For-Skill-Changes.md): Worktree Discipline for Skill Changes — governance principle, skill-file detection in swain-doctor, preflight integration. Status: Needs Manual Test.
- [SPEC-149](../../spec/Proposed/(SPEC-149)-Generalize-Trunk-Change-Detection/(SPEC-149)-Generalize-Trunk-Change-Detection.md): Generalize Trunk Change Detection — extend check-skill-changes.sh to detect non-trivial code changes beyond skill directories (project scripts, standalone tooling, test files). Status: Proposed.

## Key Dependencies

- [ADR-011](../../adr/Active/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md): Worktree Landing Via Merge With Retry — the merge workflow that worktree branches use to land on trunk.
- [SPEC-043](../../spec/Complete/(SPEC-043)-swain-do-automatic-worktree-creation/(SPEC-043)-swain-do-automatic-worktree-creation.md): swain-do automatic worktree creation — the existing mechanism for entering worktrees during implementation.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | — | Agent-suggested: wraps SPEC-148 and generalizes worktree discipline |
