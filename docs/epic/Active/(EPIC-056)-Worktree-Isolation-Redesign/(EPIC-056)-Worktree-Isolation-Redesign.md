---
title: "Worktree Isolation Redesign"
artifact: EPIC-056
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision:
  - VISION-001
  - VISION-003
parent-initiative: INITIATIVE-013
priority-weight: high
success-criteria:
  - bin/swain is worktree router with menu + flags
  - Lockfile-based claiming prevents concurrent access collisions
  - swain-sync merges to trunk from worktree, marks ready_for_cleanup
  - swain-doctor detects orphaned worktrees with stale lockfiles
  - Artifact-aware worktree naming (container vs implementable vs standing)
  - session.json archive mechanism for retro reconstruction
depends-on-artifacts:
  - ADR-025
addresses:
  - SPEC-243 (superseded)
  - SPEC-241 (integrated)
evidence-pool: ""
linked-artifacts:
  - ADR-025
  - SPIKE-053
  - SPIKE-056
  - SPIKE-057
  - DESIGN-004
  - SPEC-244
  - SPEC-245
  - SPEC-246
  - SPEC-247
  - SPEC-248
  - SPEC-249
  - SPEC-250
  - SPEC-251
  - SPEC-252
---

# EPIC-056: Worktree Isolation Redesign

## Goal

Redesign swain's worktree isolation model to be **runtime-agnostic** (not Claude Code-specific), **structurally enforced** (not prosaic directives), and **session-aware** (worktree claiming, stale detection, cleanup coordination).

## Problem Statement

Current worktree isolation assumes:
1. Claude Code's `EnterWorktree` tool (unavailable to other runtimes)
2. Persistent CWD across commands (unavailable to Crush/CLI agents)
3. One session = one worktree = one pane (too coupled)

This breaks swain's "Swain Everywhere" vision (VISION-003) — worktree discipline only works on Claude Code.

## Solution Overview

**bin/swain as worktree router:**
- Claims worktrees via lockfiles (`.agents/worktrees/<branch>.lock`)
- Tracks PID + pane_id for stale detection
- Interactive menu + flags for worktree selection/creation
- Artifact-aware naming (container vs implementable vs standing)
- Launches runtime IN worktree (cd before exec)

**Lockfile-based claiming:**
- Prevents concurrent access collisions
- Stale = both PID dead AND pane dead
- `ready_for_cleanup` flag from swain-sync

**swain-sync integration:**
- Merges trunk → worktree → push (all from worktree)
- Marks lockfile `ready_for_cleanup=true` with commit hash
- bin/swain prunes after verifying no new commits

**session.json archival:**
- Survives worktree deletion
- Enables retro reconstruction
- Compressed archive with manifest

## Child Artifacts

### Research (SPIKEs)
- **SPIKE-053** — Claude Code EnterWorktree Migration Path
- **SPIKE-056** — Artifact Model Audit + Extraction + Naming Rules
- **SPIKE-057** — swain-sync Lockfile Integration

### Architecture
- **ADR-025** — Artifact Model Correction (user interview required)

### Design
- **DESIGN-004** — bin/swain Worktree Router (menu UI, flags, lockfile format)

### Implementation
- **SPEC-244** — Lockfile Management (claim/release/stale detection)
- **SPEC-245** — bin/swain Redesign (worktree router)
- **SPEC-246** — swain-doctor Orphan Scanning
- **SPEC-247** — swain-teardown Integration (claim release, cleanup)
- **SPEC-248** — session.json Archive Mechanism
- **SPEC-249** — swain-sync Lockfile Integration (ready_for_cleanup)
- **SPEC-250** — Alignment Audit (update all skills)
- **SPEC-251** — Artifact-Aware Worktree Naming
- **SPEC-252** — swain-sync Merge Logic (trunk → worktree → push)

## Dependencies

**Blocks:**
- VISION-003 (Swain Everywhere) — runtime-agnostic isolation
- INITIATIVE-013 (Concurrent Session Safety) — worktree claiming prevents collisions

**Depends on:**
- ADR-025 — artifact model must be corrected before naming logic

## Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Runtime-agnostic isolation | Works for Crush, Claude Code, Codex, Gemini CLI |
| Structural enforcement | Lockfile claiming, not LLM directives |
| Collision prevention | Hard block for implementable/standing, soft for container |
| Stale detection | PID + pane dual-check |
| Cleanup safety | ready_for_cleanup with commit hash verification |
| Retro reconstruction | session.json archive survives worktree deletion |

## Retrospective

**Terminal state:** Proposed (retro at completion)

### Summary

Started from "tmux window title isn't changing" → discovered fundamental worktree isolation broken for non-Claude-Code runtimes → expanded to full redesign.

### Key Decisions

1. **Lockfiles over JSON registry** — simpler, git-ignorable, atomic
2. **Dual-check stale detection** — PID dead AND pane dead
3. **bin/swain does cleanup** — swain-sync marks ready, bin/swain prunes
4. **Artifact-aware naming** — containers ask for purpose, implementable/standing use title
5. **session.json archival** — survives worktree deletion for retro

### Learnings

- **Operator corrections were high-signal:** "you're proposing multiple happy paths AND we need to think about edge cases" caught premature decomposition
- **swain-sync mechanics required multiple iterations:** finally confirmed git merge/push work from worktree
- **Artifact model was outdated:** ADR-003 misclassifies SPIKE/INITIATIVE — needs superseding ADR
