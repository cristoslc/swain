---
title: "Control Thread Worktree and Session Spawning"
artifact: SPEC-298
track: implementable
status: Active
author: "gemma4:31b-cloud"
created: 2026-04-07
last-updated: 2026-04-07
priority-weight: high
type: feature
parent-epic: EPIC-071
parent-vision: VISION-006
linked-artifacts:
  - [EPIC-071](../../epic/Active/(EPIC-071)-Project-Bridge-Kernel/(EPIC-071)-Project-Bridge-Kernel.md)
  - [VISION-006](../../vision/Active/(VISION-006)-Untethered-Operator/(VISION-006)-Untethered-Operator.md)
  - [JOURNEY-004](../../journey/Active/(JOURNEY-004)-Fire-And-Forget/(JOURNEY-004)-Fire-And-Forget.md)
addresses:
  - "[SPEC-195](../(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch/(SPEC-195)-Defer-Worktree-Creation-to-Task-Dispatch.md)"
swain-do: required
---

# Control Thread Worktree and Session Spawning

## Problem Statement

Control threads in Zulip streams/topics should be able to trigger the creation of a new worktree and spawn an opencode server session in that worktree. Today, swain-init sessions are terminal-bound. The operator wants to start implementation work from a phone by messaging the control thread.

## Desired Outcomes

- An operator sends a message to a control thread requesting work on an artifact.
- The project bridge creates a worktree (via swain-do dispatch integration).
- The project bridge spawns an opencode session bound to the artifact in the new worktree.
- The session posts its live feed to a new thread in the project room.
- The worktree is discoverable and cleanable after session completion.

## External Behavior

- **Input:** Control thread message: `/workon SPEC-123` or natural language "work on SPEC-123"
- **Preconditions:**
  - Host bridge running with chat adapter connected.
  - Project bridge running for the target project.
  - Artifact (SPEC/EPIC/etc.) exists and is in an actionable phase.
- **Postconditions:**
  - New worktree created at `<repo>/../<repo>-<branch>-<session-id>`.
  - Opencode session spawned in worktree, bound to artifact.
  - New chat thread created with live feed posting.
  - Control thread responds with confirmation + link to session thread.
- **Constraints:**
  - Worktrees are scoped to the session — cleanup on session end (or explicit keep).
  - Session inherits project bridge's runtime configuration.
  - Collision detection: warn if another session is already active for the same artifact.

## Acceptance Criteria

- **Given** the operator messages `/workon SPEC-123` in the control thread, **When** the project bridge processes the command, **Then** a worktree is created at a session-scoped path.
- **Given** the worktree creation succeeds, **When** the session spawns, **Then** opencode starts in the worktree directory with the artifact bound.
- **Given** an existing session bound to SPEC-123, **When** `/workon SPEC-123` is received, **Then** the project bridge responds with a warning and offers to reconnect to the existing thread.
- **Given** the `/workon` command specifies a non-existent artifact, **When** the project bridge resolves it, **Then** it responds with "Artifact not found" and lists suggestions.
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
- Control thread command parsing for `/workon <artifact-id>`.
- Integration with swain-do worktree dispatch (builds on SPEC-195).
- Worktree lifecycle management (create, track, clean up).
- Session spawning with artifact binding.
- Thread creation for live feed.

**Out of scope:**
- Natural language parsing beyond simple `/workon` syntax (future enhancement).
- Web pipe / tunnel for web output (v2).
- Runtime adapters for runtimes other than opencode (Claude Code, etc. — separate SPEC).

## Implementation Approach

1. **Define domain command** — `start_session_with_worktree(runtime, artifact, prompt?)` in Project Bridge published language.
2. **Extend control thread handler** — parse `/workon` and dispatch to project bridge.
3. **Wire swain-do dispatch** — call SPEC-195 worktree dispatch logic from project bridge.
4. **Spawn opencode session** — execute `opencode` in worktree directory, capture stdio.
5. **Create session thread** — chat adapter creates thread, posts "Session started: SPEC-123 @ <worktree-path>".
6. **Implement cleanup** — on session end, prompt for worktree removal. Default: remove.

**Test-then-implement cycles:**
- **Cycle 1:** `/workon` command parsing and artifact resolution.
- **Cycle 2:** Worktree creation via swain-do dispatch.
- **Cycle 3:** Opencode session spawn and stdio capture.
- **Cycle 4:** Session thread creation and live feed posting.
- **Cycle 5:** Collision detection and error handling.
- **Cycle 6:** Cleanup flow.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-07 | | Created from VISION-006 decomposition. Linked to EPIC-071, JOURNEY-004. |