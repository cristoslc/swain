---
title: "Worktree Isolation Redesign"
artifact: EPIC-063
track: container
status: Complete
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
  - SPEC-276
  - SPEC-277
  - SPEC-278
  - SPEC-279
  - SPEC-280
  - SPEC-281
  - SPEC-282
  - SPEC-283
  - SPEC-284
---

# EPIC-063: Worktree Isolation Redesign

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
- **SPEC-276** — Lockfile Management (claim/release/stale detection)
- **SPEC-277** — bin/swain Redesign (worktree router)
- **SPEC-278** — swain-doctor Orphan Scanning
- **SPEC-279** — swain-teardown Integration (claim release, cleanup)
- **SPEC-280** — session.json Archive Mechanism
- **SPEC-281** — swain-sync Lockfile Integration (ready_for_cleanup)
- **SPEC-282** — Alignment Audit (update all skills)
- **SPEC-283** — Artifact-Aware Worktree Naming
- **SPEC-284** — swain-sync Merge Logic (trunk → worktree → push)

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

**Terminal state:** Active (implementation complete, pending operator verification)
**Period:** 2026-04-04 (single session)
**Related artifacts:** ADR-025, SPIKE-053, SPIKE-056, SPIKE-057, DESIGN-004, SPEC-276, SPEC-277, SPEC-278, SPEC-279, SPEC-280, SPEC-281, SPEC-282, SPEC-283, SPEC-284

### Summary

Started from "tmux window title isn't changing" in a prior session. Discovered that worktree isolation was broken for non-Claude-Code runtimes and expanded to a full redesign. This session resolved all research prerequisites (3 SPIKEs, 1 ADR), materialized 9 implementation SPECs, and implemented all of them with 83 passing tests across 5 test suites.

The key reframe: CWD persistence is the exception (Claude Code only), not the norm. Pre-launch worktree creation via bin/swain is the only universal approach. EnterWorktree was always a Claude Code-specific crutch.

### Key Decisions

1. **Lockfiles over JSON registry** — simpler, git-ignorable, atomic (SPEC-276)
2. **Dual-check stale detection** — PID dead AND pane dead (SPEC-276)
3. **bin/swain does cleanup** — swain-sync marks ready, bin/swain prunes (SPEC-277, SPEC-281)
4. **Artifact-aware naming** — containers ask for purpose, implementable/standing use title (SPEC-283, ADR-025)
5. **session.json archival** — survives worktree deletion for retro (SPEC-280)
6. **Child process, not exec** — bin/swain runs runtime as child with signal forwarding so it can clean up after exit (SPEC-277)
7. **Targeted stash pop** — prevents cross-worktree stash interference (SPEC-284)

### Learnings

- **Operator corrections were high-signal:** "you're proposing multiple happy paths AND we need to think about edge cases" caught premature decomposition in the design phase
- **SPIKEs had answers baked in:** All three SPIKEs (053, 056, 057) were drafted with confirmed answers already in the text. The "User Interview Required" section in ADR-025 was stale — the interview had happened in a prior session. Operator caught this, saving a round-trip.
- **Research agents worked well in parallel:** SPIKE-053 and SPIKE-057 ran as parallel background agents, each taking ~3 minutes. Combined findings were comprehensive and required minimal correction.
- **Pre-commit config missing in worktrees:** The worktree lacked `.pre-commit-config.yaml`, requiring `PRE_COMMIT_ALLOW_NO_CONFIG=1` for every commit. This is a worktree hygiene gap.
- **TDD subshell PID trap:** Tests calling `bash "$SCRIPT" claim` create a subshell with a new PID. The lockfile records the subshell PID, which is dead by the time stale detection runs. Fixed by writing lockfiles directly in tests with `$$` (the test process PID).
- **DESIGN-004 ID collision:** The worktree router design was assigned DESIGN-004, but that ID already existed (swain-stage Interaction Design). The find command returned the wrong file initially. Artifact ID collision is a recurring issue.

### SPEC candidates

1. **Pre-commit config in worktrees** — worktrees created by bin/swain should inherit or symlink `.pre-commit-config.yaml` from the main checkout. Currently requires manual env var override on every commit.
2. **Artifact ID collision prevention** — `next-artifact-id.sh` should check across ALL artifact types, not just the requested type. DESIGN-004 was allocated twice because the script only checked `docs/design/`.
3. **EPIC-063 integration testing** — the individual unit tests pass, but there is no end-to-end test that runs the full flow: bin/swain creates worktree -> claims lockfile -> runtime runs -> swain-sync marks ready -> bin/swain prunes. This should be a dedicated test script.

### README drift

- README says "swain-do automatically creates a linked git worktree" — **stale**: bin/swain now handles worktree creation pre-launch, not swain-do mid-session.
- README says "swain-sync lands the changes on trunk and prunes the worktree automatically" — **stale**: swain-sync now marks `ready_for_cleanup` instead of pruning. bin/swain handles pruning after runtime exit.
