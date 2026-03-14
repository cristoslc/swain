---
title: "MOTD Reactive Agent Status via Claude Code Hooks"
artifact: SPEC-041
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: feature
parent-epic: EPIC-011
linked-artifacts:
  - EPIC-011
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# MOTD Reactive Agent Status via Claude Code Hooks

## Problem Statement

The MOTD panel currently requires manual `motd update` calls to refresh agent status. When an agent starts or stops work, or uses a tool, the panel does not update automatically. This makes the panel a poor real-time dashboard and increases operator cognitive load. Originally tracked as tk swain-6oa.

## External Behavior

Claude Code hooks (`PostToolUse`, `SubagentStart`, `SubagentStop`, `Stop`, `PreToolUse`) write agent activity data to a well-known file (e.g., `memory/agent-activity.json`). The Textual TUI MOTD app reads this file and updates its status display reactively — no manual `motd update` call needed.

**Hook → file → TUI reactive update flow:**
1. Claude Code fires a hook event (e.g., `PostToolUse`)
2. A hook script appends/updates `memory/agent-activity.json` with tool name, timestamp, agent ID
3. The Textual TUI watches the file (using `watchfiles` or `inotify`) and re-renders the status panel on change
4. The panel displays: current tool in use, last action, agent session start time, idle/active state

**Out of scope:** The bash MOTD fallback — it remains static.

## Acceptance Criteria

- **Given** a Claude Code session is active and fires a `PostToolUse` event, **When** the hook runs, **Then** `memory/agent-activity.json` is updated within 1 second with the tool name and timestamp.
- **Given** the Textual TUI MOTD is running, **When** `agent-activity.json` is updated, **Then** the status panel re-renders within 2 seconds without requiring a manual command.
- **Given** a `SubagentStart` event fires, **When** the hook runs, **Then** the MOTD shows the subagent as active with its ID.
- **Given** a `Stop` event fires (session end), **When** the hook runs, **Then** the MOTD status transitions to idle.
- **Given** the hooks script is absent or errors, **When** the TUI starts, **Then** the panel renders with a "hooks not configured" notice — no crash.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| | | |

## Scope & Constraints

- Claude Code hooks API must support `PostToolUse`, `SubagentStart`, `SubagentStop`, `Stop`.
- Hook scripts live in `.claude/hooks/` and must be registered in Claude Code settings.
- The `agent-activity.json` file lives in the project memory directory (`~/.claude/projects/<slug>/memory/`).
- File watching must not create excessive CPU usage — poll interval ≥ 1s or use native `inotify`/`kqueue`.

## Implementation Approach

1. Define `memory/agent-activity.json` schema (tool, timestamp, agent_id, state).
2. Write hook scripts for `PostToolUse`, `SubagentStart`, `SubagentStop`, `Stop`.
3. Register hooks in `.claude/settings.json` (or prompt user to do so).
4. Add file watcher to the Textual TUI that triggers a panel refresh on file change.
5. Update the status panel widget to display fields from `agent-activity.json`.
6. Add graceful degradation when hooks are missing or file is absent.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | ca755446db4a68c7429812fa6b8f2837856e7050 | Initial creation from EPIC-011 decomposition; sourced from tk swain-6oa |
