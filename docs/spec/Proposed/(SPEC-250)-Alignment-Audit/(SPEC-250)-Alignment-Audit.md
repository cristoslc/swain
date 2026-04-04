---
title: "Alignment Audit"
artifact: SPEC-250
track: implementable
status: Proposed
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: low
depends-on-artifacts:
  - SPEC-244
  - SPEC-245
  - SPEC-249
  - SPEC-251
linked-artifacts:
  - SPIKE-053
---

# SPEC-250: Alignment Audit

## Goal

Update all skills to align with the new worktree isolation model. Remove EnterWorktree/ExitWorktree references, add SWAIN_WORKTREE_PATH detection, update AGENTS.md.

## Deliverables (from SPIKE-053 findings)

### Phase 1 — Env var bridge
1. swain-do: rewrite worktree preamble to check `SWAIN_WORKTREE_PATH` first, fall back to EnterWorktree
2. swain-session: add env var detection to greeting

### Phase 2 — Remove EnterWorktree
3. swain-do: remove EnterWorktree/ExitWorktree from allowed-tools
4. swain-session: remove from allowed-tools
5. swain-sync: replace `worktree-*` branch heuristic with lockfile check

### Phase 3 — Documentation
6. AGENTS.md: update worktree isolation section
7. ADR-015, ADR-024: update ExitWorktree references
8. SPEC-184: update AC-4

## Acceptance Criteria

- [ ] **AC1: swain-do preamble uses env var**
  - Checks SWAIN_WORKTREE_PATH before attempting EnterWorktree
  - If set: already in managed worktree, skip creation

- [ ] **AC2: EnterWorktree removed from allowed-tools**
  - swain-do and swain-session no longer list EnterWorktree/ExitWorktree

- [ ] **AC3: swain-sync uses lockfile detection**
  - No branch-name heuristic for worktree detection
  - Checks lockfile existence or SWAIN_WORKTREE_PATH

- [ ] **AC4: AGENTS.md updated**
  - Worktree isolation section reflects bin/swain as primary mechanism
  - Documents that CWD persistence is Claude Code-only

- [ ] **AC5: ADR references updated**
  - ADR-015, ADR-024 updated to reference new cleanup mechanism
  - SPEC-184 updated

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
