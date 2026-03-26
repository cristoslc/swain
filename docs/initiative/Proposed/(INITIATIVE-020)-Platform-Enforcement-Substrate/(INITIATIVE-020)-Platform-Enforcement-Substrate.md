---
title: "Platform Enforcement Substrate"
artifact: INITIATIVE-020
track: container
status: Proposed
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
parent-vision: VISION-005
priority-weight: high
success-criteria:
  - PreToolUse hook adapter running on Claude Code that blocks commits without ADR compliance check
  - Session-state tracker (MCP server or equivalent) that hooks can query for process compliance
  - Post-hoc audit pipeline that validates process compliance on at least one additional platform
  - Cross-platform deny rules preventing governance file tampering on 3+ platforms
depends-on-artifacts: []
addresses: []
evidence-pool: "platform-hooks-validation@21aa91c"
linked-artifacts:
  - INITIATIVE-014
  - SPIKE-038
  - SPIKE-039
  - SPIKE-040
  - SPIKE-041
  - VISION-002
  - VISION-003
  - VISION-005
---

# Platform Enforcement Substrate

## Strategic Focus

Map each target platform's deterministic enforcement mechanisms and build the minimum adapter layer that makes swain's process governance unskippable. Priority: Claude Code first (richest hook surface, current home), Gemini CLI second (strongest policy engine), then Copilot/Codex/OpenCode as the ecosystem matures.

The core question is not "can we enforce?" — the platform-hooks-validation trove confirms every platform has enforcement primitives. The question is: "what's the thinnest adapter that wires swain's process rules into each platform's native enforcement?"

## Desired Outcomes

The operator can trust that agents running under swain follow the process:
- Specs are read before implementation begins
- ADR compliance checks run before commits land
- Lifecycle transitions happen when work completes
- Required skills are invoked, not skipped
- Governance files (AGENTS.md, skill files, policies) cannot be tampered with by the agent

## Scope Boundaries

**In scope:**
- Research spikes for each enforcement mechanism (hook adapters, session-state tracker, audit pipeline, deny rules)
- Implementation of hook-based process gates on Claude Code
- Design of a portable session-state tracker (MCP server) that any platform's hooks can query
- Post-hoc audit pipeline as universal backstop
- Cross-platform deny rules for governance file protection

**Out of scope:**
- Security sandboxing ([VISION-002](../../../vision/Active/(VISION-002)-Safe-Autonomy/(VISION-002)-Safe-Autonomy.md)'s domain)
- General-purpose policy enforcement framework
- Enforcement on platforms without deterministic hook mechanisms
- Feature parity across all platforms — Claude Code gets the deepest enforcement; others get what their platform supports

## Tracks

**Track A: Pre-execution gates** — PreToolUse hooks that block actions until process requirements are met (spec read, ADR check, skill invocation)

**Track B: Session state** — MCP server or equivalent that tracks what's happened in the session (which artifacts consulted, which skills invoked, which transitions occurred) so stateless hooks can query it

**Track C: Post-hoc validation** — CI/specwatch pipeline that catches what hooks miss, especially on platforms with weaker hook coverage

**Track D: Structural protection** — Deny rules and protected paths that prevent governance file tampering across all platforms

## Research Findings

### SPIKE-038: PreToolUse Hook Adapter Feasibility — **Go (4/5 platforms)**

Validated that PreToolUse hooks can implement process governance gates (ADR compliance on commit) on 4 of 5 target platforms. Working prototypes committed for each.

| Platform | Verdict | Hook Mechanism | Key Finding |
|----------|---------|----------------|-------------|
| Claude Code | **Go** | `PreToolUse` hook | 13ms passthrough, deny-always-wins, 24 events including subagent coverage |
| Gemini CLI | **Go** | `BeforeTool` hook | Policy engine alternative for declarative rules, hook fingerprinting for security |
| Copilot CLI | **Go** | `PreToolUse` hook | Auto-discovers from `.github/hooks/`, identical `permissionDecision` field to Claude Code |
| OpenCode | **Go** | `tool.execute.before` plugin | Subagent bypass #5894 **fixed** in v1.2.20; regex bypass risk discovered |
| Codex CLI | **Structural limitation** | No PreToolUse hook | Relies on Starlark execpolicy — can block commands but can't run arbitrary validation |

**Cross-platform adapter portability:** Hook logic is nearly identical across platforms. Only JSON field names differ (`decision` vs `permissionDecision`, `toolName` vs `tool_name`). A shared core script with thin platform wrappers is viable.

**Committed prototypes:**
- `scripts/hooks/pretool-adr-gate.sh` — Claude Code
- `.gemini/hooks/adr-gate.sh` + `.gemini/settings.json` — Gemini CLI
- `.github/hooks/adr-gate.sh` + `.github/hooks/pre-tool-use.json` — Copilot CLI
- `.opencode/plugins/adr-gate.ts` — OpenCode

**Implication for Track A:** Pre-execution gates are feasible on 4 platforms. Next step is hardening the prototypes into production hooks (robust regex, shared core, additional process gates beyond ADR compliance).

**Implication for Codex:** Needs a different enforcement strategy — post-hoc audit (SPIKE-040) or MCP-server-side validation.

## Child Epics

_None yet. Remaining spikes (SPIKE-039..041) will inform epic scoping._

## Small Work (Epic-less Specs)

_None yet._

## Key Dependencies

- Remaining research spikes (SPIKE-039 through SPIKE-041) inform Tracks B, C, D
- [INITIATIVE-014](../../Active/(INITIATIVE-014)-Cross-Surface-Portability/(INITIATIVE-014)-Cross-Surface-Portability.md) (Cross-Surface Portability) provides the distribution substrate; this initiative provides the enforcement substrate
- ~~OpenCode's subagent bypass (#5894)~~ — **resolved in v1.2.20** (confirmed by SPIKE-038)
- Codex's nascent hooks engine may add PreToolUse in future versions — monitor

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | 730b957 | Initial creation |
