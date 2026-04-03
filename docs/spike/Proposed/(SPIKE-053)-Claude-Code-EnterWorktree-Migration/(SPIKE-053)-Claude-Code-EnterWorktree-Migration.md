---
title: "Claude Code EnterWorktree Migration Path"
artifact: SPIKE-053
track: implementable
status: Proposed
author: cristos
created: 2026-04-04
priority-weight: high
parent-epic: EPIC-056
type: migration
swain-do: required
---

# SPIKE-053: Claude Code EnterWorktree Migration Path

## Goal

Determine how to phase out `EnterWorktree` usage in Claude Code skills without breaking existing workflows, as bin/swain takes over worktree lifecycle management.

## Context

**Current behavior:**
- swain-do, swain-session skills use `EnterWorktree` tool (Claude Code built-in)
- Agent controls worktree creation/exit mid-conversation
- Works only in Claude Code

**New behavior (EPIC-056):**
- bin/swain creates/claims worktree BEFORE launching runtime
- Runtime inherits worktree (already in correct directory)
- `EnterWorktree` becomes redundant/breaking

**Migration challenge:**
- Existing skills have `EnterWorktree` in allowed-tools and execution logic
- Users may launch `claude` directly (without bin/swain) — need fallback
- Complete removal breaks direct Claude Code usage

## Research Questions

1. **Which skills use `EnterWorktree`?**
   - swain-do (worktree preamble)
   - swain-session (auto-isolation)
   - swain-sync (worktree detection)
   - Others?

2. **What's the replacement pattern?**
   - Read `SWAIN_WORKTREE_PATH` env var (set by bin/swain)
   - If set: already in worktree, skip creation
   - If unset: fallback to `EnterWorktree` (direct Claude usage)

3. **Phase-out timeline:**
   - Phase 1: bin/swain primary, `EnterWorktree` fallback
   - Phase 2: Deprecate `EnterWorktree` in AGENTS.md
   - Phase 3: Remove from allowed-tools

4. **Direct Claude usage:**
   - User runs `claude` without bin/swain
   - Should skills still work?
   - Document as "degraded experience — manual worktree management"

## Acceptance Criteria

- [ ] **SPIKE-053-AC1: Skill audit complete**
  - List all skills using `EnterWorktree`
  - Identify replacement logic needed

- [ ] **SPIKE-053-AC2: Fallback pattern defined**
  - Env var check + `EnterWorktree` fallback
  - Works for both bin/swain and direct Claude

- [ ] **SPIKE-053-AC3: Deprecation timeline documented**
  - Phase 1/2/3 milestones
  - AGENTS.md updates

- [ ] **SPIKE-053-AC4: Direct Claude usage documented**
  - "Degraded experience" section in docs
  - Manual worktree management instructions

## Implementation Plan

1. **Audit skills** — grep for `EnterWorktree` usage
2. **Design fallback pattern** — env var check + graceful degradation
3. **Test both paths** — bin/swain launch vs direct Claude
4. **Document deprecation** — AGENTS.md, skill comments
5. **Implement Phase 1** — bin/swain primary, fallback working

## Evidence

- Current `EnterWorktree` usage in skills
- bin/swain env var protocol (`SWAIN_WORKTREE_PATH`)
- Claude Code tool documentation

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | — | Drafted for EPIC-056 |
