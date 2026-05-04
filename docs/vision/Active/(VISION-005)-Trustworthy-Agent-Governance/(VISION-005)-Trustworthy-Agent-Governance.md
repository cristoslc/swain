---
title: "Trustworthy Agent Governance"
artifact: VISION-005
track: standing
status: Active
product-type: personal
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: high
depends-on-artifacts:
  - VISION-001
  - VISION-003
trove: "platform-hooks-validation@21aa91c, agent-alignment-monitoring@8047381"
linked-artifacts:
  - VISION-001
  - VISION-002
  - VISION-003
  - PERSONA-001
---

# Trustworthy Agent Governance

## Target Audience

The operator ([PERSONA-001](../../../persona/Active/(PERSONA-001)-Swain-Project-Developer/(PERSONA-001)-Swain-Project-Developer.md)) running swain across multiple agentic coding platforms. The operator needs confidence that agents follow swain's process — ADR compliance, lifecycle transitions, spec consultation, skill invocation — not because they're instructed to, but because the runtime enforces it.

## Value Proposition

[VISION-001](../../Superseded/(VISION-001)-Swain/(VISION-001)-Swain.md) defines what swain is. [VISION-003](../(VISION-003)-Runtime-Portability/(VISION-003)-Runtime-Portability.md) asks "can swain run everywhere?" This vision asks: **"can swain be trusted everywhere?"**

Today, swain's governance is documentary — AGENTS.md, skill files, and lifecycle conventions live in prompt context. Research confirms that agents treat documentary governance as advisory: they optimize for task completion, not process fidelity, and bypass every workflow rule when a faster direct path exists. The vk4-swain compliance audit found zero spec artifacts re-read during implementation. The OpenAI monitoring study found the same pattern at the security layer.

This vision makes swain's governance executable and unskippable. Agents follow the process because the runtime enforces it — through deterministic hooks, policy rules, and validation gates that operate outside the model's control flow. The operator's trust in swain's output scales with enforcement depth, not supervision intensity.

## Problem Statement

Three structural gaps in swain's current governance model:

1. **Documentary governance is ignored under pressure.** AGENTS.md rules, skill routing tables, and lifecycle conventions are prompt-injected. The model can and does skip them when optimizing for speed. No amount of prompt engineering fixes this — it's a structural property of advisory governance.

2. **No enforcement substrate exists.** Swain has no hooks, policies, or validation gates that run outside the model's control flow. Every governance check depends on the agent choosing to perform it. The agent-alignment-monitoring trove confirms this is a universal problem across all agentic coding tools.

3. **Platform enforcement surfaces are rich but unmapped.** The platform-hooks-validation trove reveals that every major platform (Claude Code, Gemini CLI, Codex CLI, Copilot, OpenCode) provides deterministic enforcement mechanisms — PreToolUse hooks, policy engines, permission rules, approval gates — but swain doesn't use any of them. The building blocks exist; the wiring doesn't.

## Existing Landscape

- **Claude Code hooks** (24 events, PreToolUse blocks, managed settings) — richest enforcement surface; stateful `agent` hooks can inspect session context
- **Gemini CLI policy engine** (TOML rules, 5-tier priority, OS-owned admin policies) — most granular declarative enforcement; hooks + policies in combination
- **Codex CLI execpolicy** (Starlark rules, kernel-level sandbox) — strongest sandbox story; `forbidden` rules block without prompting; but no general PreToolUse hook
- **Copilot hooks** (PreToolUse deny, validation pipeline for hosted agent) — two enforcement models: local hooks for VS Code, structural constraints for hosted coding agent
- **OpenCode plugin hooks** (`tool.execute.before` with throw-to-block) — simplest hook API; but critical subagent bypass (#5894) undermines enforcement

No existing tool or framework provides cross-platform process governance enforcement. Security-focused enforcement (sandboxing, credential scoping) is well-served by [VISION-002](../(VISION-002)-Safe-Autonomy/(VISION-002)-Safe-Autonomy.md). This vision targets the adjacent problem: workflow and process enforcement.

## Build vs. Buy

Build. No existing solution provides cross-platform process governance for agentic coding. The enforcement primitives exist on each platform (hooks, policies, permission rules) but nobody has wired them together for workflow compliance. The build scope is adapters and a session-state tracker, not a framework — swain targets each platform's native enforcement surface rather than abstracting over it.

## Maintenance Budget

Low per platform. Each platform adapter is a thin shell script or config file that hooks into the platform's native mechanism. The session-state tracker (likely an MCP server) is the only shared component. Adding a new platform should take hours, not weeks. If the adapter layer grows complex, the architecture is wrong — the platform should be doing the enforcement, not swain.

## Success Metrics

- swain's ADR compliance check runs deterministically (via hook, not agent choice) on at least one platform within 30 days
- A process governance violation (skipped lifecycle transition, missed spec read) is caught and blocked before it lands, not after
- Enforcement coverage extends to at least 3 of the 5 target platforms within 90 days
- The operator can trust that "if the agent committed it, it followed the process" — without reviewing every session transcript

## Non-Goals

- Replacing [VISION-002](../(VISION-002)-Safe-Autonomy/(VISION-002)-Safe-Autonomy.md) (Safe Autonomy) — that vision covers security sandboxing and credential scoping; this covers process governance
- Building a general-purpose agent enforcement framework — swain targets specific workflow rules, not arbitrary policy enforcement
- Achieving identical enforcement depth on all platforms — degraded enforcement (post-hoc audit) beats no enforcement
- Real-time blocking of every possible process deviation — catching the high-value violations (spec consultation, ADR compliance, lifecycle transitions) is sufficient

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | 730b957 | Initial creation |
