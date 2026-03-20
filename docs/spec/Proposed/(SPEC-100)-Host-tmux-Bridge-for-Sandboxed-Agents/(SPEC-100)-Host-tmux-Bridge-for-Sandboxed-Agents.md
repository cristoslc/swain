---
title: "Host tmux Bridge for Sandboxed Agents"
artifact: SPEC-100
track: implementable
status: Proposed
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-036
parent-initiative: ""
parent-vision: VISION-002
linked-artifacts:
  - SPEC-056
  - SPEC-081
  - SPEC-092
  - DESIGN-001
depends-on-artifacts:
  - SPEC-056
  - SPEC-081
  - SPEC-092
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Host tmux Bridge for Sandboxed Agents

## Problem Statement

`swain-session` and the tmux naming flow depend on the operator's real tmux session. Once an agent is launched inside a sandbox, that tmux context is no longer directly reachable: the sandbox cannot see the host tmux socket or reliably target the invoking pane/session. The result is a degraded workflow where the sandboxed agent can do the work but cannot keep the operator's tmux state aligned with that work.

Passing the entire host tmux socket into the sandbox would solve the reachability problem, but it would also grant far more control than swain needs. A narrower bridge is required: sandboxed agents should be able to request the specific tmux operations that swain session management already performs, and nothing broader.

## External Behavior

When a sandbox is launched from a tmux pane, the launcher captures the invoking tmux context and makes a host-tmux bridge available inside the sandbox.

The bridge contract is intentionally narrow:
- target the invoking tmux session/window/pane only
- support the subset of tmux operations needed by `swain-session` and `swain-tab-name.sh`
- reject arbitrary tmux subcommands

Expected user-visible behavior:
- A sandboxed agent running `/swain-session` updates the operator's host tmux naming state as if it were running directly in that pane
- A sandboxed agent can set or clear pane-scoped swain metadata needed for pane-aware naming
- If the sandbox was not launched from tmux, swain's tmux-dependent behavior still degrades gracefully with a clear note

The bridge may be exposed either as a dedicated helper command inside the sandbox or as a transport used transparently by existing session scripts. The important contract is behavioral compatibility, not the exact transport.

## Acceptance Criteria

- Given a sandbox launched from an active tmux pane, when the agent runs `/swain-session`, then the host tmux session/window naming reflects the sandbox's current swain context instead of no-oping
- Given a sandbox launched from tmux, when swain updates pane-scoped metadata used by `SPEC-056`, then that metadata is written to the invoking host pane rather than to an isolated in-sandbox tmux instance
- Given a sandbox not launched from tmux, when tmux-aware swain commands run, then they degrade gracefully and report that no host tmux bridge is available
- Given a sandboxed process attempts a tmux command outside the allowed swain contract, then the bridge rejects it with a clear error and does not execute it on the host
- Given two sandboxes launched from different tmux panes or sessions, when each uses the bridge, then each targets only its own invoking tmux context

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- In scope: launcher plumbing, bridge transport, tmux command allowlist, swain-session integration, graceful no-tmux fallback
- Out of scope: arbitrary `tmux` passthrough, direct host socket mounts, support for non-tmux terminal multiplexers
- Constraint: the bridge must fail closed; inability to verify target pane/session means no host tmux command is executed
- Constraint: the contract should preserve the semantics already defined in `SPEC-056` and `DESIGN-001`
- Constraint: the sandbox must not gain general host shell execution as a side effect of tmux support

## Implementation Approach

Use `SPEC-092` as the integration point. At launch time, capture the host tmux target identity and provision a minimal bridge endpoint into the sandbox. Update the swain session/tab-naming scripts to prefer the bridge when direct tmux access is unavailable, while keeping existing direct-tmux behavior unchanged outside sandboxes.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-20 | -- | Initial creation under EPIC-036 |
