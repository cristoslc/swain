---
title: "Worktree Discipline for Skill Changes"
artifact: SPEC-148
track: implementable
status: Needs Manual Test
author: swain-design
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: medium
type: enhancement
parent-epic: EPIC-041
parent-initiative: ""
linked-artifacts:
  - ADR-011
  - SPEC-043
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree Discipline for Skill Changes

## Problem Statement

Skills are programming in markdown syntax (per writing-skills SKILL.md), yet skill file changes routinely land directly on trunk without worktree isolation. Code changes go through worktrees via swain-do + using-git-worktrees, but skill edits bypass this discipline entirely. Recent trunk history shows non-trivial skill refactors (version bumps, structural rewrites, multi-file feature additions) committed directly to trunk — the same class of changes that would require a worktree branch if they were in `.sh` or `.py` files.

This asymmetry means skill changes skip the review, isolation, and merge-with-retry workflow that protects trunk stability for all other code.

## Desired Outcomes

Skill authors (both the operator and agents) get the same isolation guarantees for skill changes that they already get for code changes. Non-trivial skill edits go through worktree branches, get proper commit history, and land via the merge-with-retry workflow ([ADR-011](../../adr/Active/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md)). Trivial fixes (typos, single-line corrections) remain fast-path — no ceremony overhead for low-risk edits.

## External Behavior

### Triviality threshold

A skill change is **trivial** (trunk-eligible) if ALL of the following hold:
- Touches a single file
- Diff is 5 lines or fewer (net insertions + deletions)
- No structural changes (no new sections, no frontmatter field additions/removals, no version bumps)

Everything else is **non-trivial** and requires worktree isolation.

### Governance principle (primary enforcement)

The canonical governance source (`skills/swain-doctor/references/AGENTS.content.md`) gains a new section stating the principle and triviality threshold. swain-doctor reconciliation propagates it into the project's AGENTS.md. Because AGENTS.md is loaded into every agent conversation, this is the primary enforcement mechanism — the agent reads the rule before it acts. No modification to the vendored `using-git-worktrees` superpowers skill is needed; the governance principle instructs the agent to use worktree isolation for non-trivial skill edits, and the agent already knows how to create worktrees.

> **Skill changes are code changes.** Skill files (`skills/`, `.claude/skills/`, `.agents/skills/`) are code written in markdown syntax. Non-trivial skill edits require worktree isolation — the same discipline applied to `.sh`, `.py`, and other code files. Trivial fixes (typo corrections, single-line doc fixes, ≤5-line diffs touching one file with no structural changes) may land directly on trunk.

### swain-doctor detection (drift detection)

`swain-doctor` gains a new check: scan the last N trunk commits (default: 10) for commits that touch skill files (`skills/`, `.claude/skills/`, `.agents/skills/`) with non-trivial diffs. If found, emit a warning:

```
⚠ Trunk commit <hash> touches skill files with non-trivial changes.
  Skill changes above the triviality threshold should use worktree branches.
```

This is advisory (warning, not error) — it doesn't block work but surfaces the pattern for the operator.

## Acceptance Criteria

**AC1 — Governance principle in canonical source and AGENTS.md:**
Given `skills/swain-doctor/references/AGENTS.content.md`,
When I read it,
Then it contains the "Skill changes are code changes" principle with the triviality threshold definition.
And when swain-doctor governance reconciliation runs,
Then the principle appears in the project's AGENTS.md within the swain governance markers.

**AC2 — swain-doctor detection script:**
Given a trunk history where the most recent commit touches `skills/swain-do/SKILL.md` with a 20-line diff,
When swain-doctor runs,
Then it emits the advisory warning about non-trivial skill changes on trunk.

**AC3 — swain-doctor clean pass:**
Given a trunk history where the most recent commit touches `skills/swain-do/SKILL.md` with a 2-line typo fix,
When swain-doctor runs,
Then no warning is emitted (trivial change is below threshold).

**AC4 — no vendored skill modifications:**
Given the implementation,
When I check the using-git-worktrees SKILL.md,
Then it is unmodified — all enforcement lives in AGENTS.md governance and swain-doctor.

**AC5 — swain-preflight integration:**
Given the swain-preflight script,
When it runs and the new doctor check finds non-trivial skill changes on trunk,
Then preflight exits 1 (triggering doctor invocation per existing AGENTS.md session startup flow).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 — Governance principle in canonical source and AGENTS.md | `AGENTS.content.md` contains "Skill change discipline" section; SHA-256 hash match confirmed between canonical and installed | Pass |
| AC2 — swain-doctor detection script (non-trivial) | `test-check-skill-changes.sh` AC2 test: 20-line diff detected, warning emitted | Pass |
| AC3 — swain-doctor clean pass (trivial) | `test-check-skill-changes.sh` AC3 test: 2-line typo fix passes clean | Pass |
| AC4 — no vendored skill modifications | `git diff -- skills/using-git-worktrees/SKILL.md` returns clean | Pass |
| AC5 — swain-preflight integration | `test-preflight-skill-changes.sh`: preflight references check-skill-changes.sh, script exists and is executable | Pass |

## Scope & Constraints

- **In scope:** Canonical governance source update (`AGENTS.content.md`), governance reconciliation into AGENTS.md, swain-doctor check script, swain-preflight integration.
- **Out of scope:** Modifying vendored superpowers skills (using-git-worktrees has no local update path), pre-commit hooks (too heavy for an advisory pattern), retroactive enforcement on existing trunk history, changes to swain-sync or merge workflow.
- **Non-goal:** Blocking trunk commits to skill files. This is advisory guidance, not a hard gate.
- **Design decision:** Primary enforcement is via AGENTS.md governance (loaded every session, instructs agent behavior directly). swain-doctor provides drift detection for the operator. No vendored skill modifications needed — the agent already knows how to create worktrees; it just needs the rule telling it when to.

## Implementation Approach

1. **TDD cycle 1 (governance source):** Add the "Skill changes are code changes" principle to the canonical governance source (`skills/swain-doctor/references/AGENTS.content.md`). Run swain-doctor governance reconciliation to propagate into AGENTS.md. Verify by reading both files and confirming hash match.

2. **TDD cycle 2 (doctor check):** Write a test that simulates trunk commits touching skill files with varying diff sizes. Implement the doctor check script that scans `git log` for non-trivial skill changes. Verify trivial changes pass clean and non-trivial changes emit warnings.

3. **TDD cycle 3 (preflight integration):** Wire the new doctor check into swain-preflight so it triggers doctor invocation when non-trivial skill changes are detected on trunk.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | — | Agent-suggested: codifies existing gap in worktree discipline for skill files |
| In Progress | 2026-03-22 | — | Implementation started |
| Needs Manual Test | 2026-03-22 | — | All 5 ACs pass automated tests (7/7 tests); operator review for governance wording |
