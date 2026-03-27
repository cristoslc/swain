---
title: "allowed-tools hygiene sweep"
artifact: SPEC-077
track: implementable
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: enhancement
parent-epic: EPIC-031
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# allowed-tools hygiene sweep

## Problem Statement

The audit found two categories of allowed-tools issues across swain skills:

1. **Missing interactive tools:** swain-retro, swain-search, swain-keys, and swain-release require interactive user confirmation but don't list `AskUserQuestion` in allowed-tools. Agents must embed questions in response text, which is less reliable for structured interaction.

2. **Missing worktree tools:** swain-do and swain-session list `EnterWorktree` but not `ExitWorktree`. No skill provides guidance on when or how to exit a worktree, risking agents stranded in worktrees across skill invocations.

3. **Inconsistent declarations:** swain (meta-router) has no allowed-tools at all. swain-push lists `Edit` but only needs `Skill`. Several skills list tools they never use (swain-update lists `Write, Edit, Grep, Glob` but only uses `Bash`).

## External Behavior

Every SKILL.md's `allowed-tools` field lists exactly the tools the skill actually uses — no more, no less. Interactive skills include `AskUserQuestion`. Skills that enter worktrees include both `EnterWorktree` and `ExitWorktree` with guidance on when to exit. Skills that chain to other skills include `Skill`.

## Acceptance Criteria

**AC-1:** `AskUserQuestion` added to allowed-tools for swain-retro, swain-search, swain-keys, and swain-release.

**AC-2:** `ExitWorktree` added to allowed-tools for swain-do and swain-session, with guidance text on when to exit (e.g., "after all tasks complete" or "when returning to main checkout").

**AC-3:** Every skill's allowed-tools matches its actual tool usage — no unused tools listed, no used tools missing.

**AC-4:** Skills that invoke other skills via the Skill tool list `Skill` in allowed-tools (swain-help, swain-init, swain meta-router).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | Check frontmatter of 4 skills | |
| AC-2 | Check swain-do and swain-session frontmatter + body text | |
| AC-3 | Cross-reference allowed-tools vs. body for all 18 skills | |
| AC-4 | Check skills that chain | |

## Scope & Constraints

**In scope:** `allowed-tools` frontmatter field and ExitWorktree guidance text in all SKILL.md files.

**Out of scope:** Changing skill logic or tool usage patterns. Only aligning declarations with reality.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from audit theme #3 and #4 |
