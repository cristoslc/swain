---
title: "Gitignore .swain/session/ in consumer projects"
artifact: SPEC-305
track: implementable
status: Active
author: cristos
created: 2026-04-12
last-updated: 2026-04-13
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-002
linked-artifacts:
  - SPEC-290
  - INITIATIVE-002
  - ADR-041
  - ADR-042
  - SPIKE-071
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Gitignore .swain/session/ in consumer projects

## Problem Statement

Swain runtime state lives under `.swain/` (per [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md)). Most of `.swain/` is project-level state that belongs in every worktree — `bin/` symlinks, gate markers, caches, `specwatch-ignore`. Only `.swain/session/` (per-operator session state like `session.json`, purpose, focus lane) is session-bound and should not be versioned. Consumer projects need to ignore `.swain/session/` and only `.swain/session/`. The rest of `.swain/` must be tracked so worktrees boot without a doctor gap.

[ADR-042](../../../adr/Active/(ADR-042)-Track-Runtime-And-Peer-Agent-Dirs-Instead-Of-Symlinking.md) established that all runtime and peer-agent dirs are tracked. No gitignored directories need symlinking. Worktrees get everything they need from git. No post-checkout hook is needed. This means `.swain-init` is also tracked. The gitignore block covers only `.swain/session/`.

## Desired Outcomes

- Consumer `.gitignore` includes `.swain/session/` only. The rest of `.swain/` is tracked. `.swain-init` is tracked. Peer-agent dirs are tracked.
- Operators never commit per-session state by accident. Project-level state is versioned.
- No worktree appears "uninitialized" or loses access to scripts. Tracked files appear in worktrees via git automatically.

## External Behavior

**swain-init gitignore block.** swain-init proposes a managed block for the consumer's `.gitignore`. The block contains:

1. `.swain/session/` — the only gitignored path under `.swain/`. Everything else in `.swain/` is tracked project-level state (bin symlinks, gate markers, caches, specwatch-ignore). See [SPIKE-071](../../../research/Complete/(SPIKE-071)-Trafilatura-Content-Extraction/(SPIKE-071)-Trafilatura-Content-Extraction.md) section 8 for the track-vs-ignore breakdown.

Marker comments delimit the block. The markers are `# >>> swain managed >>>` and `# <<< swain managed <<<`. Before any write, swain-init shows the operator the exact lines it plans to add or change and asks for confirmation. A non-interactive override flag exists for CI and scripted installs. Upgrades to an existing block work the same way: diff first, confirm, then write. The operator can decline, accept as-is, or edit the list.

Peer-agent dot-folders are not included. Per [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md), swain does not impose an ignore policy for `.claude/`, `.cursor/`, `.aider/`, `.goose/`, and similar. Per [ADR-042](../../../adr/Active/(ADR-042)-Track-Runtime-And-Peer-Agent-Dirs-Instead-Of-Symlinking.md), peer-agent dirs are tracked by default. The consumer decides whether to ignore any of them.

**Remove inline symlinking.** `bin/swain` `create_session_worktree()` currently symlinks skill dirs, `.swain-init`, and peer-agent dirs into worktrees. Since all of these are now tracked, the symlinking blocks are dead code. Remove them.

**Remove swain-doctor symlink repair.** Check 12 and the [SPEC-290](../(SPEC-290)-swain-init-not-symlinked-into-pre-existing-worktrees/(SPEC-290)-swain-init-not-symlinked-into-pre-existing-worktrees.md) repair pass symlink missing dirs into worktrees. With all dirs tracked, this is dead code. Remove it.

**Doctor migration check.** swain-doctor detects a stale `.agents/` directory or an old `.agents/`-based gitignore block. On detection, it offers to move runtime files (`.agents/bin/`, `.agents/session.json`, `.agents/hook-state/`, `.agents/chart-cache/`, `.agents/search-snapshots/`, `.agents/specwatch-ignore`) to `.swain/` equivalents, update the gitignore block (`.agents/` → `.swain/session/`), and track `.swain/` and `.swain-init`. This replaces the old bin-auto-repair and gitignore-skill-folders checks. swain-init runs doctor at the end of onboarding, so init gets migration for free.

## Acceptance Criteria

**Given** a consumer project with no managed gitignore block,
**When** the operator runs `/swain-init`,
**Then** swain-init shows the proposed block containing `.swain/session/` only and asks for confirmation. On accept, the block is appended. On decline, nothing is written. Re-runs that find an identical block are no-ops.

**Given** a consumer project with an older managed block that includes `.swain-init`,
**When** the operator runs `/swain-init` or `/swain-doctor`,
**Then** a diff of the planned change is shown and confirmation is requested. `.swain-init` is removed from the block. On accept, the block upgrades in place. Rules outside the markers stay untouched.

**Given** a non-interactive install with the override flag,
**When** swain-init runs,
**Then** the write proceeds without a prompt. A record of what changed appears in the output.

**Given** `bin/swain` creates a worktree,
**When** `create_session_worktree()` runs,
**Then** no symlinking of skill dirs, `.swain-init`, or peer-agent dirs occurs. The function creates the worktree only.

**Given** a linked worktree,
**When** `swain-doctor` runs,
**Then** no symlink repair is attempted. Check 12 and the SPEC-290 repair pass are removed.

**Given** a consumer project with a stale `.agents/` directory and an old `.agents/` gitignore block,
**When** `swain-doctor` runs (or swain-init triggers it),
**Then** doctor detects the stale state, shows the migration plan (move files to `.swain/`, rewrite gitignore to `.swain/session/`), and asks for confirmation. On accept, migration runs. On decline, a warning is logged.

## Verification

<!-- Populated when entering Testing phase. Maps each acceptance criterion
     to its evidence: test name, manual check, or demo scenario.
     Leave empty until Testing. -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope.**

- Consumer gitignore writer in swain-init. Shows a diff and asks before writing. Idempotent on re-runs. Covers `.swain/session/` only. The rest of `.swain/` is tracked.
- Remove `create_session_worktree()` symlinking blocks (skill dirs, `.swain-init`, peer-agent dirs).
- Remove swain-doctor symlink repair (check 12 and SPEC-290 repair pass).
- Doctor migration check: detect stale `.agents/`, offer to move files to `.swain/`, rewrite gitignore block. Runs in doctor and at end of swain-init.

**Out of scope.**

- The `.agents/` to `.swain/` migration itself. That is a separate SPEC driven by [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md). This SPEC assumes `.swain/` is already the canonical path and that `.swain/session/` is the only gitignored subpath.
- Gitignoring peer-agent dot-folders in consumer projects. [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md) rules this out.
- Gitignoring the full `.swain/` directory. Only `.swain/session/` is ignored. The rest is tracked project-level state.
- Migrating already-committed runtime files in consumer history. That is a separate cleanup SPEC.
- Tracked config files like `AGENTS.md` and `CLAUDE.md`. Those stay tracked.
- A post-checkout hook or `core.hooksPath` configuration. Not needed. See [ADR-042](../../../adr/Active/(ADR-042)-Track-Runtime-And-Peer-Agent-Dirs-Instead-Of-Symlinking.md).

**Constraints.**

- swain-init must never write to `.gitignore` without operator confirmation. CI needs an explicit override flag.
- Markers must delimit the managed block. Operators need to see what is swain-managed.
- No `core.hooksPath` configuration is written by swain. No hook is installed.

## Implementation Approach

Four TDD cycles, in dependency order. Assumes the `.agents/` to `.swain/` migration (separate SPEC per [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md)) has landed first.

1. **Write the consumer gitignore block** in swain-init. Show the diff, ask for confirmation, honor accept or decline. Support the non-interactive override flag. Test: clean repos get the block appended after accept. Decline leaves the file alone. Re-runs are no-ops. Older blocks (with `.swain-init`) upgrade in place after accept. Rules outside the markers survive.
2. **Remove `create_session_worktree()` symlinking.** Delete the skill dir, `.swain-init`, and peer-agent dir symlink blocks. Test: worktree creation still succeeds. Worktree has access to tracked files via git.
3. **Remove swain-doctor symlink repair.** Delete check 12 and the SPEC-290 repair pass. Test: swain-doctor runs without error. No symlink repair is attempted.
4. **Doctor migration check.** New check that detects stale `.agents/` and old gitignore blocks. On confirmation, moves runtime files to `.swain/`, rewrites gitignore, and tracks new paths. Test: a project with `.agents/` on disk migrates cleanly. Decline logs a warning. swain-init gets migration for free since it runs doctor at the end.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-12 | — | Initial creation |
| Active | 2026-04-13 | — | Rescoped to `.swain/` after [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md); parent set to INITIATIVE-002 |
| Active | 2026-04-13 | — | Rescoped: track `.swain/` except `.swain/session/` (per [SPIKE-071](../../../research/Complete/(SPIKE-071)-Trafilatura-Content-Extraction/(SPIKE-071)-Trafilatura-Content-Extraction.md) section 8); full-directory ignore removed |
| Active | 2026-04-13 | — | Hook removed per [ADR-042](../../../adr/Active/(ADR-042)-Track-Runtime-And-Peer-Agent-Dirs-Instead-Of-Symlinking.md); `.swain-init` removed from gitignore block; inline symlinking and hook sections deleted; replaced with remove-symlinking cleanup work |