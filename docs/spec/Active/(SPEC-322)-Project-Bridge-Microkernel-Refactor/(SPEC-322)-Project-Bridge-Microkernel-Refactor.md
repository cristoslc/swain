---
title: "Project Bridge Microkernel Refactor"
artifact: SPEC-322
track: implementable
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
priority-weight: high
type: feature
parent-epic: EPIC-071
parent-initiative: ""
linked-artifacts:
  - ADR-046
  - ADR-038
  - EPIC-071
depends-on-artifacts:
  - ADR-046
  - ADR-038
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Project Bridge Microkernel Refactor

## Problem Statement

Project bridge imports runtime adapters as in-process Python classes instead of spawning them as subprocess plugins. This couples the kernel to every adapter's dependency tree, makes it impossible to crash-isolate adapters, and violates the plugin architecture defined in ADR-046. Adapters loaded in-process can take down the entire bridge on failure, and adding a new adapter requires modifying the kernel code.

## Desired Outcomes

ProjectBridge spawns every adapter — chat and runtime — as a subprocess plugin following ADR-046's protocol (ConfigMessage on stdin line 0, NDJSON events/commands on subsequent lines). PluginProcess is extracted to a shared module. All adapter entry points are registered in pyproject.toml. The old kernel, host bridge, main, runtime_state, and project_bridge plugin files are deleted.

## External Behavior

**Before:** Adapters imported as Python classes and called in-process.

**After:** Adapters spawned as subprocess plugins with stdin/stdout protocol.

**Protocol (per ADR-046):**
- Line 0 on stdin: JSON ConfigMessage with all adapter configuration.
- Subsequent lines: NDJSON events (adapter → kernel) and commands (kernel → adapter).

**Entry points (registered in pyproject.toml):**
- `swain-helm-zulip-chat`
- `swain-helm-opencode`
- `swain-helm-claude`
- `swain-helm-tmux`

## Acceptance Criteria

1. **Given** the PluginProcess logic currently in `kernel.py`, **when** it is extracted, **then** it lives in a shared module `plugin_process.py` and is importable by ProjectBridge without coupling to kernel internals.

2. **Given** ProjectBridge starts up, **when** it initializes, **then** it spawns a `ZulipChatAdapter` as a subprocess plugin (ConfigMessage on stdin line 0, NDJSON on subsequent lines).

3. **Given** ProjectBridge needs a runtime adapter, **when** a session starts, **then** it spawns the runtime adapter as a subprocess plugin (one per session, per ADR-038).

4. **Given** all adapter subprocess entry points, **when** the package is installed, **then** `swain-helm-zulip-chat`, `swain-helm-opencode`, `swain-helm-claude`, and `swain-helm-tmux` are registered as console_scripts in pyproject.toml.

5. **Given** the refactor is complete, **when** the codebase is checked, **then** `kernel.py`, `bridges/host.py`, `main.py`, `runtime_state.py`, and `plugins/project_bridge.py` are deleted.

6. **Given** ProjectBridge needs configuration, **when** it reads config, **then** it reads from watchdog (passed via CLI args or env vars), not from domain config.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- This spec covers the structural refactor only — behavioral changes to adapters are out of scope.
- PluginProcess extraction must preserve all existing subprocess management behavior (start, stop, health check, restart).
- The ConfigMessage schema for each adapter is dictated by ADR-046.
- Backward compatibility with existing ZulipChatAdapter is required (it already uses NDJSON on stdout, needs ConfigMessage on stdin line 0).
- No new adapters — only the four listed entry points are registered.

## Implementation Approach

1. Extract `PluginProcess` class from `kernel.py` to `plugin_process.py` with zero behavioral changes.
2. Rewrite `ProjectBridge.__init__` to spawn `ZulipChatAdapter` as a subprocess plugin instead of importing it in-process.
3. Add subprocess spawning for runtime adapters (one per session).
4. Register all four console_scripts entry points in `pyproject.toml`.
5. Update adapter entry points to read ConfigMessage from stdin line 0 on startup.
6. Delete `kernel.py`, `bridges/host.py`, `main.py`, `runtime_state.py`, `plugins/project_bridge.py`.
7. Update ProjectBridge config reading to accept watchdog-provided args/env.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |