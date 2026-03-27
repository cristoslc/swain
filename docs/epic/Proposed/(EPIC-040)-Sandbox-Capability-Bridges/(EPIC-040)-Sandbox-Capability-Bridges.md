---
title: "Sandbox Capability Bridges"
artifact: EPIC-040
track: container
status: Proposed
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
parent-vision: VISION-002
parent-initiative: INITIATIVE-017
priority-weight: medium
success-criteria:
  - Sandboxed agents can trigger the subset of host tmux behavior required for swain session management without direct host shell access
  - Sandboxed agents can access Docker MCP Gateway through an explicitly selected profile, with a safe default of `sandbox`
  - Bridge mechanisms are scoped per launched sandbox and reject commands or profiles outside the allowed contract
  - Operator-facing launcher and runbook docs explain when the bridges are active, how they are targeted, and how they fail closed
depends-on-artifacts:
  - SPEC-081
  - SPEC-092
addresses: []
trove: ""
linked-artifacts:
  - EPIC-016
  - INITIATIVE-004
  - SPEC-056
  - SPEC-081
  - SPEC-092
  - SPEC-130
  - SPEC-131
---

# Sandbox Capability Bridges

## Goal / Objective

Swain's sandbox launchers currently isolate filesystem, branch, and credentials, but they also cut sandboxed agents off from a few host capabilities that are still legitimately part of the operator workflow. Two gaps are now blocking the next round of sandbox usage:

1. `swain-session` and related tmux-aware behavior cannot affect the operator's actual tmux session from inside the sandbox.
2. Sandboxed agents cannot consume Docker MCP Gateway tools through an operator-approved profile, even when the host already exposes a curated MCP surface for safe use.

This epic adds narrowly scoped bridges for those capabilities. The intent is not to weaken isolation or create a generic host escape hatch. The intent is to let sandboxed agents reach a small, reviewable set of host integrations that swain already depends on operationally.

## Scope Boundaries

**In scope:**
- A host tmux bridge that targets the invoking tmux session/window/pane and exposes only the operations required by swain session management
- Launcher/runtime plumbing that makes Docker MCP Gateway available inside sandboxed agents via an explicitly selected profile
- Clear failure modes when a bridge is unavailable, misconfigured, or requested outside policy
- Documentation and validation for bridge scoping, lifecycle, and operator expectations

**Out of scope:**
- Arbitrary host command execution from inside the sandbox
- Broad passthrough of the operator's tmux socket, shell environment, or Docker config
- Remote MCP providers unrelated to the local Docker MCP Gateway
- Replacing sandbox isolation with a trust-based model

## Child Specs

| Spec | Title | Dependencies | Status |
|------|-------|-------------|--------|
| SPEC-130 | Host tmux Bridge for Sandboxed Agents | SPEC-056, SPEC-081, SPEC-092 | Proposed |
| SPEC-131 | Docker MCP Gateway Profile Access for Sandboxed Agents | SPEC-092 | Proposed |

## Key Dependencies

- SPEC-081 establishes per-sandbox worktree isolation; bridges must preserve that boundary
- SPEC-092 is the current unified sandbox launcher and the right integration point for bridge setup
- SPEC-056 already defines the tmux behaviors swain expects; the bridge should preserve that contract rather than invent a second session model

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-20 | -- | Initial creation for scoped host-integration work in sandboxed agent sessions |
| — | 2026-03-20 | -- | Re-parented from INITIATIVE-004 to INITIATIVE-017 (Unattended Agent Safety) |
