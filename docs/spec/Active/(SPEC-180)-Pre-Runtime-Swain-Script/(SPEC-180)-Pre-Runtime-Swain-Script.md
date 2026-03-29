---
title: "Pre-Runtime Swain Script"
artifact: SPEC-180
track: implementable
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
priority-weight: high
type: feature
parent-epic: EPIC-046
parent-initiative: ""
linked-artifacts:
  - SPIKE-051
  - ADR-017
  - ADR-018
  - ADR-015
  - ADR-019
  - SPEC-181
  - SPEC-182
depends-on-artifacts:
  - SPEC-182
addresses: []
evidence-pool: "agent-session-persistence@450cb05"
source-issue: ""
swain-do: required
---

# Pre-Runtime Swain Script

## Problem Statement

Crash detection and recovery currently runs inside the agentic runtime (swain-session skill code). This is fundamentally wrong: the runtime must be running before the skill can execute, but crash debris may block the runtime from starting cleanly. Per ADR-018, session management must be structural (bash), not prosaic (LLM reading markdown).

## Desired Outcomes

The operator runs `swain` after a system crash and gets: crash detection, debris cleanup, session resume options, and runtime launch — all before the LLM starts. No manual git lock cleanup, no stale tk lock investigation, no worktree archaeology. The script handles it in seconds with operator confirmation for destructive actions.

## External Behavior

**Inputs:** CLI arguments (e.g., `--fresh`, `--runtime gemini`), project-root configuration files (`swain.settings.json`, `.agents/session.json`), runtime session data (`~/.claude/sessions/`, `~/.copilot/session-state/`, etc.)

**Phases:**

**Phase 1 — Pre-runtime structural checks:**
- Scan runtime session directories for orphaned PIDs associated with this project (Claude Code: `~/.claude/sessions/*.json` → match `cwd`, verify PID alive; other runtimes per trove `agent-session-persistence`)
- Invoke crash debris checks ([SPEC-182](../(SPEC-182)-Crash-Debris-Detection-Checks/(SPEC-182)-Crash-Debris-Detection-Checks.md)) — git locks, stale tk locks, dangling worktrees
- Offer cleanup with operator confirmation (per [ADR-015](../../../adr/Active/(ADR-015)-Tickets-Are-Ephemeral-Execution-Scaffolding.md): never auto-discard worktree state)

**Phase 2 — Session selection (only if crashed sessions detected):**
- Present options: resume a crashed session, enter a dangling worktree with unmerged work, or start fresh
- If resuming: read `.agents/session.json` for bookmark, focus lane; query `tk ready` for in-progress tasks; locate conversation log
- Compose an initial prompt with structured resume context for the runtime

**Phase 3 — Runtime invocation:**
- Resolve runtime: per-project (`swain.settings.json → runtime`) > global (`~/.config/swain/settings.json → runtime`) > auto-detect installed (per ADR-017)
- Launch with correct flags per ADR-017 support tiers:
  - Claude Code: `claude --dangerously-skip-permissions "<prompt>"`
  - Gemini CLI: `gemini -y -i "<prompt>"`
  - Codex CLI: `codex --full-auto "<prompt>"`
  - Copilot CLI: `copilot --yolo -i "<prompt>"`
  - Crush: `crush --yolo` (Partial tier — no initial prompt)
- Initial prompt: `/swain-init` (fresh) or `/swain-session` with resume context (recovery)

**Postconditions:** Runtime is running with correct permissions and initial context. Crash debris has been cleaned. Operator has chosen whether to resume or start fresh.

## Acceptance Criteria

1. **Given** a system crash (kill -9, reboot), **when** the operator runs `swain`, **then** the script detects the orphaned session and presents recovery options before the runtime starts.
2. **Given** no crashed sessions, **when** the operator runs `swain`, **then** the script starts the runtime directly with no visible delay (fast path — skip Phase 2).
3. **Given** crash debris (git index lock, stale tk locks), **when** the script runs Phase 1, **then** debris is detected and removable with one confirmation per item.
4. **Given** a per-project runtime preference, **when** the script resolves the runtime, **then** per-project overrides global overrides auto-detect.
5. **Given** a crash with dangling worktree containing uncommitted changes, **when** the script presents resume options, **then** the worktree and its uncommitted state are surfaced prominently.
6. **Given** the operator selects "resume", **when** the runtime starts, **then** the initial prompt includes structured context (bookmark, focus lane, in-progress tasks, conversation log path).
7. **Given** `--fresh` flag, **when** the script runs, **then** Phase 2 is skipped entirely.

## Script Location and Distribution (ADR-019)

Per [ADR-019](../../../adr/Proposed/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md), the script follows the operator-facing script convention:

**Canonical location:** `skills/swain/scripts/swain`

The script is executable, committed to the swain repo, and distributed to consumer projects via `npx skills add`. It is **not** placed directly in the project root.

**`bin/` symlink:** `bin/swain -> ../skills/swain/scripts/swain` (relative path)

Created by:
- **swain-init** Phase 4.5 — during first-run onboarding, after the shell function is installed
- **swain-doctor** — on subsequent sessions, auto-repairs if missing (see below)

**Doctor health check:** swain-doctor gains a `swain symlink` check using ADR-019's standard status model (ok/missing/stale/conflict) against `bin/swain`.

## Scope & Constraints

- Pure bash — no LLM dependency, no Python, no Node. Must work even if the runtime is broken.
- Per ADR-015: never auto-discard worktree state. All destructive actions require operator confirmation.
- Per ADR-018: detection is structural (file-based), not prosaic (markdown directives).
- Per ADR-019: script lives in the skill tree; a `bin/` symlink provides the operator entry point.
- Claude Code crash detection is the primary implementation. Other runtimes degrade gracefully (fall back to swain git state).
- The script replaces the runtime detection and invocation logic currently in the shell function ([EPIC-045](../../../epic/Active/(EPIC-045)-Shell-Launcher-Onboarding/(EPIC-045)-Shell-Launcher-Onboarding.md)).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation from [SPIKE-051](../../../research/Complete/(SPIKE-051)-Tmux-Session-Persistence-After-Crash/(SPIKE-051)-Tmux-Session-Persistence-After-Crash.md) |
| Active | 2026-03-28 | — | Updated symlink from `./swain` to `bin/swain` per ADR-019 operator-facing convention |
