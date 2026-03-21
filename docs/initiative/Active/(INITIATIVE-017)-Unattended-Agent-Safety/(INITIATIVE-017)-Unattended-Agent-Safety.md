---
title: "Unattended Agent Safety"
artifact: INITIATIVE-017
track: container
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
parent-vision: VISION-002
priority-weight: high
success-criteria:
  - An unattended sandboxed agent can interact with GitHub (read issues, create PRs) using credentials that physically cannot push to protected branches
  - Credential provisioning happens on the privileged host and injects narrowed tokens into the sandbox — the agent never holds broader credentials than it needs
  - Filesystem isolation (enforced worktree) and API isolation (scoped token) provide independent, layered defense — compromising one does not compromise the other
  - The operator can leave an agent running `/loop` against a repo's issues with confidence that the worst-case outcome is a bad PR, not a broken main branch
depends-on-artifacts:
  - SPEC-081
  - SPEC-092
addresses: []
evidence-pool: ""
linked-artifacts:
  - EPIC-036
  - EPIC-037
  - INITIATIVE-010
  - INITIATIVE-011
  - INITIATIVE-013
  - SPEC-081
  - SPEC-092
  - SPIKE-035
---

# Unattended Agent Safety

## Strategic Focus

VISION-002 (Safe Autonomy) established that sandboxes are enablers, not restrictions — they let operators trust agents to run unattended. Previous initiatives (INITIATIVE-010, INITIATIVE-011) built the isolation and credential foundations. This initiative addresses the next gap: **an agent that can interact with external services (especially GitHub) while constrained so it can only propose changes, never land them directly.**

The motivating use case is an agent on a `/loop` that monitors GitHub issues, picks up eligible work, implements fixes in an isolated worktree, and opens PRs — all without the ability to push to `main` or merge its own PRs. This requires three layers of defense:

1. **Filesystem isolation** — enforced worktree at sandbox startup so the agent works on a branch, never directly on `main`
2. **API credential scoping** — the token injected into the sandbox permits `pull_requests: write` but cannot push to protected branches
3. **Host-assisted provisioning** — the privileged host (which has `gh auth`) creates and scopes the credentials, then injects only the narrowed token into the sandbox

This initiative is specifically about **trust infrastructure** — the primitives that make it safe to leave an agent alone. Future initiatives will build operational workflows (issue triage, auto-fix loops, CI integration) on top of these primitives.

## Scope Boundaries

**In scope:**
- Host-to-sandbox credential injection during `swain-box` startup (PAT, SSH key, or GitHub App token)
- Token scoping research and implementation (which GitHub mechanism gives "can PR, cannot push to main")
- Enforced worktree creation at sandbox startup so the agent's branch is isolated by default
- GitHub access from inside sandboxed containers (for reading issues, creating PRs, posting comments)
- Integration with existing `swain-keys` for signing keys vs. access keys distinction
- Bridge mechanisms for capabilities the agent needs (e.g., MCP access to GitHub) that the sandbox currently blocks

**Out of scope:**
- The `/loop` orchestration itself (already exists as a skill)
- Issue triage logic or agent-selection heuristics (future ops initiative)
- Deterministic MCP-based issue filtering (future enhancement — the architecture should accommodate it but this initiative doesn't build it)
- Multi-agent coordination (covered by INITIATIVE-013: Swarm Safety)
- General-purpose host escape hatches or weakening sandbox isolation

## Child Epics

| Epic | Title | Status |
|------|-------|--------|
| EPIC-036 | Sandbox Capability Bridges | Proposed |
| EPIC-037 | PR-Only Agent Guardrails | Active |

## Small Work (Epic-less Specs)

_None yet._

## Key Dependencies

- **SPEC-081** (Worktree-Enforced Sandbox Isolation) — provides the filesystem isolation layer this initiative builds on
- **SPEC-092** (swain-box Unified Sandbox Launcher) — the integration point for credential injection and worktree enforcement at startup
- **INITIATIVE-013** (Swarm Safety) — complementary; that initiative handles agents isolated from *each other*, this one handles an agent isolated from *the repo it operates on*
- **SPIKE-035** (Container-Compatible Auth Flows) — active research on per-runtime auth that informs how credentials reach agents

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation — trust infrastructure for unattended agent operations |
