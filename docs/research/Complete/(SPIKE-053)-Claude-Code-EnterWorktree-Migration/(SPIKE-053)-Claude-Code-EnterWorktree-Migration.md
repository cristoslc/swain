---
title: "Claude Code EnterWorktree Migration Path"
artifact: SPIKE-053
track: implementable
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
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

**Key insight: CWD persistence is the exception, not the norm.** Of the five supported runtimes (Claude Code, Gemini CLI, Codex, Copilot, Crush), only Claude Code can change its working directory mid-session via `EnterWorktree`. The other four runtimes have never had mid-session worktree switching. Pre-launch worktree creation (bin/swain) is the only approach that works universally. `EnterWorktree` was always a Claude Code-specific crutch, not a universal pattern.

## Findings

### 1. Skill Audit

**Skills with EnterWorktree/ExitWorktree in allowed-tools:**

| Skill | allowed-tools | Usage |
|-------|--------------|-------|
| **swain-do** | `EnterWorktree, ExitWorktree` | Creates worktrees in preamble; exits in plan completion handoff |
| **swain-session** | `EnterWorktree, ExitWorktree` | Defers creation to swain-do; offers "exit worktree" command |

**Skills that reference EnterWorktree/ExitWorktree in logic (not allowed-tools):**

| Skill | Reference | What it does |
|-------|-----------|-------------|
| **swain-sync** | `worktree-*` branch heuristic | Detects EnterWorktree-created worktrees by branch name; skips removal for those (defers to ExitWorktree) |

**All other skills (14) are clean** — no EnterWorktree/ExitWorktree references.

### 2. swain-do Worktree Preamble (current logic)

Triggers before any file-mutating operation when `IN_WORKTREE=no`:

1. Commit untracked files on trunk (so new artifacts are visible in worktree)
2. Check for existing worktrees matching the target SPEC via `swain-worktree-overlap.sh`
3. Call `EnterWorktree` — explicitly documented as "the only mechanism that changes the agent's working directory persistently"
4. Re-run tab naming for new branch
5. Record worktree in session.json bookmark
6. If EnterWorktree fails, stop — do not begin mutating work

### 3. bin/swain Already Creates Worktrees Pre-Launch

`prepare_session_workspace()` in bin/swain already:
- Detects checkout state via `GIT_COMMON_DIR != GIT_DIR`
- Creates worktrees via `git worktree add` when purpose text is provided
- Sets `LAUNCH_ROOT` to the worktree path
- `cd`s into it before `exec`-ing the runtime

**Gap:** bin/swain sets no env var to tell the runtime "you are in a managed worktree." Skills detect worktrees via git plumbing but cannot distinguish bin/swain-launched from direct-launched.

### 4. Worktree Detection Patterns in Codebase

| Pattern | Where used | Count |
|---------|-----------|-------|
| `GIT_COMMON_DIR != GIT_DIR` | swain-do, swain-sync, swain-session bootstrap, bin/swain, swain-trunk.sh | 5 |
| `git worktree list --porcelain` | swain-doctor, swain-teardown, bin/swain (crash debris) | 3 |
| `worktree-*` branch name convention | swain-sync cleanup heuristic | 1 |
| session.json `worktrees` array | swain-teardown orphan detection | 1 |

No skill checks `.git` file vs directory or `SWAIN_WORKTREE_PATH` (proposed but not yet implemented).

### 5. Runtime-Agnostic Patterns Already in Place

- bin/swain supports all five runtimes with per-runtime launch commands
- swain-doctor has platform dotfolder detection for `.claude`, `.codex`, `.gemini`, `.copilot`, `.opencode`, `.crush`
- swain-session is documented as "agent-agnostic — relies on AGENTS.md for auto-invocation"
- `SWAIN_PURPOSE` env var exists for runtimes without prompt support (currently only Crush)

### 6. Migration Risks

**RISK 1 (Medium): Mid-session worktree switching regresses Claude Code only.**
If the operator says "now work on SPEC-200" mid-conversation, pre-runtime worktree doesn't help. But this is only a Claude Code regression — no other runtime ever had this. The correct universal pattern is to restart the session in a new worktree. Phase 1 keeps EnterWorktree as a Claude Code convenience during transition.

**RISK 2 (High): swain-sync branch-name heuristic breaks.**
swain-sync uses `case "$BRANCH" in worktree-*)` to detect EnterWorktree-created worktrees. bin/swain uses different naming via `swain-worktree-name.sh`. Fix: replace branch-name heuristic with lockfile check or `SWAIN_WORKTREE_PATH` env var check.

**RISK 3 (High): No env var bridge.**
bin/swain creates worktrees but exports no env var. Skills can't distinguish "bin/swain put me here" from "launched directly." Fix: export `SWAIN_WORKTREE_PATH` before exec.

**RISK 4 (Medium): Direct `claude` usage without bin/swain.**
If a user runs `claude` directly, no worktree is pre-created. Without EnterWorktree in allowed-tools, the agent cannot isolate. Fix: Phase 1 keeps EnterWorktree as fallback; Phase 2 documents as degraded experience.

**RISK 5 (Low): ADR/SPEC references to ExitWorktree behavior.**
ADR-015 (ticket files and ExitWorktree warnings), ADR-024 (discard_changes default), SPEC-184 (session end calls ExitWorktree) all reference ExitWorktree semantics. These need updating when ExitWorktree is removed.

### 7. Recommended Migration Path

**Phase 1 — bin/swain primary, EnterWorktree fallback:**
- bin/swain exports `SWAIN_WORKTREE_PATH` before launch
- swain-do preamble checks `SWAIN_WORKTREE_PATH` first; if set, skip worktree creation
- If unset (direct claude launch), fall back to `EnterWorktree`
- swain-sync replaces branch-name heuristic with env var or lockfile check

**Phase 2 — Deprecate EnterWorktree:**
- Remove EnterWorktree/ExitWorktree from allowed-tools in swain-do, swain-session
- AGENTS.md documents: "worktree isolation requires bin/swain launcher"
- Direct `claude` usage documented as "degraded experience — manual worktree management"

**Phase 3 — Remove EnterWorktree references:**
- Clean all skill references
- Update ADR-015, ADR-024, SPEC-184
- Archive this SPIKE

### 8. Files Requiring Changes

| File | Change |
|------|--------|
| `skills/swain/scripts/swain` | Export `SWAIN_WORKTREE_PATH` before exec |
| `skills/swain-do/SKILL.md` | Rewrite preamble: env var check first, EnterWorktree fallback (Phase 1), then remove (Phase 2) |
| `skills/swain-session/SKILL.md` | Remove EnterWorktree/ExitWorktree from allowed-tools (Phase 2) |
| `skills/swain-sync/SKILL.md` | Replace `worktree-*` branch heuristic with lockfile/env var check |
| `AGENTS.md` | Update worktree isolation section |
| ADR-015, ADR-024, SPEC-184 | Update ExitWorktree references (Phase 3) |

## Acceptance Criteria

- [x] **SPIKE-053-AC1: Skill audit complete** — 2 skills with allowed-tools, 1 with logic reference, 14 clean
- [x] **SPIKE-053-AC2: Fallback pattern defined** — env var check + EnterWorktree fallback (Phase 1)
- [x] **SPIKE-053-AC3: Deprecation timeline documented** — Phase 1/2/3 with clear milestones
- [x] **SPIKE-053-AC4: Direct Claude usage documented** — "degraded experience" with manual worktree management

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | — | Drafted for EPIC-056 |
| Complete | 2026-04-04 | — | Research complete; findings feed SPEC-245 (bin/swain redesign) and SPEC-250 (alignment audit) |
