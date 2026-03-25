---
title: "Worktree Isolation By Default In swain-do"
artifact: SPEC-165
track: implementable
status: Active
author: operator
created: 2026-03-24
last-updated: 2026-03-24
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree Isolation By Default In swain-do

## Problem Statement

swain-do currently gates worktree isolation on whether the operation is "implementation/execution" — meaning it skips isolation for artifact-only changes (docs, specs, skill files). This creates a false distinction. Any file mutation on trunk risks:

1. **Half-finished changes polluting trunk** — an interrupted session leaves partial artifact edits on the development branch.
2. **Collision with parallel agents** — two sessions editing different skill files or specs on trunk can produce merge conflicts.
3. **Governance violation** — AGENTS.md already states "non-trivial skill edits require worktree isolation," but swain-do doesn't enforce this for skill file changes routed through task execution.

The root issue: swain-do treats "implementation" as synonymous with "source code changes" when it should mean "any mutating work tracked by a task."

## Desired Outcomes

Every mutating task tracked by swain-do executes in an isolated worktree, regardless of what files it touches. The operator gets a clean trunk that only contains completed, committed work. Parallel sessions can operate without coordination overhead.

## External Behavior

**Current behavior:** swain-do's worktree isolation preamble checks `IN_WORKTREE` and enters a worktree only when the operation is classified as "implementation/execution." Read-only operations (tk ready, status checks) and artifact-only work may proceed on trunk.

**Desired behavior:** swain-do enters a worktree for ALL task execution that will produce file changes — including artifact creation/editing, skill file changes, spec transitions, and source code implementation. The only operations that remain on trunk are purely read-only: `tk ready`, `tk status`, `tk list`, status checks, and plan inspection.

## Acceptance Criteria

1. **Given** a swain-do task that modifies any file (artifact, skill, source code, script, data),
   **When** swain-do begins execution on trunk (not already in a worktree),
   **Then** swain-do enters a worktree via `EnterWorktree` before making changes.

2. **Given** a swain-do operation that is purely read-only (`tk ready`, `tk status`, `tk list`, plan inspection),
   **When** swain-do begins execution on trunk,
   **Then** swain-do does NOT enter a worktree (no isolation overhead for reads).

3. **Given** the operator is already in a worktree,
   **When** swain-do begins any task,
   **Then** swain-do skips worktree creation and proceeds in the existing worktree.

4. **Given** the operator explicitly says "work on trunk" or "don't isolate",
   **When** swain-do begins execution,
   **Then** swain-do respects the override and proceeds on trunk with a warning.

## Reproduction Steps

1. Start a session on trunk (no worktree).
2. Invoke swain-do with a task that only modifies artifact files (e.g., "update SPEC-100 frontmatter").
3. Observe: swain-do proceeds on trunk without entering a worktree.
4. Interrupt the session mid-edit.
5. Observe: trunk has partial changes.

## Severity

medium — No data loss, but violates the isolation principle and creates merge friction for parallel agents.

## Expected vs. Actual Behavior

**Expected:** swain-do enters a worktree for any task that will modify files, including artifact-only tasks.

**Actual:** swain-do only enters a worktree for tasks classified as "implementation/execution," allowing artifact-only tasks to proceed on trunk.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

### In scope

- Modifying swain-do's worktree isolation preamble to treat all mutating tasks uniformly.
- Ensuring the read-only exception list is explicit and minimal.
- Documenting the operator override escape hatch.

### Out of scope

- Changing how swain-session auto-isolates at startup (it already enters a worktree).
- Modifying other skills' worktree behavior.
- Changing the worktree creation mechanism itself (EnterWorktree tool).

### Trunk-safe skill analysis

The following analysis classifies which skills can and SHOULD work directly on trunk vs requiring worktree isolation:

**MUST work on trunk (read-only or session-infrastructure):**

| Skill | Rationale |
|-------|-----------|
| swain-session | Session startup infrastructure — sets tab name, detects focus, auto-enters worktree. Must run on trunk to bootstrap. |
| swain-doctor | Health checks and remediation — needs to see trunk state. Idempotent. |
| swain-status | Read-only dashboard aggregation. |
| swain-help | Read-only help text. |
| swain-stage | Tmux layout management — no file mutations in the repo. |
| swain-keys | SSH key provisioning — writes to `~/.ssh/`, not the repo. |
| using-git-worktrees | Creates worktrees — must run before isolation exists. |
| systematic-debugging | Diagnostic investigation — reads files, runs tests. |

**SHOULD work in worktree (mutating):**

| Skill | Rationale |
|-------|-----------|
| swain-do | Task execution — the subject of this spec. |
| swain-design | Creates/transitions artifacts — file mutations. |
| swain-search | Creates trove files under `docs/troves/`. |
| swain-retro | Writes retrospective sections into EPIC artifacts. |
| swain-sync | Commit + push — already worktree-aware. |
| swain-release | Tag + version bump + squash-merge — already worktree-aware. |
| swain-update | Pulls new skill files — writes to `skills/`, `.claude/skills/`. |
| swain-init | Onboarding writes — AGENTS.md, hooks, `.agents/`. |
| writing-plans | Produces plan files — already requires worktree. |
| executing-plans | Implementation — already requires worktree. |
| subagent-driven-development | Implementation — already requires worktree. |
| brainstorming | Produces design docs — file mutations. |
| test-driven-development | Writes tests and code — used within worktrees. |
| writing-skills | Skill file edits — AGENTS.md governance requires isolation. |
| push | Commit + push — operates on whatever branch it's on. |
| finishing-a-development-branch | Merge/cleanup — already worktree-aware. |

**Context-dependent (safe either way):**

| Skill | Rationale |
|-------|-----------|
| swain-roadmap | Regenerates ROADMAP.md — a derived file. Trunk-safe because it's idempotent and fully regenerated. |
| swain-security-check | Runs scanners — read-only analysis, but may produce a report file. |
| requesting-code-review | Read-only analysis of diffs. |
| receiving-code-review | May produce code changes in response — should be in worktree if implementing fixes. |
| verification-before-completion | Runs verification commands — read-only. |

## Implementation Approach

1. Modify swain-do's worktree isolation preamble to check whether the operation will produce file changes (any `tk` task in `ready` or `in-progress` state), rather than whether it's classified as "implementation."
2. Define an explicit allowlist of read-only operations that skip isolation: `tk ready`, `tk status`, `tk list`, `tk show`, plan inspection.
3. Add the operator override: if the user says "work on trunk" or "don't isolate," proceed with a warning log.
4. Update swain-do's SKILL.md to document the new default.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-24 | -- | Initial creation |
