---
title: "Control Thread Worktree and Session Spawning"
artifact: SPEC-298
track: implementable
status: Active
author: "gemma4:31b-cloud"
created: 2026-04-07
last-updated: 2026-04-18
priority-weight: high
type: feature
parent-epic: EPIC-071
parent-vision: VISION-006
linked-artifacts:
  - [EPIC-071](../../../epic/Active/(EPIC-071)-Project-Bridge-Kernel/(EPIC-071)-Project-Bridge-Kernel.md)
  - [VISION-006](../../../vision/Active/(VISION-006)-Untethered-Operator/(VISION-006)-Untethered-Operator.md)
  - [JOURNEY-004](../../../journey/Active/(JOURNEY-004)-Fire-And-Forget/(JOURNEY-004)-Fire-And-Forget.md)
addresses:
  - "[SPEC-195](../(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch/(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch.md)"
swain-do: required
---

# Control Thread Worktree and Session Spawning

## Problem Statement

Control threads in Zulip streams/topics should be able to trigger worktree creation and opencode session spawning. The project bridge is a persistent daemon per project — it manages multiple worktrees and sessions, not one per worktree. The operator wants to start implementation work from a phone by messaging the control thread.

NOTE (2026-04-18): Worktrees are now auto-discovered via continuous polling (SPEC-323). The `/swain-do` command still creates worktrees but the bridge detects them automatically rather than requiring manual session spawning. `/work` is superseded by the worktree scanner — any worktree with a session gets a topic automatically.

## Desired Outcomes

- An operator sends a message to a control thread requesting work on an artifact.
- The project bridge (persistent per project) invokes swain-do to create a worktree.
- The project bridge spawns an opencode session in the new worktree, bound to the artifact.
- The session posts its live feed to a new thread in the project room.
- The worktree is tracked by the project bridge and cleanable after session completion.

## External Behavior

- **Input:** Control thread message: `/swain-do SPEC-123`
- **Preconditions:**
  - Host bridge running with chat adapter connected.
  - Project bridge running for the target project (persistent daemon).
  - Artifact (SPEC/EPIC/etc.) exists and is in an actionable phase.
- **Postconditions:**
  - New worktree created by swain-do at session-scoped path.
  - Opencode session spawned in worktree, bound to artifact.
  - New chat thread created with live feed posting.
  - Control thread responds with confirmation + worktree path + link to session thread.
- **Constraints:**
  - Dispatch is implicit from context — `/swain-do SPEC-123` in a control thread means "start work on this artifact." No subcommand needed.
  - Worktrees are scoped to the session — cleanup on session end (or explicit keep).
  - Session inherits project bridge's runtime configuration.
  - Collision detection: warn if another session is already active for the same artifact.
  - Project bridge manages multiple concurrent worktrees/sessions.

## Acceptance Criteria

- **Given** the operator messages `/swain-do SPEC-123` in the control thread, **When** the project bridge processes the command, **Then** swain-do is invoked and a worktree is created.
- **Given** the worktree creation succeeds, **When** the session spawns, **Then** opencode starts in the worktree directory with the artifact bound.
- **Given** an existing session bound to SPEC-123, **When** `/swain-do SPEC-123` is received, **Then** the project bridge responds with a warning and offers to reconnect to the existing thread.
- **Given** the `/swain-do` command specifies a non-existent artifact, **When** the project bridge resolves it, **Then** it responds with "Artifact not found" and lists suggestions.
- **Given** the session completes normally, **When** the operator confirms cleanup, **Then** the worktree is removed.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Worktree created | Session thread shows path | |
| Session spawned | Live feed posting in thread | |
| Collision detection | Warning response on duplicate | |
| Artifact resolution | Error on non-existent, suggestions | |
| Cleanup | Worktree absent after session end | |

## Scope & Constraints

**In scope:**
- Control thread command parsing for `/swain-do <artifact-id>` (dispatch is implicit from context).
- Project bridge invokes swain-do CLI as subprocess.
- Worktree lifecycle management (create, track, clean up).
- Session spawning with artifact binding.
- Thread creation for live feed.
- Project bridge manages multiple concurrent worktrees/sessions.

**Out of scope:**
- Natural language parsing (future enhancement).
- Web pipe / tunnel for web output (v2).
- Runtime adapters for runtimes other than opencode (Claude Code, etc. — separate SPEC).
- swain-do implementation — SPEC-195 owns that.

## Implementation Approach

1. **Extend control thread handler** — parse `/swain-do <artifact-id>` and forward to project bridge.
2. **Project bridge invokes swain-do** — spawn `swain-do dispatch SPEC-123` as subprocess, capture output (worktree path).
3. **Spawn opencode session** — execute `opencode` in worktree directory, capture stdio.
4. **Create session thread** — chat adapter creates thread, posts "Session started: SPEC-123 @ <worktree-path>".
5. **Implement cleanup** — on session end, prompt for worktree removal. Default: remove.
6. **Session registry** — project bridge tracks active sessions per artifact for collision detection.

**Test-then-implement cycles:**
- **Cycle 1:** `/swain-do` command parsing and artifact resolution.
- **Cycle 2:** swain-do subprocess invocation and worktree path capture.
- **Cycle 3:** Opencode session spawn and stdio capture.
- **Cycle 4:** Session thread creation and live feed posting.
- **Cycle 5:** Collision detection and session registry.
- **Cycle 6:** Cleanup flow.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-07 | | Created from VISION-006 decomposition. Linked to EPIC-071, JOURNEY-004. |
| Active | 2026-04-18 | -- | Auto-discovery via worktree scanner (SPEC-323) replaces manual session spawning (ADR-046). |