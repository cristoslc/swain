---
title: "PR-Only Agent Guardrails"
artifact: EPIC-037
track: container
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
parent-vision: VISION-002
parent-initiative: INITIATIVE-017
priority-weight: high
success-criteria:
  - swain-box creates an enforced worktree branch at sandbox startup — the sandboxed agent cannot operate on `main` directly
  - The token injected into the sandbox is scoped so the agent can create PRs and push to non-protected branches but cannot push to or merge into protected branches
  - Host-assisted credential provisioning creates the scoped token using the operator's authenticated `gh` session and injects only the narrow token into the sandbox
  - Agent issue-selection uses convention-based signals (labels like `agent-eligible`, mentions like `@swain`) with the architecture accommodating a future deterministic MCP filter layer
  - The guardrails work across both Docker container and Docker Sandbox (microVM) isolation modes
depends-on-artifacts:
  - SPEC-081
  - SPEC-092
  - SPIKE-037
addresses: []
evidence-pool: ""
linked-artifacts:
  - EPIC-040
  - INITIATIVE-013
  - SPEC-081
  - SPEC-092
  - SPIKE-037
---

# PR-Only Agent Guardrails

## Goal / Objective

Enable an unattended agent to safely monitor GitHub issues, implement fixes, and open PRs — constrained so it **cannot land changes directly**. The agent's worst-case failure mode should be "opens a bad PR," never "pushes broken code to main."

This requires combining filesystem isolation (the agent works on a worktree branch, not `main`) with API credential scoping (the injected token permits PR creation but not direct pushes to protected branches). The privileged host provisions these constraints at sandbox startup; the agent receives only the narrowed access.

## Scope Boundaries

**In scope:**
- Enforced worktree branch creation during `swain-box` startup (agent starts on `agent/<sandbox-name>` branch, never on `main`)
- Host-side credential provisioning: create a scoped GitHub token (mechanism TBD per SPIKE-037) and inject it into the sandbox as `GH_TOKEN`
- Agent-side GitHub access: reading issues, creating branches, pushing to non-protected branches, creating PRs, posting comments
- Issue-selection heuristics: label-based (`agent-eligible`), mention-based (`@swain`), with extensibility for future MCP filter
- Integration with `swain-keys` for commit signing (the agent should sign commits even with a scoped token)
- Documentation: operator runbook for setting up a PR-only agent loop

**Out of scope:**
- The specific token scoping mechanism (SPIKE-037 determines this)
- MCP-based deterministic issue filtering (future — architecture accommodates but doesn't implement)
- PR auto-merge or CI integration (separate ops concern)
- Multi-agent conflict resolution (INITIATIVE-013)

## Child Specs

| Spec | Title | Dependencies | Status |
|------|-------|-------------|--------|
| _TBD_ | Enforced worktree at swain-box startup | SPEC-081, SPEC-092 | — |
| _TBD_ | Host-assisted scoped token provisioning | SPIKE-037, SPEC-092 | — |
| _TBD_ | Agent issue-selection conventions | — | — |

_Child specs to be created after SPIKE-037 completes and the token scoping mechanism is decided._

## Key Dependencies

- **SPIKE-037** (GitHub Token Scoping Mechanisms) — must complete before the token provisioning spec can be written; determines fine-grained PAT vs GitHub App vs deploy key
- **SPEC-081** (Worktree-Enforced Sandbox Isolation) — provides the worktree creation primitives
- **SPEC-092** (swain-box Unified Sandbox Launcher) — integration point for startup-time enforcement
- **EPIC-040** (Sandbox Capability Bridges) — sibling epic; bridges provide the channels through which scoped credentials and GitHub access reach the sandbox

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation — layered guardrails for unattended PR-only agents |
