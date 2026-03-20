---
title: "Docker MCP Gateway Profile Access for Sandboxed Agents"
artifact: SPEC-101
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
  - SPEC-092
  - EPIC-033
  - DESIGN-005
depends-on-artifacts:
  - SPEC-092
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Docker MCP Gateway Profile Access for Sandboxed Agents

## Problem Statement

Docker MCP Gateway is becoming the cleanest way to expose approved tool surfaces to local agents, but swain's sandboxed runtimes currently do not inherit that capability in a controlled way. The operator may already have a curated Gateway profile intended for sandboxed work, yet agents launched through `swain-box` cannot consume it without ad hoc host mounts or manual reconfiguration inside each sandbox.

Swain needs a launcher-supported path that exposes Docker MCP Gateway to sandboxed agents while keeping the scope explicit. The preferred target is a dedicated `sandbox` profile rather than the operator's broader default profile.

## External Behavior

`swain-box` supports enabling Docker MCP Gateway access for sandboxed agents through an explicitly selected profile. The default safe target is `sandbox` when present.

Expected behavior:
- On launch, the operator can select or provide a Docker MCP Gateway profile for the sandboxed session
- When the requested profile exists, the sandboxed runtime receives only the configuration needed to use that profile's Gateway surface
- When the requested profile is absent or invalid, launch fails with a clear error that identifies the missing profile rather than silently falling back to a broader one
- Runtimes that can auto-discover MCP configuration should see the Gateway automatically; runtimes that cannot should receive a deterministic bootstrap path or operator instruction

The bridge must be profile-scoped, not config-scoped. The sandbox should not receive the operator's whole Docker or MCP configuration just to reach one approved profile.

## Acceptance Criteria

- Given Docker MCP Gateway is available on the host and a `sandbox` profile exists, when `swain-box` launches a sandboxed agent with MCP access enabled, then the agent can use Gateway-backed tools from that profile
- Given a profile name is provided explicitly, when the profile exists, then the sandboxed runtime is configured for that profile and not for any broader default
- Given the requested profile does not exist, when launch begins, then `swain-box` exits non-zero with a clear profile-specific error
- Given MCP access is enabled, when configuration is inspected inside the sandbox, then only the minimal profile-scoped bootstrap material is present rather than the operator's full host config
- Given MCP access is not enabled, when a sandbox launches, then no Docker MCP Gateway configuration is injected by default

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- In scope: launcher flags or config, profile selection logic, profile existence checks, runtime bootstrap wiring, operator-facing docs
- Out of scope: implementing Docker MCP Gateway itself, managing remote MCP servers, defining tool policy inside the Gateway profile
- Constraint: the `sandbox` profile is preferred, but explicit profile selection must remain possible
- Constraint: the launcher must never silently fall back from a requested narrow profile to a broader host-default profile
- Constraint: configuration injection should be runtime-agnostic where possible, with per-runtime shims only where unavoidable

## Implementation Approach

Extend `SPEC-092` launcher setup so MCP bootstrap is treated as another scoped runtime capability, alongside credentials and worktree selection. Detect the requested Docker MCP Gateway profile before launch, inject only the profile-scoped bootstrap material needed by the chosen runtime, and keep the default path off unless the operator explicitly enables it or configures a safe default.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-20 | -- | Initial creation under EPIC-036 |
