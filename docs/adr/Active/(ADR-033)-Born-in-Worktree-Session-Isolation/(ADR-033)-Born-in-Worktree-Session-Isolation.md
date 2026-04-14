---
title: "Born-in-Worktree Session Isolation"
artifact: ADR-033
track: standing
status: Active
author: cristos
created: 2026-04-05
last-updated: 2026-04-05
linked-artifacts:
  - EPIC-056
  - ADR-025
depends-on-artifacts: []
evidence-pool: ""
---

# Born-in-Worktree Session Isolation

## Context

Worktree isolation in swain is split across skills and the launcher. Each skill has guards that check if it runs on trunk. If so, it refuses to proceed or creates a worktree mid-session. `bin/swain` handles pre-launch isolation for external runtimes (Gemini CLI, Codex, Copilot, Crush) — those runtimes cannot change their working directory after launch. Claude Code sessions still do the "worktree dance" inside skill logic: check trunk, create a worktree, change directories.

This split creates several problems:

- **Duplicated guard logic** in every file-mutating skill.
- **Inconsistent enforcement** — a skill that forgets the guard can write to trunk.
- **Overhead for skill authors** who must understand isolation mechanics.
- **Two isolation models** that solve the same problem in different ways.

[EPIC-056](../../../epic/Proposed/(EPIC-056)-Session-Bookmark-Lifecycle-Integrity/(EPIC-056)-Session-Bookmark-Lifecycle-Integrity.md) established `bin/swain` as the primary isolation mechanism and proved the pre-launch model works for external runtimes. This ADR extends that model to all runtimes, including Claude Code.

## Decision

Every session starts inside its worktree. The launcher (`bin/swain`) creates or claims the worktree before the runtime starts. Skills never create, enter, or detect worktrees. They write files where they are — the cwd is always a worktree.

Merging happens outside the session. The operator merges via pull request or from trunk after the session ends. A session never merges its own branch.

One session, one worktree, one branch.

**Key design rules:**

1. **`bin/swain` is the single isolation gate.** All worktree creation, claiming, and cleanup flows through the launcher. No other component creates worktrees.

2. **Skills are worktree-unaware.** Skills write to their current directory. They do not check `SWAIN_WORKTREE_PATH`, detect trunk, or call `git worktree add`. Existing worktree guards in skills are removed.

3. **Merge is a post-session concern.** Sessions produce commits on a branch. Integration to trunk happens via PR (for reviewed work) or direct merge from trunk (for solo dev). The session runtime never runs `git merge` against trunk.

4. **Read-only investigation does not require a worktree.** The launcher offers a `--read-only` flag that skips worktree creation for sessions that only read files, run queries, or inspect state. If the session later needs to write, it must restart with a worktree.

5. **Trivial fixes get a fast path.** A `--quick` launcher flag creates an ephemeral worktree, applies the change, and offers to merge immediately after the session ends. This replaces the current "trivial fix on trunk" escape hatch with an isolated equivalent.

## Alternatives Considered

### Keep the distributed model

Keep the status quo. Skills detect trunk and create worktrees as needed. This requires no migration but ties skill authoring to isolation mechanics forever. Each new skill repeats the same guard logic or risks trunk writes.

### Worktree-per-task instead of worktree-per-session

A session could span multiple worktrees if it works on multiple specs. This gives finer isolation but adds complexity. Skills need to know when to switch worktrees. The session-branch mapping becomes many-to-many. For a solo developer, the added flexibility does not justify the cost.

### Hybrid model — skills detect but never create

Skills check `SWAIN_WORKTREE_PATH` and refuse to write if unset, but never create worktrees. This is simpler than today but still puts a guard in every skill. It treats the symptom (duplicated creation logic) without fixing the cause (skills knowing about isolation at all).

## Consequences

**Positive:**

- **Skill simplification.** Every file-mutating skill drops its worktree detection and creation logic. Skill authors write to cwd and trust the environment.
- **Single enforcement point.** Isolation correctness depends on one component (`bin/swain`), not every skill independently.
- **Uniform model.** All runtimes — Claude Code, Gemini CLI, Codex, Copilot, Crush — use the same pre-launch isolation. No special cases.
- **Cleaner teardown.** `swain-teardown` commits outstanding work, reports its branch, and optionally creates a PR. It does not merge or manage worktrees.

**Negative:**

- **Cross-session coordination.** Concurrent sessions can create artifact ID collisions and index conflicts. `next-artifact-id.sh` already scans all branches ([SPEC-193](../../../spec/Complete/(SPEC-193)-Artifact-ID-allocation-must-check-all-local-branches/(SPEC-193)-Artifact-ID-allocation-must-check-all-local-branches.md)), but index files (`list-*.md`) will diverge and need merge-time fixes.
- **No trunk escape hatch.** Every file mutation needs a worktree, even trivial ones. The `--quick` fast path helps but adds a launcher mode to maintain.
- **Session startup cost.** Investigation sessions that need to write must restart. The `--read-only` flag makes this explicit, but it's still friction.
- **Migration effort.** Skills with worktree guards need those guards removed. AGENTS.md needs updating. This is a one-time cost.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-05 | d2a8412a | Initial creation — formalizes born-in-worktree model |
